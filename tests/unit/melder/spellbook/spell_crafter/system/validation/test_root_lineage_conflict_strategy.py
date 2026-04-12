import pytest

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.root_lineage_conflict_strategy import (
    RootLineageConflictStrategy,
)


def _make_index(nodes: dict[str, str | None]) -> SpellSystemIndex:
    index = SpellSystemIndex()
    for spell_id, lineage_id in nodes.items():
        if lineage_id is None:
            class _NodeStub:
                def __init__(self) -> None:
                    self.spell_id = spell_id
                    self.lineage_id = None

            index._nodes[spell_id] = _NodeStub()  # noqa: SLF001
            continue

        index.upsert_node(
            SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=set(),
            )
        )
    return index


def _make_blueprints(*root_ids: str) -> dict[str, RootResolutionBlueprint]:
    result: dict[str, RootResolutionBlueprint] = {}
    for root_id in root_ids:
        dag = DirectedAcyclicWorkGraph()
        dag.add_node(key=root_id, payload=None)
        result[root_id] = RootResolutionBlueprint(
            root_spell_id=root_id,
            root_lineage_id=f"lineage-{root_id}",
            dag=dag,
        )
    return result


def test_root_lineage_conflict_ignores_single_root_per_lineage() -> None:
    diagnostics: list = []

    RootLineageConflictStrategy().run(
        index=_make_index({"root": "lineage-root"}),
        blueprints=_make_blueprints("root"),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_root_lineage_conflict_skips_missing_and_lineageless_roots() -> None:
    diagnostics: list = []

    RootLineageConflictStrategy().run(
        index=_make_index({"lineageless": None}),
        blueprints=_make_blueprints("missing", "lineageless"),
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_root_lineage_conflict_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        RootLineageConflictStrategy().run(
            index=_make_index({"root": "lineage-root"}),
            blueprints=_make_blueprints("root"),
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
