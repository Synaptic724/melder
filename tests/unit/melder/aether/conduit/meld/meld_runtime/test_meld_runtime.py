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
        mutation_plan: Optional[Any] = None,
        root_blueprint: Optional[Any] = None,
        codegen_ir: Optional[Any] = None,
) -> Any:
    """Build a minimal SpellCrafter artifact container."""
    resolved_root_blueprint = root_blueprint
    if resolved_root_blueprint is None:
        resolved_root_blueprint = SimpleNamespace(path_registry={})
    return SimpleNamespace(
        phase12_no_overrides_executor=executor,
        override_patch_map_phase10=patch_map,
        execution_plan_phase11_overrides=override_plan,
        execution_plan_phase11_overrides_with_mutations=(
            mutation_plan if mutation_plan is not None else override_plan
        ),
        root_blueprint_phase5=resolved_root_blueprint,
        codegen_ir=codegen_ir,
    )


def _override_plan(
        *,
        override_keys: Optional[list[str]] = None,
        plan_variant: str = "overrides",
) -> Any:
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
        plan_variant=plan_variant,
        root_spell_id="root",
        steps=[step],
    )


def _override_codegen_ir(
        *,
        variant_key: str = "overrides",
        signature: str = "sig-overrides",
        root_spell_id: str = "s1",
        steps_rows: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Build minimal Phase11 execution IR payload consumed by override runtime paths.
    """
    rows = steps_rows if steps_rows is not None else ({"spell_id": root_spell_id},)
    return {
        "phase8_11": {
            "execution": {
                variant_key: {
                    "signature": signature,
                    "steps_rows_signature": "sig-rows",
                    "root_spell_id": root_spell_id,
                    "steps_rows": rows,
                },
            },
        },
    }


def test_execute_rejects_none_context() -> None:
    """`execute` fails naturally when context is None."""
    with pytest.raises(AttributeError):
        MeldRuntime().execute(None)


def test_execute_rejects_none_root_spell() -> None:
    """`execute` fails naturally when root spell is missing."""
    with pytest.raises(AttributeError):
        MeldRuntime().execute(_ctx(None))


@pytest.mark.parametrize("validity", [SpellValidity.invalid, SpellValidity.gated, SpellValidity.disabled])
def test_execute_ignores_invalid_validity_state(validity: SpellValidity) -> None:
    """Runtime trusts upstream validation and executes even for non-valid validity states."""
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), system_state=_SystemState(validity))
    assert MeldRuntime().execute(_ctx(spell)) == "ok"


def test_execute_ignores_dirty_root_state() -> None:
    """Runtime does not perform dirty-root checks and executes directly."""
    spellbook = _Spellbook(aether=_Aether(_CCManager(dirty=True)))
    spell = _Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), spellbook=spellbook)
    assert MeldRuntime().execute(_ctx(spell)) == "ok"


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


def test_execute_ignores_broken_and_unvalidated_flags() -> None:
    """Runtime trusts upstream spell-state validation flags."""
    runtime = MeldRuntime()
    assert runtime.execute(
        _ctx(_Spell(spell_id="s1", crafter=_crafter(executor=lambda c: "ok"), is_broken=True))
    ) == "ok"
    assert runtime.execute(
        _ctx(_Spell(spell_id="s2", crafter=_crafter(executor=lambda c: "ok"), validated=False))
    ) == "ok"


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
    """No-overrides path fails naturally when crafter artifacts are missing."""
    runtime = MeldRuntime()
    with pytest.raises(AttributeError):
        runtime.execute(_ctx(_Spell(spell_id="s1", crafter=None)))
    with pytest.raises(MeldExecutionError) as exc:
        runtime.execute(_ctx(_Spell(spell_id="s2", crafter=_crafter(executor=None))))
    assert isinstance(exc.value.inner, TypeError)


def test_execute_mutation_only_routes_to_override_specialization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mutation-only calls use the override specialization route without patch-map apply."""
    runtime = MeldRuntime()
    mutation_plan = _override_plan(plan_variant="overrides_with_mutations")
    spell = _Spell(
        spell_id="s1",
        has_mutation_override=True,
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=None,
            override_plan=_override_plan(),
            mutation_plan=mutation_plan,
            root_blueprint=SimpleNamespace(path_registry="registry"),
            codegen_ir=_override_codegen_ir(
                variant_key="overrides_with_mutations",
                signature="sig-mut",
                root_spell_id="s1",
            ),
        ),
    )

    def _unexpected_apply(**kwargs: Any) -> Dict[Any, Any]:
        raise AssertionError("patch-map apply should not run")

    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_override_payload",
        _unexpected_apply,
    )

    compile_count = {"value": 0}

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        compile_count["value"] += 1
        assert kwargs["execution_plan"] is None
        assert kwargs["any_overrides_present"] is False
        assert kwargs["override_targets_by_spell_id"] == {}
        assert kwargs["plan_rows"] == ({"spell_id": "s1"},)

        def _executor(context: Any, override_map: Dict[Any, Any], root_args: Any) -> str:
            assert override_map == {}
            assert root_args is None
            return "mutation-ok"

        return _executor

    monkeypatch.setattr(
        runtime_module,
        "compile_phase12_overrides_executor",
        _compile_phase12_overrides_executor,
    )

    assert runtime.execute(_ctx(spell)) == "mutation-ok"
    assert compile_count["value"] == 1


