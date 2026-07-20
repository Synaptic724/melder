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
    from melder.aether.conduit.spell_space.spell_space_thread_state import (
        SpellSpaceThreadState,
    )


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

    Threading:
        Concurrency is inherited from `AbstractElasticPool`; this subclass adds
        no locking of its own.

    Lifecycle / Cleanup:
        Owned by one conduit and torn down with it. Recycling a spellspace is
        NOT destruction - `reset()` clears spellspace-scoped instances and bumps
        the version, while the permanent cleanup lane is what actually destroys
        one.

    Registration:
        MELDER KERNEL - guarded. Constructed by the owning conduit; users reach
        spellspaces through `conduit.enter_spellspace()`, never through the pool.

    Subsystem Context:
        The reuse layer under `SpellSpace`, and the sibling of `ConduitPool`
        (which does the same for lesser conduit shells). Both exist because the
        objects they pool are request-frequency objects whose construction cost
        would otherwise be paid on every scope entry.

    System Context:
        Pooling a scope object is only safe because scope identity is VERSIONED
        rather than object-identity based. A recycled spellspace bumps its
        version on reset, so any stale handle held across the recycle boundary
        fails its active-scope check instead of silently melding into a reused
        shell that now belongs to a different request. Without that versioning
        this pool would be a correctness hazard rather than an optimization -
        which is the same reasoning that makes `pooled_lesser` a distinct
        `ConduitState` rather than just an idle `lesser`.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = AbstractElasticPool.__slots__ + [
        "_owner_conduit_creations",
        "_conduit_meld",
        "_owner_conduit_id",
        "_spellspace_registry",
        "_spellspace_stack_state",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            conduit_meld: ConduitMeld,
            owner_conduit_creations: ConduitCreations,
            spellspace_registry: set[SpellSpace],
            spellspace_stack_state: SpellSpaceThreadState,
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
            spellspace_stack_state:
                Conduit-owned per-thread active-scope stack holder injected
                into pooled spellspaces so each space can perform its own
                managed context-manager exit. Referenced, never owned, by the
                pool and its spellspaces.
            **kwargs:
                Elastic pool policy arguments forwarded to the base pool.
        """
        super().__init__(**kwargs)
        self._owner_conduit_id: str = owner_conduit_id
        self._conduit_meld: ConduitMeld = conduit_meld
        self._owner_conduit_creations: ConduitCreations = owner_conduit_creations
        self._spellspace_registry: set[SpellSpace] = spellspace_registry
        self._spellspace_stack_state: SpellSpaceThreadState = (
            spellspace_stack_state
        )

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
            spellspace_stack_state=self._spellspace_stack_state,
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
            - Uses one direct deque pop miss path instead of pre-checking idle
              state under an outer Python lock.
        """
        try:
            return self._idle.pop()
        except IndexError:
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
            so the generic elastic-pool synchronization work does not add value
            on the hot path. This override keeps the same external acquire
            contract while making the direct deque pop the first operation.

        Contract:
            - Reuses one idle spellspace when available.
            - Creates one new spellspace when the idle pool is empty.
            - Preserves manual-path registry tracking when `track_registry=True`.
            - Leaves managed-path spellspaces untracked in the registry when
              `track_registry=False`.
            - Uses one direct deque pop miss path instead of pre-checking idle
              state under an outer Python lock.
        """
        try:
            pooled_space = self._idle.pop()
        except IndexError:
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
            - Appends the returned spellspace first.
            - Retains returned spellspaces while idle capacity remains at or
              below the current target.
            - Evicts one cold idle spellspace with `popleft()` when retained
              capacity is exceeded.
        """
        self._idle.append(obj)
        if len(self._idle) <= self._target_idle:
            return
        try:
            overflow_space = self._idle.popleft()
        except IndexError:
            return
        self.destroy_object(overflow_space)
