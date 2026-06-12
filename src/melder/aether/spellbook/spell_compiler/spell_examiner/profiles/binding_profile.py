import inspect
from enum import Enum, auto
from typing import Any, Dict, List, Optional, ClassVar



# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

class SpellBindingKind(Enum):
    """
    High-level classification of what is being bound.

    This is intentionally small and orthogonal to SpellType - it answers
    "what raw object did the user give us" before we project into SpellType.
    """
    __melder_internal__ = _mrg.sentinel
    CLASS = auto()
    CALLABLE = auto()
    INSTANCE = auto()
    OTHER = auto()


class SpellBindingProfile(Cleanable):
    """
    Base class for all binding profiles.

    Contract:
        - Stores the high-level binding kind and original candidate object.
        - Leaves subtype-specific detail fields to concrete binding-profile
          variants.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["kind", "original_object"]

    def __init__(self, kind: SpellBindingKind, original_object: Any) -> None:
        """
        Initialize the shared binding-profile base state.

        Args:
            kind:
                High-level binding classification for the candidate object.
            original_object:
                Original raw candidate object being profiled.

        Returns:
            None.
        """
        super().__init__()
        self.kind: SpellBindingKind = kind
        self.original_object: Any = original_object

    def cleanup(self) -> None:
        """
        Idempotently clear the shared binding-profile base state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True

        del self.kind
        del self.original_object



