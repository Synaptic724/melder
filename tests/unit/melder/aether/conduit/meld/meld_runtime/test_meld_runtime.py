"""CreationContext runtime contract tests for override and cache helpers."""
from types import SimpleNamespace
from typing import Any, Dict, Optional, Sequence, Tuple

import pytest

import melder.aether.conduit.meld.creation_context.creation_context as creation_context_module
from melder.aether.conduit.meld.creation_context.creation_context import (
    CreationContext,
    OverrideRouteConfig,
)
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
    )


def _make_route_config(
        *,
        plan_signature: Tuple[Any, ...],
        baseline_executor: Optional[Any] = None,
) -> OverrideRouteConfig:
    """
    Build an OverrideRouteConfig used by override-lane harness tests.
    """
    return OverrideRouteConfig(
        plan_signature=plan_signature,
        path_registry="registry",
        plan_rows=({"spell_id": "s1"},),
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
    context._creation_gate_lineage_id = None
    context._owner_creations = object()
    context._execute_hooks_overrides_compiled = None
    context._execute_hooks_no_overrides_compiled = None
    context._execute_no_hooks_overrides_compiled = None
    context._execute_no_hooks_no_overrides_compiled = None
    context._no_overrides_executor = None
    context._override_patch_map_phase10 = patch_map
    context._override_route_config_no_mutation = route_config_no_mutation
    context._override_route_config_mutation = route_config_mutation
    context._override_route_config_active = route_config_active
    context._override_empty_shape_key = (
        route_config_active.plan_signature,
        (),
        -1,
    )
    context._override_specialization_cache = {}
    return context


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

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        compile_count["value"] += 1
        return lambda *args, **inner_kwargs: "compiled"

    monkeypatch.setattr(
        creation_context_module,
        "compile_phase12_overrides_executor",
        _compile_phase12_overrides_executor,
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


def test_execute_with_overrides_applies_payload_and_reuses_shape_cache(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify override lane applies phase10 payload and caches phase12 specialization.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    patch_map = object()
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=patch_map,
    )
    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    override_map = {socket_ref: "value"}
    apply_calls: list[tuple[Any, Dict[str, Any]]] = []
    compile_count = {"value": 0}

    def _apply_phase10_override_payload(
            *,
            override_patch_map: Any,
            override_payload: Dict[str, Any],
    ) -> Dict[Any, Any]:
        apply_calls.append((override_patch_map, dict(override_payload)))
        return override_map

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
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

    monkeypatch.setattr(
        creation_context_module,
        "apply_phase10_override_payload",
        _apply_phase10_override_payload,
    )
    monkeypatch.setattr(
        creation_context_module,
        "compile_phase12_overrides_executor",
        _compile_phase12_overrides_executor,
    )

    caller_creations = object()
    payload = {"__args__": [1, 2], "dep": "payload"}
    assert context._execute_with_overrides(caller_creations, payload, False) == "ok"
    assert context._execute_with_overrides(caller_creations, payload, False) == "ok"
    assert apply_calls == [
        (patch_map, {"dep": "payload"}),
        (patch_map, {"dep": "payload"}),
    ]
    assert compile_count["value"] == 1


def test_execute_with_overrides_wraps_phase10_apply_failures(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify phase10 override-apply failures are wrapped as MeldExecutionError.
    """
    route_config = _make_route_config(plan_signature=("phase11", "sig", "rows"))
    context = _make_override_harness(
        route_config_active=route_config,
        route_config_no_mutation=route_config,
        patch_map=object(),
    )

    def _raise_apply(**kwargs: Any) -> Dict[Any, Any]:
        raise RuntimeError("apply-fail")

    monkeypatch.setattr(
        creation_context_module,
        "apply_phase10_override_payload",
        _raise_apply,
    )

    with pytest.raises(MeldExecutionError, match="Failed to apply overrides"):
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
    assert context._override_specialization_cache is None
    assert route_config_no_mutation.plan_signature is None
    assert route_config_mutation.plan_signature is None
