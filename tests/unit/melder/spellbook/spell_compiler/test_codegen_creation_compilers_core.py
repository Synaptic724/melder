"""Unit tests for direct codegen_creation compiler entrypoints and helpers."""

import threading
from types import SimpleNamespace

import pytest

import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_no_overrides_codegen_creation_compiler as no_overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.generalized.compilers.generalized_overrides_codegen_creation_compiler as overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_no_overrides_codegen_creation_compiler as solo_no_overrides_compiler_module
import melder.aether.spellbook.spell_compiler.codegen_creation_system.strategies.solo.compilers.solo_overrides_codegen_creation_compiler as solo_overrides_compiler_module
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


def test_no_overrides_compiler_requires_ir_payload() -> None:
    """The no-overrides compiler should reject a missing IR payload."""
    with pytest.raises(ValueError, match="codegen_ir must not be None"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir=None,
        )


def test_no_overrides_compiler_returns_none_when_no_steps_exist() -> None:
    """The no-overrides compiler should no-op when the IR has no step rows."""
    assert no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
        codegen_ir={},
        spell_lookup={},
    ) is None


def test_no_overrides_compiler_from_plan_validates_plan_and_empty_steps() -> None:
    """The plan entrypoint should reject None and no-op on empty plans."""
    with pytest.raises(ValueError, match="plan must not be None"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor_from_plan(
            plan=None,
        )

    assert no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor_from_plan(
        plan=SimpleNamespace(steps=[]),
    ) is None


def test_no_overrides_compiler_resolves_root_instance_key_preferentially() -> None:
    """Root instance resolution should prefer the canonical `(spell_id, None)` row and then fall back."""
    canonical = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("root", None)),
        ),
        root_spell_id="root",
    )
    fallback = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("root", 5)),
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )
    missing = no_overrides_compiler_module._resolve_root_instance_key(
        steps=(
            SimpleNamespace(instance_key=("dep", 2)),
        ),
        root_spell_id="root",
    )

    assert canonical == ("root", None)
    assert fallback == ("root", 5)
    assert missing is None


def test_no_overrides_compiler_supports_transient_unrolled_only_for_many_non_registering_steps() -> None:
    """Transient unrolled support should stay restricted to pure transient-many steps."""
    good = (
        SimpleNamespace(existence=Existence.many, must_register=False),
        SimpleNamespace(existence=Existence.many, must_register=False),
    )
    bad_existence = (
        SimpleNamespace(existence=Existence.unique, must_register=False),
    )
    bad_register = (
        SimpleNamespace(existence=Existence.many, must_register=True),
    )

    assert no_overrides_compiler_module._supports_transient_unrolled_plan(good) is True
    assert no_overrides_compiler_module._supports_transient_unrolled_plan(bad_existence) is False
    assert no_overrides_compiler_module._supports_transient_unrolled_plan(bad_register) is False


def test_no_overrides_compiler_normalizes_transient_schema_and_rejects_bad_lengths() -> None:
    """Transient schema normalization should coerce sequences to tuples and reject bad lengths."""
    normalized = no_overrides_compiler_module._normalize_transient_schema(
        transient_schema={
            "step_count": 1,
            "root_step_index": 0,
            "call_modes": [0],
            "dep1": [-1],
            "dep2a": [-1],
            "dep2b": [-1],
            "dep3a": [-1],
            "dep3b": [-1],
            "dep3c": [-1],
            "dep4a": [-1],
            "dep4b": [-1],
            "dep4c": [-1],
            "dep4d": [-1],
            "dep5a": [-1],
            "dep5b": [-1],
            "dep5c": [-1],
            "dep5d": [-1],
            "dep5e": [-1],
            "dep6a": [-1],
            "dep6b": [-1],
            "dep6c": [-1],
            "dep6d": [-1],
            "dep6e": [-1],
            "dep6f": [-1],
            "dep7a": [-1],
            "dep7b": [-1],
            "dep7c": [-1],
            "dep7d": [-1],
            "dep7e": [-1],
            "dep7f": [-1],
            "dep7g": [-1],
            "dep8a": [-1],
            "dep8b": [-1],
            "dep8c": [-1],
            "dep8d": [-1],
            "dep8e": [-1],
            "dep8f": [-1],
            "dep8g": [-1],
            "dep8h": [-1],
        }
    )

    assert normalized["call_modes"] == (0,)
    assert normalized["dep8h"] == (-1,)

    with pytest.raises(RuntimeError, match="length must equal step_count"):
        no_overrides_compiler_module._normalize_transient_schema(
            transient_schema={
                "step_count": 1,
                "root_step_index": 0,
                "call_modes": [0, 1],
                "dep1": [-1],
                "dep2a": [-1],
                "dep2b": [-1],
                "dep3a": [-1],
                "dep3b": [-1],
                "dep3c": [-1],
                "dep4a": [-1],
                "dep4b": [-1],
                "dep4c": [-1],
                "dep4d": [-1],
                "dep5a": [-1],
                "dep5b": [-1],
                "dep5c": [-1],
                "dep5d": [-1],
                "dep5e": [-1],
                "dep6a": [-1],
                "dep6b": [-1],
                "dep6c": [-1],
                "dep6d": [-1],
                "dep6e": [-1],
                "dep6f": [-1],
                "dep7a": [-1],
                "dep7b": [-1],
                "dep7c": [-1],
                "dep7d": [-1],
                "dep7e": [-1],
                "dep7f": [-1],
                "dep7g": [-1],
                "dep8a": [-1],
                "dep8b": [-1],
                "dep8c": [-1],
                "dep8d": [-1],
                "dep8e": [-1],
                "dep8f": [-1],
                "dep8g": [-1],
                "dep8h": [-1],
            }
        )