class ClassBindingProfile(SpellBindingProfile):
    """
    Binding-time view of a class candidate.

    Enough to fingerprint, reason about protocol compatibility, and produce diagnostics.
    Very shallow per-method view (names only), no deep inspection.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = SpellBindingProfile.__slots__ + [
        "name",
        "qualname",
        "module",
        "bases",
        "mro",
        "annotations",
        "origin_file",
        "origin_line",
        "init_signature",
        "init_signature_object",
        "_source_preview_value",
        "_source_preview_loaded",
        "is_dataclass",
        "decorated",
        "method_names",
    ]

    def __init__(
            self,
            *,
            kind: SpellBindingKind,
            original_object: Any,
            name: str,
            qualname: str,
            module: str,
            bases: Optional[List[str]] = None,
            mro: Optional[List[str]] = None,
            annotations: Optional[Dict[str, Any]] = None,
            origin_file: Optional[str] = None,
            origin_line: Optional[int] = None,
            init_signature: Optional[str] = None,
            init_signature_object: Optional[Any] = None,
            source_preview: Optional[str] = None,
            is_dataclass: bool = False,
            decorated: bool = False,
            method_names: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize one class binding profile.

        Args:
            kind:
                High-level binding kind for the candidate.
            original_object:
                Original raw class object.
            name:
                Class name.
            qualname:
                Qualified class name.
            module:
                Declaring module name.
            bases:
                Base-class names.
            mro:
                Method-resolution-order names.
            annotations:
                Detached annotation snapshot.
            origin_file:
                Optional source file path.
            origin_line:
                Optional source line number.
            init_signature:
                Optional constructor signature string (`str(inspect.signature(cls))`).
                Part of the v4 fingerprint: constructor-shape changes must
                change the spell id so stale cache bundles cannot full-hit.
            source_preview:
                Optional truncated source preview. When omitted, the preview
                is read lazily from `original_object` on first access
                (descriptor/diagnostic consumers only); the bind hot path
                never pays the source-file read.
            is_dataclass:
                Whether the class is a dataclass.
            decorated:
                Whether the class appears decorated.
            method_names:
                Detached method-name list.

        Returns:
            None.
        """
        super().__init__(kind=kind, original_object=original_object)
        self.name: str = name
        self.qualname: str = qualname
        self.module: str = module
        self.bases: List[str] = list(bases) if bases is not None else []
        self.mro: List[str] = list(mro) if mro is not None else []
        self.annotations: Dict[str, Any] = dict(annotations) if annotations is not None else {}
        self.origin_file: Optional[str] = origin_file
        self.origin_line: Optional[int] = origin_line
        self.init_signature: Optional[str] = init_signature
        # The live inspect.Signature behind `init_signature`. Immutable and
        # borrowable: the requirements finder reuses it under an identity
        # guard so each class is signature-inspected exactly once per bind.
        self.init_signature_object: Optional[Any] = init_signature_object
        self._source_preview_value: Optional[str] = source_preview
        self._source_preview_loaded: bool = source_preview is not None
        self.is_dataclass: bool = is_dataclass
        self.decorated: bool = decorated
        self.method_names: List[str] = list(method_names) if method_names is not None else []

    @property
    def source_preview(self) -> Optional[str]:
        """
        Return the truncated class source preview, reading it lazily.

        Contract:
            - First access without an explicit constructor value reads the
              first 5 source lines of `original_object` (same shape the
              eager builder used to produce) and caches the result.
            - Unreadable sources (builtins, REPL classes, frozen modules)
              cache None instead of raising.
            - Concurrent first reads are benign: the computation is
              idempotent and the last writer wins with an identical value.
        """
        if self._source_preview_loaded:
            return self._source_preview_value
        preview: Optional[str] = None
        try:
            lines, _ = inspect.getsourcelines(self.original_object)
            preview = "".join(lines[:5]).strip()
        except Exception:
            preview = None
        self._source_preview_value = preview
        self._source_preview_loaded = True
        return preview

    def cleanup(self) -> None:
        """
        Idempotently clear the class binding profile and owned detail state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        for lst in (self.bases, self.mro, self.method_names):
            if isinstance(lst, list):
                lst.clear()
        if isinstance(self.annotations, dict):
            self.annotations.clear()

        del self.origin_file
        del self.origin_line
        del self.init_signature
        del self.init_signature_object
        del self._source_preview_value
        del self._source_preview_loaded
        del self.is_dataclass
        del self.decorated
        del self.name
        del self.qualname
        del self.module
        del self.bases
        del self.mro
        del self.annotations
        del self.method_names
        super().cleanup()


class CallableParameterBindingSummary:
    """
    Minimal binding-time view of a single callable parameter (for fingerprint/diagnostics).
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = ["name", "kind", "default_repr", "annotation_repr"]

    def __init__(
            self,
            name: str,
            kind: str,
            default_repr: Optional[str],
            annotation_repr: Optional[str],
    ) -> None:
        """
        Initialize one minimal callable-parameter binding summary.

        Args:
            name:
                Parameter name.
            kind:
                Parameter kind label.
            default_repr:
                Optional default-value representation.
            annotation_repr:
                Optional annotation representation.

        Returns:
            None.
        """
        self.name: str = name
        self.kind: str = kind
        self.default_repr: Optional[str] = default_repr
        self.annotation_repr: Optional[str] = annotation_repr


