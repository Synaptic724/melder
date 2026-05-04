from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.iriftspace import IRiftSpace


@runtime_checkable
class ICodegenRiftSpace(IRiftSpace, Protocol):
    """
    Interface for CodegenRiftSpace.
    """

    @property
    def codegen_system(self) -> "ICodegenSystem":
        """
        Return the room-owned internal codegen system.
        """
        ...
