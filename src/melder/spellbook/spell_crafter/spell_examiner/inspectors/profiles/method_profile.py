from typing import Any, Dict, List, Optional
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable


class MethodProfile(Cleanable):
    """
    Structured, IDE-friendly representation of MethodInspector output.

    Purpose:
        Provide a stable, serializable record of callable inspection results
        for AI profile consumption.

    Contract:
        - Mirrors MethodInspector fields without invoking user code.
        - Provenance fields are best-effort and may be None.
        - Cleanup() is idempotent and clears all owned references.
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "name",
        "qualname",
        "module",
        "id",
        "type",
        "repr",
        "builtin_mod",
        "extension_mod",
        "file",
        "preview",
        "src_offset",
        "start_line",
        "end_line",
        "source_text",
        "signature",
        "parameters",
        "uninspectable",
        "func",
        "method",
        "builtin",
        "classmethod",
        "staticmethod",
        "generator",
        "async_gen",
        "coroutine",
        "lambda_fn",
        "abstract",
        "closure",
        "decorated",
        "wrapped_repr",
        "docstring_raw",
        "docstring_summary",
        "behavior_summary",
        "tags",
    ]

    def __init__(
            self,
            *,
            name: str,
            qualname: Optional[str],
            module: Optional[str],
            id: int,
            type: str,
            repr: str,
            builtin_mod: bool,
            extension_mod: bool,
            file: Optional[str] = None,
            preview: Optional[str] = None,
            src_offset: Optional[int] = None,
            start_line: Optional[int] = None,
            end_line: Optional[int] = None,
            source_text: Optional[str] = None,
            signature: Optional[str] = None,
            parameters: Optional[List[Dict[str, Any]]] = None,
            uninspectable: bool = False,
            func: bool = False,
            method: bool = False,
            builtin: bool = False,
            classmethod: bool = False,
            staticmethod: bool = False,
            generator: bool = False,
            async_gen: bool = False,
            coroutine: bool = False,
            lambda_fn: bool = False,
            abstract: bool = False,
            closure: Optional[List[str]] = None,
            decorated: Optional[bool] = None,
            wrapped_repr: Optional[str] = None,
            docstring_raw: Optional[str] = None,
            docstring_summary: str = "",
            behavior_summary: str = "",
            tags: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize a MethodProfile snapshot.

        Args:
            name: Callable name.
            qualname: Qualified callable name.
            module: Module path for the callable.
            id: Object id for the callable.
            type: Callable type name.
            repr: Safe repr for the callable.
            builtin_mod: True if defined in a builtin module.
            extension_mod: True if defined in an extension module.
            file: Source file path when available.
            preview: Short source preview (first 5 lines) when available.
            src_offset: Starting source line number when available.
            start_line: Starting source line number (alias of src_offset).
            end_line: Ending source line number when available.
            source_text: Full source text when available.
            signature: String signature when inspectable.
            parameters: Normalized parameter list.
            uninspectable: True when signature extraction fails.
            func: True for plain functions.
            method: True for bound methods.
            builtin: True for builtin callables.
            classmethod: True when callable is a classmethod.
            staticmethod: True when callable is a staticmethod.
            generator: True for generator functions.
            async_gen: True for async generator functions.
            coroutine: True for coroutine functions.
            lambda_fn: True for lambda callables.
            abstract: True for abstract callables.
            closure: Closure cell reprs when available.
            decorated: True when wrapper decoration is detected.
            wrapped_repr: Safe repr of the wrapper callable when decorated.
            docstring_raw: Raw callable docstring.
            docstring_summary: Derived docstring summary (may be empty).
            behavior_summary: Derived behavior summary (may be empty).
            tags: Derived tag list (may be empty).
        """
        super().__init__()
        self.name: str = name
        self.qualname: Optional[str]= qualname
        self.module: Optional[str]= module
        self.id:int  = id
        self.type:str = type
        self.repr: str = repr
        self.builtin_mod: bool = builtin_mod
        self.extension_mod: bool = extension_mod
        self.file: Optional[str] = file
        self.preview: Optional[str] = preview
        self.src_offset: int = src_offset
        self.start_line: int = start_line
        self.end_line: int = end_line
        self.source_text: Optional[str] = source_text
        self.signature: Optional[str] = signature
        self.parameters: Optional[List[Dict[str, Any]]] = list(parameters) if parameters is not None else []
        self.uninspectable: bool = uninspectable
        self.func: bool = func
        self.method: bool = method
        self.builtin: bool = builtin
        self.classmethod: bool = classmethod
        self.staticmethod: bool = staticmethod
        self.generator: bool = generator
        self.async_gen: bool = async_gen
        self.coroutine: bool = coroutine
        self.lambda_fn: bool = lambda_fn
        self.abstract: bool = abstract
        self.closure: Optional[List[str]] = list(closure) if closure is not None else None
        self.decorated: Optional[bool] = decorated
        self.wrapped_repr: Optional[str] = wrapped_repr
        self.docstring_raw: Optional[str] = docstring_raw
        self.docstring_summary: str = docstring_summary
        self.behavior_summary: str = behavior_summary
        self.tags: Optional[List[str]] = list(tags) if tags is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear owned data and references.

        Contract:
            - Clears owned parameter/closure lists before nulling references.
            - Drops detached signature, provenance, docstring, and tag data
              without touching any live callable object.
            - Leaves the profile unusable after cleanup.
        """
        if self._cleaned:
            return
        if isinstance(self.parameters, list):
            self.parameters.clear()
        if isinstance(self.closure, list):
            self.closure.clear()
        self._cleaned = True

        if isinstance(self.tags, list):
            self.tags.clear()
        del self.name
        del self.qualname
        del self.module
        del self.id
        del self.type
        del self.repr
        del self.builtin_mod
        del self.extension_mod
        del self.file
        del self.preview
        del self.src_offset
        del self.start_line
        del self.end_line
        del self.source_text
        del self.signature
        del self.parameters
        del self.uninspectable
        del self.func
        del self.method
        del self.builtin
        del self.classmethod
        del self.staticmethod
        del self.generator
        del self.async_gen
        del self.coroutine
        del self.lambda_fn
        del self.abstract
        del self.closure
        del self.decorated
        del self.wrapped_repr
        del self.docstring_raw
        del self.docstring_summary
        del self.behavior_summary
        del self.tags
