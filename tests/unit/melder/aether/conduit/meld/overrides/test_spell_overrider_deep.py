"""Deep targeting tests for SpellOverrider override matching."""
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


def test_apply_path_targets_multiple_deep_sockets() -> None:
    """
    Purpose:
        Validate PATH overrides target multiple sockets with the same deep path.
    Contract:
        - All sockets sharing the same deep param_path are updated.
    Returns:
        None.
    Raises:
        AssertionError: If any deep socket is missed.
    """
    path_registry = PathRegistry()
    socket_a = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    socket_b = _make_socket_ref(
        node_id="node-b",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"root>service>repo": "value"})

    assert result == {socket_a: "value", socket_b: "value"}


def test_apply_path_matches_exact_path_only() -> None:
    """
    Purpose:
        Validate PATH overrides require an exact path match.
    Contract:
        - A shorter path does not match deeper sockets.
    Returns:
        None.
    Raises:
        AssertionError: If non-exact paths match.
    """
    path_registry = PathRegistry()
    socket_a = _make_socket_ref(
        node_id="node-a",
        param_name="service",
        param_path=("root", "service"),
        path_registry=path_registry,
    )
    socket_b = _make_socket_ref(
        node_id="node-b",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"root>service": "value"})

    assert result == {socket_a: "value"}


def test_apply_path_trims_segments_whitespace() -> None:
    """
    Purpose:
        Validate PATH parsing trims whitespace around segments.
    Contract:
        - Whitespace-delimited paths resolve to the same sockets.
    Returns:
        None.
    Raises:
        AssertionError: If whitespace prevents matching.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({" root > service > repo ": "value"})

    assert result == {socket_ref: "value"}


def test_apply_path_supports_numeric_segment() -> None:
    """
    Purpose:
        Validate PATH overrides allow numeric segments.
    Contract:
        - Numeric string segments are treated as normal path tokens.
    Returns:
        None.
    Raises:
        AssertionError: If numeric segments do not match.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("root", "0", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"root>0>repo": "value"})

    assert result == {socket_ref: "value"}