def test_overrides_compiler_code_object_entrypoints_validate_and_delegate(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The overrides compiler should validate inputs and delegate through the code-object path cleanly."""
    with pytest.raises(ValueError, match="source must be a non-empty string"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor_code_object(
            source="",
        )

    compile_calls = []
    monkeypatch.setattr(
        overrides_compiler_module,
        "get_or_compile_executor_code",
        lambda *, source, source_name: (
            compile_calls.append((source, source_name)) or
            ("compiled", source, source_name)
        ),
    )
    code_object = overrides_compiler_module.compile_overrides_codegen_creation_executor_code_object(
        source="print('x')",
    )
    assert code_object == (
        "compiled",
        "print('x')",
        "<melder_overrides_codegen_creation_executor>",
    )
    assert compile_calls == [
        ("print('x')", "<melder_overrides_codegen_creation_executor>")
    ]

    calls = []
    monkeypatch.setattr(
        overrides_compiler_module,
        "_compile_overrides_codegen_creation_executor_core",
        lambda **kwargs: (calls.append(kwargs) or (("executor",), None)),
    )
    result = overrides_compiler_module.compile_overrides_codegen_creation_executor_from_code_object(
        code_object=("compiled",),
        execution_plan=None,
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )

    assert result == ("executor",)
    assert calls


def test_overrides_compiler_code_object_entrypoint_requires_code_object() -> None:
    """The overrides code-object entrypoint should reject a missing code object."""
    with pytest.raises(ValueError, match="code_object must not be None"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor_from_code_object(
            code_object=None,
            execution_plan=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def _make_spell(spell_id: str) -> SimpleNamespace:
    """Build a minimal callable spell stub for schema hydration tests."""
    return SimpleNamespace(
        spell_id=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
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
    result = executor(caller_creations)

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
        caller_creations,
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
    """Build a minimal schema row accepted by the no-overrides compiler hydration."""
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": 1,
        "dependency_resolution_order": (),
        "uses_positional_override": False,
        "contract_positional_override": None,
        "has_contract_payload": False,
        "contract_payload_items": (),
        "use_spell_lock_hint": False,
        "must_register": False,
    }


def _make_overrides_step_row(spell_id: str) -> dict[str, object]:
    """Build a minimal schema row accepted by the overrides compiler hydration."""
    return {
        "instance_key": (spell_id, None),
        "spell_id": spell_id,
        "existence": "many",
        "creations_target_kind": 1,
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


class _Spellspace:
    """Active spellspace stub used by spellspace-creation tests."""

    def __init__(self, spellspace_id: str, owner_conduit_id: str) -> None:
        """Store the active spellspace identity."""
        self.id = spellspace_id
        self.owner_conduit_id = owner_conduit_id


class _Creations:
    """Creations stub used by emitted no-overrides execution semantics tests."""

    def __init__(self) -> None:
        """Build empty direct stores and a shared lock surface."""
        self._lock = threading.RLock()
        self._creations: dict[str, Any] = {}
        self._disposable_creations: dict[str, Any] = {}
        self._many: list[tuple[str, Any]] = []
        self._spellspace: dict[tuple[str, str], Any] = {}
        self._disposable_spellspace: dict[
            tuple[str, str],
            tuple[Any, tuple[str, ...]],
        ] = {}
        self._owner_conduit_id = "conduit-1"
        self._active_spellspace = None

    @property
    def owner_conduit_id(self) -> str:
        """Expose the owner conduit id used by spellspace routes."""
        return self._owner_conduit_id

    def get_active_spellspace(self) -> Any:
        """Return the currently active spellspace, if any."""
        return self._active_spellspace

    def get_creation(self, spell_id: str) -> Any:
        """Return direct or disposable shared creation entries."""
        entry = self._creations.get(spell_id)
        if entry is not None and not isinstance(entry, list):
            return entry
        entry = self._disposable_creations.get(spell_id)
        if isinstance(entry, tuple):
            return entry[0]
        return None

    def add_creation(
            self,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        """Register one shared creation entry."""
        if has_disposal_methods:
            self._disposable_creations[spell_id] = (
                instance,
                tuple(disposal_methods),
            )
            return
        self._creations[spell_id] = instance

    def add_many_creations(
            self,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        """Register one many-creation entry."""
        if has_disposal_methods:
            self._many.append((spell_id, instance))
            self._disposable_creations.setdefault(spell_id, []).append(
                (instance, tuple(disposal_methods)),
            )
            return
        self._creations.setdefault(spell_id, []).append(instance)

    def register_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        """Register one spellspace-scoped creation entry."""
        if has_disposal_methods:
            self._disposable_spellspace[(spellspace_id, spell_id)] = (
                instance,
                tuple(disposal_methods),
            )
            return
        self._spellspace[(spellspace_id, spell_id)] = instance

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Any:
        """Return one spellspace-scoped creation entry."""
        entry = self._spellspace.get((spellspace_id, spell_id))
        if entry is not None:
            return entry
        entry = self._disposable_spellspace.get((spellspace_id, spell_id))
        if entry is None:
            return None
        return entry[0]


class _ExplodingLock:
    """Lock stub that fails if the runtime tries to acquire it."""

    def __enter__(self) -> "_ExplodingLock":
        """Fail on entry to prove a lock path was skipped."""
        raise AssertionError("lock should not be acquired for this path")

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """No-op exit path."""
        return None


def test_no_overrides_compiler_requires_spell_lookup_for_schema_rows() -> None:
    """Schema-row no-overrides compile should fail fast when spell lookup is missing."""
    with pytest.raises(RuntimeError, match="require spell_lookup"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (_make_no_overrides_step_row("root"),),
                "root_spell_id": "root",
            },
            spell_lookup=None,
        )


def test_no_overrides_compiler_rejects_schema_rows_missing_required_field() -> None:
    """Schema-row no-overrides compile should fail fast for missing required row fields."""
    row = _make_no_overrides_step_row("root")
    row.pop("instance_key")

    with pytest.raises(RuntimeError, match="missing required field 'instance_key'"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (row,),
                "root_spell_id": "root",
            },
            spell_lookup={"root": _make_spell("root")},
        )


def test_no_overrides_compiler_rejects_unknown_spell_id_in_schema_rows() -> None:
    """Schema-row no-overrides compile should fail when spell lookup cannot resolve a row spell id."""
    with pytest.raises(RuntimeError, match="unknown spell_id 'root'"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (_make_no_overrides_step_row("root"),),
                "root_spell_id": "root",
            },
            spell_lookup={},
        )


def test_no_overrides_compiler_rejects_unknown_existence_name() -> None:
    """Schema-row no-overrides compile should fail for unknown existence enum names."""
    row = _make_no_overrides_step_row("root")
    row["existence"] = "not_an_existence"

    with pytest.raises(RuntimeError, match="unknown existence"):
        no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
            codegen_ir={
                "steps_rows": (row,),
                "root_spell_id": "root",
            },
            spell_lookup={"root": _make_spell("root")},
        )


def test_no_overrides_compiler_supports_schema_rows_execution() -> None:
    """Schema-row no-overrides compile path should emit a callable executor that executes."""
    spell = _make_spell("root")
    executor = no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": (_make_no_overrides_step_row("root"),),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_no_overrides_codegen_creation_step_executor>"
    caller_creations = SimpleNamespace(
        _lock=threading.RLock(),
        get_creation=lambda spell_id: None,
        add_creation=lambda *args, **kwargs: None,
        add_many_creations=lambda *args, **kwargs: None,
        get_active_spellspace=lambda: None,
        register_spellspace_creation=lambda *args, **kwargs: None,
        get_spellspace_creation=lambda *args, **kwargs: None,
        owner_conduit_id="conduit-1",
    )
    assert executor(caller_creations) == "value:root"


def test_no_overrides_compiler_uses_emitted_step_source_when_transient_source_unavailable(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transient-source misses should still compile through emitted step source."""
    monkeypatch.setattr(
        no_overrides_compiler_module,
        "_build_no_overrides_codegen_executor_source",
        lambda transient_schema: None,
    )

    executor = no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": (_make_no_overrides_step_row("root"),),
            "root_spell_id": "root",
            "transient_schema": {
                "step_count": 1,
                "root_step_index": 0,
                "call_modes": (0,),
                "dep1": (-1,),
                "dep2a": (-1,),
                "dep2b": (-1,),
                "dep3a": (-1,),
                "dep3b": (-1,),
                "dep3c": (-1,),
                "dep4a": (-1,),
                "dep4b": (-1,),
                "dep4c": (-1,),
                "dep4d": (-1,),
                "dep5a": (-1,),
                "dep5b": (-1,),
                "dep5c": (-1,),
                "dep5d": (-1,),
                "dep5e": (-1,),
                "dep6a": (-1,),
                "dep6b": (-1,),
                "dep6c": (-1,),
                "dep6d": (-1,),
                "dep6e": (-1,),
                "dep6f": (-1,),
                "dep7a": (-1,),
                "dep7b": (-1,),
                "dep7c": (-1,),
                "dep7d": (-1,),
                "dep7e": (-1,),
                "dep7f": (-1,),
                "dep7g": (-1,),
                "dep8a": (-1,),
                "dep8b": (-1,),
                "dep8c": (-1,),
                "dep8d": (-1,),
                "dep8e": (-1,),
                "dep8f": (-1,),
                "dep8g": (-1,),
                "dep8h": (-1,),
            },
        },
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_no_overrides_codegen_creation_step_executor>"


