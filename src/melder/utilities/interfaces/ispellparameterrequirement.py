import inspect
from typing import Any, Optional, Protocol, runtime_checkable
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class ISpellParameterRequirement(ICleanable, Protocol):
    """
    Phase-1 parameter requirement contract consumed by later spell-crafter
    phases.
    """

    @property
    def name(self) -> str:
        ...

    @property
    def position(self) -> int:
        ...

    @property
    def kind(self) -> inspect._ParameterKind:
        ...

    @property
    def annotation(self) -> Any:
        ...

    @property
    def default_value(self) -> Any:
        ...

    @property
    def is_optional(self) -> bool:
        ...

    @property
    def di_shape(self) -> ParameterDIShape:
        ...

    @property
    def collection_element_annotation(self) -> Any:
        ...

    @property
    def spellmap_default(self) -> Optional[SpellMap]:
        ...
