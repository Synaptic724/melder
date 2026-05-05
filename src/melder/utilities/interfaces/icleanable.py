from typing import Protocol, runtime_checkable

@runtime_checkable
class ICleanable(Protocol):
    """
    Protocol definition for Cleanable.

    This protocol mirrors the public API of the Cleanable
    abstract base class.
    """

    _cleaned: bool

    @property
    def cleaned(self) -> bool:
        """Returns True if the object has already been cleaned."""
        ...

    @property
    def is_cleaned(self) -> bool:
        """Alias for `cleaned`."""
        ...

    def check_cleaned(self) -> None:
        """
        Check if the object has been cleaned.

        Raises:
            RuntimeError: If the object has already been cleaned.
        """
        ...

    def  cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...

    async def async_cleanup(self) -> None:
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        ...
