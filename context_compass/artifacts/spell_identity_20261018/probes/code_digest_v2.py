"""Prototype (melder_0, 2026-10-18; STORY-2026-10-18-spell_id_hashes_the_object_code): the code digest v2.

Not in src/. It extends probe_code_hash_prototype.py with the owner's calls of 2026-10-18:
  (1) a class's identity includes the code of the classes it inherits from;
  (2) class-level values are code ("a change anywhere is a change");
  (3) an existing object is its class's code plus its data.
Local variable names are counted (call 4, pending; counted by default).

The rules, in one place (the code-description patch states them as the contract):
  - A function: its code object (the deoptimized instruction stream with each loaded constant by value, argument
    counts, flags without CO_HAS_DOCSTRING, name tables, exception table), its defaults, its annotations (the code
    of its __annotate__), its closure values, its type parameters and its __dict__ (minus __wrapped__).
    Never: line numbers, the docstring constant, unused constants, the file path.
  - A class: module, qualname, metaclass, direct bases and, for every class in its MRO, either that class's
    own namespace digest (code outside the standard library) or its qualified name (the standard library and
    builtins). A namespace digest covers every entry of the class __dict__ except interpreter bookkeeping
    (__module__, __qualname__, __doc__, __dict__, __weakref__, __firstlineno__, __static_attributes__,
    __annotations_cache__); _abc_impl is opaque.
  - Values: builtin scalars and containers by value (sets sorted, dicts in insertion order); enum members by
    class, name and value; classes by qualified name unless nested in the class being digested (then digested);
    functions by code; typing objects by their text; known value types (datetime, Decimal, UUID, paths, regex
    patterns, ranges, slices) by repr; standard-library and Melder objects by type only; user objects by type and
    data (slots, then __dict__; cached_property values skipped); C objects without data by type; cycles marked.
  - The bound object itself: a class -> class digest; a function -> its module, qualname and encoding; a user
    object -> its class digest plus its data; a standard-library object -> its type plus its address-free repr
    (as bind does today).
"""
import dis
import enum
import functools
import hashlib
import inspect
import re
import struct
import sys
import types
import typing
import weakref
import annotationlib
import datetime
import decimal
import fractions
import ipaddress
import pathlib
import uuid
from typing import Any, List, Optional


