"""Assemble level chapters from authored guides and explicit README sections.

Source selection is declarative and fails on missing headings or lesson routes.
The assembly changes presentation and links, not the canonical tutorial text.
"""

import os
import re
import tomllib
from pathlib import Path, PurePosixPath

from example_catalog import ExampleCatalog
from site_model import Page


class ReadmeSections:
    """Index real Markdown headings while ignoring code fences."""

    _HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")

    def __init__(self, text: str) -> None:
        """Keep a source snapshot and its actual heading positions for this build."""
        self.lines = text.splitlines()
        self.headings: list[tuple[int, int, str]] = []
        fence = ""
        for index, line in enumerate(self.lines):
            stripped = line.lstrip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                fence = "" if fence == marker else marker if not fence else fence
                continue
            match = self._HEADING.match(line) if not fence else None
            if match:
                self.headings.append((index, len(match.group(1)), match.group(2)))

    def body(self, title: str) -> str:
        """Return the exact named section body, with subordinate headings promoted for a page."""
        matches = [entry for entry in self.headings if entry[2] == title]
        if len(matches) != 1:
            raise ValueError(f"README heading must match exactly once: {title!r}; found {len(matches)}.")
        start, depth, _ = matches[0]
        end = next((index for index, level, _ in self.headings if index > start and level <= depth),
                   len(self.lines))
        result: list[str] = []
        fence = ""
        for line in self.lines[start + 1:end]:
            stripped = line.lstrip()
            if stripped.startswith(("```", "~~~")):
                marker = stripped[:3]
                fence = "" if fence == marker else marker if not fence else fence
            match = self._HEADING.match(line) if not fence else None
            if match:
                line = "#" * max(2, len(match.group(1)) - depth + 1) + " " + match.group(2)
            result.append(line)
        return "\n".join(result).strip()


class Curriculum:
    """Prepare validated chapter data over the existing source/lesson publication model."""

    def __init__(self, root: Path, configuration: Path, catalog: ExampleCatalog) -> None:
        """Read declared chapters and produce source bodies before generated output is replaced."""
        self.root = root.resolve()
        self.catalog = catalog
        self.pages: list[Page] = []
        self.bodies: dict[str, str] = {}
        self.readme = ReadmeSections((root / "README.md").read_text(encoding="utf-8"))
        payload = tomllib.loads(configuration.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("curriculum.toml requires schema_version = 1.")
        for chapter in payload.get("chapter", []):
            self._chapter(chapter)

    @staticmethod
    def _relative(origin: str, target: str, suffix: str = ".md") -> str:
        """Return a portable link from a chapter to another emitted page or asset."""
        return os.path.relpath(target + suffix, str(PurePosixPath(origin).parent)).replace("\\", "/")

    def _source(self, name: str) -> str:
        """Read an explicit authored guide within docs, excluding generated/private inputs."""
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0].startswith(("_", ".")):
            raise ValueError(f"Invalid authored chapter path: {name}")
        source = (self.root / "docs" / name).resolve()
        if not source.is_relative_to(self.root / "docs") or not source.is_file():
            raise ValueError(f"Missing or escaping chapter source: {name}")
        return source.read_text(encoding="utf-8")

    def _chapter(self, chapter: dict) -> None:
        """Resolve one chapter's canonical prose and exact lesson links; reject ambiguity."""
        identifier, title, level = chapter["id"], chapter["title"], chapter["level"]
        if level not in ExampleCatalog._LEVELS or not identifier.startswith(level + "/"):
            raise ValueError(f"Chapter {identifier} does not belong to a learning level.")
        has_readme, has_source = "readme" in chapter, "source" in chapter
        if has_readme == has_source:
            raise ValueError(f"Chapter {identifier} needs one README heading or authored source.")
        body = self.readme.body(chapter["readme"]) if has_readme else self._source(chapter["source"])
        if "end_before" in chapter:
            marker = chapter["end_before"]
            if marker not in body:
                raise ValueError(f"Chapter {identifier} lost its README boundary marker: {marker}")
            body = body[:body.index(marker)].rstrip()
        if has_readme:
            body = f"# {title}\n\n" + body
        body = self._rewrite_tour_links(identifier, body)
        selected = []
        for reference in chapter.get("lessons", []):
            tier, number = reference.split(":", 1)
            matches = [lesson for lesson in self.catalog.lessons if lesson.level == tier and lesson.number == number]
            if len(matches) != 1:
                raise ValueError(f"Chapter {identifier} requires one lesson for {reference}.")
            selected.append(matches[0])
        if chapter.get("show_steps", False) and selected:
            asset = "downloads/" + selected[0].source.removeprefix("UX_and_AIX_experiences/")
            body += ("\n\n## The workflow in code\n\nThese are the core steps from the saved example. "
                     "Use its complete linked script for all class definitions and setup.\n\n"
                     f"```{{literalinclude}} {self._relative(identifier, asset, '')}\n"
                     ":language: python\n:pyobject: main\n:linenos:\n```\n")
        body += "\n\n## Runnable examples\n\n"
        body += "\n".join(f"- [{lesson.title}]({self._relative(identifier, lesson.identifier)}) "
                          f"— {lesson.level.title()} {lesson.number}" for lesson in selected)
        body += (f"\n\n[All {level} examples]({self._relative(identifier, 'examples/'+level+'/index')}) · "
                 f"[Level contents](index.md) · [Full contents]({self._relative(identifier, 'contents')})\n")
        self.pages.append(Page(identifier, title, "", level + "/index"))
        self.bodies[identifier] = body

    def _rewrite_tour_links(self, identifier: str, body: str) -> str:
        """Translate the README's tour references into the four-level site routes."""
        mappings = {
            "[Part I](#-read-only-rooms-for-endpoints)": ("Advanced: read-only rooms", "advanced/read-only-rooms"),
            "[Part I](#part-i--the-basics)": ("Beginner", "beginner/index"),
            "[Part II](#part-ii--the-ceiling)": ("Expert", "expert/index"),
            "[documentation](#documentation)": ("full contents", "contents"),
        }
        for original, (label, destination) in mappings.items():
            body = body.replace(original, f"[{label}]({self._relative(identifier, destination)})")
        return body
