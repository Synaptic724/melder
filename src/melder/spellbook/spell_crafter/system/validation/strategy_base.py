from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Mapping, Optional, List, Set

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class SpellSystemValidationStrategy(ABC):
    """
    Abstract base for system-level validation strategies.

    Concrete strategies must implement `run` to inspect phase artifacts and
    append diagnostics. Strategies should remain stateless or self-contained.
    """

    __melder_internal__ = _mrg.sentinel

    @abstractmethod
    def run(
            self,
            *,
            index: SpellSystemIndex,
            blueprints: Dict[str, RootResolutionBlueprint],
            phase4_results: Mapping[str, object],
            broken_spell_ids: Set[str],
            diagnostics: List[SystemDiagnostic],
            cancel_event: Optional[CancellationEvent],
    ) -> None:
        """
        Execute the validation strategy.

        Args:
            index: Spell system index being validated.
            blueprints: Phase-5 blueprints keyed by id.
            phase4_results: Phase-4 results keyed by id.
            broken_spell_ids: Set of broken spell ids.
            diagnostics: List to append diagnostics into.
            cancel_event: Optional cancellation signal.
        """
        ...
