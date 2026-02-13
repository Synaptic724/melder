"""Contract tests for CreationContext execution routing and planning helpers."""
import threading
import time
from types import SimpleNamespace
from typing import Any, Iterable

import pytest

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.occurrence_plan import OccurrencePlanBuilder
from melder.spellbook.spell_crafter.dag.dag_index import PathRegistry, SocketRef
from melder.spellbook.spell_crafter.dag.socket_kind import SocketKind
from melder.utilities.synchronization.creation_gate import CreationGate


def _make_socket_ref(
        *,
        node_id: str,
        param_name: str,
        param_path: Iterable[str],
        path_registry: PathRegistry,
        socket_kind: SocketKind = SocketKind.NORMAL,
) -> SocketRef:
    """
    Build a SocketRef for override-target shape helper tests.
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
        spell: Any = None,
) -> SimpleNamespace:
    """
    Build a minimal spell stub with OccurrencePlanBuilder-required attributes.
    """
    resolved_spell = spell
    if resolved_spell is None:
        def _default_callable(**_kwargs: Any) -> str:
            return "value:{0}".format(spell_id)

        resolved_spell = _default_callable
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SpellIndex(spell_id),
        spell=resolved_spell,
        existence=existence,
    )


def _make_execute_dispatch_harness() -> tuple[CreationContext, list[str]]:
    """
    Build a minimal CreationContext instance used only for execute-door routing.
    """
    calls: list[str] = []
    context = object.__new__(CreationContext)
    context._cleaned = False
    context._dynamic_environment = False
    context._creation_gate = None
    context._creation_gate_lineage_id = None

    def _hooks_no_overrides(caller_creations: Any) -> tuple[str, bool]:
        calls.append("hooks_no_overrides")
        return "no-overrides", False

    def _hooks_overrides(
            caller_creations: Any,
            overrides: dict[str, Any],
    ) -> tuple[str, bool]:
        calls.append("hooks_overrides")
        return "with-overrides", True

    def _no_hooks_no_overrides(caller_creations: Any) -> str:
        calls.append("no_hooks_no_overrides")
        return "no-hooks-no-overrides"

    def _no_hooks_overrides(
            caller_creations: Any,
            overrides: dict[str, Any],
    ) -> str:
        calls.append("no_hooks_overrides")
        return "no-hooks-overrides"

    context._execute_hooks_no_overrides_compiled = _hooks_no_overrides
    context._execute_hooks_overrides_compiled = _hooks_overrides
    context._execute_no_hooks_no_overrides_compiled = _no_hooks_no_overrides
    context._execute_no_hooks_overrides_compiled = _no_hooks_overrides
    return context, calls


def test_execute_routes_to_overrides_when_payload_present() -> None:
    """
    Verify execute routes to the hooks+overrides compiled door when overrides exist.
    """
    context, calls = _make_execute_dispatch_harness()
    assert context.execute(object(), overrides={"x": 1}) == ("with-overrides", True)
    assert calls == ["hooks_overrides"]


def test_execute_routes_to_no_overrides_when_payload_missing() -> None:
    """
    Verify execute routes to the hooks+no-overrides compiled door on empty payload.
    """
    context, calls = _make_execute_dispatch_harness()
    assert context.execute(object(), overrides=None) == ("no-overrides", False)
    assert calls == ["hooks_no_overrides"]


def test_execute_no_hooks_routes_to_overrides_when_payload_present() -> None:
    """
    Verify execute_no_hooks routes to no-hooks overrides compiled door.
    """
    context, calls = _make_execute_dispatch_harness()
    assert context.execute_no_hooks(object(), overrides={"x": 1}) == "no-hooks-overrides"
    assert calls == ["no_hooks_overrides"]


def test_execute_no_hooks_routes_to_no_overrides_when_payload_missing() -> None:
    """
    Verify execute_no_hooks routes to no-hooks no-overrides compiled door.
    """
    context, calls = _make_execute_dispatch_harness()
    assert context.execute_no_hooks(object(), overrides=None) == "no-hooks-no-overrides"
    assert calls == ["no_hooks_no_overrides"]


def test_execute_dynamic_gate_closed_raises() -> None:
    """
    Verify dynamic execute fails fast when spell-lineage gate is terminally closed.
    """
    context, _calls = _make_execute_dispatch_harness()
    context._dynamic_environment = True
    context._creation_gate_lineage_id = "lineage-s1"
    gate = CreationGate()
    gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
    context._creation_gate = gate

    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        context.execute(object(), overrides=None)


def test_execute_dynamic_gate_registers_and_unregisters_ticket() -> None:
    """
    Verify dynamic execute tracks one gate ticket around compiled dispatch.
    """
    context, calls = _make_execute_dispatch_harness()
    context._dynamic_environment = True
    context._creation_gate_lineage_id = "lineage-s1"
    gate = CreationGate()
    context._creation_gate = gate

    assert gate.active_ticket_count() == 0
    assert context.execute(object(), overrides=None) == ("no-overrides", False)
    assert calls == ["hooks_no_overrides"]
    assert gate.active_ticket_count() == 0


def test_execute_no_hooks_dynamic_gate_registers_and_unregisters_ticket() -> None:
    """
    Verify dynamic execute_no_hooks tracks one gate ticket around dispatch.
    """
    context, calls = _make_execute_dispatch_harness()
    context._dynamic_environment = True
    context._creation_gate_lineage_id = "lineage-s1"
    gate = CreationGate()
    context._creation_gate = gate

    assert gate.active_ticket_count() == 0
    assert context.execute_no_hooks(object(), overrides=None) == "no-hooks-no-overrides"
    assert calls == ["no_hooks_no_overrides"]
    assert gate.active_ticket_count() == 0


def test_execute_dynamic_gate_blocks_until_open() -> None:
    """
    Verify dynamic execute waits while gate is disabled and resumes after open.
    """
    context, calls = _make_execute_dispatch_harness()
    context._dynamic_environment = True
    context._creation_gate_lineage_id = "lineage-s1"
    gate = CreationGate()
    gate.close()
    context._creation_gate = gate

    result_box: list[tuple[str, bool]] = []
    done = threading.Event()

    def _worker() -> None:
        result_box.append(context.execute(object(), overrides=None))
        done.set()

    thread = threading.Thread(target=_worker)
    thread.start()
    time.sleep(0.03)
    gate.open()
    done.wait(timeout=1.0)
    thread.join(timeout=1.0)

    assert result_box == [("no-overrides", False)]
    assert calls == ["hooks_no_overrides"]


def test_collect_override_targets_groups_by_spell_id() -> None:
    """
    Verify override-target grouping is keyed by socket node id and shape rows.
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
    grouped, shape = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map,
    )
    assert set(grouped.keys()) == {"node-a", "node-b"}
    assert len(grouped["node-a"]) == 1
    assert len(grouped["node-b"]) == 1
    assert len(shape) == 2


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
    Verify shared-existence helper treats Existence.many as non-shared.
    """
    assert OccurrencePlanBuilder._is_shared_existence(existence) is expected


def test_instance_key_for_occurrence_shared_collapses_path() -> None:
    """
    Verify shared occurrence keys collapse path-id for shared existences.
    """
    spell = _make_spell(spell_id="node", existence=Existence.unique)
    builder = object.__new__(OccurrencePlanBuilder)
    builder._spell_lookup = {"node": spell}
    path_registry = PathRegistry()
    path_id = path_registry.extend_path(path_registry.root_path_id, "left")
    assert builder._instance_key_for_occurrence(("node", path_id)) == ("node", None)


def test_instance_key_for_occurrence_many_preserves_path() -> None:
    """
    Verify Existence.many keeps occurrence path-id in instance keys.
    """
    spell = _make_spell(spell_id="node", existence=Existence.many)
    builder = object.__new__(OccurrencePlanBuilder)
    builder._spell_lookup = {"node": spell}
    path_registry = PathRegistry()
    path_id = path_registry.extend_path(path_registry.root_path_id, "left")
    assert builder._instance_key_for_occurrence(("node", path_id)) == ("node", path_id)


def test_select_canonical_occurrence_returns_lexicographically_smallest() -> None:
    """
    Verify canonical occurrence selection is deterministic across insertion order.
    """
    path_registry = PathRegistry()
    left_id = path_registry.extend_path(path_registry.root_path_id, "left")
    right_id = path_registry.extend_path(path_registry.root_path_id, "right")
    occurrences = [("node", right_id), ("node", left_id)]
    assert OccurrencePlanBuilder._select_canonical_occurrence(occurrences) == ("node", left_id)


def test_build_override_shape_key_tracks_socket_targets() -> None:
    """
    Verify shape key changes when socket-target shape changes.
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

    _, shape_a = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map_a,
    )
    _, shape_b = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map_b,
    )

    key_a = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides", "sig-rows"),
        socket_shape=shape_a,
        root_positional_override=None,
    )
    key_b = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides", "sig-rows"),
        socket_shape=shape_b,
        root_positional_override=None,
    )
    assert key_a != key_b


def test_build_override_shape_key_tracks_positional_arity() -> None:
    """
    Verify shape key includes root positional override arity.
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
    _, shape = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map,
    )

    no_args_key = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides", "sig-rows"),
        socket_shape=shape,
        root_positional_override=None,
    )
    two_args_key = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides", "sig-rows"),
        socket_shape=shape,
        root_positional_override=("a", "b"),
    )
    assert no_args_key != two_args_key


def test_build_override_shape_key_changes_when_signature_changes() -> None:
    """
    Verify shape key changes when the plan-signature tuple changes.
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
    _, shape = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map,
    )

    key_a = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides-a", "sig-rows"),
        socket_shape=shape,
        root_positional_override=None,
    )
    key_b = CreationContext._build_override_shape_key(
        plan_signature=("phase11_overrides_ir", "sig-overrides-b", "sig-rows"),
        socket_shape=shape,
        root_positional_override=None,
    )
    assert key_a != key_b
