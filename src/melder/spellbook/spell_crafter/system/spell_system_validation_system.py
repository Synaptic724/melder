from __future__ import annotations

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
            strategy.run(
                index=index,
                blueprints=blueprints,
                phase4_results=phase4_results,
                broken_spell_ids=broken_spell_ids,
                diagnostics=diagnostics,
                cancel_event=cancel_event,
            )

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
