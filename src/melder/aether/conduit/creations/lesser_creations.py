from uuid import UUID, uuid4
from threading import RLock
from typing import List, Optional
# Melder imports
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.general_base.sealable import Sealable
from melder.utilities.interfaces.interfaces import ISealable
class LesserCreations(Sealable):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str]):
        """
        Initialize a new LesserCreations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The internal dictionaries hold references to the locally created objects,
        indexed by the spell's unique ID (`UUID`).
        """
        super().__init__()
        self._unique_per_scope: ConcurrentDict[UUID, object] = ConcurrentDict()
        self._many: ConcurrentDict[UUID, ConcurrentList[object]] = ConcurrentDict()

        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

        self._sealed = False
        self._lock = RLock()

    #region Destructor

    def seal(self) -> None:
        """
        Seal the creations manager, disposing of all managed objects.

        Once sealed, no further modifications are allowed. If any disposal method fails,
        an `ExceptionGroup` containing all errors is raised.

        Raises:
            ExceptionGroup: Contains a list of all exceptions encountered during cleanup.
        """
        if self._sealed:
            return
        with self._lock:
            if self._sealed:
                return
            self._sealed = True
            errors = []

            errors.extend(self._seal_unique_per_scope())
            errors.extend(self._seal_many())

            self._unique_per_scope = None
            self._many = None
            self._disposal_method_names = None

            if errors:
                raise ExceptionGroup("Errors occurred during sealing", errors)

    def _seal_unique_per_scope(self) -> List[Exception]:
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

    def _seal_many(self) -> List[Exception]:
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

        Attempts to clean up an object based on configured disposal mechanisms.

        Disposal Priority:
          1. **ISealable:** If the object implements `ISealable`, call its `seal()` method.
          2. **Configured Methods:** If disposal is enabled, attempt user-defined cleanup methods (`disposal_method_names`).

        Args:
            item (object): The object instance to dispose of.

        Returns:
            Optional[Exception]: Returns a `RuntimeError` if cleanup failed during an attempt, else `None`.
        """
        if item is None:
            return None

        # Priority 1: ISeal interface
        if isinstance(item, ISealable):
            try:
                item.seal()
                return None
            except Exception as ex:
                return RuntimeError(f"Failed to seal ISeal object {item}: {ex}")

        # Priority 2: Disposal methods
        if not self._disposal_enabled:
            return None

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                method = getattr(item, method_name)
                if callable(method):
                    try:
                        method()
                        return None  # Cleanup successful
                    except Exception as ex:
                        return RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")

        # If no cleanup methods succeeded or were found, treat as no error
        return None

    #endregion Destructor


    def transfer_data_and_clear(self) -> dict:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and seals the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        # Note: Assuming ConcurrentDict/ConcurrentList provide thread-safe copy/clear operations.
        # Temporary freeze before copy/clear for consistency (implementation detail of ConcurrentDict/List)
        # self._unique_per_scope.freeze()
        # self._many.freeze()
        try:
            data = {
                "unique_per_scope": self._unique_per_scope.copy(),
                "many": self._many.copy()
            }
        finally:
            self._unique_per_scope.clear()
            self._many.clear()
            self.seal()

        return data


    def add_unique_per_scope(self, key: UUID, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (UUID): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique_per_scope:
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = item

    def add_many(self, key: UUID, item: object) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (UUID): Collection identifier (Spell ID).
            item (object): Object instance to add.

        Raises:
            RuntimeError: If the Creations manager is sealed.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)