def test_execute_mutation_with_overrides_requires_patch_map() -> None:
    """Mutation route still requires phase10 patch-map when per-call overrides are provided."""
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        has_mutation_override=True,
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=None,
            override_plan=_override_plan(),
            mutation_plan=_override_plan(plan_variant="overrides_with_mutations"),
            codegen_ir=_override_codegen_ir(
                variant_key="overrides_with_mutations",
                root_spell_id="s1",
            ),
        ),
    )

    with pytest.raises(MeldExecutionError, match="Phase 10 override patch map"):
        runtime.execute(_ctx(spell, overrides={"x": 1}))


def test_execute_with_root_args_only_skips_patch_map_apply(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    `__args__`-only overrides skip Phase10 patch-map application.
    """
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=None,
            override_plan=_override_plan(),
            codegen_ir=_override_codegen_ir(root_spell_id="s1"),
        ),
    )

    def _unexpected_apply(**kwargs: Any) -> Dict[Any, Any]:
        raise AssertionError("patch-map apply should not run for __args__-only overrides")

    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_override_payload",
        _unexpected_apply,
    )

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        assert kwargs["override_targets_by_spell_id"] == {}
        assert kwargs["any_overrides_present"] is True

        def _executor(context: Any, override_map: Dict[Any, Any], root_args: Any) -> str:
            assert override_map == {}
            assert root_args == (1, 2)
            return "ok"

        return _executor

    monkeypatch.setattr(
        runtime_module,
        "compile_phase12_overrides_executor",
        _compile_phase12_overrides_executor,
    )

    assert runtime.execute(_ctx(spell, overrides={"__args__": [1, 2]})) == "ok"


def test_execute_mutation_with_root_args_only_skips_patch_map_apply(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Mutation route allows `__args__`-only payloads without a Phase10 patch map.
    """
    runtime = MeldRuntime()
    mutation_plan = _override_plan(plan_variant="overrides_with_mutations")
    spell = _Spell(
        spell_id="s1",
        has_mutation_override=True,
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=None,
            override_plan=_override_plan(),
            mutation_plan=mutation_plan,
            codegen_ir=_override_codegen_ir(
                variant_key="overrides_with_mutations",
                root_spell_id="s1",
            ),
        ),
    )

    def _unexpected_apply(**kwargs: Any) -> Dict[Any, Any]:
        raise AssertionError("patch-map apply should not run for __args__-only overrides")

    monkeypatch.setattr(
        runtime_module,
        "apply_phase10_override_payload",
        _unexpected_apply,
    )

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        assert kwargs["execution_plan"] is None
        assert kwargs["override_targets_by_spell_id"] == {}
        assert kwargs["any_overrides_present"] is True

        def _executor(context: Any, override_map: Dict[Any, Any], root_args: Any) -> str:
            assert override_map == {}
            assert root_args == (3,)
            return "mutation-args-only-ok"

        return _executor

    monkeypatch.setattr(
        runtime_module,
        "compile_phase12_overrides_executor",
        _compile_phase12_overrides_executor,
    )

    assert runtime.execute(_ctx(spell, overrides={"__args__": [3]})) == "mutation-args-only-ok"


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


def test_execute_with_overrides_requires_patch_map_and_execution_ir() -> None:
    """Override path requires patch-map apply support and codegen IR contracts."""
    runtime = MeldRuntime()
    no_patch = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=None,
            override_plan=object(),
            codegen_ir=_override_codegen_ir(root_spell_id="s1"),
        ),
    )
    with pytest.raises(MeldExecutionError, match="Phase 10 override patch map"):
        runtime.execute(_ctx(no_patch, overrides={"x": 1}))

    no_ir = _Spell(
        spell_id="s2",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=object(),
            override_plan=None,
            codegen_ir=None,
        ),
    )
    with pytest.raises(TypeError):
        runtime.execute(_ctx(no_ir, overrides={"x": 1}))


