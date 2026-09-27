"""Audit built documentation metadata using only local HTML/XML and explicit policy.

This complements check_site.py. It does not query search engines, HTTP headers,
redirects or robots.txt; Read the Docs serves its own platform-managed robots file.
"""

import argparse
import fnmatch
import json
import os
import sys
import tomllib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal, Optional, TypedDict
from urllib.parse import quote, unquote, urlsplit


class SeoIssue(TypedDict):
    """One publication error or warning tied to its relative page or sitemap path."""

    level: str
    path: str
    message: str


class SeoPage(TypedDict):
    """Decoded metadata observed on one included HTML document."""

    path: str
    title: str
    description: str
    canonical: str
    h1_count: int
    noindex: bool


class SeoReport(TypedDict):
    """Deterministic local audit result; counts describe checks, never search ranking."""

    base_url: str
    html_directory: str
    content_pages: int
    errors: int
    warnings: int
    allow_noindex: bool
    issues: list[SeoIssue]
    pages: list[SeoPage]
    limitations: str


class SeoMetadata(HTMLParser):
    """Parse head metadata and headings without executing scripts or retaining handles."""

    def __init__(self, content: str) -> None:
        """Parse a document; missing or duplicate elements remain visible to the policy check."""
        super().__init__(convert_charrefs=True)
        self._in_head = False
        self._in_title = False
        self._in_h1 = False
        self.titles: list[str] = []
        self.h1s: list[str] = []
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.lang = ""
        self.feed(content)
        self.close()

    @staticmethod
    def normalized(value: str) -> str:
        """Fold HTML whitespace without changing punctuation or Unicode text."""
        return " ".join(value.split())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        """Collect declared elements; description/canonical/robots values must come from head."""
        values = dict(attrs)
        if tag == "html":
            self.lang = (values.get("lang") or "").strip()
        elif tag == "head":
            self._in_head = True
        elif tag == "title" and self._in_head:
            self._in_title = True
            self.titles.append("")
        elif tag == "h1":
            self._in_h1 = True
            self.h1s.append("")
        elif tag == "meta" and self._in_head:
            name = (values.get("name") or "").casefold()
            content = self.normalized(values.get("content") or "")
            if name == "description":
                self.descriptions.append(content)
            elif name in ("robots", "googlebot"):
                self.robots.append(content.casefold())
        elif tag == "link" and self._in_head:
            if "canonical" in (values.get("rel") or "").casefold().split():
                self.canonicals.append((values.get("href") or "").strip())

    def handle_endtag(self, tag: str) -> None:
        """End text collection at its element boundary, including a closed head."""
        if tag == "head":
            self._in_head = False
            self._in_title = False
        elif tag == "title":
            self._in_title = False
        elif tag == "h1":
            self._in_h1 = False

    def handle_data(self, data: str) -> None:
        """Accumulate nested text only for the currently open title or main heading."""
        if self._in_title:
            self.titles[-1] += data
        if self._in_h1:
            self.h1s[-1] += data


