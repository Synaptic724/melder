"""Contract tests for Phase12 override specialization compiler."""

import threading
from types import SimpleNamespace
from typing import Any, Dict, Tuple

import pytest

import melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor as phase12_module
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.blueprints.execution_plan import ExecutionPlanTargetKind
from melder.spellbook.spell_crafter.blueprints.phase12_overrides_executor import (
    build_phase12_override_step_target_counts_from_rows,
    compile_phase12_overrides_executor_code_object,
    compile_phase12_overrides_executor_from_code_object,
    compile_phase12_overrides_executor,
    compile_phase12_overrides_executor_from_source,
    emit_phase12_overrides_executor_source,
    emit_phase12_overrides_executor_shape_source,
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


class _TrackingPathRegistry:
    """Path registry stub that tracks parent/depth calls for filtering tests."""

    def __init__(
            self,
            parent_map: Dict[int, Any],
            depth_map: Dict[int, Any],
    ) -> None:
        self._parent_map = parent_map
        self._depth_map = depth_map
        self.parent_calls = 0
        self.depth_calls = 0
        self.raise_on_access = False

    def parent_id(self, path_id: int) -> Any:
        if self.raise_on_access:
            raise AssertionError("parent_id should not be called during runtime execution.")
        self.parent_calls += 1
        return self._parent_map.get(path_id)

    def depth(self, path_id: int) -> Any:
        if self.raise_on_access:
            raise AssertionError("depth should not be called during runtime execution.")
        self.depth_calls += 1
        return self._depth_map.get(path_id)


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
    result = executor(
        context.caller_creations,
        {},
        None,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )

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


def test_compile_phase12_overrides_executor_prebinds_step_metadata() -> None:
    """Generated override source prebinds step metadata tuples for hot-path access."""
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
    assert "step_spells" in executor.__code__.co_varnames
    assert "step_existences" in executor.__code__.co_varnames
    assert "step_instance_keys" in executor.__code__.co_varnames
    assert "step_use_spell_lock_hints" in executor.__code__.co_varnames
    assert "step_has_targeted_overrides" in executor.__code__.co_varnames
    assert "step_must_register_flags" in executor.__code__.co_varnames


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
    result = executor(
        context.caller_creations,
        {},
        None,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )
    assert result == "value:root"


def test_compile_phase12_overrides_executor_code_object_rejects_empty_source() -> None:
    """Code-object helper requires non-empty emitted source."""
    with pytest.raises(ValueError, match="source must be a non-empty string"):
        compile_phase12_overrides_executor_code_object(source="")


def test_compile_phase12_overrides_executor_from_code_object_supports_schema_rows_execution() -> None:
    """Code-object compile path emits a callable executor that executes."""
    spell = _make_spell("root")
    source = emit_phase12_overrides_executor_source(step_count=1)
    code_object = compile_phase12_overrides_executor_code_object(source=source)
    executor = compile_phase12_overrides_executor_from_code_object(
        code_object=code_object,
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
    result = executor(
        context.caller_creations,
        {},
        None,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )
    assert result == "value:root"


def test_emit_phase12_overrides_executor_source_rejects_negative_step_count() -> None:
    """Source emitter enforces non-negative step counts."""
    with pytest.raises(ValueError, match="step_count must not be negative"):
        emit_phase12_overrides_executor_source(step_count=-1)


def test_emit_phase12_overrides_executor_shape_source_rejects_missing_required_field() -> None:
    """Shape emitter fails fast when required row fields are missing."""
    row = _make_plan_row("root")
    row.pop("must_register")

    with pytest.raises(RuntimeError, match="missing required field 'must_register'"):
        emit_phase12_overrides_executor_shape_source(
            plan_rows=(row,),
            root_spell_id="root",
        )


def test_emit_phase12_overrides_executor_shape_source_rejects_unknown_existence_name() -> None:
    """Shape emitter fails fast when row existence names are invalid."""
    row = _make_plan_row("root")
    row["existence"] = "not_an_existence"

    with pytest.raises(RuntimeError, match="unknown existence"):
        emit_phase12_overrides_executor_shape_source(
            plan_rows=(row,),
            root_spell_id="root",
        )


def test_emit_phase12_overrides_executor_shape_source_specializes_target_and_existence() -> None:
    """Shape emitter removes runtime target/existence selection from emitted source."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
    )

    assert "step_creations_target_kinds" not in source
    assert "step_existences" not in source
    assert "if target_kind_0 in (" not in source
    assert "existence_0 = step_existences[0]" not in source
    assert "step_root_positional_override_0 = root_positional_override" not in source
    assert "step_root_positional_override_0 = None" not in source


def test_emit_phase12_overrides_executor_shape_source_prebinds_non_root_override_to_none() -> None:
    """Shape emitter elides positional locals when root positional overrides are impossible."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("dep"),),
        root_spell_id="root",
    )

    assert "step_root_positional_override_0 = None" not in source
    assert "root_positional_override if is_root_step_0 else None" not in source


def test_emit_phase12_overrides_executor_shape_source_static_spell_flags_elide_dynamic_invoke_branches() -> None:
    """Shape emitter uses spell lookup metadata to remove dynamic invoke-type branching."""
    row = _make_plan_row("root")
    spell = _make_spell("root")
    spell.is_class_spell = True

    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
    )

    assert "is_callable_spell_0 = step_is_callable_spell[0]" not in source
    assert "if is_callable_spell_0:" not in source
    assert "if is_existing_unique_creation_0:" not in source


