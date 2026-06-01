"""CreationContext runtime contract tests for override and cache helpers."""
from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple

import pytest

import melder.aether.conduit.meld.creation_context.creation_context as creation_context_module
from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)
from melder.aether.spellbook.spell_compiler.blueprints.execution_plan import ExecutionPlanTargetKind
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _SocketKind:
    """Socket-kind value holder used by override socket-ref stubs."""

    def __init__(self, value: str) -> None:
        self.value = value


class _SocketRef:
    """Hashable socket-ref key used in override-map helper tests."""

    def __init__(self, node_id: str, param_name: str, path_id: int, kind: str) -> None:
        self.node_id = node_id
        self.param_name = param_name
        self.param_path_id = path_id
        self.socket_kind = _SocketKind(kind)

    def __hash__(self) -> int:
        return hash((self.node_id, self.param_name, self.param_path_id, self.socket_kind.value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _SocketRef):
            return False
        return (
            self.node_id == other.node_id
            and self.param_name == other.param_name
            and self.param_path_id == other.param_path_id
            and self.socket_kind.value == other.socket_kind.value
        )


def _make_spell(spell_id: str = "s1") -> Any:
    """
    Build a minimal spell stub required by CreationContext override helpers.
    """
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        _owner_creations=object(),
    )


def _make_plan_row(spell_id: str = "s1") -> Dict[str, Any]:
    """
    Build a minimal schema step row accepted by Phase12 override compile paths.
    """
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": ExecutionPlanTargetKind.CALLER,
        "shared_instance": True,
        "dependency_resolution_order": (),
        "override_match_prefix": None,
        "override_match_prefix_len": 0,
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
    }


def _make_route_config(
        *,
        plan_signature: Tuple[Any, ...],
        baseline_executor: Optional[Any] = None,
        plan_rows: Optional[Tuple[Dict[str, Any], ...]] = None,
) -> OverrideRouteConfig:
    """
    Build an OverrideRouteConfig used by override-lane harness tests.
    """
    return OverrideRouteConfig(
        plan_signature=plan_signature,
        path_registry="registry",
        plan_rows=plan_rows if plan_rows is not None else (_make_plan_row("s1"),),
        root_spell_id="s1",
        spell_lookup={"s1": object()},
        empty_shape_key=(plan_signature, (), -1),
        baseline_executor=baseline_executor,
    )


def _make_override_harness(
        *,
        route_config_active: OverrideRouteConfig,
        route_config_no_mutation: Optional[OverrideRouteConfig] = None,
        route_config_mutation: Optional[OverrideRouteConfig] = None,
        patch_map: Optional[Any] = None,
) -> CreationContext:
    """
    Build an object-level CreationContext harness for override runtime tests.
    """
    context = object.__new__(CreationContext)
    context._cleaned = False
    context._spell = _make_spell()
    context._spell_id = "s1"
    context._dynamic_environment = False
    context._creation_gate = None
    context._creation_gate_index_id = None
    context._owner_creations = object()
    context._execute_hooks_overrides_compiled = None
    context._execute_hooks_no_overrides_compiled = None
    context._execute_no_hooks_overrides_compiled = None
    context._execute_no_hooks_no_overrides_compiled = None
    context._no_overrides_executor = None
    context._override_targeting = patch_map
    if patch_map is None or not hasattr(
            patch_map,
            "_apply_with_socket_shape_prechecked",
    ):
        context._override_apply_with_socket_shape_prechecked_phase10 = None
    else:
        context._override_apply_with_socket_shape_prechecked_phase10 = (
            patch_map._apply_with_socket_shape_prechecked
        )
    context._override_route_config_no_mutation = route_config_no_mutation
    context._override_route_config_mutation = route_config_mutation
    context._override_route_config_active = route_config_active
    context._override_empty_shape_key = (
        route_config_active.plan_signature,
        (),
        -1,
    )
    context._override_specialization_cache = {}
    context._override_executor_source_cache_by_plan_signature = {}
    context._override_executor_code_object_cache_by_plan_signature = {}
    context._override_prefilter_step_targets_cache = {}
    context._override_prefilter_path_metadata_cache = {}
    context._override_socket_shape_cache = {}
    context._override_last_socket_shape = None
    context._override_last_root_positional_arity = -1
    context._override_last_executor = None
    return context


class _Gate:
    """Minimal CreationGate stub for execute-path tests."""

    def __init__(self, *, enabled: bool = True, closed: bool = False) -> None:
        self.enabled = enabled
        self._closed = closed
        self.wait_calls = 0
        self.register_calls = 0
        self.unregister_calls = 0

    def is_closed(self) -> bool:
        return self._closed

    def wait(self) -> None:
        self.wait_calls += 1

    def register_ticket(self) -> None:
        self.register_calls += 1

    def unregister_ticket(self) -> None:
        self.unregister_calls += 1


def test_split_override_payload_keeps_payload_when_no_root_args() -> None:
    """
    Verify payload split returns the original mapping when __args__ is absent.
    """
    spell = _make_spell()
    payload = {"dep": "value"}
    stripped_payload, root_args = CreationContext._split_override_payload(
        spell=spell,
        override_payload=payload,
    )
    assert stripped_payload is payload
    assert root_args is None


