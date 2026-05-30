import threading
from typing import TYPE_CHECKING, Optional, Union, ClassVar

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.aether.conduit.creations.creations import Creations
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
if TYPE_CHECKING:
    from melder.aether.conduit.creations.conduit_creations import (
        ConduitCreations,
    )
    from melder.aether.conduit.meld.meld import Meld
    from melder.aether.conduit.spell_space.spell_space_pool import SpellSpacePool



class SpellSpace(Cleanable):
    """
    Explicit scope handle for `Existence.unique_per_spell_space`.

    Purpose:
        Represent one spellspace-bound resolution window without storing a live
        conduit back-reference. The conduit remains the factory for spellspaces,
        but the runtime scope object carries only the explicit collaborators it
        needs to execute, reset, and unregister itself.

    Contract:
        - Owns one stable spellspace id and one stable owner conduit id.
        - Delegates runtime execution through one owned `SpellSpaceMeld`.
        - Clears spellspace-scoped instances through the injected `Creations`.
        - Unregisters itself from the injected spellspace registry on cleanup.
        - Does not own conduit-wide resolution caches or control-plane state.

    Threading:
        - Uses an internal `RLock` for cleanup/reset idempotence.

    Lifecycle:
        - Created by `Conduit.create_spellspace(...)` or `Conduit.enter_spellspace(...)`.
        - Normal cleanup returns the spellspace to its conduit-local pool.
        - Permanent cleanup drops all injected collaborators.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_id",
        "_owner_conduit_id",
        "_meld",
        "_creations",
        "_owner_conduit_creations",
        "_spellspace_registry",
        "_spellspace_pool",
        "_permanent_cleanup_requested",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            meld: Meld,
            owner_conduit_creations: ConduitCreations,
            spellspace_registry: set["SpellSpace"],
            spellspace_pool: SpellSpacePool,
    ) -> None:
        """
        Create one explicit spellspace scope.

        Args:
            owner_conduit_id:
                Stable id of the conduit that created this spellspace.
            meld:
                Meld runtime used for explicit spellspace execution.
            owner_conduit_creations:
                Conduit-owned creations manager used for conduit-scoped and
                active-spellspace-routed execution beneath the spellspace front
                door.
            spellspace_registry:
                Conduit-owned registry set used for spellspace lifecycle
                bookkeeping and self-unregistration.
            spellspace_pool:
                Conduit-local pool that should receive this spellspace on
                normal cleanup.

        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._id: str = IDBuilder.create_id()
        self._owner_conduit_id: str = owner_conduit_id
        self._meld: Meld = meld
        self._creations: Creations = Creations(
            owner_conduit_id=owner_conduit_id,
            id=self._id,
        )
        self._owner_conduit_creations: ConduitCreations = owner_conduit_creations
        self._spellspace_registry: set[SpellSpace] = spellspace_registry
        self._spellspace_pool: SpellSpacePool = spellspace_pool
        self._permanent_cleanup_requested: bool = False

    def cleanup(self) -> None:
        """
        Cleanup this spellspace through either the reusable or permanent lane.

        Contract:
            - Normal cleanup returns this spellspace to the conduit-local pool
              after reusable cleanup.
            - `permanent_cleanup()` forces the destructive lane even when a
              pool is attached.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            if self._permanent_cleanup_requested:
                self._cleanup_for_destroy()
                return
            self._cleanup_for_pool_reuse()
        self._spellspace_pool.release(self)

    def permanent_cleanup(self) -> None:
        """
        Permanently destroy this spellspace instead of returning it to a pool.

        Contract:
            - Flips the permanent cleanup flag immediately.
            - Reuses the normal cleanup entrypoint so all public teardown still
              flows through one surface.
        """
        self._permanent_cleanup_requested = True
        self.cleanup()
        
    def _cleanup_for_pool_reuse(self) -> None:
        """
        Clear spellspace-scoped runtime state so this object can be retained.

        Contract:
            - Clears spellspace-scoped creations for this spellspace id.
            - Removes this spellspace from the active registry.
            - Keeps collaborator references intact for later reuse.
        """
        self._creations.reset_for_pool()
        self._spellspace_registry.discard(self)

    def _cleanup_for_destroy(self) -> None:
        """
        Permanently destroy this spellspace and release collaborator references.

        Contract:
            - Clears spellspace-scoped creations before dropping references.
            - Removes this spellspace from the current registry.
            - Deletes the pool reference as part of final teardown.
        """
        self._creations.cleanup()
        self._spellspace_registry.discard(self)
        self._cleaned = True
        del self._spellspace_registry
        del self._owner_conduit_id
        del self._meld
        del self._creations
        del self._owner_conduit_creations
        del self._spellspace_pool
        del self._permanent_cleanup_requested

    @property
    def id(self) -> str:
        """
        Return the stable identifier for this spellspace.

        Returns:
            str: Unique id assigned at construction.
        """
        return self._id

    @property
    def owner_conduit_id(self) -> str:
        """
        Return the stable owner conduit id for this spellspace.

        Returns:
            str: Owner conduit id injected at construction time.
        """
        return self._owner_conduit_id

    def meld(
            self,
            spell_name: Optional[str] = None,
            *,
            spell: Optional[Union[str, object]] = None,
            spellframe: Optional[Union[str, object]] = None,
            binding_name: Optional[str] = None,
            spell_override: Optional[Union[dict, list, tuple]] = None,
    ) -> object:
        """
        Delegate one meld call through the injected Meld runtime.

        Contract:
            - Delegates resolution and lifecycle behavior to the shared
              conduit meld runtime through its spellspace front door.
            - Propagates runtime failures from the meld pipeline unchanged.

        Returns:
            object: The resolved runtime object returned by the shared meld runtime.
        """
        return self._meld.spellspace_meld(
            spellspace=self,
            spellspace_creations=self._creations,
            owner_conduit_creations=self._owner_conduit_creations,
            spell_name=spell_name,
            spell=spell,
            spellframe=spellframe,
            binding_name=binding_name,
            spell_override=spell_override,
        )
