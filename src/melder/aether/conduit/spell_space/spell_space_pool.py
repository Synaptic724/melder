from typing import TYPE_CHECKING, Any, ClassVar, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool

if TYPE_CHECKING:
    from melder.aether.conduit.creations.conduit_creations import (
        ConduitCreations,
    )
    from melder.aether.conduit.meld.conduit_meld import ConduitMeld


class SpellSpacePool(AbstractElasticPool[SpellSpace]):
    """
    Elastic pool for reusable `SpellSpace` objects.

    Purpose:
        Keep spellspace instances alive across repeated use so normal cleanup
        can recycle them instead of permanently destroying them each time.

    Contract:
        - Pool ownership is conduit-local in this slice.
        - Reused spellspaces stay attached to the configured conduit runtime.
        - Destruction uses the spellspace permanent cleanup lane.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = AbstractElasticPool.__slots__ + [
        "_owner_conduit_creations",
        "_conduit_meld",
        "_owner_conduit_id",
        "_spellspace_registry",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            conduit_meld: ConduitMeld,
            owner_conduit_creations: ConduitCreations,
            spellspace_registry: set[SpellSpace],
            **kwargs: Any,
    ) -> None:
        """
        Initialize one conduit-local spellspace pool.

        Args:
            owner_conduit_id:
                Stable owner conduit id for pooled spellspaces.
            conduit_meld:
                Conduit-facing meld runtime used as the shared-core source for
                pooled spellspace meld objects.
            owner_conduit_creations:
                Conduit-owned creations manager used by pooled spellspaces
                when they need conduit-scoped routing.
            spellspace_registry:
                Conduit-owned registry used for spellspace bookkeeping.
            **kwargs:
                Elastic pool policy arguments forwarded to the base pool.
        """
        super().__init__(**kwargs)
        self._owner_conduit_id: str = owner_conduit_id
        self._conduit_meld: ConduitMeld = conduit_meld
        self._owner_conduit_creations: ConduitCreations = owner_conduit_creations
        self._spellspace_registry: set[SpellSpace] = spellspace_registry

    def create_object(self, *args: Any, **kwargs: Any) -> SpellSpace:
        """
        Create one new spellspace owned by this pool's conduit runtime.
        """
        return SpellSpace(
            owner_conduit_id=self._owner_conduit_id,
            conduit_meld=self._conduit_meld,
            owner_conduit_creations=self._owner_conduit_creations,
            spellspace_registry=self._spellspace_registry,
            spellspace_pool=self,
        )

    def prepare_object(
            self,
            obj: SpellSpace,
            *args: Any,
            track_registry: bool = True,
            **kwargs: Any,
    ) -> SpellSpace:
        """
        Reactivate one spellspace before use.
        """
        if track_registry:
            obj._registry_tracked = True
            obj._spellspace_registry.add(obj)
        return obj

    def acquire_untracked(self, *args: Any, **kwargs: Any) -> SpellSpace:
        """
        Acquire one managed spellspace without registry bookkeeping.

        Purpose:
            The managed `enter_spellspace()` path already tracks active
            spellspaces on the conduit-local stack, so it does not need the
            manual-path registry reactivation performed by `prepare_object()`.

        Contract:
            - Reuses one idle spellspace when available.
            - Creates one new spellspace when the idle pool is empty.
            - Returns the spellspace with `_registry_tracked == False`.
            - Performs no registry add and no `prepare_object(...)` call.
            - Skips generic diagnostic in-use bookkeeping because this trusted
              private fixed-capacity hot path does not use the generic elastic
              accounting contract.
        """
        with self._lock:
            if self._enabled and self._idle:
                return self._idle.pop()
            return self.create_object(*args, **kwargs)

    def acquire(
            self,
            *args: Any,
            track_registry: bool = True,
            **kwargs: Any,
    ) -> SpellSpace:
        """
        Acquire one spellspace with conduit-local fixed-capacity fast-path rules.

        Purpose:
            SpellSpace pools are created with fixed `baseline_idle == max_idle`,
            so the generic elastic-pool stretch/decay bookkeeping does not add
            value on the hot path. This override keeps the same external acquire
            contract while skipping the generic time-based policy work.

        Contract:
            - Reuses one idle spellspace when available.
            - Creates one new spellspace when the idle pool is empty.
            - Preserves manual-path registry tracking when `track_registry=True`.
            - Leaves managed-path spellspaces untracked in the registry when
              `track_registry=False`.
            - Skips generic diagnostic in-use bookkeeping because this trusted
              private fixed-capacity hot path does not use the generic elastic
              accounting contract.
        """
        with self._lock:
            if self._enabled and self._idle:
                pooled_space = self._idle.pop()
            else:
                pooled_space = self.create_object(*args, **kwargs)
        return self.prepare_object(
            pooled_space,
            *args,
            track_registry=track_registry,
            **kwargs,
        )

    def destroy_object(self, obj: SpellSpace) -> None:
        """
        Permanently destroy one spellspace that should not be retained.
        """
        obj.permanent_cleanup()

    def release(self, obj: SpellSpace) -> None:
        """
        Return one spellspace to idle storage or destroy it.

        Contract:
            - Uses a conduit-local fixed-capacity fast path.
            - Assumes trusted private callers do not double-return the same
              spellspace shell.
            - Retains returned spellspaces while idle capacity remains below the
              current target.
            - Destroys excess spellspaces immediately instead of paying generic
              elastic-pool time/decay bookkeeping that this pool does not need.
            - Skips generic diagnostic in-use bookkeeping because this trusted
              private fixed-capacity hot path does not use the generic elastic
              accounting contract.
        """
        with self._lock:
            if self._enabled and len(self._idle) < self._target_idle:
                self._idle.append(obj)
                return
            self.destroy_object(obj)