class CodeDigest:
    """One digest service; memoizes code-object digests (code objects are immutable), never class digests."""

    TAG = "melder-code-digest/v2"
    ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")
    EXCLUDED_CLASS_KEYS = frozenset({
        "__module__", "__qualname__", "__doc__", "__dict__", "__weakref__", "__firstlineno__",
        "__static_attributes__", "__annotations_cache__",
    })
    OPAQUE_CLASS_KEYS = frozenset({"_abc_impl"})
    REPR_VALUE_TYPES = (
        datetime.date, datetime.time, datetime.timedelta, datetime.tzinfo, decimal.Decimal, fractions.Fraction,
        uuid.UUID, pathlib.PurePath, re.Pattern, range, slice, ipaddress.IPv4Address, ipaddress.IPv6Address,
        ipaddress.IPv4Network, ipaddress.IPv6Network,
    )
    SCALAR_TYPES = (bool, int, float, complex, str, bytes, bytearray)
    BUILTIN_CALLABLE_TYPES = (
        types.BuiltinFunctionType, types.MethodDescriptorType, types.WrapperDescriptorType,
        types.MethodWrapperType, types.ClassMethodDescriptorType, types.GetSetDescriptorType,
        types.MemberDescriptorType,
    )
    STDLIB = frozenset(sys.stdlib_module_names)
    LOAD_CONST = dis.opmap["LOAD_CONST"]
    EXTENDED_ARG = dis.opmap["EXTENDED_ARG"]

    def __init__(self) -> None:
        self._code_memo: "weakref.WeakKeyDictionary[types.CodeType, str]" = weakref.WeakKeyDictionary()

    # ---------------------------------------------------------------- targets
    def spell_id(self, target: Any) -> str:
        """The prototype spell_id: TAG, interpreter tag and the target's encoding, hashed."""
        return self._sha("\n".join([self.TAG, sys.implementation.cache_tag, self.target_encoding(target)]))

    def target_encoding(self, target: Any) -> str:
        """Encode the bound object itself (class, function, or object)."""
        if inspect.isclass(target):
            return "class " + self.class_digest(target, set())
        if isinstance(target, types.FunctionType):
            # Like a class, a function target is named where it is defined: module and qualname, then its code.
            return "function " + str(target.__module__) + " " + target.__qualname__ + " " + self._function(
                target, set(), None)
        if isinstance(target, (types.MethodType, functools.partial, enum.Enum, tuple, list, set, frozenset, dict)
                      + self.SCALAR_TYPES + self.BUILTIN_CALLABLE_TYPES):
            return "value " + self.encode(target, set(), None)
        if self._is_user_object(target):
            return "object " + self._object(target, set(), None, top=True)
        if self._is_library_object(target):
            return "library " + self._qualified(type(target)) + " " + self.ADDRESS.sub("", repr(target))
        return "value " + self.encode(target, set(), None)

    # ---------------------------------------------------------------- classes
    def class_digest(self, cls: type, path: set) -> str:
        """Header, direct bases, metaclass and the MRO: own namespace digests for user code, names otherwise."""
        if id(cls) in path:
            return "cycle:" + self._qualified(cls)
        path = path | {id(cls)}
        lines = [
            "module " + cls.__module__, "qualname " + cls.__qualname__,
            "meta " + self._class_ref_or_digest(type(cls), path),
            "bases " + ",".join(self._qualified(base) for base in cls.__bases__),
        ]
        for klass in cls.__mro__:
            if klass is cls:
                lines.append("own " + self._namespace_digest(cls, path))
            elif self._is_library_class(klass):
                lines.append("mro " + self._qualified(klass))
            else:
                lines.append("mro " + self._qualified(klass) + " " + self._namespace_digest(klass, path))
        return self._sha("\n".join(lines))

    def _namespace_digest(self, cls: type, path: set) -> str:
        lines = []
        for name, value in cls.__dict__.items():
            if name in self.EXCLUDED_CLASS_KEYS:
                continue
            if name in self.OPAQUE_CLASS_KEYS:
                lines.append(name + "=opaque:" + self._qualified(type(value)))
                continue
            lines.append(name + "=" + self.encode(value, path, cls))
        lines.sort()
        return self._sha("\n".join(lines))

    def _class_ref_or_digest(self, cls: type, path: set) -> str:
        if self._is_library_class(cls):
            return self._qualified(cls)
        return self._qualified(cls) + ":" + self.class_digest(cls, path)

    # ---------------------------------------------------------------- functions
    def _function(self, fn: types.FunctionType, path: set, owner: Optional[type]) -> str:
        if id(fn) in path:
            return "cycle:fn"
        path = path | {id(fn)}
        parts = ["fn " + str(fn.__module__) + ":" + fn.__name__, "code " + self.code_digest(fn.__code__),
                 "defaults " + self.encode(fn.__defaults__, path, owner),
                 "kwdefaults " + self.encode(fn.__kwdefaults__, path, owner)]
        annotate = fn.__annotate__
        if isinstance(annotate, types.FunctionType):
            parts.append("annotate " + self._function(annotate, path, owner))
        if fn.__closure__:
            for name, cell in zip(fn.__code__.co_freevars, fn.__closure__):
                if name == "__classdict__":
                    # An annotate function's view of the class body namespace (docstring included): the class
                    # namespace is encoded on its own, so the cell is a marker, never its contents.
                    parts.append("cell __classdict__=<class namespace>")
                    continue
                try:
                    contents = cell.cell_contents
                except ValueError:
                    parts.append("cell " + name + "=<empty>")
                    continue
                parts.append("cell " + name + "=" + self.encode(contents, path, owner))
        if fn.__type_params__:
            parts.append("type_params " + self.encode(fn.__type_params__, path, owner))
        extra = {key: value for key, value in fn.__dict__.items() if key != "__wrapped__"}
        if extra:
            parts.append("dict " + self.encode(extra, path, owner))
        return self._sha("\n".join(parts))

    def code_digest(self, code: types.CodeType) -> str:
        """The code object's instruction stream and name tables; no line numbers, no docstring, no file path.

        The stream is the deoptimized bytecode (`co_code`) re-read as (opcode, argument) pairs with EXTENDED_ARG
        folded in. A LOAD_CONST argument is replaced by the order in which the stream first uses that constant, and
        the used constants are hashed in that order (canonical text; nested code by its own digest). So a constant
        no instruction loads - the docstring 3.14 keeps in co_consts[0] (CO_HAS_DOCSTRING), or a constant the
        optimizer left unused there - never counts, and the constant table's layout does not matter. The name
        tables (co_names, co_varnames, co_cellvars, co_freevars) give the other arguments their meaning.
        Memoized per code object (code objects are immutable).
        """
        cached = self._code_memo.get(code)
        if cached is not None:
            return cached
        consts, raw = code.co_consts, code.co_code
        ops, args, extended = bytearray(), [], 0
        first_use: dict = {}
        used: List[str] = []
        for index in range(0, len(raw), 2):
            op, arg = raw[index], extended | raw[index + 1]
            if op == self.EXTENDED_ARG:
                extended = arg << 8
                continue
            extended = 0
            if op == self.LOAD_CONST:
                ordinal = first_use.get(arg)
                if ordinal is None:
                    ordinal = first_use[arg] = len(used)
                    used.append(self._const(consts[arg]))
                arg = ordinal
            ops.append(op)
            args.append(arg)
        parts = [code.co_name, f"{code.co_argcount},{code.co_posonlyargcount},{code.co_kwonlyargcount}",
                 str(code.co_flags & ~inspect.CO_HAS_DOCSTRING), bytes(ops).hex(),
                 struct.pack(f"<{len(args)}I", *args).hex(), code.co_exceptiontable.hex(),
                 ",".join(code.co_names), ",".join(code.co_varnames), ",".join(code.co_cellvars),
                 ",".join(code.co_freevars), "|".join(used)]
        digest = self._sha("\n".join(parts))
        self._code_memo[code] = digest
        return digest

    def _const(self, value: Any) -> str:
        if isinstance(value, types.CodeType):
            return "code:" + self.code_digest(value)
        if isinstance(value, frozenset):
            return "frozenset(" + ",".join(sorted(self._const(item) for item in value)) + ")"
        if isinstance(value, tuple):
            return "(" + ",".join(self._const(item) for item in value) + ")"
        return self.ADDRESS.sub("", repr(value))

    # ---------------------------------------------------------------- values
    def encode(self, value: Any, path: set, owner: Optional[type]) -> str:
        """Encode one value reached from a class namespace, a function or an object's data."""
        if value is None or value is Ellipsis or value is NotImplemented:
            return repr(value)
        if isinstance(value, enum.Enum):
            return f"enum:{self._qualified(type(value))}.{value.name}={self.encode(value._value_, path, owner)}"
        if isinstance(value, self.SCALAR_TYPES):
            base = next(kind for kind in self.SCALAR_TYPES if isinstance(value, kind))
            return f"{self._qualified(type(value))}:{base.__repr__(value)}"
        if isinstance(value, (tuple, list)):
            return self._container(value, path, owner, lambda: "[" + ",".join(
                self.encode(item, path | {id(value)}, owner) for item in value) + "]")
        if isinstance(value, (set, frozenset)):
            return self._container(value, path, owner, lambda: "{" + ",".join(
                sorted(self.encode(item, path | {id(value)}, owner) for item in value)) + "}")
        if isinstance(value, (dict, types.MappingProxyType)):
            return self._container(value, path, owner, lambda: "{" + ",".join(
                self.encode(key, path | {id(value)}, owner) + ":" + self.encode(item, path | {id(value)}, owner)
                for key, item in value.items()) + "}")
        if inspect.isclass(value):
            if owner is not None and self._is_nested_in(value, owner):
                return "nested:" + self.class_digest(value, path)
            return "class:" + self._qualified(value)
        if isinstance(value, types.FunctionType):
            return "fn:" + self._function(value, path, owner)
        if isinstance(value, (staticmethod, classmethod)):
            return type(value).__name__ + "(" + self.encode(value.__func__, path, owner) + ")"
        if isinstance(value, property):
            return "property(" + ",".join(self.encode(accessor, path, owner)
                                          for accessor in (value.fget, value.fset, value.fdel)) + ")"
        if isinstance(value, functools.cached_property):
            return "cached_property(" + self.encode(value.func, path, owner) + ")"
        if isinstance(value, types.MethodType):
            return "method(" + self.encode(value.__func__, path, owner) + " of " + self.encode(
                value.__self__, path, owner) + ")"
        if isinstance(value, functools.partial):
            return "partial(" + ",".join(self.encode(part, path, owner)
                                         for part in (value.func, value.args, value.keywords)) + ")"
        if isinstance(value, types.ModuleType):
            return "module:" + value.__name__
        if isinstance(value, types.CodeType):
            return "code:" + self.code_digest(value)
        if isinstance(value, self.BUILTIN_CALLABLE_TYPES):
            holder = getattr(value, "__objclass__", None)
            return "builtin:" + (self._qualified(holder) + "." if holder is not None else "") + str(
                getattr(value, "__qualname__", getattr(value, "__name__", type(value).__name__)))
        typing_text = self._typing(value, path, owner)
        if typing_text is not None:
            return typing_text
        if isinstance(value, self.REPR_VALUE_TYPES):
            return self._qualified(type(value)) + ":" + self.ADDRESS.sub("", repr(value))
        if isinstance(value, (weakref.ref, weakref.ProxyType, weakref.CallableProxyType)):
            return "weakref:" + self._qualified(type(value))
        if self._is_library_object(value):
            return "ref:" + self._qualified(type(value))
        if self._is_user_object(value):
            return self._object(value, path, owner, top=False)
        return "opaque:" + self._qualified(type(value))

    def _container(self, value: Any, path: set, owner: Optional[type], render: Any) -> str:
        if id(value) in path:
            return "cycle:" + type(value).__name__
        return self._qualified(type(value)) + render()

    def _object(self, obj: Any, path: set, owner: Optional[type], top: bool) -> str:
        if id(obj) in path:
            return "cycle:" + self._qualified(type(obj))
        path = path | {id(obj)}
        cls = type(obj)
        head = ("objclass:" + self.class_digest(cls, path)) if top else ("obj:" + self._qualified(cls))
        fields = []
        for klass in cls.__mro__:
            slots = klass.__dict__.get("__slots__", ())
            for slot in ((slots,) if isinstance(slots, str) else slots):
                if slot in ("__dict__", "__weakref__"):
                    continue
                attribute = "_" + klass.__name__.lstrip("_") + slot if slot.startswith("__") and not slot.endswith("__") else slot
                try:
                    fields.append("slot " + slot + "=" + self.encode(object.__getattribute__(obj, attribute), path, owner))
                except AttributeError:
                    fields.append("slot " + slot + "=<unset>")
        data = obj.__dict__ if hasattr(obj, "__dict__") else {}
        for key, item in data.items():
            if isinstance(inspect.getattr_static(cls, key, None), functools.cached_property):
                continue
            fields.append("attr " + str(key) + "=" + self.encode(item, path, owner))
        return head + "{" + ";".join(fields) + "}"

    def _typing(self, value: Any, path: set, owner: Optional[type]) -> Optional[str]:
        if isinstance(value, annotationlib.ForwardRef):
            return "fwd:" + value.__forward_arg__
        if isinstance(value, (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple)):
            parts = [type(value).__name__, value.__name__]
            for flag in ("__covariant__", "__contravariant__", "__infer_variance__"):
                parts.append(str(getattr(value, flag, None)))
            for hook in ("evaluate_bound", "evaluate_constraints", "evaluate_default"):
                function = getattr(value, hook, None)
                parts.append(self.encode(function, path, owner) if function is not None else "-")
            return "typevar:" + "|".join(parts)
        if isinstance(value, typing.TypeAliasType):
            return "alias:" + value.__name__ + "|" + self.encode(value.evaluate_value, path, owner)
        if type(value).__module__ in ("typing", "types", "annotationlib"):
            return "typing:" + self.ADDRESS.sub("", repr(value))
        return None

    # ---------------------------------------------------------------- helpers
    def _is_library_module(self, module: Optional[str]) -> bool:
        return module is None or module == "builtins" or module.split(".")[0] in self.STDLIB

    def _is_library_class(self, cls: type) -> bool:
        return self._is_library_module(getattr(cls, "__module__", None))

    def _is_library_object(self, value: Any) -> bool:
        module = getattr(type(value), "__module__", None)
        return self._is_library_module(module) or (module or "").startswith("melder.")

    def _is_user_object(self, value: Any) -> bool:
        if self._is_library_object(value):
            return False
        return hasattr(value, "__dict__") or any("__slots__" in klass.__dict__ for klass in type(value).__mro__[:-1])

    @staticmethod
    def _is_nested_in(cls: type, owner: type) -> bool:
        return cls.__module__ == owner.__module__ and cls.__qualname__.startswith(owner.__qualname__ + ".")

    @staticmethod
    def _qualified(cls: Any) -> str:
        return f"{getattr(cls, '__module__', '?')}.{getattr(cls, '__qualname__', getattr(cls, '__name__', '?'))}"

    @staticmethod
    def _sha(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
