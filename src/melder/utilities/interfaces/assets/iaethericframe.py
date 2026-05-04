from typing import Protocol, Optional, List, Dict, Any, Set

from melder.utilities.interfaces.assets.icleanable import ICleanable


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
