from typing import Optional, Callable, Set

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
        - In dynamic mode, spell-lineage gate operations are coordinated
          through `CreationGateController`.
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

    def _resolve_or_create_spell_lineage_gate(
            self,
            lineage_id: str,
    ) -> CreationGate:
        """
        Internal

        Resolve existing or create a new spell-lineage CreationGate.

        Contract:
            - Reuses existing lineage gate when already registered.
            - Creates and registers a new lineage gate when missing.
            - Tracks only gates created by this factory instance.

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

    @staticmethod
    def _enter_spell_lineage_gate(
            gate: CreationGate,
            lineage_id: str,
    ) -> None:
        """
        Internal

        Enter one spell-lineage gate admission section for context operations.

        Contract:
            - Raises immediately when lineage gate is terminally closed.
            - Waits when lineage gate is temporarily disabled.
            - Registers one active ticket on successful admission.

        Args:
            gate:
                Target spell-lineage gate.
            lineage_id:
                Spell-lineage key used in diagnostics.

        Returns:
            None.

        Raises:
            RuntimeError:
                If the lineage gate is closed.
        """
        if gate.is_closed():
            raise RuntimeError(
                f"CreationGate is closed for spell lineage '{lineage_id}'."
            )
        if not gate.enabled:
            gate.wait()
            if gate.is_closed():
                raise RuntimeError(
                    f"CreationGate is closed for spell lineage '{lineage_id}'."
                )
        gate.register_ticket()

    @staticmethod
    def _leave_spell_lineage_gate(gate: CreationGate) -> None:
        """
        Internal

        Leave one spell-lineage gate admission section.

        Contract:
            - Unregisters one ticket previously registered by enter path.

        Args:
            gate:
                Target spell-lineage gate.

        Returns:
            None.
        """
        gate.unregister_ticket()

    def _run_with_optional_spell_lineage_gate(
            self,
            spell: ISpell,
            operation: Callable[[Optional[CreationGate], Optional[str]], CreationContext],
    ) -> CreationContext:
        """
        Internal

        Execute one factory operation with optional dynamic spell-lineage gating.

        Contract:
            - Automatic mode executes operation directly.
            - Dynamic mode uses spell-lineage gate admission + ticket tracking.
            - Gate ticket is always released on exit.

        Args:
            spell:
                Spell target for lineage lookup.
            operation:
                Operation callback to execute under gate governance.
                Receives `(creation_gate, lineage_id)` in dynamic mode and
                `(None, None)` in automatic mode.

        Returns:
            CreationContext:
                Operation result.
        """
        if not self._dynamic_environment:
            return operation(None, None)

        lineage_id = self._lineage_id_for_spell(spell)
        gate = self._resolve_or_create_spell_lineage_gate(lineage_id)
        self._enter_spell_lineage_gate(gate, lineage_id)
        try:
            return operation(gate, lineage_id)
        finally:
            self._leave_spell_lineage_gate(gate)

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
        self.check_cleaned()
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
        """
        self.check_cleaned()
        def _operation(
                creation_gate: Optional[CreationGate],
                lineage_id: Optional[str],
        ) -> CreationContext:
            built_creation_context = self._builder.build(
                spell,
                dynamic_environment=self._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_lineage_id=lineage_id,
            )
            with spell._lock:
                spell.check_cleaned()
                previous_creation_context = spell._creation_context
                if built_creation_context.is_cleaned:
                    self._cleanup_creation_context(built_creation_context)
                    raise RuntimeError(
                        "Cannot publish a cleaned CreationContext to spell cache."
                    )
                spell._creation_context = built_creation_context
            self._cleanup_creation_context(previous_creation_context)
            return built_creation_context

        return self._run_with_optional_spell_lineage_gate(spell, _operation)

    def get_or_build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Resolve one spell-owned context and build on miss without locks.

        Contract:
            - Lock-free miss path by design.
            - Duplicate concurrent builds are accepted if output is equivalent.
            - Context ownership remains on Spell (`spell._creation_context`).
        """
        def _operation(
                creation_gate: Optional[CreationGate],
                lineage_id: Optional[str],
        ) -> CreationContext:
            current_creation_context = spell._creation_context
            if (
                    current_creation_context is not None
                    and not current_creation_context.is_cleaned
            ):
                return current_creation_context

            built_creation_context = self._builder.build(
                spell,
                dynamic_environment=self._dynamic_environment,
                creation_gate=creation_gate,
                creation_gate_lineage_id=lineage_id,
            )
            with spell._lock:
                spell.check_cleaned()
                current_creation_context = spell._creation_context
                if (
                        current_creation_context is None
                        or current_creation_context.is_cleaned
                ):
                    if built_creation_context.is_cleaned:
                        self._cleanup_creation_context(built_creation_context)
                        raise RuntimeError(
                            "Cannot publish a cleaned CreationContext to spell cache."
                        )
                    spell._creation_context = built_creation_context
                    return built_creation_context

            self._cleanup_creation_context(built_creation_context)
            if current_creation_context is None:
                raise RuntimeError("Failed to publish CreationContext for spell.")
            return current_creation_context

        return self._run_with_optional_spell_lineage_gate(spell, _operation)

    def rebuild_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Force rebuild and replace the spell-owned CreationContext.

        Contract:
            - Ignores existing context cache hit.
            - Useful for explicit runtime rebind flows.
        """
        self.check_cleaned()
        return self.build_and_bind_for_spell(spell)

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

        creation_gate_controller = self._creation_gate_controller
        for lineage_id in list(self._created_spell_lineage_ids):
            try:
                gate = creation_gate_controller.get_spell_lineage_gate(lineage_id)
                if gate is not None:
                    creation_gate_controller.unregister_spell_lineage_gate(lineage_id)
                    gate.cleanup()
            except Exception:
                pass
        self._created_spell_lineage_ids.clear()

        builder = self._builder
        if builder is not None:
            try:
                builder.cleanup()
            except Exception:
                pass
        self._builder = None
        self._dynamic_environment = None
        self._creation_gate_controller = None
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
