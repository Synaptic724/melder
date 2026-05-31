"""Unit tests for the scaffolded Phase 12 processor/codegen-plan surface."""

from types import SimpleNamespace
from typing import Any

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_builder import (
    SpellArtifactProcessorBuilder,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_codegen_model import (
    SpellCodegenModel,
)
from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_plan import (
    SpellCodegenPlan,
)
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_12 import (
    CompilerPhase12,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


def _seed_artifact(artifact: SpellCompilerArtifact) -> None:
    """Populate the artifact with the minimum meaningful Phase 12 input surface."""
    artifact._requirements = object()
    artifact._requirements_shape_profile_phase1 = {"parameter_count": 3}
    artifact._symbolic_graph = object()
    artifact._resolution_frame = object()
    artifact._validation_result_phase4 = object()
    artifact._validated_phase4 = True
    artifact._validation_result_phase6 = object()
    artifact._validated_phase6 = True
    artifact._validated = True
    artifact._root_blueprint_phase5 = SimpleNamespace()
    artifact._entire_dag_blueprint_phase5 = {"spell-1": object()}
    artifact._spell_system_index_phase5 = object()
    artifact._requires_spellspace_request_phase5 = False
    artifact._occurrence_plan_phase8 = object()
    artifact._occurrence_shape_profile_phase8 = {
        "unique_spell_count": 5,
        "shared_spell_count": 1,
        "max_occurrence_depth": 4,
        "max_width": 2,
    }
    artifact._phase8_occurrence_plan_input_signature = "occ-sig"
    artifact._phase8_occurrence_plan_fast_key = ("occ-fast",)
    artifact._injection_plan_phase9 = object()
    artifact._injection_shape_profile_phase9 = {"instance_spec_count": 2}
    artifact._phase9_injection_plan_input_signature = "inj-sig"
    artifact._override_patch_map_phase10 = object()
    artifact._mutation_patch_map_phase10 = object()
    artifact._override_shape_profile_phase10 = {"target_spec_count": 4}
    artifact._phase10_patch_maps_input_signature = ("patch-fast",)
    root_spell = SimpleNamespace(
        existence=Existence.unique_per_conduit,
    )
    root_step = SimpleNamespace(
        instance_key=("spell-1", 0),
        dependency_keys=[("dep-1", 0), ("dep-2", 0)],
        existence=Existence.unique_per_conduit,
        spell=root_spell,
    )
    artifact._execution_plan_phase11 = object()
    artifact._execution_plan_phase11_overrides = object()
    artifact._execution_plan_phase11_no_overrides = SimpleNamespace(
        fast_transient_plan=None,
        root_instance_key=("spell-1", 0),
        steps=(root_step,),
    )
    artifact._execution_plan_step_count_phase11 = 9
    artifact._execution_plan_unique_spell_count_phase11 = 5
    artifact._execution_plan_max_occurrence_depth_phase11 = 4
    artifact._execution_plan_max_dependency_count_phase11 = 3
    artifact._execution_plan_has_calln_phase11 = False
    artifact._execution_plan_has_contract_payloads_phase11 = True
    artifact._execution_plan_has_existing_creations_phase11 = False
    artifact._execution_shape_profile_phase11 = {
        "spell_lock_step_count": 0,
        "must_register_count": 2,
    }
    artifact._phase11_no_overrides_plan_signature = "plan-sig"
    artifact._phase11_no_overrides_transient_schema = {"schema": 1}
    artifact._phase13_no_overrides_executor = object()
    artifact._phase13_no_overrides_executor_signature = "executor-sig"
    artifact._phase11_no_overrides_input_signature = "phase11-input"
    artifact._phase11_no_overrides_fast_key = ("phase11-fast",)
    artifact._codegen_ir = {"phase8_11": {"execution": {}}}
    artifact._phase8_11_codegen_ir_dirty = False


def test_phase12_processor_consumes_full_artifact_surface() -> None:
    """Phase 12 processor should expose all grouped spell/artifact sections."""
    artifact = SpellCompilerArtifact("spell-1")
    _seed_artifact(artifact)

    processor = SpellArtifactProcessorBuilder(
        strategies=(),
    ).build()
    state = processor.process(artifact)

    assert isinstance(state, SpellCodegenModel)
    assert state.build_kind == "construct"
    assert state.existence is Existence.unique_per_conduit
    assert state.route_family == "unique_per_conduit"
    assert state.node_count == 5
    assert state.root_dependency_count == 2
    assert state.max_depth == 4
    assert state.max_width == 0 or state.max_width == 2
    assert state.max_dependency_count == 3
    assert state.has_calln is False
    assert state.contract_payload_count == 0
    assert state.target_spec_count == 4
    assert state.fast_transient_eligible is False


def test_phase12_run_stores_processor_state_and_codegen_plan() -> None:
    """Phase 12 should store the scaffolded processor state and plan on the artifact."""
    phase = CompilerPhase12()
    artifact = SpellCompilerArtifact("spell-1")
    _seed_artifact(artifact)
    spell = SimpleNamespace()
    spellbook = SimpleNamespace()

    phase.run(spellbook, spell, artifact)

    assert isinstance(artifact._phase12_processor_state, SpellCodegenModel)
    assert isinstance(artifact._phase12_codegen_plan, SpellCodegenPlan)
    assert artifact._phase12_codegen_plan.route_key == "unique_per_conduit"
    assert artifact._phase12_codegen_plan.supports_no_overrides_lane is True
    assert artifact._phase12_codegen_plan.supports_overrides_lane is True
    assert artifact._phase12_codegen_plan.supports_mutation_lane is True
    assert artifact._phase12_codegen_plan.no_overrides_family == "shared_dag_plan"
    assert artifact._phase12_codegen_plan.processor_strategy_ids == ()


def test_phase12_processor_builder_constructs_processor_with_registry() -> None:
    """The processor builder should only act as a strategy-registry factory."""
    processor_builder = SpellArtifactProcessorBuilder(
        strategies=(),
    )

    processor = processor_builder.build()

    assert processor is not None


def test_phase12_artifacts_clear_when_phase11_artifacts_clear() -> None:
    """Phase 12 outputs should clear with the Phase 11 cleanup path."""
    phase = CompilerPhase12()
    artifact = SpellCompilerArtifact("spell-1")
    _seed_artifact(artifact)
    spell = SimpleNamespace()
    spellbook = SimpleNamespace()
    phase.run(spellbook, spell, artifact)

    artifact._cleanup_execution_plans_phase11()

    assert artifact._phase12_processor_state is None
    assert artifact._phase12_codegen_plan is None
