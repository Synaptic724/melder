import threading
from typing import Callable, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.command_system.command_system import (
    CommandSystem,
)
from melder.aether.nexus.rift.rift_space.rift_event import RiftEvent
from melder.aether.nexus.rift.rift_space.workstation import Workstation
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.interfaces import (
    IRiftEvent,
    IRiftEventConfiguration,
    IRiftSpace,
)
from melder.aether.nexus.rift.rift_space.rift_event_configuration import RiftEventConfiguration


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
        - Owns a room-local event callback registry for outbound runtime-event
          publication.
        - Carries a room-level event configuration seam for future
          event-hook enrichment.
        - Does not yet implement full action history, memory points,
          checkpoints, or disposition semantics.

    Room Mode Matrix:
        Shared base behavior:
        - Every room owns a workstation, command system, viewer attachment
          point, selected-target state, and room-local event callback
          registry/config.
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
        the attached `RiftEventConfiguration` plus the owned workstation.
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
        "_selected_target_ids_by_frame_name",
        "_event_callbacks_by_subscription_id",
        "_workstation",
        "_command_system",
        "_event_configuration",
    ]

    def __init__(
            self,
            owner_rift_id: str,
            *,
            space_name: Optional[str] = None,
            space_kind: str = "base",
            metadata: Optional[Dict[str, object]] = None,
            frame_viewer: Optional[FrameViewer] = None,
            event_configuration: Optional[IRiftEventConfiguration] = None,
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
            frame_viewer:
                Optional attached frame-surface viewer for this space.
            event_configuration:
                Optional room-level event configuration.
            space_id:
                Optional explicit room id. When omitted a new id is created.

        Returns:
            None.

        Contract:
            - Copies incoming metadata into a room-owned mutable dict.
            - Uses the supplied event configuration when provided.
            - Creates and owns a default `RiftEventConfiguration` when none is
              supplied.

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
        if frame_viewer is not None and not isinstance(frame_viewer, FrameViewer):
            raise TypeError("frame_viewer must be a FrameViewer when provided.")
        self._frame_viewer: Optional[FrameViewer] = frame_viewer
        self._selected_target_ids_by_frame_name: Dict[str, List[str]] = {}
        self._event_callbacks_by_subscription_id: Dict[
            str,
            Callable[[IRiftEvent], None],
        ] = {}
        self._workstation: Workstation = Workstation(
            self._space_id,
            default_weak_ref_bindings=(
                space_kind == RiftSpaceType.static.value
            ),
            event_publisher=self._publish_runtime_event,
        )
        self._command_system: CommandSystem = self._create_command_system()
        self._event_configuration: IRiftEventConfiguration = (
            event_configuration if event_configuration is not None else RiftEventConfiguration()
        )

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup room-local state and the attached event
        configuration.

        Contract:
            - Cleans the owned event configuration before dropping references.
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
            self._event_configuration.cleanup()
            self._space_name = None
            self._owner_rift_id = None
            self._space_kind = None
            self._metadata.clear()
            self._metadata = None
            self._frame_viewer = None
            self._selected_target_ids_by_frame_name.clear()
            self._selected_target_ids_by_frame_name = None
            self._event_callbacks_by_subscription_id.clear()
            self._event_callbacks_by_subscription_id = None
            self._workstation = None
            self._command_system = None
            self._event_configuration = None
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

    def attach_frame_viewer(self, frame_viewer: FrameViewer) -> None:
        """
        Internal

        Attach or replace the frame-surface viewer for this space.

        Args:
            frame_viewer:
                Viewer to attach to this space.

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

    def detach_frame_viewer(self) -> None:
        """
        Internal

        Remove and cleanup the attached frame-surface viewer when present.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._frame_viewer is None:
                return
            self._frame_viewer.cleanup()
            self._frame_viewer = None

    def list_frame_names(self) -> List[str]:
        """
        Internal

        Return the assigned frame names visible through the attached viewer.

        Returns:
            List[str]: Assigned frame names.
        """
        self.check_cleaned()
        with self._lock:
            return self.get_required_frame_viewer().list_frame_names()

    def list_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[object]:
        """
        Internal

        Return available targets from the attached viewer.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.
            profile_name:
                Optional active local view profile name.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[object]: Available targets from the attached viewer.
        """
        self.check_cleaned()
        with self._lock:
            return self.get_required_frame_viewer().execute_method(
                "list_targets",
                frame_name=frame_name,
                profile_name=profile_name,
                source_kind=source_kind,
            )

    def describe_available_targets(
            self,
            *,
            frame_name: Optional[str] = None,
            profile_name: Optional[str] = None,
            source_kind: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Internal

        Return profile-shaped target descriptions from the attached viewer.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default
                assigned view is used.
            profile_name:
                Optional active local view profile name.
            source_kind:
                Optional target-kind filter.

        Returns:
            List[Dict[str, object]]: Available target descriptions.
        """
        self.check_cleaned()
        with self._lock:
            return self.get_required_frame_viewer().execute_method(
                "describe_targets",
                frame_name=frame_name,
                profile_name=profile_name,
                source_kind=source_kind,
            )

    def get_required_frame_viewer(self) -> FrameViewer:
        """
        Internal

        Return the attached frame viewer or raise.

        Returns:
            FrameViewer: Attached frame viewer.
        """
        self.check_cleaned()
        with self._lock:
            if self._frame_viewer is None:
                raise ValueError(
                    "RiftSpace '{0}' has no attached frame viewer.".format(self._space_id)
                )
            return self._frame_viewer

    def list_selected_target_ids(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[str]:
        """
        Internal

        Return selected target ids for one frame or for the default view frame.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default viewer
                frame is used.

        Returns:
            List[str]: Selected target ids.
        """
        self.check_cleaned()
        with self._lock:
            selected_frame_name = (
                frame_name
                if frame_name is not None
                else self.get_required_frame_viewer().default_view_frame_name
            )
            if selected_frame_name is None:
                raise ValueError("RiftSpace has no default selected frame.")
            return list(self._selected_target_ids_by_frame_name.get(selected_frame_name, []))

    def select_target(
            self,
            target_id: str,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Internal

        Select one available target through the attached viewer.

        Args:
            target_id:
                Available target id to select.
            frame_name:
                Optional assigned frame name. When omitted, the default viewer
                frame is used.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if not target_id:
                raise ValueError("target_id cannot be empty.")
            viewer = self.get_required_frame_viewer()
            selected_frame_name = frame_name or viewer.default_view_frame_name
            if selected_frame_name is None:
                raise ValueError("RiftSpace has no default selected frame.")
            target_ids = [
                frame_link.link_id
                for frame_link in viewer.execute_method(
                    "list_targets",
                    frame_name=selected_frame_name
                )
            ]
            if target_id not in target_ids:
                raise ValueError(
                    "Target '{0}' was not found in frame '{1}'.".format(
                        target_id,
                        selected_frame_name,
                    )
                )
            selected_target_ids = self._selected_target_ids_by_frame_name.setdefault(
                selected_frame_name,
                [],
            )
            if target_id in selected_target_ids:
                return
            selected_target_ids.append(target_id)

    def clear_selected_targets(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> None:
        """
        Internal

        Clear selected target ids for one frame or for every frame.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, clears every frame's
                selected target ids.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if frame_name is None:
                self._selected_target_ids_by_frame_name.clear()
                return
            self._selected_target_ids_by_frame_name.pop(frame_name, None)

    def describe_selected_targets(
            self,
            *,
            frame_name: Optional[str] = None,
    ) -> List[Dict[str, object]]:
        """
        Internal

        Return descriptions for the currently selected targets.

        Args:
            frame_name:
                Optional assigned frame name. When omitted, the default viewer
                frame is used.

        Returns:
            List[Dict[str, object]]: Selected target descriptions.
        """
        self.check_cleaned()
        with self._lock:
            viewer = self.get_required_frame_viewer()
            selected_frame_name = frame_name or viewer.default_view_frame_name
            if selected_frame_name is None:
                raise ValueError("RiftSpace has no default selected frame.")
            target_descriptions_by_id = {
                description["target_id"]: description
                for description in viewer.execute_method(
                    "describe_targets",
                    frame_name=selected_frame_name,
                )
            }
            selected_descriptions: List[Dict[str, object]] = []
            for target_id in self._selected_target_ids_by_frame_name.get(selected_frame_name, []):
                try:
                    description = target_descriptions_by_id[target_id]
                except KeyError as exc:
                    raise ValueError(
                        "Target '{0}' was not found in frame '{1}'.".format(
                            target_id,
                            selected_frame_name,
                        )
                    ) from exc
                selected_descriptions.append(
                    {
                        "frame_name": selected_frame_name,
                        "target_id": description["target_id"],
                        "source_kind": description["source_kind"],
                        "source_id": description["source_id"],
                        "display_name": description["display_name"],
                    }
                )
            return selected_descriptions

    @property
    def event_configuration(self) -> IRiftEventConfiguration:
        """
        Purpose:
            Return the room-level event configuration.

        Contract:
            - Returns the room-local configuration seam for future
              action/memory enrichment, not a global ARS configuration object.
            - The returned object is owned by this room and cleaned with it.

        Returns:
            IRiftEventConfiguration: The room event configuration object.
        """
        self.check_cleaned()
        with self._lock:
            return self._event_configuration

    def register_event_callback(
            self,
            callback: Callable[[IRiftEvent], None],
    ) -> str:
        """
        Register one event callback for this room.

        Args:
            callback:
                Callback invoked once per emitted event.

        Returns:
            str: Stable subscription id for later unregistration.
        """
        self.check_cleaned()
        if not callable(callback):
            raise TypeError("callback must be callable.")
        with self._lock:
            subscription_id = IDBuilder.create_id()
            self._event_callbacks_by_subscription_id[subscription_id] = callback
            return subscription_id

    def unregister_event_callback(self, subscription_id: str) -> None:
        """
        Remove one event callback subscription by id.

        Args:
            subscription_id:
                Subscription id returned by `register_event_callback(...)`.

        Returns:
            None.
        """
        self.check_cleaned()
        if not subscription_id:
            raise ValueError("subscription_id cannot be empty.")
        with self._lock:
            self._event_callbacks_by_subscription_id.pop(subscription_id, None)

    def create_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> IRiftEvent:
        """
        Create one room-local runtime event without emitting it.

        Args:
            event_type:
                Stable event type name.
            payload:
                Optional payload mapping.
            frame_name:
                Optional related frame name.
            metadata:
                Optional metadata mapping.

        Returns:
            IRiftEvent: New event object.
        """
        self.check_cleaned()
        if not event_type:
            raise ValueError("event_type cannot be empty.")
        return RiftEvent(
            event_type=event_type,
            rift_id=self._owner_rift_id,
            space_id=self._space_id,
            space_kind=self._space_kind,
            frame_name=frame_name,
            payload=payload,
            metadata=metadata,
        )

    def emit_event(self, event: IRiftEvent) -> None:
        """
        Emit one runtime event to all registered callbacks.

        Args:
            event:
                Event object to emit.

        Returns:
            None.
        """
        self.check_cleaned()
        if not isinstance(event, IRiftEvent):
            raise TypeError("event must satisfy IRiftEvent.")
        with self._lock:
            callbacks = list(self._event_callbacks_by_subscription_id.values())
        for callback in callbacks:
            callback(event)

    def create_and_emit_event(
            self,
            event_type: str,
            *,
            payload: Optional[Dict[str, object]] = None,
            frame_name: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> IRiftEvent:
        """
        Create one runtime event and emit it immediately.

        Args:
            event_type:
                Stable event type name.
            payload:
                Optional payload mapping.
            frame_name:
                Optional related frame name.
            metadata:
                Optional metadata mapping.

        Returns:
            IRiftEvent: Emitted event object.
        """
        event = self.create_event(
            event_type,
            payload=payload,
            frame_name=frame_name,
            metadata=metadata,
        )
        self.emit_event(event)
        return event

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
        normalized_payload = dict(event_payload)
        event_type = normalized_payload.pop("event_type", "runtime_event")
        frame_name = normalized_payload.pop("frame_name", None)
        metadata = normalized_payload.pop("metadata", None)
        self.create_and_emit_event(
            event_type,
            payload=normalized_payload,
            frame_name=frame_name,
            metadata=metadata,
        )
