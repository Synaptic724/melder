import threading
from types import SimpleNamespace
from typing import Any

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import (
    ExecutionPlanCallMode,
    ExecutionPlanTargetKind,
)
import melder.spellbook.spell_crafter.blueprints.phase12_no_overrides_executor as phase12_module
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError


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
        spell=lambda: f"value:{spell_id}",
        _owner_creations=None,
        _lock=threading.RLock(),
        has_disposal_methods=False,
        disposal_method_names=(),
    )


def _make_step_row(spell_id: str) -> dict[str, object]:
    """Build a minimal schema row accepted by no-overrides step hydration."""
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


class _CreationRecord:
    """Container matching creations registry value contract."""

    def __init__(self, value: Any) -> None:
        self.value = value


class _Spellspace:
    """Active spellspace stub used by spellspace-creation tests."""

    def __init__(self, spellspace_id: str, owner_conduit: Any) -> None:
        self.id = spellspace_id
        self.owner_conduit = owner_conduit


class _Conduit:
    """Conduit stub exposing active spellspace lookup for creations."""

    def __init__(self) -> None:
        self._active_spellspace = None

    def get_active_spellspace(self) -> Any:
        return self._active_spellspace


class _Creations:
    """Creations stub for emitted no-overrides execution semantics tests."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._creations: dict[str, _CreationRecord] = {}
        self._many: list[tuple[str, Any]] = []
        self._spellspace: dict[tuple[str, str], _CreationRecord] = {}
        self._conduit = _Conduit()

    def add_creation(
            self,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        self._creations[spell_id] = _CreationRecord(instance)

    def add_many_creations(
            self,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        self._many.append((spell_id, instance))

    def register_spellspace_creation(
            self,
            spellspace_id: str,
            spell_id: str,
            instance: Any,
            *,
            has_disposal_methods: bool,
            disposal_methods: Any,
    ) -> None:
        self._spellspace[(spellspace_id, spell_id)] = _CreationRecord(instance)

    def get_spellspace_creation(self, spellspace_id: str, spell_id: str) -> Any:
        return self._spellspace.get((spellspace_id, spell_id))


class _ExplodingLock:
    """Lock stub that fails if the emitted path tries to acquire spell lock."""

    def __enter__(self) -> "_ExplodingLock":
        raise AssertionError("spell lock should not be acquired for this path")

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


def _make_transient_schema() -> dict[str, object]:
    """Build a one-step transient schema row set for codegen-path tests."""
    return {
        "step_count": 1,
        "root_step_index": 0,
        "call_modes": (ExecutionPlanCallMode.CALL0,),
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
    }


def test_compile_phase12_no_overrides_executor_raises_on_transient_compile_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure transient source compile failures are hard-fail errors.

    Contract:
        - Invalid generated transient source raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: "def _phase12_executor(:\n    pass",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_schema, steps: {},
    )

    with pytest.raises(RuntimeError, match="code generation failed"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )


def test_compile_phase12_no_overrides_executor_raises_when_callable_missing(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure generated source must define the transient executor callable.

    Contract:
        - Missing `_phase12_executor` symbol raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: "x = 1",
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_executor_namespace",
        lambda transient_schema, steps: {},
    )

    with pytest.raises(RuntimeError, match="did not define a callable _phase12_executor"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )


def test_compile_phase12_no_overrides_executor_uses_emitted_step_source_when_transient_source_unavailable(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure transient-source misses still compile through emitted step source.

    Contract:
        - When transient source generation returns None, emitted step source is used.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_executor_source",
        lambda transient_schema: None,
    )

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_phase12_no_overrides_step_executor>"


def test_compile_phase12_no_overrides_executor_transient_uses_direct_call_path() -> None:
    """
    Transient executor stays on the direct emitted-call path.

    Contract:
        - The transient no-overrides executor does not depend on a separate
          native dispatcher seam.
        - Generated transient executors invoke the emitted direct-call path and
          still return the rooted result.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": _make_transient_schema(),
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_phase12_no_overrides_transient_executor>"
    assert executor() == "value:root"


