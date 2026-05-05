from typing import Protocol, runtime_checkable
from melder.utilities.interfaces.assets.iriftspace import IRiftSpace
from melder.utilities.interfaces.assets.istaticcommandsystem import IStaticCommandSystem

@runtime_checkable
class IStaticRiftSpace(IRiftSpace, Protocol):
    """
    Interface for StaticRiftSpace.
    """

    @property
    def command_system(self) -> IStaticCommandSystem:
        """
        Return the room-local static command system owned by this space.
        """
        ...
