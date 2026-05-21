from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from threading import RLock
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class ILesserCreations(ICleanable, Protocol):
    """
    Manages instantiated objects within a **Lesser Conduit** (Child Scope).

    Lesser Creations is a reduced scope manager, only tracking objects with
    `unique_per_scope` and `many` lifecycles, as other scopes (`unique`, etc.)
    are delegated to the parent Conduit.

    **Key Responsibilities:**
      * Storage and disposal of local-scope objects.
      * Providing a snapshot of local objects for transfer during an upgrade.
    """

    # -----------------
    # Attributes
    # -----------------
    _unique_per_scope: Dict[str, object]
    _many: Dict[str, List[object]]
    _lock: RLock
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _cleanup_unique_per_scope(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_scope` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_many(self) -> List[Exception]:
        """
        Internal

        Disposes of all multi-instance objects registered under the `many` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _attempt_cleanup(self, item: object) -> Optional[Exception]:
        """
        Internal

        Attempt to clean up an object strictly via a prioritized list of method names.

        Behavior:
          - Returns None if `item` is None.
          - Iterates the Creation's `disposal_method_names` in order
            (e.g., ["cleanup", "close", "dispose"]).
          - For the first attribute found on `item` that is callable, calls it.
          - If the call succeeds, returns None.
          - If the call raises, returns a RuntimeError wrapping the original exception.
          - If no listed methods exist on the object, returns None (treated as no-op).

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def transfer_data_and_clear(self) -> Dict[str, Any]:
        """
        Creates a lightweight snapshot of the current creations, clears the internal state, and cleans the manager.

        This is used when a Lesser Conduit is upgraded to a Normal Conduit, transferring ownership of local creations.

        Returns:
            dict: A dictionary containing copies of the internal state (`unique_per_scope` and `many`).
        """
        ...

    def add_unique_per_scope(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Adds a singleton object instance to the `unique_per_scope` scope.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in the `unique_per_scope` scope.
        """
        ...

    def add_many(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Adds an object instance to a multi-instance collection under the `many` scope.

        If the collection for the given key does not exist, it is created.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        ...

