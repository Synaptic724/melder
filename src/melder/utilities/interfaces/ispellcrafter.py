from typing import Any, Callable, Dict, Optional, Protocol, Set, Tuple, runtime_checkable

from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import (
    SpellValidationResult,
)
from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import ExecutionPlan
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.utilities.interfaces.icleanable import ICleanable
from melder.utilities.interfaces.iinjectionplan import IInjectionPlan
from melder.utilities.interfaces.ioccurrenceplan import IOccurrencePlan
from melder.utilities.interfaces.imutationpatchmap import IMutationPatchMap
from melder.utilities.interfaces.ioverridepatchmap import IOverridePatchMap
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispellrequirements import ISpellRequirements
from melder.utilities.interfaces.ispell import ISpell
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent


@runtime_checkable
class ISpellCrafter(ICleanable, Protocol):
    """
    Per-spell orchestration surface for the SpellCrafter pipeline.

    This protocol mirrors the public API of: class:`SpellCrafter` for all
    spell-local resolution, validation, and plan-compilation artifacts.
    """

    @property
    def spell(self) -> ISpell:
        """
        The owning: class: 'Spell` for this crafter.

        Returns:
            ISpell: The live spell instance supplied at construction time.

        Raises:
            RuntimeError:
                If this crafter has been cleaned and no longer owns a spell
                reference.
        """
        ...

    @property
    def requirements(self) -> Optional[ISpellRequirements]:
        """
        Phase 1 artifact for this spell, if it has been computed.

        This is the same object returned by: meth:`run_phase_requirements`.
        When the crafter was initialized from a prebuilt resolution profile,
        this property may be populated before Phase 1 is run locally.
        """
        ...

    @property
    def symbolic_graph(self) -> Optional[SpellSymbolicGraph]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.
        """
        ...

    @property
    def resolution_frame(self) -> Optional[SpellResolutionFrame]:
        """
        Phase 3 artifact for this spell, if it has been computed.

        The resolution frame is a **summary view** over the concrete
        dependency DAG that is pushed into the owning: class: 'Spell` via: meth:`Spell._add_build_details`. It records the spell id and the
        topological order of all nodes participating in that DAG.
        """
        ...

    @property
    def validation_result_phase4(self) -> Optional[SpellValidationResult]:
        """
        Phase 4 validation result artifact, if any.

        Return the concrete `SpellValidationResult` from Phase 4 when present.
        to avoid constraining callers.
        """
        ...

    @property
    def root_blueprint_phase5(self) -> Optional[IRootResolutionBlueprint]:
        """
        Phase 5 root blueprint for this spell, if one has been attached.

        The root blueprint is the bridge from spell-local structural work into
        the later system-validation and change-control layers. It describes the
        owned root DAG that downstream phases use for system diagnostics,
        component-of indexing, and later plan compilation.
        """
        ...

    @property
    def occurrence_plan_phase8(self) -> Optional[IOccurrencePlan]:
        """
        Phase 8 occurrence plan artifact, if compiled for this spell.

        Returns:
            Optional[IOccurrencePlan]:
                The compiled OccurrencePlan for this spell, or None if Phase 8
                has not run yet, foundational resolution blocked later phases,
                or the spell bypasses this plan family.
        """
        ...

    @property
    def injection_plan_phase9(self) -> Optional[IInjectionPlan]:
        """
        Phase 9 injection plan artifact, if compiled for this spell.

        Returns:
            Optional[IInjectionPlan]:
                The compiled InjectionPlan for this spell, or None if Phase 9
                has not run yet, foundational resolution blocked later phases,
                or the spell bypasses this plan family.
        """
        ...

    @property
    def override_patch_map_phase10(self) -> Optional[IOverridePatchMap]:
        """
        Phase 10 override patch map artifact, if compiled for this spell.

        This artifact describes how caller-supplied override payloads should be
        projected onto the spell's rooted blueprint without rebuilding the
        earlier structural phases.
        """
        ...

    @property
    def mutation_patch_map_phase10(self) -> Optional[IMutationPatchMap]:
        """
        Phase 10 mutation patch map artifact, if compiled for this spell.

        This artifact carries the mutation-overlay mapping needed when the
        runtime applies spell-level mutation overrides to the rooted blueprint.
        It remains absent when Phase 10 has not run or when the spell does not
        participate in that mutation-capable path.
        """
        ...

    @property
    def execution_plan_phase11(self) -> Optional[ExecutionPlan]:
        """
        Canonical Phase 11 execution plan artifact for this spell.

        This is the broad execution-plan view produced after occurrence,
        injection, and patch-map compilation. More specialized plan variants
        may also be cached for fast override-free or override-only dispatch.
        """
        ...

    @property
    def execution_plan_phase11_no_overrides(self) -> Optional[ExecutionPlan]:
        """
        Cached Phase 11 execution plan variant for override-free fast paths.

        This plan exists so the runtime can dispatch the common no-overrides
        lane without re-specializing the broader Phase 11 artifact at call
        time.
        """
        ...

    @property
    def execution_plan_phase11_overrides(self) -> Optional[ExecutionPlan]:
        """
        Cached Phase 11 execution plan variant for override payloads without
        mutation overlays.
        """
        ...

    @property
    def execution_plan_phase11_overrides_with_mutations(self) -> Optional[ExecutionPlan]:
        """
        Phase 11 execution plan variant that still carries mutation-aware
        override semantics.

        The current implementation exposes the broad `_execution_plan_phase11`
        cache for this lane rather than storing a second dedicated mutation
        variant field.
        """
        ...

    @property
    def phase12_no_overrides_executor(self) -> Optional[Callable[..., Any]]:
        """
        Phase 12 compiled no-overrides executor for this spell.

        Purpose:
            Expose the spell-scoped compiled executor built from Phase 11
            semantics so CreationContext execution can dispatch directly
            without rebuilding transient codegen structures.
        Contract:
            - Returns None when the spell has no transient-only fast path.
            - Callable returns the constructed root instance for this spell.
        Returns:
            Optional[Callable[..., Any]]:
                Compiled no-overrides executor that accepts direct creations
                inputs, or None when unavailable.
        """
        ...

    @property
    def codegen_ir(self) -> Optional[Dict[str, Any]]:
        """
        Spell-scoped Codegen IR harvested from phases 2-11.

        Purpose:
            Provide a single spell-local payload that Phase 12 compilation can
            consume without re-deriving phase semantics at runtime.
        Contract:
            - Returns None until at least one phase export has populated IR.
            - Flushes pending phase8-11 export when that payload is marked dirty.
            - Returned mapping is owned by this crafter and treated as read-only.
        Returns:
            Optional[Dict[str, Any]]:
                Current IR payload for this spell, or None.
        """
        ...

    @property
    def spell_system_index_phase5(self) -> Optional[SpellSystemIndex]:
        """
        Phase 5 spell-system index attached to this spell, if available.

        This index is the spell-local handle to the wider Phase 5 system view
        used by later validation and planning work.
        """
        ...

    def get_phase5_spell_ids(self) -> Set[str]:
        """
        Return the spell ids currently covered by the local Phase 5 system-index state.

        Returns:
            Set[str]: Spell ids visible through the local Phase 5 index.
        """
        ...

    def get_phase5_root_ids(self) -> Tuple[str, ...]:
        """
        Return the root ids currently covered by local Phase 5 rooted blueprints.

        Returns:
            Tuple[str, ...]: Root ids visible through local Phase 5 blueprints.
        """
        ...

    @property
    def validation_result_phase6(self) -> Optional[SpellSystemValidationState]:
        """
        Phase 6 validation result artifact, if any.

        Return the concrete `SpellSystemValidationState` from Phase 6 when present.
        to avoid constraining callers.
        """
        ...

    @property
    def validated(self) -> bool:
        """
        True if the validation phases classified this spell as valid.
        This requires both Phase 4 and Phase 6 to have passed, and the spell
        not to be marked as broken.
        """
        ...

    @property
    def is_broken(self) -> bool:
        """
        True if the validation phase classified this spell as broken / unsafe.
        """
        ...

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
        """
        ...

    def reset_phase_artifacts(self) -> None:
        """
        Release transient validation/build artifacts without disposing of the
        crafter.

        Contract:
            - Clears the reusable artifacts owned by Phases 1-4 and Phase 6.
            - Preserves later rooted/planning artifacts so a spell that already
              advanced into runtime planning does not lose those caches.
            - Keeps the crafter alive for future phase runs.
        """
        ...

    def cleanup_phase_artifacts(self) -> None:
        """
        Backward-compatible alias for reset_phase_artifacts.

        This keeps the SpellCrafter reusable for future phase runs while
        releasing the transient structural-validation artifact set.
        """
        ...

    def set_root_blueprint_phase5(self, blueprint: IRootResolutionBlueprint) -> None:
        """
        Attach the Phase 5 root blueprint for this spell.

        Contract:
            - Stores the owned-root blueprint that later validation and plan
              phases consume.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because they depend on the
              rooted blueprint shape.
        """
        ...

    def set_spell_system_index_phase5(self, index: SpellSystemIndex) -> None:
        """
        Attach the Phase 5 spell-system index for this spell.

        Contract:
            - Stores the spell-local handle to the wider system index.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because downstream
              planning may depend on index content.
        """
        ...

    def clear_phase5_artifacts(self) -> None:
        """
        Deterministically clear Phase 5 state and all dependent later-phase
        artifacts.
        """
        ...

    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 - Analyze the Spell constructor and capture DI requirements.

        Responsibilities:
            * Inspect the bound Spell's constructor and classify every parameter
              into a: class:`ParameterDIShape` (normal DI, SpellMap, contracts, etc.).
            * Build a: class:`SpellRequirements` object that records per-parameter
              metadata (name, position, shape, optionality, annotations).
            * Store the requirements on this SpellCrafter (``_requirements``) for
              later phases to consume.

        Contracts:
            * Must only be called for a Spell that is fully constructed and
              attached to a Spellbook.
            * Does **not** call any other phases. The caller is responsible for
              running phases in order.
            * Does **not** mutate the Spell, SpellSystemStates, or any DAG
              structures. It only updates this SpellCrafter's internal state.
            * Does not return a value; consumers read "self._requirements".
        """
        ...

    def run_phase_symbolic_graph(
            self,
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
        ...

    def run_phase_local_frame(
            self,
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
        ...

    def run_phase_validation(
            self,
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
              via: attr:`validation_result`, :attr:`validated`, and: attr:`is_broken`.
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
        ...

    def run_phase_root_blueprints(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 entrypoint.

        Builds deep DAG blueprints (RootResolutionBlueprints) and a frame-level: class:`SpellSystemIndex`. This step uses only *existing* Phase 1-4 artifacts;
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
        ...

    def run_phase_root_blueprints_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 local entrypoint.

        Purpose:
            Build Phase 5 artifacts for only the target spell and its
            transitive dependency closure, so meld-triggered revalidation
            does not recompile unrelated spells.
        """
        ...

    def run_phase_occurrence_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 8 - Occurrence plan compilation.

        Compiles an OccurrencePlan for spells with attached Phase-5 blueprints.
        Existing-creation spells are treated as a no-op.

        Contract:
            - Requires Phase 5 artifacts to be available.
            - Builds plan only when a blueprint is attached for this spell.
            - Replaces any existing OccurrencePlan for this spell.
            - Uses the Spellbook-managed spell_id_pool (spell_id -> ISpell) as the
              spell lookup map without rebuilding it per phase.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.
        """
        ...

    def run_phase_injection_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            ValueError:
                If conduit_id is empty.
            RuntimeError:
                If Phase 8 artifacts are missing for this spell, or if the
                root blueprint is missing for this spell.
            OperationCancelledError:
                If cancel_event signals cancellation.

        Threading:
            - Not thread-safe; expected to run under spellbook phase scheduling.

        Lifecycle:
            - Replaces any prior InjectionPlan reference for this spell.
            - Prior plan objects are cleaned during SpellCrafter teardown.
        """
        ...

    def run_phase_patch_maps(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None.

        Raises:
            ValueError:
                If conduit_id is empty.
            RuntimeError:
                If Phase 5 artifacts are missing or the root blueprint is missing
                for this spell.
            OperationCancelledError:
                If cancel_event signals cancellation.

        Threading:
            - Not thread-safe; expected to run under spellbook phase scheduling.

        Lifecycle:
            - Replaces any prior patch map references for this spell.
            - Prior map objects are cleaned during SpellCrafter teardown.
        """
        ...

    def run_phase_execution_plan(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
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
        ...

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation.

        Runs system-level validation strategies over Phase-5 artifacts and
        Phase-4 outcomes. Records per-conduit resolution validity via
        "SpellSystemStates" and caches the frame-level validation state on
        every SpellCrafter in the Spellbook.

        Note:
            When Phase-4 results have been cleaned but Phase 4 previously
            completed successfully, we still include a placeholder entry
            in the phase4_results map so MissingPhase4Strategy can treat
            the spell as validated.
        """
        ...

    def run_phase_system_validation_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 local entrypoint.

        Purpose:
            Validate only the locally scoped Phase 5 graph produced by
            "run_phase_root_blueprints_local".
        Contract:
            - Uses the same strategy set as frame-wide Phase 6.
            - Records per-conduit validity only for scoped spell/root ids.
            - Publishes Phase 6 validation state to scoped spell crafters only.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.
        Returns:
            None.
        """
        ...

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring.

        Behaviour (conduit-scoped, idempotent):
        - Ensure the ChangeControlManager is present for the frame.
        - Ensure the component-of index is (re)built from the Phase-5 root blueprints.
        - Ensure the revalidator hook is registered.
        """
        ...

    def run_phase_change_control_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 local entrypoint.

        Purpose:
            Refresh change-control wiring only for locally revalidated roots.
        Contract:
            - Upserts component-of mappings for local root blueprints.
            - Preserves mappings for unrelated roots on the conduit.
            - Registers a revalidator when missing.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal (unused).
        Returns:
            None.
        """
        ...

    def run_structural_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **structural phases only** (1-4) in a sequence.

        This is typically invoked via: meth:`Spell.run_structural_phases` and
        is used for global, conduit-agnostic structural validation.

        Execution order:
            1. Requirements (Phase 1)
            2. Symbolic graph (Phase 2)
            3. Local frame / DAG (Phase 3)
            4. Validation (Phase 4)

        Returns:
            None. The crafter retains all intermediate artifacts until: meth: 'cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        Notes:
            Phase artifacts are cleaned after Phase 7; structural data remains in
            SpellSystemStates and on the Spell itself.
        """
        ...

    def run_all_phases(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run all phases in sequence for this spell.

        This is typically invoked via: meth:`Spell.run_all_phases` (a facade)
        and is intended for batch compilation / `meld()` cycles.

        Execution order:
            - Phase 1: Requirements
            - Phase 2: Symbolic graph
            - Phase 3: Local frame / DAG
            - Phase 4: Validation
            - Phase 5: Root blueprints
            - Phase 6: System validation
            - Phase 7: Change control
            - Phase 8: Occurrence plan
            - Phase 9: Injection plan
            - Phase 10: Patch maps
            - Phase 11: Execution plan

        Plan-phase gate:
            - If conduit resolution state reports foundational errors after
              phases 5/6/7, phases 8/9/10/11 are skipped for this run.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation signal shared across the scheduler.

        Returns:
            None. The crafter retains all intermediate artifacts until: meth: 'cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        """
        ...

