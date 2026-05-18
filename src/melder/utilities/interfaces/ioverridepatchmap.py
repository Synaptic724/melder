from typing import Dict, List, Mapping, Protocol, runtime_checkable
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IOverridePatchMap(ICleanable, Protocol):
    """
    Phase-10 override patch-map contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def targets_by_spec(self) -> Dict[str, List[SocketRef]]:
        ...

    @property
    def specificity_by_spec(self) -> Mapping[str, int]:
        ...
