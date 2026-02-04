import pytest

from typing import Sequence

from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _path_id(registry: PathRegistry, path: Sequence[str]) -> int:
    current = registry.root_path_id
    for segment in path:
        current = registry.extend_path(current, segment)
    return current


def _make_blueprint(
    *,
    root_id: str = "root",
    lineage_id: str = "lineage",
    ordered: tuple[str, ...] = ("a", "b", "root"),
    sockets: tuple[SocketRef, ...] | None = None,
    dag_index: DagIndex | None = None,
) -> RootResolutionBlueprint:
    dag = DirectedAcyclicWorkGraph()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("root")
    dag.add_dependency("a", "root")
    dag.add_dependency("b", "root")
    if dag_index is None:
        dag_index = DagIndex()
    if sockets:
        for socket in sockets:
            dag_index.add_socket(socket)
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=lineage_id,
        dag=dag,
        ordered_node_ids=ordered,
        socket_refs=sockets,
        dag_index=dag_index,
    )


def test_init_requires_root_id_and_dag():
    with pytest.raises(ValueError):
        RootResolutionBlueprint(None, "lineage", DirectedAcyclicWorkGraph())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        RootResolutionBlueprint("root", "lineage", None)  # type: ignore[arg-type]


def test_properties_return_copies_and_metadata():
    index = DagIndex()
    sockets = (
        SocketRef(
            "root",
            "p",
            _path_id(index.path_registry, ("p",)),
            SocketKind.NORMAL,
        ),
        SocketRef(
            "child",
            "c",
            _path_id(index.path_registry, ("root", "c")),
            SocketKind.SPELL_CONTRACT,
        ),
    )
    bp = _make_blueprint(sockets=sockets, dag_index=index)
    assert bp.root_spell_id == "root"
    assert bp.root_lineage_id == "lineage"
    assert bp.dag is not None
    assert bp.ordered_node_ids == ["a", "b", "root"]
    assert bp.socket_refs == list(sockets)
    # copies are returned
    refs = bp.socket_refs
    refs.clear()
    assert bp.socket_refs == list(sockets)


def test_add_socket_ref_indexes_dag_index():
    index = DagIndex()
    bp = _make_blueprint(dag_index=index)
    bp.ensure_dag_index_built()
    ref = SocketRef(
        "root",
        "param",
        _path_id(index.path_registry, ("root", "param")),
        SocketKind.NORMAL,
    )
    bp.add_socket_ref(ref)
    assert bp.socket_refs == [ref]
    assert bp.dag_index.get_by_exact_path(("root", "param")) == [ref]
    assert bp.dag_index.get_by_name("param") == [ref]


def test_add_socket_ref_rejects_none():
    bp = _make_blueprint()
    with pytest.raises(ValueError):
        bp.add_socket_ref(None)  # type: ignore[arg-type]


def test_replace_dag_index_swaps_reference():
    bp = _make_blueprint()
    replacement = DagIndex()
    ref = SocketRef(
        "root",
        "p",
        _path_id(replacement.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    replacement.add_socket(ref)
    bp.replace_dag_index(replacement)
    assert bp.dag_index is replacement
    with pytest.raises(ValueError):
        bp.replace_dag_index(None)  # type: ignore[arg-type]


def test_cleanup_idempotent_and_nulls_references():
    bp = _make_blueprint()
    bp.add_socket_ref(
        SocketRef(
            "root",
            "p",
            _path_id(bp.path_registry, ("p",)),
            SocketKind.NORMAL,
        )
    )
    dag = bp.dag
    index = bp.dag_index
    bp.cleanup()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.root_spell_id
    assert dag.cleaned is True
    assert index.cleaned is True


def test_accessors_raise_after_cleanup():
    bp = _make_blueprint()
    bp.cleanup()
    with pytest.raises(RuntimeError):
        _ = bp.dag
    with pytest.raises(RuntimeError):
        _ = bp.ordered_node_ids
    with pytest.raises(RuntimeError):
        bp.add_socket_ref(
            SocketRef(
                "root",
                "p",
                _path_id(PathRegistry(), ("p",)),
                SocketKind.NORMAL,
            )
        )


def test_ordered_node_ids_returns_copy():
    bp = _make_blueprint()
    ids = bp.ordered_node_ids
    ids.append("mutate")
    assert bp.ordered_node_ids == ["a", "b", "root"]


def test_defaults_create_index_and_empty_refs():
    bp = _make_blueprint(sockets=None, dag_index=None)
    assert bp.socket_refs == []
    assert isinstance(bp.dag_index, DagIndex)


def test_replace_dag_index_then_add_socket_ref_uses_new_index():
    bp = _make_blueprint()
    new_index = DagIndex()
    bp.replace_dag_index(new_index)
    bp.ensure_dag_index_built()
    ref = SocketRef(
        "root",
        "p",
        _path_id(new_index.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    bp.add_socket_ref(ref)
    assert bp.dag_index is new_index
    assert bp.dag_index.get_by_exact_path(("p",)) == [ref]
