import threading
import ulid
from typing import Any, Callable, Optional, List, TypeVar, Generic
from collections.abc import Iterable, Iterator
from functools import reduce as _reduce

# Melder Imports
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.data_structures.weak_data_structures.weak_ref_node import WeakRefNode


_T = TypeVar("_T")


class WeakConcurrentList(Generic[_T], Cleanable):
    """
    WeakConcurrentList
    ==================

    A thread-safe list-like container that stores **weak references** to objects
    instead of strong references. This allows items to be garbage-collected without
    the list's explicit involvement, making it suitable for object tracking and resource management.

    Key Properties:
    * **Weak References:** Internally stores `WeakRefNode[_T]` instances.
    * **Dereferencing:** Accessors (like `__getitem__` and iteration) dereference the node, returning the live object.
    * **Dead Entries:** Accessing a dead entry (where the referent was collected) raises `DeadReferenceError`.
    * **Pruning:** Supports optional automatic pruning of dead entries via GC callbacks (`auto_prune`).
    * **Concurrency:** Synchronized via `threading.RLock` or `AgenticRLock`.

    Weak Semantics and Callbacks:
    * **GC Path:** When a referenced object is collected, the weakref callback fires, marks the node dead, and invokes the list's `_on_node_collected` method.
    * **Per-Node Callbacks:** Can be attached (e.g., via `append_with_callback`) and are fired both on GC and during explicit removal/cleanup.
    """

    __slots__ = (
            Cleanable.__slots__
            + ["_lock", "_list", "_freeze", "_id", "_auto_prune"]
    )

    def __init__(
            self,
            initial: Optional[Iterable[_T]] = None,
            auto_prune: bool = False,
    ) -> None:
        """
        Initialize the WeakConcurrentList.

        Args:
            initial (Iterable[_T], optional):
                Initial iterable of objects to weak-reference and store. Defaults to None.
            auto_prune (bool, optional):
                If True, enables GC callbacks to attempt to prune dead nodes immediately. Defaults to False.
        """
        super().__init__()
        self._id: str = str(ulid.ULID())
        self._lock: threading.RLock = threading.RLock()

        self._list: List[WeakRefNode[_T]] = []
        self._freeze: bool = False
        self._auto_prune: bool = auto_prune

        if initial:
            for item in initial:
                self._list.append(self._make_node(item))

    # -------------------------------------------------------------------------
    # Internal helpers for node construction and GC callbacks
    # -------------------------------------------------------------------------

    def _make_node(self, item: _T) -> WeakRefNode[_T]:
        """
        Internal

        Creates a `WeakRefNode` instance wired to this list's GC callback (`_on_node_collected`).

        Args:
            item (_T): The object to store a weak reference to.

        Returns:
            WeakRefNode[_T]: The newly created node.
        """
        return WeakRefNode(item, on_collect=self._on_node_collected)

    def _on_node_collected(self, node: WeakRefNode[_T]) -> None:
        """
        Internal

        Parent/container callback invoked from the node's weakref GC path.

        If `auto_prune` is enabled, this method attempts to acquire the lock and remove the node by identity. This is acceptable only because the node's callbacks have already fired.

        Args:
            node (WeakRefNode[_T]): The node whose referent was collected.
        """
        if self._cleaned or not self._auto_prune:
            return

        try:
            self._lock.acquire()
        except Exception:
            # Cannot acquire lock on GC path, skip pruning
            return

        try:
            if self._cleaned or self._list is None:
                return

            # Remove by identity if still present.
            for idx, n in enumerate(self._list):
                if n is node:
                    # GC already fired callbacks; just cleanup node resources and drop it.
                    try:
                        node.cleanup()
                    finally:
                        del self._list[idx]
                    break
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
        Dispose (clear) this WeakConcurrentList, releasing its nodes and resources.

        Once cleaned:
        * The `_cleaned` flag is set to True.
        * All internal nodes are signaled, cleaned, and their references dropped.
        * The internal list and lock are cleared.

        Raises:
            RuntimeError: If called while the lock is held externally.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            for node in self._list:
                # Explicit removal path: fire callbacks, then cleanup.
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            self._list.clear()
            self._list = None
        self._lock = None

    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """
        Returns the unique identifier for this WeakConcurrentList instance.

        Returns:
            str: The ULID identifier.
        """
        return self._id

    @property
    def auto_prune(self) -> bool:
        """
        Returns whether dead nodes are automatically pruned:
        * Via GC callbacks (`_on_node_collected`).
        * Before certain read operations (`len`, `__iter__`, `to_list`).

        Returns:
            bool: True if auto-pruning is enabled, False otherwise.
        """
        return self._auto_prune

    @auto_prune.setter
    def auto_prune(self, value: bool) -> None:
        """
        Sets whether automatic pruning of dead nodes is enabled.

        Args:
            value (bool): The new value for auto-pruning.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._auto_prune = bool(value)

    def freeze(self) -> None:
        """
        Freezes the list, preventing structural modifications (`append`, `insert`, `remove`, `clear`, etc.).

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = True

    @property
    def is_frozen(self) -> bool:
        """
        Returns whether the list is frozen.

        Returns:
            bool: True if frozen, False otherwise.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        return self._freeze

    def unfreeze(self) -> None:
        """
        Unfreezes the list, allowing structural modifications again.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = False

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _ensure_not_frozen(self) -> None:
        """
        Internal

        Checks the freeze state and raises an error if modifications are attempted on a frozen list.

        Raises:
            TypeError: If the list is frozen.
        """
        if self._freeze:
            raise TypeError("Cannot modify a frozen WeakConcurrentList")

    def _prune_dead_locked(self) -> None:
        """
        Internal

        Removes all dead nodes from the underlying list and cleans up the node objects.

        Must be called with `self._lock` already held.
        """
        new_list: List[WeakRefNode[_T]] = []
        for node in self._list:
            if node.dead:
                node.cleanup()
            else:
                new_list.append(node)
        self._list = new_list

    def prune(self) -> None:
        """
        Explicitly removes all dead nodes from the list.

        This is safe to call at any time, regardless of the `auto_prune` setting.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self._prune_dead_locked()

    def _materialize_slice(self, nodes: List[WeakRefNode[_T]]) -> List[_T]:
        """
        Internal

        Helper to convert a list of nodes into concrete values.

        Args:
            nodes (List[WeakRefNode[_T]]): The list of nodes to dereference.

        Returns:
            List[_T]: The list of live objects.

        Raises:
            DeadReferenceError: If any node in the slice is dead.
        """
        result: List[_T] = []
        for node in nodes:
            # Strict=True ensures DeadReferenceError is raised
            result.append(node.deref(strict=True))
        return result

    # -------------------------------------------------------------------------
    # Core sequence interface
    # -------------------------------------------------------------------------

    def __getitem__(self, index: int | slice) -> _T | List[_T]:
        """
        Get an item or a slice from the list.

        Args:
            index (int | slice): The index or slice object.

        Returns:
            _T | List[_T]: A single live item or a list of live items.

        Raises:
            RuntimeError: If the list has been cleaned.
            IndexError: If the index is out of range.
            DeadReferenceError: If the accessed item(s) have been garbage collected.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()

            if isinstance(index, int):
                try:
                    node = self._list[index]
                except IndexError:
                    raise IndexError("WeakConcurrentList index out of range")
                return node.deref(strict=True)
            else:
                nodes = self._list[index]
                return self._materialize_slice(nodes)

    def __setitem__(self, index: int | slice, value: _T | Iterable[_T]) -> None:
        """
        Set an item or slice in the list, wrapping new values in `WeakRefNode`.

        Args:
            index (int | slice): The index or slice object.
            value (_T | Iterable[_T]): The new item or iterable of items to set.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
            IndexError: If the index is out of range.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            if isinstance(index, int):
                try:
                    node = self._make_node(value)
                    self._list[index] = node
                except IndexError:
                    raise IndexError("WeakConcurrentList index out of range")
            else:
                if isinstance(value, Iterable) and not isinstance(value, str):
                    nodes = [self._make_node(v) for v in value]
                else:
                    nodes = [self._make_node(value)]
                self._list[index] = nodes

    def __delitem__(self, index: int | slice) -> None:
        """
        Delete an item or slice from the list.

        Before removal, callbacks are fired and nodes are cleaned.

        Args:
            index (int | slice): The index or slice object to delete.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
            IndexError: If the index is out of range.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            try:
                if isinstance(index, int):
                    node = self._list[index]
                    try:
                        node.fire_callbacks()
                    finally:
                        node.cleanup()
                    del self._list[index]
                else:
                    nodes = self._list[index]
                    for node in nodes:
                        try:
                            node.fire_callbacks()
                        finally:
                            node.cleanup()
                    del self._list[index]
            except IndexError:
                if isinstance(index, int):
                    raise IndexError("WeakConcurrentList index out of range")
                else:
                    raise

    def append(self, item: _T) -> None:
        """
        Append an item (weakly-referenced) to the end of the list.

        Args:
            item (_T): The item to append.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            self._list.append(self._make_node(item))

    def append_with_callback(
            self,
            item: _T,
            on_collect: Callable[[WeakRefNode[_T]], None],
    ) -> None:
        """
        Append an item with a per-node collection callback.

        The provided callback is invoked when the referent is collected (GC path) or when the node is explicitly removed/cleaned up.

        Args:
            item (_T): The item to append.
            on_collect (Callable[[WeakRefNode[_T]], None]): The callback function to execute on node collection/cleanup.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            node = self._make_node(item)
            node.add_callback(on_collect)
            self._list.append(node)

    def extend(self, items: Iterable[_T]) -> None:
        """
        Extend the list by appending weak references to elements from the iterable.

        Args:
            items (Iterable[_T]): The iterable containing items to append.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            for x in items:
                self._list.append(self._make_node(x))

    def insert(self, index: int, item: _T) -> None:
        """
        Insert an item (weakly-referenced) at the specified index.

        Args:
            index (int): The index at which to insert the item.
            item (_T): The item to insert.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            self._list.insert(index, self._make_node(item))

    def remove(self, item: _T) -> None:
        """
        Remove the first occurrence of an item from the list based on value equality (`==`).

        Note: Dead entries are skipped. If `auto_prune` is enabled, pruning occurs before search.

        Args:
            item (_T): The item value to search for and remove.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
            ValueError: If the item is not found in the live entries of the list.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()

            for idx, node in enumerate(self._list):
                try:
                    if node.deref(strict=True) == item:
                        try:
                            node.fire_callbacks()
                        finally:
                            node.cleanup()
                        del self._list[idx]
                        return
                except DeadReferenceError:
                    continue
            raise ValueError(f"'{item}' not in WeakConcurrentList")

    def pop(self, index: int = -1) -> _T:
        """
        Remove and return the item at the given index (default is last).

        Args:
            index (int): The index of the item to pop (defaults to -1).

        Returns:
            _T: The item that was popped.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
            IndexError: If the list is empty or the index is out of range.
            DeadReferenceError: If the item at the index was garbage collected.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            if not self._list:
                raise IndexError("pop from empty WeakConcurrentList")

            try:
                node = self._list.pop(index)
            except IndexError:
                raise IndexError("WeakConcurrentList index out of range for pop")

            try:
                value = node.deref(strict=True)
            finally:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            return value

    def clear(self) -> None:
        """
        Remove all items from the list, cleaning up all internal nodes.

        Raises:
            RuntimeError: If the list has been cleaned.
            TypeError: If the list is frozen.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            for node in self._list:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            self._list.clear()

    # -------------------------------------------------------------------------
    # Pickling / deepcopy support
    # -------------------------------------------------------------------------
    def __getstate__(self) -> dict:
        """
        Build a serialization-friendly snapshot of the list state.

        Returns:
            dict: Snapshot payload containing live values and configuration
            flags, but excluding the live lock and node objects.
        """
        return {
            "_id": self._id,
            "_freeze": self._freeze,
            "_auto_prune": self._auto_prune,
            "_values": self.to_list(),
            "_cleaned": self._cleaned,
        }

    def __setstate__(self, state: dict) -> None:
        """
        Restore this list from a pickled or deep-copied state payload.
        """
        self._id = state.get("_id", str(ulid.ULID()))
        self._freeze = state.get("_freeze", False)
        self._auto_prune = state.get("_auto_prune", False)
        self._cleaned = state.get("_cleaned", False)
        self._lock = threading.RLock()
        self._list = []
        if self._cleaned:
            return
        for v in state.get("_values", []):
            self._list.append(self._make_node(v))

    def reverse(self) -> None:
        """
        Reverse the list in place (order of nodes), preserving weak semantics.
        """
        self.check_cleaned()
        self._ensure_not_frozen()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            self._list.reverse()

    def __len__(self) -> int:
        """
        Returns the number of nodes (dead or alive) in the list.

        If `auto_prune` is enabled, dead nodes are pruned before counting.

        Returns:
            int: The number of nodes in the list.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            return len(self._list)

    def count(self, item: Any) -> int:
        """
        Count occurrences of ``item`` among live entries.

        Returns:
            int: Number of live entries equal to `item`.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            total = 0
            for node in self._list:
                try:
                    if node.deref(strict=True) == item:
                        total += 1
                except DeadReferenceError:
                    if self._auto_prune:
                        continue
                    raise
            return total

    def index(self, item: Any, start: int = 0, stop: Optional[int] = None) -> int:
        """
        Return the first index of ``item`` among live entries.

        Returns:
            int: Index of the first matching live value.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            end = len(self._list) if stop is None else min(stop, len(self._list))
            for idx in range(start, end):
                node = self._list[idx]
                try:
                    if node.deref(strict=True) == item:
                        return idx
                except DeadReferenceError:
                    if self._auto_prune:
                        continue
                    raise
            raise ValueError(f"{item!r} is not in list")

    def copy(self) -> "WeakConcurrentList[_T]":
        """
        Return a shallow copy containing only current live values.
        """
        return WeakConcurrentList(self.to_list(), auto_prune=self._auto_prune)

    def __iter__(self) -> Iterator[_T]:
        """
        Iterates over the live values in the list.

        A snapshot is taken under the lock. Dead nodes encountered during iteration will raise `DeadReferenceError`.

        Yields:
            _T: The next live item.

        Raises:
            RuntimeError: If the list has been cleaned.
            DeadReferenceError: If a node in the snapshot has been garbage collected.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            snapshot = list(self._list)

        def _iter_values() -> Iterator[_T]:
            for node in snapshot:
                yield node.deref(strict=True)

        return _iter_values()

    def __reversed__(self) -> Iterator[_T]:
        """
        Iterate over live elements in reverse order.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            snapshot = list(reversed(self._list))
        def _rev() -> Iterator[_T]:
            for node in snapshot:
                yield node.deref(strict=True)
        return _rev()

    def __contains__(self, item: Any) -> bool:
        """
        Check if an item is present in the live entries of the list.

        If `auto_prune` is enabled, dead nodes are pruned before search.

        Args:
            item (Any): The value to check for presence.

        Returns:
            bool: True if the item is found, False otherwise.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            for node in self._list:
                try:
                    if node.deref(strict=True) == item:
                        return True
                except DeadReferenceError:
                    continue
            return False

    def __repr__(self) -> str:
        """
        Returns the official string representation of the WeakConcurrentList, showing live values and `<dead>` markers.

        Returns:
            str: The official string representation.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            values: List[Any] = []
            for node in self._list:
                val = node.deref(strict=False)
                values.append(val if val is not None else "<dead>")
            return f"WeakConcurrentList({values!r})"

    def __str__(self) -> str:
        """
        Returns the informal string representation of the WeakConcurrentList (list of values).

        Returns:
            str: The informal string representation.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            values: List[Any] = []
            for node in self._list:
                val = node.deref(strict=False)
                values.append(val if val is not None else "<dead>")
            return str(values)

    def __bool__(self) -> bool:
        """
        Returns True if the list contains at least one node (dead or alive).

        If `auto_prune` is enabled, dead nodes are pruned first.

        Returns:
            bool: True if the list is non-empty, False otherwise.
        """
        return len(self) != 0

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison against another list/tuple/WeakConcurrentList using live values.
        """
        if isinstance(other, WeakConcurrentList):
            try:
                return self.to_list() == other.to_list()
            except DeadReferenceError:
                return False
        if isinstance(other, (list, tuple)):
            try:
                return self.to_list() == list(other)
            except DeadReferenceError:
                return False
        return False

    def __ne__(self, other: object) -> bool:
        """
        Return the logical negation of `__eq__(other)` for convenience.

        Returns:
            bool: True when the other object is not equal to this list.
        """
        return not self.__eq__(other)

    def to_list(self) -> List[_T]:
        """
        Returns a **strong** standard Python list containing only the currently **live** values.

        Returns:
            List[_T]: A new list containing strong references to the live items.

        Raises:
            RuntimeError: If the list has been cleaned.
            DeadReferenceError: If a node is found to be dead during conversion.
        """
        self.check_cleaned()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            # Strict=True ensures DeadReferenceError is raised
            return [node.deref(strict=True) for node in self._list]

    # -------------------------------------------------------------------------
    # Higher-order helpers
    # -------------------------------------------------------------------------
    def map(self, func: Callable[[_T], _T]) -> "WeakConcurrentList[_T]":
        """
        Apply ``func`` to each live element and return a new weak list of results.
        """
        return WeakConcurrentList((func(v) for v in self.to_list()), auto_prune=self._auto_prune)

    def filter(self, func: Callable[[_T], bool]) -> "WeakConcurrentList[_T]":
        """
        Keep only live elements where ``func(value)`` returns True.
        """
        return WeakConcurrentList((v for v in self.to_list() if func(v)), auto_prune=self._auto_prune)

    def reduce(self, func: Callable[[Any, _T], Any], initial: Any) -> Any:
        """
        Reduce the live elements using ``func`` starting from ``initial``.

        Returns:
            Any: Reduced accumulator value.
        """
        return _reduce(func, self.to_list(), initial)

    # -------------------------------------------------------------------------
    # Context managers (same pattern as ConcurrentList)
    # -------------------------------------------------------------------------

    def __enter__(self):
        """
        Enter the synchronization context and acquire the internal lock.

        Returns:
            WeakConcurrentList[_T]: The list instance.

        Raises:
            RuntimeError: If the list has been cleaned.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the synchronization context and release the internal lock.
        """
        try:
            self._lock.release()
        except RuntimeError:
            pass
