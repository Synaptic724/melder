"""S5a: retire the Phase-5 per-path socket overlay - anchored source edits.

Usage: python apply_s5a_edits.py <tree_root> [--check]

spell_system_root_blueprint_builder.py: `_overlay_sockets_and_index(blueprint, topologies)` becomes
`_install_fresh_index(blueprint)` (fresh DagIndex and PathRegistry, no SocketRefs, no path walk); both entry points
stop reading `snapshot.topologies`; docstrings and comments follow; the unused SocketRef and SpellLocalTopology
imports go. root_resolution_blueprint.py: docstrings and one comment only. Each anchor must match exactly once or
nothing is written. Engine: ../s3_staging/apply_s3b1_edits.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

BUILDER = "src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py"
BLUEPRINT = "src/melder/aether/spellbook/spell_compiler/blueprints/root_resolution_blueprint.py"

IMPORT_OLD = """from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, SocketRef
"""
IMPORT_NEW = """from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex
"""

TC_OLD = """    from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
        SpellSystemAdjacencySnapshot,
    )
    from melder.aether.spellbook.spell_compiler.topology.spell_local_topology import (
        SpellLocalTopology,
    )
"""
TC_NEW = """    from melder.aether.spellbook.spell_compiler.system.spell_system_adjacency_snapshot import (
        SpellSystemAdjacencySnapshot,
    )
"""

CLASS_DOC_OLD = """        * This is *purely structural*:
              - node payloads are None,
              - param_name and socket_kind on edges are left unset (None).
          Socket metadata and DagIndex are overlaid in later Phase-5 steps.
"""
CLASS_DOC_NEW = """        * This is *purely structural*:
              - node payloads are None,
              - param_name and socket_kind on edges are left unset (None).
        * Each blueprint gets a fresh DagIndex and PathRegistry and records no
          SocketRefs. Phase 8 mints the root-relative path ids of its
          occurrences into that registry. Nothing here walks logical paths, so
          the cost follows spells and edges, never the number of paths (the
          per-path socket overlay that ran here had no reader that needed it
          and was retired on 2026-09-26).
"""

ROOTS_OLD = """
                socket_refs=None,              # Phase-5 socket overlay will populate
                dag_index=None,                # Phase-5 DagIndex builder will populate
            )

            topologies = snapshot.topologies
            if topologies is None:
                raise RuntimeError("Missing topologies in SpellSystemAdjacencySnapshot")
            self._overlay_sockets_and_index(
                blueprint=blueprint,
                topologies=topologies,
            )
"""
ROOTS_NEW = """
                socket_refs=None,              # compiled blueprints record no SocketRefs
                dag_index=None,                # _install_fresh_index installs it below
            )
            self._install_fresh_index(blueprint)
"""

SINGLE_DOC_OLD = """            - SocketRefs and DagIndex are overlaid from snapshot topologies.
"""
SINGLE_DOC_NEW = """            - The blueprint gets a fresh DagIndex and PathRegistry and records
              no SocketRefs; Phase 8 mints the path ids it needs.
"""

SINGLE_OLD = """
            socket_refs=None,              # Phase-5 socket overlay will populate
            dag_index=None,                # Phase-5 DagIndex builder will populate
        )

        topologies = snapshot.topologies
        if topologies is None:
            raise RuntimeError("Missing topologies in SpellSystemAdjacencySnapshot")
        self._overlay_sockets_and_index(
            blueprint=blueprint,
            topologies=topologies,
        )
"""
SINGLE_NEW = """
            socket_refs=None,              # compiled blueprints record no SocketRefs
            dag_index=None,                # _install_fresh_index installs it below
        )
        self._install_fresh_index(blueprint)
