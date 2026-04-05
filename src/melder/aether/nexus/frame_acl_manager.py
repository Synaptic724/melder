import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


class FrameACLManager(Cleanable):
    """
    Internal

    Nexus-owned coordinator for frame-scoped ACL containers.

    Purpose:
        Own the per-frame ACL containers and provide the root coordination
        point for frame-scoped ACL access without pushing ACL history/builder
        objects directly into the descriptor.

    Contract:
        - Owned by `Nexus`.
        - Owns `frame_name -> FrameACLContainer`.
        - Ensures each frame has at most one container.
        - Facades current/head/list/select/rollback mechanics for the
          underlying chain per frame.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_frame_acl_containers_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one Nexus-owned frame ACL manager.
        """
        super().__init__()
        self._lock: threading.RLock = threading.RLock()
        self._frame_acl_containers_by_name: Dict[str, FrameACLContainer] = {}

    @property
    def frame_acl_containers_by_name(self) -> Dict[str, FrameACLContainer]:
        """
        Return a snapshot of the manager-owned frame ACL containers.

        Returns:
            Dict[str, FrameACLContainer]: Snapshot of container mapping.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._frame_acl_containers_by_name)

    def _ensure_frame_acl_container(
            self,
            frame_name: str,
    ) -> FrameACLContainer:
        """
        Return the frame ACL container for one frame, creating it if missing.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLContainer: Existing or newly created frame ACL container.
        """
        self.check_cleaned()
        with self._lock:
            container = self._frame_acl_containers_by_name.get(frame_name)
            if container is None:
                container = FrameACLContainer(frame_name)
                self._frame_acl_containers_by_name[frame_name] = container
            return container

    def _get_required_frame_acl_container(
            self,
            frame_name: str,
    ) -> FrameACLContainer:
        """
        Return one existing frame ACL container or raise.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLContainer: Existing frame ACL container.

        Raises:
            KeyError: If no container exists for the frame.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._frame_acl_containers_by_name[frame_name]
            except KeyError as exc:
                raise KeyError(frame_name) from exc

    def _get_or_create_frame_acl_builder(
            self,
            frame_name: str,
    ) -> FrameACLBuilder:
        """
        Return the unique builder object for one frame.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLBuilder: Unique builder object for the frame container.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_builder

    def _get_current_frame_acl_configuration(
            self,
            frame_name: str,
    ) -> FrameACLConfiguration:
        """
        Return the current selected ACL configuration for one frame.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLConfiguration: Current config for the frame.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.get_current_configuration()

    def _get_head_frame_acl_configuration(
            self,
            frame_name: str,
    ) -> FrameACLConfiguration:
        """
        Return the head ACL configuration for one frame.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            FrameACLConfiguration: Head config for the frame.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.get_head_configuration()

    def _get_frame_acl_configuration(
            self,
            frame_name: str,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Return one specific ACL configuration node for a frame.

        Args:
            frame_name:
                Owning frame name.
            configuration_id:
                Target config id.

        Returns:
            FrameACLConfiguration: Requested config node.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.get_configuration(
            configuration_id
        )

    def _list_frame_acl_configurations(
            self,
            frame_name: str,
            limit: Optional[int] = None,
    ) -> List[FrameACLConfiguration]:
        """
        Return ACL configurations for one frame from newest to oldest.

        Args:
            frame_name:
                Owning frame name.
            limit:
                Optional maximum count.

        Returns:
            List[FrameACLConfiguration]: Ordered config-node list.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.list_configurations(
            limit=limit
        )

    def _list_frame_acl_configuration_ids(
            self,
            frame_name: str,
            limit: Optional[int] = None,
    ) -> List[str]:
        """
        Return ACL configuration ids for one frame from newest to oldest.

        Args:
            frame_name:
                Owning frame name.
            limit:
                Optional maximum count.

        Returns:
            List[str]: Ordered config id list.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.list_configuration_ids(
            limit=limit
        )

    def _insert_head_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            select_as_current: bool,
    ) -> FrameACLConfiguration:
        """
        Insert one locked ACL config at the head of the frame chain.

        Args:
            frame_name:
                Owning frame name.
            configuration:
                Config node to insert.
            select_as_current:
                Whether the new head should also become current.

        Returns:
            FrameACLConfiguration: Inserted config node.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        container.frame_acl_validator.validate_configuration(configuration)
        return container.frame_acl_configuration_chain.insert_head_configuration(
            configuration,
            select_as_current=select_as_current,
        )

    def _select_current_frame_acl_configuration(
            self,
            frame_name: str,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Select one existing config as current for a frame.

        Args:
            frame_name:
                Owning frame name.
            configuration_id:
                Config id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current config.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.select_current_configuration(configuration_id)

    def _rollback_frame_acl_configuration(
            self,
            frame_name: str,
            configuration_id: str,
    ) -> FrameACLConfiguration:
        """
        Roll current selection back to one historical config for a frame.

        Args:
            frame_name:
                Owning frame name.
            configuration_id:
                Historical config id to make current.

        Returns:
            FrameACLConfiguration: Newly selected current config.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.rollback_to_configuration(configuration_id)

    def _create_new_from_acl_configuration(
            self,
            frame_name: str,
            configuration_id: str,
            *,
            reason: str,
    ) -> FrameACLConfiguration:
        """
        Create a new draft config copied from an existing config in the frame
        chain.

        Args:
            frame_name:
                Owning frame name.
            configuration_id:
                Source config id.
            reason:
                Human-readable creation reason.

        Returns:
            FrameACLConfiguration: New unlocked config copied from the source.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_configuration_chain.create_new_from_acl_configuration(
            configuration_id,
            reason=reason,
        )

    def _remove_frame_acl_container(self, frame_name: str) -> bool:
        """
        Remove and cleanup one frame ACL container by frame name.

        Args:
            frame_name:
                Owning frame name.

        Returns:
            bool: True when a container existed and was removed, otherwise
            False.
        """
        self.check_cleaned()
        with self._lock:
            container = self._frame_acl_containers_by_name.pop(frame_name, None)
            if container is None:
                return False
            container.cleanup()
            return True

    def cleanup(self) -> None:
        """
        Idempotently clear the manager and all owned containers.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            for container in self._frame_acl_containers_by_name.values():
                container.cleanup()
            self._frame_acl_containers_by_name.clear()
            self._frame_acl_containers_by_name = None
        self._lock = None
