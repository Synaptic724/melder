"""Additional contract tests for meld runtime/planning helpers."""
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Optional
from unittest.mock import MagicMock
import pytest
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.spellbook.spell_crafter.dag.dag_index import PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind


def _make_socket_ref(
    *,
    node_id: str,
    param_name: str,
    param_path: Iterable[str],
    path_registry: PathRegistry,
    socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Build a SocketRef for override targeting.
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


def _make_override_execution_plan(
    *,
    plan_variant: str = "overrides",
    root_spell_id: str = "root",
    step_overrides: Optional[Dict[str, Any]] = None,
) -> SimpleNamespace:
    """
    Build a minimal override execution-plan stub for shape-key tests.
    """
    step = SimpleNamespace(
        instance_key=("node", None),
        spell=_make_spell(spell_id="node"),
        existence=Existence.unique,
        creations_target_kind=1,
        shared_instance=False,
        dependency_resolution_order=[("dep", [("dep-node", None)])],
        override_match_prefix=None,
        override_match_prefix_len=0,
        override_keys=["dep"],
        use_spell_lock_hint=False,
        must_register=False,
        uses_positional_override=False,
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
    )
    if step_overrides:
        for key, value in step_overrides.items():
            setattr(step, key, value)
    return SimpleNamespace(
        plan_variant=plan_variant,
        root_spell_id=root_spell_id,
        steps=[step],
    )


def test_execute_routes_to_overrides_when_payload_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify execute routes to override execution when overrides are provided.
    """
    runtime = MeldRuntime()
    monkeypatch.setattr(
        MeldRuntime,
        "_enforce_spell_invariants",
        staticmethod(lambda spell, conduit_id: None),
    )
    calls: list[str] = []

    def _execute_no_overrides(*, context: Any, spell: Any) -> str:
        calls.append("no")
        return "no-overrides"

    def _execute_with_overrides(*, context: Any, spell: Any) -> str:
        calls.append("with")
        return "with-overrides"

    monkeypatch.setattr(
        MeldRuntime,
        "_execute_no_overrides",
        staticmethod(_execute_no_overrides),
    )
    monkeypatch.setattr(
        MeldRuntime,
        "_execute_with_overrides",
        staticmethod(_execute_with_overrides),
    )

    spell = SimpleNamespace(
        has_mutation_override=False,
        spell_index=SpellIndex("root"),
        spell_name="root",
    )
    context = SimpleNamespace(
        root_spell=spell,
        conduit_id="conduit-1",
        overrides={"x": 1},
    )

    assert runtime.execute(context) == "with-overrides"
    assert calls == ["with"]


def test_execute_routes_to_no_overrides_when_payload_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify execute routes to no-overrides execution when overrides are empty.
    """
    runtime = MeldRuntime()
    monkeypatch.setattr(
        MeldRuntime,
        "_enforce_spell_invariants",
        staticmethod(lambda spell, conduit_id: None),
    )
    calls: list[str] = []

    def _execute_no_overrides(*, context: Any, spell: Any) -> str:
        calls.append("no")
        return "no-overrides"

    def _execute_with_overrides(*, context: Any, spell: Any) -> str:
        calls.append("with")
        return "with-overrides"

    monkeypatch.setattr(
        MeldRuntime,
        "_execute_no_overrides",
        staticmethod(_execute_no_overrides),
    )
    monkeypatch.setattr(
        MeldRuntime,
        "_execute_with_overrides",
        staticmethod(_execute_with_overrides),
    )

    spell = SimpleNamespace(
        has_mutation_override=False,
        spell_index=SpellIndex("root"),
        spell_name="root",
    )
    context = SimpleNamespace(
        root_spell=spell,
        conduit_id="conduit-1",
        overrides=None,
    )

    assert runtime.execute(context) == "no-overrides"
    assert calls == ["no"]


def test_collect_override_targets_groups_by_spell_id() -> None:
    """
    Verify override targets are grouped by spell id.
    """
    path_registry = PathRegistry()
    override_map = {
        _make_socket_ref(
            node_id="node-a",
            param_name="x",
            param_path=("x",),
            path_registry=path_registry,
        ): "a",
        _make_socket_ref(
            node_id="node-b",
            param_name="y",
            param_path=("y",),
            path_registry=path_registry,
        ): "b",
    }
    grouped = MeldRuntime._collect_override_targets(override_map=override_map)
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
    path_registry = PathRegistry()
    path_id = path_registry.extend_path(path_registry.root_path_id, "left")
    assert builder._instance_key_for_occurrence(("node", path_id)) == ("node", None)


def test_instance_key_for_occurrence_many_preserves_path() -> None:
    """
    Verify Existence.many preserves occurrence paths.
    """
    spell = _make_spell(spell_id="node", existence=Existence.many)
    builder = object.__new__(OccurrencePlanBuilder)
    builder._spell_lookup = {"node": spell}
    path_registry = PathRegistry()
    path_id = path_registry.extend_path(path_registry.root_path_id, "left")
    assert builder._instance_key_for_occurrence(("node", path_id)) == ("node", path_id)


def test_select_canonical_occurrence_returns_lexicographically_smallest() -> None:
    """
    Verify canonical occurrence selection is stable across insertion order.
    """
    path_registry = PathRegistry()
    left_id = path_registry.extend_path(path_registry.root_path_id, "left")
    right_id = path_registry.extend_path(path_registry.root_path_id, "right")
    occurrences = [("node", right_id), ("node", left_id)]
    assert OccurrencePlanBuilder._select_canonical_occurrence(occurrences) == ("node", left_id)


def test_build_override_shape_key_tracks_socket_targets() -> None:
    """
    Verify override shape key changes with socket target shape.
    """
    path_registry = PathRegistry()
    override_map_a = {
        _make_socket_ref(
            node_id="node",
            param_name="x",
            param_path=("left", "x"),
            path_registry=path_registry,
        ): "left",
        _make_socket_ref(
            node_id="node",
            param_name="y",
            param_path=("right", "y"),
            path_registry=path_registry,
        ): "right",
    }
    override_map_b = {
        _make_socket_ref(
            node_id="node",
            param_name="x",
            param_path=("left", "x"),
            path_registry=path_registry,
        ): "left",
    }

    grouped_a = MeldRuntime._collect_override_targets(override_map=override_map_a)
    grouped_b = MeldRuntime._collect_override_targets(override_map=override_map_b)
    execution_plan = _make_override_execution_plan()
    plan_signature = MeldRuntime._build_override_plan_signature(
        execution_plan=execution_plan,
    )

    key_a = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature,
        override_targets_by_spell_id=grouped_a,
        root_positional_override=None,
    )
    key_b = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature,
        override_targets_by_spell_id=grouped_b,
        root_positional_override=None,
    )
    assert key_a != key_b


