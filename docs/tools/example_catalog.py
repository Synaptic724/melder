"""Render the saved curriculum without importing or executing its lesson modules.

Catalog declarations are reconciled against the real files before output starts.
Code is copied byte-for-byte into generated downloads, never re-authored here.
"""

import ast
import dataclasses
import hashlib
import html
import json
import os
import re
import subprocess
import textwrap
import tomllib
import zipfile
from pathlib import Path, PurePosixPath

from site_model import Page


@dataclasses.dataclass(frozen=True)
class Lesson:
    """Value-only metadata derived from one actual lesson's header and source identity."""

    source: str
    level: str
    number: str
    identifier: str
    title: str
    goal: str
    surfaces: str
    topics: tuple[str, ...]
    digest: str


class ExampleCatalog:
    """Reconcile and render four collections with no retained handles or runtime imports."""

    _LEVELS = ("beginner", "intermediate", "advanced", "expert")
    _TITLES = ("🟢 Beginner", "🟡 Intermediate", "🟠 Advanced", "🔵 Expert")
    _HEADER = re.compile(r"^(TIER|GOAL|SURFACE EXERCISED|VERIFY):\s*(.*)$")
    _TOPICS = (
        ("Registration", ("bind", "registration", "scan")),
        ("Resolution", ("meld", "resolv", "injection", "spellmap")),
        ("Lifetimes & cleanup", ("cleanup", "dispos", "lifetime", "lifecycle", "memory")),
        ("Configuration", ("config", "freeze", "posture", "knob")),
        ("Connections", ("link", "contract", "transfer", "cluster", "conduit cloud")),
        ("Inspection", ("inspect", "viewer", "describe", "inventory", "introspect")),
        ("Agent rooms & codegen", ("codegen", "workstation", "agent", "rift", "nexus")),
        ("Persistence & restore", ("persist", "checkpoint", "restore", "crystal", "reboot")),
        ("Research & change", ("research", "notch", "mutation", "diff", "impact", "campaign")),
        ("Concurrency", ("parallel", "concurr", "thread", "gate", "reader")),
    )

    def __init__(self, root: Path, configuration: Path) -> None:
        """Borrow immutable roots; load and validate all declared lesson metadata immediately."""
        self.root = root.resolve()
        self.source_root = self.root / "UX_and_AIX_experiences"
        self.lessons: list[Lesson] = []
        self.level_directories: dict[str, str] = {}
        self.pages: list[Page] = []
        self.bodies: dict[str, str] = {}
        # One immutable input snapshot keeps checksums, downloads, and bundles
        # consistent if a canonical file changes during this build.
        self.source_bytes: dict[str, bytes] = {}
        self._configuration = tomllib.loads(configuration.read_text(encoding="utf-8"))
        self._revision = self._source_revision()
        self._load()
        self._render()

    def _source_revision(self) -> str:
        """Use the hosted build commit or actual checkout HEAD for source links."""
        configured = os.environ.get("READTHEDOCS_GIT_COMMIT_HASH")
        if configured:
            return configured
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root, check=False,
                                capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return str(self._configuration["source_ref"])

    @classmethod
    def fields(cls, docstring: str) -> dict[str, str]:
        """Read the explicit header grammar; leave historical verification text separate."""
        chunks: dict[str, list[str]] = {}
        current = ""
        for line in docstring.splitlines():
            match = cls._HEADER.match(line)
            if match:
                current, first = match.groups()
                chunks[current] = [first]
            elif current:
                chunks[current].append(line)
        return {key: textwrap.dedent("\n".join(value)).strip() for key, value in chunks.items()}

    @classmethod
    def _topics(cls, text: str) -> tuple[str, ...]:
        """Assign browse labels from explicit goal/surface text; labels do not claim runtime behavior."""
        lowered = text.casefold().replace("_", " ")
        return tuple(title for title, words in cls._TOPICS if any(word in lowered for word in words))

    def _load(self) -> None:
        """Reconcile declared filenames with each source directory and require truthful header metadata."""
        if self._configuration.get("schema_version") != 1:
            raise ValueError("catalog.toml requires schema_version = 1.")
        levels = self._configuration["level"]
        if tuple(row["slug"] for row in levels) != self._LEVELS:
            raise ValueError("The catalog must declare the four learning levels in order.")
        overrides = {row["source"]: row for row in self._configuration.get("lesson", [])}
        for ordinal, row in enumerate(levels, 1):
            level = row["slug"]
            directory = f"{ordinal:02d}_{level}"
            if row["directory"] != directory:
                raise ValueError(f"Catalog directory for {level} must be {directory}.")
            self.level_directories[level] = directory
            path = (self.source_root / directory).resolve()
            if not path.is_relative_to(self.source_root.resolve()):
                raise ValueError(f"Example directory escaped its public root: {directory}")
            discovered = {item.name for item in path.glob("[0-9]*.py")}
            declared = row["sources"]
            if len(set(declared)) != len(declared) or set(declared) != discovered:
                raise ValueError(f"Catalog drift in {directory}: unregistered={sorted(discovered-set(declared))}; "
                                 f"missing={sorted(set(declared)-discovered)}; check duplicate declarations.")
            for member in sorted(path.glob("*.py")):
                if not member.is_file() or not member.resolve().is_relative_to(path):
                    raise ValueError(f"Escaping collection source or helper: {member.name}")
                self.source_bytes[member.relative_to(self.root).as_posix()] = member.read_bytes()
            for name in sorted(declared):
                source = path / name
                if source.name != name or not source.resolve().is_relative_to(path):
                    raise ValueError(f"Escaping lesson source: {name}")
                self.lessons.append(self._lesson(source, level, overrides))
        identifiers = [lesson.identifier for lesson in self.lessons]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("The lesson catalog contains duplicate page identifiers.")

    def _lesson(self, path: Path, level: str, overrides: dict) -> Lesson:
        """Extract syntax/header facts from one source, rejecting missing editorial contracts."""
        raw = self.source_bytes[path.relative_to(self.root).as_posix()]
        tree = ast.parse(raw.decode("utf-8-sig"), filename=str(path))
        fields = self.fields(ast.get_docstring(tree, clean=True) or "")
        relative = path.relative_to(self.root).as_posix()
        override = overrides.get(relative, {})
        for key in ("TIER", "GOAL", "SURFACE EXERCISED"):
            if not fields.get(key) and key not in override:
                raise ValueError(f"Lesson {relative} is missing {key}; correct its metadata from source.")
        if not fields["TIER"].casefold().startswith(level):
            raise ValueError(f"Lesson level disagrees with its source collection: {relative}")
        title = override.get("title", path.stem[3:].replace("_", " ").capitalize())
        identifier = override.get("id", f"examples/{level}/{path.stem.replace('_', '-')}")
        goal = override["GOAL"] if "GOAL" in override else fields["GOAL"]
        surfaces = override.get("SURFACE EXERCISED", fields.get("SURFACE EXERCISED", ""))
        topics = tuple(override.get("topics", self._topics(goal + " " + surfaces)))
        return Lesson(relative, level, path.stem[:2], identifier, title, goal, surfaces,
                      topics, hashlib.sha256(raw).hexdigest())

    def _title(self, level: str) -> str:
        """Return the owner-defined visible label for a validated level."""
        return self._TITLES[self._LEVELS.index(level)]

    @staticmethod
    def _link(origin: str, target: str, suffix: str = ".md") -> str:
        """Make a relative page/asset link using the emitted document's actual directory."""
        return os.path.relpath(target + suffix, str(PurePosixPath(origin).parent)).replace("\\", "/")

    def _cards(self, origin: str, lessons: list[Lesson]) -> str:
        """Create escaped static lesson cards; the optional browser filter only narrows this full list."""
        cards = ['<ul class="example-list">']
        for lesson in lessons:
            # Blank lines terminate a Markdown HTML block, even inside an
            # attribute. Search data is plain text and must remain one line.
            search = " ".join(" ".join((lesson.title, lesson.goal, lesson.surfaces, *lesson.topics)).split()).casefold()
            badges = "".join(f'<span class="example-topic">{html.escape(topic)}</span>' for topic in lesson.topics)
            link = self._link(origin, lesson.identifier, ".html")
            teaser = textwrap.shorten(" ".join(lesson.goal.split()), width=190, placeholder="…")
            cards.append(f'<li class="example-item" data-level="{lesson.level}" '
                         f'data-topics="{html.escape(json.dumps(lesson.topics), quote=True)}" '
                         f'data-search="{html.escape(search, quote=True)}">'
                         f'<span class="example-level">{self._title(lesson.level)} · {lesson.number}</span>'
                         f'<h3><a href="{link}">{html.escape(lesson.title)}</a></h3>'
                         f'<p>{html.escape(teaser)}</p><div>{badges}</div></li>')
        cards.append("</ul>")
        return "\n".join(cards)

    def _filters(self) -> str:
        """Render accessible filter controls; the complete list below works without this enhancement."""
        topics = sorted({topic for lesson in self.lessons for topic in lesson.topics})
        levels = ''.join(f'<option value="{level}">{self._title(level)}</option>' for level in self._LEVELS)
        options = ''.join(f'<option>{html.escape(topic)}</option>' for topic in topics)
        return ('<form class="example-filters" id="example-filters" role="search">'
                '<label>Find an example<input id="example-search" name="q" type="search" '
                'placeholder="Try cleanup, SpellMap, checkpoints…"></label>'
                f'<label>Level<select id="example-level" name="level"><option value="">All levels</option>{levels}</select></label>'
                f'<label>Topic<select id="example-topic" name="topic"><option value="">All topics</option>{options}</select></label>'
                '<button type="reset">Clear filters</button></form>'
                f'<p id="example-results" role="status" aria-live="polite">{len(self.lessons)} examples</p>')

    def _lesson_body(self, lesson: Lesson) -> str:
        """Render a complete source-backed lesson page without claiming that its assertions have run."""
        source_name = lesson.source.removeprefix("UX_and_AIX_experiences/")
        download = self._link(lesson.identifier, "downloads/" + source_name, "")
        guide = self._link(lesson.identifier, lesson.level + "/index")
        catalog = self._link(lesson.identifier, "examples/" + lesson.level + "/index")
        bundle = self._link(lesson.identifier, "downloads/" + lesson.level + "-examples.zip", "")
        source_url = str(self._configuration["repository_url"]).rstrip('/') + f"/blob/{self._revision}/{lesson.source}"
        paragraphs = "\n\n".join(" ".join(block.split()) for block in lesson.goal.split("\n\n") if block.strip())
        return (f"# {lesson.title}\n\n**{self._title(lesson.level)} · Lesson {lesson.number}**\n\n"
                f"{paragraphs}\n\n## Before you run\n\n"
                f"Use the [{lesson.level.title()} guide]({guide}) for prerequisite concepts. "
                "Run from a checkout with Melder installed and Python 3.14 free-threading selected. "
                "The collection download includes the level's local helper modules.\n\n"
                f"## Run the saved script\n\n```bash\npython {lesson.source}\n```\n\n"
                f"```powershell\npy -3.14t {lesson.source}\n```\n\n"
                f"{{download}}`Download this collection <{bundle}>` · [Source on GitHub]({source_url})\n\n"
                f"## Public surface\n\n{lesson.surfaces}\n\n"
                f"## Code\n\n```{{literalinclude}} {download}\n:language: python\n:linenos:\n```\n\n"
                f"## Check the outcome\n\nThe script contains its own assertions or demonstrated refusal paths. "
                "Run it to evaluate those checks against your installed version. "
                "The code above is taken directly from the saved file; no run output is invented here.\n\n"
                f"[More {lesson.level} examples]({catalog}) · [Level guide]({guide})\n")

    def _render(self) -> None:
        """Prepare generated pages and bodies as data before the shared builder writes any output."""
        for level in self._LEVELS:
            identifier = f"examples/{level}/index"
            lessons = [lesson for lesson in self.lessons if lesson.level == level]
            self.pages.append(Page(identifier, self._title(level) + " examples", "", "examples/index"))
            self.bodies[identifier] = (f"# {self._title(level)} examples\n\n"
                f"**{len(lessons)} saved lessons.** Follow their order or choose a topic that answers your question.\n\n"
                f"[Open the {level.title()} guide]({self._link(identifier, level+'/index')}) · "
                f"[All examples]({self._link(identifier, 'examples/index')})\n\n" + self._cards(identifier, lessons))
            for lesson in lessons:
                self.pages.append(Page(lesson.identifier, lesson.title, "", identifier))
                self.bodies[lesson.identifier] = self._lesson_body(lesson)
        self.bodies["examples/index"] = (f"\n\n## All {len(self.lessons)} saved examples\n\n"
            + self._filters() + "\n\n" + self._cards("examples/index", self.lessons))

    def write_assets(self, destination: Path) -> None:
        """Write selected lesson/helper sources, deterministic level bundles, and a source-fidelity index."""
        for level, directory in self.level_directories.items():
            target = destination / "downloads" / directory
            target.mkdir(parents=True, exist_ok=True)
            bundle = destination / "downloads" / (level + "-examples.zip")
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                prefix = f"UX_and_AIX_experiences/{directory}/"
                for source_name in sorted(name for name in self.source_bytes if name.startswith(prefix)):
                    (target / PurePosixPath(source_name).name).write_bytes(self.source_bytes[source_name])
                    info = zipfile.ZipInfo(source_name,
                                           date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, self.source_bytes[source_name])
        manifest = {"schema_version": 1, "source_revision": self._revision,
                    "lessons": [dataclasses.asdict(lesson) for lesson in self.lessons]}
        (destination / "catalog.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                                   encoding="utf-8", newline="\n")
