from typing import Dict, Optional, runtime_checkable, Protocol
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iaethericframeconfiguration import IAethericFrameConfiguration
from melder.utilities.interfaces.iconduit import IConduit
from melder.utilities.interfaces.iconduitcloud import IConduitCloud
from melder.utilities.interfaces.idevopsmanager import IDevOpsManager
from melder.utilities.interfaces.ispellindex import ISpellIndex
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates

@runtime_checkable
class IAethericFrame(ICleanable, Protocol):
    """
    Manage one isolated runtime frame within `Aether`.

    `AethericFrame` is the per-frame ownership boundary beneath the global
    `Aether` singleton. It owns the frame-local conduit registry, spell/index
    registries, cluster state, frame-level posture/config references, and the
    DevOps and mutation services tied to that frame.

    Contract:
      - Owns root conduits and their spell registries.
      - Owns a stable root-conduit name index for per-frame lookup.
      - Owns the version registry for all `SpellIndex` lineages in this frame.
      - Owns `SpellSystemStates` and `DevOpsManager` for this frame.
      - Owns one narrow frame-level AR posture object distinct from the richer
        shared Spellbook configuration object.
      - Detaches itself from `Aether` only after frame-owned cleanup completes.

    Threading / Concurrency:
      - Uses one frame-local `RLock` to guard cleanup and frame-owned registry
        mutation.
      - Relies on child objects to guard their own internal state.
    """
    _id: str
    _conduits: Dict[str, IConduit]
    _conduit_cloud: IConduitCloud
    _conduit_clusters: Dict[str, object]
    name: str

    @property
    def spell_system_states(self) -> ISpellSystemStates:
        """
        Return the frame-owned `SpellSystemStates` registry.
        """
        ...

    @property
    def dev_ops_manager(self) -> IDevOpsManager:
        """
        Return the frame-owned DevOps hub.
        """
        ...

    @property
    def frame_configuration(self) -> Optional[IAethericFrameConfiguration]:
        """
        Return the canonical frame-owned posture object.
        """
        ...

    def __enter__(self) -> "IAethericFrame":
        """
        Enter the frame lock context and return the frame.
        """
        ...

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the frame lock context and release the frame lock.
        """
        ...

    def freeze_frame_configuration(
            self,
            origin_spellbook_id: Optional[str] = None,
    ) -> IAethericFrameConfiguration:
        """
        Freeze the current frame-owned posture object.
        """
        ...

    def bind_frame_configuration(
            self,
            frame_configuration: IAethericFrameConfiguration,
    ) -> IAethericFrameConfiguration:
        """
        Bind one posture object onto this frame and return the canonical owner.
        """
        ...

    def refresh_version_registry(self) -> None:
        """
        Rebuild the frame-owned version registry from the current spell registry.
        """
        ...

    def has_version(self, version_id: str) -> bool:
        """
        Return whether the given version id exists anywhere in this frame.
        """
        ...

    def get_all_versions(self) -> set[str]:
        """
        Return the flat set of all cached version ids in this frame.
        """
        ...

    def find_and_return_spell_index(
            self,
            version_id: str,
    ) -> ISpellIndex | None:
        """
        Return the `SpellIndex` that owns the given version id, if any.
        """
        ...
