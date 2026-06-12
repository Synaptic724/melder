"""Unit tests for current-surface compiler phase 2 symbolic graph build."""

from types import SimpleNamespace
from typing import Any

import pytest

import melder.aether.spellbook.spell_compiler.phases.compiler_phase_2 as compiler_phase_2_module
from melder.aether.spellbook.spell_compiler.phases.compiler_phase_2 import (
    CompilerPhase2,
)
from melder.aether.spellbook.spell_compiler.spell_requirements_finder.parameter_di_shape import (
    ParameterDIShape,
)
from tests.unit.melder.spellbook.spell_compiler.support.compiler_test_support import (
    make_spell,
)


class _CancelStub:
    """Minimal cancellation stub for compiler phase tests."""

    def __init__(self, is_set: bool) -> None:
        """Store the initial cancellation posture."""
        self.is_set = is_set
        self.throw_calls = 0

    def throw_if_set(self) -> None:
        """Record cancellation and raise the expected runtime error."""
        self.throw_calls += 1
        raise RuntimeError("cancelled")


def _make_param(
        name: str,
        position: int,
        di_shape: ParameterDIShape,
        *,
        annotation: Any = None,
        collection_element_annotation: Any = None,
        spellmap_default: Any = None,
        default_value: Any = None,
        is_optional: bool = False,
) -> Any:
    """Build a minimal Phase 2 requirements parameter stub."""
    return SimpleNamespace(
        name=name,
        position=position,
        di_shape=di_shape,
        annotation=annotation,
        collection_element_annotation=collection_element_annotation,
        spellmap_default=spellmap_default,
        default_value=default_value,
        is_optional=is_optional,
    )


def test_run_raises_without_phase1_requirements() -> None:
    """Phase 2 should fail fast when Phase 1 has not populated requirements."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact

    phase = CompilerPhase2()

    with pytest.raises(RuntimeError, match="before Phase 1 requirements"):
        phase.run(spell, artifact)


def test_run_raises_without_current_spell_id() -> None:
    """Phase 2 should require a bound current spell id."""
    spell = make_spell("spell-1")
    spell.spell_index.current = None
    artifact = spell._compiler_artifact
    artifact._requirements = SimpleNamespace(parameters=[])

    phase = CompilerPhase2()

    with pytest.raises(RuntimeError, match="bound spell current id"):
        phase.run(spell, artifact)


def test_run_builds_graph_for_supported_dependency_shapes(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase 2 should convert supported DI shapes into symbolic dependencies."""
    spell = make_spell("root")
    artifact = spell._compiler_artifact
    spellmap_default = {"kind": "spellmap-default"}
    captured_calls: list[tuple[Any, Any]] = []

    class _FakeSpellContract:
        """Minimal stand-in for SpellContract canonical key extraction."""

        def __init__(self, canonical_key) -> None:
            self.canonical_key = canonical_key

    artifact._requirements = SimpleNamespace(
        parameters=[
            _make_param(
                "single",
                0,
                ParameterDIShape.SINGLE_BY_ANNOTATION,
                annotation=str,
            ),
            _make_param(
                "collection",
                1,
                ParameterDIShape.COLLECTION_BY_ANNOTATION,
                collection_element_annotation=int,
                is_optional=True,
            ),
            _make_param(
                "spellmap",
                2,
                ParameterDIShape.SPELLMAP_DEFAULT,
                spellmap_default=spellmap_default,
            ),
            _make_param(
                "plain",
                3,
                ParameterDIShape.PLAIN,
                annotation=float,
            ),
            _make_param(
                "contract",
                4,
                ParameterDIShape.SPELL_CONTRACT,
                annotation="frame-a",
                default_value=_FakeSpellContract(("frame-a", "__default__")),
            ),
            _make_param(
                "ignored",
                5,
                ParameterDIShape.IGNORE,
                annotation=bytes,
            ),
        ]
    )

    monkeypatch.setattr(
        compiler_phase_2_module,
        "SpellContract",
        _FakeSpellContract,
    )
    monkeypatch.setattr(
        compiler_phase_2_module.SharedCompilerExecutions,
        "capture_phase2_5_codegen_ir",
        lambda bound_spell, compiler_artifact: captured_calls.append(
            (bound_spell, compiler_artifact)
        ),
    )

    phase = CompilerPhase2()
    phase.run(spell, artifact)

    graph = artifact._symbolic_graph
    assert graph is not None
    assert graph.spell_id == "root"
    assert len(graph.dependencies) == 5

    dependencies = {dep.param_name: dep for dep in graph.dependencies}

    assert dependencies["single"].target_annotation is str
    assert dependencies["single"].is_collection is False
    assert dependencies["collection"].target_annotation is int
    assert dependencies["collection"].is_collection is True
    assert dependencies["collection"].is_optional is True
    assert dependencies["spellmap"].spellmap_default is spellmap_default
    assert dependencies["plain"].target_annotation is float
    assert dependencies["contract"].contract_key == ("frame-a", "__default__")
    # Eager phase2_5 IR capture was removed from the phase body (write-only
    # snapshot, discarded same pass); guard against reintroduction.
    assert captured_calls == []


def test_run_honors_cancellation_before_graph_build() -> None:
    """Phase 2 should abort before graph construction when cancelled."""
    spell = make_spell("spell-1")
    artifact = spell._compiler_artifact
    artifact._requirements = SimpleNamespace(parameters=[])
    cancel_event = _CancelStub(is_set=True)

    phase = CompilerPhase2()

    with pytest.raises(RuntimeError, match="cancelled"):
        phase.run(spell, artifact, cancel_event=cancel_event)

    assert cancel_event.throw_calls == 1
