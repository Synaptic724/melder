from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from threading import RLock
from melder.utilities.interfaces.icleanable import ICleanable
from melder.aether.conduit.creations.creation import Creation

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
    _owner_conduit_id: str
    _id: str

    def _attempt_cleanup(self, creation: object) -> Optional[Exception]:
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

    def get_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
    ) -> Optional[Creation]:
        """
        Return one spellspace-scoped creation wrapper, if present.

        Args:
            spellspace_id: Spellspace bucket identifier.
            spell_id: Spell id inside the spellspace bucket.

        Returns:
            Optional[Creation]: Stored creation wrapper or None.
        """
        ...

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the owning conduit id for this creations manager.

        Returns:
            str: Stable owner conduit id.
        """
        ...

    def get_active_spellspace(self) -> Any:
        """
        Return the currently active spellspace for this creations owner.

        Returns:
            Any: Active spellspace object or None.
        """
        ...

    def clear_spellspace_instances(self, spellspace_id: str) -> None:
        """
        Clear and dispose all creations for one spellspace bucket.

        Args:
            spellspace_id: Spellspace bucket identifier.

        Returns:
            None.
        """
        ...

