"""Codegen-only contract tests for MeldRuntime."""

from collections import deque
from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest

import melder.aether.conduit.meld.meld_runtime.meld_runtime as runtime_module
from melder.aether.conduit.meld.meld_runtime.meld_runtime import MeldRuntime
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


class _SystemState:
    """Expose validity for runtime gate checks."""

    def __init__(self, validity: SpellValidity) -> None:
        self.validity = validity


class _CCManager:
    """Expose deterministic dirty-root checks."""

    def __init__(self, *, dirty: bool, raise_on_call: bool = False) -> None:
        self._dirty = dirty
        self._raise_on_call = raise_on_call

    def is_root_dirty(self, conduit_id: str, root_id: str) -> bool:
        if self._raise_on_call:
            raise RuntimeError("cc-fail")
        return self._dirty


class _Aether:
    """Expose change-control manager lookup."""

    def __init__(self, manager: Any, *, raise_lookup: bool = False) -> None:
        self._manager = manager
        self._raise_lookup = raise_lookup

    def _get_change_control_manager(self, frame: str) -> Any:
        if self._raise_lookup:
            raise RuntimeError("lookup-fail")
        return self._manager


class _Spellbook:
    """Minimal spellbook fields used by runtime invariants."""

    def __init__(self, *, validation_required: bool = True, aether: Optional[Any] = None) -> None:
        self._spellbook_validation_required = validation_required
        self._aether = aether
        self._spell_id_pool: Dict[str, Any] = {}


class _SocketKind:
    """Socket kind value holder for override map keys."""

    def __init__(self, value: str) -> None:
        self.value = value


class _SocketRef:
    """Hashable socket-ref key for override payload maps."""

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


class _Spell:
    """Spell stub matching runtime-owned contract fields."""

    def __init__(
            self,
            *,
            spell_id: str,
            crafter: Optional[Any],
            spellbook: Optional[Any] = None,
            system_state: Optional[Any] = None,
            has_mutation_override: bool = False,
            is_broken: bool = False,
            validated: bool = True,
            is_class_spell: bool = True,
            is_method_spell: bool = False,
            is_lambda_spell: bool = False,
    ) -> None:
        self.spell_index = SpellIndex(spell_id)
        self.spell_id = spell_id
        self.spell_name = spell_id
        self.aetheric_frame = "default"
        self._crafter = crafter
        self.system_state = system_state
        self.has_mutation_override = has_mutation_override
        self.is_broken = is_broken
        self.validated = validated
        self.is_class_spell = is_class_spell
        self.is_method_spell = is_method_spell
        self.is_lambda_spell = is_lambda_spell
        self._spellbook = spellbook if spellbook is not None else _Spellbook()


def _ctx(spell: Any, overrides: Optional[Any] = None, conduit_id: Optional[str] = "cid") -> Any:
    """Build a minimal runtime context object."""
    return SimpleNamespace(
        root_spell=spell,
        overrides=overrides,
        conduit_id=conduit_id,
        caller_creations_lock_held=False,
        caller_creations=None,
    )


def _crafter(
        *,
        executor: Optional[Any] = None,
        patch_map: Optional[Any] = None,
        override_plan: Optional[Any] = None,
        root_blueprint: Optional[Any] = None,
        codegen_ir: Optional[Any] = None,
) -> Any:
    """Build a minimal SpellCrafter artifact container."""
    return SimpleNamespace(
        phase12_no_overrides_executor=executor,
        override_patch_map_phase10=patch_map,
        execution_plan_phase11_overrides=override_plan,
        root_blueprint_phase5=root_blueprint,
        codegen_ir=codegen_ir,
    )


def _override_plan(*, override_keys: Optional[list[str]] = None) -> Any:
    """
    Build a minimal override execution-plan stub for runtime routing tests.
    """
    keys = override_keys if override_keys is not None else ["dep"]
    step = SimpleNamespace(
        instance_key=("dep-spell", None),
        spell=SimpleNamespace(spell_index=SpellIndex("dep-spell")),
        existence=Existence.unique,
        creations_target_kind=1,
        shared_instance=False,
        dependency_resolution_order=[("dep", [("dep-spell", None)])],
        override_match_prefix=None,
        override_match_prefix_len=0,
        override_keys=keys,
        use_spell_lock_hint=False,
        must_register=False,
        uses_positional_override=False,
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
    )
    return SimpleNamespace(
        plan_variant="overrides",
        root_spell_id="root",
        steps=[step],
    )


