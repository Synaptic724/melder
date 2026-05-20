from typing import Optional

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler import (
    SpellCompiler,
)
from melder.aether.spellbook.spell_crafter.spell_crafter import SpellCrafter
from melder.aether.spellbook.spell_crafter.validation.validation_system import (
    SpellValidationSystem,
)
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import (
    CancellationEvent,
)


@mypyc_attr(native_class=True)
class SpellCompilerSystem(Cleanable):
    """
    Compiler-owned orchestration surface for spell compilation phases.

    Purpose:
        Own the instantiated compiler and the validator collaborator used to
        execute spell compilation phases against spell-owned
        `SpellCompilerArtifact` state.

    Contract:
        - Owns one borrowed `Spellbook` reference.
        - Owns one instantiated `SpellCompiler`.
        - Owns one instantiated `SpellValidationSystem`.
        - Does not own per-spell compiler artifact state; that remains on the
          spell.
        - Current wiring covers phases 1-5 only in this tranche.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spellbook",
        "_spell_compiler",
        "_spell_validator",
    ]

    def __init__(self, spellbook: ISpellbook) -> None:
        """
        Initialize one compiler-system foundation object.

        Args:
            spellbook:
                Spellbook whose spell/compiler context this system serves.

        Raises:
            ValueError:
                If spellbook is None.
        """
        super().__init__()
        if spellbook is None:
            raise ValueError("spellbook cannot be None.")
        self._spellbook: ISpellbook = spellbook
        self._spell_compiler: SpellCompiler = SpellCompiler()
        self._spell_validator: SpellValidationSystem = SpellValidationSystem()

    def cleanup(self) -> None:
        """
        Release owned compiler collaborators and the borrowed spellbook reference.

        Contract:
            - Idempotent cleanup.
            - Does not clean the spellbook itself.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spell_validator
        del self._spell_compiler
        del self._spellbook

    def create_spell_crafter_for_spell(self, spell: ISpell) -> SpellCrafter:
        """
        Create one concrete SpellCrafter for the supplied spell.

        Args:
            spell:
                Spell whose crafter surface should be materialized.

        Returns:
            SpellCrafter:
                Concrete crafter bound to the supplied spell.
        """
        return SpellCrafter(spell)

    def run_phase_requirements(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 1 for the supplied spell.
        """
        self._spell_compiler.run_phase_requirements(
            spell,
            spell._compiler_artifact,
            cancel_event=cancel_event,
        )

    def run_phase_symbolic_graph(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 2 for the supplied spell.
        """
        self._spell_compiler.run_phase_symbolic_graph(
            spell,
            spell._compiler_artifact,
            cancel_event=cancel_event,
        )

    def run_phase_local_frame(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 3 for the supplied spell.
        """
        self._spell_compiler.run_phase_local_frame(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_validation(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 4 for the supplied spell.
        """
        self._spell_compiler.run_phase_validation(
            spell,
            spell._compiler_artifact,
            self._spell_validator,
            self._spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 5 for the supplied spell and conduit scope.
        """
        self._spell_compiler.run_phase_root_blueprints(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints_local(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 5 local-scope variant.
        """
        self._spell_compiler.run_phase_root_blueprints_local(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_system_validation(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 6 for the supplied spell and conduit scope.
        """
        self._spell_compiler.run_phase_system_validation(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_system_validation_local(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 6 local-scope variant.
        """
        self._spell_compiler.run_phase_system_validation_local(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 7 for the supplied spell and conduit scope.
        """
        self._spell_compiler.run_phase_change_control(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control_local(
            self,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 7 local-scope variant.
        """
        self._spell_compiler.run_phase_change_control_local(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_occurrence_plan(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 8 for the supplied spell.
        """
        self._spell_compiler.run_phase_occurrence_plan(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            self._spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_injection_plan(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 9 for the supplied spell.
        """
        self._spell_compiler.run_phase_injection_plan(
            spell,
            spell._compiler_artifact,
            cancel_event=cancel_event,
        )

    def run_phase_patch_maps(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 10 for the supplied spell.
        """
        self._spell_compiler.run_phase_patch_maps(
            spell,
            spell._compiler_artifact,
            cancel_event=cancel_event,
        )

    def run_phase_execution_plan(
            self,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Execute compiler phase 11 for the supplied spell.
        """
        self._spell_compiler.run_phase_execution_plan(
            spell,
            spell._compiler_artifact,
            self._spellbook,
            cancel_event=cancel_event,
        )

    def compile_phase12_no_overrides_executor(
            self,
            spell: ISpell,
    ) -> None:
        """
        Execute compiler phase 12 no-overrides executor compilation.
        """
        self._spell_compiler.compile_phase12_no_overrides_executor(
            spell,
            spell._compiler_artifact,
        )

    def compile_phase12_no_overrides_executor_from_plan(
            self,
            spell: ISpell,
            execution_plan: ExecutionPlan,
    ) -> None:
        """
        Execute compiler phase 12 no-overrides compile-from-plan path.
        """
        self._spell_compiler.compile_phase12_no_overrides_executor_from_plan(
            spell,
            spell._compiler_artifact,
            execution_plan,
        )

    def compile_phase12_no_overrides_executor_from_payload(
            self,
            spell: ISpell,
            no_overrides_payload: Dict[str, Any],
    ) -> None:
        """
        Execute compiler phase 12 no-overrides compile-from-payload path.
        """
        self._spell_compiler.compile_phase12_no_overrides_executor_from_payload(
            spell,
            spell._compiler_artifact,
            no_overrides_payload,
        )