"""

OVERLAY_START = """    def _overlay_sockets_and_index(
"""
OVERLAY_NEW = '''    @staticmethod
    def _install_fresh_index(blueprint: RootResolutionBlueprint) -> None:
        """
        Give ``blueprint`` a fresh DagIndex and PathRegistry.

        Purpose:
            Phase 8 mints the root-relative path id of every occurrence into the
            blueprint's PathRegistry, so each compiled blueprint needs its own
            empty registry. Nothing else is recorded: compiled blueprints carry
            no SocketRefs.

        Contract:
            - Replaces the blueprint's index, so a reused blueprint never keeps
              stale path ids or socket entries.
            - Walks no paths and records no SocketRef; the cost is constant per
              blueprint. The per-path socket overlay that ran here until
              2026-09-26 visited every logical path below the root (exponential
              on shared diamonds) and no reader needed its output.

        Args:
            blueprint:
                Blueprint just built by this builder.

        Returns:
            None.

        Raises:
            RuntimeError: If ``blueprint`` was already cleaned.
        """
        blueprint.replace_dag_index(DagIndex())
'''

BP_CLASS_OLD = """    This blueprint is the handoff object between structural spell compilation
    and the later system/planning phases. It does not discover dependencies or
    validate policy by itself; instead, it packages the rooted DAG, stable
    execution order, and socket-targeting metadata that later components use
    for system validation, change-control/component-of wiring, and Phase 8-10
    planning/override targeting.
"""
BP_CLASS_NEW = """    This blueprint is the handoff object between structural spell compilation
    and the later system/planning phases. It does not discover dependencies or
    validate policy by itself; instead, it packages the rooted DAG, stable
    execution order, and the PathRegistry that Phase 8 mints root-relative path
    ids into, for system validation, change-control/component-of wiring, and
    Phase 8-10 planning. Compiled blueprints record no SocketRefs (the Phase-5
    per-path overlay was retired on 2026-09-26); the socket collection and its
    targeting index hold only refs a caller adds through `add_socket_ref`.
"""

BP_INIT_OLD = """        # Socket metadata (can be populated incrementally by Phase 5 builder).
"""
BP_INIT_NEW = """        # Socket metadata; Phase 5 records none, direct callers may add refs.
"""

BP_REFS_OLD = """        Return all socket references participating in this rooted DAG.

        Each socket ref carries the root-relative path information later used
        for override targeting, diagnostics, and patch-map construction. The
        returned list is a copy.
"""
BP_REFS_NEW = """        Return the socket references recorded on this blueprint.

        Compiled Phase-5 blueprints record none; the list holds only refs added
        through `add_socket_ref`. Each ref carries a root-relative path id from
        this blueprint's PathRegistry. The returned list is a copy.
"""

BP_REPLACE_OLD = """        Normally not needed - Phase 5 can just add sockets via this blueprint;
        provided for completeness / testing.
"""
BP_REPLACE_NEW = """        Phase 5 uses it to give each compiled blueprint a fresh index and
        PathRegistry; tests may use it too.
"""

EDITS = {
    BUILDER: [
        ("replace", IMPORT_OLD, IMPORT_NEW),
        ("replace", TC_OLD, TC_NEW),
        ("replace", CLASS_DOC_OLD, CLASS_DOC_NEW),
        ("replace", ROOTS_OLD, ROOTS_NEW),
        ("replace", SINGLE_DOC_OLD, SINGLE_DOC_NEW),
        ("replace", SINGLE_OLD, SINGLE_NEW),
        ("cut", OVERLAY_START, None),
        ("append", OVERLAY_NEW),
    ],
    BLUEPRINT: [
        ("replace", BP_CLASS_OLD, BP_CLASS_NEW),
        ("replace", BP_INIT_OLD, BP_INIT_NEW),
        ("replace", BP_REFS_OLD, BP_REFS_NEW),
        ("replace", BP_REPLACE_OLD, BP_REPLACE_NEW),
    ],
}


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit; `append` adds text after the file's last line in its line ending."""
    if edit[0] != "append":
        return _apply_one(data, edit, rel)
    nl = "\r\n" if data.endswith("\r\n") else "\n"
    return data + nl + edit[1].replace("\n", nl)


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
