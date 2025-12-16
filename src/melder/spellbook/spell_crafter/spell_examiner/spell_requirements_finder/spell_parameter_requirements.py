import inspect
import threading
from typing import Any, Optional
# Melder imports
from melder.spellbook.spell_crafter.spell_examiner.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.conduit.meld.contracts.spell_map import SpellMap
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellParameterRequirement(Cleanable):
    """
    Phase 1 description of a **single constructor parameter** for a spell.

    This is intentionally **read-only-ish** and lightweight. It captures just
    enough to drive later phases (symbolic graphs, DAG construction, actual
    resolution) without doing any heavy lookups here.

    It does **not** perform any resolution:

        * No spellbook lookups.
        * No existence policy decisions.
        * No DAG or graph construction.

    It only describes:

        * The raw parameter signature shape (name, position, kind, default).
        * How DI *might* satisfy it (via type-hint, SpellMap, collection).
        * Optionality and element type info for collections.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_name",
        "_position",
        "_kind",
        "_annotation",
        "_default_value",
        "_has_default",
        "_is_var_positional",
        "_is_var_keyword",
        "_is_keyword_only",
        "_is_optional",
        "_di_shape",
        "_collection_element_annotation",
        "_spellmap_default",
    ]

    def __init__(
            self,
            *,
            name: str,
            position: int,
            kind: inspect._ParameterKind,
            annotation: Any,
            default_value: Any,
            has_default: bool,
            is_var_positional: bool,
            is_var_keyword: bool,
            is_keyword_only: bool,
            is_optional: bool,
            di_shape: ParameterDIShape,
            collection_element_annotation: Any = None,
            spellmap_default: Optional[SpellMap] = None,
    ) -> None:
        Cleanable.__init__(self)

        if not name:
            raise ValueError("Parameter name must be a non-empty string.")

        self._lock: threading.RLock = threading.RLock()

        self._name: str = name
        self._position: int = position
        self._kind: inspect._ParameterKind = kind
        self._annotation: Any = annotation
        self._default_value: Any = default_value
        self._has_default: bool = has_default
        self._is_var_positional: bool = is_var_positional
        self._is_var_keyword: bool = is_var_keyword
        self._is_keyword_only: bool = is_keyword_only
        self._is_optional: bool = is_optional
        self._di_shape: ParameterDIShape = di_shape
        self._collection_element_annotation: Any = collection_element_annotation
        self._spellmap_default: Optional[SpellMap] = spellmap_default

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically tear down this requirement descriptor.

        We do **not** mutate any external state or the original callable; we
        only drop references held by this object so it can be GC'ed cleanly.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._name = None
            self._position = -1
            self._kind = None
            self._annotation = None
            self._default_value = None
            self._has_default = False
            self._is_var_positional = False
            self._is_var_keyword = False
            self._is_keyword_only = False
            self._is_optional = False
            self._di_shape = None
            self._collection_element_annotation = None
            self._spellmap_default = None
            self._cleaned = True

        self._lock = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        self.check_cleaned()
        return self._name

    @property
    def position(self) -> int:
        self.check_cleaned()
        return self._position

    @property
    def kind(self) -> inspect._ParameterKind:
        self.check_cleaned()
        return self._kind

    @property
    def annotation(self) -> Any:
        """
        The **effective** annotation object as seen on the callable.

        This may still be a ``typing`` object, a bare class, a string
        (if ``from __future__ import annotations`` is used), or something else.
        No attempt is made here to "resolve" it.
        """
        self.check_cleaned()
        return self._annotation

    @property
    def default_value(self) -> Any:
        """
        Raw default value from the signature, if present.

        For DI classification, the important special case is when this is a
        :class:`SpellMap`, in which case :attr:`di_shape` will be
        :data:`ParameterDIShape.SPELLMAP_DEFAULT`.
        """
        self.check_cleaned()
        return self._default_value

    @property
    def has_default(self) -> bool:
        self.check_cleaned()
        return self._has_default

    @property
    def is_var_positional(self) -> bool:
        self.check_cleaned()
        return self._is_var_positional

    @property
    def is_var_keyword(self) -> bool:
        self.check_cleaned()
        return self._is_var_keyword

    @property
    def is_keyword_only(self) -> bool:
        self.check_cleaned()
        return self._is_keyword_only

    @property
    def is_optional(self) -> bool:
        """
        True if the parameter is **logically optional** from a DI perspective.

        This is inferred from annotation forms like ``Optional[T]`` or
        ``Union[T, None]`` or ``T | None``.

        Note:
            This says nothing about how overrides behave; it's just what the
            callable's signature implies.
        """
        self.check_cleaned()
        return self._is_optional

    @property
    def di_shape(self) -> ParameterDIShape:
        """
        How DI is expected to satisfy this parameter (if at all).

        See :class:`ParameterDIShape` for semantics.
        """
        self.check_cleaned()
        return self._di_shape

    @property
    def collection_element_annotation(self) -> Any:
        """
        If :attr:`di_shape` is :data:`ParameterDIShape.COLLECTION_BY_ANNOTATION`,
        this holds the element annotation (e.g. ``IMyHandler`` for
        ``list[IMyHandler]``).

        Otherwise this is ``None``.
        """
        self.check_cleaned()
        return self._collection_element_annotation

    @property
    def spellmap_default(self) -> Optional[SpellMap]:
        """
        If :attr:`di_shape` is :data:`ParameterDIShape.SPELLMAP_DEFAULT`, this
        holds the default :class:`SpellMap` instance.

        Otherwise this is ``None``.
        """
        self.check_cleaned()
        return self._spellmap_default
