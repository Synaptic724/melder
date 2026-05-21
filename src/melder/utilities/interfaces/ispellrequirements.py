from typing import Any, Optional, Protocol, Sequence, runtime_checkable
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispellparameterrequirement import (
    ISpellParameterRequirement,
)


@runtime_checkable
class ISpellRequirements(ICleanable, Protocol):
    """
    Phase-1 per-spell requirements artifact contract.
    """

    @property
    def spell_id(self) -> str:
        ...

    @property
    def spell_type(self) -> SpellType:
        ...

    @property
    def existence(self) -> Existence:
        ...

    @property
    def spellframe(self) -> Any:
        ...

    @property
    def binding_name(self) -> Optional[str]:
        ...

    @property
    def parameters(self) -> Sequence[ISpellParameterRequirement]:
        ...

