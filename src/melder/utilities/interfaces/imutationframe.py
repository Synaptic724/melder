from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ichangecontrolmanager import IChangeControlManager
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates


@runtime_checkable
class IMutationFrame(ICleanable, Protocol):
    """
    Structural contract for the tentative frame-scoped mutation facade.

    Purpose:
        Describe the minimal frame-scoped mutation helper surface without
        forcing callers onto the concrete `MutationFrame` placeholder class.
    """

    @property
    def aetheric_frame_name(self) -> str:
        """
        Return the owning Aetheric frame name for this mutation facade.
        """
        ...

    @property
    def spell_system_states(self) -> "ISpellSystemStates":
        """
        Return the referenced spell-system-state registry for this frame.
        """
        ...

    @property
    def change_control_manager(self) -> "IChangeControlManager":
        """
        Return the referenced change-control manager for this frame.
        """
        ...
