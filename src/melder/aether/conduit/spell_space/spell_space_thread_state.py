import threading
from typing import Any, List, Optional

from melder.utilities.general_base.cleanable import Cleanable


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
    """

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
    """

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
