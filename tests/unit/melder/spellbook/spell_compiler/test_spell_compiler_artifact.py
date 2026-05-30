"""Unit tests for SpellCompilerArtifact current-surface lifecycle semantics."""

import pytest

from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    CleanupTracker,
)


def test_artifact_rejects_empty_spell_id() -> None:
    """Artifact construction should reject an empty spell identifier."""
    with pytest.raises(ValueError, match="spell_id cannot be empty"):
        SpellCompilerArtifact("")


def test_artifact_stores_spell_id() -> None:
    """Artifact should retain the owning spell identifier."""
    artifact = SpellCompilerArtifact("spell-1")

    assert artifact.spell_id == "spell-1"


def test_artifact_structural_fields_start_empty() -> None:
    """Structural phase fields should start empty."""
    artifact = SpellCompilerArtifact("spell-1")

    assert artifact._requirements is None
    assert artifact._symbolic_graph is None
    assert artifact._resolution_frame is None
    assert artifact._validation_result_phase4 is None
    assert artifact._validation_result_phase6 is None
    assert artifact._validated_phase4 is False
    assert artifact._validated_phase6 is False
    assert artifact._validated is False
    assert artifact._is_broken is False


def test_artifact_later_phase_fields_start_empty() -> None:
    """Later phase fields should start empty."""
    artifact = SpellCompilerArtifact("spell-1")

    assert artifact._root_blueprint_phase5 is None
    assert artifact._requires_spellspace_request_phase5 is False
    assert artifact._occurrence_plan_phase8 is None
    assert artifact._injection_plan_phase9 is None
    assert artifact._override_patch_map_phase10 is None
    assert artifact._mutation_patch_map_phase10 is None
    assert artifact._execution_plan_phase11 is None
    assert artifact._execution_plan_phase11_no_overrides is None
    assert artifact._execution_plan_phase11_overrides is None
    assert artifact._phase13_no_overrides_executor is None
    assert artifact._spell_system_index_phase5 is None
    assert artifact._entire_dag_blueprint_phase5 is None
    assert artifact._phase8_11_codegen_ir_dirty is False


@pytest.mark.parametrize(
    "field_name",
    [
        "_requirements",
        "_symbolic_graph",
        "_resolution_frame",
        "_validation_result_phase4",
        "_validation_result_phase6",
        "_root_blueprint_phase5",
        "_occurrence_plan_phase8",
        "_injection_plan_phase9",
        "_override_patch_map_phase10",
        "_mutation_patch_map_phase10",
        "_execution_plan_phase11",
        "_execution_plan_phase11_no_overrides",
        "_execution_plan_phase11_overrides",
        "_spell_system_index_phase5",
    ],
)
def test_cleanup_calls_cleanup_on_owned_single_artifact_fields(
        field_name: str,
) -> None:
    """Cleanup should call cleanup once for every single owned artifact field."""
    artifact = SpellCompilerArtifact("spell-1")
    child = CleanupTracker()
    setattr(artifact, field_name, child)

    artifact.cleanup()

    assert child.cleanup_calls == 1


def test_cleanup_calls_cleanup_on_entire_dag_blueprint_map_values() -> None:
    """Cleanup should cleanup each blueprint stored in the full root map."""
    artifact = SpellCompilerArtifact("spell-1")
    root_a = CleanupTracker()
    root_b = CleanupTracker()
    artifact._entire_dag_blueprint_phase5 = {
        "root-a": root_a,
        "root-b": root_b,
    }

    artifact.cleanup()

    assert root_a.cleanup_calls == 1
    assert root_b.cleanup_calls == 1