def test_apply_unique_matches_single_deep_socket() -> None:
    """
    Purpose:
        Validate UNIQUE overrides target a single deep socket by name.
    Contract:
        - A unique param name maps to its socket regardless of path depth.
    Returns:
        None.
    Raises:
        AssertionError: If the unique target is not resolved.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="cache",
        param_path=("root", "service", "cache"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"*cache": "value"})

    assert result == {socket_ref: "value"}


def test_apply_unique_raises_when_multiple_depths_match() -> None:
    """
    Purpose:
        Validate UNIQUE overrides raise when multiple sockets share the name.
    Contract:
        - Unique overrides must resolve to exactly one socket.
    Returns:
        None.
    Raises:
        AssertionError: If multiple matches do not raise.
    """
    path_registry = PathRegistry()
    socket_a = _make_socket_ref(
        node_id="node-a",
        param_name="cache",
        param_path=("root", "cache"),
        path_registry=path_registry,
    )
    socket_b = _make_socket_ref(
        node_id="node-b",
        param_name="cache",
        param_path=("root", "service", "cache"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="expected exactly one"):
        overrider.apply({"*cache": "value"})


def test_apply_broadcast_targets_multiple_depths() -> None:
    """
    Purpose:
        Validate BROADCAST overrides target all sockets with the same name.
    Contract:
        - Every socket whose param_name matches receives the broadcast value.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast matching is incomplete.
    """
    path_registry = PathRegistry()
    socket_a = _make_socket_ref(
        node_id="node-a",
        param_name="logger",
        param_path=("root", "logger"),
        path_registry=path_registry,
    )
    socket_b = _make_socket_ref(
        node_id="node-b",
        param_name="logger",
        param_path=("root", "service", "logger"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"**logger": "value"})

    assert result == {socket_a: "value", socket_b: "value"}


def test_apply_path_overrides_broadcast_for_deep_socket_when_broadcast_last() -> None:
    """
    Purpose:
        Validate PATH overrides win over BROADCAST for the same socket.
    Contract:
        - The deep socket keeps the PATH value even when BROADCAST is applied later.
        - Other sockets still receive the BROADCAST value.
    Returns:
        None.
    Raises:
        AssertionError: If specificity precedence is incorrect.
    """
    path_registry = PathRegistry()
    socket_root = _make_socket_ref(
        node_id="node-root",
        param_name="repo",
        param_path=("root", "repo"),
        path_registry=path_registry,
    )
    socket_deep = _make_socket_ref(
        node_id="node-deep",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_root, socket_deep],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply(
        {"root>service>repo": "path", "**repo": "broadcast"}
    )

    assert result == {socket_root: "broadcast", socket_deep: "path"}


def test_apply_broadcast_keeps_path_on_only_one_socket() -> None:
    """
    Purpose:
        Validate BROADCAST does not override a more specific PATH for one socket.
    Contract:
        - The targeted PATH socket keeps its value.
        - Other sockets with the same name receive the broadcast value.
    Returns:
        None.
    Raises:
        AssertionError: If broadcast overrides a path-specific socket.
    """
    path_registry = PathRegistry()
    socket_root = _make_socket_ref(
        node_id="node-root",
        param_name="repo",
        param_path=("root", "repo"),
        path_registry=path_registry,
    )
    socket_deep = _make_socket_ref(
        node_id="node-deep",
        param_name="repo",
        param_path=("root", "service", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_root, socket_deep],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply(
        {"**repo": "broadcast", "root>service>repo": "path"}
    )

    assert result == {socket_root: "broadcast", socket_deep: "path"}


def test_apply_combined_specificities_across_sockets() -> None:
    """
    Purpose:
        Validate combined PATH, UNIQUE, and BROADCAST overrides work together.
    Contract:
        - Each socket receives the override that targets it with correct precedence.
    Returns:
        None.
    Raises:
        AssertionError: If any socket receives the wrong value.
    """
    path_registry = PathRegistry()
    socket_repo = _make_socket_ref(
        node_id="node-repo",
        param_name="repo",
        param_path=("root", "repo"),
        path_registry=path_registry,
    )
    socket_cache = _make_socket_ref(
        node_id="node-cache",
        param_name="cache",
        param_path=("root", "cache"),
        path_registry=path_registry,
    )
    socket_logger = _make_socket_ref(
        node_id="node-logger",
        param_name="logger",
        param_path=("root", "service", "logger"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_repo, socket_cache, socket_logger],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply(
        {"**logger": "broadcast", "*cache": "unique", "root>repo": "path"}
    )

    assert result == {
        socket_repo: "path",
        socket_cache: "unique",
        socket_logger: "broadcast",
    }


def test_apply_conflicting_same_specificity_deep_path_raises() -> None:
    """
    Purpose:
        Validate conflicting PATH overrides on the same deep socket raise.
    Contract:
        - Different values at the same specificity trigger a RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If conflicting overrides do not raise.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("a", "b", "c"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="Conflicting overrides"):
        overrider.apply({"a>b>c": "one", "a > b > c": "two"})


