from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.ichangecontrolmanager import IChangeControlManager
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.ispellsystemstates import ISpellSystemStates


@runtime_checkable
class IMutationConduit(ICleanable, Protocol):
    """
    Structural contract for the conduit-scoped mutation facade.

    Purpose:
        Describe the minimal conduit-scoped mutation helper surface without
        forcing callers onto the concrete `MutationConduit` placeholder class.
    """

    @property
    def conduit(self) -> "IConduit":
        """
        Return the underlying conduit this mutation facade is attached to.
        """
        ...

    @property
    def spell_system_states(self) -> "ISpellSystemStates":
        """
        Return the referenced spell-system-state registry for this conduit.
        """
        ...

    @property
    def change_control_manager(self) -> "IChangeControlManager":
        """
        Return the referenced change-control manager for this conduit.
        """
        ...
