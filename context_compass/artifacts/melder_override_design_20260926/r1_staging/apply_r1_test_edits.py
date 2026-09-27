"""R1 tests: follow the retirement of the targeting surface - anchored edits, function removals and deletions.

Usage: python apply_r1_test_edits.py <tree_root> [--check]

Test functions whose subject is the removed surface (SocketRef, DagIndex, DagTargetingEngine, SocketRefSanityStrategy,
the blueprint socket API, the phase-5 capture socket rows, `_install_fresh_index`) are removed by name through the
AST; tests that also asserted "no SocketRef" now assert only that no path is minted; the blueprint unit file is
rewritten for the PathRegistry-owning blueprint. DELETES lists files whose only subject is the removed surface (the
caller removes them). Each anchor must match exactly once or nothing is written. Engine: ../s3_staging/apply_s3b1_edits.py.
"""

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

U = "tests/unit/melder/spellbook/"
CC = "tests/component/melder/spellbook/spell_crafter/"
DELETES = [
    U + "spell_crafter/system/validation/test_socket_ref_sanity_strategy.py",
    U + "spell_crafter/dag/test_dag_index_and_targeting.py",
    "tests/unit/melder/aether/conduit/meld/overrides/test_spell_overrider.py",
    "tests/unit/melder/aether/conduit/meld/overrides/test_spell_overrider_deep.py",
    "tests/unit/melder/aether/conduit/meld/overrides/test_spell_overrider_matrix.py",
    CC + "dag/test_spellbook_component_dag_targeting.py",
    CC + "dag/test_spellbook_component_dag_index_builder.py",
]

BLUEPRINT_TESTS = '''import pytest

from typing import Optional, Sequence

from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)


def _path_id(registry: PathRegistry, path: Sequence[str]) -> int:
    """Mint `path` in `registry` and return its id."""
    current = registry.root_path_id
    for segment in path:
        current = registry.extend_path(current, segment)
    return current


def _make_blueprint(
    *,
    root_id: str = "root",
    lineage_id: str = "lineage",
    ordered: tuple[str, ...] = ("a", "b", "root"),
    path_registry: Optional[PathRegistry] = None,
) -> RootResolutionBlueprint:
    """Build a blueprint over a two-dependency DAG."""
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("root")
    dag.add_dependency("a", "root")
    dag.add_dependency("b", "root")
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=lineage_id,
        dag=dag,
        ordered_node_ids=ordered,
        path_registry=path_registry,
    )


def test_init_requires_root_id_and_dag() -> None:
    """A blueprint needs a root id and a DAG."""
    with pytest.raises(ValueError):
        RootResolutionBlueprint(None, "lineage", DirectedAcyclicWorkGraph())
    with pytest.raises(ValueError):
        RootResolutionBlueprint("root", "lineage", None)


def test_properties_return_metadata_and_the_supplied_registry() -> None:
    """Accessors return the constructor's values; a supplied PathRegistry is owned as given."""
    registry = PathRegistry()
    path_id = _path_id(registry, ("p",))
    bp = _make_blueprint(path_registry=registry)
    assert bp.root_spell_id == "root"
    assert bp.root_lineage_id == "lineage"
    assert bp.dag is not None
    assert bp.ordered_node_ids == ["a", "b", "root"]
    assert bp.path_registry is registry
    assert bp.path_registry.resolve_path_id(("p",)) == path_id


def test_defaults_create_a_fresh_registry_per_blueprint() -> None:
    """Without a registry each blueprint owns its own, holding only the root path."""
    first = _make_blueprint()
    second = _make_blueprint()
    assert first.path_registry is not second.path_registry
    assert first.path_registry.resolve_path_id(()) == first.path_registry.root_path_id
    assert first.path_registry.resolve_path_id(("p",)) is None


def test_cleanup_idempotent_and_cleans_owned_children() -> None:
    """Cleanup is idempotent and cleans the DAG and the PathRegistry it owns."""
    bp = _make_blueprint()
    dag = bp.dag
    registry = bp.path_registry
    bp.cleanup()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.root_spell_id
    assert dag.cleaned is True
    assert registry.cleaned is True


def test_accessors_raise_after_cleanup() -> None:
    """Every accessor refuses a cleaned blueprint."""
    bp = _make_blueprint()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.dag
    with pytest.raises(RuntimeError):
        _ = bp.ordered_node_ids
    with pytest.raises(RuntimeError):
        _ = bp.path_registry


def test_ordered_node_ids_returns_copy() -> None:
    """Mutating the returned order does not change the blueprint."""
    bp = _make_blueprint()
    ids = bp.ordered_node_ids
    ids.append("mutate")
    assert bp.ordered_node_ids == ["a", "b", "root"]
'''

