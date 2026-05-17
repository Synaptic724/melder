from typing import runtime_checkable, Any, Dict, List, Optional, Protocol, Set
from melder.utilities.interfaces.icleanable import ICleanable

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
    name: str

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
