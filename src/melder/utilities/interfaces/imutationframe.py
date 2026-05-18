from typing import Protocol, runtime_checkable

from melder.utilities.interfaces.icleanable import ICleanable


@runtime_checkable
class IMutationFrame(ICleanable, Protocol):
    """
    Structural contract for the tentative frame-scoped mutation facade.
    """

    @property
    def aetheric_frame_name(self) -> str:
        ...

    @property
    def mutation_research(self) -> "IMutationResearch":
        ...

    @property
    def spell_system_states(self) -> "ISpellSystemStates":
        ...

    @property
    def change_control_manager(self) -> "IChangeControlManager":
        ...