def test_execute_rejects_none_context() -> None:
    """`execute` raises ValueError when context is None."""
    with pytest.raises(ValueError, match="context must not be None"):
        MeldRuntime().execute(None)


def test_execute_rejects_none_root_spell() -> None:
    """`execute` raises ValueError when root spell is missing."""
    with pytest.raises(ValueError, match="root_spell must not be None"):
        MeldRuntime().execute(_ctx(None))


@pytest.mark.parametrize("validity", [SpellValidity.invalid, SpellValidity.gated, SpellValidity.disabled])
def test_execute_blocks_invalid_validity(validity: SpellValidity) -> None:
    """Runtime blocks invalid/gated/disabled lineage validity states."""
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), system_state=_SystemState(validity))
    with pytest.raises(MeldExecutionError, match=validity.name):
        MeldRuntime().execute(_ctx(spell))


def test_execute_blocks_dirty_root() -> None:
    """Runtime blocks dirty-root execution via change-control manager."""
    spellbook = _Spellbook(aether=_Aether(_CCManager(dirty=True)))
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), spellbook=spellbook)
    with pytest.raises(MeldExecutionError, match="marked dirty"):
        MeldRuntime().execute(_ctx(spell))


def test_execute_ignores_change_control_lookup_errors() -> None:
    """Runtime continues when change-control lookup raises unexpectedly."""
    calls = []

    def _executor(context: Any) -> str:
        calls.append(context)
        return "ok"

    spellbook = _Spellbook(aether=_Aether(None, raise_lookup=True))
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=_executor), spellbook=spellbook)
    context = _ctx(spell)
    assert MeldRuntime().execute(context) == "ok"
    assert calls == [context]


def test_execute_blocks_broken_and_unvalidated() -> None:
    """Runtime blocks broken and unvalidated spells."""
    runtime = MeldRuntime()
    with pytest.raises(MeldExecutionError, match="broken spell"):
        runtime.execute(_ctx(_Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), is_broken=True)))
    with pytest.raises(MeldExecutionError, match="not been validated"):
        runtime.execute(_ctx(_Spell(spell_id="s2", crafter=_crafter(executor=lambda c: "ok"), validated=False)))


def test_execute_no_overrides_dispatches_executor_and_wraps_errors() -> None:
    """No-overrides path dispatches executor and wraps unexpected failures."""
    runtime = MeldRuntime()
    context_calls = []

    def _ok(context: Any) -> str:
        context_calls.append(context)
        return "built"

    spell = _Spell(spell_id="s1", crafter=_crafter(executor=_ok))
    context = _ctx(spell)
    assert runtime.execute(context) == "built"
    assert context_calls == [context]

    def _boom(context: Any) -> Any:
        raise RuntimeError("boom")

    spell_boom = _Spell(spell_id="s2", crafter=_crafter(executor=_boom))
    with pytest.raises(MeldExecutionError) as exc:
        runtime.execute(_ctx(spell_boom))
    assert isinstance(exc.value.inner, RuntimeError)


def test_execute_no_overrides_requires_crafter_and_executor() -> None:
    """No-overrides path requires crafter and compiled phase12 executor."""
    runtime = MeldRuntime()
    with pytest.raises(MeldExecutionError, match="Missing SpellCrafter"):
        runtime.execute(_ctx(_Spell(spell_id="s1", crafter=None)))
    with pytest.raises(MeldExecutionError, match="Missing Phase 12 no-overrides executor"):
        runtime.execute(_ctx(_Spell(spell_id="s2", crafter=_crafter(executor=None))))


def test_execute_rejects_mutation_override() -> None:
    """Mutation overrides are hard-failed on codegen runtime path."""
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(executor=lambda c: "ok"),
        has_mutation_override=True,
    )
    with pytest.raises(MeldExecutionError, match="Mutation overrides are not supported"):
        runtime.execute(_ctx(spell))


