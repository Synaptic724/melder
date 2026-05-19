from __future__ import annotations

from melder.aether.aether import Aether
from melder.aether.aetheric_frame.aetheric_frame import AethericFrame
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.spell_system_validation_system import (
    SpellSystemValidationSystem,
)
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)


def _register_index(states, spell_id: str) -> SpellIndex:
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
    states.register_index(index, object())
    return index


class _DiagnosticStrategy(SpellSystemValidationStrategy):
    """
    Purpose:
        Emit a configured SystemDiagnostic for component validation.
    Contract:
        - Appends the diagnostic to the shared diagnostics list.
    """

    def __init__(self, diagnostic: SystemDiagnostic) -> None:
        """
        Purpose:
            Capture the diagnostic for emission.
        Contract:
            - Stores the diagnostic instance for run().
        Args:
            diagnostic: SystemDiagnostic to append during validation.
        """
        self._diagnostic = diagnostic

    def run(
        self,
        *,
        index: SpellSystemIndex,
        blueprints: dict[str, object],
        phase4_results: dict[str, object],
        broken_spell_ids: set[str],
        spell_system_states: object,
        spell_lookup: dict[str, object],
        diagnostics: list[SystemDiagnostic],
        cancel_event,
    ) -> None:
        """
        Purpose:
            Append the configured diagnostic.
        Contract:
            - Adds the diagnostic without mutation.
        Args:
            index: System index for the frame.
            blueprints: Root blueprints for the frame.
            phase4_results: Phase-4 result map.
            broken_spell_ids: Broken spell ids.
            spell_system_states: SpellSystemStates instance.
            spell_lookup: Mapping of spell ids to spell objects.
            diagnostics: Shared diagnostics list.
            cancel_event: Optional cancellation signal.
        Returns:
            None.
        """
        diagnostics.append(self._diagnostic)


def test_component_system_diagnostic_warning_roundtrip() -> None:
    """
    Purpose:
        Validate warning diagnostics flow through system validation.
    Contract:
        - Warning diagnostics appear in the validation state.
        - Conduit resolution validity is set to valid.
    Returns:
        None.
    Raises:
        AssertionError: If warnings are lost or resolution validity is not valid.
    """
    frame = AethericFrame(Aether(), "component-system-diagnostic-warning")
    states = frame._spell_system_states
    root_id = "root-diagnostic-warning"
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    warning = SystemDiagnostic(
        code="warning_diag",
        message="warning diagnostic",
        severity=SystemDiagnosticSeverity.WARNING,
        spell_id=root_id,
        root_id=root_id,
        details={"detail": "value"},
    )

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        system = SpellSystemValidationSystem([_DiagnosticStrategy(warning)])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == [warning]
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.valid
        assert warning.details == {"detail": "value"}
    finally:
        frame.cleanup()


def test_component_system_diagnostic_error_gates_states() -> None:
    """
    Purpose:
        Validate error diagnostics gate lineage validity.
    Contract:
        - Error diagnostics appear in the validation state.
        - Conduit resolution validity is invalid.
    Returns:
        None.
    Raises:
        AssertionError: If errors are not propagated or resolution validity is not invalid.
    """
    frame = AethericFrame(Aether(), "component-system-diagnostic-error")
    states = frame._spell_system_states
    root_id = "root-diagnostic-error"
    root_index = _register_index(states, root_id)
    states.update_dependencies(root_index, [])

    error = SystemDiagnostic(
        code="error_diag",
        message="error diagnostic",
        severity=SystemDiagnosticSeverity.ERROR,
        spell_id=root_id,
        root_id=root_id,
    )

    try:
        index = SpellSystemIndex()
        index.upsert_node(
            SpellSystemNode(
                spell_id=root_id,
                lineage_id=root_index.id,
                is_root=True,
            )
        )
        system = SpellSystemValidationSystem([_DiagnosticStrategy(error)])
        try:
            result = system.validate(
                index=index,
                blueprints={},
                phase4_results={},
                broken_spell_ids=set(),
                spell_system_states=states,
                conduit_id="cid",
            )
        finally:
            system.cleanup()

        assert result.is_valid is False
        assert result.errors == [error]
        assert result.warnings == []
        conduit_state = states.get_conduit_resolution_state("cid")
        assert conduit_state is not None
        assert conduit_state.get_spell_validity(root_id) is SpellValidity.invalid
    finally:
        frame.cleanup()