SVS = CC + "system/validation/test_spellbook_component_system_validation_system.py"
SVS_HELPER_OLD = '''def _build_blueprint(
    *,
    root_id: str,
    dependency_id: str,
    add_socket: bool = True,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a simple root blueprint with one dependency edge.
    Contract:
        - DAG contains root and dependency nodes.
        - Edge is dependency -> root.
        - Socket refs are populated when add_socket is True.
    Args:
        root_id: Root spell id.
        dependency_id: Dependency spell id.
        add_socket: Whether to add a socket ref for the dependency edge.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
'''
SVS_HELPER_NEW = '''def _build_blueprint(
    *,
    root_id: str,
    dependency_id: str,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a simple root blueprint with one dependency edge.
    Contract:
        - DAG contains root and dependency nodes.
        - Edge is dependency -> root.
    Args:
        root_id: Root spell id.
        dependency_id: Dependency spell id.
    Returns:
        RootResolutionBlueprint: The constructed blueprint.
    """
'''
SVS_BODY_OLD = '''    if add_socket:
        blueprint.ensure_dag_index_built()
        path_registry = blueprint.path_registry
        path_id = path_registry.extend_path(path_registry.root_path_id, "dependency")
        socket = SocketRef(
            node_id=root_id,
            param_name="dependency",
            param_path_id=path_id,
            socket_kind=SocketKind.NORMAL,
        )
        blueprint.add_socket_ref(socket)
    return blueprint
'''
SVS_BODY_NEW = '''    return blueprint
'''
SANITY_IMPORT = '''from melder.aether.spellbook.spell_compiler.system.validation.socket_ref_sanity_strategy import (
    SocketRefSanityStrategy,
)
'''

NO_REFS_LINE_8 = "        assert blueprint.socket_refs == []\n"
DOC_SUBS = [
    ("- No SocketRef is recorded and no path is minted (Phase 8 mints paths).",
     "- No path is minted here (Phase 8 mints paths)."),
    ("- No SocketRef is recorded (Phase 8 mints the paths).", "- No path is minted here (Phase 8 mints the paths)."),
    ("- No SocketRef is recorded (Phase 8 mints the deep paths).",
     "- No path is minted here (Phase 8 mints the deep paths)."),
    ("- No SocketRef is recorded (Phase 8 mints one path per branch).",
     "- No path is minted here (Phase 8 mints one path per branch)."),
    ("        - No SocketRef is recorded.\n", "        - No path is minted here.\n"),
    ("- Topology sockets are not copied into SocketRefs and mint no path.", "- Topology sockets mint no path here."),
    ("or socket refs appear.", "or a path is minted."),
    ("If socket refs are recorded or the DAG grows.", "If a path is minted or the DAG grows."),
    ("If socket refs are recorded or the DAG is incomplete.", "If a path is minted or the DAG is incomplete."),
]

UNIT_BUILDER = U + "spell_crafter/system/test_spell_system_root_blueprint_builder.py"
UB_OLD = '''    """Phase 5 keeps the dependency DAG but records no SocketRef and mints no path, whatever the topologies hold."""
'''
UB_NEW = '''    """Phase 5 keeps the dependency DAG and mints no path, whatever the topologies hold."""
'''
UB_BODY_OLD = '''    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]
    blueprint.ensure_dag_index_built()

    assert set(blueprint.dag.nodes) == {"root", "child", "leaf"}
    assert blueprint.socket_refs == []
    assert list(blueprint.dag_index.iter_all_sockets()) == []
    assert blueprint.path_registry.resolve_path_id(("child",)) is None
'''
UB_BODY_NEW = '''    blueprint = SpellSystemRootBlueprintBuilder().build_root_blueprints(snapshot)["root"]

    assert set(blueprint.dag.nodes) == {"root", "child", "leaf"}
    assert blueprint.path_registry.resolve_path_id(("child",)) is None
'''
UB_EMPTY_OLD = '''    assert bp.dag_index.get_by_name("child") == []
'''
UB_EMPTY_NEW = '''    assert set(bp.dag.nodes) == {"root", "child"}
'''

