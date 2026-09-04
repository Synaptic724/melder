"""Assemble and build Melder's explicitly selected public documentation.

The tool owns only docs/_build output. It validates navigation and source paths
before replacing the generated source directory. Canonical inputs are read-only.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Mapping, Optional

from site_model import Asset, Page
from example_catalog import ExampleCatalog
from curriculum import Curriculum


class DocumentationBuilder:
    """Own one bounded docs build without retaining file handles or runtime objects.

    Contract: input validation finishes before generated-source cleanup. Output
    paths must resolve below this repository's docs/_build directory. The four
    learning levels and single-parent navigation are enforced before generation.
    """

    _LEVEL_IDS = ("beginner/index", "intermediate/index", "advanced/index", "expert/index")
    _LEVEL_TITLES = ("🟢 Beginner", "🟡 Intermediate", "🟠 Advanced", "🔵 Expert")
    _PUBLIC_ASSET_ROOTS = ("UX_and_AIX_experiences", "architecture_and_design")

    def __init__(self, root: Optional[Path] = None) -> None:
        """Resolve the repository root; the supplied path is borrowed immutable configuration."""
        self.root = (root or Path(__file__).resolve().parents[2]).resolve()
        self.docs = self.root / "docs"
        self.generated = self.docs / "_build"
        self.pages: list[Page] = []
        self.assets: list[Asset] = []
        self.catalog: Optional[ExampleCatalog] = None
        self.generated_bodies: dict[str, str] = {}

    @staticmethod
    def _text(row: object, key: str) -> str:
        """Return a declared string field; reject malformed configuration with its field name."""
        if not isinstance(row, dict):
            raise ValueError("Each navigation declaration must be a TOML table.")
        value = row.get(key)
        if not isinstance(value, str):
            raise ValueError(f"Navigation field {key!r} must be a string.")
        return value

    @staticmethod
    def _rows(payload: Mapping[str, object], key: str) -> list[object]:
        """Return a declared table array; reject scalar or object values before processing rows."""
        rows = payload.get(key, [])
        if not isinstance(rows, list):
            raise ValueError(f"Navigation {key!r} must be an array of tables.")
        return rows

    @staticmethod
    def _relative(value: str) -> PurePosixPath:
        """Validate a nonempty portable relative path without traversal or platform drive syntax."""
        path = PurePosixPath(value)
        if (not value or not path.parts or path.as_posix() != value or path.is_absolute()
                or ".." in path.parts or "\\" in value or ":" in value):
            raise ValueError(f"Expected a contained relative path, got {value!r}.")
        return path

    def _input(self, base: Path, value: str) -> Path:
        """Resolve an existing input under its declared root; reject symlinks escaping that root."""
        candidate = (base / self._relative(value)).resolve()
        if not candidate.is_relative_to(base.resolve()) or not candidate.is_file():
            raise ValueError(f"Missing or escaping documentation input: {value}")
        return candidate

    def load(self) -> None:
        """Parse and validate all navigation/assets before any generated directory is touched."""
        payload = tomllib.loads((self.docs / "navigation.toml").read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("docs/navigation.toml requires schema_version = 1.")
        self.pages = [Page(*(self._text(row, key) for key in ("id", "title", "source", "parent")))
                      for row in self._rows(payload, "page")]
        self.assets = [Asset(self._text(row, "source"), self._text(row, "target"))
                       for row in self._rows(payload, "asset")]
        self.catalog = None
        self.generated_bodies = {}
        if "example_catalog" in payload:
            self.catalog = ExampleCatalog(self.root, self._input(self.docs, self._text(payload, "example_catalog")))
            generated = {page.identifier: page for page in self.catalog.pages}
            self.pages = [Page(page.identifier, page.title, page.source,
                               generated[page.identifier].parent if page.identifier in generated else page.parent)
                          for page in self.pages]
            existing = {page.identifier for page in self.pages}
            self.pages.extend(page for page in self.catalog.pages if page.identifier not in existing)
            self.generated_bodies = self.catalog.bodies
        if "curriculum" in payload:
            if self.catalog is None:
                raise ValueError("Curriculum chapters require the validated example catalog.")
            curriculum = Curriculum(self.root, self._input(self.docs, self._text(payload, "curriculum")), self.catalog)
            self.pages.extend(curriculum.pages)
            self.generated_bodies.update(curriculum.bodies)
        identifiers = [page.identifier for page in self.pages]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Navigation contains duplicate page IDs.")
        if not self.pages or identifiers[0] != "index" or self.pages[0].parent:
            raise ValueError("The first navigation page must be the parentless index.")
        learning = tuple(page.identifier for page in self.pages if page.identifier in self._LEVEL_IDS)
        if learning != self._LEVEL_IDS:
            raise ValueError("Learning levels must be Beginner, Intermediate, Advanced, Expert in order.")
        if tuple(page.title for page in self.pages if page.identifier in self._LEVEL_IDS) != self._LEVEL_TITLES:
            raise ValueError("Learning level names and indicators must match the README exactly.")
        for page in self.pages:
            self._relative(page.identifier)
            if page.identifier in self._LEVEL_IDS and page.parent != "index":
                raise ValueError(f"Learning level {page.identifier!r} must be a direct root child.")
            if page.identifier != "index" and page.parent not in identifiers:
                raise ValueError(f"Page {page.identifier!r} needs a declared parent.")
            if page.source:
                if self._relative(page.source).parts[0].startswith(("_", ".")):
                    raise ValueError(f"Page source must be authored public content: {page.source}")
                self._input(self.docs, page.source)
            elif page.identifier != "contents" and page.identifier not in self.generated_bodies:
                raise ValueError(f"Page {page.identifier!r} has no authored source.")
        parents = {page.identifier: page.parent for page in self.pages}
        for identifier in identifiers:
            ancestors: set[str] = set()
            while identifier:
                if identifier in ancestors:
                    raise ValueError(f"Navigation parent cycle at {identifier}.")
                ancestors.add(identifier)
                identifier = parents[identifier]
        targets: set[str] = set()
        for asset in self.assets:
            if self._relative(asset.source).parts[0] not in self._PUBLIC_ASSET_ROOTS:
                raise ValueError(f"Asset is outside the public input roots: {asset.source}")
            self._input(self.root, asset.source)
            self._relative(asset.target)
            if asset.target in targets or asset.target.endswith((".md", ".rst")):
                raise ValueError(f"Duplicate or document-shaped asset target: {asset.target}")
            targets.add(asset.target)

    def _output(self, name: str) -> Path:
        """Return an expected generated child; refuse paths escaping the repository build root."""
        if self.docs.resolve() != self.root / "docs":
            raise ValueError("The documentation root must not redirect outside this repository.")
        expected = self.root / "docs" / "_build"
        if self.generated.resolve() != expected:
            raise ValueError("docs/_build must not redirect outside the documentation root.")
        target = (self.generated / self._relative(name)).resolve()
        if target == expected or not target.is_relative_to(expected):
            raise ValueError(f"Refusing unsafe generated output: {target}")
        return target

    def _children(self, parent: str) -> list[Page]:
        """Return children in the single declared navigation order."""
        return [page for page in self.pages if page.parent == parent]

    def _contents(self, parent: str = "index", depth: int = 0) -> str:
        """Render the complete hierarchy as links without creating a second Sphinx parent graph."""
        lines: list[str] = []
        for page in self._children(parent):
            if page.identifier == "contents":
                continue
            lines.append(f"{'  ' * depth}- [{page.title}]({page.identifier}.md)")
            nested = self._contents(page.identifier, depth + 1)
            if nested:
                lines.append(nested)
        return "\n".join(lines)

    def prepare(self) -> Path:
        """Validate, then replace only the verified generated source tree and return its path."""
        self.load()
        source = self._output("source")
        if source.exists():
            shutil.rmtree(source)
        source.mkdir(parents=True)
        for page in self.pages:
            destination = source / (page.identifier + ".md")
            destination.parent.mkdir(parents=True, exist_ok=True)
            if page.source:
                body = (self.docs / page.source).read_text(encoding="utf-8")
            elif page.identifier == "contents":
                body = "# Full Contents\n\nChoose any topic or follow a level in order.\n\n" + self._contents() + "\n"
            else:
                body = self.generated_bodies[page.identifier]
            if self.catalog is not None and page.identifier == "examples/index":
                body += self.generated_bodies[page.identifier]
            if self.catalog is not None and page.identifier in self._LEVEL_IDS:
                level = page.identifier.split('/')[0]
                count = sum(lesson.level == level for lesson in self.catalog.lessons)
                body += f"\n\n## Runnable examples\n\n[Browse all {count} {level} lessons](../examples/{level}/index.md).\n"
                chapters = self._children(page.identifier)
                if chapters:
                    body += "\n## Level contents\n\n" + "\n".join(
                        f"- [{child.title}]({os.path.relpath(child.identifier, level).replace(chr(92), '/')}.md)"
                        for child in chapters) + "\n"
            children = self._children(page.identifier)
            if children:
                relative = [child.title + " <" + os.path.relpath(
                    child.identifier, str(PurePosixPath(page.identifier).parent)).replace("\\", "/") + ">"
                    for child in children]
                # A blank line terminates a preceding raw HTML catalog block.
                body += "\n\n```{toctree}\n:hidden:\n\n" + "\n".join(relative) + "\n```\n"
            destination.write_text(body, encoding="utf-8", newline="\n")
        for asset in self.assets:
            destination = source / asset.target
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self._input(self.root, asset.source), destination)
        if self.catalog is not None:
            self.catalog.write_assets(source)
        return source

    def build(self, builder: str = "html") -> int:
        """Prepare selected inputs and run Sphinx; return its real status and retain diagnostics."""
        source = self.prepare()
        output = self._output(builder)
        output.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, "-m", "sphinx", "-q", "-b", builder, "-W", "--keep-going",
                   "-c", str(self.docs), "-d", str(self._output("doctrees")),
                   str(source), str(output)]
        status = subprocess.run(command, cwd=self.root, check=False).returncode
        if status == 0:
            sys.stdout.write(f"Built {len(self.pages)} pages: {output}\n")
        return status

    def run(self) -> int:
        """Run prepare/check/build commands; configuration and IO errors produce actionable failures."""
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("command", choices=("prepare", "check", "build"), nargs="?", default="build")
        parser.add_argument("--builder", choices=("html", "dirhtml", "epub", "latex"), default="html")
        args = parser.parse_args()
        try:
            if args.command == "check":
                self.load()
                sys.stdout.write(f"Navigation valid: {len(self.pages)} pages, {len(self.assets)} assets.\n")
                return 0
            if args.command == "prepare":
                sys.stdout.write(str(self.prepare()) + "\n")
                return 0
            return self.build(args.builder)
        except (OSError, ValueError, KeyError, TypeError) as error:
            sys.stderr.write(f"Documentation build refused: {error}\n")
            return 2


if __name__ == "__main__":
    raise SystemExit(DocumentationBuilder().run())
