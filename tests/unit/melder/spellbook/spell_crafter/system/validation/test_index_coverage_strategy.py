import pytest

from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_crafter.system.spell_system_node import SpellSystemNode
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.index_coverage_strategy import (
    IndexCoverageStrategy,
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


def _make_blueprint(root_id: str, *node_ids: str) -> RootResolutionBlueprint:
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(key=node_id, payload=None)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage-{root_id}",
        dag=dag,
    )


def test_index_coverage_skips_nodes_present_in_blueprints() -> None:
    diagnostics: list = []

    IndexCoverageStrategy().run(
        index=_make_index("root", "dep"),
        blueprints={"root": _make_blueprint("root", "root", "dep")},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_index_coverage_reports_each_uncovered_node() -> None:
    diagnostics: list = []

    IndexCoverageStrategy().run(
        index=_make_index("root", "orphan-a", "orphan-b"),
        blueprints={"root": _make_blueprint("root", "root")},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert {diag.code for diag in diagnostics} == {"index_node_missing_from_blueprints"}
    assert {diag.spell_id for diag in diagnostics} == {"orphan-a", "orphan-b"}
    assert all(diag.severity is SystemDiagnosticSeverity.ERROR for diag in diagnostics)


def test_index_coverage_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        IndexCoverageStrategy().run(
            index=_make_index("root"),
            blueprints={"root": _make_blueprint("root", "root")},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )
