from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from threading import RLock
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class ICreations(ICleanable, Protocol):
    """
    Manages all instantiated objects within a Conduit (Normal Scope).

    This manager is responsible for tracking object instances based on their lifecycle
    (`unique`, `unique_per_scope`, `many`, etc.) and enforcing resource disposal upon cleaning.

    **Key Responsibilities:**
      * Storage and lifecycle management of created objects.
      * Controlled resource disposal via `ICleanable` or configured cleanup methods.
    """

    # -----------------
    # Attributes
    # -----------------
    _lock: RLock
    _creations: 'Dict[str, object]'
    _id: str

    # -----------------
    # Methods
    # -----------------
    def _cleanup_unique(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_unique_per_lineage(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_lineage` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

    def _cleanup_unique_per_cluster(self) -> List[Exception]:
        """
        Internal

        Disposes of all objects registered under the `unique_per_cluster` existence scope.

        Returns:
            List[Exception]: List of any cleanup errors encountered.
        """
        ...

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

        Notes:
          - No Protocol/type checks are performed.
          - Cleanup semantics are entirely defined by the configured method list.

        Args:
            item: The object instance to dispose.

        Returns:
            Optional[Exception]: RuntimeError if a chosen cleanup method raised; otherwise None.
        """
        ...

    def _upgrade_from_lesser_conduit(self, **kwargs: Any) -> None:
        """
        Internal

        Transfers creations data from a `LesserCreations` instance during a conduit upgrade.

        Args:
            **kwargs: Dictionary containing creation scopes (e.g., `unique_per_scope`, `many`).

        Raises:
            RuntimeError: If the `Creations` manager already contains objects before transfer.
        """
        ...

    def add_creation(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one non-spellspace singleton creation.

        Args:
            key (str): Unique identifier (Spell ID).
            item (object): Object instance to manage.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
            ValueError: If the key already exists in creations.
        """
        ...

    def add_many_creations(
            self,
            key: str,
            item: object,
            *,
            has_disposal_methods: bool = False,
            disposal_methods: Optional[List[str]] = None,
    ) -> None:
        """
        Register one creation in the many-creations collection for the key.

        Args:
            key (str): Collection identifier (Spell ID).
            item (object): Object instance to add.
            has_disposal_methods: True when the spell declares disposal methods.
            disposal_methods: Ordered list of disposal method names for this creation.

        Raises:
            RuntimeError: If the Creations manager is cleaned.
        """
        ...

    def extract_spell_creations(self, spell_id: str) -> List[Dict[str, Any]]:
        """
        Remove and serialize all tracked creation state for one spell lineage.

        Purpose:
            Support ownership-transfer and rollback flows that need to move one
            lineage's live creation payload between conduit-owned `Creations`
            stores without destroying the underlying runtime objects first.

        Args:
            spell_id: Current version spell identifier whose creation payload
                should be extracted.

        Returns:
            List[Dict[str, Any]]:
                Serialized creation entries suitable for
                `restore_spell_creations(...)`.

        Raises:
            RuntimeError:
                If the Creations manager is cleaned.
        """
        ...

    def restore_spell_creations(
            self,
            spell_id: str,
            creations: List[Dict[str, Any]],
    ) -> None:
        """
        Restore previously extracted creation state for one spell lineage.

        Purpose:
            Rehydrate lineage-owned creation payloads that were previously
            extracted by `extract_spell_creations(...)`, typically during
            ownership transfer or rollback.

        Args:
            spell_id: Current version spell identifier that should regain the
                supplied creation payload.
            creations:
                Serialized entries produced by `extract_spell_creations(...)`.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the Creations manager is cleaned.
        """
        ...
