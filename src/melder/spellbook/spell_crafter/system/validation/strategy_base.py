from abc import ABC, abstractmethod
from typing import Dict, Mapping, Optional, List, Set

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.interfaces import ISpell, ISpellSystemStates
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class SpellSystemValidationStrategy(ABC):
    """
    Contract for one Phase 6 system-validation strategy.

    Strategies run over the frame-level Phase 5 outputs
    (`SpellSystemIndex` + `RootResolutionBlueprint` map) plus selected Phase 4
    spell-validation results. Each strategy is responsible for one coherent
    class of system-level invariant, such as graph consistency, missing Phase 4
    coverage, or root viability.

    Contract:
        - Strategies are invoked by `SpellSystemValidationSystem` in the order
          they were registered.
        - Strategies append diagnostics into the shared `diagnostics` list
          rather than returning a separate result object.
        - Strategies should stay stateless or otherwise self-contained so they
          are safe to reuse across validation runs.
        - Strategies may inspect but must not mutate the supplied Phase 5/6
          inputs.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = ()

    @abstractmethod
    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            spell_system_states: ISpellSystemStates,
            spell_lookup: Mapping[str, ISpell],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Execute one system-level validation pass over shared Phase 5/6 inputs.

        Args:
            index:
                Frame-level spell system index being validated.
            blueprints:
                Root blueprints keyed by root spell id.
            phase4_results:
                Per-spell Phase 4 validation artifacts keyed by spell id.
            broken_spell_ids:
                Spell ids already known to be broken at the spell-validation
                layer.
            spell_system_states:
                SpellSystemStates registry for topology and lineage data.
            spell_lookup:
                Visible spell version ids to spell objects for the current
                validation scope.
            diagnostics:
                Shared list to append new diagnostics into.
            cancel_event:
                Optional cancellation signal that strategies should honor during
                longer scans.
        """
        ...