def test_compile_phase12_no_overrides_executor_supports_steps_rows_schema() -> None:
    """
    Ensure schema-only step rows can be hydrated into executable plan steps.

    Contract:
        - `steps_rows` plus `spell_lookup` compiles into a callable executor.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert callable(executor)
    assert executor.__code__.co_filename == "<melder_phase12_no_overrides_step_executor>"


def test_compile_phase12_no_overrides_executor_delegates_to_shared_entry_input_compiler(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure the IR entrypoint routes through shared entry-input compilation.

    Contract:
        - `compile_phase12_no_overrides_executor(...)` delegates to
          `_compile_no_overrides_executor_from_entry_inputs(...)`.
        - Delegation includes entrypoint-specific missing-root error text.
    """
    captured: dict[str, Any] = {}
    expected_executor = lambda: None

    def _fake_shared_compile(
            *,
            steps: tuple[Any, ...],
            root_instance_key: Any,
            root_spell_id: Any,
            transient_schema: Any,
            missing_root_instance_key_message: str,
    ) -> Any:
        captured["steps"] = steps
        captured["root_instance_key"] = root_instance_key
        captured["root_spell_id"] = root_spell_id
        captured["transient_schema"] = transient_schema
        captured["missing_root_instance_key_message"] = missing_root_instance_key_message
        return expected_executor

    monkeypatch.setattr(
        phase12_module,
        "_compile_no_overrides_executor_from_entry_inputs",
        _fake_shared_compile,
    )

    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert executor is expected_executor
    assert len(captured["steps"]) == 1
    assert captured["steps"][0].instance_key == ("root", None)
    assert captured["root_instance_key"] is None
    assert captured["root_spell_id"] == "root"
    assert captured["transient_schema"] is None
    assert captured["missing_root_instance_key_message"] == (
        "Phase 12 IR is missing a resolvable root instance key."
    )


