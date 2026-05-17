import weakref
import threading
from typing import Generic, TypeVar, Optional, Callable, Union, Any, Iterator
from contextlib import contextmanager
import ulid

# Command Ops imports
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.general_base.isync import ISync

T = TypeVar("T")
R = TypeVar("R")

_OnCollect = Callable[["SyncWeakRef[T]"], None]


class SyncWeakRef(Cleanable, ISync, Generic[T]):
    """
    SyncWeakRef(target)
    ===================

    A thread-safe, non-owning weak reference wrapper with
    phantom-style notification and optional auto-cleanup.

    Core behavior:
    --------------
    - Non-owning:
        * Uses `weakref.ref(target)` internally.
        * Does NOT keep the target alive.
    - Thread-safe wrapper:
        * Synchronizes access to the weak reference itself.
        * Does NOT make the target object thread-safe.
    - Lifetime inspection:
        * `is_alive()`   -> bool
        * `try_get()`    -> Optional[T]
        * `get()`        -> T or raises ReferenceError
    - Update operations:
        * `set(obj)`     -> replace the target reference
        * `cas(expected, new)` -> compare-and-swap by identity
        * `swap(new)`    -> swap and return previous target (if alive)

    Phantom-style features:
    -----------------------
    - Optional GC callback:
        * `on_collect`: Callable[[SyncWeakRef[T]], None]
        * Invoked when the target is about to be finalized.
        * Called exactly once per referent lifetime.
    - Phantom flag:
        * `has_fired` property indicates whether the GC callback fired.
    - Optional auto-cleanup:
        * `auto_cleanup=True`:
            - When the referent is collected, `cleanup()` is invoked
              on this SyncWeakRef instance.
            - After that, any use of the wrapper raises RuntimeError.

    Cleanable contract:
    -------------------
    - `cleanup()`:
        * Clears the weak reference and callback.
        * Marks the wrapper as cleaned.
        * Best-effort cleans the internal lock if it supports cleanup().
        * Idempotent and safe under concurrent calls.

    IMPORTANT:
    ----------
    SyncWeakRef does NOT provide thread safety for the target object.
    The target MUST be internally thread-safe if accessed concurrently.
    This class only synchronizes the weak-reference wrapper and its
    phantom/cleanup behavior.
    """

    __slots__ = (
            Cleanable.__slots__
            + [
                "_weak",
                "_lock",
                "_id",
                "_on_collect",
                "_auto_cleanup",
                "_phantom_fired",
            ]
    )
    __melder_internal__ = _mrg.sentinel

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(
            self,
            target: T,
            on_collect: Optional[_OnCollect] = None,
            auto_cleanup: bool = False,
    ):
        """
        Initialize a SyncWeakRef.

        Parameters:
        -----------
        target:
            The object to weakly reference. Must be weak-referenceable.
        on_collect:
            Optional callback invoked when the referent is about to be
            finalized. Signature: (ref: SyncWeakRef[T]) -> None.
        auto_cleanup:
            If True, `cleanup()` is automatically invoked when the
            referent is collected. This effectively prunes the wrapper
            once the target dies.
        """
        super().__init__()
        self._id = str(ulid.ULID())
        self._on_collect: Optional[_OnCollect] = on_collect
        self._auto_cleanup: bool = auto_cleanup
        self._phantom_fired: bool = False

        # Create weak reference immediately (no ownership) and register
        # an internal callback for phantom-style notification.
        self._weak: weakref.ref[T] = weakref.ref(target, self._weakref_callback)
        self._lock: threading.RLock = threading.RLock()

    # ------------------------------------------------------------------
    # Weakref callback (phantom signal)
    # ------------------------------------------------------------------
    def _weakref_callback(self, _wr: weakref.ref[T]) -> None:
        """
        Internal weakref callback.

        This is invoked by Python's GC machinery when the referent is
        about to be finalized. It:
        - Marks phantom state (`_phantom_fired = True`).
        - Invokes the user callback, if any.
        - Optionally triggers auto-cleanup.

        NOTE:
        -----
        - This callback must be best-effort and low-risk.
        - It does NOT acquire the object's main lock to avoid deadlocks.
        - It tolerates the wrapper already being cleaned.
        """
        # If already cleaned, nothing to do.
        if self._cleaned:
            return

        # Mark phantom-firing state.
        self._phantom_fired = True

        # Snapshot callback and auto-cleanup flag to minimize race windows.
        cb = self._on_collect
        auto = self._auto_cleanup

        # Invoke user callback (if any).
        if cb is not None:
            try:
                cb(self)
            except Exception:
                # Swallow exceptions to avoid interfering with GC.
                pass

        # Optionally clean up the wrapper itself.
        if auto:
            try:
                self.cleanup()
            except Exception:
                # Best-effort: ignore failures from cleanup in this path.
                pass

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def cleanup(self) -> None:
        """
        Clean up this wrapper (NOT the target).

        After cleanup:
        - Wrapper is marked cleaned.
        - Underlying weak reference and callback are removed.
        - All operations raise RuntimeError via check_cleaned().
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True

            # Drop weakref and callback.
            del self._weak
            del self._on_collect

        del self._lock

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @classmethod
    def _coerce(cls, val):
        """
        Return the normalized scalar form expected by this wrapper type.

        Contract:
        - Base `SyncWeakRef` performs no coercion and returns the value
          unchanged.
        - Subclasses may override this when they need stricter normalization.
        """
        return val

    def _unwrap_other(self, other):
        """
        Normalize `other` for comparison against this wrapper's referent.

        Contract:
        - If `other` is another sync wrapper, returns its current value through
          `get()`.
        - Otherwise returns the raw value unchanged.
        """
        return other.get() if ISync._is_sync(other) else other

    def check_cleaned(self):
        """
        Raise when the wrapper has already been cleaned.

        Contract:
        - Overrides the base guard to provide a `SyncWeakRef`-specific error
          message.
        """
        if self._cleaned:
            raise RuntimeError("SyncWeakRef has been cleaned and cannot be used.")

    # ------------------------------------------------------------------
    # Phantom / callback API
    # ------------------------------------------------------------------
    @property
    def has_fired(self) -> bool:
        """
        Returns True if the GC/phantom callback has fired
        (i.e., the referent has been collected).
        """
        return self._phantom_fired

    def register_on_collect(self, callback: Optional[_OnCollect]) -> None:
        """
        Register or replace the on-collect callback.

        Parameters:
        -----------
        callback:
            A callable of the form (ref: SyncWeakRef[T]) -> None, or None
            to clear an existing callback.

        Raises:
        -------
        RuntimeError:
            If this SyncWeakRef has already been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            self._on_collect = callback

    def enable_auto_cleanup(self) -> None:
        """
        Enable auto-cleanup behavior.

        When the referent is collected, this SyncWeakRef will call
        `cleanup()` automatically (in the weakref callback).
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            self._auto_cleanup = True

    def disable_auto_cleanup(self) -> None:
        """
        Disable wrapper auto-cleanup when the referent is collected.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            self._auto_cleanup = False

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    def is_alive(self) -> bool:
        """
        Return whether the current weak-reference target is still alive.

        Returns:
            bool: True when the referent can still be resolved.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            if self._weak is None:
                return False
            return self._weak() is not None

    def try_get(self) -> Optional[T]:
        """
        Return the referenced object when it is still alive.

        Returns:
            Optional[T]: Live referent when available; otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            if self._weak is None:
                return None
            return self._weak()

    def get(self) -> T:
        """
        Get the referenced object.

        Raises:
            ReferenceError: if the weakref is dead.
            RuntimeError:   if this SyncWeakRef has been cleaned.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()

            if self._weak is None:
                raise ReferenceError("Weak reference has been cleared.")

            obj = self._weak()
            if obj is None:
                raise ReferenceError("Referenced object is no longer alive.")
            return obj

    snapshot = property(get)

    # ------------------------------------------------------------------
    # CAS / swap
    # ------------------------------------------------------------------
    def set(self, obj: T) -> None:
        """
        Forcefully update the weak reference target.

        This replaces the underlying weakref with a new one pointing
        at the given object.

        Args:
            obj: New referent to track weakly.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            self._weak = weakref.ref(obj, self._weakref_callback)

    def cas(self, expected: T, new: T) -> bool:
        """
        Compare-and-set on the referenced live object identity.

        Semantics:
        ----------
        - Loads the current target via `try_get()`.
        - If it is exactly `expected` (by identity), replaces the weak
          reference with a new one pointing at `new`.
        - Returns True on success, False otherwise.

        Returns:
            bool: True when the expected live referent matched and the swap was
            applied; otherwise False.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            current = self.try_get()
            if current is expected:
                self._weak = weakref.ref(new, self._weakref_callback)
                return True
            return False

    def swap(self, new: T) -> Optional[T]:
        """
        Replace the target and return the previous live value (if any).

        Returns:
        --------
        Optional[T]:
            The previously referenced object if it was still alive,
            otherwise None.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            old = self.try_get()
            self._weak = weakref.ref(new, self._weakref_callback)
            return old

    # ------------------------------------------------------------------
    # Transform (read-only)
    # ------------------------------------------------------------------
    def transform(self, fn: Callable[[T], R]) -> R:
        """
        Apply a read-only transform to the referenced object.

        Raises:
            ReferenceError: if object is dead.
            RuntimeError:   if this SyncWeakRef has been cleaned.

        Returns:
            R: Result returned by `fn(obj)` for the live referent.
        """
        obj = self.get()
        return fn(obj)

    map = transform

    # ------------------------------------------------------------------
    # locked() context
    # ------------------------------------------------------------------
    @contextmanager
    def locked(self) -> Iterator[T]:
        """
        Lock the wrapper, then yield the referenced object (if alive).

        Example:
        --------
        >>> with ref.locked() as obj:
        ...     obj.do_something()

        Yields:
            T: Live referent while the wrapper lock is held.
        """
        self.check_cleaned()
        with self._lock:
            self.check_cleaned()
            obj = self.get()
            yield obj

    # ------------------------------------------------------------------
    # Dunder & repr
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        """Return a debug-oriented representation of wrapper liveness state."""
        if self._cleaned:
            return "SyncWeakRef(cleaned)"

        alive = self.try_get() is not None
        state = "alive" if alive else "dead"
        phantom = ", phantom_fired=True" if self._phantom_fired else ""
        return f"SyncWeakRef({state} id={self._id}{phantom})"

    def __eq__(self, other: Any) -> bool:
        """
        Equality comparison is based on the underlying referent (if alive).

        - If `other` is ISync-compatible, compare `self.try_get()` to `other.try_get()`.
        - Otherwise, compare `self.try_get()` directly to `other`.

        Returns:
            bool: Equality result derived from the currently resolved referent.
        """
        if ISync._is_sync(other):
            return self.try_get() == other.try_get()  # type: ignore[attr-defined]
        return self.try_get() == other

    def __hash__(self) -> int:
        """
        Hash the contained object if possible; fall back to id(self) or id(obj).

        If the referent is dead:
            - Returns id(self) to keep the wrapper usable in sets/dicts.
        If the referent is alive but unhashable:
            - Falls back to id(obj).

        Returns:
            int: Hash of the live referent when possible, otherwise an id-based
            fallback.
        """
        obj = self.try_get()
        if obj is None:
            return id(self)
        try:
            return hash(obj)
        except TypeError:
            return id(obj)