def test_override_route_config_cleanup_nulls_fields_and_is_idempotent() -> None:
    """
    Verify OverrideRouteConfig cleanup clears owned references and is idempotent.
    """
    config = _make_route_config(plan_signature=("phase11", "sig", "rows"))

    config.cleanup()
    config.cleanup()

    assert not hasattr(config, 'plan_signature')
    assert not hasattr(config, 'path_registry')
    assert not hasattr(config, 'plan_rows')
    assert not hasattr(config, 'root_spell_id')
    assert not hasattr(config, 'spell_lookup')
    assert not hasattr(config, 'empty_shape_key')
    assert not hasattr(config, 'baseline_executor')


def test_creation_context_init_requires_creation_gate_in_dynamic_mode() -> None:
    """
    Verify dynamic CreationContext requires a CreationGate.
    """
    with pytest.raises(ValueError, match="creation_gate cannot be None"):
        CreationContext(
            spell=_make_spell(),
            dynamic_environment=True,
            creation_gate=None,
            creation_gate_index_id="index-1",
            resolve_route_key=CreationContext.ROUTE_MANY,
        )


def test_creation_context_init_selects_mutation_route_and_seeds_baseline_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify __init__ selects the mutation override route and seeds baseline executors.
    """
    hook_overrides = lambda *args, **kwargs: ("hooks-overrides", True)
    hook_no_overrides = lambda *args, **kwargs: ("hooks-no-overrides", True)
    no_hooks_overrides = lambda *args, **kwargs: "no-hooks-overrides"
    no_hooks_no_overrides = lambda *args, **kwargs: "no-hooks-no-overrides"

    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_hooks_overrides_only_executor",
        lambda **kwargs: hook_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_hooks_no_overrides_executor",
        lambda **kwargs: hook_no_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_instance_overrides_only_executor",
        lambda **kwargs: no_hooks_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_instance_no_overrides_executor",
        lambda **kwargs: no_hooks_no_overrides,
    )

    baseline_no_mutation = lambda *args, **kwargs: "baseline-no-mutation"
    baseline_mutation = lambda *args, **kwargs: "baseline-mutation"
    route_config_no_mutation = _make_route_config(
        plan_signature=("phase11", "no-mutation", "rows"),
        baseline_executor=baseline_no_mutation,
    )
    route_config_mutation = _make_route_config(
        plan_signature=("phase11", "mutation", "rows"),
        baseline_executor=baseline_mutation,
    )
    patch_map = SimpleNamespace(
        _apply_with_socket_shape_prechecked=lambda **kwargs: ({}, ()),
    )

    context = CreationContext(
        spell=_make_spell(),
        dynamic_environment=False,
        creation_gate=None,
        creation_gate_index_id=None,
        resolve_route_key=CreationContext.ROUTE_MANY,
        fast_transient_no_overrides_enabled=True,
        no_overrides_executor=lambda *args, **kwargs: "direct-no-overrides",
        override_targeting=patch_map,
        override_route_config_no_mutation=route_config_no_mutation,
        override_route_config_mutation=route_config_mutation,
    )

    assert context._override_route_config_active is route_config_mutation
    assert context._override_empty_shape_key == (
        route_config_mutation.plan_signature,
        (),
        -1,
    )
    assert context._override_specialization_cache[
        (route_config_no_mutation.plan_signature, (), -1)
    ] is baseline_no_mutation
    assert context._override_specialization_cache[
        (route_config_mutation.plan_signature, (), -1)
    ] is baseline_mutation
    assert context._execute_hooks_no_overrides_compiled is hook_overrides
    assert context._execute_no_hooks_no_overrides_compiled is no_hooks_overrides


def test_creation_context_init_non_mutation_route_uses_no_override_compilers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify __init__ uses the explicit no-override compiler lanes when mutation routing is absent.
    """
    hook_overrides = lambda *args, **kwargs: ("hooks-overrides", True)
    hook_no_overrides = lambda *args, **kwargs: ("hooks-no-overrides", False)
    no_hooks_overrides = lambda *args, **kwargs: "no-hooks-overrides"
    no_hooks_no_overrides = lambda *args, **kwargs: "no-hooks-no-overrides"

    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_hooks_overrides_only_executor",
        lambda **kwargs: hook_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_hooks_no_overrides_executor",
        lambda **kwargs: hook_no_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_instance_overrides_only_executor",
        lambda **kwargs: no_hooks_overrides,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_creation_context_instance_no_overrides_executor",
        lambda **kwargs: no_hooks_no_overrides,
    )

    route_config_no_mutation = _make_route_config(
        plan_signature=("phase11", "no-mutation", "rows"),
    )

    context = CreationContext(
        spell=_make_spell(),
        dynamic_environment=False,
        creation_gate=None,
        creation_gate_index_id=None,
        resolve_route_key=CreationContext.ROUTE_MANY,
        fast_transient_no_overrides_enabled=True,
        no_overrides_executor=lambda *args, **kwargs: "direct-no-overrides",
        override_targeting=None,
        override_route_config_no_mutation=route_config_no_mutation,
        override_route_config_mutation=None,
    )

    assert context._override_route_config_active is route_config_no_mutation
    assert context._execute_hooks_overrides_compiled is hook_overrides
    assert context._execute_hooks_no_overrides_compiled is hook_no_overrides
    assert context._execute_no_hooks_overrides_compiled is no_hooks_overrides
    assert context._execute_no_hooks_no_overrides_compiled is no_hooks_no_overrides
    assert context._override_apply_with_socket_shape_prechecked_phase10 is None


