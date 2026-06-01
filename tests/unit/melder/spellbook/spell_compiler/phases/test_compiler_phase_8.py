"""Unit tests for the live phase-8 analyzer wrapper."""

from types import SimpleNamespace

from melder.aether.spellbook.spell_compiler.phases.compiler_phase_8 import (
    CompilerPhase8,
)


class _AnalyzerStub:
    """Analyzer stub that records delegation and cleanup calls."""

    __slots__ = [
        "analyze_calls",
        "cleanup_calls",
    ]

    def __init__(self) -> None:
        """Initialize empty call counters for the stub."""
        self.analyze_calls = []
        self.cleanup_calls = 0

    def analyze_occurrence(self, spell, artifact) -> None:
        """Record the delegated analyze call."""
        self.analyze_calls.append((spell, artifact))

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_calls += 1


def test_run_delegates_to_spell_analyzer() -> None:
    """Phase 8 should delegate directly to the owned analyzer facade."""
    phase = CompilerPhase8()
    analyzer = _AnalyzerStub()
    phase._spell_analyzer = analyzer
    spell = SimpleNamespace()
    artifact = SimpleNamespace()
    spellbook = SimpleNamespace()
    spell_system_states = SimpleNamespace()

    phase.run(spell, artifact, spellbook, spell_system_states)

    assert analyzer.analyze_calls == [
        (spell, artifact),
    ]


def test_cleanup_releases_owned_analyzer_once() -> None:
    """Phase 8 cleanup should cleanup the owned analyzer exactly once."""
    phase = CompilerPhase8()
    analyzer = _AnalyzerStub()
    phase._spell_analyzer = analyzer

    phase.cleanup()
    phase.cleanup()

    assert analyzer.cleanup_calls == 1
