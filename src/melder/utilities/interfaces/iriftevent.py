from typing import Dict, Optional, Protocol, runtime_checkable

@runtime_checkable
class IRiftEvent(Protocol):
    """
    Interface for one emitted Rift-space runtime event.
    """

    @property
    def event_id(self) -> str:
        """
        Return the stable event id.
        """
        ...

    @property
    def event_type(self) -> str:
        """
        Return the stable event type.
        """
        ...

    @property
    def emitted_at(self) -> str:
        """
        Return the UTC emitted timestamp.
        """
        ...

    @property
    def rift_id(self) -> str:
        """
        Return the owning Rift id.
        """
        ...

    @property
    def space_id(self) -> str:
        """
        Return the emitting space id.
        """
        ...

    @property
    def space_kind(self) -> str:
        """
        Return the emitting space kind.
        """
        ...

    @property
    def frame_name(self) -> Optional[str]:
        """
        Return the optional related frame name.
        """
        ...

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