def test_build_override_shape_key_tracks_positional_arity() -> None:
    """
    Verify override shape key includes root positional override arity.
    """
    path_registry = PathRegistry()
    override_map = {
        _make_socket_ref(
            node_id="node",
            param_name="x",
            param_path=("left", "x"),
            path_registry=path_registry,
        ): "match",
        _make_socket_ref(
            node_id="node",
            param_name="y",
            param_path=("right", "y"),
            path_registry=path_registry,
        ): "skip",
    }
    grouped = MeldRuntime._collect_override_targets(override_map=override_map)
    execution_plan = _make_override_execution_plan()
    plan_signature = MeldRuntime._build_override_plan_signature(
        execution_plan=execution_plan,
    )

    no_args_key = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature,
        override_targets_by_spell_id=grouped,
        root_positional_override=None,
    )
    two_args_key = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature,
        override_targets_by_spell_id=grouped,
        root_positional_override=("a", "b"),
    )
    assert no_args_key != two_args_key


def test_build_override_shape_key_ignores_plan_object_identity_for_equivalent_plans() -> None:
    """
    Equivalent plan semantics produce the same shape key across object rebuilds.
    """
    path_registry = PathRegistry()
    override_map = {
        _make_socket_ref(
            node_id="node",
            param_name="x",
            param_path=("left", "x"),
            path_registry=path_registry,
        ): "left",
    }
    grouped = MeldRuntime._collect_override_targets(override_map=override_map)
    plan_a = _make_override_execution_plan()
    plan_b = _make_override_execution_plan()
    plan_signature_a = MeldRuntime._build_override_plan_signature(
        execution_plan=plan_a,
    )
    plan_signature_b = MeldRuntime._build_override_plan_signature(
        execution_plan=plan_b,
    )

    key_a = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature_a,
        override_targets_by_spell_id=grouped,
        root_positional_override=None,
    )
    key_b = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature_b,
        override_targets_by_spell_id=grouped,
        root_positional_override=None,
    )
    assert key_a == key_b


def test_build_override_shape_key_changes_when_plan_semantics_change() -> None:
    """
    Shape key changes when execution-plan step semantics change.
    """
    path_registry = PathRegistry()
    override_map = {
        _make_socket_ref(
            node_id="node",
            param_name="x",
            param_path=("left", "x"),
            path_registry=path_registry,
        ): "left",
    }
    grouped = MeldRuntime._collect_override_targets(override_map=override_map)
    plan_a = _make_override_execution_plan(
        step_overrides={"override_keys": ["dep"]},
    )
    plan_b = _make_override_execution_plan(
        step_overrides={"override_keys": ["dep", "other"]},
    )
    plan_signature_a = MeldRuntime._build_override_plan_signature(
        execution_plan=plan_a,
    )
    plan_signature_b = MeldRuntime._build_override_plan_signature(
        execution_plan=plan_b,
    )

    key_a = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature_a,
        override_targets_by_spell_id=grouped,
        root_positional_override=None,
    )
    key_b = MeldRuntime._build_override_shape_key(
        plan_signature=plan_signature_b,
        override_targets_by_spell_id=grouped,
        root_positional_override=None,
    )
    assert key_a != key_b
