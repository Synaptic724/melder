from typing import TYPE_CHECKING, Any, Callable, ClassVar, Optional

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
          `_no_overrides_executor`, `_no_overrides_instance_executor`, and
          `_overrides_executor` directly on their non-dynamic no-hooks fast
          lane. Those reads are per-call through the live spell-published
          context and are never cached on the doors, so context
          replacement/cleanup semantics are unchanged. Renaming or
          repurposing these slots requires updating both doors.
        - `_no_overrides_instance_executor` is the INSTANCE-ONLY twin of
          `_no_overrides_executor` (same inner executor wrapped by the
          instance-variant route template, `(meld) -> instance`). The
          no-hooks lanes call it to avoid allocating and discarding the
          `(instance, created)` tuple on every warm meld; the hooks lane
          keeps the tuple door. Both slots swap TOGETHER at every publish
          site (cold -> hot -> specialized) and share the self-replacing
          contract.
        - Executor slots are SELF-REPLACING: generalized hydration installs
          cold delegating doors first and hot-swaps the final hydrated
          executors into `_no_overrides_executor` / `_overrides_executor` in
          place on first execution. Any reader that retains an executor
          reference across calls pins the cold door and defeats the swap;
          readers must re-read the slot per call.

    Owned State:
        The four executor slots plus `_dynamic_environment` and the creation
        gate handles. The executor slots are MUTABLE by design - see the
        self-replacing contract above.

    Threading:
        Hot path under free-threaded 3.14t. The self-replacing slots are
        written in place on first execution, so concurrent callers may race to
        install the hydrated door; the swap is idempotent because both threads
        compute the same executor. Gate admission is enforced per call rather
        than cached.

    Lifecycle / Cleanup:
        Owned by the `Spell` (`spell._creation_context`), not by a meld door.
        Cleanup bumps the spell's door epoch, which is what invalidates the
        meld doors' warm fast-lane entries.

    Registration:
        MELDER KERNEL - guarded. Built by `CreationContextBuilder` through
        `CreationContextFactory`; never user-instantiated and never bindable.

    Subsystem Context:
        The last object between `Meld` and a real instance. Meld resolves the
        spell and decides reuse-vs-construct; this class executes the phase-11
        doors that actually build it and register it into `Creations`. The two
        meld doors read its slots directly on their fast lane, which is why the
        docstring names those slots as an internal contract rather than an
        implementation detail.

    System Context:
        The self-replacing executor design is a cold-start optimization with a
        sharp edge, and the edge is the reason it is documented so loudly.
        Phase 11 installs a COLD delegating door first so the context is usable
        immediately; on first execution the hydrated executor replaces it in
        place. That means the slot IS the indirection - anything that caches an
        executor reference across calls pins the cold door forever and silently
        loses the optimization, which is exactly why `Meld`'s fast-door registry
        stores the CONTEXT and re-reads `_no_overrides_executor` per hit rather
        than storing the executor itself.
        The instance-only twin exists for the same reason at a smaller scale:
        warm no-hooks melds are the common case, and returning `(instance,
        created)` there would allocate and immediately discard a tuple on every
        resolution. The hooks lane keeps the tuple door because it genuinely
        needs the `created` flag to decide whether activation hooks fire.
    """
    __ast_helper_access__: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Spell-bound runtime executor context. Melder kernel machinery: read it "
        "to understand the runtime, do not drive it directly."
    )

    __slots__ = Cleanable.__slots__ + [
        "_spell",
        "_spell_id",
        "_dynamic_environment",
        "_creation_gate",
        "_creation_gate_index_id",
        "_no_overrides_executor",
        "_no_overrides_instance_executor",
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
            no_overrides_instance_executor: Optional[Callable[..., Any]] = None,
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
            no_overrides_instance_executor:
                Instance-only twin of `no_overrides_executor` returning the
                bare instance; consumed by the no-hooks meld lanes.
            overrides_executor:
                Phase-11-provided final overrides executor returning
                `(instance, created)`.

        Raises:
            ValueError:
                If `dynamic_environment` is true and `creation_gate` is not
                supplied.

        Returns:
            None.
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
        self._no_overrides_instance_executor = no_overrides_instance_executor
        self._overrides_executor = overrides_executor

    def cleanup(self) -> None:
        """
        Deterministically release runtime references.

        Returns:
            None.
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
        del self._no_overrides_instance_executor
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
            no_overrides_instance_executor: Optional[Callable[..., Any]] = None,
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
            no_overrides_instance_executor=no_overrides_instance_executor,
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
            meld: "Meld",
            overrides: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, bool]:
        """
        Execute one meld resolution through the hooks-aware runtime doors.

        `unique_per_conduit_lineage` routing reads the lineage-root store off
        `meld._root_creations` inside the door, so no extra argument
        is threaded here.
        """
        if not self._dynamic_environment:
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(meld)
            overrides_executor = self._overrides_executor
            return overrides_executor(meld, overrides)

        creation_gate = self._creation_gate
        index_id = self._creation_gate_index_id
        if creation_gate is None:
            raise RuntimeError(
                f"CreationGate is unavailable for spell index '{index_id}'."
            )
        # Ticket-first admission (drain-race fix 2026-07-12): visible
        # ticket before state validation - see CreationGate.admit_ticket.
        creation_gate.admit_ticket()
        try:
            if overrides is None:
                no_overrides_executor = self._no_overrides_executor
                return no_overrides_executor(meld)
            overrides_executor = self._overrides_executor
            return overrides_executor(meld, overrides)
        finally:
            creation_gate.unregister_ticket()

    def execute_no_hooks(
            self,
            meld: "Meld",
            overrides: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Execute one meld resolution through the direct no-hooks runtime doors.

        `unique_per_conduit_lineage` routing reads the lineage-root store off
        `meld._root_creations` inside the door, so no extra argument
        is threaded here.
        """
        if not self._dynamic_environment:
            if overrides is None:
                # Instance-only door: no (instance, created) tuple to build
                # and discard on the no-hooks lane.
                return self._no_overrides_instance_executor(meld)
            overrides_executor = self._overrides_executor
            return overrides_executor(meld, overrides)[0]

        creation_gate = self._creation_gate
        index_id = self._creation_gate_index_id
        if creation_gate is None:
            raise RuntimeError(
                f"CreationGate is unavailable for spell index '{index_id}'."
            )
        # Ticket-first admission (drain-race fix 2026-07-12): visible
        # ticket before state validation - see CreationGate.admit_ticket.
        creation_gate.admit_ticket()
        try:
            if overrides is None:
                return self._no_overrides_instance_executor(meld)
            overrides_executor = self._overrides_executor
            return overrides_executor(meld, overrides)[0]
        finally:
            creation_gate.unregister_ticket()
