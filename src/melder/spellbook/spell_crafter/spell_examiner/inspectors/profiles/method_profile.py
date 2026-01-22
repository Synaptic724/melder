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
        self.name = name
        self.qualname = qualname
        self.module = module
        self.id = id
        self.type = type
        self.repr = repr
        self.builtin_mod = builtin_mod
        self.extension_mod = extension_mod
        self.file = file
        self.preview = preview
        self.src_offset = src_offset
        self.start_line = start_line
        self.end_line = end_line
        self.source_text = source_text
        self.signature = signature
        self.parameters = list(parameters) if parameters is not None else []
        self.uninspectable = uninspectable
        self.func = func
        self.method = method
        self.builtin = builtin
        self.classmethod = classmethod
        self.staticmethod = staticmethod
        self.generator = generator
        self.async_gen = async_gen
        self.coroutine = coroutine
        self.lambda_fn = lambda_fn
        self.abstract = abstract
        self.closure = list(closure) if closure is not None else None
        self.decorated = decorated
        self.wrapped_repr = wrapped_repr
        self.docstring_raw = docstring_raw
        self.docstring_summary = docstring_summary
        self.behavior_summary = behavior_summary
        self.tags = list(tags) if tags is not None else []

    def cleanup(self) -> None:
        """
        Idempotently clear owned data and references.

        Contract:
            - Clears lists/dicts and nulls all fields after cleanup.
        """
        if self._cleaned:
            return
        if isinstance(self.parameters, list):
            self.parameters.clear()
        if isinstance(self.closure, list):
            self.closure.clear()
        self.name = None
        self.qualname = None
        self.module = None
        self.id = None
        self.type = None
        self.repr = None
        self.builtin_mod = None
        self.extension_mod = None
        self.file = None
        self.preview = None
        self.src_offset = None
        self.start_line = None
        self.end_line = None
        self.source_text = None
        self.signature = None
        self.parameters = None
        self.uninspectable = None
        self.func = None
        self.method = None
        self.builtin = None
        self.classmethod = None
        self.staticmethod = None
        self.generator = None
        self.async_gen = None
        self.coroutine = None
        self.lambda_fn = None
        self.abstract = None
        self.closure = None
        self.decorated = None
        self.wrapped_repr = None
        self.docstring_raw = None
        self.docstring_summary = None
        self.behavior_summary = None
        self.tags = None
        self._cleaned = True
