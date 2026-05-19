import pytest

from melder.aether.spellbook.spell_crafter.blueprints.root_resolution_blueprint import RootResolutionBlueprint
from melder.aether.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_crafter.system.system_diagnostic import (
    SystemDiagnosticSeverity,
)
from melder.aether.spellbook.spell_crafter.system.validation.broken_spell_in_dag_strategy import (
    BrokenSpellInDagStrategy,
)


def _blueprint_with_nodes(root_id: str, *node_ids: str) -> dict:
    dag = DirectedAcyclicWorkGraph()
    for nid in node_ids:
        dag.add_node(key=nid, payload=None)
    bp = RootResolutionBlueprint(root_spell_id=root_id, root_lineage_id=None, dag=dag)
    return {root_id: bp}


def test_no_broken_ids_produces_no_diagnostics():
    strategy = BrokenSpellInDagStrategy()
    diagnostics: list = []
    blueprints = _blueprint_with_nodes("root", "a", "b")

    strategy.run(
        index=None,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_non_matching_broken_ids_produces_no_diagnostics():
    strategy = BrokenSpellInDagStrategy()
    diagnostics: list = []
    blueprints = _blueprint_with_nodes("root", "a")

    strategy.run(
        index=None,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids={"missing"},
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_matching_broken_ids_emit_diagnostic_with_details():
    strategy = BrokenSpellInDagStrategy()
    diagnostics: list = []
    blueprints = _blueprint_with_nodes("root", "broken", "ok")

    strategy.run(
        index=None,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids={"broken"},
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert len(diagnostics) == 1
    diag = diagnostics[0]
    assert diag.code == "broken_spell_in_dag"
    assert diag.severity is SystemDiagnosticSeverity.ERROR
    assert diag.spell_id == "broken"
    assert diag.root_id == "root"
    assert "broken" in diag.message and "root" in diag.message


def test_cancel_event_honored_before_work():
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    strategy = BrokenSpellInDagStrategy()
    diagnostics: list = []
    blueprints = _blueprint_with_nodes("root", "a")

    with pytest.raises(RuntimeError, match="cancelled"):
        strategy.run(
            index=None,
            blueprints=blueprints,
            phase4_results={},
            broken_spell_ids={"a"},
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=diagnostics,
            cancel_event=_Cancel(),
        )


def test_multiple_broken_ids_emit_multiple_diagnostics():
    strategy = BrokenSpellInDagStrategy()
    diagnostics: list = []
    blueprints = _blueprint_with_nodes("root", "a", "b", "c")

    strategy.run(
        index=None,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids={"a", "c"},
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert {d.spell_id for d in diagnostics} == {"a", "c"}
    assert all(d.root_id == "root" for d in diagnostics)
    assert all(d.severity is SystemDiagnosticSeverity.ERROR for d in diagnostics)


def test_diagnostics_are_appended_not_overwritten():
    strategy = BrokenSpellInDagStrategy()
    existing = ["keep-me"]
    blueprints = _blueprint_with_nodes("root", "a")

    strategy.run(
        index=None,
        blueprints=blueprints,
        phase4_results={},
        broken_spell_ids={"a"},
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=existing,
        cancel_event=None,
    )

    assert existing[0] == "keep-me"
    assert len(existing) == 2
    assert isinstance(existing[1], object)
