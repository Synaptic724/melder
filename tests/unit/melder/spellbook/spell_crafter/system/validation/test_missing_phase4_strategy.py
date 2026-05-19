from __future__ import annotations

import pytest

from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.missing_phase4_strategy import (
    MissingPhase4Strategy,
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


class _ToggleCancel:
    """
    Purpose:
        Toggle cancellation state after the first is_set check.
    Contract:
        Raises once a second check is performed.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize the toggle state.
        Contract:
            Starts with cancellation disabled for the first check.
        Returns:
            None.
        """
        self._checks = 0

    @property
    def is_set(self) -> bool:
        """
        Purpose:
            Toggle to cancelled on the second check.
        Contract:
            Returns False on first check, True thereafter.
        Returns:
            bool: True once cancellation should be honored.
        """
        self._checks += 1
        return self._checks > 1

    def throw_if_set(self) -> None:
        """
        Purpose:
            Raise once cancellation has been toggled on.
        Contract:
            Raises RuntimeError when cancellation is active.
        Raises:
            RuntimeError: When cancellation has been toggled on.
        """
        if self._checks > 1:
            raise RuntimeError("cancelled")


def _node(spell_id: str) -> SpellSystemNode:
    """
    Purpose:
        Build a SpellSystemNode with a deterministic lineage id.
    Contract:
        Uses the provided spell_id for both identity and lineage naming.
    Args:
        spell_id: Spell identifier for the node.
    Returns:
        SpellSystemNode: The configured node instance.
    """
    return SpellSystemNode(
        spell_id=spell_id,
        lineage_id=f"lineage-{spell_id}",
    )


def _index(*spell_ids: str) -> SpellSystemIndex:
    """
    Purpose:
        Build a SpellSystemIndex populated with nodes for the provided ids.
    Contract:
        Inserts nodes in order without additional mutation.
    Args:
        spell_ids: Spell ids to insert into the index.
    Returns:
        SpellSystemIndex: The populated index.
    """
    idx = SpellSystemIndex()
    for spell_id in spell_ids:
        idx.upsert_node(_node(spell_id))
    return idx


def _blueprint(*, root_id: str, node_ids: tuple[str, ...]) -> dict[str, RootResolutionBlueprint]:
    """
    Purpose:
        Build a RootResolutionBlueprint with the provided node ids.
    Contract:
        Adds nodes without dependencies; order reflects insertion order.
    Args:
        root_id: Root id for the blueprint mapping.
        node_ids: Node ids to add to the DAG.
    Returns:
        dict[str, RootResolutionBlueprint]: Mapping containing the blueprint.
    """
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(node_id)
    return {
        root_id: RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=f"lineage-{root_id}",
            dag=dag,
        )
    }


def test_no_blueprints_produces_no_diagnostics() -> None:
    """
    Purpose:
        Ensure empty blueprints yield no diagnostics.
    Contract:
        Leaves diagnostics empty when no roots are provided.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index(),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_all_nodes_have_phase4_results() -> None:
    """
    Purpose:
        Verify no diagnostics when every node has a Phase-4 result.
    Contract:
        Leaves diagnostics empty for a complete Phase-4 result set.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a", "b"))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={"a": object(), "b": object()},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_missing_single_node_emits_diagnostic() -> None:
    """
    Purpose:
        Ensure a missing Phase-4 result produces one diagnostic.
    Contract:
        Emits missing_phase4_validation for the missing node.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic fields are incorrect.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a", "b"))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={"a": object()},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    diag = diags[0]
    assert diag.code == "missing_phase4_validation"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id == "b"
    assert diag.root_id == "root"
    assert "Phase-4" in diag.message


def test_missing_multiple_nodes_emits_multiple_diagnostics() -> None:
    """
    Purpose:
        Verify each missing node emits a diagnostic.
    Contract:
        Emits missing_phase4_validation for each node without results.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics do not match missing nodes.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a", "b"))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 2
    assert {d.spell_id for d in diags} == {"a", "b"}
    assert {d.code for d in diags} == {"missing_phase4_validation"}


