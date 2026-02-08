"""Contract tests for Phase12 override specialization compiler."""

import threading
from types import SimpleNamespace
from typing import Any, Dict

import pytest

import melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor as phase12_module
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import ExecutionPlanTargetKind
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    compile_phase12_overrides_executor,
    compile_phase12_overrides_executor_from_source,
    emit_phase12_overrides_executor_source,
)
from melder.utilities.custom_exceptions.meld_execution_error import MeldExecutionError


def _make_spell(spell_id: str) -> Any:
    """Build a minimal spell stub for schema-row override compiler tests."""
    return SimpleNamespace(
        spell_id=spell_id,
        spell_name=spell_id,
        spell_index=SimpleNamespace(current=spell_id),
        existence=Existence.many,
        is_existing_creation=False,
        is_class_spell=False,
        is_method_spell=False,
        is_lambda_spell=False,
        spell=f"value:{spell_id}",
        _owner_creations=None,
        _lock=threading.RLock(),
        has_disposal_methods=False,
        disposal_method_names=(),
    )


def _make_plan_row(spell_id: str) -> Dict[str, Any]:
    """Build a minimal schema step row accepted by override compiler hydration."""
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


class _SocketKind:
    """Socket kind value wrapper for override map keys."""

    def __init__(self, value: str) -> None:
        self.value = value


class _SocketRef:
    """Hashable socket ref used to drive override substitution in tests."""

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


class _CreationRecord:
    """Container matching creations registry record contract."""

    def __init__(self, value: Any) -> None:
        self.value = value


