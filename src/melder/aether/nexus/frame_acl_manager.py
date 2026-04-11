import threading
from typing import Callable, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

from melder.aether.nexus.acl.builder.frame_acl_builder import FrameACLBuilder
from melder.aether.nexus.acl.configurations.frame_acl_command_configuration import (
    FrameACLCommandConfiguration,
)
from melder.aether.nexus.acl.frame_acl_configuration import FrameACLConfiguration
from melder.aether.nexus.acl.frame_acl_container import FrameACLContainer
from melder.aether.nexus.acl.configurations.frame_acl_codegen_configuration import (
    FrameACLCodegenConfiguration,
)
from melder.aether.nexus.acl.configurations.frame_acl_view_configuration import (
    FrameACLViewConfiguration,
)
from melder.aether.nexus.acl.configurations.profiles.codegen.frame_acl_codegen_profile import (
    FrameACLCodegenProfile,
)
from melder.aether.nexus.acl.configurations.profiles.frame_acl_profile import (
    FrameACLProfile,
)
from melder.aether.nexus.acl.configurations.profiles.builder.frame_acl_profile_builder import (
    FrameACLProfileBuilder,
)
from melder.aether.nexus.acl.configurations.profiles.view.frame_acl_view_profile import (
    FrameACLViewProfile,
)
from melder.aether.nexus.frame_descriptor.frame_descriptor import FrameDescriptor


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
        "_version",
        "_change_callback",
        "_frame_acl_profile_builder",
        "_frame_acl_containers_by_name",
        "_frame_acl_profiles_by_name",
    ]

    def __init__(
            self,
            *,
            change_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
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
        self._version: str = "0.0.1"
        self._change_callback: Optional[Callable[[str], None]] = change_callback
        self._frame_acl_profile_builder: FrameACLProfileBuilder = (
            FrameACLProfileBuilder()
        )
        self._frame_acl_containers_by_name: Dict[str, FrameACLContainer] = {}
        self._frame_acl_profiles_by_name: Dict[str, FrameACLProfile] = {}

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
            for frame_acl_profile in self._frame_acl_profiles_by_name.values():
                frame_acl_profile.cleanup()
            self._frame_acl_profile_builder.cleanup()
            self._frame_acl_containers_by_name.clear()
            self._frame_acl_profiles_by_name.clear()
            self._change_callback = None
            self._frame_acl_profile_builder = None
            self._frame_acl_containers_by_name = None
            self._frame_acl_profiles_by_name = None
            self._version = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable manager identifier.

        Returns:
            str: Stable manager id.
        """
        self.check_cleaned()
        return self._id

    @property
    def version(self) -> str:
        """
        Return the current placeholder ACL manager version string.

        Returns:
            str: Current ACL manager version.
        """
        self.check_cleaned()
        return self._version

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

    @property
    def frame_acl_profiles_by_name(self) -> Dict[str, FrameACLProfile]:
        """
        Return a snapshot of the manager-owned ACL profile registry.

        Contract:
            - Returns a shallow copy of the mapping.
            - The returned dictionary is detached from future manager writes.
            - Profile objects inside the snapshot remain manager-owned.

        Returns:
            Dict[str, FrameACLProfile]:
                Snapshot of the profile-name keyed registry.
        """
        self.check_cleaned()
        with self._lock:
            return dict(self._frame_acl_profiles_by_name)

    @property
    def frame_acl_profile_builder(self) -> FrameACLProfileBuilder:
        """
        Return the manager-owned ACL profile builder/library.

        Contract:
            Returns the live manager-owned builder object, not a detached copy.

        Returns:
            FrameACLProfileBuilder: Manager-owned ACL profile builder/library.
        """
        self.check_cleaned()
        return self._frame_acl_profile_builder

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
                container = FrameACLContainer(
                    frame_name,
                    profile_builder=self._frame_acl_profile_builder,
                    change_callback=self._change_callback,
                )
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
            *,
            view_contract_name: str = "default",
            command_contract_name: str = "default",
            codegen_contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return one assembled ACL snapshot for the selected family contracts.

        Args:
            frame_name:
                Stable frame name whose selected ACL snapshot is requested.
            view_contract_name:
                Selected view contract name.
            command_contract_name:
                Selected command contract name.
            codegen_contract_name:
                Selected codegen contract name.

        Returns:
            FrameACLConfiguration:
                Assembled ACL snapshot for the selected family contracts.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.build_selected_configuration(
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
            reason="manager_selected_configuration",
        )

    def _get_current_view_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Return the current selected view configuration for one frame/contract.

        Returns:
            FrameACLViewConfiguration: Current view configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_view_configuration(contract_name)

    def _get_current_command_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Return the current selected command configuration for one frame/contract.

        Returns:
            FrameACLCommandConfiguration: Current command configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_command_configuration(contract_name)

    def _get_current_codegen_frame_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Return the current selected codegen configuration for one frame/contract.

        Returns:
            FrameACLCodegenConfiguration: Current codegen configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_codegen_configuration(contract_name)

    def _get_named_frame_acl_configuration(
            self,
            frame_name: str,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Return one named ACL configuration for a frame.

        Purpose:
            Resolve one frame-local named ACL contract through the manager
            boundary.

        Args:
            frame_name:
                Stable frame name that owns the contract registry.
            contract_name:
                Frame-local contract name to resolve.

        Returns:
            FrameACLConfiguration:
                Named ACL configuration for the frame.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_named_configuration(contract_name)

    def _list_named_frame_acl_configuration_names(
            self,
            frame_name: str,
    ) -> List[str]:
        """
        Return all named ACL contract names for one frame.

        Purpose:
            Expose the frame-local named contract registry keys through the
            manager boundary.

        Args:
            frame_name:
                Stable frame name that owns the contract registry.

        Returns:
            List[str]:
                Named ACL contract names for the frame.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.list_named_configuration_names()

    def _register_named_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Register one named ACL configuration for a frame.

        Purpose:
            Add a new frame-local named contract through the manager boundary.

        Args:
            frame_name:
                Stable frame name that owns the contract registry.
            configuration:
                Locked ACL configuration node to register.
            contract_name:
                Frame-local contract name.

        Returns:
            FrameACLConfiguration:
                Registered named configuration node.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.register_named_configuration(
            configuration,
            contract_name=contract_name,
        )

    def _install_named_frame_acl_configuration(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            *,
            contract_name: str = "default",
    ) -> FrameACLConfiguration:
        """
        Install one same-name ACL bundle revision into an existing contract set.

        Args:
            frame_name:
                Stable frame name that owns the ACL registry.
            configuration:
                Locked ACL configuration node to install.
            contract_name:
                Same-name contract to advance.

        Returns:
            FrameACLConfiguration: Installed assembled configuration snapshot.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.install_configuration(
            configuration,
            contract_name=contract_name,
        )

    def _get_current_view_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLViewConfiguration:
        """
        Return the current selected view configuration for one frame/contract.

        Returns:
            FrameACLViewConfiguration: Current selected view configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_view_configuration(contract_name)

    def _get_current_command_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCommandConfiguration:
        """
        Return the current selected command configuration for one frame/contract.

        Returns:
            FrameACLCommandConfiguration: Current selected command configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_command_configuration(contract_name)

    def _get_current_codegen_acl_configuration(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
    ) -> FrameACLCodegenConfiguration:
        """
        Return the current selected codegen configuration for one frame/contract.

        Returns:
            FrameACLCodegenConfiguration: Current selected codegen configuration.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.get_current_codegen_configuration(contract_name)

    def _validate_frame_acl_configuration_against_descriptor(
            self,
            frame_name: str,
            configuration: FrameACLConfiguration,
            frame_descriptor: FrameDescriptor,
    ) -> bool:
        """
        Validate one frame ACL configuration against descriptor payload truth.

        Args:
            frame_name:
                Stable frame name that owns the ACL container.
            configuration:
                Candidate ACL configuration node.
            frame_descriptor:
                Descriptor truth for the same frame.

        Returns:
            bool: True when validation succeeds.
        """
        self.check_cleaned()
        container = self._ensure_frame_acl_container(frame_name)
        return container.frame_acl_validator.validate_configuration_against_descriptor(
            configuration,
            frame_descriptor,
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

    def _register_frame_acl_profile(
            self,
            frame_acl_profile: FrameACLProfile,
    ) -> None:
        """
        Register or replace one named ACL profile in the manager registry.

        Args:
            frame_acl_profile:
                Profile object to store by its own name.

        Contract:
            - Replaces any existing distinct profile registered under the same
              name.
            - Cleans the displaced profile object before storing the new one.

        Returns:
            None.

        Raises:
            TypeError:
                If `frame_acl_profile` is not a `FrameACLProfile`.
        """
        self.check_cleaned()
        if not isinstance(frame_acl_profile, FrameACLProfile):
            raise TypeError("frame_acl_profile must be a FrameACLProfile.")
        with self._lock:
            existing = self._frame_acl_profiles_by_name.get(frame_acl_profile.name)
            if existing is not None and existing is not frame_acl_profile:
                existing.cleanup()
            self._frame_acl_profiles_by_name[frame_acl_profile.name] = frame_acl_profile

    def _register_view_acl_profile(
            self,
            view_profile: FrameACLViewProfile,
    ) -> None:
        """
        Register or replace one reusable view ACL profile.

        Args:
            view_profile:
                Reusable view profile to store.

        Contract:
            Delegates registration to the manager-owned profile builder/library.

        Returns:
            None.
        """
        self.check_cleaned()
        self._frame_acl_profile_builder.register_view_profile(view_profile)

    def _register_codegen_acl_profile(
            self,
            codegen_profile: FrameACLCodegenProfile,
    ) -> None:
        """
        Register or replace one reusable codegen ACL profile.

        Args:
            codegen_profile:
                Reusable codegen profile to store.

        Contract:
            Delegates registration to the manager-owned profile builder/library.

        Returns:
            None.
        """
        self.check_cleaned()
        self._frame_acl_profile_builder.register_codegen_profile(codegen_profile)

    def _get_required_frame_acl_profile(
            self,
            profile_name: str,
    ) -> FrameACLProfile:
        """
        Return one existing ACL profile from the manager registry or raise.

        Args:
            profile_name:
                Profile name to resolve.

        Contract:
            - Does not synthesize or compose a missing profile.
            - Fails fast when the requested name is absent.

        Returns:
            FrameACLProfile: Existing stored profile.

        Raises:
            KeyError: If the profile is not registered.
        """
        self.check_cleaned()
        with self._lock:
            try:
                return self._frame_acl_profiles_by_name[profile_name]
            except KeyError as exc:
                raise KeyError(profile_name) from exc

    def _list_frame_acl_profile_names(self) -> List[str]:
        """
        Return the current ACL profile names in insertion order.

        Contract:
            Returns a snapshot list of the manager-local composed profile
            registry keys.

        Returns:
            List[str]: Current profile names.
        """
        self.check_cleaned()
        with self._lock:
            return list(self._frame_acl_profiles_by_name.keys())

    def _list_view_acl_profile_names(self) -> List[str]:
        """
        Return the current reusable view-profile names.

        Contract:
            Delegates to the manager-owned profile builder and returns a
            snapshot of registered reusable view-profile names.

        Returns:
            List[str]: Current view-profile names.
        """
        self.check_cleaned()
        return self._frame_acl_profile_builder.list_view_profile_names()

    def _list_codegen_acl_profile_names(self) -> List[str]:
        """
        Return the current reusable codegen-profile names.

        Contract:
            Delegates to the manager-owned profile builder and returns a
            snapshot of registered reusable codegen-profile names.

        Returns:
            List[str]: Current codegen-profile names.
        """
        self.check_cleaned()
        return self._frame_acl_profile_builder.list_codegen_profile_names()

    def _remove_frame_acl_profile(self, profile_name: str) -> bool:
        """
        Remove and cleanup one ACL profile by name.

        Args:
            profile_name:
                Profile name to remove.

        Contract:
            - Removes the composed profile from the manager-local registry.
            - Cleans the removed profile before returning.
            - Returns False when the name is not registered.

        Returns:
            bool: True when the profile existed and was removed.
        """
        self.check_cleaned()
        with self._lock:
            frame_acl_profile = self._frame_acl_profiles_by_name.pop(
                profile_name,
                None,
            )
            if frame_acl_profile is None:
                return False
            frame_acl_profile.cleanup()
            return True

    def _create_frame_acl_profile(
            self,
            profile_name: str,
            *,
            view_profile_name: str = "safe",
            codegen_profile_name: str = "safe",
    ) -> FrameACLProfile:
        """
        Compose and register one frame ACL profile from reusable view/codegen
        profiles.

        Args:
            profile_name:
                Stable composed profile name to create.
            view_profile_name:
                Reusable view-profile name to compose in.
            codegen_profile_name:
                Reusable codegen-profile name to compose in.

        Contract:
            - Delegates composition to the manager-owned profile builder.
            - Registers the resulting composed profile in the manager-local
              profile registry before returning it.

        Returns:
            FrameACLProfile: Newly composed and registered frame ACL profile.
        """
        self.check_cleaned()
        frame_acl_profile = self._frame_acl_profile_builder.create_profile(
            profile_name,
            view_profile_name=view_profile_name,
            codegen_profile_name=codegen_profile_name,
        )
        self._register_frame_acl_profile(frame_acl_profile)
        return frame_acl_profile
