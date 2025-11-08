from abc import ABC, abstractmethod

class Sealable(ABC):
    """
    Sealable
    -----------
    Abstract base class for all Sealable objects in the system.

    Objects that manage runtime, memory, open resources, or registration
    must implement this interface.

    Supports context-manager usage:
        with MyObject(...) as obj:
            ...
        # seal() is called automatically on exit.

    Contract:
    ---------
    - `seal()` must be safe to call multiple times.
    - All sealing must set `_sealed = True` when sealing completes.
    """

    __slots__ = ['_sealed']

    def __init__(self):
        self._sealed = False

    @property
    def sealed(self) -> bool:
        """Returns True if the object has already been sealed."""
        return self._sealed

    @property
    def is_sealed(self) -> bool:
        """Alias for `sealed`."""
        return self._sealed

    def check_sealed(self):
        """
        Check if the object has been sealed.

        Raises:
            RuntimeError: If the object has already been sealed.
        """
        if self._sealed:
            raise RuntimeError(f"{self.__class__.__name__} has already been sealed. ")

    @abstractmethod
    def seal(self):
        """
        Seal must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement seal().")

    async def async_seal(self):
        """
        Seal must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement async_seal().")