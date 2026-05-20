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
            Create a new SpellCrafter for one bound: class: 'Spell`.
            
            Args:
                spell:
                    The owning spell. The crafter treats it as read-only except
                    when later phases push finalized build details back into the
                    spell through internal spell-owned update hooks.
                resolution_profile:
                    Optional prebuilt resolution profile. When supplied, the crafter
                    seeds Phase 1 requirements from that profile instead of
                    rebuilding them immediately.
            
            Contract:
                - Captures shared spell-owned services needed by later phases, such
                  as the spell validator and spell-system-state view.
                - Starts with empty artifact caches for all later phases.
                - Allows callers that already built a resolution profile to avoid
                  duplicating the first requirements extraction step.
        """
        super().__init__()
        self._spell_compiler: SpellCompiler = SpellCompiler()
        self._spell_validator: SpellValidationSystem = SpellValidationSystem()

    def cleanup(self) -> None:
        """
            Deterministically release all crafter-owned phase artifacts.
            
            Behaviour:
                * Cleans and clears structural artifacts from Phases 1-4.
                * Cleans and clears later blueprint/plan/index artifacts from
                  Phases 5-11 when present.
                * Drops cached compiled executor/codegen state.
                * Resets validation and broken-state flags held by the crafter.
                * Releases references to the owning spell and shared helper
                  services without mutating or disposing those external owners.
            
            Contract:
                Cleanup is idempotent. After cleanup, the crafter is unusable and
                future accesses must fail through `check_cleaned()`.
        """
        if self._cleaned:
            return
        self._cleaned = True
        del self._spell_validator
        del self._spell_compiler

    def run_phase_requirements(
            self,
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

        Args:
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
            spell: ISpell,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
            Phase 2 - Build the symbolic dependency graph for this Spell.
            
            Responsibilities:
                * Consume Phase 1 requirements and construct a: class:`SpellSymbolicGraph` describing all constructor sockets.
                * Create one: class:`SpellSymbolicDependency` per constructor
                  parameter that should be represented as a socket, including:
                      - plain (caller-supplied) parameters,
                      - normal DI sockets (single, collection, SpellMap),
                      - SpellContract sockets,
                      - MutationContract sockets.
                * Store the symbolic graph on this SpellCrafter
                  (``_symbolic_graph``) for later phases.
            
            Contracts:
                * Phase 1 (requirements) must already have run successfully.
                  This method will raise if requirements are missing; it does
                  **not** auto-run Phase 1.
                * Does **not** build any concrete DAG or talk to SpellSystemStates.
                * Does **not** mutate the Spell. It only updates this
                  SpellCrafter's internal state.
                * Does not return a value; consumers read "self._symbolic_graph".
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
            Phase 3 - Build the local-frame DAG and constructor topology.
            
            Responsibilities:
                * Consume Phase 1 requirements and Phase 2 symbolic graph for the
                  bound Spell.
                * Resolve **normal** DI sockets (single, collection, SpellMap)
                  against the Spellbook and build a **local-frame DAG** where:
                      - the root node is this Spell's version id, and
                      - direct edges represent first-hop constructor dependencies.
                * Track, per constructor parameter, which dependency spell ids were
                  bound during resolution.
                * Build a: class:`SpellLocalTopology` snapshot that describes all
                  sockets (normal, SpellContract, MutationContract) and their
                  concrete targets where applicable.
                * Register both:
                      - direct dependency spell ids, and
                      - the local topology
                  into: class:`SpellSystemStates`.
            
            Socket semantics:
                * Normal DI shapes (single, collection, SpellMap) produce DAG nodes,
                  DAG edges, and concrete "target_spell_ids" entries in topology.
                * SpellContract and MutationContract sockets are **metadata-only** at
                  this phase:
                      - they appear in the symbolic graph and topology,
                      - they do **not** produce DAG edges or bound targets yet.
                * Plain parameters are **metadata-only** at this phase:
                      - they appear in the symbolic graph and topology,
                      - they do **not** produce DAG edges or bound targets.
            
            Contracts:
                * Phases 1 and 2 must already have completed successfully. If
                  requirements or symbolic graph are missing, this method raises
                  instead of auto-running earlier phases.
                * Assumes the bound Spell is attached to a Spellbook; direct
                  Spellbook map iteration is used for resolution.
                * Stores the local DAG and direct dependency list on the Spell via: meth:`Spell._add_build_details`, and keeps a: class:`SpellResolutionFrame` internally on this SpellCrafter.
                * Does not return a value; callers rely on:
                      - "self._resolution_frame" for ordering, and
                      - SpellSystemStates for dependencies and topology.
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
            Phase 4 - Per-spell validation using SpellValidationSystem.
            
            Responsibilities:
                * Assume Phases 1-3 have completed for this Spell.
                * Delegate to: class:`SpellValidationSystem` to validate this spell
                  using:
                      - Phase 1 requirements,
                      - Phase 2 symbolic graph,
                      - Phase 3 resolution frame.
                * Cache the resulting: class:`SpellValidationResult 'and expose it
                  via: attr:`validation_result`, :attr:`validated`,
                  and: attr:`is_broken`.
                * Update global structural validity (SpellSystemState) when available,
                  including gating spells with missing SpellContract providers.
            
            Contracts:
                * Does **not** call Phases 1-3. If any of the required artifacts
                  are missing, this method raises.
                * Does **not** mutate the Spell or build any DAGs. It only records
                  validation outcome and diagnostics on this SpellCrafter.
                * If the SpellSystemState is no longer valid (unknown/gated/invalid),
                  the validation is re-run even if this phase is previously completed.
                * Returns "None"; callers rely on the stored validation result and
                  flags instead of a direct return value.
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
            Phase 5 entrypoint.
            
            Builds deep DAG blueprints (RootResolutionBlueprints) and a frame-level
            SpellSystemIndex. This step uses only *existing* Phase 1-4 artifacts;
            no new discovery occurs. The resulting DAGs and index are scoped to
            spells visible to the current Spellbook (local + contracted).
            
            Phase 5 produces two related outputs:
                - A root-only blueprint map for system validation (Phase 6).
                - Per-spell blueprints attached to constructed spells so Phase 8-10
                  and Phase 11 compilation can proceed for any meldable spell.
                - The change-control component of the map is rebuilt from **owned** roots
                  only, so contracted roots are not revalidated by this conduit.
            
            Args:
                conduit_id:
                    Conduit identifier used to scope resolution artifacts.
                cancel_event:
                    Optional cancellation handle.
            
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

        Returns:
            None.
        """
        self._spell_compiler.run_phase_occurrence_plan(
            spell,
            spell._compiler_artifact,
            spellbook,
            spellbook._spell_system_states,
        )

    def run_phase_injection_plan(
            self,
            spell: ISpell,
    ) -> None:
        """
            Phase 9 - Injection plan compilation.
            
            Compiles an InjectionPlan for spells using Phase-8 occurrence plans.
            Existing-creation spells are treated as a no-op.
            
            Purpose:
                Precompute dependency-to-parameter wiring so meld can inject without
                recomputing occurrence-driven dependency paths at runtime.
            
            Contract:
                - Requires Phase 8 artifacts to be available.
                - Builds plan only when an occurrence plan is attached for this spell.
                - Replaces any existing InjectionPlan for this spell.
                - Does not mutate the occurrence plan.
            
            Args:
                spell:
                    Spell whose Phase 9 artifacts should be produced.
            
            Returns:
                None.
            
            Raises:
                RuntimeError:
                    If Phase 8 artifacts are missing for this spell, or if the
                    root blueprint is missing for this spell.
        """
        self._spell_compiler.run_phase_injection_plan(
            spell,
            spell._compiler_artifact,
        )

    def run_phase_patch_maps(
            self,
            spell: ISpell,
    ) -> None:
        """
            Phase 10 - Patch map compilation.
            
            Compiles override and mutation patch maps for spells using
            Phase-5 blueprints. Existing-creation spells are treated as a no-op.
            
            Purpose:
                Precompute override and mutation targeting so meld can apply
                TargetSpec overrides without scanning the blueprint every call.
            
            Contract:
                - Requires Phase 5 artifacts to be available.
                - Builds maps only when a blueprint is attached for this spell.
                - Replaces any existing patch maps for this spell.
                - Does not mutate the root blueprint.
            
            Args:
                spell:
                    Spell whose Phase 10 artifacts should be produced.
            
            Returns:
                None.
            
            Raises:
                RuntimeError:
                    If Phase 5 artifacts are missing or the root blueprint is missing
                    for this spell.
        """
        self._spell_compiler.run_phase_patch_maps(
            spell,
            spell._compiler_artifact,
        )

    def run_phase_execution_plan(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
    ) -> None:
        """
            Phase 11 - Execution plan compilation.
            
            Compiles a Phase 11 ExecutionPlan for spells using Phase 8-9
            artifacts. Existing-creation spells are treated as a no-op.
            Emits plan variants for override-free, override-aware, and
            override+mutation-aware execution plan.
            
            Contract:
                - Requires Phase 8 artifacts to be available.
                - Uses Phase 9 injection plan when available.
                - Replaces existing ExecutionPlan references for this spell.
                - Uses the Spellbook-managed spell_id_pool (spell_id -> ISpell) as the
                  spell lookup map without rebuilding it per phase.
                - Reuses cached no-overrides plan when the deterministic Phase11 no-overrides input signature is unchanged.
                - Reuses the full cached phase11 variant set when the signature is
                  unchanged and cached sibling variants are available.
                - Falls back to the legacy no-overrides rebuild path when signature
                  inputs are missing.
        """
        self._spell_compiler.run_phase_execution_plan(
            spell,
            spell._compiler_artifact,
            spellbook,
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
            spell._compiler_artifact,
            spellbook,
            conduit_id,
        )

    def run_phase_change_control_local(
            self,
            spellbook: ISpellbook,
            spell: ISpell,
            conduit_id: str,
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
            spell._compiler_artifact,
            spellbook,
            conduit_id,
        )

    def get_local_resolution_scoped_spell_ids(
            self,
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
            spell: ISpell,
    ) -> Tuple[str, ...]:
        """
        Return the root ids currently covered by this spell's local Phase 5 scope.

        Contract:
            - Falls back to `(spell.spell_id,)` when no local Phase 5 rooted
              blueprints are available yet.

        Args:
            spell:
                Spell whose local Phase 5 root scope is being inspected.

        Returns:
            Tuple[str, ...]: Root ids in the local target-resolution scope.
        """
        root_blueprints = spell._compiler_artifact._entire_dag_blueprint_phase5
        if root_blueprints is None or len(root_blueprints) == 0:
            return (spell.spell_id,)
        return tuple(root_blueprints.keys())

    def reset_phase_artifacts(
            self,
            spell: ISpell,
    ) -> None:
        """
        Release transient structural-validation artifacts for one spell.

        Purpose:
            Surface the old `SpellCrafter.reset_phase_artifacts(...)` lifecycle
            intent through the compiler-system front API so callers can reset a
            spell's reusable Phase 1-4 / Phase 6 state without disposing of the
            later planning/runtime caches.

        Contract:
            - Resets only the structural-validation artifact group owned by the
              spell's compiler artifact.
            - Preserves Phase 5 and later plan/codegen state.
            - Does not replace or dispose of the spell-owned compiler artifact
              itself.

        Args:
            spell:
                Spell whose compiler artifact should drop the transient
                structural-validation state.

        Returns:
            None.
        """
        spell._compiler_artifact.reset_phase_artifacts()

    def cleanup_phase_artifacts(
            self,
            spell: ISpell,
    ) -> None:
        """
        Backward-compatible alias for structural artifact reset.

        Purpose:
            Preserve the old `SpellCrafter.cleanup_phase_artifacts(...)`
            lifecycle surface while the runtime is still in an additive fork.

        Contract:
            - Behaves exactly like `reset_phase_artifacts(spell)`.
            - Keeps the spell-owned compiler artifact alive for future phase
              runs.

        Args:
            spell:
                Spell whose transient structural-validation artifacts should be
                released.

        Returns:
            None.
        """
        spell._compiler_artifact.cleanup_phase_artifacts()

    def clear_phase5_artifacts(
            self,
            spell: ISpell,
    ) -> None:
        """
        Clear Phase 5 and later compiler state for one spell.

        Purpose:
            Surface the old `SpellCrafter.clear_phase5_artifacts(...)`
            lifecycle operation through the compiler-system front API so callers
            can explicitly drop rooted-planning/runtime caches while preserving
            the spell's structural artifacts.

        Contract:
            - Clears Phase 5 rooted blueprints/index state.
            - Clears Phase 8-11 planning/codegen cache state.
            - Clears the cached Phase 12 no-overrides executor state.
            - Preserves the spell-owned compiler artifact object itself.

        Args:
            spell:
                Spell whose Phase 5 and later compiler state should be cleared.

        Returns:
            None.
        """
        spell._compiler_artifact.clear_phase5_artifacts()

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
        )
        self.run_phase_occurrence_plan(
            spellbook,
            spell,
        )
        self.run_phase_injection_plan(
            spell,
        )
        self.run_phase_patch_maps(
            spell,
        )
        self.run_phase_execution_plan(
            spellbook,
            spell,
        )
        spell._compiler_artifact.cleanup_phase_artifacts()
