from typing import TYPE_CHECKING, Any, ClassVar

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
        - Does not perform real lesser-conduit reuse yet.
        - `create_object(...)` and `destroy_object(...)` are explicit
          placeholders until the later wiring slice lands.

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

    def create_object(self, *args: Any, **kwargs: Any) -> Conduit:
        """
        Placeholder lesser-conduit creation hook.

        Raises:
            NotImplementedError:
                Always, until real lesser-conduit acquire wiring is added.
        """
        raise NotImplementedError(
            "ConduitPool.create_object() is not wired yet."
        )

    def destroy_object(self, obj: Conduit) -> None:
        """
        Permanently destroy one pooled lesser conduit.

        Contract:
            - Uses the conduit hard-destroy lane.
            - Assumes the pooled conduit implements `permanent_cleanup()`.
        """
        obj.permanent_cleanup()
