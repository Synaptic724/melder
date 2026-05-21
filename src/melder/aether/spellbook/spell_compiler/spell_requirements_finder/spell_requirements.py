import threading
from typing import Any, Optional, Sequence, List, Iterable

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_parameter_requirements import (
    SpellParameterRequirement,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import ParameterDIShape
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
@mypyc_attr(native_class=True)
class SpellRequirements(Cleanable):
    """
    Phase 1 **per-spell requirements artifact**.

    This object answers the question:

        * "Given this spell, what does its call target want from DI?"

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
    #__melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell_id",
        "_spell_type",
        "_existence",
        "_spellframe",
        "_binding_name",
        "_parameters",
    ]
    __deletable__ = [
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
        """
        Initialize one phase-1 requirements artifact for a spell.

        Args:
            spell_id:
                Owning spell identifier.
            spell_type:
                Spell type derived from the raw binding shape.
            existence:
                Spell existence policy.
            spellframe:
                Spellframe associated with the spell, if any.
            binding_name:
                Optional logical binding name.
            parameters:
                Optional ordered parameter requirements.

        Returns:
            None.
        """
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
            self._cleaned = True

            del self._parameters
            del self._spell_id
            del self._spell_type
            del self._existence
            del self._spellframe
            del self._binding_name
        del self._lock

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spell_id(self) -> str:
        """
        Return the owning spell identifier for this requirements artifact.
        """
        self.check_cleaned()
        return self._spell_id

    @property
    def spell_type(self) -> SpellType:
        """
        Return the spell type derived from the phase-1 binding analysis.
        """
        self.check_cleaned()
        return self._spell_type

    @property
    def existence(self) -> Existence:
        """
        Return the spell existence policy captured for this requirements artifact.
        """
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
    def parameters(self) -> Sequence['SpellParameterRequirement']:
        """
        Ordered, per-parameter requirements for the spell's primary call target.

        This is returned as a **read-only sequence** from the caller's point
        of view; mutating it in-place is not supported.
        """
        self.check_cleaned()
        return tuple(self._parameters)


    # ------------------------------------------------------------------
    # Parameter classification helpers
    # ------------------------------------------------------------------

    def iter_di_parameters(self) -> Iterable['SpellParameterRequirement']:
        """
        Iterate over parameters that are **intended to be satisfied by DI**.

        This includes parameters whose :attr:`di_shape` is one of:

        * :data:`ParameterDIShape.SINGLE_BY_ANNOTATION`
        * :data:`ParameterDIShape.COLLECTION_BY_ANNOTATION`
        * :data:`ParameterDIShape.SPELLMAP_DEFAULT`

        These are the parameters that Phase 2+ will turn into symbolic
        dependencies and, eventually, concrete resolution DAG nodes.
        """
        self.check_cleaned()

        for param in self._parameters:
            di_shape = param.di_shape
            if di_shape in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
            ):
                yield param

    def iter_plain_parameters(self) -> Iterable['SpellParameterRequirement']:
        """
        Iterate over parameters whose :attr:`di_shape` is
        :data:`ParameterDIShape.PLAIN`.

        For these parameters, Melder does **not** perform automatic DI.
        They are intended to be satisfied by:

        * Default values on the parameter itself, or
        * Root-level ``spell_override`` payloads, or
        * Manual composition by the caller.

        This includes both required and optional/plain parameters; see
        :meth:`iter_required_holes` for the stricter subset that have
        **no default** at all.
        """
        self.check_cleaned()

        for param in self._parameters:
            if param.di_shape is ParameterDIShape.PLAIN:
                yield param

    def iter_required_holes(self) -> Iterable['SpellParameterRequirement']:
        """
        Iterate over **required holes** - parameters that Melder will never
        auto-wire and that also have **no default value**.

        Definition (Phase 1 view):

        * :attr:`SpellParameterRequirement.di_shape` is
          :data:`ParameterDIShape.PLAIN`.
        * :attr:`SpellParameterRequirement.has_default` is ``False``.

        These parameters **must** be satisfied by the caller somehow
        (e.g. via ``spell_override`` or by constructing intermediate objects
        manually) or resolution will fail once we try to instantiate the spell.

        Notes
        -----
        * Optional vs non-optional is *not* considered here. If you encode
          Optional/Union shapes without giving a default, they will still be
          reported as holes - Melder will not guess a union branch for you.
        * This method is purely structural; it does not perform any
          spellbook lookups or consider existence policies.
        """
        self.check_cleaned()

        for param in self._parameters:
            if (
                    param.di_shape is ParameterDIShape.PLAIN
                    and not param.has_default
            ):
                yield param

    def has_required_holes(self) -> bool:
        """
        Convenience predicate: return ``True`` if this spell has at least
        one **required hole** as defined by :meth:`iter_required_holes`.

        This is useful for fast checks in validation, tooling, or diagnostics
        without having to allocate an intermediate list.
        """
        self.check_cleaned()

        for _ in self.iter_required_holes():
            return True
        return False
