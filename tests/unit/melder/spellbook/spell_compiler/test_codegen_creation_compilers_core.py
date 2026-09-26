"""Unit tests for direct codegen_creation compiler entrypoints and helpers."""

import threading
from types import SimpleNamespace

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler as no_overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.many_only.compilers.many_only_no_overrides_codegen_creation_compiler as many_only_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler as solo_no_overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler as solo_overrides_compiler_module
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


def test_many_only_row_hydration_resolves_root_instance_key_preferentially() -> None:
    """Root instance resolution should prefer the canonical `(spell_id, None)` row and then fall back."""
    canonical = many_only_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("root", None)),
        ),
        root_spell_id="root",
    )
    fallback = many_only_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )
    missing = many_only_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )

    assert canonical == ("root", None)
    assert fallback == ("root", 5)
    assert missing is None


def _make_spell(spell_id: str) -> SimpleNamespace:
    """
    Build a minimal callable spell stub for schema hydration tests.

    Like a real Spell it carries its frame's SpellSystemStates; this registry holds
    no Phase-3 topology, so solo executors bind the raw call target.
    """
    return SimpleNamespace(
        spell_id=spell_id,
        spell_index=SimpleNamespace(selected_spell_id=spell_id),
        _spell_system_states=SimpleNamespace(get_local_topology=lambda spell_index: None),
        spell_name=spell_id,
        existence=Existence.many,
        is_existing_creation=False,
        is_class_spell=True,
        is_method_spell=False,
        is_lambda_spell=False,
        spell=lambda: "value:{0}".format(spell_id),
        _owner_creations=None,
        _lock=threading.RLock(),
        has_disposal_methods=False,
        disposal_method_names=(),
        user_created_object=None,
    )


def _make_recording_creations() -> SimpleNamespace:
    """Build a minimal creations probe that records registration calls."""
    add_creation_calls = []
    add_many_calls = []

    def _add_creation(*args, **kwargs):
        add_creation_calls.append((args, kwargs))

    def _add_many_creations(*args, **kwargs):
        add_many_calls.append((args, kwargs))

    return SimpleNamespace(
        add_creation=_add_creation,
        add_many_creations=_add_many_creations,
        add_creation_calls=add_creation_calls,
        add_many_calls=add_many_calls,
    )


def _meld_for(store: Any) -> SimpleNamespace:
    """
    Wrap a creation store as the meld door the codegen executors read stores off.

    The migrated executors take the resolving meld and read the route store off
    it (`_conduit_creations` / `_spellspace_creations` / `_root_creations` /
    `_cluster_creations.resolved_store()`), so tests pass this wrapper rather
    than the bare store.
    """
    return SimpleNamespace(
        _conduit_creations=store,
        _spellspace_creations=store,
        _root_creations=store,
        _cluster_creations=SimpleNamespace(resolved_store=lambda: store),
    )


