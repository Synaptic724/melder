"""Unit tests for the live phase-11 codegen-creation wrapper."""

from types import SimpleNamespace

from melder.aether.spellbook.spell_compiler.phases.compiler_phase_11 import (
    CompilerPhase11,
)


class _CreationSystemStub:
    """Codegen-creation stub that records delegation and cleanup calls."""

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


def test_run_delegates_to_codegen_creation_system() -> None:
    """Phase 11 should delegate directly to the owned codegen creation facade."""
    phase = CompilerPhase11()
    creation_system = _CreationSystemStub()
    phase._codegen_creation_system = creation_system
    spell = SimpleNamespace()
    artifact = SimpleNamespace()
    spellbook = SimpleNamespace()

    phase.run(spell, artifact, spellbook)

    assert creation_system.build_calls == [artifact]


def test_cleanup_releases_owned_codegen_creation_system_once() -> None:
    """Phase 11 cleanup should cleanup the owned creation system exactly once."""
    phase = CompilerPhase11()
    creation_system = _CreationSystemStub()
    phase._codegen_creation_system = creation_system

    phase.cleanup()
    phase.cleanup()

    assert creation_system.cleanup_calls == 1
