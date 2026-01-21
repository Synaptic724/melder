from __future__ import annotations

import pytest

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import (
    GraphConsistencyStrategy,
)


class _CancelStub:
    """
    Purpose:
        Provide a minimal cancellation event stub for strategy tests.
    Contract:
        - If is_set is True, throw_if_set raises the configured exception.
        - If is_set is False, throw_if_set is a no-op.
    Args:
        is_set: Whether cancellation is considered active.
        exc: Exception instance to raise when cancelled.
    """

    def __init__(self, *, is_set: bool = True, exc: Exception | None = None) -> None:
        """
        Purpose:
            Initialize the stub with a fixed cancellation state.
        Contract:
            Stores the provided state and exception for later use.
        Args:
            is_set: Whether cancellation is active.
            exc: Optional exception to raise; defaults to RuntimeError.
        Returns:
            None.
        """
        self._is_set = is_set
        self._exc = exc or RuntimeError("cancelled")

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Report whether cancellation is currently active.
        Contract:
            Returns the value provided at initialization.
        Returns:
            bool: True when cancellation is active.
        """
        return self._is_set

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise the configured exception when cancellation is active.
        Contract:
            Raises only when is_set is True.
        Raises:
            Exception: The configured cancellation exception.
        """
        if self.is_set:
            raise self._exc


def _node(spell_id: str, *, deps: set[str] | None = None) -> SpellSystemNode:
    """
    Purpose:
        Build a SpellSystemNode with a deterministic lineage id.
    Contract:
        Applies the provided dependency set as-is.
    Args:
        spell_id: Spell identifier for the node.
        deps: Optional dependency ids for the node.
    Returns:
        SpellSystemNode: The configured node instance.
    """
    return SpellSystemNode(
        spell_id=spell_id,
        lineage_id=f"lineage-{spell_id}",
        dependencies=deps or (),
    )


def _index(*nodes: SpellSystemNode) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex populated with provided nodes.
    Contract:
        Inserts nodes in order without additional mutation.
    Args:
        nodes: SpellSystemNode instances to upsert.
    Returns:
        SpellSystemIndex: The populated index.
    """
    idx = SpellSystemIndex()
    for node in nodes:
        idx.upsert_node(node)
    return idx


def _blueprint(
    *,
    root_id: str,
    node_ids: tuple[str, ...],
    edges: tuple[tuple[str, str], ...],
) -> dict[str, RootResolutionBlueprint]:
    """
    Purpose:
        Build a RootResolutionBlueprint with an explicit DAG shape.
    Contract:
        Adds nodes first, then wires dependency edges parent -> child.
    Args:
        root_id: Root id for the blueprint mapping.
        node_ids: Node ids to add to the DAG.
        edges: Parent/child edge tuples to wire into the DAG.
    Returns:
        dict[str, RootResolutionBlueprint]: Mapping containing the blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(node_id)
    for parent_id, child_id in edges:
        dag.add_dependency(parent_id, child_id)
    return {
        root_id: RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=f"lineage-{root_id}",
            dag=dag,
        )
    }


def test_matching_graph_produces_no_diagnostics() -> None:
    """
    Purpose:
        Verify matching blueprint and index edges produce no diagnostics.
    Contract:
        Leaves diagnostics empty for a consistent graph.
    Returns:
        None.
    Raises:
        AssertionError: If any diagnostics are emitted.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(("a", "b"),),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert diags == []


def test_missing_child_node_emits_missing_index_node() -> None:
    """
    Purpose:
        Ensure a blueprint node missing from the index is flagged.
    Contract:
        Emits a single missing_index_node diagnostic for the child.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing or incorrect.
    """
    idx = _index(_node("a"))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(("a", "b"),),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "missing_index_node"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id == "b"
    assert diag.root_id == "root"


def test_missing_parent_node_emits_missing_index_node() -> None:
    """
    Purpose:
        Verify a dependency parent absent from the index is reported.
    Contract:
        Emits missing_index_node diagnostics for the missing parent, including
        the parent as a standalone blueprint node.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic does not reference the parent.
    """
    idx = _index(_node("b", deps={"a"}))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(("a", "b"),),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 2
    assert {d.code for d in diags} == {"missing_index_node"}
    assert {d.severity for d in diags} == {SystemDiagnosticSeverity.ERROR}
    assert {d.spell_id for d in diags} == {"a"}
    assert {d.root_id for d in diags} == {"root"}


def test_edge_mismatch_index_emits_diagnostic_with_details() -> None:
    """
    Purpose:
        Validate mismatch diagnostics when a blueprint edge is absent in the index.
    Contract:
        Emits edge_mismatch_index with expected details.
    Returns:
        None.
    Raises:
        AssertionError: If details or metadata do not match.
    """
    idx = _index(_node("a"), _node("b", deps=set()))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(("a", "b"),),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "edge_mismatch_index"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id == "b"
    assert diag.root_id == "root"
    assert diag.details == {"parent_id": "a", "child_id": "b", "root_id": "root"}


def test_edge_missing_from_blueprint_emits_diagnostic() -> None:
    """
    Purpose:
        Ensure index edges absent from blueprints are reported.
    Contract:
        Emits edge_missing_from_blueprint with expected details.
    Returns:
        None.
    Raises:
        AssertionError: If the missing edge diagnostic is incorrect.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "edge_missing_from_blueprint"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id == "b"
    assert diag.root_id is None
    assert diag.details == {"parent_id": "a", "child_id": "b"}


