import pytest

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.spellbook.spell_crafter.system.validation.lineage_version_conflict_strategy import (
    LineageVersionConflictStrategy,
)


def _make_index(nodes: dict[str, str | None]) -> SpellSystemIndex:
    index = SpellSystemIndex()
    for spell_id, lineage_id in nodes.items():
        if lineage_id is None:
            class _NodeStub:
                def __init__(self, sid: str) -> None:
                    self.spell_id = sid
                    self.lineage_id = None

            index._nodes[spell_id] = _NodeStub(spell_id)  # noqa: SLF001
            continue
        index.upsert_node(
            SpellSystemNode(
                spell_id=spell_id,
                lineage_id=lineage_id,
                dependencies=set(),
            )
        )
    return index


def _make_blueprint(root_id: str, node_ids: list[str]) -> RootResolutionBlueprint:
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(key=node_id, payload=None)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage-{root_id}",
        dag=dag,
    )


def test_lineage_version_conflict_ignores_single_version_per_lineage() -> None:
    diagnostics: list = []

    LineageVersionConflictStrategy().run(
        index=_make_index({"root": "lineage-root", "v1": "lineage-shared"}),
        blueprints={"root": _make_blueprint("root", ["root", "v1"])},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_lineage_version_conflict_skips_missing_and_lineageless_nodes() -> None:
    diagnostics: list = []

    LineageVersionConflictStrategy().run(
        index=_make_index({"root": "lineage-root", "lineageless": None}),
        blueprints={
            "root": _make_blueprint("root", ["root", "missing", "lineageless"])
        },
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_lineage_version_conflict_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        LineageVersionConflictStrategy().run(
            index=_make_index({"root": "lineage-root"}),
            blueprints={"root": _make_blueprint("root", ["root"])},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
