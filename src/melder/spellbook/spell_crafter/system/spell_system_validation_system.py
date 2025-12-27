from typing import Dict, Iterable, List, Optional, Set
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.validation.strategy_base import (
    SpellSystemValidationStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class SpellSystemValidationSystem(Cleanable):
    """
    Orchestrates system-level validation strategies over Phase 5 artifacts and Phase 4 outcomes.

    Purpose:
        Aggregate system-level validation diagnostics and update lineage validity
        for all spells in the current frame.
    Contract:
        - Strategies are executed in the order provided at construction.
        - Diagnostics are collected and returned via SpellSystemValidationState.
        - Lineage validity is set to VALID when no error diagnostics exist, and
          to GATED when any error diagnostics are present.
    Threading:
        Callers are responsible for external synchronization when sharing inputs
        across threads. This class does not introduce additional locking.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_strategies",
    ]

    def __init__(self, strategies: Iterable[SpellSystemValidationStrategy]) -> None:
        super().__init__()
        if strategies is None:
            raise ValueError("strategies must not be None.")
        self._strategies: Optional[List[SpellSystemValidationStrategy]] = list(
            strategies
        )

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        if self._strategies is not None:
            self._strategies.clear()
        self._strategies = None

    def validate(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Dict[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> SpellSystemValidationState:
        """
        Run system-level validation and update per-lineage validity.

        Purpose:
            Validate the system-level DAG artifacts produced in Phase 5 and
            record a frame-wide validation verdict.
        Contract:
            - Executes each configured strategy in order against shared inputs.
            - Collects diagnostics across strategies into a single list.
            - Auto-populates diagnostic source attribution when missing.
            - Marks all lineages VALID on success or GATED on error diagnostics.
            - Returns a validation state containing all diagnostics and nodes.
        Args:
            index: Frame-level spell system index to validate.
            blueprints: Root blueprints keyed by root spell id.
            phase4_results: Phase-4 validation artifacts keyed by spell id.
            broken_spell_ids: Set of spell ids flagged as broken in Phase 4.
            spell_system_states: Registry used to mark lineage validity.
            cancel_event: Optional cancellation signal for long-running validation.
        Returns:
            SpellSystemValidationState: Aggregated diagnostics and validity.
        Raises:
            ValueError: If required inputs are None.
            Exception: Propagates cancellation exceptions or strategy errors.
        """
        self.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        if blueprints is None:
            raise ValueError("blueprints must not be None.")
        if spell_system_states is None:
            raise ValueError("spell_system_states must not be None.")
        if self._strategies is None:
            raise RuntimeError("Validation strategies have been cleaned.")

        diagnostics: List[SystemDiagnostic] = []

        for strategy in self._strategies:
            if cancel_event is not None and cancel_event.is_set:
                cancel_event.throw_if_set()
            before_count = len(diagnostics)
            strategy.run(
                index=index,
                blueprints=blueprints,
                phase4_results=phase4_results,
                broken_spell_ids=broken_spell_ids,
                diagnostics=diagnostics,
                cancel_event=cancel_event,
            )
            if len(diagnostics) > before_count:
                source = type(strategy).__name__
                for diag in diagnostics[before_count:]:
                    if isinstance(diag, SystemDiagnostic) and diag.source is None:
                        diag._source = source

        has_error = any(
            diag.severity is SystemDiagnosticSeverity.ERROR for diag in diagnostics
        )

        if has_error:
            self._set_validity(
                spell_system_states=spell_system_states,
                spell_ids=index.nodes.keys(),
                validity=SpellValidity.gated,
                change_reason=SpellStateChangeReason.validation_failed,
            )
        else:
            self._set_validity(
                spell_system_states=spell_system_states,
                spell_ids=index.nodes.keys(),
                validity=SpellValidity.valid,
                change_reason=SpellStateChangeReason.validation_passed,
            )

        errors = [
            diag for diag in diagnostics if diag.severity is SystemDiagnosticSeverity.ERROR
        ]
        warnings = [
            diag
            for diag in diagnostics
            if diag.severity is SystemDiagnosticSeverity.WARNING
        ]

        return SpellSystemValidationState(
            is_valid=not has_error,
            errors=errors,
            warnings=warnings,
            nodes=index.nodes,
        )

    def _set_validity(
            self,
            *,
            spell_system_states: ISpellSystemStates,
            spell_ids: Iterable[str],
            validity: SpellValidity,
            change_reason: SpellStateChangeReason,
    ) -> None:
        """
        Apply a validity flag to all supplied spell_ids if their lineage state exists.
        """
        for spell_id in spell_ids:
            state = spell_system_states.get_by_spell_id(spell_id)
            if state is None:
                continue
            try:
                state.set_validity(
                    validity,
                    change_reason=change_reason,
                )
            except Exception:
                continue
