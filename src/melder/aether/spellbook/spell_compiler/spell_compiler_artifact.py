import threading
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple, ClassVar

from melder.utilities.general_base.cleanable import Cleanable
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
if TYPE_CHECKING:
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_contract_analysis import (
        SpellOccurrenceContractAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.spell_analyzer.data.spell_occurrence_graph_analysis import (
        SpellOccurrenceGraphAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_instance_analysis import (
        SpellOccurrenceInstanceAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.artifact_processor.data.spell_occurrence_order_analysis import (
        SpellOccurrenceOrderAnalysis,
    )
    from melder.aether.spellbook.spell_compiler.blueprints.injection_plan import InjectionPlan
    from melder.aether.spellbook.spell_compiler.blueprints.patch_maps import MutationPatchMap, OverridePatchMap
    from melder.aether.spellbook.spell_compiler.spell_requirements_finder.spell_requirements import (
        SpellRequirements,
    )
    from melder.aether.spellbook.spell_compiler.validation.spell_validation_result import (
        SpellValidationResult,
    )
    from melder.aether.spellbook.spell_compiler.system.spell_system_validation_state import (
        SpellSystemValidationState,
    )
    from melder.aether.spellbook.spell_compiler.system.spell_system_index import (
        SpellSystemIndex,
    )
    from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import (
        ExecutionPlan,
    )
    from melder.aether.spellbook.spell_compiler.profiles.resolution_profile import (
        SpellResolutionFrame,
    )
    from melder.aether.spellbook.spell_compiler.symbolic_graph.spell_symbolic_graph import (
        SpellSymbolicGraph,
    )
    from melder.aether.spellbook.spell_compiler.blueprints.occurrence_plan import (
        OccurrencePlan,
    )
    from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import RootResolutionBlueprint



class SpellCompilerArtifact(Cleanable):
    """
    Spell-scoped compiler artifact container.

    Purpose:
        Provide an explicit home for the mutable compiler/build artifacts that
        are currently stored implicitly on `SpellCrafter`.

    Contract:
        - Holds only spell-scoped compiler/build state.
        - Owns cleanup of attached artifact objects when they expose a cleanup
          method.
        - Does not own `Spell`, `Spellbook`, validators, or frame-level
          services.
        - Starts empty and additive; existing `SpellCrafter` behavior remains
          authoritative until later slices migrate reads and writes.
    """
    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "spell_id",
        "_requirements",
        "_requirements_shape_profile_phase1",
        "_symbolic_graph",
        "_resolution_frame",
        "_validation_result_phase4",
        "_validated_phase4",
        "_validation_result_phase6",
        "_validated_phase6",
        "_validated",
        "_root_blueprint_phase5",
        "_requires_spellspace_request_phase5",
        "_occurrence_analysis_input_signature",
        "_occurrence_analysis_fast_key",
        "_occurrence_graph_analysis",
        "_occurrence_order_analysis",
        "_occurrence_instance_analysis",
        "_occurrence_contract_analysis",
        "_occurrence_analysis_shape_profile",
        "_phase8_occurrence_plan_input_signature",
        "_phase8_occurrence_plan_fast_key",
        "_occurrence_plan_phase8",
        "_occurrence_shape_profile_phase8",
        "_phase9_injection_plan_input_signature",
        "_injection_plan_phase9",
        "_injection_shape_profile_phase9",
        "_override_patch_map_phase10",
        "_mutation_patch_map_phase10",
        "_phase10_patch_maps_input_signature",
        "_override_shape_profile_phase10",
        "_execution_plan_phase11",
        "_execution_plan_phase11_no_overrides",
        "_execution_plan_phase11_overrides",
        "_execution_plan_step_count_phase11",
        "_execution_plan_unique_spell_count_phase11",
        "_execution_plan_max_occurrence_depth_phase11",
        "_execution_plan_max_dependency_count_phase11",
        "_execution_plan_has_calln_phase11",
        "_execution_plan_has_contract_payloads_phase11",
        "_execution_plan_has_existing_creations_phase11",
        "_execution_shape_profile_phase11",
        "_phase11_no_overrides_plan_signature",
        "_phase11_no_overrides_transient_schema",
        "_phase13_no_overrides_executor",
        "_phase13_no_overrides_executor_signature",
        "_phase11_no_overrides_input_signature",
        "_phase11_no_overrides_fast_key",
        "_phase12_processor_state",
        "_phase12_codegen_plan",
        "_codegen_ir",
        "_phase8_11_codegen_ir_dirty",
        "_spell_system_index_phase5",
        "_is_broken",
        "_entire_dag_blueprint_phase5",
    ]

    def __init__(self, spell_id: str) -> None:
        """
            Create a new SpellCrafter for one bound: class: 'Spell`.
            
            Args:
                spell_id:
                    The spell identifier. Must be non-empty.
            
            Contract:
                - Captures shared spell-owned services needed by later phases, such
                  as the spell validator and spell-system-state view.
                - Starts with empty artifact caches for all later phases.
                - Allows callers that already built a resolution profile to avoid
                  duplicating the first requirements extraction step.
        """
        super().__init__()
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self.spell_id: str = spell_id
        self._requirements: Optional[SpellRequirements] = None
        self._requirements_shape_profile_phase1: Optional[Dict[str, Any]] = None
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        self._resolution_frame: Optional[SpellResolutionFrame] = None
        self._validation_result_phase4: Optional[SpellValidationResult] = None
        self._validated_phase4: bool = False
        self._validation_result_phase6: Optional[SpellSystemValidationState] = None
        self._validated_phase6: bool = False
        self._validated: bool = False
        self._root_blueprint_phase5: Optional[RootResolutionBlueprint] = None
        self._requires_spellspace_request_phase5: bool = False
        self._occurrence_analysis_input_signature: Optional[str] = None
        self._occurrence_analysis_fast_key: Optional[Tuple[Any, ...]] = None
        self._occurrence_graph_analysis: Optional[SpellOccurrenceGraphAnalysis] = None
        self._occurrence_order_analysis: Optional[SpellOccurrenceOrderAnalysis] = None
        self._occurrence_instance_analysis: Optional[SpellOccurrenceInstanceAnalysis] = None
        self._occurrence_contract_analysis: Optional[SpellOccurrenceContractAnalysis] = None
        self._occurrence_analysis_shape_profile: Optional[Dict[str, Any]] = None
        self._phase8_occurrence_plan_input_signature: Optional[str] = None
        self._phase8_occurrence_plan_fast_key: Optional[Tuple[Any, ...]] = None
        self._occurrence_plan_phase8: Optional[OccurrencePlan] = None
        self._occurrence_shape_profile_phase8: Optional[Dict[str, Any]] = None
        self._phase9_injection_plan_input_signature: Optional[str] = None
        self._injection_plan_phase9: Optional[InjectionPlan] = None
        self._injection_shape_profile_phase9: Optional[Dict[str, Any]] = None
        self._override_patch_map_phase10: Optional[OverridePatchMap] = None
        self._mutation_patch_map_phase10: Optional[MutationPatchMap] = None
        self._phase10_patch_maps_input_signature: Optional[Tuple[Any, ...]] = None
        self._override_shape_profile_phase10: Optional[Dict[str, Any]] = None
        self._execution_plan_phase11: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_no_overrides: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_overrides: Optional[ExecutionPlan] = None
        self._execution_plan_step_count_phase11: Optional[int] = None
        self._execution_plan_unique_spell_count_phase11: Optional[int] = None
        self._execution_plan_max_occurrence_depth_phase11: Optional[int] = None
        self._execution_plan_max_dependency_count_phase11: Optional[int] = None
        self._execution_plan_has_calln_phase11: Optional[bool] = None
        self._execution_plan_has_contract_payloads_phase11: Optional[bool] = None
        self._execution_plan_has_existing_creations_phase11: Optional[bool] = None
        self._execution_shape_profile_phase11: Optional[Dict[str, Any]] = None
        self._phase11_no_overrides_plan_signature: Optional[str] = None
        self._phase11_no_overrides_transient_schema: Optional[Dict[str, Any]] = None
        self._phase13_no_overrides_executor: Optional[Callable[..., Any]] = None
        self._phase13_no_overrides_executor_signature: Optional[str] = None
        self._phase11_no_overrides_input_signature: Optional[str] = None
        self._phase11_no_overrides_fast_key: Optional[Tuple[Any, ...]] = None
        self._phase12_processor_state: Optional[Any] = None
        self._phase12_codegen_plan: Optional[Any] = None
        self._codegen_ir: Optional[Dict[str, Any]] = None
        self._phase8_11_codegen_ir_dirty: bool = False
        self._spell_system_index_phase5: Optional[SpellSystemIndex] = None
        self._is_broken: bool = False
        self._entire_dag_blueprint_phase5: Optional[
            Dict[str, RootResolutionBlueprint]
        ] = None

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
            self._cleanup_phase12_artifacts()
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
            self._cleanup_occurrence_analysis_artifacts()
            self._cleaned = True
            self._phase8_11_codegen_ir_dirty = False
            self._validated_phase4 = False
            self._validated_phase6 = False
            self._is_broken = False

            del self.spell_id
            del self._root_blueprint_phase5
            del self._requires_spellspace_request_phase5
            del self._occurrence_analysis_input_signature
            del self._occurrence_analysis_fast_key
            del self._occurrence_graph_analysis
            del self._occurrence_order_analysis
            del self._occurrence_instance_analysis
            del self._occurrence_contract_analysis
            del self._occurrence_analysis_shape_profile
            del self._requirements_shape_profile_phase1
            del self._phase8_occurrence_plan_input_signature
            del self._phase8_occurrence_plan_fast_key
            del self._occurrence_plan_phase8
            del self._occurrence_shape_profile_phase8
            del self._phase9_injection_plan_input_signature
            del self._injection_plan_phase9
            del self._injection_shape_profile_phase9
            del self._override_patch_map_phase10
            del self._mutation_patch_map_phase10
            del self._phase10_patch_maps_input_signature
            del self._override_shape_profile_phase10
            del self._execution_plan_phase11
            del self._execution_plan_phase11_no_overrides
            del self._execution_plan_phase11_overrides
            del self._execution_plan_step_count_phase11
            del self._execution_plan_unique_spell_count_phase11
            del self._execution_plan_max_occurrence_depth_phase11
            del self._execution_plan_max_dependency_count_phase11
            del self._execution_plan_has_calln_phase11
            del self._execution_plan_has_contract_payloads_phase11
            del self._execution_plan_has_existing_creations_phase11
            del self._execution_shape_profile_phase11
            del self._phase11_no_overrides_plan_signature
            del self._phase11_no_overrides_transient_schema
            del self._phase13_no_overrides_executor
            del self._phase13_no_overrides_executor_signature
            del self._phase11_no_overrides_input_signature
            del self._phase11_no_overrides_fast_key
            del self._phase12_processor_state
            del self._phase12_codegen_plan
            del self._codegen_ir
            del self._spell_system_index_phase5
            del self._entire_dag_blueprint_phase5

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
        self.check_cleaned()
        with self._lock:
            if self._cleaned:
                return
            self._cleanup_phase_artifacts_locked()
            from melder.aether.spellbook.spell_compiler.phases.shared_compiler_executions import (
                SharedCompilerExecutions,
            )
            SharedCompilerExecutions.reset_phase2_5_codegen_ir(self)

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
                - Best-effort cleans owned artifact objects before pulling them.
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
        self._requirements_shape_profile_phase1 = None
        self._symbolic_graph = None
        self._validation_result_phase4 = None
        self._validation_result_phase6 = None

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
        self.check_cleaned()
        self._root_blueprint_phase5 = None
        self._requires_spellspace_request_phase5 = False
        self._occurrence_analysis_input_signature = None
        self._occurrence_analysis_fast_key = None
        self._occurrence_analysis_shape_profile = None
        self._cleanup_occurrence_analysis_artifacts()
        self._phase8_occurrence_plan_input_signature = None
        self._phase8_occurrence_plan_fast_key = None
        self._occurrence_shape_profile_phase8 = None

        if self._occurrence_plan_phase8 is not None:
            try:
                self._occurrence_plan_phase8.cleanup()
            except Exception:
                pass
        self._occurrence_plan_phase8 = None

        self._phase9_injection_plan_input_signature = None
        self._injection_shape_profile_phase9 = None
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
        self._override_shape_profile_phase10 = None
        self._cleanup_execution_plans_phase11()
        self._spell_system_index_phase5 = None

        self._phase8_11_codegen_ir_dirty = False
        self._phase11_no_overrides_plan_signature = None
        self._phase11_no_overrides_transient_schema = None
        self._phase13_no_overrides_executor = None
        self._phase13_no_overrides_executor_signature = None
        self._phase11_no_overrides_input_signature = None
        self._phase11_no_overrides_fast_key = None

    def _cleanup_occurrence_analysis_artifacts(self) -> None:
        """
        Deterministically clean all occurrence-analysis artifacts.

        Contract:
            - Best-effort cleans all four occurrence-analysis objects.
            - Clears the occurrence-analysis slots regardless of individual cleanup
              failures.
            - Safe to call repeatedly.
        """
        occurrence_graph_analysis = self._occurrence_graph_analysis
        if occurrence_graph_analysis is not None:
            try:
                occurrence_graph_analysis.cleanup()
            except Exception:
                pass
        occurrence_order_analysis = self._occurrence_order_analysis
        if occurrence_order_analysis is not None:
            try:
                occurrence_order_analysis.cleanup()
            except Exception:
                pass
        occurrence_instance_analysis = self._occurrence_instance_analysis
        if occurrence_instance_analysis is not None:
            try:
                occurrence_instance_analysis.cleanup()
            except Exception:
                pass
        occurrence_contract_analysis = self._occurrence_contract_analysis
        if occurrence_contract_analysis is not None:
            try:
                occurrence_contract_analysis.cleanup()
            except Exception:
                pass
        self._occurrence_graph_analysis = None
        self._occurrence_order_analysis = None
        self._occurrence_instance_analysis = None
        self._occurrence_contract_analysis = None

    def _cleanup_phase12_artifacts(self) -> None:
        """
        Deterministically clean Phase 12 processor/codegen-plan artifacts.

        Contract:
            - Best-effort cleans both Phase 12 outputs when they expose a
              cleanup method.
            - Clears the Phase 12 slots regardless of individual cleanup
              failures.
            - Safe to call repeatedly.
        """
        phase12_processor_state = self._phase12_processor_state
        if phase12_processor_state is not None:
            try:
                phase12_processor_state.cleanup()
            except Exception:
                pass
        phase12_codegen_plan = self._phase12_codegen_plan
        if phase12_codegen_plan is not None:
            try:
                phase12_codegen_plan.cleanup()
            except Exception:
                pass
        self._phase12_processor_state = None
        self._phase12_codegen_plan = None

    def _cleanup_execution_plans_phase11(self) -> None:
        """
        Deterministically clean all Phase 11 execution plan variants.

        Contract:
            - Best-effort cleans all three execution-plan caches for no-overrides,
              overrides, and default variant.
            - Leaves non-plan mutable state (for example phase-5 caches) untouched.

        Returns:
            None.
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
        self._execution_plan_step_count_phase11 = None
        self._execution_plan_unique_spell_count_phase11 = None
        self._execution_plan_max_occurrence_depth_phase11 = None
        self._execution_plan_max_dependency_count_phase11 = None
        self._execution_plan_has_calln_phase11 = None
        self._execution_plan_has_contract_payloads_phase11 = None
        self._execution_plan_has_existing_creations_phase11 = None
        self._execution_shape_profile_phase11 = None
        self._phase11_no_overrides_plan_signature = None
        self._phase11_no_overrides_transient_schema = None
        self._cleanup_phase12_artifacts()




