import threading
from typing import Dict, List, Optional, Union
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iframeaclcodegenconfiguration import (
    FrameACLCodegenConfiguration,
)
from melder.utilities.interfaces.iframeaclcommandconfiguration import (
    FrameACLCommandConfiguration,
)
from melder.utilities.interfaces.iframeaclviewconfiguration import (
    FrameACLViewConfiguration,
)

ACLFamilyConfiguration = Union[
    FrameACLViewConfiguration,
    FrameACLCommandConfiguration,
    FrameACLCodegenConfiguration,
]


class FrameACLConfigurationChain(Cleanable):
    """
    Purpose:
        Own one named revision chain for one ACL configuration family.

    Contract:
        - The chain owns one family/name lineage, not the whole frame ACL
          bundle.
        - Construction requires one default locked configuration node that
          becomes both head and current.
        - New committed nodes insert at the head.
        - Current selection may diverge from head during rollback or staged
          activation flows.
        - Tail trimming is the only delete path; arbitrary deletion is not part
          of the chain contract.

    Threading:
        Uses one instance `threading.RLock` to serialize head/current/history
        mutation and ordered traversal.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_family_name",
        "_contract_name",
        "_history_limit",
        "_head_configuration_id",
        "_current_configuration_id",
        "_configurations_by_id",
    ]

    def __init__(
            self,
            *,
            family_name: str,
            contract_name: str,
            default_configuration: ACLFamilyConfiguration,
            history_limit: int = 30,
    ) -> None:
        """
        Initialize one family/name configuration chain.

        Args:
            family_name:
                ACL family name such as `view`, `command`, or `codegen`.
            contract_name:
                Named contract within that family.
            default_configuration:
                Initial locked configuration node to seed the chain.
            history_limit:
                Maximum number of retained revisions.

        Returns:
            None.
        """
        super().__init__()
        if not family_name:
            raise ValueError("family_name cannot be empty.")
        if not contract_name:
            raise ValueError("contract_name cannot be empty.")
        if not isinstance(history_limit, int) or history_limit < 1:
            raise ValueError("history_limit must be an integer >= 1.")
        self._validate_revision_payload(default_configuration)
        if not default_configuration.locked:
            raise ValueError("default_configuration must be locked.")

        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._family_name: str = family_name
        self._contract_name: str = contract_name
        self._history_limit: int = history_limit
        self._configurations_by_id: Dict[str, ACLFamilyConfiguration] = {}

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

            del self._configurations_by_id
            del self._family_name
            del self._contract_name
            del self._history_limit
            del self._head_configuration_id
            del self._current_configuration_id
        del self._lock

    @property
    def family_name(self) -> str:
        """
        Return the owning ACL family name.

        Returns:
            str: ACL family name.
        """
        self.check_cleaned()
        return self._family_name

    @property
    def contract_name(self) -> str:
        """
        Return the owning contract name.

        Returns:
            str: Named contract name.
        """
        self.check_cleaned()
        return self._contract_name

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
                Configuration id to inspect.

        Returns:
            bool: True when the config exists.
        """
        self.check_cleaned()
        with self._lock:
            return configuration_id in self._configurations_by_id

    def get_head_configuration(self) -> ACLFamilyConfiguration:
        """
        Return the current head configuration node.

        Returns:
            Any: Head configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._head_configuration_id]

    def get_current_configuration(self) -> ACLFamilyConfiguration:
        """
        Return the currently selected configuration node.

        Returns:
            Any: Current configuration node.
        """
        self.check_cleaned()
        with self._lock:
            return self._configurations_by_id[self._current_configuration_id]

    def get_configuration(self, configuration_id: str) -> ACLFamilyConfiguration:
        """
        Return one specific configuration node or raise.

        Args:
            configuration_id:
                Target configuration id.

        Returns:
            Any: Owned configuration node.
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
    ) -> List[ACLFamilyConfiguration]:
        """
        Return the owned config nodes from newest to oldest.

        Args:
            limit:
                Optional maximum number of returned configuration nodes.

        Returns:
            List[Any]: Ordered configuration-node list.
        """
        self.check_cleaned()
        if limit is not None and (not isinstance(limit, int) or limit < 1):
            raise ValueError("limit must be an integer >= 1 when provided.")
        with self._lock:
            ordered_configurations: List[ACLFamilyConfiguration] = []
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

        Returns:
            int: Number of owned config nodes.
        """
        self.check_cleaned()
        with self._lock:
            return len(self._configurations_by_id)

    def insert_head_configuration(
            self,
            configuration: ACLFamilyConfiguration,
            *,
            select_as_current: bool,
    ) -> ACLFamilyConfiguration:
        """
        Insert a locked configuration node at the head of the chain.

        Args:
            configuration:
                Locked configuration node to insert.
            select_as_current:
                True when the new head should also become the current node.

        Returns:
            Any: Inserted configuration node.
        """
        self.check_cleaned()
        self._validate_revision_payload(configuration)
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
            configuration.finalize()
            self._configurations_by_id[configuration_id] = configuration
            self._head_configuration_id = configuration_id
            if select_as_current:
                self._current_configuration_id = configuration_id
            self.trim_tail()
            return configuration

    def select_current_configuration(self, configuration_id: str) -> ACLFamilyConfiguration:
        """
        Select one existing configuration as current.

        Args:
            configuration_id:
                Existing configuration id to select as current.

        Returns:
            Any: Newly selected current configuration.
        """
        self.check_cleaned()
        with self._lock:
            configuration = self.get_configuration(configuration_id)
            self._current_configuration_id = configuration_id
            return configuration

    def rollback_to_configuration(self, configuration_id: str) -> ACLFamilyConfiguration:
        """
        Roll current selection back to one historical configuration.

        Args:
            configuration_id:
                Historical configuration id to restore as current.

        Returns:
            Any: Newly selected current configuration.
        """
        self.check_cleaned()
        return self.select_current_configuration(configuration_id)

    def create_new_from_acl_configuration(
            self,
            configuration_id: str,
            *,
            reason: str,
    ) -> ACLFamilyConfiguration:
        """
        Create a new draft config copied from an existing config in the chain.

        Args:
            configuration_id:
                Source configuration id to copy from.
            reason:
                Human-readable reason recorded on the new draft node.

        Returns:
            Any: New unlocked configuration copied from the source.
        """
        self.check_cleaned()
        source_configuration = self.get_configuration(configuration_id)
        return type(source_configuration).create_new_from_configuration(
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

    @staticmethod
    def _validate_revision_payload(configuration: Any) -> None:
        """
        Validate that the incoming config object supports chain semantics.

        Args:
            configuration:
                Candidate configuration node.

        Returns:
            None.
        """
        required_attributes = (
            "configuration_id",
            "previous_configuration_id",
            "locked",
            "set_previous_configuration_id",
            "finalize",
            "cleanup",
        )
        for attribute_name in required_attributes:
            if not hasattr(configuration, attribute_name):
                raise TypeError(
                    "configuration must support '{0}' for chain ownership.".format(
                        attribute_name
                    )
                )