def test_emit_phase12_overrides_executor_shape_source_specializes_static_target_count() -> None:
    """Shape emitter removes dynamic override-target-count branching for static shapes."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        override_targeted_spell_ids=("root",),
        override_target_counts_by_spell_id=(("root", 1),),
    )

    assert "override_target_count_0 = step_override_target_counts[0]" not in source
    assert "if override_target_count_0 == 0:" not in source


def test_emit_phase12_overrides_executor_shape_source_duplicate_spell_id_skips_static_count_specialization() -> None:
    """Shape emitter avoids fixed [0] indexing lanes when one spell_id maps to multiple steps."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(
            _make_plan_row("dup"),
            _make_plan_row("dup"),
        ),
        root_spell_id="dup",
        override_targeted_spell_ids=("dup",),
        override_target_counts_by_spell_id=(("dup", 1),),
    )

    assert "single_override_socket_0 = override_targets_0[0]" not in source
    assert "single_override_socket_1 = override_targets_1[0]" not in source
    assert "for override_socket_0 in override_targets_0:" in source
    assert "for override_socket_1 in override_targets_1:" in source


def test_emit_phase12_overrides_executor_shape_source_uses_per_step_target_counts_when_provided() -> None:
    """Shape emitter can specialize duplicate spell_id rows safely with per-step counts."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(
            _make_plan_row("dup"),
            _make_plan_row("dup"),
        ),
        root_spell_id="dup",
        override_targeted_spell_ids=("dup",),
        override_target_counts_by_spell_id=(("dup", 1),),
        override_target_counts_by_step=(1, 0),
    )

    assert "single_override_socket_0 = override_targets_0[0]" in source
    assert "single_override_socket_1 = override_targets_1[0]" not in source
    assert "override_values_1 = _EMPTY_OVERRIDE_VALUES" in source


def test_emit_phase12_overrides_executor_shape_source_inlines_many_registration() -> None:
    """Shape emitter inlines Existence.many registration when must_register is true."""
    row = _make_plan_row("root")
    row["must_register"] = True

    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(row,),
        root_spell_id="root",
    )

    assert "with creations_0._lock:" in source
    assert "creations_0.add_many_creations(" in source
    assert "_register_spell_instance_prebound(" not in source


def test_emit_phase12_overrides_executor_shape_source_skips_many_registration_when_static_disposal_is_false() -> None:
    """Shape emitter omits many-registration emission when disposal metadata is statically false."""
    row = _make_plan_row("root")
    row["must_register"] = True
    spell = _make_spell("root")
    spell.has_disposal_methods = False

    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
    )

    assert "creations_0.add_many_creations(" not in source
    assert "spell_id_0 = step_spell_ids[0]" not in source
    assert "has_disposal_methods_0 = step_has_disposal_methods[0]" not in source
    assert "disposal_methods_0 = step_disposal_methods[0]" not in source


def test_emit_phase12_overrides_executor_shape_source_inlines_many_registration_without_runtime_disposal_branch_when_static_true() -> None:
    """Shape emitter emits direct many-registration when disposal metadata is statically true."""
    row = _make_plan_row("root")
    row["must_register"] = True
    spell = _make_spell("root")
    spell.has_disposal_methods = True
    spell.disposal_method_names = ("cleanup",)

    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
    )

    assert "creations_0.add_many_creations(" in source
    assert "if has_disposal_methods_0:" not in source
    assert "has_disposal_methods=True" in source
    assert "has_disposal_methods_0 = step_has_disposal_methods[0]" not in source


def test_emit_phase12_overrides_executor_shape_source_skips_many_registration_metadata_when_unused() -> None:
    """Shape emitter skips per-step registration metadata for non-registering many rows."""
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
    )

    assert "spell_id_0 = step_spell_ids[0]" not in source
    assert "has_disposal_methods_0 = step_has_disposal_methods[0]" not in source
    assert "disposal_methods_0 = step_disposal_methods[0]" not in source


def test_emit_phase12_overrides_executor_shape_source_uses_direct_callable_invoke_for_static_empty_kwargs() -> None:
    """Shape emitter calls callable spells directly when kwargs are statically empty."""
    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = lambda: "ok"

    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
        spell_lookup={"root": spell},
    )

    assert "kwargs_0 = {}" not in source
    assert "plan_step_0.spell.spell()" in source
    assert "plan_step_0.spell.spell(**kwargs_0)" not in source


def test_build_phase12_override_step_target_counts_from_rows_filters_duplicate_spell_steps() -> None:
    """Per-step target counts honor row-level shared/non-shared matching rules."""
    socket_a = _SocketRef("dup", "value", 10, "normal")
    socket_b = _SocketRef("dup", "value", 11, "normal")
    row_a = _make_plan_row("dup")
    row_b = _make_plan_row("dup")
    row_a["shared_instance"] = False
    row_b["shared_instance"] = False
    row_a["override_match_prefix"] = "parent-a"
    row_b["override_match_prefix"] = "parent-b"
    row_a["override_match_prefix_len"] = 0
    row_b["override_match_prefix_len"] = 0

    path_registry = _TrackingPathRegistry(
        parent_map={
            10: "parent-a",
            11: "parent-b",
        },
        depth_map={
            10: 1,
            11: 1,
        },
    )

    counts = build_phase12_override_step_target_counts_from_rows(
        plan_rows=(row_a, row_b),
        override_targets_by_spell_id={"dup": (socket_a, socket_b)},
        path_registry=path_registry,
    )

    assert counts == (1, 1)


def test_compile_phase12_overrides_executor_from_shape_source_supports_schema_rows_execution() -> None:
    """Shape-source code object compile path emits a callable executor that executes."""
    spell = _make_spell("root")
    source = emit_phase12_overrides_executor_shape_source(
        plan_rows=(_make_plan_row("root"),),
        root_spell_id="root",
    )
    code_object = compile_phase12_overrides_executor_code_object(source=source)
    executor = compile_phase12_overrides_executor_from_code_object(
        code_object=code_object,
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
    assert "step_creations_target_kinds" not in executor.__code__.co_varnames
    assert "step_existences" not in executor.__code__.co_varnames

    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        caller_creations_lock_held=False,
    )
    result = executor(
        context.caller_creations,
        {},
        None,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )

    assert result == "value:root"


def test_emit_phase12_overrides_executor_source_uses_prebound_must_register_flags() -> None:
    """Generated source uses prebound must-register tuple flags in many-step blocks."""
    source = emit_phase12_overrides_executor_source(step_count=1)

    assert "step_must_register_flags=step_must_register_flags" in source
    assert "must_register_0 = step_must_register_flags[0]" in source
    assert "plan_step_0.must_register" not in source


def test_emit_phase12_overrides_executor_source_prebinds_root_positional_override_once_per_step() -> None:
    """Generated source prebinds root positional payload once per step and reuses it."""
    source = emit_phase12_overrides_executor_source(step_count=1)

    assert (
        "step_root_positional_override_0 = root_positional_override if "
        "is_root_step_0 else None"
    ) in source
    assert source.count("root_positional_override if is_root_step_0 else None") == 1
    assert source.count("root_positional_override=step_root_positional_override_0") == 4


def test_emit_phase12_overrides_executor_source_uses_prebound_targeted_override_flags() -> None:
    """Generated source wires per-step targeted-override bool flags from prebound tuple."""
    source = emit_phase12_overrides_executor_source(step_count=1)

    assert "step_has_targeted_overrides=step_has_targeted_overrides" in source
    assert "has_targeted_overrides_0 = step_has_targeted_overrides[0]" in source
    assert "has_targeted_overrides_0 = bool(override_targets_0)" not in source


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
        context.caller_creations,
        {socket_ref: "override-value"},
        ("runtime-positional",),
        caller_creations_lock_held=context.caller_creations_lock_held,
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
        executor(
            context.caller_creations,
            {},
            ("arg",),
            owner_creations=context.owner_creations,
            caller_creations_lock_held=context.caller_creations_lock_held,
        )


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
        executor(
            context.caller_creations,
            {socket_ref: "override"},
            None,
            owner_creations=context.owner_creations,
            caller_creations_lock_held=context.caller_creations_lock_held,
        )


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
        executor(
            context.caller_creations,
            {socket_ref: "override"},
            None,
            owner_creations=context.owner_creations,
            caller_creations_lock_held=context.caller_creations_lock_held,
        )


def test_build_step_override_targets_prefilters_non_shared_steps() -> None:
    """Compile-time target preparation filters non-shared targets by path metadata."""
    socket_keep = _SocketRef("dep", "value", 101, "normal")
    socket_drop = _SocketRef("dep", "value", 202, "normal")
    path_registry = _TrackingPathRegistry(
        parent_map={101: 7, 202: 5},
        depth_map={101: 2, 202: 2},
    )
    steps = (
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=False,
            override_match_prefix=7,
            override_match_prefix_len=1,
        ),
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=True,
            override_match_prefix=None,
            override_match_prefix_len=0,
        ),
    )

    step_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
    )

    assert step_targets[0] == (socket_keep,)
    assert step_targets[1] == (socket_keep, socket_drop)
    assert path_registry.parent_calls == 2
    assert path_registry.depth_calls == 2


def test_build_step_override_targets_caches_path_metadata_across_steps() -> None:
    """Non-shared prefilter reuses per-socket path metadata across repeated step checks."""
    socket_keep = _SocketRef("dep", "value", 101, "normal")
    socket_drop = _SocketRef("dep", "value", 202, "normal")
    path_registry = _TrackingPathRegistry(
        parent_map={101: 7, 202: 5},
        depth_map={101: 2, 202: 2},
    )
    steps = (
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=False,
            override_match_prefix=7,
            override_match_prefix_len=1,
        ),
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=False,
            override_match_prefix=7,
            override_match_prefix_len=1,
        ),
    )

    step_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
    )

    assert step_targets[0] == (socket_keep,)
    assert step_targets[1] == (socket_keep,)
    assert path_registry.parent_calls == 2
    assert path_registry.depth_calls == 2


def test_build_step_override_targets_reuses_external_path_metadata_cache_across_calls() -> None:
    """Shared external path metadata cache prevents repeated registry lookups across calls."""
    socket_keep = _SocketRef("dep", "value", 101, "normal")
    socket_drop = _SocketRef("dep", "value", 202, "normal")
    path_registry = _TrackingPathRegistry(
        parent_map={101: 7, 202: 5},
        depth_map={101: 2, 202: 2},
    )
    steps = (
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=False,
            override_match_prefix=7,
            override_match_prefix_len=1,
        ),
    )
    path_metadata_cache: Dict[Any, Tuple[Any, Any]] = {}

    first_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
        prefilter_path_metadata_cache=path_metadata_cache,
    )
    parent_calls_after_first = path_registry.parent_calls
    depth_calls_after_first = path_registry.depth_calls
    second_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
        prefilter_path_metadata_cache=path_metadata_cache,
    )

    assert first_targets == second_targets
    assert path_registry.parent_calls == parent_calls_after_first
    assert path_registry.depth_calls == depth_calls_after_first


def test_build_step_override_targets_reuses_prefilter_step_target_cache() -> None:
    """Prefilter step-target cache bypasses repeat filtering work for same cache key."""
    socket_keep = _SocketRef("dep", "value", 101, "normal")
    socket_drop = _SocketRef("dep", "value", 202, "normal")
    path_registry = _TrackingPathRegistry(
        parent_map={101: 7, 202: 5},
        depth_map={101: 2, 202: 2},
    )
    steps = (
        SimpleNamespace(
            spell=_make_spell("dep"),
            shared_instance=False,
            override_match_prefix=7,
            override_match_prefix_len=1,
        ),
    )
    cache_key = ("plan-signature", (("dep", 101, "value", "normal"),))
    step_targets_cache: Dict[Tuple[Any, ...], Tuple[Tuple[Any, ...], ...]] = {}
    path_metadata_cache: Dict[Any, Tuple[Any, Any]] = {}

    first_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
        prefilter_step_targets_cache=step_targets_cache,
        prefilter_cache_key=cache_key,
        prefilter_path_metadata_cache=path_metadata_cache,
    )
    parent_calls_after_first = path_registry.parent_calls
    depth_calls_after_first = path_registry.depth_calls
    path_registry.raise_on_access = True
    second_targets = phase12_module._build_step_override_targets(
        steps=steps,
        override_targets_by_spell_id={"dep": (socket_keep, socket_drop)},
        path_registry=path_registry,
        prefilter_step_targets_cache=step_targets_cache,
        prefilter_cache_key=cache_key,
        prefilter_path_metadata_cache=path_metadata_cache,
    )

    assert first_targets == ((socket_keep,),)
    assert second_targets == first_targets
    assert path_registry.parent_calls == parent_calls_after_first
    assert path_registry.depth_calls == depth_calls_after_first
    assert step_targets_cache[cache_key] == first_targets


def test_compile_phase12_overrides_executor_non_shared_path_filtering_is_compile_time_only() -> None:
    """Runtime override materialization does not call path registry after compile."""
    captured: Dict[str, Any] = {}

    def _callable(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return kwargs.get("value")

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    row = _make_plan_row("root")
    row["shared_instance"] = False
    row["override_match_prefix"] = 7
    row["override_match_prefix_len"] = 1
    socket_keep = _SocketRef("root", "value", 11, "normal")
    socket_drop = _SocketRef("root", "value", 12, "normal")
    path_registry = _TrackingPathRegistry(
        parent_map={11: 7, 12: 9},
        depth_map={11: 2, 12: 2},
    )

    executor = compile_phase12_overrides_executor(
        execution_plan=None,
        plan_rows=(row,),
        root_spell_id="root",
        spell_lookup={"root": spell},
        override_targets_by_spell_id={"root": (socket_keep, socket_drop)},
        any_overrides_present=True,
        path_registry=path_registry,
    )
    parent_calls_after_compile = path_registry.parent_calls
    depth_calls_after_compile = path_registry.depth_calls

    path_registry.raise_on_access = True
    context = SimpleNamespace(
        caller_creations=SimpleNamespace(_lock=threading.RLock()),
        owner_creations=None,
        caller_creations_lock_held=False,
    )
    result = executor(
        context.caller_creations,
        {
            socket_keep: "keep",
            socket_drop: "drop",
        },
        None,
        owner_creations=context.owner_creations,
        caller_creations_lock_held=context.caller_creations_lock_held,
    )

    assert result == "keep"
    assert captured["value"] == "keep"
    assert path_registry.parent_calls == parent_calls_after_compile
    assert path_registry.depth_calls == depth_calls_after_compile


def test_build_kwargs_with_overrides_fast_path_returns_override_copy() -> None:
    """Kwargs helper fast path returns a copy of override values when no base payload exists."""
    plan_step = SimpleNamespace(
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=False,
    )
    override_values = {"value": "override"}

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values=override_values,
    )

    assert kwargs == {"value": "override"}
    assert kwargs is not override_values


def test_build_kwargs_with_overrides_contract_payload_only_returns_copy() -> None:
    """Overrides kwargs helper returns a copy for contract-payload-only steps."""
    contract_payload = {"value": "contract"}
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload=contract_payload,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={},
    )

    assert kwargs == {"value": "contract"}
    assert kwargs is not contract_payload


def test_build_kwargs_with_overrides_contract_payload_only_filters_args_key() -> None:
    """Overrides contract-only fast path filters `__args__` when positional override is enabled."""
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

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={},
    )

    assert kwargs == {"value": "contract"}


def test_build_kwargs_with_overrides_single_and_multi_dependency_shapes() -> None:
    """Overrides kwargs helper maps one dependency to scalar and many to list."""
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

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={
            dep_key_one: "v1",
            dep_key_two: "v2",
            dep_key_three: "v3",
        },
        override_values={},
    )

    assert kwargs == {
        "single": "v1",
        "multi": ["v2", "v3"],
    }


def test_build_kwargs_with_overrides_override_precedence_skips_dependency_lookup() -> None:
    """Override values take precedence and bypass dependency lookup for the same param."""
    dep_key_missing = ("dep-missing", None)
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(
            ("value", (dep_key_missing,)),
        ),
        contract_positional_override=None,
        has_contract_payload=False,
        contract_payload=None,
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={"value": "override"},
    )

    assert kwargs == {"value": "override"}


def test_build_kwargs_with_overrides_override_precedence_beats_contract_payload() -> None:
    """Override values still outrank contract payload values and missing dependencies."""
    dep_key_missing = ("dep-missing", None)
    plan_step = SimpleNamespace(
        spell=_make_spell("root"),
        dependency_resolution_order=(
            ("value", (dep_key_missing,)),
        ),
        contract_positional_override=None,
        has_contract_payload=True,
        contract_payload={"value": "contract"},
        uses_positional_override=False,
    )

    kwargs = phase12_module._build_kwargs_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_values={"value": "override"},
    )

    assert kwargs == {"value": "override"}


def test_build_kwargs_with_overrides_two_dependency_fast_path_skips_iteration() -> None:
    """Overrides kwargs helper resolves two dependencies without sequence iteration."""
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

    kwargs = phase12_module._build_kwargs_with_overrides(
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


def test_construct_spell_instance_with_overrides_skips_helper_for_empty_non_root_overrides(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Construct helper bypasses override-value builder when no targeted/root overrides exist."""
    captured: Dict[str, Any] = {}
    plan_step = SimpleNamespace(spell=_make_spell("root"))

    def _build_kwargs_with_overrides(**kwargs: Any) -> Dict[str, Any]:
        captured["override_values"] = kwargs["override_values"]
        return {"value": "payload"}

    def _invoke_spell_with_kwargs(**kwargs: Any) -> str:
        captured["invoked_kwargs"] = kwargs["kwargs"]
        return "instance"

    monkeypatch.setattr(
        phase12_module,
        "_build_step_override_values",
        lambda **kwargs: (_ for _ in ()).throw(
            AssertionError("override-values helper must not run for empty non-root payloads")
        ),
    )
    monkeypatch.setattr(
        phase12_module,
        "_build_kwargs_with_overrides",
        _build_kwargs_with_overrides,
    )
    monkeypatch.setattr(
        phase12_module,
        "_invoke_spell_with_kwargs",
        _invoke_spell_with_kwargs,
    )

    result = phase12_module._construct_spell_instance_with_overrides(
        plan_step=plan_step,
        instance_results={},
        override_targets=(),
        override_map={},
        root_positional_override=None,
    )

    assert result == "instance"
    assert captured["override_values"] == {}
    assert captured["invoked_kwargs"] == {"value": "payload"}