def test_compile_phase12_no_overrides_executor_from_plan_delegates_to_shared_entry_input_compiler(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Ensure plan entrypoint routes through shared entry-input compilation.

    Contract:
        - `compile_phase12_no_overrides_executor_from_plan(...)` delegates to
          `_compile_no_overrides_executor_from_entry_inputs(...)`.
        - Delegation includes entrypoint-specific missing-root error text.
    """
    captured: dict[str, Any] = {}
    expected_executor = lambda: None

    def _fake_shared_compile(
            *,
            steps: tuple[Any, ...],
            root_instance_key: Any,
            root_spell_id: Any,
            transient_schema: Any,
            missing_root_instance_key_message: str,
    ) -> Any:
        captured["steps"] = steps
        captured["root_instance_key"] = root_instance_key
        captured["root_spell_id"] = root_spell_id
        captured["transient_schema"] = transient_schema
        captured["missing_root_instance_key_message"] = missing_root_instance_key_message
        return expected_executor

    monkeypatch.setattr(
        phase12_module,
        "_compile_no_overrides_executor_from_entry_inputs",
        _fake_shared_compile,
    )

    plan = SimpleNamespace(
        steps=("step",),
        root_instance_key=("root", None),
        root_spell_id="root",
    )

    executor = phase12_module.compile_phase12_no_overrides_executor_from_plan(
        plan=plan,
        transient_schema={"step_count": 0, "root_step_index": 0},
    )

    assert executor is expected_executor
    assert captured["steps"] == ("step",)
    assert captured["root_instance_key"] == ("root", None)
    assert captured["root_spell_id"] == "root"
    assert captured["transient_schema"] == {"step_count": 0, "root_step_index": 0}
    assert captured["missing_root_instance_key_message"] == (
        "Phase 12 plan is missing a resolvable root instance key."
    )


def test_compile_no_overrides_executor_from_entry_inputs_resolves_missing_root_key() -> None:
    """
    Shared entry-input helper resolves root key from root spell id fallback.

    Contract:
        - Missing root instance key resolves through `_resolve_root_instance_key`.
        - Resolved key is forwarded into the shared compile path.
    """
    captured: dict[str, Any] = {}
    expected_executor = lambda: None

    def _fake_compile_from_steps(
            *,
            steps: tuple[Any, ...],
            root_instance_key: Any,
            transient_schema: Any,
    ) -> Any:
        captured["steps"] = steps
        captured["root_instance_key"] = root_instance_key
        captured["transient_schema"] = transient_schema
        return expected_executor

    original_compile_from_steps = phase12_module._compile_no_overrides_executor_from_steps
    phase12_module._compile_no_overrides_executor_from_steps = _fake_compile_from_steps
    try:
        result = phase12_module._compile_no_overrides_executor_from_entry_inputs(
            steps=(SimpleNamespace(instance_key=("root", None)),),
            root_instance_key=None,
            root_spell_id="root",
            transient_schema=None,
            missing_root_instance_key_message="missing root key",
        )
    finally:
        phase12_module._compile_no_overrides_executor_from_steps = original_compile_from_steps

    assert result is expected_executor
    assert captured["root_instance_key"] == ("root", None)
    assert captured["transient_schema"] is None


def test_compile_no_overrides_executor_from_entry_inputs_raises_with_entry_message() -> None:
    """
    Shared entry-input helper preserves caller-specific root-resolution errors.

    Contract:
        - Missing fallback root resolution raises RuntimeError with the caller
          message provided by the entrypoint.
    """
    with pytest.raises(RuntimeError, match="entrypoint root message"):
        phase12_module._compile_no_overrides_executor_from_entry_inputs(
            steps=(SimpleNamespace(instance_key=("other", None)),),
            root_instance_key=None,
            root_spell_id="root",
            transient_schema=None,
            missing_root_instance_key_message="entrypoint root message",
        )


def test_compile_phase12_no_overrides_executor_inlines_creations_target_routing() -> None:
    """
    Ensure emitted step executors route creations targets without helper dispatch.

    Contract:
        - Generated code does not reference `_select_creations_for_target_kind`.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert "_select_creations_for_target_kind" not in executor.__code__.co_names


def test_compile_phase12_no_overrides_executor_prebinds_step_existences() -> None:
    """
    Ensure emitted step executors prebind required per-step metadata.

    Contract:
        - Generated executor defaults include `step_existences`.
        - Generated executor no longer prebinds per-step creations target kinds.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir=codegen_ir,
        spell_lookup={"root": _make_spell("root")},
    )

    assert "step_spells" in executor.__code__.co_varnames
    assert "step_existences" in executor.__code__.co_varnames
    assert "step_instance_keys" in executor.__code__.co_varnames
    assert "step_creations_target_kinds" not in executor.__code__.co_varnames


def test_compile_phase12_no_overrides_executor_requires_spell_lookup_for_steps_rows() -> None:
    """
    Ensure schema-only step rows fail fast when spell lookup is missing.

    Contract:
        - Missing spell_lookup with `steps_rows` raises RuntimeError.
    """
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": None,
    }

    with pytest.raises(RuntimeError, match="require spell_lookup"):
        phase12_module.compile_phase12_no_overrides_executor(codegen_ir=codegen_ir)


def test_compile_phase12_no_overrides_executor_rejects_invalid_transient_schema() -> None:
    """Malformed transient schema fails fast before transient code generation."""
    codegen_ir = {
        "steps_rows": (_make_step_row("root"),),
        "root_spell_id": "root",
        "transient_schema": {"step_count": 1},
    }

    with pytest.raises(RuntimeError, match="missing required field 'root_step_index'"):
        phase12_module.compile_phase12_no_overrides_executor(
            codegen_ir=codegen_ir,
            spell_lookup={"root": _make_spell("root")},
        )


def test_compile_phase12_no_overrides_executor_reuses_spellspace_singleton_from_emitted_path() -> None:
    """
    Spellspace existence route reuses an active spellspace singleton.

    Contract:
        - First execution constructs and registers spellspace creation.
        - Second execution reuses existing spellspace creation.
    """
    creations = _Creations()
    creations._conduit._active_spellspace = _Spellspace("space-1", creations._conduit)
    call_counter = {"value": 0}

    def _build_root() -> str:
        call_counter["value"] += 1
        return "root-instance"

    spell = _make_spell("root")
    spell.existence = Existence.unique_per_spell_space
    spell.spell = _build_root
    row = _make_step_row("root")
    row["existence"] = "unique_per_spell_space"
    row["creations_target_kind"] = ExecutionPlanTargetKind.SPELLSPACE
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "root-instance"
    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "root-instance"
    assert call_counter["value"] == 1


def test_compile_phase12_no_overrides_executor_requires_active_spellspace_for_spellspace_existence() -> None:
    """
    Spellspace existence route fails fast when no active spellspace exists.
    """
    creations = _Creations()
    spell = _make_spell("root")
    spell.existence = Existence.unique_per_spell_space
    row = _make_step_row("root")
    row["existence"] = "unique_per_spell_space"
    row["creations_target_kind"] = ExecutionPlanTargetKind.SPELLSPACE
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    with pytest.raises(SpellSpaceScopeError, match="requires an active SpellSpace"):
        executor(
            caller_creations=context.caller_creations,
            owner_creations=context.owner_creations,
            caller_creations_lock_held=context.caller_creations_lock_held,
        )


def test_compile_phase12_no_overrides_executor_skips_spell_lock_when_caller_lock_is_held() -> None:
    """
    Emitted unique route suppresses spell lock when caller creations lock is held.
    """
    creations = _Creations()
    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell._lock = _ExplodingLock()
    row = _make_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.CALLER
    row["use_spell_lock_hint"] = True
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=True,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "value:root"


def test_compile_phase12_no_overrides_executor_existing_hit_skips_spell_and_creations_locks() -> None:
    """
    Existing shared-instance hits skip spell/creations lock acquisition.
    """
    creations = _Creations()
    creations._lock = _ExplodingLock()
    creations._creations["root"] = _CreationRecord("existing-root")
    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell._lock = _ExplodingLock()
    row = _make_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.CALLER
    row["use_spell_lock_hint"] = True
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "existing-root"


def test_compile_phase12_no_overrides_executor_existing_hit_skips_creations_lock_without_spell_hint() -> None:
    """
    Existing shared-instance hits skip creations lock when spell-lock hint is disabled.
    """
    creations = _Creations()
    creations._lock = _ExplodingLock()
    creations._creations["root"] = _CreationRecord("existing-root")
    spell = _make_spell("root")
    spell.existence = Existence.unique
    row = _make_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.CALLER
    row["use_spell_lock_hint"] = False
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "existing-root"


@pytest.mark.parametrize(
    "existence_name,target_kind,must_register,has_disposal,expect_reuse,expect_many_count,activate_spellspace",
    (
        (
            "unique",
            ExecutionPlanTargetKind.CALLER,
            True,
            False,
            True,
            0,
            False,
        ),
        (
            "unique_per_conduit",
            ExecutionPlanTargetKind.CALLER,
            True,
            False,
            True,
            0,
            False,
        ),
        (
            "many",
            ExecutionPlanTargetKind.CALLER,
            False,
            False,
            False,
            0,
            False,
        ),
        (
            "many",
            ExecutionPlanTargetKind.CALLER,
            True,
            True,
            False,
            2,
            False,
        ),
        (
            "unique_per_spell_space",
            ExecutionPlanTargetKind.SPELLSPACE,
            True,
            False,
            True,
            0,
            True,
        ),
    ),
)
def test_compile_phase12_no_overrides_executor_existence_matrix(
        existence_name: str,
        target_kind: int,
        must_register: bool,
        has_disposal: bool,
        expect_reuse: bool,
        expect_many_count: int,
        activate_spellspace: bool,
) -> None:
    """
    Generated no-overrides executor preserves existence semantics across scopes.

    Contract:
        - Shared scopes reuse existing creations after first registration.
        - Existence.many constructs each call.
        - many-registration only writes to many-creation storage when disposal exists.
        - Spellspace target path reuses active spellspace registrations.
    """
    creations = _Creations()
    if activate_spellspace:
        creations._conduit._active_spellspace = _Spellspace("space-1", creations._conduit)
    call_counter = {"value": 0}

    def _build_root() -> str:
        call_counter["value"] += 1
        return "root-instance-{0}".format(call_counter["value"])

    spell = _make_spell("root")
    spell.spell = _build_root
    spell.existence = Existence[existence_name]
    spell.has_disposal_methods = has_disposal
    spell.disposal_method_names = ("cleanup",) if has_disposal else ()
    row = _make_step_row("root")
    row["existence"] = existence_name
    row["creations_target_kind"] = target_kind
    row["must_register"] = must_register

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    first = executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )
    second = executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )
    if expect_reuse:
        assert first == second
        assert call_counter["value"] == 1
    else:
        assert first != second
        assert call_counter["value"] == 2
    assert len(creations._many) == expect_many_count


def test_compile_phase12_no_overrides_executor_owner_target_prefers_spell_owner_creations() -> None:
    """
    OWNER target routes registration through spell-owned creations when available.
    """
    caller_creations = _Creations()
    context_owner_creations = _Creations()
    spell_owner_creations = _Creations()
    call_counter = {"value": 0}

    def _build_root() -> str:
        call_counter["value"] += 1
        return "owner-instance"

    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell.spell = _build_root
    spell._owner_creations = spell_owner_creations
    row = _make_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.OWNER
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=caller_creations,
        owner_creations=context_owner_creations,
        caller_creations_lock_held=False,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "owner-instance"
    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "owner-instance"
    assert call_counter["value"] == 1
    assert "root" in spell_owner_creations._creations
    assert "root" not in context_owner_creations._creations
    assert "root" not in caller_creations._creations


def test_compile_phase12_no_overrides_executor_owner_target_falls_back_to_context_owner_creations() -> None:
    """
    OWNER target uses context owner_creations when spell owner-creations is absent.
    """
    caller_creations = _Creations()
    context_owner_creations = _Creations()

    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell._owner_creations = None
    row = _make_step_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.OWNER
    row["must_register"] = True

    executor = phase12_module.compile_phase12_no_overrides_executor(
        codegen_ir={
            "steps_rows": (row,),
            "root_spell_id": "root",
            "transient_schema": None,
        },
        spell_lookup={"root": spell},
    )
    context = SimpleNamespace(
        caller_creations=caller_creations,
        owner_creations=context_owner_creations,
        caller_creations_lock_held=False,
    )

    assert executor(
        caller_creations=context.caller_creations,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    ) == "value:root"
    assert "root" in context_owner_creations._creations
    assert "root" not in caller_creations._creations


def test_build_kwargs_no_overrides_fast_path_returns_empty_dict() -> None:
    """No-overrides kwargs helper fast path returns empty kwargs for empty call recipe."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={},
    )

    assert kwargs == {}


