from typing import Dict, List, Protocol, runtime_checkable
from melder.aether.spellbook.spell_compiler.blueprints.patch_maps import MutationEdgePatch
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IMutationPatchMap(ICleanable, Protocol):
    """
    Phase-10 mutation patch-map contract consumed by `SpellCrafter`.
    """

    @property
    def root_spell_id(self) -> str:
        ...

    @property
    def targets_by_spec(self) -> Dict[str, List[MutationEdgePatch]]:
        ...