def test_execute_routes_automatic_mode_to_compiled_lanes() -> None:
    """
    Verify automatic-mode execute selects the correct compiled door.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    context._execute_hooks_no_overrides_compiled = lambda caller_creations: ("auto-no-overrides", False)
    context._execute_hooks_overrides_compiled = lambda caller_creations, overrides: ("auto-overrides", True)

    assert context.execute(caller_creations="caller", overrides=None) == ("auto-no-overrides", False)
    assert context.execute(caller_creations="caller", overrides={"x": 1}) == ("auto-overrides", True)


def test_execute_dynamic_mode_waits_registers_and_unregisters_gate() -> None:
    """
    Verify dynamic execute waits on disabled gates and balances ticket registration.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    gate = _Gate(enabled=False, closed=False)
    context._dynamic_environment = True
    context._creation_gate = gate
    context._creation_gate_index_id = "index-1"
    context._execute_hooks_no_overrides_compiled = lambda caller_creations: ("dynamic-no-overrides", False)

    result = context.execute(caller_creations="caller", overrides=None)

    assert result == ("dynamic-no-overrides", False)
    assert gate.wait_calls == 1
    assert gate.register_calls == 1
    assert gate.unregister_calls == 1


def test_execute_dynamic_mode_raises_when_gate_is_closed() -> None:
    """
    Verify dynamic execute fails fast when the CreationGate is closed.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    gate = _Gate(enabled=True, closed=True)
    context._dynamic_environment = True
    context._creation_gate = gate
    context._creation_gate_index_id = "index-closed"

    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        context.execute(caller_creations="caller", overrides=None)

    assert gate.register_calls == 0
    assert gate.unregister_calls == 0


def test_execute_no_hooks_dynamic_mode_routes_overrides_and_balances_gate() -> None:
    """
    Verify dynamic no-hooks execution uses the no-hooks override lane and balances tickets.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    gate = _Gate(enabled=True, closed=False)
    context._dynamic_environment = True
    context._creation_gate = gate
    context._creation_gate_index_id = "index-no-hooks"
    context._execute_no_hooks_overrides_compiled = lambda caller_creations, overrides: "dynamic-no-hooks-overrides"

    result = context.execute_no_hooks(caller_creations="caller", overrides={"x": 1})

    assert result == "dynamic-no-hooks-overrides"
    assert gate.register_calls == 1
    assert gate.unregister_calls == 1


def test_execute_no_hooks_routes_automatic_mode_to_compiled_lanes() -> None:
    """
    Verify automatic-mode no-hooks execution selects the correct compiled door.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    context._execute_no_hooks_no_overrides_compiled = lambda caller_creations: "auto-no-hooks-no-overrides"
    context._execute_no_hooks_overrides_compiled = lambda caller_creations, overrides: "auto-no-hooks-overrides"

    assert context.execute_no_hooks(caller_creations="caller", overrides=None) == "auto-no-hooks-no-overrides"
    assert context.execute_no_hooks(caller_creations="caller", overrides={"x": 1}) == "auto-no-hooks-overrides"


def test_execute_no_hooks_dynamic_mode_waits_registers_and_returns_no_overrides() -> None:
    """
    Verify dynamic no-hooks execution waits on disabled gates and balances tickets.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    gate = _Gate(enabled=False, closed=False)
    context._dynamic_environment = True
    context._creation_gate = gate
    context._creation_gate_index_id = "index-no-hooks-wait"
    context._execute_no_hooks_no_overrides_compiled = lambda caller_creations: "dynamic-no-hooks-no-overrides"

    result = context.execute_no_hooks(caller_creations="caller", overrides=None)

    assert result == "dynamic-no-hooks-no-overrides"
    assert gate.wait_calls == 1
    assert gate.register_calls == 1
    assert gate.unregister_calls == 1


def test_execute_no_hooks_dynamic_mode_raises_when_gate_closes_after_wait() -> None:
    """
    Verify dynamic no-hooks execution fails when the gate closes after waiting.
    """

    class _ClosingGate(_Gate):
        def wait(self) -> None:
            super().wait()
            self._closed = True

    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    gate = _ClosingGate(enabled=False, closed=False)
    context._dynamic_environment = True
    context._creation_gate = gate
    context._creation_gate_index_id = "index-no-hooks-close"

    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        context.execute_no_hooks(caller_creations="caller", overrides=None)

    assert gate.wait_calls == 1
    assert gate.register_calls == 0
    assert gate.unregister_calls == 0


def test_cleanup_swallows_route_config_cleanup_failures_and_nulls_runtime_refs() -> None:
    """
    Verify cleanup tolerates route-config cleanup failures while still nulling runtime state.
    """

    class _FailingRouteConfig:
        def __init__(self) -> None:
            self.calls = 0

        def cleanup(self) -> None:
            self.calls += 1
            raise RuntimeError("boom")

    route_config_active = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config_active,
        route_config_no_mutation=None,
        route_config_mutation=None,
        patch_map=object(),
    )
    failing_no_mutation = _FailingRouteConfig()
    failing_mutation = _FailingRouteConfig()
    context._override_route_config_no_mutation = failing_no_mutation
    context._override_route_config_mutation = failing_mutation

    context.cleanup()

    assert failing_no_mutation.calls == 1
    assert failing_mutation.calls == 1
    assert not hasattr(context, "_spell")
    assert not hasattr(context, "_spell_id")
    assert not hasattr(context, "_override_specialization_cache")
    assert not hasattr(context, "_override_last_executor")


