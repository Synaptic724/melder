import threading
from typing import Any, Dict, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_link.frame_link_contract import FrameLinkContract
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.rift_space.capability_rift_space import CapabilityRiftSpace
from melder.aether.nexus.rift.rift_space.codegen_rift_space import CodegenRiftSpace
from melder.aether.nexus.rift.rift_space.rift_event_configuration import RiftEventConfiguration
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import (
    IAethericFrame,
    INexus,
    IRift,
    IRiftConfiguration,
    IRiftSpace,
    ISafeLogger,
)


class Rift(Cleanable, IRift):
    """
    Internal

    Live Rift runtime object created and registered by `Nexus`.

    Purpose:
        Represent one live Rift that owns its own immediate runtime state,
        explicit frame-link contracts and one owned room without requiring a
        separate public state object.

    Contract:
        - Owns a per-Rift configuration snapshot, explicit frame-link
          contracts, and one primary room.
        - Owns only live Rift runtime state, not global registry or Nexus-wide
          configuration.
        - Programs one primary concrete space from the chosen Rift
          `space_type` during creation.
        - Does not eagerly realize Nexus frames during creation.
        - Defers target-frame selection to later explicit linking.
        - Treats `Aether` as hidden substrate reached later by lower runtime
          layers such as workstation/workspace logic.

    Room Mode Matrix:
        - `static`
          - Programs `StaticRiftSpace`.
          - Uses the static viewer/command posture.
          - Defaults workstation binds to weak when callers omit `weak_ref`.
          - Denies topology mutation and direct create-path spell activation.
        - `capability`
          - Programs `CapabilityRiftSpace`.
          - Broad manual runtime/object access without codegen.
          - Defaults workstation binds to strong.
          - Lower Melder frame/runtime truth still decides what actually works.
        - `codegen`
          - Programs `CodegenRiftSpace`.
          - Currently shares the same broad manual runtime posture as
          capability.
          - Reserved for later codegen-oriented differentiation.

    Lifecycle:
        Created by `Nexus`, then registered into the Nexus registry. Cleanup
        clears the owned room and owned live-state references.

    TODO:
        When Rift-owned Melder frames are introduced for local conduit hosting,
        bind them in the most permissive AR posture by default:
        `rift_enabled=True`, `ai_native_enabled=True`, and
        `system_state=dynamic`.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_rift_name",
        "_lock",
        "_logger",
        "_nexus",
        "_configuration",
        "_frame_link_contracts_by_frame_name",
        "_space",
        "_is_registered",
        "_is_active",
        "_metadata",
    ]

    def __init__(
            self,
            nexus: INexus,
            *,
            configuration: IRiftConfiguration,
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            space_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
            logger: Optional[Any] = None,
    ) -> None:
        """
        Internal

        Initialize one live Rift object.

        Args:
            nexus:
                Owning Nexus singleton.
            configuration:
                Finalized per-Rift configuration snapshot.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            space_id:
                Optional explicit primary-space id.
            metadata:
                Optional Rift-level metadata.
            logger:
                Optional explicit logger override used instead of the default
                provider-backed logger.

        Returns:
            None.

        Contract:
            - Copies incoming metadata into a Rift-owned mutable dict.
            - Starts with no engaged target-frame contracts.
            - Programs one primary concrete space from the configuration's
              `space_type` and room/event settings.
            - Defers logger resolution to `_initialize_logging(...)`.
        """
        if nexus is None:
            raise TypeError("nexus cannot be None.")
        if not isinstance(nexus, INexus):
            raise TypeError("nexus must satisfy INexus.")
        if not nexus.is_configured:
            raise RuntimeError("Rift requires a configured Nexus.")
        if not nexus.is_enabled:
            raise RuntimeError("Rift requires an enabled Nexus.")
        if not configuration.frozen:
            raise RuntimeError("Rift requires a finalized RiftConfiguration.")

        super().__init__()
        self._id: str = rift_id or IDBuilder.create_id()
        self._rift_name: Optional[str] = rift_name
        self._lock: threading.RLock = threading.RLock()
        self._logger: ISafeLogger = InitHelpers.resolve_safe_logger(None)
        self._nexus: INexus = nexus
        self._configuration: IRiftConfiguration = configuration
        self._frame_link_contracts_by_frame_name: Dict[str, FrameLinkContract] = {}
        self._space: Optional[IRiftSpace] = None
        self._is_registered: bool = False
        self._is_active: bool = False
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._initialize_logging(logger)
        self._space = self._create_primary_space_from_configuration(space_id=space_id)

    def _initialize_logging(self, logger: Optional[Any]) -> None:
        """
        Internal

        Establish the Rift logger through the hosted utility system.

        Priority:
            1) Explicit logger arg
            2) AetherUtilitySystem channel logger
            3) Silent no-op logger

        Args:
            logger:
                Optional explicit logger override.

        Returns:
            None.
        """
        try:
            if logger is not None:
                self._logger = InitHelpers.resolve_safe_logger(logger)
            else:
                self._logger = InitHelpers.resolve_channel_logger(
                    self,
                    groups=["rift", "lifecycle"],
                    system_groups=["nexus", "aether"],
                    props={
                        "rift_id": self._id,
                        "rift_name": self._rift_name,
                    },
                    channels="system",
                )
        except Exception as e:
            self._logger = InitHelpers.resolve_safe_logger(None)
            self._logger.error(
                f"Failed to initialize Rift logger: {e}",
                "_initialize_logging",
                exc_info=True,
            )

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup the live Rift object.

        Contract:
            - Cleans every owned room before clearing the room registries.
            - Cleans the owned per-Rift configuration snapshot before dropping
              the reference.
            - Clears room registries and live state references only after owned
              teardown completes.
            - Does not attempt to clean Nexus or Aether-owned global state.
            - Leaves the Rift unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        lock = self._lock
        with lock:
            if self._cleaned:
                return
            self._logger.info("Cleaning Rift runtime state.", "cleanup")
            self._cleaned = True
            if self._space is not None:
                self._space.cleanup()
            if self._configuration is not None:
                self._configuration.cleanup()
            self._metadata.clear()
            self._nexus = None
            self._configuration = None
            for frame_link_contract in self._frame_link_contracts_by_frame_name.values():
                frame_link_contract.cleanup()
            self._frame_link_contracts_by_frame_name.clear()
            self._frame_link_contracts_by_frame_name = None
            self._space = None
            self._is_registered = None
            self._is_active = None
            self._metadata = None
            self._rift_name = None
            self._id = None
        if self._logger is not None:
            self._logger.cleanup()
            self._logger = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Purpose:
            Return the canonical Rift id.

        Returns:
            str: Stable Rift id.
        """
        self.check_cleaned()
        return self._id

    @property
    def rift_name(self) -> Optional[str]:
        """
        Purpose:
            Return the optional stable Rift name.

        Returns:
            Optional[str]: Rift name when one is assigned.
        """
        self.check_cleaned()
        return self._rift_name

    @property
    def configuration(self) -> IRiftConfiguration:
        """
        Purpose:
            Return the finalized per-Rift configuration snapshot.

        Returns:
            IRiftConfiguration: Owned configuration snapshot.
        """
        self.check_cleaned()
        return self._configuration

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        """
        Internal

        Return the frame names assigned to this Rift.

        Returns:
            Tuple[str, ...]: Assigned frame names.
        """
        self.check_cleaned()
        return tuple(self._frame_link_contracts_by_frame_name.keys())

    def get_frame_link_contract(self, frame_name: str) -> FrameLinkContract:
        """
        Return the per-frame contract for one engaged frame.

        Args:
            frame_name:
                Engaged target frame name.

        Returns:
            FrameLinkContract: Per-frame contract object.

        Raises:
            ValueError:
                If `frame_name` is empty or not engaged on this Rift.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        try:
            return self._frame_link_contracts_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Rift '{0}' is not engaged with frame '{1}'.".format(
                    self._id,
                    frame_name,
                )
            ) from exc

    def get_selected_contract_names(self, frame_name: str) -> Dict[str, str]:
        """
        Return the selected ACL contract names for one engaged frame.

        Args:
            frame_name:
                Engaged target frame name.

        Returns:
            Dict[str, str]: Selected view/command/codegen contract names.
        """
        return self.get_frame_link_contract(frame_name).get_selected_contract_names()

    def target_frame(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
    ) -> None:
        """
        Internal

        Validate and engage one target frame on this Rift's frame contract.

        Args:
            frame_name:
                Target frame name to engage.
            contract_name:
                Same-name ACL contract convenience selector for the target
                frame.
            view_contract_name:
                Optional explicit selected view ACL contract name.
            command_contract_name:
                Optional explicit selected command ACL contract name.
            codegen_contract_name:
                Optional explicit selected codegen ACL contract name.

        Contract:
            - Validates target-frame policy and runtime posture through Nexus.
            - Resolves and validates the selected named ACL contract for the
              frame against descriptor truth.
            - Registers the frame on the Rift-local frame contract.
            - Refreshes the owned-space viewer when descriptor truth is
              available for the currently assigned frame set.

        Returns:
            None.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        normalized_acl_selection = self._nexus._normalize_acl_selection_input(
            {
                "view": view_contract_name or contract_name,
                "command": command_contract_name or contract_name,
                "codegen": codegen_contract_name or contract_name,
            }
        )
        is_new_frame = frame_name not in self._frame_link_contracts_by_frame_name
        self._nexus._validate_target_frame_names((frame_name,))
        requested_space_type = self._configuration.get_property("space_type")
        self._nexus._validate_target_frame_runtime_requirements(
            frame_name,
            requested_space_type,
        )
        try:
            self._nexus._get_required_frame_descriptor(frame_name)
        except KeyError as exc:
            raise ValueError(
                "Target frame '{0}' has no descriptor and cannot be targeted yet.".format(
                    frame_name
                )
            ) from exc
        configuration = self._nexus._frame_acl_manager._get_current_frame_acl_configuration(
            frame_name,
            view_contract_name=normalized_acl_selection["view"],
            command_contract_name=normalized_acl_selection["command"],
            codegen_contract_name=normalized_acl_selection["codegen"],
        )
        self._nexus._frame_acl_manager._validate_frame_acl_configuration_against_descriptor(
            frame_name,
            configuration,
            self._nexus._get_required_frame_descriptor(frame_name),
        )
        if is_new_frame:
            self._nexus._validate_target_frame_budget((frame_name,))
            self._frame_link_contracts_by_frame_name[frame_name] = FrameLinkContract(
                rift_id=self._id,
                frame_name=frame_name,
                view_contract_name=normalized_acl_selection["view"],
                command_contract_name=normalized_acl_selection["command"],
                codegen_contract_name=normalized_acl_selection["codegen"],
                metadata={
                    "rift_name": self._rift_name,
                },
            )
        else:
            self._frame_link_contracts_by_frame_name[
                frame_name
            ].set_selected_contract_names(
                contract_name=contract_name,
                view_contract_name=normalized_acl_selection["view"],
                command_contract_name=normalized_acl_selection["command"],
                codegen_contract_name=normalized_acl_selection["codegen"],
            )
        if is_new_frame:
            self._nexus._increment_ref_count(
                self._nexus._target_frame_ref_counts,
                frame_name,
            )
        self.attach_frame_viewer()

    def create_frame_viewer(
            self,
            *,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Internal

        Build one frame viewer from this Rift's assigned-frame contract.

        Args:
            view_profile_name:
                View profile name applied to each assigned view.
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.

        Contract:
            Delegates viewer creation to the owning `Nexus` using this Rift's
            current assigned-frame contract.

        Returns:
            FrameViewer: Hosted frame viewer for this Rift.
        """
        self.check_cleaned()
        return self._nexus.create_frame_viewer_for_rift(
            self._id,
            view_profile_name=view_profile_name,
            viewer_profile_name=viewer_profile_name,
        )

    def create_cached_frame_viewer(
            self,
            *,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Internal

        Build or reuse one cached frame viewer from this Rift's assigned-frame
        contract.

        Args:
            view_profile_name:
                View profile name applied to each assigned view.
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.

        Contract:
            Delegates cached-viewer creation to the owning `Nexus` and may
            reuse prior cached viewer state for this Rift/profile combination.

        Returns:
            FrameViewer: Detached cached frame viewer for this Rift.
        """
        self.check_cleaned()
        return self._nexus.create_cached_frame_viewer_for_rift(
            self._id,
            view_profile_name=view_profile_name,
            viewer_profile_name=viewer_profile_name,
        )

    def create_new_frame_viewer(
            self,
            frame_name: str,
            *,
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Internal

        Build one new frame-specific viewer transaction through this Rift.

        Args:
            frame_name:
                Target frame name to materialize for this Rift.
            viewer_profile_name:
                Selected viewer profile name for the target frame.

        Returns:
            FrameViewer: Frame-scoped viewer for the requested frame.
        """
        self.check_cleaned()
        self.get_frame_link_contract(frame_name)
        return self._nexus.create_frame_viewer_for_rift_frame(
            self._id,
            frame_name,
            viewer_profile_name=viewer_profile_name,
        )

    def attach_frame_viewer(
            self,
            *,
            cached: bool = False,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Internal

        Build one frame viewer from this Rift and attach it to the owned space.

        Args:
            cached:
                When True, uses the cached viewer creation path.
            view_profile_name:
                View profile name applied to each assigned view.
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.

        Returns:
            FrameViewer: Attached frame viewer.
        """
        self.check_cleaned()
        space = self.space
        frame_viewer = (
            self.create_cached_frame_viewer(
                view_profile_name=view_profile_name,
                viewer_profile_name=viewer_profile_name,
            )
            if cached
            else self.create_frame_viewer(
                view_profile_name=view_profile_name,
                viewer_profile_name=viewer_profile_name,
            )
        )
        space.attach_frame_viewer(frame_viewer)
        return frame_viewer

    def get_frame_viewer(self) -> FrameViewer:
        """
        Internal

        Return the attached frame viewer for the owned space or raise.

        Returns:
            FrameViewer: Attached frame viewer for the owned space.
        """
        self.check_cleaned()
        space = self.space
        frame_viewer = space.frame_viewer
        if frame_viewer is None:
            raise ValueError(
                "RiftSpace '{0}' has no attached frame viewer.".format(space.space_id)
            )
        return frame_viewer

    @property
    def space(self) -> IRiftSpace:
        """
        Purpose:
            Return the one owned RiftSpace for this Rift.

        Returns:
            IRiftSpace: Owned primary space.
        """
        self.check_cleaned()
        if self._space is None:
            raise ValueError("Rift has no owned space.")
        return self._space

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Purpose:
            Return the live Rift metadata map.

        Contract:
            Returns the live mutable metadata dict owned by this Rift, not a
            detached copy.

        Returns:
            Dict[str, object]: Rift-level metadata.
        """
        self.check_cleaned()
        return self._metadata

    @property
    def is_registered(self) -> bool:
        """
        Purpose:
            Return whether this Rift is registered in Nexus.

        Returns:
            bool: True when registered.
        """
        self.check_cleaned()
        return self._is_registered

    @property
    def is_active(self) -> bool:
        """
        Purpose:
            Return whether this Rift is currently active.

        Returns:
            bool: True when active.
        """
        self.check_cleaned()
        return self._is_active

    def mark_registered(self) -> None:
        """
        Internal

        Mark this Rift as registered in Nexus.

        Contract:
            - Sets the local registration flag under the Rift lock.
            - Does not register the Rift in Nexus by itself; callers should
              use this after the owning Nexus registry mutation succeeds.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_registered = True

    def mark_active(self) -> None:
        """
        Internal

        Mark this Rift as active.

        Contract:
            - Sets only the local active-state flag under the Rift lock.
            - Does not create spaces or register additional runtime objects.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_active = True

    def mark_inactive(self) -> None:
        """
        Internal

        Mark this Rift as inactive.

        Contract:
            - Clears only the local active-state flag under the Rift lock.
            - Does not remove spaces or detach frame assignments.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self._is_active = False

    def _create_primary_space_from_configuration(
            self,
            *,
            space_id: Optional[str] = None,
    ) -> IRiftSpace:
        """
        Internal

        Create the one primary concrete space declared by the Rift
        configuration.

        Contract:
            - Instantiates exactly one primary room from the configured
              `space_type`.
            - Uses the configured space name and a cloned event configuration.
            - Returns the resulting room so the Rift can own it directly as its
              immutable primary space.
            - Current mapping is:
              - `static` -> `StaticRiftSpace`
              - `capability` -> `CapabilityRiftSpace`
              - `codegen` -> `CodegenRiftSpace`

        Args:
            space_id:
                Optional explicit primary-space id.

        Returns:
            IRiftSpace: Primary space for this Rift.
        """
        self.check_cleaned()
        configured_space_type = self._configuration.get_property("space_type")
        configured_space_name = self._configuration.get_property("space_name")
        configured_event_configuration = self._configuration.get_property(
            "event_configuration"
        )
        cloned_event_configuration = self._clone_rift_event_configuration(
            configured_event_configuration
        )
        if configured_space_type == RiftSpaceType.codegen:
            primary_space = CodegenRiftSpace(
                owner_rift_id=self._id,
                space_name=configured_space_name,
                event_configuration=cloned_event_configuration,
                space_id=space_id,
            )
        elif configured_space_type == RiftSpaceType.capability:
            primary_space = CapabilityRiftSpace(
                owner_rift_id=self._id,
                space_name=configured_space_name,
                event_configuration=cloned_event_configuration,
                space_id=space_id,
            )
        else:
            primary_space = StaticRiftSpace(
                owner_rift_id=self._id,
                space_name=configured_space_name,
                event_configuration=cloned_event_configuration,
                space_id=space_id,
            )
        return primary_space

    @staticmethod
    def _clone_rift_event_configuration(
            event_configuration: Optional[object],
    ) -> RiftEventConfiguration:
        """
        Internal

        Clone the configured primary-space event configuration.

        Args:
            event_configuration:
                Optional source room-event configuration.

        Returns:
            RiftEventConfiguration: Detached room-event configuration.
        """
        if event_configuration is None:
            return RiftEventConfiguration()
        return RiftEventConfiguration(
            action_enrichers=list(event_configuration._action_enrichers),
            memory_enrichers=list(event_configuration._memory_enrichers),
            action_observers=list(event_configuration._action_observers),
            memory_observers=list(event_configuration._memory_observers),
        )
    def get_nexus_frame(self, frame_name: Optional[str] = None) -> IAethericFrame:
        """
        Internal

        Return one Nexus-managed frame through Nexus policy.

        Args:
            frame_name:
                Optional explicit Nexus frame name.

        Contract:
            Delegates frame resolution to Nexus using this Rift's identity and
            the current Nexus/Rift frame policy.

        Returns:
            IAethericFrame: Resolved Nexus frame.
        """
        self.check_cleaned()
        return self._nexus.get_nexus_frame_for_rift(self._id, frame_name=frame_name)

    def create_nexus_frame(
            self,
            frame_name: Optional[str] = None,
            immutable: bool = False,
    ) -> IAethericFrame:
        """
        Internal

        Create one Nexus-managed frame through Nexus policy.

        Args:
            frame_name:
                Optional explicit Nexus frame name.
            immutable:
                Immutable flag for indexed/shared creation.

        Contract:
            Delegates frame creation/recovery to Nexus using this Rift's
            identity and current frame policy.

        Returns:
            IAethericFrame: Created or recovered Nexus frame.
        """
        self.check_cleaned()
        return self._nexus.create_nexus_frame_for_rift(
            self._id,
            frame_name=frame_name,
            immutable=immutable,
        )

    def list_accessible_nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Internal

        Return the Nexus frame names this Rift may currently access.

        Contract:
            Delegates to Nexus and returns a snapshot tuple of currently
            accessible frame names for this Rift.

        Returns:
            Tuple[str, ...]: Accessible Nexus frame names.
        """
        self.check_cleaned()
        return self._nexus.list_accessible_nexus_frame_names(self._id)

    def on_nexus_frame_disposed(self, frame_name: str) -> None:
        """
        Internal

        Placeholder hook for later Rift/workspace frame-disposal event
        propagation.

        Args:
            frame_name:
                Frame name that was disposed externally.

        Contract:
            Currently logs the disposal observation only; it does not yet
            mutate local frame-name state or room attachments.

        Returns:
            None.
        """
        self.check_cleaned()
        self._logger.info(
            "Observed disposal of Nexus frame '{0}'.".format(frame_name),
            "on_nexus_frame_disposed",
        )
        return
