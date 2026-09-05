"""Reconcile the public export registry and prepare source-driven Sphinx references.

Discovery parses the package facade without importing Melder. Autodoc owns later
signature and docstring rendering; this layer selects objects and reader routes.
"""

import ast
import json
import os
import re
import tomllib
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from site_model import Page

if TYPE_CHECKING:
    from example_catalog import ExampleCatalog


class ApiReference:
    """Select every declared export exactly once and add explicit returned-object references."""

    def __init__(self, root: Path, configuration: Path, revision: str) -> None:
        """Read immutable build inputs and validate the complete selection before publishing pages."""
        self.root = root.resolve()
        self.revision = revision
        self.pages: list[Page] = []
        self.bodies: dict[str, str] = {}
        self.inventory: list[dict[str, str]] = []
        self.targets: dict[str, str] = {}
        payload = tomllib.loads(configuration.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1:
            raise ValueError("api.toml requires schema_version = 1.")
        exports, self.imports = self._exports()
        groups = payload["group"]
        selected = [name for group in groups for name in group["exports"]]
        if len(set(selected)) != len(selected) or set(selected) != set(exports):
            raise ValueError(f"Public API selection drift: missing={sorted(set(exports)-set(selected))}; "
                             f"unexpected={sorted(set(selected)-set(exports))}; check duplicates.")
        group_ids = [group["id"] for group in groups]
        if len(set(group_ids)) != len(group_ids):
            raise ValueError("API group IDs must be unique.")
        for group in groups:
            self._group(group, set(payload["functions"]))
        for returned in payload.get("returned", []):
            if returned["group"] not in group_ids:
                raise ValueError(f"Unknown API group for returned surface: {returned['name']}")
            self._object(returned["name"], returned["target"], returned["group"],
                         "autoclass", returned["via"], "returned")
        self._index(groups)

    def _exports(self) -> tuple[list[str], dict[str, str]]:
        """Read the literal public export list and concrete import origins without booting the package."""
        tree = ast.parse((self.root / "src/melder/__init__.py").read_text(encoding="utf-8"))
        exports: list[str] = []
        imports: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.module + "." + alias.name
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
            ):
                exports = ast.literal_eval(node.value)
        if not exports or not all(isinstance(name, str) for name in exports):
            raise ValueError("The public facade must declare a nonempty literal __all__ list.")
        return exports, imports

    @staticmethod
    def _link(origin: str, target: str) -> str:
        """Return a portable relative document link from one emitted reference page."""
        return os.path.relpath(target + ".md", str(PurePosixPath(origin).parent)).replace("\\", "/")

    def _group(self, group: dict, functions: set[str]) -> None:
        """Create a topical entry and give each root export one documented disposition."""
        identifier = "reference/api/" + group["id"]
        self.pages.append(Page(identifier, group["title"], "", "reference/api"))
        body = f"# {group['title']}\n\n[Read the guide]({self._link(identifier, group['guide'])}).\n\n"
        if group.get("kind") == "values":
            body += ("These values belong to the installed package. Metadata identifies that package; "
                     "the four document objects expose its shipped documentation.\n\n")
        for name in group["exports"]:
            if name not in self.imports:
                raise ValueError(f"Public export has no concrete import origin: {name}")
            if group.get("kind") == "values":
                body += f"- `melder.{name}`\n"
                self.inventory.append({"name": name, "target": self.imports[name],
                                       "disposition": "documented value", "page": identifier})
                continue
            directive = "autofunction" if name in functions else "autoclass"
            self._object(name, "melder." + name, group["id"], directive,
                         "import melder as md", "export")
        self.bodies[identifier] = body

    def _object(self, name: str, target: str, group: str, directive: str,
                via: str, kind: str) -> None:
        """Select one reference object and require its concrete source module to exist."""
        origin = self.imports[name] if kind == "export" else target
        module = origin.rsplit(".", 1)[0]
        source = Path("src", *module.split(".")).with_suffix(".py")
        canonical = (self.root / source).resolve()
        if (not module.startswith("melder.") or not canonical.is_relative_to(self.root / "src/melder")
                or not canonical.is_file()):
            raise ValueError(f"Missing API source for {target}: {source}")
        slug = re.sub(r"[^a-z0-9-]", "-", name.lower()).strip("-")
        identifier = f"reference/api/{group}/{slug}"
        if identifier in self.bodies or target in self.targets:
            raise ValueError(f"Duplicate API object or page: {target}")
        self.targets[target] = identifier
        self.pages.append(Page(identifier, name, "", "reference/api/" + group))
        source_url = "https://github.com/Synaptic724/melder/blob/" + self.revision + "/" + source.as_posix()
        entry = (f"Use `md.{name}` from the public package namespace." if kind == "export" else
                 f"Receive this surface through **{via}**; use that owning object's public entry point.")
        options = "   :members:\n   :member-order: bysource\n" if directive == "autoclass" else ""
        self.bodies[identifier] = (
            f"# {name}\n\n{entry}\n\n[Implementation source]({source_url})\n\n"
            f"```{{eval-rst}}\n.. {directive}:: {origin}\n{options}```\n\n"
            f"[Topic reference]({self._link(identifier, 'reference/api/'+group)}) · "
            f"[Full contents]({self._link(identifier, 'contents')})\n"
        )
        self.inventory.append({"name": name, "target": target, "origin": origin,
                               "disposition": "documented " + kind, "page": identifier})

    def _index(self, groups: list[dict]) -> None:
        """Connect topical reference entries and their object pages without a second toctree graph."""
        introduction = (self.root / "docs/reference/api.md").resolve()
        if not introduction.is_relative_to(self.root / "docs"):
            raise ValueError("The API introduction must remain within authored docs.")
        self.bodies["reference/api"] = introduction.read_text(encoding="utf-8")
        for group in groups:
            identifier = "reference/api/" + group["id"]
            self.bodies["reference/api"] += (
                f"\n- [{group['title']}]({self._link('reference/api', identifier)})\n"
            )
            children = [page for page in self.pages if page.parent == identifier]
            if children:
                self.bodies[identifier] += "\n## Objects\n\n" + "\n".join(
                    f"- [{page.title}]({self._link(identifier, page.identifier)})" for page in children
                ) + "\n"
        self.bodies["reference/api"] += (
            "\n\nThe inventory reconciles every package export and identifies additional returned surfaces. "
            "Contracts below are rendered from their Python docstrings.\n\n"
            "{download}`Download the API inventory <../downloads/api-inventory.json>`\n"
        )

    def connect_examples(self, catalog: ExampleCatalog) -> None:
        """Link names explicitly mentioned by lesson headers to their selected API contracts.

        This is a navigation association, not a claim of behavioral verification.
        Match complete names so Spell does not also match Spellbook or SpellSpace.
        """
        exported = [entry for entry in self.inventory if entry["disposition"] == "documented export"]
        for lesson in catalog.lessons:
            selected = [entry for entry in exported
                        if re.search(r"\b" + re.escape(entry["name"]) + r"\b", lesson.surfaces)]
            if selected:
                links = "\n".join(
                    f"- [{entry['name']}]({self._link(lesson.identifier, entry['page'])})"
                    for entry in selected
                )
                catalog.bodies[lesson.identifier] += "\n## API contracts\n\n" + links + "\n"

    def write_assets(self, destination: Path) -> None:
        """Write the explicit public selection as plain JSON beside the existing downloads."""
        downloads = destination / "downloads"
        downloads.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": 1, "source_revision": self.revision, "objects": self.inventory}
        (downloads / "api-inventory.json").write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
