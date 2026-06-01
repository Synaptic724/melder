"""Unit tests for current-surface `SpellCompilerArtifact` lifecycle semantics."""

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


def test_artifact_later_fields_start_empty() -> None:
    """Later compiler fields should start empty under the current model/plan/creation surface."""
    artifact = SpellCompilerArtifact("spell-1")

    assert artifact._root_blueprint_phase5 is None
    assert artifact._requires_spellspace_request_phase5 is False
    assert artifact._occurrence_graph_analysis is None
    assert artifact._occurrence_order_analysis is None
    assert artifact._occurrence_instance_analysis is None
    assert artifact._occurrence_contract_analysis is None
    assert artifact._spell_codegen_model is None
    assert artifact._spell_codegen_plan is None
    assert artifact._spell_codegen_creation is None
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
        "_spell_system_index_phase5",
        "_occurrence_graph_analysis",
        "_occurrence_order_analysis",
        "_occurrence_instance_analysis",
        "_occurrence_contract_analysis",
        "_spell_codegen_model",
        "_spell_codegen_plan",
        "_spell_codegen_creation",
    ],
)
def test_cleanup_calls_cleanup_on_owned_artifact_fields(field_name: str) -> None:
    """Cleanup should call cleanup once for each owned artifact field that exposes it."""
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


def test_cleanup_deletes_current_later_fields() -> None:
    """Cleanup should delete the current later-phase and generic output fields."""
    artifact = SpellCompilerArtifact("spell-1")

    artifact.cleanup()

    assert not hasattr(artifact, "spell_id")
    assert not hasattr(artifact, "_root_blueprint_phase5")
    assert not hasattr(artifact, "_occurrence_graph_analysis")
    assert not hasattr(artifact, "_occurrence_order_analysis")
    assert not hasattr(artifact, "_occurrence_instance_analysis")
    assert not hasattr(artifact, "_occurrence_contract_analysis")
    assert not hasattr(artifact, "_spell_codegen_model")
    assert not hasattr(artifact, "_spell_codegen_plan")
    assert not hasattr(artifact, "_spell_codegen_creation")
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
    """Reset should clear structural-validation fields while preserving rooted and later state."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._requirements = CleanupTracker()
    artifact._symbolic_graph = CleanupTracker()
    artifact._resolution_frame = CleanupTracker()
    artifact._validation_result_phase4 = CleanupTracker()
    artifact._validation_result_phase6 = CleanupTracker()
    artifact._root_blueprint_phase5 = object()
    artifact._spell_codegen_model = object()

    artifact.reset_phase_artifacts()

    assert artifact._requirements is None
    assert artifact._symbolic_graph is None
    assert artifact._resolution_frame is None
    assert artifact._validation_result_phase4 is None
    assert artifact._validation_result_phase6 is None
    assert artifact._root_blueprint_phase5 is not None
    assert artifact._spell_codegen_model is not None


def test_cleanup_phase_artifacts_alias_matches_reset_phase_artifacts() -> None:
    """cleanup_phase_artifacts should behave as the structural reset alias."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._requirements = CleanupTracker()
    artifact._root_blueprint_phase5 = object()

    artifact.cleanup_phase_artifacts()

    assert artifact._requirements is None
    assert artifact._root_blueprint_phase5 is not None


def test_clear_phase5_artifacts_clears_rooted_occurrence_and_codegen_outputs() -> None:
    """clear_phase5_artifacts should clear rooted state, occurrence analyses, and generic outputs."""
    artifact = SpellCompilerArtifact("spell-1")
    artifact._root_blueprint_phase5 = object()
    artifact._requires_spellspace_request_phase5 = True
    artifact._occurrence_analysis_input_signature = "occ"
    artifact._occurrence_analysis_fast_key = ("occ-fast",)
    artifact._occurrence_graph_analysis = CleanupTracker()
    artifact._occurrence_order_analysis = CleanupTracker()
    artifact._occurrence_instance_analysis = CleanupTracker()
    artifact._occurrence_contract_analysis = CleanupTracker()
    artifact._spell_codegen_model = CleanupTracker()
    artifact._spell_codegen_plan = CleanupTracker()
    artifact._spell_codegen_creation = CleanupTracker()
    artifact._spell_system_index_phase5 = object()

    artifact.clear_phase5_artifacts()

    assert artifact._root_blueprint_phase5 is None
    assert artifact._requires_spellspace_request_phase5 is False
    assert artifact._occurrence_analysis_input_signature is None
    assert artifact._occurrence_analysis_fast_key is None
    assert artifact._occurrence_graph_analysis is None
    assert artifact._occurrence_order_analysis is None
    assert artifact._occurrence_instance_analysis is None
    assert artifact._occurrence_contract_analysis is None
    assert artifact._spell_codegen_model is None
    assert artifact._spell_codegen_plan is None
    assert artifact._spell_codegen_creation is None
    assert artifact._spell_system_index_phase5 is None


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
