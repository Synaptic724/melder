import threading
from typing import Dict, List, Union

from melder.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.nexus.acl.configurations.profiles.view.hybrid_profile import (
    HybridViewProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.view.permissive_profile import (
    PermissiveViewProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.view.precision import (
    PrecisionViewProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.view.safe_profile import (
    SafeViewProfileStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
ViewProfileStrategy = Union[
    SafeViewProfileStrategy,
    HybridViewProfileStrategy,
    PermissiveViewProfileStrategy,
    PrecisionViewProfileStrategy,
]


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

    Threading:
        One instance lock; strategy-registry mutation is grouped state under a
        nogil runtime.

    Registration:
        MELDER KERNEL - guarded. Manager-owned; reached through the ACL layer.

    Subsystem Context:
        The strategy registry for the view family only. Its two siblings own
        the other families, and the deliberate separation means a family can
        gain a preset without touching the others.

    System Context:
        `build_profile(name)` returns a FRESH profile per call rather than a
        shared instance, and that matters because the applied configuration
        that references a profile owns detached rulesets - handing out one
        shared mutable profile would let one frame's authoring perturb another's
        effective policy.
        Registering presets through `load_defaults()` rather than hardcoding
        them keeps the catalog extensible: a deployment can add a posture
        without forking the builder, which is the same registered-strategy
        pattern the transaction and information families use.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. FrameACLViewProfileBuilder runtime object. Melder kernel machinery: "
        "read it to understand the runtime, do not drive it directly."
    )

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
        self._strategies_by_name: Dict[str, ViewProfileStrategy] = {}
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
            strategy: ViewProfileStrategy,
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
    ) -> ViewProfileStrategy:
        """
        Return one registered view-profile strategy or raise.

        Args:
            strategy_name: Registered strategy name to fetch.

        Returns:
            ViewProfileStrategy: The registered strategy.

        Raises:
            KeyError: If no strategy is registered under that name.
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

        Args:
            strategy_name: Registered strategy name whose `build()` runs.

        Returns:
            FrameACLViewProfile: A freshly built view profile.

        Raises:
            KeyError: If no strategy is registered under that name.
        """
        self.check_cleaned()
        strategy = self.get_required_strategy(strategy_name)
        return strategy.build()
