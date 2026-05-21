import inspect
import threading
from typing import TYPE_CHECKING, Any, Optional

from mypy_extensions import mypyc_attr

# Melder imports
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.conduit.meld.contracts.spell_map import SpellMap
@mypyc_attr(native_class=True)
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
        """
        Initialize one phase-1 parameter requirement descriptor.

        Args:
            name:
                Parameter name from the inspected signature.
            position:
                Positional index within the inspected callable signature.
            kind:
                Raw `inspect.Parameter.kind` value.
            annotation:
                Effective annotation object for the parameter.
            default_value:
                Raw default value from the signature.
            has_default:
                Whether the signature exposes a default value.
            is_var_positional:
                Whether the parameter is `*args`.
            is_var_keyword:
                Whether the parameter is `**kwargs`.
            is_keyword_only:
                Whether the parameter is keyword-only.
            is_optional:
                Whether the parameter is logically optional from the DI point
                of view.
            di_shape:
                Phase-1 DI classification for the parameter.
            collection_element_annotation:
                Optional collection element annotation when the parameter
                expects a collection.
            spellmap_default:
                Optional default `SpellMap` when the parameter uses the
                explicit spell-map shape.

        Returns:
            None.
        """
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
            self._cleaned = True
            self._position = -1
            self._has_default = False
            self._is_var_positional = False
            self._is_var_keyword = False
            self._is_keyword_only = False
            self._is_optional = False

            del self._name
            del self._kind
            del self._annotation
            del self._default_value
            del self._di_shape
            del self._collection_element_annotation
            del self._spellmap_default
        del self._lock

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """
        Return the parameter name from the inspected signature.
        """
        self.check_cleaned()
        return self._name

    @property
    def position(self) -> int:
        """
        Return the parameter's positional index within the inspected signature.
        """
        self.check_cleaned()
        return self._position

    @property
    def kind(self) -> inspect._ParameterKind:
        """
        Return the raw `inspect.Parameter.kind` classification.
        """
        self.check_cleaned()
        return self._kind

    @property
    def annotation(self) -> Any:
        """
        The **effective** annotation object as seen on the callable.

        This may be a ``typing`` object, a bare class, or a string if
        forward references could not be resolved. Phase 1 attempts to
        resolve forward references so DI can match real types.
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
        """
        Return whether the parameter exposes a default value in the signature.
        """
        self.check_cleaned()
        return self._has_default

    @property
    def is_var_positional(self) -> bool:
        """
        Return whether the parameter represents `*args`.
        """
        self.check_cleaned()
        return self._is_var_positional

    @property
    def is_var_keyword(self) -> bool:
        """
        Return whether the parameter represents `**kwargs`.
        """
        self.check_cleaned()
        return self._is_var_keyword

    @property
    def is_keyword_only(self) -> bool:
        """
        Return whether the parameter is keyword-only.
        """
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