def test_build_kwargs_no_overrides_contract_payload_only_returns_copy() -> None:
    """No-overrides kwargs helper returns a copy for contract-payload-only steps."""
    contract_payload = {"value": "contract"}
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload=contract_payload,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={},
    )

    assert kwargs == {"value": "contract"}
    assert kwargs is not contract_payload


def test_build_kwargs_no_overrides_contract_payload_only_filters_args_key() -> None:
    """No-overrides contract-only fast path filters `__args__` when positional override is enabled."""
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload={
            "__args__": ("contract-arg",),
            "value": "contract",
        },
        uses_positional_override=True,
    )

    kwargs = phase12_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={},
    )

    assert kwargs == {"value": "contract"}


def test_build_kwargs_no_overrides_single_and_multi_dependency_shapes() -> None:
    """No-overrides kwargs helper maps one dependency to scalar and many to list."""
    dep_key_one = ("dep-a", None)
    dep_key_two = ("dep-b", None)
    dep_key_three = ("dep-c", None)
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(
            ("single", (dep_key_one,)),
            ("multi", (dep_key_two, dep_key_three)),
        ),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={
            dep_key_one: "v1",
            dep_key_two: "v2",
            dep_key_three: "v3",
        },
    )

    assert kwargs == {
        "single": "v1",
        "multi": ["v2", "v3"],
    }


