from typing import Optional, Protocol, Tuple, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IFrameViewer(ICleanable, Protocol):
    """
    Interface for the public Rift-backed frame viewer host.
    """

    def list_frame_names(self) -> Tuple[str, ...]:
        """
        Return the hosted frame names currently visible through this viewer.
        """
        ...

    def get_view_frame(self, frame_name: Optional[str] = None) -> object:
        """
        Return the frame-scoped helper for one hosted frame.
        """
        ...

    def get_view_multiframe(self) -> object:
        """
        Return the cross-frame helper surface for this viewer host.
        """
        ...
