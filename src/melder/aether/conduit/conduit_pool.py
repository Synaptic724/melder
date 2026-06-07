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
        - Inherits pool policy locking from `AbstractElasticPool`.
        - Adds no extra shared mutable state beyond the root-conduit reference.
    """

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
            - Skips generic diagnostic in-use bookkeeping because this trusted
              private fixed-capacity hot path does not use the generic elastic
              accounting contract.
        """
        with self._lock:
            if not self._enabled or not self._idle:
                return None
            return self._idle.pop()

    def destroy_object(self, obj: Conduit) -> None:
        """
        Permanently destroy one pooled lesser conduit.

        Contract:
            - Uses the conduit hard-destroy lane.
            - Assumes the pooled conduit implements `permanent_cleanup()`.
        """
        obj.permanent_cleanup()

    def return_lesser_conduit(self, conduit: Conduit) -> None:
        """
        Return one lesser conduit shell to the idle pool or destroy it.

        Purpose:
            Support soft lesser cleanup before full pool-acquire wiring exists.

        Contract:
            - Retains the conduit when idle capacity allows.
            - Destroys the conduit through the hard lane when the pool is
              disabled or already full.
            - Assumes trusted private callers return each conduit at most once.
            - Applies at most one decay step only when the idle list is already
              at the current retained limit.
            - Skips generic diagnostic in-use bookkeeping because this trusted
              private fixed-capacity hot path does not use the generic elastic
              accounting contract.
        """
        with self._lock:
            if self._enabled and len(self._idle) < self._target_idle:
                self._idle.append(conduit)
                return
            if self._enabled and not self._is_fixed_capacity_target_locked():
                now = self._time_func()
                self._apply_decay_once_locked(now)
                if self._enabled and len(self._idle) < self._target_idle:
                    self._idle.append(conduit)
                    return
            self.destroy_object(conduit)
