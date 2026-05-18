from contextlib import contextmanager
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
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
from melder.utilities.interfaces.icommandsystem import ICommandSystem
from melder.utilities.interfaces.irifteventsystem import IRiftEventSystem
from melder.utilities.interfaces.iriftgate import IRiftGate
from melder.utilities.interfaces.iriftmemorysystem import IRiftMemorySystem
from melder.utilities.interfaces.iriftspace import IRiftSpace


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
        "_id",
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
        "_pre_category_hooks_by_name",
        "_post_category_hooks_by_name",
        "_pre_action_hooks_by_key",
        "_post_action_hooks_by_key",
        "_action_hook_keys_by_subscription_id",
        "_action_hook_depth_by_category",
    ]
    _ACTION_HOOK_CATEGORIES: Tuple[str, ...] = (
        "command",
        "viewer",
        "codegen",
    )

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

        self._id: str = space_id or IDBuilder.create_id()
        self._space_name: Optional[str] = space_name
        self._owner_rift_id: str = owner_rift_id
        self._lock: threading.RLock = threading.RLock()
        self._space_kind: str = space_kind
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}
        self._rift_gate: Optional[IRiftGate] = rift_gate
        self._memory_system: RiftMemorySystem = RiftMemorySystem(
            rift_id=self._owner_rift_id,
            space_type=self._space_kind,
        )
        self._event_system: RiftEventSystem = RiftEventSystem(
            rift_id=self._owner_rift_id,
            space_id=self._id,
            space_kind=self._space_kind,
        )
        self._workstation: Workstation = Workstation(
            self._id,
            default_weak_ref_bindings=(
                space_kind == RiftSpaceType.static.value
            ),
            event_publisher=self._publish_runtime_event,
        )
        self._command_system: CommandSystem = self._create_command_system(rift)
        self._pre_category_hooks_by_name: Dict[
            str,
            Dict[str, Callable[[], None]],
        ] = {}
        self._post_category_hooks_by_name: Dict[
            str,
            Dict[str, Callable[[], None]],
        ] = {}
        self._pre_action_hooks_by_key: Dict[
            Tuple[str, str],
            Dict[str, Callable[[], None]],
        ] = {}
        self._post_action_hooks_by_key: Dict[
            Tuple[str, str],
            Dict[str, Callable[[], None]],
        ] = {}
        self._action_hook_keys_by_subscription_id: Dict[
            str,
            Tuple[str, str, str],
        ] = {}
        self._action_hook_depth_by_category: Dict[str, int] = {
            category_name: 0
            for category_name in self._ACTION_HOOK_CATEGORIES
        }
        frame_viewer: FrameViewer
        if space_kind == RiftSpaceType.static.value:
            from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
                StaticFrameViewer,
            )
            frame_viewer = StaticFrameViewer(
                rift=rift,
                action_hook_scope_factory=self._entered_action_hook_scope,
            )
        else:
            frame_viewer = FrameViewer(
                rift=rift,
                action_hook_scope_factory=self._entered_action_hook_scope,
            )
        self._frame_viewer = frame_viewer

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
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            if self._frame_viewer is not None:
                self._frame_viewer.cleanup()
            self._command_system.cleanup()
            self._workstation.cleanup()
            self._event_system.cleanup()
            self._pre_category_hooks_by_name.clear()
            self._post_category_hooks_by_name.clear()
            self._pre_action_hooks_by_key.clear()
            self._post_action_hooks_by_key.clear()
            self._action_hook_keys_by_subscription_id.clear()
            self._action_hook_depth_by_category.clear()
            self._metadata.clear()
            self._memory_system.cleanup()

            del self._space_name
            del self._owner_rift_id
            del self._space_kind
            del self._metadata
            del self._frame_viewer
            del self._rift_gate
            del self._memory_system
            del self._event_system
            del self._workstation
            del self._command_system
            del self._pre_category_hooks_by_name
            del self._post_category_hooks_by_name
            del self._pre_action_hooks_by_key
            del self._post_action_hooks_by_key
            del self._action_hook_keys_by_subscription_id
            del self._action_hook_depth_by_category
            del self._id

        del self._lock

    def register_category_pre_hook(
            self,
            category: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one category-wide pre hook.

        Args:
            category:
                Action category (`command`, `viewer`, or `codegen`).
            callback:
                Zero-argument callback to run before any top-level action in
                the category.

        Returns:
            str: Stable subscription id for later unregistration.
        """
        self.check_cleaned()
        return self._register_category_hook(
            phase="pre",
            category=category,
            callback=callback,
        )

    def register_category_post_hook(
            self,
            category: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one category-wide post hook.

        Args:
            category:
                Action category (`command`, `viewer`, or `codegen`).
            callback:
                Zero-argument callback to run after any top-level action in the
                category.

        Returns:
            str: Stable subscription id for later unregistration.
        """
        self.check_cleaned()
        return self._register_category_hook(
            phase="post",
            category=category,
            callback=callback,
        )

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
            return self._id

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
    def command_system(self) -> ICommandSystem:
        """
        Purpose:
            Return the room-local command system.

        Contract:
            - Returns the live command system object owned by this room.
            - The returned command system is cleaned with the room and is not a
              detached copy.

        Returns:
            ICommandSystem: Room-local command system.
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
        self.check_cleaned()
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

    def register_action_pre_hook(
            self,
            category: str,
            action_name: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one pre-action hook for one room action category and name.

        Args:
            category:
                Action category (`command`, `viewer`, or `codegen`).
            action_name:
                Stable public action name.
            callback:
                Zero-argument callback to run before the action body.

        Returns:
            str: Stable subscription id for later unregistration.
        """
        return self._register_action_hook(
            phase="pre",
            category=category,
            action_name=action_name,
            callback=callback,
        )

    def register_action_post_hook(
            self,
            category: str,
            action_name: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one post-action hook for one room action category and name.

        Args:
            category:
                Action category (`command`, `viewer`, or `codegen`).
            action_name:
                Stable public action name.
            callback:
                Zero-argument callback to run after the action exits.

        Returns:
            str: Stable subscription id for later unregistration.
        """
        self.check_cleaned()
        return self._register_action_hook(
            phase="post",
            category=category,
            action_name=action_name,
            callback=callback,
        )

    def unregister_action_hook(self, subscription_id: str) -> None:
        """
        Remove one action-hook subscription by id.

        Args:
            subscription_id:
                Stable subscription id returned by hook registration.

        Returns:
            None.
        """
        self.check_cleaned()
        if not subscription_id:
            raise ValueError("subscription_id cannot be empty.")
        with self._lock:
            hook_key = self._action_hook_keys_by_subscription_id.pop(
                subscription_id,
                None,
            )
            if hook_key is None:
                return
            phase, category, action_name = hook_key
            if action_name == "*":
                registry = self._get_category_hook_registry(phase)
                category_hooks = registry.get(category)
                if category_hooks is None:
                    return
                category_hooks.pop(subscription_id, None)
                if len(category_hooks) == 0:
                    registry.pop(category, None)
                return
            action_registry = self._get_action_hook_registry(phase)
            action_hooks = action_registry.get((category, action_name))
            if action_hooks is None:
                return
            action_hooks.pop(subscription_id, None)
            if len(action_hooks) == 0:
                action_registry.pop((category, action_name), None)

    @contextmanager
    def _entered_action_hook_scope(
            self,
            *,
            category: str,
            action_name: str,
    ) -> Any:
        """
        Enter one room-owned action-hook scope.

        Contract:
            - Fires pre hooks on the first nested entry for the category.
            - Suppresses nested re-entry for the same category so nested
              viewer/helper calls do not double-fire hooks.
            - Fires post hooks only when the matching top-level entry exits
              after pre hooks completed successfully.
        """
        self.check_cleaned()
        self._validate_action_hook_category(category)
        if not action_name:
            raise ValueError("action_name cannot be empty.")
        pre_category_callbacks: Tuple[Callable[[], None], ...] = tuple()
        pre_action_callbacks: Tuple[Callable[[], None], ...] = tuple()
        top_level = False
        pre_completed = False
        with self._lock:
            current_depth = self._action_hook_depth_by_category[category]
            top_level = current_depth == 0
            self._action_hook_depth_by_category[category] = current_depth + 1
            if top_level:
                pre_category_callbacks = tuple(
                    self._pre_category_hooks_by_name.get(
                        category,
                        {},
                    ).values()
                )
                pre_action_callbacks = tuple(
                    self._pre_action_hooks_by_key.get(
                        (category, action_name),
                        {},
                    ).values()
                )
        try:
            if top_level:
                for callback in pre_category_callbacks:
                    callback()
                for callback in pre_action_callbacks:
                    callback()
                pre_completed = True
            yield
        finally:
            post_action_callbacks: Tuple[Callable[[], None], ...] = tuple()
            post_category_callbacks: Tuple[Callable[[], None], ...] = tuple()
            with self._lock:
                current_depth = self._action_hook_depth_by_category[category]
                next_depth = current_depth - 1
                self._action_hook_depth_by_category[category] = next_depth
                if top_level and pre_completed and next_depth == 0:
                    post_action_callbacks = tuple(
                        self._post_action_hooks_by_key.get(
                            (category, action_name),
                            {},
                        ).values()
                    )
                    post_category_callbacks = tuple(
                        self._post_category_hooks_by_name.get(
                            category,
                            {},
                        ).values()
                    )
            if top_level and pre_completed:
                for callback in post_action_callbacks:
                    callback()
                for callback in post_category_callbacks:
                    callback()

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
        raw_event_type = normalized_payload.pop("event_type", "runtime_event")
        if not isinstance(raw_event_type, str):
            raise TypeError("event_type must be a string.")
        event_type: str = raw_event_type
        raw_frame_name = normalized_payload.pop("frame_name", None)
        if raw_frame_name is not None and not isinstance(raw_frame_name, str):
            raise TypeError("frame_name must be a string or None.")
        frame_name: Optional[str] = raw_frame_name
        raw_metadata = normalized_payload.pop("metadata", None)
        if raw_metadata is not None and not isinstance(raw_metadata, dict):
            raise TypeError("metadata must be a dict or None.")
        metadata: Optional[Dict[str, object]] = raw_metadata
        event_system.create_and_emit_event(
            event_type,
            payload=normalized_payload,
            frame_name=frame_name,
            metadata=metadata,
        )

    def _register_action_hook(
            self,
            *,
            phase: str,
            category: str,
            action_name: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one room-owned action hook.

        Args:
            phase:
                Hook phase (`pre` or `post`).
            category:
                Action category (`command`, `viewer`, or `codegen`).
            action_name:
                Stable public action name.
            callback:
                Zero-argument hook callback.

        Returns:
            str: Stable subscription id.
        """
        self.check_cleaned()
        if phase not in ("pre", "post"):
            raise ValueError("phase must be 'pre' or 'post'.")
        self._validate_action_hook_category(category)
        if not action_name:
            raise ValueError("action_name cannot be empty.")
        if not callable(callback):
            raise TypeError("callback must be callable.")
        with self._lock:
            subscription_id = IDBuilder.create_id()
            registry = self._get_action_hook_registry(phase)
            action_key = (category, action_name)
            action_hooks = registry.setdefault(action_key, {})
            action_hooks[subscription_id] = callback
            self._action_hook_keys_by_subscription_id[subscription_id] = (
                phase,
                category,
                action_name,
            )
            return subscription_id

    def _register_category_hook(
            self,
            *,
            phase: str,
            category: str,
            callback: Callable[[], None],
    ) -> str:
        """
        Register one room-owned category-wide hook.

        Args:
            phase:
                Hook phase (`pre` or `post`).
            category:
                Action category (`command`, `viewer`, or `codegen`).
            callback:
                Zero-argument hook callback.

        Returns:
            str: Stable subscription id.
        """
        self.check_cleaned()
        if phase not in ("pre", "post"):
            raise ValueError("phase must be 'pre' or 'post'.")
        self._validate_action_hook_category(category)
        if not callable(callback):
            raise TypeError("callback must be callable.")
        with self._lock:
            subscription_id = IDBuilder.create_id()
            registry = self._get_category_hook_registry(phase)
            category_hooks = registry.setdefault(category, {})
            category_hooks[subscription_id] = callback
            self._action_hook_keys_by_subscription_id[subscription_id] = (
                phase,
                category,
                "*",
            )
            return subscription_id

    def _get_action_hook_registry(
            self,
            phase: str,
    ) -> Dict[Tuple[str, str], Dict[str, Callable[[], None]]]:
        """
        Return the room-owned registry for one hook phase.

        Args:
            phase:
                Hook phase (`pre` or `post`).

        Returns:
            Dict[Tuple[str, str], Dict[str, Callable[[], None]]]:
                Registry keyed by `(category, action_name)`.
        """
        self.check_cleaned()
        if phase == "pre":
            return self._pre_action_hooks_by_key
        if phase == "post":
            return self._post_action_hooks_by_key
        raise ValueError("phase must be 'pre' or 'post'.")

    def _get_category_hook_registry(
            self,
            phase: str,
    ) -> Dict[str, Dict[str, Callable[[], None]]]:
        """
        Return the room-owned registry for one category-wide hook phase.

        Args:
            phase:
                Hook phase (`pre` or `post`).

        Returns:
            Dict[str, Dict[str, Callable[[], None]]]:
                Registry keyed by category name.
        """
        self.check_cleaned()
        if phase == "pre":
            return self._pre_category_hooks_by_name
        if phase == "post":
            return self._post_category_hooks_by_name
        raise ValueError("phase must be 'pre' or 'post'.")

    def _validate_action_hook_category(self, category: str) -> None:
        """
        Validate one action-hook category name.

        Args:
            category:
                Candidate category name.

        Returns:
            None.
        """
        self.check_cleaned()
        if not category:
            raise ValueError("category cannot be empty.")
        if category not in self._ACTION_HOOK_CATEGORIES:
            raise ValueError(
                "Unsupported action hook category '{0}'.".format(category)
            )
