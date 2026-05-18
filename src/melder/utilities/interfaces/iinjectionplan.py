from typing import Mapping, Optional, Protocol, runtime_checkable, Tuple
from melder.utilities.interfaces.iinjectionspec import IInjectionSpec
from melder.utilities.interfaces.icleanable import ICleanable

OccurrenceKey = Tuple[str, int]
InstanceKey = Tuple[str, Optional[int]]

@runtime_checkable
class IInjectionPlan(ICleanable, Protocol):
    """
    Phase-9 injection plan contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def instance_injections(self) -> Mapping[InstanceKey, IInjectionSpec]:
        ...

    def select_for_runtime(
            self,
            *,
            root_spell_id: str,
    ) -> Optional[Mapping[InstanceKey, IInjectionSpec]]:
        ...