def test_execute_none_result_rules() -> None:
    """Factory spells reject None; non-factory spells allow None."""
    runtime = MeldRuntime()
    with pytest.raises(MeldExecutionError, match="returned None"):
        runtime.execute(_ctx(_Spell(spell_id="s1", crafter=_crafter(executor=lambda c: None), is_class_spell=True)))
    non_factory = _Spell(
        spell_id="s2",
        crafter=_crafter(executor=lambda c: None),
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
    )
    assert runtime.execute(_ctx(non_factory)) is None


def test_execute_with_overrides_requires_patch_map_and_plan() -> None:
    """Override path requires phase10 patch-map and phase11 override plan artifacts."""
    runtime = MeldRuntime()
    no_patch = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "x", patch_map=None, override_plan=object()))
    with pytest.raises(MeldExecutionError, match="Phase 10 override patch map"):
        runtime.execute(_ctx(no_patch, overrides={"x": 1}))

    no_plan = _Spell(spell_id="s2", crafter=_crafter(executor=lambda c: "x", patch_map=object(), override_plan=None))
    with pytest.raises(MeldExecutionError, match="Phase 11 override execution plan"):
        runtime.execute(_ctx(no_plan, overrides={"x": 1}))


def test_resolve_override_plan_signature_prefers_codegen_ir_payload() -> None:
    """Override shape-key signature prefers codegen IR override signature when available."""
    plan = _override_plan()
    crafter = _crafter(
        executor=lambda c: "x",
        patch_map=object(),
        override_plan=plan,
    )
    crafter.codegen_ir = {
        "phase8_11": {
            "execution": {
                "overrides": {
                    "signature": "sig-overrides",
                    "steps_rows_signature": "sig-rows",
                },
            },
        },
    }

    signature = MeldRuntime._resolve_override_plan_signature(
        crafter=crafter,
        execution_plan=plan,
    )

    assert signature == ("phase11_overrides_ir", "sig-overrides", "sig-rows")


def test_resolve_override_plan_signature_falls_back_to_plan_signature() -> None:
    """Override shape-key signature falls back to execution-plan semantic signature."""
    plan = _override_plan()
    crafter = _crafter(
        executor=lambda c: "x",
        patch_map=object(),
        override_plan=plan,
    )
    crafter.codegen_ir = None

    signature = MeldRuntime._resolve_override_plan_signature(
        crafter=crafter,
        execution_plan=plan,
    )
    expected = MeldRuntime._build_override_plan_signature(
        execution_plan=plan,
    )

    assert signature == expected


def test_resolve_override_execution_ir_payload_returns_overrides_payload() -> None:
    """Override execution IR resolver returns the overrides payload when present."""
    crafter = _crafter(
        executor=lambda c: "x",
        patch_map=object(),
        override_plan=_override_plan(),
        codegen_ir={
            "phase8_11": {
                "execution": {
                    "overrides": {
                        "signature": "sig-overrides",
                        "steps_rows_signature": "sig-rows",
                    },
                },
            },
        },
    )

    payload = MeldRuntime._resolve_override_execution_ir_payload(
        crafter=crafter,
    )

    assert payload == {
        "signature": "sig-overrides",
        "steps_rows_signature": "sig-rows",
    }


