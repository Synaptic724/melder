from abc import ABC, abstractmethod


class Seal(ABC):
    """
    Abstract base class for all disposable objects in the system.

    Usage:
        Any object that holds threads, memory, open resources, or registration
        within ThreadFactory must implement this.

        Automatically supports context-manager usage:
            with MyObject(...) as obj:
                ...
            # dispose() is called automatically on exit.

    Implementations MUST:
        - Provide a `seal()` method.
        - Register all their cleanups inside `seal()`.
        - Handle multiple calls to `seal()` gracefully.
    """
    __slots__ = ["_sealed"] # Prevents memory leaks by ensuring the object is not kept alive by circular references.
    def __init__(self):
        self._sealed = False

    @property
    def sealed(self):
        """
        Check if the object is sealed.
        :return: True if sealed, False otherwise.
        """
        return self._sealed

    @abstractmethod
    def seal(self):
        """
        Seal must be implemented by subclasses.
        It MUST:
            - Release all allocated resources.
            - Kill or join all running threads.
            - Deregister itself from any supervisors or orchestrators.
            - Clear any persistent state to avoid memory leakage.
            - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement this method.")
