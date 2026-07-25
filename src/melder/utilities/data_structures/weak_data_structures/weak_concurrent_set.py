import threading
from copy import deepcopy
from types import TracebackType
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Set,
    TypeVar,
    ClassVar,
)

# Melder Imports
from melder.utilities.custom_exceptions.dead_reference_error import DeadReferenceError
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.ulid_factory import new_ulid
from melder.utilities.data_structures.weak_data_structures.weak_ref_node import WeakRefNode

_T = TypeVar("_T")


class WeakConcurrentSet(Generic[_T], Cleanable):
    """
    WeakConcurrentSet
    =================

    A thread-safe, *weakly referenced* set of objects.

    This container stores **WeakRefNode[_T]** internally and exposes the
    underlying objects as if it were a normal set:

    * Values are held via `WeakRefNode` (weak references).
    * When a value is garbage-collected:
      - Its `WeakRefNode` marks itself dead.
      - The node's GC callback may inform this set (via `_on_node_collected`).
      - If `auto_prune` is enabled, the node is removed automatically.
    * Accessors (iteration, `to_set`, etc.) dereference nodes and will raise
      `DeadReferenceError` if a dead entry is encountered, unless it has
      already been pruned.

    Concurrency
    -----------
    * A per-instance lock (`threading.RLock` or `AgenticRLock`) protects
      structural mutations.
    * `freeze()` / `unfreeze()`:
      - When frozen, **mutations are forbidden** and raise `TypeError`.
      - Read operations may skip some locking (they assume no user-driven
        structural changes once frozen).
    * Auto-pruning:
      - If `auto_prune=True`, dead nodes are removed:
        - From GC callback path (best-effort, GC thread).
        - Or on certain read paths (`__len__`, `__iter__`, `to_set`) when lock
          is held.

    Cleanable Contract
    ------------------
    * `cleanup()`:
      - Idempotent.
      - Fires any node callbacks via `node.fire_callbacks()`.
      - Calls `node.cleanup()` on all nodes.

    MEMBERSHIP IS BY IDENTITY OF A LIVING OBJECT:
        An object leaves this set by being collected, not by being removed. That
        makes membership a question about LIFETIME rather than about content:
        "is this thing still alive and known to me". A member that nothing else
        references drops out on its own.

        Consequence: `x in s` is a point-in-time answer that can be falsified by
        the next collection, and `len(s)` is advisory unless you just pruned.

    Responsibilities:
        - Hold members weakly, without ordering.
        - Dereference on access, raising rather than yielding a dead entry.
        - Optionally prune collected members automatically.
        - Fire node callbacks on GC and at teardown.

    Owned State:
        - The node collection, the lock, the frozen flag, the auto-prune flag,
          and an id. The NODES are owned; their referents are not.

    Threading:
        - A per-instance lock protects structural mutation.
        - Frozen mode lets reads skip some locking by assuming no user-driven
          structural change - but NOT no change: collection still removes
          members while frozen, because GC does not respect the freeze.
        - GC callbacks arrive on the collecting thread; pruning from there is
          best-effort.

    Lifecycle / Cleanup:
        - Idempotent. Fires node callbacks BEFORE cleaning nodes, so registered
          handlers still run at teardown rather than being dropped.

    Registration:
        Exported for direct construction and use (owner ruling 2026-07-19).

    Subsystem Context:
        The membership member of the weak-container trio beside
        `WeakConcurrentDict` (mapping) and `WeakConcurrentList` (ordered), all
        three built on `WeakRefNode`. It carries neither keys nor order, so it
        is the smallest of the three - the shared liveness rules with nothing
        added on top.

    System Context:
        Substrate-level, outside the DGR boot order. It suits the
        "who is currently participating" question - membership registries that
        must not keep participants alive merely by remembering them.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Set holding members WEAKLY - membership is a question "
        "about lifetime, since a member nothing else references drops out on "
        "its own. `x in s` is point-in-time and len() is advisory unless you "
        "just pruned. freeze() speeds reads but does not stop collection."
    )

    __slots__ = (
            Cleanable.__slots__
            + ["_lock", "_set", "_freeze", "_id", "_auto_prune"]
    )

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------
    def __init__(
            self,
            initial: Optional[Iterable[_T]] = None,
            auto_prune: bool = False,
    ) -> None:
        """
        Initialize a new WeakConcurrentSet.

        Args:
            initial:
                Optional iterable of initial objects to weak-reference and insert
                into the set. Each element must be weak-referenceable and
                hashable (see notes below).
            auto_prune:
                If True, the set will try to automatically remove dead nodes:
                    * From GC callbacks via `_on_node_collected`.
                    * From certain read paths that call `_prune_dead_locked()`.

        Raises:
            TypeError:
                If `initial` is a string/bytes-like object, or any element:
                  - cannot be weak-referenced, or
                  - is not hashable (once you make WeakRefNode enforce that).

        Returns:
            None.
        """
        super().__init__()

        self._id: str = new_ulid()
        self._freeze: bool = False
        self._auto_prune: bool = bool(auto_prune)
        self._lock: threading.RLock = threading.RLock()

        self._set: Set[WeakRefNode[_T]] = set()

        if initial is None:
            return

        # Strings/bytes are ambiguous as "iterables of characters"
        if isinstance(initial, (str, bytes, bytearray)):
            raise TypeError(
                "WeakConcurrentSet does not allow strings/bytes as the "
                "initial iterable; wrap them in a list or other container."
            )

        # Ensure it's iterable and populate nodes
        for item in initial:
            self._set.add(self._make_node(item))

    # -------------------------------------------------------------------------
    # Internal node helpers
    # -------------------------------------------------------------------------
    def _make_node(self, item: _T) -> WeakRefNode[_T]:
        """
        Create a WeakRefNode for this set, wiring the GC callback.

        Args:
            item:
                The object to weak-reference. Must support weak references and
                be compatible with your WeakRefNode hashing policy.

        Returns:
            WeakRefNode[_T]: The created node.

        Raises:
            TypeError:
                If the object cannot be weak-referenced (WeakRefNode will raise).
        """
        # NOTE: For safe usage inside sets, WeakRefNode.__hash__ MUST be stable.
        return WeakRefNode(item, on_collect=self._on_node_collected)

    def _on_node_collected(self, node: WeakRefNode[_T]) -> None:
        """
        GC-path callback invoked when a referent is collected.

        This is called from `WeakRefNode._weakref_callback` when:
            - The referent is about to be finalized.
            - The node has marked itself dead and fired its own callbacks.

        Behavior:
            * If this set is already cleaned or auto_prune is False -> no-op.
            * Otherwise, best-effort:
              - Acquire the set lock.
              - If the node is still present, remove and cleanup it.

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
            if self._cleaned or self._set is None:
                return

            if node in self._set:
                try:
                    # GC path: callbacks already fired by WeakRefNode itself.
                    node.cleanup()
                finally:
                    self._set.discard(node)
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
        Deterministically dispose this WeakConcurrentSet.

        Once cleaned:

          * `_cleaned` is set to True.
          * All remaining nodes:
              - Have their callbacks fired via `node.fire_callbacks()`.
              - Are then `cleanup()`-ed.
          * The internal set is cleared and set to None.
          * The lock is released and nulled.
          * If using AgenticRLock, its `cleanup()` is invoked best-effort.

        This method is **idempotent** and thread-safe.

        Returns:
            None.
        """
        if self._cleaned:
            return

        with self._lock:
            if self._cleaned:
                return

            self._cleaned = True

            for node in self._set:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            self._set.clear()

            del self._set
        del self._lock

    # -------------------------------------------------------------------------
    # Configuration / state
    # -------------------------------------------------------------------------
    @property
    def id(self) -> str:
        """
        Get the unique identifier for this WeakConcurrentSet instance.

        Returns:
            str: The unique ULID-based identifier.
        """
        return self._id

    @property
    def auto_prune(self) -> bool:
        """
        Whether this set automatically prunes dead nodes.

        Returns:
            bool:
                True if auto-pruning is enabled, False otherwise.
        """
        return self._auto_prune

    @auto_prune.setter
    def auto_prune(self, value: bool) -> None:
        """
        Enable or disable automatic pruning of dead nodes.

        Args:
            value:
                If True, dead nodes will be removed automatically from GC path
                and from certain read paths. If False, pruning must be done
                manually via `prune()`.

        Raises:
            RuntimeError:
                If this set has already been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._auto_prune = bool(value)

    def freeze(self) -> None:
        """
        Freeze the set, forbidding further mutations.

        Once frozen:

          * Mutating methods (`add`, `remove`, `clear`, etc.) will raise
            `TypeError`.
          * Some read operations may avoid acquiring the lock, assuming no
            concurrent structural changes from user code.

        NOTE:
            GC may still mark nodes dead in the background. This does not
            violate the "frozen" contract; it only affects *liveness* of
            entries, not the structure of `_set` from user perspective.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = True

    def unfreeze(self) -> None:
        """
        Unfreeze the set, allowing mutations again.

        After calling this, mutating methods behave normally.

        Raises:
            RuntimeError:
                If the set has been cleaned.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._freeze = False

    @property
    def is_frozen(self) -> bool:
        """
        Check whether the set is currently frozen.

        Returns:
            bool: True if frozen, False otherwise.
        """
        return self._freeze

    def _ensure_mutable(self) -> None:
        """
        Internal guard ensuring the set is not frozen.

        Raises:
            TypeError:
                If the set is currently frozen and a mutation is attempted.
        """
        if self._freeze:
            raise TypeError("Cannot modify a frozen WeakConcurrentSet")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _prune_dead_locked(self) -> None:
        """
        Prune all dead nodes from the internal set.

        This method must be called with `self._lock` already held.

        Dead nodes:
          * Have already had their GC callbacks fired.
          * Are explicitly `cleanup()`-ed here before being discarded.
        """
        if self._set is None:
            return

        alive: Set[WeakRefNode[_T]] = set()
        for node in self._set:
            if node.dead:
                node.cleanup()
            else:
                alive.add(node)
        self._set = alive

    def prune(self) -> None:
        """
        Public entry point to prune all dead nodes.

        This can be used even if `auto_prune` is False to clean the set of
        nodes whose referents have already been collected.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._prune_dead_locked()

    def _snapshot_nodes(self) -> Set[WeakRefNode[_T]]:
        """
        Take a snapshot of the internal node set for read-only use.

        If `auto_prune` is enabled, dead nodes are pruned during this snapshot.

        Returns:
            Set[WeakRefNode[_T]]: A copy of the internal node set.
        """
        if self._freeze:
            # In frozen mode, structure should not change from user code, but
            # we still defensively copy to avoid surprises if GC mutates state.
            nodes = self._set
            if nodes is None:
                return set()
            # No lock: frozen is read-most, GC path is already best-effort.
            if self._auto_prune:
                # Best-effort pruning without lock is *not* safe, so only
                # prune under lock when needed.
                with self._lock:
                    self._prune_dead_locked()
                    nodes = self._set
                    return set(nodes) if nodes is not None else set()
            return set(nodes)

        # Non-frozen path: use the lock.
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            nodes = self._set
            return set(nodes) if nodes is not None else set()

    def _values_from_nodes(self, nodes: Iterable[WeakRefNode[_T]]) -> Set[_T]:
        """
        Materialize a set of live values from a node iterable.

        Args:
            nodes:
                Iterable of WeakRefNode instances.

        Returns:
            set[_T]: A new set of underlying values.

        Raises:
            DeadReferenceError:
                If any node in the iterable is dead.
        """
        result: Set[_T] = set()
        for node in nodes:
            # strict=True ensures we loudly fail if a dead node slips through.
            result.add(node.deref(strict=True))
        return result

    # -------------------------------------------------------------------------
    # Core CRUD operations
    # -------------------------------------------------------------------------
    def add(self, item: _T) -> None:
        """
        Add an item to the set (weakly referenced).

        Args:
            item:
                The object to insert. Must:
                  * Support weak references.
                  * Be hashable for correct set semantics (via WeakRefNode).

        Raises:
            TypeError:
                If the set is frozen, or if the item is not compatible with
                WeakRefNode (e.g., cannot be weak-referenced).

        Returns:
            None.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            self._set.add(self._make_node(item))

    def remove(self, item: _T) -> None:
        """
        Remove the first live occurrence of a value equal to `item`.

        Membership is determined by dereferencing each node and comparing the
        underlying value via `==`.

        Args:
            item:
                The value to remove.

        Raises:
            KeyError:
                If no live node with a value equal to `item` is found.

        Returns:
            None.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()

            # Linear scan; we don't rely on node hashing here.
            for node in list(self._set):
                try:
                    if node.deref(strict=True) == item:
                        try:
                            node.fire_callbacks()
                        finally:
                            node.cleanup()
                        self._set.discard(node)
                        return
                except DeadReferenceError:
                    # Dead nodes can be skipped; they may be pruned later.
                    continue

        raise KeyError(item)

    def discard(self, item: _T) -> None:
        """
        Remove the first live occurrence of a value equal to `item`, if present.

        This behaves like `remove`, but does not raise if no such item exists.

        Args:
            item:
                The value to remove (if present).

        Returns:
            None.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()

            for node in list(self._set):
                try:
                    if node.deref(strict=True) == item:
                        try:
                            node.fire_callbacks()
                        finally:
                            node.cleanup()
                        self._set.discard(node)
                        return
                except DeadReferenceError:
                    continue

    def clear(self) -> None:
        """
        Remove all nodes from the set.

        All nodes:
          * Have their callbacks fired.
          * Are then cleaned and discarded.

        Returns:
            None.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            for node in self._set:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()
            self._set.clear()

    # -------------------------------------------------------------------------
    # Bulk operations & conversions
    # -------------------------------------------------------------------------
    def to_set(self) -> Set[_T]:
        """
        Return a **shallow snapshot** of all live values in the set.

        Returns:
            set[_T]: A new set containing all live underlying values.

        Raises:
            DeadReferenceError:
                If any node in the container is dead and has not yet been pruned.
        """
        self.check_cleaned()
        nodes = self._snapshot_nodes()
        return self._values_from_nodes(nodes)

    def to_list(self) -> list[_T]:
        """
        Materialize all live values into a standard Python list.

        This does not preserve weak-reference behavior; it returns strong
        references to the currently live values only.

        Returns:
            list[_T]:
                A new list containing all live values.

        Raises:
            DeadReferenceError:
                If any node in the set is dead and has not yet been pruned.
        """
        return list(self.to_set())

    # -------------------------------------------------------------------------
    # Introspection / dunder helpers
    # -------------------------------------------------------------------------
    def __contains__(self, item: Any) -> bool:
        """
        Check whether a live value equal to `item` exists in the set.

        Args:
            item:
                The value to test for membership.

        Returns:
            bool:
                True if any live node's value compares equal to `item`, False
                otherwise.

        Note:
            This is implemented as a linear scan over live values; we do not
            rely on hash lookups for correctness here.
        """
        self.check_cleaned()
        for node in self._snapshot_nodes():
            try:
                if node.deref(strict=True) == item:
                    return True
            except DeadReferenceError:
                continue
        return False

    def __len__(self) -> int:
        """
        Return the number of nodes currently stored.

        If `auto_prune` is enabled, dead nodes are removed before counting.

        Returns:
            int: The number of nodes (live + any remaining dead if not pruned).
        """
        self.check_cleaned()
        if self._freeze:
            # In frozen mode, we trust structure not to be mutated concurrently.
            nodes = self._set
            if nodes is None:
                return 0
            # We do **not** automatically prune here unless `auto_prune` is True
            # and we want deterministic shrink. To keep behavior consistent
            # with other containers, call into snapshot helper.
            if self._auto_prune:
                nodes = self._snapshot_nodes()
                return len(nodes)
            return len(nodes)

        with self._lock:
            if self._auto_prune:
                self._prune_dead_locked()
            return len(self._set)

    def __iter__(self) -> Iterator[_T]:
        """
        Iterate over all live values in the set.

        Returns:
            Iterator[_T]: An iterator over the live values.

        Raises:
            DeadReferenceError:
                If a dead node is encountered during iteration and has not
                been pruned yet.
        """
        self.check_cleaned()
        def _iter() -> Iterator[_T]:
            for node in self._snapshot_nodes():
                yield node.deref(strict=True)

        return _iter()

    # -------------------------------------------------------------------------
    # Set operations (union, intersection, etc.)
    # -------------------------------------------------------------------------
    def _materialize_other(self, other: Iterable[Any]) -> set[_T]:
        """
        Convert another iterable or weak set into a concrete set of values.

        Returns:
            set[_T]: Materialized comparison/update operand.
        """
        return set(other if not isinstance(other, WeakConcurrentSet) else other.to_set())

    def isdisjoint(self, other: Iterable[Any]) -> bool:
        """
        Return whether this set and `other` share no live values.

        Args:
            other:
                Iterable compared against this set's live values.

        Returns:
            bool: True when this set's LIVE values share nothing with `other`. Values
                already collected are not considered.
        """
        return self.to_set().isdisjoint(self._materialize_other(other))

    def issubset(self, other: Iterable[Any]) -> bool:
        """
        Return whether all live values in this set also appear in `other`.

        Args:
            other:
                Iterable this set's live values must be contained by.

        Returns:
            bool: True when every LIVE value here also appears in `other`.
        """
        return self.to_set().issubset(self._materialize_other(other))

    def issuperset(self, other: Iterable[Any]) -> bool:
        """
        Return whether all values in `other` appear among this set's live values.

        Args:
            other:
                Iterable whose values must all appear among the live values.

        Returns:
            bool: True when every value in `other` appears among this set's LIVE values.
        """
        return self.to_set().issuperset(self._materialize_other(other))

    def union(self, *others: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """
        Return a new weak set containing the union of this set and `others`.

        Returns:
            WeakConcurrentSet[_T]: A new weak set over the union. Membership is still
                weak, so the result does not keep any member alive.
        """
        result = self.to_set()
        for o in others:
            result |= self._materialize_other(o)
        return WeakConcurrentSet(result, auto_prune=self._auto_prune)

    def intersection(self, *others: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """
        Return a new weak set containing the live intersection with `others`.

        Contract:
            Snapshots this set's currently-live members via `to_set()`,
            intersects with each materialized `other`, and returns a NEW
            `WeakConcurrentSet`. Members are held WEAKLY, so the result never
            keeps a value alive; already-dead referents are excluded from the
            snapshot. This set is not mutated.

        Args:
            *others:
                Iterables to intersect against; each is materialized to its
                live values before intersecting.

        Returns:
            WeakConcurrentSet[_T]: A new weak set over the live intersection.
        """
        result = self.to_set()
        for o in others:
            result &= self._materialize_other(o)
        return WeakConcurrentSet(result, auto_prune=self._auto_prune)

    def difference(self, *others: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """
        Return a new weak set containing live values not present in `others`.

        Contract:
            Snapshots this set's currently-live members via `to_set()`, removes
            each materialized `other`, and returns a NEW `WeakConcurrentSet`.
            Members are held WEAKLY, so the result never keeps a value alive.
            This set is not mutated.

        Args:
            *others:
                Iterables whose live values are removed from the result.

        Returns:
            WeakConcurrentSet[_T]: A new weak set of live values absent from
                `others`.
        """
        result = self.to_set()
        for o in others:
            result -= self._materialize_other(o)
        return WeakConcurrentSet(result, auto_prune=self._auto_prune)

    def symmetric_difference(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """
        Return a new weak set containing values present in exactly one operand.

        Args:
            other:
                Iterable to compare against.

        Returns:
            WeakConcurrentSet[_T]: A new weak set of values present in exactly one
                operand.
        """
        result = self.to_set() ^ self._materialize_other(other)
        return WeakConcurrentSet(result, auto_prune=self._auto_prune)

    def update(self, *others: Iterable[Any]) -> None:
        """
        Mutate this set to include the union of its current live values and `others`.

        Args:
            others:
                Iterables whose values are added. Added values are held WEAKLY.

        Returns:
            None.
        """
        self._ensure_mutable()
        with self._lock:
            base = self._values_from_nodes(self._set)
            for o in others:
                base |= self._materialize_other(o)
            self._set.clear()
            for v in base:
                self._set.add(self._make_node(v))

    def intersection_update(self, *others: Iterable[Any]) -> None:
        """
        Mutate this set to keep only live values shared with `others`.

        Args:
            others:
                Iterables to intersect against; this set is mutated in place.

        Returns:
            None.
        """
        self._ensure_mutable()
        with self._lock:
            base = self._values_from_nodes(self._set)
            for o in others:
                base &= self._materialize_other(o)
            self._set.clear()
            for v in base:
                self._set.add(self._make_node(v))

    def difference_update(self, *others: Iterable[Any]) -> None:
        """
        Mutate this set to remove live values found in `others`.

        Args:
            others:
                Iterables whose values are removed from this set in place.

        Returns:
            None.
        """
        self._ensure_mutable()
        with self._lock:
            base = self._values_from_nodes(self._set)
            for o in others:
                base -= self._materialize_other(o)
            self._set.clear()
            for v in base:
                self._set.add(self._make_node(v))

    def symmetric_difference_update(self, other: Iterable[Any]) -> None:
        """
        Mutate this set to the symmetric difference of its live values and `other`.

        Args:
            other:
                Iterable to compare against; this set is mutated in place.

        Returns:
            None.
        """
        self._ensure_mutable()
        with self._lock:
            base = self._values_from_nodes(self._set)
            base ^= self._materialize_other(other)
            self._set.clear()
            for v in base:
                self._set.add(self._make_node(v))

    # PEP 584-style operators
    def __or__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Return `self.union(other)`."""
        return self.union(other)

    def __and__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Return `self.intersection(other)`."""
        return self.intersection(other)

    def __sub__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Return `self.difference(other)`."""
        return self.difference(other)

    def __xor__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Return `self.symmetric_difference(other)`."""
        return self.symmetric_difference(other)

    def __ior__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Apply `update(other)` in place and return this set."""
        self.update(other)
        return self

    def __iand__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Apply `intersection_update(other)` in place and return this set."""
        self.intersection_update(other)
        return self

    def __isub__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Apply `difference_update(other)` in place and return this set."""
        self.difference_update(other)
        return self

    def __ixor__(self, other: Iterable[Any]) -> "WeakConcurrentSet[_T]":
        """Apply `symmetric_difference_update(other)` in place and return this set."""
        self.symmetric_difference_update(other)
        return self

    def __bool__(self) -> bool:
        """
        Truthiness for the set.

        Returns:
            bool:
                False if both:
                  * The set is logically empty, or
                  * Only dead nodes remain (and auto_prune cleaned them).
                True otherwise.
        """
        return len(self) != 0

    def __repr__(self) -> str:
        """
        Return a debug representation of the WeakConcurrentSet.

        Dead entries are displayed as ``'<dead>'`` to avoid raising during
        repr generation.

        Contract:
            - Non-strict deref, so a dead entry renders as `<dead>` rather than
              raising. Debug/telemetry only.

        Returns:
            str: `WeakConcurrentSet([...])` over live values and `<dead>` marks.

        Raises:
            RuntimeError: If the set has been cleaned.
        """
        self.check_cleaned()
        values = []
        for node in self._snapshot_nodes():
            val = node.deref(strict=False)
            values.append(val if val is not None else "<dead>")
        return f"{self.__class__.__name__}({values!r})"

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison against another WeakConcurrentSet or plain set-like.

        Live values are compared; dead entries will raise unless already pruned.

        Contract:
            - Compares LIVE values via `to_set()`; only `WeakConcurrentSet`,
              `set`, and `frozenset` are comparable - anything else is False. A
              dead entry not yet pruned raises during materialization.

        Args:
            other:
                Object to compare against.

        Returns:
            bool: True when the live value sets are equal.
        """
        if isinstance(other, WeakConcurrentSet):
            return self.to_set() == other.to_set()
        if isinstance(other, (set, frozenset)):
            return self.to_set() == set(other)
        return False

    def __ne__(self, other: object) -> bool:
        """Return the negated result of :meth:`__eq__`."""
        return not self.__eq__(other)

    # -------------------------------------------------------------------------
    # Higher-order helpers (map / filter / reduce)
    # -------------------------------------------------------------------------
    def map(self, func: Callable[[_T], Any]) -> "WeakConcurrentSet[Any]":
        """
        Apply a function to each live value and return a new WeakConcurrentSet.

        Args:
            func:
                Callable of the form ``func(value) -> Any``.

        Returns:
            WeakConcurrentSet[Any]:
                A new weak set holding the mapped results as weak references.

        Raises:
            DeadReferenceError:
                If any node is dead during mapping and has not been pruned.
        """
        self.check_cleaned()
        values = {func(v) for v in self}
        return WeakConcurrentSet(initial=values)

    def filter(self, func: Callable[[_T], bool]) -> "WeakConcurrentSet[_T]":
        """
        Filter live values using a predicate and return a new WeakConcurrentSet.

        Args:
            func:
                Predicate callable of the form ``func(value) -> bool``.
                Values for which this returns True are retained.

        Returns:
            WeakConcurrentSet[_T]:
                A new weak set containing only values for which the predicate
                returned True.

        Raises:
            DeadReferenceError:
                If any node is dead during filtering and has not been pruned.
        """
        self.check_cleaned()
        values = {v for v in self if func(v)}
        return WeakConcurrentSet(initial=values)

    def reduce(
            self,
            func: Callable[[Any, _T], Any],
            initial: Optional[Any] = None,
    ) -> Any:
        """
        Reduce the live values in the set to a single result.

        Args:
            func:
                Callable of the form ``func(accumulator, value) -> Any``.
            initial:
                Optional initial accumulator value. If omitted, the reduction
                starts from the first element of the set.

        Returns:
            Any: The final accumulated value.

        Raises:
            TypeError:
                If the set is empty and `initial` is None.
            DeadReferenceError:
                If any node is dead during reduction and has not been pruned.
        """
        self.check_cleaned()
        # Materialize into a list for ordered reduction (order of a set is still
        # arbitrary, but stable for this call).
        items = list(self)

        if not items and initial is None:
            raise TypeError("reduce() of empty WeakConcurrentSet with no initial value")

        from functools import reduce as _reduce

        if initial is None:
            return _reduce(func, items)
        return _reduce(func, items, initial)

    # -------------------------------------------------------------------------
    # Set API extensions
    # -------------------------------------------------------------------------
    def pop(self) -> _T:
        """
        Remove and return an arbitrary live element. Mirrors `set.pop`.

        Raises:
            KeyError: If the set is empty.
            TypeError: If the set is frozen.
            DeadReferenceError: If a dead node is encountered before pruning.

        Returns:
            _T: An arbitrary live element, removed from the set.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            if not self._set:
                raise KeyError("pop from an empty WeakConcurrentSet")
            node = next(iter(self._set))
            self._set.remove(node)
            val = node.deref(strict=True)
            try:
                node.fire_callbacks()
            finally:
                node.cleanup()
            return val

    def batch_update(self, func: Callable[[Set[_T]], None]) -> None:
        """
        Perform a batch mutation under a single lock acquisition.

        Args:
            func:
                A callable that receives a **strongly-referenced** `set` of
                values, representing the current live contents. It may mutate
                this set arbitrarily.

                Signature:
                    ``func(values: set[_T]) -> None``

                After `func` returns, this WeakConcurrentSet:
                  * Drops all existing nodes.
                  * Rebuilds internal nodes from the mutated value set.

        Raises:
            TypeError:
                If the set is frozen.
            DeadReferenceError:
                If a dead node is encountered while materializing current
                values before the batch update.

        Returns:
            None.
        """
        self.check_cleaned()
        self._ensure_mutable()
        with self._lock:
            # Materialize current live values (may raise DeadReferenceError).
            current_values = self._values_from_nodes(self._set)
            # Let caller mutate this strong set snapshot.
            func(current_values)

            # Tear down old nodes.
            for node in self._set:
                try:
                    node.fire_callbacks()
                finally:
                    node.cleanup()

            # Rebuild from mutated values.
            self._set.clear()
            for v in current_values:
                self._set.add(self._make_node(v))

    # -------------------------------------------------------------------------
    # Copying
    # -------------------------------------------------------------------------
    def __copy__(self) -> "WeakConcurrentSet[_T]":
        """
        Return a shallow copy of this WeakConcurrentSet.

        Returns:
            WeakConcurrentSet[_T]:
                A new WeakConcurrentSet containing the same live values,
                each wrapped in a new WeakRefNode.
        """
        values = self.to_set()
        return WeakConcurrentSet(
            initial=values,
            auto_prune=self._auto_prune,
        )

    def __deepcopy__(self, memo: dict) -> "WeakConcurrentSet[_T]":
        """
        Return a deep copy of this WeakConcurrentSet.

        Args:
            memo:
                Memoization dictionary used by :mod:`copy` to avoid duplicating
                shared objects and handle cycles.

        Returns:
            WeakConcurrentSet[_T]:
                A new WeakConcurrentSet containing deep-copied values.
        """
        values = deepcopy(self.to_set(), memo)
        return WeakConcurrentSet(
            initial=values,
            auto_prune=self._auto_prune,
        )

    # -------------------------------------------------------------------------
    # Context managers
    # -------------------------------------------------------------------------
    def __enter__(self) -> "WeakConcurrentSet[_T]":
        """
        Enter the runtime context for this set.

        This acquires the internal lock and returns the set itself, allowing:

            with weak_set:
                # direct, locked usage

        **Warning**:
            Within the context, you are responsible for avoiding long/blocking
            operations while holding the lock.

        Returns:
            WeakConcurrentSet[_T]: This instance.

        Raises:
            RuntimeError:
                If the set has already been cleaned.
        """
        self.check_cleaned()
        self._lock.acquire()
        return self

    def __exit__(
            self,
            exc_type: Optional[type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the runtime context for this set.

        This releases the internal lock acquired in `__enter__`.

        Contract:
            - Always releases the lock; a spurious release `RuntimeError` is
              swallowed. Never suppresses exceptions from the with-body.

        Args:
            exc_type:
                Exception type, if any.
            exc_val:
                Exception instance, if any.
            exc_tb:
                Traceback object, if any.

        Returns:
            None.
        """
        try:
            self._lock.release()
        except RuntimeError:
            # In case it's already released or cleaned.
            pass
