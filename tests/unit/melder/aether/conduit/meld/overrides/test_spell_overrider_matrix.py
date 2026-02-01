"""Matrix-style SpellOverrider tests for deep path and specificity coverage."""
from dataclasses import dataclass
from typing import Iterable

import pytest

from melder.aether.conduit.meld.overrides.spell_overrider import SpellOverrider
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


@dataclass(frozen=True)
class _MatrixData:
    """
    Purpose:
        Bundle a test blueprint and lookup maps for matrix tests.
    Contract:
        - blueprint is a RootResolutionBlueprint with an indexed DagIndex.
        - by_path maps path strings to SocketRef instances.
        - by_name maps param_name strings to SocketRef lists.
    """
    blueprint: RootResolutionBlueprint
    by_path: dict[str, SocketRef]
    by_name: dict[str, list[SocketRef]]


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: tuple[str, ...],
    path_registry: PathRegistry,
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Purpose:
        Build a SocketRef for override targeting.
    Contract:
        - Returns a SocketRef with the supplied attributes.
    Args:
        node_id: Spell id owning the socket.
        param_name: Parameter name on the spell.
        param_path: Override path segments.
        socket_kind: Socket classification.
    Returns:
        SocketRef: Socket reference with the requested attributes.
    """
    path_id = path_registry.root_path_id
    for segment in param_path:
        path_id = path_registry.extend_path(path_id, segment)
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path_id=path_id,
        socket_kind=socket_kind,
    )


def _make_blueprint(
    *,
    root_id: str,
    root_lineage_id: str,
    socket_refs: Iterable[SocketRef],
    path_registry: PathRegistry,
) -> RootResolutionBlueprint:
    """
    Purpose:
        Build a RootResolutionBlueprint with sockets indexed for overrides.
    Contract:
        - Adds every socket to the DAG index.
        - Ensures each socket node id is represented in the DAG.
    Args:
        root_id: Root spell id for the blueprint.
        root_lineage_id: Lineage id for the root spell.
        socket_refs: Socket refs to add to the targeting index.
    Returns:
        RootResolutionBlueprint: Blueprint ready for SpellOverrider.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(root_id)
    index = DagIndex(path_registry=path_registry)
    socket_list = list(socket_refs)
    for socket_ref in socket_list:
        dag.add_node(socket_ref.node_id)
        index.add_socket(socket_ref)
    ordered_ids = dag.collect_dependency_ids()
    return RootResolutionBlueprint(
        root_spell_id=root_id,
        root_lineage_id=root_lineage_id,
        dag=dag,
        ordered_node_ids=ordered_ids,
        socket_refs=socket_list,
        dag_index=index,
    )


def _build_matrix_blueprint() -> _MatrixData:
    """
    Purpose:
        Build a blueprint with deep paths for matrix-style override tests.
    Contract:
        - Provides sockets with shared names across multiple depths.
        - Includes numeric path segments for indexing coverage.
    Returns:
        _MatrixData: Blueprint and lookup maps for matrix tests.
    """
    specs = [
        ("node-root", "repo", ("root", "repo")),
        ("node-service", "repo", ("root", "service", "repo")),
        ("node-cache", "cache", ("root", "service", "cache")),
        ("node-logger-a", "logger", ("root", "service", "logger")),
        ("node-logger-b", "logger", ("root", "metrics", "logger")),
        ("node-dsn", "dsn", ("root", "service", "db", "dsn")),
        ("node-size", "size", ("root", "service", "db", "pool", "size")),
        ("node-timeout", "timeout", ("root", "service", "db", "pool", "timeout")),
        ("node-queue", "queue", ("root", "tasks", "queue")),
        ("node-retry", "retry", ("root", "tasks", "queue", "retry")),
        ("node-h0", "repo", ("root", "handler", "0", "repo")),
        ("node-h1", "repo", ("root", "handler", "1", "repo")),
        ("node-sink", "sink", ("root", "ops", "sink")),
        ("node-mode", "mode", ("root", "ops", "sink", "mode")),
        ("node-level", "level", ("root", "ops", "trace", "level")),
    ]
    path_registry = PathRegistry()
    sockets = [
        _make_socket_ref(
            node_id=node_id,
            param_name=param_name,
            param_path=param_path,
            path_registry=path_registry,
        )
        for node_id, param_name, param_path in specs
    ]
    by_path: dict[str, SocketRef] = {
        path_registry.format_path(socket.param_path_id): socket for socket in sockets
    }
    by_name: dict[str, list[SocketRef]] = {}
    for socket in sockets:
        by_name.setdefault(socket.param_name, []).append(socket)
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=sockets,
        path_registry=path_registry,
    )
    return _MatrixData(blueprint=blueprint, by_path=by_path, by_name=by_name)


def _expected_map(
    by_path: dict[str, SocketRef],
    assignments: dict[str, str],
) -> dict[SocketRef, str]:
    """
    Purpose:
        Build an expected override map from path-to-value assignments.
    Contract:
        - Each path key is resolved to a SocketRef using by_path.
    Args:
        by_path: Path-to-SocketRef mapping for the matrix blueprint.
        assignments: Mapping of path key to expected override value.
    Returns:
        dict[SocketRef, str]: Socket-keyed expected map.
    """
    return {by_path[path]: value for path, value in assignments.items()}


