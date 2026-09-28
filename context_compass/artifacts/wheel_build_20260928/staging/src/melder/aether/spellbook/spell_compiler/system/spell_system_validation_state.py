from typing import TYPE_CHECKING, List, Mapping, Optional, ClassVar



from melder.utilities.general_base.cleanable import Cleanable
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
    from melder.aether.spellbook.spell_compiler.system.system_diagnostic import SystemDiagnostic


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
        """
        Initialize a frame-level system validation verdict.

        Contract:
            - Stores validation outcome plus diagnostic buckets for the current
              Phase 6 run.
            - Copies diagnostic lists into state-owned storage.
            - Keeps the node mapping by reference as snapshot context.
        """
        super().__init__()
        self._is_valid: bool = bool(is_valid)
        self._errors: List[SystemDiagnostic] = list(errors) if errors else []
        self._warnings: List[SystemDiagnostic] = list(warnings) if warnings else []
        self._nodes: Optional[Mapping[str, SpellSystemNode]] = nodes

    def cleanup(self) -> None:
        """
        Deterministically release stored diagnostics and node references.

        Contract:
            - Idempotent: safe to call multiple times.
            - Best-effort cleans owned diagnostics before clearing containers.
        """
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
        """Return the frame-level validity verdict for this validation pass."""
        self.check_cleaned()
        return self._is_valid

    @property
    def errors(self) -> List[SystemDiagnostic]:
        """Return a copy of the recorded error diagnostics."""
        self.check_cleaned()
        return list(self._errors)

    @property
    def warnings(self) -> List[SystemDiagnostic]:
        """Return a copy of the recorded warning diagnostics."""
        self.check_cleaned()
        return list(self._warnings)

    @property
    def nodes(self) -> Optional[Mapping[str, SpellSystemNode]]:
        """Return the optional node snapshot attached to this validation state."""
        self.check_cleaned()
        return self._nodes