def test_overrides_compiler_requires_spell_lookup_for_schema_rows() -> None:
    """Schema-row overrides compile should fail fast when spell lookup is missing."""
    with pytest.raises(RuntimeError, match="require spell_lookup"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor(
            execution_plan=None,
            plan_rows=(_make_overrides_step_row("root"),),
            root_spell_id="root",
            spell_lookup=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_overrides_compiler_rejects_schema_rows_missing_required_field() -> None:
    """Schema-row overrides compile should fail fast for missing required row fields."""
    row = _make_overrides_step_row("root")
    row.pop("instance_key")

    with pytest.raises(RuntimeError, match="missing required field 'instance_key'"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_overrides_compiler_rejects_unknown_spell_id_and_existence_in_schema_rows() -> None:
    """Schema-row overrides compile should fail for unknown spell ids and invalid existence names."""
    with pytest.raises(RuntimeError, match="unknown spell_id 'root'"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor(
            execution_plan=None,
            plan_rows=(_make_overrides_step_row("root"),),
            root_spell_id="root",
            spell_lookup={},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )

    row = _make_overrides_step_row("root")
    row["existence"] = "not_an_existence"
    with pytest.raises(RuntimeError, match="unknown existence"):
        overrides_compiler_module.compile_overrides_codegen_creation_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_overrides_compiler_supports_schema_rows_execution_and_prebound_metadata() -> None:
    """Schema-row overrides compile path should emit a callable executor with prebound step metadata."""
    spell = _make_spell("root")
    executor = overrides_compiler_module.compile_overrides_codegen_creation_executor(
        execution_plan=None,
        plan_rows=(_make_overrides_step_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )
    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_overrides_codegen_creation_executor>"
    assert "_resolve_step_instance_with_overrides" not in executor.__code__.co_names
    assert "step_spells" in executor.__code__.co_varnames
    assert "step_existences" in executor.__code__.co_varnames
    assert "step_instance_keys" in executor.__code__.co_varnames
    assert executor(
        context.caller_creations,
        {},
        None,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "value:root"


def test_overrides_compiler_emitted_source_rejects_negative_step_count() -> None:
    """The overrides emitted-source helper should enforce non-negative step counts."""
    with pytest.raises(ValueError, match="step_count must not be negative"):
        overrides_compiler_module.emit_overrides_codegen_creation_executor_source(
            step_count=-1,
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
            spell_index=SimpleNamespace(current="root"),
            spell_name="root",
        ),
        dependency_resolution_order=(
            ("single", (("dep", None),)),
            ("many", (("a", None), ("b", None))),
        ),
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


def test_no_overrides_compiler_construct_spell_instance_rejects_invalid_positional_payload() -> None:
    """Invalid `__args__` payloads should fail fast in the no-overrides compiler."""
    plan_step = SimpleNamespace(
        spell=SimpleNamespace(
            spell_index=SimpleNamespace(current="root"),
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
            spell_index=SimpleNamespace(current="root"),
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


def test_no_overrides_compiler_spellspace_route_reuses_existing_spellspace_singleton() -> None:
    """The no-overrides compiler should reuse an existing spellspace creation instead of reconstructing it."""
    creations = _Creations()
    creations._active_spellspace = _Spellspace("space-1", creations.owner_conduit_id)
    call_counter = {"value": 0}

    def _build_root() -> str:
        call_counter["value"] += 1
        return "root-instance"

    spell = _make_spell("root")
    spell.existence = Existence.unique_per_spell_space
    spell.spell = _build_root
    row = _make_no_overrides_step_row("root")
    row["existence"] = "unique_per_spell_space"
    row["creations_target_kind"] = 3
    row["must_register"] = True

    executor = no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )

    assert executor(creations) == "root-instance"
    assert executor(creations) == "root-instance"
    assert call_counter["value"] == 1


def test_no_overrides_compiler_existing_hit_skips_locks() -> None:
    """Existing shared-instance hits should skip both spell and creations lock acquisition."""
    creations = _Creations()
    creations._lock = _ExplodingLock()
    creations._creations["root"] = "existing-root"
    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell._lock = _ExplodingLock()
    row = _make_no_overrides_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = 1
    row["use_spell_lock_hint"] = True
    row["must_register"] = True

    executor = no_overrides_compiler_module.compile_no_overrides_codegen_creation_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )

    assert executor(creations, caller_creations_lock_held=False) == "existing-root"


class _OverrideSocketRef:
    """Hashable override-target probe for overrides compiler helper tests."""

    def __init__(
            self,
            node_id: str,
            param_name: str,
            param_path_id: int,
            socket_kind_value: int = 0,
    ) -> None:
        """Store stable target metadata for override-helper paths."""
        self.node_id = node_id
        self.param_name = param_name
        self.param_path_id = param_path_id
        self.socket_kind_value = socket_kind_value

    def __hash__(self) -> int:
        """Keep the probe usable as a dictionary key."""
        return hash(
            (
                self.node_id,
                self.param_name,
                self.param_path_id,
                self.socket_kind_value,
            )
        )


def test_overrides_compiler_build_kwargs_fast_path_returns_override_copy() -> None:
    """Override-only kwargs path should return a detached copy of override values."""
    override_values = {"value": "override"}
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values=override_values,
    )

    assert kwargs == {"value": "override"}
    assert kwargs is not override_values


def test_overrides_compiler_build_kwargs_contract_payload_only_returns_copy() -> None:
    """Contract-payload-only kwargs should return a detached payload copy."""
    contract_payload = {"value": "contract"}
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload=contract_payload,
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={},
    )

    assert kwargs == {"value": "contract"}
    assert kwargs is not contract_payload


def test_overrides_compiler_build_kwargs_contract_payload_only_filters_args_key() -> None:
    """Contract-payload-only kwargs should filter `__args__` when positional override mode is enabled."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload={"__args__": ("left",), "value": "contract"},
        uses_positional_override=True,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={},
    )

    assert kwargs == {"value": "contract"}


def test_overrides_compiler_build_kwargs_single_and_multi_dependency_shapes() -> None:
    """Override-aware kwargs helper should preserve single-value and list-aggregation dependency semantics."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(
            ("single", (("dep-a", None),)),
            ("multi", (("dep-b", None), ("dep-c", None))),
        ),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={
            ("dep-a", None): "v1",
            ("dep-b", None): "v2",
            ("dep-c", None): "v3",
        },
        override_values={},
    )

    assert kwargs == {
        "single": "v1",
        "multi": ["v2", "v3"],
    }


def test_overrides_compiler_build_kwargs_override_precedence_skips_dependency_lookup() -> None:
    """Override values should bypass dependency lookup for the same parameter."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(("value", (("dep-missing", None),)),),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={"value": "override"},
    )

    assert kwargs == {"value": "override"}


def test_overrides_compiler_build_kwargs_override_precedence_beats_contract_payload() -> None:
    """Override values should outrank contract payload values too."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(("value", (("dep-missing", None),)),),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload={"value": "contract"},
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={"value": "override"},
    )

    assert kwargs == {"value": "override"}


def test_overrides_compiler_build_kwargs_two_dependency_fast_path_skips_iteration() -> None:
    """Two-dependency override-aware kwargs should not fall back to generic iteration."""
    first_dependency_key = ("dep-a", None)
    second_dependency_key = ("dep-b", None)

    class _TwoDependencyKeys:
        """Two-key dependency sequence that fails if generic iteration runs."""

        def __len__(self) -> int:
            return 2

        def __getitem__(self, index: int) -> Any:
            if index == 0:
                return first_dependency_key
            if index == 1:
                return second_dependency_key
            raise IndexError(index)

        def __iter__(self) -> Any:
            raise AssertionError("two-dependency fast path must not iterate dependency keys")

    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(("multi", _TwoDependencyKeys()),),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = overrides_compiler_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={
            first_dependency_key: "v1",
            second_dependency_key: "v2",
        },
        override_values={},
    )

    assert kwargs == {
        "multi": ["v1", "v2"],
    }


