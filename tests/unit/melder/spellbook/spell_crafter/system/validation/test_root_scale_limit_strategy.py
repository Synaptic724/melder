import pytest

from melder.aether.spellbook.spell_compiler.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.aether.spellbook.spell_compiler.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.aether.spellbook.spell_compiler.system.spell_system_index import SpellSystemIndex
from melder.aether.spellbook.spell_compiler.system.validation.root_scale_limit_strategy import (
    RootScaleLimitStrategy,
)


def _blueprint(root_id: str, node_ids: list[str]) -> RootResolutionBlueprint:
    dag = DirectedAcyclicWorkGraph()
    for node_id in node_ids:
        dag.add_node(key=node_id, payload=None)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=f"lineage-{root_id}",
        dag=dag,
    )


def test_root_scale_limit_honors_cancellation() -> None:
    class _Cancel:
        @property
        def is_set(self):
            return True

        def throw_if_set(self):
            raise RuntimeError("cancelled")

    with pytest.raises(RuntimeError, match="cancelled"):
        RootScaleLimitStrategy().run(
            index=SpellSystemIndex(),
            blueprints={"root": _blueprint("root", ["root"])},
            phase4_results={},
            broken_spell_ids=set(),
            spell_system_states=object(),
            spell_lookup={},
            diagnostics=[],
            cancel_event=_Cancel(),
        )


def test_root_scale_limit_disabled_depth_skips_missing_root_depth_checks() -> None:
    diagnostics: list = []

    RootScaleLimitStrategy(
        max_nodes=0,
        max_edges=0,
        max_depth=0,
        max_fan_out=0,
    ).run(
        index=SpellSystemIndex(),
        blueprints={"root": _blueprint("root", ["other"])},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_root_scale_limit_missing_root_skips_depth_walk() -> None:
    diagnostics: list = []

    RootScaleLimitStrategy(
        max_nodes=0,
        max_edges=0,
        max_depth=1,
        max_fan_out=0,
    ).run(
        index=SpellSystemIndex(),
        blueprints={"root": _blueprint("root", ["other"])},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_root_scale_limit_ignores_ordering_failures() -> None:
    diagnostics: list = []
    root_node = type("_DagNode", (), {"id": "root", "dependencies": [], "dependents": []})()

    class _RaisingDag:
        def __init__(self) -> None:
            self.nodes = {"root": root_node}

        def get_node(self, node_id: str):
            return root_node if node_id == "root" else None

        def collect_dependency_ids(self):
            raise RuntimeError("ordering failed")

    blueprint = type("_Blueprint", (), {"dag": _RaisingDag()})()

    RootScaleLimitStrategy(
        max_nodes=0,
        max_edges=0,
        max_depth=1,
        max_fan_out=0,
    ).run(
        index=SpellSystemIndex(),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []


def test_root_scale_limit_ignores_missing_nodes_in_ordering() -> None:
    diagnostics: list = []
    root_node = type("_DagNode", (), {"id": "root", "dependencies": [], "dependents": []})()

    class _SparseDag:
        def __init__(self) -> None:
            self.nodes = {"root": root_node}

        def get_node(self, node_id: str):
            return root_node if node_id == "root" else None

        def collect_dependency_ids(self):
            return ["root", "ghost"]

    blueprint = type("_Blueprint", (), {"dag": _SparseDag()})()

    RootScaleLimitStrategy(
        max_nodes=0,
        max_edges=0,
        max_depth=1,
        max_fan_out=0,
    ).run(
        index=SpellSystemIndex(),
        blueprints={"root": blueprint},
        phase4_results={},
        broken_spell_ids=set(),
        spell_system_states=object(),
        spell_lookup={},
        diagnostics=diagnostics,
        cancel_event=None,
    )

    assert diagnostics == []
