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
    Burst-oriented holder pool for reusable `SpellSpace` shells.

    Purpose:
        Retain idle spellspace shells for fast reuse while keeping shell
        creation outside the hot borrow path on pool misses.

    Contract:
        - Pool ownership is conduit-local in this slice.
        - Reused spellspaces stay attached to the configured conduit runtime.
        - Destruction uses the spellspace permanent cleanup lane.
        - Borrow misses return `None` so the caller can create outside the
          holder path.
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

    def acquire_untracked(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> Optional[SpellSpace]:
        """
        Acquire one managed spellspace without registry bookkeeping.

        Purpose:
            The managed `enter_spellspace()` path already tracks active
            spellspaces on the conduit-local stack, so it only needs an idle
            shell when one is available.

        Contract:
            - Reuses one idle spellspace when available.
            - Returns `None` on a pool miss after recording borrow pressure.
            - Performs no registry add and no `prepare_object(...)` call.
        """
        pooled_space = self._try_acquire_idle()
        if pooled_space is not None:
            return pooled_space
        self._record_borrow_miss()
        return None

    def acquire(
            self,
            *args: Any,
            track_registry: bool = True,
            **kwargs: Any,
    ) -> Optional[SpellSpace]:
        """
        Acquire one manual spellspace shell with optional registry tracking.

        Purpose:
            Manual `create_spellspace()` needs registry tracking when an idle
            spellspace shell is reused, but on a miss the caller still owns the
            new-object construction step.

        Contract:
            - Reuses one idle spellspace when available.
            - Returns `None` on a pool miss after recording borrow pressure.
            - Preserves manual-path registry tracking when `track_registry=True`.
        """
        pooled_space = self._try_acquire_idle()
        if pooled_space is not None:
            return self.prepare_object(
                pooled_space,
                *args,
                track_registry=track_registry,
                **kwargs,
            )
        self._record_borrow_miss()
        return None

    def destroy_object(self, obj: SpellSpace) -> None:
        """
        Permanently destroy one spellspace that should not be retained.
        """
        obj.permanent_cleanup()

    def release(self, obj: SpellSpace) -> None:
        """
        Return one spellspace to idle storage or destroy it.

        Contract:
            - Delegates to the shared coarse burst-holder logic.
            - Assumes trusted private callers do not double-return the same
              spellspace shell.
        """
        super().release(obj)
