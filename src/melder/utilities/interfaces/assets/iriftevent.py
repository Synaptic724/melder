from typing import runtime_checkable, Protocol, Optional, Dict


@runtime_checkable
class IRiftEvent(Protocol):
    """
    Interface for one emitted Rift-space runtime event.
    """

    event_id: str
    event_type: str
    emitted_at: str
    rift_id: str
    space_id: str
    space_kind: str
    frame_name: Optional[str]

    @property
    def payload(self) -> Dict[str, object]:
        """
        Return the event payload mapping.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return the event metadata mapping.
        """
        ...
