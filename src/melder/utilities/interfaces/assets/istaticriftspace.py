from typing import runtime_checkable, Protocol

from melder.utilities.interfaces.assets.iriftspace import IRiftSpace


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