def test_build_step_override_values_fast_path_returns_empty_when_no_targets(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step override values helper returns empty payload without touching target-map helper."""
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("target helper must not be called for empty targets")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(),
        override_map={},
        root_positional_override=None,
    )

    assert values == {}


def test_build_step_override_values_fast_path_returns_root_positional_payload(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Step override values helper returns only root positional payload for empty targets."""
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("target helper must not be called for empty targets")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(),
        override_map={},
        root_positional_override=("arg-1",),
    )

    assert values == {"__args__": ("arg-1",)}


def test_build_step_override_values_single_target_fast_path_without_root_args(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Single-target helper path materializes direct param mapping without generic helper."""
    socket_ref = _SocketRef("root", "value", 7, "normal")
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("generic target helper must not be called for single target")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(socket_ref,),
        override_map={socket_ref: "override-value"},
        root_positional_override=None,
    )

    assert values == {"value": "override-value"}


def test_build_step_override_values_single_target_fast_path_with_root_args(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Single-target helper path merges direct param mapping with root positional args."""
    socket_ref = _SocketRef("root", "value", 7, "normal")
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("generic target helper must not be called for single target")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(socket_ref,),
        override_map={socket_ref: "override-value"},
        root_positional_override=("arg-1",),
    )

    assert values == {
        "value": "override-value",
        "__args__": ("arg-1",),
    }