class CallableBindingProfile(SpellBindingProfile):
    """
    Binding-time view of a function, method, or lambda spell candidate.

    Contract:
        - Stores callable identity, signature, and shallow parameter
          summaries.
        - Avoids deeper runtime-resolution detail, which belongs to later
          profile phases.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = SpellBindingProfile.__slots__ + [
        "name",
        "qualname",
        "module",
        "object_id",
        "type_name",
        "repr_string",
        "signature",
        "parameters",
        "builtin_module",
        "extension_module",
        "lambda_function",
        "abstract",
    ]

    def __init__(
            self,
            *,
            kind: SpellBindingKind,
            original_object: Any,
            name: str,
            qualname: Optional[str],
            module: Optional[str],
            object_id: int,
            type_name: str,
            repr_string: str,
            signature: Optional[str],
            parameters: Optional[List[CallableParameterBindingSummary]] = None,
            builtin_module: bool = False,
            extension_module: bool = False,
            lambda_function: bool = False,
            abstract: bool = False,
    ) -> None:
        """
        Initialize one callable binding profile.

        Args:
            kind:
                High-level binding kind for the candidate.
            original_object:
                Original raw callable object.
            name:
                Callable name.
            qualname:
                Optional qualified callable name.
            module:
                Optional declaring module name.
            object_id:
                Runtime object id.
            type_name:
                Callable type name.
            repr_string:
                Detached representation string.
            signature:
                Optional callable signature string.
            parameters:
                Optional detached parameter summaries.
            builtin_module:
                Whether the callable comes from a builtin module.
            extension_module:
                Whether the callable comes from an extension module.
            lambda_function:
                Whether the callable is a lambda.
            abstract:
                Whether the callable appears abstract.

        Returns:
            None.
        """
        super().__init__(kind=kind, original_object=original_object)
        self.name: str = name
        self.qualname: Optional[str] = qualname
        self.module: Optional[str] = module
        self.object_id: int = object_id
        self.type_name: str = type_name
        self.repr_string: str = repr_string
        self.signature: Optional[str] = signature
        self.parameters: Optional[List[CallableParameterBindingSummary]] = list(parameters) if parameters is not None else []
        self.builtin_module: bool = builtin_module
        self.extension_module: bool = extension_module
        self.lambda_function: bool = lambda_function
        self.abstract: bool = abstract

    def cleanup(self) -> None:
        """
        Idempotently clear the callable binding profile and owned summaries.

        Returns:
            None.
        """
        if self._cleaned:
            return
        if isinstance(self.parameters, list):
            self.parameters.clear()

        del self.name
        del self.qualname
        del self.module
        del self.object_id
        del self.type_name
        del self.repr_string
        del self.signature
        del self.parameters
        del self.builtin_module
        del self.extension_module
        del self.lambda_function
        del self.abstract

        super().cleanup()


class InstanceBindingProfile(SpellBindingProfile):
    """
    Binding-time view of an existing object instance bound as an EXISTING_CREATION spell.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = SpellBindingProfile.__slots__ + [
        "type_name",
        "module",
        "repr_string",
    ]

    def __init__(
            self,
            *,
            kind: SpellBindingKind,
            original_object: Any,
            type_name: str,
            module: str,
            repr_string: str,
    ) -> None:
        """
        Initialize one instance binding profile.

        Args:
            kind:
                High-level binding kind for the candidate.
            original_object:
                Original raw instance object.
            type_name:
                Runtime type name.
            module:
                Declaring module name.
            repr_string:
                Detached representation string.

        Returns:
            None.
        """
        super().__init__(kind=kind, original_object=original_object)
        self.type_name: str = type_name
        self.module: str = module
        self.repr_string: str = repr_string

    def cleanup(self) -> None:
        """
        Idempotently clear the instance binding profile.

        Returns:
            None.
        """
        if self._cleaned:
            return

        del self.type_name
        del self.module
        del self.repr_string

        super().cleanup()


class OtherBindingProfile(SpellBindingProfile):
    """
    Fallback binding profile for anything that does not fit normal shapes.

    Contract:
        Stores only the minimum detached identity/representation surface for
        otherwise unsupported candidate types.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = SpellBindingProfile.__slots__ + [
        "type_name",
        "module",
        "repr_string",
    ]

    def __init__(
            self,
            *,
            kind: SpellBindingKind,
            original_object: Any,
            type_name: str,
            module: str,
            repr_string: str,
    ) -> None:
        """
        Initialize one fallback binding profile.

        Args:
            kind:
                High-level binding kind for the candidate.
            original_object:
                Original raw object.
            type_name:
                Runtime type name.
            module:
                Declaring module name.
            repr_string:
                Detached representation string.

        Returns:
            None.
        """
        super().__init__(kind=kind, original_object=original_object)
        self.type_name: str = type_name
        self.module: str = module
        self.repr_string: str = repr_string

    def cleanup(self) -> None:
        """
        Idempotently clear the fallback binding profile.

        Returns:
            None.
        """
        if self._cleaned:
            return
        del self.type_name
        del self.module
        del self.repr_string
        super().cleanup()
