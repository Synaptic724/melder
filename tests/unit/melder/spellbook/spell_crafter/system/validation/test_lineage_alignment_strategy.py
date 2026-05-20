import pytest

from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_compiler.system.validation.lineage_alignment_strategy import (
    LineageAlignmentStrategy,
)


def _make_index(*spell_ids: str) -> SpellSystemIndex:
    index = SpellSystemIndex()
    for spell_id in spell_ids:
        index.upsert_node(
            SpellSystemNode(
                spell_id=spell_id,
                lineage_id=f"lineage-{spell_id}",
                dependencies=set(),
            )
        )
    return index


def _make_blueprint(root_id: str, root_lineage_id: str | None) -> RootResolutionBlueprint:
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(key=root_id, payload=None)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=root_lineage_id,
        dag=dag,
    )


def test_lineage_alignment_skips_missing_index_root() -> None:
    diagnostics: list = []

    LineageAlignmentStrategy().run(
        index=_make_index("other"),
        blueprints={"root": _make_blueprint("root", "lineage-root")},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_lineage_alignment_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        LineageAlignmentStrategy().run(
            index=_make_index("root"),
            blueprints={"root": _make_blueprint("root", "lineage-root")},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
