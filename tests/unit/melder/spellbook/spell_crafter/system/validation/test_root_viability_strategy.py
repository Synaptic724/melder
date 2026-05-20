from __future__ import annotations

import pytest

from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.root_viability_strategy import (
    RootViabilityStrategy,
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
        Toggle cancellation state on the second is_set check.
    Contract:
        Raises once the second check is performed.
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


def test_no_existing_errors_produces_no_diagnostics() -> None:
    """
    Purpose:
        Ensure no diagnostics are emitted when no errors exist.
    Contract:
        Leaves diagnostics unchanged when error-free.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = []
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert diags == []


def test_existing_error_emits_root_not_viable() -> None:
    """
    Purpose:
        Verify an existing error for a root triggers a root_not_viable diagnostic.
    Contract:
        Appends a root_not_viable error diagnostic for the affected root.
    Returns:
        None.
    Raises:
        AssertionError: If the diagnostic fields are incorrect.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    existing = [
        SystemDiagnostic(
            code="pre",
            message="boom",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=None,
    )
    assert len(existing) == 2
    added = existing[1]
    assert added.code == "root_not_viable"
    assert added.severity is SystemDiagnosticSeverity.ERROR
    assert added.root_id == "root"
    assert added.spell_id is None


def test_error_without_root_id_does_not_trigger() -> None:
    """
    Purpose:
        Ensure root viability ignores errors without a root_id.
    Contract:
        Does not emit root_not_viable when root_id is None.
    Returns:
        None.
    Raises:
        AssertionError: If a diagnostic is emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags = [
        SystemDiagnostic(
            code="pre",
            message="boom",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id=None,
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "pre"


def test_warning_does_not_trigger_root_not_viable() -> None:
    """
    Purpose:
        Validate warnings do not affect root viability.
    Contract:
        Ignores non-error diagnostics when determining viability.
    Returns:
        None.
    Raises:
        AssertionError: If root_not_viable is emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags = [
        SystemDiagnostic(
            code="warn",
            message="warn",
            severity=SystemDiagnosticSeverity.WARNING,
            root_id="root",
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "warn"


def test_multiple_roots_emit_only_for_roots_with_errors() -> None:
    """
    Purpose:
        Ensure only roots with existing errors receive root_not_viable diagnostics.
    Contract:
        Emits one root_not_viable per root with errors.
    Returns:
        None.
    Raises:
        AssertionError: If unexpected roots are marked not viable.
    """
    blueprints: dict[str, RootResolutionBlueprint] = {}
    blueprints.update(_blueprint(root_id="r1", node_ids=("a",)))
    blueprints.update(_blueprint(root_id="r2", node_ids=("b",)))
    blueprints.update(_blueprint(root_id="r3", node_ids=("c",)))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="r1",
            spell_id="a",
        ),
        SystemDiagnostic(
            code="e2",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="r2",
            spell_id="b",
        ),
    ]
    RootViabilityStrategy().run(
        index=_index("a", "b", "c"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    new_roots = {d.root_id for d in diags if d.code == "root_not_viable"}
    assert new_roots == {"r1", "r2"}


def test_multiple_errors_for_same_root_emit_once() -> None:
    """
    Purpose:
        Confirm a root with multiple errors gets a single viability diagnostic.
    Contract:
        Emits one root_not_viable per root despite multiple existing errors.
    Returns:
        None.
    Raises:
        AssertionError: If more than one viability diagnostic is emitted.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id="a",
        ),
        SystemDiagnostic(
            code="e2",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id="a",
        ),
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    added = [d for d in diags if d.code == "root_not_viable"]
    assert len(added) == 1


def test_cancel_event_halts_before_processing() -> None:
    """
    Purpose:
        Ensure cancellation is honored before any root processing begins.
    Contract:
        Raises the cancellation exception without appending diagnostics.
    Returns:
        None.
    Raises:
        RuntimeError: When cancellation is signaled.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id="a",
        )
    ]
    with pytest.raises(RuntimeError, match="cancelled"):
        RootViabilityStrategy().run(
            index=_index("a"),
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_CancelStub(is_set=True),
        )
    assert all(d.code != "root_not_viable" for d in diags)


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
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="r1",
            spell_id="a",
        ),
        SystemDiagnostic(
            code="e2",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="r2",
            spell_id="b",
        ),
    ]
    with pytest.raises(RuntimeError, match="cancelled"):
        RootViabilityStrategy().run(
            index=_index("a", "b"),
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diags,
            cancel_event=_ToggleCancel(),
        )
    roots = {d.root_id for d in diags if d.code == "root_not_viable"}
    assert roots == {"r1"}


def test_blueprints_empty_does_not_add_viability_diagnostics() -> None:
    """
    Purpose:
        Ensure no viability diagnostics are added when no roots are provided.
    Contract:
        Leaves diagnostics unchanged when blueprints is empty.
    Returns:
        None.
    Raises:
        AssertionError: If a root_not_viable diagnostic is appended.
    """
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "e1"


def test_error_for_unknown_root_does_not_emit_viability() -> None:
    """
    Purpose:
        Confirm errors for roots not present in blueprints do not emit viability diagnostics.
    Contract:
        Does not append root_not_viable when the root is not in blueprints.
    Returns:
        None.
    Raises:
        AssertionError: If a viability diagnostic is appended.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="ghost",
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    assert len(diags) == 1
    assert diags[0].code == "e1"


def test_error_without_spell_id_still_triggers_viability() -> None:
    """
    Purpose:
        Ensure root errors trigger viability even when spell_id is None.
    Contract:
        Appends root_not_viable for the affected root.
    Returns:
        None.
    Raises:
        AssertionError: If the viability diagnostic is missing.
    """
    blueprints = _blueprint(root_id="root", node_ids=("a",))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root",
            spell_id=None,
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    added = [d for d in diags if d.code == "root_not_viable"]
    assert len(added) == 1
    assert added[0].root_id == "root"


def test_root_not_viable_message_includes_root_id() -> None:
    """
    Purpose:
        Validate the diagnostic message contains the root identifier.
    Contract:
        root_not_viable message references the root id.
    Returns:
        None.
    Raises:
        AssertionError: If the message does not include the root id.
    """
    blueprints = _blueprint(root_id="root-x", node_ids=("a",))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="root-x",
            spell_id="a",
        )
    ]
    RootViabilityStrategy().run(
        index=_index("a"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    message = [d.message for d in diags if d.code == "root_not_viable"][0]
    assert "root-x" in message


def test_warnings_for_root_do_not_trigger_viability() -> None:
    """
    Purpose:
        Ensure warnings for a root do not produce viability diagnostics.
    Contract:
        Emits root_not_viable only for roots with errors.
    Returns:
        None.
    Raises:
        AssertionError: If a warning-only root is marked not viable.
    """
    blueprints: dict[str, RootResolutionBlueprint] = {}
    blueprints.update(_blueprint(root_id="r1", node_ids=("a",)))
    blueprints.update(_blueprint(root_id="r2", node_ids=("b",)))
    diags: list[SystemDiagnostic] = [
        SystemDiagnostic(
            code="w1",
            message="warn",
            severity=SystemDiagnosticSeverity.WARNING,
            root_id="r1",
            spell_id="a",
        ),
        SystemDiagnostic(
            code="e1",
            message="err",
            severity=SystemDiagnosticSeverity.ERROR,
            root_id="r2",
            spell_id="b",
        ),
    ]
    RootViabilityStrategy().run(
        index=_index("a", "b"),
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diags,
        cancel_event=None,
    )
    roots = {d.root_id for d in diags if d.code == "root_not_viable"}
    assert roots == {"r2"}
