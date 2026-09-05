"""Validate built HTML navigation, anchors, assets, publication boundaries, and lesson source fidelity."""

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlsplit

from build_docs import DocumentationBuilder


class HtmlDocument(HTMLParser):
    """Collect actual HTML destinations and anchors without executing scripts or making network requests."""

    def __init__(self, content: str) -> None:
        """Parse one complete document and retain plain link/anchor/accessibility evidence."""
        super().__init__(convert_charrefs=True)
        self.identifiers: set[str] = set()
        self.links: list[str] = []
        self.duplicates: list[str] = []
        self.missing_alt = 0
        self.feed(content)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        """Record explicit browser-visible link/asset attributes and named fragment targets."""
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            if identifier in self.identifiers:
                self.duplicates.append(identifier)
            self.identifiers.add(identifier)
        if tag == "a" and values.get("name"):
            self.identifiers.add(values["name"])
        if values.get("href"):
            self.links.append(values["href"])
        if values.get("src"):
            self.links.append(values["src"])
        if tag == "img" and "alt" not in values:
            self.missing_alt += 1


class SiteCheck:
    """Verify the complete rendered site against the same explicit source model used to build it."""

    def __init__(self, root: Optional[Path] = None) -> None:
        """Resolve immutable roots; all state belongs to this individual verification run."""
        self.builder = DocumentationBuilder(root)
        self.directory = self.builder._output("html")
        self.documents: dict[Path, HtmlDocument] = {}
        self.errors: list[str] = []
        self.link_count = 0

    @staticmethod
    def destination(root: Path, origin: Path, url: str) -> tuple[Optional[Path], str]:
        """Resolve a local URL without network access, keeping query strings out of path/anchor checks."""
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            return None, ""
        name = unquote(parsed.path)
        path = root / name.lstrip("/") if name.startswith("/") else origin.parent / name
        if not name:
            path = origin
        if name.endswith("/"):
            path /= "index.html"
        return path.resolve(), unquote(parsed.fragment)

    def _links(self) -> None:
        """Verify every local file/fragment destination and collect concrete failures."""
        for origin, document in self.documents.items():
            relative = origin.relative_to(self.directory).as_posix()
            for url in document.links:
                path, fragment = self.destination(self.directory, origin, url)
                if path is None:
                    continue
                self.link_count += 1
                if not path.is_relative_to(self.directory) or not path.is_file():
                    self.errors.append(f"{relative}: missing local destination {url}")
                elif fragment and path.suffix == ".html" and fragment not in self.documents[path].identifiers:
                    self.errors.append(f"{relative}: missing fragment {url}")
            if document.duplicates:
                self.errors.append(f"{relative}: duplicate IDs {document.duplicates}")
            if document.missing_alt:
                self.errors.append(f"{relative}: {document.missing_alt} image(s) lack an alt attribute")

    def _coverage(self) -> None:
        """Require every declared page and every direct Full Contents route to exist."""
        expected = {page.identifier for page in self.builder.pages}
        for identifier in sorted(expected):
            if self.directory / (identifier + ".html") not in self.documents:
                self.errors.append(f"Missing declared page: {identifier}")
        contents = self.directory / "contents.html"
        if contents not in self.documents:
            self.errors.append("Full Contents was not generated.")
            return
        linked = {
            path for url in self.documents[contents].links
            for path, _ in [self.destination(self.directory, contents, url)] if path is not None
        }
        for identifier in sorted(expected - {"index", "contents"}):
            if self.directory / (identifier + ".html") not in linked:
                self.errors.append(f"Full Contents omits {identifier}")

    def _sources(self) -> None:
        """Compare every stable lesson/helper download with its exact current canonical bytes."""
        if self.builder.catalog is None:
            return
        for name, expected in self.builder.catalog.source_bytes.items():
            path = self.directory / "downloads" / name.removeprefix("UX_and_AIX_experiences/")
            if not path.is_file() or path.read_bytes() != expected:
                self.errors.append(f"Lesson/helper source drift: {name}")
        for path in self.directory.rglob("*"):
            parts = path.relative_to(self.directory).parts
            if any(part in ("context_compass", ".git", ".venv", "node_modules") for part in parts):
                self.errors.append(f"Private/unselected directory in output: {path.relative_to(self.directory)}")
            if path.name.lower() in ("agents.md", "skills.md", "_concept_map.txt"):
                self.errors.append(f"Working document in public output: {path.name}")

    def run(self) -> int:
        """Write a compact generated report and return nonzero for any deterministic site defect."""
        self.builder.load()
        self.documents = {path.resolve(): HtmlDocument(path.read_text(encoding="utf-8"))
                          for path in self.directory.rglob("*.html")}
        self._links()
        self._coverage()
        self._sources()
        report = {"html_files": len(self.documents), "declared_pages": len(self.builder.pages),
                  "local_links": self.link_count, "errors": sorted(set(self.errors))}
        (self.builder.generated / "site-check.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n",
        )
        if self.errors:
            sys.stderr.write("\n".join(report["errors"][:30]) + "\n")
            sys.stderr.write(f"Site validation failed: {len(report['errors'])} distinct error(s).\n")
            return 1
        sys.stdout.write(f"Site valid: {report['declared_pages']} pages, {self.link_count} local links; sources match.\n")
        return 0


if __name__ == "__main__":
    raise SystemExit(SiteCheck().run())
