import threading
from typing import Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.profiles.frame_viewer_profile_builder import (
    FrameViewerProfileBuilder,
)
from melder.aether.nexus.rift.projection.frame_projection_set import (
    FrameProjectionSet,
)
from melder.aether.nexus.rift.rift_space.event_system.rift_event_system import (
    RiftEventSystem,
)
from melder.aether.nexus.rift.rift_space.memory_system.rift_memory_system import (
    RiftMemorySystem,
)
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.workstation import Workstation
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IRiftEventSystem,
    IRiftGate,
    IRiftMemorySystem,
    IRiftSpace,
)


class RiftSpace(Cleanable, IRiftSpace):
    """
    Internal

    Base room/workspace class for `Rift`.

    Purpose:
        Provide the base room/workspace contract for `Rift`.

    Contract:
        - Owns stable room identity and room-local metadata.
        - Keeps a room name for paired lookup through the owning Rift.
        - Carries a room-kind marker (`base`, `static`, `dynamic`).
        - Owns a room-local workstation canvas for saved bindings and active
          target state.
        - Owns a room-local command system for controlled getter/execute
          operations above the viewer/workstation split.
        - Builds the command system through a room-owned factory seam so room
          subclasses can compose a mode-specific command surface without
          changing the public `space.command_system` access pattern.
        - Owns a room-local `RiftMemorySystem` for sequencing and shared memory
          context.
        - Owns one room-local `RiftEventSystem` for outbound runtime-event
          publication.
        - Does not yet implement full action history, memory points,
          checkpoints, or disposition semantics.

    Room Mode Matrix:
        Shared base behavior:
        - Every room owns a workstation, command system, viewer attachment
          point, room-local memory system, and one room-local event system.
        - Lower Melder frame/runtime truth still governs what actually works on
          automatic versus dynamic frames.

        `static`:
        - Uses the static viewer/command specializations.
        - Spell-facing room surface is live-only and more restrictive.
        - Workstation defaults weak when binds omit `weak_ref`.

        `capability`:
        - Uses the broad manual runtime command surface.
        - Workstation defaults strong when binds omit `weak_ref`.
        - No codegen distinction is added here.

        `dynamic`:
        - Currently uses the same broad manual runtime command surface as
          capability.
        - Intended to be the later codegen-oriented room.

    Lifecycle:
        Owned by a `Rift`. Cleanup clears room-local fields and cleans
        the owned event system plus the owned workstation.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_space_id",
        "_space_name",
        "_owner_rift_id",
        "_lock",
        "_space_kind",
        "_metadata",
        "_frame_viewer",
        "_rift_gate",
        "_projection_sets_by_frame_name",
        "_memory_system",
        "_event_system",
        "_workstation",
        "_command_system",
    ]

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            space_kind: str = "base",
            metadata: Optional[Dict[str, object]] = None,
            rift_gate: Optional[IRiftGate] = None,
            space_id: Optional[str] = None,
    ) -> None:
        """
        Internal

        Initialize the base room.

        Args:
            owner_rift_id:
                Canonical owning Rift id.
            space_name:
                Optional stable room name.
            space_kind:
                Room-kind discriminator.
            metadata:
                Extensible room-local metadata.
            rift_gate:
                Optional Rift-owned gate for room-local admission control.
            space_id:
                Optional explicit room id. When omitted a new id is created.

        Returns:
            None.

        Contract:
            - Copies incoming metadata into a room-owned mutable dict.
            - Creates and owns one room-local `RiftEventSystem`.

        Raises:
            ValueError: If `owner_rift_id` is empty.
        """
        super().__init__()
        if not owner_rift_id:
            raise ValueError("owner_rift_id cannot be empty.")

        self._space_id: str = space_id or IDBuilder.create_id()
        self._space_name: Optional[str] = space_name
        self._owner_rift_id: str = owner_rift_id
        self._lock: threading.RLock = threading.RLock()
        self._space_kind: str = space_kind
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._frame_viewer: Optional[FrameViewer] = None
        self._rift_gate: Optional[IRiftGate] = rift_gate
        self._projection_sets_by_frame_name: Dict[str, FrameProjectionSet] = {}
        self._memory_system: IRiftMemorySystem = RiftMemorySystem(
            rift_id=self._owner_rift_id,
            space_type=self._space_kind,
        )
        self._event_system: IRiftEventSystem = RiftEventSystem(
            rift_id=self._owner_rift_id,
            space_id=self._space_id,
            space_kind=self._space_kind,
        )
        self._workstation: Workstation = Workstation(
            self._space_id,
            default_weak_ref_bindings=(
                space_kind == RiftSpaceType.static.value
            ),
            event_publisher=self._publish_runtime_event,
        )
        self._command_system: CommandSystem = self._create_command_system()

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup room-local state and the owned event system.

        Contract:
            - Cleans the owned event system before dropping references.
            - Clears room identity metadata and room-local metadata maps.
            - Leaves the room unusable after cleanup.

        Returns:
            None.
        """
        if self._cleaned:
            return
        lock = self._lock
        with lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._frame_viewer is not None:
                self._frame_viewer.cleanup()
            self._command_system.cleanup()
            self._workstation.cleanup()
            self._event_system.cleanup()
            self._space_name = None
            self._owner_rift_id = None
            self._space_kind = None
            self._metadata.clear()
            self._metadata = None
            self._frame_viewer = None
            self._rift_gate = None
            for projection_set in self._projection_sets_by_frame_name.values():
                projection_set.cleanup()
            self._projection_sets_by_frame_name.clear()
            self._projection_sets_by_frame_name = None
            self._memory_system.cleanup()
            self._memory_system = None
            self._event_system = None
            self._workstation = None
            self._command_system = None
            self._space_id = None
        self._lock = None

    @property
    def space_id(self) -> str:
        """
        Purpose:
            Return the canonical room id.

        Returns:
            str: The room id.
        """
        self.check_cleaned()
        with self._lock:
            return self._space_id

    @property
    def space_name(self) -> Optional[str]:
        """
        Purpose:
            Return the optional stable room name.

        Returns:
            Optional[str]: Room name, if one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._space_name

    @property
    def owner_rift_id(self) -> str:
        """
        Purpose:
            Return the canonical owning Rift id.

        Returns:
            str: Owning Rift id.
        """
        self.check_cleaned()
        with self._lock:
            return self._owner_rift_id

    @property
    def space_kind(self) -> str:
        """
        Purpose:
            Return the room-kind discriminator.

        Returns:
            str: Room kind label.
        """
        self.check_cleaned()
        with self._lock:
            return self._space_kind

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Purpose:
            Return the room-local metadata map.

        Contract:
            Returns the live mutable metadata dict owned by this room, not a
            detached copy.

        Returns:
            Dict[str, object]: Extensible room metadata.
        """
        self.check_cleaned()
        with self._lock:
            return self._metadata

    @property
    def frame_viewer(self) -> Optional[FrameViewer]:
        """
        Purpose:
            Return the optional attached frame-surface viewer for this space.

        Returns:
            Optional[FrameViewer]: Attached frame viewer when one exists.
        """
        self.check_cleaned()
        with self._lock:
            return self._frame_viewer

    @property
    def rift_gate(self) -> Optional[IRiftGate]:
        """
        Purpose:
            Return the optional Rift-owned gate bound to this room.

        Returns:
            Optional[IRiftGate]: Bound Rift gate when present.
        """
        self.check_cleaned()
        with self._lock:
            return self._rift_gate

    @property
    def workstation(self) -> Workstation:
        """
        Purpose:
            Return the room-local workstation canvas.

        Contract:
            - Returns the live workstation object owned by this room.
            - The returned workstation is cleaned with the room and is not a
              detached copy.

        Returns:
            Workstation: Room-local workstation canvas.
        """
        self.check_cleaned()
        with self._lock:
            return self._workstation

    @property
    def command_system(self) -> CommandSystem:
        """
        Purpose:
            Return the room-local command system.

        Contract:
            - Returns the live command system object owned by this room.
            - The returned command system is cleaned with the room and is not a
              detached copy.

        Returns:
            CommandSystem: Room-local command system.
        """
        self.check_cleaned()
        with self._lock:
            return self._command_system

    def _create_command_system(self) -> CommandSystem:
        """
        Build the room-local command system owned by this space.

        Contract:
            - Base `RiftSpace` composes the shared generic command surface.
            - Room subclasses may override this factory to return a
              mode-specific command-system subclass while preserving the same
              public `space.command_system` contract.

        Returns:
            CommandSystem: Room-local command system for this space.
        """
        return CommandSystem(
            space=self,
            workstation=self._workstation,
        )

    def _build_frame_viewer(
            self,
            *,
            viewer_profile_name: str = "general",
            selected_profile_names_by_frame_name: Optional[Dict[str, str]] = None,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> FrameViewer:
        """
        Build one generic room-owned viewer from the installed projections.

        Purpose:
            Assemble the live viewer surface directly inside the room from the
            room-owned `ViewProjection` objects.

        Contract:
            - Requires at least one installed projection set.
            - Clones detached ACL configuration and compiled access-surface
              state for viewer ownership.
            - Passes the room-owned `RiftGate` into the viewer constructor.
            - Does not mutate the installed projection objects.

        Args:
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.
            selected_profile_names_by_frame_name:
                Optional explicit selected viewer profile names keyed by frame.
            default_view_frame_name:
                Optional explicit default frame name for the viewer.
            metadata:
                Optional metadata overlay merged onto room-derived viewer
                metadata.

        Returns:
            FrameViewer: Detached generic viewer built from installed
            projections.
        """
        self.check_cleaned()
        with self._lock:
            projection_sets_by_frame_name = dict(self._projection_sets_by_frame_name)
            rift_gate = self._rift_gate
        if len(projection_sets_by_frame_name) == 0:
            raise ValueError("RiftSpace has no installed projection sets.")
        viewer_profile_builder = FrameViewerProfileBuilder()
        viewer_profile = viewer_profile_builder.get_required_profile(
            viewer_profile_name
        )
        active_profiles_by_name = {
            profile_name: viewer_profile_builder.get_required_profile(
                profile_name
            ).clone()
            for profile_name in viewer_profile_builder.list_profile_names()
        }
        normalized_selected_profile_names = (
            dict(selected_profile_names_by_frame_name)
            if selected_profile_names_by_frame_name is not None
            else {}
        )
        for frame_name in projection_sets_by_frame_name.keys():
            if frame_name not in normalized_selected_profile_names:
                normalized_selected_profile_names[frame_name] = viewer_profile.name
        selected_contract_names_by_frame_name = {
            frame_name: dict(
                projection_set.metadata.get(
                    "selected_contract_names",
                    {
                        "view": "default",
                        "command": "default",
                        "codegen": "default",
                    },
                )
            )
            for frame_name, projection_set in projection_sets_by_frame_name.items()
        }
        viewer_metadata = {
            "frame_count": len(projection_sets_by_frame_name),
            "available_view_count": len(projection_sets_by_frame_name),
            "assigned_frame_names": tuple(projection_sets_by_frame_name.keys()),
            "acl_selection_by_frame_name": selected_contract_names_by_frame_name,
            "contract_names_by_frame_name": selected_contract_names_by_frame_name,
            "viewer_profile_name": viewer_profile.name,
            "viewer_profile_version": viewer_profile.version,
            "default_grouping": viewer_profile.default_grouping,
            "default_detail_level": viewer_profile.default_detail_level,
            "enabled_helpers": viewer_profile.enabled_helpers,
            "tool_names": viewer_profile.list_tool_names(),
            "tool_handler_names_by_name": viewer_profile.tool_handler_names_by_name,
        }
        if metadata is not None:
            viewer_metadata.update(metadata)
        try:
            return FrameViewer(
                profile_builder=FrameViewerProfileBuilder(),
                active_profiles_by_name=active_profiles_by_name,
                default_profile_name=viewer_profile.name,
                frame_descriptors_by_name={
                    frame_name: projection_set.view_projection.frame_descriptor
                    for frame_name, projection_set in projection_sets_by_frame_name.items()
                },
                frame_acl_configurations_by_frame_name={
                    frame_name: FrameViewer._clone_frame_acl_configuration(
                        projection_set.view_projection.frame_acl_configuration,
                        reason="rift_space_viewer_clone",
                    )
                    for frame_name, projection_set in projection_sets_by_frame_name.items()
                },
                compiled_access_surfaces_by_frame_name={
                    frame_name: FrameViewer._clone_compiled_access_surface(
                        projection_set.view_projection.compiled_access_surface
                    )
                    for frame_name, projection_set in projection_sets_by_frame_name.items()
                },
                selected_profile_names_by_frame_name=normalized_selected_profile_names,
                default_view_frame_name=default_view_frame_name,
                rift_gate=rift_gate,
                metadata=viewer_metadata,
            )
        finally:
            viewer_profile_builder.cleanup()

    def _rebuild_frame_viewer(
            self,
            *,
            viewer_profile_name: str = "general",
            selected_profile_names_by_frame_name: Optional[Dict[str, str]] = None,
            default_view_frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> FrameViewer:
        """
        Build and install one fresh room-owned viewer from installed projections.

        Args:
            viewer_profile_name:
                Viewer profile name applied to the hosted viewer.
            selected_profile_names_by_frame_name:
                Optional explicit selected viewer profile names keyed by frame.
            default_view_frame_name:
                Optional explicit default frame name for the viewer.
            metadata:
                Optional metadata overlay merged onto room-derived viewer
                metadata.

        Returns:
            FrameViewer: Installed room-owned viewer.
        """
        frame_viewer = self._build_frame_viewer(
            viewer_profile_name=viewer_profile_name,
            selected_profile_names_by_frame_name=selected_profile_names_by_frame_name,
            default_view_frame_name=default_view_frame_name,
            metadata=metadata,
        )
        self._replace_frame_viewer(frame_viewer)
        return frame_viewer

    def _replace_frame_viewer(self, frame_viewer: FrameViewer) -> None:
        """
        Internal

        Replace the currently attached frame-surface viewer for this room.

        Purpose:
            Apply one newly built viewer object to the room's live state without
            exposing viewer replacement as a public room API seam.

        Contract:
            - Requires a concrete `FrameViewer` instance.
            - Cleans the previously attached viewer when the replacement object
              is different.
            - Stores the replacement viewer as the room's current viewer.

        Args:
            frame_viewer:
                Replacement viewer to store on this room.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if not isinstance(frame_viewer, FrameViewer):
                raise TypeError("frame_viewer must be a FrameViewer.")
            if self._frame_viewer is not None and self._frame_viewer is not frame_viewer:
                self._frame_viewer.cleanup()
            self._frame_viewer = frame_viewer

    def _clear_frame_viewer(self) -> None:
        """
        Internal

        Clear and cleanup the currently attached frame-surface viewer.

        Purpose:
            Remove the room's current viewer as part of internal room lifecycle
            management without exposing a public detach seam.

        Contract:
            - Safe to call when no viewer is attached.
            - Cleans the currently attached viewer before dropping the
              reference.
            - Leaves the room with no attached viewer afterwards.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._frame_viewer is None:
                return
            self._frame_viewer.cleanup()
            self._frame_viewer = None

    def replace_projection_sets(
            self,
            projection_sets_by_frame_name: Dict[str, FrameProjectionSet],
            *,
            merge: bool = False,
    ) -> None:
        """
        Replace the room-owned projection sets.

        Args:
            projection_sets_by_frame_name:
                Fresh projection sets keyed by frame name.
            merge:
                When True, replace only the named incoming projection sets and
                preserve unaffected installed sets.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if merge:
                merged_projection_sets_by_frame_name = dict(
                    self._projection_sets_by_frame_name
                )
                for frame_name, projection_set in (
                        projection_sets_by_frame_name.items()
                ):
                    current_projection_set = merged_projection_sets_by_frame_name.get(
                        frame_name
                    )
                    if (
                            current_projection_set is not None
                            and current_projection_set is not projection_set
                    ):
                        current_projection_set.cleanup()
                    merged_projection_sets_by_frame_name[frame_name] = projection_set
                self._projection_sets_by_frame_name = (
                    merged_projection_sets_by_frame_name
                )
                return
            for projection_set in self._projection_sets_by_frame_name.values():
                projection_set.cleanup()
            self._projection_sets_by_frame_name = dict(projection_sets_by_frame_name)

    def get_required_frame_projection_set(self, frame_name: str) -> FrameProjectionSet:
        """
        Return one required projection set by frame name.

        Args:
            frame_name:
                Target frame name.

        Returns:
            FrameProjectionSet: Required projection set.
        """
        self.check_cleaned()
        try:
            return self._projection_sets_by_frame_name[frame_name]
        except KeyError as exc:
            raise ValueError(
                "Projection set for frame '{0}' was not found.".format(frame_name)
            ) from exc

    def get_required_view_projection(self, frame_name: str):
        """
        Return one required view projection.

        Args:
            frame_name:
                Target frame name.

        Returns:
            ViewProjection: Required view projection.
        """
        return self.get_required_frame_projection_set(frame_name).view_projection

    def get_required_command_projection(self, frame_name: str):
        """
        Return one required command projection.

        Args:
            frame_name:
                Target frame name.

        Returns:
            CommandProjection: Required command projection.
        """
        return self.get_required_frame_projection_set(frame_name).command_projection

    def get_required_codegen_projection(self, frame_name: str):
        """
        Return one required codegen projection.

        Args:
            frame_name:
                Target frame name.

        Returns:
            CodegenProjection: Required codegen projection.
        """
        return self.get_required_frame_projection_set(frame_name).codegen_projection

    @property
    def event_system(self) -> IRiftEventSystem:
        """
        Purpose:
            Return the room-local event system.

        Contract:
            - Returns the live `RiftEventSystem` owned by this room.
            - The returned object is cleaned with the room.

        Returns:
            IRiftEventSystem: Room-local event system.
        """
        self.check_cleaned()
        with self._lock:
            return self._event_system

    @property
    def memory_system(self) -> IRiftMemorySystem:
        """
        Purpose:
            Return the room-local memory sequencing system.

        Contract:
            - Returns the live `RiftMemorySystem` owned by this room.
            - The returned object is cleaned with the room.

        Returns:
            IRiftMemorySystem: Room-local memory system.
        """
        self.check_cleaned()
        with self._lock:
            return self._memory_system

    def _publish_runtime_event(self, event_payload: Dict[str, object]) -> None:
        """
        Adapt one producer payload into a room-local event emission.

        Args:
            event_payload:
                Event payload contributed by a room-local producer.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            event_system = self._event_system
        normalized_payload = dict(event_payload)
        event_type = normalized_payload.pop("event_type", "runtime_event")
        frame_name = normalized_payload.pop("frame_name", None)
        metadata = normalized_payload.pop("metadata", None)
        event_system.create_and_emit_event(
            event_type,
            payload=normalized_payload,
            frame_name=frame_name,
            metadata=metadata,
        )