def test_edge_missing_from_blueprint_with_empty_blueprints() -> None:
    """
    Purpose:
        Confirm missing edge checks still run when no blueprints are provided.
    Contract:
        Emits edge_missing_from_blueprint based solely on the index.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic is missing.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}))
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    assert diags[0].code == "edge_missing_from_blueprint"


def test_union_edges_across_blueprints_prevents_missing_edge() -> None:
    """
    Purpose:
        Ensure edge presence in any blueprint suppresses missing-edge diagnostics.
    Contract:
        Produces no diagnostics when at least one blueprint contains the edge.
    Returns:
        None.
    Raises:
        AssertionError: If a missing-edge diagnostic is emitted.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}))
    blueprints = {}
    blueprints.update(
        _blueprint(
            root_id="r1",
            node_ids=("a", "b"),
            edges=(("a", "b"),),
        )
    )
    blueprints.update(
        _blueprint(
            root_id="r2",
            node_ids=("a", "b"),
            edges=(),
        )
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert diags == []


def test_diagnostics_list_reused_appends_new() -> None:
    """
    Purpose:
        Verify diagnostics are appended rather than replacing existing entries.
    Contract:
        Preserves the original diagnostic and adds a new one.
    Returns:
        None.
    Raises:
        AssertionError: If the existing diagnostic is lost.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(),
    )
    existing = [SystemDiagnostic("pre", "keep")]

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=None,
    )

    assert existing[0].code == "pre"
    assert any(d.code == "edge_missing_from_blueprint" for d in existing)


def test_cancel_event_raises_before_processing() -> None:
    """
    Purpose:
        Confirm cancellation is honored before processing blueprints.
    Contract:
        Raises the cancellation exception without emitting diagnostics.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    idx = _index(_node("a"))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a",),
        edges=(),
    )
    diags: list[SystemDiagnostic] = []

    with pytest.raises(RuntimeError, match="cancelled"):
        GraphConsistencyStrategy().run(
            index=idx,
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_CancelStub(is_set=True),
        )

    assert diags == []


def test_multiple_edge_mismatches_emit_multiple_diagnostics() -> None:
    """
    Purpose:
        Ensure multiple mismatched edges each produce a diagnostic.
    Contract:
        Emits edge_mismatch_index for each mismatched edge.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic count is wrong.
    """
    idx = _index(_node("a"), _node("b", deps=set()), _node("c", deps=set()))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b", "c"),
        edges=(("a", "b"), ("a", "c")),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 2
    assert {d.code for d in diags} == {"edge_mismatch_index"}
    assert {d.spell_id for d in diags} == {"b", "c"}


def test_multiple_missing_edges_emit_multiple_diagnostics() -> None:
    """
    Purpose:
        Verify each missing index edge yields a diagnostic.
    Contract:
        Emits edge_missing_from_blueprint per missing edge.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are missing.
    """
    idx = _index(_node("a"), _node("b", deps={"a"}), _node("c", deps={"a"}))
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b", "c"),
        edges=(),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 2
    assert {d.code for d in diags} == {"edge_missing_from_blueprint"}
    assert {d.spell_id for d in diags} == {"b", "c"}


def test_index_nodes_without_dependencies_not_reported_when_blueprints_empty() -> None:
    """
    Purpose:
        Confirm nodes with no dependencies produce no diagnostics in isolation.
    Contract:
        Leaves diagnostics empty when only standalone nodes exist.
    Returns:
        None.
    Raises:
        AssertionError: If any diagnostics are emitted.
    """
    idx = _index(_node("solo"))
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert diags == []


def test_missing_index_nodes_across_blueprints_reported_per_root() -> None:
    """
    Purpose:
        Ensure missing nodes are reported for each root that references them.
    Contract:
        Emits missing_index_node diagnostics for each root-child pair.
    Returns:
        None.
    Raises:
        AssertionError: If root-specific diagnostics are absent.
    """
    idx = _index(_node("a"))
    blueprints = {}
    blueprints.update(
        _blueprint(
            root_id="r1",
            node_ids=("a", "b"),
            edges=(("a", "b"),),
        )
    )
    blueprints.update(
        _blueprint(
            root_id="r2",
            node_ids=("a", "c"),
            edges=(("a", "c"),),
        )
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 2
    pairs = {(d.spell_id, d.root_id) for d in diags}
    assert pairs == {("b", "r1"), ("c", "r2")}


def test_missing_index_nodes_reported_for_each_blueprint_node() -> None:
    """
    Purpose:
        Verify every blueprint node missing from the index yields a diagnostic.
    Contract:
        Emits missing_index_node for each missing node in the blueprint DAG.
    Returns:
        None.
    Raises:
        AssertionError: If a missing node is not reported.
    """
    idx = _index()
    blueprints = _blueprint(
        root_id="root",
        node_ids=("a", "b"),
        edges=(),
    )
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 2
    assert {d.code for d in diags} == {"missing_index_node"}
    assert {d.spell_id for d in diags} == {"a", "b"}


def test_edge_missing_from_blueprint_includes_non_index_parent() -> None:
    """
    Purpose:
        Ensure missing-edge diagnostics can reference parents absent from the index.
    Contract:
        Emits edge_missing_from_blueprint using the dependency id from the index node.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic does not include the parent id.
    """
    idx = _index(_node("b", deps={"ghost"}))
    diags: list[SystemDiagnostic] = []

    GraphConsistencyStrategy().run(
        index=idx,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )

    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "edge_missing_from_blueprint"
    assert diag.details == {"parent_id": "ghost", "child_id": "b"}
