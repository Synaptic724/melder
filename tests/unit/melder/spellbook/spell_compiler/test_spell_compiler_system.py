"""Unit tests for SpellCompilerSystem current-surface façade behavior."""

from typing import Any

import pytest

from melder.aether.spellbook.spell_compiler.spell_compiler import SpellCompiler
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spell_compiler.validation.validation_system import (
    SpellValidationSystem,
)
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
    make_spellbook,
)


def test_system_initializes_owned_compiler_and_validator() -> None:
    """SpellCompilerSystem should own the current compiler and validator collaborators."""
    compiler_system = SpellCompilerSystem()

    assert isinstance(compiler_system._spell_compiler, SpellCompiler)
    assert isinstance(compiler_system._spell_validator, SpellValidationSystem)


def test_system_cleanup_drops_owned_surfaces() -> None:
    """Cleanup should delete the owned compiler and validator surfaces."""
    compiler_system = SpellCompilerSystem()

    compiler_system.cleanup()

    assert not hasattr(compiler_system, "_spell_compiler")
    assert not hasattr(compiler_system, "_spell_validator")


def test_run_phase_requirements_uses_spell_owned_artifact(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 1 façade should pass the spell-owned artifact to SpellCompiler."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell()
    calls: list[tuple[Any, ...]] = []

    compiler_system._spell_compiler = type(
        "_CompilerStub",
        (),
        {
            "run_phase_requirements": staticmethod(
                lambda spell, artifact, cancel_event=None: calls.append(
                    (spell, artifact, cancel_event)
                )
            )
        },
    )

    compiler_system.run_phase_requirements(spell, cancel_event="cancel")

    assert calls == [(spell, spell._compiler_artifact, "cancel")]


def test_run_phase_validation_uses_owned_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 4 façade should pass the system-owned validator to SpellCompiler."""
    compiler_system = SpellCompilerSystem()
    spellbook = make_spellbook()
    spell = make_spell()
    calls: list[tuple[Any, ...]] = []

    compiler_system._spell_compiler = type(
        "_CompilerStub",
        (),
        {
            "run_phase_validation": staticmethod(
                lambda spell, artifact, validator, spell_system_states, cancel_event=None, validation_pass_cache=None: calls.append(
                    (spell, artifact, validator, spell_system_states, cancel_event)
                )
            )
        },
    )

    compiler_system.run_phase_validation(spellbook, spell, cancel_event="cancel")

    assert calls == [
        (
            spell,
            spell._compiler_artifact,
            compiler_system._spell_validator,
            spellbook._spell_system_states,
            "cancel",
        )
    ]


def test_get_local_resolution_scoped_spell_ids_includes_self_and_index_nodes() -> None:
    """Local spell scope should include the target spell plus local index nodes."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell("root")
    spell._compiler_artifact._spell_system_index_phase5 = type(
        "_Index",
        (),
        {
            "nodes": {
                "root": object(),
                "dep-a": object(),
                "dep-b": object(),
            }
        },
    )()

    assert compiler_system.get_local_resolution_scoped_spell_ids(spell) == {
        "root",
        "dep-a",
        "dep-b",
    }


def test_get_local_resolution_scoped_root_ids_falls_back_to_spell_id() -> None:
    """Local root scope should fall back to the target spell id when map is empty."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell("root")

    assert compiler_system.get_local_resolution_scoped_root_ids(spell) == ("root",)


def test_get_local_resolution_scoped_root_ids_uses_root_map_keys() -> None:
    """Local root scope should use the local rooted blueprint map keys when present."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell("root")
    spell._compiler_artifact._entire_dag_blueprint_phase5 = {
        "root-a": object(),
        "root-b": object(),
    }

    assert compiler_system.get_local_resolution_scoped_root_ids(spell) == (
        "root-a",
        "root-b",
    )


def test_is_current_spell_phase5_root_returns_true_for_matching_root() -> None:
    """Root identity helper should return True for matching blueprint root ids."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell("root")
    spell._compiler_artifact._root_blueprint_phase5 = type(
        "_RootBlueprint",
        (),
        {"root_spell_id": "root"},
    )()

    assert compiler_system.is_current_spell_phase5_root(spell) is True


def test_is_current_spell_phase5_root_returns_false_without_matching_root() -> None:
    """Root identity helper should return False when blueprint is missing or mismatched."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell("root")

    assert compiler_system.is_current_spell_phase5_root(spell) is False

    spell._compiler_artifact._root_blueprint_phase5 = type(
        "_RootBlueprint",
        (),
        {"root_spell_id": "other"},
    )()

    assert compiler_system.is_current_spell_phase5_root(spell) is False


def test_reset_phase_artifacts_delegates_to_artifact(monkeypatch: pytest.MonkeyPatch) -> None:
    """reset_phase_artifacts should forward directly to the spell-owned artifact."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell()
    calls: list[str] = []

    monkeypatch.setattr(
        SpellCompilerArtifact,
        "reset_phase_artifacts",
        lambda self: calls.append("reset"),
    )

    compiler_system.reset_phase_artifacts(spell)

    assert calls == ["reset"]


def test_cleanup_phase_artifacts_alias_delegates_to_artifact(monkeypatch: pytest.MonkeyPatch) -> None:
    """cleanup_phase_artifacts should forward to the artifact alias surface."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell()
    calls: list[str] = []

    monkeypatch.setattr(
        SpellCompilerArtifact,
        "cleanup_phase_artifacts",
        lambda self: calls.append("cleanup"),
    )

    compiler_system.cleanup_phase_artifacts(spell)

    assert calls == ["cleanup"]


def test_clear_phase5_artifacts_delegates_to_artifact(monkeypatch: pytest.MonkeyPatch) -> None:
    """clear_phase5_artifacts should delegate to the spell-owned artifact."""
    compiler_system = SpellCompilerSystem()
    spell = make_spell()
    spell.requires_spellspace_request = True
    calls: list[str] = []

    monkeypatch.setattr(
        SpellCompilerArtifact,
        "clear_phase5_artifacts",
        lambda self: calls.append("clear"),
    )

    compiler_system.clear_phase5_artifacts(spell)

    assert calls == ["clear"]
    assert spell.requires_spellspace_request is False


def test_run_structural_phases_calls_phases_1_to_4_in_order(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Structural helper should call phases 1 to 4 in order."""
    compiler_system = SpellCompilerSystem()
    spellbook = make_spellbook()
    spell = make_spell()
    call_order: list[str] = []

    monkeypatch.setattr(SpellCompilerSystem, "run_phase_requirements", lambda self, spell, cancel_event=None: call_order.append("phase1"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_symbolic_graph", lambda self, spell, cancel_event=None: call_order.append("phase2"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_local_frame", lambda self, spellbook, spell, cancel_event=None: call_order.append("phase3"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_validation", lambda self, spellbook, spell, cancel_event=None: call_order.append("phase4"))

    compiler_system.run_structural_phases(spellbook, spell, cancel_event="cancel")

    assert call_order == ["phase1", "phase2", "phase3", "phase4"]


def test_run_all_phases_calls_phases_1_to_11_in_order(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full helper should call phases 1 to 11 in documented order."""
    compiler_system = SpellCompilerSystem()
    spellbook = make_spellbook()
    spell = make_spell()
    call_order: list[str] = []

    monkeypatch.setattr(SpellCompilerSystem, "run_phase_requirements", lambda self, spell, cancel_event=None: call_order.append("phase1"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_symbolic_graph", lambda self, spell, cancel_event=None: call_order.append("phase2"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_local_frame", lambda self, spellbook, spell, cancel_event=None: call_order.append("phase3"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_validation", lambda self, spellbook, spell, cancel_event=None: call_order.append("phase4"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_root_blueprints", lambda self, spellbook, spell, conduit_id, cancel_event=None: call_order.append("phase5"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_system_validation", lambda self, spellbook, spell, conduit_id, cancel_event=None: call_order.append("phase6"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_change_control", lambda self, spellbook, spell, conduit_id: call_order.append("phase7"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_occurrence_plan", lambda self, spellbook, spell: call_order.append("phase8"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_injection_plan", lambda self, spell: call_order.append("phase9"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_patch_maps", lambda self, spell: call_order.append("phase10"))
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_execution_plan", lambda self, spellbook, spell: call_order.append("phase11"))

    compiler_system.run_all_phases(spellbook, spell, "cid", cancel_event="cancel")

    assert call_order == [
        "phase1",
        "phase2",
        "phase3",
        "phase4",
        "phase5",
        "phase6",
        "phase7",
        "phase8",
        "phase9",
        "phase10",
        "phase11",
    ]


def test_run_all_phases_cleans_structural_artifacts_and_creation_context(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full helper should cleanup structural artifacts and spell creation context at the end."""
    compiler_system = SpellCompilerSystem()
    spellbook = make_spellbook()
    spell = make_spell()
    artifact_calls: list[str] = []

    monkeypatch.setattr(SpellCompilerSystem, "run_phase_requirements", lambda self, spell, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_symbolic_graph", lambda self, spell, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_local_frame", lambda self, spellbook, spell, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_validation", lambda self, spellbook, spell, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_root_blueprints", lambda self, spellbook, spell, conduit_id, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_system_validation", lambda self, spellbook, spell, conduit_id, cancel_event=None: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_change_control", lambda self, spellbook, spell, conduit_id: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_occurrence_plan", lambda self, spellbook, spell: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_injection_plan", lambda self, spell: None)
    monkeypatch.setattr(SpellCompilerSystem, "run_phase_patch_maps", lambda self, spell: None)
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_execution_plan",
        lambda self, spellbook, spell: spell._cleanup_creation_context(),
    )
    monkeypatch.setattr(
        SpellCompilerArtifact,
        "cleanup_phase_artifacts",
        lambda self: artifact_calls.append("artifact"),
    )

    compiler_system.run_all_phases(spellbook, spell, "cid", cancel_event="cancel")

    assert artifact_calls == ["artifact"]
    assert spell._cleanup_creation_context_calls == ["cleanup"]


def test_run_all_phases_forwards_cancel_event_to_supported_phases(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Full helper should forward one cancel event to every phase that accepts it."""
    compiler_system = SpellCompilerSystem()
    spellbook = make_spellbook()
    spell = make_spell()
    cancel = object()
    received: list[tuple[str, Any]] = []

    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_requirements",
        lambda self, spell, cancel_event=None: received.append(("phase1", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_symbolic_graph",
        lambda self, spell, cancel_event=None: received.append(("phase2", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_local_frame",
        lambda self, spellbook, spell, cancel_event=None: received.append(("phase3", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_validation",
        lambda self, spellbook, spell, cancel_event=None: received.append(("phase4", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_root_blueprints",
        lambda self, spellbook, spell, conduit_id, cancel_event=None: received.append(("phase5", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_system_validation",
        lambda self, spellbook, spell, conduit_id, cancel_event=None: received.append(("phase6", cancel_event)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_change_control",
        lambda self, spellbook, spell, conduit_id: received.append(("phase7", None)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_occurrence_plan",
        lambda self, spellbook, spell: received.append(("phase8", None)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_injection_plan",
        lambda self, spell: received.append(("phase9", None)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_patch_maps",
        lambda self, spell: received.append(("phase10", None)),
    )
    monkeypatch.setattr(
        SpellCompilerSystem,
        "run_phase_execution_plan",
        lambda self, spellbook, spell: received.append(("phase11", None)),
    )
    monkeypatch.setattr(
        SpellCompilerArtifact,
        "cleanup_phase_artifacts",
        lambda self: None,
    )

    compiler_system.run_all_phases(spellbook, spell, "cid", cancel_event=cancel)

    assert received == [
        ("phase1", cancel),
        ("phase2", cancel),
        ("phase3", cancel),
        ("phase4", cancel),
        ("phase5", cancel),
        ("phase6", cancel),
        ("phase7", None),
        ("phase8", None),
        ("phase9", None),
        ("phase10", None),
        ("phase11", None),
    ]