def test_seed_baseline_override_executor_noops_without_shape_or_executor() -> None:
    """
    Verify baseline seeding is a no-op when route config lacks required payload.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    context._override_specialization_cache.clear()

    route_config.empty_shape_key = None
    context._seed_baseline_override_executor(route_config)
    assert context._override_specialization_cache == {}

    route_config.empty_shape_key = (route_config.plan_signature, (), -1)
    route_config.baseline_executor = None
    context._seed_baseline_override_executor(route_config)
    assert context._override_specialization_cache == {}


def test_split_override_payload_strips_root_args_without_mutating_input() -> None:
    """
    Verify root-args split strips __args__ while preserving input payload.
    """
    spell = _make_spell()
    payload = {"__args__": [1, 2], "dep": "value"}
    stripped_payload, root_args = CreationContext._split_override_payload(
        spell=spell,
        override_payload=payload,
    )
    assert stripped_payload == {"dep": "value"}
    assert root_args == (1, 2)
    assert payload == {"__args__": [1, 2], "dep": "value"}


def test_split_override_payload_root_args_only_returns_empty_target_payload() -> None:
    """
    Verify __args__-only payloads split to empty target overrides.
    """
    spell = _make_spell()
    stripped_payload, root_args = CreationContext._split_override_payload(
        spell=spell,
        override_payload={"__args__": (7, 8)},
    )
    assert stripped_payload == {}
    assert root_args == (7, 8)


def test_split_override_payload_preserves_multiple_named_entries() -> None:
    """
    Verify root-args split preserves all non-__args__ entries when multiple named overrides exist.
    """
    spell = _make_spell()
    stripped_payload, root_args = CreationContext._split_override_payload(
        spell=spell,
        override_payload={"__args__": [1], "dep": "value", "other": "second"},
    )
    assert stripped_payload == {"dep": "value", "other": "second"}
    assert root_args == (1,)


def test_split_override_payload_rejects_non_sequence_root_args() -> None:
    """
    Verify split rejects invalid __args__ payload types.
    """
    spell = _make_spell()
    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        CreationContext._split_override_payload(
            spell=spell,
            override_payload={"__args__": "not-a-sequence"},
        )


def test_collect_override_targets_and_socket_shape_is_deterministic() -> None:
    """
    Verify override target grouping and socket-shape output are deterministic.
    """
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")
    socket_c = _SocketRef("s2", "z", 3, "optional")

    map_a = {socket_a: "va", socket_b: "vb", socket_c: "vc"}
    map_b = {socket_c: "vc", socket_b: "vb", socket_a: "va"}

    targets_a, shape_a = CreationContext._collect_override_targets_and_socket_shape(
        override_map=map_a,
    )
    targets_b, shape_b = CreationContext._collect_override_targets_and_socket_shape(
        override_map=map_b,
    )

    assert targets_a == targets_b
    assert shape_a == shape_b
    assert targets_a["s1"] == (socket_b, socket_a)
    assert targets_a["s2"] == (socket_c,)


def test_collect_override_socket_shape_matches_grouped_shape_output() -> None:
    """
    Verify shape-only helper matches grouped helper socket-shape output.
    """
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")
    socket_c = _SocketRef("s2", "z", 3, "optional")
    override_map = {socket_c: "vc", socket_b: "vb", socket_a: "va"}

    _, grouped_shape = CreationContext._collect_override_targets_and_socket_shape(
        override_map=override_map,
    )
    shape_only = CreationContext._collect_override_socket_shape(
        override_map=override_map,
    )

    assert shape_only == grouped_shape


def test_collect_override_socket_shape_two_socket_fast_path_sorts_rows() -> None:
    """
    Verify shape-only helper sorts two-socket fast-path rows deterministically.
    """
    socket_a = _SocketRef("s2", "z", 9, "normal")
    socket_b = _SocketRef("s1", "a", 1, "normal")

    shape_only = CreationContext._collect_override_socket_shape(
        override_map={socket_a: "va", socket_b: "vb"},
    )

    assert shape_only == (
        ("s1", 1, "a", "normal"),
        ("s2", 9, "z", "normal"),
    )


def test_collect_override_targets_from_socket_shape_matches_grouped_output() -> None:
    """
    Verify grouped-target reconstruction from socket-shape matches legacy helper.
    """
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")
    socket_c = _SocketRef("s2", "z", 3, "optional")
    override_map = {socket_c: "vc", socket_b: "vb", socket_a: "va"}

    grouped_targets, grouped_shape = (
        CreationContext._collect_override_targets_and_socket_shape(
            override_map=override_map,
        )
    )
    reconstructed_targets = CreationContext._collect_override_targets_from_socket_shape(
        override_map=override_map,
        socket_shape=grouped_shape,
    )

    assert reconstructed_targets == grouped_targets


def test_collect_override_targets_and_socket_shape_empty_map_returns_empty_outputs() -> None:
    """
    Verify grouped-target helper returns empty outputs for an empty override map.
    """
    grouped_targets, socket_shape = (
        CreationContext._collect_override_targets_and_socket_shape(
            override_map={},
        )
    )
    assert grouped_targets == {}
    assert socket_shape == ()


def test_collect_override_targets_and_socket_shape_single_socket_fast_path() -> None:
    """
    Verify grouped-target helper uses the single-socket fast path.
    """
    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    grouped_targets, socket_shape = (
        CreationContext._collect_override_targets_and_socket_shape(
            override_map={socket_ref: "value"},
        )
    )
    assert grouped_targets == {"s1": (socket_ref,)}
    assert socket_shape == (("s1", 7, "dep", "normal"),)


def test_collect_override_targets_and_socket_shape_two_socket_fast_path_same_spell() -> None:
    """
    Verify grouped-target helper keeps two same-spell sockets in one grouped tuple.
    """
    socket_a = _SocketRef("s1", "b", 9, "normal")
    socket_b = _SocketRef("s1", "a", 1, "normal")

    grouped_targets, socket_shape = (
        CreationContext._collect_override_targets_and_socket_shape(
            override_map={socket_a: "va", socket_b: "vb"},
        )
    )

    assert grouped_targets == {"s1": (socket_b, socket_a)}
    assert socket_shape == (
        ("s1", 1, "a", "normal"),
        ("s1", 9, "b", "normal"),
    )


def test_collect_override_targets_and_socket_shape_two_socket_fast_path_different_spells() -> None:
    """
    Verify grouped-target helper keeps two different-spell sockets in separate buckets.
    """
    socket_a = _SocketRef("s2", "b", 9, "normal")
    socket_b = _SocketRef("s1", "a", 1, "normal")

    grouped_targets, socket_shape = (
        CreationContext._collect_override_targets_and_socket_shape(
            override_map={socket_a: "va", socket_b: "vb"},
        )
    )

    assert grouped_targets == {"s1": (socket_b,), "s2": (socket_a,)}
    assert socket_shape == (
        ("s1", 1, "a", "normal"),
        ("s2", 9, "b", "normal"),
    )


def test_collect_override_targets_from_socket_shape_empty_shape_returns_empty() -> None:
    """
    Verify grouped-target reconstruction returns empty mapping for an empty shape.
    """
    assert (
        CreationContext._collect_override_targets_from_socket_shape(
            override_map={},
            socket_shape=(),
        )
        == {}
    )


def test_build_override_shape_key_uses_precomputed_socket_shape_and_arity() -> None:
    """
    Verify shape key includes plan signature, socket shape, and arg arity.
    """
    shape_key = CreationContext._build_override_shape_key(
        plan_signature=("plan", "sig"),
        socket_shape=(("s1", 7, "dep", "normal"),),
        root_positional_override=(1, 2, 3),
    )
    assert shape_key == (
        ("plan", "sig"),
        (("s1", 7, "dep", "normal"),),
        3,
    )


def test_get_or_compile_override_executor_caches_compiled_executor(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify override specialization compile runs once per shape key.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    compile_count = {"value": 0}
    source_emit_count = {"value": 0}
    code_compile_count = {"value": 0}

    def _emit_phase13_overrides_executor_shape_source(
            *,
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            override_targeted_spell_ids: Tuple[str, ...],
            override_target_counts_by_spell_id: Tuple[Tuple[str, int], ...],
            override_target_counts_by_step: Tuple[int, ...],
            has_root_positional_override: bool,
    ) -> str:
        source_emit_count["value"] += 1
        return f"source:{len(plan_rows)}:{root_spell_id}"

    def _compile_phase13_overrides_executor_code_object(*, source: str) -> Any:
        code_compile_count["value"] += 1
        return f"code:{source}"

    def _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub(**kwargs: Any) -> Any:
        compile_count["value"] += 1
        return lambda *args, **inner_kwargs: "compiled"

    monkeypatch.setattr(
        creation_context_module,
        "emit_phase13_overrides_executor_shape_source",
        _emit_phase13_overrides_executor_shape_source,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_phase13_overrides_executor_code_object",
        _compile_phase13_overrides_executor_code_object,
    )
    monkeypatch.setattr(
        creation_context_module,
        "_compile_phase13_overrides_executor_from_code_object_with_prefilter_cache",
        _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub,
    )

    shape_key = (route_config.plan_signature, (), -1)
    first = context._get_or_compile_override_executor(
        shape_key=shape_key,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )
    second = context._get_or_compile_override_executor(
        shape_key=shape_key,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )

    assert first is second
    assert compile_count["value"] == 1
    assert source_emit_count["value"] == 1
    assert code_compile_count["value"] == 1


def test_get_or_compile_override_executor_reuses_plan_signature_artifacts_across_misses(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify miss-path specializations emit artifacts per shape-key miss.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    source_emit_count = {"value": 0}
    code_compile_count = {"value": 0}
    specialization_compile_count = {"value": 0}

    def _emit_phase13_overrides_executor_shape_source(
            *,
            plan_rows: Sequence[Dict[str, Any]],
            root_spell_id: Optional[str],
            spell_lookup: Optional[Dict[str, Any]],
            override_targeted_spell_ids: Tuple[str, ...],
            override_target_counts_by_spell_id: Tuple[Tuple[str, int], ...],
            override_target_counts_by_step: Tuple[int, ...],
            has_root_positional_override: bool,
    ) -> str:
        source_emit_count["value"] += 1
        return f"source:{len(plan_rows)}:{root_spell_id}"

    def _compile_phase13_overrides_executor_code_object(*, source: str) -> Any:
        code_compile_count["value"] += 1
        return f"code:{source}"

    def _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub(**kwargs: Any) -> Any:
        specialization_compile_count["value"] += 1
        return lambda *args, **inner_kwargs: "compiled"

    monkeypatch.setattr(
        creation_context_module,
        "emit_phase13_overrides_executor_shape_source",
        _emit_phase13_overrides_executor_shape_source,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_phase13_overrides_executor_code_object",
        _compile_phase13_overrides_executor_code_object,
    )
    monkeypatch.setattr(
        creation_context_module,
        "_compile_phase13_overrides_executor_from_code_object_with_prefilter_cache",
        _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub,
    )

    shape_key_a = (route_config.plan_signature, (("s1", 7, "a", "normal"),), -1)
    shape_key_b = (route_config.plan_signature, (("s1", 9, "b", "normal"),), -1)
    first = context._get_or_compile_override_executor(
        shape_key=shape_key_a,
        override_targets_by_spell_id={},
        any_overrides_present=True,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )
    second = context._get_or_compile_override_executor(
        shape_key=shape_key_b,
        override_targets_by_spell_id={},
        any_overrides_present=True,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )

    assert callable(first)
    assert callable(second)
    assert source_emit_count["value"] == 2
    assert code_compile_count["value"] == 2
    assert specialization_compile_count["value"] == 2


def test_get_or_compile_override_executor_passes_prefilter_cache_contract(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify schema-row compile path passes CreationContext prefilter caches/keys.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    compile_calls: list[dict[str, Any]] = []

    def _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub(**kwargs: Any) -> Any:
        compile_calls.append(kwargs)
        return lambda *args, **inner_kwargs: "compiled"

    monkeypatch.setattr(
        creation_context_module,
        "_compile_phase13_overrides_executor_from_code_object_with_prefilter_cache",
        _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub,
    )

    prefilter_cache_key = (route_config.plan_signature, (("s1", 7, "dep", "normal"),))
    shape_key_a = (route_config.plan_signature, (("s1", 7, "dep", "normal"),), -1)
    shape_key_b = (route_config.plan_signature, (("s1", 7, "dep", "normal"),), 2)
    context._get_or_compile_override_executor(
        shape_key=shape_key_a,
        override_targets_by_spell_id={},
        any_overrides_present=True,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
        prefilter_cache_key=prefilter_cache_key,
    )
    context._get_or_compile_override_executor(
        shape_key=shape_key_b,
        override_targets_by_spell_id={},
        any_overrides_present=True,
        path_registry=route_config.path_registry,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
        prefilter_cache_key=prefilter_cache_key,
    )

    assert len(compile_calls) == 2
    first_call = compile_calls[0]
    second_call = compile_calls[1]
    assert first_call["prefilter_step_targets_cache"] is context._override_prefilter_step_targets_cache
    assert first_call["prefilter_path_metadata_cache"] is context._override_prefilter_path_metadata_cache
    assert first_call["prefilter_cache_key"] == prefilter_cache_key
    assert second_call["prefilter_cache_key"] == prefilter_cache_key


def test_get_or_compile_override_executor_without_plan_rows_uses_full_compiler(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify fallback compile path uses full compiler when schema rows are absent.
    """
    route_config = _make_route_config(
        plan_signature=("phase11", "sig", "rows"),
        plan_rows=(),
    )
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    compile_count = {"value": 0}

    def _compile_phase13_overrides_executor(**kwargs: Any) -> Any:
        compile_count["value"] += 1
        return lambda *args, **inner_kwargs: "compiled"

    monkeypatch.setattr(
        creation_context_module,
        "compile_phase13_overrides_executor",
        _compile_phase13_overrides_executor,
    )
    monkeypatch.setattr(
        creation_context_module,
        "_compile_phase13_overrides_executor_from_code_object_with_prefilter_cache",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("code-object path must not run when plan_rows are absent")
        ),
    )

    shape_key = (route_config.plan_signature, (), -1)
    first = context._get_or_compile_override_executor(
        shape_key=shape_key,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=route_config.path_registry,
        plan_rows=None,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )
    second = context._get_or_compile_override_executor(
        shape_key=shape_key,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=route_config.path_registry,
        plan_rows=None,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
    )

    assert first is second
    assert compile_count["value"] == 1


