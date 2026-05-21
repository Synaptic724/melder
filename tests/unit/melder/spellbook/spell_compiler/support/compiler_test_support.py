"""Shared support helpers for current-surface SpellCompiler unit tests."""

from types import SimpleNamespace
from typing import Any

from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.utilities.general_base.cleanable import Cleanable


class CleanupTracker(Cleanable):
    """Track cleanup calls for artifact-owned child objects."""

    def __init__(self) -> None:
        """Initialize cleanup call tracking."""
        super().__init__()
        self.cleanup_calls = 0

    def cleanup(self) -> None:
        """Record cleanup and mark the tracker cleaned."""
        self.cleanup_calls += 1
        self._cleaned = True

    async def async_cleanup(self) -> None:
        """Satisfy the Cleanable contract for the tracker."""
        raise NotImplementedError("async cleanup is not used in unit tests")


def make_spell(spell_id: str = "spell-1") -> Any:
    """Build a minimal spell stub for compiler/artifact/system tests."""
    artifact = SpellCompilerArtifact(spell_id)
    cleanup_calls: list[str] = []

    def _cleanup_creation_context() -> None:
        cleanup_calls.append("cleanup")

    return SimpleNamespace(
        spell_id=spell_id,
        spell_index=SimpleNamespace(
            current=spell_id,
            id="lineage-{0}".format(spell_id),
        ),
        _compiler_artifact=artifact,
        _cleanup_creation_context=_cleanup_creation_context,
        _cleanup_creation_context_calls=cleanup_calls,
    )


def make_spellbook() -> Any:
    """Build a minimal spellbook stub for compiler-system façade tests."""
    return SimpleNamespace(
        _spell_system_states=object(),
        _spell_id_pool={},
    )
