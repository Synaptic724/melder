from typing import Any, Dict, Optional

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler import (
    SpellCompiler,
)
from melder.aether.spellbook.spell_crafter.spell_crafter import SpellCrafter
from melder.aether.spellbook.spell_crafter.validation.validation_system import (
    SpellValidationSystem,
)
from melder.aether.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
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
        - Delegates through the compiled `SpellCompiler` surface for phases
          1-12.
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
        Run compiler phase 1 (requirements) for a spell.

        Purpose:
            Delegate to the shared compiler to produce and cache phase-1
            requirements data on the spell's compiler artifact.

        Contract:
            - Does not require conduit-scoped state.
            - Uses the owning spell's `_compiler_artifact` as mutable target.
            - Honors cooperative cancellation while collecting requirements.
        Args:
            spell:
                Spell for which phase 1 artifacts are built.
            cancel_event:
                Optional cancellation signal for phase-1 processing.
        Returns:
            None.
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
        Run compiler phase 2 (symbolic graph) for a spell.

        Purpose:
            Delegate to the shared compiler to construct symbolic graph state from
            phase-1 requirements and store it on the spell artifact.

        Contract:
            - Requires the target spell to have an active compiler artifact.
            - Uses the per-spell artifact as cache/transfer surface.
            - Supports cancellation.
        Args:
            spell:
                Spell whose symbolic graph is being built.
            cancel_event:
                Optional cancellation signal for phase-2 processing.
        Returns:
            None.
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
        Run compiler phase 3 (local frame / DAG) for a spell.

        Purpose:
            Build local frame artifacts from symbolic graph and spell-system state,
            storing phase-3 outputs in the spell's compiler artifact.

        Contract:
            - Uses system-state from the owning spellbook for local visibility.
            - Delegates to phase-3 implementation in `SpellCompiler`.
            - Honors cancellation.
        Args:
            spell:
                Spell under local-frame compilation.
            cancel_event:
                Optional cancellation signal for phase-3 processing.
        Returns:
            None.
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
        Run compiler phase 4 (validation) for a spell.

        Purpose:
            Validate spell-level structural output from local frame execution and
            persist validation artifacts on the spell artifact.

        Contract:
            - Uses the system validator owned by this compiler system.
            - Uses the spellbook's spell-system state view when available.
            - Supports cancellation.
        Args:
            spell:
                Spell to validate.
            cancel_event:
                Optional cancellation signal for phase-4 processing.
        Returns:
            None.
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
        Run compiler phase 5 (root blueprints) for a spell.

        Purpose:
            Build root blueprints under the provided conduit and cache them on the
            spell's compiler artifact.

        Contract:
            - Requires phase 3/4 artifacts for the same spell.
            - Uses owning spellbook and spell-system-state for scope resolution.
            - Propagates cancellation to phase-5 internals.
        Args:
            spell:
                Spell that owns conduit-scoped blueprints.
            conduit_id:
                Conduit identifier for scope.
            cancel_event:
                Optional cancellation signal for phase-5 processing.
        Returns:
            None.
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
        Run local phase 5 (root blueprints) for a spell.

        Purpose:
            Compile local-only blueprints with the same storage and cancellation
            behavior as phase 5.

        Contract:
            - Restricts compilation to the local spellbook scope.
            - Updates the spell's local blueprint artifacts only.
            - Preserves conduit scope via `conduit_id`.
        Args:
            spell:
                Spell being locally resolved.
            conduit_id:
                Conduit identifier for scope.
            cancel_event:
                Optional cancellation signal for local phase-5 processing.
        Returns:
            None.
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
        Run compiler phase 6 (system validation) for a spell.

        Purpose:
            Validate system invariants for conduit-specific blueprints and store
            phase-6 validation outputs on the spell artifact.

        Contract:
            - Uses spellbook and spell-system-state context.
            - Requires phase-5 artifacts to be present.
            - Supports cancellation.
        Args:
            spell:
                Spell to run system validation for.
            conduit_id:
                Conduit identifier for validation scope.
            cancel_event:
                Optional cancellation signal for phase-6 processing.
        Returns:
            None.
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
        Run local phase 6 (system validation) for a spell.

        Purpose:
            Validate system state for locally-scoped roots and cache results in the
            spell artifact.

        Contract:
            - Uses local phase-5 artifacts produced on this spell.
            - Returns validation artifacts in the same artifact format.
            - Uses provided cancellation signal.
        Args:
            spell:
                Spell owning local validation scope.
            conduit_id:
                Conduit identifier for local system validation.
            cancel_event:
                Optional cancellation signal for local phase-6 processing.
        Returns:
            None.
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
        Run compiler phase 7 (change-control wiring) for a spell.

        Purpose:
            Register component-of and revalidation wiring for spell roots under the
            provided conduit scope.

        Contract:
            - Depends on completed phase-5 artifacts.
            - Operates through spellbook-level change-control infrastructure.
            - Honors optional cancellation signal.
        Args:
            spell:
                Spell being integrated into change-control.
            conduit_id:
                Conduit identifier for change-control scope.
            cancel_event:
                Optional cancellation signal for phase-7 processing.
        Returns:
            None.
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
        Run local phase 7 change-control wiring for a spell.

        Purpose:
            Register local-only component-of mappings and revalidators for local
            roots.

        Contract:
            - Mirrors phase-7 behavior over the local scope.
            - Reuses the same spell artifact storage and cancellation path.
        Args:
            spell:
                Spell with local roots to integrate.
            conduit_id:
                Conduit identifier for local change-control scope.
            cancel_event:
                Optional cancellation signal for local phase-7 processing.
        Returns:
            None.
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
        Run compiler phase 8 (occurrence plan) for a spell.

        Purpose:
            Build occurrence plan artifacts from validated root/system artifacts and
            persist them on the spell artifact.

        Contract:
            - Uses spellbook and spell-system state for dynamic planning context.
            - Requires upstream phase artifacts in the spell artifact.
            - Supports cancellation.
        Args:
            spell:
                Spell being planned.
            cancel_event:
                Optional cancellation signal for phase-8 processing.
        Returns:
            None.
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
        Run compiler phase 9 (injection plan) for a spell.

        Purpose:
            Transform occurrence artifacts into injector plan state on the spell
            compiler artifact.

        Contract:
            - Requires phase-8 outputs where applicable.
            - Delegates plan synthesis to the shared compiler.
            - Supports cancellation.
        Args:
            spell:
                Spell for which injection plans are built.
            cancel_event:
                Optional cancellation signal for phase-9 processing.
        Returns:
            None.
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
        Run compiler phase 10 (patch maps) for a spell.

        Purpose:
            Produce override/mutation patch maps from injection plans for later
            execution-plan synthesis.

        Contract:
            - Uses phase-9 injection output.
            - Stores patch maps on the per-spell artifact.
            - Supports cancellation.
        Args:
            spell:
                Spell for which patch maps are built.
            cancel_event:
                Optional cancellation signal for phase-10 processing.
        Returns:
            None.
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
        Run compiler phase 11 (execution plan) for a spell.

        Purpose:
            Compile and cache final execution plans for spell invocation on the
            spell artifact.

        Contract:
            - Requires complete phase-8/9/10 artifact chain.
            - Uses spellbook context for root and override resolution.
            - Supports cancellation.
        Args:
            spell:
                Spell for which execution plans are generated.
            cancel_event:
                Optional cancellation signal for phase-11 processing.
        Returns:
            None.
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
        Compile the phase-12 no-overrides executor for a spell.

        Purpose:
            Delegate to the shared compiler to generate and cache a callable
            executor from artifact-derived execution-plan state.

        Contract:
            - Requires phase-11 execution-plan artifacts.
            - Writes compiled no-overrides executor to the spell artifact.
        Args:
            spell:
                Spell owning the compiled executor.
        Returns:
            None.
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
        Compile the phase-12 no-overrides executor from a provided plan.

        Purpose:
            Build and cache a no-overrides executor directly from an execution
            plan without recomputing the plan through standard phase-11 flow.

        Contract:
            - Uses the supplied `execution_plan` object.
            - Refreshes executor cache metadata in the spell artifact.
        Args:
            spell:
                Spell owning the execution strategy.
            execution_plan:
                Concrete execution plan used for executor compilation.
        Returns:
            None.
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
        Compile the phase-12 no-overrides executor from payload data.

        Purpose:
            Compile executor output from serialized phase-11 payload when an
            execution plan object is unavailable.

        Contract:
            - Uses payload fields expected by phase-12 compilation helpers.
            - Updates executor caching metadata on the spell artifact.
        Args:
            spell:
                Spell owning the compiled executor.
            no_overrides_payload:
                Serialized execution-plan payload.
        Returns:
            None.
        """
        self._spell_compiler.compile_phase12_no_overrides_executor_from_payload(
            spell,
            spell._compiler_artifact,
            no_overrides_payload,
        )
