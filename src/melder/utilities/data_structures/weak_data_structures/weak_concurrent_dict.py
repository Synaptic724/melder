from __future__ import annotations

import functools
import threading
from copy import deepcopy
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import ulid

# Melder Imports
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.data_structures.weak_data_structures.weak_ref_node import WeakRefNode

_K = TypeVar("_K")
_V = TypeVar("_V")


class _WeakDictKeysView(Collection[_K]):
    def __init__(self, parent: "WeakConcurrentDict[_K, _V]") -> None:
        self._parent = parent

    def __iter__(self) -> Iterator[_K]:
        self._parent.check_cleaned()
        for k, _ in self._parent._snapshot_items():
            yield k

    def __len__(self) -> int:
        return len(self._parent)

    def __contains__(self, key: object) -> bool:
        return key in self._parent

    # Set-like operations
    def _as_set(self) -> set[_K]:
        return set(iter(self))

    def __and__(self, other: Iterable[Any]) -> set[_K]:
        return self._as_set().__and__(set(other))

    def __or__(self, other: Iterable[Any]) -> set[_K]:
        return self._as_set().__or__(set(other))

    def __sub__(self, other: Iterable[Any]) -> set[_K]:
        return self._as_set().__sub__(set(other))

    def __xor__(self, other: Iterable[Any]) -> set[_K]:
        return self._as_set().__xor__(set(other))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self)!r})"


class _WeakDictItemsView(Collection[Tuple[_K, _V]]):
    def __init__(self, parent: "WeakConcurrentDict[_K, _V]") -> None:
        self._parent = parent

    def __iter__(self) -> Iterator[Tuple[_K, _V]]:
        self._parent.check_cleaned()
        for k, node in self._parent._snapshot_items():
            yield (k, node.deref(strict=True))

    def __len__(self) -> int:
        return len(self._parent)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, tuple) or len(item) != 2:
            return False
        key, val = item
        try:
            current = self._parent[key]  # may raise
        except Exception:
            return False
        return current == val

    # Set-like operations
    def _as_set(self) -> set[Tuple[_K, _V]]:
        return set(iter(self))

    def __and__(self, other: Iterable[Any]) -> set[Tuple[_K, _V]]:
        return self._as_set().__and__(set(other))

    def __or__(self, other: Iterable[Any]) -> set[Tuple[_K, _V]]:
        return self._as_set().__or__(set(other))

    def __sub__(self, other: Iterable[Any]) -> set[Tuple[_K, _V]]:
        return self._as_set().__sub__(set(other))

    def __xor__(self, other: Iterable[Any]) -> set[Tuple[_K, _V]]:
        return self._as_set().__xor__(set(other))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self)!r})"


class _WeakDictValuesView(Collection[_V]):
    def __init__(self, parent: "WeakConcurrentDict[_K, _V]") -> None:
        self._parent = parent

    def __iter__(self) -> Iterator[_V]:
        self._parent.check_cleaned()
        for _, node in self._parent._snapshot_items():
            yield node.deref(strict=True)

    def __len__(self) -> int:
        return len(self._parent)

    def __contains__(self, value: object) -> bool:
        for v in self:
            if v == value:
                return True
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({list(self)!r})"


