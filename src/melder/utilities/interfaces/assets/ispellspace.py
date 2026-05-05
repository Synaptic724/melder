from typing import Any, Optional, Protocol, runtime_checkable
from melder.utilities.interfaces.assets.icleanable import ICleanable

@runtime_checkable
class ISpellSpace(ICleanable, Protocol):
    """
    Scope handle for spellspace-scoped lifecycles.

    Purpose:
        Define the public contract for a SpellSpace-like object that
        manages a spellspace scope owned by a Conduit.
    Contract:
        - Provides a stable id and monotonic version counter.
        - Enforces active-scope checks for meld calls.
        - Supports reset and cleanup semantics consistent with SpellSpace.
    Threading:
        - No internal locking is required by the contract; callers should
          synchronize via the owning Conduit if used concurrently.
    Lifecycle:
        - cleanup() is idempotent and releases owner references.
    """

    _id: str
    _owner_conduit: Optional["IConduit"]
    _version: int

    @property
    def id(self) -> str:
        """
        Stable identifier for this spellspace scope.

        Returns:
            str: Unique ID assigned at construction time.
        """
        ...

    @property
    def owner_conduit(self) -> Optional["IConduit"]:
        """
        Owning Conduit for this spellspace.

        Returns:
            Optional[IConduit]: The owner conduit, or None after cleanup.
        """
        ...

    @property
    def version(self) -> int:
        """
        Monotonic version counter for this spellspace.

        Contract:
            - Increments on reset().

        Returns:
            int: Current version value.
        """
        ...

    def meld(
            self,
            spell_name: str | None = None,
            *,
            spell: str | object | None = None,
            spellframe: str | object | None = None,
            binding_name: str | None = None,
            spell_override: Optional[dict | list | tuple] = None,
    ) -> Any:
        """
        Delegate meld to the owner Conduit while enforcing active scope.

        Contract:
            - Raises SpellSpaceScopeError if this spellspace is not active.
            - Propagates errors from the owning Conduit meld pipeline.

        Args:
            spell_name: Optional human-readable spell name.
            spell: Unique spell identifier (typically version id).
            spellframe: Optional spellframe metadata.
            binding_name: Optional binding name metadata.
            spell_override: Optional override payload for meld metadata.

        Returns:
            Any: The resolved instance from the owner Conduit.
        """
        ...

    def reset(self) -> None:
        """
        Clear spellspace-bound instances and increment version.

        Contract:
            - Clears spellspace-specific creations in the owner.
            - Increments the version counter on success.

        Raises:
            SpellSpaceScopeError: If the owner does not expose spellspace storage.
            RuntimeError: If this SpellSpace has been cleaned.
        """
        ...