def test_get_or_build_override_executor_source_caches_emitted_source() -> None:
    """
    Verify emitted override source is cached per source-cache key.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    source_cache_key = (route_config.plan_signature, (), -1)

    first = context._get_or_build_override_executor_source(
        source_cache_key=source_cache_key,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
        override_targeted_spell_ids=(),
        override_target_counts_by_spell_id=(),
        override_target_counts_by_step=(),
        has_root_positional_override=False,
    )
    second = context._get_or_build_override_executor_source(
        source_cache_key=source_cache_key,
        plan_rows=route_config.plan_rows,
        root_spell_id=route_config.root_spell_id,
        spell_lookup=route_config.spell_lookup,
        override_targeted_spell_ids=(),
        override_target_counts_by_spell_id=(),
        override_target_counts_by_step=(),
        has_root_positional_override=False,
    )

    assert second is first


def test_get_or_build_override_executor_code_object_caches_compiled_code_object() -> None:
    """
    Verify compiled override code objects are cached per source-cache key.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    source_cache_key = (route_config.plan_signature, (), -1)

    first = context._get_or_build_override_executor_code_object(
        source_cache_key=source_cache_key,
        source="def compiled_executor():\n    return 'ok'\n",
    )
    second = context._get_or_build_override_executor_code_object(
        source_cache_key=source_cache_key,
        source="this source should not be recompiled",
    )

    assert second is first


