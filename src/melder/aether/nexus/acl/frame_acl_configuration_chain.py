import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.utilities.helpers.id_builder import IDBuilder


class FrameACLConfigurationChain(Cleanable):
    """
    Purpose:
        Own the complete ACL configuration history for one frame.

    Contract:
        - The chain is the only owner of configuration nodes once they are
          committed.
        - Construction seeds one default locked configuration as both the head
          and current node.
        - New committed nodes insert at the head.
        - Current selection may diverge from head during rollback or staged
          activation flows.
        - Tail trimming is the only delete path; arbitrary deletion is not
          part of the chain contract.

    Threading:
        Uses one instance `threading.RLock` to serialize head/current/history
        mutation and ordered traversal.

    Lifecycle:
        Cleanup is idempotent and cascades into every owned configuration node
        before the chain drops its indexes and lock.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
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

        Purpose:
            Create the per-frame configuration-history owner and seed it with
            the required default configuration node.

        Contract:
            - `frame_name` must be non-empty.
            - `history_limit` must allow at least one retained node.
            - The default node is immediately owned by the chain and is both
              head and current.

        Args:
            frame_name:
                Stable frame name that owns this chain.
            history_limit:
                Maximum number of configuration nodes retained by the chain.

        Returns:
            None.

        Raises:
            ValueError:
                If `frame_name` is empty or `history_limit` is less than 1.
            TypeError:
                If `history_limit` is not an integer.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")
        self._id: str = IDBuilder.create_id()
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

        Purpose:
            Tear down the configuration-history owner and each committed node it
            owns.

        Contract:
            - Safe to call more than once.
            - Cleans every owned configuration before clearing indexes.
            - Leaves the chain unusable after completion.

        Threading:
            Acquires the chain lock so teardown does not race with list/select/
            insert operations.

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

        Purpose:
            Expose the stable frame identity that anchors this chain.

        Returns:
            str: Owning frame name.
        """
        self.check_cleaned()
        return self._frame_name

    @property
    def history_limit(self) -> int:
        """
        Return the configured history limit.

        Purpose:
            Expose the maximum retained node count enforced by tail trimming.

        Returns:
            int: Maximum retained chain length.
        """
        self.check_cleaned()
        return self._history_limit

    @property
    def head_configuration_id(self) -> str:
        """
        Return the current head configuration id.

        Purpose:
            Expose the newest committed configuration id in the chain.

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

        Purpose:
            Expose the configuration id currently treated as active by the
            frame-local ACL subsystem.

        Returns:
            str: Current selected configuration id.
        """
        self.check_cleaned()
        with self._lock:
            return self._current_configuration_id

    def has_configuration(self, configuration_id: str) -> bool:
        """
        Return whether the chain currently owns the given config id.

        Purpose:
            Provide a lightweight existence check without materializing the
            configuration node.

        Args:
            configuration_id:
                Configuration id to inspect.

        Returns:
            bool: True when the config exists.
        """
        self.check_cleaned()
        with self._lock:
            return configuration_id in self._configurations_by_id

    def get_head_configuration(self) -> FrameACLConfiguration:
        """
        Return the current head configuration node.

        Purpose:
            Resolve the newest committed configuration node.

        Returns:
            FrameACLConfiguration: Head configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._head_configuration_id]

    def get_current_configuration(self) -> FrameACLConfiguration:
        """
        Return the currently selected configuration node.

        Purpose:
            Resolve the configuration node currently selected as active.

        Returns:
            FrameACLConfiguration: Current configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._current_configuration_id]

    def get_configuration(self, configuration_id: str) -> FrameACLConfiguration:
        """
        Return one specific configuration node or raise.

        Purpose:
            Resolve one owned configuration node by id.

        Args:
            configuration_id:
                Target configuration id.

        Returns:
            FrameACLConfiguration: Owned config node.

        Raises:
            KeyError:
                If the configuration id is not present in the chain.
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

        Purpose:
            Walk the chain in chronological head-to-tail order for history
            inspection.

        Contract:
            - Traversal follows `previous_configuration_id`, not dictionary
              insertion order.
            - Returned nodes remain chain-owned.

        Args:
            limit:
                Optional maximum number of returned configuration nodes.

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

        Purpose:
            Provide a lightweight ordered chain view without exposing node
            objects.

        Args:
            limit:
                Optional maximum number of returned ids.

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

        Purpose:
            Expose the current chain size for validation and history control.

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

        Purpose:
            Commit a new configuration node into the chain as the newest known
            state.

        Contract:
            - Rejects non-configuration inputs.
            - Rejects nodes for another frame.
            - Rejects unlocked nodes and duplicate ids.
            - Rewrites the new node's previous pointer to the old head.
            - Trims the tail after insertion when the history limit is
              exceeded.

        Args:
            configuration:
                Locked configuration node to insert.
            select_as_current:
                True when the new head should also become the current selected
                node.

        Returns:
            FrameACLConfiguration: Inserted configuration node.

        Raises:
            TypeError:
                If `configuration` is not a `FrameACLConfiguration`.
            ValueError:
                If the configuration targets another frame, is unlocked, or is
                already present in the chain.
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

        Purpose:
            Move the chain's current pointer without changing head order.

        Args:
            configuration_id:
                Existing configuration id to select as current.

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

        Purpose:
            Provide a semantic rollback entrypoint over current-pointer
            selection.

        Args:
            configuration_id:
                Historical configuration id to restore as current.

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

        Purpose:
            Seed a new unlocked configuration node from a known chain state
            without inserting it yet.

        Args:
            configuration_id:
                Source configuration id to copy from.
            reason:
                Human-readable reason recorded on the new draft node.

        Returns:
            FrameACLConfiguration: New unlocked config copied from the source.

        Raises:
            KeyError:
                If the source configuration id is not present in the chain.
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

        Purpose:
            Enforce bounded history retention without disturbing head order.

        Contract:
            - Removes only oldest tail nodes.
            - Never trims the current node.
            - Stops early when trimming would require deleting the current node.

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
