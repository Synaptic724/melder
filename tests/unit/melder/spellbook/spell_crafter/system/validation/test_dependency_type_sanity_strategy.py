import pytest

from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.system_diagnostic import (
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_compiler.system.validation.dependency_type_sanity_strategy import (
    DependencyTypeSanityStrategy,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType


def _make_index_with_dependency(
    *,
    dependency_id: str = "dep",
    dependency_type: SpellType | None = None,
) -> SpellSystemIndex:
    index = SpellSystemIndex()
    index.upsert_node(
        SpellSystemNode(
            spell_id="root",
            lineage_id="lineage-root",
            dependencies={dependency_id},
            existence=Existence.unique,
            spell_type=SpellType.SPELL,
        )
    )
    if dependency_type is not None:
        index.upsert_node(
            SpellSystemNode(
                spell_id=dependency_id,
                lineage_id="lineage-dep",
                dependencies=set(),
                existence=Existence.unique,
                spell_type=dependency_type,
            )
        )
    return index


def test_dependency_type_sanity_warns_for_disallowed_dependency_type() -> None:
    diagnostics: list = []

    DependencyTypeSanityStrategy().run(
        index=_make_index_with_dependency(dependency_type=SpellType.METHOD),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert diag.code == "dependency_type_unexpected"
    assert diag.severity is SystemDiagnosticSeverity.WARNING
    assert diag.spell_id == "root"
    assert diag.details["dependency_id"] == "dep"
    assert diag.details["dependency_type"] == "METHOD"


def test_dependency_type_sanity_skips_missing_and_typeless_dependencies() -> None:
    index = _make_index_with_dependency(dependency_type=None)
    index.upsert_node(
        SpellSystemNode(
            spell_id="none-type",
            lineage_id="lineage-none",
            dependencies=set(),
            existence=Existence.unique,
            spell_type=None,
        )
    )
    index.get_node("root").add_dependency("none-type")
    diagnostics: list = []

    DependencyTypeSanityStrategy().run(
        index=index,
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_dependency_type_sanity_skips_allowed_dependency_type() -> None:
    diagnostics: list = []

    DependencyTypeSanityStrategy().run(
        index=_make_index_with_dependency(dependency_type=SpellType.SPELL),
        blueprints={},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_dependency_type_sanity_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        DependencyTypeSanityStrategy().run(
            index=_make_index_with_dependency(dependency_type=SpellType.METHOD),
            blueprints={},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