class _Creations:
    """Creations stub used by override emitted-route semantics tests."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._creations: dict[str, _CreationRecord] = {}
        self._spellspace: dict[tuple[str, str], _CreationRecord] = {}
        self._conduit = SimpleNamespace(get_active_spellspace=lambda: None)

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
        self._creations[spell_id] = _CreationRecord(instance)

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


def test_compile_phase12_overrides_executor_requires_spell_lookup_for_schema_rows() -> None:
    """Schema-row override compile fails fast when spell lookup is missing."""
    with pytest.raises(RuntimeError, match="require spell_lookup"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup=None,
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_schema_rows_missing_required_field() -> None:
    """Schema-row override compile fails fast for missing required row fields."""
    row = _make_plan_row("root")
    row.pop("instance_key")
    with pytest.raises(RuntimeError, match="missing required field 'instance_key'"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_unknown_spell_id_in_schema_rows() -> None:
    """Schema-row override compile fails when spell lookup cannot resolve a row spell id."""
    with pytest.raises(RuntimeError, match="unknown spell_id 'root'"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup={},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_rejects_unknown_existence_name() -> None:
    """Schema-row override compile fails for unknown existence enum names."""
    row = _make_plan_row("root")
    row["existence"] = "not_an_existence"
    with pytest.raises(RuntimeError, match="unknown existence"):
        compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(row,),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_supports_schema_rows_execution() -> None:
    """Schema-row override compile path emits a callable executor that executes."""
    spell = _make_spell("root")
    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )
    assert executor.__code__.co_filename == "<melder_phase12_overrides_executor>"
    assert "_resolve_step_instance_with_overrides" not in executor.__code__.co_names

    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )
    result = executor(context, {}, None)

    assert result == "value:root"


def test_compile_phase12_overrides_executor_inlines_creations_target_routing() -> None:
    """Generated override source does not call creations-target helper dispatch."""
    spell = _make_spell("root")
    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )
    assert "_select_creations_for_target_kind" not in executor.__code__.co_names


def test_compile_phase12_overrides_executor_from_source_supports_schema_rows_execution() -> None:
    """Source-restored compile path emits a callable executor that executes."""
    spell = _make_spell("root")
    source = emit_phase12_overrides_executor_source(step_count=1)
    executor = compile_phase12_overrides_executor_from_source(
        source=source,
        execution_plan=None,
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=False,
        path_registry=None,
    )
    assert executor.__code__.co_filename == "<melder_phase12_overrides_executor>"
    assert "_resolve_step_instance_with_overrides" not in executor.__code__.co_names

    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )
    result = executor(context, {}, None)
    assert result == "value:root"


def test_emit_phase12_overrides_executor_source_rejects_negative_step_count() -> None:
    """Source emitter enforces non-negative step counts."""
    with pytest.raises(ValueError, match="step_count must not be negative"):
        emit_phase12_overrides_executor_source(step_count=-1)


def test_compile_phase12_overrides_executor_raises_on_codegen_error(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Compilation fails fast when generated source cannot compile."""
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_overrides_executor_source",
        lambda step_count: "def _phase12_executor(:\n    pass",
    )

    with pytest.raises(RuntimeError, match="code generation failed"):
        phase12_module.compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_raises_when_callable_missing(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Compilation fails when generated source omits `_phase12_executor`."""
    monkeypatch.setattr(
        phase12_module,
        "_build_phase12_overrides_executor_source",
        lambda step_count: "x = 1",
    )

    with pytest.raises(RuntimeError, match="did not define a callable _phase12_executor"):
        phase12_module.compile_phase12_overrides_executor(
            execution_plan=None,
            plan_rows=(_make_plan_row("root"),),
            root_spell_id="root",
            spell_lookup={"root": _make_spell("root")},
            override_targets_by_spell_id={},
            any_overrides_present=False,
            path_registry=None,
        )


def test_compile_phase12_overrides_executor_contract_and_root_override_precedence() -> None:
    """
    Root positional overrides and socket overrides outrank contract payload defaults.
    """
    captured: Dict[str, Any] = {}

    def _callable(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {"args": args, "kwargs": kwargs}

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable

    row = _make_plan_row("root")
    row["uses_positional_override"] = True
    row["contract_positional_override"] = ("contract-positional",)
    row["has_contract_payload"] = True
    row["contract_payload_items"] = (
        ("value", "contract-value"),
        ("__args__", ("contract-args",)),
    )

    socket_ref = _SocketRef("root", "value", 7, "normal")
    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={"root": (socket_ref,)},
        any_overrides_present=True,
        path_registry=None,
    )

    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )
    result = executor(
        context,
        {socket_ref: "override-value"},
        ("runtime-positional",),
    )

    assert result["args"] == ("runtime-positional",)
    assert result["kwargs"]["value"] == "override-value"
    assert captured["args"] == ("runtime-positional",)
    assert captured["kwargs"]["value"] == "override-value"


def test_compile_phase12_overrides_executor_rejects_root_override_on_existing_shared_instance() -> None:
    """
    Root-level override payloads reject reuse of an existing shared root instance.
    """
    creations = _Creations()
    creations._creations["root"] = _CreationRecord("existing-root")
    spell = _make_spell("root")
    spell.existence = Existence.unique
    spell._owner_creations = creations
    row = _make_plan_row("root")
    row["existence"] = "unique"
    row["creations_target_kind"] = ExecutionPlanTargetKind.OWNER

    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={},
        any_overrides_present=True,
        path_registry=None,
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    with pytest.raises(MeldExecutionError, match="root spell that already exists"):
        executor(context, {}, ("arg",))


def test_compile_phase12_overrides_executor_rejects_targeted_override_on_existing_instance() -> None:
    """
    Targeted socket overrides reject reuse of an existing shared instance.
    """
    creations = _Creations()
    creations._creations["dep"] = _CreationRecord("existing-dep")
    root_spell = _make_spell("root")
    dep_spell = _make_spell("dep")
    dep_spell.existence = Existence.unique_per_conduit
    root_row = _make_plan_row("root")
    dep_row = _make_plan_row("dep")
    dep_row["existence"] = "unique_per_conduit"
    dep_row["creations_target_kind"] = ExecutionPlanTargetKind.CALLER
    socket_ref = _SocketRef("dep", "value", 11, "normal")

    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(root_row, dep_row),
        root_spell_id="root",
        spell_lookup={"root": root_spell, "dep": dep_spell},
        override_targets_by_spell_id={"dep": (socket_ref,)},
        any_overrides_present=True,
        path_registry=None,
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        executor(context, {socket_ref: "override"}, None)


def test_compile_phase12_overrides_executor_rejects_targeted_override_on_existing_spellspace_instance() -> None:
    """
    Spellspace-scoped targeted overrides reject reuse of existing spellspace instances.
    """
    creations = _Creations()
    active_conduit = SimpleNamespace()
    active_spellspace = SimpleNamespace(
        id="space-1",
        owner_conduit=active_conduit,
    )
    active_conduit.get_active_spellspace = lambda: active_spellspace
    creations._conduit = active_conduit
    creations._spellspace[(active_spellspace.id, "dep")] = _CreationRecord("existing-dep")

    root_spell = _make_spell("root")
    dep_spell = _make_spell("dep")
    dep_spell.existence = Existence.unique_per_spell_space
    root_row = _make_plan_row("root")
    dep_row = _make_plan_row("dep")
    dep_row["existence"] = "unique_per_spell_space"
    dep_row["creations_target_kind"] = ExecutionPlanTargetKind.SPELLSPACE
    socket_ref = _SocketRef("dep", "value", 12, "normal")

    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(root_row, dep_row),
        root_spell_id="root",
        spell_lookup={"root": root_spell, "dep": dep_spell},
        override_targets_by_spell_id={"dep": (socket_ref,)},
        any_overrides_present=True,
        path_registry=None,
    )
    context = SimpleNamespace(
        caller_creations=creations,
        owner_creations=creations,
        caller_creations_lock_held=False,
    )

    with pytest.raises(MeldExecutionError, match="spell instance that already exists"):
        executor(context, {socket_ref: "override"}, None)
