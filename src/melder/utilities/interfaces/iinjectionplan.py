from typing import Any, Dict, Optional, Protocol, runtime_checkable
from melder.spellbook.spell_crafter.blueprints.injection_plan import InjectionSpec
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import InstanceKey
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IInjectionPlan(ICleanable, Protocol):
    """
    Phase-9 injection plan contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def instance_injections(self) -> Dict[InstanceKey, InjectionSpec]:
        ...

    def select_for_runtime(
            self,
            *,
            root_spell_id: str,
    ) -> Optional[Dict[InstanceKey, InjectionSpec]]:
        ...