class SeoCheck:
    """Audit one HTML build with explicit canonical, description and indexing policy.

    The instance retains parsed values only. Repeated run() calls reset those
    values and produce the same result for identical files. Generated pages are
    never modified; filesystem/parse failures propagate to the CLI's input error.
    """

    _IGNORED_PARTS = frozenset(("_static", "_modules", "_sources", "_downloads", "downloads"))
    _IGNORED_PAGES = frozenset(("search.html", "genindex.html", "py-modindex.html", "404.html"))
    _SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

    def __init__(self, directory: Path, base_url: str, required: tuple[str, ...] = (),
                 allow_noindex: bool = False) -> None:
        """Validate immutable inputs before reading pages; raise ValueError for invalid roots/base URLs."""
        self.root = directory.resolve()
        self.base_url = base_url.rstrip("/") + "/"
        parsed = urlsplit(self.base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("Canonical base must be an absolute HTTP(S) URL without query or fragment.")
        if not self.root.is_dir():
            raise ValueError(f"HTML directory does not exist: {self.root}")
        self._base_path = parsed.path
        self.required = required
        self.allow_noindex = allow_noindex
        self.issues: list[SeoIssue] = []
        self.pages: list[SeoPage] = []
        self._sitemap_urls: set[str] = set()
        self._matched_required: set[str] = set()
        self._has_sitemap = False

    def _issue(self, level: str, path: str, message: str) -> None:
        """Append one ordered issue without changing page or source data."""
        self.issues.append({"level": level, "path": path, "message": message})

    def _sitemap(self) -> None:
        """Validate the page sitemap and contained local destinations before auditing inclusion."""
        path = self.root / "sitemap.xml"
        if not path.is_file():
            self._issue("error", "sitemap.xml", "Missing sitemap; build with READTHEDOCS_CANONICAL_URL.")
            return
        if not path.resolve().is_relative_to(self.root):
            self._issue("error", "sitemap.xml", "Sitemap escapes the output directory via symlink.")
            return
        tree = ET.parse(path)
        if tree.getroot().tag != self._SITEMAP_NS + "urlset":
            self._issue("error", "sitemap.xml", "Expected the generated page-level sitemap (urlset).")
            return
        self._has_sitemap = True
        for element in tree.findall(f"{self._SITEMAP_NS}url/{self._SITEMAP_NS}loc"):
            url = (element.text or "").strip()
            if url in self._sitemap_urls:
                self._issue("error", "sitemap.xml", f"Duplicate sitemap URL: {url}")
            self._sitemap_urls.add(url)
            self._sitemap_target(url)

    def _sitemap_target(self, url: str) -> None:
        """Check one sitemap URL's version/base and corresponding contained output file."""
        if not url.startswith(self.base_url):
            self._issue("error", "sitemap.xml", f"URL is outside the expected base: {url}")
            return
        parsed = urlsplit(url)
        if parsed.query or parsed.fragment:
            self._issue("error", "sitemap.xml", f"Query or fragment in sitemap URL: {url}")
        relative = unquote(parsed.path[len(self._base_path):])
        if not relative or relative.endswith("/"):
            relative += "index.html"
        target = (self.root / relative).resolve()
        if not target.is_relative_to(self.root) or not target.is_file():
            self._issue("error", "sitemap.xml", f"URL does not map to an existing local file: {url}")

    def _page(self, path: Path, relative: str) -> None:
        """Parse and check one content page, recording its exact decoded metadata."""
        if not path.resolve().is_relative_to(self.root):
            self._issue("error", relative, "HTML file escapes the output directory via symlink.")
            return
        meta = SeoMetadata(path.read_text(encoding="utf-8"))
        expected = self.base_url + quote(relative, safe="/")
        matched = {pattern for pattern in self.required if fnmatch.fnmatchcase(relative, pattern)}
        self._matched_required.update(matched)
        title = meta.normalized(meta.titles[0]) if meta.titles else ""
        description = meta.descriptions[0] if meta.descriptions else ""
        canonical = meta.canonicals[0] if meta.canonicals else ""
        if len(meta.titles) != 1 or not title:
            self._issue("error", relative, "Expected exactly one nonempty title in head.")
        if len(meta.h1s) != 1 or not meta.normalized(meta.h1s[0]):
            self._issue("warning", relative, "Expected one clear nonempty H1 (editorial convention).")
        if not meta.lang:
            self._issue("warning", relative, "Missing HTML lang attribute.")
        if len(meta.descriptions) > 1:
            self._issue("error", relative, "More than one description tag; choose one metadata owner.")
        if not description:
            self._issue("error" if matched else "warning", relative, "Missing nonempty description.")
        if len(meta.canonicals) != 1 or not canonical:
            self._issue("error", relative, "Expected exactly one nonempty canonical link in head.")
        elif canonical != expected:
            self._issue("error", relative, f"Expected canonical {expected}; found {canonical}.")
        noindex = any({"noindex", "none"}.intersection(value.replace(",", " ").split()) for value in meta.robots)
        if noindex and not self.allow_noindex:
            self._issue("error", relative, "Unexpected noindex on an indexed content page.")
        if self._has_sitemap and expected not in self._sitemap_urls:
            self._issue("error", relative, "Content page missing from the version sitemap.")
        if self._has_sitemap and canonical and canonical not in self._sitemap_urls:
            self._issue("error", relative, "Canonical does not appear in the version sitemap.")
        self.pages.append({"path": relative, "title": title, "description": description,
                           "canonical": canonical, "h1_count": len(meta.h1s), "noindex": noindex})

    def _duplicates(self, field: Literal["title", "description"], level: str) -> None:
        """Report shared nonempty text after whitespace normalization and Unicode case folding."""
        grouped: dict[str, list[str]] = {}
        for page in self.pages:
            value = page[field]
            if value:
                grouped.setdefault(value.casefold(), []).append(page["path"])
        for value, paths in sorted(grouped.items()):
            if len(paths) > 1:
                self._issue(level, ", ".join(paths), f"Duplicate {field}: {value}")

    def run(self) -> SeoReport:
        """Return a stable report; propagate unreadable input errors instead of claiming a pass.

        Result lists are copied so a later run clearing this instance's working
        collections cannot alter a report already handed to its caller.
        """
        self.issues.clear()
        self.pages.clear()
        self._sitemap_urls.clear()
        self._matched_required.clear()
        self._has_sitemap = False
        self._sitemap()
        for path in sorted(self.root.rglob("*.html")):
            relative_path = path.relative_to(self.root)
            relative = relative_path.as_posix()
            if self._IGNORED_PARTS.intersection(relative_path.parts) or relative in self._IGNORED_PAGES:
                continue
            self._page(path, relative)
        if not self.pages:
            self._issue("error", ".", "No content HTML files found.")
        for pattern in sorted(set(self.required) - self._matched_required):
            self._issue("error", ".", f"Required-description pattern matched no page: {pattern}")
        self._duplicates("title", "error")
        self._duplicates("description", "warning")
        return {"base_url": self.base_url, "html_directory": str(self.root),
                "content_pages": len(self.pages), "errors": sum(item["level"] == "error" for item in self.issues),
                "warnings": sum(item["level"] == "warning" for item in self.issues),
                "allow_noindex": self.allow_noindex, "issues": list(self.issues), "pages": list(self.pages),
                "limitations": "Local HTML/XML only; no live headers, robots, redirects, indexing or ranking checks."}

    @staticmethod
    def policy_patterns(path: Optional[Path]) -> tuple[str, ...]:
        """Read an optional schema-versioned TOML policy; reject malformed required-page lists."""
        if path is None:
            return ()
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
        patterns = payload.get("required_descriptions")
        if (payload.get("schema_version") != 1 or not isinstance(patterns, list)
                or not all(isinstance(value, str) and value.strip() for value in patterns)):
            raise ValueError("SEO policy requires schema_version = 1 and a list of nonempty required_descriptions.")
        return tuple(patterns)

    @classmethod
    def main(cls) -> int:
        """Run the CLI: return 0 for valid output, 1 for policy errors, 2 for unreadable inputs.

        RTD external builds are intentional previews and may retain noindex.
        Other callers opt in with --allow-noindex. Only the optional JSON report
        is written; errors leave the generated pages and source tree untouched.
        """
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("directory", type=Path)
        parser.add_argument("--base-url", required=True)
        parser.add_argument("--policy", type=Path)
        parser.add_argument("--require-description", action="append", default=[], metavar="GLOB")
        parser.add_argument("--allow-noindex", action="store_true", help="Allow intentionally unindexed previews.")
        parser.add_argument("--json", type=Path, dest="json_path")
        args = parser.parse_args()
        try:
            required = cls.policy_patterns(args.policy) + tuple(args.require_description)
            preview = args.allow_noindex or os.environ.get("READTHEDOCS_VERSION_TYPE") == "external"
            report = cls(args.directory, args.base_url, required, preview).run()
            if args.json_path:
                args.json_path.parent.mkdir(parents=True, exist_ok=True)
                args.json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except (OSError, ValueError, ET.ParseError) as error:
            sys.stderr.write(f"SEO audit could not run: {error}\n")
            return 2
        sys.stdout.write(f"Audited {report['content_pages']} content pages: "
                         f"{report['errors']} errors, {report['warnings']} warnings.\n")
        errors = [issue for issue in report["issues"] if issue["level"] == "error"]
        for issue in errors[:30]:
            sys.stderr.write(f"ERROR: {issue['path']}: {issue['message']}\n")
        if report["warnings"] or len(errors) > 30:
            sys.stdout.write("Use --json for all page metadata and individual issues.\n")
        return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(SeoCheck.main())
