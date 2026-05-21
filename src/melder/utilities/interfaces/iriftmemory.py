from typing import Dict, Protocol, runtime_checkable

@runtime_checkable
class IRiftMemory(Protocol):
    """
    Interface for one immutable Rift execution memory record.
    """

    @property
    def memory_id(self) -> str:
        """Return the stable memory id."""
        ...

    @property
    def created_at(self) -> str:
        """Return the UTC creation timestamp."""
        ...

    @property
    def frame_name(self) -> str:
        """Return the required frame name for this memory."""
        ...

    @property
    def action_name(self) -> str:
        """Return the action name captured by this memory."""
        ...

    @property
    def step_counter(self) -> int:
        """Return the step counter snapshot."""
        ...

    @property
    def epoch_counter(self) -> int:
        """Return the epoch counter snapshot."""
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the memory metadata mapping.
        """
        ...