def test_build_kwargs_no_overrides_two_dependency_fast_path_skips_iteration() -> None:
    """No-overrides kwargs helper resolves two dependencies without sequence iteration."""
    first_dependency_key = ("dep-a", None)
    second_dependency_key = ("dep-b", None)

    class _TwoDependencyKeys:
        """Two-key sequence that fails if fallback iteration path is used."""

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
        dependency_resolution_order=(
            ("multi", _TwoDependencyKeys()),
        ),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_no_overrides(
        plan_step=plan_step,
        instance_results={
            first_dependency_key: "v1",
            second_dependency_key: "v2",
        },
    )

    assert kwargs == {
        "multi": ["v1", "v2"],
    }


def test_construct_spell_instance_rejects_invalid_positional_payload() -> None:
    """No-overrides construct helper rejects invalid non-sequence positional payloads."""
    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = lambda **kwargs: kwargs
    plan_step = SimpleNamespace(
        spell=spell,
        dependency_resolution_order=(),
        contract_positional_override="bad-args",
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    with pytest.raises(phase12_module.MeldExecutionError, match="__args__ override must be a list or tuple"):
        phase12_module._construct_spell_instance(
            plan_step=plan_step,
            instance_results={},
        )


def test_construct_spell_instance_accepts_tuple_positional_payload() -> None:
    """No-overrides construct helper accepts tuple positional payloads for invocation."""
    captured: Dict[str, Any] = {}

    def _callable(*args: Any, **kwargs: Any) -> str:
        captured["args"] = args
        captured["kwargs"] = dict(kwargs)
        return "ok"

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    tuple_payload = ("left", "right")
    plan_step = SimpleNamespace(
        spell=spell,
        dependency_resolution_order=(),
        contract_positional_override=tuple_payload,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=True,
    )

    result = phase12_module._construct_spell_instance(
        plan_step=plan_step,
        instance_results={},
    )

    assert result == "ok"
    assert captured["args"] == tuple_payload
    assert captured["kwargs"] == {}
    assert plan_step.contract_positional_override == tuple_payload

def test_normalize_transient_schema_normalizes_and_validates() -> None:
    """Transient schema normalization returns tuples and rejects malformed payloads."""
    normalized = phase12_module._normalize_transient_schema(
        transient_schema=_make_transient_schema(),
    )

    assert normalized["step_count"] == 1
    assert normalized["root_step_index"] == 0
    assert isinstance(normalized["call_modes"], tuple)
    assert isinstance(normalized["dep1"], tuple)

    bad_schema = _make_transient_schema()
    del bad_schema["dep1"]
    with pytest.raises(RuntimeError, match="missing required field 'dep1'"):
        phase12_module._normalize_transient_schema(transient_schema=bad_schema)

    bad_length_schema = _make_transient_schema()
    bad_length_schema["dep1"] = ()
    with pytest.raises(RuntimeError, match="length must equal step_count"):
        phase12_module._normalize_transient_schema(transient_schema=bad_length_schema)


def test_supports_transient_unrolled_plan_requires_many_and_no_registration() -> None:
    """Transient unrolled plans require many-existence and no registration."""
    assert phase12_module._supports_transient_unrolled_plan(
        (
            SimpleNamespace(existence=Existence.many, must_register=False),
            SimpleNamespace(existence=Existence.many, must_register=False),
        )
    ) is True
    assert phase12_module._supports_transient_unrolled_plan(
        (
            SimpleNamespace(existence=Existence.unique, must_register=False),
        )
    ) is False
    assert phase12_module._supports_transient_unrolled_plan(
        (
            SimpleNamespace(existence=Existence.many, must_register=True),
        )
    ) is False


def test_unrolled_call_helpers_cover_supported_and_unsupported_modes() -> None:
    """Unrolled transient call helpers handle trivial modes and reject unsupported ones."""
    arg_refs = phase12_module._build_unrolled_call_arg_refs(
        step_index=0,
        call_mode=ExecutionPlanCallMode.CALL2,
        transient_dep1=(-1,),
        transient_dep2a=(1,),
        transient_dep2b=(2,),
        transient_dep3a=(-1,),
        transient_dep3b=(-1,),
        transient_dep3c=(-1,),
        transient_dep4a=(-1,),
        transient_dep4b=(-1,),
        transient_dep4c=(-1,),
        transient_dep4d=(-1,),
        transient_dep5a=(-1,),
        transient_dep5b=(-1,),
        transient_dep5c=(-1,),
        transient_dep5d=(-1,),
        transient_dep5e=(-1,),
        transient_dep6a=(-1,),
        transient_dep6b=(-1,),
        transient_dep6c=(-1,),
        transient_dep6d=(-1,),
        transient_dep6e=(-1,),
        transient_dep6f=(-1,),
        transient_dep7a=(-1,),
        transient_dep7b=(-1,),
        transient_dep7c=(-1,),
        transient_dep7d=(-1,),
        transient_dep7e=(-1,),
        transient_dep7f=(-1,),
        transient_dep7g=(-1,),
        transient_dep8a=(-1,),
        transient_dep8b=(-1,),
        transient_dep8c=(-1,),
        transient_dep8d=(-1,),
        transient_dep8e=(-1,),
        transient_dep8f=(-1,),
        transient_dep8g=(-1,),
        transient_dep8h=(-1,),
    )

    assert arg_refs == ("v1", "v2")
    assert phase12_module._build_unrolled_call_expression(
        step_index=0,
        call_mode=ExecutionPlanCallMode.CALL0,
        transient_dep1=(-1,),
        transient_dep2a=(1,),
        transient_dep2b=(2,),
        transient_dep3a=(-1,),
        transient_dep3b=(-1,),
        transient_dep3c=(-1,),
        transient_dep4a=(-1,),
        transient_dep4b=(-1,),
        transient_dep4c=(-1,),
        transient_dep4d=(-1,),
        transient_dep5a=(-1,),
        transient_dep5b=(-1,),
        transient_dep5c=(-1,),
        transient_dep5d=(-1,),
        transient_dep5e=(-1,),
        transient_dep6a=(-1,),
        transient_dep6b=(-1,),
        transient_dep6c=(-1,),
        transient_dep6d=(-1,),
        transient_dep6e=(-1,),
        transient_dep6f=(-1,),
        transient_dep7a=(-1,),
        transient_dep7b=(-1,),
        transient_dep7c=(-1,),
        transient_dep7d=(-1,),
        transient_dep7e=(-1,),
        transient_dep7f=(-1,),
        transient_dep7g=(-1,),
        transient_dep8a=(-1,),
        transient_dep8b=(-1,),
        transient_dep8c=(-1,),
        transient_dep8d=(-1,),
        transient_dep8e=(-1,),
        transient_dep8f=(-1,),
        transient_dep8g=(-1,),
        transient_dep8h=(-1,),
    ) == "t0()"
    assert phase12_module._build_unrolled_call_arg_refs(
        step_index=0,
        call_mode=ExecutionPlanCallMode.CALLN,
        transient_dep1=(-1,),
        transient_dep2a=(1,),
        transient_dep2b=(2,),
        transient_dep3a=(-1,),
        transient_dep3b=(-1,),
        transient_dep3c=(-1,),
        transient_dep4a=(-1,),
        transient_dep4b=(-1,),
        transient_dep4c=(-1,),
        transient_dep4d=(-1,),
        transient_dep5a=(-1,),
        transient_dep5b=(-1,),
        transient_dep5c=(-1,),
        transient_dep5d=(-1,),
        transient_dep5e=(-1,),
        transient_dep6a=(-1,),
        transient_dep6b=(-1,),
        transient_dep6c=(-1,),
        transient_dep6d=(-1,),
        transient_dep6e=(-1,),
        transient_dep6f=(-1,),
        transient_dep7a=(-1,),
        transient_dep7b=(-1,),
        transient_dep7c=(-1,),
        transient_dep7d=(-1,),
        transient_dep7e=(-1,),
        transient_dep7f=(-1,),
        transient_dep7g=(-1,),
        transient_dep8a=(-1,),
        transient_dep8b=(-1,),
        transient_dep8c=(-1,),
        transient_dep8d=(-1,),
        transient_dep8e=(-1,),
        transient_dep8f=(-1,),
        transient_dep8g=(-1,),
        transient_dep8h=(-1,),
    ) is None


def test_resolve_transient_targets_validates_step_count_and_callable_steps() -> None:
    """Transient target resolution enforces step-count and callable-step contracts."""
    callable_step = SimpleNamespace(
        spell=SimpleNamespace(
            is_class_spell=True,
            is_method_spell=False,
            is_lambda_spell=False,
            spell=lambda: "ok",
        )
    )

    assert phase12_module._resolve_transient_targets(
        steps=(callable_step,),
        transient_step_count=1,
    ) == (callable_step.spell.spell,)

    with pytest.raises(RuntimeError, match="step_count does not match hydrated steps"):
        phase12_module._resolve_transient_targets(
            steps=(callable_step,),
            transient_step_count=2,
        )

    non_callable_step = SimpleNamespace(
        spell=SimpleNamespace(
            is_class_spell=False,
            is_method_spell=False,
            is_lambda_spell=False,
            spell="not-callable",
        )
    )
    with pytest.raises(RuntimeError, match="requires callable steps"):
        phase12_module._resolve_transient_targets(
            steps=(non_callable_step,),
            transient_step_count=1,
        )
