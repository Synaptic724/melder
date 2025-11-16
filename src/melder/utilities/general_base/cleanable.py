from abc import ABC, abstractmethod

class Cleanable(ABC):
    """
    Cleanable
    -----------
    Abstract base class for all Cleanable objects in the system.

    Objects that manage runtime, memory, open resources, or registration
    within commandops must implement this interface.

    Supports context-manager usage:
        with MyObject(...) as obj:
            ...
        # cleanup() is called automatically on exit.

    Contract:
    ---------
    - `cleanup()` must be safe to call multiple times.
    - All cleanup must set `_cleaned = True` when cleanup completes.
    """

    __slots__ = ['_cleaned']

    def __init__(self):
        self._cleaned = False

    @property
    def cleaned(self) -> bool:
        """Returns True if the object has already been cleaned."""
        return self._cleaned

    @property
    def is_cleaned(self) -> bool:
        """Alias for `cleaned`."""
        return self._cleaned

    def check_cleaned(self):
        """
        Check if the object has been cleaned.

        Raises:
            RuntimeError: If the object has already been cleaned.
        """
        if self._cleaned:
            raise RuntimeError(f"{self.__class__.__name__} has already been cleaned. ")

    @abstractmethod
    def cleanup(self):
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement cleanup().")

    async def async_cleanup(self):
        """
        Dispose must be implemented by subclasses.

        Must:
        -----
        - Release all resources.
        - Deregister or finalize any allocations.
        - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement async_cleanup().")

    class _CleanupContext:
        """
        A standalone context manager that guarantees a call to cleanup()
        after the block exits, regardless of exceptions.

        It does NOT lock the object or interact with the object's own
        __enter__/__exit__. It is a completely separate deterministic
        teardown mechanism.

        This version ensures:
            - cleanup() is always called exactly once.
            - the reference to the owner is explicitly nulled.
            - no strong references remain after exit.
        """
        __slots__ = ("_owner", "_cleaned")

        def __init__(self, owner):
            self._owner = owner
            self._cleaned = False

        def __enter__(self):
            return self._owner

        def __exit__(self, exc_type, exc, tb):
            # Guarantee cleanup only once.
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


    def using_cleanup(self):
        """
        Return a context manager that performs cleanup() automatically
        when leaving the block.

        Examples
        --------
        # Use the object normally inside the block,
        # then guarantee cleanup afterward.
        with obj.using_cleanup():
            obj.do_something()

        # Does not interfere with the object's normal lock-based
        # __enter__/__exit__ context manager.
        """
        return Cleanable._CleanupContext(self)


    def async_using_cleanup(self):
        """
        Return an async context manager that performs async_cleanup()
        automatically when leaving the block.

        This method itself is NOT async. It returns an object that implements
        __aenter__ / __aexit__, which is what `async with` requires.
        """
        class _AsyncCleanupContext:
            __slots__ = ("_owner", "_cleaned")

            def __init__(self, owner):
                self._owner = owner
                self._cleaned = False

            async def __aenter__(self):
                return self._owner

            async def __aexit__(self, exc_type, exc, tb):
                owner = self._owner
                if owner is not None and not self._cleaned:
                    self._cleaned = True
                    try:
                        await owner.async_cleanup()
                    except Exception:
                        pass

                # Drop the reference
                self._owner = None
                return False

        return _AsyncCleanupContext(self)