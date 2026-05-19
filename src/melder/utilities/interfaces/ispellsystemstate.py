from typing import Iterable, Optional, Protocol, Set, runtime_checkable
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_state_change_reason import (
    SpellStateChangeReason,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class ISpellSystemState(ICleanable, Protocol):
    """
    Spell-lineage structural state contract consumed by `SpellCrafter`.
    """

    @property
    def spell_index_id(self) -> str:
        ...

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
            *,
            change_reason: Optional[SpellStateChangeReason] = None,
            flags_to_add: Optional[Iterable[SpellState]] = None,
            flags_to_remove: Optional[Iterable[SpellState]] = None,
            transitively_dirty: Optional[bool] = None,
    ) -> None:
        ...

    def clear_dirty(self, last_validated_at: Optional[float]) -> None:
        ...
