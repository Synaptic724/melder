from typing import Dict, Protocol, runtime_checkable
from melder.nexus.rift.projection.codegen_projection import CodegenProjection
from melder.nexus.rift.projection.command_projection import CommandProjection
from melder.nexus.rift.projection.view_projection import ViewProjection
from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IFrameProjectionSet(ICleanable, Protocol):
    """
    Rift-owned bundle of compiled projections for one targeted frame.

    Purpose:
        Define the projection-set contract consumed by `Rift` without coupling
        the runtime to the concrete `FrameProjectionSet` implementation.

    Contract:
        - Represents exactly one target frame.
        - Owns one projection of each family: view, command, and codegen.
        - Exposes one generation token that changes when the set is rebuilt.
        - Metadata access must be detached so callers do not mutate the owned
          runtime object through returned mappings.
    """

    @property
    def frame_name(self) -> str:
        """
        Return the target frame name for this projection set.
        """
        ...

    @property
    def generation(self) -> str:
        """
        Return the generation token for this projection set.
        """
        ...

    @property
    def view_projection(self) -> ViewProjection:
        """
        Return the owned view projection for this frame.
        """
        ...

    @property
    def command_projection(self) -> CommandProjection:
        """
        Return the owned command projection for this frame.
        """
        ...

    @property
    def codegen_projection(self) -> CodegenProjection:
        """
        Return the owned codegen projection for this frame.
        """
        ...

    @property
    def metadata(self) -> Dict[str, object]:
        """
        Return a detached metadata snapshot for this projection set.
        """
        ...

