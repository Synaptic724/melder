from typing import TYPE_CHECKING, Any, ClassVar

from melder.__melder_registration_guard__ import (
    __melder_registration_guard__ as _mrg,
)
from melder.aether.conduit.spell_space.spell_space import SpellSpace
from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.conduit.meld.meld import Meld


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
        "_creations",
        "_meld",
        "_owner_conduit_id",
        "_spellspace_registry",
    ]

    def __init__(
            self,
            *,
            owner_conduit_id: str,
            meld: Meld,
            creations: Creations,
            spellspace_registry: set[SpellSpace],
            **kwargs: Any,
    ) -> None:
        """
        Initialize one conduit-local spellspace pool.

        Args:
            owner_conduit_id:
                Stable owner conduit id for pooled spellspaces.
            meld:
                Meld runtime used by pooled spellspaces.
            creations:
                Creations manager used by pooled spellspaces.
            spellspace_registry:
                Conduit-owned registry used for spellspace bookkeeping.
            **kwargs:
                Elastic pool policy arguments forwarded to the base pool.
        """
        super().__init__(**kwargs)
        self._owner_conduit_id: str = owner_conduit_id
        self._meld: Meld = meld
        self._creations: Creations = creations
        self._spellspace_registry: set[SpellSpace] = spellspace_registry

    def create_object(self, *args: Any, **kwargs: Any) -> SpellSpace:
        """
        Create one new spellspace owned by this pool's conduit runtime.
        """
        return SpellSpace(
            owner_conduit_id=self._owner_conduit_id,
            meld=self._meld,
            creations=self._creations,
            spellspace_registry=self._spellspace_registry,
            spellspace_pool=self,
        )

    def prepare_object(
            self,
            obj: SpellSpace,
            *args: Any,
            **kwargs: Any,
    ) -> SpellSpace:
        """
        Reactivate one spellspace before use.
        """
        obj._spellspace_registry.add(obj)
        return obj

    def destroy_object(self, obj: SpellSpace) -> None:
        """
        Permanently destroy one spellspace that should not be retained.
        """
        obj.permanent_cleanup()

    def release(self, obj: SpellSpace) -> None:
        """
        Return one spellspace to idle storage or destroy it.

        Contract:
            - Uses the same simplified private-pool release policy as
              `ConduitPool`.
            - Assumes trusted private callers do not double-return the same
              spellspace shell.
            - Applies at most one decay step only when the idle list is already
              at the current retained limit.
        """
        with self._lock:
            if self._in_use_count > 0:
                self._in_use_count -= 1
            if self._enabled and len(self._idle) < self._target_idle:
                self._idle.append(obj)
                return
            if self._enabled:
                now = self._time_func()
                self._apply_decay_once_locked(now)
                if len(self._idle) < self._target_idle:
                    self._idle.append(obj)
                    return
            self.destroy_object(obj)
