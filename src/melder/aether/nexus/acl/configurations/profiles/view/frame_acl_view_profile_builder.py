import threading
from typing import Dict, List

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.acl.configurations.profiles.view.hybrid_profile import (
    HybridViewProfileStrategy,
)
from melder.aether.nexus.acl.configurations.profiles.view.permissive_profile import (
    PermissiveViewProfileStrategy,
)
from melder.aether.nexus.acl.configurations.profiles.view.precision import (
    PrecisionViewProfileStrategy,
)
from melder.aether.nexus.acl.configurations.profiles.view.safe_profile import (
    SafeViewProfileStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iframeaclviewprofilestrategy import IFrameACLViewProfileStrategy


class FrameACLViewProfileBuilder(Cleanable):
    """
    Purpose:
        Own the reusable view-profile construction strategies and build view
        profile instances from them.

    Contract:
        - Owns strategy registration for the view family only.
        - `load_defaults()` registers the standard view preset strategies.
        - `build_profile(name)` returns a fresh configured view profile from the
          selected strategy.
        - Uses an instance lock because strategy registry mutation is grouped
          state in a nogil runtime.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one view profile strategy builder/registry.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._strategies_by_name: Dict[str, IFrameACLViewProfileStrategy] = {}
        self.load_defaults()

    def cleanup(self) -> None:
        """
        Idempotently clear the strategy registry.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._strategies_by_name.clear()
            del self._strategies_by_name
            del self._id
        del self._lock

    @property
    def id(self) -> str:
        """
        Return the stable builder identifier.
        """
        self.check_cleaned()
        return self._id

    def load_defaults(self) -> None:
        """
        Register the standard reusable view-profile strategies.

        Returns:
            None.
        """
        self.check_cleaned()
        self.register_strategy(SafeViewProfileStrategy())
        self.register_strategy(HybridViewProfileStrategy())
        self.register_strategy(PermissiveViewProfileStrategy())
        self.register_strategy(PrecisionViewProfileStrategy())

    def register_strategy(
            self,
            strategy: IFrameACLViewProfileStrategy,
    ) -> None:
        """
        Register or replace one view-profile construction strategy.

        Args:
            strategy:
                View-profile strategy to register.

        Returns:
            None.
        """
        self.check_cleaned()
        if strategy is None:
            raise TypeError("strategy cannot be None.")
        strategy_name = strategy.name
        if not strategy_name:
            raise ValueError("strategy.name cannot be empty.")
        with self._lock:
            self._strategies_by_name[strategy_name] = strategy

    def get_required_strategy(
            self,
            strategy_name: str,
    ) -> IFrameACLViewProfileStrategy:
        """
        Return one registered view-profile strategy or raise.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._strategies_by_name[strategy_name]
            except KeyError as exc:
                raise KeyError(strategy_name) from exc

    def list_strategy_names(self) -> List[str]:
        """
        Return registered strategy names in insertion order.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._strategies_by_name.keys())

    def build_profile(
            self,
            strategy_name: str,
    ) -> FrameACLViewProfile:
        """
        Build one fresh view profile instance from the named strategy.
        """
        self.check_cleaned()
        strategy = self.get_required_strategy(strategy_name)
        return strategy.build()
