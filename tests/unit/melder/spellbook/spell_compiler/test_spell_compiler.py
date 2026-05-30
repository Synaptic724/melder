"""Unit tests for SpellCompiler current-surface phase delegation."""

from typing import Any

import pytest

from melder.aether.spellbook.spell_compiler.spell_compiler import SpellCompiler
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
    make_spellbook,
)


def test_compiler_initializes_all_phase_surfaces() -> None:
    """SpellCompiler should own one instantiated phase surface for phases 1-13."""
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
    assert compiler._phase_12 is not None
    assert compiler._phase_13 is not None


@pytest.mark.parametrize(
    ("method_name", "phase_attr", "args_builder", "kwargs_builder"),
    [
        ("run_phase_requirements", "_phase_1", lambda spell, spellbook: (spell, spell._compiler_artifact), lambda: {"cancel_event": "cancel"}),
        ("run_phase_symbolic_graph", "_phase_2", lambda spell, spellbook: (spell, spell._compiler_artifact), lambda: {"cancel_event": "cancel"}),
        ("run_phase_local_frame", "_phase_3", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states), lambda: {"cancel_event": "cancel"}),
        ("run_phase_validation", "_phase_4", lambda spell, spellbook: (spell, spell._compiler_artifact, "validator", spellbook._spell_system_states), lambda: {"cancel_event": "cancel"}),
        ("run_phase_root_blueprints", "_phase_5", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid"), lambda: {"cancel_event": "cancel"}),
        ("run_phase_root_blueprints_local", "_phase_5", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid"), lambda: {"cancel_event": "cancel"}),
        ("run_phase_system_validation", "_phase_6", lambda spell, spellbook: (spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid"), lambda: {"cancel_event": "cancel"}),
        ("run_phase_system_validation_local", "_phase_6", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid"), lambda: {"cancel_event": "cancel"}),
        ("run_phase_change_control", "_phase_7", lambda spell, spellbook: (spell._compiler_artifact, spellbook, "cid"), lambda: {}),
        ("run_phase_change_control_local", "_phase_7", lambda spell, spellbook: (spell._compiler_artifact, spellbook, "cid"), lambda: {}),
        ("run_phase_occurrence_plan", "_phase_8", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states), lambda: {}),
        ("run_phase_injection_plan", "_phase_9", lambda spell, spellbook: (spell, spell._compiler_artifact), lambda: {}),
        ("run_phase_patch_maps", "_phase_10", lambda spell, spellbook: (spell, spell._compiler_artifact), lambda: {}),
        ("run_phase_execution_plan", "_phase_11", lambda spell, spellbook: (spell, spell._compiler_artifact, spellbook), lambda: {}),
    ],
)
def test_compiler_phase_methods_delegate_to_the_expected_phase_surface(
        monkeypatch: pytest.MonkeyPatch,
        method_name: str,
        phase_attr: str,
        args_builder: Any,
        kwargs_builder: Any,
) -> None:
    """Each compiler method should delegate to the matching phase surface with current args."""
    compiler = SpellCompiler()
    spell = make_spell()
    spellbook = make_spellbook()
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    if method_name in ("run_phase_root_blueprints", "run_phase_system_validation", "run_phase_change_control"):
        phase_surface = type(
            "_PhaseStub",
            (),
            {
                "run_frame_wide": staticmethod(
                    lambda *args, **kwargs: calls.append((args, kwargs))
                ),
            },
        )()
    elif method_name in ("run_phase_root_blueprints_local", "run_phase_system_validation_local", "run_phase_change_control_local"):
        phase_surface = type(
            "_PhaseStub",
            (),
            {
                "run_local": staticmethod(
                    lambda *args, **kwargs: calls.append((args, kwargs))
                ),
            },
        )()
    else:
        phase_surface = type(
            "_PhaseStub",
            (),
            {
                "run": staticmethod(
                    lambda *args, **kwargs: calls.append((args, kwargs))
                ),
            },
        )()
    setattr(
        compiler,
        phase_attr,
        phase_surface,
    )

    method = getattr(compiler, method_name)
    if method_name == "run_phase_validation":
        method(spell, spell._compiler_artifact, "validator", spellbook._spell_system_states, cancel_event="cancel")
    elif method_name in ("run_phase_local_frame",):
        method(spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, cancel_event="cancel")
    elif method_name in ("run_phase_root_blueprints", "run_phase_root_blueprints_local"):
        method(spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid", cancel_event="cancel")
    elif method_name in ("run_phase_system_validation_local",):
        method(spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid", cancel_event="cancel")
    elif method_name in ("run_phase_system_validation",):
        method(spell._compiler_artifact, spellbook, spellbook._spell_system_states, "cid", cancel_event="cancel")
    elif method_name in ("run_phase_change_control", "run_phase_change_control_local"):
        method(spell._compiler_artifact, spellbook, "cid")
    elif method_name == "run_phase_occurrence_plan":
        method(spell, spell._compiler_artifact, spellbook, spellbook._spell_system_states)
    elif method_name == "run_phase_execution_plan":
        method(spell, spell._compiler_artifact, spellbook)
    else:
        method(*args_builder(spell, spellbook), **kwargs_builder())

    assert calls == [
        (
            args_builder(spell, spellbook),
            kwargs_builder(),
        )
    ]