def test_overrides_compiler_build_step_override_values_fast_path_returns_empty_when_no_targets() -> None:
    """No targets and no root args should return an empty override payload."""
    original_builder = overrides_compiler_module._build_instance_override_map
    overrides_compiler_module._build_instance_override_map = (
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("target helper must not run for empty targets")
        )
    )
    try:
        override_values = overrides_compiler_module._build_step_override_values(
            override_targets=(),
            override_map={},
            root_positional_override=None,
        )
    finally:
        overrides_compiler_module._build_instance_override_map = original_builder

    assert override_values == {}


def test_overrides_compiler_build_step_override_values_fast_path_returns_root_positional_payload() -> None:
    """No targets plus root args should return only the root positional payload."""
    original_builder = overrides_compiler_module._build_instance_override_map
    overrides_compiler_module._build_instance_override_map = (
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("target helper must not run for empty targets")
        )
    )
    try:
        override_values = overrides_compiler_module._build_step_override_values(
            override_targets=(),
            override_map={},
            root_positional_override=("left",),
        )
    finally:
        overrides_compiler_module._build_instance_override_map = original_builder

    assert override_values == {
        "__args__": ("left",),
    }


def test_overrides_compiler_build_step_override_values_single_target_fast_paths() -> None:
    """Single-target helper path should bypass the generic map builder and preserve root args when supplied."""
    socket_ref = _OverrideSocketRef("root", "value", 7)
    override_map = {socket_ref: "override"}
    original_builder = overrides_compiler_module._build_instance_override_map
    overrides_compiler_module._build_instance_override_map = (
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("generic target helper must not run for single target")
        )
    )
    try:
        without_args = overrides_compiler_module._build_step_override_values(
            override_targets=(socket_ref,),
            override_map=override_map,
            root_positional_override=None,
        )
        with_args = overrides_compiler_module._build_step_override_values(
            override_targets=(socket_ref,),
            override_map=override_map,
            root_positional_override=("left",),
        )
    finally:
        overrides_compiler_module._build_instance_override_map = original_builder

    assert without_args == {"value": "override"}
    assert with_args == {
        "value": "override",
        "__args__": ("left",),
    }