def test_cleanup_swallows_child_cleanup_exceptions() -> None:
    """Cleanup should continue even when owned child cleanup raises."""
    artifact = SpellCompilerArtifact("spell-1")

    class _FailingCleanupTracker(CleanupTracker):
        """Cleanup tracker that raises after recording cleanup."""

        def cleanup(self) -> None:
            self.cleanup_calls += 1
            self._cleaned = True
            raise RuntimeError("cleanup boom")

    requirements = _FailingCleanupTracker()
    root_blueprint = _FailingCleanupTracker()
    dag_blueprint = _FailingCleanupTracker()
    artifact._requirements = requirements
    artifact._root_blueprint_phase5 = root_blueprint
    artifact._entire_dag_blueprint_phase5 = {"root": dag_blueprint}

    artifact.cleanup()

    assert artifact._cleaned is True
    assert requirements.cleanup_calls == 1
    assert root_blueprint.cleanup_calls == 1
    assert dag_blueprint.cleanup_calls == 1


def test_cleanup_deletes_spell_identity_and_later_phase_fields() -> None:
    """Cleanup should delete identity and later-phase owned fields."""
    artifact = SpellCompilerArtifact("spell-1")

    artifact.cleanup()

    assert not hasattr(artifact, "spell_id")
    assert not hasattr(artifact, "_root_blueprint_phase5")
    assert not hasattr(artifact, "_occurrence_plan_phase8")
    assert not hasattr(artifact, "_injection_plan_phase9")
    assert not hasattr(artifact, "_override_patch_map_phase10")
    assert not hasattr(artifact, "_mutation_patch_map_phase10")
    assert not hasattr(artifact, "_execution_plan_phase11")
    assert not hasattr(artifact, "_execution_plan_phase11_no_overrides")
    assert not hasattr(artifact, "_execution_plan_phase11_overrides")
    assert not hasattr(artifact, "_spell_system_index_phase5")


def test_cleanup_is_idempotent_for_owned_children() -> None:
    """Repeated cleanup should not re-clean owned child artifacts."""
    artifact = SpellCompilerArtifact("spell-1")
    child = CleanupTracker()
    artifact._requirements = child

    artifact.cleanup()
    artifact.cleanup()

    assert child.cleanup_calls == 1


def test_reset_phase_artifacts_clears_structural_fields_only() -> None:
    """Reset should clear structural-validation fields while preserving later state."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._requirements = object()
    artifact._symbolic_graph = object()
    artifact._resolution_frame = object()
    artifact._validation_result_phase4 = object()
    artifact._validation_result_phase6 = object()
    artifact._root_blueprint_phase5 = object()
    artifact._occurrence_plan_phase8 = object()

    artifact.reset_phase_artifacts()

    assert artifact._requirements is None
    assert artifact._symbolic_graph is None
    assert artifact._resolution_frame is None
    assert artifact._validation_result_phase4 is None
    assert artifact._validation_result_phase6 is None
    assert artifact._root_blueprint_phase5 is not None
    assert artifact._occurrence_plan_phase8 is not None


def test_cleanup_phase_artifacts_alias_matches_reset_phase_artifacts() -> None:
    """cleanup_phase_artifacts should behave as the structural reset alias."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._requirements = object()
    artifact._root_blueprint_phase5 = object()

    artifact.cleanup_phase_artifacts()

    assert artifact._requirements is None
    assert artifact._root_blueprint_phase5 is not None


