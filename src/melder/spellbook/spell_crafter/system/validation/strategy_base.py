from __future__ import annotations

from typing import Dict, Mapping, Protocol, Optional, List, Set

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


class SpellSystemValidationStrategy(Protocol):
    """
    Protocol for system-level validation strategies.

    Implementations should be stateless or self-contained; any heavy state
    should be cleaned by the caller if retained.
    """

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
        ...
