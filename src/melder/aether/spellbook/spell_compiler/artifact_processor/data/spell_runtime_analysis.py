from typing import Any, Dict, List, Tuple

from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable


class SpellRuntimeRecord:
    """
    Processor-owned runtime spell record.

    Purpose:
        Hold the spell-static runtime facts needed by planner strategies without
        forcing those strategies to reopen the live spellbook maps.
    """

    __slots__ = [
        "spell_id",
        "spell_name",
        "spell",
        "call_target",
        "existence",
        "is_existing_creation",
        "is_class_spell",
        "is_method_spell",
        "is_lambda_spell",
        "has_disposal_methods",
        "disposal_method_names",
        "user_created_object",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            spell_name: str,
            spell: Any,
            call_target: Any,
            existence: Existence,
            is_existing_creation: bool,
            is_class_spell: bool,
            is_method_spell: bool,
            is_lambda_spell: bool,
            has_disposal_methods: bool,
            disposal_method_names: Tuple[str, ...],
            user_created_object: Any,
    ) -> None:
        """
        Build one runtime spell record.
        """
        self.spell_id = spell_id
        self.spell_name = spell_name
        self.spell = spell
        self.call_target = call_target
        self.existence = existence
        self.is_existing_creation = is_existing_creation
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell
        self.has_disposal_methods = has_disposal_methods
        self.disposal_method_names = disposal_method_names
        self.user_created_object = user_created_object


class SpellRuntimeAnalysis(Cleanable):
    """
    Processor-owned runtime spell section.

    Purpose:
        Hold the per-spell static runtime facts the planner needs when building
        execution lane payloads from the fitted model.
    """

    __slots__ = Cleanable.__slots__ + [
        "records_by_spell_id",
        "spell_count",
    ]

    def __init__(
            self,
            *,
            records_by_spell_id: Dict[str, SpellRuntimeRecord],
    ) -> None:
        """
        Build one runtime spell section.
        """
        super().__init__()
        self.records_by_spell_id = records_by_spell_id
        self.spell_count = len(records_by_spell_id)

    def cleanup(self) -> None:
        """
        Deterministically release owned runtime spell section data.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self.records_by_spell_id.clear()
        del self.records_by_spell_id
        del self.spell_count
