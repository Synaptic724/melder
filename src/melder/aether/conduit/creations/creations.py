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
        """
        self._unique = ConcurrentDict()
        self._unique_per_scope = ConcurrentDict()
        self._many = ConcurrentDict()

        self._disposal_enabled = disposal_enabled
        self._disposal_method_names = disposal_method_names or []

        self.sealed = False
        self._lock = threading.RLock()

    def add_unique(self, key: uuid4, item: object) -> None:
        """
        Add a unique object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self.sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key in self._unique:
            raise ValueError(f"Key {key} already exists in unique objects.")
        self._unique[key] = item

    def add_unique_per_scope(self, key: uuid4, item: object) -> None:
        """
        Add a unique-per-scope object to the manager.

        Args:
            key (uuid4): Unique identifier.
            item (object): Object to manage.
        """
        if self.sealed:
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
        if self.sealed:
            raise RuntimeError("Cannot add to sealed Creations.")
        if key not in self._many:
            self._many[key] = ConcurrentList()
        self._many[key].append(item)

    def seal(self) -> None:
        """
        Seal the creations, disposing of all managed objects.

        Once sealed, no further modifications are allowed.
        """
        if self.sealed:
            return

        with self._lock:
            self._seal_unique()
            self._seal_unique_per_scope()
            self._seal_many()

            self._unique = None
            self._unique_per_scope = None
            self._many = None
            self._disposal_method_names = None
            self.sealed = True

    def _seal_unique(self) -> None:
        """
        Dispose of all unique objects.
        :return:
        """
        for _, item in self._unique.items():
            if item is not None:
                self._attempt_cleanup(item)
        self._unique.dispose()

    def _seal_unique_per_scope(self) -> None:
        """
        Dispose of all unique-per-scope objects.
        :return:
        """
        for _, item in self._unique_per_scope.items():
            if item is not None:
                self._attempt_cleanup(item)
        self._unique_per_scope.dispose()

    def _seal_many(self) -> None:
        """
        Dispose of all multi-instance objects.
        :return:
        """
        for _, items in self._many.items():
            for item in items:
                if item is not None:
                    self._attempt_cleanup(item)
            items.dispose()
        self._many.dispose()

    def _attempt_cleanup(self, item: object) -> None:
        """
        Attempt to clean up an object by calling its disposal method.

        Priority:
          1. If object implements ISeal, call its seal() method (always).
          2. If disposal is enabled, attempt user-defined cleanup methods.
          3. If none succeed, object remains untouched.
        """
        if item is None:
            return

        # Priority 1: ISeal interface
        if isinstance(item, ISeal):
            try:
                item.seal()
            except Exception as ex:
                raise RuntimeError(f"Failed to seal ISeal object {item}: {ex}")
            return

        # Priority 2: Disposal methods
        if not self._disposal_enabled:
            return

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                method = getattr(item, method_name)
                if callable(method):
                    try:
                        method()
                        return  # Cleanup successful
                    except Exception as ex:
                        raise RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")
