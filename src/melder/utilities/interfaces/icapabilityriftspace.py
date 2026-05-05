from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.icapabilitycommandsystem import ICapabilityCommandSystem
from melder.utilities.interfaces.iriftspace import IRiftSpace

@runtime_checkable
class ICapabilityRiftSpace(IRiftSpace, Protocol):
    """
    Interface for CapabilityRiftSpace.
    """

    @property
    def command_system(self) -> ICapabilityCommandSystem:
        """
        Return the room-local capability command system owned by this space.
        """
        ...
