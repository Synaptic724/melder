from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.conduit.creations.creations import Creations
    from melder.aether.spellbook.spell import Spell
    from melder.utilities.synchronization.creation_gate import CreationGate


class CreationContext(Cleanable):
    """
    Spell-bound runtime executor context.

    Purpose:
        Hold the final spell-static execution doors emitted by phase 11 and run
        them under the dynamic creation-gate policy used by meld.

    Contract:
        - `CreationContext` keeps dynamic gate handling because that is runtime
          policy, not compiler planning.
        - Phase 11 now owns route/transient specialization and publishes the
          final 2 tuple-return runtime doors directly.
        - `no_overrides_executor` and `overrides_executor` both return
          `(instance, created)`.
        - `execute(...)` returns `(instance, created)`.
        - `execute_no_hooks(...)` returns only the instance.
        - Door-facing internal contract: the meld front doors
          (`ConduitMeld`, `SpellSpaceMeld`) read `_dynamic_environment`,
          `_no_overrides_executor`, and `_overrides_executor` directly on
          their non-dynamic no-hooks fast lane. Those reads are per-call
          through the live spell-published context and are never cached on
          the doors, so context replacement/cleanup semantics are unchanged.
          Renaming or repurposing these slots requires updating both doors.
        - Executor slots are SELF-REPLACING: generalized hydration installs
          cold delegating doors first and hot-swaps the final hydrated
          executors into `_no_overrides_executor` / `_overrides_executor` in
          place on first execution. Any reader that retains an executor
          reference across calls pins the cold door and defeats the swap;
          readers must re-read the slot per call.
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
            no_overrides_executor: Optional[Callable[..., Any]] = None,
            overrides_executor: Optional[Callable[..., Any]] = None,
    ) -> None:
        """
        Build one spell-bound runtime context.

        Args:
            spell:
                Spell this context is bound to.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode.
            creation_gate:
                Shared spell-index gate for dynamic-mode admission.
            creation_gate_index_id:
                Stable spell-index id used in gate diagnostics.
            no_overrides_executor:
                Phase-11-provided final no-overrides executor returning
                `(instance, created)`.
            overrides_executor:
                Phase-11-provided final overrides executor returning
                `(instance, created)`.

        Raises:
            ValueError:
                If `dynamic_environment` is true and `creation_gate` is not
                supplied.
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

    @classmethod
    def load_cached(
            cls,
            *,
            spell: "Spell",
            dynamic_environment: bool = False,
            creation_gate: Optional["CreationGate"] = None,
            creation_gate_index_id: Optional[str] = None,
            no_overrides_executor: Optional[Callable[..., Any]],
            overrides_executor: Optional[Callable[..., Any]],
            publish: bool = False,
    ) -> "CreationContext":
        """
        Build one generic CreationContext from already-rehydrated cache outputs.

        Purpose:
            Keep cache rehydration out of the constructor call sites while still
            letting experiments or future cache loaders publish a spell-bound
            context from prebuilt executors.
        """
        loaded_creation_context = cls(
            spell=spell,
            dynamic_environment=dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=creation_gate_index_id,
            no_overrides_executor=no_overrides_executor,
            overrides_executor=overrides_executor,
        )
        if publish:
            previous_creation_context = spell._creation_context
            spell._creation_context = loaded_creation_context
            current_state = spell._creation_context_switch.state
            if current_state < 2:
                spell._creation_context_switch.advance(2 - current_state)
            elif current_state > 2:
                spell._creation_context_switch.advance(-(current_state - 2))
            if (
                    previous_creation_context is not None
                    and previous_creation_context is not loaded_creation_context
            ):
                try:
                    previous_creation_context.cleanup()
                except Exception:
                    pass
        return loaded_creation_context

    def execute(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, bool]:
        """
        Execute one meld resolution through the hooks-aware runtime doors.

        `unique_per_conduit_lineage` routing reads the lineage-root store off
        `caller_creations._root_creations` inside the door, so no extra argument
        is threaded here.
        """
        if not self._dynamic_environment:
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(caller_creations)
            overrides_executor = self._overrides_executor
            return overrides_executor(caller_creations, overrides)

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
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(caller_creations)
            overrides_executor = self._overrides_executor
            return overrides_executor(caller_creations, overrides)
        finally:
            creation_gate.unregister_ticket()

    def execute_no_hooks(
            self,
            caller_creations: "Creations",
            overrides: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute one meld resolution through the direct no-hooks runtime doors.

        `unique_per_conduit_lineage` routing reads the lineage-root store off
        `caller_creations._root_creations` inside the door, so no extra argument
        is threaded here.
        """
        if not self._dynamic_environment:
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(caller_creations)[0]
            overrides_executor = self._overrides_executor
            return overrides_executor(caller_creations, overrides)[0]

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
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(caller_creations)[0]
            overrides_executor = self._overrides_executor
            return overrides_executor(caller_creations, overrides)[0]
        finally:
            creation_gate.unregister_ticket()
