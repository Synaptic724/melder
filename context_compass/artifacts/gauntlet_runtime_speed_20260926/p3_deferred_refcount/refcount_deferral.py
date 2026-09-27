import gc
import sys
import sysconfig
import threading
from collections import deque
from types import CellType, CodeType, FunctionType, MethodType, ModuleType
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Optional, Set, Tuple


#region RefcountDeferral


class RefcountDeferral:
    """
    Move Melder's long-lived runtime objects to deferred reference counting on free-threaded CPython.

    Purpose:
        On a free-threaded (PEP 703) CPython every object is owned by the thread
        that created it. The owner adjusts the object's reference count with
        plain stores; every other thread pays an atomic add and an atomic
        subtract on a shared counter for each reference it takes, and the cache
        line holding that counter moves between cores. Melder builds its kernel
        (spellbook, spells, creation contexts, generated executors, the root
        conduit's meld and stores) on the thread that conjures, and its pooled
        scope shells on whichever thread first needed them - yet every warm meld
        and every scope cycle on every other thread reads those objects. Measured
        on 3.14t, a worker-thread load of an object owned by another live thread
        costs ~9 ns more than a load of its own object, and the scope cycle of the
        real-world gauntlet was 21-29% slower than it needs to be.

        CPython 3.14 exposes the remedy the interpreter itself uses for code
        objects, module-level functions and classes:
        `PyUnstable_Object_EnableDeferredRefcount`. A deferred object is not
        reference-counted when it is loaded onto the evaluation stack, from any
        thread. This helper applies it to the Melder-owned part of an object
        graph.

    Contract:
        - Acts only on free-threaded CPython builds that export the C function;
          everywhere else (GIL builds, other interpreters, missing symbol) every
          method returns 0 and touches nothing.
        - Defers only objects Melder owns: instances of classes defined in the
          `melder` package, functions and bound methods (Melder's generated
          executors are closures, which the interpreter does not defer by
          itself), closure cells, and the builtin containers (dict, list, tuple,
          set, frozenset, deque) that hold no object of another package at the
          time of the walk (the "userfree" rule).
        - Never defers or descends into: classes (already deferred by the
          interpreter), modules, code objects, module globals dictionaries,
          thread-local objects, or instances of classes from any other package
          (user objects, stdlib objects). A container that holds such an object
          is not deferred, so dropping it still releases those objects
          immediately.
        - Descends only through the given roots and objects it newly deferred,
          so a later walk from a new object stops at the already-deferred kernel
          instead of re-walking it.
        - Best effort and idempotent: a container that changes size while it is
          read is left alone; deferring an already deferred object is a no-op.

    Lifecycle / Memory:
        A deferred object is reclaimed by the cyclic garbage collector rather than
        at the moment its last reference disappears. Melder's cleanup contract
        deletes owned fields explicitly, so user objects held by a cleaned Melder
        object are still released at cleanup; only the Melder object's own memory
        waits for the next collection.

    Threading:
        Thread-safe. The C function is thread-safe, and the walk only reads
        attributes and iterates containers; it takes no lock. Only a Melder
        instance without `__slots__` is read with `gc.get_referents`, which
        briefly pauses other threads.
    """

    __slots__ = ()

    @staticmethod
    def _resolve_enable() -> Optional[Callable[[object], int]]:
        """
        Resolve `PyUnstable_Object_EnableDeferredRefcount` once, when the class is created.

        Returns:
            Optional[Callable[[object], int]]: The C function (returns 1 when it
            deferred the object, 0 when the object was already deferred or cannot
            be), or None on GIL builds, non-CPython interpreters, or a CPython
            that does not export it.
        """
        if sys.implementation.name != "cpython" or not sysconfig.get_config_var("Py_GIL_DISABLED"):
            return None
        # Imported here so GIL builds never load ctypes for a feature they do not use.
        import ctypes

        try:
            enable = ctypes.pythonapi.PyUnstable_Object_EnableDeferredRefcount
        except AttributeError:
            return None
        enable.argtypes = [ctypes.py_object]
        enable.restype = ctypes.c_int
        return enable

    # Class-level constants, fixed when the class is created.
    _ENABLE: ClassVar[Optional[Callable[[object], int]]] = _resolve_enable()
    _CONTAINER_TYPES: ClassVar[Tuple[type, ...]] = (dict, list, tuple, set, frozenset, deque)
    _SCALAR_TYPES: ClassVar[Tuple[type, ...]] = (str, bytes, int, float, complex, bool, type(None))
    _MAX_CONTAINER_NESTING: ClassVar[int] = 3

    @classmethod
    def available(cls) -> bool:
        """
        Report whether this interpreter supports deferral.

        Returns:
            bool: True on a free-threaded CPython that exports the C function.
        """
        return cls._ENABLE is not None

    @classmethod
    def defer_graph(cls, *roots: object) -> int:
        """
        Defer the Melder-owned objects reachable from `roots`.

        Purpose:
            Called at the few points where Melder publishes long-lived runtime
            structure: the end of a conjure (spellbook and root conduit), executor
            hydration, pooled scope-shell construction and fast meld door entries.

        Contract:
            - Applies the rules in the class docstring. Roots are always
              descended; other objects are descended only when this walk deferred
              them (or when they are containers kept alive by a deferred parent).
            - Returns immediately with 0 when deferral is unavailable.

        Args:
            *roots:
                Objects to start from. Each root is classified like any other
                object and, unless it is skipped (a user instance, class, module,
                code object or scalar), always descended - even when it was
                already deferred - so a walk from an existing object still reaches
                objects attached to it since its last walk.

        Returns:
            int: Number of objects newly deferred by this call.
        """
        enable = cls._ENABLE
        if enable is None:
            return 0
        deferred = 0
        visited: Set[int] = set()
        # Keep every visited object alive until the walk ends so ids cannot be reused mid-walk.
        keep_alive: List[object] = []
        slot_cache: Dict[type, Tuple[Tuple[str, ...], bool]] = {}
        stack: List[Tuple[object, bool]] = [(root, True) for root in roots]
        while stack:
            obj, is_root = stack.pop()
            key = id(obj)
            if key in visited:
                continue
            visited.add(key)
            keep_alive.append(obj)
            kind = cls._classify(obj)
            if kind == "skip":
                continue
            if kind == "defer":
                newly = enable(obj) == 1
                deferred += newly
                if not (newly or is_root):
                    continue
            # "user_container": not deferred, but still searched for Melder objects.
            for child in cls._children(obj, kind, slot_cache):
                stack.append((child, False))
        return deferred

    @classmethod
    def _classify(cls, obj: object) -> str:
        """
        Classify one object for the walk.

        Returns:
            str: "defer" for objects to defer and descend, "user_container" for
            containers that hold a non-Melder object (searched, not deferred), and
            "skip" for everything else.
        """
        obj_type = type(obj)
        if obj_type in cls._SCALAR_TYPES or isinstance(obj, (type, ModuleType, CodeType, threading.local)):
            return "skip"
        if isinstance(obj, (FunctionType, MethodType, CellType)):
            return "defer"
        if isinstance(obj, cls._CONTAINER_TYPES):
            if isinstance(obj, dict) and "__builtins__" in obj:
                # A module globals dictionary, reached through a function.
                return "skip"
            if cls._holds_foreign(obj, 0):
                return "user_container"
            return "defer"
        if cls._is_melder_type(obj_type):
            return "defer"
        return "skip"

    @staticmethod
    def _is_melder_type(obj_type: type) -> bool:
        """
        Return whether `obj_type` is defined in the `melder` package.

        Args:
            obj_type: The concrete type of an object (never a base class: a user
                subclass of a Melder base belongs to the user).

        Returns:
            bool: True for `melder` and `melder.*` modules.
        """
        module = obj_type.__module__
        return module == "melder" or module.startswith("melder.")

    @classmethod
    def _holds_foreign(cls, container: Any, depth: int) -> bool:
        """
        Return whether a container holds an object from outside Melder (checked recursively, bounded).

        Contract:
            - Scalars, classes, modules, functions, methods, cells and Melder
              instances are Melder-safe; nested containers are checked the same
              way up to `_MAX_CONTAINER_NESTING` levels, beyond which the
              container is treated as foreign.
            - A container that changes size while it is read counts as foreign
              (conservative: it is then neither deferred nor trusted).

        Args:
            container: A dict, list, tuple, set, frozenset or deque.
            depth: Current nesting depth.

        Returns:
            bool: True when any element (or dict key) is foreign.
        """
        if depth > cls._MAX_CONTAINER_NESTING:
            return True
        try:
            items: Iterable[Any] = (
                list(container.keys()) + list(container.values())
                if isinstance(container, dict)
                else list(container)
            )
        except RuntimeError:
            return True
        for item in items:
            item_type = type(item)
            if item_type in cls._SCALAR_TYPES:
                continue
            if isinstance(item, (type, ModuleType, FunctionType, MethodType, CellType)):
                continue
            if isinstance(item, cls._CONTAINER_TYPES):
                if cls._holds_foreign(item, depth + 1):
                    return True
                continue
            if not cls._is_melder_type(item_type):
                return True
        return False

    @classmethod
    def _children(
            cls,
            obj: object,
            kind: str,
            slot_cache: Dict[type, Tuple[Tuple[str, ...], bool]],
    ) -> List[object]:
        """
        Return the objects `obj` references that the walk may visit next.

        Contract:
            - Functions: closure cells, defaults and keyword defaults (never
              `__globals__`, the module namespace).
            - Bound methods: the bound object and the function.
            - Cells: the contents, when set.
            - Containers: elements, and keys and values for dicts.
            - Melder instances: every slot value across the class hierarchy (see
              `_instance_children`).

        Returns:
            List[object]: Referenced objects; empty when nothing can be read.
        """
        if isinstance(obj, FunctionType):
            children: List[object] = list(obj.__closure__ or ())
            if obj.__defaults__:
                children.append(obj.__defaults__)
            if obj.__kwdefaults__:
                children.append(obj.__kwdefaults__)
            return children
        if isinstance(obj, MethodType):
            return [obj.__self__, obj.__func__]
        if isinstance(obj, CellType):
            try:
                return [obj.cell_contents]
            except ValueError:
                return []
        if isinstance(obj, cls._CONTAINER_TYPES):
            try:
                if isinstance(obj, dict):
                    return list(obj.keys()) + list(obj.values())
                return list(obj)
            except RuntimeError:
                return []
        return cls._instance_children(obj, slot_cache)

    @classmethod
    def _instance_children(
            cls,
            obj: object,
            slot_cache: Dict[type, Tuple[Tuple[str, ...], bool]],
    ) -> List[object]:
        """
        Read the attribute values of one Melder instance.

        Contract:
            - Slot names are gathered once per class for the whole walk,
              including name-mangled private slots; an unset slot is skipped.
            - An instance whose class hierarchy also gives it a `__dict__` is read
              through `gc.get_referents`, which visits the stored values without
              materializing the dictionary (reading `__dict__` would allocate one
              and slow later attribute access). That call pauses other threads
              briefly; Melder's hot classes declare `__slots__`, so it is rare.

        Returns:
            List[object]: The values currently stored on the instance.
        """
        obj_type = type(obj)
        cached = slot_cache.get(obj_type)
        if cached is None:
            cached = cls._slot_names(obj_type)
            slot_cache[obj_type] = cached
        names, has_dict = cached
        if has_dict:
            return list(gc.get_referents(obj))
        values: List[object] = []
        for name in names:
            try:
                values.append(object.__getattribute__(obj, name))
            except AttributeError:
                continue
        return values

    @staticmethod
    def _slot_names(obj_type: type) -> Tuple[Tuple[str, ...], bool]:
        """
        Collect the slot attribute names of `obj_type` and whether its instances also carry a `__dict__`.

        Args:
            obj_type: A Melder class.

        Returns:
            Tuple[Tuple[str, ...], bool]: Slot names across the MRO (mangled where
            Python mangles them), and True when some class in the MRO other than
            `object` declares no `__slots__`.
        """
        names: List[str] = []
        has_dict = False
        for klass in obj_type.__mro__[:-1]:
            declared = klass.__dict__.get("__slots__")
            if declared is None:
                has_dict = True
                continue
            if isinstance(declared, str):
                declared = (declared,)
            for name in declared:
                if name in ("__dict__", "__weakref__"):
                    if name == "__dict__":
                        has_dict = True
                    continue
                if name.startswith("__") and not name.endswith("__"):
                    name = f"_{klass.__name__.lstrip('_')}{name}"
                names.append(name)
        return tuple(names), has_dict


#endregion RefcountDeferral
