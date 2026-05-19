import pytest

from typing import Sequence

from melder.aether.spellbook.spell_crafter.dag.dag_index import (
    DagIndex,
    DagIndexBuilder,
    DagTargetingEngine,
    PathRegistry,
    SocketRef,
)
from melder.aether.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.aether.spellbook.spell_crafter.dag.target_spec import TargetSpec, TargetSpecKind


def _path_id(registry: PathRegistry, path: Sequence[str]) -> int:
    current = registry.root_path_id
    for segment in path:
        current = registry.extend_path(current, segment)
    return current


def test_dag_index_add_and_get():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    assert index.get_by_exact_path(("p",)) == [ref]
    assert index.get_by_name("p") == [ref]
    assert list(index.iter_all_sockets()) == [ref]


def test_dag_index_iter_all_sockets_dedupes():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    index.add_socket(ref)  # same ref; should not duplicate
    assert list(index.iter_all_sockets()) == [ref]


def test_dag_index_cleanup_blocks_access():
    index = DagIndex()
    index.cleanup()
    with pytest.raises(AttributeError):
        registry = PathRegistry()
        index.add_socket(
            SocketRef(
                "n1",
                "p",
                _path_id(registry, ("p",)),
                SocketKind.NORMAL,
            )
        )


def test_dag_targeting_resolve_path_success_and_errors():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("a", "b")),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.PATH, path=("a", "b"), param_name=None)
    result = engine.resolve(spec, lambda r: True)
    assert result == [ref]
    spec_empty = TargetSpec(kind=TargetSpecKind.PATH, path=(), param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(spec_empty, lambda r: True)
    spec_missing = TargetSpec(kind=TargetSpecKind.PATH, path=("missing",), param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(spec_missing, lambda r: True)


def test_dag_targeting_resolve_unique_enforces_cardinality():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.UNIQUE, path=None, param_name="p")
    assert engine.resolve(spec, lambda r: True) == [ref]

    # zero matches
    spec_zero = TargetSpec(kind=TargetSpecKind.UNIQUE, path=None, param_name="missing")
    with pytest.raises(RuntimeError):
        engine.resolve(spec_zero, lambda r: True)

    # multiple matches
    index.add_socket(
        SocketRef(
            "n2",
            "p",
            _path_id(index.path_registry, ("p2",)),
            SocketKind.NORMAL,
        )
    )
    with pytest.raises(RuntimeError):
        engine.resolve(spec, lambda r: True)


def test_dag_targeting_resolve_broadcast_requires_matches():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("p",)),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.BROADCAST, path=None, param_name="p")
    assert engine.resolve(spec, lambda r: True) == [ref]
    spec_none = TargetSpec(kind=TargetSpecKind.BROADCAST, path=None, param_name="missing")
    with pytest.raises(RuntimeError):
        engine.resolve(spec_none, lambda r: True)


def test_dag_targeting_validates_spec_and_filter():
    index = DagIndex()
    engine = DagTargetingEngine(index)
    with pytest.raises(ValueError):
        engine.resolve(None, lambda r: True)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        engine.resolve(TargetSpec(kind=TargetSpecKind.PATH, path=("a",), param_name=None), None)  # type: ignore[arg-type]


def test_dag_targeting_missing_param_name_errors():
    index = DagIndex()
    engine = DagTargetingEngine(index)
    path_spec = TargetSpec(kind=TargetSpecKind.PATH, path=(), param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(path_spec, lambda r: True)

    unique_spec = TargetSpec(kind=TargetSpecKind.UNIQUE, path=None, param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(unique_spec, lambda r: True)

    broadcast_spec = TargetSpec(kind=TargetSpecKind.BROADCAST, path=None, param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(broadcast_spec, lambda r: True)


def test_dag_targeting_unknown_kind_raises_runtime():
    index = DagIndex()
    engine = DagTargetingEngine(index)

    class DummySpec:
        kind = object()
        path = None
        param_name = None

    with pytest.raises(RuntimeError):
        engine.resolve(DummySpec(), lambda r: True)  # type: ignore[arg-type]


def test_dag_targeting_filter_can_remove_all_candidates():
    index = DagIndex()
    ref = SocketRef(
        "n1",
        "p",
        _path_id(index.path_registry, ("a",)),
        SocketKind.NORMAL,
    )
    index.add_socket(ref)
    engine = DagTargetingEngine(index)

    spec_path = TargetSpec(kind=TargetSpecKind.PATH, path=("a",), param_name=None)
    with pytest.raises(RuntimeError):
        engine.resolve(spec_path, lambda r: False)

    spec_unique = TargetSpec(kind=TargetSpecKind.UNIQUE, path=None, param_name="p")
    with pytest.raises(RuntimeError):
        engine.resolve(spec_unique, lambda r: False)

    spec_broadcast = TargetSpec(kind=TargetSpecKind.BROADCAST, path=None, param_name="p")
    with pytest.raises(RuntimeError):
        engine.resolve(spec_broadcast, lambda r: False)


def test_dag_index_builder_shallow_builds_refs():
    class DummySocket:
        def __init__(self, name, kind):
            self.param_name = name
            self.socket_kind = kind

    sockets = [DummySocket("a", SocketKind.NORMAL), DummySocket("b", SocketKind.SPELL_CONTRACT)]
    index = DagIndexBuilder.build_shallow("owner", sockets)
    paths = {
        index.path_registry.format_path(ref.param_path_id)
        for ref in index.iter_all_sockets()
    }
    assert paths == {"a", "b"}
    with pytest.raises(ValueError):
        DagIndexBuilder.build_shallow(None, sockets)  # type: ignore[arg-type]


def test_dag_index_builder_empty_sockets_returns_empty_index():
    index = DagIndexBuilder.build_shallow("owner", [])
    assert list(index.iter_all_sockets()) == []


def test_dag_targeting_cleanup_nulls_index_and_is_idempotent():
    index = DagIndex()
    engine = DagTargetingEngine(index)
    engine.cleanup()
    engine.cleanup()
    assert engine.cleaned
    with pytest.raises(AttributeError):
        engine.resolve(TargetSpec(kind=TargetSpecKind.PATH, path=("a",), param_name=None), lambda r: True)