def test_solo_no_overrides_compiler_emits_compiled_code_and_preserves_registration(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Solo no-overrides should compile through the shared code-cache seam and preserve route behavior."""
    compile_calls = []

    def _compile_via_cache(*, source: str, source_name: str):
        compile_calls.append((source, source_name))
        return compile(source, source_name, "exec")

    monkeypatch.setattr(
        solo_no_overrides_compiler_module,
        "get_or_compile_executor_code",
        _compile_via_cache,
    )

    spell = _make_spell("solo-no")
    caller_creations = _make_recording_creations()

    executor = (
        solo_no_overrides_compiler_module.compile_solo_no_overrides_codegen_creation_executor(
            spell=spell,
            solo_emit_key="unique_per_conduit",
            fast_transient_no_overrides_enabled=False,
        )
    )
    result = executor(_meld_for(caller_creations))

    assert result == "value:solo-no"
    assert len(compile_calls) == 1
    assert compile_calls[0][1].startswith("<solo_no_overrides_codegen_creation:")
    assert caller_creations.add_creation_calls == [
        (("solo-no", "value:solo-no"), {})
    ]
    assert caller_creations.add_many_calls == []


def test_solo_overrides_compiler_emits_compiled_code_and_preserves_override_behavior(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Solo overrides should compile through the shared code-cache seam and preserve root-only override behavior."""
    compile_calls = []

    def _compile_via_cache(*, source: str, source_name: str):
        compile_calls.append((source, source_name))
        return compile(source, source_name, "exec")

    monkeypatch.setattr(
        solo_overrides_compiler_module,
        "get_or_compile_executor_code",
        _compile_via_cache,
    )

    def _call_target(*args, **kwargs):
        return {
            "args": args,
            "kwargs": kwargs,
        }

    spell = _make_spell("solo-over")
    spell.spell = _call_target
    caller_creations = _make_recording_creations()

    executor = (
        solo_overrides_compiler_module.compile_solo_overrides_codegen_creation_executor(
            spell=spell,
            solo_emit_key="unique_per_conduit",
        )
    )
    result = executor(
        _meld_for(caller_creations),
        {
            "__args__": ("left",),
            "right": "value",
        },
    )

    assert result == {
        "args": ("left",),
        "kwargs": {
            "right": "value",
        },
    }
    assert len(compile_calls) == 1
    assert compile_calls[0][1].startswith("<solo_overrides_codegen_creation:")
    assert caller_creations.add_creation_calls == [
        (("solo-over", result), {})
    ]
    assert caller_creations.add_many_calls == []


def _make_no_overrides_step_row(spell_id: str) -> dict[str, object]:
    """Build a minimal schema row accepted by the generalized row hydration."""
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": 1,
        "dependency_resolution_order": (),
        "collection_param_names": (),
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
    }


def test_no_overrides_compiler_requires_spell_lookup_for_schema_rows() -> None:
    """Manifest row hydration should fail fast when spell lookup is missing."""
    with pytest.raises(RuntimeError, match="require spell_lookup"):
        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(_make_no_overrides_step_row("root"),),
            spell_lookup=None,
        )


def test_no_overrides_compiler_rejects_schema_rows_missing_required_field() -> None:
    """Manifest row hydration should fail fast for missing required row fields."""
    row = _make_no_overrides_step_row("root")
    row.pop("instance_key")

    with pytest.raises(RuntimeError, match="missing required field 'instance_key'"):
        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(row,),
            spell_lookup={"root": _make_spell("root")},
        )


def test_no_overrides_compiler_rejects_unknown_spell_id_in_schema_rows() -> None:
    """Manifest row hydration should fail when spell lookup cannot resolve a row spell id."""
    with pytest.raises(RuntimeError, match="unknown spell_id 'root'"):
        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(_make_no_overrides_step_row("root"),),
            spell_lookup={},
        )


def test_no_overrides_compiler_rejects_unknown_existence_name() -> None:
    """Manifest row hydration should fail for unknown existence enum names."""
    row = _make_no_overrides_step_row("root")
    row["existence"] = "not_an_existence"

    with pytest.raises(RuntimeError, match="unknown existence"):
        no_overrides_compiler_module._hydrate_steps_from_rows(
            steps_rows=(row,),
            spell_lookup={"root": _make_spell("root")},
        )


def test_no_overrides_compiler_build_kwargs_contract_payload_only_returns_copy() -> None:
    """Contract-payload-only kwargs should return a detached payload copy."""
    contract_payload = {"fixed": "value"}
    plan_step = SimpleNamespace(
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        uses_positional_override=False,
        contract_payload=contract_payload,
    )

    kwargs = no_overrides_compiler_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={},
    )

    assert kwargs == {"fixed": "value"}
    assert kwargs is not contract_payload


