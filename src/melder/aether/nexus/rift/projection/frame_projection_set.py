from typing import Dict, Optional

from melder.aether.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.aether.nexus.rift.projection.command_projection import CommandProjection
from melder.aether.nexus.rift.projection.view_projection import ViewProjection
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder


class FrameProjectionSet(Cleanable):
    """
    Owned set of consumer-shaped projections for one targeted frame.

    Purpose:
        Bundle the current view, command, and codegen projections for one frame
        together with one generation marker so `RiftSpace` can swap them as one
        coherent unit during ACL refresh.

    Contract:
        - Owns exactly one projection of each family for one frame.
        - Owns one generation token that changes whenever the set is rebuilt.
        - Cleanup cascades into the owned projections.
    """

    __slots__ = Cleanable.__slots__ + [
        "_frame_name",
        "_generation",
        "_view_projection",
        "_command_projection",
        "_codegen_projection",
        "_metadata",
    ]

    def __init__(
            self,
            *,
            frame_name: str,
            view_projection: ViewProjection,
            command_projection: CommandProjection,
            codegen_projection: CodegenProjection,
            generation: Optional[str] = None,
            metadata: Optional[Dict[str, object]] = None,
    ) -> None:
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._frame_name: str = frame_name
        self._generation: str = generation or IDBuilder.create_id()
        self._view_projection: ViewProjection = view_projection
        self._command_projection: CommandProjection = command_projection
        self._codegen_projection: CodegenProjection = codegen_projection
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """Idempotently cleanup the owned projections."""
        if self._cleaned:
            return
        self._cleaned = True
        self._view_projection.cleanup()
        self._command_projection.cleanup()
        self._codegen_projection.cleanup()
        self._frame_name = None
        self._generation = None
        self._view_projection = None
        self._command_projection = None
        self._codegen_projection = None
        self._metadata.clear()
        self._metadata = None

    @property
    def frame_name(self) -> str:
        """Return the target frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def generation(self) -> str:
        """Return the generation token for this projection set."""
        self.check_cleaned()
        return self._generation

    @property
    def view_projection(self) -> ViewProjection:
        """Return the owned view projection."""
        self.check_cleaned()
        return self._view_projection

    @property
    def command_projection(self) -> CommandProjection:
        """Return the owned command projection."""
        self.check_cleaned()
        return self._command_projection

    @property
    def codegen_projection(self) -> CodegenProjection:
        """Return the owned codegen projection."""
        self.check_cleaned()
        return self._codegen_projection

    @property
    def metadata(self) -> Dict[str, object]:
        """Return a detached metadata copy."""
        self.check_cleaned()
        return dict(self._metadata)
