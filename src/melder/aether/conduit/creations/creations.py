import uuid
from uuid import uuid4
import threading
from typing import List, Optional
from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.concurrent_list import ConcurrentList
from melder.utilities.interfaces import ISeal

class Creations(ISeal):
    """
    Manages all instantiated objects within a Conduit.

    Responsibilities:
      - Storage and lifecycle management of created objects
      - Organized handling of unique, unique-per-scope, and many-instance collections
      - Controlled resource disposal and sealing based on configuration
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str]):
        """
        Initialize a new Creations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The items in this dictionary hold references to the objects created by the conduit.
        The UUID is the spellID of the object.
        """
        super().__init__()
        self._lock = threading.RLock()
        self._unique: ConcurrentDict[uuid.UUID, object] = ConcurrentDict()
        self._unique_per_scope: ConcurrentDict[uuid.UUID, object] = ConcurrentDict()
        self._many: ConcurrentDict[uuid.UUID, ConcurrentList[object]] = ConcurrentDict()
        self._unique_per_lineage: ConcurrentDict[uuid.UUID, object] = ConcurrentDict()
        self._unique_per_cluster: ConcurrentDict[uuid.UUID, object] = ConcurrentDict()

        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

    def _upgrade_from_lesser_conduit(self, **kwargs) -> None:
        """
        Upgrade from LesserCreations to Creations.

        This method is a placeholder for any specific upgrade logic needed.
        """
        if not len(self._unique_per_scope) == 0 and not len(self._many) == 0:
            raise RuntimeError("Objects already exist in conduit, cannot transfer data.")

        self._unique_per_scope = kwargs.get("unique_per_scope")
        self._many = kwargs.get("many")

    def add_unique(self, key: uuid4, item: object) -> None:
        """
        Add a unique object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique:
            raise ValueError(f"Key {key} already exists in unique objects.")
        self._unique[key] = item

    def add_unique_per_lineage(self, key: uuid4, item: object) -> None:
        """
        Add a unique-per-lineage object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique_per_lineage:
            raise ValueError(f"Key {key} already exists in unique-per-lineage objects.")
        self._unique_per_lineage[key] = item

    def add_unique_per_cluster(self, key: uuid4, item: object) -> None:
        """
        Add a unique-per-cluster object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique_per_cluster:
            raise ValueError(f"Key {key} already exists in unique-per-cluster objects.")
        self._unique_per_cluster[key] = item

    def add_unique_per_scope(self, key: uuid4, item: object) -> None:
        """
        Add a unique-per-scope object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique_per_scope:
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = item

    def add_many(self, key: uuid4, item: object) -> None:
        """
        Add an object to a multi-instance collection.

        Args:
            key (uuid4): Collection identifier.
            item (object): Object to add.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)

    def seal(self) -> None:
        """
        Seal the creations, disposing of all managed objects.

        Once sealed, no further modifications are allowed.
        """
        if self._sealed:
            return

        with self._lock:
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
            self._sealed = True

            if errors:
                raise ExceptionGroup("Errors occurred during sealing", errors)

    def _seal_unique(self) -> List[Exception]:
        """
        Dispose of all unique objects.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique.dispose()
        return errors

    def _seal_unique_per_lineage(self) -> List[Exception]:
        """
        Dispose of all unique-per-lineage objects.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_lineage.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_lineage.dispose()
        return errors

    def _seal_unique_per_cluster(self) -> List[Exception]:
        """
        Dispose of all unique-per-cluster objects.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_cluster.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_cluster.dispose()
        return errors

    def _seal_unique_per_scope(self) -> List[Exception]:
        """
        Dispose of all unique-per-scope objects.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_scope.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_scope.dispose()
        return errors

    def _seal_many(self) -> List[Exception]:
        """
        Dispose of all multi-instance objects.

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
            items.dispose()
        self._many.dispose()
        return errors

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Attempt to clean up an object by calling its disposal method.

        Priority:
          1. If object implements ISeal, call its seal() method (always).
          2. If disposal is enabled, attempt user-defined cleanup methods.
          3. If none succeed, object remains untouched.

        Returns:
            Exception if cleanup failed, else None.
        """
        if item is None:
            return None

        # Priority 1: ISeal interface
        if isinstance(item, ISeal):
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


class LesserCreations(ISeal):
    """
    Manages all instantiated objects within a Conduit.

    Responsibilities:
      - Storage and lifecycle management of created objects
      - Organized handling of unique, unique-per-scope, and many-instance collections
      - Controlled resource disposal and sealing based on configuration
    """

    def __init__(self, disposal_enabled: bool, disposal_method_names: List[str]):
        """
        Initialize a new Creations manager.

        Args:
            disposal_enabled (bool): Whether disposal behavior is active.
            disposal_method_names (List[str]): List of method names to attempt during cleanup.

        The items in this dictionary hold references to the objects created by the conduit.
        The UUID is the spellID of the object.
        """
        super().__init__()
        self._unique_per_scope: ConcurrentDict[uuid.UUID, object] = ConcurrentDict()
        self._many: ConcurrentDict[uuid.UUID, ConcurrentList[object]] = ConcurrentDict()

        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

        self._sealed = False
        self._lock = threading.RLock()

    def transfer_data_and_clear(self) -> dict:
        """
        Creates a lightweight snapshot of the current creations.
        Returns a dict containing copies of internal state.
        """
        self._unique_per_scope.freeze()
        self._many.freeze()
        try:
            return {
                "unique_per_scope": self._unique_per_scope.copy(),  # Assuming ConcurrentDict has copy()
                "many": self._many.copy()  # Assuming ConcurrentDict and ConcurrentList have copy()
            }
        finally:
            self._unique_per_scope.clear()
            self._many.clear()
            self.seal()


    def add_unique_per_scope(self, key: uuid4, item: object) -> None:
        """
        Add a unique-per-scope object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique_per_scope:
            raise ValueError(f"Key {key} already exists in unique-per-scope objects.")
        self._unique_per_scope[key] = item

    def add_many(self, key: uuid4, item: object) -> None:
        """
        Add an object to a multi-instance collection.

        Args:
            key (uuid4): Collection identifier.
            item (object): Object to add.
        """
        if self._sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)

    def seal(self) -> None:
        """
        Seal the creations, disposing of all managed objects.

        Once sealed, no further modifications are allowed.
        """
        if self._sealed:
            return

        with self._lock:
            errors = []

            errors.extend(self._seal_unique_per_scope())
            errors.extend(self._seal_many())

            self._unique_per_scope = None
            self._many = None
            self._disposal_method_names = None
            self._sealed = True

            if errors:
                raise ExceptionGroup("Errors occurred during sealing", errors)

    def _seal_unique_per_scope(self) -> List[Exception]:
        """
        Dispose of all unique-per-scope objects.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        errors = []
        for _, item in self._unique_per_scope.items():
            if item is not None:
                maybe_error = self._attempt_cleanup(item)
                if maybe_error:
                    errors.append(maybe_error)
        self._unique_per_scope.dispose()
        return errors

    def _seal_many(self) -> List[Exception]:
        """
        Dispose of all multi-instance objects.

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
            items.dispose()
        self._many.dispose()
        return errors

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Attempt to clean up an object by calling its disposal method.

        Priority:
          1. If object implements ISeal, call its seal() method (always).
          2. If disposal is enabled, attempt user-defined cleanup methods.
          3. If none succeed, object remains untouched.

        Returns:
            Exception if cleanup failed, else None.
        """
        if item is None:
            return None

        # Priority 1: ISeal interface
        if isinstance(item, ISeal):
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
