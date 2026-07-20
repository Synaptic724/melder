import threading
from typing import Any, List, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.custom_exceptions.spell_space_scope_error import (
    SpellSpaceScopeError,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class _SpellSpaceLocal(threading.local):
    """
    Per-thread spellspace storage for one `SpellSpaceThreadState`.

    Purpose:
        Ensure each participating thread starts with one concrete
        `spellspace_stack` list so the owner does not need owned-code
        `getattr(...)` probes to discover whether thread-local state exists.

    Contract:
        - Every thread gets its own independent `spellspace_stack` list.
        - The list is initialized eagerly on first access in each thread.

    Threading:
        Extends `threading.local`, so attribute storage is per-thread by
        construction. No lock is needed or taken.

    Lifecycle / Cleanup:
        Owned by one `SpellSpaceThreadState` and released with it.

    Registration:
        MELDER KERNEL - guarded, matching the existing private-class precedent
        (`_Specificity`). Private and unreachable from user code.

    Subsystem Context:
        The storage primitive under `SpellSpaceThreadState`; it holds the
        per-thread list, while the holder owns the contract and cleanup.

    System Context:
        The eager `__init__` is the point of this class existing at all, and
        the reason is a policy rule rather than convenience: `threading.local`
        subclasses normally force callers into `getattr(local, "stack", None)`
        probes to discover whether the current thread has been initialized, and
        `banned_patterns.md:8-18` forbids defensive `getattr`/`hasattr` on
        owned attributes. Initializing the stack eagerly per thread makes the
        attribute unconditionally present, so the owner can use direct access
        and keep the owned-code contract strict.
    """

    __melder_internal__ = _mrg.sentinel
    def __init__(self) -> None:
        """
        Initialize the current thread's spellspace stack.

        Returns:
            None.
        """
        self.spellspace_stack: List[Any] = []


class SpellSpaceThreadState(Cleanable):
    """
    Thread-local spellspace stack holder for one conduit.

    Purpose:
        Provide one lightweight active spellspace stack per thread for a single
        conduit without relying on dynamically-created `ContextVar` objects.

    Contract:
        - Active spellspaces are isolated per thread.
        - Recursive spellspace entry is represented by list push/pop order.
        - `get()` preserves the older conduit-private list-shaped access
          pattern so directly implicated tests and experiments can continue to
          force or clear state explicitly.
        - `set(...)` replaces the current thread's whole spellspace stack with
          a detached copy of the provided list.
        - `cleanup()` retires the holder and prevents future access through
          `check_cleaned()`.

    Owned State:
        One `_local` (`_SpellSpaceLocal`), which itself owns the per-thread
        `spellspace_stack` lists.

    Threading:
        Isolation IS the design: each thread sees only its own stack, so no
        lock is required or taken. This is a deliberate alternative to
        dynamically-created `ContextVar` objects.

    Lifecycle / Cleanup:
        Owned by one conduit. `cleanup()` retires the holder and subsequent
        access raises through `check_cleaned()`.

    Registration:
        MELDER KERNEL - guarded. Internal conduit state; users interact with
        spellspaces through `conduit.enter_spellspace()`.

    Subsystem Context:
        The per-thread half of spellspace scoping, beneath `SpellSpace` and
        `SpellSpacePool`. It answers "which spellspace is active for THIS
        thread right now" - the question `SpellSpaceMeld` must resolve before it
        may serve `unique_per_spell_space`.

    System Context:
        A STACK rather than a single slot, because spellspace entry nests: a
        request may enter an inner scope and must restore the outer one on
        exit, so push/pop order is the representation of recursion. A single
        pointer would make nested entry silently destroy the parent scope.
        Thread-local rather than shared is what makes concurrent requests safe
        without contention - two threads in the same conduit genuinely have
        different active spellspaces, and any shared structure would need a
        lock on the hottest possible path.
        `set(...)` replaces the whole stack with a detached copy, which exists
        for tests and experiments that must force or clear state explicitly;
        it is deliberately not part of the normal enter/exit flow.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + ["_local"]

    def __init__(self) -> None:
        """
        Initialize one thread-local spellspace state holder.

        Returns:
            None.
        """
        super().__init__()
        self._local: _SpellSpaceLocal = _SpellSpaceLocal()

    def cleanup(self) -> None:
        """
        Retire this thread-local spellspace state holder.

        Contract:
            - Idempotent cleanup.
            - Clears the current thread's spellspace stack before dropping the
              local holder reference.
            - After cleanup, public accessors fail through `check_cleaned()`.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._local.spellspace_stack.clear()
        del self._local

    def get(self) -> List[Any]:
        """
        Return the current thread's spellspace stack as a list-shaped view.

        Returns:
            List[Any]:
                Detached copy of the current thread's spellspace stack.
        """
        return list(self._local.spellspace_stack)

    def set(self, stack: List[Any]) -> None:
        """
        Replace the current thread's spellspace stack from a list-shaped view.

        Args:
            stack:
                Detached spellspace stack for the current thread.

        Returns:
            None.

        Raises:
            TypeError:
                If `stack` is not a list.
        """
        if not isinstance(stack, list):
            raise TypeError("spellspace stack must be a list.")
        self._local.spellspace_stack = list(stack)

    def push(self, space: Any) -> None:
        """
        Push one active spellspace onto the current thread stack.

        Purpose:
            Provide a direct hot-path append operation so callers that only
            need stack mutation do not have to round-trip through list-copy
            `get()` / `set()` helpers.

        Args:
            space:
                Spellspace object becoming active on the current thread.

        Returns:
            None.
        """
        self._local.spellspace_stack.append(space)

    def pop(self) -> Any:
        """
        Pop and return the current thread's active spellspace.

        Returns:
            Any:
                Previously active spellspace object.

        Raises:
            IndexError:
                If the current thread stack is empty.
        """
        return self._local.spellspace_stack.pop()

    def pop_expected(self, expected: Any) -> Any:
        """
        Pop the current active spellspace only when it matches `expected`.

        Purpose:
            Fuse top-of-stack validation and pop into one hot-path operation so
            managed spellspace exit does not need separate `get_active()` and
            `pop()` calls.

        Args:
            expected:
                Spellspace object that must currently be the top-of-stack
                entry for the active thread.

        Returns:
            Any:
                The same spellspace object that was popped from the current
                thread stack.

        Raises:
            SpellSpaceScopeError:
                If the current thread stack is empty or the active spellspace
                is not `expected`.
        """
        stack = self._local.spellspace_stack
        if not stack or stack[-1] is not expected:
            raise SpellSpaceScopeError(
                "SpellSpace stack corruption detected while exiting."
            )
        return stack.pop()

    def clear_current_thread(self) -> None:
        """
        Clear the current thread's spellspace stack in place.

        Returns:
            None.
        """
        self._local.spellspace_stack.clear()

    def drain(self) -> List[Any]:
        """
        Detach and return the current thread's full spellspace stack.

        Purpose:
            Provide a destructive read for cleanup paths that need the current
            thread's stack exactly once before resetting it to empty.

        Contract:
            - Empty fast path: when the stack is already empty (the common
              pooled scope-cycle case - scopes exited properly before
              cleanup), the LIVE empty list is returned without allocating a
              replacement or writing the thread-local slot. Callers must
              treat the returned list as read-only; both cleanup callers only
              iterate it.
            - Non-empty stacks are detached exactly as before: the caller
              owns the returned list and the thread resets to a fresh empty
              stack.

        Returns:
            List[Any]:
                Previously active spellspace stack for the current thread.
        """
        stack = self._local.spellspace_stack
        if not stack:
            # Per-cycle hot path (`_cleanup_spellspaces_for_pool`): skip the
            # list allocation + thread-local store when there is nothing to
            # detach.
            return stack
        self._local.spellspace_stack = []
        return stack

    def get_active(self) -> Optional[Any]:
        """
        Return the current thread's active spellspace, if any.

        Returns:
            Optional[Any]:
                Active spellspace object for the current thread, or `None`.
        """
        stack = self._local.spellspace_stack
        if not stack:
            return None
        return stack[-1]
