"""Unit tests for the live phase-10 planner wrapper."""

from types import SimpleNamespace

from melder.aether.spellbook.spell_compiler.phases.compiler_phase_10 import (
    CompilerPhase10,
)


class _PlannerStub:
    """Planner stub that records delegation and cleanup calls."""

    __slots__ = [
        "build_calls",
        "cleanup_calls",
    ]

    def __init__(self) -> None:
        """Initialize empty call counters for the stub."""
        self.build_calls = []
        self.cleanup_calls = 0

    def build(self, artifact) -> None:
        """Record the delegated build call."""
        self.build_calls.append(artifact)

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_calls += 1


def test_run_delegates_to_spell_codegen_planner() -> None:
    """Phase 10 should delegate directly to the owned planner facade."""
    phase = CompilerPhase10()
    planner = _PlannerStub()
    phase._codegen_planner = planner
    spell = SimpleNamespace()
    artifact = SimpleNamespace()

    phase.run(spell, artifact)

    assert planner.build_calls == [artifact]


def test_cleanup_releases_owned_planner_once() -> None:
    """Phase 10 cleanup should cleanup the owned planner exactly once."""
    phase = CompilerPhase10()
    planner = _PlannerStub()
    phase._codegen_planner = planner

    phase.cleanup()
    phase.cleanup()

    assert planner.cleanup_calls == 1
