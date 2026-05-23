import threading
from typing import Any, List, Optional


class SpellSpaceThreadState:
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
    """

    __slots__ = ("_local",)

    def __init__(self) -> None:
        """
        Initialize one thread-local spellspace state holder.

        Returns:
            None.
        """
        self._local: threading.local = threading.local()

    def get(self) -> List[Any]:
        """
        Return the current thread's spellspace stack as a list-shaped view.

        Returns:
            List[Any]:
                Detached copy of the current thread's spellspace stack.
        """
        stack = getattr(self._local, "spellspace_stack", None)
        if stack is None:
            return []
        return list(stack)

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
        stack = getattr(self._local, "spellspace_stack", None)
        if not stack:
            return None
        return stack[-1]
