import pytest

from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.index_dependency_sanity_strategy import (
    IndexDependencySanityStrategy,
)


def _make_index(edges: dict[str, set[str]]) -> SpellSystemIndex:
    index = SpellSystemIndex()
    for spell_id, deps in edges.items():
        index.upsert_node(
            SpellSystemNode(
                spell_id=spell_id,
                lineage_id=f"lineage-{spell_id}",
                dependencies=deps,
            )
        )
    return index


def test_index_dependency_sanity_reports_multiple_missing_dependencies() -> None:
    diagnostics: list = []

    IndexDependencySanityStrategy().run(
        index=_make_index({"root": {"missing-a", "missing-b"}}),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"missing_index_dependency"}
    assert {diag.details["dependency_id"] for diag in diagnostics} == {
        "missing-a",
        "missing-b",
    }
    assert all(diag.severity is SystemDiagnosticSeverity.ERROR for diag in diagnostics)


def test_index_dependency_sanity_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        IndexDependencySanityStrategy().run(
            index=_make_index({"root": {"missing"}}),
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