def test_clear_phase5_artifacts_clears_rooted_and_later_state() -> None:
    """clear_phase5_artifacts should clear rooted and later-plan state."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = object()
    artifact._requires_spellspace_request_phase5 = True
    artifact._phase8_occurrence_plan_input_signature = "phase8"
    artifact._phase9_injection_plan_input_signature = "phase9"
    artifact._phase10_patch_maps_input_signature = ("phase10",)
    artifact._occurrence_plan_phase8 = CleanupTracker()
    artifact._injection_plan_phase9 = CleanupTracker()
    artifact._override_patch_map_phase10 = CleanupTracker()
    artifact._mutation_patch_map_phase10 = CleanupTracker()
    artifact._execution_plan_phase11 = CleanupTracker()
    artifact._execution_plan_phase11_no_overrides = CleanupTracker()
    artifact._execution_plan_phase11_overrides = CleanupTracker()
    artifact._spell_system_index_phase5 = object()
    artifact._phase13_no_overrides_executor = object()
    artifact._phase11_no_overrides_input_signature = "phase11"

    artifact.clear_phase5_artifacts()

    assert artifact._root_blueprint_phase5 is None
    assert artifact._requires_spellspace_request_phase5 is False
    assert artifact._phase8_occurrence_plan_input_signature is None
    assert artifact._phase9_injection_plan_input_signature is None
    assert artifact._phase10_patch_maps_input_signature is None
    assert artifact._occurrence_plan_phase8 is None
    assert artifact._injection_plan_phase9 is None
    assert artifact._override_patch_map_phase10 is None
    assert artifact._mutation_patch_map_phase10 is None
    assert artifact._execution_plan_phase11 is None
    assert artifact._execution_plan_phase11_no_overrides is None
    assert artifact._execution_plan_phase11_overrides is None
    assert artifact._spell_system_index_phase5 is None
    assert artifact._phase13_no_overrides_executor is None
    assert artifact._phase11_no_overrides_input_signature is None


def test_clear_phase5_artifacts_preserves_structural_fields() -> None:
    """clear_phase5_artifacts should not clear structural-validation state."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._requirements = "req"
    artifact._symbolic_graph = "sym"
    artifact._resolution_frame = "frame"
    artifact._validation_result_phase4 = "phase4"
    artifact._validation_result_phase6 = "phase6"

    artifact.clear_phase5_artifacts()

    assert artifact._requirements == "req"
    assert artifact._symbolic_graph == "sym"
    assert artifact._resolution_frame == "frame"
    assert artifact._validation_result_phase4 == "phase4"
    assert artifact._validation_result_phase6 == "phase6"


def test_cleanup_execution_plans_phase11_cleans_variants_and_clears_fields() -> None:
    """Phase 11 cleanup helper should clean all cached plans and clear their refs."""
    artifact = SpellCompilerArtifact("spell-1")
    main = CleanupTracker()
    no_overrides = CleanupTracker()
    overrides = CleanupTracker()
    artifact._execution_plan_phase11 = main
    artifact._execution_plan_phase11_no_overrides = no_overrides
    artifact._execution_plan_phase11_overrides = overrides
    artifact._phase11_no_overrides_plan_signature = "sig"
    artifact._phase11_no_overrides_transient_schema = {"schema": 1}

    artifact._cleanup_execution_plans_phase11()

    assert main.cleanup_calls == 1
    assert no_overrides.cleanup_calls == 1
    assert overrides.cleanup_calls == 1
    assert artifact._execution_plan_phase11 is None
    assert artifact._execution_plan_phase11_no_overrides is None
    assert artifact._execution_plan_phase11_overrides is None
    assert artifact._phase11_no_overrides_plan_signature is None
    assert artifact._phase11_no_overrides_transient_schema is None


def test_cleanup_execution_plans_phase11_swallows_cleanup_failures() -> None:
    """Phase 11 cleanup helper should swallow per-plan cleanup failures."""
    artifact = SpellCompilerArtifact("spell-1")

    class _FailingCleanupTracker(CleanupTracker):
        """Cleanup tracker that raises after recording cleanup."""

        def cleanup(self) -> None:
            self.cleanup_calls += 1
            self._cleaned = True
            raise RuntimeError("cleanup boom")

    main = _FailingCleanupTracker()
    overrides = _FailingCleanupTracker()
    artifact._execution_plan_phase11 = main
    artifact._execution_plan_phase11_overrides = overrides

    artifact._cleanup_execution_plans_phase11()

    assert main.cleanup_calls == 1
    assert overrides.cleanup_calls == 1
    assert artifact._execution_plan_phase11 is None
    assert artifact._execution_plan_phase11_overrides is None

