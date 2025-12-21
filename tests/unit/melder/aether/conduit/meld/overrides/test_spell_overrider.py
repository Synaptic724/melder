"""Contract tests for SpellOverrider override targeting."""
from typing import Iterable
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.meld.overrides.spell_overrider import SpellOverrider
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.dag_index import DagIndex, SocketRef
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: tuple[str, ...],
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Build a SocketRef for override targeting.

    Args:
        node_id: Spell id owning the socket.
        param_name: Parameter name on the spell.
        param_path: Override path segments.
        socket_kind: Socket classification.

    Returns:
        SocketRef: Socket reference with the requested attributes.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=param_path,
        socket_kind=socket_kind,
    )


def _make_blueprint(
    *,
    root_id: str,
    root_lineage_id: str,
    socket_refs: Iterable[SocketRef],
) -> RootResolutionBlueprint:
    """
    Build a RootResolutionBlueprint with sockets indexed for overrides.

    Args:
        root_id: Root spell id for the blueprint.
        root_lineage_id: Lineage id for the root spell.
        socket_refs: Socket refs to add to the targeting index.

    Returns:
        RootResolutionBlueprint: Blueprint ready for SpellOverrider.
    """
    dag = DirectedAcyclicWorkGraph()
    dag.add_node(root_id)
    index = DagIndex()
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


def test_init_requires_blueprint() -> None:
    """
    Verify SpellOverrider rejects a None blueprint.

    Contract:
        - blueprint must not be None.
    """
    with pytest.raises(ValueError, match="blueprint must not be None"):
        SpellOverrider(None)


def test_cleanup_clears_references_and_is_idempotent() -> None:
    """
    Verify cleanup clears references and can be called repeatedly.

    Contract:
        - cleanup invokes the targeting engine cleanup.
        - cleanup nulls engine and blueprint references.
        - cleanup is idempotent.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)
    engine_mock = MagicMock()
    overrider._engine = engine_mock

    overrider.cleanup()

    engine_mock.cleanup.assert_called_once()
    assert overrider._engine is None
    assert overrider._blueprint is None
    assert overrider.cleaned is True

    overrider.cleanup()
    assert overrider._engine is None
    assert overrider._blueprint is None


def test_cleanup_ignores_engine_cleanup_errors() -> None:
    """
    Verify cleanup swallows engine cleanup exceptions.

    Contract:
        - engine cleanup errors do not propagate.
        - cleanup still nulls references.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)
    engine_mock = MagicMock()
    engine_mock.cleanup.side_effect = RuntimeError("boom")
    overrider._engine = engine_mock

    overrider.cleanup()

    assert overrider._engine is None
    assert overrider._blueprint is None


def test_apply_returns_empty_for_none_override() -> None:
    """
    Verify None overrides return an empty map.

    Contract:
        - None spell_override returns {}.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    assert overrider.apply(None) == {}


def test_apply_returns_empty_for_empty_override() -> None:
    """
    Verify empty overrides return an empty map.

    Contract:
        - empty dict spell_override returns {}.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    assert overrider.apply({}) == {}


def test_apply_path_targets_all_exact_matches() -> None:
    """
    Verify PATH overrides target all exact path matches.

    Contract:
        - path overrides apply to every socket with the same param_path.
    """
    socket_a = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    socket_b = _make_socket_ref(
        node_id="node-2",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"dep": "value"})

    assert result == {socket_a: "value", socket_b: "value"}


def test_apply_unique_targets_single_match() -> None:
    """
    Verify UNIQUE overrides target exactly one socket.

    Contract:
        - unique overrides map to the single matching socket.
    """
    socket_repo = _make_socket_ref(
        node_id="node-1",
        param_name="repo",
        param_path=("repo",),
    )
    socket_logger = _make_socket_ref(
        node_id="node-2",
        param_name="logger",
        param_path=("logger",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_repo, socket_logger],
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"*repo": "value"})

    assert result == {socket_repo: "value"}


def test_apply_unique_raises_for_zero_match() -> None:
    """
    Verify UNIQUE overrides error when no socket matches.

    Contract:
        - missing unique targets raise RuntimeError.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="unique override"):
        overrider.apply({"*missing": "value"})


def test_apply_unique_raises_for_multiple_matches() -> None:
    """
    Verify UNIQUE overrides error when multiple sockets match.

    Contract:
        - unique overrides must resolve to exactly one socket.
    """
    socket_a = _make_socket_ref(
        node_id="node-1",
        param_name="repo",
        param_path=("repo",),
    )
    socket_b = _make_socket_ref(
        node_id="node-2",
        param_name="repo",
        param_path=("alt", "repo"),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="expected exactly one"):
        overrider.apply({"*repo": "value"})


def test_apply_broadcast_targets_all_matches() -> None:
    """
    Verify BROADCAST overrides target all matching sockets.

    Contract:
        - broadcast overrides apply to every matching socket.
    """
    socket_a = _make_socket_ref(
        node_id="node-1",
        param_name="logger",
        param_path=("logger",),
    )
    socket_b = _make_socket_ref(
        node_id="node-2",
        param_name="logger",
        param_path=("child", "logger"),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_a, socket_b],
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"**logger": "value"})

    assert result == {socket_a: "value", socket_b: "value"}


def test_apply_broadcast_raises_for_no_matches() -> None:
    """
    Verify BROADCAST overrides error when no socket matches.

    Contract:
        - missing broadcast targets raise RuntimeError.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="broadcast override"):
        overrider.apply({"**missing": "value"})


def test_apply_prefers_more_specific_overrides() -> None:
    """
    Verify specificity precedence favors PATH over UNIQUE over BROADCAST.

    Contract:
        - more specific overrides replace less specific ones.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="repo",
        param_path=("repo",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    result = overrider.apply({"**repo": "broad", "*repo": "unique", "repo": "path"})

    assert result == {socket_ref: "path"}


def test_apply_raises_on_conflicting_same_specificity() -> None:
    """
    Verify conflicting rules with the same specificity raise an error.

    Contract:
        - same-specificity overrides with different values are rejected.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="b",
        param_path=("a", "b"),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    with pytest.raises(RuntimeError, match="Conflicting overrides"):
        overrider.apply({"a>b": "first", "a > b": "second"})


def test_apply_after_cleanup_raises() -> None:
    """
    Verify apply rejects usage after cleanup.

    Contract:
        - cleaned instances raise RuntimeError on apply.
    """
    socket_ref = _make_socket_ref(
        node_id="node-1",
        param_name="dep",
        param_path=("dep",),
    )
    blueprint = _make_blueprint(
        root_id="root",
        root_lineage_id="lineage-1",
        socket_refs=[socket_ref],
    )
    overrider = SpellOverrider(blueprint)

    overrider.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        overrider.apply({})
