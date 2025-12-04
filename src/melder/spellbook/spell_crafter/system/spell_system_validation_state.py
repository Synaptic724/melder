from __future__ import annotations

from typing import List, Mapping, Optional

from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.system_diagnostic import SystemDiagnostic
from melder.utilities.general_base.cleanable import Cleanable


class SpellSystemValidationState(Cleanable):
    """
    Frame-level system validation verdict.
    """

    __slots__ = Cleanable.__slots__ + [
        "_is_valid",
        "_errors",
        "_warnings",
        "_nodes",
    ]

    def __init__(
            self,
            *,
            is_valid: bool,
            errors: Optional[List[SystemDiagnostic]] = None,
            warnings: Optional[List[SystemDiagnostic]] = None,
            nodes: Optional[Mapping[str, SpellSystemNode]] = None,
    ) -> None:
        super().__init__()
        self._is_valid: bool = bool(is_valid)
        self._errors: List[SystemDiagnostic] = list(errors) if errors else []
        self._warnings: List[SystemDiagnostic] = list(warnings) if warnings else []
        self._nodes: Optional[Mapping[str, SpellSystemNode]] = nodes

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self._cleaned = True
        for diag in self._errors:
            try:
                diag.cleanup()
            except Exception:
                pass
        for diag in self._warnings:
            try:
                diag.cleanup()
            except Exception:
                pass
        self._errors.clear()
        self._warnings.clear()
        self._errors = []
        self._warnings = []
        self._nodes = None

    @property
    def is_valid(self) -> bool:
        self.check_cleaned()
        return self._is_valid

    @property
    def errors(self) -> List[SystemDiagnostic]:
        self.check_cleaned()
        return list(self._errors)

    @property
    def warnings(self) -> List[SystemDiagnostic]:
        self.check_cleaned()
        return list(self._warnings)

    @property
    def nodes(self) -> Optional[Mapping[str, SpellSystemNode]]:
        self.check_cleaned()
        return self._nodes
