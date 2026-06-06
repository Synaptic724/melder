from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional, Tuple

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.conduit.creations.creations import Creations
    from melder.utilities.synchronization.creation_gate import CreationGate


class CreationContext(Cleanable):
    """
    Thin spell-bound runtime executor dispatcher.

    Purpose:
        Hold the final phase-11 runtime doors for one spell so meld can route
        execution without carrying compiler residue in the hot path.

    Contract:
        - `no_overrides_executor` and `overrides_executor` are the only
          executor doors this object dispatches.
        - Each executor returns `(instance, created)`.
        - Dynamic gate handling remains here because it is runtime policy, not
          compiler planning.
        - Hook orchestration stays outside this object in meld.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_spell_id",
        "_dynamic_environment",
        "_creation_gate",
        "_creation_gate_index_id",
        "_no_overrides_executor",
        "_overrides_executor",
    ]

    def __init__(
            self,
            *,
            spell: "Spell",
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
            no_overrides_executor: Optional[Callable[..., Tuple[Any, bool]]] = None,
            overrides_executor: Optional[Callable[..., Tuple[Any, bool]]] = None,
    ) -> None:
        """
        Build one spell-bound runtime dispatcher.
        """
        super().__init__()
        self._spell = spell
        self._spell_id = spell.spell_id
        self._dynamic_environment = bool(dynamic_environment)
        if self._dynamic_environment and creation_gate is None:
            raise ValueError(
                "creation_gate cannot be None when dynamic_environment is True."
            )
        self._creation_gate = creation_gate
        self._creation_gate_index_id = creation_gate_index_id
        self._no_overrides_executor = no_overrides_executor
        self._overrides_executor = overrides_executor

    def cleanup(self) -> None:
        """
        Deterministically release runtime references.
        """
        if self._cleaned:
            return
        self._cleaned = True

        del self._spell
        del self._spell_id
        del self._dynamic_environment
        del self._creation_gate
        del self._creation_gate_index_id
        del self._no_overrides_executor
        del self._overrides_executor

    def execute(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> Tuple[Any, bool]:
        """
        Execute one meld resolution against the final phase-11 runtime doors.
        """
        if not self._dynamic_environment:
            return self._dispatch(caller_creations, overrides)

        creation_gate = self._creation_gate
        index_id = self._creation_gate_index_id
        if creation_gate is None:
            raise RuntimeError(
                f"CreationGate is unavailable for spell index '{index_id}'."
            )
        if creation_gate.is_closed():
            raise RuntimeError(
                f"CreationGate is closed for spell index '{index_id}'."
            )
        if not creation_gate.enabled:
            creation_gate.wait()
            if creation_gate.is_closed():
                raise RuntimeError(
                    f"CreationGate is closed for spell index '{index_id}'."
                )
        try:
            creation_gate.register_ticket()
            return self._dispatch(caller_creations, overrides)
        finally:
            creation_gate.unregister_ticket()

    def execute_no_hooks(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute one meld resolution and discard the created flag.
        """
        instance, _created = self.execute(caller_creations, overrides)
        return instance

    def _dispatch(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]],
    ) -> Tuple[Any, bool]:
        """
        Dispatch to the appropriate final runtime door.
        """
        if overrides is None:
            executor = self._no_overrides_executor
            if executor is None:
                raise RuntimeError(
                    "No-overrides executor is unavailable for this spell."
                )
            return executor(caller_creations)

        executor = self._overrides_executor
        if executor is None:
            raise RuntimeError(
                "Overrides executor is unavailable for this spell."
            )
        return executor(caller_creations, overrides)