def test_resolve_override_execution_signature_prefers_codegen_ir_payload() -> None:
    """Override shape-key signature resolves from codegen IR execution payload."""
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
    signature = MeldRuntime._build_override_plan_signature_from_ir_payload(
        override_execution_ir_payload=payload,
    )

    assert signature == ("phase11_overrides_ir", "sig-overrides", "sig-rows")


def test_build_override_plan_signature_from_ir_payload_requires_signature() -> None:
    """IR payload signature helper enforces payload and signature requirements."""
    signature = MeldRuntime._build_override_plan_signature_from_ir_payload(
        override_execution_ir_payload={
            "signature": "sig-overrides",
            "steps_rows_signature": "sig-rows",
        },
    )
    assert signature == ("phase11_overrides_ir", "sig-overrides", "sig-rows")

    with pytest.raises(TypeError):
        MeldRuntime._build_override_plan_signature_from_ir_payload(
            override_execution_ir_payload=None,
        )
    with pytest.raises(KeyError):
        MeldRuntime._build_override_plan_signature_from_ir_payload(
            override_execution_ir_payload={"steps_rows_signature": "sig-rows"},
        )


def test_resolve_override_execution_signature_prefers_mutation_codegen_payload_when_requested() -> None:
    """Override shape-key signature supports selecting mutation execution payloads."""
    crafter = _crafter(
        executor=lambda c: "x",
        patch_map=object(),
        override_plan=_override_plan(),
        mutation_plan=_override_plan(plan_variant="overrides_with_mutations"),
    )
    crafter.codegen_ir = {
        "phase8_11": {
            "execution": {
                "overrides_with_mutations": {
                    "signature": "sig-mutations",
                    "steps_rows_signature": "sig-rows-mut",
                },
            },
        },
    }

    payload = MeldRuntime._resolve_override_execution_ir_payload(
        crafter=crafter,
        execution_ir_key="overrides_with_mutations",
    )
    signature = MeldRuntime._build_override_plan_signature_from_ir_payload(
        override_execution_ir_payload=payload,
    )

    assert signature == ("phase11_overrides_ir", "sig-mutations", "sig-rows-mut")


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


def test_resolve_override_execution_ir_payload_supports_mutation_variant_key() -> None:
    """Override execution IR resolver supports selecting mutation variant payloads."""
    crafter = _crafter(
        executor=lambda c: "x",
        patch_map=object(),
        override_plan=_override_plan(),
        mutation_plan=_override_plan(plan_variant="overrides_with_mutations"),
        codegen_ir={
            "phase8_11": {
                "execution": {
                    "overrides_with_mutations": {
                        "signature": "sig-mutations",
                        "steps_rows_signature": "sig-rows-mut",
                    },
                },
            },
        },
    )

    payload = MeldRuntime._resolve_override_execution_ir_payload(
        crafter=crafter,
        execution_ir_key="overrides_with_mutations",
    )

    assert payload == {
        "signature": "sig-mutations",
        "steps_rows_signature": "sig-rows-mut",
    }


def test_split_override_payload_strips_root_args_without_mutating_input() -> None:
    """Root args split keeps input payload stable and returns stripped target payload."""
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(executor=lambda c: "x"),
    )
    payload = {"__args__": [1, 2], "dep": "value"}

    stripped_payload, root_args = MeldRuntime._split_override_payload(
        spell=spell,
        override_payload=payload,
    )

    assert stripped_payload == {"dep": "value"}
    assert root_args == (1, 2)
    assert payload == {"__args__": [1, 2], "dep": "value"}
    assert stripped_payload is not payload


def test_split_override_payload_rejects_non_sequence_root_args() -> None:
    """Root args split rejects invalid `__args__` payload types."""
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(executor=lambda c: "x"),
    )
    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        MeldRuntime._split_override_payload(
            spell=spell,
            override_payload={"__args__": "not-a-sequence"},
        )


def test_split_override_payload_root_args_only_returns_empty_target_payload() -> None:
    """Root-args-only payload split returns empty target payload without key bleed."""
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(executor=lambda c: "x"),
    )
    stripped_payload, root_args = MeldRuntime._split_override_payload(
        spell=spell,
        override_payload={"__args__": (7, 8)},
    )

    assert stripped_payload == {}
    assert root_args == (7, 8)


