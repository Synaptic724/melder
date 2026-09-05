"""Publish the manifest-selected architecture collection without duplicating its authored source."""

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from site_model import Asset, Page
from curriculum import ReadmeSections


class ArchitectureReference:
    """Prepare canonical architecture pages, local image/download routes, and source links.

    Only manifest documents and SVG/Mermaid assets linked by those documents
    enter the site. Repository source/test links remain revision-pinned Git links.
    """

    _LINK = re.compile(r"(!?)\[([^\]]+)\]\(([^\s)]+)\)")
    _ASSET_TYPES = frozenset((".svg", ".mmd"))

    def __init__(self, root: Path, revision: str) -> None:
        """Validate manifest inputs and adapt links before generated output is replaced."""
        self.root = root.resolve()
        self.directory = self.root / "architecture_and_design"
        self.revision = revision
        self.pages: list[Page] = []
        self.bodies: dict[str, str] = {}
        self.assets: list[Asset] = []
        self.selected_assets: set[str] = set()
        self.documents: dict[Path, str] = {}
        manifest = json.loads((self.directory / "manifest.json").read_text(encoding="utf-8"))
        if manifest["schema_version"] != 1:
            raise ValueError("Architecture manifest requires schema_version = 1.")
        for entry in manifest["documents"]:
            source = self._source(entry["path"])
            identifier = self._identifier(entry["path"])
            if source in self.documents or identifier in self.documents.values():
                raise ValueError(f"Duplicate architecture document: {entry['path']}")
            self.documents[source] = identifier
        self._verify_diagrams(manifest["diagrams"])
        for source, identifier in self.documents.items():
            body = source.read_text(encoding="utf-8")
            title = re.search(r"^# (.+)$", body, flags=re.MULTILINE)
            if title is None:
                raise ValueError(f"Architecture document needs a title: {source.name}")
            if identifier != "reference/architecture":
                self.pages.append(Page(identifier, title.group(1).strip(), "", "reference/architecture"))
            self.bodies[identifier] = self._adapt(body, source, identifier)

    def _source(self, relative: str) -> Path:
        """Resolve a real architecture input and refuse path traversal or escaped symlinks."""
        path = PurePosixPath(relative)
        source = (self.directory / path).resolve()
        if path.is_absolute() or ".." in path.parts or not source.is_relative_to(self.directory):
            raise ValueError(f"Architecture input escapes its public root: {relative}")
        if not source.is_file():
            raise ValueError(f"Missing architecture input: {relative}")
        return source

    @staticmethod
    def _identifier(relative: str) -> str:
        """Keep canonical subdirectories while mapping their README pages to stable index URLs."""
        path = PurePosixPath(relative).with_suffix("")
        if relative == "README.md":
            return "reference/architecture"
        if path.name == "README":
            path = path.with_name("index")
        return "reference/architecture/" + path.as_posix()

    def _verify_diagrams(self, diagrams: list[dict]) -> None:
        """Check existing manifest hashes, treating Mermaid source line endings as logical text.

        Git can check text out as CRLF on Windows. LF normalization matches the
        manifest's committed source hash without regenerating a canonical drawing.
        SVG output remains checked byte-for-byte against its recorded hash.
        """
        for diagram in diagrams:
            source = self._source(diagram["source"]).read_bytes().replace(b"\r\n", b"\n")
            rendered = self._source(diagram["rendered"]).read_bytes()
            if hashlib.sha256(source).hexdigest() != diagram["source_sha256"]:
                raise ValueError(f"Stale Mermaid source: {diagram['source']}; review its canonical diagram.")
            if hashlib.sha256(rendered).hexdigest() != diagram["rendered_sha256"]:
                raise ValueError(f"Stale rendered diagram: {diagram['rendered']}")

    @staticmethod
    def _relative(identifier: str, target: str) -> str:
        """Link between emitted pages/assets regardless of the original source directory depth."""
        return os.path.relpath(target, str(PurePosixPath(identifier).parent)).replace("\\", "/")

    def _adapt(self, body: str, source: Path, identifier: str) -> str:
        """Rewrite selected relative destinations while retaining all authored prose and captions."""
        def replace(match: re.Match) -> str:
            """Resolve one Markdown link without publishing unselected repository material."""
            image, label, target = match.groups()
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or target.startswith("#"):
                return match.group(0)
            destination = (source.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(self.root) or not destination.is_file():
                raise ValueError(f"Missing or escaping architecture link in {source.name}: {target}")
            fragment = "#" + parsed.fragment if parsed.fragment else ""
            if destination in self.documents:
                href = self._relative(identifier, self.documents[destination] + ".md") + fragment
                return f"[{label}]({href})"
            if destination.is_relative_to(self.directory) and destination.suffix in self._ASSET_TYPES:
                relative = destination.relative_to(self.directory).as_posix()
                output = "media/architecture/" + relative
                if relative not in self.selected_assets:
                    self.assets.append(Asset(destination.relative_to(self.root).as_posix(), output))
                    self.selected_assets.add(relative)
                href = self._relative(identifier, output) + fragment
                if image:
                    return f"![{label}]({href})"
                return "{download}`" + label.replace("`", "") + " <" + href + ">`"
            relative = destination.relative_to(self.root).as_posix()
            if relative.startswith(("context_compass/", ".")):
                raise ValueError(f"Architecture page links private work state: {relative}")
            href = f"https://github.com/Synaptic724/melder/blob/{self.revision}/{relative}" + fragment
            return f"[{label}]({href})"

        lines: list[str] = []
        fence = ""
        for line in body.splitlines(keepends=True):
            previous = fence
            fence = ReadmeSections._fence_state(line, fence)
            lines.append(line if previous or fence else self._LINK.sub(replace, line))
        if fence:
            raise ValueError(f"Unclosed architecture code fence in {source.name}")
        result = "".join(lines)
        source_path = source.relative_to(self.root).as_posix()
        return (result + "\n\n---\n\n"
                f"[Canonical source](https://github.com/Synaptic724/melder/blob/{self.revision}/{source_path}) · "
                f"[Full contents]({self._relative(identifier, 'contents.md')})\n")