def test_execute_with_overrides_applies_payload_and_uses_cached_specialization(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override path applies payload, compiles specialization once per shape, and reuses cache."""
    runtime = MeldRuntime()
    plan = _override_plan()
    patch_map = object()
    root_blueprint = SimpleNamespace(path_registry="registry")
    codegen_ir = {
        "phase8_11": {
            "execution": {
                "overrides": {
                    "signature": "sig-overrides",
                    "steps_rows_signature": "sig-rows",
                    "root_spell_id": "s1",
                    "steps_rows": ({"spell_id": "s1"},),
                },
            },
        },
    }
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=patch_map,
            override_plan=plan,
            root_blueprint=root_blueprint,
            codegen_ir=codegen_ir,
        ),
    )
    socket_ref = _SocketRef("s1", "dep", 7, "normal")
    override_map = {socket_ref: "value"}

    apply_calls = []
    compile_count = {"value": 0}

    def _apply_phase10_override_payload(*, override_patch_map: Any, override_payload: Dict[str, Any]) -> Dict[Any, Any]:
        apply_calls.append((override_patch_map, dict(override_payload)))
        return override_map

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        compile_count["value"] += 1
        assert kwargs["plan_rows"] == ({"spell_id": "s1"},)
        assert kwargs["root_spell_id"] == "s1"
        assert kwargs["spell_lookup"] is spell._spellbook._spell_id_pool

        def _executor(context: Any, received_override_map: Dict[Any, Any], root_args: Any) -> str:
            assert received_override_map is override_map
            assert root_args == (1, 2)
            return "ok"

        return _executor

    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", _apply_phase10_override_payload)
    monkeypatch.setattr(runtime_module, "compile_phase12_overrides_executor", _compile_phase12_overrides_executor)

    context = _ctx(spell, overrides={"__args__": [1, 2], "dep": "payload"})
    assert runtime.execute(context) == "ok"
    assert runtime.execute(context) == "ok"
    assert apply_calls == [(patch_map, {"dep": "payload"}), (patch_map, {"dep": "payload"})]
    assert compile_count["value"] == 1


def test_execute_with_overrides_wraps_patch_or_executor_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override path wraps patch-map and compiled-executor runtime errors."""
    runtime = MeldRuntime()
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "x", patch_map=object(), override_plan=_override_plan()))

    def _raise_apply(**kwargs: Any) -> Dict[Any, Any]:
        raise RuntimeError("patch-fail")

    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", _raise_apply)
    with pytest.raises(MeldExecutionError) as exc:
        runtime.execute(_ctx(spell, overrides={"x": 1}))
    assert isinstance(exc.value.inner, RuntimeError)

    socket_ref = _SocketRef("s1", "x", 1, "normal")
    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", lambda **kwargs: {socket_ref: "v"})

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        def _executor(context: Any, override_map: Dict[Any, Any], root_args: Any) -> Any:
            raise RuntimeError("exec-fail")

        return _executor

    monkeypatch.setattr(runtime_module, "compile_phase12_overrides_executor", _compile_phase12_overrides_executor)
    with pytest.raises(MeldExecutionError) as exc2:
        runtime.execute(_ctx(spell, overrides={"x": 1}))
    assert isinstance(exc2.value.inner, RuntimeError)


def test_execute_with_overrides_wraps_shape_key_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override path wraps malformed-plan shape-key failures as MeldExecutionError."""
    runtime = MeldRuntime()
    malformed_plan = SimpleNamespace(plan_variant="overrides", root_spell_id="root")
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=object(),
            override_plan=malformed_plan,
        ),
    )
    socket_ref = _SocketRef("s1", "x", 1, "normal")
    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", lambda **kwargs: {socket_ref: "v"})

    with pytest.raises(MeldExecutionError, match="Failed to build override specialization shape key") as exc:
        runtime.execute(_ctx(spell, overrides={"x": 1}))
    assert isinstance(exc.value.inner, ValueError)


def test_fast_transient_and_cleanup_contract() -> None:
    """Fast transient executes phase12 executor with None context; cleanup clears cache state."""
    runtime = MeldRuntime()
    calls = []

    def _executor(context: Any) -> str:
        calls.append(context)
        return "t"

    spell = _Spell(spell_id="s1", crafter=_crafter(executor=_executor))
    assert runtime.execute_fast_transient(spell=spell, conduit_id="cid") == "t"
    assert runtime.codegen_fast_transient(spell=spell, conduit_id="cid") == "t"
    assert calls == [None, None]

    runtime._override_specialization_cache["s1"] = {("k",): lambda *args: None}
    runtime._override_specialization_order["s1"] = deque([("k",)])
    runtime.cleanup()
    assert runtime._cleaned is True
    assert runtime._override_specialization_cache is None
    assert runtime._override_specialization_order is None
    assert runtime._max_override_specializations_per_spell is None
