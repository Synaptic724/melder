from threading import RLock
from typing import List, Optional

# Melder imports
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import IConduit


class LesserCreations(Cleanable):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str], conduit: IConduit):
        """
        Initialize a new LesserCreations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The internal dictionaries hold references to the locally created objects,
        indexed by the spell's unique ID (str).
        """
        super().__init__()
        self._conduit: IConduit = conduit
        self._id: str = conduit._id
        self._lock = RLock()

        # Internal storage for managed objects
        self._unique_per_scope: ConcurrentDict[str, object] = ConcurrentDict()
        self._many: ConcurrentDict[str, ConcurrentList[object]] = ConcurrentDict()

        # Disposal configuration
        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

    #region Destructor

    def cleanup(self) -> None:
        """
        Cleanup the creations manager, disposing of all managed objects.

        Once cleaned, no further modifications are allowed. If any disposal method fails,
        an `ExceptionGroup` containing all errors is raised.

        Raises:
            ExceptionGroup: Contains a list of all exceptions encountered during cleanup.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            errors = []

            errors.extend(self._cleanup_unique_per_scope())
            errors.extend(self._cleanup_many())

            self._unique_per_scope = None
            self._many = None
            self._conduit = None
            self._disposal_method_names = None

            if errors:
                raise ExceptionGroup("Errors occurred during cleanup", errors)

    def _cleanup_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_scope.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_scope.cleanup()
        return errors

    def _cleanup_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, items in self._many.items():
            for item in items:
                if item is not None:
                    maybe_error = self._attempt_cleanup(item)
                    if maybe_error:
                        errors.append(maybe_error)
            items.cleanup()
        self._many.cleanup()
        return errors

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        if item is None:
            return None

        if not self._disposal_enabled:
            return None

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                method = getattr(item, method_name)
                if callable(method):
                    try:
                        method()
                        return None
                    except Exception as ex:
                        return RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")

        return None


    #endregion Destructor


    def transfer_data_and_clear(self) -> dict:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and cleans the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        self.check_cleaned()
        try:
            data = {
                "unique_per_scope": self._unique_per_scope.copy(),
                "many": self._many.copy()
            }
        finally:
            self._unique_per_scope.clear()
            self._many.clear()
            self.cleanup()

        return data


    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        self.check_cleaned()
        if key in self._unique_per_scope:
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = item

    def add_many(self, key: str, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (UUID): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        self.check_cleaned()
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)