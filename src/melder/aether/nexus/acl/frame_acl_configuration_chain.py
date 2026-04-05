import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration


class FrameACLConfigurationChain(Cleanable):
    """
    Internal

    Linked history owner for one frame's ACL configuration nodes.

    Purpose:
        Provide one stable chain object that owns all ACL configuration nodes
        for a frame and exposes current/head/history mechanics independently of
        the builder and validator internals.

    Contract:
        - Owns all configuration nodes for the frame.
        - Starts with one default locked config as both head and current.
        - Supports head insertion, current selection, rollback, and tail trim.
        - Tail trim is the only delete behavior.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_name",
        "_history_limit",
        "_head_configuration_id",
        "_current_configuration_id",
        "_configurations_by_id",
    ]

    def __init__(
            self,
            frame_name: str,
            *,
            history_limit: int = 30,
    ) -> None:
        """
        Initialize one configuration chain with one default head/current config.

        Args:
            frame_name:
                Owning frame name.
            history_limit:
                Maximum number of configuration nodes retained in the chain.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")

        self._lock: threading.RLock = threading.RLock()
        self._frame_name: str = frame_name
        self._history_limit: int = history_limit
        self._configurations_by_id: Dict[str, FrameACLConfiguration] = {}

        default_configuration = FrameACLConfiguration.create_default(frame_name)
        default_configuration_id = default_configuration.configuration_id
        self._configurations_by_id[default_configuration_id] = default_configuration
        self._head_configuration_id: str = default_configuration_id
        self._current_configuration_id: str = default_configuration_id


    def cleanup(self) -> None:
        """
        Idempotently clear the chain and all owned configuration nodes.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for configuration in self._configurations_by_id.values():
                configuration.cleanup()
            self._configurations_by_id.clear()
            self._configurations_by_id = None
            self._frame_name = None
            self._history_limit = None
            self._head_configuration_id = None
            self._current_configuration_id = None
        self._lock = None


    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def history_limit(self) -> int:
        """
        Return the configured history limit.

        Returns:
            int: Maximum retained chain length.
        """
        self.check_cleaned()
        return self._history_limit

    @property
    def head_configuration_id(self) -> str:
        """
        Return the current head configuration id.

        Returns:
            str: Head configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._head_configuration_id

    @property
    def current_configuration_id(self) -> str:
        """
        Return the current selected configuration id.

        Returns:
            str: Current selected configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._current_configuration_id

    def has_configuration(self, configuration_id: str) -> bool:
        """
        Return whether the chain currently owns the given config id.

        Args:
            configuration_id:
                Config id to inspect.

        Returns:
            bool: True when the config exists.
        """
        self.check_cleaned()
        with self._lock:
            return configuration_id in self._configurations_by_id

    def get_head_configuration(self) -> FrameACLConfiguration:
        """
        Return the current head configuration node.

        Returns:
            FrameACLConfiguration: Head configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._head_configuration_id]

    def get_current_configuration(self) -> FrameACLConfiguration:
        """
        Return the currently selected configuration node.

        Returns:
            FrameACLConfiguration: Current configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._current_configuration_id]

    def get_configuration(self, configuration_id: str) -> FrameACLConfiguration:
        """
        Return one specific configuration node or raise.

        Args:
            configuration_id:
                Target config id.

        Returns:
            FrameACLConfiguration: Owned config node.

        Raises:
            KeyError: If the config id is not present.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._configurations_by_id[configuration_id]
            except KeyError as exc:
                raise KeyError(configuration_id) from exc

    def list_configurations(
            self,
            limit: Optional[int] = None,
    ) -> List[FrameACLConfiguration]:
        """
        Return the owned config nodes from newest to oldest.

        Args:
            limit:
                Optional maximum number of returned nodes.

        Returns:
            List[FrameACLConfiguration]: Ordered config-node list.
        """
        self.check_cleaned()
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise ValueError("limit must be an integer >= 1 when provided.")
        with self._lock:
            ordered_configurations: List[FrameACLConfiguration] = []
            next_configuration_id: Optional[str] = self._head_configuration_id
            while next_configuration_id is not None:
                configuration = self._configurations_by_id[next_configuration_id]
                ordered_configurations.append(configuration)
                if limit is not None and len(ordered_configurations) >= limit:
                    break
                next_configuration_id = configuration.previous_configuration_id
            return ordered_configurations

    def list_configuration_ids(
            self,
            limit: Optional[int] = None,
    ) -> List[str]:
        """
        Return owned config ids from newest to oldest.

        Args:
            limit:
                Optional maximum number of ids.

        Returns:
            List[str]: Ordered config id list.
        """
        self.check_cleaned()
        return [
            configuration.configuration_id
            for configuration in self.list_configurations(limit=limit)
        ]

    def count_configurations(self) -> int:
        """
        Return the number of owned config nodes.

        Returns:
            int: Number of owned config nodes.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._configurations_by_id)

    def insert_head_configuration(
            self,
            configuration: FrameACLConfiguration,
            *,
            select_as_current: bool,
    ) -> FrameACLConfiguration:
        """
        Insert a locked configuration node at the head of the chain.

        Args:
            configuration:
                Configuration node to insert.
            select_as_current:
                Whether the new head should also become current.

        Returns:
            FrameACLConfiguration: Inserted configuration node.
        """
        self.check_cleaned()
        if not isinstance(configuration, FrameACLConfiguration):
            raise TypeError("configuration must be a FrameACLConfiguration.")
        if configuration.frame_name != self._frame_name:
            raise ValueError(
                "FrameACLConfiguration targets frame '{0}', expected '{1}'.".format(
                    configuration.frame_name,
                    self._frame_name,
                )
            )
        if not configuration.locked:
            raise ValueError("Configuration must be locked before insertion.")

        with self._lock:
            configuration_id = configuration.configuration_id
            if configuration_id in self._configurations_by_id:
                raise ValueError(
                    "Configuration '{0}' already exists in the chain.".format(
                        configuration_id
                    )
                )
            previous_head_configuration_id = self._head_configuration_id
            configuration._previous_configuration_id = previous_head_configuration_id
            self._configurations_by_id[configuration_id] = configuration
            self._head_configuration_id = configuration_id
            if select_as_current:
                self._current_configuration_id = configuration_id
            self.trim_tail()
            return configuration

    def select_current_configuration(self, configuration_id: str) -> FrameACLConfiguration:
        """
        Select one existing configuration as current.

        Args:
            configuration_id:
                Config id to select as current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        with self._lock:
            configuration = self.get_configuration(configuration_id)
            self._current_configuration_id = configuration_id
            return configuration

    def rollback_to_configuration(self, configuration_id: str) -> FrameACLConfiguration:
        """
        Roll current selection back to one historical configuration.

        Args:
            configuration_id:
                Historical config id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current configuration.
        """
        self.check_cleaned()
        return self.select_current_configuration(configuration_id)

    def create_new_from_acl_configuration(
            self,
            configuration_id: str,
            *,
            reason: str,
    ) -> FrameACLConfiguration:
        """
        Create a new draft config copied from an existing config in the chain.

        Args:
            configuration_id:
                Source config id to copy from.
            reason:
                Human-readable creation reason.

        Returns:
            FrameACLConfiguration: New unlocked config copied from the source.
        """
        self.check_cleaned()
        source_configuration = self.get_configuration(configuration_id)
        return FrameACLConfiguration.create_new_from_acl_configuration(
            source_configuration,
            reason=reason,
        )

    def trim_tail(self) -> None:
        """
        Trim oldest tail nodes until the chain fits the history limit.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            while len(self._configurations_by_id) > self._history_limit:
                configuration_ids = self.list_configuration_ids()
                if len(configuration_ids) <= 1:
                    return
                tail_configuration_id = configuration_ids[-1]
                if tail_configuration_id == self._current_configuration_id:
                    return

                parent_configuration_id = None
                for configuration_id in configuration_ids[:-1]:
                    candidate_configuration = self._configurations_by_id[configuration_id]
                    if candidate_configuration.previous_configuration_id == tail_configuration_id:
                        parent_configuration_id = configuration_id
                        break

                tail_configuration = self._configurations_by_id.pop(
                    tail_configuration_id
                )
                tail_configuration.cleanup()

                if parent_configuration_id is not None:
                    parent_configuration = self._configurations_by_id[parent_configuration_id]
                    parent_configuration._previous_configuration_id = None