def test_split_override_payload_tuple_root_args_preserves_tuple_identity() -> None:
    """Tuple root args are preserved by split normalization without rebuilding tuple values."""
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(executor=lambda c: "x"),
    )
    root_args_payload = (9, 10)
    stripped_payload, root_args = MeldRuntime._split_override_payload(
        spell=spell,
        override_payload={
            "__args__": root_args_payload,
            "dep": "value",
        },
    )

    assert stripped_payload == {"dep": "value"}
    assert root_args is root_args_payload


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
    """Override path wraps patch-map errors and lets executor failures bubble."""
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=object(),
            override_plan=_override_plan(),
            codegen_ir=_override_codegen_ir(root_spell_id="s1"),
        ),
    )

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
    with pytest.raises(RuntimeError, match="exec-fail"):
        runtime.execute(_ctx(spell, overrides={"x": 1}))
    


def test_execute_with_overrides_wraps_shape_key_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override path wraps malformed IR shape-key failures as MeldExecutionError."""
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=object(),
            override_plan=_override_plan(),
            codegen_ir={
                "phase8_11": {
                    "execution": {
                        "overrides": {
                            "steps_rows_signature": "sig-rows",
                            "root_spell_id": "s1",
                            "steps_rows": ({"spell_id": "s1"},),
                        },
                    },
                },
            },
        ),
    )
    socket_ref = _SocketRef("s1", "x", 1, "normal")
    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", lambda **kwargs: {socket_ref: "v"})

    with pytest.raises(MeldExecutionError, match="Failed to build override specialization shape key") as exc:
        runtime.execute(_ctx(spell, overrides={"x": 1}))
    assert isinstance(exc.value.inner, KeyError)


def test_collect_override_targets_and_socket_shape_grouping_is_stable_for_equivalent_maps() -> None:
    """Socket-ref grouping/sorting is stable across equivalent insertion orders."""
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")

    map_a = {socket_a: "va", socket_b: "vb"}
    map_b = {socket_b: "vb", socket_a: "va"}

    targets_a, shape_a = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map=map_a,
    )
    targets_b, shape_b = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map=map_b,
    )

    assert targets_a == targets_b
    assert shape_a == shape_b
    assert targets_a["s1"] == (socket_b, socket_a)


def test_collect_override_targets_and_socket_shape_is_deterministic() -> None:
    """Combined grouping+shape helper emits stable deterministic structures."""
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")
    socket_c = _SocketRef("s2", "z", 3, "optional")

    map_a = {socket_a: "va", socket_b: "vb", socket_c: "vc"}
    map_b = {socket_c: "vc", socket_b: "vb", socket_a: "va"}

    targets_a, shape_a = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map=map_a,
    )
    targets_b, shape_b = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map=map_b,
    )

    assert targets_a == targets_b
    assert shape_a == shape_b
    assert targets_a["s1"] == (socket_b, socket_a)
    assert targets_a["s2"] == (socket_c,)
    assert shape_a == (
        ("s1", 1, "b", "normal"),
        ("s1", 9, "a", "normal"),
        ("s2", 3, "z", "optional"),
    )


def test_collect_override_targets_and_socket_shape_single_socket_fast_path_output() -> None:
    """Single-socket payloads emit deterministic grouped target and shape tuples."""
    socket_ref = _SocketRef("s1", "dep", 7, "normal")

    targets, shape = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map={socket_ref: "value"},
    )

    assert targets == {"s1": (socket_ref,)}
    assert shape == (("s1", 7, "dep", "normal"),)


def test_collect_override_targets_and_socket_shape_single_socket_fast_path_skips_sort(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Single-socket payloads bypass sort work in the collection helper."""
    socket_ref = _SocketRef("s1", "dep", 7, "normal")

    def _unexpected_sorted(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("sorted should not run for single-socket payloads")

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr("builtins.sorted", _unexpected_sorted)
        targets, shape = MeldRuntime._collect_override_targets_and_socket_shape(
            override_map={socket_ref: "value"},
        )

    assert targets == {"s1": (socket_ref,)}
    assert shape == (("s1", 7, "dep", "normal"),)


def test_collect_override_targets_and_socket_shape_two_socket_fast_path_output() -> None:
    """Two-socket payloads emit deterministic grouped targets and sorted shape rows."""
    socket_a = _SocketRef("s1", "a", 9, "normal")
    socket_b = _SocketRef("s1", "b", 1, "normal")

    targets, shape = MeldRuntime._collect_override_targets_and_socket_shape(
        override_map={socket_a: "va", socket_b: "vb"},
    )

    assert targets == {"s1": (socket_b, socket_a)}
    assert shape == (
        ("s1", 1, "b", "normal"),
        ("s1", 9, "a", "normal"),
    )


def test_collect_override_targets_and_socket_shape_two_socket_fast_path_skips_sort(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two-socket payloads bypass sort work while preserving deterministic output order."""
    socket_a = _SocketRef("s2", "z", 5, "normal")
    socket_b = _SocketRef("s1", "a", 8, "optional")

    def _unexpected_sorted(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("sorted should not run for two-socket payloads")

    with monkeypatch.context() as scoped_patch:
        scoped_patch.setattr("builtins.sorted", _unexpected_sorted)
        targets, shape = MeldRuntime._collect_override_targets_and_socket_shape(
            override_map={socket_a: "va", socket_b: "vb"},
        )

    assert targets == {
        "s1": (socket_b,),
        "s2": (socket_a,),
    }
    assert shape == (
        ("s1", 8, "a", "optional"),
        ("s2", 5, "z", "normal"),
    )


def test_build_override_shape_key_uses_precomputed_socket_shape() -> None:
    """Shape-key builder accepts precomputed socket-shape tuples as-is."""
    shape_key = MeldRuntime._build_override_shape_key(
        plan_signature=("plan", "sig"),
        socket_shape=(("s1", 7, "dep", "normal"),),
        root_positional_override=(1, 2, 3),
    )

    assert shape_key == (
        ("plan", "sig"),
        (("s1", 7, "dep", "normal"),),
        3,
    )


def test_execute_with_overrides_evicts_oldest_shape_when_cache_is_bounded(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Per-spell override specialization cache evicts oldest shape in FIFO order."""
    runtime = MeldRuntime()
    runtime._max_override_specializations_per_spell = 1
    patch_map = object()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=patch_map,
            override_plan=_override_plan(),
            codegen_ir=_override_codegen_ir(root_spell_id="s1"),
        ),
    )
    socket_ref_a = _SocketRef("s1", "a", 1, "normal")
    socket_ref_b = _SocketRef("s1", "b", 2, "normal")

    def _apply_phase10_override_payload(
            *,
            override_patch_map: Any,
            override_payload: Dict[str, Any],
    ) -> Dict[Any, Any]:
        assert override_patch_map is patch_map
        if "a" in override_payload:
            return {socket_ref_a: "va"}
        return {socket_ref_b: "vb"}

    compile_count = {"value": 0}

    def _compile_phase12_overrides_executor(**kwargs: Any) -> Any:
        compile_count["value"] += 1

        def _executor(context: Any, override_map: Dict[Any, Any], root_args: Any) -> str:
            if socket_ref_a in override_map:
                return "shape-a"
            return "shape-b"

        return _executor

    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", _apply_phase10_override_payload)
    monkeypatch.setattr(runtime_module, "compile_phase12_overrides_executor", _compile_phase12_overrides_executor)

    assert runtime.execute(_ctx(spell, overrides={"a": 1})) == "shape-a"
    assert runtime.execute(_ctx(spell, overrides={"b": 1})) == "shape-b"
    assert runtime.execute(_ctx(spell, overrides={"a": 1})) == "shape-a"
    assert compile_count["value"] == 3


