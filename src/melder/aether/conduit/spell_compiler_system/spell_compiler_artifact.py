import threading
from typing import Any, Callable, Dict, Optional, Tuple

from mypy_extensions import mypyc_attr

from melder.utilities.general_base.cleanable import Cleanable
from melder.utilities.interfaces.iinjectionplan import IInjectionPlan
from melder.utilities.interfaces.imutationpatchmap import IMutationPatchMap
from melder.utilities.interfaces.ioccurrenceplan import IOccurrencePlan
from melder.utilities.interfaces.ioverridepatchmap import IOverridePatchMap
from melder.utilities.interfaces.irootresolutionblueprint import IRootResolutionBlueprint
from melder.utilities.interfaces.ispellrequirements import ISpellRequirements
from melder.aether.spellbook.spell_crafter.profiles.resolution_profile import (
    SpellResolutionFrame,
)
from melder.aether.spellbook.spell_crafter.symbolic_graph.spell_symbolic_graph import (
    SpellSymbolicGraph,
)
from melder.aether.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlan,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import (
    SpellSystemIndex,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_validation_state import (
    SpellSystemValidationState,
)
from melder.aether.spellbook.spell_crafter.validation.spell_validation_result import (
    SpellValidationResult,
)


@mypyc_attr(native_class=True)
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

    __slots__ = Cleanable.__slots__ + [
        "_lock",
        "spell_id",
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
        "_phase11_no_overrides_plan_signature",
        "_phase11_no_overrides_transient_schema",
        "_phase12_no_overrides_executor",
        "_phase12_no_overrides_executor_signature",
        "_phase11_no_overrides_input_signature",
        "_phase11_no_overrides_fast_key",
        "_codegen_ir",
        "_phase8_11_codegen_ir_dirty",
        "_spell_system_index_phase5",
        "_is_broken",
        "_entire_dag_blueprint_phase5",
    ]

    def __init__(self, spell_id: str) -> None:
        """
        Initialize one empty compiler artifact container.

        Purpose:
            Create a new artifact bucket dedicated to one spell identity and
            initialize all phase cache fields to their unset state.

        Contract:
            - Tracks only spell-scoped compiler/build caches for phase
              pipelines.
            - Starts empty so callers must fill artifacts through compiler phase
              execution.
            - Holds a lock for any future synchronized cleanup or cache-reset
              operations.

        Args:
            spell_id: Owning spell version identity stamped into this artifact.

        Raises:
            ValueError: If `spell_id` is empty.

        Returns:
            None.
        """
        super().__init__()
        if not spell_id:
            raise ValueError("spell_id cannot be empty.")
        self._lock: threading.RLock = threading.RLock()
        self.spell_id: str = spell_id
        self._requirements: Optional[ISpellRequirements] = None
        self._symbolic_graph: Optional[SpellSymbolicGraph] = None
        self._resolution_frame: Optional[SpellResolutionFrame] = None
        self._validation_result_phase4: Optional[SpellValidationResult] = None
        self._validated_phase4: bool = False
        self._validation_result_phase6: Optional[SpellSystemValidationState] = None
        self._validated_phase6: bool = False
        self._validated: bool = False
        self._root_blueprint_phase5: Optional[IRootResolutionBlueprint] = None
        self._phase8_occurrence_plan_input_signature: Optional[str] = None
        self._phase8_occurrence_plan_fast_key: Optional[Tuple[Any, ...]] = None
        self._occurrence_plan_phase8: Optional[IOccurrencePlan] = None
        self._phase9_injection_plan_input_signature: Optional[str] = None
        self._injection_plan_phase9: Optional[IInjectionPlan] = None
        self._override_patch_map_phase10: Optional[IOverridePatchMap] = None
        self._mutation_patch_map_phase10: Optional[IMutationPatchMap] = None
        self._phase10_patch_maps_input_signature: Optional[Tuple[Any, ...]] = None
        self._execution_plan_phase11: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_no_overrides: Optional[ExecutionPlan] = None
        self._execution_plan_phase11_overrides: Optional[ExecutionPlan] = None
        self._phase11_no_overrides_plan_signature: Optional[str] = None
        self._phase11_no_overrides_transient_schema: Optional[Dict[str, Any]] = None
        self._phase12_no_overrides_executor: Optional[Callable[..., Any]] = None
        self._phase12_no_overrides_executor_signature: Optional[str] = None
        self._phase11_no_overrides_input_signature: Optional[str] = None
        self._phase11_no_overrides_fast_key: Optional[Tuple[Any, ...]] = None
        self._codegen_ir: Optional[Dict[str, Any]] = None
        self._phase8_11_codegen_ir_dirty: bool = False
        self._spell_system_index_phase5: Optional[SpellSystemIndex] = None
        self._is_broken: bool = False
        self._entire_dag_blueprint_phase5: Optional[
            Dict[str, IRootResolutionBlueprint]
        ] = None

    def cleanup(self) -> None:
        """
        Deterministically release attached compiler/build artifacts.

        Contract:
            - Idempotent cleanup.
            - Best-effort cleans attached artifact objects when they expose
              `cleanup()`.
            - Drops local references after cleanup completes.

        Returns:
            None.
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

            del self.spell_id
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
            del self._phase11_no_overrides_plan_signature
            del self._phase11_no_overrides_transient_schema
            del self._phase12_no_overrides_executor
            del self._phase12_no_overrides_executor_signature
            del self._phase11_no_overrides_input_signature
            del self._phase11_no_overrides_fast_key
            del self._codegen_ir
            del self._spell_system_index_phase5
            del self._entire_dag_blueprint_phase5

    def reset_phase_artifacts(self) -> None:
        """
        Release structural-validation artifacts while keeping later plan state.

        Contract:
            - Clears the reusable Phase 1-4 artifacts only.
            - Clears the exported `phase2_5` codegen snapshot because its
              structural source artifacts are no longer valid after reset.
            - Preserves Phase 5 and later plan/codegen artifacts.

        Returns:
            None.
        """
        self.check_cleaned()
        with self._lock:
            if self._cleaned:
                return
            self._cleanup_phase_artifacts_locked()
            from melder.aether.conduit.spell_compiler_system.phases.shared_compiler_executions import (
                SharedCompilerExecutions,
            )
            SharedCompilerExecutions.reset_phase2_5_codegen_ir(self)

    def cleanup_phase_artifacts(self) -> None:
        """
        Backward-compatible alias for structural artifact reset.

        Contract:
            - Behaves exactly like `reset_phase_artifacts()`.

        Returns:
            None.
        """
        self.reset_phase_artifacts()

    def _cleanup_phase_artifacts_locked(self) -> None:
        """
        Internal structural-artifact cleanup for the Phase 1-4 state group.

        Contract:
            - Best-effort cleans owned structural-validation artifacts.
            - Leaves Phase 5 and later state untouched.

        Returns:
            None.
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

    def clear_phase5_artifacts(self) -> None:
        """
        Clear Phase 5 and later state while keeping Phase 1-4 artifacts.

        Contract:
            - Drops the Phase 5 blueprint reference.
            - Cleans and nulls Phase 8-11 plan/executor state.
            - Clears the Phase 5 system index.
            - Resets later transient execution/signature state.

        Args:
            None.

        Returns:
            None.
        """
        self.check_cleaned()
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
        self._cleanup_execution_plans_phase11()
        self._spell_system_index_phase5 = None

        self._phase8_11_codegen_ir_dirty = False
        self._phase11_no_overrides_plan_signature = None
        self._phase11_no_overrides_transient_schema = None
        self._phase12_no_overrides_executor = None
        self._phase12_no_overrides_executor_signature = None
        self._phase11_no_overrides_input_signature = None
        self._phase11_no_overrides_fast_key = None

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
        self._phase11_no_overrides_plan_signature = None
        self._phase11_no_overrides_transient_schema = None
