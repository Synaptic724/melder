from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.iriftspace import IRiftSpace

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
