import threading
from typing import Any, Optional, Sequence, List

# Melder imports
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable


class SpellRequirements(Cleanable):
    """
    Phase 1 **per-spell requirements artifact**.

    This object answers the question:

        *“Given this Spell, what does its call target **want** from DI?”*

    It is intentionally limited to:

        * Identity and metadata (spell_id, spell_type, existence, spellframe,
          binding_name).
        * A sequence of :class:`SpellParameterRequirement` instances describing
          the constructor/call parameters.

    It does **not**:

        * Resolve anything against the Spellbook.
        * Decide existence policies.
        * Build DAGs or symbolic graphs.

    Those concerns are reserved for later phases.
    """

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_spell_type",
        "_existence",
        "_spellframe",
        "_binding_name",
        "_parameters",
    ]

    def __init__(
            self,
            *,
            spell_id: str,
            spell_type: SpellType,
            existence: Existence,
            spellframe: Any,
            binding_name: Optional[str],
            parameters: Optional[List["SpellParameterRequirement"]] = None,
    ) -> None:
        Cleanable.__init__(self)

        if not spell_id:
            raise ValueError("spell_id must be a non-empty string.")

        self._lock: threading.RLock = threading.RLock()
        self._spell_id: str = spell_id
        self._spell_type: SpellType = spell_type
        self._existence: Existence = existence
        self._spellframe: Any = spellframe
        self._binding_name: Optional[str] = binding_name
        self._parameters: List["SpellParameterRequirement"] = (
            parameters if parameters is not None else []
        )

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this requirements artifact.

        This will cascade cleanup to all contained
        :class:`SpellParameterRequirement` instances.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            for param in self._parameters:
                try:
                    param.cleanup()
                except Exception:
                    # We never let cleanup explosions bubble up from here.
                    pass

            self._parameters = []
            self._spell_id = None
            self._spell_type = None
            self._existence = None
            self._spellframe = None
            self._binding_name = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spell_id(self) -> str:
        self.check_cleaned()
        return self._spell_id

    @property
    def spell_type(self) -> SpellType:
        self.check_cleaned()
        return self._spell_type

    @property
    def existence(self) -> Existence:
        self.check_cleaned()
        return self._existence

    @property
    def spellframe(self) -> Any:
        """
        The spellframe associated with this spell, if any.

        This can be:

            * A Protocol / interface type.
            * A string frame key (e.g. "order_handlers").
            * ``None`` for frame-less spells.
        """
        self.check_cleaned()
        return self._spellframe

    @property
    def binding_name(self) -> Optional[str]:
        """
        Logical binding name for this spell (if any).
        """
        self.check_cleaned()
        return self._binding_name

    @property
    def parameters(self) -> Sequence["SpellParameterRequirement"]:
        """
        Ordered, per-parameter requirements for the spell's primary call target.

        This is returned as a **read-only sequence** from the caller's point
        of view; mutating it in-place is not supported.
        """
        self.check_cleaned()
        return tuple(self._parameters)
