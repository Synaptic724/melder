from __future__ import annotations

import pytest

from melder.aether.aetheric_frame import AethericFrame
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


def _register_lineage(states, spell_id: str) -> SpellIndex:
    """
    Purpose:
        Register a spell lineage into SpellSystemStates.
    Contract:
        - Returns a SpellIndex with current id set to spell_id.
        - Registers the lineage in the states registry.
    Args:
        states: SpellSystemStates registry.
        spell_id: Version id to register.
    Returns:
        SpellIndex: The created spell index.
    """
    index = SpellIndex(spell_id)
    states.register_lineage(index, object())
    return index


class _EmitDiagnosticsStrategy(SpellSystemValidationStrategy):
    """
    Purpose:
        Emit both an error and a warning for validation state coverage.
    Contract:
        - Appends the diagnostics to the shared list.
    """

    def __init__(self, error: SystemDiagnostic, warning: SystemDiagnostic) -> None:
        """
        Purpose:
            Capture diagnostics to emit.
        Contract:
            - Stores the diagnostics for run().
        Args:
            error: Error diagnostic to append.
            warning: Warning diagnostic to append.
        """
        self._error = error
        self._warning = warning

    def run(
        self,
        *,
        index: SpellSystemIndex,
        blueprints: dict[str, object],
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        diagnostics: list[SystemDiagnostic],
        cancel_event,
    ) -> None:
        """
        Purpose:
            Append the configured diagnostics.
        Contract:
            - Adds the diagnostics without mutation.
        Args:
            index: System index for the frame.
            blueprints: Root blueprints for the frame.
            phase4_results: Phase-4 result map.
            broken_spell_ids: Broken spell ids.
            diagnostics: Shared diagnostics list.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        """
        diagnostics.append(self._error)
        diagnostics.append(self._warning)


def test_component_validation_state_cleanup_disposes_diagnostics() -> None:
    """
    Purpose:
        Validate validation state cleanup disposes diagnostics.
    Contract:
        - Diagnostics are cleaned when the state is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics remain active after cleanup.
    """
    error = SystemDiagnostic(code="err", message="error")
    warning = SystemDiagnostic(
        code="warn",
        message="warning",
        severity=SystemDiagnosticSeverity.WARNING,
    )
    state = SpellSystemValidationState(
        is_valid=False,
        errors=[error],
        warnings=[warning],
    )
    state.cleanup()

    assert error.cleaned is True
    assert warning.cleaned is True
    with pytest.raises(RuntimeError):
        _ = error.code
    with pytest.raises(RuntimeError):
        _ = warning.code


def test_component_validation_state_nodes_mapping_is_live() -> None:
    """
    Purpose:
        Validate validation state nodes mapping stays live with the index.
    Contract:
        - New nodes added to the index appear in state.nodes.
    Returns:
        None.
    Raises:
        AssertionError: If nodes mapping diverges.
    """
    index = SpellSystemIndex()
    node_a = SpellSystemNode(spell_id="node-a", lineage_id="lineage-a")
    index.upsert_node(node_a)
    state = SpellSystemValidationState(
        is_valid=True,
        nodes=index.nodes,
    )

    node_b = SpellSystemNode(spell_id="node-b", lineage_id="lineage-b")
    index.upsert_node(node_b)
    assert "node-b" in state.nodes


def test_component_validation_state_from_system_validation_tracks_diagnostics() -> None:
    """
    Purpose:
        Validate diagnostics are separated into errors and warnings.
    Contract:
        - Errors and warnings appear in their respective lists.
        - State cleanup disposes the diagnostics.
    Returns:
        None.
    Raises:
        AssertionError: If diagnostics are not captured or cleaned.
    """
    frame = AethericFrame("component-validation-state-diagnostics")
    states = frame._spell_system_states
    root_id = "root-validation-state"
    root_index = _register_lineage(states, root_id)
    states.update_dependencies(root_index, [])

    error = SystemDiagnostic(code="err", message="error")
    warning = SystemDiagnostic(
        code="warn",
        message="warning",
        severity=SystemDiagnosticSeverity.WARNING,
    )
    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(spell_id=root_id, lineage_id=root_index.id, is_root=True)
        )
        system = SpellSystemValidationSystem(
            [_EmitDiagnosticsStrategy(error, warning)]
        )
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
            )
        finally:
            system.cleanup()

        assert result.errors == [error]
        assert result.warnings == [warning]
        result.cleanup()
        assert error.cleaned is True
        assert warning.cleaned is True
    finally:
        frame.cleanup()
