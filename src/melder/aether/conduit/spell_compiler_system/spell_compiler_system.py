from typing import Optional, Set, Tuple

from mypy_extensions import mypyc_attr

from melder.aether.conduit.spell_compiler_system.spell_compiler import (
    SpellCompiler,
)
from melder.aether.spellbook.spell_crafter.validation.validation_system import (
    SpellValidationSystem,
)
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.interfaces.ispellbook import ISpellbook
from melder.utilities.general_base.cleanable import Cleanable
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
        - Owns one instantiated `SpellCompiler`.
        - Owns one instantiated `SpellValidationSystem`.
        - Does not own per-spell compiler artifact state; that remains on the
          spell.
        - Does not own a Spellbook; callers provide `spellbook` explicitly at
          call time.
        - Delegates through the compiled `SpellCompiler` surface for phases
          1-12.
    """

    __slots__ = Cleanable.__slots__ + [
        "_spell_compiler",
        "_spell_validator",
    ]

    def __init__(self) -> None:
        """
        Initialize one compiler-system foundation object.

        Contract:
            - Creates one reusable SpellCompiler instance.
            - Creates one reusable SpellValidationSystem instance.
            - Does not capture Spellbook state; spellbook is a call-time input
              for front-facing phase entrypoints.
        """
        super().__init__()
        self._spell_compiler: SpellCompiler = SpellCompiler()
        self._spell_validator: SpellValidationSystem = SpellValidationSystem()

    def cleanup(self) -> None:
        """
        Release owned compiler collaborators.

        Contract:
            - Idempotent cleanup.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spell_validator
        del self._spell_compiler

    def run_phase_requirements(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 - Requirements extraction (front-facing compiler-system facade).

        Delegates to the compiler system to analyze constructor requirements
        and capture dependency metadata for this spell.

        Contract:
            - Requires a live Spell (not cleaned).
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute any later phases.
            - Accepts `spellbook` explicitly even though Phase 1 does not
              currently need it, so the compiler-system facade keeps one
              consistent front-facing shape.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose Phase 1 artifacts should be produced.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Notes:
            Phase artifacts are cleaned after Phase 7; spell-level dependency
            data and system state remain available.
        """
        self._spell_compiler.run_phase_requirements(
            spell,
            spell._compiler_artifact,
            cancel_event=cancel_event,
        )

    def run_phase_symbolic_graph(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 - Symbolic graph construction (front-facing compiler-system facade).

        Delegates to the compiler system to build the symbolic dependency graph
        for this spell from Phase 1 requirements.

        Contract:
            - Requires Phase 1 to be completed successfully.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.
            - Accepts `spellbook` explicitly to keep the compiler-system entry
              contract uniform even though this phase does not currently need it.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose Phase 2 artifacts should be produced.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

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
            spellbook: ISpellbook,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 3 - Local resolution frame / DAG (front-facing compiler-system facade).

        Delegates to the compiler system to resolve dependencies against the
        Spellbook and build the local resolution frame.

        Contract:
            - Requires Phases 1 and 2 to be completed successfully.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook whose visible spell pool and system-state surface are
                used for local-frame resolution.
            spell:
                Spell whose Phase 3 artifacts should be produced.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_local_frame(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_validation(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 - Per-spell validation (front-facing compiler-system facade).

        Delegates to the compiler system to validate this spell's Phase 1-3
        artifacts and set validated/broken flags.

        Contract:
            - Requires Phases 1-3 to be completed successfully.
            - Does not return a value; results are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing frame-level spell-system state for
                structural validity updates.
            spell:
                Spell whose Phase 4 validation should run.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_validation(
            spellbook,
            spell,
            spell._compiler_artifact,
            self._spell_validator,
            spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 - Root blueprint construction (front-facing compiler-system facade).

        Delegates to the compiler system to build system-level DAG blueprints
        and a SpellSystemIndex for the current frame.

        Contract:
            - Requires Phase 4 to be completed successfully.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing visibility, ownership, and frame-level
                system-state context.
            spell:
                Spell whose Phase 5 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_root_blueprints(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_root_blueprints_local(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 local - target spell closure blueprint construction (front-facing compiler-system facade).

        Delegates to the compiler system to build local Phase 5 artifacts for
        the target spell and its dependency closure.

        Contract:
            - Requires Phase 4 to be completed successfully.
            - Scope is limited to this spell plus transitive dependencies.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing visibility, ownership, and frame-level
                system-state context.
            spell:
                Spell whose local Phase 5 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_root_blueprints_local(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_occurrence_plan(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation (front-facing compiler-system facade).

        Delegates to the compiler system to compile the occurrence plan for root
        spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing lookup and system-state context for
                occurrence-plan compilation.
            spell:
                Spell whose Phase 8 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_occurrence_plan(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            cancel_event=cancel_event,
        )

    def run_phase_injection_plan(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 9 - Injection plan compilation (front-facing compiler-system facade).

        Delegates to the compiler system to compile the injection plan for root
        spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 8 artifacts to be available.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose Phase 9 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

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
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 10 - Patch map compilation (front-facing compiler-system facade).

        Delegates to the compiler system to compile override and mutation patch
        maps for root spells. Non-root spells are treated as a no-op.

        Contract:
            - Requires Phase 9 artifacts to be available.
            - Does not return a value; artifacts are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose Phase 10 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

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
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 11 - Execution plan compilation (front-facing compiler-system facade).

        Delegates to the compiler system to compile the execution plan for root
        spells. Non-root spells are treated as a no-op.

        Contract:
            - Invalidates the spell-owned CreationContext after execution-plan
              changes so meld rebuilds a fresh spell-shaped runtime context.
            - Preserves the internal phase-11/12 split, but extends the front
              execution-plan path to compile the phase-12 no-overrides executor
              immediately after phase 11 completes.

        Args:
            spellbook:
                Spellbook providing spell lookup and runtime compiler context.
            spell:
                Spell whose Phase 11 artifacts should be produced.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_execution_plan(
            spell,
            spell._compiler_artifact,
            spellbook,
            cancel_event=cancel_event,
        )
        spell._cleanup_creation_context()

    def run_phase_system_validation(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation (front-facing compiler-system facade).

        Delegates to the compiler system to validate system-level DAG integrity
        and update per-conduit resolution validity.

        Contract:
            - Requires Phase 5 to be completed successfully.
            - Does not return a value; results are stored on the spell-owned
              compiler artifact.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing visibility and frame-level system-state
                context.
            spell:
                Spell whose Phase 6 validation should run.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_system_validation(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_system_validation_local(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 local - scoped system validation (front-facing compiler-system facade).

        Delegates to the compiler system to validate only the local Phase 5
        scope for this spell.

        Contract:
            - Requires local Phase 5 artifacts.
            - Updates per-conduit resolution validity for scoped ids only.
            - Does not execute later phases.

        Args:
            spellbook:
                Spellbook providing visibility and frame-level system-state
                context.
            spell:
                Spell whose local Phase 6 validation should run.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_system_validation_local(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring (front-facing compiler-system facade).

        Delegates to the compiler system to ensure change-control wiring and
        component-of indexing are prepared for this frame.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Does not return a value; wiring occurs inside the compiler-owned
              phase path.

        Args:
            spellbook:
                Spellbook providing the frame-level change-control surface.
            spell:
                Spell whose Phase 7 wiring should run.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_change_control(
            spell,
            spell._compiler_artifact,
            spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def run_phase_change_control_local(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 local - scoped change-control wiring (front-facing compiler-system facade).

        Delegates to the compiler system to refresh change-control mappings only
        for locally revalidated roots.

        Contract:
            - Requires local Phase 5 artifacts.
            - Preserves component-of mappings for unrelated roots.

        Args:
            spellbook:
                Spellbook providing the frame-level change-control surface.
            spell:
                Spell whose local Phase 7 wiring should run.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        self._spell_compiler.run_phase_change_control_local(
            spell,
            spell._compiler_artifact,
            spellbook,
            conduit_id,
            cancel_event=cancel_event,
        )

    def get_local_resolution_scoped_spell_ids(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
    ) -> Set[str]:
        """
        Return the spell ids currently covered by this spell's local Phase 5 scope.

        Contract:
            - Always includes this spell's current `spell_id`.
            - Adds any additional spell ids present in the local Phase 5 system
              index when that artifact exists.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose local Phase 5 scope is being inspected.

        Returns:
            Set[str]: Spell ids in the local target-resolution scope.
        """
        scoped_spell_ids: Set[str] = {spell.spell_id}
        system_index = spell._compiler_artifact._spell_system_index_phase5
        if system_index is not None:
            scoped_spell_ids.update(system_index.nodes.keys())
        return scoped_spell_ids

    def get_local_resolution_scoped_root_ids(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
    ) -> Tuple[str, ...]:
        """
        Return the root ids currently covered by this spell's local Phase 5 scope.

        Contract:
            - Falls back to `(spell.spell_id,)` when no local Phase 5 rooted
              blueprints are available yet.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose local Phase 5 root scope is being inspected.

        Returns:
            Tuple[str, ...]: Root ids in the local target-resolution scope.
        """
        root_blueprints = spell._compiler_artifact._entire_dag_blueprint_phase5
        if root_blueprints is None or len(root_blueprints) == 0:
            return (spell.spell_id,)
        return tuple(root_blueprints.keys())

    def run_structural_phases(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run structural phases only (1-4) for a spell.

        Phases executed via the compiler system:
            1. Requirements extraction.
            2. Symbolic graph construction.
            3. Local resolution frame / DAG construction.
            4. Validation.

        Each phase honors the optional `CancellationEvent`. If the event is
        set, the underlying phase methods raise through the shared cancellation
        path.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose structural phases should be run.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            Exception: Propagates exceptions raised by the underlying phases.
        """
        self.run_phase_requirements(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_symbolic_graph(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_local_frame(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_validation(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )

    def run_all_phases(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run all compiler / resolution phases for a spell, in order.

        Phases executed via the compiler system:
            - Phase 1: Requirements extraction.
            - Phase 2: Symbolic graph construction.
            - Phase 3: Local resolution frame / DAG construction.
            - Phase 4: Validation.
            - Phase 5: Root blueprint construction.
            - Phase 6: System validation.
            - Phase 7: Change-control wiring.
            - Phase 8: Occurrence plan compilation.
            - Phase 9: Injection plan compilation.
            - Phase 10: Patch map compilation.
            - Phase 11: Execution plan compilation.
            - Phase 12: No-overrides executor compilation.

        Each phase honors the optional `CancellationEvent`. If the event is
        set, the underlying phase methods raise through the shared cancellation
        path.

        Args:
            spellbook:
                Spellbook providing the runtime/compiler context for this
                request.
            spell:
                Spell whose full compiler / resolution phase set should run.
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            Exception: Propagates exceptions raised by the underlying phases.
        """
        self.run_phase_requirements(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_symbolic_graph(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_local_frame(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_validation(
            spellbook,
            spell,
            cancel_event=cancel_event,
        )
        self.run_phase_root_blueprints(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_system_validation(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_change_control(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_occurrence_plan(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_injection_plan(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_patch_maps(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        self.run_phase_execution_plan(
            spellbook,
            spell,
            conduit_id,
            cancel_event=cancel_event,
        )
        spell._compiler_artifact.cleanup_phase_artifacts()
