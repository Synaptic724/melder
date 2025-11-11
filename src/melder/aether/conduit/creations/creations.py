from threading import RLock
from typing import List, Optional
import ulid
# Melder imports
from melder.utilities.data_structures.concurrent_dictionary import ConcurrentDict
from melder.utilities.data_structures.concurrent_list import ConcurrentList
from melder.utilities.general_base.sealable import Sealable

#TODO: Create a creations object to encapsulate the objects under my control.

class Creations(Sealable):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon sealing.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ISealable` or configured cleanup methods.
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str]):
        """
        Initialize a new Creations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The internal dictionaries hold references to the objects created by the conduit,
        indexed by the spell's unique ID (`str`).
        """
        super().__init__()
        self._id: str = str(ulid.ULID())
        self._lock = RLock()
        self._unique: ConcurrentDict[str, object] = ConcurrentDict()
        self._unique_per_scope: ConcurrentDict[str, object] = ConcurrentDict()
        self._many: ConcurrentDict[str, ConcurrentList[object]] = ConcurrentDict()
        self._unique_per_lineage: ConcurrentDict[str, object] = ConcurrentDict()
        self._unique_per_cluster: ConcurrentDict[str, object] = ConcurrentDict()

        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

    #region Destructor
    def seal(self) -> None:
        """
        Seal the creations manager, disposing of all managed objects across all existence types.

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

            errors.extend(self._seal_unique())
            errors.extend(self._seal_unique_per_scope())
            errors.extend(self._seal_many())
            errors.extend(self._seal_unique_per_lineage())
            errors.extend(self._seal_unique_per_cluster())

            self._unique = None
            self._unique_per_scope = None
            self._many = None
            self._disposal_method_names = None

            if errors:
                raise ExceptionGroup("Errors occurred during sealing", errors)

    def _seal_unique(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique.cleanup()
        return errors

    def _seal_unique_per_lineage(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_lineage` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_lineage.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_lineage.cleanup()
        return errors

    def _seal_unique_per_cluster(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_cluster` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_cluster.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_cluster.cleanup()
        return errors

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

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None or disposal is disabled.
          - Iterates `self._disposal_method_names` in order (e.g., ["seal", "cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Notes:
          - No Protocol/type checks are performed.
          - Cleanup semantics are entirely defined by the configured method list.

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

    def _upgrade_from_lesser_conduit(self, **kwargs) -> None:
        """
        Internal

        Transfers creations data from a `LesserCreations` instance during a conduit upgrade.

        Args:
            **kwargs: Dictionary containing creation scopes (e.g., `unique_per_scope`, `many`).

        Raises:
            RuntimeError: If the `Creations` manager already contains objects before transfer.
        """
        if not len(self._unique_per_scope) == 0 and not len(self._many) == 0:
            raise RuntimeError("Objects already exist in conduit, cannot transfer data.")

        self._unique_per_scope = kwargs.get("unique_per_scope")
        self._many = kwargs.get("many")

    def add_unique(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique` scope.

        Args:
            key (UUID): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique` scope.
        """
        self.check_sealed()
        if key in self._unique:
            raise ValueError(f"Key {key} already exists in unique objects.")
        self._unique[key] = item

    def add_unique_per_lineage(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_lineage` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_lineage` scope.
        """
        self.check_sealed()
        if key in self._unique_per_lineage:
            raise ValueError(f"Key {key} already exists in unique-per-lineage objects.")
        self._unique_per_lineage[key] = item

    def add_unique_per_cluster(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_cluster` scope.

        Args:
            key (UUID): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_cluster` scope.
        """
        self.check_sealed()
        if key in self._unique_per_cluster:
            raise ValueError(f"Key {key} already exists in unique-per-cluster objects.")
        self._unique_per_cluster[key] = item

    def add_unique_per_scope(self, key: str, item: object) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.

        Raises:
            RuntimeError: If the Creations manager is sealed.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        self.check_sealed()
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
            RuntimeError: If the Creations manager is sealed.
        """
        self.check_sealed()
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)