import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import IChangeControlManager, ISpellSystemStates
from melder.utilities.interfaces.imutationframe import IMutationFrame
from melder.utilities.interfaces.imutationresearch import IMutationResearch


class MutationFrame(Cleanable, IMutationFrame):
    """
    Placeholder frame-scoped mutation facade.

    Purpose:
        Provide a possible future frame-scoped mutation transaction surface
        without making it the owner of conduits or broader frame runtime state.

    Contract:
        - References, but does not own, `MutationResearch`,
          `SpellSystemStates`, and `ChangeControlManager`.
        - Stores only the target frame name plus referenced services.
        - Current implementation is intentionally skeletal and may later prove
          unnecessary.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_aetheric_frame_name",
        "_mutation_research",
        "_spell_system_states",
        "_change_control_manager",
    ]

    def __init__(
            self,
            *,
            aetheric_frame_name: str,
            mutation_research: IMutationResearch,
            spell_system_states: ISpellSystemStates,
            change_control_manager: IChangeControlManager,
    ) -> None:
        """
        Initialize one placeholder mutation frame.

        Returns:
            None.
        """
        super().__init__()
        if not aetheric_frame_name:
            raise ValueError("aetheric_frame_name cannot be empty.")
        if mutation_research is None:
            raise ValueError("mutation_research cannot be None.")
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None.")
        if change_control_manager is None:
            raise ValueError("change_control_manager cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._aetheric_frame_name: Optional[str] = aetheric_frame_name
        self._mutation_research = mutation_research
        self._spell_system_states: Optional[ISpellSystemStates] = spell_system_states
        self._change_control_manager: Optional[IChangeControlManager] = change_control_manager

    def cleanup(self) -> None:
        """
        Idempotently clear placeholder references.

        Returns:
            None.
        """
        if self._cleaned:
            return
        with self._lock:
            if self._cleaned:
                return
            self._cleaned = True
            self._aetheric_frame_name = None
            self._mutation_research = None
            self._spell_system_states = None
            self._change_control_manager = None
            self._id = None
        self._lock = None

    @property
    def id(self) -> str:
        """
        Return the stable placeholder id.

        Returns:
            str: Stable placeholder id.
        """
        self.check_cleaned()
        return self._id

    @property
    def aetheric_frame_name(self) -> str:
        """
        Return the target frame name this placeholder coordinates.

        Returns:
            str: Target frame name.
        """
        self.check_cleaned()
        return self._aetheric_frame_name

    @property
    def mutation_research(self) -> IMutationResearch:
        """
        Return the owning mutation-research root.

        Returns:
            MutationResearch: Root mutation-research object.
        """
        self.check_cleaned()
        return self._mutation_research

    @property
    def spell_system_states(self) -> ISpellSystemStates:
        """
        Return the referenced spell-system-states surface.

        Returns:
            ISpellSystemStates: Referenced spell-system-states surface.
        """
        self.check_cleaned()
        return self._spell_system_states

    @property
    def change_control_manager(self) -> IChangeControlManager:
        """
        Return the referenced change-control manager.

        Returns:
            IChangeControlManager: Referenced change-control manager.
        """
        self.check_cleaned()
        return self._change_control_manager
