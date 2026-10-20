from typing import TYPE_CHECKING, Generic, Optional, Type, TypeVar

if TYPE_CHECKING:
    from types import TracebackType

    from melder.aether.conduit.creations.managed_spell_quantity import ManagedSpellQuantity

ManagedObjectT = TypeVar("ManagedObjectT")


class ManagedSpellLease(Generic[ManagedObjectT]):
    """
    One object leased from a managed spell's pool, and the one way to hand it back.

    Purpose:
        Pair a leased object with the pool it came from so it can be given back once - by `release()` or by leaving
        a `with` block - without looking the pool up again. Returned by `ReleaseManagedSpell().managed(obj)` and, from
        S5, by `Conduit.managed_spell_meld(...)`.

    Contract:
        - Holds the object and its pool, both borrowed: the object is the holder's to use until released, the pool is
          its root store's.
        - `release()` gives the object back once (`pool.put_back(obj)`: the pool's resets, then idle for the next
          lease); every later call does nothing. The lease counts as released even when the put-back raised - a
          raising reset (the pool destroyed the object) or a pool torn down with its root (the object stays the
          holder's) - so nothing is ever given back twice.
        - `object` answers the leased object until the lease is released, then raises: the object went back to its
          pool and may already be leased again.
        - `with lease as obj:` binds the object; leaving the block releases it, whether or not the block raised, and
          never suppresses the block's exception. A release error raised while the block was raising propagates with
          the block's exception as its `__context__`.
        - Identity is not tracked (owner, 2026-10-14): the lease trusts that the object is the one it carries.

    Threading:
        A handle for one holder, not a thread-safe object: releasing one lease from two threads at once may put the
        object back twice. Different leases are independent. The pool behind it is thread-safe.

    Lifecycle / Cleanup:
        The lease owns nothing. Releasing it drops its references to the object and the pool; the `released` flag
        stays readable.

    Registration:
        MELDER KERNEL - guarded. Created by `ReleaseManagedSpell.managed` (and S5's `Conduit.managed_spell_meld`);
        never bound as a spell.

    Subsystem Context:
        The managed lifetime (EPIC-2026-10-14-managed_spell_quantity): a meld leases an object from its root's pool;
        `ReleaseManagedSpell` or a lease gives it back. A class, never a generator, because a generator-based context
        manager costs about 600 ns more per use (measured 2026-10-14).

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        access: public. One leased managed object and its way back: `with ReleaseManagedSpell().managed(obj) as o:`
        releases `o` on exit (resets run, the object is pooled for the next lease); `lease.release()` does it by
        hand, once. Get one from ReleaseManagedSpell().managed(obj).
    """

    __slots__ = ("_object", "_pool", "_released")

    def __init__(self, obj: ManagedObjectT, pool: ManagedSpellQuantity) -> None:
        """
        Pair one leased object with the pool it goes back to.

        Args:
            obj:
                The leased object (borrowed; the holder's to use until released).
            pool:
                The pool it was leased from (borrowed; owned by its root's store).

        Returns:
            None.
        """
        self._object: ManagedObjectT = obj
        self._pool: ManagedSpellQuantity = pool
        self._released: bool = False

    @property
    def object(self) -> ManagedObjectT:
        """
        Return the leased object.

        Raises:
            RuntimeError: If the lease was released; its object went back to its pool.

        Returns:
            ManagedObjectT: The leased object.
        """
        if self._released:
            raise RuntimeError("This ManagedSpellLease was released; its object went back to its pool.")
        return self._object

    @property
    def released(self) -> bool:
        """
        Return whether the lease has given its object back.

        Returns:
            bool: True once `release()` ran (even if the put-back raised).
        """
        return self._released

    def release(self) -> None:
        """
        Give the object back to its pool, once.

        Contract:
            - The first call marks the lease released, drops its references and puts the object back
              (`pool.put_back`): the pool's resets run in order, then the object is idle for the next lease.
            - Every later call returns without doing anything.

        Raises:
            RuntimeError: The pool was torn down with its root; the object is the holder's to dispose.
            Exception: What a reset raised, after the pool destroyed the object.
            ExceptionGroup: A raising reset whose disposal failed too, or an elastic trim's disposal failures.

        Returns:
            None.
        """
        if self._released:
            return
        self._released = True
        obj = self._object
        pool = self._pool
        del self._object
        del self._pool
        pool.put_back(obj)

    def __enter__(self) -> ManagedObjectT:
        """
        Return the leased object for the `with` block.

        Raises:
            RuntimeError: If the lease was already released.

        Returns:
            ManagedObjectT: The leased object.
        """
        return self.object

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        """
        Release the object when the `with` block ends, never suppressing the block's exception.

        Args:
            exc_type: The type of the exception the block raised, or None.
            exc: The exception the block raised, or None.
            traceback: Its traceback, or None.

        Raises:
            As `release()`.

        Returns:
            None: Never suppresses.
        """
        self.release()
