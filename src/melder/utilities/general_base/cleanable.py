import threading
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Literal, Optional, Type





class Cleanable(ABC):
    """

    Purpose:
        Abstract base class for objects that own an explicit cleanup lifecycle.
        This is the single teardown contract shared across the entire runtime.

    Responsibilities:
        - Own the canonical `_cleaned` lifecycle flag.
        - Provide `check_cleaned()` as the one guard for rejecting
          use-after-clean.
        - Provide `using_cleanup()` as a context manager that guarantees exactly
          one cleanup call on exit.
        - Require subclasses to implement deterministic teardown.

    Contract:
        - `cleanup()` must be idempotent.
        - Subclasses must set `_cleaned = True` when cleanup completes.
        - `check_cleaned()` is the canonical guard for rejecting use-after-clean.
        - `using_cleanup()` provides a separate helper context that guarantees
          one cleanup call on exit.
        - Every `Cleanable` starts live: `_cleaned` is False after `__init__`.

    Owned State:
        - `_cleaned`: the live/cleaned flag. The only state this base owns.

    Threading:
        The base itself holds no lock; `_cleaned` is a plain bool. Subclasses
        that can race cleanup against active work are responsible for their own
        lock, and the established pattern is to check `_cleaned`, acquire, then
        re-check inside the lock. On free-threaded builds that double-check is
        not optional.

    Lifecycle / Cleanup:
        Live on construction, cleaned exactly once. The repository teardown order
        for subclasses is: clean children, delete owned field references, then
        clean the logger last. Post-cleanup, an object is assumed unused; prefer
        letting `check_cleaned()` raise over silently returning.

    Registration:
        GUARDED. `Cleanable` is present in the generated `INTERNAL_MANIFEST`, so
        binding `Cleanable` itself is refused.

        Subclasses are unaffected. Enforcement is an EXACT `(module, qualname)`
        membership test in `bind.assert_allowed(...)` and does NOT walk the MRO,
        so a user subclass carries its own module and qualname, is absent from
        the manifest, and binds normally. `Cleanable` is referenced across ~277
        files and is explicitly intended for user subclassing; that
        non-inheritance is what makes guarding the base harmless here.

        A regression asserting that a user subclass of `Cleanable` still binds
        successfully guards that property.

    Subsystem Context:
        One of three `utilities/general_base/` base classes, alongside `Sync`
        (synchronization base) and `AbstractElasticPool` (pooling base). This is
        the most widely inherited type in the codebase: the crystals, the
        conduit runtime, the spellbook registries, the Nexus/Rift surfaces, and
        most utilities all descend from it. It hands off to nothing - it is the
        floor.

    System Context:
        Beneath every layer of the DGR and outside the boot order entirely.
        Cleanup ordering across the runtime (Conduit tears down Meld, Ward, then
        Creations; Aether cleans frames then resets singleton state) is
        expressed through this one contract, which is why its idempotence
        guarantee is load-bearing for the whole system rather than a local
        convenience.
    """

    __ast_helper_access__: str = "public"
    __agent_purpose__: str = (
        "access: public. Base cleanup contract. Subclass this when your object "
        "owns resources that need deterministic teardown; implement cleanup() "
        "idempotently and guard live-only methods with check_cleaned(). "
        "Registration-guarded, but lookup is exact and does not inherit, so "
        "your subclasses stay bindable."
    )

    __slots__ = ['_cleaned']

    _cleaned: bool

    def __init__(self) -> None:
        """
        Initialize the live/cleaned lifecycle flag for a new cleanable object.

        Contract:
        - Every `Cleanable` starts live with `_cleaned=False`.
        - Subclasses may extend initialization, but they inherit this one
          canonical cleaned-state flag.

        Returns:
            None.
        """
        self._cleaned: bool = False

    @property
    def cleaned(self) -> bool:
        """
        Return whether the object has already been cleaned.

        Contract:
            - MONOTONIC latch: reads the `_cleaned` flag, which only ever
              moves False -> True. Once this returns True it never returns
              False again for the object's life.

        Returns:
            bool:
                True when `_cleaned` has been set.
        """
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """
        Alias for `cleaned`.

        Contract:
            - Exact alias: reads the same `_cleaned` flag as `cleaned`, with
              the same monotonic semantics. Both spellings exist because call
              sites across the runtime use both.

        Returns:
            bool:
                Current cleaned-state flag.
        """
        return self._cleaned

    def check_cleaned(self) -> None:
        """
        Raise when the object has already been cleaned.

        Contract:
        - Subclasses use this as the standard use-after-clean guard.
        - No-op while the object is still live.

        Raises:
            RuntimeError: If the object has already been cleaned.

        Returns:
            None.
        """
        if self._cleaned:
            raise RuntimeError(f"{self.__class__.__name__} has already been cleaned. ")

    @abstractmethod
    def cleanup(self) -> None:
        """
        Release owned resources and mark the object cleaned.

        Subclass contract:
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        - Set `_cleaned = True` when teardown completes.

        Raises:
            NotImplementedError:
                Always on the base; every concrete subclass overrides it.

        Returns:
            None.
        """
        raise NotImplementedError("Subclasses must implement cleanup().")

    async def async_cleanup(self) -> None:
        """
        Async cleanup hook for subclasses that support asynchronous teardown.

        Subclass contract:
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        - Preserve the same lifecycle semantics as `cleanup()` once async
          teardown completes.

        Raises:
            NotImplementedError:
                Always on the base; subclasses that support async teardown
                override it.

        Returns:
            None.
        """
        raise NotImplementedError("Subclasses must implement async_cleanup().")

    class _CleanupContext:
        """
        Standalone context manager that guarantees one cleanup call on exit.

        Contract:
            - Does not rely on the owner's own `__enter__` / `__exit__`.
            - Calls `owner.cleanup()` at most once.
            - Drops the strong owner reference after exit.
            - Never suppresses exceptions raised by the caller's block.
        """
        __slots__ = ("_owner", "_cleaned", "_lock")

        _cleaned: bool

        def __init__(self, owner: "Cleanable") -> None:
            """
            Bind the helper context to one cleanable owner.

            Contract:
            - Stores one strong owner reference until exit.
            - Tracks whether cleanup has already been triggered so exit remains
              idempotent.

            Args:
                owner:
                    The cleanable object this context cleans up exactly once on
                    exit.
            """
            self._owner: Optional["Cleanable"] = owner
            self._cleaned: bool = False
            self._lock: threading.RLock = threading.RLock()

        def __enter__(self) -> "Cleanable":
            """
            Enter the cleanup helper context and return the owner.

            Contract:
                - Acquires the context's own `RLock` for the duration of the
                  `with` block, so entry and the single cleanup-on-exit are
                  serialized.

            Returns:
                Cleanable:
                    The owner object protected by this helper.

            Raises:
                RuntimeError:
                    If the context has already exited and dropped its owner.
            """
            self._lock.acquire()
            if self._owner is None:
                raise RuntimeError("Cleanup context no longer owns a live object.")
            return self._owner

        def __exit__(
                self,
                exc_type: Optional[Type[BaseException]],
                exc: Optional[BaseException],
                tb: Optional[TracebackType],
        ) -> Literal[False]:
            """
            Exit the cleanup helper context and trigger owner cleanup once.

            Contract:
                - Calls `owner.cleanup()` AT MOST ONCE across repeated exits,
                  swallowing any exception it raises (best-effort teardown),
                  then drops the strong owner reference so nothing leaks.
                - Never suppresses exceptions from the caller's `with` block.
                - Releases the context lock in a `finally`.

            Args:
                exc_type:
                    Exception type raised in the `with` block, or None.
                exc:
                    Exception instance raised in the `with` block, or None.
                tb:
                    Traceback for the `with`-block exception, or None.

            Returns:
                Literal[False]:
                    Always False so caller exceptions are never suppressed.
            """
            # Guarantee cleanup only once.
            try:
                owner = self._owner
                if owner is not None and not self._cleaned:
                    self._cleaned = True
                    try:
                        owner.cleanup()
                    except Exception:
                        pass

                # Explicitly drop the reference so nothing is leaked.
                self._owner = None

                # Do NOT suppress user exceptions.
                return False
            finally:
                self._lock.release()


    def using_cleanup(self) -> "_CleanupContext":
        """
        Return a helper context manager that guarantees `cleanup()` on exit.

        Contract:
        - Independent of any context-manager behavior implemented by the owner.
        - Intended for callers that want deterministic cleanup without relying
          on the object's own `__enter__` / `__exit__`.

        Returns:
            Cleanable._CleanupContext:
                Helper context manager bound to this object.
        """
        return Cleanable._CleanupContext(self)
