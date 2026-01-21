from typing import Any, Dict, List, Optional
# Melder Imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable


class MethodProfile(Cleanable):
    """Structured, IDE-friendly representation of MethodInspector output."""
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
    ) -> None:
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

    def cleanup(self) -> None:
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
        self._cleaned = True
