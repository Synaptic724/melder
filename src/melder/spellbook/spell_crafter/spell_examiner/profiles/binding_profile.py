from __future__ import annotations
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


class SpellBindingKind(Enum):
    """
    High-level classification of what is being bound.

    This is intentionally small and orthogonal to SpellType – it answers
    "what raw object did the user give us" before we project into SpellType.
    """

    CLASS = auto()
    CALLABLE = auto()
    INSTANCE = auto()
    OTHER = auto()


class SpellBindingProfile(Cleanable):
    """Base class for all binding profiles."""

    __slots__ = Cleanable.__slots__ + ["kind", "original_object"]

    def __init__(self, kind: SpellBindingKind, original_object: Any) -> None:
        super().__init__()
        self.kind = kind
        self.original_object = original_object

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.kind = None
        self.original_object = None
        self._cleaned = True


class ClassBindingProfile(SpellBindingProfile):
    """
    Binding-time view of a class candidate.

    Enough to fingerprint, reason about protocol compatibility, and produce diagnostics.
    Very shallow per-method view (names only), no deep inspection.
    """

    __slots__ = SpellBindingProfile.__slots__ + [
        "name",
        "qualname",
        "module",
        "bases",
        "mro",
        "annotations",
        "origin_file",
        "origin_line",
        "source_preview",
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
            source_preview: Optional[str] = None,
            is_dataclass: bool = False,
            decorated: bool = False,
            method_names: Optional[List[str]] = None,
    ) -> None:
        super().__init__(kind=kind, original_object=original_object)
        self.name = name
        self.qualname = qualname
        self.module = module
        self.bases = list(bases) if bases is not None else []
        self.mro = list(mro) if mro is not None else []
        self.annotations = dict(annotations) if annotations is not None else {}
        self.origin_file = origin_file
        self.origin_line = origin_line
        self.source_preview = source_preview
        self.is_dataclass = is_dataclass
        self.decorated = decorated
        self.method_names = list(method_names) if method_names is not None else []

    def cleanup(self) -> None:
        if self._cleaned:
            return
        for lst in (self.bases, self.mro, self.method_names):
            if isinstance(lst, list):
                lst.clear()
        if isinstance(self.annotations, dict):
            self.annotations.clear()
        self.origin_file = None
        self.origin_line = None
        self.source_preview = None
        self.is_dataclass = None
        self.decorated = None
        self.name = None
        self.qualname = None
        self.module = None
        self.bases = None
        self.mro = None
        self.annotations = None
        self.method_names = None
        super().cleanup()


class CallableParameterBindingSummary:
    """
    Minimal binding-time view of a single callable parameter (for fingerprint/diagnostics).
    """

    __slots__ = ["name", "kind", "default_repr", "annotation_repr"]

    def __init__(
            self,
            name: str,
            kind: str,
            default_repr: Optional[str],
            annotation_repr: Optional[str],
    ) -> None:
        self.name = name
        self.kind = kind
        self.default_repr = default_repr
        self.annotation_repr = annotation_repr


class CallableBindingProfile(SpellBindingProfile):
    """Binding-time view of a function / method / lambda spell candidate."""

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
        super().__init__(kind=kind, original_object=original_object)
        self.name = name
        self.qualname = qualname
        self.module = module
        self.object_id = object_id
        self.type_name = type_name
        self.repr_string = repr_string
        self.signature = signature
        self.parameters = list(parameters) if parameters is not None else []
        self.builtin_module = builtin_module
        self.extension_module = extension_module
        self.lambda_function = lambda_function
        self.abstract = abstract

    def cleanup(self) -> None:
        if self._cleaned:
            return
        if isinstance(self.parameters, list):
            self.parameters.clear()
        self.name = None
        self.qualname = None
        self.module = None
        self.object_id = None
        self.type_name = None
        self.repr_string = None
        self.signature = None
        self.parameters = None
        self.builtin_module = None
        self.extension_module = None
        self.lambda_function = None
        self.abstract = None
        super().cleanup()


class InstanceBindingProfile(SpellBindingProfile):
    """
    Binding-time view of an existing object instance bound as an EXISTING_CREATION spell.
    """

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
        super().__init__(kind=kind, original_object=original_object)
        self.type_name = type_name
        self.module = module
        self.repr_string = repr_string

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.type_name = None
        self.module = None
        self.repr_string = None
        super().cleanup()


class OtherBindingProfile(SpellBindingProfile):
    """Fallback binding profile for anything that does not fit normal shapes."""

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
        super().__init__(kind=kind, original_object=original_object)
        self.type_name = type_name
        self.module = module
        self.repr_string = repr_string

    def cleanup(self) -> None:
        if self._cleaned:
            return
        self.type_name = None
        self.module = None
        self.repr_string = None
        super().cleanup()
