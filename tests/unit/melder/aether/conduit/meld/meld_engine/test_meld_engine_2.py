"""Additional contract tests for meld runtime/planning helpers."""
from types import SimpleNamespace
from typing import Any, Iterable

import pytest

from melder.aether.conduit.meld.meld_engine.meld_engine import MeldEngine
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.spellbook.spell_crafter.dag.dag_index import SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: Iterable[str],
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Build a SocketRef for override targeting.
    """
    return SocketRef(
        node_id=node_id,
        param_name=param_name,
        param_path=tuple(param_path),
        socket_kind=socket_kind,
    )


def _make_spell(
    *,
    spell_id: str,
    existence: Existence = Existence.unique,
    spell: Any | None = None,
) -> SimpleNamespace:
    """
    Build a minimal spell stub with OccurrencePlanBuilder-required attributes.
    """
    if spell is None:
        def _default_callable(**_kwargs: Any) -> str:
            return f"value:{spell_id}"
        spell = _default_callable
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SpellIndex(spell_id),
        spell=spell,
        existence=existence,
    )


def test_detect_any_overrides_true_with_override_map() -> None:
    """
    Verify override detection returns True for socket overrides.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("x",)): 1
    }
    assert MeldRuntime._detect_any_overrides(
        override_payload=None,
        override_map=override_map,
        contract_overrides_by_spell_id={},
    ) is True


def test_detect_any_overrides_false_with_empty_inputs() -> None:
    """
    Verify override detection returns False with no overrides.
    """
    assert MeldRuntime._detect_any_overrides(
        override_payload=None,
        override_map={},
        contract_overrides_by_spell_id={},
    ) is False


def test_collect_override_targets_groups_by_spell_id() -> None:
    """
    Verify override targets are grouped by spell id.
    """
    override_map = {
        _make_socket_ref(node_id="node-a", param_name="x", param_path=("x",)): "a",
        _make_socket_ref(node_id="node-b", param_name="y", param_path=("y",)): "b",
    }
    grouped = MeldRuntime._collect_override_targets(override_map)
    assert set(grouped.keys()) == {"node-a", "node-b"}
    assert len(grouped["node-a"]) == 1
    assert len(grouped["node-b"]) == 1


@pytest.mark.parametrize(
    "existence, expected",
    (
        (Existence.many, False),
        (Existence.unique, True),
        (Existence.unique_per_conduit, True),
    ),
)
def test_is_shared_existence_marks_many_as_false(
    existence: Existence,
    expected: bool,
) -> None:
    """
    Verify shared existence detection treats Existence.many as non-shared.
    """
    assert OccurrencePlanBuilder._is_shared_existence(existence) is expected


def test_instance_key_for_occurrence_shared_collapses_path() -> None:
    """
    Verify shared occurrences collapse to None paths.
    """
    spell = _make_spell(spell_id="node", existence=Existence.unique)
    builder = object.__new__(OccurrencePlanBuilder)
    builder._spell_lookup = {"node": spell}
    assert builder._instance_key_for_occurrence(("node", ("left",))) == ("node", None)


def test_instance_key_for_occurrence_many_preserves_path() -> None:
    """
    Verify Existence.many preserves occurrence paths.
    """
    spell = _make_spell(spell_id="node", existence=Existence.many)
    builder = object.__new__(OccurrencePlanBuilder)
    builder._spell_lookup = {"node": spell}
    assert builder._instance_key_for_occurrence(("node", ("left",))) == ("node", ("left",))


def test_select_canonical_occurrence_returns_first() -> None:
    """
    Verify canonical occurrence selection returns the first entry.
    """
    occurrences = [("node", ("left",)), ("node", ("right",))]
    assert OccurrencePlanBuilder._select_canonical_occurrence(occurrences) == occurrences[0]


def test_build_instance_override_map_shared_applies_all_params() -> None:
    """
    Verify shared override selection ignores param paths.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("left", "x")): "left",
        _make_socket_ref(node_id="node", param_name="y", param_path=("right", "y")): "right",
    }
    engine = object.__new__(MeldEngine)
    engine._override_map = override_map
    override_targets = list(override_map.keys())
    overrides = engine._build_instance_override_map(
        override_targets=override_targets,
        shared=True,
        match_prefix=("left",),
        match_prefix_len=1,
    )
    assert overrides == {"x": "left", "y": "right"}


def test_build_instance_override_map_path_matches_prefix() -> None:
    """
    Verify per-path override selection matches occurrence prefixes.
    """
    override_map = {
        _make_socket_ref(node_id="node", param_name="x", param_path=("left", "x")): "match",
        _make_socket_ref(node_id="node", param_name="y", param_path=("right", "y")): "skip",
    }
    engine = object.__new__(MeldEngine)
    engine._override_map = override_map
    override_targets = list(override_map.keys())
    overrides = engine._build_instance_override_map(
        override_targets=override_targets,
        shared=False,
        match_prefix=("left",),
        match_prefix_len=1,
    )
    assert overrides == {"x": "match"}
