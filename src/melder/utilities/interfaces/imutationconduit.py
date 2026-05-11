from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IMutationConduit(ICleanable, Protocol):
    """
    Structural contract for the conduit-scoped mutation facade.
    """

    @property
    def conduit(self):
        ...

    @property
    def mutation_research(self):
        ...

    @property
    def spell_system_states(self):
        ...

    @property
    def change_control_manager(self):
        ...