EDITS = {
    U + "spell_crafter/dag/test_dag_index.py": [
        ("defs", "ALLDAG"),
        ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, PathRegistry, SocketRef\n",
         "from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry\n"),
    ],
    U + "spell_crafter/blueprints/test_root_resolution_blueprint.py": [("write", BLUEPRINT_TESTS)],
    CC + "dag/test_spellbook_component_dag_index_and_spec.py": [
        ("defs", ["test_component_dag_index_collects_and_queries_sockets",
                  "test_component_dag_index_iter_all_sockets_dedupes_duplicates",
                  "test_component_dag_targeting_unique_raises_on_multiple_matches",
                  "test_component_dag_targeting_broadcast_raises_on_no_matches",
                  "test_component_dag_targeting_rejects_empty_path_spec",
                  "test_component_dag_index_cleanup_blocks_future_usage",
                  "test_component_dag_targeting_engine_cleanup_cleans_index"]),
        ("replace", '''from melder.aether.spellbook.spell_compiler.dag.dag_index import (
    DagIndex,
    DagTargetingEngine,
    PathRegistry,
    SocketRef,
)
''', ""),
    ],
    SVS: [
        ("defs", ["test_component_system_validation_socket_ref_index_missing_entries",
                  "test_component_system_validation_detects_orphan_dag_index_socket"]),
        ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, SocketRef\n", ""),
        ("replace", SANITY_IMPORT, ""),
        ("replace", SVS_HELPER_OLD, SVS_HELPER_NEW),
        ("replace", SVS_BODY_OLD, SVS_BODY_NEW),
        ("replace", "            RootViabilityStrategy(),\n            SocketRefSanityStrategy(),\n        ]\n",
         "            RootViabilityStrategy(),\n        ]\n"),
    ],
    CC + "system/validation/test_spellbook_component_system_validation_strategies_expanded.py": [
        ("defs", ["_make_socket_ref", "test_component_socket_ref_sanity_no_issues_for_valid_index",
                  "test_component_socket_ref_sanity_reports_duplicate_socket_ref",
                  "test_component_socket_ref_sanity_reports_missing_index_entries",
                  "test_component_socket_ref_sanity_reports_orphan_index_socket",
                  "test_component_socket_ref_sanity_scopes_diagnostics_to_root"]),
        ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, PathRegistry, SocketRef\n",
         "from melder.aether.spellbook.spell_compiler.dag.dag_index import PathRegistry\n"),
        ("replace", SANITY_IMPORT, ""),
    ],
    CC + "system/test_spellbook_component_spell_system.py": [
        ("defs", ["test_component_spell_system_validation_reports_socket_ref_duplicate",
                  "test_component_spell_system_validation_reports_orphan_socket_ref"]),
        ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import SocketRef\n", ""),
        ("replace", SANITY_IMPORT, ""),
        ("replace", NO_REFS_LINE_8, ""),
        ("subs", DOC_SUBS),
    ],
    "tests/integration/melder/spellbook/test_spellbook_integration_validation_system.py": [
        ("defs", ["test_spell_validation_phase6_reports_socket_ref_index_mismatch",
                  "test_spell_validation_phase6_reports_socket_ref_duplicate",
                  "test_spell_validation_phase6_reports_orphan_dag_index_socket"]),
        ("replace", "from melder.aether.spellbook.spell_compiler.dag.dag_index import DagIndex, SocketRef\n", ""),
    ],
    U + "spell_compiler/phases/test_shared_compiler_executions.py": [
        ("defs", ["test_build_phase5_socket_rows_returns_sorted_socket_schema_rows"]),
    ],
    UNIT_BUILDER: [
        ("defs", ["test_blueprint_without_topologies_has_empty_index",
                  "test_install_fresh_index_rejects_none_and_cleaned_blueprints",
                  "test_blueprint_without_topologies_records_no_socket_refs",
                  "test_install_fresh_index_replaces_index_and_registry"]),
        ("replace", UB_OLD, UB_NEW),
        ("replace", UB_BODY_OLD, UB_BODY_NEW),
        ("replace", "    assert bp.socket_refs == []\n    assert bp.path_registry.resolve_path_id",
         "    assert bp.path_registry.resolve_path_id"),
        ("replace", "    assert set(bp.dag.nodes.keys()) == {\"root\", \"mid\", \"leaf\"}\n    assert bp.socket_refs == []\n",
         "    assert set(bp.dag.nodes.keys()) == {\"root\", \"mid\", \"leaf\"}\n"),
        ("replace", UB_EMPTY_OLD, UB_EMPTY_NEW),
        ("replace", "def test_compiled_blueprint_records_no_socket_refs_or_paths():\n",
         "def test_compiled_blueprint_mints_no_paths():\n"),
    ],
    CC + "system/test_spellbook_component_spell_system_root_blueprint_builder.py": [
        ("replace", "        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}\n        assert blueprint.socket_refs == []\n"
                    "        assert blueprint.path_registry.resolve_path_id((\"mid\",)) is None\n",
         "        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}\n"
         "        assert blueprint.path_registry.resolve_path_id((\"mid\",)) is None\n"),
        ("replace", "        assert blueprint.socket_refs == []\n        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}\n",
         "        assert blueprint.path_registry.resolve_path_id((\"mid\",)) is None\n"
         "        assert set(blueprint.dag.nodes) == {root_id, mid_id, leaf_id}\n"),
        ("replace", "        assert set(blueprint.dag.nodes) == {root_id}\n        assert blueprint.socket_refs == []\n",
         "        assert set(blueprint.dag.nodes) == {root_id}\n"
         "        assert blueprint.path_registry.resolve_path_id((\"config\",)) is None\n"),
        ("subs", DOC_SUBS),
    ],
    CC + "system/test_spellbook_component_spell_system_adjacency_snapshot.py": [
        ("replace", NO_REFS_LINE_8, ""),
        ("subs", DOC_SUBS),
    ],
    CC + "system/test_spellbook_component_spell_system_phase5_contracts.py": [
        ("replace", NO_REFS_LINE_8, ""),
        ("subs", DOC_SUBS),
    ],
    CC + "phases/test_spellbook_component_spell_crafter_phase5.py": [
        ("replace", NO_REFS_LINE_8, ""),
        ("subs", DOC_SUBS),
    ],
    "tests/component/melder/aether/conduit/test_conduit_component_meld_overrides.py": [
        ("replace", "    assert ordered_ids[-1] == service_id\n\n    assert blueprint.socket_refs == []\n",
         "    assert ordered_ids[-1] == service_id\n\n    assert blueprint.path_registry.resolve_path_id((\"repo\",)) is None\n"),
        ("replace", "    assert blueprint.socket_refs == []\n",
         "    assert blueprint.path_registry.resolve_path_id((\"service_a\",)) is None\n"),
        ("subs", DOC_SUBS),
    ],
    "tests/component/melder/spellbook/test_spellbook_component_override_required.py": [
        ("replace", "            assert artifact._root_blueprint_phase5.socket_refs == []\n", ""),
    ],
    "tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py": [
        ("replace", '        path_registry=path_registry,\n        socket_refs=[\n            SimpleNamespace(\n'
                    '                node_id="spell-1",\n                param_name="svc",\n                param_path_id=7,\n'
                    '                socket_kind=SocketKind.NORMAL,\n            )\n        ],\n    )\n',
         '        path_registry=path_registry,\n    )\n'),
        ("replace", "    signature is the hash of the five key parts.\n", "    signature is the hash of the four key parts.\n"),
        ("replace", '        id(path_registry),\n        (("spell-1", "svc", 7, SocketKind.NORMAL.value),),\n        expected_digest,\n',
         '        id(path_registry),\n        expected_digest,\n'),
        ("replace", "    assert keys[0][:4] == keys[1][:4]\n    assert keys[0][4] != keys[1][4]\n",
         "    assert keys[0][:3] == keys[1][:3]\n    assert keys[0][3] != keys[1][3]\n"),
    ],
    "tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py": [
        ("replace", "        socket_refs=(),\n", ""),
        ("replace", "        ensure_dag_index_built=lambda: None,\n", ""),
    ],
    "tests/component/melder/aether/conduit/test_conduit_component_meld_overrides_deep.py": [
        ("replace", "These tests exercise SpellOverrider through Conduit.meld to validate\n"
                    "deep path targeting, wildcard rules, precedence, and error handling.\n",
         "These tests exercise override key-set plans through Conduit.meld to\n"
         "validate deep path targeting, wildcard rules, precedence, and error handling.\n"),
    ],
}


