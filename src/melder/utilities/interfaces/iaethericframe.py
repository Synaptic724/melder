from typing import runtime_checkable, Any, Optional, Protocol
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iconduitcloud import IConduitCloud

class IAethericFrame(ICleanable, Protocol):
    """
    An Interface for an isolated "universe" or "frame" within the Aether.

    An AethericFrame holds all top-level conduits, spell registries, and
    configurations for a specific, isolated domain.

    Attributes:
        name (str): The unique name of this frame.
        _configuration (Optional[Any]): The frozen configuration for this frame.
        _conduit_cloud (IConduitCloud): The abstract factory for named conduits.
        _conduits (Dict[str, IConduit]): Stores all root conduits.
        _spell_registry (Dict[str, Set[str]]): Maps
            conduit ids to their owned spell IDs.
        _conduit_clusters (Dict[str, List[str]]): Organizes
            conduits into named groups.
    """
    name: str
    _id: str
    _aether: "IAether"
    _configuration: Optional[Any]  # Use 'Configuration' if it's a known type
    _conduit_cloud: IConduitCloud
    _conduits: 'Dict[str, IConduit]'
    _spell_registry: 'Dict[str, Set[str]]'
    _conduit_clusters: 'Dict[str, List[str]]'

    @property
    def frame_configuration(self) -> Optional[Any]:
        """
        Return the canonical frame-owned posture object.
        """
        ...

    def freeze_frame_configuration(
            self,
            origin_spellbook_id: Optional[str] = None,
    ) -> Any:
        """
        Freeze the current frame-owned posture object.
        """
        ...

    def bind_frame_configuration(
            self,
            frame_configuration: Any,
    ) -> Any:
        """
        Bind one posture object onto this frame and return the canonical owner.
        """
        ...
