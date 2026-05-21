import threading
from typing import TYPE_CHECKING, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.id_builder import IDBuilder

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.aether.aetheric_frame.dev_ops.change_control_manager.change_control_manager import ChangeControlManager
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import SpellSystemStates
    from melder.mutation_research.mutation_research import MutationResearch


class MutationConduit(Cleanable):
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
            conduit: Conduit,
            mutation_research: MutationResearch,
            spell_system_states: SpellSystemStates,
            change_control_manager: ChangeControlManager,
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
        self._conduit: Conduit = conduit
        self._mutation_research = mutation_research
        self._spell_system_states: SpellSystemStates = spell_system_states
        self._change_control_manager: ChangeControlManager = change_control_manager

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
            del self._conduit
            del self._mutation_research
            del self._spell_system_states
            del self._change_control_manager
            del self._id
        del self._lock

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
    def conduit(self) -> Conduit:
        """
        Return the underlying conduit reference.

        Returns:
            Conduit: Underlying conduit.
        """
        self.check_cleaned()
        return self._conduit

    @property
    def mutation_research(self) -> MutationResearch:
        """
        Return the owning mutation-research root.

        Returns:
            MutationResearch: Root mutation-research object.
        """
        self.check_cleaned()
        return self._mutation_research

    @property
    def spell_system_states(self) -> SpellSystemStates:
        """
        Return the referenced spell-system-states surface.

        Returns:
            SpellSystemStates: Referenced spell-system-states surface.
        """
        self.check_cleaned()
        return self._spell_system_states

    @property
    def change_control_manager(self) -> ChangeControlManager:
        """
        Return the referenced change-control manager.

        Returns:
            ChangeControlManager: Referenced change-control manager.
        """
        self.check_cleaned()
        return self._change_control_manager


