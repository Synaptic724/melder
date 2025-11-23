from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class SpellBindingKind(Enum):
    """
    High-level classification of what is being bound.

    This is intentionally small and orthogonal to SpellType – it answers
    "what raw object did the user give us" *before* we project into SpellType.
    """

    CLASS = auto()
    CALLABLE = auto()
    INSTANCE = auto()
    OTHER = auto()


@dataclass
class SpellBindingProfile:
    """
    Root base class for all binding profiles.

    Binding profiles are:
        * Lightweight.
        * Computed at bind-time.
        * Only contain what is needed to:
            - derive a deterministic fingerprint,
            - enforce binding rules,
            - choose SpellType.

    They do NOT contain deep DI semantics or AI-oriented metadata.
    """

    kind: SpellBindingKind
    original_object: Any


@dataclass
class ClassBindingProfile(SpellBindingProfile):
    """
    Binding-time view of a class candidate.

    This is enough to:
        * fingerprint deterministically,
        * reason about Protocol compatibility,
        * enforce basic binding rules,
        * produce nice diagnostics.

    It intentionally avoids per-method heavy inspection.
    """

    name: str
    qualname: str
    module: str

    bases: List[str] = field(default_factory=list)
    mro: List[str] = field(default_factory=list)
    annotations: Dict[str, Any] = field(default_factory=dict)

    origin_file: Optional[str] = None
    origin_line: Optional[int] = None
    source_preview: Optional[str] = None

    is_dataclass: bool = False
    decorated: bool = False

    # Very shallow method view – just names, not full signatures.
    method_names: List[str] = field(default_factory=list)


@dataclass
class CallableParameterBindingSummary:
    """
    Minimal, binding-time view of a single callable parameter.

    The goal is to have enough information for:
        * fingerprinting,
        * basic diagnostics,
        * (optionally) future heuristics,
    without doing deep DI classification (that's ResolutionProfile's job).
    """

    name: str
    kind: str
    default_repr: Optional[str]
    annotation_repr: Optional[str]


@dataclass
class CallableBindingProfile(SpellBindingProfile):
    """
    Binding-time view of a function / method / lambda spell candidate.
    """

    name: str
    qualname: Optional[str]
    module: Optional[str]
    object_id: int
    type_name: str
    repr_string: str

    signature: Optional[str]
    parameters: List[CallableParameterBindingSummary] = field(default_factory=list)

    builtin_module: bool = False
    extension_module: bool = False
    lambda_function: bool = False
    abstract: bool = False


@dataclass
class InstanceBindingProfile(SpellBindingProfile):
    """
    Binding-time view of an existing object instance being bound
    as an EXISTING_CREATION-style spell.
    """

    type_name: str
    module: str
    repr_string: str


@dataclass
class OtherBindingProfile(SpellBindingProfile):
    """
    Fallback binding profile for anything that does not fit the normal
    class / callable / instance shapes.

    Provided for completeness and better error messages.
    """

    type_name: str
    module: str
    repr_string: str
