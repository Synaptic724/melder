import threading
from typing import Any, Dict, List, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
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
        - Carries a room-kind marker (`base`, `static`, `capability`,
          `codegen`).
        - Owns a room-local workstation canvas for saved bindings and active
          target state.
        - Owns a room-local command system for controlled getter/execute
          operations above the viewer/workstation split.
        - Builds the command system through a room-owned factory seam so room
          subclasses can compose a mode-specific command surface without
          changing the public `space.command_system` access pattern.
        - Owns a durable attached `FrameViewer` asset.
        - Acts as the asset host, not the projection manager.
        - Owns a room-local `RiftMemorySystem` for sequencing and shared memory
          context.
        - Owns one room-local `RiftEventSystem` for outbound runtime-event
          publication.
        - Does not yet implement full action history, memory points,
          checkpoints, or disposition semantics.

    Room Mode Matrix:
        Shared base behavior:
        - Every room owns a workstation, command system, viewer asset,
          room-local memory system, and one room-local event system.
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

        `codegen`:
        - Currently uses the same broad manual runtime command surface as
          capability.
        - Intended to be the later codegen-oriented room.

    Lifecycle:
        Owned by a `Rift`. Cleanup clears room-local fields and the owned
        viewer, workstation, memory system, and event system.
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
        "_memory_system",
        "_event_system",
        "_workstation",
        "_command_system",
    ]

    def __init__(
            self,
            owner_rift_id: str,
            *,
            rift: Any,
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
            rift:
                Owning `Rift` that manages projection-driven asset updates.
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
            - Creates and owns one durable room-local `FrameViewer` asset.
            - Creates and owns one room-local `RiftEventSystem`.

        Raises:
            ValueError: If `owner_rift_id` is empty.
        """
        super().__init__()
        if not owner_rift_id:
            raise ValueError("owner_rift_id cannot be empty.")
        if rift is None:
            raise TypeError("rift cannot be None.")

        self._space_id: str = space_id or IDBuilder.create_id()
        self._space_name: Optional[str] = space_name
        self._owner_rift_id: str = owner_rift_id
        self._lock: threading.RLock = threading.RLock()
        self._space_kind: str = space_kind
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._rift_gate: Optional[IRiftGate] = rift_gate
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
        self._command_system: CommandSystem = self._create_command_system(rift)
        if space_kind == RiftSpaceType.static.value:
            from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
                StaticFrameViewer,
            )
            self._frame_viewer = StaticFrameViewer(
                rift=rift,
            )
        else:
            self._frame_viewer = FrameViewer(
                rift=rift,
            )

    def cleanup(self) -> None:
        """
        Internal

        Idempotently cleanup room-local state and the owned event system.

        Contract:
            - Cleans the owned durable viewer asset.
            - Cleans the owned command system, workstation, memory system, and
              event system before dropping references.
            - Clears room identity metadata and room-local metadata maps after
              owned child cleanup completes.
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
    def frame_viewer(self) -> FrameViewer:
        """
        Purpose:
            Return the attached frame-surface viewer for this space.

        Contract:
            - Active rooms always own one viewer asset.
            - The viewer may host zero frames before any projection exists.

        Returns:
            FrameViewer: Attached frame viewer for this active space.
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

    def _create_command_system(self, rift: Any) -> CommandSystem:
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
            rift=rift,
            space=self,
            workstation=self._workstation,
        )

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
