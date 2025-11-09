from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class MethodProfile:
    """Structured, IDE-friendly representation of MethodInspector output."""
    # Required fields
    name: str
    qualname: Optional[str]
    module: Optional[str]
    id: int
    type: str
    repr: str
    builtin_mod: bool
    extension_mod: bool

    # Optional / defaulted
    file: Optional[str] = None
    preview: Optional[str] = None
    src_offset: Optional[int] = None
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    uninspectable: bool = False

    # Callable trait flags – default to False
    func: bool = False
    method: bool = False
    builtin: bool = False
    classmethod: bool = False
    staticmethod: bool = False
    generator: bool = False
    async_gen: bool = False
    coroutine: bool = False
    lambda_fn: bool = False
    abstract: bool = False

    # Advanced details
    closure: Optional[List[str]] = None
    decorated: Optional[bool] = None
    wrapped_repr: Optional[str] = None
