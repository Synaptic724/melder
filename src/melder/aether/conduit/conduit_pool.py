from typing import TYPE_CHECKING, Any, ClassVar, Optional

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit


class ConduitPool(AbstractElasticPool[Any]):
    """
    Root-conduit-owned elastic pool scaffold for reusable lesser conduits.

    Purpose:
        Provide a concrete home for lesser-conduit pooling state before real
        lesser-conduit acquire/release wiring is implemented.

    Contract:
        - Owned by one root conduit.
        - Keeps a stable reference to that root conduit and its id.
        - Stores only lesser conduits.
        - Hands back one retained lesser when available.
        - Never constructs a new conduit itself.

    Threading:
        - Idle deque operations follow the base pool's deque-first advisory
          policy.
        - Adds no extra shared mutable state beyond the root-conduit reference.

    Registration:
        MELDER KERNEL - guarded. Constructed and owned by one root `Conduit`;
        never user-bound.

    Subsystem Context:
        The conduit subsystem's lesser-conduit pool - a concrete
        `AbstractElasticPool` subclass owned by one root conduit. It holds the
        pool state (root reference + id) and hands back a retained lesser conduit
        when one is idle; it never constructs a conduit itself (creation stays
        with the conduit layer, so this is the reuse/retention seam only). It is
        currently a SCAFFOLD ahead of the full lesser-conduit acquire/release
        wiring.

    System Context:
        Pooling lesser conduits per root exists so repeated sub-conduit creation
        inside one root does not churn allocation - the same deque-first
        fixed-capacity policy the SpellSpace pool uses. Scoping the pool to the
        OWNING root rather than a global pool keeps a root's reused conduits
        inside its own lifecycle and cleanup boundary, so tearing down a root
        reclaims exactly its pooled lessers and nothing shared.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Root-conduit-owned elastic pool scaffold for reusable lesser conduits. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = AbstractElasticPool.__slots__ + [
        "_root_conduit",
        "_root_conduit_id",
    ]

    def __init__(
            self,
            *,
            root_conduit: Conduit,
            **kwargs: Any,
    ) -> None:
        """
        Initialize one root-owned conduit pool scaffold.

        Args:
            root_conduit:
                Root conduit that owns this pool.
            **kwargs:
                Elastic pool policy arguments forwarded to the base pool.

        Returns:
            None.
        """
        super().__init__(**kwargs)
        self._root_conduit: Conduit = root_conduit
        self._root_conduit_id: str = root_conduit._id

    @property
    def root_conduit(self) -> Conduit:
        """
        Return the root conduit that owns this pool.

        Returns:
            Conduit:
                Root conduit that created and owns this pool.
        """
        return self._root_conduit

    @property
    def root_conduit_id(self) -> str:
        """
        Return the stable owner root conduit id for this pool.

        Returns:
            str:
                Root conduit id captured during pool construction.
        """
        return self._root_conduit_id

    def create_object(self, *args: Any, **kwargs: Any) -> Optional[Conduit]:
        """
        Return one retained lesser conduit shell when available.

        Contract:
            - Reuses an idle lesser when available.
            - Returns `None` when the pool is empty.
            - Returns the lesser unattached so the caller still owns new-lesser
              creation, hook order, and lineage-link timing.
            - Uses one direct deque pop miss path instead of pre-checking idle
              state under an outer Python lock.
        """
        try:
            return self._idle.pop()
        except IndexError:
            return None

    def destroy_object(self, obj: Conduit) -> None:
        """
        Permanently destroy one pooled lesser conduit.

        Contract:
            - Uses the conduit hard-destroy lane.
            - Assumes the pooled conduit implements `permanent_cleanup()`.

        Returns:
            None.
        """
        obj.permanent_cleanup()

    def return_lesser_conduit(self, conduit: Conduit) -> None:
        """
        Return one lesser conduit shell to the idle pool or destroy it.

        Purpose:
            Support soft lesser cleanup before full pool-acquire wiring exists.

        Contract:
            - Assumes trusted private callers return each conduit at most once.
            - Appends the returned conduit first.
            - Retains the conduit while idle capacity remains at or below the
              current target.
            - Evicts one cold idle conduit with `popleft()` when retained
              capacity is exceeded.

        Returns:
            None.
        """
        self._idle.append(conduit)
        if len(self._idle) <= self._target_idle:
            return
        try:
            overflow_conduit = self._idle.popleft()
        except IndexError:
            return
        self.destroy_object(overflow_conduit)
