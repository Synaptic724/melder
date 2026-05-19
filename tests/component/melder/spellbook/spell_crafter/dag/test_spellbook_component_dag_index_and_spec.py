import pytest

from typing import Sequence

from melder.aether.spellbook.spell_crafter.dag.dag_index import (
    DagIndex,
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


def test_component_target_spec_parses_paths_and_wildcards() -> None:
    """
    Purpose:
        Validate TargetSpec parsing for path and wildcard forms.
    Contract:
        - PATH specs parse into segments.
        - UNIQUE and BROADCAST specs capture param_name.
    Returns:
        None.
    """
    path_spec = TargetSpec.parse(" root > child > leaf ")
    assert path_spec.kind is TargetSpecKind.PATH
    assert path_spec.path == ("root", "child", "leaf")
    assert path_spec.param_name is None

    unique_spec = TargetSpec.parse("*repo")
    assert unique_spec.kind is TargetSpecKind.UNIQUE
    assert unique_spec.param_name == "repo"

    broadcast_spec = TargetSpec.parse("**logger")
    assert broadcast_spec.kind is TargetSpecKind.BROADCAST
    assert broadcast_spec.param_name == "logger"


def test_component_target_spec_rejects_empty_or_missing_names() -> None:
    """
    Purpose:
        Validate TargetSpec rejects empty or malformed inputs.
    Contract:
        - Empty or missing parameter names raise ValueError.
    Returns:
        None.
    """
    with pytest.raises(ValueError):
        TargetSpec.parse("   ")
    with pytest.raises(ValueError):
        TargetSpec.parse("*")
    with pytest.raises(ValueError):
        TargetSpec.parse("**")


def test_component_dag_index_collects_and_queries_sockets() -> None:
    """
    Purpose:
        Validate DagIndex stores sockets and resolves by name/path.
    Contract:
        - get_by_exact_path returns only sockets with the matching path.
        - get_by_name returns all sockets that share the same param name.
        - iter_all_sockets returns each socket once.
    Returns:
        None.
    """
    index = DagIndex()
    repo_socket = SocketRef(
        node_id="root",
        param_name="repo",
        param_path_id=_path_id(index.path_registry, ("repo",)),
        socket_kind=SocketKind.NORMAL,
    )
    nested_socket = SocketRef(
        node_id="service",
        param_name="repo",
        param_path_id=_path_id(index.path_registry, ("service", "repo")),
        socket_kind=SocketKind.NORMAL,
    )
    index.add_socket(repo_socket)
    index.add_socket(nested_socket)

    exact = index.get_by_exact_path(("repo",))
    assert exact == [repo_socket]

    by_name = index.get_by_name("repo")
    assert set(by_name) == {repo_socket, nested_socket}

    all_sockets = list(index.iter_all_sockets())
    assert set(all_sockets) == {repo_socket, nested_socket}


def test_component_dag_index_iter_all_sockets_dedupes_duplicates() -> None:
    """
    Purpose:
        Validate iter_all_sockets yields unique sockets by value.
    Contract:
        - Duplicate socket refs are returned only once.
    Returns:
        None.
    """
    index = DagIndex()
    socket = SocketRef(
        node_id="root",
        param_name="repo",
        param_path_id=_path_id(index.path_registry, ("repo",)),
        socket_kind=SocketKind.NORMAL,
    )
    index.add_socket(socket)
    index.add_socket(socket)

    all_sockets = list(index.iter_all_sockets())
    assert all_sockets == [socket]


def test_component_dag_targeting_unique_raises_on_multiple_matches() -> None:
    """
    Purpose:
        Validate UNIQUE targeting errors when more than one socket matches.
    Contract:
        - RuntimeError is raised when multiple sockets share the same name.
    Returns:
        None.
    """
    index = DagIndex()
    index.add_socket(
        SocketRef(
            node_id="root",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("repo",)),
            socket_kind=SocketKind.NORMAL,
        )
    )
    index.add_socket(
        SocketRef(
            node_id="child",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("child", "repo")),
            socket_kind=SocketKind.NORMAL,
        )
    )

    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.UNIQUE, path=None, param_name="repo")

    with pytest.raises(RuntimeError):
        engine.resolve(spec, lambda socket: True)


def test_component_dag_targeting_broadcast_raises_on_no_matches() -> None:
    """
    Purpose:
        Validate BROADCAST targeting errors when nothing matches.
    Contract:
        - RuntimeError is raised when the broadcast resolves zero sockets.
    Returns:
        None.
    """
    index = DagIndex()
    index.add_socket(
        SocketRef(
            node_id="root",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("repo",)),
            socket_kind=SocketKind.NORMAL,
        )
    )
    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.BROADCAST, path=None, param_name="missing")

    with pytest.raises(RuntimeError):
        engine.resolve(spec, lambda socket: True)


def test_component_dag_targeting_rejects_empty_path_spec() -> None:
    """
    Purpose:
        Validate PATH specs without segments are rejected.
    Contract:
        - RuntimeError is raised for empty PATH targets.
    Returns:
        None.
    """
    index = DagIndex()
    index.add_socket(
        SocketRef(
            node_id="root",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("repo",)),
            socket_kind=SocketKind.NORMAL,
        )
    )
    engine = DagTargetingEngine(index)
    spec = TargetSpec(kind=TargetSpecKind.PATH, path=(), param_name=None)

    with pytest.raises(RuntimeError):
        engine.resolve(spec, lambda socket: True)


def test_component_dag_index_cleanup_blocks_future_usage() -> None:
    """
    Purpose:
        Validate DagIndex cleanup disables access.
    Contract:
        - Access after cleanup raises AttributeError.
    Returns:
        None.
    """
    index = DagIndex()
    index.add_socket(
        SocketRef(
            node_id="root",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("repo",)),
            socket_kind=SocketKind.NORMAL,
        )
    )
    index.cleanup()

    assert index.cleaned is True
    with pytest.raises(AttributeError):
        index.get_by_name("repo")


def test_component_dag_targeting_engine_cleanup_cleans_index() -> None:
    """
    Purpose:
        Validate DagTargetingEngine cleanup cascades to its index.
    Contract:
        - Index is cleaned when engine is cleaned.
    Returns:
        None.
    """
    index = DagIndex()
    index.add_socket(
        SocketRef(
            node_id="root",
            param_name="repo",
            param_path_id=_path_id(index.path_registry, ("repo",)),
            socket_kind=SocketKind.NORMAL,
        )
    )
    engine = DagTargetingEngine(index)
    engine.cleanup()

    assert engine.cleaned is True
    assert index.cleaned is True