class WeakConcurrentDict(Generic[_K, _V], Cleanable):
    """
    WeakConcurrentDict
    ==================

    A thread-safe, *weakly referenced* dictionary of values.

    This container stores **WeakRefNode[_V]** internally and exposes the
    underlying values as if it were a normal dict:

    * Keys are stored **strongly**.
    * Values are wrapped in `WeakRefNode` and held weakly.
    * When a value is garbage-collected:
      - Its `WeakRefNode` marks itself dead.
      - The node's GC callback may inform this dict (via `_on_node_collected`).
      - If `auto_prune` is enabled, the entry is removed automatically.
    * Accessors that dereference nodes (`__getitem__`, `values()`, etc.) may
      raise `DeadReferenceError` if a dead entry is still present and not
      yet pruned.

    Concurrency
    -----------
    * A per-instance lock (`threading.RLock`) protects
      structural mutations and, in non-frozen mode, read paths that snapshot
      internal state.
    * `freeze()` / `unfreeze()`:
      - When frozen, **mutations are forbidden** and raise `TypeError`.
      - Read operations avoid acquiring the lock in the hot path, but may
        still use it internally for best-effort pruning when `auto_prune` is
        enabled.

    Auto-pruning
    ------------
    * If `auto_prune=True`, dead nodes are removed:
        - From GC callback path (best-effort, GC thread).
        - From certain read paths that call `_prune_dead_locked()`:
            - `__len__()`
            - `keys()`, `values()`, `items()`
            - `__iter__()`, `to_dict()`, `map()`, `filter()`, `reduce()`
    * If `auto_prune=False`, the container will keep dead nodes until:
        - `prune()` is called explicitly, or
        - GC callback happens to remove them (if the dict is still alive).

    Cleanable Contract
    ------------------
    * `cleanup()`:
      - Idempotent.
      - Calls `node.fire_callbacks()` and then `node.cleanup()` for all nodes.
      - Clears the internal dict and releases the lock.
    """

    __slots__ = (
            Cleanable.__slots__
            + ["_dict", "_lock", "_freeze", "_id", "_auto_prune"]
    )

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------
    def __init__(
            self,
            initial: Optional[Union[Mapping[_K, _V], Iterable[Tuple[_K, _V]]]] = None,
            auto_prune: bool = False,
    ) -> None:
        """
        Initialize a new WeakConcurrentDict.

        Args:
            initial:
                Optional mapping or iterable of ``(key, value)`` pairs to seed
                the dictionary. Values will be wrapped in `WeakRefNode` and
                held weakly.
            auto_prune:
                If True, the dict will try to automatically remove dead nodes:
                    * From GC callbacks via `_on_node_collected`.
                    * From certain read paths that call `_prune_dead_locked()`.

        Raises:
            TypeError:
                If any value in `initial` cannot be weak-referenced (raised
                by `WeakRefNode`).
        """
        super().__init__()

        self._id: str = str(ulid.ULID())
        self._freeze: bool = False
        self._auto_prune: bool = bool(auto_prune)
        self._lock: threading.RLock = threading.RLock()

        # Materialize initial as a simple dict of strong values.
        raw: Dict[_K, _V] = {}
        if initial is not None:
            if hasattr(initial, "keys"):
                # Mapping-like
                for k in initial.keys():
                    raw[k] = initial[k]
            else:
                # Iterable of (k, v)
                for k, v in initial:
                    raw[k] = v

        # Wrap all values in WeakRefNode
        self._dict: Dict[_K, WeakRefNode[_V]] = {
            k: self._make_node(v) for k, v in raw.items()
        }

    # -------------------------------------------------------------------------
    # Alt constructors
    # -------------------------------------------------------------------------
    @classmethod
    def fromkeys(
            cls,
            keys: Iterable[_K],
            value: Optional[_V] = None,
            *,
            auto_prune: bool = False,
    ) -> "WeakConcurrentDict[_K, _V]":
        """
        Create a WeakConcurrentDict from an iterable of keys, assigning each to the same value.

        Mirrors ``dict.fromkeys`` semantics (including any TypeError raised if the value cannot
        be weak-referenced).

        Args:
            keys: Iterable of keys.
            value: Value to associate with every key.
            auto_prune: Whether the resulting dict should auto-prune dead entries.
        """
        items = [(k, value) for k in keys]
        return cls(initial=items, auto_prune=auto_prune)

    # -------------------------------------------------------------------------
    # Internal node helpers
    # -------------------------------------------------------------------------
    def _make_node(self, value: _V) -> WeakRefNode[_V]:
        """
        Create a WeakRefNode for this dict, wiring the GC callback.

        Args:
            value:
                The value to weak-reference. Must support weak references.

        Returns:
            WeakRefNode[_V]: The created node.

        Raises:
            TypeError:
                If the object cannot be weak-referenced.
        """
        return WeakRefNode(value, on_collect=self._on_node_collected)

    def _on_node_collected(self, node: WeakRefNode[_V]) -> None:
        """
        GC-path callback invoked when a value referent is collected.

        This is called from `WeakRefNode._weakref_callback` when:
            - The referent is about to be finalized.
            - The node has marked itself dead and fired its own callbacks.

        Behavior:
            * If this dict is already cleaned or `auto_prune` is False → no-op.
            * Otherwise, best-effort:
              - Acquire the dict lock.
              - Scan for the key mapping to `node`.
              - Remove the entry and `cleanup()` the node.

        IMPORTANT:
            This runs on the **GC/finalizer path**, not on a normal app thread.
            If you enable `auto_prune`, you accept that this method may acquire
            the lock in that context. Exceptions are swallowed.
        """
        if self._cleaned or not self._auto_prune:
            return

        try:
            self._lock.acquire()
        except Exception:
            return

        try:
            if self._cleaned or self._dict is None:
                return

            target_key: Optional[_K] = None
            # Snapshot items to avoid "dict changed size" while scanning.
            for k, stored_node in list(self._dict.items()):
                if stored_node is node:
                    target_key = k
                    break

            if target_key is not None:
                try:
                    node.cleanup()
                finally:
                    self._dict.pop(target_key, None)
        finally:
            try:
                self._lock.release()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Deterministically dispose this WeakConcurrentDict.

        Once cleaned:

          * `_cleaned` is set to True.
          * All remaining nodes:
              - Have their callbacks fired via `node.fire_callbacks()`.
              - Are then `cleanup()`-ed.
          * The internal dict is cleared and set to None.
          * The lock is released and nulled.
          * If using AgenticRLock, its `cleanup()` is invoked best-effort.

        This method is **idempotent** and thread-safe.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            if self._dict is not None:
                for node in self._dict.values():
                    try:
                        node.fire_callbacks()
                    finally:
                        node.cleanup()
                self._dict.clear()
                self._dict = None

        self._lock = None

    # -------------------------------------------------------------------------
    # Configuration / state
    # -------------------------------------------------------------------------
    @property
    def id(self) -> str:
        """
        Get the unique identifier for this WeakConcurrentDict instance.

        Returns:
            str: The unique ULID-based identifier.
        """
        return self._id

    @property
    def auto_prune(self) -> bool:
        """
        Whether this dict automatically prunes dead entries.

        Returns:
            bool:
                True if auto-pruning is enabled, False otherwise.
        """
        return self._auto_prune

    @auto_prune.setter
    def auto_prune(self, value: bool) -> None:
        """
        Enable or disable automatic pruning of dead entries.

        Args:
            value:
                If True, dead entries may be removed automatically from GC path
                and from certain read paths. If False, pruning must be done
                manually via :meth:`prune`.

        Raises:
            RuntimeError:
                If this dict has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._auto_prune = bool(value)

    def freeze(self) -> None:
        """
        Freeze the dict, forbidding further mutations.

        Once frozen:

          * Mutating methods (`__setitem__`, `pop`, `clear`, `update`, etc.)
            will raise `TypeError`.
          * Some read operations may avoid acquiring the lock, assuming no
            concurrent structural changes from user code.

        NOTE:
            GC may still mark nodes dead in the background. This does not
            violate the "frozen" contract; it only affects liveness of values,
            not explicit user-driven structural changes.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = True

    def unfreeze(self) -> None:
        """
        Unfreeze the dict, allowing mutations again.

        After calling this, mutating methods behave normally.

        Raises:
            RuntimeError:
                If the dict has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = False

    @property
    def is_frozen(self) -> bool:
        """
        Check whether the dict is currently frozen.

        Returns:
            bool: True if frozen, False otherwise.
        """
        return self._freeze

    def _ensure_mutable(self) -> None:
        """
        Internal guard ensuring the dict is not frozen.

        Raises:
            TypeError:
                If the dict is currently frozen and a mutation is attempted.
        """
        if self._freeze:
            raise TypeError("Cannot modify a frozen WeakConcurrentDict")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _prune_dead_locked(self) -> None:
        """
        Prune all dead nodes from the internal dict.

        This method must be called with `self._lock` already held.
        """
        if self._dict is None:
            return

        dead_keys: List[_K] = []
        for k, node in self._dict.items():
            if node.dead:
                node.cleanup()
                dead_keys.append(k)

        for k in dead_keys:
            self._dict.pop(k, None)

    def prune(self) -> None:
        """
        Public entry point to prune all dead entries.

        This can be used even if `auto_prune` is False to clean the dict of
        keys whose values have already been collected.
        """
        self.check_cleaned()
        with self._lock:
            self._prune_dead_locked()

    def _snapshot_items(self) -> List[Tuple[_K, WeakRefNode[_V]]]:
        """
        Take a snapshot of the internal dict as a list of (key, node) pairs.

        If `auto_prune` is enabled, dead nodes are pruned during this snapshot.

        Returns:
            list[tuple[_K, WeakRefNode[_V]]]: Snapshot of (key, node) pairs.
        """
        if self._freeze:
            mapping = self._dict
            if mapping is None:
                return []

            if self._auto_prune:
                with self._lock:
                    self._prune_dead_locked()
                    mapping = self._dict
                    return list(mapping.items()) if mapping is not None else []
            return list(mapping.items())

        # Non-frozen path: use the lock.
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            mapping = self._dict
            return list(mapping.items()) if mapping is not None else []

    # -------------------------------------------------------------------------
    # Core CRUD operations
    # -------------------------------------------------------------------------
    def __getitem__(self, key: _K) -> _V:
        """
        Get a value by key, dereferencing the weak node.

        Args:
            key:
                The key to retrieve.

        Returns:
            _V: The live value associated with the key.

        Raises:
            KeyError:
                If the key is not present.
            DeadReferenceError:
                If the underlying value has been collected and not yet pruned.
        """
        self.check_cleaned()

        if self._freeze:
            if self._dict is None:
                raise KeyError(key)
            node = self._dict[key]
            return node.deref(strict=True)

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None or key not in self._dict:
                raise KeyError(key)
            node = self._dict[key]
            return node.deref(strict=True)

    def __setitem__(self, key: _K, value: _V) -> None:
        """
        Associate a key with a weakly-referenced value.

        Args:
            key:
                The key to set.
            value:
                The new value to store (wrapped in a `WeakRefNode`).

        Raises:
            TypeError:
                If the dict is frozen, or if the value is not compatible with
                `WeakRefNode` (e.g., cannot be weak-referenced).
        """
        self.check_cleaned()
        self._ensure_mutable()

        with self._lock:
            if self._dict is None:
                self._dict = {}
            old = self._dict.get(key)
            if old is not None:
                try:
                    old.fire_callbacks()
                finally:
                    old.cleanup()
            self._dict[key] = self._make_node(value)

    def __delitem__(self, key: _K) -> None:
        """
        Delete an item by key.

        Args:
            key:
                The key to delete.

        Raises:
            TypeError:
                If the dict is frozen.
            KeyError:
                If the key is not present.
        """
        self.check_cleaned()
        self._ensure_mutable()

        with self._lock:
            if self._dict is None or key not in self._dict:
                raise KeyError(key)
            node = self._dict.pop(key)
            try:
                node.fire_callbacks()
            finally:
                node.cleanup()

    def __contains__(self, key: object) -> bool:
        """
        Check if a key is present and its value is still alive.

        Args:
            key:
                The key to check.

        Returns:
            bool:
                True if the key exists and its value is live, False otherwise.
        """
        self.check_cleaned()

        if self._freeze:
            if self._dict is None:
                return False
            node = self._dict.get(key)
            if node is None:
                return False
            return not node.dead

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None:
                return False
            node = self._dict.get(key)
            return node is not None and not node.dead

    def clear(self) -> None:
        """
        Remove all entries from the dict.

        All nodes:
          * Have their callbacks fired.
          * Are then cleaned and discarded.

        Raises:
            TypeError:
                If the dict is frozen.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            if self._dict is None:
                return
            for node in self._dict.values():
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            self._dict.clear()

    def get(self, key: _K, default: Optional[_V] = None) -> Optional[_V]:
        """
        Return the value for key if it exists and is live, else default.

        Args:
            key:
                The key to look up.
            default:
                The default value to return if the key is not found or the
                value has been collected.

        Returns:
            Optional[_V]: The live value, or `default`.
        """
        self.check_cleaned()

        if self._freeze:
            if self._dict is None:
                return default
            node = self._dict.get(key)
            if node is None or node.dead:
                return default
            try:
                return node.deref(strict=True)
            except DeadReferenceError:
                return default

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None:
                return default
            node = self._dict.get(key)
            if node is None or node.dead:
                return default
            try:
                return node.deref(strict=True)
            except DeadReferenceError:
                return default

    def pop(self, key: _K, default: Optional[_V] = None) -> _V:
        """
        Remove the specified key and return its value.

        If the key is not found, return `default` if given, otherwise raise
        `KeyError`.

        Args:
            key:
                The key to remove.
            default:
                The default to return if the key is not found.

        Returns:
            _V: The live value associated with the key, or `default` if
            provided and the key is absent.

        Raises:
            TypeError:
                If the dict is frozen.
            KeyError:
                If the key is not found and `default` is not provided.
            DeadReferenceError:
                If the value exists but has been collected and `default` is
                not provided.
        """
        self.check_cleaned()
        self._ensure_mutable()

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None or key not in self._dict:
                if default is not None:
                    return default
                raise KeyError(key)

            node = self._dict.pop(key)
            try:
                value = node.deref(strict=True)
            finally:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            return value

    def popitem(self) -> Tuple[_K, _V]:
        """
        Remove and return an arbitrary ``(key, value)`` pair.

        Returns:
            tuple[_K, _V]: The key and live value removed.

        Raises:
            TypeError:
                If the dict is frozen.
            KeyError:
                If the dict is empty.
            DeadReferenceError:
                If the chosen entry's value has been collected and not yet
                pruned.
        """
        self.check_cleaned()
        self._ensure_mutable()

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None or not self._dict:
                raise KeyError("popitem(): dictionary is empty")

            key, node = self._dict.popitem()
            try:
                value = node.deref(strict=True)
            finally:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            return key, value

    def setdefault(self, key: _K, default: Optional[_V] = None) -> Optional[_V]:
        """
        If key is in the dict and its value is live, return it.

        Otherwise, insert key with a weakly-referenced `default` and return
        `default`.

        Args:
            key:
                The key to look up or insert.
            default:
                The value to use if key is missing.

        Returns:
            Optional[_V]: The existing or newly set live value.

        Raises:
            TypeError:
                If the dict is frozen.
            TypeError:
                If the `default` cannot be weak-referenced (raised by
                `WeakRefNode`).
        """
        self.check_cleaned()
        self._ensure_mutable()

        if default is None:
            # If default is None, and key is missing, we still insert a
            # WeakRefNode(None) which will raise TypeError; this mirrors
            # strong dict semantics except for weakref constraints.
            pass

        with self._lock:
            if self._dict is None:
                self._dict = {}
            node = self._dict.get(key)
            if node is not None and not node.dead:
                try:
                    return node.deref(strict=True)
                except DeadReferenceError:
                    # fall through to reset default
                    pass

            # Either missing, or dead; overwrite with default
            new_node = self._make_node(default)
            self._dict[key] = new_node
            return default

    def update(
            self,
            other: Optional[Union[Mapping[_K, _V], Iterable[Tuple[_K, _V]]]] = None,
            **kwargs: _V,
    ) -> None:
        """
        Update the dict with key/value pairs from another mapping, iterable
        of pairs, or keyword arguments.

        Existing keys are overwritten with new weakly-referenced values.

        Args:
            other:
                Another mapping or iterable of ``(key, value)`` pairs.
            **kwargs:
                Additional key/value pairs supplied as keyword arguments.

        Raises:
            TypeError:
                If the dict is frozen.
            TypeError:
                If any incoming value cannot be weak-referenced.
        """
        self.check_cleaned()
        self._ensure_mutable()

        if other is None:
            other = {}

        with self._lock:
            if self._dict is None:
                self._dict = {}

            # Mapping-like
            if hasattr(other, "keys"):
                for k in other.keys():
                    v = other[k]
                    old = self._dict.get(k)
                    if old is not None:
                        try:
                            old.fire_callbacks()
                        finally:
                            old.cleanup()
                    self._dict[k] = self._make_node(v)
            else:
                # Iterable of (k, v)
                for k, v in other:
                    old = self._dict.get(k)
                    if old is not None:
                        try:
                            old.fire_callbacks()
                        finally:
                            old.cleanup()
                    self._dict[k] = self._make_node(v)

            # kwargs
            for k, v in kwargs.items():
                old = self._dict.get(k)
                if old is not None:
                    try:
                        old.fire_callbacks()
                    finally:
                        old.cleanup()
                self._dict[k] = self._make_node(v)

    # -------------------------------------------------------------------------
    # Introspection / views
    # -------------------------------------------------------------------------
    def __len__(self) -> int:
        """
        Return the number of entries currently stored.

        If `auto_prune` is enabled, dead entries are removed before counting.

        Returns:
            int: The number of entries (live + any remaining dead if not
            pruned).
        """
        self.check_cleaned()

        if self._freeze:
            mapping = self._dict
            if mapping is None:
                return 0
            if self._auto_prune:
                # Delegate to snapshot helper for deterministic pruning.
                return len(self._snapshot_items())
            return len(mapping)

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            if self._dict is None:
                return 0
            return len(self._dict)

    def __bool__(self) -> bool:
        """
        Truthiness for the dict.

        Returns:
            bool:
                False if the dict is logically empty (or only dead entries
                remain and have been pruned), True otherwise.
        """
        return len(self) != 0

    def __iter__(self) -> Iterator[_K]:
        """
        Iterate over the keys in the dict.

        This uses a snapshot to avoid mutation-during-iteration issues.

        Returns:
            Iterator[_K]: An iterator over the keys.
        """
        self.check_cleaned()
        items = self._snapshot_items()
        return (k for k, _ in items)

    def __reversed__(self) -> Iterator[_K]:
        """
        Iterate over keys in reverse insertion order (snapshot).

        Mirrors ``dict.__reversed__`` semantics on a snapshot of keys.
        """
        self.check_cleaned()
        items = self._snapshot_items()
        return (k for k, _ in reversed(items))

    def keys(self) -> Collection[_K]:
        """
        Return a dynamic keys view (similar to ``dict.keys()``).
        """
        return _WeakDictKeysView(self)

    def values(self) -> Collection[_V]:
        """
        Return a dynamic values view (similar to ``dict.values()``).
        """
        return _WeakDictValuesView(self)

    def items(self) -> Collection[Tuple[_K, _V]]:
        """
        Return a dynamic items view (similar to ``dict.items()``).
        """
        return _WeakDictItemsView(self)

    def to_dict(self) -> Dict[_K, _V]:
        """
        Return a shallow snapshot of the dict as a plain Python dict.

        Returns:
            dict[_K, _V]: A new dict mapping keys to live values.

        Raises:
            DeadReferenceError:
                If any node is dead and has not yet been pruned.
        """
        self.check_cleaned()
        return dict(self.items())

    # -------------------------------------------------------------------------
    # Higher-order helpers (map / filter / reduce)
    # -------------------------------------------------------------------------
    def map(
            self, func: Callable[[_K, _V], Tuple[_K, _V]]
    ) -> "WeakConcurrentDict[_K, _V]":
        """
        Apply a function to each (key, value) pair and return a new
        WeakConcurrentDict with the transformed results.

        Args:
            func:
                A function that takes ``(key, value)`` and returns a new
                ``(key, value)`` pair.

        Returns:
            WeakConcurrentDict[_K, _V]:
                A new dictionary with transformed pairs.

        Raises:
            DeadReferenceError:
                If any node is dead while materializing current items.
        """
        self.check_cleaned()
        items = self.items()  # may raise DeadReferenceError

        new_items: List[Tuple[_K, _V]] = []
        for k, v in items:
            new_items.append(func(k, v))
        return WeakConcurrentDict(initial=new_items)

    def filter(
            self, func: Callable[[_K, _V], bool]
    ) -> "WeakConcurrentDict[_K, _V]":
        """
        Filter items based on a predicate and return a new WeakConcurrentDict.

        Args:
            func:
                Predicate of the form ``func(key, value) -> bool``. Items for
                which this returns True are retained.

        Returns:
            WeakConcurrentDict[_K, _V]:
                A new dictionary containing only items where the predicate
                returned True.

        Raises:
            DeadReferenceError:
                If any node is dead while materializing current items.
        """
        self.check_cleaned()

        new_items: List[Tuple[_K, _V]] = []
        for k, v in self.items():
            if func(k, v):
                new_items.append((k, v))
        return WeakConcurrentDict(initial=new_items)

    def reduce(
            self,
            func: Callable[[Any, Tuple[_K, _V]], Any],
            initial: Optional[Any] = None,
    ) -> Any:
        """
        Reduce the (key, value) pairs to a single result.

        Args:
            func:
                Callable of the form ``func(accumulator, (key, value)) -> Any``.
            initial:
                Optional initial accumulator value. If omitted, the reduction
                starts from the first item.

        Returns:
            Any: The final accumulated value.

        Raises:
            TypeError:
                If the dict is empty and `initial` is None.
            DeadReferenceError:
                If any node is dead while materializing current items.
        """
        self.check_cleaned()
        items = self.items()  # may raise DeadReferenceError

        if not items and initial is None:
            raise TypeError("reduce() of empty WeakConcurrentDict with no initial value")

        def pairwise_reduce(acc: Any, kv: Tuple[_K, _V]) -> Any:
            return func(acc, kv)

        if initial is None:
            return functools.reduce(pairwise_reduce, items)
        return functools.reduce(pairwise_reduce, items, initial)

    def batch_update(self, func: Callable[[Dict[_K, _V]], None]) -> None:
        """
        Perform a batch mutation under a single lock acquisition.

        This method materializes a strong `dict[key, value]` snapshot, lets
        the caller mutate that snapshot, then replaces all entries in this
        WeakConcurrentDict with new nodes wrapping the mutated values.

        Args:
            func:
                A callable that receives a **strongly-referenced** plain dict
                of the current live contents. It may mutate this dict
                arbitrarily.

                Signature:
                    ``func(values: dict[_K, _V]) -> None``

        Raises:
            TypeError:
                If the dict is frozen.
            DeadReferenceError:
                If a dead node is encountered while materializing current
                items before the batch update.
        """
        self.check_cleaned()
        self._ensure_mutable()

        with self._lock:
            # Materialize current live values (may raise DeadReferenceError).
            live_items = self.items()
            strong: Dict[_K, _V] = {k: v for k, v in live_items}

            # Let caller mutate this strong snapshot.
            func(strong)

            # Tear down old nodes.
            if self._dict is not None:
                for node in self._dict.values():
                    try:
                        node.fire_callbacks()
                    finally:
                        node.cleanup()
                self._dict.clear()
            else:
                self._dict = {}

            # Rebuild from mutated values.
            for k, v in strong.items():
                self._dict[k] = self._make_node(v)

    # -------------------------------------------------------------------------
    # Copying
    # -------------------------------------------------------------------------
    def copy(self) -> "WeakConcurrentDict[_K, _V]":
        """
        Return a shallow copy of this WeakConcurrentDict.

        The new dict contains the same live values, each wrapped in a new
        `WeakRefNode`.

        Returns:
            WeakConcurrentDict[_K, _V]: A new WeakConcurrentDict instance.
        """
        self.check_cleaned()
        return WeakConcurrentDict(
            initial=self.items(),  # re-wrap values
            auto_prune=self._auto_prune,
        )

    def __copy__(self) -> "WeakConcurrentDict[_K, _V]":
        """
        Shallow copy support for :mod:`copy`.

        Returns:
            WeakConcurrentDict[_K, _V]: A shallow copy of this dict.
        """
        return self.copy()

    def __deepcopy__(self, memo: dict) -> "WeakConcurrentDict[_K, _V]":
        """
        Return a deep copy of this WeakConcurrentDict.

        Args:
            memo:
                Memoization dictionary used by :mod:`copy` to avoid duplicating
                shared objects and handle cycles.

        Returns:
            WeakConcurrentDict[_K, _V]:
                A new WeakConcurrentDict containing deep-copied values.
        """
        self.check_cleaned()
        deep_items: List[Tuple[_K, _V]] = []
        for k, v in self.items():
            deep_items.append((deepcopy(k, memo), deepcopy(v, memo)))
        return WeakConcurrentDict(
            initial=deep_items,
            auto_prune=self._auto_prune,
        )

    # -------------------------------------------------------------------------
    # Dunder & identity
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a debug representation of the WeakConcurrentDict.

        Dead entries are represented as ``'<dead>'`` to avoid raising during
        repr generation.
        """
        self.check_cleaned()
        parts: List[str] = []
        for k, node in self._snapshot_items():
            val = node.deref(strict=False)
            display = val if val is not None else "<dead>"
            parts.append(f"{k!r}: {display!r}")
        inner = ", ".join(parts)
        return f"{self.__class__.__name__}({{{inner}}})"

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the dict.
        """
        self.check_cleaned()
        return str(self.to_dict())

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison with another WeakConcurrentDict or a plain dict.

        Two WeakConcurrentDict instances are considered equal if their
        `to_dict()` snapshots (live values only) are equal.

        Args:
            other:
                The object to compare against.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, WeakConcurrentDict):
            # Compare snapshots of live values.
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return False

    def __or__(self, other: Mapping[_K, _V] | Iterable[Tuple[_K, _V]]) -> "WeakConcurrentDict[_K, _V]":
        """
        Merge two mappings/iterables into a new WeakConcurrentDict (PEP 584 style).
        """
        self.check_cleaned()
        if other is None:
            other = {}
        merged = list(self.items())
        # other may be mapping-like or iterable
        if hasattr(other, "items"):
            merged.extend(list(other.items()))  # type: ignore[arg-type]
        else:
            merged.extend(list(other))  # type: ignore[arg-type]
        return WeakConcurrentDict(initial=merged, auto_prune=self._auto_prune)

    def __ior__(self, other: Mapping[_K, _V] | Iterable[Tuple[_K, _V]]) -> "WeakConcurrentDict[_K, _V]":
        """
        In-place merge (|=) with another mapping/iterable (PEP 584 style).
        """
        self.update(other)
        return self

    def __ror__(self, other: Mapping[_K, _V] | Iterable[Tuple[_K, _V]]) -> "WeakConcurrentDict[_K, _V]":
        """
        Right-hand merge to support ``mapping | WeakConcurrentDict`` (PEP 584 style).

        The right-hand operand (``self``) wins on key conflicts, mirroring built-in dict behavior.
        """
        # Build from the left operand first, then merge self so our keys win.
        left = WeakConcurrentDict(initial=other, auto_prune=self._auto_prune)
        return left.__or__(self)

    def __ne__(self, other: object) -> bool:
        """
        Inequality comparison.

        Args:
            other:
                The object to compare against.

        Returns:
            bool: True if not equal, False otherwise.
        """
        return not self.__eq__(other)

    # -------------------------------------------------------------------------
    # Context managers
    # -------------------------------------------------------------------------
    def __enter__(self) -> "WeakConcurrentDict[_K, _V]":
        """
        Enter the runtime context for this dict.

        This acquires the internal lock and returns the dict itself, allowing:

            with weak_dict:
                # direct, locked usage

        **Warning**:
            Within the context, you are responsible for avoiding long/blocking
            operations while holding the lock.

        Returns:
            WeakConcurrentDict[_K, _V]: This instance.

        Raises:
            RuntimeError:
                If the dict has already been cleaned.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the runtime context for this dict.

        This releases the internal lock acquired in `__enter__`.

        Args:
            exc_type:
                Exception type, if any.
            exc_val:
                Exception instance, if any.
            exc_tb:
                Traceback object, if any.
        """
        try:
            self._lock.release()
        except RuntimeError:
            # In case it's already released or cleaned.
            pass