def test_execute_with_overrides_wraps_schema_compile_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Override path lets schema-row compile failures bubble."""
    runtime = MeldRuntime()
    spell = _Spell(
        spell_id="s1",
        crafter=_crafter(
            executor=lambda c: "x",
            patch_map=object(),
            override_plan=_override_plan(),
            codegen_ir={
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
            },
        ),
    )
    socket_ref = _SocketRef("s1", "x", 1, "normal")
    monkeypatch.setattr(runtime_module, "apply_phase10_override_payload", lambda **kwargs: {socket_ref: "v"})
    monkeypatch.setattr(
        runtime_module,
        "compile_phase12_overrides_executor",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("schema-fail")),
    )

    with pytest.raises(RuntimeError, match="schema-fail"):
        runtime.execute(_ctx(spell, overrides={"x": 1}))


def test_no_overrides_fast_transient_and_cleanup_contract() -> None:
    """Fast transient no-overrides path executes with None context; cleanup clears cache state."""
    runtime = MeldRuntime()
    calls = []

    def _executor(context: Any) -> str:
        calls.append(context)
        return "t"

    spell = _Spell(spell_id="s1", crafter=_crafter(executor=_executor))
    assert runtime.execute_no_overrides_fast_transient(spell=spell) == "t"
    assert calls == [None]

    runtime._override_specialization_cache["s1"] = {("k",): lambda *args: None}
    runtime._override_specialization_order["s1"] = deque([("k",)])
    runtime.cleanup()
    assert runtime._cleaned is True
    assert runtime._override_specialization_cache is None
    assert runtime._override_specialization_order is None
    assert runtime._max_override_specializations_per_spell is None
