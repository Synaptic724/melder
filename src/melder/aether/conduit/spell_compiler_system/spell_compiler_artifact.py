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
        """
        if self._cleaned:
            return

        self._cleaned = True

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

        if self._resolution_frame is not None:
            try:
                self._resolution_frame.cleanup()
            except Exception:
                pass

        if self._validation_result_phase4 is not None:
            try:
                self._validation_result_phase4.cleanup()
            except Exception:
                pass

        if self._validation_result_phase6 is not None:
            try:
                self._validation_result_phase6.cleanup()
            except Exception:
                pass

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

        self._cleanup_phase5_blueprint_map()

        del self.spell_id
        del self._requirements
        del self._symbolic_graph
        del self._resolution_frame
        del self._validation_result_phase4
        del self._validated_phase4
        del self._validation_result_phase6
        del self._validated_phase6
        del self._validated
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
        del self._phase8_11_codegen_ir_dirty
        del self._spell_system_index_phase5
        del self._is_broken
        del self._entire_dag_blueprint_phase5

    def _cleanup_phase5_blueprint_map(self) -> None:
        """
        Best-effort cleanup for the retained Phase 5 blueprint map.

        Returns:
            None.
        """
        blueprint_map = self._entire_dag_blueprint_phase5
        if blueprint_map is None:
            return
        for blueprint in list(blueprint_map.values()):
            if blueprint is None:
                continue
            try:
                blueprint.cleanup()
            except Exception:
                pass
        try:
            blueprint_map.clear()
        except Exception:
            pass