def test_no_overrides_compiler_build_kwargs_contract_payload_filters_args_key_when_positional_enabled() -> None:
    """Contract-payload-only kwargs should filter `__args__` when positional override mode is enabled."""
    plan_step = SimpleNamespace(
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        uses_positional_override=True,
        contract_payload={"__args__": [1, 2], "fixed": "value"},
    )

    kwargs = no_overrides_compiler_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={},
    )

    assert kwargs == {"fixed": "value"}


def test_no_overrides_compiler_build_kwargs_single_and_multi_dependency_shapes() -> None:
    """The no-overrides kwargs helper should preserve single-value and list-aggregation dependency semantics."""
    plan_step = SimpleNamespace(
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(selected_spell_id="root"),
            spell_name="root",
        ),
        dependency_resolution_order=(
            ("single", (("dep", None),)),
            ("many", (("a", None), ("b", None))),
        ),
        collection_param_names=frozenset(),
        contract_positional_override=None,
        has_contract_payload=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    instance_results = {
        ("dep", None): "value",
        ("a", None): "a",
        ("b", None): "b",
    }

    kwargs = no_overrides_compiler_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
    )

    assert kwargs["single"] == "value"
    assert kwargs["many"] == ["a", "b"]


def test_no_overrides_compiler_build_kwargs_wraps_single_member_collection_socket() -> None:
    """A collection socket with exactly one wired member injects a one-element list, not a bare scalar."""
    plan_step = SimpleNamespace(
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(selected_spell_id="root"),
            spell_name="root",
        ),
        dependency_resolution_order=(
            ("plugins", (("only", None),)),
            ("single", (("dep", None),)),
        ),
        collection_param_names=frozenset({"plugins"}),
        contract_positional_override=None,
        has_contract_payload=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    instance_results = {
        ("only", None): "member",
        ("dep", None): "value",
    }

    kwargs = no_overrides_compiler_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results=instance_results,
    )

    assert kwargs["plugins"] == ["member"]
    assert kwargs["single"] == "value"


def test_no_overrides_compiler_construct_spell_instance_rejects_invalid_positional_payload() -> None:
    """Invalid `__args__` payloads should fail fast in the no-overrides compiler."""
    plan_step = SimpleNamespace(
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(selected_spell_id="root"),
            spell_name="root",
            existence=Existence.many,
            is_existing_creation=False,
            is_class_spell=True,
            is_method_spell=False,
            is_lambda_spell=False,
            spell=lambda: "never",
        ),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    original_builder = no_overrides_compiler_module._build_kwargs_no_overrides
    no_overrides_compiler_module._build_kwargs_no_overrides = (
        lambda *, plan_step, instance_results: {"__args__": "bad"}
    )
    try:
        with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
            no_overrides_compiler_module._construct_spell_instance(
                plan_step=plan_step,
                instance_results={},
            )
    finally:
        no_overrides_compiler_module._build_kwargs_no_overrides = original_builder


def test_no_overrides_compiler_construct_spell_instance_accepts_tuple_positional_payload() -> None:
    """Tuple positional payloads should be forwarded unchanged by the no-overrides compiler."""
    captured = {}

    def _callable(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return "ok"

    plan_step = SimpleNamespace(
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(selected_spell_id="root"),
            spell_name="root",
            existence=Existence.many,
            is_existing_creation=False,
            is_class_spell=True,
            is_method_spell=False,
            is_lambda_spell=False,
            spell=_callable,
        ),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=False,
        uses_positional_override=False,
        contract_payload=None,
    )
    original_builder = no_overrides_compiler_module._build_kwargs_no_overrides
    no_overrides_compiler_module._build_kwargs_no_overrides = (
        lambda *, plan_step, instance_results: {"__args__": ("left", "right")}
    )
    try:
        assert no_overrides_compiler_module._construct_spell_instance(
            plan_step=plan_step,
            instance_results={},
        ) == "ok"
    finally:
        no_overrides_compiler_module._build_kwargs_no_overrides = original_builder

    assert captured["args"] == ("left", "right")
    assert captured["kwargs"] == {}


