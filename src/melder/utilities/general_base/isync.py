import threading
from typing import Any, ClassVar

class ISync:
    """
    Abstract helper mix-in for thread-safe sync-value wrappers.

    `ISync` provides the shared coordination helpers used by the concrete sync
    wrappers. It does not define the storage type itself; instead it standardizes
    how sync values identify themselves, unwrap peer operands, coordinate dual-lock
    binary operations, and survive pickling.

    Contract:
    - `_is_sync_value` is the fast marker used by runtime helpers.
    - `_unwrap_other()` converts peer sync wrappers or raw values into the scalar
      type owned by the current concrete subclass.
    - `_perform_binary_op()` acquires two sync-wrapper locks in deterministic order
      to reduce deadlock risk.
    - Concrete subclasses must provide `_value`, `_lock`, `get()`, and a
      `_coerce(...)` classmethod appropriate for their scalar type.

    """

    __slots__: ClassVar[tuple] = ()
    _is_sync_value: ClassVar[bool] = True

    # ----------  helpers shared by ALL Sync* types  -----------------
    @staticmethod
    def _is_sync(obj) -> bool:
        """
        Return whether `obj` is any `ISync` subclass instance.

        Contract:
        - Uses the shared `ISync` marker type instead of concrete subclass
          checks.
        - Exists so binary-operation helpers can stay generic across sync
          wrapper implementations.
        """
        return isinstance(obj, ISync)

    # NOTE: self._coerce(val) is defined in each concrete subclass
    def _unwrap_other(self, other):
        """
        Convert `other` into the scalar type expected by this sync wrapper.

        Contract:
        - If `other` is another `ISync` wrapper, its exposed value is coerced
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

    def _perform_binary_op(self, other, op, r_operation=False):
        """
        Execute one binary operation with deterministic lock ordering.

        Contract:
        - Uses `_acquire_two(...)` when both operands are sync wrappers.
        - Preserves reflected-operation ordering when `r_operation=True`.
        - Falls back to `_unwrap_other(...)` for raw-value operands.
        - Returns the raw `op(...)` result; it does not wrap the result back
          into a sync type on its own.
        """
        if ISync._is_sync(other):
            first, second = ISync._acquire_two(self, other)
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
    def _acquire_two(a: "ISync", b: "ISync"):
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
    def __getstate__(self):
        """
        Return the instance state for pickling.

        Contract:
        - Serializes only the wrapped scalar value.
        - Never serializes the runtime lock object.
        """
        return {"_value": self.get()}        # plain float, fully picklable

    def __setstate__(self, state):
        """
        Reinitialize the sync wrapper after unpickling.

        Contract:
        - Rebuilds `_value` through the concrete class `_coerce(...)`.
        - Creates a fresh `threading.RLock` for the unpickled instance.
        """
        #self._value = float(state["_value"]) #Remove August 11 2025
        self._value = type(self)._coerce(state["_value"])
        self._lock  = threading.RLock()
