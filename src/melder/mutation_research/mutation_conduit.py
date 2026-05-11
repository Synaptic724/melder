import threading
from typing import Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder
from melder.utilities.interfaces import IChangeControlManager, IConduit, ISpellSystemStates
from melder.utilities.interfaces.imutationconduit import IMutationConduit
from melder.utilities.interfaces.imutationresearch import IMutationResearch


class MutationConduit(Cleanable, IMutationConduit):
    """
    Placeholder conduit-scoped mutation facade.

    Purpose:
        Provide the future orchestration surface for conduit-scoped mutation
        transactions without bloating `Conduit` itself.

    Contract:
        - References, but does not own, the underlying `Conduit`.
        - References, but does not own, `MutationResearch`,
          `SpellSystemStates`, and `ChangeControlManager`.
        - Current implementation is intentionally skeletal.
    """

    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_id",
        "_lock",
        "_conduit",
        "_mutation_research",
        "_spell_system_states",
        "_change_control_manager",
    ]

    def __init__(
            self,
            *,
            conduit: IConduit,
            mutation_research: IMutationResearch,
            spell_system_states: ISpellSystemStates,
            change_control_manager: IChangeControlManager,
    ) -> None:
        """
        Initialize one placeholder mutation conduit.

        Returns:
            None.
        """
        super().__init__()
        if conduit is None:
            raise ValueError("conduit cannot be None.")
        if mutation_research is None:
            raise ValueError("mutation_research cannot be None.")
        if spell_system_states is None:
            raise ValueError("spell_system_states cannot be None.")
        if change_control_manager is None:
            raise ValueError("change_control_manager cannot be None.")
        self._id: str = IDBuilder.create_id()
        self._lock: threading.RLock = threading.RLock()
        self._conduit: Optional[IConduit] = conduit
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
            self._conduit = None
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
    def conduit(self) -> IConduit:
        """
        Return the underlying conduit reference.

        Returns:
            IConduit: Underlying conduit.
        """
        self.check_cleaned()
        return self._conduit

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
