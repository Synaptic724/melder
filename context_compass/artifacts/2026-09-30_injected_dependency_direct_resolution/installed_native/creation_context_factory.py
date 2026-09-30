from typing import TYPE_CHECKING, Optional, Set, ClassVar

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
    from melder.utilities.synchronization.creation_gate import CreationGate
    from melder.utilities.synchronization.creation_gate_controller import (
        CreationGateController,
    )



from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable


class CreationContextFactory(Cleanable):
    """
    Produce spell-shaped `CreationContext` instances.

    Purpose:
        Keep Meld front-door logic minimal by centralizing context construction
        behind one factory contract.

    Contract:
        - Factory does not own shared caches outside spell ownership.
        - Spell owns the context lifecycle through `spell._creation_context`.
        - Get-or-build path is lock-free and race-tolerant.
        - Factory delegates all shape rules to `CreationContextBuilder`.
        - In dynamic mode, the factory resolves /creates one spell-index gate
          and injects it into built contexts for runtime execution admission.

    Owned State:
        `_dynamic_environment`, `_creation_gate_controller`, and
        `_created_spell_index_ids` (the set of index ids this factory has
        already provisioned a gate for).

    Threading:
        LOCK-FREE on the ready path. The cold path elects exactly one builder
        through the spell's CounterSwitch (followers park until it publishes).
        A builder that fails records the cause on the spell and releases its
        claim, so followers wake and report that cause instead of waiting for
        a publication that will never come. Input stability comes from the
        spell-index gate: dynamic melds build and execute while holding a
        ticket, and rebuild windows drain those tickets before phases replace
        the plan (see CreationContextRebuild).

    Lifecycle / Cleanup:
        Cleanable. It does NOT own the contexts it produces - `Spell` owns them
        through `spell._creation_context`, which is why factory cleanup cannot
        strand a live context.

    Registration:
        MELDER KERNEL - guarded. Constructed by the conduit runtime; never
        user-instantiated and never bindable.

    Subsystem Context:
        The WHEN half of context construction, paired with
        `CreationContextBuilder` (the WHAT). It sits between the meld doors and
        the builder, and it is the seam where dynamic-mode admission gets wired
        in - the builder itself stays policy-free.

    System Context:
        The ready path stays lock-free because it runs on every meld; the
        cold path is a per-spell election, never a global lock, so cold builds
        of different spells never contend. The factory does not guard its
        inputs: a build reads the spell's phase-11 plan, and keeping that plan
        present during the build is the rebuild window's job, not the
        factory's.
        The gate injection is why this class is dynamic-aware at all. In
        dynamic mode, execution admission is per-spell-index rather than
        per-conduit, so the factory resolves or creates ONE gate per index and
        threads it into the contexts it builds; `_created_spell_index_ids`
        exists so that provisioning happens once per index rather than once per
        context.

    AGENT_ACCESS: internal

    AGENT_PURPOSE:
        access: internal. Produce spell-shaped `CreationContext` instances. Melder kernel
        machinery: read it to understand the runtime, do not drive it directly.
    """

    __slots__ = Cleanable.__slots__ + [
        "_dynamic_environment",
        "_creation_gate_controller",
        "_created_spell_index_ids",
    ]

    def __init__(
            self,
            *,
            dynamic_environment: bool = False,
            creation_gate_controller: CreationGateController,
    ) -> None:
        """
        Initialize one factory.

        Args:
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. Propagated
                to build CreationContext instances.
            creation_gate_controller:
                Frame-owned CreationGateController used for spell-index gate
                registration and ticket governance during dynamic runtime.

        Raises:
            ValueError:
                If `creation_gate_controller` is None.

        Returns:
            None.
        """
        super().__init__()
        if creation_gate_controller is None:
            raise ValueError("creation_gate_controller cannot be None.")
        self._dynamic_environment: bool = bool(dynamic_environment)
        self._creation_gate_controller: CreationGateController = (
            creation_gate_controller
        )
        self._created_spell_index_ids: Set[str] = set()

    def cleanup(self) -> None:
        """
        Deterministically release the factory.

        Contract:
            - Idempotent cleanup.
            - Best-effort cleanup of builder-owned resources is unnecessary
              because the builder is stateless.
            - Clears builder-free reference usage to prevent post-clean confusion.

        Returns:
            None.
        """
        if self._cleaned:
            return
        self._cleaned = True

        self._created_spell_index_ids.clear()

        del self._dynamic_environment
        del self._creation_gate_controller
        del self._created_spell_index_ids

    @staticmethod
    def _cleanup_creation_context(
            creation_context: Optional[CreationContext],
    ) -> None:
        """
        Best-effort cleanup helper for a superseded spell-owned context.

        This is used when publication logic replaces one spell-bound
        `CreationContext` with another and needs to retire the old instance
        without letting cleanup failures break the successful publish path.
        """
        if creation_context is None:
            return
        try:
            creation_context.cleanup()
        except Exception:
            pass

    @staticmethod
    def _stage_cache_after_publish(
            spell: Spell,
            creation_context: CreationContext,
    ) -> None:
        """
        Stage the published CreationContext cache bundle into Spellbook memory.

        Contract:
            - No-op when spell-level caching is disabled.
            - Uses the just-published CreationContext bundle directly.
            - Stages only. File persistence is deferred to the enclosing
              top-level operation boundary (conjure or meld).
        """
        if not spell._caching_enabled:
            return
        _ = creation_context
        spell.emit_cache()


    def _index_id_for_spell(self, spell: Spell) -> str:
        """
        Return the stable spell-index id used for gate-controller operations.

        The factory keys creation-gate registration by SpellIndex identity
        rather than by the current spell version, so all contexts for the same
        spell-index slot share one admission gate.

        Args:
            spell: Spell whose spell-index id should be resolved.

        Returns:
            str: Stable spell-index id derived from `SpellIndex.id`.
        """
        return spell.spell_index.id

    def _resolve_or_create_spell_index_gate(self, index_id: str) -> CreationGate:
        """
        Return the shared creation gate for one spell index.

        The factory does not perform admission or ticket management itself; it
        only ensures that every context built for the same index sees the
        same `CreationGate` object. If the controller has not seen the index
        yet, the gate is created and the index id is recorded as factory-
        created bookkeeping.

        Args:
            index_id: Stable spell-index key.

        Returns:
            CreationGate: Shared gate object for this spell index.
        """
        creation_gate_controller = self._creation_gate_controller
        gate = creation_gate_controller.get_spell_index_gate(index_id)
        if gate is not None:
            return gate
        gate = creation_gate_controller.create_spell_index_gate(index_id)
        self._created_spell_index_ids.add(index_id)
        return gate

    def _resolve_runtime_gate_for_spell(
            self,
            spell: Spell,
    ) -> tuple[Optional[CreationGate], Optional[str]]:
        """
        Resolve the gate metadata that should be injected into the built
        context.

        This is the mode switch between automatic and dynamic runtime paths:

        - automatic mode builds contexts with no gate metadata
        - dynamic mode injects the shared spell-index gate plus its stable id so the
          context can enforce runtime admission checks during execute paths

        Args:
            spell: Spell whose runtime gate metadata should be attached.

        Returns:
            tuple[Optional[CreationGate], Optional[str]]:
                `(gate, index_id)` for context runtime admission checks.
        """
        if not self._dynamic_environment:
            return None, None
        index_id = self._index_id_for_spell(spell)
        gate = self._resolve_or_create_spell_index_gate(index_id)
        return gate, index_id

    def build_for_spell(self, spell: "Spell") -> "CreationContext":
        """
        Build one fresh context for the spell without publishing it back onto
        the spell.

        Args:
            spell: Spell that conceptually owns the built context.

        Returns:
            CreationContext: New spell-shaped context ready for runtime use.
        """
        creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
        return CreationContextBuilder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=index_id,
        )

    def build_and_bind_for_spell(self, spell: "Spell") -> "CreationContext":
        """
        Build one CreationContext and bind it onto the target spell.

        Contract:
            - Always builds a fresh context from the current spell state.
            - Replaces any existing spell-owned context reference.
            - Best-effort cleans replaced context.
            - Opens the spell-owned CounterSwitch latch after publish.
            - Does not use spell lock primitives.
        """
        creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
        built_creation_context = CreationContextBuilder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_index_id=index_id,
        )
        previous_creation_context = spell._creation_context
        spell._creation_context = built_creation_context
        self._set_creation_context_switch_open(spell)
        self._stage_cache_after_publish(spell, built_creation_context)
        self._cleanup_creation_context(previous_creation_context)
        return built_creation_context

    def resolve_spell_index_gate(self, spell: "Spell") -> Optional[CreationGate]:
        """
        Return the shared spell-index CreationGate the spell's contexts use.

        Contract:
            - Automatic mode: returns None (no runtime admission gate).
            - Dynamic mode: returns the controller's gate for the spell's
              stable index id, creating it on first use exactly as
              `build_for_spell` would.

        Args:
            spell: Spell whose index gate is resolved.

        Returns:
            Optional[CreationGate]:
                The gate borrowed from the frame's controller, or None.
        """
        return self._resolve_runtime_gate_for_spell(spell)[0]

    def get_or_build_for_spell(self, spell: "Spell") -> "CreationContext":
        """
        Resolve one spell-owned context via spell-level CounterSwitch election.

        Contract:
            - Uses `spell._creation_context_switch.selector()` for one-leader
              get-or-build election.
            - Leader builds/publishes context and opens latch to state `2`,
              then clears any recorded build failure.
            - Leader failure records the exception on
              `spell._creation_context_failure`, releases its claim (state
              1 -> 0, which wakes followers) and re-raises the original.
            - Followers block while pending (`state == 1`) and then read the
              published context; a follower woken by a failed leader raises
              RuntimeError chained from the recorded cause.
            - Context ownership remains on Spell (`spell._creation_context`).
            - Does not use `spell._lock` for hot-path access/publication.
            - Does not inspect `CreationContext.is_cleaned`; switch state is
              treated as the single source of truth for readiness.
            - Single selector pass: no retry loops.

        Args:
            spell: Spell whose context is resolved.

        Returns:
            CreationContext:
                Spell-owned cached or newly built context.

        Raises:
            RuntimeError:
                Propagated from `CreationContextBuilder.build` for the leader;
                raised for a follower when no context was published.
        """
        creation_context_switch = spell._creation_context_switch
        if creation_context_switch.state >= 2:
            creation_context = spell._creation_context
            if creation_context is None:
                raise RuntimeError(
                    "Spell creation context switch is open but no context is published."
                )
            return creation_context
        switch_state = creation_context_switch.selector()
        if switch_state == 1:
            creation_gate, index_id = self._resolve_runtime_gate_for_spell(spell)
            try:
                built_creation_context = CreationContextBuilder.build(
                    spell,
                    dynamic_environment=self._dynamic_environment,
                    creation_gate=creation_gate,
                    creation_gate_index_id=index_id,
                )
            except BaseException as error:
                # Release the claim so parked followers wake and report this
                # cause; a pending latch with no builder would park them forever.
                spell._creation_context_failure = error
                if creation_context_switch.state == 1:
                    creation_context_switch.advance(-1)
                raise
            spell._creation_context = built_creation_context
            creation_context_switch.advance(1)
            spell._creation_context_failure = None
            self._stage_cache_after_publish(spell, built_creation_context)
            return built_creation_context
        creation_context = spell._creation_context
        if creation_context is None:
            failure = spell._creation_context_failure
            if failure is not None:
                raise RuntimeError(
                    "Spell creation context was not published: the selected "
                    f"builder failed ({type(failure).__name__}: {failure})."
                ) from failure
            raise RuntimeError(
                "Spell creation context was not published by the selected builder."
            )
        return creation_context

    @staticmethod
    def _set_creation_context_switch_open(spell: Spell) -> None:
        """
        Force a spell-owned CounterSwitch into an open latch state (`2`).

        Purpose:
            Normalize switch state after a successful context publication so
            readers can take the hot path without waiting.

        Contract:
            - `state < 2` is advanced upward to `2`.
            - `state > 2` is reduced down to `2`.
            - Uses only CounterSwitch public API (`state`, `advance`).

        Args:
            spell:
                Spell whose switch should be normalized to open state.

        Returns:
            None.
        """
        current_state = spell._creation_context_switch.state
        if current_state < 2:
            spell._creation_context_switch.advance(2 - current_state)
        elif current_state > 2:
            spell._creation_context_switch.advance(-(current_state - 2))

    def rebuild_for_spell(self, spell: "Spell") -> "CreationContext":
        """
        Force rebuild and replace the spell-owned CreationContext.

        Contract:
            - Ignores existing context cache hit.
            - Useful for explicit runtime rebind flows.
        """
        return self.build_and_bind_for_spell(spell)