def test_apply_multiple_path_keys_fill_map() -> None:
    """
    Purpose:
        Validate multiple PATH overrides populate the override map.
    Contract:
        - Each path key maps to its corresponding socket.
    Returns:
        None.
    Raises:
        AssertionError: If any mapping is missing.
    """
    path_registry = PathRegistry()
    socket_a = _make_socket_ref(
        node_id="node-a",
        param_name="a",
        param_path=("root", "a"),
        path_registry=path_registry,
    )
    socket_b = _make_socket_ref(
        node_id="node-b",
        param_name="b",
        param_path=("root", "b"),
        path_registry=path_registry,
    )
    socket_c = _make_socket_ref(
        node_id="node-c",
        param_name="c",
        param_path=("root", "service", "c"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b, socket_c],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply(
        {"root>a": "value-a", "root>b": "value-b", "root>service>c": "value-c"}
    )

    assert result == {
        socket_a: "value-a",
        socket_b: "value-b",
        socket_c: "value-c",
    }


def test_apply_same_specificity_same_value_no_conflict_deep_path() -> None:
    """
    Purpose:
        Validate duplicate PATH overrides with the same value are allowed.
    Contract:
        - Same-specificity overrides with equal values do not raise.
    Returns:
        None.
    Raises:
        AssertionError: If the override value is incorrect.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("a", "b", "c"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"a>b>c": "value", "a > b > c": "value"})

    assert result == {socket_ref: "value"}


def test_apply_raises_on_path_only_separators() -> None:
    """
    Purpose:
        Validate invalid PATH keys containing only separators are rejected.
    Contract:
        - A path with no segments raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If invalid path keys do not raise.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("repo",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(ValueError, match="did not contain any segments"):
        overrider.apply({">": "value"})


def test_apply_unique_raises_on_missing_param_name() -> None:
    """
    Purpose:
        Validate UNIQUE overrides require a param name.
    Contract:
        - Missing param names raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If missing names do not raise.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("repo",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(ValueError, match="missing a parameter name"):
        overrider.apply({"*   ": "value"})


def test_apply_broadcast_raises_on_missing_param_name() -> None:
    """
    Purpose:
        Validate BROADCAST overrides require a param name.
    Contract:
        - Missing param names raise ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If missing names do not raise.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("repo",),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(ValueError, match="missing a parameter name"):
        overrider.apply({"**   ": "value"})


def test_apply_path_targets_spell_contract_socket() -> None:
    """
    Purpose:
        Validate PATH overrides target SpellContract sockets.
    Contract:
        - Non-normal socket kinds are still eligible for overrides.
    Returns:
        None.
    Raises:
        AssertionError: If SpellContract sockets are skipped.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="contract",
        param_path=("root", "contract"),
        path_registry=path_registry,
        socket_kind=SocketKind.SPELL_CONTRACT,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"root>contract": "value"})

    assert result == {socket_ref: "value"}


def test_apply_unique_targets_mutation_contract_socket() -> None:
    """
    Purpose:
        Validate UNIQUE overrides target MutationContract sockets.
    Contract:
        - Unique targeting still applies for mutation contract sockets.
    Returns:
        None.
    Raises:
        AssertionError: If mutation contract sockets are skipped.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="mutant",
        param_path=("root", "mutant"),
        path_registry=path_registry,
        socket_kind=SocketKind.MUTATION_CONTRACT,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"*mutant": "value"})

    assert result == {socket_ref: "value"}


def test_apply_broadcast_targets_spell_contract_socket() -> None:
    """
    Purpose:
        Validate BROADCAST overrides target SpellContract sockets.
    Contract:
        - Broadcast targeting includes SpellContract sockets by name.
    Returns:
        None.
    Raises:
        AssertionError: If SpellContract sockets are skipped.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="contract",
        param_path=("root", "service", "contract"),
        path_registry=path_registry,
        socket_kind=SocketKind.SPELL_CONTRACT,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"**contract": "value"})

    assert result == {socket_ref: "value"}


def test_apply_path_overrides_unique_for_same_socket() -> None:
    """
    Purpose:
        Validate PATH overrides beat UNIQUE overrides on the same socket.
    Contract:
        - Higher specificity PATH overrides replace UNIQUE values.
    Returns:
        None.
    Raises:
        AssertionError: If PATH does not override UNIQUE.
    """
    path_registry = PathRegistry()
    socket_ref = _make_socket_ref(
        node_id="node-a",
        param_name="repo",
        param_path=("root", "repo"),
        path_registry=path_registry,
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
        path_registry=path_registry,
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"*repo": "unique", "root>repo": "path"})

    assert result == {socket_ref: "path"}
