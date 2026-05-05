from typing import Dict, Protocol, runtime_checkable

@runtime_checkable
class IRiftMemory(Protocol):
    """
    Interface for one immutable Rift execution memory record.
    """

    memory_id: str
    created_at: str
    frame_name: str
    action_name: str
    step_counter: int
    epoch_counter: int

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the memory metadata mapping.
        """
        ...
