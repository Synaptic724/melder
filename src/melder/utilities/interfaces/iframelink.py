from typing import Dict, Protocol, runtime_checkable
from melder.utilities.interfaces.icleanable import ICleanable

@runtime_checkable
class IFrameLink(ICleanable, Protocol):
    """
    Interface for one view-safe frame target entry.
    """

    @property
    def link_id(self) -> str:
        """
        Return the canonical target-entry id.
        """
        ...

    @property
    def frame_name(self) -> str:
        """
        Return the owning frame name.
        """
        ...

    @property
    def source_kind(self) -> str:
        """
        Return the source kind label.
        """
        ...

    @property
    def source_id(self) -> str:
        """
        Return the stable source identifier.
        """
        ...

    @property
    def display_name(self) -> str:
        """
        Return the viewer-facing display name.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return detached metadata for the target entry.
        """
        ...

    def clone(self) -> "IFrameLink":
        """
        Return a detached copy of this target entry.
        """
        ...

