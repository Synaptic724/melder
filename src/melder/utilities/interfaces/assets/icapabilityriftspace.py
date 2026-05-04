from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.iriftspace import IRiftSpace


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