def test_execute_with_overrides_uses_baseline_executor_for_none_payload() -> None:
    """
    Verify override lane uses route baseline executor when payload is None.
    """
    calls: list[tuple[Any, Dict[Any, Any], Optional[Sequence[Any]], Any, bool]] = []

    def _baseline_executor(
            caller_creations: Any,
            override_map: Dict[Any, Any],
            root_args: Optional[Sequence[Any]],
            *,
            owner_creations: Any,
            caller_creations_lock_held: bool,
    ) -> str:
        calls.append(
            (
                caller_creations,
                override_map,
                root_args,
                owner_creations,
                caller_creations_lock_held,
            )
        )
        return "baseline"

    route_config = _make_route_config(
        plan_signature=("phase11", "baseline", "rows"),
        baseline_executor=_baseline_executor,
    )
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    caller_creations = object()
    result = context._execute_with_overrides(
        caller_creations=caller_creations,
        overrides=None,
        caller_creations_lock_held=True,
    )

    assert result == "baseline"
    assert len(calls) == 1
    assert calls[0][0] is caller_creations
    assert calls[0][1] == {}
    assert calls[0][2] is None
    assert calls[0][4] is True


def test_execute_with_overrides_without_baseline_executor_uses_empty_shape_compile_path(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify override execution falls back to the empty-shape compile path when no baseline exists.
    """
    route_config = _make_route_config(
        plan_signature=("phase11", "no-baseline", "rows"),
        baseline_executor=None,
    )
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )
    calls: list[dict[str, Any]] = []

    def _compiled_executor(
            caller_creations: Any,
            override_map: Dict[Any, Any],
            root_args: Optional[Sequence[Any]],
            *,
            owner_creations: Any,
            caller_creations_lock_held: bool,
    ) -> str:
        calls.append(
            {
                "caller_creations": caller_creations,
                "override_map": override_map,
                "root_args": root_args,
                "owner_creations": owner_creations,
                "caller_creations_lock_held": caller_creations_lock_held,
            }
        )
        return "compiled-empty-shape"

    monkeypatch.setattr(
        CreationContext,
        "_get_or_compile_override_executor",
        lambda self, **kwargs: _compiled_executor,
    )

    result = context._execute_with_overrides(
        caller_creations="caller",
        overrides=None,
        caller_creations_lock_held=False,
    )

    assert result == "compiled-empty-shape"
    assert calls == [
        {
            "caller_creations": "caller",
            "override_map": {},
            "root_args": None,
            "owner_creations": context._owner_creations,
            "caller_creations_lock_held": False,
        }
    ]


def test_execute_with_overrides_applies_payload_and_reuses_shape_cache(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify override lane applies phase10 payload and caches phase13 specialization.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    class _PatchMap:
        def apply_with_socket_shape(
                self,
                override_payload: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            apply_calls.append(dict(override_payload))
            return (
                override_map,
                CreationContext._collect_override_socket_shape(
                    override_map=override_map,
                ),
            )

        def _apply_with_socket_shape_prechecked(
                self,
                *,
                spell_override: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            return self.apply_with_socket_shape(spell_override)

    patch_map = _PatchMap()
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=patch_map,
    )
    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    override_map = {socket_ref: "value"}
    apply_calls: list[Dict[str, Any]] = []
    compile_count = {"value": 0}

    def _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub(**kwargs: Any) -> Any:
        compile_count["value"] += 1

        def _executor(
                caller_creations: Any,
                received_override_map: Dict[Any, Any],
                root_args: Optional[Sequence[Any]],
                *,
                owner_creations: Any,
                caller_creations_lock_held: bool,
        ) -> str:
            assert received_override_map is override_map
            assert root_args == (1, 2)
            return "ok"

        return _executor

    def _unexpected_collect(**kwargs: Any) -> Any:
        raise AssertionError(
            "legacy grouped collector must not run in _execute_with_overrides",
        )

    monkeypatch.setattr(
        CreationContext,
        "_collect_override_targets_and_socket_shape",
        staticmethod(_unexpected_collect),
    )
    monkeypatch.setattr(
        creation_context_module,
        "_compile_phase13_overrides_executor_from_code_object_with_prefilter_cache",
        _compile_phase13_overrides_executor_from_code_object_with_prefilter_cache_stub,
    )

    caller_creations = object()
    payload = {"__args__": [1, 2], "dep": "payload"}
    assert context._execute_with_overrides(caller_creations, payload, False) == "ok"
    assert context._execute_with_overrides(caller_creations, payload, False) == "ok"
    assert apply_calls == [
        {"dep": "payload"},
        {"dep": "payload"},
    ]
    assert compile_count["value"] == 1


def test_execute_with_overrides_cache_hit_skips_grouping_and_compile(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify cache-hit override execution bypasses grouping and specialization compile.
    """
    class _PatchMap:
        def apply_with_socket_shape(
                self,
                override_payload: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            return (
                override_map,
                CreationContext._collect_override_socket_shape(
                    override_map=override_map,
                ),
            )

        def _apply_with_socket_shape_prechecked(
                self,
                *,
                spell_override: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            return self.apply_with_socket_shape(spell_override)

    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=_PatchMap(),
    )
    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    override_map = {socket_ref: "value"}

    shape_key = CreationContext._build_override_shape_key(
        plan_signature=route_config.plan_signature,
        socket_shape=CreationContext._collect_override_socket_shape(
            override_map=override_map,
        ),
        root_positional_override=None,
    )

    def _cached_executor(
            caller_creations: Any,
            received_override_map: Dict[Any, Any],
            root_args: Optional[Sequence[Any]],
            *,
            owner_creations: Any,
            caller_creations_lock_held: bool,
    ) -> str:
        assert received_override_map is override_map
        assert root_args is None
        return "cached"

    context._override_specialization_cache[shape_key] = _cached_executor

    def _unexpected_collect(**kwargs: Any) -> Any:
        raise AssertionError("target grouping must not run on cache hit")

    def _unexpected_compile(**kwargs: Any) -> Any:
        raise AssertionError("phase13 compile must not run on cache hit")

    monkeypatch.setattr(
        CreationContext,
        "_collect_override_targets_from_socket_shape",
        staticmethod(_unexpected_collect),
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_phase13_overrides_executor",
        _unexpected_compile,
    )

    result = context._execute_with_overrides(
        caller_creations=object(),
        overrides={"dep": "payload"},
        caller_creations_lock_held=False,
    )
    assert result == "cached"


def test_collect_override_socket_shape_cached_handles_empty_and_cache_hit() -> None:
    """
    Verify cached socket-shape collection handles empty maps and reuses cached rows.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    assert context._collect_override_socket_shape_cached(override_map={}) == ()

    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    override_map = {socket_ref: "value"}
    first = context._collect_override_socket_shape_cached(override_map=override_map)
    second = context._collect_override_socket_shape_cached(override_map=override_map)

    assert second is first


def test_collect_override_socket_shape_cached_two_and_many_paths_reuse_cache() -> None:
    """
    Verify cached socket-shape collection reuses cached rows for two-socket and many-socket paths.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    socket_a = _SocketRef("s2", "z", 9, "normal")
    socket_b = _SocketRef("s1", "a", 1, "normal")
    double_map = {socket_a: "va", socket_b: "vb"}
    first_double = context._collect_override_socket_shape_cached(override_map=double_map)
    second_double = context._collect_override_socket_shape_cached(override_map=double_map)
    assert second_double is first_double

    socket_c = _SocketRef("s3", "b", 3, "optional")
    many_map = {socket_a: "va", socket_b: "vb", socket_c: "vc"}
    first_many = context._collect_override_socket_shape_cached(override_map=many_map)
    second_many = context._collect_override_socket_shape_cached(override_map=many_map)
    assert second_many is first_many


def test_execute_with_overrides_wraps_phase10_apply_failures(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify phase10 override-apply failures are wrapped as MeldExecutionError.
    """
    class _PatchMap:
        def apply_with_socket_shape(
                self,
                override_payload: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            raise RuntimeError("apply-fail")

        def _apply_with_socket_shape_prechecked(
                self,
                *,
                spell_override: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            return self.apply_with_socket_shape(spell_override)

    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=_PatchMap(),
    )

    with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
        context._execute_with_overrides(
            caller_creations=object(),
            overrides={"dep": "payload"},
            caller_creations_lock_held=False,
        )


def test_execute_with_overrides_missing_patch_map_raises_meld_execution_error() -> None:
    """
    Verify override execution raises MeldExecutionError when no phase10 patch map is available.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=None,
    )

    with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
        context._execute_with_overrides(
            caller_creations=object(),
            overrides={"dep": "payload"},
            caller_creations_lock_held=False,
        )


def test_execute_with_overrides_reraises_meld_execution_error_from_phase10() -> None:
    """
    Verify override execution preserves MeldExecutionError raised by phase10 apply.
    """

    class _PatchMap:
        def _apply_with_socket_shape_prechecked(
                self,
                *,
                spell_override: Dict[str, Any],
        ) -> Tuple[Dict[Any, Any], Tuple[Tuple[Any, ...], ...]]:
            raise MeldExecutionError(
                spell_id="s1",
                spell_name="s1",
                message="already-wrapped",
            )

    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=_PatchMap(),
    )

    with pytest.raises(MeldExecutionError, match="already-wrapped"):
        context._execute_with_overrides(
            caller_creations=object(),
            overrides={"dep": "payload"},
            caller_creations_lock_held=False,
        )


def test_cleanup_clears_runtime_cache_and_route_refs() -> None:
    """
    Verify cleanup clears override cache and cleans route-config children.
    """
    route_config_no_mutation = _make_route_config(plan_signature=("phase11", "a", "rows"))
    route_config_mutation = _make_route_config(plan_signature=("phase11", "b", "rows"))
    context = _make_override_harness(
        route_config_active=route_config_no_mutation,
        route_config_no_mutation=route_config_no_mutation,
        route_config_mutation=route_config_mutation,
        patch_map=object(),
    )
    context._override_specialization_cache[("k",)] = lambda *args, **kwargs: None

    context.cleanup()
    context.cleanup()

    assert context.cleaned is True
    assert not hasattr(context, '_override_specialization_cache')
    assert not hasattr(context, '_override_executor_source_cache_by_plan_signature')
    assert not hasattr(context, '_override_executor_code_object_cache_by_plan_signature')
    assert not hasattr(context, '_override_prefilter_step_targets_cache')
    assert not hasattr(context, '_override_prefilter_path_metadata_cache')
    assert not hasattr(context, '_override_apply_with_socket_shape_prechecked_phase10')
    assert not hasattr(route_config_no_mutation, 'plan_signature')
    assert not hasattr(route_config_mutation, 'plan_signature')

