from melder.utilities.concurrent_dictionary import ConcurrentDict
from melder.utilities.interfaces import ISeal
import threading
from typing import List, Optional

class Creations(ISeal):
    """
    Creations manages all instantiated objects within a Conduit.

    It handles lifecycle operations such as:
      - Sealing and resource disposal
      - Organized storage of unique, unique-per-scope, and many instances

    Disposal behavior is governed by the application-wide configuration,
    specifically:
      - Whether disposal is enabled
      - Which method names to attempt during cleanup
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

    def add_unique(self, key: str, item: object) -> None:
        pass

    def add_unique_per_scope(self, key: str, item: object) -> None:
        pass

    def add_many(self, key: str, item: object) -> None:
        pass

    def seal(self) -> None:
        """
        Seal the creations, cleaning up all managed objects.

        Once sealed, no further modifications are allowed.
        """
        if self.sealed:
            return

        with self._lock:
            self._seal_unique()
            self._seal_unique_per_scope()
            self._seal_many()
            self.sealed = True

    def _seal_unique(self) -> None:
        for _, item in self._unique.items():
            if item is not None:
                self._attempt_cleanup(item)
        self._unique.dispose()

    def _seal_unique_per_scope(self) -> None:
        for _, item in self._unique_per_scope.items():
            if item is not None:
                self._attempt_cleanup(item)
        self._unique_per_scope.dispose()

    def _seal_many(self) -> None:
        for _, items in self._many.items():
            for item in items:
                if item is not None:
                    self._attempt_cleanup(item)
        self._many.dispose()

    def _attempt_cleanup(self, item: object) -> None:
        """
        Attempt to clean up an object by calling its seal/disposal method.

        Priority:
          1. If the object is an instance of ISeal, call seal() (always, even if disposal is disabled).
          2. Else, if disposal is enabled, attempt to call a custom disposal method.
          3. Else, skip.

        If disposal is globally disabled, only ISeal objects will be cleaned up.
        """
        if item is None:
            return

        # Priority 1: If it is an ISeal object, ALWAYS seal it
        if isinstance(item, ISeal):
            try:
                item.seal()
            except Exception as ex:
                raise RuntimeError(f"Failed to seal ISeal object {item}: {ex}")
            return  # Done, no further disposal needed

        # Priority 2: If disposal is globally enabled, use configured disposal methods
        if not self._disposal_enabled:
            return

        for method_name in self._disposal_method_names:
            if hasattr(item, method_name):
                method = getattr(item, method_name)
                if callable(method):
                    try:
                        method()
                        return  # Stop after first successful cleanup
                    except Exception as ex:
                        raise RuntimeError(f"Failed to dispose object {item} using method '{method_name}': {ex}")
