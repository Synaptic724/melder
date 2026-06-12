"""Unit tests for current-surface `SpellCompiler` delegation."""

from typing import Any, Callable

import pytest

from melder.aether.spellbook.spell_compiler.spell_compiler import SpellCompiler
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
    make_spellbook,
)


def test_compiler_initializes_live_phase_surfaces_1_through_11() -> None:
    """SpellCompiler should own the current live phase-1-to-phase-11 surfaces only."""
    compiler = SpellCompiler()

    assert compiler._phase_1 is not None
    assert compiler._phase_2 is not None
    assert compiler._phase_3 is not None
    assert compiler._phase_4 is not None
    assert compiler._phase_5 is not None
    assert compiler._phase_6 is not None
    assert compiler._phase_7 is not None
    assert compiler._phase_8 is not None
    assert compiler._phase_9 is not None
    assert compiler._phase_10 is not None
    assert compiler._phase_11 is not None
    assert not hasattr(compiler, "_phase_12")
    assert not hasattr(compiler, "_phase_13")


def test_compiler_phase_methods_delegate_to_current_phase_surfaces(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each compiler method should delegate to the current phase surface with the current signature."""
    compiler = SpellCompiler()
    spell = make_spell()
    artifact = spell._compiler_artifact
    spellbook = make_spellbook()
    spell_system_states = spellbook._spell_system_states
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def _record(name: str) -> Callable[..., None]:
        """Build one recorder callable for the delegated phase entry."""
        return lambda *args, **kwargs: calls.append((name, args, kwargs))

    compiler._phase_1 = type("_Phase1Stub", (), {"run": staticmethod(_record("phase1"))})()
    compiler._phase_2 = type("_Phase2Stub", (), {"run": staticmethod(_record("phase2"))})()
    compiler._phase_3 = type("_Phase3Stub", (), {"run": staticmethod(_record("phase3"))})()
    compiler._phase_4 = type("_Phase4Stub", (), {"run": staticmethod(_record("phase4"))})()
    compiler._phase_5 = type(
        "_Phase5Stub",
        (),
        {
            "run_frame_wide": staticmethod(_record("phase5_frame")),
            "run_local": staticmethod(_record("phase5_local")),
        },
    )()
    compiler._phase_6 = type(
        "_Phase6Stub",
        (),
        {
            "run_frame_wide": staticmethod(_record("phase6_frame")),
            "run_local": staticmethod(_record("phase6_local")),
        },
    )()
    compiler._phase_7 = type(
        "_Phase7Stub",
        (),
        {
            "run_frame_wide": staticmethod(_record("phase7_frame")),
            "run_local": staticmethod(_record("phase7_local")),
        },
    )()
    compiler._phase_8 = type("_Phase8Stub", (), {"run": staticmethod(_record("phase8"))})()
    compiler._phase_9 = type("_Phase9Stub", (), {"run": staticmethod(_record("phase9"))})()
    compiler._phase_10 = type("_Phase10Stub", (), {"run": staticmethod(_record("phase10"))})()
    compiler._phase_11 = type("_Phase11Stub", (), {"run": staticmethod(_record("phase11"))})()

    compiler.run_phase_requirements(spell, artifact, cancel_event="cancel")
    compiler.run_phase_symbolic_graph(spell, artifact, cancel_event="cancel")
    compiler.run_phase_local_frame(
        spell,
        artifact,
        spellbook,
        spell_system_states,
        cancel_event="cancel",
    )
    compiler.run_phase_validation(
        spell,
        artifact,
        "validator",
        spell_system_states,
        cancel_event="cancel",
    )
    compiler.run_phase_root_blueprints(
        spell,
        artifact,
        spellbook,
        spell_system_states,
        "cid",
        cancel_event="cancel",
    )
    compiler.run_phase_root_blueprints_local(
        spell,
        artifact,
        spellbook,
        spell_system_states,
        "cid",
        cancel_event="cancel",
    )
    compiler.run_phase_system_validation(
        artifact,
        spellbook,
        spell_system_states,
        "cid",
        cancel_event="cancel",
    )
    compiler.run_phase_system_validation_local(
        spell,
        artifact,
        spellbook,
        spell_system_states,
        "cid",
        cancel_event="cancel",
    )
    compiler.run_phase_change_control(artifact, spellbook, "cid")
    compiler.run_phase_change_control_local(artifact, spellbook, "cid")
    compiler.run_phase_occurrence_plan(spell, artifact, spellbook, spell_system_states)
    compiler.run_phase_injection_plan(spell, artifact)
    compiler.run_phase_patch_maps(spell, artifact)
    compiler.run_phase_execution_plan(spell, artifact, spellbook)

    assert calls == [
        ("phase1", (spell, artifact), {"cancel_event": "cancel"}),
        ("phase2", (spell, artifact), {"cancel_event": "cancel"}),
        ("phase3", (spell, artifact, spellbook, spell_system_states), {"cancel_event": "cancel"}),
        ("phase4", (spell, artifact, "validator", spell_system_states), {"cancel_event": "cancel", "validation_pass_cache": None}),
        ("phase5_frame", (spell, artifact, spellbook, spell_system_states, "cid"), {"cancel_event": "cancel"}),
        ("phase5_local", (spell, artifact, spellbook, spell_system_states, "cid"), {"cancel_event": "cancel"}),
        ("phase6_frame", (artifact, spellbook, spell_system_states, "cid"), {"cancel_event": "cancel"}),
        ("phase6_local", (spell, artifact, spellbook, spell_system_states, "cid"), {"cancel_event": "cancel"}),
        ("phase7_frame", (artifact, spellbook, "cid"), {}),
        ("phase7_local", (artifact, spellbook, "cid"), {}),
        ("phase8", (spell, artifact, spellbook, spell_system_states), {}),
        ("phase9", (spell, artifact), {}),
        ("phase10", (spell, artifact), {}),
        ("phase11", (spell, artifact, spellbook), {}),
    ]