@pytest.fixture()
def matrix_data() -> _MatrixData:
    """
    Purpose:
        Provide the shared matrix blueprint and lookup maps.
    Contract:
        - Returns a fresh _MatrixData instance per test.
    Returns:
        _MatrixData: Blueprint and lookup maps.
    """
    return _build_matrix_blueprint()


@pytest.mark.parametrize(
    "key,expected_paths",
    [
        ("root>repo", ["root>repo"]),
        ("root>service>repo", ["root>service>repo"]),
        ("root>service>cache", ["root>service>cache"]),
        ("root>service>logger", ["root>service>logger"]),
        ("root>metrics>logger", ["root>metrics>logger"]),
        ("root>service>db>dsn", ["root>service>db>dsn"]),
        ("root>service>db>pool>size", ["root>service>db>pool>size"]),
        ("root>service>db>pool>timeout", ["root>service>db>pool>timeout"]),
        ("root>tasks>queue>retry", ["root>tasks>queue>retry"]),
        ("root>handler>0>repo", ["root>handler>0>repo"]),
        (" root > service > repo ", ["root>service>repo"]),
        ("root>ops>sink>mode", ["root>ops>sink>mode"]),
        ("root>ops>trace>level", ["root>ops>trace>level"]),
    ],
)
def test_matrix_path_targets_expected(
    matrix_data: _MatrixData,
    key: str,
    expected_paths: list[str],
) -> None:
    """
    Purpose:
        Validate PATH overrides map to exact path sockets in the matrix blueprint.
    Contract:
        - Each path key targets only the sockets with the matching path.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        key: Override key to apply.
        expected_paths: Path keys expected to match.
    Returns:
        None.
    Raises:
        AssertionError: If the override map is incorrect.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    result = overrider.apply({key: "value"})

    expected = _expected_map(
        matrix_data.by_path,
        {path: "value" for path in expected_paths},
    )
    assert result == expected


@pytest.mark.parametrize(
    "key",
    [
        "root>missing",
        "root>service>missing",
        "root>handler>2>repo",
        "root>tasks>queue>missing",
    ],
)
def test_matrix_path_missing_raises(matrix_data: _MatrixData, key: str) -> None:
    """
    Purpose:
        Validate missing PATH keys raise RuntimeError.
    Contract:
        - Path keys with no matching sockets are rejected.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        key: Missing path override key.
    Returns:
        None.
    Raises:
        AssertionError: If missing paths do not raise.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    with pytest.raises(RuntimeError, match="No sockets found for override path"):
        overrider.apply({key: "value"})


@pytest.mark.parametrize(
    "param_name,expected_path",
    [
        ("cache", "root>service>cache"),
        ("dsn", "root>service>db>dsn"),
        ("size", "root>service>db>pool>size"),
        ("timeout", "root>service>db>pool>timeout"),
        ("queue", "root>tasks>queue"),
        ("retry", "root>tasks>queue>retry"),
        ("mode", "root>ops>sink>mode"),
        ("level", "root>ops>trace>level"),
        ("sink", "root>ops>sink"),
    ],
)
def test_matrix_unique_targets_expected(
    matrix_data: _MatrixData,
    param_name: str,
    expected_path: str,
) -> None:
    """
    Purpose:
        Validate UNIQUE overrides resolve single sockets by name.
    Contract:
        - Unique param names resolve to their single socket.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        param_name: Param name to target.
        expected_path: Expected path for the unique socket.
    Returns:
        None.
    Raises:
        AssertionError: If unique targeting fails.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    result = overrider.apply({f"*{param_name}": "value"})

    expected = _expected_map(matrix_data.by_path, {expected_path: "value"})
    assert result == expected


@pytest.mark.parametrize(
    "param_name,match",
    [
        ("repo", "expected exactly one"),
        ("logger", "expected exactly one"),
        ("missing", "No sockets found for unique override"),
    ],
)
def test_matrix_unique_errors(
    matrix_data: _MatrixData,
    param_name: str,
    match: str,
) -> None:
    """
    Purpose:
        Validate UNIQUE overrides reject missing or ambiguous matches.
    Contract:
        - Missing or multiple matches raise RuntimeError.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        param_name: Param name to target.
        match: Expected error message fragment.
    Returns:
        None.
    Raises:
        AssertionError: If UNIQUE errors do not raise.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    with pytest.raises(RuntimeError, match=match):
        overrider.apply({f"*{param_name}": "value"})