def _remove_defs(data: str, names: object, rel: str) -> str:
    """Remove top-level functions by name (or every one naming DagIndex/SocketRef when names is 'ALLDAG')."""
    tree = ast.parse(data)
    lines = data.splitlines(keepends=True)
    drop = set()
    found = set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue
        body = "".join(lines[node.lineno - 1:node.end_lineno])
        hit = re.search("DagIndex|SocketRef", body) if names == "ALLDAG" else node.name in names
        if hit:
            found.add(node.name)
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            drop.update(range(start - 1, node.end_lineno))
    if names != "ALLDAG" and found != set(names):
        raise SystemExit(f"{rel}: functions not found: {sorted(set(names) - found)}")
    kept = [line for index, line in enumerate(lines) if index not in drop]
    text = "".join(kept)
    nl = "\r\n" if "\r\n" in text else "\n"
    blank4 = nl * 4
    while blank4 in text:
        text = text.replace(blank4, nl * 3)
    return text


def _unused_names(data: str) -> dict:
    """Map each top-level imported name and private helper that no Name node reads to its AST node."""
    tree = ast.parse(data)
    candidates = {}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                candidates[(alias.asname or alias.name).split(".")[0]] = node
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name.startswith("_"):
            candidates[node.name] = node
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    return {name: node for name, node in candidates.items() if name not in used and name != "annotations"}


