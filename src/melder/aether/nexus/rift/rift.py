import threading
from typing import Any, Dict, Optional, Sequence, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.aether import Aether
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_link.frame_link_contract import FrameLinkContract
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.rift_space.capability_rift_space import CapabilityRiftSpace
from melder.aether.nexus.rift.rift_space.dynamic_rift_space import DynamicRiftSpace
from melder.aether.nexus.rift.rift_space.rift_event_configuration import RiftEventConfiguration
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.helpers.init_helpers import InitHelpers
from melder.utilities.interfaces.interfaces import (
    IAether,
    IAethericFrame,
    IConduit,
    IConduitCloud,
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
        frame-name assignments/defaults, and room registry without requiring a
        separate public state object.

    Contract:
        - Owns per-Rift configuration snapshot, frame-name assignments, and
          local room registry state.
        - Owns only live Rift runtime state, not global registry or Nexus-wide
          configuration.
        - Programs one primary concrete space from the chosen Rift
          `space_type` during creation.
        - Defers target-frame selection to a later explicit action.
        - Treats `Aether` as hidden substrate reached later by lower runtime
          layers such as workstation/workspace logic.

    Lifecycle:
        Created by `Nexus`, then registered into the Nexus registry. Cleanup
        clears room registries and owned live-state references.

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
        "_aether",
        "_configuration",
        "_nexus_frame_names",
        "_default_nexus_frame_name",
        "_target_frame_names",
        "_default_target_frame_name",
        "_frame_link_contract",
        "_local_conduit_id",
        "_active_space_id",
        "_is_registered",
        "_is_active",
        "_metadata",
        "_spaces_by_id",
        "_space_ids_by_name",
    ]

    def __init__(
            self,
            nexus: INexus,
            *,
            configuration: IRiftConfiguration,
            nexus_frame_names: Sequence[str],
            default_nexus_frame_name: str,
            target_frame_names: Sequence[str],
            default_target_frame_name: Optional[str],
            rift_name: Optional[str] = None,
            rift_id: Optional[str] = None,
            local_conduit_id: Optional[str] = None,
            active_space_id: Optional[str] = None,
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
            nexus_frame_names:
                Assigned internal Nexus frame names for this Rift.
            default_nexus_frame_name:
                Default internal Nexus frame name for this Rift.
            target_frame_names:
                Optional assigned target/userland frame names for this Rift.
            default_target_frame_name:
                Optional default target/userland frame name for this Rift.
            rift_name:
                Optional stable Rift name.
            rift_id:
                Optional explicit Rift id.
            local_conduit_id:
                Optional live local conduit id.
            active_space_id:
                Optional active room id.
            metadata:
                Optional Rift-level metadata.
            logger:
                Optional explicit logger override used instead of the default
                provider-backed logger.

        Returns:
            None.

        Contract:
            - Copies incoming frame-name sequences into Rift-owned tuples.
            - Copies incoming metadata into a Rift-owned mutable dict.
            - Builds and owns the initial `FrameLinkContract` for assigned
              target-frame access.
            - Programs one primary concrete space from the configuration's
              `space_type` and room/event settings.
            - Defers logger resolution to `_initialize_logging(...)`.
        """
        if nexus is None:
            raise TypeError("nexus cannot be None.")
        if not isinstance(nexus, INexus):
            raise TypeError("nexus must satisfy INexus.")
        nexus.check_cleaned()
        if not nexus.is_configured:
            raise RuntimeError("Rift requires a configured Nexus.")
        if not nexus.is_enabled:
            raise RuntimeError("Rift requires an enabled Nexus.")
        if not configuration.frozen:
            raise RuntimeError("Rift requires a finalized RiftConfiguration.")
        if not nexus_frame_names:
            raise ValueError("nexus_frame_names cannot be empty.")
        if default_nexus_frame_name not in nexus_frame_names:
            raise ValueError("default_nexus_frame_name must be present in nexus_frame_names.")
        normalized_target_frame_names = tuple(target_frame_names)
        if (
                default_target_frame_name is not None
                and default_target_frame_name not in normalized_target_frame_names
        ):
            raise ValueError("default_target_frame_name must be present in target_frame_names.")

        super().__init__()
        self._id: str = rift_id or IDBuilder.create_id()
        self._rift_name: Optional[str] = rift_name
        self._lock: threading.RLock = threading.RLock()
        self._logger: ISafeLogger = InitHelpers.resolve_safe_logger(None)
        self._nexus: INexus = nexus
        self._aether: IAether = Aether()
        self._configuration: IRiftConfiguration = configuration
        self._nexus_frame_names: Tuple[str, ...] = tuple(nexus_frame_names)
        self._default_nexus_frame_name: str = default_nexus_frame_name
        self._target_frame_names: Tuple[str, ...] = normalized_target_frame_names
        self._default_target_frame_name: Optional[str] = default_target_frame_name
        self._frame_link_contract: FrameLinkContract = FrameLinkContract(
            rift_id=self._id,
            assigned_frame_names=self._target_frame_names,
            default_frame_name=self._default_target_frame_name,
            metadata={
                "rift_name": self._rift_name,
                "nexus_frame_names": self._nexus_frame_names,
            },
        )
        self._local_conduit_id: Optional[str] = local_conduit_id
        self._active_space_id: Optional[str] = active_space_id
        self._is_registered: bool = False
        self._is_active: bool = False
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._spaces_by_id: Dict[str, IRiftSpace] = {}
        self._space_ids_by_name: Dict[str, str] = {}
        self._initialize_logging(logger)
        self._create_primary_space_from_configuration(space_id=active_space_id)

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
                        "default_nexus_frame_name": self._default_nexus_frame_name,
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
            - Clears room registries and live state references.
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
            self._spaces_by_id.clear()
            self._space_ids_by_name.clear()
            self._metadata.clear()

            self._nexus = None
            self._aether = None
            self._configuration = None
            self._nexus_frame_names = None
            self._default_nexus_frame_name = None
            self._target_frame_names = None
            self._default_target_frame_name = None
            self._frame_link_contract.cleanup()
            self._frame_link_contract = None
            self._local_conduit_id = None
            self._active_space_id = None
            self._is_registered = None
            self._is_active = None
            self._metadata = None
            self._spaces_by_id = None
            self._space_ids_by_name = None
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

    @property
    def nexus_frame_names(self) -> Tuple[str, ...]:
        """
        Purpose:
            Return the assigned internal Nexus frame names for this Rift.

        Returns:
            Tuple[str, ...]: Internal Nexus frame names.
        """
        self.check_cleaned()
        return self._nexus_frame_names

    @property
    def default_nexus_frame_name(self) -> str:
        """
        Purpose:
            Return the default internal Nexus frame name for this Rift.

        Returns:
            str: Default Nexus frame name.
        """
        self.check_cleaned()
        return self._default_nexus_frame_name

    @property
    def target_frame_names(self) -> Tuple[str, ...]:
        """
        Purpose:
            Return the assigned target/userland frame names for this Rift.

        Returns:
            Tuple[str, ...]: Target frame names.
        """
        self.check_cleaned()
        return self._target_frame_names

    @property
    def default_target_frame_name(self) -> Optional[str]:
        """
        Purpose:
            Return the default target/userland frame name for this Rift.

        Returns:
            Optional[str]: Default target frame name when one exists.
        """
        self.check_cleaned()
        return self._default_target_frame_name

    @property
    def local_conduit_id(self) -> Optional[str]:
        """
        Purpose:
            Return the optional live local conduit id attached to this Rift.

        Returns:
            Optional[str]: Local conduit id, if one is set.
        """
        self.check_cleaned()
        return self._local_conduit_id

    @property
    def frame_link_contract(self) -> FrameLinkContract:
        """
        Purpose:
            Return the Rift-local frame availability contract.

        Returns:
            FrameLinkContract: Current Rift-local assigned-frame contract.
        """
        self.check_cleaned()
        return self._frame_link_contract

    def list_assigned_frame_names(self) -> Tuple[str, ...]:
        """
        Internal

        Return the frame names assigned to this Rift.

        Returns:
            Tuple[str, ...]: Assigned frame names.
        """
        self.check_cleaned()
        return self._frame_link_contract.assigned_frame_names

    def get_conduit_cloud(
            self,
            frame_name: Optional[str] = None,
    ) -> IConduitCloud:
        """
        Return the conduit cloud for one targeted frame.

        Args:
            frame_name:
                Optional explicit target frame name. When omitted, the Rift
                default target frame is used.

        Returns:
            IConduitCloud: The frame-local conduit cloud.

        Raises:
            ValueError:
                If the requested frame is not targeted, no target frame is
                available, or there are multiple targeted frames without a
                default.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.get_conduit_cloud(resolved_frame_name)

    def list_conduit_ids(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the conduit ids for one targeted frame.

        Args:
            frame_name:
                Optional explicit target frame name.

        Returns:
            Tuple[str, ...]: Snapshot of conduit ids.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.list_conduit_ids(resolved_frame_name)

    def list_conduit_names(
            self,
            frame_name: Optional[str] = None,
    ) -> Tuple[str, ...]:
        """
        Return the conduit names for one targeted frame.

        Args:
            frame_name:
                Optional explicit target frame name.

        Returns:
            Tuple[str, ...]: Snapshot of conduit names.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.list_conduit_names(resolved_frame_name)

    def count_conduits(self, frame_name: Optional[str] = None) -> int:
        """
        Return the number of conduits in one targeted frame.

        Args:
            frame_name:
                Optional explicit target frame name.

        Returns:
            int: Number of conduits registered in the frame.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.count_conduits(resolved_frame_name)

    def has_conduit_id(
            self,
            conduit_id: str,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one conduit id exists in one targeted frame.

        Args:
            conduit_id:
                Conduit id to check.
            frame_name:
                Optional explicit target frame name.

        Returns:
            bool: True when the conduit id exists in the frame.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.has_conduit_id(conduit_id, resolved_frame_name)

    def has_conduit_name(
            self,
            name: str,
            frame_name: Optional[str] = None,
    ) -> bool:
        """
        Return whether one conduit name exists in one targeted frame.

        Args:
            name:
                Conduit name to check.
            frame_name:
                Optional explicit target frame name.

        Returns:
            bool: True when the conduit name exists in the frame.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.has_conduit_name(name, resolved_frame_name)

    def find_conduit_id_by_name(
            self,
            name: str,
            frame_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Return the conduit id registered for one name in one targeted frame.

        Args:
            name:
                Conduit name to resolve.
            frame_name:
                Optional explicit target frame name.

        Returns:
            Optional[str]: Matching conduit id, or None when missing.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.find_conduit_id_by_name(name, resolved_frame_name)

    def get_conduit_by_id(
            self,
            conduit_id: str,
            frame_name: Optional[str] = None,
    ) -> IConduit:
        """
        Return one conduit object by id from one targeted frame.

        Args:
            conduit_id:
                Conduit id to resolve.
            frame_name:
                Optional explicit target frame name.

        Returns:
            IConduit: Matching conduit object.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.get_conduit_by_id(conduit_id, resolved_frame_name)

    def get_conduit_by_name(
            self,
            name: str,
            frame_name: Optional[str] = None,
    ) -> IConduit:
        """
        Return one conduit object by name from one targeted frame.

        Args:
            name:
                Conduit name to resolve.
            frame_name:
                Optional explicit target frame name.

        Returns:
            IConduit: Matching conduit object.
        """
        self.check_cleaned()
        resolved_frame_name = self._resolve_conduit_frame_name(frame_name)
        return self._aether.get_conduit_by_name(name, resolved_frame_name)

    def target_frame(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
            set_as_default: bool = False,
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
            set_as_default:
                When True, the engaged frame also becomes the default target
                frame for this Rift.

        Contract:
            - Validates target-frame policy and runtime posture through Nexus.
            - Resolves and validates the selected named ACL contract for the
              frame against descriptor truth.
            - Registers the frame on the Rift-local frame contract.
            - Refreshes the active-space viewer when descriptor truth is
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
        is_new_frame = not self._frame_link_contract.has_frame(frame_name)
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
        self._frame_link_contract.register_frame(
            frame_name,
            set_as_default=set_as_default,
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
            self._target_frame_names = self._frame_link_contract.assigned_frame_names
        if set_as_default:
            self._default_target_frame_name = frame_name
        self.attach_frame_viewer_to_space(space_id=self._active_space_id)

    def engage_frame(
            self,
            frame_name: str,
            *,
            contract_name: str = "default",
            view_contract_name: Optional[str] = None,
            command_contract_name: Optional[str] = None,
            codegen_contract_name: Optional[str] = None,
            set_as_default: bool = False,
    ) -> None:
        """
        Internal

        Backward-compatible alias for `target_frame(...)`.

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
            set_as_default:
                When True, the engaged frame also becomes the default target
                frame for this Rift.

        Returns:
            None.
        """
        self.target_frame(
            frame_name,
            contract_name=contract_name,
            view_contract_name=view_contract_name,
            command_contract_name=command_contract_name,
            codegen_contract_name=codegen_contract_name,
            set_as_default=set_as_default,
        )

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
        if not self._frame_link_contract.has_frame(frame_name):
            raise ValueError(
                "Rift '{0}' is not engaged with frame '{1}'.".format(
                    self._id,
                    frame_name,
                )
            )
        return self._nexus.create_frame_viewer_for_rift_frame(
            self._id,
            frame_name,
            viewer_profile_name=viewer_profile_name,
        )

    def attach_frame_viewer_to_space(
            self,
            *,
            space_id: Optional[str] = None,
            cached: bool = False,
            view_profile_name: str = "general",
            viewer_profile_name: str = "general",
    ) -> FrameViewer:
        """
        Internal

        Build one frame viewer from this Rift and attach it to a space.

        Args:
            space_id:
                Optional target space id. When omitted, the active space is
                used.
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
        target_space_id = space_id or self._active_space_id
        if target_space_id is None:
            raise ValueError("Rift has no target space for frame viewer attachment.")
        space = self.get_space(target_space_id)
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

    def get_space_frame_viewer(self, space_id: Optional[str] = None) -> FrameViewer:
        """
        Internal

        Return the attached frame viewer for one space or raise.

        Args:
            space_id:
                Optional target space id. When omitted, the active space is
                used.

        Returns:
            FrameViewer: Attached frame viewer for the selected space.
        """
        self.check_cleaned()
        target_space_id = space_id or self._active_space_id
        if target_space_id is None:
            raise ValueError("Rift has no target space for frame viewer access.")
        frame_viewer = self.get_space(target_space_id).frame_viewer
        if frame_viewer is None:
            raise ValueError(
                "RiftSpace '{0}' has no attached frame viewer.".format(target_space_id)
            )
        return frame_viewer

    @property
    def active_space_id(self) -> Optional[str]:
        """
        Purpose:
            Return the optional active room id for this Rift.

        Returns:
            Optional[str]: Active room id when one is selected.
        """
        self.check_cleaned()
        return self._active_space_id

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

    def register_space(self, space: IRiftSpace) -> None:
        """
        Internal

        Register one `RiftSpace` under this Rift.

        Args:
            space:
                Room object to register.

        Contract:
            - Rejects spaces owned by another Rift.
            - Indexes the room by id and, when present, by stable name.
            - Sets the first registered room as the active room by default.

        Returns:
            None.

        Raises:
            ValueError: If the room belongs to another Rift or collides by id or name.
        """
        self.check_cleaned()
        with self._lock:
            if space.owner_rift_id != self._id:
                raise ValueError("space.owner_rift_id must match the owning Rift id.")
            if space.space_id in self._spaces_by_id:
                raise ValueError("Space with id '{0}' already exists.".format(space.space_id))

            self._spaces_by_id[space.space_id] = space
            if space.space_name:
                if space.space_name in self._space_ids_by_name:
                    raise ValueError("Space name '{0}' already exists.".format(space.space_name))
                self._space_ids_by_name[space.space_name] = space.space_id
            if self._active_space_id is None:
                self._active_space_id = space.space_id
            self._logger.info(
                "Registered RiftSpace '{0}' (id={1}).".format(space.space_name, space.space_id),
                "register_space",
            )

    def _create_primary_space_from_configuration(
            self,
            *,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Create and register the primary concrete space declared by the Rift
        configuration.

        Contract:
            - Instantiates exactly one primary room from the configured
              `space_type`.
            - Uses the configured space name and a cloned event configuration.
            - Registers the resulting room immediately so the Rift always has
              a working primary-space anchor after creation.

        Args:
            space_id:
                Optional explicit primary-space id.

        Returns:
            None.
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
        if configured_space_type == RiftSpaceType.dynamic:
            primary_space = DynamicRiftSpace(
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
        self.register_space(primary_space)

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


    def get_space(self, space_id: str) -> IRiftSpace:
        """
        Internal

        Return one registered space by id.

        Args:
            space_id:
                Canonical room id.

        Contract:
            Returns the live registered room object, not a detached copy.

        Returns:
            IRiftSpace: Registered room object.
        """
        self.check_cleaned()
        try:
            return self._spaces_by_id[space_id]
        except KeyError as exc:
            raise ValueError("Space with id '{0}' was not found.".format(space_id)) from exc

    def get_space_by_name(self, space_name: str) -> IRiftSpace:
        """
        Internal

        Resolve one registered space through the name -> id index.

        Args:
            space_name:
                Stable room name.

        Contract:
            Resolves through the Rift's name-to-id index and then returns the
            same live room object exposed by `get_space(...)`.

        Returns:
            IRiftSpace: Registered room object.
        """
        self.check_cleaned()
        try:
            space_id = self._space_ids_by_name[space_name]
        except KeyError as exc:
            raise ValueError("Space with name '{0}' was not found.".format(space_name)) from exc
        return self.get_space(space_id)

    def set_active_space(self, space_id: str) -> None:
        """
        Internal

        Set the active space by canonical id.

        Args:
            space_id:
                Canonical room id.

        Contract:
            - Validates that the target room is already registered.
            - Updates only the active-room pointer; it does not mutate the room
              registry itself.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            self.get_space(space_id)
            self._active_space_id = space_id
            self._logger.info(
                "Active RiftSpace set to id={0}.".format(space_id),
                "set_active_space",
            )

    def list_space_ids(self) -> list[str]:
        """
        Internal

        Return the current registered space ids.

        Contract:
            Returns a snapshot list built from the current room registry keys.

        Returns:
            list[str]: Snapshot of room ids.
        """
        self.check_cleaned()
        return list(self._spaces_by_id.keys())

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

    def _resolve_conduit_frame_name(self, frame_name: Optional[str]) -> str:
        """
        Resolve one targeted frame name for conduit discovery helpers.

        Args:
            frame_name:
                Optional explicit target frame name.

        Returns:
            str: Resolved targeted frame name.

        Raises:
            ValueError:
                If the requested frame is not targeted, no target frame is
                available, or there are multiple targeted frames without a
                default.
        """
        self.check_cleaned()
        if frame_name is not None:
            if not self._frame_link_contract.has_frame(frame_name):
                raise ValueError(
                    "Rift is not targeting frame '{0}'.".format(frame_name)
                )
            return frame_name
        if self._default_target_frame_name is not None:
            return self._default_target_frame_name
        if len(self._target_frame_names) == 1:
            return self._target_frame_names[0]
        if len(self._target_frame_names) == 0:
            raise ValueError("Rift has no targeted frame for conduit discovery.")
        raise ValueError(
            "Rift has multiple targeted frames and no default target frame for conduit discovery."
        )

    def _attach_nexus_frame_name(self, frame_name: str) -> None:
        """
        Internal

        Add one Nexus frame name to this Rift's known attachment set.

        Args:
            frame_name:
                Frame name to append if missing.

        Contract:
            - Deduplicates frame names.
            - Replaces the stored tuple with a new tuple when appending.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if frame_name in self._nexus_frame_names:
                return
            self._nexus_frame_names = self._nexus_frame_names + (frame_name,)