def test_build_step_override_values_two_target_fast_path_without_root_args(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two-target helper path materializes direct param mapping without generic helper."""
    first_socket_ref = _SocketRef("root", "value_a", 7, "normal")
    second_socket_ref = _SocketRef("root", "value_b", 8, "normal")
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("generic target helper must not be called for two targets")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(first_socket_ref, second_socket_ref),
        override_map={
            first_socket_ref: "override-a",
            second_socket_ref: "override-b",
        },
        root_positional_override=None,
    )

    assert values == {
        "value_a": "override-a",
        "value_b": "override-b",
    }


def test_build_step_override_values_two_target_fast_path_with_root_args(
        monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two-target helper path merges direct param mapping with root positional args."""
    first_socket_ref = _SocketRef("root", "value_a", 7, "normal")
    second_socket_ref = _SocketRef("root", "value_b", 8, "normal")
    monkeypatch.setattr(
        phase12_module,
        "_build_instance_override_map",
        lambda override_targets, override_map: (_ for _ in ()).throw(
            AssertionError("generic target helper must not be called for two targets")
        ),
    )

    values = phase12_module._build_step_override_values(
        override_targets=(first_socket_ref, second_socket_ref),
        override_map={
            first_socket_ref: "override-a",
            second_socket_ref: "override-b",
        },
        root_positional_override=("arg-1",),
    )

    assert values == {
        "value_a": "override-a",
        "value_b": "override-b",
        "__args__": ("arg-1",),
    }


def test_invoke_spell_with_kwargs_preserves_args_payload_mapping() -> None:
    """Invoke helper does not mutate input kwargs when `__args__` payload is supplied."""
    captured: Dict[str, Any] = {}

    def _callable(*args: Any, **kwargs: Any) -> str:
        captured["args"] = args
        captured["kwargs"] = dict(kwargs)
        return "ok"

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    kwargs_payload = {"__args__": [1, 2], "value": "override"}

    result = phase12_module._invoke_spell_with_kwargs(
        spell=spell,
        kwargs=kwargs_payload,
    )

    assert result == "ok"
    assert captured["args"] == (1, 2)
    assert captured["kwargs"] == {"value": "override"}
    assert kwargs_payload == {"__args__": [1, 2], "value": "override"}


def test_invoke_spell_with_kwargs_accepts_tuple_args_payload_and_preserves_mapping() -> None:
    """Invoke helper accepts tuple `__args__` payloads and does not mutate input kwargs."""
    captured: Dict[str, Any] = {}

    def _callable(*args: Any, **kwargs: Any) -> str:
        captured["args"] = args
        captured["kwargs"] = dict(kwargs)
        return "ok"

    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = _callable
    kwargs_payload = {"__args__": (1, 2), "value": "override"}

    result = phase12_module._invoke_spell_with_kwargs(
        spell=spell,
        kwargs=kwargs_payload,
    )

    assert result == "ok"
    assert captured["args"] == (1, 2)
    assert captured["kwargs"] == {"value": "override"}
    assert kwargs_payload == {"__args__": (1, 2), "value": "override"}


def test_invoke_spell_with_kwargs_rejects_invalid_args_payload_type() -> None:
    """Invoke helper rejects invalid non-sequence `__args__` payloads."""
    spell = _make_spell("root")
    spell.is_class_spell = True
    spell.spell = lambda **kwargs: kwargs

    with pytest.raises(MeldExecutionError, match="__args__ override must be a list or tuple"):
        phase12_module._invoke_spell_with_kwargs(
            spell=spell,
            kwargs={"__args__": None},
        )


def test_resolve_root_instance_key_prefers_canonical_root_and_falls_back_to_first_match() -> None:
    """Root-instance helper prefers `(root, None)` and falls back to the first root match."""
    steps = (
        SimpleNamespace(instance_key=("root", 7)),
        SimpleNamespace(instance_key=("root", None)),
        SimpleNamespace(instance_key=("dep", 1)),
    )

    assert phase12_module._resolve_root_instance_key(
        steps=steps,
        root_spell_id="root",
    ) == ("root", None)

    assert phase12_module._resolve_root_instance_key(
        steps=(SimpleNamespace(instance_key=("root", 7)), SimpleNamespace(instance_key=("dep", 1))),
        root_spell_id="root",
    ) == ("root", 7)

    assert phase12_module._resolve_root_instance_key(
        steps=steps,
        root_spell_id=None,
    ) is None


def test_build_phase12_overrides_executor_namespace_prebinds_root_and_target_metadata() -> None:
    """Namespace builder prebinds root/target metadata needed by emitted override source."""
    root_spell = _make_spell("root")
    dep_spell = _make_spell("dep")
    steps = (
        SimpleNamespace(
            instance_key=("root", None),
            spell=root_spell,
            existence=Existence.unique,
            creations_target_kind=ExecutionPlanTargetKind.OWNER,
            use_spell_lock_hint=True,
            must_register=True,
        ),
        SimpleNamespace(
            instance_key=("dep", 1),
            spell=dep_spell,
            existence=Existence.many,
            creations_target_kind=ExecutionPlanTargetKind.CALLER,
            use_spell_lock_hint=False,
            must_register=False,
        ),
    )
    socket_ref = _SocketRef("root", "value", 7, "normal")

    namespace = phase12_module._build_phase12_overrides_executor_namespace(
        steps=steps,
        step_override_targets=((socket_ref,), ()),
        root_instance_key=("root", None),
        root_spell_id="root",
        any_overrides_present=True,
    )

    assert namespace["step_spell_ids"] == ("root", "dep")
    assert namespace["step_is_root"] == (True, False)
    assert namespace["step_has_targeted_overrides"] == (True, False)
    assert namespace["step_override_target_counts"] == (1, 0)
    assert namespace["step_use_spell_lock_hints"] == (True, False)
    assert namespace["step_must_register_flags"] == (True, False)
    assert namespace["root_instance_key"] == ("root", None)
    assert namespace["any_overrides_present"] is True