def _prune_orphans(original: str, data: str, rel: str) -> str:
    """Remove imports and private helpers that the edits above left unused (used in the original).

    Names already unused in the original are left alone (no drive-by clean-up). An import statement is removed
    only when every name it binds is orphaned; a partly orphaned statement stops the script for a hand edit.
    Runs to a fixed point, since removing a helper can orphan the imports only it used.
    """
    before = set(_unused_names(original))
    while True:
        orphans = {k: v for k, v in _unused_names(data).items() if k not in before}
        if not orphans:
            return data
        lines = data.splitlines(keepends=True)
        drop = set()
        for name, node in orphans.items():
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                bound = {(a.asname or a.name).split(".")[0] for a in node.names}
                if not bound <= set(orphans):
                    raise SystemExit(f"{rel}: import at line {node.lineno} is partly orphaned ({name}); edit by hand")
                drop.update(range(node.lineno - 1, node.end_lineno))
            else:
                start = min([d.lineno for d in node.decorator_list] + [node.lineno])
                drop.update(range(start - 1, node.end_lineno))
        text = "".join(line for index, line in enumerate(lines) if index not in drop)
        nl = "\r\n" if "\r\n" in text else "\n"
        while nl * 4 in text:
            text = text.replace(nl * 4, nl * 3)
        print(f"{rel}: pruned orphans {sorted(orphans)}")
        data = text


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit of any kind."""
    kind = edit[0]
    if kind == "defs":
        return _remove_defs(data, edit[1], rel)
    if kind == "write":
        return edit[1]
    if kind == "subs":
        for old, new in edit[1]:
            for variant_old, variant_new in ((old.replace("\n", "\r\n"), new.replace("\n", "\r\n")), (old, new)):
                data = data.replace(variant_old, variant_new)
        return data
    return _apply_one(data, edit, rel)


def main() -> None:
    """Check every anchor and every file to delete, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    for rel in DELETES:
        if not (root / rel).is_file():
            raise SystemExit(f"missing file to delete: {rel}")
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        original = path.read_bytes().decode("utf-8")
        data = original
        for edit in edits:
            data = _apply(data, edit, rel)
        data = _prune_orphans(original, data, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))
    for rel in DELETES:
        print("to delete: " + rel)


if __name__ == "__main__":
    main()
