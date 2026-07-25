from typing import TYPE_CHECKING, Dict, Optional

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

if TYPE_CHECKING:
    from melder.nexus.rift.projection.codegen_projection import CodegenProjection
    from melder.nexus.rift.projection.command_projection import CommandProjection
    from melder.nexus.rift.projection.view_projection import ViewProjection



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

    Threading:
        Swapped as ONE unit during refresh, which is what makes the triple
        coherent for concurrent readers.

    Registration:
        MELDER KERNEL - guarded. Compiled by the ACL layer and held as Rift
        projection state.

    Subsystem Context:
        The bundle of view, command, and codegen projections for one frame,
        plus one generation marker.

    System Context:
        Bundling with a GENERATION MARKER is what allows `RiftSpace` to swap
        projections as one coherent unit. Swapping the three independently would
        create windows where a room's view answers came from one ACL revision
        while its command answers came from another - an inconsistency no
        consumer could detect and none of the three projections is wrong enough
        to reveal.
        This is the object the Nexus refresh fan-out actually replaces: block
        entrants at the Rift gate, drain in-flight tickets, swap the set,
        reopen. The generation marker makes it possible to tell whether a room
        is running current policy without comparing the projections themselves.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Owned set of consumer-shaped projections for one targeted frame. "
        "Melder kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_frame_name",
        "_id",
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
        """
        Bundle one frame's projection triple under a generation token.

        Contract:
            - Takes ownership of all three passed projections (view,
              command, codegen); cleanup cascades into each.
            - `generation` identifies this exact build; when omitted a fresh
              id is minted (via `IDBuilder`) so every rebuild is
              distinguishable and `RiftSpace` can tell whether a room runs
              current policy without comparing projections.
            - Copies `metadata` into a fresh dict.

        Args:
            frame_name:
                Target frame for the bundled triple; must be non-empty.
            view_projection:
                Owned view projection for the frame.
            command_projection:
                Owned command projection for the frame.
            codegen_projection:
                Owned codegen projection for the frame.
            generation:
                Optional generation token; a fresh id is minted when omitted.
            metadata:
                Optional set metadata; copied defensively (None -> {}).

        Raises:
            ValueError: If `frame_name` is empty.

        Returns:
            None.
        """
        super().__init__()
        if not frame_name:
            raise ValueError("frame_name cannot be empty.")
        self._frame_name: str = frame_name
        self._id: str = generation or IDBuilder.create_id()
        self._view_projection: ViewProjection = view_projection
        self._command_projection: CommandProjection = command_projection
        self._codegen_projection: CodegenProjection = codegen_projection
        self._metadata: Dict[str, object] = dict(metadata) if metadata else {}

    def cleanup(self) -> None:
        """
        Idempotently cleanup the owned projections.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._view_projection.cleanup()
        self._command_projection.cleanup()
        self._codegen_projection.cleanup()
        self._metadata.clear()

        del self._frame_name
        del self._id
        del self._view_projection
        del self._command_projection
        del self._codegen_projection

        del self._metadata

    @property
    def frame_name(self) -> str:
        """Return the target frame name."""
        self.check_cleaned()
        return self._frame_name

    @property
    def generation(self) -> str:
        """Return the generation token for this projection set."""
        self.check_cleaned()
        return self._id

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

