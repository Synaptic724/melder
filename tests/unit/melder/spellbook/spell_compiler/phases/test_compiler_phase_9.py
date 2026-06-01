"""Unit tests for the live phase-9 processor wrapper."""

from types import SimpleNamespace

from melder.aether.spellbook.spell_compiler.phases.compiler_phase_9 import (
    CompilerPhase9,
)


class _ProcessorStub:
    """Processor stub that records delegation and cleanup calls."""

    __slots__ = [
        "process_calls",
        "cleanup_calls",
    ]

    def __init__(self) -> None:
        """Initialize empty call counters for the stub."""
        self.process_calls = []
        self.cleanup_calls = 0

    def process(self, spell, artifact) -> None:
        """Record the delegated process call."""
        self.process_calls.append((spell, artifact))

    def cleanup(self) -> None:
        """Record one cleanup call."""
        self.cleanup_calls += 1


def test_run_delegates_to_spell_artifact_processor() -> None:
    """Phase 9 should delegate directly to the owned processor facade."""
    phase = CompilerPhase9()
    processor = _ProcessorStub()
    phase._artifact_processor = processor
    spell = SimpleNamespace()
    artifact = SimpleNamespace()

    phase.run(spell, artifact)

    assert processor.process_calls == [
        (spell, artifact),
    ]


def test_cleanup_releases_owned_processor_once() -> None:
    """Phase 9 cleanup should cleanup the owned processor exactly once."""
    phase = CompilerPhase9()
    processor = _ProcessorStub()
    phase._artifact_processor = processor

    phase.cleanup()
    phase.cleanup()

    assert processor.cleanup_calls == 1
