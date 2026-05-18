from typing import Optional, Protocol, Set, runtime_checkable
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class ISpellSystemState(ICleanable, Protocol):
    """
    Spell-lineage structural state contract consumed by `SpellCrafter`.
    """

    @property
    def validity(self) -> SpellValidity:
        ...

    @property
    def flags(self) -> Set[SpellState]:
        ...

    @property
    def change_reason(self) -> Optional[SpellStateChangeReason]:
        ...

    def set_validity(
            self,
            validity: SpellValidity,
            reason: Optional[SpellStateChangeReason] = None,
    ) -> None:
        ...

    def clear_dirty(self, validated_at: float) -> None:
        ...
