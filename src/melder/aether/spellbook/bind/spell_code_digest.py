import annotationlib
import datetime
import decimal
import dis
import enum
import fractions
import functools
import hashlib
import importlib.metadata
import inspect
import ipaddress
import os
import pathlib
import re
import site
import struct
import sys
import sysconfig
import types
import typing
import uuid
import weakref
from typing import Any, ClassVar, Dict, FrozenSet, List, Optional, Tuple

# Melder Imports
from melder.aether.spellbook.spell_compiler.spell_examiner.inspectors.inspector_utility import InspectorUtility
from melder.utilities.general_base.cleanable import Cleanable


#region SpellCodeDigest


class SpellCodeDigest(Cleanable):
    """
    Compute a registration target's spell_id: the SHA256 of its code and, for an existing object, its data.

    Purpose:
        A spell_id names WHAT was registered, never HOW it was bound (the owner, 2026-10-18: "the object's binding
        handle shouldn't be part of its SHA256 hash ... we only want to read the object registered its methods, its
        actual code not its docstrings or comments"). This class is the one place that rule lives: `Bind` asks it for
        the id of every class, function and object it registers, and `Bind.spell_id_inspector` asks it to re-derive
        the id of an object that may already be registered.

    Contract:
        - `spell_id(target)` is the SHA256 hex digest of `TAG` ("v5-code"), the interpreter's cache tag
          (`sys.implementation.cache_tag`) and the target's encoding (`target_encoding`), newline-joined. Nothing from
          the bind call - spellframe, binding name, existence, disposal names, resolvable, managed settings - enters
          it; those are the spell's `BindingManifest`, hashed separately.
        - What moves it: any real code change - a method or constructor body, a parameter, a default, an annotation,
          a class-level value, a nested class, a decorator's code, a closure's captured value, a renamed local
          variable, a base class's code outside the standard library - and an existing object's data.
        - What never moves it: docstrings, comments, blank lines, line numbers, the order a class body defines its
          members in, runtime specialization, `sys.monitoring` and `sys.settrace`, executing the same source twice,
          reading a class's annotations, `isinstance` checks and `ABC.register`.
        - Installed third-party code (decision B, the owner 2026-10-18): a class, metaclass or function whose module
          file lies under an installed site-packages directory is NAMED by its qualified name and distribution
          version, never digested; an object of such a class is its type, that version and its address-free repr.
          Application code - the project's modules, `__main__`, editable installs, a module that cannot be located -
          is digested. Melder's own objects encode by type only (`ref:`); a Melder class in an MRO is code like any
          other (digested from source, named by version when installed).
        - Deterministic: the same code, data and interpreter give the same id in every process, hash seed and GIL
          mode. Compiled instructions differ between Python minor versions and under -O, so ids are per interpreter.
        - Never raises for a target: an unknown value encodes as `opaque:<type>`, a failing repr as a placeholder,
          and data nested past the recursion limit falls back to the target's type and address-free repr.
        - Runs no target code, except `repr()` of a target with no Python-visible state, of a value type's object and
          of an installed third-party object (the calls the retired fingerprint made). Reads go through type and
          instance dictionaries, `type.__getattribute__`, `object.__getattribute__` and `inspect.getattr_static`, and
          containers are walked through their builtin base type, so a target's `__getattr__`, `__iter__` or
          `__eq__` never runs.
        - Not part of an id: code a target only names (a module-level helper its methods call, a class referenced as
          a class-level value unless nested in it). Those are other objects; when they are spells, their own ids move.

    Threading / Concurrency:
        Holds no lock. Its memos are not thread-safe, so one instance serves one caller at a time: `Bind` calls it
        under its own lock, and `Bind.spell_id_inspector` builds a fresh instance per call. Containers, instance
        dictionaries and class namespaces read from a target are copied in one call before they are walked, so a
        concurrent writer never makes a walk raise (the walk sees the data as it was at that copy).

    Lifecycle / Cleanup:
        Owns four memos and nothing else: code-object digests (weakly keyed, so an entry leaves with its code
        object), module locations, distribution versions and the import-name -> distribution map. Classes, functions
        and objects are encoded afresh at every call because they are mutable: an object is hashed as it is at bind,
        and a class-level value mutated at runtime moves the id. `cleanup()` clears and deletes the memos; it is
        idempotent, and every public method raises through `check_cleaned()` afterwards.

    Registration:
        MELDER KERNEL - guarded. Owned by `Bind` (one per Bind, cleaned with it); `Bind.spell_id_inspector` builds its
        own per call. Never bound as a spell.

    Subsystem Context:
        EPIC-2026-10-18-spell_identity_is_the_code, S1. It replaces `Bind.sha256_profile`, which hashed a shallow
        outline of the target (names and signatures, no method body) together with the bind call, so an edited method
        kept its id and one class bound under two names was two spells. Under this rule an edit is a new version an
        agent can stage and notch, and one object is one spell: the existing duplicate-id refusals refuse a second
        registration. The exact encoding is the epic's code-description patch (spell_code_digest).

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. The spell_id rule: the SHA256 of what a registered class, function or object IS - its code,
        inherited code, class-level values and an object's data - never how it was bound. Read it to know why two
        bindings of one class are one spell and why an edited method is a new version.
    """

    __slots__ = Cleanable.__slots__ + [
        "_code_memo",
        "_site_roots",
        "_third_party_memo",
        "_version_memo",
        "_distributions",
    ]

    # The hash domain. Change it whenever the encoding below changes meaning, so an old id is never minted again for
    # different content.
    TAG: ClassVar[str] = "v5-code"
    # Class-namespace keys that are not code: the header (module, qualname), the docstring, the descriptors the
    # interpreter makes, a line number, attribute names derived from the methods' code, and the annotations cache
    # that reading annotations fills.
    EXCLUDED_CLASS_KEYS: ClassVar[FrozenSet[str]] = frozenset({
        "__module__", "__qualname__", "__doc__", "__dict__", "__weakref__", "__firstlineno__",
        "__static_attributes__", "__annotations_cache__",
    })
    # Python 3.14 writes `__annotate_func__ = None` (with the cache) into a class WITHOUT annotations the first time
    # anything reads them, and Melder reads them at bind; it is skipped while None, so an id never depends on whether
    # annotations were read. A class WITH annotations holds its annotate function from creation, and it is encoded.
    ANNOTATE_FUNC_KEY: ClassVar[str] = "__annotate_func__"
    # ABCMeta's registry, mutated by `register` and isinstance checks: its type counts, its contents never do.
    OPAQUE_CLASS_KEYS: ClassVar[FrozenSet[str]] = frozenset({"_abc_impl"})
    SCALAR_TYPES: ClassVar[Tuple[type, ...]] = (bool, int, float, complex, str, bytes, bytearray)
    CONTAINER_TYPES: ClassVar[Tuple[type, ...]] = (tuple, list, set, frozenset, dict, types.MappingProxyType)
    # Value types whose repr is their value (addresses removed, for a user subclass's default repr).
    REPR_VALUE_TYPES: ClassVar[Tuple[type, ...]] = (
        datetime.date, datetime.time, datetime.timedelta, datetime.tzinfo, decimal.Decimal, fractions.Fraction,
        uuid.UUID, pathlib.PurePath, re.Pattern, range, slice, ipaddress.IPv4Address, ipaddress.IPv6Address,
        ipaddress.IPv4Network, ipaddress.IPv6Network,
    )
    BUILTIN_CALLABLE_TYPES: ClassVar[Tuple[type, ...]] = (
        types.BuiltinFunctionType, types.MethodDescriptorType, types.WrapperDescriptorType,
        types.MethodWrapperType, types.ClassMethodDescriptorType, types.GetSetDescriptorType,
        types.MemberDescriptorType,
    )
    WEAKREF_TYPES: ClassVar[Tuple[type, ...]] = (weakref.ref, weakref.ProxyType, weakref.CallableProxyType)
    TYPEVAR_TYPES: ClassVar[Tuple[type, ...]] = (typing.TypeVar, typing.ParamSpec, typing.TypeVarTuple)
    TYPING_MODULES: ClassVar[FrozenSet[str]] = frozenset({"typing", "types", "annotationlib"})
    # Rule 2c of the contract: targets encoded as a value.
    VALUE_TARGET_TYPES: ClassVar[Tuple[type, ...]] = (
        (types.MethodType, functools.partial, enum.Enum) + SCALAR_TYPES + (tuple, list, set, frozenset, dict)
        + BUILTIN_CALLABLE_TYPES
    )
    STDLIB_MODULES: ClassVar[FrozenSet[str]] = frozenset(sys.stdlib_module_names) | frozenset({"builtins"})
    CONST_OPCODES: ClassVar[FrozenSet[int]] = frozenset(dis.hasconst)
    EXTENDED_ARG: ClassVar[int] = dis.opmap["EXTENDED_ARG"]
    DOCSTRING_FLAG: ClassVar[int] = inspect.CO_HAS_DOCSTRING
    UNKNOWN_VERSION: ClassVar[str] = "?==?"

    def __init__(self) -> None:
        """
        Create a digest service with empty memos.

        Contract:
            - Starts with empty memos. The site-packages roots are discovered on first need (a module outside the
              standard library), so a digest that never meets one does no filesystem work.

        Returns:
            None.
        """
        super().__init__()
        self._code_memo: weakref.WeakKeyDictionary[types.CodeType, str] = weakref.WeakKeyDictionary()
        self._site_roots: Optional[Tuple[str, ...]] = None
        self._third_party_memo: Dict[str, bool] = {}
        self._version_memo: Dict[str, str] = {}
        self._distributions: Optional[Dict[str, List[str]]] = None

    def cleanup(self) -> None:
        """
        Drop the memos; the digest cannot be used afterwards.

        Contract:
            - Idempotent: a second call returns at once.
            - Clears, then deletes, the memos and the site roots. Holds no other resource and no logger.
            - Every public method raises RuntimeError through `check_cleaned()` afterwards.

        Threading:
            No lock: the owner serializes calls and cleans the digest only when no call is running (`Bind` cleans it
            under its own lock).

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._code_memo.clear()
        self._third_party_memo.clear()
        self._version_memo.clear()
        del self._code_memo
        del self._site_roots
        del self._third_party_memo
        del self._version_memo
        del self._distributions

    def spell_id(self, target: Any) -> str:
        """
        Return the spell_id of a registration target.

        Contract:
            - The SHA256 hex digest (64 characters) of `TAG`, the interpreter's cache tag and the target's encoding,
              newline-joined and UTF-8 encoded (lone surrogates passed through, so no text makes it raise).
            - When the target's data is nested past the recursion limit, the target is encoded by its type and
              address-free repr (`repr <qualified type> <repr>`), no finer than the retired fingerprint for it.
            - Called twice, it gives the same id unless the target, a class of its MRO or its data changed in between.

        Args:
            target: The class, function or object being registered (or inspected).

        Raises:
            RuntimeError: If this digest has been cleaned.

        Returns:
            str: The 64-character spell_id.
        """
        self.check_cleaned()
        try:
            encoding = self._target_encoding(target)
        except RecursionError:
            encoding = self._repr_encoding(target)
        return self._sha(self.TAG + "\n" + str(sys.implementation.cache_tag) + "\n" + encoding)

    def target_encoding(self, target: Any) -> str:
        """
        Return the text a target's spell_id hashes, for diagnostics and tests.

        Contract:
            The first rule that matches (the code-description patch, rule 2):
            - a class: `class <class digest>`, or `class <qualified> <dist>==<version>` when installed third-party;
            - a plain function: `function <module> <qualname> <function digest>`, or
              `function <qualified> <dist>==<version>` when installed third-party;
            - a bound method, partial, enum member, scalar, tuple, list, set, frozenset, dict or builtin:
              `value <encoding>`;
            - an object with Python-visible state whose class is application code:
              `object objclass:<class digest>{<data>}`;
            - an object of an installed third-party class other than Melder's: `object ext:<qualified>
              <dist>==<version> <address-free repr>`;
            - anything else: `repr <qualified type> <address-free repr>`.

        Args:
            target: The class, function or object.

        Raises:
            RuntimeError: If this digest has been cleaned.
            RecursionError: If the target's data is nested past the recursion limit (`spell_id` falls back instead).

        Returns:
            str: The encoding.
        """
        self.check_cleaned()
        return self._target_encoding(target)

    #region Targets

    def _target_encoding(self, target: Any) -> str:
        """
        Apply rule 2 of the contract to a target (see `target_encoding`).

        Args:
            target: The class, function or object.

        Returns:
            str: The encoding.
        """
        empty: FrozenSet[int] = frozenset()
        if isinstance(target, type):
            if self._is_third_party_module(self._class_module(target)):
                return "class " + self._named(target)
            return "class " + self._class_digest(target, empty)
        if isinstance(target, types.FunctionType):
            module = self._function_module(target)
            if self._is_third_party_module(module):
                return "function " + self._named(target)
            return "function " + module + " " + target.__qualname__ + " " + self._function_digest(target, empty, None)
        if isinstance(target, self.VALUE_TARGET_TYPES):
            return "value " + self._encode(target, empty, None)
        module = self._class_module(type(target))
        melder = self._is_melder_module(module)
        if self._is_application_module(module) and self._has_visible_state(target):
            return "object " + self._object_encoding(target, empty, None, True)
        if not melder and self._is_third_party_module(module):
            return "object " + self._external(target)
        return self._repr_encoding(target)

    @classmethod
    def _repr_encoding(cls, target: Any) -> str:
        """
        Encode a target by its type and address-free repr (rule 2e, and the deep-data fallback).

        Args:
            target: The target.

        Returns:
            str: `repr <qualified type> <repr without " at 0x..." addresses>`.
        """
        return "repr " + cls._qualified(type(target)) + " " + InspectorUtility.stable_repr(target)

    def _external(self, value: Any) -> str:
        """
        Encode an object of an installed third-party class: its type, the distribution version, its repr.

        Args:
            value: The object.

        Returns:
            str: `ext:<qualified> <dist>==<version> <address-free repr>`.
        """
        return "ext:" + self._named(type(value)) + " " + InspectorUtility.stable_repr(value)

    #region Classes

    def _class_digest(self, cls: type, path: FrozenSet[int]) -> str:
        """
        Digest a class: its header, metaclass, direct bases and, per MRO entry, its code or its name.

        Contract:
            - Lines: `module`, `qualname`, `meta`, `bases`, then one per class of the MRO in order - `own <namespace
              digest>` for the class itself, `mro <qualified>` for a standard-library or builtin class,
              `mro <qualified> <dist>==<version>` for an installed third-party class, `mro <qualified> <namespace
              digest>` for any other. The SHA256 of the lines.
            - A class already on the current path encodes as `cycle:<qualified>`.

        Args:
            cls: The class.
            path: Ids of the classes, functions, containers and objects being encoded above this one.

        Returns:
            str: The class digest (64 hex characters), or the cycle marker.
        """
        if id(cls) in path:
            return "cycle:" + self._qualified(cls)
        path = path | {id(cls)}
        lines: List[str] = [
            "module " + self._class_text(cls, "__module__"),
            "qualname " + self._class_text(cls, "__qualname__"),
            "meta " + self._meta_text(type(cls), path),
            "bases " + ",".join(self._qualified(base) for base in type.__getattribute__(cls, "__bases__")),
        ]
        for klass in type.__getattribute__(cls, "__mro__"):
            module = self._class_module(klass)
            if klass is cls:
                lines.append("own " + self._namespace_digest(klass, path))
            elif self._is_library_module(module):
                lines.append("mro " + self._qualified(klass))
            elif self._is_third_party_module(module):
                lines.append("mro " + self._named(klass))
            else:
                lines.append("mro " + self._qualified(klass) + " " + self._namespace_digest(klass, path))
        return self._sha("\n".join(lines))

    def _meta_text(self, meta: type, path: FrozenSet[int]) -> str:
        """
        Encode a class's metaclass: named when standard library or installed, digested otherwise.

        Args:
            meta: The metaclass (`type(cls)`).
            path: The current encoding path.

        Returns:
            str: `<qualified>`, `<qualified> <dist>==<version>` or `<qualified> <class digest>`.
        """
        module = self._class_module(meta)
        if self._is_library_module(module):
            return self._qualified(meta)
        if self._is_third_party_module(module):
            return self._named(meta)
        return self._qualified(meta) + " " + self._class_digest(meta, path)

    def _namespace_digest(self, klass: type, path: FrozenSet[int]) -> str:
        """
        Digest one class's own namespace (`klass.__dict__`), every entry but interpreter bookkeeping.

        Contract:
            - One line per entry: an excluded key is skipped, `__annotate_func__` is skipped while None, an opaque
              key gives `<name>=opaque:<qualified type>`, any other gives `<name>=<encoding>` with the class as the
              owner (so a class nested in it is digested). The lines are sorted (definition order never counts),
              joined and hashed.
            - The namespace is copied in one call before the walk; a concurrent class mutation never makes it raise.

        Args:
            klass: The class whose namespace is digested.
            path: The current encoding path.

        Returns:
            str: The namespace digest (64 hex characters).
        """
        lines: List[str] = []
        # One-call copy: a class may be mutated by another thread while it is digested.
        for name, value in list(type.__getattribute__(klass, "__dict__").items()):
            if name in self.EXCLUDED_CLASS_KEYS:
                continue
            if name == self.ANNOTATE_FUNC_KEY and value is None:
                continue
            label = name if isinstance(name, str) else self._encode(name, path, klass)
            if name in self.OPAQUE_CLASS_KEYS:
                lines.append(label + "=opaque:" + self._qualified(type(value)))
                continue
            lines.append(label + "=" + self._encode(value, path, klass))
        lines.sort()
        return self._sha("\n".join(lines))

    def _is_nested_in(self, cls: type, owner: type) -> bool:
        """
        Return whether a class is defined inside another (same module, qualname under the owner's).

        Args:
            cls: The class met as a value.
            owner: The class whose namespace (or method) holds it.

        Returns:
            bool: True when `cls` is nested in `owner`.
        """
        return (
            self._class_module(cls) == self._class_module(owner)
            and self._class_text(cls, "__qualname__").startswith(self._class_text(owner, "__qualname__") + ".")
        )

    #region Functions and code

    def _function_digest(self, function: types.FunctionType, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Digest a plain Python function: its code, defaults, annotations' code, closure, type parameters and dict.

        Contract:
            - Lines: `fn <module>:<name>`, `code <code digest>`, `defaults`, `kwdefaults`; `annotate <function
              digest>` when `__annotate__` is a function; one `cell` line per closure cell in `co_freevars` order;
              `type_params` when not empty; `dict` (the function's `__dict__` without `__wrapped__`, which the
              wrapper's closure already holds) when not empty. The SHA256 of the lines.
            - A decorated function is the wrapper itself: the decorator's code and, through the closure, the
              wrapped function's both count.
            - A function already on the current path encodes as `cycle:fn`.

        Args:
            function: The function.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            str: The function digest (64 hex characters), or the cycle marker.
        """
        if id(function) in path:
            return "cycle:fn"
        path = path | {id(function)}
        lines: List[str] = [
            "fn " + self._function_module(function) + ":" + function.__name__,
            "code " + self._code_digest(function.__code__),
            "defaults " + self._encode(function.__defaults__, path, owner),
            "kwdefaults " + self._encode(function.__kwdefaults__, path, owner),
        ]
        annotate = function.__annotate__
        if isinstance(annotate, types.FunctionType):
            lines.append("annotate " + self._function_digest(annotate, path, owner))
        closure = function.__closure__
        if closure:
            lines.extend(self._closure_lines(function.__code__.co_freevars, closure, path, owner))
        type_params = function.__type_params__
        if type_params:
            lines.append("type_params " + self._encode(type_params, path, owner))
        extra = {key: value for key, value in list(dict.items(function.__dict__)) if key != "__wrapped__"}
        if extra:
            lines.append("dict " + self._encode(extra, path, owner))
        return self._sha("\n".join(lines))

    def _closure_lines(
            self,
            freevars: Tuple[str, ...],
            closure: Tuple[types.CellType, ...],
            path: FrozenSet[int],
            owner: Optional[type],
    ) -> List[str]:
        """
        Encode a function's closure cells, in `co_freevars` order.

        Contract:
            - `__classdict__` (an annotate function's view of the class body namespace, docstring included) is a
              marker: the class namespace is encoded by its own rules. An empty cell is `<empty>`; any other cell is
              its contents' encoding, so a factory's captured values count.

        Args:
            freevars: The function's free variable names.
            closure: Its cells.
            path: The current encoding path.
            owner: The class whose namespace holds the function, or None.

        Returns:
            List[str]: One `cell <name>=<text>` line per cell.
        """
        lines: List[str] = []
        for name, cell in zip(freevars, closure):
            if name == "__classdict__":
                lines.append("cell __classdict__=<class namespace>")
                continue
            try:
                contents = cell.cell_contents
            except ValueError:
                lines.append("cell " + name + "=<empty>")
                continue
            lines.append("cell " + name + "=" + self._encode(contents, path, owner))
        return lines

    def _code_digest(self, code: types.CodeType) -> str:
        """
        Digest a code object: its instruction stream and name tables - no line numbers, docstring or file path.

        Contract:
            - Walks `co_code` (the deoptimized stream, so specialization, sys.monitoring and tracing never show) two
              bytes at a time, folding EXTENDED_ARG into the next argument. The argument of every opcode in
              `dis.hasconst` is replaced by the order in which the stream first loads that constant, and that
              constant's text is recorded at its first use; so a constant no instruction loads (3.14 keeps the
              docstring in `co_consts[0]`, flagged CO_HAS_DOCSTRING) never counts, nor does the table's layout.
            - Lines: `co_name`; the three argument counts; `co_flags` without CO_HAS_DOCSTRING; the opcodes (hex);
              the arguments as little-endian unsigned 32-bit integers (hex); `co_exceptiontable` (hex); `co_names`,
              `co_varnames` (so a renamed local counts), `co_cellvars` and `co_freevars`; the used constants' texts.
            - Memoized per code object (code objects are immutable; the memo is weakly keyed).

        Args:
            code: The code object.

        Returns:
            str: The code digest (64 hex characters).
        """
        cached = self._code_memo.get(code)
        if cached is not None:
            return cached
        constants = code.co_consts
        raw = code.co_code
        const_opcodes = self.CONST_OPCODES
        extended_arg = self.EXTENDED_ARG
        opcodes = bytearray()
        arguments: List[int] = []
        first_use: Dict[int, int] = {}
        used: List[str] = []
        extended = 0
        for index in range(0, len(raw), 2):
            opcode = raw[index]
            argument = extended | raw[index + 1]
            if opcode == extended_arg:
                extended = argument << 8
                continue
            extended = 0
            if opcode in const_opcodes:
                ordinal = first_use.get(argument)
                if ordinal is None:
                    ordinal = len(used)
                    first_use[argument] = ordinal
                    used.append(self._constant_text(constants[argument]))
                argument = ordinal
            opcodes.append(opcode)
            arguments.append(argument)
        lines: List[str] = [
            code.co_name,
            str(code.co_argcount) + "," + str(code.co_posonlyargcount) + "," + str(code.co_kwonlyargcount),
            str(code.co_flags & ~self.DOCSTRING_FLAG),
            bytes(opcodes).hex(),
            struct.pack("<" + str(len(arguments)) + "I", *arguments).hex(),
            code.co_exceptiontable.hex(),
            ",".join(code.co_names),
            ",".join(code.co_varnames),
            ",".join(code.co_cellvars),
            ",".join(code.co_freevars),
            "|".join(used),
        ]
        digest = self._sha("\n".join(lines))
        self._code_memo[code] = digest
        return digest

    def _constant_text(self, value: Any) -> str:
        """
        Return the text of one constant a code object loads.

        Contract:
            - A code object is `code:<code digest>`; a frozenset its items' texts, sorted; a tuple its items' texts,
              in order; a number, string or bytes literal, None, Ellipsis or a bool its exact repr (an integer too
              long for decimal text in hex); anything else its repr with " at 0x..." addresses removed.

        Args:
            value: An entry of `co_consts`.

        Returns:
            str: The constant's text.
        """
        if isinstance(value, types.CodeType):
            return "code:" + self._code_digest(value)
        if isinstance(value, frozenset):
            return "frozenset(" + ",".join(sorted(self._constant_text(item) for item in value)) + ")"
        if isinstance(value, tuple):
            return "(" + ",".join(self._constant_text(item) for item in value) + ")"
        if isinstance(value, int) and not isinstance(value, bool):
            return self._int_text(value)
        if value is None or value is Ellipsis or isinstance(value, (bool, float, complex, str, bytes)):
            return repr(value)
        return InspectorUtility.stable_repr(value)

    #region Values

    def _encode(self, value: Any, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Encode one value reached from a class namespace, a function or an object's data (the contract's table).

        Contract:
            The first row that matches: None, Ellipsis and NotImplemented by repr; an enum member; a scalar; a
            container; a class (`nested:<digest>` when nested in the owner, else `class:<qualified>`); a plain
            function (`fn:<digest>`, or `fn:<qualified> <dist>==<version>` when installed third-party); a
            descriptor, method, partial, module, code object or builtin; then typing objects, value types, weak
            references, standard-library and Melder objects (`ref:`), installed third-party objects (`ext:`),
            application objects with Python-visible state (`obj:`), and `opaque:<type>` for anything else.

        Args:
            value: The value.
            path: The current encoding path.
            owner: The class whose namespace the value belongs to, or None.

        Returns:
            str: The value's encoding.
        """
        if value is None or value is Ellipsis or value is NotImplemented:
            return repr(value)
        if isinstance(value, enum.Enum):
            return self._enum_text(value, path, owner)
        if isinstance(value, self.SCALAR_TYPES):
            return self._scalar_text(value)
        if isinstance(value, self.CONTAINER_TYPES):
            return self._container_text(value, path, owner)
        if isinstance(value, type):
            if owner is not None and self._is_nested_in(value, owner):
                return "nested:" + self._class_digest(value, path)
            return "class:" + self._qualified(value)
        if isinstance(value, types.FunctionType):
            if self._is_third_party_module(self._function_module(value)):
                return "fn:" + self._named(value)
            return "fn:" + self._function_digest(value, path, owner)
        descriptor_text = self._descriptor_text(value, path, owner)
        if descriptor_text is not None:
            return descriptor_text
        return self._object_text(value, path, owner)

    def _enum_text(self, member: enum.Enum, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Encode an enum member by its class, name and value (read from the member's own dictionary).

        Args:
            member: The enum member.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            str: `enum:<qualified class>.<name>=<value encoding>`, or `enum:<qualified class>.<unset>`.
        """
        head = "enum:" + self._qualified(type(member)) + "."
        try:
            name = object.__getattribute__(member, "_name_")
            member_value = object.__getattribute__(member, "_value_")
        except AttributeError:
            return head + "<unset>"
        label = name if isinstance(name, str) else self._encode(name, path, owner)
        return head + label + "=" + self._encode(member_value, path, owner)

    @classmethod
    def _scalar_text(cls, value: Any) -> str:
        """
        Encode a scalar (bool, int, float, complex, str, bytes, bytearray or a subclass) through its builtin base.

        Contract:
            - `<qualified type>:<repr through the builtin base type>`, so a subclass's own `__repr__` never runs; an
              integer too long for decimal text (the interpreter's conversion limit) is written in hex.

        Args:
            value: The scalar.

        Returns:
            str: The encoding.
        """
        for kind in cls.SCALAR_TYPES:
            if isinstance(value, kind):
                if kind is int:
                    return cls._qualified(type(value)) + ":" + cls._int_text(value)
                return cls._qualified(type(value)) + ":" + kind.__repr__(value)
        return "opaque:" + cls._qualified(type(value))

    @staticmethod
    def _int_text(value: int) -> str:
        """
        Return an integer's decimal text, or its hex text when it exceeds the decimal conversion limit.

        Args:
            value: An int (or int subclass) value.

        Returns:
            str: `int.__repr__(value)`, or `hex:<digits>` for an integer too long for decimal text.
        """
        try:
            return int.__repr__(value)
        except ValueError:
            return "hex:" + int.__format__(value, "x")

    def _container_text(self, value: Any, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Encode a tuple, list, set, frozenset, dict or mappingproxy by its items.

        Contract:
            - `<qualified type>[<items>]` for a tuple or list, `<qualified type>{<items, sorted by their text>}` for a
              set or frozenset, `<qualified type>{<key>:<value>, in insertion order}` for a dict or mappingproxy.
            - Items are read through the builtin base type in one call (a subclass's `__iter__` never runs, and a
              concurrent writer never makes the walk raise). A container already on the path is `cycle:<type>`.

        Args:
            value: The container.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            str: The encoding.
        """
        head = self._qualified(type(value))
        if id(value) in path:
            return "cycle:" + head
        inner = path | {id(value)}
        if isinstance(value, tuple):
            items = list(tuple.__iter__(value))
        elif isinstance(value, list):
            items = list(list.__iter__(value))
        elif isinstance(value, frozenset):
            return head + "{" + ",".join(sorted(self._encode(item, inner, owner)
                                                for item in list(frozenset.__iter__(value)))) + "}"
        elif isinstance(value, set):
            return head + "{" + ",".join(sorted(self._encode(item, inner, owner)
                                                for item in list(set.__iter__(value)))) + "}"
        else:
            entries = list(dict.items(value)) if isinstance(value, dict) else list(value.items())
            return head + "{" + ",".join(self._encode(key, inner, owner) + ":" + self._encode(item, inner, owner)
                                         for key, item in entries) + "}"
        return head + "[" + ",".join(self._encode(item, inner, owner) for item in items) + "]"

    def _descriptor_text(self, value: Any, path: FrozenSet[int], owner: Optional[type]) -> Optional[str]:
        """
        Encode a static or class method, property, cached property, bound method, partial, module, code or builtin.

        Args:
            value: The value.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            Optional[str]: The encoding, or None when the value is none of these.
        """
        if isinstance(value, staticmethod):
            return "staticmethod(" + self._encode(value.__func__, path, owner) + ")"
        if isinstance(value, classmethod):
            return "classmethod(" + self._encode(value.__func__, path, owner) + ")"
        if isinstance(value, property):
            accessors = (value.fget, value.fset, value.fdel)
            return "property(" + ",".join(self._encode(accessor, path, owner) for accessor in accessors) + ")"
        if isinstance(value, functools.cached_property):
            return "cached_property(" + self._encode(object.__getattribute__(value, "func"), path, owner) + ")"
        if isinstance(value, types.MethodType):
            return ("method(" + self._encode(value.__func__, path, owner) + " of "
                    + self._encode(value.__self__, path, owner) + ")")
        if isinstance(value, functools.partial):
            parts = (value.func, value.args, value.keywords)
            return "partial(" + ",".join(self._encode(part, path, owner) for part in parts) + ")"
        if isinstance(value, types.ModuleType):
            name = value.__dict__.get("__name__")
            return "module:" + (name if isinstance(name, str) else "?")
        if isinstance(value, types.CodeType):
            return "code:" + self._code_digest(value)
        if isinstance(value, self.BUILTIN_CALLABLE_TYPES):
            return "builtin:" + self._builtin_text(value)
        return None

    @classmethod
    def _builtin_text(cls, value: Any) -> str:
        """
        Name a builtin function, method or slot/member descriptor by its owner and name.

        Contract:
            - A descriptor with `__objclass__` is `<owner qualified>.<__name__>`; a builtin function is
              `<__module__>.<__qualname__>` (`__qualname__` alone when it has no module, as for a bound builtin
              method). Read with `object.__getattribute__`; no address enters it.

        Args:
            value: The builtin callable.

        Returns:
            str: The name text.
        """
        owner_class = cls._static_attribute(value, "__objclass__")
        if isinstance(owner_class, type):
            return cls._qualified(owner_class) + "." + cls._text_attribute(value, "__name__")
        module = cls._static_attribute(value, "__module__")
        qualname = cls._text_attribute(value, "__qualname__")
        return (module + "." + qualname) if isinstance(module, str) else qualname

    def _object_text(self, value: Any, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Encode a value that is no scalar, container, class, function or descriptor (the table's last rows).

        Args:
            value: The value.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            str: A typing encoding, `<qualified>:<repr>` for a value type, `weakref:<type>`, `ref:<type>`,
            `ext:<qualified> <dist>==<version> <repr>`, `obj:<type>{<data>}` or `opaque:<type>`.
        """
        typing_text = self._typing_text(value, path, owner)
        if typing_text is not None:
            return typing_text
        value_type = type(value)
        if isinstance(value, self.REPR_VALUE_TYPES):
            return self._qualified(value_type) + ":" + InspectorUtility.stable_repr(value)
        if isinstance(value, self.WEAKREF_TYPES):
            return "weakref:" + self._qualified(value_type)
        module = self._class_module(value_type)
        if self._is_library_module(module) or self._is_melder_module(module):
            return "ref:" + self._qualified(value_type)
        if self._is_third_party_module(module):
            return self._external(value)
        if self._has_visible_state(value):
            return self._object_encoding(value, path, owner, False)
        return "opaque:" + self._qualified(value_type)

    def _typing_text(self, value: Any, path: FrozenSet[int], owner: Optional[type]) -> Optional[str]:
        """
        Encode a typing object: a ForwardRef by its text, a type parameter or alias by its parts, any other by repr.

        Contract:
            - TypeVar, ParamSpec, TypeVarTuple: `typevar:<kind>|<name>|<variance flags>|<bound>|<constraints>|
              <default>`, each lazily evaluated part by its evaluate function's code (never called) or, for one given
              eagerly, by its stored value; `-` when absent.
            - TypeAliasType: `alias:<name>|<value>`, the same way. Any other object of `typing`, `types` or
              `annotationlib`: `typing:<repr, addresses removed>`.

        Args:
            value: The value.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            Optional[str]: The encoding, or None when the value is not a typing object.
        """
        if isinstance(value, annotationlib.ForwardRef):
            return "fwd:" + self._text_attribute(value, "__forward_arg__")
        if isinstance(value, self.TYPEVAR_TYPES):
            parts: List[str] = [self._class_text(type(value), "__name__"), self._text_attribute(value, "__name__")]
            for flag in ("__covariant__", "__contravariant__", "__infer_variance__"):
                flag_value = self._static_attribute(value, flag)
                parts.append(repr(flag_value) if flag_value is None or isinstance(flag_value, bool) else "?")
            parts.append(self._lazy_text(value, "evaluate_bound", "__bound__", path, owner))
            parts.append(self._lazy_text(value, "evaluate_constraints", "__constraints__", path, owner))
            parts.append(self._lazy_text(value, "evaluate_default", "__default__", path, owner))
            return "typevar:" + "|".join(parts)
        if isinstance(value, typing.TypeAliasType):
            return ("alias:" + self._text_attribute(value, "__name__") + "|"
                    + self._lazy_text(value, "evaluate_value", "__value__", path, owner))
        if self._class_module(type(value)) in self.TYPING_MODULES:
            return "typing:" + InspectorUtility.stable_repr(value)
        return None

    def _lazy_text(self, value: Any, hook: str, stored: str, path: FrozenSet[int], owner: Optional[type]) -> str:
        """
        Encode one lazily evaluable part of a type parameter or alias without evaluating it.

        Contract:
            - No evaluator: `-`. A function evaluator (PEP 695/696 syntax): its function encoding, never called. Any
              other evaluator (a constant one, for a part given eagerly): `const:` and the stored value's encoding.

        Args:
            value: The TypeVar, ParamSpec, TypeVarTuple or TypeAliasType.
            hook: The evaluator attribute (`evaluate_bound`, ...).
            stored: The attribute holding the eagerly given value (`__bound__`, ...).
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            str: The part's text.
        """
        evaluator = self._static_attribute(value, hook)
        if evaluator is None:
            return "-"
        if isinstance(evaluator, types.FunctionType):
            return self._encode(evaluator, path, owner)
        return "const:" + self._encode(self._static_attribute(value, stored), path, owner)

    #region Objects

    def _object_encoding(self, obj: Any, path: FrozenSet[int], owner: Optional[type], top: bool) -> str:
        """
        Encode an application object by its class and its data (its slots, then its instance dictionary).

        Contract:
            - The registration target itself is `objclass:<class digest>{<data>}`; an object met in data is
              `obj:<qualified type>{<data>}`. Data fields are `;`-joined. An object already on the path is
              `cycle:<qualified type>`.

        Args:
            obj: The object.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.
            top: True for the registration target.

        Returns:
            str: The encoding.
        """
        obj_type = type(obj)
        if id(obj) in path:
            return "cycle:" + self._qualified(obj_type)
        inner = path | {id(obj)}
        head = ("objclass:" + self._class_digest(obj_type, inner)) if top else ("obj:" + self._qualified(obj_type))
        fields = self._slot_fields(obj, obj_type, inner, owner)
        fields.extend(self._dict_fields(obj, obj_type, inner, owner))
        return head + "{" + ";".join(fields) + "}"

    def _slot_fields(self, obj: Any, obj_type: type, path: FrozenSet[int], owner: Optional[type]) -> List[str]:
        """
        Encode an object's `__slots__` values, class by class along its MRO.

        Contract:
            - Each name a class's `__slots__` declares (a string or a list, tuple, dict or set of strings;
              `__dict__` and `__weakref__` skipped; a private name mangled with that class's name), read with
              `object.__getattribute__`: `slot <name>=<encoding>`, or `slot <name>=<unset>`.

        Args:
            obj: The object.
            obj_type: Its type.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            List[str]: The slot fields.
        """
        fields: List[str] = []
        for klass in type.__getattribute__(obj_type, "__mro__"):
            declared = type.__getattribute__(klass, "__dict__").get("__slots__", ())
            if isinstance(declared, str):
                names: List[Any] = [declared]
            elif isinstance(declared, (list, tuple, dict, set, frozenset)):
                names = list(declared)
            else:
                names = []
            for name in names:
                if not isinstance(name, str) or name in ("__dict__", "__weakref__"):
                    continue
                try:
                    slot_value = object.__getattribute__(obj, self._mangled(klass, name))
                except AttributeError:
                    fields.append("slot " + name + "=<unset>")
                    continue
                fields.append("slot " + name + "=" + self._encode(slot_value, path, owner))
        return fields

    def _dict_fields(self, obj: Any, obj_type: type, path: FrozenSet[int], owner: Optional[type]) -> List[str]:
        """
        Encode an object's instance dictionary, in insertion order.

        Contract:
            - `attr <key>=<encoding>` per entry, read with `object.__getattribute__` and copied in one call; a key whose
              class attribute (`inspect.getattr_static`) is a `functools.cached_property` is skipped (its value is a
              cache, filled by reading it).

        Args:
            obj: The object.
            obj_type: Its type.
            path: The current encoding path.
            owner: The class whose namespace holds it, or None.

        Returns:
            List[str]: The attribute fields (empty when the object has no instance dictionary).
        """
        try:
            data = object.__getattribute__(obj, "__dict__")
        except AttributeError:
            return []
        if not isinstance(data, dict):
            return []
        fields: List[str] = []
        for key, item in list(dict.items(data)):
            if isinstance(key, str):
                if isinstance(inspect.getattr_static(obj_type, key, None), functools.cached_property):
                    continue
                label = key
            else:
                label = self._encode(key, path, owner)
            fields.append("attr " + label + "=" + self._encode(item, path, owner))
        return fields

    @classmethod
    def _has_visible_state(cls, obj: Any) -> bool:
        """
        Return whether an object has Python-visible state: an instance dictionary or a `__slots__` entry in its MRO.

        Args:
            obj: The object.

        Returns:
            bool: True when its data can be read without running its code.
        """
        try:
            object.__getattribute__(obj, "__dict__")
            return True
        except AttributeError:
            pass
        for klass in type.__getattribute__(type(obj), "__mro__"):
            if klass is not object and "__slots__" in type.__getattribute__(klass, "__dict__"):
                return True
        return False

    @classmethod
    def _mangled(cls, klass: type, name: str) -> str:
        """
        Apply Python's private-name mangling to a slot name declared by a class.

        Args:
            klass: The declaring class.
            name: The declared slot name.

        Returns:
            str: `_<Class><name>` for a `__private` name of a class whose name is not all underscores, else the name.
        """
        if not name.startswith("__") or name.endswith("__"):
            return name
        stripped = cls._class_text(klass, "__name__").lstrip("_")
        return ("_" + stripped + name) if stripped else name

    #region Names and installed packages

    @staticmethod
    def _static_attribute(obj: Any, name: str) -> Any:
        """
        Read an attribute through `object.__getattribute__`, without running a `__getattr__`.

        Args:
            obj: The object.
            name: The attribute name.

        Returns:
            Any: The attribute's value, or None when it is absent.
        """
        try:
            return object.__getattribute__(obj, name)
        except AttributeError:
            return None

    @classmethod
    def _text_attribute(cls, obj: Any, name: str) -> str:
        """
        Read a string attribute through `object.__getattribute__`.

        Args:
            obj: The object.
            name: The attribute name.

        Returns:
            str: The value, or "?" when it is absent or not a string.
        """
        value = cls._static_attribute(obj, name)
        return value if isinstance(value, str) else "?"

    @staticmethod
    def _class_text(cls: type, name: str) -> str:
        """
        Read a string attribute of a class through `type.__getattribute__` (a metaclass's `__getattr__` never runs).

        Args:
            cls: The class.
            name: `__module__`, `__qualname__` or `__name__`.

        Returns:
            str: The value, or "?" when it is absent or not a string.
        """
        try:
            value = type.__getattribute__(cls, name)
        except AttributeError:
            return "?"
        return value if isinstance(value, str) else "?"

    @classmethod
    def _qualified(cls, klass: type) -> str:
        """
        Return a class's `<module>.<qualname>`.

        Args:
            klass: The class.

        Returns:
            str: The qualified name ("?" for a part that is absent).
        """
        return cls._class_text(klass, "__module__") + "." + cls._class_text(klass, "__qualname__")

    @staticmethod
    def _class_module(klass: type) -> Optional[str]:
        """
        Return a class's module name.

        Args:
            klass: The class.

        Returns:
            Optional[str]: The module name, or None when the class has none (treated as standard library).
        """
        try:
            module = type.__getattribute__(klass, "__module__")
        except AttributeError:
            return None
        return module if isinstance(module, str) else None

    @staticmethod
    def _function_module(function: types.FunctionType) -> str:
        """
        Return a function's module text: its `__module__`, "None" for a function exec'd without one.

        Args:
            function: The function.

        Returns:
            str: The module text ("?" for a non-string module).
        """
        module = function.__module__
        if module is None:
            return "None"
        return module if isinstance(module, str) else "?"

    def _is_library_module(self, module: Optional[str]) -> bool:
        """
        Return whether a module is standard library: its top-level name is a standard module or `builtins`, or none.

        Args:
            module: The module name, or None.

        Returns:
            bool: True for the standard library.
        """
        return module is None or module.partition(".")[0] in self.STDLIB_MODULES

    @staticmethod
    def _is_melder_module(module: Optional[str]) -> bool:
        """
        Return whether a module is Melder's (`melder` or `melder.*`).

        Args:
            module: The module name, or None.

        Returns:
            bool: True for Melder's modules.
        """
        return module is not None and (module == "melder" or module.startswith("melder."))

    def _is_application_module(self, module: Optional[str]) -> bool:
        """
        Return whether a module is application code: not standard library, not Melder, not installed third-party.

        Args:
            module: The module name, or None.

        Returns:
            bool: True for application code.
        """
        return (
            not self._is_library_module(module)
            and not self._is_melder_module(module)
            and not self._is_third_party_module(module)
        )

    def _is_third_party_module(self, module: Optional[str]) -> bool:
        """
        Return whether a module is installed third-party: not standard library, its file under a site-packages root.

        Contract:
            - A module that is not loaded, not a module object or has no file cannot be located and is application
              code. Memoized per module name.

        Args:
            module: The module name, or None.

        Returns:
            bool: True for an installed third-party module (Melder included, when it is installed).
        """
        if self._is_library_module(module):
            return False
        known = self._third_party_memo.get(module)
        if known is not None:
            return known
        loaded = sys.modules.get(module)
        located = loaded.__dict__.get("__file__") if isinstance(loaded, types.ModuleType) else None
        result = isinstance(located, str) and self._under_site_root(located)
        self._third_party_memo[module] = result
        return result

    def _under_site_root(self, file: str) -> bool:
        """
        Return whether a module file lies under one of the interpreter's site-packages directories.

        Args:
            file: The module's `__file__`.

        Returns:
            bool: True when the resolved path starts with a site-packages root.
        """
        roots = self._site_roots
        if roots is None:
            roots = self._discover_site_roots()
            self._site_roots = roots
        try:
            resolved = str(pathlib.Path(file).resolve())
        except (OSError, RuntimeError, ValueError):
            resolved = file
        return any(resolved.startswith(root) for root in roots)

    @staticmethod
    def _discover_site_roots() -> Tuple[str, ...]:
        """
        Collect the interpreter's site-packages directories, resolved, each ending with a path separator.

        Contract:
            - `sysconfig` purelib and platlib, `site.getsitepackages()` and `site.getusersitepackages()`; a `site`
              function the interpreter lacks contributes nothing.

        Returns:
            Tuple[str, ...]: The roots, sorted.
        """
        candidates: List[str] = []
        paths = sysconfig.get_paths()
        for key in ("purelib", "platlib"):
            path = paths.get(key)
            if path:
                candidates.append(path)
        try:
            candidates.extend(site.getsitepackages())
        except AttributeError:
            pass
        try:
            user_site = site.getusersitepackages()
        except AttributeError:
            user_site = ""
        if user_site:
            candidates.append(user_site)
        roots = set()
        for path in candidates:
            try:
                resolved = str(pathlib.Path(path).resolve())
            except (OSError, RuntimeError, ValueError):
                resolved = path
            roots.add(resolved.rstrip(os.sep) + os.sep)
        return tuple(sorted(roots))

    def _named(self, value: Any) -> str:
        """
        Name an installed class or function by its qualified name and distribution version.

        Args:
            value: A class or a plain function.

        Returns:
            str: `<qualified> <dist>==<version>` (`?==?` when no distribution is found).
        """
        if isinstance(value, type):
            module = self._class_module(value)
            qualified = self._qualified(value)
        else:
            module = self._function_module(value)
            qualified = module + "." + value.__qualname__
        return qualified + " " + self._version(module if module is not None else "?")

    def _version(self, module: str) -> str:
        """
        Return the distribution that installs a module's top-level package, with its version.

        Contract:
            - `importlib.metadata.version(<top-level name>)` first; when the import name is no distribution name,
              `packages_distributions()` (read once per digest; the first distribution in sorted order). Memoized per
              top-level name.

        Args:
            module: The module name.

        Returns:
            str: `<dist>==<version>`, or `?==?` when none is found.
        """
        top = module.partition(".")[0]
        known = self._version_memo.get(top)
        if known is not None:
            return known
        text = self.UNKNOWN_VERSION
        try:
            text = f"{top}=={importlib.metadata.version(top)}"
        except importlib.metadata.PackageNotFoundError:
            if self._distributions is None:
                self._distributions = {name: list(dists) for name, dists in
                                       importlib.metadata.packages_distributions().items()}
            names = sorted(self._distributions.get(top) or [])
            if names:
                try:
                    text = f"{names[0]}=={importlib.metadata.version(names[0])}"
                except importlib.metadata.PackageNotFoundError:
                    text = self.UNKNOWN_VERSION
        self._version_memo[top] = text
        return text

    @staticmethod
    def _sha(text: str) -> str:
        """
        Return the SHA256 hex digest of a text (UTF-8, lone surrogates passed through).

        Args:
            text: The text.

        Returns:
            str: 64 hex characters.
        """
        return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()