def test_overrides_compiler_build_step_override_values_two_target_fast_paths() -> None:
    """Two-target helper path should bypass the generic map builder and preserve root args when supplied."""
    first_socket_ref = _OverrideSocketRef("root", "value_a", 7)
    second_socket_ref = _OverrideSocketRef("root", "value_b", 8)
    override_map = {
        first_socket_ref: "override-a",
        second_socket_ref: "override-b",
    }
    original_builder = overrides_compiler_module._build_instance_override_map
    overrides_compiler_module._build_instance_override_map = (
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("generic target helper must not run for two targets")
        )
    )
    try:
        without_args = overrides_compiler_module._build_step_override_values(
            override_targets=(first_socket_ref, second_socket_ref),
            override_map=override_map,
            root_positional_override=None,
        )
        with_args = overrides_compiler_module._build_step_override_values(
            override_targets=(first_socket_ref, second_socket_ref),
            override_map=override_map,
            root_positional_override=("left",),
        )
    finally:
        overrides_compiler_module._build_instance_override_map = original_builder

    assert without_args == {
        "value_a": "override-a",
        "value_b": "override-b",
    }
    assert with_args == {
        "value_a": "override-a",
        "value_b": "override-b",
        "__args__": ("left",),
    }


def test_overrides_compiler_invoke_spell_with_kwargs_preserves_args_payload_mapping() -> None:
    """Override-aware invocation should preserve the caller payload while unpacking `__args__`."""
    captured = {}

    def _callable(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = dict(kwargs)
        return "ok"

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    kwargs_payload = {"__args__": [1, 2], "value": "override"}

    result = overrides_compiler_module._invoke_spell_with_kwargs(
        spell=spell,
        kwargs=kwargs_payload,
    )

    assert result == "ok"
    assert captured["args"] == (1, 2)
    assert captured["kwargs"] == {"value": "override"}
    assert kwargs_payload == {"__args__": [1, 2], "value": "override"}


def test_overrides_compiler_invoke_spell_with_kwargs_accepts_tuple_args_payload_and_preserves_mapping() -> None:
    """Tuple `__args__` payloads should be forwarded unchanged without mutating the input mapping."""
    captured = {}

    def _callable(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = dict(kwargs)
        return "ok"

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    kwargs_payload = {"__args__": (1, 2), "value": "override"}

    result = overrides_compiler_module._invoke_spell_with_kwargs(
        spell=spell,
        kwargs=kwargs_payload,
    )

    assert result == "ok"
    assert captured["args"] == (1, 2)
    assert captured["kwargs"] == {"value": "override"}
    assert kwargs_payload == {"__args__": (1, 2), "value": "override"}


def test_overrides_compiler_invoke_spell_with_kwargs_rejects_invalid_args_payload_type() -> None:
    """Invalid non-sequence `__args__` payloads should fail fast in the override path too."""
    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = lambda **kwargs: kwargs

    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        overrides_compiler_module._invoke_spell_with_kwargs(
            spell=spell,
            kwargs={"__args__": None},
        )


def test_overrides_compiler_namespace_prebinds_root_and_target_metadata() -> None:
    """Namespace builder should prebind the root and per-step metadata used by emitted override source."""
    root_spell = _make_spell("root")
    dep_spell = _make_spell("dep")
    socket_ref = _OverrideSocketRef("root", "value", 7)
    steps = (
        SimpleNamespace(
            instance_key=("root", None),
            spell=root_spell,
            existence=Existence.unique,
            creations_target_kind=1,
            use_spell_lock_hint=True,
            must_register=True,
            is_existing_creation=False,
        ),
        SimpleNamespace(
            instance_key=("dep", 1),
            spell=dep_spell,
            existence=Existence.many,
            creations_target_kind=2,
            use_spell_lock_hint=False,
            must_register=False,
            is_existing_creation=False,
        ),
    )

    namespace = overrides_compiler_module._build_overrides_codegen_creation_executor_namespace(
        steps=steps,
        step_override_targets=((socket_ref,), ()),
        root_instance_key=("root", None),
        root_spell_id="root",
        any_overrides_present=True,
    )

    assert namespace["root_instance_key"] == ("root", None)
    assert namespace["root_spell_id"] == "root"
    assert namespace["any_overrides_present"] is True
    assert namespace["step_spells"] == (root_spell, dep_spell)
    assert namespace["step_instance_keys"] == (("root", None), ("dep", 1))
    assert namespace["step_is_root"] == (True, False)
    assert namespace["step_has_targeted_overrides"] == (True, False)
    assert namespace["step_override_target_counts"] == (1, 0)

