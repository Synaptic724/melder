import threading
from typing import Dict, List, Union

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
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
    """

    __melder_internal__ = _mrg.sentinel
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
        """
        self.check_cleaned()
        strategy = self.get_required_strategy(strategy_name)
        return strategy.build()
