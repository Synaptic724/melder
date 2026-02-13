from typing import Optional, Set

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.interfaces import ISpell
from melder.utilities.synchronization.creation_gate import CreationGate
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


class CreationContextFactory(Cleanable):
    """
    Produce spell-shaped `CreationContext` instances.

    Purpose:
        Keep Meld front-door logic minimal by centralizing context construction
        behind one factory contract.

    Contract:
        - Factory does not own shared caches outside spell ownership.
        - Spell owns context lifecycle through `spell._creation_context`.
        - Get-or-build path is lock-free and race-tolerant.
        - Factory delegates all shape rules to `CreationContextBuilder`.
        - In dynamic mode, factory resolves/creates one spell-lineage gate
          and injects it into built contexts for runtime execution admission.
    """

    __slots__ = Cleanable.__slots__ + [
        "_builder",
        "_dynamic_environment",
        "_creation_gate_controller",
        "_created_spell_lineage_ids",
    ]

    def __init__(
            self,
            *,
            builder: Optional[CreationContextBuilder] = None,
            dynamic_environment: bool = False,
            creation_gate_controller: CreationGateController,
    ) -> None:
        """
        Initialize one factory.

        Args:
            builder:
                Optional custom builder. Defaults to `CreationContextBuilder`.
            dynamic_environment:
                True when the owning conduit runs in dynamic mode. Propagated
                to built CreationContext instances.
            creation_gate_controller:
                Frame-owned CreationGateController used for spell-lineage gate
                registration and ticket governance during dynamic runtime.

        Raises:
            ValueError:
                If `creation_gate_controller` is None.
        """
        super().__init__()
        if creation_gate_controller is None:
            raise ValueError("creation_gate_controller cannot be None.")
        if builder is None:
            builder = CreationContextBuilder()
        self._builder: CreationContextBuilder = builder
        self._dynamic_environment: bool = bool(dynamic_environment)
        self._creation_gate_controller: CreationGateController = (
            creation_gate_controller
        )
        self._created_spell_lineage_ids: Set[str] = set()

    def cleanup(self) -> None:
        """
        Deterministically release the factory and its builder reference.

        Contract:
            - Idempotent cleanup.
            - Best-effort cleanup is forwarded to the owned builder.
            - Clears builder reference to prevent post-clean usage.
        """
        if self._cleaned:
            return
        self._cleaned = True

        try:
            self._builder.cleanup()
        except Exception:
            pass
        self._builder = None
        self._dynamic_environment = None
        self._creation_gate_controller = None
        self._created_spell_lineage_ids.clear()
        self._created_spell_lineage_ids = None

    @staticmethod
    def _cleanup_creation_context(
            creation_context: Optional[CreationContext],
    ) -> None:
        """
        Best-effort cleanup helper for detached CreationContext instances.
        """
        if creation_context is None:
            return
        try:
            creation_context.cleanup()
        except Exception:
            pass


    def _lineage_id_for_spell(self, spell: ISpell) -> str:
        """
        Internal

        Resolve the spell-lineage identifier used for gate registry operations.

        Contract:
            - Uses SpellIndex lineage id as the stable spell-lineage key.

        Args:
            spell:
                Spell whose lineage id should be resolved.

        Returns:
            str:
                Stable spell-lineage id.
        """
        return spell.spell_index.id

    def _resolve_or_create_spell_lineage_gate(self, lineage_id: str) -> CreationGate:
        """
        Internal

        Resolve existing or create a new spell-lineage CreationGate.

        Contract:
            - Reuses existing lineage gate when already registered.
            - Creates and registers a new lineage gate when missing.
            - Factory does not perform gate admission/ticket operations.

        Args:
            lineage_id:
                Spell-lineage key.

        Returns:
            CreationGate:
                Resolved gate for this lineage.
        """
        creation_gate_controller = self._creation_gate_controller
        gate = creation_gate_controller.get_spell_lineage_gate(lineage_id)
        if gate is not None:
            return gate
        gate = creation_gate_controller.create_spell_lineage_gate(lineage_id)
        self._created_spell_lineage_ids.add(lineage_id)
        return gate

    def _resolve_runtime_gate_for_spell(
            self,
            spell: ISpell,
    ) -> tuple[Optional[CreationGate], Optional[str]]:
        """
        Internal

        Resolve runtime gate metadata injected into built CreationContext objects.

        Contract:
            - Automatic mode returns `(None, None)`.
            - Dynamic mode returns a shared spell-lineage gate and lineage id.

        Args:
            spell:
                Spell target whose lineage gate should be attached.

        Returns:
            tuple[Optional[CreationGate], Optional[str]]:
                `(gate, lineage_id)` for context runtime admission checks.
        """
        if not self._dynamic_environment:
            return None, None
        lineage_id = self._lineage_id_for_spell(spell)
        gate = self._resolve_or_create_spell_lineage_gate(lineage_id)
        return gate, lineage_id

    def build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Build one context for the given spell.

        Args:
            spell:
                Spell that will own the built context.

        Returns:
            CreationContext:
                New spell-shaped context ready for runtime execution.
        """
        creation_gate, lineage_id = self._resolve_runtime_gate_for_spell(spell)
        return self._builder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_lineage_id=lineage_id,
        )

    def build_and_bind_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Build one CreationContext and bind it onto the target spell.

        Contract:
            - Always builds a fresh context from current spell state.
            - Replaces any existing spell-owned context reference.
            - Best-effort cleans replaced context.
            - Opens the spell-owned CounterSwitch latch after publish.
            - Does not use spell lock primitives.
        """
        creation_gate, lineage_id = self._resolve_runtime_gate_for_spell(spell)
        built_creation_context = self._builder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_lineage_id=lineage_id,
        )
        previous_creation_context = spell._creation_context
        spell._creation_context = built_creation_context
        self._set_creation_context_switch_open(spell)
        self._cleanup_creation_context(previous_creation_context)
        return built_creation_context

    def get_or_build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Resolve one spell-owned context via spell-level CounterSwitch election.

        Contract:
            - Uses `spell._creation_context_switch.selector()` for one-leader
              get-or-build election.
            - Leader builds/publishes context and opens latch to state `2`.
            - Followers block while pending (`state == 1`) and then read cache.
            - Context ownership remains on Spell (`spell._creation_context`).
            - Does not use `spell._lock` for hot-path access/publication.
            - Does not inspect `CreationContext.is_cleaned`; switch state is
              treated as the single source of truth for readiness.
            - Single selector pass: no retry loops.

        Returns:
            CreationContext:
                Spell-owned cached or newly built context.
        """
        creation_context_switch = spell._creation_context_switch
        if creation_context_switch.state >= 2:
            return spell._creation_context
        switch_state = creation_context_switch.selector()
        if switch_state == 1:
            creation_gate, lineage_id = self._resolve_runtime_gate_for_spell(spell)
            built_creation_context = self._builder.build(
                spell,
                dynamic_environment=self._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_lineage_id=lineage_id,
            )
            spell._creation_context = built_creation_context
            creation_context_switch.advance(1)
            return built_creation_context
        return spell._creation_context

    @staticmethod
    def _set_creation_context_switch_open(spell: ISpell) -> None:
        """
        Internal

        Force a spell-owned CounterSwitch into open latch state (`2`).

        Purpose:
            Normalize switch state after successful context publication so
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

    def rebuild_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Force rebuild and replace the spell-owned CreationContext.

        Contract:
            - Ignores existing context cache hit.
            - Useful for explicit runtime rebind flows.
        """
        return self.build_and_bind_for_spell(spell)
