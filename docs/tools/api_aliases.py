"""Preserve real public facade aliases while Sphinx renders canonical source-module objects."""

import json
from typing import TYPE_CHECKING, cast

from sphinx.domains.python import PythonDomain

if TYPE_CHECKING:
    from docutils.nodes import document
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


class PublicApiAliases:
    """Own one build's value-only alias map; the Python domain owns its object inventory."""

    def __init__(self) -> None:
        """Start with no aliases; handbook builds intentionally contain no API reference pages."""
        self.aliases: dict[str, str] = {}

    def load(self, app: Sphinx) -> None:
        """Read the explicitly generated public inventory, refusing a missing full-site input."""
        if not (app.srcdir / "reference/api.md").is_file():
            return
        inventory = app.srcdir / "downloads/api-inventory.json"
        data = json.loads(inventory.read_text(encoding="utf-8"))
        self.aliases = {entry["origin"]: entry["target"] for entry in data["objects"]
                        if entry["disposition"] == "documented export"}

    def register(self, app: Sphinx, tree: document) -> None:
        """Register true facade aliases for the current document and its documented members.

        Snapshot the external domain inventory because registration mutates it.
        Source descriptions remain at canonical modules, avoiding viewcode's
        single-prefix-per-module ambiguity when facade and returned types coexist.
        """
        domain = cast(PythonDomain, app.env.get_domain("py"))
        for canonical, entry in list(domain.objects.items()):
            if entry.docname != app.env.current_document.docname or entry.aliased:
                continue
            for origin, alias in self.aliases.items():
                if canonical == origin or canonical.startswith(origin + "."):
                    name = alias + canonical[len(origin):]
                    if name != canonical and name not in domain.objects:
                        domain.note_object(name, entry.objtype, entry.node_id, aliased=True)

    def verify(self, app: Sphinx, environment: BuildEnvironment) -> None:
        """Fail the build when a declared public alias has no real documented object target."""
        domain = cast(PythonDomain, environment.get_domain("py"))
        missing = sorted(set(self.aliases.values()) - set(domain.objects))
        if missing:
            raise ValueError(f"Unresolved public API aliases: {missing}")


def setup(app: Sphinx) -> dict[str, object]:
    """Attach the alias adapter to Sphinx's native object-inventory lifecycle."""
    aliases = PublicApiAliases()
    app.connect("builder-inited", aliases.load)
    app.connect("doctree-read", aliases.register)
    app.connect("env-updated", aliases.verify)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
