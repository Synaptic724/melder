from abc import abstractmethod, ABC


class IDisposable(ABC):
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
        - Provide a `dispose()` method.
        - Register all their cleanups inside `dispose()`.
        - Optionally provide a `cleanup()` alias.
        - Handle multiple calls to `dispose()` gracefully.
    """
    __slots__ = ["_disposed", ] # Prevents memory leaks by ensuring the object is not kept alive by circular references.

    def __init__(self):
        self._disposed = False

    @property
    def disposed(self):
        """
        Check if the object is sealed.
        :return: True if sealed, False otherwise.
        """
        return self._disposed

    @abstractmethod
    def dispose(self):
        """
        Dispose must be implemented by subclasses.
        It MUST:
            - Release all allocated resources.
            - Kill or join all running threads.
            - Deregister itself from any supervisors or orchestrators.
            - Clear any persistent state to avoid memory leakage.
            - Be idempotent (safe to call multiple times).
        """
        raise NotImplementedError("Subclasses must implement this method.")
