import threading
import time
import hashlib
import inspect
import pickle
import typing
import types
from typing import Any, Callable, Optional, List, Dict, Tuple, Set, Union, Collection, get_args, get_origin
# Melder Imports
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import DirectedAcyclicWorkGraph
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_dependency import (
    SpellSymbolicDependency,
)
from melder.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.spellbook.spell_crafter.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.spellbook.spell_crafter.system.spell_system_adjacency_builder import SpellSystemAdjacencyBuilder
from melder.spellbook.spell_crafter.system.spell_system_adjacency_snapshot import SpellSystemAdjacencySnapshot
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.spell_system_root_blueprint_builder import SpellSystemRootBlueprintBuilder
from melder.spellbook.spell_types.spell_types import SpellType
from melder.spellbook.existence.existence import Existence
from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.helpers.general_helpers import SpellInputUtils
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements_finder import (
    SpellRequirementsFinder,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.spell_requirements import (
    SpellRequirements,
)
from melder.spellbook.spell_crafter.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from melder.aether.conduit.meld.contracts.spell_contract import SpellContract
from melder.aether.conduit.meld.contracts.mutation_contract import MutationContract
from melder.utilities.interfaces import ISpell, ISpellSystemStates, ISpellValidationSystem, ISpellbook
from melder.utilities.synchronization.cancellation_event_signal import CancellationEvent
from melder.aether.dev_ops.spell_system_states.spell_state import SpellState
from melder.aether.dev_ops.spell_system_states.spell_state_change_reason import SpellStateChangeReason
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.utilities.custom_exceptions.spellbook_validation_error import SpellbookValidationError
from melder.spellbook.spell_crafter.topology.spell_local_topology import (
    SpellLocalTopology,
    SpellSocketDescriptor,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.spellbook.spell_crafter.blueprints.patch_maps import (
    MutationPatchMap,
    OverridePatchMap,
    PatchMapBuilder,
)
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import RootResolutionBlueprint
from melder.spellbook.spell_crafter.blueprints.injection_plan import (
    InjectionPlan,
    InjectionPlanBuilder,
)
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import (
    OccurrencePlan,
    OccurrencePlanBuilder,
)
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
    ExecutionPlanBuilder,
    ExecutionPlanCallMode,
    ExecutionPlanVariant,
)
from melder.spellbook.spell_crafter.blueprints.phase12_no_overrides_executor import (
    compile_phase12_no_overrides_executor,
    compile_phase12_no_overrides_executor_from_plan,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnostic,
    SystemDiagnosticSeverity,
)
from melder.spellbook.spell_crafter.system.spell_system_validation_state import SpellSystemValidationState
from melder.spellbook.spell_crafter.system.spell_system_validation_system import SpellSystemValidationSystem
from melder.spellbook.spell_crafter.system.validation.cycle_detection_strategy import CycleDetectionStrategy
from melder.spellbook.spell_crafter.system.validation.broken_spell_in_dag_strategy import BrokenSpellInDagStrategy
from melder.spellbook.spell_crafter.system.validation.graph_consistency_strategy import GraphConsistencyStrategy
from melder.spellbook.spell_crafter.system.validation.dependency_type_sanity_strategy import (
    DependencyTypeSanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_coverage_strategy import (
    IndexCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.index_dependency_sanity_strategy import (
    IndexDependencySanityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_alignment_strategy import (
    LineageAlignmentStrategy,
)
from melder.spellbook.spell_crafter.system.validation.lineage_version_conflict_strategy import (
    LineageVersionConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.missing_phase4_strategy import MissingPhase4Strategy
from melder.spellbook.spell_crafter.system.validation.ownership_consistency_strategy import (
    OwnershipConsistencyStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_coverage_strategy import (
    RootCoverageStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_lineage_conflict_strategy import (
    RootLineageConflictStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_reachability_strategy import (
    RootReachabilityStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_scale_limit_strategy import (
    RootScaleLimitStrategy,
)
from melder.spellbook.spell_crafter.system.validation.visibility_gap_strategy import (
    VisibilityGapStrategy,
)
from melder.spellbook.spell_crafter.system.validation.topology_dependency_mismatch_strategy import (
    TopologyDependencyMismatchStrategy,
)
from melder.spellbook.spell_crafter.system.validation.identity_mixing_strategy import (
    IdentityMixingStrategy,
)
from melder.spellbook.spell_crafter.system.validation.contracted_version_drift_strategy import (
    ContractedVersionDriftStrategy,
)
from melder.spellbook.spell_crafter.system.validation.scope_ordering_strategy import (
    ScopeOrderingStrategy,
)
from melder.spellbook.spell_crafter.system.validation.contract_graph_cycle_strategy import (
    ContractGraphCycleStrategy,
)
from melder.spellbook.spell_crafter.system.validation.root_viability_strategy import RootViabilityStrategy
from melder.spellbook.spell_crafter.system.validation.socket_ref_sanity_strategy import SocketRefSanityStrategy
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg

class SpellCrafter(Cleanable):
    """
    Per-spell orchestration surface for the SpellCrafter pipeline.

    This class is the spell-local owner for the artifacts that turn one bound
    :class:`Spell` from "registered metadata" into "validated, plan-bearing
    runtime input." It starts with the structural phases that inspect the
    callable surface and build the local dependency picture, then retains the
    later conduit-scoped artifacts that resolution and meld-time gates depend
    on for that same spell.

    Conceptual ownership is split like this:

        * :class:`Spellbook` owns long-lived registries, frame integration, and
          the multi-spell phase orchestration.
        * :class:`Spell` owns durable identity and the final concrete build
          details pushed back into the spell.
        * :class:`SpellCrafter` owns the transient and semi-transient artifacts
          produced while compiling one spell through Phases 1-11.

    Phase coverage:

        1. Requirements (signature -> SpellRequirements)
        2. Symbolic graph (requirements -> symbolic constructor sockets)
        3. Local frame / DAG (symbolic graph + Spellbook -> executable frame)
        4. Structural validation (frame + policies -> validated / broken flags)
        5-11. Root blueprints, system validation, change-control wiring, and
              later plan/codegen artifacts when this spell participates in them

    Existing-creation spells can legitimately stop earlier in that later phase
    family because they already own a backing instance and therefore do not
    need the same execution-plan artifacts as constructed spells.

    Lifecycle:
        - One crafter instance is attached to one spell version at a time.
        - Artifacts are cached so later phases and meld-time revalidation can
          reuse them without rebuilding from scratch on every access.
        - :meth:`cleanup` releases crafter-owned artifacts only; it does not
          dispose the owning :class:`Spell`, its :class:`Spellbook`, or the
          frame-level control-plane services they reference.

    Identity:
        All phase artifacts produced by this crafter are keyed by the spell's
        versioned identity ``spell.spell_index.current``. That version id is
        written into artifacts such as:

        * :class:`SpellRequirements.spell_id`
        * :class:`SpellSymbolicGraph.spell_id`
        * :class:`SpellSymbolicDependency.spell_id`
    """
    __melder_internal__ = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "_spell",
        "_requirements",
        "_symbolic_graph",
        "_resolution_frame",
        "_validation_result_phase4",
        "_validated_phase4",
        "_validation_result_phase6",
        "_validated_phase6",
        "_validated",
        "_root_blueprint_phase5",
        "_phase8_occurrence_plan_input_signature",
        "_phase8_occurrence_plan_fast_key",
        "_occurrence_plan_phase8",
        "_phase9_injection_plan_input_signature",
        "_injection_plan_phase9",
        "_override_patch_map_phase10",
        "_mutation_patch_map_phase10",
        "_phase10_patch_maps_input_signature",
        "_execution_plan_phase11",
        "_execution_plan_phase11_no_overrides",
        "_execution_plan_phase11_overrides",
        "_phase12_no_overrides_executor",
        "_phase12_no_overrides_executor_signature",
        "_phase11_no_overrides_input_signature",
        "_phase11_no_overrides_fast_key",
        "_codegen_ir",
        "_phase8_11_codegen_ir_dirty",
        "_spell_system_index_phase5",
        "_is_broken",
        "_entire_dag_blueprint_phase5",
        "_spell_validator",
        "_spell_system_states",
    ]

    def __init__(
            self,
            spell: ISpell,
            *,
            resolution_profile: Optional[Any] = None,
    ) -> None:
        """
        Create a new SpellCrafter for one bound :class:`Spell`.

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
        Cleanable.__init__(self)

        if spell is None:
            raise ValueError("spell must not be None.")

        self._lock: threading.RLock = threading.RLock()
        self._spell: ISpell = spell
        self._spell_validator: ISpellValidationSystem = self._spell._spellbook._spell_validator
        self._spell_system_states: Optional[ISpellSystemStates] = self._spell._spell_system_states
        self._requirements: Optional[SpellRequirements] = None
        if resolution_profile is not None:
            self._requirements = resolution_profile.requirements
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        # Phase 3 artifact - currently a SpellResolutionFrame summarising the
        # concrete dependency DAG that is pushed into the owning Spell.
        self._resolution_frame: Optional[SpellResolutionFrame] = None
        self._validation_result_phase4: Any = None
        self._validated_phase4: bool = False
        self._validation_result_phase6: Any = None
        self._validated_phase6: bool = False
        self._root_blueprint_phase5: Optional[RootResolutionBlueprint] = None
        self._phase8_occurrence_plan_input_signature: Optional[str] = None
        self._phase8_occurrence_plan_fast_key: Optional[Tuple[Any, ...]] = None
        self._occurrence_plan_phase8: Optional[OccurrencePlan] = None
        self._phase9_injection_plan_input_signature: Optional[str] = None
        self._injection_plan_phase9: Optional[InjectionPlan] = None
        self._override_patch_map_phase10: Optional[OverridePatchMap] = None
        self._mutation_patch_map_phase10: Optional[MutationPatchMap] = None
        self._phase10_patch_maps_input_signature: Optional[Tuple[Any, ...]] = None
        self._execution_plan_phase11: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_no_overrides: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_overrides: Optional[ExecutionPlan] = None
        self._phase12_no_overrides_executor: Optional[Callable[..., Any]] = None
        self._phase12_no_overrides_executor_signature: Optional[str] = None
        self._phase11_no_overrides_input_signature: Optional[str] = None
        self._phase11_no_overrides_fast_key: Optional[Tuple[Any, ...]] = None
        self._codegen_ir: Optional[Dict[str, Any]] = None
        self._phase8_11_codegen_ir_dirty: bool = False
        self._spell_system_index_phase5: Optional[SpellSystemIndex] = None
        self._entire_dag_blueprint_phase5 : Optional[Dict[str, RootResolutionBlueprint]] = None
        self._is_broken: bool = False

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup(self) -> None:
        """
        Deterministically release all crafter-owned phase artifacts.

        Behavior:
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

        with self._lock:
            if self._cleaned:
                return

            self._cleanup_phase_artifacts_locked()
            if self._root_blueprint_phase5 is not None:
                try:
                    self._root_blueprint_phase5.cleanup()
                except Exception:
                    pass
            if self._occurrence_plan_phase8 is not None:
                try:
                    self._occurrence_plan_phase8.cleanup()
                except Exception:
                    pass
            if self._injection_plan_phase9 is not None:
                try:
                    self._injection_plan_phase9.cleanup()
                except Exception:
                    pass
            if self._override_patch_map_phase10 is not None:
                try:
                    self._override_patch_map_phase10.cleanup()
                except Exception:
                    pass
            if self._mutation_patch_map_phase10 is not None:
                try:
                    self._mutation_patch_map_phase10.cleanup()
                except Exception:
                    pass
            if self._execution_plan_phase11 is not None:
                try:
                    self._execution_plan_phase11.cleanup()
                except Exception:
                    pass
            if self._execution_plan_phase11_no_overrides is not None:
                try:
                    self._execution_plan_phase11_no_overrides.cleanup()
                except Exception:
                    pass
            if self._execution_plan_phase11_overrides is not None:
                try:
                    self._execution_plan_phase11_overrides.cleanup()
                except Exception:
                    pass
            if self._spell_system_index_phase5 is not None:
                try:
                    self._spell_system_index_phase5.cleanup()
                except Exception:
                    pass
            if self._entire_dag_blueprint_phase5 is not None:
                for blueprint in list(self._entire_dag_blueprint_phase5.values()):
                    if blueprint is None:
                        continue
                    try:
                        blueprint.cleanup()
                    except Exception:
                        pass
                try:
                    self._entire_dag_blueprint_phase5.clear()
                except Exception:
                    pass
            self._cleaned = True
            self._phase8_11_codegen_ir_dirty = False
            self._validated_phase4 = False
            self._validated_phase6 = False
            self._is_broken = False

            del self._root_blueprint_phase5
            del self._phase8_occurrence_plan_input_signature
            del self._phase8_occurrence_plan_fast_key
            del self._occurrence_plan_phase8
            del self._phase9_injection_plan_input_signature
            del self._injection_plan_phase9
            del self._override_patch_map_phase10
            del self._mutation_patch_map_phase10
            del self._phase10_patch_maps_input_signature
            del self._execution_plan_phase11
            del self._execution_plan_phase11_no_overrides
            del self._execution_plan_phase11_overrides
            del self._phase12_no_overrides_executor
            del self._phase12_no_overrides_executor_signature
            del self._phase11_no_overrides_input_signature
            del self._phase11_no_overrides_fast_key
            del self._codegen_ir
            del self._spell_system_index_phase5
            del self._entire_dag_blueprint_phase5
            del self._spell_system_states
            del self._spell
            del self._spell_validator

    # ------------------------------------------------------------------
    # Core properties
    # ------------------------------------------------------------------

    @property
    def spell(self) -> ISpell:
        """
        The owning :class:`Spell` for this crafter.

        Returns:
            ISpell: The live spell instance supplied at construction time.

        Raises:
            RuntimeError:
                If this crafter has been cleaned and no longer owns a spell
                reference.
        """
        self.check_cleaned()
        return self._spell

    @property
    def requirements(self) -> Optional[SpellRequirements]:
        """
        Phase 1 artifact for this spell, if it has been computed.

        This is the same object returned by :meth:`run_phase_requirements`.
        When the crafter was initialized from a prebuilt resolution profile,
        this property may be populated before Phase 1 is run locally.
        """
        self.check_cleaned()
        return self._requirements

    @property
    def symbolic_graph(self) -> Optional[SpellSymbolicGraph]:
        """
        Phase 2 symbolic graph for this spell, if it has been computed.
        """
        self.check_cleaned()
        return self._symbolic_graph

    @property
    def resolution_frame(self) -> Optional[SpellResolutionFrame]:
        """
        Phase 3 artifact for this spell, if it has been computed.

        The resolution frame is a **summary view** over the concrete
        dependency DAG that is pushed into the owning :class:`Spell` via
        :meth:`Spell._add_build_details`. It records the spell id and the
        topological order of all nodes participating in that DAG.
        """
        self.check_cleaned()
        return self._resolution_frame

    @property
    def validation_result_phase4(self) -> Any:
        """
        Phase 4 validation result artifact, if any.

        Once Phase 4 is wired, this will typically be a
        :class:`SpellValidationResult` produced by the
        :class:`SpellValidationSystem`. For now the type is kept as ``Any``
        to avoid constraining callers.
        """
        self.check_cleaned()
        return self._validation_result_phase4

    @property
    def root_blueprint_phase5(self) -> Optional[RootResolutionBlueprint]:
        """
        Phase 5 root blueprint for this spell, if one has been attached.

        The root blueprint is the bridge from spell-local structural work into
        the later system-validation and change-control layers. It describes the
        owned root DAG that downstream phases use for system diagnostics,
        component-of indexing, and later plan compilation.
        """
        self.check_cleaned()
        return self._root_blueprint_phase5

    @property
    def occurrence_plan_phase8(self) -> Optional[OccurrencePlan]:
        """
        Phase 8 occurrence plan artifact, if compiled for this spell.

        Returns:
            Optional[OccurrencePlan]:
                The compiled OccurrencePlan for this spell, or None if Phase 8
                has not run yet, foundational resolution blocked later phases,
                or the spell bypasses this plan family.
        """
        self.check_cleaned()
        return self._occurrence_plan_phase8

    @property
    def injection_plan_phase9(self) -> Optional[InjectionPlan]:
        """
        Phase 9 injection plan artifact, if compiled for this spell.

        Returns:
            Optional[InjectionPlan]:
                The compiled InjectionPlan for this spell, or None if Phase 9
                has not run yet, foundational resolution blocked later phases,
                or the spell bypasses this plan family.
        """
        self.check_cleaned()
        return self._injection_plan_phase9

    @property
    def override_patch_map_phase10(self) -> Optional[OverridePatchMap]:
        """
        Phase 10 override patch map artifact, if compiled for this spell.

        This artifact describes how caller-supplied override payloads should be
        projected onto the spell's rooted blueprint without rebuilding the
        earlier structural phases.
        """
        self.check_cleaned()
        return self._override_patch_map_phase10

    @property
    def mutation_patch_map_phase10(self) -> Optional[MutationPatchMap]:
        """
        Phase 10 mutation patch map artifact, if compiled for this spell.

        This artifact carries the mutation-overlay mapping needed when the
        runtime applies spell-level mutation overrides to the rooted blueprint.
        It remains absent when Phase 10 has not run or when the spell does not
        participate in that mutation-capable path.
        """
        self.check_cleaned()
        return self._mutation_patch_map_phase10

    @property
    def execution_plan_phase11(self) -> Optional[ExecutionPlan]:
        """
        Canonical Phase 11 execution plan artifact for this spell.

        This is the broad execution-plan view produced after occurrence,
        injection, and patch-map compilation. More specialized plan variants
        may also be cached for fast override-free or override-only dispatch.
        """
        self.check_cleaned()
        return self._execution_plan_phase11

    @property
    def execution_plan_phase11_no_overrides(self) -> Optional[ExecutionPlan]:
        """
        Cached Phase 11 execution plan variant for override-free fast paths.

        This plan exists so the runtime can dispatch the common no-overrides
        lane without re-specializing the broader Phase 11 artifact at call
        time.
        """
        self.check_cleaned()
        return self._execution_plan_phase11_no_overrides

    @property
    def execution_plan_phase11_overrides(self) -> Optional[ExecutionPlan]:
        """
        Cached Phase 11 execution plan variant for override payloads without
        mutation overlays.
        """
        self.check_cleaned()
        return self._execution_plan_phase11_overrides

    @property
    def execution_plan_phase11_overrides_with_mutations(
            self,
    ) -> Optional[ExecutionPlan]:
        """
        Phase 11 execution plan variant that still carries mutation-aware
        override semantics.

        The current implementation exposes the broad `_execution_plan_phase11`
        cache for this lane rather than storing a second dedicated mutation
        variant field.
        """
        self.check_cleaned()
        return self._execution_plan_phase11

    @property
    def phase12_no_overrides_executor(self) -> Optional[Callable[..., Any]]:
        """
        Phase 12 compiled no-overrides executor for this spell.

        Purpose:
            Expose the spell-scoped compiled executor built from Phase 11
            semantics so CreationContext execution can dispatch directly without rebuilding
            transient codegen structures.
        Contract:
            - Returns None when the spell has no transient-only fast path.
            - Callable returns the constructed root instance for this spell.
        Returns:
            Optional[Callable[..., Any]]:
                Compiled no-overrides executor that accepts direct creations
                inputs, or None when unavailable.
        """
        self.check_cleaned()
        return self._phase12_no_overrides_executor

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
        self.check_cleaned()
        self._capture_phase8_11_codegen_ir_if_dirty()
        return self._codegen_ir

    @property
    def spell_system_index_phase5(self) -> Optional[SpellSystemIndex]:
        """
        Phase 5 spell-system index attached to this spell, if available.

        This index is the spell-local handle to the wider Phase 5 system view
        used by later validation and planning work.
        """
        self.check_cleaned()
        return self._spell_system_index_phase5


    @property
    def validation_result_phase6(self) -> Any:
        """
        Phase 6 validation result artifact, if any.

        Once Phase 6 is wired, this will typically be a
        :class:`SpellValidationResult` produced by the
        :class:`SpellValidationSystem`. For now the type is kept as ``Any``
        to avoid constraining callers.
        """
        self.check_cleaned()
        return self._validation_result_phase6

    @property
    def validated(self) -> bool:
        """
        True if the validation phases classified this spell as valid.
        This requires both Phase 4 and Phase 6 to have passed, and the spell
        not to be marked as broken.
        """
        self.check_cleaned()
        return bool(self._validated_phase4 and self._validated_phase6 and not self._is_broken)

    @property
    def is_broken(self) -> bool:
        """
        True if the validation phase classified this spell as broken / unsafe.
        """
        self.check_cleaned()
        return self._is_broken

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def reset_phase_artifacts(self) -> None:
        """
        Release transient validation/build artifacts without disposing the
        crafter.

        Contract:
            - Clears the reusable artifacts owned by Phases 1-4 and Phase 6.
            - Preserves later rooted/planning artifacts so a spell that already
              advanced into runtime planning does not lose those caches.
            - Keeps the crafter alive for future phase runs.
        """
        self.check_cleaned()
        with self._lock:
            if self._cleaned:
                return
            self._cleanup_phase_artifacts_locked()

    def cleanup_phase_artifacts(self) -> None:
        """
        Backward-compatible alias for reset_phase_artifacts.

        This keeps the SpellCrafter reusable for future phase runs while
        releasing the transient structural-validation artifact set.
        """
        self.reset_phase_artifacts()

    def _cleanup_phase_artifacts_locked(self) -> None:
        """
        Internal helper that clears the reusable structural-validation artifact
        set under the crafter lock.

        Contract:
            - Best-effort cleans owned artifact objects before nulling them.
            - Leaves Phase 5 and later plan/codegen artifacts untouched.
            - Refreshes the phase2_5 codegen snapshot after the structural
              layers are cleared.
        """
        if self._requirements is not None:
            try:
                self._requirements.cleanup()
            except Exception:
                pass

        if self._symbolic_graph is not None:
            try:
                self._symbolic_graph.cleanup()
            except Exception:
                pass

        if self._resolution_frame is not None and isinstance(self._resolution_frame, Cleanable):
            try:
                self._resolution_frame.cleanup()
            except Exception:
                pass

        if self._validation_result_phase4 is not None and isinstance(self._validation_result_phase4, Cleanable):
            try:
                self._validation_result_phase4.cleanup()
            except Exception:
                pass

        if self._validation_result_phase6 is not None and isinstance(self._validation_result_phase6, Cleanable):
            try:
                self._validation_result_phase6.cleanup()
            except Exception:
                pass

        self._resolution_frame = None
        self._requirements = None
        self._symbolic_graph = None
        self._validation_result_phase4 = None
        self._validation_result_phase6 = None
        self._capture_phase2_5_codegen_ir()

    def set_root_blueprint_phase5(self, blueprint: RootResolutionBlueprint) -> None:
        """
        Attach the Phase 5 root blueprint for this spell.

        Contract:
            - Stores the owned-root blueprint that later validation and plan
              phases consume.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because they depend on the
              rooted blueprint shape.
        """
        self.check_cleaned()
        if blueprint is None:
            raise ValueError("blueprint must not be None.")
        self._root_blueprint_phase5 = blueprint
        self._capture_phase2_5_codegen_ir()
        self._reset_phase8_11_codegen_ir()

    def set_spell_system_index_phase5(self, index: SpellSystemIndex) -> None:
        """
        Attach the Phase 5 spell-system index for this spell.

        Contract:
            - Stores the spell-local handle to the wider system index.
            - Refreshes Phase 2-5 exported IR.
            - Invalidates later Phase 8-11 IR caches because downstream
              planning may depend on index content.
        """
        self.check_cleaned()
        if index is None:
            raise ValueError("index must not be None.")
        self._spell_system_index_phase5 = index
        self._capture_phase2_5_codegen_ir()
        self._reset_phase8_11_codegen_ir()

    def clear_phase5_artifacts(self) -> None:
        """
        Deterministically clear Phase 5 state and all dependent later-phase
        artifacts.

        Contract:
            - Drops the Phase 5 blueprint reference.
            - Cleans and nulls compiled occurrence, injection, patch-map, and
              execution-plan artifacts that depend on that Phase 5 state.
            - Clears the spell-system index and later-phase cache signatures.
            - Leaves Phase 1-4 artifacts intact.
        """
        self._root_blueprint_phase5 = None
        self._phase8_occurrence_plan_input_signature = None
        self._phase8_occurrence_plan_fast_key = None
        if self._occurrence_plan_phase8 is not None:
            try:
                self._occurrence_plan_phase8.cleanup()
            except Exception:
                pass
        self._occurrence_plan_phase8 = None
        self._phase9_injection_plan_input_signature = None
        if self._injection_plan_phase9 is not None:
            try:
                self._injection_plan_phase9.cleanup()
            except Exception:
                pass
        self._injection_plan_phase9 = None
        if self._override_patch_map_phase10 is not None:
            try:
                self._override_patch_map_phase10.cleanup()
            except Exception:
                pass
        self._override_patch_map_phase10 = None
        if self._mutation_patch_map_phase10 is not None:
            try:
                self._mutation_patch_map_phase10.cleanup()
            except Exception:
                pass
        self._mutation_patch_map_phase10 = None
        self._phase10_patch_maps_input_signature = None
        if self._execution_plan_phase11 is not None:
            try:
                self._execution_plan_phase11.cleanup()
            except Exception:
                pass
        self._execution_plan_phase11 = None
        if self._execution_plan_phase11_no_overrides is not None:
            try:
                self._execution_plan_phase11_no_overrides.cleanup()
            except Exception:
                pass
        self._execution_plan_phase11_no_overrides = None
        if self._execution_plan_phase11_overrides is not None:
            try:
                self._execution_plan_phase11_overrides.cleanup()
            except Exception:
                pass
        self._execution_plan_phase11_overrides = None
        self._spell_system_index_phase5 = None
        self._reset_phase8_11_codegen_ir()
        self._capture_phase2_5_codegen_ir()

    def _build_phase10_patch_maps_input_signature(
            self,
            root_blueprint: Optional[RootResolutionBlueprint],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build deterministic phase10 input signature for patch-map reuse.

        Purpose:
            Detect whether phase10 patch-map inputs changed so warm runs can
            safely skip redundant patch-map rebuilds.
        Contract:
            - Returns None when blueprint input is unavailable.
            - Includes only lightweight blueprint identity/shape fields.
        Args:
            root_blueprint:
                Phase5 root blueprint used as patch-map source.
        Returns:
            Optional[Tuple[Any, ...]]:
                Deterministic signature tuple or None when unavailable.
        """
        if root_blueprint is None:
            return None
        path_registry_identity = None
        socket_ref_count = 0
        ordered_node_count = 0
        try:
            path_registry_identity = id(root_blueprint.path_registry)
            socket_ref_count = len(root_blueprint.socket_refs or ())
            ordered_node_count = len(root_blueprint.ordered_node_ids or ())
        except Exception:
            return None
        return (
            root_blueprint.root_spell_id,
            path_registry_identity,
            socket_ref_count,
            ordered_node_count,
        )

    def _build_phase8_occurrence_plan_fast_key(
            self,
            *,
            root_blueprint: Optional[RootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, ISpell]],
    ) -> Optional[Tuple[Any, ...]]:
        """
        Build a lightweight deterministic key for phase8 signature reuse.

        Purpose:
            Avoid recomputing deep phase8 signature hashing when no-mutation
            inputs are unchanged between warm runs.
        Contract:
            - Returns None when required inputs are unavailable.
            - Returns None when any spell has a mutation override, forcing the
              deep signature path that includes mutation payload semantics.
            - Mirrors no-mutation phase8 signature surfaces used for plan reuse.
        Args:
            root_blueprint:
                Phase5 root blueprint for this spell.
            spell_lookup:
                Spell lookup map keyed by spell id.
        Returns:
            Optional[Tuple[Any, ...]]:
                Deterministic fast-key tuple or None when deep-signature
                fallback is required.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    tuple(sorted(socket_ref.target_spell_ids)),
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        try:
            spell_rows_list: List[Tuple[Any, ...]] = []
            for spell_id, spell in sorted(spell_lookup.items()):
                if spell.mutation_override:
                    return None
                spell_rows_list.append(
                    (
                        spell_id,
                        spell.spell_index.current,
                        spell.existence.name,
                        bool(spell.is_existing_creation),
                    )
                )
            spell_rows = tuple(spell_rows_list)
        except Exception:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if self._spell_system_states is not None:
            local_topologies = getattr(self._spell_system_states, "_local_topologies", None)
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            spellbook = self._spell._spellbook
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            system_state = spellbook._aetheric_frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return (
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

    def _build_phase8_occurrence_plan_input_signature(
            self,
            *,
            root_blueprint: Optional[RootResolutionBlueprint],
            spell_lookup: Optional[Dict[str, ISpell]],
    ) -> Optional[str]:
        """
        Build deterministic phase8 input signature for occurrence-plan reuse.

        Purpose:
            Detect semantic drift in phase8 inputs so warm runs can safely skip
            redundant occurrence-plan rebuilds when inputs are unchanged.
        Contract:
            - Returns None when required inputs are unavailable, forcing rebuild.
            - Includes blueprint shape, spell mutation/existence signals, local
              topology socket structure, and contracted-provider routing state.
        Args:
            root_blueprint:
                Phase5 root blueprint for this spell.
            spell_lookup:
                Spell lookup map keyed by spell id.
        Returns:
            Optional[str]:
                Deterministic signature string or None when rebuild must proceed.
        """
        if root_blueprint is None or spell_lookup is None:
            return None

        try:
            ordered_node_ids = tuple(root_blueprint.ordered_node_ids)
            path_registry_identity = id(root_blueprint.path_registry)
            blueprint_socket_rows = tuple(
                (
                    socket_ref.node_id,
                    socket_ref.param_name,
                    socket_ref.param_path_id,
                    tuple(sorted(socket_ref.target_spell_ids)),
                )
                for socket_ref in (root_blueprint.socket_refs or ())
            )
        except Exception:
            return None

        try:
            spell_rows = tuple(
                (
                    spell_id,
                    spell.spell_index.current,
                    spell.existence.name,
                    bool(spell.is_existing_creation),
                    self._freeze_phase11_schema_value(spell.mutation_override),
                )
                for spell_id, spell in sorted(spell_lookup.items())
            )
        except Exception:
            return None

        topology_rows: Tuple[Any, ...] = ()
        local_topologies = None
        if self._spell_system_states is not None:
            local_topologies = getattr(self._spell_system_states, "_local_topologies", None)
        if local_topologies is not None:
            try:
                topology_rows_list: List[Tuple[Any, ...]] = []
                for spell_id in sorted(local_topologies.keys()):
                    topology = local_topologies.get(spell_id)
                    if topology is None:
                        continue
                    socket_rows = tuple(
                        (
                            socket.param_name,
                            tuple(sorted(socket.target_spell_ids)),
                        )
                        for socket in topology.sockets
                    )
                    topology_rows_list.append((spell_id, socket_rows))
                topology_rows = tuple(topology_rows_list)
            except Exception:
                return None

        try:
            spellbook = self._spell._spellbook
            contracted_lookup = spellbook._lookup_contracted_spells
            contracted_maps = spellbook._contracted_spells
            system_state = spellbook._aetheric_frame_configuration.system_state
        except Exception:
            return None

        try:
            contracted_rows_list: List[Tuple[Any, ...]] = []
            for conduit_id in sorted(contracted_lookup.keys()):
                lookup_map = contracted_lookup.get(conduit_id)
                if lookup_map is None:
                    continue
                contracted_map = contracted_maps.get(conduit_id)
                for contract_key in sorted(lookup_map.keys()):
                    spell_index = lookup_map.get(contract_key)
                    if spell_index is None:
                        continue
                    provider_spell_id = None
                    if contracted_map is not None:
                        provider_spell = contracted_map.get(spell_index)
                        if provider_spell is not None:
                            provider_spell_id = provider_spell.spell_index.current
                    contracted_rows_list.append(
                        (
                            conduit_id,
                            contract_key[0],
                            contract_key[1],
                            provider_spell_id,
                        )
                    )
            contracted_rows = tuple(contracted_rows_list)
        except Exception:
            return None

        return self._hash_codegen_signature(
            root_blueprint.root_spell_id,
            ordered_node_ids,
            path_registry_identity,
            blueprint_socket_rows,
            spell_rows,
            topology_rows,
            system_state,
            contracted_rows,
        )

    def _build_phase9_injection_plan_input_signature(
            self,
            *,
            occurrence_plan: Optional[OccurrencePlan],
    ) -> Optional[str]:
        """
        Build deterministic phase9 input signature for injection-plan reuse.

        Purpose:
            Detect phase9 semantic drift using phase8 signature state so warm
            runs can safely skip redundant injection-plan rebuilds with minimal
            additional signature overhead.
        Contract:
            - Returns None when occurrence-plan inputs are unavailable.
            - Reuses phase8 occurrence-plan input signature when present.
            - Falls back to rebuild (None) when phase8 signature is unavailable.
        Args:
            occurrence_plan:
                Phase8 occurrence plan used to build phase9 injection plan.
        Returns:
            Optional[str]:
                Deterministic signature string or None when rebuild must proceed.
        """
        if occurrence_plan is None:
            return None
        return self._phase8_occurrence_plan_input_signature

    def _ensure_codegen_ir(self) -> Dict[str, Any]:
        """
        Ensure spell-scoped Codegen IR storage is initialized.

        Purpose:
            Centralize IR allocation so phase exporters can write into one
            stable payload owned by this crafter.
        Contract:
            - Initializes exactly once per crafter lifecycle.
            - Returns the owned mapping by reference.
        Returns:
            Dict[str, Any]:
                Mutable IR mapping for this spell.
        """
        if self._codegen_ir is None:
            self._codegen_ir = {
                "spell_id": self._spell.spell_index.current,
                "lineage_id": self._spell.spell_index.id,
                "phase2_5": {},
                "phase8_11": {},
                "signatures": {},
            }
        return self._codegen_ir

    @staticmethod
    def _serialize_codegen_signature_part(part: Any) -> bytes:
        """
        Serialize one signature part into deterministic bytes.

        Purpose:
            Avoid expensive mega-`repr(...)` materialization on large nested
            IR payloads while preserving deterministic signature behavior.
        Contract:
            - Uses typed fastpaths for common scalar values.
            - Uses direct `pickle` fallback for container and unsupported values.
            - Falls back to `repr(...).encode(...)` for non-picklable values.
        Args:
            part:
                One primitive/tuple/dict/set signature segment.
        Returns:
            bytes:
                Deterministic encoded bytes for hashing.
        """
        part_type = type(part)
        if part_type is dict or part_type is tuple or part_type is list or part_type is set or part_type is frozenset:
            try:
                return pickle.dumps(part, protocol=5)
            except (pickle.PickleError, TypeError, AttributeError):
                return repr(part).encode("utf-8")
        if part is None:
            return b"N"
        if part_type is bool:
            return b"B1" if part else b"B0"
        if part_type is int:
            return b"I" + str(part).encode("ascii")
        if part_type is float:
            return b"F" + repr(part).encode("ascii")
        if part_type is str:
            return b"S" + part.encode("utf-8")
        if part_type is bytes:
            return b"Y" + part
        if part_type is bytearray:
            return b"Y" + bytes(part)
        try:
            return pickle.dumps(part, protocol=5)
        except (pickle.PickleError, TypeError, AttributeError):
            return repr(part).encode("utf-8")

    @staticmethod
    def _hash_codegen_signature(*parts: Any) -> str:
        """
        Build a deterministic signature from primitive IR parts.

        Purpose:
            Produce stable fingerprints for phase-exported IR slices so Phase 12
            compilation can skip unchanged payloads.
        Contract:
            - Signature is deterministic for equal ordered inputs.
            - Does not depend on process-randomized object identity.
        Args:
            *parts:
                Ordered primitive payload parts.
        Returns:
            str:
                SHA256 hex digest for the supplied parts.
        """
        digest = hashlib.sha256()
        for part in parts:
            digest.update(SpellCrafter._serialize_codegen_signature_part(part))
            digest.update(b"|")
        return digest.hexdigest()

    def _capture_phase2_5_codegen_ir(self) -> None:
        """
        Export phases 2-5 artifacts into the spell-scoped Codegen IR payload.

        Purpose:
            Persist normalized structural metadata used by downstream Phase 12
            planning without re-reading mutable phase objects at runtime.
        Contract:
            - Safe to call repeatedly; latest phase artifacts overwrite prior IR.
            - Captures deterministic, order-stable tuples for signatures.
            - Updates `signatures.phase2_5` on each export.
        Returns:
            None.
        """
        symbolic_dependencies: Tuple[Tuple[Any, ...], ...] = ()
        if self._symbolic_graph is not None:
            symbolic_dependencies = tuple(
                (
                    dependency.param_name,
                    dependency.position,
                    dependency.di_shape.name,
                    dependency.is_optional,
                    dependency.is_collection,
                    dependency.contract_key,
                    dependency.contract_late_binding,
                )
                for dependency in self._symbolic_graph.dependencies
            )

        local_ordered_node_ids: Tuple[str, ...] = ()
        if self._resolution_frame is not None:
            local_ordered_node_ids = tuple(self._resolution_frame.ordered_node_ids)

        dependency_ids: Tuple[str, ...] = ()
        if self._spell.dependencies:
            dependency_ids = tuple(self._spell.dependencies)

        phase4_issue_codes: Tuple[str, ...] = ()
        if self._validation_result_phase4 is not None:
            phase4_issue_codes = tuple(
                issue.code
                for issue in self._validation_result_phase4.issues
            )

        phase5_root_spell_id: Optional[str] = None
        phase5_root_lineage_id: Optional[str] = None
        phase5_root_ordered_node_ids: Tuple[str, ...] = ()
        phase5_socket_ref_count = 0
        phase5_socket_rows: Tuple[Tuple[Any, ...], ...] = ()
        phase5_dag_edge_rows: Tuple[Tuple[Any, ...], ...] = ()
        if self._root_blueprint_phase5 is not None:
            phase5_root_spell_id = self._root_blueprint_phase5.root_spell_id
            try:
                phase5_root_lineage_id = self._root_blueprint_phase5.root_lineage_id
            except AttributeError:
                phase5_root_lineage_id = None
            phase5_root_ordered_node_ids = tuple(self._root_blueprint_phase5.ordered_node_ids)
            phase5_socket_ref_count = len(self._root_blueprint_phase5.socket_refs)
            phase5_socket_rows = self._build_phase5_socket_rows()
            phase5_dag_edge_rows = self._build_phase5_dag_edge_rows()

        phase5_index_spell_ids: Tuple[str, ...] = ()
        if self._spell_system_index_phase5 is not None:
            phase5_index_spell_ids = tuple(sorted(self._spell_system_index_phase5.nodes.keys()))

        phase2_5_signature = self._hash_codegen_signature(
            symbolic_dependencies,
            local_ordered_node_ids,
            dependency_ids,
            self._validated_phase4,
            self._is_broken,
            phase4_issue_codes,
            phase5_root_spell_id,
            phase5_root_lineage_id,
            phase5_root_ordered_node_ids,
            phase5_socket_ref_count,
            phase5_socket_rows,
            phase5_dag_edge_rows,
            phase5_index_spell_ids,
        )

        phase2_5_payload = {
            "symbolic_dependencies": symbolic_dependencies,
            "local_ordered_node_ids": local_ordered_node_ids,
            "dependency_ids": dependency_ids,
            "phase4_validated": self._validated_phase4,
            "phase4_is_broken": self._is_broken,
            "phase4_issue_codes": phase4_issue_codes,
            "phase5_root_spell_id": phase5_root_spell_id,
            "phase5_root_lineage_id": phase5_root_lineage_id,
            "phase5_root_ordered_node_ids": phase5_root_ordered_node_ids,
            "phase5_socket_ref_count": phase5_socket_ref_count,
            "phase5_socket_rows": phase5_socket_rows,
            "phase5_dag_edge_rows": phase5_dag_edge_rows,
            "phase5_index_spell_ids": phase5_index_spell_ids,
            "signature": phase2_5_signature,
        }

        ir_payload = self._ensure_codegen_ir()
        ir_payload["phase2_5"] = phase2_5_payload
        ir_payload["signatures"]["phase2_5"] = phase2_5_signature

    def _build_fast_transient_schema(
            self,
            transient_plan: Optional[Tuple[Any, ...]],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert the Phase11 transient tuple into a schema-only IR payload.

        Purpose:
            Remove callable/object references from transient payload export while
            preserving all indices needed for no-overrides transient codegen.
        Contract:
            - Returns None when no transient plan exists.
            - Returned payload contains only ints and tuples of ints.
        Args:
            transient_plan:
                Phase 11 transient tuple payload.
        Returns:
            Optional[Dict[str, Any]]:
                Schema-only transient payload, or None.
        """
        if transient_plan is None:
            return None
        return {
            "step_count": transient_plan[0],
            "root_step_index": transient_plan[1],
            "call_modes": tuple(transient_plan[3]),
            "dep1": tuple(transient_plan[4]),
            "dep2a": tuple(transient_plan[5]),
            "dep2b": tuple(transient_plan[6]),
            "dep3a": tuple(transient_plan[7]),
            "dep3b": tuple(transient_plan[8]),
            "dep3c": tuple(transient_plan[9]),
            "dep4a": tuple(transient_plan[10]),
            "dep4b": tuple(transient_plan[11]),
            "dep4c": tuple(transient_plan[12]),
            "dep4d": tuple(transient_plan[13]),
            "dep5a": tuple(transient_plan[14]),
            "dep5b": tuple(transient_plan[15]),
            "dep5c": tuple(transient_plan[16]),
            "dep5d": tuple(transient_plan[17]),
            "dep5e": tuple(transient_plan[18]),
            "dep6a": tuple(transient_plan[19]),
            "dep6b": tuple(transient_plan[20]),
            "dep6c": tuple(transient_plan[21]),
            "dep6d": tuple(transient_plan[22]),
            "dep6e": tuple(transient_plan[23]),
            "dep6f": tuple(transient_plan[24]),
            "dep7a": tuple(transient_plan[25]),
            "dep7b": tuple(transient_plan[26]),
            "dep7c": tuple(transient_plan[27]),
            "dep7d": tuple(transient_plan[28]),
            "dep7e": tuple(transient_plan[29]),
            "dep7f": tuple(transient_plan[30]),
            "dep7g": tuple(transient_plan[31]),
            "dep8a": tuple(transient_plan[32]),
            "dep8b": tuple(transient_plan[33]),
            "dep8c": tuple(transient_plan[34]),
            "dep8d": tuple(transient_plan[35]),
            "dep8e": tuple(transient_plan[36]),
            "dep8f": tuple(transient_plan[37]),
            "dep8g": tuple(transient_plan[38]),
            "dep8h": tuple(transient_plan[39]),
        }

    def _build_fast_transient_signature(
            self,
            transient_schema: Optional[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Build a deterministic signature for a Phase 11 fast transient plan.

        Purpose:
            Fingerprint transient plan structure without including call-target
            object identities, which are process-local and nondeterministic.
        Contract:
            - Returns None when no transient plan exists.
            - Signature includes step counts, call modes, and dependency index
              arrays used by no-overrides execution.
        Args:
            transient_schema:
                Schema-only transient payload exported by
                `_build_fast_transient_schema`.
        Returns:
            Optional[str]:
                Deterministic transient signature, or None.
        """
        if transient_schema is None:
            return None
        return self._hash_codegen_signature(
            transient_schema["step_count"],
            transient_schema["root_step_index"],
            transient_schema["call_modes"],
            transient_schema["dep1"],
            transient_schema["dep2a"],
            transient_schema["dep2b"],
            transient_schema["dep3a"],
            transient_schema["dep3b"],
            transient_schema["dep3c"],
            transient_schema["dep4a"],
            transient_schema["dep4b"],
            transient_schema["dep4c"],
            transient_schema["dep4d"],
            transient_schema["dep5a"],
            transient_schema["dep5b"],
            transient_schema["dep5c"],
            transient_schema["dep5d"],
            transient_schema["dep5e"],
            transient_schema["dep6a"],
            transient_schema["dep6b"],
            transient_schema["dep6c"],
            transient_schema["dep6d"],
            transient_schema["dep6e"],
            transient_schema["dep6f"],
            transient_schema["dep7a"],
            transient_schema["dep7b"],
            transient_schema["dep7c"],
            transient_schema["dep7d"],
            transient_schema["dep7e"],
            transient_schema["dep7f"],
            transient_schema["dep7g"],
            transient_schema["dep8a"],
            transient_schema["dep8b"],
            transient_schema["dep8c"],
            transient_schema["dep8d"],
            transient_schema["dep8e"],
            transient_schema["dep8f"],
            transient_schema["dep8g"],
            transient_schema["dep8h"],
        )

    @staticmethod
    def _instance_key_sort_key(
            instance_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        """
        Build a deterministic sort key for instance-key tuples.

        Purpose:
            Keep schema-row ordering stable for `(spell_id, path_id)` keys.
        Contract:
            - `None` path ids sort before concrete path ids.
            - Spell id remains the primary sort dimension.
        Args:
            instance_key:
                Instance key `(spell_id, path_id)`.
        Returns:
            Tuple[str, int]:
                Comparable sort key.
        """
        path_id = instance_key[1]
        return (
            instance_key[0],
            -1 if path_id is None else path_id,
        )

    @staticmethod
    def _occurrence_key_sort_key(
            occurrence_key: Tuple[str, Optional[int]],
    ) -> Tuple[str, int]:
        """
        Build a deterministic sort key for occurrence-key tuples.

        Purpose:
            Keep occurrence schema row ordering stable across equivalent maps.
        Contract:
            - `None` path ids sort before concrete path ids.
            - Spell id remains the primary sort dimension.
        Args:
            occurrence_key:
                Occurrence key `(spell_id, path_id)`.
        Returns:
            Tuple[str, int]:
                Comparable sort key.
        """
        path_id = occurrence_key[1]
        return (
            occurrence_key[0],
            -1 if path_id is None else path_id,
        )

    @staticmethod
    def _socket_row_sort_key(
            socket_row: Tuple[str, str, int, str],
    ) -> Tuple[str, int, str, str]:
        """
        Build a deterministic sort key for socket schema rows.

        Purpose:
            Normalize patch-map and phase5 socket row ordering.
        Contract:
            - Sorts by node id, then path id, then parameter name, then kind.
        Args:
            socket_row:
                Socket row `(node_id, param_name, param_path_id, socket_kind)`.
        Returns:
            Tuple[str, int, str, str]:
                Comparable sort key.
        """
        return (
            socket_row[0],
            socket_row[2],
            socket_row[1],
            socket_row[3],
        )

    def _build_phase5_socket_rows(self) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase5 socket references.

        Purpose:
            Export explicit socket routing data from the root blueprint into
            Phase2-5 IR without leaking live socket objects.
        Contract:
            - Returns only primitive tuple rows.
            - Ignores malformed socket objects that do not expose required fields.
            - Output row order is deterministic.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(node_id, param_name, param_path_id, socket_kind)`.
        """
        if self._root_blueprint_phase5 is None:
            return ()
        rows: List[Tuple[Any, ...]] = []
        for socket_ref in self._root_blueprint_phase5.socket_refs:
            try:
                rows.append(
                    (
                        socket_ref.node_id,
                        socket_ref.param_name,
                        socket_ref.param_path_id,
                        socket_ref.socket_kind.value,
                    )
                )
            except AttributeError:
                continue
        rows.sort(key=self._socket_row_sort_key)
        return tuple(rows)

    def _build_phase5_dag_edge_rows(self) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase5 DAG edges.

        Purpose:
            Export explicit parent->child routing from the root blueprint DAG so
            codegen consumers can validate structural semantics from IR alone.
        Contract:
            - Returns only primitive tuple rows.
            - Ignores malformed DAG nodes that do not expose expected fields.
            - Output row order is deterministic.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(parent_spell_id, child_spell_id, param_name, socket_kind)`.
        """
        if self._root_blueprint_phase5 is None:
            return ()
        try:
            dag = self._root_blueprint_phase5.dag
            nodes = dag.nodes
        except AttributeError:
            return ()
        rows: List[Tuple[Any, ...]] = []
        for parent_spell_id in sorted(nodes.keys()):
            parent_node = nodes[parent_spell_id]
            try:
                dependents = list(parent_node.dependents)
            except AttributeError:
                continue
            for child_node in dependents:
                try:
                    child_spell_id = child_node.id
                except AttributeError:
                    continue
                param_name = None
                try:
                    param_name = child_node.incoming_params.get(parent_node)
                except AttributeError:
                    param_name = None
                socket_kind = None
                try:
                    raw_socket_kind = dag._socket_kinds.get((parent_node, child_node))
                except AttributeError:
                    raw_socket_kind = None
                if raw_socket_kind is not None:
                    try:
                        socket_kind = raw_socket_kind.value
                    except AttributeError:
                        socket_kind = repr(raw_socket_kind)
                rows.append(
                    (
                        parent_spell_id,
                        child_spell_id,
                        param_name,
                        socket_kind,
                    )
                )
        rows.sort(
            key=lambda row: (
                row[0],
                row[1],
                "" if row[2] is None else row[2],
                "" if row[3] is None else str(row[3]),
            )
        )
        return tuple(rows)

    def _build_occurrence_graph_rows(
            self,
            occurrence_graph: Dict[Tuple[str, Optional[int]], Dict[str, List[Tuple[str, Optional[int]]]]],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for the Phase8 occurrence graph.

        Purpose:
            Export occurrence graph topology as schema-only tuples so consumers
            can validate dependency routing without live plan objects.
        Contract:
            - Returns only primitive tuple rows.
            - Sorts occurrences and dependency occurrence lists deterministically.
        Args:
            occurrence_graph:
                Occurrence graph mapping from Phase8 plan.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(occurrence_key, dependency_rows)`.
        """
        rows: List[Tuple[Any, ...]] = []
        for occurrence_key in sorted(
                occurrence_graph.keys(),
                key=self._occurrence_key_sort_key,
        ):
            dependency_map = occurrence_graph[occurrence_key]
            dependency_rows: List[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]]] = []
            for param_name in sorted(dependency_map.keys()):
                dependency_occurrences = dependency_map[param_name]
                normalized_occurrences_list = [
                    tuple(dependency_occurrence)
                    for dependency_occurrence in dependency_occurrences
                ]
                if len(normalized_occurrences_list) > 1:
                    normalized_occurrences_list.sort(
                        key=self._occurrence_key_sort_key,
                    )
                normalized_occurrences = tuple(normalized_occurrences_list)
                dependency_rows.append((param_name, normalized_occurrences))
            rows.append(
                (
                    tuple(occurrence_key),
                    tuple(dependency_rows),
                )
            )
        return tuple(rows)

    def _build_occurrence_instance_key_rows(
            self,
            instance_keys_by_spell_id: Dict[str, List[Tuple[str, Optional[int]]]],
    ) -> Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...]:
        """
        Build deterministic schema rows for Phase8 instance-key planning.

        Purpose:
            Export per-spell instance key planning from occurrence plans in a
            stable schema-only representation.
        Contract:
            - Returns only primitive tuple rows.
            - Spell ids and instance-key lists are deterministically ordered.
        Args:
            instance_keys_by_spell_id:
                Mapping from spell id to planned instance keys.
        Returns:
            Tuple[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]], ...]:
                Rows `(spell_id, instance_keys)`.
        """
        rows: List[Tuple[str, Tuple[Tuple[str, Optional[int]], ...]]] = []
        for spell_id in sorted(instance_keys_by_spell_id.keys()):
            instance_keys_list = [
                tuple(instance_key)
                for instance_key in instance_keys_by_spell_id[spell_id]
            ]
            if len(instance_keys_list) > 1:
                instance_keys_list.sort(key=self._instance_key_sort_key)
            instance_keys = tuple(instance_keys_list)
            rows.append((spell_id, instance_keys))
        return tuple(rows)

    def _build_occurrence_canonical_rows(
            self,
            canonical_occurrences_by_spell_id: Dict[str, Tuple[str, Optional[int]]],
    ) -> Tuple[Tuple[str, Tuple[str, Optional[int]]], ...]:
        """
        Build deterministic schema rows for Phase8 canonical occurrences.

        Purpose:
            Export the shared-occurrence canonical mapping in schema form for
            deterministic validation and signature coverage.
        Contract:
            - Returns only primitive tuple rows.
            - Spell-id order is deterministic.
        Args:
            canonical_occurrences_by_spell_id:
                Mapping from spell id to canonical occurrence key.
        Returns:
            Tuple[Tuple[str, Tuple[str, Optional[int]]], ...]:
                Rows `(spell_id, canonical_occurrence_key)`.
        """
        rows: List[Tuple[str, Tuple[str, Optional[int]]]] = []
        for spell_id in sorted(canonical_occurrences_by_spell_id.keys()):
            rows.append(
                (
                    spell_id,
                    tuple(canonical_occurrences_by_spell_id[spell_id]),
                )
            )
        return tuple(rows)

    def _build_occurrence_contract_override_rows(
            self,
            contract_overrides_by_occurrence: Dict[Tuple[str, Optional[int]], Dict[str, Any]],
    ) -> Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]:
        """
        Build deterministic schema rows for occurrence-scoped contract payloads.

        Purpose:
            Export Phase8 contract payload overlays with deterministic value
            freezing for signature and contract-audit use.
        Contract:
            - Returns only primitive tuple rows.
            - Payload items are key-sorted and recursively frozen.
        Args:
            contract_overrides_by_occurrence:
                Mapping from occurrence key to payload mapping.
        Returns:
            Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]:
                Rows `(occurrence_key, payload_items)`.
        """
        rows: List[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]]] = []
        for occurrence_key in sorted(
                contract_overrides_by_occurrence.keys(),
                key=self._occurrence_key_sort_key,
        ):
            payload = contract_overrides_by_occurrence[occurrence_key]
            payload_items = tuple(
                sorted(
                    (
                        param_name,
                        self._freeze_phase11_schema_value(value),
                    )
                    for param_name, value in payload.items()
                )
            )
            rows.append((tuple(occurrence_key), payload_items))
        return tuple(rows)

    def _build_occurrence_contract_override_spell_rows(
            self,
            contract_overrides_by_spell_id: Dict[str, List[Tuple[Tuple[str, Optional[int]], Dict[str, Any]]]],
    ) -> Tuple[Tuple[str, Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]], ...]:
        """
        Build deterministic schema rows for spell-grouped contract payloads.

        Purpose:
            Export spell-grouped contract payload overlays from Phase8 in a
            deterministic schema for contract completeness audits.
        Contract:
            - Returns only primitive tuple rows.
            - Spell ids and grouped occurrence rows are deterministically ordered.
        Args:
            contract_overrides_by_spell_id:
                Mapping from spell id to `(occurrence_key, payload)` entries.
        Returns:
            Tuple[Tuple[str, Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]], ...]:
                Rows `(spell_id, occurrence_payload_rows)`.
        """
        rows: List[Tuple[str, Tuple[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]], ...]]] = []
        for spell_id in sorted(contract_overrides_by_spell_id.keys()):
            grouped_rows: List[Tuple[Tuple[str, Optional[int]], Tuple[Tuple[str, Any], ...]]] = []
            for occurrence_key, payload in contract_overrides_by_spell_id[spell_id]:
                payload_items = tuple(
                    sorted(
                        (
                            param_name,
                            self._freeze_phase11_schema_value(value),
                        )
                        for param_name, value in payload.items()
                    )
                )
                grouped_rows.append((tuple(occurrence_key), payload_items))
            grouped_rows.sort(
                key=lambda row: self._occurrence_key_sort_key(row[0]),
            )
            rows.append((spell_id, tuple(grouped_rows)))
        return tuple(rows)

    def _build_injection_instance_rows(
            self,
            instance_injections: Dict[Tuple[str, Optional[int]], Any],
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase9 injection specifications.

        Purpose:
            Export per-instance injection semantics (dependency keys, contract
            payloads, aggregation flags) as deterministic schema-only rows.
        Contract:
            - Returns only primitive tuple rows.
            - Expects InjectionSpec/ParamSource contract fields to be present.
            - Fails fast when malformed/cleaned artifacts violate contract.
        Args:
            instance_injections:
                Mapping from instance key to InjectionSpec-like objects.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(instance_key, allow_list, uses_positional, contract_items, param_rows)`.
        """
        rows: List[Tuple[Any, ...]] = []
        for instance_key in sorted(
                instance_injections.keys(),
                key=self._instance_key_sort_key,
        ):
            injection_spec = instance_injections[instance_key]
            allow_list_aggregation = bool(injection_spec.allow_list_aggregation)
            uses_positional_override = bool(injection_spec.uses_positional_override)
            contract_payload_items: Tuple[Tuple[str, Any], ...] = ()
            param_rows: List[Tuple[Any, ...]] = []
            contract_payload = injection_spec.contract_payload
            if contract_payload:
                contract_payload_items = tuple(
                    sorted(
                        (
                            param_name,
                            self._freeze_phase11_schema_value(value),
                        )
                        for param_name, value in contract_payload.items()
                    )
                )

            param_sources = injection_spec.param_sources
            if param_sources:
                for param_name in sorted(param_sources.keys()):
                    param_source = param_sources[param_name]
                    kind = param_source.kind
                    dependency_keys: Tuple[Tuple[str, Optional[int]], ...] = ()
                    raw_dependency_keys = param_source.dependency_keys
                    if raw_dependency_keys:
                        dependency_key_list = [
                            tuple(dependency_key)
                            for dependency_key in raw_dependency_keys
                        ]
                        if len(dependency_key_list) > 1:
                            dependency_key_list.sort(
                                key=self._instance_key_sort_key,
                            )
                        dependency_keys = tuple(dependency_key_list)
                    override_key = param_source.override_key
                    contract_key = param_source.contract_key
                    param_rows.append(
                        (
                            param_name,
                            kind,
                            dependency_keys,
                            override_key,
                            contract_key,
                        )
                    )

            rows.append(
                (
                    tuple(instance_key),
                    allow_list_aggregation,
                    uses_positional_override,
                    contract_payload_items,
                    tuple(param_rows),
                )
            )
        return tuple(rows)

    def _build_override_target_rows(
            self,
            override_patch_map: Any,
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase10 override patch-map targets.

        Purpose:
            Export concrete socket-target rows grouped by TargetSpec for
            codegen contract completeness and signature invalidation.
        Contract:
            - Returns only primitive tuple rows.
            - Includes specificity values when available.
            - Expects OverridePatchMap target/spec specificity contracts.
            - Fails fast when malformed/cleaned artifacts violate contract.
        Args:
            override_patch_map:
                OverridePatchMap-like object.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(spec_key, specificity, socket_rows)`.
        """
        if override_patch_map is None:
            return ()
        targets_by_spec = override_patch_map._targets_by_spec
        specificity_by_spec = override_patch_map._specificity_by_spec

        rows: List[Tuple[Any, ...]] = []
        for spec_key in sorted(targets_by_spec.keys()):
            raw_targets = targets_by_spec[spec_key]
            socket_rows: List[Tuple[str, str, int, str]] = []
            for socket_ref in raw_targets:
                socket_rows.append(
                    (
                        socket_ref.node_id,
                        socket_ref.param_name,
                        socket_ref.param_path_id,
                        socket_ref.socket_kind.value,
                    )
                )
            if len(socket_rows) > 1:
                socket_rows.sort(key=self._socket_row_sort_key)

            specificity_value = None
            if specificity_by_spec:
                specificity = specificity_by_spec.get(spec_key)
                if specificity is not None:
                    specificity_value = int(specificity)

            rows.append(
                (
                    spec_key,
                    specificity_value,
                    tuple(socket_rows),
                )
            )
        return tuple(rows)

    def _build_mutation_target_rows(
            self,
            mutation_patch_map: Any,
    ) -> Tuple[Tuple[Any, ...], ...]:
        """
        Build deterministic schema rows for Phase10 mutation patch-map targets.

        Purpose:
            Export concrete mutation-edge patch descriptors grouped by TargetSpec
            for codegen contract completeness and signature invalidation.
        Contract:
            - Returns only primitive tuple rows.
            - Expects MutationPatchMap target contract fields.
            - Fails fast when malformed/cleaned artifacts violate contract.
        Args:
            mutation_patch_map:
                MutationPatchMap-like object.
        Returns:
            Tuple[Tuple[Any, ...], ...]:
                Rows `(spec_key, patch_rows)`.
        """
        if mutation_patch_map is None:
            return ()
        targets_by_spec = mutation_patch_map._targets_by_spec
        rows: List[Tuple[Any, ...]] = []
        for spec_key in sorted(targets_by_spec.keys()):
            raw_patches = targets_by_spec[spec_key]
            patch_rows: List[Tuple[Any, ...]] = []
            for patch in raw_patches:
                patch_rows.append(
                    (
                        patch.child_spell_id,
                        patch.param_name,
                        patch.param_path_id,
                        patch.old_parent_id,
                    )
                )
            if len(patch_rows) > 1:
                patch_rows.sort(
                    key=lambda row: (
                        row[0],
                        row[1],
                        row[2],
                        "" if row[3] is None else row[3],
                    )
                )
            rows.append((spec_key, tuple(patch_rows)))
        return tuple(rows)

    @staticmethod
    def _freeze_phase11_schema_value(value: Any) -> Any:
        """
        Normalize arbitrary values into deterministic schema-safe forms.

        Purpose:
            Convert nested payload values into primitive/tuple structures so
            Phase11 IR rows can be serialized without leaking live objects.
        Contract:
            - Primitive values are returned as-is.
            - Dict/list/tuple/set values are recursively normalized.
            - Non-primitive objects are represented by deterministic repr text.
        Args:
            value:
                Raw value captured from plan metadata.
        Returns:
            Any:
                Deterministic schema-safe value.
        """
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (
                        key,
                        SpellCrafter._freeze_phase11_schema_value(item),
                    )
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(
                SpellCrafter._freeze_phase11_schema_value(item)
                for item in value
            )
        if isinstance(value, set):
            return tuple(
                sorted(
                    (
                        SpellCrafter._freeze_phase11_schema_value(item)
                        for item in value
                    ),
                    key=repr,
                )
            )
        return repr(value)

    def _build_phase11_step_ir_row(
            self,
            step: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Build one schema-only Phase11 step row for IR export.

        Purpose:
            Capture step semantics without exporting live plan/spell objects.
        Contract:
            - Output contains only primitive/tuple values.
            - Includes all no-overrides and overrides semantics consumed by
              compilers and runtime shape-key signatures.
        Args:
            step:
                ExecutionPlanStep-like object.
        Returns:
            Dict[str, Any]:
                Normalized step row.
        """
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        )
        contract_payload_items: Tuple[Any, ...] = ()
        if step.contract_payload:
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        self._freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        override_match_prefix = None
        override_match_prefix_len = 0
        override_keys: Tuple[Any, ...] = ()
        expects_overrides = False
        if include_override_metadata:
            override_match_prefix = step.override_match_prefix
            override_match_prefix_len = step.override_match_prefix_len
            override_keys = tuple(step.override_keys)
            expects_overrides = step.expects_overrides
        return {
            "instance_key": tuple(step.instance_key),
            "spell_id": step.spell.spell_index.current,
            "existence": step.existence.name,
            "creations_target_kind": step.creations_target_kind,
            "shared_instance": step.shared_instance,
            "dependency_resolution_order": dependency_resolution_order,
            "override_match_prefix": override_match_prefix,
            "override_match_prefix_len": override_match_prefix_len,
            "override_keys": override_keys,
            "expects_overrides": expects_overrides,
            "contract_keys": tuple(step.contract_keys),
            "allow_list_aggregation": step.allow_list_aggregation,
            "uses_positional_override": step.uses_positional_override,
            "contract_positional_override": self._freeze_phase11_schema_value(
                step.contract_positional_override,
            ),
            "has_contract_payload": step.has_contract_payload,
            "contract_payload_items": contract_payload_items,
            "lock_hint": step.lock_hint,
            "use_spell_lock_hint": step.use_spell_lock_hint,
            "requires_spellspace": step.requires_spellspace,
            "owner_conduit_required": step.owner_conduit_required,
            "must_register": step.must_register,
            "disposal_method_names": tuple(step.disposal_method_names),
        }

    def _build_phase11_variant_ir_payload(
            self,
            plan: Optional[ExecutionPlan],
    ) -> Dict[str, Any]:
        """
        Export one Phase 11 execution-plan variant into IR fields.

        Purpose:
            Normalize plan metadata and signatures so Phase 12 and runtime
            dispatch can consume a deterministic payload.
        Contract:
            - Returns a payload dictionary for any input; empty plan fields are
              represented as None/empty tuples.
            - Exposes schema-only step/transient payloads with no live objects.
        Args:
            plan:
                Execution plan variant to export.
        Returns:
            Dict[str, Any]:
                Normalized Phase 11 variant payload.
        """
        if plan is None:
            return {
                "plan_variant": None,
                "root_spell_id": None,
                "step_count": 0,
                "step_spell_ids": (),
                "transient_signature": None,
                "signature": None,
                "transient_schema": None,
                "steps_rows": (),
                "steps_rows_signature": None,
            }

        steps = plan.steps
        include_override_metadata = (
            plan.plan_variant != ExecutionPlanVariant.NO_OVERRIDES_FAST
        )
        steps_rows = tuple(
            self._build_phase11_step_ir_row(
                step,
                include_override_metadata=include_override_metadata,
            )
            for step in steps
        )
        # Hash the full tuple payload as one signature part to avoid per-row
        # serializer churn while preserving deterministic invalidation behavior.
        steps_rows_signature = self._hash_codegen_signature(steps_rows)
        step_spell_ids = tuple(
            step.spell.spell_index.current
            for step in steps
        )
        transient_schema = self._build_fast_transient_schema(plan.fast_transient_plan)
        transient_signature = self._build_fast_transient_signature(transient_schema)
        signature = self._hash_codegen_signature(
            plan.plan_variant,
            plan.root_spell_id,
            step_spell_ids,
            steps_rows_signature,
            transient_signature,
        )
        return {
            "plan_variant": plan.plan_variant,
            "root_spell_id": plan.root_spell_id,
            "step_count": len(steps),
            "step_spell_ids": step_spell_ids,
            "transient_signature": transient_signature,
            "signature": signature,
            "transient_schema": transient_schema,
            "steps_rows": steps_rows,
            "steps_rows_signature": steps_rows_signature,
        }

    def _build_phase12_no_overrides_step_signature_row(
            self,
            step: Any,
    ) -> Tuple[Any, ...]:
        """
        Build one deterministic signature row for no-overrides compile caching.

        Purpose:
            Capture only the step fields that influence phase12 no-overrides
            compiled source/namespace behavior without constructing full IR
            payload dict rows.
        Contract:
            - Returns a tuple-only row with deterministic ordering.
            - Includes dependency, contract, lock, and registration semantics.
        Args:
            step:
                ExecutionPlanStep-like object.
        Returns:
            Tuple[Any, ...]:
                Deterministic row used by no-overrides plan signature hashing.
        """
        dependency_resolution_order = tuple(
            (
                param_name,
                tuple(dependency_keys),
            )
            for param_name, dependency_keys in step.dependency_resolution_order
        )
        contract_payload_items: Tuple[Any, ...] = ()
        if step.contract_payload:
            contract_payload_items = tuple(
                sorted(
                    (
                        param_name,
                        self._freeze_phase11_schema_value(value),
                    )
                    for param_name, value in step.contract_payload.items()
                )
            )
        return (
            tuple(step.instance_key),
            step.spell.spell_index.current,
            step.existence.name,
            step.creations_target_kind,
            dependency_resolution_order,
            bool(step.uses_positional_override),
            self._freeze_phase11_schema_value(step.contract_positional_override),
            bool(step.has_contract_payload),
            contract_payload_items,
            bool(step.use_spell_lock_hint),
            bool(step.must_register),
        )

    def _build_phase11_spell_signature_row(
            self,
            spell: ISpell,
    ) -> Tuple[Any, ...]:
        """
        Build deterministic spell metadata row for Phase 11 no-overrides inputs.

        Purpose:
            Capture spell fields consumed by `ExecutionPlanBuilder.build` so
            phase11 can detect when no-overrides rebuild is required.
        Contract:
            - Includes existence/register/disposal and optimistic-object identity.
            - Uses primitive/tuple values only for deterministic hashing.
        Args:
            spell:
                Spell referenced by occurrence execution order.
        Returns:
            Tuple[Any, ...]:
                Deterministic spell metadata row.
        """
        optimistic_object_identity = None
        if spell.user_created_object is not None:
            optimistic_object_identity = id(spell.user_created_object)
        is_callable_spell = spell.spell_type in (
            SpellType.SPELL,
            SpellType.SPELL_WITH_SPELLFRAME,
            SpellType.SPELL_WITH_BINDING_NAME,
            SpellType.SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.METHOD,
            SpellType.METHOD_WITH_BINDING_NAME,
            SpellType.METHOD_WITH_SPELLFRAME,
            SpellType.METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            SpellType.LAMBDA_METHOD_WITH_SPELLFRAME,
            SpellType.LAMBDA_METHOD_WITH_BINDING_NAME_WITH_SPELLFRAME,
        )
        must_register = True
        if spell.existence is Existence.many and not spell.has_disposal_methods:
            must_register = False
        return (
            spell.spell_index.current,
            spell.existence.name,
            bool(spell.is_existing_creation),
            bool(is_callable_spell),
            bool(must_register),
            bool(spell.has_disposal_methods),
            tuple(spell.disposal_method_names),
            optimistic_object_identity,
        )

    @staticmethod
    def _build_phase11_injection_spec_signature_row(
            injection_spec: Any,
            *,
            include_override_metadata: bool = True,
    ) -> Tuple[Any, ...]:
        """
        Build deterministic InjectionSpec row for Phase 11 input signatures.

        Purpose:
            Normalize injection metadata used by `ExecutionPlanBuilder.build`
            without allocating Phase 11 steps.
        Contract:
            - Includes param source wiring, aggregation flags, and contract payload.
            - Returns tuple-only deterministic structure.
        Args:
            injection_spec:
                Phase 9 InjectionSpec-like object.
        Returns:
            Tuple[Any, ...]:
                Deterministic signature row.
        """
        param_rows: List[Tuple[Any, ...]] = []
        param_sources = injection_spec.param_sources
        for param_name in sorted(param_sources.keys()):
            param_source = param_sources[param_name]
            dependency_keys = None
            if param_source.dependency_keys is not None:
                dependency_keys = tuple(
                    tuple(dependency_key)
                    for dependency_key in param_source.dependency_keys
                )
            override_key = None
            if include_override_metadata:
                override_key = param_source.override_key
            param_rows.append(
                (
                    param_name,
                    param_source.kind,
                    dependency_keys,
                    override_key,
                    param_source.contract_key,
                )
            )

        contract_payload = injection_spec.contract_payload
        normalized_contract_payload = None
        if contract_payload is not None:
            normalized_contract_payload = dict(contract_payload)
            if (
                    "__args__" in normalized_contract_payload
                    and isinstance(normalized_contract_payload["__args__"], list)
            ):
                normalized_contract_payload["__args__"] = tuple(
                    normalized_contract_payload["__args__"]
                )

        return (
            tuple(param_rows),
            bool(injection_spec.allow_list_aggregation),
            bool(injection_spec.uses_positional_override),
            normalized_contract_payload,
        )

    def _build_phase11_no_overrides_input_signature(
            self,
            *,
            occurrence_plan: OccurrencePlan,
            injection_plan: Optional[InjectionPlan],
            spell_lookup: Dict[str, ISpell],
    ) -> Optional[str]:
        """
        Build deterministic no-overrides input signature for Phase 11 reuse.

        Purpose:
            Detect semantic drift in plan-builder inputs so repeated warm runs
            can safely skip redundant no-overrides full builds.
        Contract:
            - Returns `None` when required spell/injection inputs are missing,
              forcing the legacy rebuild path.
            - Includes occurrence graph rows, injection wiring rows, and spell
              metadata consumed by `ExecutionPlanBuilder.build`.
        Args:
            occurrence_plan:
                Phase 8 occurrence plan for this spell.
            injection_plan:
                Optional Phase 9 injection plan.
            spell_lookup:
                Spell lookup map keyed by spell id.
        Returns:
            Optional[str]:
                Deterministic input signature, or `None` when rebuild must not be
                elided due to missing inputs.
        """
        try:
            execution_order = tuple(occurrence_plan.execution_order)
            shared_spell_ids = occurrence_plan.shared_spell_ids
            shared_spell_ids_row = tuple(sorted(shared_spell_ids))
            root_instance_key = tuple(occurrence_plan.root_instance_key)
            root_spell_id = occurrence_plan.root_spell_id
            contract_dependencies_complete = bool(
                occurrence_plan.contract_dependencies_complete,
            )
            occurrence_graph = occurrence_plan.occurrence_graph
            instance_keys_by_spell_id = occurrence_plan.instance_keys_by_spell_id
            canonical_occurrences_by_spell_id = occurrence_plan.canonical_occurrences_by_spell_id
            contract_overrides_by_occurrence = occurrence_plan.contract_overrides_by_occurrence
        except AttributeError:
            return None

        spell_rows: List[Tuple[Any, ...]] = []
        occurrence_rows: List[Tuple[Any, ...]] = []

        for spell_id in execution_order:
            spell = spell_lookup.get(spell_id)
            if spell is None:
                return None
            spell_rows.append(self._build_phase11_spell_signature_row(spell))

            canonical_occurrence = canonical_occurrences_by_spell_id.get(spell_id)
            instance_keys = instance_keys_by_spell_id.get(spell_id, ())
            for instance_key in instance_keys:
                occurrence = (spell_id, instance_key[1])
                if spell_id in shared_spell_ids and canonical_occurrence is not None:
                    occurrence = canonical_occurrence
                dependencies = occurrence_graph.get(occurrence, {})
                dependency_rows: List[Tuple[Any, ...]] = []
                for param_name in sorted(dependencies.keys()):
                    dependency_rows.append(
                        (
                            param_name,
                            tuple(
                                tuple(dependency_occurrence)
                                for dependency_occurrence in dependencies[param_name]
                            ),
                        )
                    )
                contract_payload = contract_overrides_by_occurrence.get(occurrence)
                if contract_payload is not None and "__args__" in contract_payload:
                    args_payload = contract_payload["__args__"]
                    if isinstance(args_payload, list):
                        contract_payload = dict(contract_payload)
                        contract_payload["__args__"] = tuple(args_payload)
                occurrence_rows.append(
                    (
                        tuple(instance_key),
                        tuple(occurrence),
                        tuple(dependency_rows),
                        contract_payload,
                    )
                )

        injection_rows: Tuple[Any, ...] = ()
        if injection_plan is not None:
            try:
                injection_lookup = injection_plan.select_for_runtime(
                    root_spell_id=root_spell_id,
                )
            except AttributeError:
                return None
            if injection_lookup is None:
                return None
            injection_rows_list: List[Tuple[Any, ...]] = []
            for instance_key in sorted(injection_lookup.keys()):
                try:
                    injection_spec_row = self._build_phase11_injection_spec_signature_row(
                        injection_lookup[instance_key],
                        include_override_metadata=False,
                    )
                except AttributeError:
                    return None
                injection_rows_list.append(
                    (
                        tuple(instance_key),
                        injection_spec_row,
                    )
                )
            injection_rows = tuple(injection_rows_list)

        return self._hash_codegen_signature(
            root_spell_id,
            root_instance_key,
            contract_dependencies_complete,
            execution_order,
            shared_spell_ids_row,
            tuple(spell_rows),
            tuple(occurrence_rows),
            injection_rows,
        )

    def _build_phase12_no_overrides_plan_signature(
            self,
            plan: ExecutionPlan,
            transient_schema: Optional[Dict[str, Any]],
    ) -> str:
        """
        Build deterministic no-overrides compile signature from a Phase11 plan.

        Purpose:
            Fingerprint compile-affecting plan semantics in phase11 hot path
            without building full no-overrides IR payload rows.
        Contract:
            - Includes root instance key, step semantic rows, and transient
              schema signature.
            - Returned signature changes when no-overrides compiler inputs drift.
        Args:
            plan:
                No-overrides execution plan.
            transient_schema:
                Schema-only transient payload for this plan.
        Returns:
            str:
                Deterministic compile cache signature.
        """
        step_signature_rows = tuple(
            self._build_phase12_no_overrides_step_signature_row(step)
            for step in plan.steps
        )
        transient_signature = self._build_fast_transient_signature(transient_schema)
        root_instance_key = None
        if plan.root_instance_key is not None:
            root_instance_key = tuple(plan.root_instance_key)
        return self._hash_codegen_signature(
            plan.root_spell_id,
            root_instance_key,
            step_signature_rows,
            transient_signature,
        )

    def _capture_phase8_11_codegen_ir(self) -> None:
        """
        Export phases 8-11 artifacts into the spell-scoped Codegen IR payload.

        Purpose:
            Publish normalized execution-planning metadata needed by Phase 12
            compilation and runtime plan dispatch.
        Contract:
            - Safe to call repeatedly; latest phase artifacts overwrite prior IR.
            - Updates `signatures.phase8_11` on each export.
            - Keeps override/mutation variants distinct.
        Returns:
            None.
        """
        occurrence_execution_order: Tuple[str, ...] = ()
        occurrence_root_instance_key: Optional[Tuple[str, Optional[int]]] = None
        occurrence_shared_spell_ids: Tuple[str, ...] = ()
        occurrence_contract_complete: Optional[bool] = None
        occurrence_graph_rows: Tuple[Tuple[Any, ...], ...] = ()
        occurrence_instance_key_rows: Tuple[Tuple[Any, ...], ...] = ()
        occurrence_canonical_rows: Tuple[Tuple[Any, ...], ...] = ()
        occurrence_contract_override_rows: Tuple[Tuple[Any, ...], ...] = ()
        occurrence_contract_override_spell_rows: Tuple[Tuple[Any, ...], ...] = ()
        if self._occurrence_plan_phase8 is not None:
            occurrence_execution_order = tuple(self._occurrence_plan_phase8.execution_order)
            occurrence_root_instance_key = self._occurrence_plan_phase8.root_instance_key
            occurrence_shared_spell_ids = tuple(sorted(self._occurrence_plan_phase8.shared_spell_ids))
            occurrence_contract_complete = self._occurrence_plan_phase8.contract_dependencies_complete
            try:
                occurrence_graph_rows = self._build_occurrence_graph_rows(
                    self._occurrence_plan_phase8.occurrence_graph,
                )
            except AttributeError:
                occurrence_graph_rows = ()
            try:
                occurrence_instance_key_rows = self._build_occurrence_instance_key_rows(
                    self._occurrence_plan_phase8.instance_keys_by_spell_id,
                )
            except AttributeError:
                occurrence_instance_key_rows = ()
            try:
                occurrence_canonical_rows = self._build_occurrence_canonical_rows(
                    self._occurrence_plan_phase8.canonical_occurrences_by_spell_id,
                )
            except AttributeError:
                occurrence_canonical_rows = ()
            try:
                occurrence_contract_override_rows = self._build_occurrence_contract_override_rows(
                    self._occurrence_plan_phase8.contract_overrides_by_occurrence,
                )
            except AttributeError:
                occurrence_contract_override_rows = ()
            try:
                occurrence_contract_override_spell_rows = self._build_occurrence_contract_override_spell_rows(
                    self._occurrence_plan_phase8.contract_overrides_by_spell_id,
                )
            except AttributeError:
                occurrence_contract_override_spell_rows = ()

        injection_instance_keys: Tuple[Tuple[str, Optional[int]], ...] = ()
        injection_instance_rows: Tuple[Tuple[Any, ...], ...] = ()
        if self._injection_plan_phase9 is not None:
            injection_instance_keys = tuple(
                sorted(
                    self._injection_plan_phase9.instance_injections.keys(),
                    key=lambda key: (key[0], -1 if key[1] is None else key[1]),
                )
            )
            try:
                injection_instance_rows = self._build_injection_instance_rows(
                    self._injection_plan_phase9.instance_injections,
                )
            except AttributeError:
                injection_instance_rows = ()

        override_target_specs: Tuple[str, ...] = ()
        override_target_rows: Tuple[Tuple[Any, ...], ...] = ()
        if self._override_patch_map_phase10 is not None:
            override_target_specs = tuple(sorted(self._override_patch_map_phase10._targets_by_spec.keys()))
            override_target_rows = self._build_override_target_rows(
                self._override_patch_map_phase10,
            )

        mutation_target_specs: Tuple[str, ...] = ()
        mutation_target_rows: Tuple[Tuple[Any, ...], ...] = ()
        if self._mutation_patch_map_phase10 is not None:
            mutation_target_specs = tuple(sorted(self._mutation_patch_map_phase10._targets_by_spec.keys()))
            mutation_target_rows = self._build_mutation_target_rows(
                self._mutation_patch_map_phase10,
            )

        no_overrides_payload = self._build_phase11_variant_ir_payload(self._execution_plan_phase11_no_overrides)
        overrides_payload = self._build_phase11_variant_ir_payload(self._execution_plan_phase11_overrides)
        overrides_with_mutations_payload = self._build_phase11_variant_ir_payload(self._execution_plan_phase11)

        phase8_11_signature = self._hash_codegen_signature(
            occurrence_execution_order,
            occurrence_root_instance_key,
            occurrence_shared_spell_ids,
            occurrence_contract_complete,
            occurrence_graph_rows,
            occurrence_instance_key_rows,
            occurrence_canonical_rows,
            occurrence_contract_override_rows,
            occurrence_contract_override_spell_rows,
            injection_instance_keys,
            injection_instance_rows,
            override_target_specs,
            override_target_rows,
            mutation_target_specs,
            mutation_target_rows,
            no_overrides_payload["signature"],
            overrides_payload["signature"],
            overrides_with_mutations_payload["signature"],
        )

        phase8_11_payload = {
            "occurrence": {
                "execution_order": occurrence_execution_order,
                "root_instance_key": occurrence_root_instance_key,
                "shared_spell_ids": occurrence_shared_spell_ids,
                "contract_dependencies_complete": occurrence_contract_complete,
                "graph_rows": occurrence_graph_rows,
                "instance_key_rows": occurrence_instance_key_rows,
                "canonical_occurrence_rows": occurrence_canonical_rows,
                "contract_override_rows": occurrence_contract_override_rows,
                "contract_override_spell_rows": occurrence_contract_override_spell_rows,
            },
            "injection": {
                "instance_keys": injection_instance_keys,
                "instance_key_count": len(injection_instance_keys),
                "instance_rows": injection_instance_rows,
            },
            "patch_maps": {
                "override_target_specs": override_target_specs,
                "override_target_rows": override_target_rows,
                "mutation_target_specs": mutation_target_specs,
                "mutation_target_rows": mutation_target_rows,
            },
            "execution": {
                "no_overrides": no_overrides_payload,
                "overrides": overrides_payload,
                "overrides_with_mutations": overrides_with_mutations_payload,
            },
            "signature": phase8_11_signature,
        }

        ir_payload = self._ensure_codegen_ir()
        ir_payload["phase8_11"] = phase8_11_payload
        ir_payload["signatures"]["phase8_11"] = phase8_11_signature
        self._phase8_11_codegen_ir_dirty = False

    def _mark_phase8_11_codegen_ir_dirty(self) -> None:
        """
        Mark phase8_11 codegen export as stale.

        Purpose:
            Record that one or more Phase8-11 artifacts changed and a new IR
            export is required before consumers read phase8_11 payloads.
        Contract:
            - Idempotent; repeated calls keep dirty state true.
            - Does not mutate codegen payloads directly.
        Returns:
            None.
        """
        self._phase8_11_codegen_ir_dirty = True

    def _capture_phase8_11_codegen_ir_if_dirty(self) -> None:
        """
        Flush phase8_11 codegen export only when stale.

        Purpose:
            Avoid repeated full payload/signature rebuilds while preserving
            freshness for codegen-ir readers and any compile calls that consume
            exported phase8-11 payloads.
        Contract:
            - No-op when dirty flag is false.
            - Executes full `_capture_phase8_11_codegen_ir` once per dirty cycle.
        Returns:
            None.
        """
        if not self._phase8_11_codegen_ir_dirty:
            return
        self._capture_phase8_11_codegen_ir()

    def _compile_phase12_no_overrides_executor(self) -> None:
        """
        Compile and cache the spell-scoped Phase 12 no-overrides executor.

        Purpose:
            Consume exported Phase 11 IR and build the callable artifact used
            by CreationContext no-overrides fast paths.
        Contract:
            - Reuses existing executor when IR signature is unchanged.
            - Stores None when no compatible transient IR exists.
            - Never mutates Phase 11 plans.
        Returns:
            None.
        """
        if self._codegen_ir is None:
            self._compile_phase12_no_overrides_executor_from_payload(None)
            return

        phase8_11 = self._codegen_ir["phase8_11"]
        execution_payload = phase8_11.get("execution")
        if not execution_payload:
            self._compile_phase12_no_overrides_executor_from_payload(None)
            return

        no_overrides_payload = execution_payload.get("no_overrides")
        self._compile_phase12_no_overrides_executor_from_payload(no_overrides_payload)

    def _compile_phase12_no_overrides_executor_from_plan(
            self,
            plan: Optional[ExecutionPlan],
    ) -> None:
        """
        Compile/cache phase12 no-overrides executor from a Phase11 plan object.

        Purpose:
            Keep `run_phase_execution_plan` on a plan-based hot path so warm
            compile cache checks do not require building no-overrides IR payload
            dict rows.
        Contract:
            - Stores `None` executor/signature when plan is missing or empty.
            - Reuses existing executor when plan-derived signature is unchanged.
            - Raises when compilation fails for a non-empty plan.
        Args:
            plan:
                Phase11 no-overrides execution plan or `None`.
        Returns:
            None.
        """
        if plan is None or not plan.steps:
            self._phase12_no_overrides_executor = None
            self._phase12_no_overrides_executor_signature = None
            self._spell.resolution_complete = False
            return

        transient_schema = self._build_fast_transient_schema(plan.fast_transient_plan)
        plan_signature = self._build_phase12_no_overrides_plan_signature(
            plan=plan,
            transient_schema=transient_schema,
        )
        if (
                plan_signature == self._phase12_no_overrides_executor_signature
                and self._phase12_no_overrides_executor is not None
        ):
            self._spell.resolution_complete = True
            return

        compiled_executor = compile_phase12_no_overrides_executor_from_plan(
            plan=plan,
            transient_schema=transient_schema,
        )
        if len(plan.steps) > 0 and compiled_executor is None:
            raise RuntimeError(
                "Phase 12 no-overrides executor compilation failed for a non-empty plan."
            )
        self._phase12_no_overrides_executor = compiled_executor
        self._phase12_no_overrides_executor_signature = plan_signature
        self._spell.resolution_complete = True

    def _compile_phase12_no_overrides_executor_from_payload(
            self,
            no_overrides_payload: Optional[Dict[str, Any]],
    ) -> None:
        """
        Compile/cache phase12 no-overrides executor from a payload mapping.

        Purpose:
            Compile from exported phase8-11 payloads when codegen-ir readers
            trigger lazy capture or when payload-only compile paths are used.
        Contract:
            - Stores `None` executor/signature when payload is missing.
            - Reuses existing executor when payload signature is unchanged.
            - Raises on malformed payload shape for non-empty plans.
        Args:
            no_overrides_payload:
                Phase11 no-overrides payload dictionary or `None`.
        Returns:
            None.
        """
        if not no_overrides_payload:
            self._phase12_no_overrides_executor = None
            self._phase12_no_overrides_executor_signature = None
            self._spell.resolution_complete = False
            return

        required_payload_fields = (
            "signature",
            "step_count",
            "root_spell_id",
        )
        for field_name in required_payload_fields:
            if field_name not in no_overrides_payload:
                raise RuntimeError(
                    "Phase 12 no-overrides IR payload is missing required field "
                    f"'{field_name}'."
                )

        has_steps_rows = "steps_rows" in no_overrides_payload and bool(no_overrides_payload.get("steps_rows"))
        if not has_steps_rows:
            raise RuntimeError(
                "Phase 12 no-overrides IR payload must provide non-empty "
                "'steps_rows'."
            )

        payload_signature = no_overrides_payload["signature"]
        if (
                payload_signature == self._phase12_no_overrides_executor_signature
                and self._phase12_no_overrides_executor is not None
        ):
            self._spell.resolution_complete = True
            return

        compiled_executor = compile_phase12_no_overrides_executor(
            codegen_ir=no_overrides_payload,
            spell_lookup=self._spell._spellbook._spell_id_pool,
        )
        if no_overrides_payload.get("step_count", 0) > 0 and compiled_executor is None:
            raise RuntimeError(
                "Phase 12 no-overrides executor compilation failed for a non-empty plan."
            )
        self._phase12_no_overrides_executor = compiled_executor
        self._phase12_no_overrides_executor_signature = payload_signature
        self._spell.resolution_complete = True

    def _reset_phase2_5_codegen_ir(self) -> None:
        """
        Clear the phase2_5 segment from Codegen IR.

        Purpose:
            Keep IR aligned with lifecycle cleanup when structural artifacts are
            discarded.
        Contract:
            - No-op when IR is not initialized.
            - Preserves phase8_11 payloads and compiled executor artifacts.
        Returns:
            None.
        """
        if self._codegen_ir is None:
            return
        self._codegen_ir["phase2_5"] = {}
        self._codegen_ir["signatures"].pop("phase2_5", None)

    def _reset_phase8_11_codegen_ir(self) -> None:
        """
        Clear the phase8_11 segment from Codegen IR and Phase 12 artifacts.

        Purpose:
            Ensure runtime execution artifacts are invalidated whenever Phase 8+
            plans are cleared.
        Contract:
            - No-op when IR is not initialized.
            - Always clears compiled no-overrides executor cache.
            - Resets pending phase8_11 dirty state.
        Returns:
            None.
        """
        if self._codegen_ir is not None:
            self._codegen_ir["phase8_11"] = {}
            self._codegen_ir["signatures"].pop("phase8_11", None)
        self._phase8_11_codegen_ir_dirty = False
        self._phase12_no_overrides_executor = None
        self._phase12_no_overrides_executor_signature = None
        self._spell.resolution_complete = False
        self._phase8_occurrence_plan_input_signature = None
        self._phase8_occurrence_plan_fast_key = None
        self._phase9_injection_plan_input_signature = None
        self._phase10_patch_maps_input_signature = None
        self._phase11_no_overrides_input_signature = None
        self._phase11_no_overrides_fast_key = None


    def _notify_dependencies_updated(self, dependency_ids: List[str]) -> None:
        """
        Notify the SpellSystemStates registry that this spell's direct
        dependencies (by spell_id) have been updated.

        This is the Phase 3 -> system-state bridge:

        - It does *not* recompute anything itself.
        - It simply forwards the concrete dependency_ids that were pushed back
          into the owning Spell via ``_add_build_details(...)``.
        """
        # If this crafter has been cleaned, bail early; the manager may already
        # be torn down as part of frame cleanup.
        self.check_cleaned()

        if self._spell_system_states is None or self._spell.spell_index is None:
            return

        # SpellSystemStates.update_dependencies performs its own internal
        # gating and dirty-tracking based on this new edge set.
        self._spell_system_states.update_dependencies(self._spell.spell_index, dependency_ids or [])

    def _throw_if_cancelled(self, cancel_event: Optional[CancellationEvent]) -> None:
        """
        Helper that checks the cancellation token and throws if set.
        """
        if cancel_event is not None and cancel_event.is_set:
            cancel_event.throw_if_set()

    def _iter_all_spells(self):
        """
        Iterate all visible spells via the Spellbook's live spell_id_pool.

        Purpose:
            Provide a single internal iterator that Phase 3 can use for
            resolution without relying on any scanner wrapper.
        Contract:
            - Yields ``(spell_index, spell)`` in the insertion order of
              ``_spell_id_pool``.
            - Uses the Spellbook's live ``_spell_id_pool`` directly; no copies
              or snapshots are created.
        Returns:
            Iterator[Tuple[SpellIndex, ISpell]]: Live iteration stream.
        """
        spellbook = self._spell._spellbook
        for spell_instance in spellbook._spell_id_pool.values():
            yield spell_instance.spell_index, spell_instance

    def _normalize_annotation_for_matching(self, annotation: Any) -> Any:
        """
        Normalize a DI annotation for Phase 3 matching.

        This unwraps Optional/Union-with-None annotations and converts
        ForwardRef tokens into their string names so name-based matching
        can succeed for local forward references.

        Args:
            annotation:
                The raw annotation object from Phase 1.

        Returns:
            Any:
                The normalized annotation to use for matching.
        """
        if isinstance(annotation, typing.ForwardRef):
            return annotation.__forward_arg__

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin in (Union, types.UnionType) and args:
            non_none_args: List[Any] = []
            for arg in args:
                if isinstance(arg, typing.ForwardRef):
                    arg_value = arg.__forward_arg__
                else:
                    arg_value = arg
                if arg_value is type(None):
                    continue
                non_none_args.append(arg_value)

            if len(non_none_args) == 1:
                return non_none_args[0]

        return annotation

    def _matches_annotation(
            self,
            annotation: Any,
            binding_name: Optional[str],
            spell_obj: ISpell,
            *,
            require_class_spell: bool,
    ) -> bool:
        """
        Return True if ``spell_obj`` is a candidate for the given annotation.

        Matching rules (Phase 3 view):

          * Optional/Union annotations should be normalized before matching.
          * If the annotation is a string, match by spell name or frame name.
          * Then try concrete-class match: ``spell_obj.spell is annotation``.
          * Then try frame match: ``spell_obj.spellframe is/== annotation``.
          * If ``binding_name`` is not None, require an exact match.

        If ``require_class_spell`` is True, method / lambda style spells are
        excluded. This enforces the rule that *single* DI by plain type-hint
        only ever targets class/creation spells; method/lambda spells must be
        obtained explicitly via SpellMap or root-level meld.
        """
        # Filter out method / lambda style spells for "single" DI.
        if require_class_spell:
            spell_type = spell_obj.spell_type
            if spell_type in (
                    SpellType.METHOD,
                    SpellType.METHOD_WITH_BINDING_NAME,
                    SpellType.LAMBDA_METHOD_WITH_BINDING_NAME,
            ):
                return False

        if isinstance(annotation, typing.ForwardRef):
            annotation = annotation.__forward_arg__

        if isinstance(annotation, str):
            if spell_obj.spell_name == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            frame = spell_obj.spellframe
            if isinstance(frame, str) and frame == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

            if inspect.isclass(frame) and frame.__name__ == annotation:
                if binding_name is not None and spell_obj.binding_name != binding_name:
                    return False
                return True

        # Concrete class match.
        if spell_obj.spell is annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        # Frame / protocol / string-key match.
        frame = spell_obj.spellframe
        if frame is annotation or frame == annotation:
            if binding_name is not None and spell_obj.binding_name != binding_name:
                return False
            return True

        return False

    def _resolve_single_by_annotation(
            self,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SINGLE_BY_ANNOTATION dependency to exactly one class/creation
        spell.

        Returns:
            Dict[SpellIndex, ISpell]: mapping with **exactly one** entry.

        Raises:
            RuntimeError:
                If zero or multiple candidates are found.
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        # Parameter-level binding metadata does not exist yet; we only support
        # the default binding for now.
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells():
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=True,
            ):
                candidates[index] = spell_obj

        if not candidates:
            raise RuntimeError(
                f"SpellCrafter Phase 3: no DI candidate found for parameter "
                f"{dep.param_name!r} on spell {self._spell.spell_name!r} "
                f"(annotation={annotation!r})."
            )

        if len(candidates) > 1:
            # Ambiguous single DI - tell the user how to disambiguate.
            names = ", ".join(
                sorted(spell.spell_name for spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: multiple DI candidates found for "
                f"parameter {dep.param_name!r} on spell {self._spell.spell_name!r} "
                f"(annotation={annotation!r}). "
                f"Candidates: {names}. "
                "Use a SpellMap with an explicit spellframe/binding_name or a "
                "collection type (e.g. list[FrameType]) to inject multiple "
                "implementations."
            )

        return candidates

    def _resolve_collection_by_annotation(
            self,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a COLLECTION_BY_ANNOTATION dependency to **all** matching
        spells (classes, methods, lambdas) bound under the given frame/type.

        This corresponds to list[FrameType]-style DI where the user explicitly
        asked for "all implementations".

        Returns:
            Dict[SpellIndex, Spell]: mapping of all candidates. It is valid
            for this mapping to be empty (an empty collection will be injected).
        """
        annotation = self._normalize_annotation_for_matching(dep.target_annotation)
        binding_name: Optional[str] = None

        candidates: Dict[Any, ISpell] = {}

        for index, spell_obj in self._iter_all_spells():
            # For collection DI we deliberately allow methods/lambdas - the
            # frame is the grouping mechanism.
            if self._matches_annotation(
                    annotation,
                    binding_name,
                    spell_obj,
                    require_class_spell=False,
            ):
                candidates[index] = spell_obj

        return candidates

    def _socket_kind_for_dep(self, dep: SpellSymbolicDependency) -> SocketKind:
        """
        Map a symbolic dependency's DI shape into a SocketKind.

        NORMAL:
            Regular DI parameter (annotation, SpellMap, collection) or a
            plain constructor socket.
        SPELL_CONTRACT:
            SpellContract socket - must be satisfied by a provider.
        MUTATION_CONTRACT:
            MutationContract socket - can be rewired at meld-time.

        For now we classify based solely on `dep.di_shape`. If we later
        introduce additional DI shapes, this is the central mapping point.
        """
        di_shape = dep.di_shape

        if di_shape is ParameterDIShape.SPELL_CONTRACT:
            return SocketKind.SPELL_CONTRACT
        if di_shape is ParameterDIShape.MUTATION_CONTRACT:
            return SocketKind.MUTATION_CONTRACT

        return SocketKind.NORMAL

    def _dependency_key_for_dep(
            self,
            dep: SpellSymbolicDependency,
    ) -> Optional[Tuple[str, str]]:
        """
        Internal

        Resolve the canonical dependency key for a NORMAL DI socket.

        For SpellMap defaults, this uses the SpellMap's canonical key.
        For annotation-driven shapes (single/collection), this normalizes
        the frame key from the target annotation using the default binding.

        Args:
            dep: Symbolic dependency being mapped.
        Returns:
            Optional[Tuple[str, str]]: The normalized (frame_key, binding_key),
            or None if the dependency does not participate in DI keying.
        """
        if dep is None:
            return None

        if dep.di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
            spellmap = dep.spellmap_default
            if spellmap is None:
                return None
            return spellmap.canonical_key

        if dep.di_shape in (
            ParameterDIShape.SINGLE_BY_ANNOTATION,
            ParameterDIShape.COLLECTION_BY_ANNOTATION,
        ):
            if dep.target_annotation is None:
                return None
            return SpellInputUtils.normalize_spell_key(
                spellframe=dep.target_annotation,
                binding_name=None,
            )

        return None

    def _resolve_spellmap_default(
            self,
            dep: SpellSymbolicDependency,
    ) -> Dict[Any, ISpell]:
        """
        Resolve a SPELLMAP_DEFAULT dependency using the original SpellMap
        default attached to the parameter.

        SpellMap defaults are **explicit** - they may point at classes,
        methods, lambdas, or frame+binding pairs. We honour the user's
        intent exactly and still enforce uniqueness.
        """
        spellmap = dep.spellmap_default
        if spellmap is None:
            return {}

        candidates: Dict[Any, ISpell] = {}

        # If the SpellMap carries an explicit spell callable/class, that wins.
        explicit_spell = spellmap.spell
        frame = spellmap.spellframe
        binding_name = spellmap.binding_name

        if explicit_spell is not None:
            for index, spell_obj in self._iter_all_spells():
                if spell_obj.spell is not explicit_spell:
                    continue

                # Optional frame/binding_name refinement.
                if frame is not None:
                    spell_frame = spell_obj.spellframe
                    if not (spell_frame is frame or spell_frame == frame):
                        continue

                if binding_name is not None and spell_obj.binding_name != binding_name:
                    continue

                candidates[index] = spell_obj
        else:
            # Frame+binding only - scan all visible spells for matches.
            for index, spell_obj in self._iter_all_spells():
                if spell_obj.spellframe is spellmap.spellframe or spell_obj.spellframe == spellmap.spellframe:
                    if spell_obj.binding_name == spellmap.binding_name:
                        candidates[index] = spell_obj

        if not candidates:
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default could not be resolved for "
                f"parameter {dep.param_name!r} on spell {self._spell.spell_name!r}. "
                f"SpellMap={spellmap!r}."
            )

        if len(candidates) > 1:
            names = ", ".join(
                sorted(spell.spell_name for spell in candidates.values())
            )
            raise RuntimeError(
                "SpellCrafter Phase 3: SpellMap default resolved to multiple "
                f"candidates for parameter {dep.param_name!r} on spell "
                f"{self._spell.spell_name!r}. Candidates: {names}. "
                "SpellMap defaults must be unambiguous."
            )

        return candidates

    # ------------------------------------------------------------------
    # Phase 1 - Requirements
    # ------------------------------------------------------------------

    def run_phase_requirements(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 1 - Analyse the Spell constructor and capture DI requirements.

        Responsibilities:
            * Inspect the bound Spell's constructor and classify every parameter
              into a :class:`ParameterDIShape` (normal DI, SpellMap, contracts, etc.).
            * Build a :class:`SpellRequirements` object that records per-parameter
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
            * Does not return a value; consumers read ``self._requirements``.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is not None:
            return

        finder = SpellRequirementsFinder(self._spell)
        requirements = finder.build_requirements(cancel_event=cancel_event)
        # We deliberately do not call finder.cleanup() here, because the finder
        # owns the same SpellRequirements instance we are going to retain.
        self._requirements = requirements

    # ------------------------------------------------------------------
    # Phase 2 - Symbolic Graph
    # ------------------------------------------------------------------

    def run_phase_symbolic_graph(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 2 - Build the symbolic dependency graph for this Spell.

        Responsibilities:
            * Consume Phase 1 requirements and construct a
              :class:`SpellSymbolicGraph` describing all constructor sockets.
            * Create one :class:`SpellSymbolicDependency` per constructor
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
            * Does not return a value; consumers read ``self._symbolic_graph``.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is None:
            raise RuntimeError(
                "SpellCrafter Phase 2: cannot build symbolic graph before "
                "Phase 1 requirements have completed."
            )

        # Versioned identity from SpellIndex.
        version_id: str = self._spell.spell_index.current

        deps: List[SpellSymbolicDependency] = []

        for param in self._requirements.parameters:
            di_shape: ParameterDIShape = param.di_shape
            contract_key = None
            contract_late_binding = None

            # Only shapes that participate in the symbolic socket graph.
            if di_shape not in (
                    ParameterDIShape.SINGLE_BY_ANNOTATION,
                    ParameterDIShape.COLLECTION_BY_ANNOTATION,
                    ParameterDIShape.SPELLMAP_DEFAULT,
                    ParameterDIShape.PLAIN,
                    ParameterDIShape.SPELL_CONTRACT,
                    ParameterDIShape.MUTATION_CONTRACT,
            ):
                # Shapes like IGNORE do not participate in sockets.
                continue

            # Map shape -> symbolic metadata.
            if di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                target_annotation = None
                is_collection = False
                spellmap_default = param.spellmap_default

            elif di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                target_annotation = param.collection_element_annotation
                is_collection = True
                spellmap_default = None

            elif di_shape is ParameterDIShape.PLAIN:
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None

            elif di_shape is ParameterDIShape.SPELL_CONTRACT:
                # Contract socket.
                #
                # For now we reuse the raw annotation as the "target" so that
                # later phases (5-7) can infer what this contract is over,
                # without committing to any specific resolution semantics yet.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
                if isinstance(param.default_value, SpellContract):
                    contract_key = param.default_value.canonical_key

            elif di_shape is ParameterDIShape.MUTATION_CONTRACT:
                # Mutation socket.
                #
                # Same approach as SPELL_CONTRACT: we record the socket +
                # annotation so that later contract/mutation logic (early vs
                # late binding, _mutation_overrides, etc.) has visibility.
                target_annotation = param.annotation
                is_collection = False
                spellmap_default = None
                if isinstance(param.default_value, MutationContract):
                    contract_key = param.default_value.canonical_key
                    contract_late_binding = param.default_value.late_binding

            else:
                # Should not happen given the filter above, but kept for
                # robustness.
                continue

            dep = SpellSymbolicDependency(
                spell_version_id=version_id,
                param_name=param.name,
                position=param.position,
                di_shape=di_shape,
                is_optional=param.is_optional,
                target_annotation=target_annotation,
                is_collection=is_collection,
                spellmap_default=spellmap_default,
                contract_key=contract_key,
                contract_late_binding=contract_late_binding,
            )
            deps.append(dep)

        self._symbolic_graph = SpellSymbolicGraph(
            spell_version_id=version_id,
            dependencies=deps,
        )
        self._capture_phase2_5_codegen_ir()


    # ------------------------------------------------------------------
    # Phase 3 - Local Frame / DAG
    # ------------------------------------------------------------------
    def _build_local_topology(
            self,
            graph: SpellSymbolicGraph,
            socket_targets: Dict[tuple[str, int], List[str]],
    ) -> SpellLocalTopology:
        """
        Internal helper for Phase 3.

        Construct a :class:`SpellLocalTopology` describing this Spell's
        constructor sockets, based on:

            * the symbolic dependencies from :class:`SpellSymbolicGraph`, and
            * the concrete dependency spell ids resolved during Phase 3.

        For each :class:`SpellSymbolicDependency`:
            * Determine ``socket_kind`` from its :class:`ParameterDIShape`.
            * Copy ``is_collection`` and ``is_optional`` flags from the
              symbolic graph.
            * Look up any concrete targets via ``socket_targets`` using
                ``(param_name, position)``. Normal DI sockets may have one or
                many targets; contract, mutation, and plain sockets will
                typically have none at this phase.
            * Preserve contract metadata for SpellContract / MutationContract
              sockets (canonical key, late-binding flag).
            * Create a :class:`SpellSocketDescriptor` for that parameter.

        The resulting :class:`SpellLocalTopology` is a per-spell, constructor-
        local view of sockets that later phases (blueprint assembly, override
        targeting, change-control) will consume. It is registered into
        :class:`SpellSystemStates` by Phase 3; this method does not talk to
        SpellSystemStates directly.
        """
        self.check_cleaned()

        if self._spell is None or self._spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        spell_id = self._spell.spell_index.current
        descriptors: List[SpellSocketDescriptor] = []

        for dep in graph.dependencies:
            key = (dep.param_name, dep.position)
            targets = socket_targets.get(key)
            if targets:
                target_spell_ids = tuple(targets)
            else:
                target_spell_ids = ()

            socket_kind = self._socket_kind_for_dep(dep)

            dependency_key = None
            if socket_kind is SocketKind.NORMAL:
                dependency_key = self._dependency_key_for_dep(dep)

            descriptor = SpellSocketDescriptor(
                  spell_id=spell_id,
                  param_name=dep.param_name,
                  position=dep.position,
                  socket_kind=socket_kind,
                  is_collection=dep.is_collection,
                  is_optional=dep.is_optional,
                  target_spell_ids=target_spell_ids,
                  dependency_key=dependency_key,
                  contract_key=dep.contract_key,
                  contract_late_binding=dep.contract_late_binding,
            )
            descriptors.append(descriptor)

        topology = SpellLocalTopology(
            spell_id=spell_id,
            sockets=descriptors,
        )
        return topology


    def _build_local_frame_dag(
            self,
            requirements: SpellRequirements,
            graph: SpellSymbolicGraph,
            cancellation_event: CancellationEvent,
            *,
            return_dependencies: bool = False,
    ) -> Union[DirectedAcyclicWorkGraph, Tuple[DirectedAcyclicWorkGraph, List[str]]]:
        """
        Internal helper for Phase 3.

        Build the concrete DAG for this Spell's **local frame** and emit
        constructor topology into SpellSystemStates.

        Responsibilities:
            * Add a DAG node for the root Spell (current SpellIndex version).
            * For each symbolic dependency:
                  - resolve normal DI shapes via direct Spellbook map iteration,
                  - add DAG nodes for resolved dependency spells,
                  - add edges from each dependency node to the root node,
                    tagging edges with ``param_name`` and ``socket_kind``.
            * Track, per constructor socket ``(param_name, position)``, the
              concrete dependency spell ids resolved in this phase.
            * Build a :class:`SpellLocalTopology` from the symbolic graph plus
              the per-socket targets.
            * Call into :class:`SpellSystemStates` to:
                  - record direct dependency spell ids, and
                  - register the local topology for this Spell.

        Important:
            * This helper does **not** mutate the Spell object. All artifacts
              (DAG, topology, dependency ids) remain in this SpellCrafter and
              SpellSystemStates.
            * If ``return_dependencies`` is True, returns a tuple of
              ``(dag, dependency_spell_ids)``; otherwise returns only the DAG.
            * SpellContract and MutationContract sockets take part in the
              symbolic graph and topology, but do not produce DAG edges or
              concrete targets at this stage.
        """
        self.check_cleaned()

        if requirements is None:
            raise ValueError("requirements must not be None.")
        if graph is None:
            raise ValueError("graph must not be None.")

        self._throw_if_cancelled(cancellation_event)

        if self._spell is None or self._spell.spell_index is None:
            raise RuntimeError("SpellCrafter has no bound Spell with a SpellIndex.")

        root_id = self._spell.spell_index.current
        dag = DirectedAcyclicWorkGraph()

        # Register the root node first.
        dag.add_node(key=root_id, payload=self._spell)

        # Track all dependency spell IDs for SpellSystemStates.
        dependency_spell_ids: List[str] = []

        # Track per-socket resolutions for local topology:
        # keyed by (param_name, position) -> [spell_id, ...]
        socket_targets: Dict[tuple[str, int], List[str]] = {}

        for dep in graph.dependencies:
            self._throw_if_cancelled(cancellation_event)

            di_shape = dep.di_shape

            # Only "normal" DI shapes produce concrete DAG edges for now.
            if di_shape is ParameterDIShape.SINGLE_BY_ANNOTATION:
                resolved = self._resolve_single_by_annotation(dep=dep)
            elif di_shape is ParameterDIShape.COLLECTION_BY_ANNOTATION:
                resolved = self._resolve_collection_by_annotation(dep=dep)
            elif di_shape is ParameterDIShape.SPELLMAP_DEFAULT:
                resolved = self._resolve_spellmap_default(dep=dep)
            else:
                # SpellContract / MutationContract / PLAIN and any future shapes
                # are currently metadata-only at the DAG level. They still
                # participate in local topology below.
                resolved = {}

            if not resolved:
                continue

            key = (dep.param_name, dep.position)
            targets_for_socket = socket_targets.setdefault(key, [])

            for spell_index, spell_obj in resolved.items():
                dep_spell_id = spell_index.current
                dependency_spell_ids.append(dep_spell_id)
                targets_for_socket.append(dep_spell_id)

                dag.add_node(key=dep_spell_id, payload=spell_obj)
                dag.add_dependency(
                    parent_key=dep_spell_id,
                    child_key=root_id,
                    param_name=dep.param_name,
                    socket_kind=self._socket_kind_for_dep(dep),
                )

        # Snapshot local topology for this spell's constructor.
        topology = self._build_local_topology(graph, socket_targets)

        # Update spell-system state with dependency IDs and local topology.
        if self._spell_system_states is not None and self._spell.spell_index is not None:
            self._spell_system_states.update_dependencies(
                self._spell.spell_index,
                dependency_spell_ids,
            )
            self._spell_system_states.register_local_topology(
                self._spell.spell_index,
                topology,
            )

        if return_dependencies:
            return dag, dependency_spell_ids

        return dag


    # ------------------------------------------------------------------
    # Phase 3 - Local frame / DAG
    # ------------------------------------------------------------------

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
            * Build a :class:`SpellLocalTopology` snapshot that describes all
              sockets (normal, SpellContract, MutationContract) and their
              concrete targets where applicable.
            * Register both:
                  - direct dependency spell ids, and
                  - the local topology
              into :class:`SpellSystemStates`.

        Socket semantics:
            * Normal DI shapes (single, collection, SpellMap) produce DAG nodes,
              DAG edges, and concrete ``target_spell_ids`` entries in topology.
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
            * Stores the local DAG and direct dependency list on the Spell via
              :meth:`Spell._add_build_details`, and keeps a
              :class:`SpellResolutionFrame` internally on this SpellCrafter.
            * Does not return a value; callers rely on:
                  - ``self._resolution_frame`` for ordering, and
                  - SpellSystemStates for dependencies and topology.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        if self._requirements is None or self._symbolic_graph is None:
            raise RuntimeError(
                "SpellCrafter Phase 3: cannot build local frame before "
                "Phases 1-2 have completed."
            )


        dag, dependency_spell_ids = self._build_local_frame_dag(
            requirements=self._requirements,
            graph=self._symbolic_graph,
            cancellation_event=cancel_event,
            return_dependencies=True,
        )

        # Topological order of node ids (deps first, then root).
        ordered_node_ids = dag.collect_dependency_ids()

        self._resolution_frame  = SpellResolutionFrame(
            spell_id=self._spell.spell_index.current,
            ordered_node_ids=ordered_node_ids,
        )

        # Persist dependency metadata on the Spell for validation and contract linking.
        unique_dependencies = list(dict.fromkeys(dependency_spell_ids))
        try:
            self._spell._add_build_details(
                dag=dag,
                dependencies=unique_dependencies,
            )
        except AttributeError:
            # Test stubs may not implement the build-details hook.
            pass
        self._capture_phase2_5_codegen_ir()

    # ------------------------------------------------------------------
    # Phase 4 - Validation
    # ------------------------------------------------------------------

    def run_phase_validation(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 4 - Per-spell validation using SpellValidationSystem.

        Responsibilities:
            * Assume Phases 1-3 have completed for this Spell.
            * Delegate to :class:`SpellValidationSystem` to validate this spell
              using:
                  - Phase 1 requirements,
                  - Phase 2 symbolic graph,
                  - Phase 3 resolution frame.
            * Cache the resulting :class:`SpellValidationResult` and expose it
              via :attr:`validation_result`, :attr:`validated`,
              and :attr:`is_broken`.
            * Update global structural validity (SpellSystemState) when available,
              including gating spells with missing SpellContract providers.

        Contracts:
            * Does **not** call Phases 1-3. If any of the required artifacts
              are missing, this method raises.
            * Does **not** mutate the Spell or build any DAGs. It only records
              validation outcome and diagnostics on this SpellCrafter.
            * If the SpellSystemState is no longer valid (unknown/gated/invalid),
              the validation is re-run even if this phase previously completed.
            * Returns ``None``; callers rely on the stored validation result and
              flags instead of a direct return value.
        """
        self.check_cleaned()
        self._throw_if_cancelled(cancel_event)

        # If we've already validated and the structural state is still valid, do nothing.
        if self._validated_phase4 and self._validation_result_phase4 is not None:
            if self._spell_system_states is not None and self._spell.spell_index is not None:
                state = self._spell_system_states.get_by_index_id(self._spell.spell_index.id)
                if state is None or state.validity is SpellValidity.valid:
                    return
            else:
                return

        # Hard contract: Phases 1-3 must have been run explicitly.
        if (
                self._requirements is None
                or self._symbolic_graph is None
                or self._resolution_frame is None
        ):
            raise RuntimeError(
                "SpellCrafter Phase 4: cannot run validation before Phases 1-3 "
                "have completed."
            )

        # Use the Spellbook-level SpellValidationSystem.
        result = self._spell_validator.validate_spell(
            spell=self._spell,
            requirements=self._requirements,
            symbolic_graph=self._symbolic_graph,
            resolution_frame=self._resolution_frame,
            cancel_event=cancel_event,
        )

        # Cache result + flags on the crafter; the Spell exposes these via
        # properties (validation_result / validated / is_broken).
        self._validation_result_phase4 = result
        self._validated_phase4 = True

        # For now: any error -> broken. You can refine this later via severity.
        self._is_broken = result.has_errors
        has_contract_missing_provider = False
        for issue in result.issues:
            if issue.code == "SPELL_CONTRACT_MISSING_PROVIDER":
                has_contract_missing_provider = True
                break

        # Update global structural validity for this lineage.
        if self._spell_system_states is not None and self._spell.spell_index is not None:
            state = self._spell_system_states.get_by_index_id(self._spell.spell_index.id)
            if state is not None:
                if self._is_broken:
                    state.set_validity(
                        SpellValidity.invalid,
                        change_reason=SpellStateChangeReason.validation_failed,
                    )
                else:
                    state.clear_dirty(time.time())
                    if has_contract_missing_provider:
                        state.set_validity(
                            SpellValidity.gated,
                            change_reason=SpellStateChangeReason.contract_unvalidated,
                            flags_to_add=[SpellState.contract_unvalidated],
                        )
                    else:
                        state.set_validity(
                            SpellValidity.valid,
                            change_reason=SpellStateChangeReason.validation_passed,
                            flags_to_remove=[SpellState.contract_unvalidated],
                        )
        self._capture_phase2_5_codegen_ir()

    # ------------------------------------------------------------------
    # Phase 5 - Build Deep Dag Structures
    # ------------------------------------------------------------------

    def run_phase_root_blueprints(
            self,
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
            - The change-control component-of map is rebuilt from **owned** roots
              only, so contracted roots are not revalidated by this conduit.

        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation handle.

        Returns:
            None.
        """
        self.check_cleaned()

        # --- 1. Build adjacency snapshot from system states ----------------
        adjacency_builder = SpellSystemAdjacencyBuilder()
        snapshot = adjacency_builder.build(self._spell_system_states)

        # --- 2. Filter to spellbook-visible spells -------------------------
        # Use the live spell_id_pool (no copies) for version-id -> Spell lookup.
        spellbook = self._spell._spellbook
        visible_spell_ids = spellbook._spell_id_pool.keys()

        filtered_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids=visible_spell_ids,
        )

        # --- 3. Build deep DAGs for visible roots --------------------------
        root_builder = SpellSystemRootBlueprintBuilder()
        root_blueprints = root_builder.build_root_blueprints(filtered_snapshot)

        # --- 4. Construct system-level index -------------------------------
        system_index = SpellSystemIndex()

        for spell_id, deps in filtered_snapshot.dependencies.items():
            state = self._spell_system_states.get_by_spell_id(spell_id)
            lineage_id: str = state.spell_index_id
            spell_instance = spellbook._spell_id_pool[spell_id]

            node = SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=deps,
                existence=spell_instance.existence,
                spell_type=spell_instance.spell_type,
                conduit_id=spell_instance._owner_conduit_id,
                ward_id=None,
                is_root=spell_id in filtered_snapshot.root_spell_ids,
            )

            system_index.upsert_node(node)

        # --- 5. Attach artifacts to SpellCrafters -------------------------
        for spell_id, spell_instance in spellbook._spell_id_pool.items():
            crafter_for_spell = spell_instance._ensure_crafter()

            crafter_for_spell.set_spell_system_index_phase5(system_index)

            if spell_instance.is_existing_creation:
                # Existing-creation spells do not require execution plans.
                continue

            blueprint = root_blueprints.get(spell_id)
            if blueprint is None:
                blueprint = root_builder.build_blueprint_for_spell_id(
                    root_spell_id=spell_id,
                    snapshot=filtered_snapshot,
                )

            crafter_for_spell.set_root_blueprint_phase5(blueprint)

        # --- 6. Store artifacts on self for completeness -------------------
        # The root-only blueprint map is retained for system validation; per-spell
        # blueprints are attached directly to each SpellCrafter above.
        self._spell_system_index_phase5 = system_index
        self._entire_dag_blueprint_phase5 = root_blueprints
        self._capture_phase2_5_codegen_ir()
        self._reset_phase8_11_codegen_ir()

        # Rebuild component-of index and register a revalidation hook for dirty roots.
        frame_name = spellbook._aetheric_frame
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = self._filter_root_blueprints_to_owned(root_blueprints)
        change_control_manager.rebuild_component_of(conduit_id, owned_root_blueprints)

        def _revalidate_dirty_roots(
                dirty_roots: Set[str],
                cancel_event: Optional[CancellationEvent],
        ) -> Set[str]:
            """
            Revalidate the supplied dirty roots for this conduit.

            This closure is the Phase 5 bridge back into the change-control
            manager. When a conduit marks owned roots dirty, the frame-level
            change-control layer calls this hook with the affected root spell
            ids so each root can rebuild its structural and foundational
            resolution artifacts in the context of the same conduit.

            Contract:
                - Resolves each root spell from the live Spellbook
                  `_spell_id_pool`.
                - Reuses the spell-owned `SpellCrafter` for that root.
                - Runs `run_all_phases(...)` through the foundational phase set
                  needed for dirty-root recovery.
                - Returns only the subset of root ids that completed
                  revalidation successfully.

            Returns:
                Set[str]:
                    Root ids that successfully revalidated for this conduit.
            """
            validated_roots: Set[str] = set()
            for root_id in dirty_roots:
                spell_instance = spellbook._spell_id_pool[root_id]
                crafter = spell_instance._ensure_crafter()
                crafter.run_all_phases(conduit_id=conduit_id, cancel_event=cancel_event)
                validated_roots.add(root_id)

            return validated_roots

        change_control_manager.set_revalidator(conduit_id, _revalidate_dirty_roots)

    def _collect_local_scope_spell_ids(
            self,
            *,
            root_spell_id: str,
            snapshot: SpellSystemAdjacencySnapshot,
    ) -> Set[str]:
        """
        Collect dependency-closure spell ids for local Phase 5-7 execution.

        Purpose:
            Limit local resolution phases to the target spell and all spells it
            depends on directly or transitively.
        Contract:
            - Traverses dependency edges from root to leaves.
            - Returns only ids present in the provided snapshot.
            - Never mutates the snapshot.
        Args:
            root_spell_id:
                Target spell id whose dependency closure should be resolved.
            snapshot:
                Visibility-filtered adjacency snapshot.
        Returns:
            Set[str]:
                Target spell id plus dependency closure.
        """
        self.check_cleaned()
        if root_spell_id not in snapshot.all_spell_ids:
            return set()

        scoped_spell_ids: Set[str] = set()
        pending: List[str] = [root_spell_id]

        while pending:
            spell_id = pending.pop()
            if spell_id in scoped_spell_ids:
                continue
            if spell_id not in snapshot.all_spell_ids:
                continue
            scoped_spell_ids.add(spell_id)
            for dependency_id in snapshot.dependencies.get(spell_id, ()):
                if dependency_id not in scoped_spell_ids:
                    pending.append(dependency_id)

        return scoped_spell_ids

    def _build_system_index_for_snapshot(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            spell_lookup: Dict[str, ISpell],
    ) -> SpellSystemIndex:
        """
        Build a SpellSystemIndex for a pre-filtered adjacency snapshot.

        Purpose:
            Share index construction between frame-wide and local Phase 5 paths.
        Contract:
            - Requires every snapshot spell id to be present in spell_lookup.
            - Resolves lineage ids from SpellSystemStates.
            - Does not mutate snapshot or spell_lookup.
        Args:
            snapshot:
                Snapshot to materialize into an index.
            spell_lookup:
                Visible spell_id -> spell map.
        Returns:
            SpellSystemIndex:
                Index populated for all snapshot spell ids.
        """
        self.check_cleaned()
        system_index = SpellSystemIndex()
        for spell_id, deps in snapshot.dependencies.items():
            state = self._spell_system_states.get_by_spell_id(spell_id)
            lineage_id = state.spell_index_id
            spell_instance = spell_lookup[spell_id]

            node = SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=deps,
                existence=spell_instance.existence,
                spell_type=spell_instance.spell_type,
                conduit_id=spell_instance._owner_conduit_id,
                ward_id=None,
                is_root=spell_id in snapshot.root_spell_ids,
            )
            system_index.upsert_node(node)

        return system_index

    def _attach_phase5_artifacts_for_snapshot(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            root_blueprints: Dict[str, RootResolutionBlueprint],
            system_index: SpellSystemIndex,
            spell_lookup: Dict[str, ISpell],
            root_builder: SpellSystemRootBlueprintBuilder,
    ) -> None:
        """
        Attach Phase 5 artifacts to all spells participating in a snapshot.

        Purpose:
            Ensure scoped spells have consistent Phase 5 artifacts before
            Phase 6-11 are executed.
        Contract:
            - Updates only spells included in snapshot.all_spell_ids.
            - Existing-creation spells get index only and skip blueprints.
            - Builds fallback per-spell blueprint when not present as a root.
        Args:
            snapshot:
                Scoped adjacency snapshot.
            root_blueprints:
                Root blueprint map produced for this snapshot.
            system_index:
                System index for this snapshot.
            spell_lookup:
                Visible spell_id -> spell map.
            root_builder:
                Builder used for per-spell fallback blueprints.
        Returns:
            None.
        """
        self.check_cleaned()
        for spell_id in snapshot.all_spell_ids:
            spell_instance = spell_lookup[spell_id]
            crafter_for_spell = spell_instance._ensure_crafter()
            crafter_for_spell.set_spell_system_index_phase5(system_index)

            if spell_instance.is_existing_creation:
                continue

            blueprint = root_blueprints.get(spell_id)
            if blueprint is None:
                blueprint = root_builder.build_blueprint_for_spell_id(
                    root_spell_id=spell_id,
                    snapshot=snapshot,
                )
            crafter_for_spell.set_root_blueprint_phase5(blueprint)

    def run_phase_root_blueprints_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 5 local entrypoint.

        Purpose:
            Build Phase 5 artifacts for only the target spell and its
            transitive dependency closure so meld-triggered revalidation
            does not recompile unrelated spells.
        Contract:
            - Uses the same builders and invariants as frame-wide Phase 5.
            - Scope is limited to target spell dependency closure.
            - Attaches index/blueprints only to scoped spells.
            - Updates this crafter's Phase 5 caches with local artifacts.
        Args:
            conduit_id:
                Conduit identifier used to scope resolution artifacts.
            cancel_event:
                Optional cancellation handle.
        Returns:
            None.
        """
        self.check_cleaned()
        target_spell_id = self._spell.spell_index.current

        adjacency_builder = SpellSystemAdjacencyBuilder()
        snapshot = adjacency_builder.build(self._spell_system_states)

        spellbook = self._spell._spellbook
        spell_lookup = spellbook._spell_id_pool
        visible_spell_ids = spell_lookup.keys()
        visible_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=snapshot,
            visible_spell_ids=visible_spell_ids,
        )

        scoped_spell_ids = self._collect_local_scope_spell_ids(
            root_spell_id=target_spell_id,
            snapshot=visible_snapshot,
        )
        scoped_snapshot = self._filter_snapshot_to_visible_spells(
            snapshot=visible_snapshot,
            visible_spell_ids=scoped_spell_ids,
        )

        root_builder = SpellSystemRootBlueprintBuilder()
        local_root_blueprints = root_builder.build_root_blueprints(scoped_snapshot)
        system_index = self._build_system_index_for_snapshot(
            snapshot=scoped_snapshot,
            spell_lookup=spell_lookup,
        )
        self._attach_phase5_artifacts_for_snapshot(
            snapshot=scoped_snapshot,
            root_blueprints=local_root_blueprints,
            system_index=system_index,
            spell_lookup=spell_lookup,
            root_builder=root_builder,
        )

        self._spell_system_index_phase5 = system_index
        self._entire_dag_blueprint_phase5 = local_root_blueprints
        self._capture_phase2_5_codegen_ir()
        self._reset_phase8_11_codegen_ir()

    def _filter_snapshot_to_visible_spells(
            self,
            *,
            snapshot: SpellSystemAdjacencySnapshot,
            visible_spell_ids: Collection[str],
    ) -> SpellSystemAdjacencySnapshot:
        """
        Internal

        Filter a frame-wide adjacency snapshot to spells visible in this Spellbook.

        Purpose:
            Ensure Phase-5/6 validation only considers spells that the current
            Spellbook can resolve (local + contracted).
        Contract:
            - Dependency sets are referenced directly from the adjacency view.
            - Reverse edges and root spell ids are recomputed using visible spell ids.
            - Topologies are retained only for visible spell ids.
        Args:
            snapshot:
                Frame-wide SpellSystemAdjacencySnapshot to filter.
            visible_spell_ids:
                Version ids visible to this Spellbook. This collection is treated
                as a live view and is not copied.
        Returns:
            SpellSystemAdjacencySnapshot:
                A filtered snapshot scoped to the provided spell ids.
        """
        self.check_cleaned()
        all_spell_ids: Collection[str] = visible_spell_ids
        dependencies: Dict[str, Set[str]] = {}
        reverse_dependencies: Dict[str, Set[str]] = {}
        topologies: Dict[str, "SpellLocalTopology"] = {}

        for spell_id in all_spell_ids:
            deps = snapshot.dependencies.get(spell_id, set())
            filtered_deps = {dep_id for dep_id in deps if dep_id in all_spell_ids}
            dependencies[spell_id] = filtered_deps
            for dep_id in filtered_deps:
                reverse_dependencies.setdefault(dep_id, set()).add(spell_id)

            topology = snapshot.topologies.get(spell_id)
            if topology is not None:
                topologies[spell_id] = topology

        root_spell_ids = {spell_id for spell_id in all_spell_ids if spell_id not in reverse_dependencies}

        return SpellSystemAdjacencySnapshot(
            dependencies=dependencies,
            reverse_dependencies=reverse_dependencies,
            all_spell_ids=all_spell_ids,
            root_spell_ids=root_spell_ids,
            topologies=topologies,
        )

    def _filter_root_blueprints_to_owned(
            self,
            root_blueprints: Dict[str, RootResolutionBlueprint],
    ) -> Dict[str, RootResolutionBlueprint]:
        """
        Internal

        Filter root blueprints to owned spell ids only.

        Purpose:
            Limit component-of rebuilds to spell ids owned by this Spellbook
            while still allowing contracted spells to appear as dependencies
            under owned roots.
        Contract:
            - Returns a new mapping containing only roots present in
              `spellbook._spells_by_id`.
            - Does not mutate the provided root_blueprints mapping.
        Args:
            root_blueprints:
                Mapping of root spell_id to RootResolutionBlueprint.
        Returns:
            Dict[str, RootResolutionBlueprint]:
                Filtered mapping containing only owned roots.
        """
        self.check_cleaned()
        spellbook = self._spell._spellbook
        owned_spell_ids = spellbook._spells_by_id.keys()
        return {
            root_id: blueprint
            for root_id, blueprint in root_blueprints.items()
            if root_id in owned_spell_ids
        }


    # ------------------------------------------------------------------
    # Phase 8 - Occurrence Plan
    # ------------------------------------------------------------------

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
        self.check_cleaned()
        if self._spell.is_existing_creation:
            return
        root_blueprint = self._root_blueprint_phase5
        spell_lookup = self._spell._spellbook._spell_id_pool
        phase8_occurrence_plan_fast_key = self._build_phase8_occurrence_plan_fast_key(
            root_blueprint=root_blueprint,
            spell_lookup=spell_lookup,
        )
        can_reuse_phase8_signature_fast_key = (
            phase8_occurrence_plan_fast_key is not None
            and self._phase8_occurrence_plan_fast_key == phase8_occurrence_plan_fast_key
            and self._phase8_occurrence_plan_input_signature is not None
        )
        if can_reuse_phase8_signature_fast_key:
            occurrence_plan_input_signature = self._phase8_occurrence_plan_input_signature
        else:
            occurrence_plan_input_signature = self._build_phase8_occurrence_plan_input_signature(
                root_blueprint=root_blueprint,
                spell_lookup=spell_lookup,
            )
        if phase8_occurrence_plan_fast_key is not None:
            self._phase8_occurrence_plan_fast_key = phase8_occurrence_plan_fast_key
        else:
            self._phase8_occurrence_plan_fast_key = None
        if (
                occurrence_plan_input_signature is not None
                and occurrence_plan_input_signature == self._phase8_occurrence_plan_input_signature
                and self._occurrence_plan_phase8 is not None
        ):
            return

        builder = OccurrencePlanBuilder(
            root_spell=self._spell,
            blueprint=root_blueprint,
            spell_lookup=spell_lookup,
            system_states=self._spell_system_states,
        )
        plan = builder.build()

        # Hot-swap the plan without cleaning the previous object in-place.
        # Concurrent phase runners may still hold references to the prior plan.
        self._occurrence_plan_phase8 = plan
        self._phase8_occurrence_plan_input_signature = occurrence_plan_input_signature
        self._mark_phase8_11_codegen_ir_dirty()


    # ------------------------------------------------------------------
    # Phase 9 - Injection Plan
    # ------------------------------------------------------------------

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
                If Phase 8 artifacts are missing for this spell or if the
                root blueprint is missing for this spell.
            OperationCancelledError:
                If cancel_event signals cancellation.

        Threading:
            - Not thread-safe; expected to run under spellbook phase scheduling.

        Lifecycle:
            - Replaces any prior InjectionPlan reference for this spell.
            - Prior plan objects are cleaned during SpellCrafter teardown.
        """
        self.check_cleaned()
        if self._spell.is_existing_creation:
            return

        occurrence_plan = self._occurrence_plan_phase8
        injection_plan_input_signature = self._build_phase9_injection_plan_input_signature(
            occurrence_plan=occurrence_plan,
        )
        if (
                injection_plan_input_signature is not None
                and injection_plan_input_signature == self._phase9_injection_plan_input_signature
                and self._injection_plan_phase9 is not None
        ):
            return

        builder = InjectionPlanBuilder(
            occurrence_plan=occurrence_plan,
        )
        plan = builder.build()

        # Hot-swap the plan without cleaning the previous object in-place.
        # Concurrent phase runners may still hold references to the prior plan.
        self._injection_plan_phase9 = plan
        self._phase9_injection_plan_input_signature = injection_plan_input_signature
        self._mark_phase8_11_codegen_ir_dirty()


    # ------------------------------------------------------------------
    # Phase 10 - Patch Maps
    # ------------------------------------------------------------------

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
        self.check_cleaned()
        if self._spell.is_existing_creation:
            return

        root_blueprint = self._root_blueprint_phase5
        patch_maps_input_signature = self._build_phase10_patch_maps_input_signature(
            root_blueprint,
        )
        if (
                patch_maps_input_signature is not None
                and patch_maps_input_signature == self._phase10_patch_maps_input_signature
                and self._override_patch_map_phase10 is not None
                and self._mutation_patch_map_phase10 is not None
        ):
            return

        builder = PatchMapBuilder(
            blueprint=root_blueprint,
        )
        override_patch_map = builder.build_override_patch_map()
        mutation_patch_map = builder.build_mutation_patch_map()

        # Hot-swap patch maps without cleaning previous objects in-place.
        # Concurrent runners may still be reading the prior maps.
        self._override_patch_map_phase10 = override_patch_map
        self._mutation_patch_map_phase10 = mutation_patch_map
        self._phase10_patch_maps_input_signature = patch_maps_input_signature
        self._mark_phase8_11_codegen_ir_dirty()


    # ------------------------------------------------------------------
    # Phase 11 - Execution Assembly Plan
    # ------------------------------------------------------------------

    def _cache_execution_plan_metrics(
            self,
            *,
            occurrence_plan: OccurrencePlan,
            plan: ExecutionPlan,
    ) -> None:
        """
        Cache Phase 11 execution-plan metrics on the owning spell.

        Contract:
            - Requires valid Phase 8 occurrence plan and Phase 11 plan inputs.
            - Stores derived metrics on the spell for fast runtime inspection.
            - Intended for small/shallow graph path selection heuristics.
        """
        if occurrence_plan is None or plan is None:
            return

        steps = plan.steps
        step_count = len(steps)
        unique_spell_count = len(plan.spell_id_step_index)

        max_dependency_count = 0
        has_contract_payloads = False
        has_existing_creations = False

        for step in steps:
            dependency_count = len(step.dependency_keys)
            if dependency_count > max_dependency_count:
                max_dependency_count = dependency_count
            if step.has_contract_payload:
                has_contract_payloads = True
            if step.spell.is_existing_creation:
                has_existing_creations = True

        max_occurrence_depth = 0
        occurrence_graph = occurrence_plan.occurrence_graph
        if occurrence_graph:
            path_registry = occurrence_plan.path_registry
            for _, path_id in occurrence_graph.keys():
                depth = path_registry.depth(path_id)
                if depth > max_occurrence_depth:
                    max_occurrence_depth = depth

        has_calln: Optional[bool] = None
        fast_plan = plan.fast_plan
        if fast_plan is not None:
            fast_call_modes = fast_plan[20]
            has_calln = ExecutionPlanCallMode.CALLN in fast_call_modes

        dispatch_route = "ENGINE"
        if plan.fast_transient_plan is not None and not has_existing_creations:
            if max_occurrence_depth <= 3 and step_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_0"
            elif max_occurrence_depth <= 6 and step_count <= 16 and max_dependency_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_1"
            elif max_occurrence_depth <= 8 and step_count <= 24 and max_dependency_count <= 8:
                dispatch_route = "FAST_TRANSIENT_TIER_2"
            elif max_occurrence_depth <= 9 and step_count <= 32 and max_dependency_count <= 10:
                dispatch_route = "FAST_TRANSIENT_TIER_3"
            else:
                dispatch_route = "ENGINE"

        self._spell.execution_plan_step_count = step_count
        self._spell.execution_plan_unique_spell_count = unique_spell_count
        self._spell.execution_plan_max_occurrence_depth = max_occurrence_depth
        self._spell.execution_plan_max_dependency_count = max_dependency_count
        self._spell.execution_plan_has_calln = has_calln
        self._spell.execution_plan_has_contract_payloads = has_contract_payloads
        self._spell.execution_plan_has_existing_creations = has_existing_creations
        self._spell.execution_plan_dispatch_route = dispatch_route

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
            - Reuses cached no-overrides plan when deterministic Phase11
              no-overrides input signature is unchanged.
            - Reuses the full cached phase11 variant set when signature is
              unchanged and cached sibling variants are available.
            - Falls back to the legacy no-overrides rebuild path when signature
              inputs are missing.
        """
        self.check_cleaned()
        if self._spell.is_existing_creation:
            return

        occurrence_plan = self._occurrence_plan_phase8
        injection_plan = self._injection_plan_phase9
        spell_lookup = self._spell._spellbook._spell_id_pool

        # Fast key avoids rebuilding the deep phase11 no-overrides signature
        # when phase8/phase9 inputs and plan references are unchanged.
        phase11_no_overrides_fast_key = (
            self._phase8_occurrence_plan_input_signature,
            self._phase9_injection_plan_input_signature,
            id(occurrence_plan),
            id(injection_plan),
            id(spell_lookup),
        )
        can_reuse_no_overrides_fast_key = (
            self._phase8_occurrence_plan_input_signature is not None
            and (
                injection_plan is None
                or self._phase9_injection_plan_input_signature is not None
            )
        )
        if (
                can_reuse_no_overrides_fast_key
                and
                self._phase11_no_overrides_fast_key == phase11_no_overrides_fast_key
                and self._phase11_no_overrides_input_signature is not None
        ):
            no_overrides_input_signature = self._phase11_no_overrides_input_signature
        else:
            no_overrides_input_signature = self._build_phase11_no_overrides_input_signature(
                occurrence_plan=occurrence_plan,
                injection_plan=injection_plan,
                spell_lookup=spell_lookup,
            )
            if can_reuse_no_overrides_fast_key:
                self._phase11_no_overrides_fast_key = phase11_no_overrides_fast_key
            else:
                self._phase11_no_overrides_fast_key = None
        previous_no_overrides_signature = self._phase11_no_overrides_input_signature
        no_overrides_signature_unchanged = (
            no_overrides_input_signature is not None
            and previous_no_overrides_signature == no_overrides_input_signature
        )
        if (
                no_overrides_signature_unchanged
                and self._execution_plan_phase11_no_overrides is not None
                and self._execution_plan_phase11_overrides is not None
                and self._execution_plan_phase11 is not None
        ):
            cached_plan_no_overrides = self._execution_plan_phase11_no_overrides
            self._phase11_no_overrides_input_signature = no_overrides_input_signature
            self._cache_execution_plan_metrics(
                occurrence_plan=occurrence_plan,
                plan=cached_plan_no_overrides,
            )
            if (
                    self._phase12_no_overrides_executor is None
                    or self._phase12_no_overrides_executor_signature is None
            ):
                self._compile_phase12_no_overrides_executor_from_plan(
                    cached_plan_no_overrides,
                )
            return

        plan_no_overrides: ExecutionPlan
        if (
                no_overrides_signature_unchanged
                and self._execution_plan_phase11_no_overrides is not None
        ):
            plan_no_overrides = self._execution_plan_phase11_no_overrides
        else:
            plan_no_overrides = self._build_execution_plan_variant(
                occurrence_plan=occurrence_plan,
                injection_plan=injection_plan,
                spell_lookup=spell_lookup,
                plan_variant=ExecutionPlanVariant.NO_OVERRIDES_FAST,
            )
        self._phase11_no_overrides_input_signature = no_overrides_input_signature

        plan_overrides = self._build_execution_plan_variant(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=ExecutionPlanVariant.OVERRIDES,
        )

        plan_overrides_with_mutations = self._build_execution_plan_variant(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=ExecutionPlanVariant.OVERRIDES_WITH_MUTATIONS,
        )

        self._cache_execution_plan_metrics(
            occurrence_plan=occurrence_plan,
            plan=plan_no_overrides,
        )

        # Hot-swap execution plans without cleaning previous plan objects
        # in-place; concurrent meld calls may still be executing old plans.
        self._execution_plan_phase11_no_overrides = plan_no_overrides
        self._execution_plan_phase11_overrides = plan_overrides
        self._execution_plan_phase11 = plan_overrides_with_mutations
        self._mark_phase8_11_codegen_ir_dirty()
        self._compile_phase12_no_overrides_executor_from_plan(plan_no_overrides)

    def _build_execution_plan_variant(
            self,
            *,
            occurrence_plan: OccurrencePlan,
            injection_plan: Optional[InjectionPlan],
            spell_lookup: Dict[str, ISpell],
            plan_variant: str,
    ) -> ExecutionPlan:
        """
        Build one Phase 11 execution-plan variant from phase8/phase9 artifacts.

        Purpose:
            Provide the canonical builder path used when variant reuse is not
            possible or when a full rebuild is explicitly required.
        Contract:
            - Returns a fresh `ExecutionPlan` object for the requested variant.
            - Does not mutate source occurrence/injection artifacts.
        Args:
            occurrence_plan:
                Phase8 occurrence plan.
            injection_plan:
                Optional phase9 injection plan.
            spell_lookup:
                Spell lookup map keyed by spell id.
            plan_variant:
                Target `ExecutionPlanVariant` label.
        Returns:
            ExecutionPlan:
                Fresh execution plan for the requested variant.
        """
        builder = ExecutionPlanBuilder(
            occurrence_plan=occurrence_plan,
            injection_plan=injection_plan,
            spell_lookup=spell_lookup,
            plan_variant=plan_variant,
        )
        return builder.build()

    def _try_build_execution_plan_variant_from_base(
            self,
            *,
            base_plan: Any,
            plan_variant: str,
    ) -> Optional[ExecutionPlan]:
        """
        Attempt to derive a non-fast Phase 11 variant from an existing base plan.

        Purpose:
            Reuse shared step/index structure from the no-overrides plan to avoid
            repeated full `ExecutionPlanBuilder.build()` passes for sibling
            variants.
        Contract:
            - Returns a fresh `ExecutionPlan` with copied list/dict containers so
              cleanup remains isolated per variant.
            - Returns `None` when the base plan does not expose the required
              structure (for example in test stubs), allowing a safe fallback to
              the legacy full-build path.
            - Derived variants do not carry fast-path arrays/transient plans.
        Args:
            base_plan:
                Source plan expected to expose execution-plan structural fields.
            plan_variant:
                Target variant label for the derived plan.
        Returns:
            Optional[ExecutionPlan]:
                Derived plan when compatible, otherwise `None`.
        """
        try:
            root_spell_id = base_plan.root_spell_id
            root_instance_key = base_plan.root_instance_key
            steps = base_plan.steps
            spell_id_step_index = base_plan.spell_id_step_index
            optimistic_object_refs_by_spell_id = base_plan.optimistic_object_refs_by_spell_id
            available_param_by_spell_id = base_plan.available_param_by_spell_id
        except AttributeError:
            return None

        if root_spell_id is None or root_instance_key is None:
            return None
        if (
                steps is None
                or spell_id_step_index is None
                or optimistic_object_refs_by_spell_id is None
                or available_param_by_spell_id is None
        ):
            return None

        try:
            return ExecutionPlan(
                root_spell_id=root_spell_id,
                root_instance_key=root_instance_key,
                steps=list(steps),
                spell_id_step_index=dict(spell_id_step_index),
                optimistic_object_refs_by_spell_id=dict(optimistic_object_refs_by_spell_id),
                available_param_by_spell_id=dict(available_param_by_spell_id),
                plan_variant=plan_variant,
            )
        except (TypeError, ValueError):
            return None

    def _cleanup_execution_plans_phase11(self) -> None:
        """
        Deterministically clean all Phase 11 execution plan variants.
        """
        if self._execution_plan_phase11 is not None:
            try:
                self._execution_plan_phase11.cleanup()
            except Exception:
                pass
        if self._execution_plan_phase11_no_overrides is not None:
            try:
                self._execution_plan_phase11_no_overrides.cleanup()
            except Exception:
                pass
        if self._execution_plan_phase11_overrides is not None:
            try:
                self._execution_plan_phase11_overrides.cleanup()
            except Exception:
                pass
        self._execution_plan_phase11 = None
        self._execution_plan_phase11_no_overrides = None
        self._execution_plan_phase11_overrides = None
        self._reset_phase8_11_codegen_ir()


    # ------------------------------------------------------------------
    # Phase 6 - System-level Validation
    # ------------------------------------------------------------------

    def run_phase_system_validation(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 - System-level validation.

        Runs system-level validation strategies over Phase-5 artifacts and
        Phase-4 outcomes. Records per-conduit resolution validity via
        SpellSystemStates and caches the frame-level validation state on
        every SpellCrafter in the Spellbook.

        Note:
            When Phase-4 results have been cleaned but Phase 4 previously
            completed successfully, we still include a placeholder entry
            in the phase4_results map so MissingPhase4Strategy can treat
            the spell as validated.
        """
        self.check_cleaned()

        phase4_results: Dict[str, Any] = {}
        broken_spell_ids: Set[str] = set()

        spellbook = self._spell._spellbook
        spell_lookup: Dict[str, ISpell] = spellbook._spell_id_pool
        for spell_id, spell_instance in spell_lookup.items():
            crafter = spell_instance._crafter
            phase4_results[spell_id] = crafter._validation_result_phase4
            if crafter._is_broken:
                broken_spell_ids.add(spell_id)

        strategies = [
            CycleDetectionStrategy(),
            BrokenSpellInDagStrategy(),
            GraphConsistencyStrategy(),
            MissingPhase4Strategy(),
            RootReachabilityStrategy(),
            RootCoverageStrategy(),
            IndexDependencySanityStrategy(),
            VisibilityGapStrategy(),
            TopologyDependencyMismatchStrategy(),
            IdentityMixingStrategy(),
            ContractedVersionDriftStrategy(),
            LineageAlignmentStrategy(),
            IndexCoverageStrategy(),
            LineageVersionConflictStrategy(),
            RootLineageConflictStrategy(),
            OwnershipConsistencyStrategy(),
            DependencyTypeSanityStrategy(),
            ScopeOrderingStrategy(),
            ContractGraphCycleStrategy(),
            RootScaleLimitStrategy(),
            RootViabilityStrategy(),
            SocketRefSanityStrategy(),
        ]

        validator = SpellSystemValidationSystem(strategies=strategies)
        validation_state: SpellSystemValidationState = validator.validate(
            index=self._spell_system_index_phase5,
            blueprints=self._entire_dag_blueprint_phase5,
            phase4_results=phase4_results,
            broken_spell_ids=broken_spell_ids,
            spell_system_states=self._spell_system_states,
            conduit_id=conduit_id,
            spell_lookup=spell_lookup,
            cancel_event=cancel_event,
        )

        self._validation_result_phase6 = validation_state
        self._validated_phase6 = True
        for spell_instance in spell_lookup.values():
            crafter = spell_instance._ensure_crafter()
            crafter._validation_result_phase6 = validation_state
            crafter._validated_phase6 = True

    def run_phase_system_validation_local(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 6 local entrypoint.

        Purpose:
            Validate only the locally scoped Phase 5 graph produced by
            ``run_phase_root_blueprints_local``.
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
        self.check_cleaned()
        spellbook = self._spell._spellbook
        spell_lookup_pool = spellbook._spell_id_pool
        index = self._spell_system_index_phase5
        blueprints = self._entire_dag_blueprint_phase5
        if index is None or blueprints is None:
            raise RuntimeError("Phase 6 local requires Phase 5 local artifacts.")

        phase4_results: Dict[str, Any] = {}
        broken_spell_ids: Set[str] = set()
        scoped_spell_lookup: Dict[str, ISpell] = {}

        for spell_id in index.nodes.keys():
            spell_instance = spell_lookup_pool[spell_id]
            scoped_spell_lookup[spell_id] = spell_instance
            crafter = spell_instance._crafter
            phase4_results[spell_id] = crafter._validation_result_phase4
            if crafter._is_broken:
                broken_spell_ids.add(spell_id)

        visibility_gap_diagnostics = self._collect_local_visibility_gap_diagnostics(
            scoped_spell_ids=index.nodes.keys(),
            spell_lookup=spell_lookup_pool,
            root_ids=blueprints.keys(),
        )
        visibility_gap_diagnostics.extend(
            self._collect_local_blueprint_visibility_gap_diagnostics(
                blueprints=blueprints,
                spell_lookup=spell_lookup_pool,
            )
        )
        if visibility_gap_diagnostics:
            self._spell_system_states.bulk_set_conduit_spell_validity(
                conduit_id,
                {spell_id: SpellValidity.invalid for spell_id in index.nodes.keys()},
                change_reason=SpellStateChangeReason.validation_failed,
            )
            self._spell_system_states.bulk_set_conduit_root_validity(
                conduit_id,
                {root_id: SpellValidity.invalid for root_id in blueprints.keys()},
                change_reason=SpellStateChangeReason.validation_failed,
            )
            self._spell_system_states.record_conduit_diagnostics(
                conduit_id,
                visibility_gap_diagnostics,
            )
            validation_state = SpellSystemValidationState(
                is_valid=False,
                errors=visibility_gap_diagnostics,
                warnings=[],
                nodes=index.nodes,
            )
            self._validation_result_phase6 = validation_state
            self._validated_phase6 = True
            for spell_instance in scoped_spell_lookup.values():
                crafter = spell_instance._ensure_crafter()
                crafter._validation_result_phase6 = validation_state
                crafter._validated_phase6 = True
            return

        strategies = [
            CycleDetectionStrategy(),
            BrokenSpellInDagStrategy(),
            GraphConsistencyStrategy(),
            MissingPhase4Strategy(),
            RootReachabilityStrategy(),
            RootCoverageStrategy(),
            IndexDependencySanityStrategy(),
            VisibilityGapStrategy(),
            TopologyDependencyMismatchStrategy(),
            IdentityMixingStrategy(),
            ContractedVersionDriftStrategy(),
            LineageAlignmentStrategy(),
            IndexCoverageStrategy(),
            LineageVersionConflictStrategy(),
            RootLineageConflictStrategy(),
            OwnershipConsistencyStrategy(),
            DependencyTypeSanityStrategy(),
            ScopeOrderingStrategy(),
            ContractGraphCycleStrategy(),
            RootScaleLimitStrategy(),
            RootViabilityStrategy(),
            SocketRefSanityStrategy(),
        ]

        validator = SpellSystemValidationSystem(strategies=strategies)
        validation_state = validator.validate(
            index=index,
            blueprints=blueprints,
            phase4_results=phase4_results,
            broken_spell_ids=broken_spell_ids,
            spell_system_states=self._spell_system_states,
            conduit_id=conduit_id,
            spell_lookup=scoped_spell_lookup,
            cancel_event=cancel_event,
        )

        self._validation_result_phase6 = validation_state
        self._validated_phase6 = True
        for spell_instance in scoped_spell_lookup.values():
            crafter = spell_instance._ensure_crafter()
            crafter._validation_result_phase6 = validation_state
            crafter._validated_phase6 = True

    def _collect_local_visibility_gap_diagnostics(
            self,
            *,
            scoped_spell_ids: Collection[str],
            spell_lookup: Dict[str, ISpell],
            root_ids: Collection[str],
    ) -> List[SystemDiagnostic]:
        """
        Collect visibility-gap diagnostics for local Phase 6 validation.

        Purpose:
            Detect unresolved dependency spell ids in local topologies before
            Phase 8 compilation attempts to construct occurrence plans.
        Contract:
            - Emits one ERROR diagnostic per unique missing dependency edge.
            - Uses local topology target_spell_ids as the source of truth.
            - Never mutates SpellSystemStates or spell objects.
        Args:
            scoped_spell_ids:
                Spell ids participating in local validation scope.
            spell_lookup:
                Visible spell_id -> spell map for the current Spellbook.
            root_ids:
                Root ids for the local validation scope.
        Returns:
            List[SystemDiagnostic]:
                Visibility-gap diagnostics; empty when scope is fully visible.
        """
        self.check_cleaned()
        ordered_root_ids = sorted(root_ids)
        root_id = ordered_root_ids[0] if ordered_root_ids else self._spell.spell_index.current
        diagnostics: List[SystemDiagnostic] = []
        seen: Set[Tuple[str, str, str]] = set()
        for spell_id in scoped_spell_ids:
            topology = self._spell_system_states.get_local_topology_by_id(spell_id)
            if topology is None:
                continue
            for socket in topology.iter_sockets():
                for dependency_id in socket.target_spell_ids:
                    if dependency_id in spell_lookup:
                        continue
                    signature = (spell_id, socket.param_name, dependency_id)
                    if signature in seen:
                        continue
                    seen.add(signature)
                    diagnostics.append(
                        SystemDiagnostic(
                            code="visibility_gap_dependency_filtered",
                            message=(
                                f"Spell '{spell_id}' parameter '{socket.param_name}' "
                                f"depends on '{dependency_id}', but that dependency is "
                                "not visible to this Spellbook."
                            ),
                            severity=SystemDiagnosticSeverity.ERROR,
                            spell_id=spell_id,
                            root_id=root_id,
                            source="LocalVisibilityGapGuard",
                            details={
                                "spell_id": spell_id,
                                "param_name": socket.param_name,
                                "missing_dependency_id": dependency_id,
                            },
                        )
                    )
        return diagnostics

    def _collect_local_blueprint_visibility_gap_diagnostics(
            self,
            *,
            blueprints: Dict[str, RootResolutionBlueprint],
            spell_lookup: Dict[str, ISpell],
    ) -> List[SystemDiagnostic]:
        """
        Collect visibility-gap diagnostics from local Phase 5 root blueprints.

        Purpose:
            Catch hidden dependency nodes that are present in blueprint DAGs but
            not visible in this Spellbook's spell pool.
        Contract:
            - Emits one ERROR diagnostic per unique (root_id, missing_spell_id).
            - Never mutates blueprint or spell pool artifacts.
        Args:
            blueprints:
                Local root blueprints produced by Phase 5 local.
            spell_lookup:
                Visible spell_id -> spell map for the current Spellbook.
        Returns:
            List[SystemDiagnostic]:
                Visibility-gap diagnostics derived from blueprint DAG contents.
        """
        self.check_cleaned()
        diagnostics: List[SystemDiagnostic] = []
        seen: Set[Tuple[str, str]] = set()
        for root_id, blueprint in blueprints.items():
            dag = blueprint.dag
            for dependency_id in dag.nodes.keys():
                if dependency_id in spell_lookup:
                    continue
                signature = (root_id, dependency_id)
                if signature in seen:
                    continue
                seen.add(signature)
                diagnostics.append(
                    SystemDiagnostic(
                        code="visibility_gap_dependency_filtered",
                        message=(
                            f"Root '{root_id}' references dependency "
                            f"'{dependency_id}', but that dependency is not "
                            "visible to this Spellbook."
                        ),
                        severity=SystemDiagnosticSeverity.ERROR,
                        spell_id=dependency_id,
                        root_id=root_id,
                        source="LocalVisibilityGapGuard",
                        details={
                            "root_id": root_id,
                            "missing_dependency_id": dependency_id,
                        },
                    )
                )
        return diagnostics


    # ------------------------------------------------------------------
    # Phase 7 - Change-control / Component-of Index
    # ------------------------------------------------------------------

    def run_phase_change_control(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Phase 7 - Change-control wiring.

        Behaviour (conduit-scoped, idempotent):
        - Ensure ChangeControlManager is present for the frame.
        - Ensure the component-of index is (re)built from the Phase-5 root blueprints.
        - Ensure the revalidator hook is registered.
        """
        self.check_cleaned()
        self._ensure_change_control_ready(conduit_id)

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
        self.check_cleaned()
        self._ensure_change_control_ready_local(conduit_id)

    def _ensure_change_control_ready(self, conduit_id: str) -> None:
        """
        Internal helper to (re)wire change-control after Phase 5 artifacts exist.
        """
        spellbook = self._spell._spellbook
        frame_name = spellbook._aetheric_frame
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = self._filter_root_blueprints_to_owned(self._entire_dag_blueprint_phase5)
        change_control_manager.rebuild_component_of(conduit_id, owned_root_blueprints)
        if conduit_id not in change_control_manager._revalidate_fn_by_conduit:
            def _revalidate_dirty_roots(
                    dirty_roots: Set[str],
                    cancel_event: Optional[CancellationEvent],
            ) -> Set[str]:
                """
                Revalidate dirty roots for the conduit-wide Phase 7 hook.

                This closure is registered once on the conduit's
                ChangeControlManager slot so later dirty-root events can drive
                a full spell-level recompilation through the current
                Spellbook/runtime view.

                Contract:
                    - Resolves each dirty root from the live spell pool.
                    - Reuses the spell's attached crafter rather than creating
                      a new orchestration object.
                    - Runs full `run_all_phases(...)` recovery for each root in
                      this conduit context.
                    - Returns only the roots that completed successfully.
                """
                validated_roots: Set[str] = set()
                for root_id in dirty_roots:
                    spell_instance = spellbook._spell_id_pool[root_id]
                    crafter = spell_instance._crafter
                    crafter.run_all_phases(conduit_id=conduit_id, cancel_event=cancel_event)
                    validated_roots.add(root_id)

                return validated_roots

            change_control_manager.set_revalidator(conduit_id, _revalidate_dirty_roots)

    def _ensure_change_control_ready_local(self, conduit_id: str) -> None:
        """
        Internal helper to upsert local change-control wiring after local Phase 5.

        Contract:
            - Requires local Phase 5 root blueprints on this crafter.
            - Uses component-of upsert semantics to preserve unrelated roots.
            - Registers the same revalidator contract as frame-wide wiring.
        """
        spellbook = self._spell._spellbook
        frame_name = spellbook._aetheric_frame
        change_control_manager = spellbook._aether._get_change_control_manager(frame_name)
        owned_root_blueprints = self._filter_root_blueprints_to_owned(self._entire_dag_blueprint_phase5)
        change_control_manager.upsert_component_of(conduit_id, owned_root_blueprints)
        if conduit_id not in change_control_manager._revalidate_fn_by_conduit:
            def _revalidate_dirty_roots(
                    dirty_roots: Set[str],
                    cancel_event: Optional[CancellationEvent],
            ) -> Set[str]:
                """
                Revalidate dirty roots for the local Phase 7 change-control hook.

                This local variant mirrors the frame-wide revalidation contract
                but is installed from the local wiring path so scoped
                revalidation can still hand dirty roots back into the full
                spell-phase pipeline for this conduit.

                Contract:
                    - Resolves each dirty root from the live spell pool.
                    - Reuses the spell's attached crafter.
                    - Runs full `run_all_phases(...)` recovery for each root in
                      this conduit context.
                    - Returns only the roots that completed successfully.
                """
                validated_roots: Set[str] = set()
                for root_id in dirty_roots:
                    spell_instance = spellbook._spell_id_pool[root_id]
                    crafter = spell_instance._crafter
                    crafter.run_all_phases(conduit_id=conduit_id, cancel_event=cancel_event)
                    validated_roots.add(root_id)

                return validated_roots

            change_control_manager.set_revalidator(conduit_id, _revalidate_dirty_roots)


    # ------------------------------------------------------------------
    # Convenience - run all phases
    # ------------------------------------------------------------------

    def run_structural_phases(
            self,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run **structural phases only** (1-4) in sequence.

        This is typically invoked via :meth:`Spell.run_structural_phases` and
        is used for global, conduit-agnostic structural validation.

        Execution order:
            1. Requirements (Phase 1)
            2. Symbolic graph (Phase 2)
            3. Local frame / DAG (Phase 3)
            4. Validation (Phase 4)

        Returns:
            None. The crafter retains all intermediate artifacts until
            :meth:`cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        Notes:
            Phase artifacts are cleaned after Phase 7; structural data remains in
            SpellSystemStates and on the Spell itself.
        """
        self.run_phase_requirements(cancel_event=cancel_event)
        self.run_phase_symbolic_graph(cancel_event=cancel_event)
        self.run_phase_local_frame(cancel_event=cancel_event)
        self.run_phase_validation(cancel_event=cancel_event)

    def run_all_phases(
            self,
            conduit_id: str,
            cancel_event: Optional[CancellationEvent] = None,
    ) -> None:
        """
        Convenience helper to run all phases in sequence for this spell.

        This is typically invoked via :meth:`Spell.run_all_phases` (a facade)
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
            None. The crafter retains all intermediate artifacts until
            :meth:`cleanup` is called. The owning Spell only needs to hold the
            final DAG and dependency spell_ids once Phase 3 is fully implemented.
        """
        if not conduit_id:
            raise ValueError("conduit_id must not be empty.")
        self.run_phase_requirements(cancel_event=cancel_event)
        self.run_phase_symbolic_graph(cancel_event=cancel_event)
        self.run_phase_local_frame(cancel_event=cancel_event)
        self.run_phase_validation(cancel_event=cancel_event)
        self.run_phase_root_blueprints(conduit_id, cancel_event=cancel_event)
        self.run_phase_system_validation(conduit_id, cancel_event=cancel_event)
        self.run_phase_change_control(conduit_id, cancel_event=cancel_event)

        resolution_state = self._spell_system_states.get_conduit_resolution_state(conduit_id)
        if resolution_state is not None and resolution_state.has_errors():
            self.cleanup_phase_artifacts()
            return

        self.run_phase_occurrence_plan(conduit_id, cancel_event=cancel_event)
        self.run_phase_injection_plan(conduit_id, cancel_event=cancel_event)
        self.run_phase_patch_maps(conduit_id, cancel_event=cancel_event)
        self.run_phase_execution_plan(conduit_id, cancel_event=cancel_event)
        self.cleanup_phase_artifacts()
