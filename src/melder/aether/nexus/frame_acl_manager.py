import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

from melder.aether.nexus.acl.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer


class FrameACLManager(Cleanable):
    """
    Purpose:
        Coordinate all frame-scoped ACL containers owned by one `Nexus`
        instance.

    Contract:
        - This manager is owned by `Nexus`; callers should not construct or
          share it independently.
        - The manager is the sole owner of the
          `frame_name -> FrameACLContainer` mapping.
        - Each frame name resolves to at most one live container at a time.
        - Container lookup, creation, removal, and snapshot reads are
          serialized through the manager lock.
        - The manager does not own descriptor state, compiled access surfaces,
          or viewer/codegen consumers; it only coordinates frame ACL
          containers and their chain-facing operations.

    Threading:
        Uses one instance `threading.RLock` to protect multi-step container-map
        reads and writes.

    Lifecycle:
        Cleanup is idempotent. Cleanup cascades into all owned containers
        before the manager drops its registry and lock references.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_frame_acl_containers_by_name",
    ]

    def __init__(self) -> None:
        """
        Initialize one empty frame ACL manager.

        Purpose:
            Construct the manager-owned container registry used by `Nexus` for
            frame-scoped ACL access.

        Contract:
            - Starts with no containers.
            - Creates the manager lock immediately so future container-map
              mutation is serialized from the beginning of the object's life.

        Returns:
            None.
        """
        super().__init__()
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._frame_acl_containers_by_name: Dict[str, FrameACLContainer] = {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup the manager and all owned containers.

        Purpose:
            Tear down the manager-owned frame ACL container registry in one
            deterministic pass.

        Contract:
            - Safe to call more than once.
            - Cleans each owned container before clearing the registry.
            - Leaves the manager unusable after completion.

        Threading:
            Acquires the manager lock so no other container-map mutation can
            interleave with teardown.

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

    @property
    def frame_acl_containers_by_name(self) -> Dict[str, FrameACLContainer]:
        """
        Return a snapshot of the manager-owned container registry.

        Purpose:
            Expose the current frame-to-container mapping for inspection
            without handing callers the live mutable registry.

        Contract:
            - Returns a shallow copy of the mapping.
            - The returned dictionary is detached from future manager writes.
            - Container objects inside the snapshot remain manager-owned.

        Returns:
            Dict[str, FrameACLContainer]:
                Snapshot of the frame-name keyed container registry.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._frame_acl_containers_by_name)

    def _ensure_frame_acl_container(
            self,
            frame_name: str,
    ) -> FrameACLContainer:
        """
        Return the frame ACL container for one frame, creating it if needed.

        Purpose:
            Provide the canonical frame-local ACL container lookup/creation path
            for all manager callers.

        Contract:
            - Creates at most one container per frame name.
            - Reuses the existing container when one is already registered.
            - Newly created containers start with their own default ACL chain,
              validator, and builder objects.

        Args:
            frame_name:
                Stable frame name that owns the target ACL container.

        Returns:
            FrameACLContainer:
                Existing or newly created frame ACL container for the frame.
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

        Purpose:
            Resolve a frame container only when absence is a real error instead
            of an invitation to create defaults.

        Contract:
            - Does not create missing containers.
            - Fails fast when the frame has no registered ACL container.

        Args:
            frame_name:
                Stable frame name whose ACL container must already exist.

        Returns:
            FrameACLContainer:
                Existing frame ACL container for the frame.

        Raises:
            KeyError:
                If the frame has no registered ACL container.
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

        Purpose:
            Provide the frame-scoped ACL authoring surface without exposing the
            container internals directly.

        Contract:
            - Ensures the frame container exists.
            - Returns the same builder object for repeated calls against the
              same frame.

        Args:
            frame_name:
                Stable frame name whose builder should be returned.

        Returns:
            FrameACLBuilder:
                The one builder object owned by the frame container.
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

        Purpose:
            Surface the chain-selected live ACL configuration for a frame
            through the manager boundary.

        Args:
            frame_name:
                Stable frame name whose current configuration is requested.

        Returns:
            FrameACLConfiguration:
                The currently selected ACL configuration for the frame.
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

        Purpose:
            Surface the newest committed ACL configuration node for a frame
            through the manager boundary.

        Args:
            frame_name:
                Stable frame name whose head configuration is requested.

        Returns:
            FrameACLConfiguration:
                The head ACL configuration node for the frame.
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

        Purpose:
            Resolve one historical or current ACL configuration node by id for a
            frame-scoped chain.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            configuration_id:
                Target configuration id inside the chain.

        Returns:
            FrameACLConfiguration:
                Requested configuration node.

        Raises:
            KeyError:
                If the frame exists but the configuration id is not present in
                its chain.
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

        Purpose:
            Provide an ordered history view over a frame's ACL configuration
            chain.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            limit:
                Optional maximum number of returned configuration nodes.

        Returns:
            List[FrameACLConfiguration]:
                Ordered configuration-node list from newest to oldest.
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

        Purpose:
            Provide a lightweight ordered history view without exposing the full
            configuration nodes.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            limit:
                Optional maximum number of returned ids.

        Returns:
            List[str]:
                Ordered configuration id list from newest to oldest.
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

        Purpose:
            Validate and commit a new configuration node into the frame's
            history chain through the manager boundary.

        Args:
            frame_name:
                Stable frame name that owns the target chain.
            configuration:
                Locked configuration node to commit.
            select_as_current:
                True when the inserted head should also become the current
                selected configuration.

        Returns:
            FrameACLConfiguration:
                Inserted configuration node.

        Raises:
            TypeError, ValueError:
                Propagated when validation fails or the chain rejects the node.
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

        Purpose:
            Move the frame's current configuration pointer without creating a
            new configuration node.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            configuration_id:
                Existing configuration id to make current.

        Returns:
            FrameACLConfiguration:
                Newly selected current configuration.
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

        Purpose:
            Provide a semantic rollback entrypoint over the underlying
            current-selection mechanics.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            configuration_id:
                Historical configuration id to restore as current.

        Returns:
            FrameACLConfiguration:
                Newly selected current configuration.
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

        Purpose:
            Seed a new draft configuration from one existing node in the
            frame-scoped history chain.

        Args:
            frame_name:
                Stable frame name that owns the configuration chain.
            configuration_id:
                Source configuration id to copy from.
            reason:
                Human-readable reason recorded on the new draft node.

        Returns:
            FrameACLConfiguration:
                New unlocked configuration copied from the source node.
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

        Purpose:
            Tear down a frame container when the frame-level ACL subsystem
            should no longer exist for that frame.

        Contract:
            - Removes the container from the manager registry first.
            - Cleans the container before returning.
            - Returns False when the frame never had a registered container.

        Args:
            frame_name:
                Stable frame name whose container should be removed.

        Returns:
            bool:
                True when a container existed and was removed; otherwise False.
        """
        self.check_cleaned()
        with self._lock:
            container = self._frame_acl_containers_by_name.pop(frame_name, None)
            if container is None:
                return False
            container.cleanup()
            return True
