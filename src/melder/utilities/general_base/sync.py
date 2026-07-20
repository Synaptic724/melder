import threading
from typing import Any, Callable, ClassVar, Dict, Tuple



class Sync:
    """

    Purpose:
        Abstract helper mix-in for thread-safe sync-value wrappers. Provides the
        shared coordination helpers used by concrete sync wrappers without
        defining the storage type itself.

    Responsibilities:
        - Publish the fast `_is_sync_value` marker that runtime helpers check.
        - Normalize peer wrappers or raw values into the concrete subclass's
          scalar type.
        - Acquire two wrapper locks in deterministic order for binary operations.
        - Survive pickling without losing wrapper identity.

    Contract:
    - `_is_sync_value` is the fast marker used by runtime helpers.
    - `_unwrap_other()` converts peer sync wrappers or raw values into the scalar
      type owned by the current concrete subclass.
    - `_perform_binary_op()` acquires two sync-wrapper locks in deterministic order
      to reduce deadlock risk.
    - Concrete subclasses must provide `_value`, `_lock`, `get()`, and a
      `_coerce(...)` classmethod appropriate for their scalar type.

    Owned State:
        None. This mix-in deliberately owns no storage; `_value` and `_lock` are
        the concrete subclass's to declare.

    Threading:
        This class exists BECAUSE of threading. `_perform_binary_op()` is the
        deadlock-avoidance surface: two wrappers touched in one operation are
        locked in a deterministic order, so two threads operating on the same
        pair from opposite directions cannot deadlock. On free-threaded builds
        that ordering is the difference between correct and hung, not a
        micro-optimization.

    Lifecycle / Cleanup:
        No cleanup contract. `Sync` is a behavioral mix-in, not a resource owner,
        and deliberately does NOT inherit `Cleanable`. Concrete subclasses that
        own resources compose cleanup themselves.

    Registration:
        BASE CLASS - DELIBERATELY UNGUARDED. Do NOT add `__melder_internal__`
        to this class. The guard resolves the sentinel through `getattr`, which
        walks the MRO, so tagging this mix-in would tag every sync wrapper
        descended from it, including any a user writes. Concrete Melder-owned
        wrappers such as `SyncWeakRef` carry the sentinel individually.

    Subsystem Context:
        One of three `utilities/general_base/` base classes, alongside
        `Cleanable` (teardown contract) and `AbstractElasticPool` (pooling). The
        narrowest of the three: no state, no lifecycle, just the coordination
        protocol shared by sync wrappers. Its concrete in-tree descendant is
        `SyncWeakRef` under `utilities/synchronization/`.

    System Context:
        Beneath the DGR entirely and outside the boot order. Nothing in binding
        or resolution constructs a `Sync`; it exists so that shared scalar state
        touched from multiple threads has one correct locking discipline instead
        of each call site inventing its own.
    """

    _ast_helper_access: str = "public"
    __agent_purpose__: str = (
        "access: public. Base mix-in for thread-safe value wrappers. Subclass "
        "this when you need a shared scalar touched from multiple threads; "
        "supply _value, _lock, get(), and _coerce(). Deliberately not "
        "registration-guarded so user subclasses stay bindable."
    )

    __slots__ = ()
    _is_sync_value: ClassVar[bool] = True
    _value: Any
    _lock: threading.RLock

    # ----------  helpers shared by ALL Sync* types  -----------------
    @classmethod
    def _coerce(cls, val: Any) -> Any:
        """
        Normalize one scalar value for this concrete sync wrapper type.

        Contract:
        - Concrete sync wrappers override this to coerce peer values into the
          scalar form they store internally.
        - The base mix-in does not choose a scalar policy on its own.
        """
        raise NotImplementedError("Sync subclasses must implement _coerce().")

    def get(self) -> Any:
        """
        Return the current wrapped scalar value.

        Contract:
        - Concrete sync wrappers expose their stored scalar through this
          method.
        - The shared mix-in uses this for pickling and peer-value unwrapping.

        Returns:
            Any: The current value, read under the instance lock.
        """
        raise NotImplementedError("Sync subclasses must implement get().")

    @staticmethod
    def _is_sync(obj: object) -> bool:
        """
    Return whether `obj` is any `Sync` subclass instance.

        Contract:
        - Uses the shared `Sync` marker type instead of concrete subclass
          checks.
        - Exists so binary-operation helpers can stay generic across sync
          wrapper implementations.
        """
        return isinstance(obj, Sync)

    # NOTE: self._coerce(val) is defined in each concrete subclass
    def _unwrap_other(self, other: Any) -> Any:
        """
        Convert `other` into the scalar type expected by this sync wrapper.

        Contract:
        - If `other` is another `Sync` wrapper, its exposed value is coerced
          through this concrete wrapper's `_coerce(...)`.
        - If `other` is a raw value, coercion is attempted directly.
        - If coercion fails, the original value is returned so the caller's
          operation can raise the real incompatibility error.

        """
        if self._is_sync(other):          # another Sync value
            return self._coerce(other.get())
        try:                              # raw numeric / str
            return self._coerce(other)
        except Exception:
            return other                  # let caller raise if truly incompatible

    def _perform_binary_op(
            self,
            other: Any,
            op: Callable[[Any, Any], Any],
            r_operation: bool = False,
    ) -> Any:
        """
        Execute one binary operation with deterministic lock ordering.

        Contract:
        - Uses `_acquire_two(...)` when both operands are sync wrappers.
        - Preserves reflected-operation ordering when `r_operation=True`.
        - Falls back to `_unwrap_other(...)` for raw-value operands.
        - Returns the raw `op(...)` result; it does not wrap the result back
          into a sync type on its own.
        """
        if Sync._is_sync(other):
            first, second = Sync._acquire_two(self, other)
            with first._lock, second._lock:
                # figure out which side is left/right
                a = self._value if not r_operation else other._value
                b = other._value if not r_operation else self._value
                return op(a, b)
        else:
            other_val = self._unwrap_other(other)
            with self._lock:
                return op(other_val, self._value) if r_operation else op(self._value, other_val)

    @staticmethod
    def _acquire_two(a: "Sync", b: "Sync") -> Tuple["Sync", "Sync"]:
        """
        Return the two sync objects in deterministic lock order.

        Contract:
        - Orders by object id so both sides agree on the same acquisition order.
        - Used to reduce deadlock risk in dual-sync binary operations.
        """
        return ((a, b) if id(a) <= id(b) else (b, a))

    # ------------------------------------------------------------------ #
    #  Pickle support – exclude the RLock and rebuild it on load
    # ------------------------------------------------------------------ #
    def __getstate__(self) -> Dict[str, Any]:
        """
        Return the instance state for pickling.

        Contract:
        - Serializes only the wrapped scalar value.
        - Never serializes the runtime lock object.
        """
        return {"_value": self.get()}        # plain float, fully picklable

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Reinitialize the sync wrapper after unpickling.

        Contract:
        - Rebuilds `_value` through the concrete class `_coerce(...)`.
        - Creates a fresh `threading.RLock` for the unpickled instance.
        """
        # Route state restoration through subclass-defined slots instead of
        # claiming the base mix-in owns concrete storage fields.
        setattr(self, "_value", type(self)._coerce(state["_value"]))
        setattr(self, "_lock", threading.RLock())


# Backward compatibility alias.
ISync = Sync