@pytest.mark.parametrize(
    "param_name,expected_paths",
    [
        ("repo", ["root>repo", "root>service>repo", "root>handler>0>repo", "root>handler>1>repo"]),
        ("logger", ["root>service>logger", "root>metrics>logger"]),
        ("cache", ["root>service>cache"]),
        ("queue", ["root>tasks>queue"]),
        ("retry", ["root>tasks>queue>retry"]),
        ("sink", ["root>ops>sink"]),
        ("mode", ["root>ops>sink>mode"]),
        ("level", ["root>ops>trace>level"]),
    ],
)
def test_matrix_broadcast_targets_expected(
    matrix_data: _MatrixData,
    param_name: str,
    expected_paths: list[str],
) -> None:
    """
    Purpose:
        Validate BROADCAST overrides resolve all sockets by name.
    Contract:
        - Broadcast param names map to every socket with that name.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        param_name: Param name to broadcast.
        expected_paths: Path keys expected to match.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast targeting is incorrect.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    result = overrider.apply({f"**{param_name}": "value"})

    expected = _expected_map(
        matrix_data.by_path,
        {path: "value" for path in expected_paths},
    )
    assert result == expected


def test_matrix_broadcast_missing_raises(matrix_data: _MatrixData) -> None:
    """
    Purpose:
        Validate BROADCAST overrides reject missing param names.
    Contract:
        - Missing broadcast targets raise RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If missing broadcast targets do not raise.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    with pytest.raises(RuntimeError, match="No sockets found for broadcast override"):
        overrider.apply({"**missing": "value"})


@pytest.mark.parametrize(
    "override_map,expected_paths",
    [
        (
            {"**repo": "broad", "root>repo": "path"},
            {
                "root>repo": "path",
                "root>service>repo": "broad",
                "root>handler>0>repo": "broad",
                "root>handler>1>repo": "broad",
            },
        ),
        (
            {"**logger": "broad", "root>service>logger": "path"},
            {
                "root>service>logger": "path",
                "root>metrics>logger": "broad",
            },
        ),
        (
            {"**cache": "broad", "*cache": "unique"},
            {"root>service>cache": "unique"},
        ),
        (
            {"**cache": "broad", "*cache": "unique", "root>service>cache": "path"},
            {"root>service>cache": "path"},
        ),
        (
            {"**sink": "broad", "*mode": "unique", "root>ops>sink>mode": "path"},
            {
                "root>ops>sink": "broad",
                "root>ops>sink>mode": "path",
            },
        ),
        (
            {
                "**repo": "broad",
                "root>handler>0>repo": "path-a",
                "root>handler>1>repo": "path-b",
            },
            {
                "root>repo": "broad",
                "root>service>repo": "broad",
                "root>handler>0>repo": "path-a",
                "root>handler>1>repo": "path-b",
            },
        ),
    ],
)
def test_matrix_specificity_precedence(
    matrix_data: _MatrixData,
    override_map: dict[str, str],
    expected_paths: dict[str, str],
) -> None:
    """
    Purpose:
        Validate specificity precedence across PATH, UNIQUE, and BROADCAST.
    Contract:
        - PATH overrides beat UNIQUE and BROADCAST for the same socket.
        - UNIQUE overrides beat BROADCAST for the same socket.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        override_map: Override map applied to the overrider.
        expected_paths: Expected socket assignments keyed by path.
    Returns:
        None.
    Raises:
        AssertionError: If specificity precedence is incorrect.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    result = overrider.apply(override_map)

    expected = _expected_map(matrix_data.by_path, expected_paths)
    assert result == expected


@pytest.mark.parametrize(
    "override_map",
    [
        {"root>service>repo": "a", "root > service > repo": "b"},
        {"root>service>cache": "a", "root>service>cache ": "b"},
        {"*cache": "a", "* cache": "b"},
        {"**logger": "a", "** logger": "b"},
        {"root>ops>sink>mode": "a", "root > ops > sink > mode": "b"},
        {"*mode": "a", "* mode": "b"},
    ],
)
def test_matrix_conflicting_same_specificity_raises(
    matrix_data: _MatrixData,
    override_map: dict[str, str],
) -> None:
    """
    Purpose:
        Validate conflicting overrides at the same specificity raise errors.
    Contract:
        - Conflicting PATH/UNIQUE/BROADCAST rules are rejected.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        override_map: Override map with conflicting rules.
    Returns:
        None.
    Raises:
        AssertionError: If conflicts do not raise.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    with pytest.raises(RuntimeError, match="Conflicting overrides"):
        overrider.apply(override_map)


@pytest.mark.parametrize(
    "override_map,match",
    [
        ({None: "value"}, "Override key must not be None"),
        ({"": "value"}, "Override key must not be empty"),
        ({"   ": "value"}, "Override key must not be empty"),
        ({">": "value"}, "did not contain any segments"),
        ({"*": "value"}, "missing a parameter name"),
        ({"**": "value"}, "missing a parameter name"),
    ],
)
def test_matrix_invalid_keys_raise(
    matrix_data: _MatrixData,
    override_map: dict[object, str],
    match: str,
) -> None:
    """
    Purpose:
        Validate invalid override keys raise ValueError.
    Contract:
        - Invalid keys are rejected before targeting.
    Args:
        matrix_data: Shared matrix blueprint and lookup maps.
        override_map: Override map with invalid keys.
        match: Expected error message fragment.
    Returns:
        None.
    Raises:
        AssertionError: If invalid keys do not raise.
    """
    overrider = SpellOverrider(matrix_data.blueprint)

    with pytest.raises(ValueError, match=match):
        overrider.apply(override_map)