def test_missing_across_multiple_roots_emits_per_root() -> None:
    """
    Purpose:
        Ensure diagnostics include root_id for each affected root.
    Contract:
        Emits a diagnostic per missing node per root.
    Returns:
        None.
    Raises:
        AssertionError: If root-specific diagnostics are missing.
    """
    blueprints: dict[str, RootResolutionBlueprint] = {}
    blueprints.update(_blueprint(root_id="r1", node_ids=("a", "b")))
    blueprints.update(_blueprint(root_id="r2", node_ids=("b", "c")))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b", "c"),
        blueprints=blueprints,
        phase4_results={"a": object()},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert {(d.spell_id, d.root_id) for d in diags} == {
        ("b", "r1"),
        ("b", "r2"),
        ("c", "r2"),
    }


def test_diagnostics_list_reused_appends_new_entries() -> None:
    """
    Purpose:
        Confirm diagnostics are appended rather than replaced.
    Contract:
        Preserves existing diagnostics and adds new ones.
    Returns:
        None.
    Raises:
        AssertionError: If existing diagnostics are lost.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    existing = [SystemDiagnostic("pre", "keep")]
    MissingPhase4Strategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=None,
    )
    assert existing[0].code == "pre"
    assert any(d.code == "missing_phase4_validation" for d in existing)


def test_cancel_event_halts_before_processing() -> None:
    """
    Purpose:
        Ensure cancellation is honored before any work is performed.
    Contract:
        Raises the cancellation exception without emitting diagnostics.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = []
    with pytest.raises(RuntimeError, match="cancelled"):
        MissingPhase4Strategy().run(
            index=_index("a"),
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_CancelStub(is_set=True),
        )
    assert diags == []


def test_cancel_event_checked_between_roots() -> None:
    """
    Purpose:
        Verify cancellation can stop processing between roots.
    Contract:
        Processes the first root, then raises before the second.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is toggled on.
    """
    blueprints: dict[str, RootResolutionBlueprint] = {}
    blueprints.update(_blueprint(root_id="r1", node_ids=("a",)))
    blueprints.update(_blueprint(root_id="r2", node_ids=("b",)))
    diags: list[SystemDiagnostic] = []
    with pytest.raises(RuntimeError, match="cancelled"):
        MissingPhase4Strategy().run(
            index=_index("a", "b"),
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_ToggleCancel(),
        )
    assert {d.root_id for d in diags} == {"r1"}


def test_phase4_results_extra_entries_ignored() -> None:
    """
    Purpose:
        Confirm extra Phase-4 results outside the DAG do not cause diagnostics.
    Contract:
        Leaves diagnostics empty when all DAG nodes are covered.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a", "b"))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={"a": object(), "b": object(), "extra": object()},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_empty_dag_produces_no_diagnostics() -> None:
    """
    Purpose:
        Ensure a blueprint with an empty DAG yields no diagnostics.
    Contract:
        Leaves diagnostics empty when no nodes exist.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=())
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index(),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_phase4_results_none_value_considered_present() -> None:
    """
    Purpose:
        Validate that a None value still counts as a present Phase-4 result.
    Contract:
        Does not emit diagnostics when the key exists in phase4_results.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={"a": None},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_missing_phase4_only_considers_dag_nodes() -> None:
    """
    Purpose:
        Ensure only DAG nodes are checked for Phase-4 results.
    Contract:
        Emits diagnostics only for nodes present in the blueprint DAG.
    Returns:
        None.
    Raises:
        AssertionError: If a non-DAG node is reported missing.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].spell_id == "a"


def test_missing_phase4_message_includes_spell_and_root() -> None:
    """
    Purpose:
        Verify diagnostic messages include both spell and root identifiers.
    Contract:
        The message references the missing spell id and root id.
    Returns:
        None.
    Raises:
        AssertionError: If message content does not include identifiers.
    """
    blueprints = _blueprint(root_id="root-x", node_ids=("spell-x",))
    diags: list[SystemDiagnostic] = []
    MissingPhase4Strategy().run(
        index=_index("spell-x"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    message = diags[0].message
    assert "spell-x" in message
    assert "root-x" in message
