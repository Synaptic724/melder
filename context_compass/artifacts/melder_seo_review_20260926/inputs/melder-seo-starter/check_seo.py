#!/usr/bin/env python3
"""Audit Melder's generated HTML. Standard library only; makes no network requests.

This is a local publication-policy check, not a Google ranking or indexing test.
It complements docs/tools/check_site.py rather than replacing its link checks.
Python 3.10+; run Melder's own documentation build with its required Python 3.14.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

IGNORED_PARTS = {"_static", "_modules", "_sources", "_downloads", "downloads"}
IGNORED_PAGES = {"search.html", "genindex.html", "py-modindex.html", "404.html"}
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def normalized(text: str) -> str:
    return " ".join(text.split())


class Metadata(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.in_h1 = False
        self.titles: list[str] = []
        self.h1s: list[str] = []
        self.descriptions: list[str] = []
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.lang = ""
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = (attrs.get("lang") or "").strip()
        elif tag == "head":
            self.in_head = True
        elif tag == "title" and self.in_head:
            self.in_title = True
            self.titles.append("")
        elif tag == "h1":
            self.in_h1 = True
            self.h1s.append("")
        elif tag == "meta" and self.in_head:
            name = (attrs.get("name") or "").casefold()
            content = normalized(attrs.get("content") or "")
            if name == "description":
                self.descriptions.append(content)
            elif name in {"robots", "googlebot"}:
                self.robots.append(content.casefold())
        elif tag == "link" and self.in_head:
            if "canonical" in (attrs.get("rel") or "").casefold().split():
                self.canonicals.append((attrs.get("href") or "").strip())

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        elif tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title and self.titles:
            self.titles[-1] += data
        if self.in_h1 and self.h1s:
            self.h1s[-1] += data


def audit(root: Path, base_url: str, required: tuple[str, ...] = ()) -> dict:
    root = root.resolve()
    base_url = base_url.rstrip("/") + "/"
    parsed_base = urlsplit(base_url)
    if (parsed_base.scheme not in {"http", "https"} or not parsed_base.netloc
            or parsed_base.query or parsed_base.fragment):
        raise ValueError("--base-url must be an absolute HTTP(S) URL without query or fragment")
    if not root.is_dir():
        raise ValueError(f"HTML directory does not exist: {root}")
    issues: list[dict[str, str]] = []
    pages: list[dict] = []

    def issue(level: str, path: str, message: str):
        issues.append({"level": level, "path": path, "message": message})

    sitemap_path = root / "sitemap.xml"
    sitemap_urls: set[str] = set()
    has_sitemap = False
    if not sitemap_path.is_file():
        issue("error", "sitemap.xml", "Missing sitemap; set READTHEDOCS_CANONICAL_URL before building.")
    else:
        tree = ET.parse(sitemap_path)
        if tree.getroot().tag != SITEMAP_NS + "urlset":
            issue("error", "sitemap.xml", "Expected Melder's page-level sitemap (urlset), not a sitemap index.")
        else:
            has_sitemap = True
            for element in tree.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc"):
                url = (element.text or "").strip()
                if url in sitemap_urls:
                    issue("error", "sitemap.xml", f"Duplicate URL: {url}")
                sitemap_urls.add(url)
                if not url.startswith(base_url):
                    issue("error", "sitemap.xml", f"URL is outside expected version/base: {url}")
                    continue
                parsed = urlsplit(url)
                if parsed.query or parsed.fragment:
                    issue("error", "sitemap.xml", f"Query or fragment in sitemap URL: {url}")
                relative = unquote(parsed.path[len(parsed_base.path):])
                if relative.endswith("/") or not relative:
                    relative += "index.html"
                target = (root / relative).resolve()
                if not target.is_relative_to(root) or not target.is_file():
                    issue("error", "sitemap.xml", f"URL does not map to an existing local file: {url}")

    titles: dict[str, list[str]] = defaultdict(list)
    descriptions: dict[str, list[str]] = defaultdict(list)
    matched_required: set[str] = set()
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root).as_posix()
        if IGNORED_PARTS.intersection(path.relative_to(root).parts) or relative in IGNORED_PAGES:
            continue
        if not path.resolve().is_relative_to(root):
            issue("error", relative, "HTML file escapes the output directory via symlink")
            continue
        meta = Metadata(path.read_text(encoding="utf-8"))
        must_describe = False
        for pattern in required:
            if fnmatch.fnmatchcase(relative, pattern):
                must_describe = True
                matched_required.add(pattern)
        expected = base_url + quote(relative, safe="/")
        title = normalized(meta.titles[0]) if meta.titles else ""
        description = meta.descriptions[0] if meta.descriptions else ""
        canonical = meta.canonicals[0] if meta.canonicals else ""
        if len(meta.titles) != 1 or not title:
            issue("error", relative, "Expected exactly one nonempty <title> in <head>")
        else:
            titles[title.casefold()].append(relative)
        # One H1 is a chosen documentation convention, not a Google ranking rule.
        if len(meta.h1s) != 1 or not normalized(meta.h1s[0]):
            issue("warning", relative, "Expected one clear, nonempty H1 (editorial convention)")
        if not meta.lang:
            issue("warning", relative, "Missing html lang attribute (accessibility/metadata check)")
        if len(meta.descriptions) > 1:
            issue("error", relative, "More than one meta description; choose a single owner")
        if not description:
            issue("error" if must_describe else "warning", relative, "Missing nonempty meta description")
        else:
            descriptions[description.casefold()].append(relative)
        if len(meta.canonicals) != 1 or not canonical:
            issue("error", relative, "Expected exactly one nonempty canonical link in <head>")
        elif canonical != expected:
            issue("error", relative, f"Expected canonical {expected}; found {canonical}. Review intentional exceptions.")
        noindex = any({"noindex", "none"}.intersection(value.replace(",", " ").split()) for value in meta.robots)
        if noindex:
            issue("error", relative, "noindex on a content page in this public/indexable-build audit")
        if has_sitemap and expected not in sitemap_urls:
            issue("error", relative, "Content page missing from this version's sitemap")
        if has_sitemap and canonical and canonical not in sitemap_urls:
            issue("error", relative, "Canonical does not appear in this version's sitemap")
        pages.append({"path": relative, "title": title, "description": description,
                      "canonical": canonical, "h1_count": len(meta.h1s), "noindex": noindex})
    if not pages:
        issue("error", ".", "No content HTML files found")
    for pattern in sorted(set(required) - matched_required):
        issue("error", ".", f"Required-description pattern matched no page: {pattern}")
    for title, paths in titles.items():
        if len(paths) > 1:
            issue("error", ", ".join(paths), f"Duplicate title: {title}")
    for description, paths in descriptions.items():
        if len(paths) > 1:
            issue("warning", ", ".join(paths), "Duplicate meta description; review page-specific summaries")
    return {"base_url": base_url, "html_directory": str(root), "content_pages": len(pages),
            "errors": sum(item["level"] == "error" for item in issues),
            "warnings": sum(item["level"] == "warning" for item in issues),
            "issues": issues, "pages": pages,
            "limitations": "Local HTML only. Does not inspect HTTP headers, robots.txt, live redirects, Google indexing, or performance. Assumes Melder's html builder and version-local self-canonicals."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--require-description", action="append", default=[], metavar="GLOB",
                        help="Fail on missing descriptions for this relative-HTML glob; repeat as needed")
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args()
    try:
        report = audit(args.directory, args.base_url, tuple(args.require_description))
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"SEO audit could not run: {exc}", file=sys.stderr)
        return 2
    print(f"Audited {report['content_pages']} content pages: {report['errors']} errors, {report['warnings']} warnings.")
    for item in report["issues"][:60]:
        print(f"{item['level'].upper()}: {item['path']}: {item['message']}")
    if len(report["issues"]) > 60:
        print("Additional issues omitted from console; use --json for the full report.")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
