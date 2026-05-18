import threading
from typing import Callable, Dict, Optional
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

from melder.aether.nexus.rift.rift_space.memory_system.rift_memory import RiftMemory
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces.iriftmemorysystem import IRiftMemorySystem


class RiftMemorySystem(Cleanable, IRiftMemorySystem):
    """
    Internal

    Locked source of truth for RiftSpace memory sequencing and shared context.

    Purpose:
        Centralize the counters and shared metadata used to build immutable
        `RiftMemory` records so command/view/workstation emission can reuse one
        coherent memory context.

    Contract:
        - Owns `step_counter` and `epoch_counter`.
        - Owns shared memory metadata including `rift_id`, `space_type`, and
          optional CommandOps context fields.
        - Produces immutable `RiftMemory` snapshots.
        - Cleanup is idempotent and clears all owned mutable state.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_rift_id",
        "_space_type",
        "_step_counter",
        "_epoch_counter",
        "_task_name",
        "_activity_name",
        "_mission_name",
        "_agent_name",
        "_agent_id",
        "_metadata",
        "_memory_callbacks_by_subscription_id",
    ]

    def __init__(
            self,
            *,
            rift_id: str,
            space_type: str,
            step_counter: int = 0,
            epoch_counter: int = 0,
    ) -> None:
        """
        Initialize one Rift memory system.

        Args:
            rift_id:
                Owning Rift id.
            space_type:
                Owning space type.
            step_counter:
                Initial step counter value.
            epoch_counter:
                Initial epoch counter value.

        Returns:
            None.
        """
        super().__init__()
        if not rift_id:
            raise ValueError("rift_id cannot be empty.")
        if not space_type:
            raise ValueError("space_type cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self._rift_id: str = rift_id
        self._space_type: str = space_type
        self._step_counter: int = step_counter
        self._epoch_counter: int = epoch_counter
        self._task_name: Optional[str] = None
        self._activity_name: Optional[str] = None
        self._mission_name: Optional[str] = None
        self._agent_name: Optional[str] = None
        self._agent_id: Optional[str] = None
        self._metadata: Dict[str, object] = {}
        self._memory_callbacks_by_subscription_id: Dict[
            str,
            Callable[[RiftMemory], None],
        ] = {}

    def cleanup(self) -> None:
        """
        Idempotently clear memory-system state.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._metadata.clear()
            self._memory_callbacks_by_subscription_id.clear()

            del self._metadata
            del self._task_name
            del self._activity_name
            del self._mission_name
            del self._agent_name
            del self._agent_id
            del self._memory_callbacks_by_subscription_id
            del self._step_counter
            del self._epoch_counter
            del self._space_type
            del self._rift_id
        del self._lock

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id."""
        self.check_cleaned()
        return self._rift_id

    @property
    def space_type(self) -> str:
        """Return the owning space type."""
        self.check_cleaned()
        return self._space_type

    @property
    def step_counter(self) -> int:
        """Return the current step counter."""
        self.check_cleaned()
        with self._lock:
            return self._step_counter

    @property
    def epoch_counter(self) -> int:
        """Return the current epoch counter."""
        self.check_cleaned()
        with self._lock:
            return self._epoch_counter

    @property
    def memory_enabled(self) -> bool:
        """Return whether memory emission is currently enabled."""
        self.check_cleaned()
        with self._lock:
            return bool(self._memory_callbacks_by_subscription_id)

    def increment_step(self) -> int:
        """Increment and return the step counter."""
        self.check_cleaned()
        with self._lock:
            self._step_counter = self._step_counter + 1
            return self._step_counter

    def reset_step(self) -> None:
        """Reset the step counter to zero."""
        self.check_cleaned()
        with self._lock:
            self._step_counter = 0

    def increment_epoch(self, *, reset_step: bool = True) -> int:
        """Increment the epoch counter and optionally reset step."""
        self.check_cleaned()
        with self._lock:
            self._epoch_counter = self._epoch_counter + 1
            if reset_step:
                self._step_counter = 0
            return self._epoch_counter

    def reset_epoch(self) -> None:
        """Reset the epoch counter to zero."""
        self.check_cleaned()
        with self._lock:
            self._epoch_counter = 0

    def update_context(
            self,
            *,
            task_name: Optional[str] = None,
            activity_name: Optional[str] = None,
            mission_name: Optional[str] = None,
            agent_name: Optional[str] = None,
            agent_id: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Update shared CommandOps-facing memory context.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if task_name is not None:
                self._task_name = task_name
            if activity_name is not None:
                self._activity_name = activity_name
            if mission_name is not None:
                self._mission_name = mission_name
            if agent_name is not None:
                self._agent_name = agent_name
            if agent_id is not None:
                self._agent_id = agent_id
            if metadata:
                self._metadata.update(metadata)

    def clear_context(self) -> None:
        """Clear optional CommandOps-facing context and shared metadata."""
        self.check_cleaned()
        with self._lock:
            self._task_name = None
            self._activity_name = None
            self._mission_name = None
            self._agent_name = None
            self._agent_id = None
            self._metadata.clear()

    def describe_state(self) -> Dict[str, object]:
        """Return a detached snapshot of current memory-system state."""
        self.check_cleaned()
        with self._lock:
            return {
                "rift_id": self._rift_id,
                "space_type": self._space_type,
                "step_counter": self._step_counter,
                "epoch_counter": self._epoch_counter,
                "task_name": self._task_name,
                "activity_name": self._activity_name,
                "mission_name": self._mission_name,
                "agent_name": self._agent_name,
                "agent_id": self._agent_id,
                "metadata": dict(self._metadata),
            }

    def create_memory(
            self,
            *,
            frame_name: str,
            action_name: str,
            metadata: Optional[Dict[str, object]] = None,
            increment_step: bool = True,
    ) -> RiftMemory:
        """
        Create one immutable Rift memory snapshot.

        Args:
            frame_name:
                Required frame name.
            action_name:
                Required action name.
            metadata:
                Optional action-specific metadata.
            increment_step:
                When True, increments step before capturing the snapshot.

        Returns:
            RiftMemory: New immutable memory record.
        """
        self.check_cleaned()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        if not action_name:
            raise ValueError("action_name cannot be empty.")
        with self._lock:
            if increment_step:
                self._step_counter = self._step_counter + 1
            memory_metadata = dict(self._metadata)
            memory_metadata["rift_id"] = self._rift_id
            memory_metadata["space_type"] = self._space_type
            if self._task_name is not None:
                memory_metadata["task_name"] = self._task_name
            if self._activity_name is not None:
                memory_metadata["activity_name"] = self._activity_name
            if self._mission_name is not None:
                memory_metadata["mission_name"] = self._mission_name
            if self._agent_name is not None:
                memory_metadata["agent_name"] = self._agent_name
            if self._agent_id is not None:
                memory_metadata["agent_id"] = self._agent_id
            if metadata:
                memory_metadata.update(metadata)
            return RiftMemory(
                frame_name=frame_name,
                action_name=action_name,
                step_counter=self._step_counter,
                epoch_counter=self._epoch_counter,
                metadata=memory_metadata,
            )

    def register_memory_callback(
            self,
            callback: Callable[[RiftMemory], None],
    ) -> str:
        """
        Register one callback for emitted memory records.

        Args:
            callback:
                Callback invoked once per emitted memory record.

        Returns:
            str: Stable subscription id for later unregistration.

        Raises:
            TypeError: If `callback` is not callable.
        """
        self.check_cleaned()
        if not callable(callback):
            raise TypeError("callback must be callable.")
        with self._lock:
            subscription_id = IDBuilder.create_id()
            self._memory_callbacks_by_subscription_id[subscription_id] = callback
            return subscription_id

    def unregister_memory_callback(self, subscription_id: str) -> None:
        """
        Remove one memory callback subscription by id.

        Args:
            subscription_id:
                Subscription id returned by `register_memory_callback(...)`.

        Returns:
            None.

        Raises:
            ValueError: If `subscription_id` is empty.
        """
        self.check_cleaned()
        if not subscription_id:
            raise ValueError("subscription_id cannot be empty.")
        with self._lock:
            self._memory_callbacks_by_subscription_id.pop(subscription_id, None)

    def emit_memory(self, memory: RiftMemory) -> None:
        """
        Emit one memory record to every registered callback.

        Args:
            memory:
                Memory record to emit.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            callbacks = list(self._memory_callbacks_by_subscription_id.values())
        for callback in callbacks:
            callback(memory)

    def create_and_emit_memory(
            self,
            *,
            frame_name: str,
            action_name: str,
            metadata: Optional[Dict[str, object]] = None,
            increment_step: bool = True,
    ) -> RiftMemory:
        """
        Create one memory record and emit it immediately.

        Args:
            frame_name:
                Required frame name.
            action_name:
                Required action name.
            metadata:
                Optional action-specific metadata.
            increment_step:
                When True, increments step before capturing the snapshot.

        Returns:
            RiftMemory: Emitted immutable memory record.
        """
        self.check_cleaned()
        memory = self.create_memory(
            frame_name=frame_name,
            action_name=action_name,
            metadata=metadata,
            increment_step=increment_step,
        )
        self.emit_memory(memory)
        return memory
