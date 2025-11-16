from __future__ import annotations

import ulid
import weakref
from typing import Generic, TypeVar, Optional, Callable, List, Any

# CommandOps Imports
from command_ops.utilities.exceptions.dead_reference_error import DeadReferenceError
from command_ops.utilities.interfaces.cleanable import Cleanable

_T = TypeVar("_T")
_OnCollect = Callable[["WeakRefNode[_T]"], None]


class WeakRefNode(Cleanable, Generic[_T]):
    """
    WeakRefNode
    ===========

    A reusable weak-reference node for weak data structures, with
    phantom-style Garbage Collection (GC) notification.

    This node wraps a single object, allowing it to be garbage collected while still
    notifying the container about its death.

    **Responsibilities:**
    * **Reference:** Holds a weak reference to a target object.
    * **Liveness Tracking:** Tracks when the target is collected (`dead` / `is_alive()`).
    * **Access:** Provides safe accessors like `try_get()` and `get()`.
    * **Mutation:** Supports updating the reference target (`set()`, `swap()`, `cas()`).
    * **Callbacks:** Fires a single `on_collect` callback (for the parent container) and additional callbacks when the referent is GC'd.

    **Concurrency & GC Notes:**
    * **No Internal Lock:** External synchronization is the responsibility of the owning container (e.g., `WeakConcurrentList`).
    * **GC Path:** The weakref callback runs on the GC path. Callbacks should be small, best-effort, and should only grab locks if the risks are understood and accepted by the container's design.

    **Cleanable Contract:**
    * **`cleanup()`:** Clears the weakref and all callbacks, marking the node as dead and cleaned. This operation is idempotent.
    """

    __slots__ = (
            Cleanable.__slots__
            + [
                "_ref",
                "_id",
                "_dead",
                "_on_collect",
                "_callbacks",
                "_phantom_fired",
            ]
    )

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(
            self,
            target: _T,
            on_collect: Optional[_OnCollect] = None,
    ) -> None:
        """
        Initialize a WeakRefNode.

        Args:
            target (_T):
                The object to weakly reference. Must be weak-referenceable.
            on_collect (Optional[_OnCollect], optional):
                Optional parent/container callback invoked when the referent is collected.
                Defaults to None. This is fired from the GC weakref callback.

        Raises:
            TypeError: If the `target` object does not support weak references.
        """
        super().__init__()
        self._id: str = str(ulid.ULID())
        self._dead: bool = False
        self._on_collect: Optional[_OnCollect] = on_collect
        self._callbacks: List[_OnCollect] = []
        self._phantom_fired: bool = False

        try:
            # Attach our GC callback
            self._ref: Optional[weakref.ref[_T]] = weakref.ref(
                target, self._weakref_callback
            )
        except TypeError as e:
            raise TypeError(
                f"WeakRefNode can only wrap objects that support weak references; "
                f"got {type(target).__name__!r}"
            ) from e

    # ------------------------------------------------------------------
    # Weakref callback (phantom signal)
    # ------------------------------------------------------------------
    def _weakref_callback(self, _wr: weakref.ref[_T]) -> None:
        """
        Internal weakref callback invoked by Python's GC when the referent is about to be finalized.

        This method:
        * Marks `_dead = True` and `_phantom_fired = True`.
        * Invokes all registered callbacks (`on_collect` and extra callbacks).

        NOTE: This runs on the GC cleanup path. Callbacks must be best-effort and should swallow exceptions.
        """
        if self._cleaned:
            return

        self._dead = True
        self._phantom_fired = True

        # Snapshot and clear callbacks before invoking
        parent_cb = self._on_collect
        extra_cbs = list(self._callbacks)
        self._on_collect = None
        self._callbacks.clear()

        # Parent/container callback
        if parent_cb is not None:
            try:
                parent_cb(self)
            except Exception:
                pass

        # Extra per-node callbacks
        for cb in extra_cbs:
            try:
                cb(self)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Core lifecycle
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Deterministically tears down this node, clearing all references and resources.

        This method is idempotent.
        """
        if self._cleaned:
            return

        self._cleaned = True
        self._ref = None
        self._on_collect = None
        self._callbacks.clear()
        self._dead = True

    @property
    def id(self) -> str:
        """
        Returns the unique identifier for this node, useful for debugging or telemetry.

        Returns:
            str: The ULID identifier.
        """
        return self._id

    # ------------------------------------------------------------------
    # Liveness & access (SyncWeakRef-style)
    # ------------------------------------------------------------------
    @property
    def dead(self) -> bool:
        """
        Returns True if the underlying object has been collected, the weakref is cleared, or the node has been explicitly cleaned.

        Returns:
            bool: True if the referent is dead, False otherwise.
        """
        if self._dead:
            return True
        if self._ref is None:
            self._dead = True
            return True
        if self._ref() is None:
            self._dead = True
            return True
        return False

    @property
    def has_fired(self) -> bool:
        """
        Returns True if the GC/phantom callback has fired at least once (i.e., the referent was collected).

        Returns:
            bool: True if the GC callback fired.
        """
        return self._phantom_fired

    def is_alive(self) -> bool:
        """
        Returns True if the underlying object is still alive.

        Returns:
            bool: True if the referent exists.
        """
        return not self.dead

    def try_get(self) -> Optional[_T]:
        """
        Returns the underlying object if it is still alive, otherwise returns None.

        Returns:
            Optional[_T]: The live object, or None.
        """
        if self._ref is None or self.dead:
            return None
        return self._ref()

    def get(self) -> _T:
        """
        Returns the underlying object.

        Returns:
            _T: The live object.

        Raises:
            DeadReferenceError: If the target has already been collected.
        """
        if self._ref is None or self.dead:
            raise DeadReferenceError("WeakRefNode target has already been collected.")

        obj = self._ref()
        if obj is None:
            self._dead = True
            raise DeadReferenceError("WeakRefNode target has already been collected.")
        return obj

    # Alias for SyncWeakRef API
    snapshot = property(get)

    # ------------------------------------------------------------------
    # Mutating the reference (container must serialize externally)
    # ------------------------------------------------------------------
    def set(self, obj: _T) -> None:
        """
        Forcefully updates the weak reference target, replacing the underlying weakref with a new one pointing at `obj`.

        The same GC callback remains attached.

        Args:
            obj (_T): The new object to weakly reference.

        Raises:
            RuntimeError: If attempting to set the target on a cleaned node.
            TypeError: If the new object does not support weak references.
        """
        if self._cleaned:
            raise RuntimeError("Cannot set target on a cleaned WeakRefNode.")

        try:
            self._ref = weakref.ref(obj, self._weakref_callback)
        except TypeError as e:
            raise TypeError(
                f"WeakRefNode can only wrap objects that support weak references; "
                f"got {type(obj).__name__!r}"
            ) from e
        self._dead = False
        self._phantom_fired = False

    def swap(self, new: _T) -> Optional[_T]:
        """
        Replaces the target and returns the previous live value (if any).

        Args:
            new (_T): The new object to weakly reference.

        Returns:
            Optional[_T]: The previous live object, or None if it was dead.
        """
        old = self.try_get()
        self.set(new)
        return old

    def cas(self, expected: _T, new: _T) -> bool:
        """
        Compare-and-set operation on the underlying live object identity.

        If the current live object is the `expected` object (by identity `is`), it is replaced with `new`.

        Args:
            expected (_T): The expected object identity.
            new (_T): The new object to set if the comparison succeeds.

        Returns:
            bool: True if the object was replaced, False otherwise.

        Raises:
            RuntimeError: If attempting to perform `cas()` on a cleaned node.
        """
        if self._cleaned:
            raise RuntimeError("Cannot perform cas() on a cleaned WeakRefNode.")

        current = self.try_get()
        if current is expected and current is not None:
            self.set(new)
            return True
        return False

    # ------------------------------------------------------------------
    # Functional helpers
    # ------------------------------------------------------------------
    def transform(self, fn: Callable[[_T], Any]) -> Any:
        """
        Applies a read-only transform to the referenced live object.

        Args:
            fn (Callable[[_T], Any]): The function to apply to the live object.

        Returns:
            Any: The result of the function call.

        Raises:
            DeadReferenceError: If the object is dead.
        """
        obj = self.get()
        return fn(obj)

    map = transform

    def deref(self, *, strict: bool = True) -> Optional[_T]:
        """
        Convenience helper to retrieve the target, acting as a wrapper around `try_get()`/`get()`.

        Args:
            strict (bool):
                - If True (default), raises `DeadReferenceError` if the object is gone.
                - If False, returns None if the object is gone.

        Returns:
            Optional[_T]: The target object, or None if not found and `strict=False`.

        Raises:
            DeadReferenceError: If `strict=True` and the object is dead.
        """
        if strict:
            return self.get()
        return self.try_get()

    # ------------------------------------------------------------------
    # Callback management
    # ------------------------------------------------------------------
    def add_callback(self, cb: _OnCollect) -> None:
        """
        Registers an additional callback to be invoked when the referent is collected (GC path) or when `fire_callbacks()` is called.

        Args:
            cb (_OnCollect): The callback function.

        Raises:
            RuntimeError: If attempting to add a callback to a cleaned node.
        """
        if self._cleaned:
            raise RuntimeError("Cannot add callback to a cleaned WeakRefNode.")
        if cb is not None:
            self._callbacks.append(cb)

    def fire_callbacks(self) -> None:
        """
        Manually invokes all registered callbacks (`on_collect` and extra callbacks) once, then clears them.

        This allows a container to force firing callbacks in a controlled context instead of waiting for GC.
        """
        if not self._callbacks and self._on_collect is None:
            return

        parent_cb = self._on_collect
        extra_cbs = list(self._callbacks)

        # Clear them so they can only fire once in the explicit path
        self._on_collect = None
        self._callbacks.clear()

        # Parent callback
        if parent_cb is not None:
            try:
                parent_cb(self)
            except Exception:
                pass

        # Extra per-node callbacks
        for cb in extra_cbs:
            try:
                cb(self)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Dunder & identity
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Returns the official string representation of the WeakRefNode.

        Returns:
            str: The representation showing ID, liveness state, and phantom status.
        """
        state = "dead" if self.dead else "alive"
        phantom = ", phantom_fired=True" if self._phantom_fired else ""
        return f"WeakRefNode(id={self._id!r}, state={state}{phantom})"

    def __eq__(self, other: Any) -> bool:
        """
        Equality comparison (``==``) based on **node identity**, not referent value.

        Two WeakRefNode instances are considered equal if and only if they
        represent the same logical node (i.e., they share the same ULID-based
        identifier). The liveness or identity of the underlying referent is
        not taken into account for equality.

        This design keeps the equality contract consistent with ``__hash__``,
        which is also derived solely from the node's ID.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if ``other`` is a WeakRefNode with the same internal ID,
                  False otherwise.
        """
        if isinstance(other, WeakRefNode):
            return self._id == other._id
        return False

    def __hash__(self) -> int:
        """
        Return a stable, node-identity-based hash.

        The hash is derived solely from this node's ULID identifier and does
        not depend on the underlying referent's liveness or value. This means:

        * The hash never changes over the lifetime of the node.
        * The hash remains valid even after the referent is garbage-collected.
        * The ``__eq__`` / ``__hash__`` contract is honored because equality
          also uses the node ID.

        Returns:
            int: The hash value for this node.
        """
        return hash(self._id)
