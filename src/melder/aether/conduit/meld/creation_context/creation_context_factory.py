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
        creation_gate, lineage_id = self._resolve_runtime_gate_for_spell(spell)
        built_creation_context = self._builder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_lineage_id=lineage_id,
        )
        previous_creation_context: Optional[CreationContext] = None
        publish_error: Optional[Exception] = None

        with spell._lock:
            try:
                spell.check_cleaned()
            except Exception as exc:
                publish_error = exc
            else:
                previous_creation_context = spell._creation_context
                if built_creation_context.is_cleaned:
                    publish_error = RuntimeError(
                        "Cannot publish a cleaned CreationContext to spell cache."
                    )
                else:
                    spell._creation_context = built_creation_context

        if publish_error is not None:
            self._cleanup_creation_context(built_creation_context)
            raise publish_error

        self._cleanup_creation_context(previous_creation_context)
        return built_creation_context

    def get_or_build_for_spell(self, spell: ISpell) -> CreationContext:
        """
        Resolve one spell-owned context and build on miss without locks.

        Contract:
            - Lock-free miss path by design.
            - Duplicate concurrent builds are accepted if output is equivalent.
            - Context ownership remains on Spell (`spell._creation_context`).
        """
        self.check_cleaned()
        current_creation_context = spell._creation_context
        if (
                current_creation_context is not None
                and not current_creation_context.is_cleaned
        ):
            return current_creation_context

        creation_gate, lineage_id = self._resolve_runtime_gate_for_spell(spell)
        built_creation_context = self._builder.build(
            spell,
            dynamic_environment=self._dynamic_environment,
            creation_gate=creation_gate,
            creation_gate_lineage_id=lineage_id,
        )

        with spell._lock:
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

        builder = self._builder
        if builder is not None:
            try:
                builder.cleanup()
            except Exception:
                pass
        self._builder = None
        self._dynamic_environment = None
        self._creation_gate_controller = None
        created_spell_lineage_ids = self._created_spell_lineage_ids
        created_spell_lineage_ids.clear()
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
