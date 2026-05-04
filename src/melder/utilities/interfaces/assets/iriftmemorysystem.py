from typing import runtime_checkable, Protocol, Optional, Dict, Callable

from melder.utilities.interfaces.assets.icleanable import ICleanable


@runtime_checkable
class IRiftMemorySystem(ICleanable, Protocol):
    """
    Interface for the RiftSpace-owned memory sequencing and context system.
    """

    @property
    def rift_id(self) -> str:
        """Return the owning Rift id."""
        ...

    @property
    def space_type(self) -> str:
        """Return the owning space type."""
        ...

    @property
    def step_counter(self) -> int:
        """Return the current step counter."""
        ...

    @property
    def epoch_counter(self) -> int:
        """Return the current epoch counter."""
        ...

    @property
    def memory_enabled(self) -> bool:
        """Return whether memory emission is currently enabled."""
        ...

    def increment_step(self) -> int:
        """Increment and return the step counter."""
        ...

    def reset_step(self) -> None:
        """Reset the step counter."""
        ...

    def increment_epoch(self, *, reset_step: bool = True) -> int:
        """Increment and return the epoch counter."""
        ...

    def reset_epoch(self) -> None:
        """Reset the epoch counter."""
        ...

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
        """Update shared memory context."""
        ...

    def clear_context(self) -> None:
        """Clear shared memory context."""
        ...

    def describe_state(self) -> Dict[str, object]:
        """Return a detached memory-system state snapshot."""
        ...

    def create_memory(
            self,
            *,
            frame_name: str,
            action_name: str,
            metadata: Optional[Dict[str, object]] = None,
            increment_step: bool = True,
    ) -> IRiftMemory:
        """Create one immutable Rift memory record."""
        ...

    def register_memory_callback(
            self,
            callback: Callable[[IRiftMemory], None],
    ) -> str:
        """Register one memory callback and return its subscription id."""
        ...

    def unregister_memory_callback(self, subscription_id: str) -> None:
        """Remove one memory callback subscription by id."""
        ...

    def emit_memory(self, memory: IRiftMemory) -> None:
        """Emit one memory record to all registered callbacks."""
        ...

    def create_and_emit_memory(
            self,
            *,
            frame_name: str,
            action_name: str,
            metadata: Optional[Dict[str, object]] = None,
            increment_step: bool = True,
    ) -> IRiftMemory:
        """Create one memory record and emit it immediately."""
        ...
