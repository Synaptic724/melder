import threading
from typing import Dict, List, Union

from melder.nexus.acl.configurations.profiles.command.frame_acl_command_profile import (
    FrameACLCommandProfile,
)
from melder.nexus.acl.configurations.profiles.command.hybrid_profile import (
    HybridCommandProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.command.permissive_profile import (
    PermissiveCommandProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.command.precision import (
    PrecisionCommandProfileStrategy,
)
from melder.nexus.acl.configurations.profiles.command.safe_profile import (
    SafeCommandProfileStrategy,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
CommandProfileStrategy = Union[
    SafeCommandProfileStrategy,
    HybridCommandProfileStrategy,
    PermissiveCommandProfileStrategy,
    PrecisionCommandProfileStrategy,
]


class FrameACLCommandProfileBuilder(Cleanable):
    """

    Purpose:
        Own the reusable command-profile construction strategies and build
        command profile instances from them.

    Contract:
        - Owns strategy registration for the command family only.
        - `load_defaults()` registers the standard command preset strategies.
        - `build_profile(name)` returns a fresh configured command profile from
          the selected strategy.
        - Uses an instance lock because strategy registry mutation is grouped
          state in a nogil runtime.

    Threading:
        One instance lock; strategy-registry mutation is grouped state under a
        nogil runtime.

    Registration:
        MELDER KERNEL - guarded. Manager-owned; reached through the ACL layer.

    Subsystem Context:
        The strategy registry for the command family only. Its two siblings own
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

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. FrameACLCommandProfileBuilder runtime object. Melder kernel machinery:
        read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_strategies_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one command profile strategy builder/registry.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._strategies_by_name: Dict[str, CommandProfileStrategy] = {}
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
        Register the standard reusable command-profile strategies.

        Returns:
            None.
        """
        self.check_cleaned()
        self.register_strategy(SafeCommandProfileStrategy())
        self.register_strategy(HybridCommandProfileStrategy())
        self.register_strategy(PermissiveCommandProfileStrategy())
        self.register_strategy(PrecisionCommandProfileStrategy())

    def register_strategy(
            self,
            strategy: CommandProfileStrategy,
    ) -> None:
        """
        Register or replace one command-profile construction strategy.

        Args:
            strategy:
                Command-profile strategy to register.

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
    ) -> CommandProfileStrategy:
        """
        Return one registered command-profile strategy or raise.

        Args:
            strategy_name: Registered strategy name to fetch.

        Returns:
            CommandProfileStrategy: The registered strategy.

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
    ) -> FrameACLCommandProfile:
        """
        Build one fresh command profile instance from the named strategy.

        Args:
            strategy_name: Registered strategy name whose `build()` runs.

        Returns:
            FrameACLCommandProfile: A freshly built command profile.

        Raises:
            KeyError: If no strategy is registered under that name.
        """
        self.check_cleaned()
        strategy = self.get_required_strategy(strategy_name)
        return strategy.build()
