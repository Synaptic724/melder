import builtins

import pytest

from melder.nexus.rift.codegen_system.execution.codegen_compiler import (
    CodegenCompiler,
)
from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.nexus.rift.codegen_system.execution.codegen_executor import (
    CodegenExecutor,
)
from melder.nexus.rift.codegen_system.namespace.codegen_control_surface import (
    CodegenControlSurface,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_builder import (
    CodegenNamespaceBuilder,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_builtins_strategy import (
    CodegenBuiltinsStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_command_strategy import (
    CodegenCommandStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_control_strategy import (
    CodegenControlStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_room_objects_strategy import (
    CodegenRoomObjectsStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_target_strategy import (
    CodegenTargetStrategy,
)
from melder.nexus.rift.codegen_system.namespace.strategies.codegen_workstation_strategy import (
    CodegenWorkstationStrategy,
)
from melder.nexus.rift.codegen_system.observability.codegen_event_publisher import (
    CodegenEventPublisher,
)
from melder.nexus.rift.codegen_system.observability.codegen_monitor import (
    CodegenMonitor,
)
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from tests._codegen_system_support import (
    CodegenSpaceDouble,
    DetachedRiftProjectionOwner,
    build_namespace_configuration,
)


@pytest.mark.parametrize(
    ("include_viewer", "include_workstation", "include_command", "include_codegen", "expected"),
    [
        (False, False, False, False, tuple()),
        (True, False, False, False, ("viewer",)),
        (False, True, False, False, ("workstation",)),
        (False, False, True, False, ("command",)),
        (False, False, False, True, ("codegen",)),
        (True, True, False, False, ("viewer", "workstation")),
        (True, False, True, False, ("viewer", "command")),
        (True, False, False, True, ("viewer", "codegen")),
        (False, True, True, False, ("workstation", "command")),
        (False, True, False, True, ("workstation", "codegen")),
        (False, False, True, True, ("command", "codegen")),
        (True, True, True, False, ("viewer", "workstation", "command")),
        (True, True, False, True, ("viewer", "workstation", "codegen")),
        (True, False, True, True, ("viewer", "command", "codegen")),
        (False, True, True, True, ("workstation", "command", "codegen")),
        (True, True, True, True, ("viewer", "workstation", "command", "codegen")),
    ],
)
def test_unit_codegen_namespace_configuration_exposed_names_matrix(
        include_viewer: bool,
        include_workstation: bool,
        include_command: bool,
        include_codegen: bool,
        expected: tuple,
) -> None:
    configuration = CodegenNamespaceConfiguration(
        frame_name="ops",
        include_viewer=include_viewer,
        include_workstation=include_workstation,
        include_target=False,
        include_command=include_command,
        include_codegen=include_codegen,
    )

    assert configuration.exposed_names == expected


def test_unit_codegen_namespace_configuration_default_exposed_names_include_target() -> None:
    configuration = build_namespace_configuration()

    assert configuration.exposed_names == (
        "viewer",
        "workstation",
        "target",
        "command",
        "codegen",
    )


@pytest.mark.parametrize(
    ("locals_dict", "expected"),
    [
        ({}, None),
        ({"result": 1}, 1),
        ({"result": "ok"}, "ok"),
        ({"value": 4}, None),
        ({"result": None}, None),
    ],
)
def test_unit_codegen_namespace_get_result_matrix(
        locals_dict: dict,
        expected: object,
) -> None:
    configuration = build_namespace_configuration()
    namespace = CodegenNamespace(
        configuration=configuration,
        globals_dict={},
        locals_dict=locals_dict,
    )

    assert namespace.get_result() == expected


@pytest.mark.parametrize(
    ("imports_enabled", "denied_builtin_names"),
    [
        (False, tuple()),
        (True, tuple()),
        (False, ("eval",)),
        (True, ("eval", "exec")),
        (False, ("__import__",)),
        (True, ("getattr", "setattr")),
        (False, ("globals", "locals", "vars")),
        (True, ("compile", "breakpoint")),
    ],
)
def test_unit_codegen_namespace_configuration_round_trip_flags(
        imports_enabled: bool,
        denied_builtin_names: tuple,
) -> None:
    configuration = build_namespace_configuration(
        imports_enabled=imports_enabled,
        denied_builtin_names=denied_builtin_names,
    )

    assert configuration.imports_enabled is imports_enabled
    assert configuration.denied_builtin_names == denied_builtin_names


@pytest.mark.parametrize(
    ("exposed_names", "expected_key"),
    [
        (("viewer",), "viewer"),
        (("workstation",), "workstation"),
        (("command",), "command"),
        (("codegen",), "codegen"),
    ],
)
def test_unit_codegen_namespace_strategies_expose_expected_entries(
        exposed_names: tuple,
        expected_key: str,
) -> None:
    space = CodegenSpaceDouble()
    rift = DetachedRiftProjectionOwner()
    configuration = CodegenNamespaceConfiguration(
        frame_name="ops",
        include_viewer=("viewer" in exposed_names),
        include_workstation=("workstation" in exposed_names),
        include_target=("target" in exposed_names),
        include_command=("command" in exposed_names),
        include_codegen=("codegen" in exposed_names),
    )
    target_value = object()
    if "target" in exposed_names:
        space.workstation.set_target(target_value)

    room_entries = CodegenRoomObjectsStrategy().build_namespace_entries(
        configuration,
        rift=rift,
        space=space,
    )
    workstation_entries = CodegenWorkstationStrategy().build_namespace_entries(
        configuration,
        space=space,
    )
    target_entries = CodegenTargetStrategy().build_namespace_entries(
        configuration,
        space=space,
    )
    command_entries = CodegenCommandStrategy().build_namespace_entries(
        configuration,
        space=space,
    )
    codegen_entries = CodegenControlStrategy().build_namespace_entries(
        configuration,
        space=space,
    )
    merged_entries = {}
    merged_entries.update(room_entries)
    merged_entries.update(workstation_entries)
    merged_entries.update(target_entries)
    merged_entries.update(command_entries)
    merged_entries.update(codegen_entries)

    assert expected_key in merged_entries
    if expected_key == "target":
        assert merged_entries["target"] is target_value


def test_unit_codegen_namespace_builder_exposes_target_when_present() -> None:
    builder = CodegenNamespaceBuilder()
    space = CodegenSpaceDouble()
    rift = DetachedRiftProjectionOwner()
    target_value = object()
    space.workstation.set_target(target_value)

    namespace = builder.build(
        build_namespace_configuration(),
        rift=rift,
        space=space,
    )

    assert namespace.globals_dict["target"] is target_value


def test_unit_codegen_namespace_builder_exposes_none_when_target_missing() -> None:
    builder = CodegenNamespaceBuilder()
    space = CodegenSpaceDouble()
    rift = DetachedRiftProjectionOwner()

    namespace = builder.build(
        build_namespace_configuration(),
        rift=rift,
        space=space,
    )

    assert "target" in namespace.globals_dict
    assert namespace.globals_dict["target"] is None


@pytest.mark.parametrize(
    "denied_builtin_name",
    (
        "eval",
        "exec",
        "compile",
        "dir",
        "getattr",
        "globals",
        "locals",
        "setattr",
        "delattr",
        "vars",
        "__import__",
        "breakpoint",
    ),
)
def test_unit_codegen_builtins_strategy_removes_denied_builtins(
        denied_builtin_name: str,
) -> None:
    strategy = CodegenBuiltinsStrategy()
    configuration = build_namespace_configuration(
        denied_builtin_names=(denied_builtin_name,),
    )

    entries = strategy.build_namespace_entries(configuration)

    assert "__builtins__" in entries
    assert denied_builtin_name not in entries["__builtins__"]
    assert "len" in entries["__builtins__"]


@pytest.mark.parametrize(
    ("code", "expected_result"),
    [
        ("result = 1", 1),
        ("result = 1 + 1", 2),
        ("value = 7", None),
        ("result = 'ok'", "ok"),
        ("result = [1, 2, 3]", [1, 2, 3]),
        ("result = {'x': 1}", {"x": 1}),
        (
            "class Right:\n"
            "    def __init__(self, value: int) -> None:\n"
            "        self.value = value\n"
            "class Left:\n"
            "    def __init__(self, right: Right) -> None:\n"
            "        self.right = right\n"
            "    def read(self) -> int:\n"
            "        return self.right.value\n"
            "result = Left(Right(11)).read()",
            11,
        ),
    ],
)
def test_unit_codegen_compiler_and_executor_matrix(
        code: str,
        expected_result: object,
) -> None:
    configuration = build_namespace_configuration()
    namespace = CodegenNamespace(
        configuration=configuration,
        globals_dict={"__builtins__": dict(vars(builtins))},
        locals_dict={},
    )
    context = type("Context", (), {})()
    context.code = code
    context.transaction_id = "txn-1"
    context.frame_name = "ops"
    context.namespace = namespace

    compiled_code = CodegenCompiler().compile(context)
    result = CodegenExecutor().execute(compiled_code, context)

    assert result.accepted is True
    if expected_result is None:
        assert "result" not in result.to_payload()
    else:
        assert result.result == expected_result


@pytest.mark.parametrize(
    ("result_builder", "expected_reason"),
    [
        (lambda: CodegenValidationResult.validation_accepted(frame_name="ops"), "codegen_validation_accepted"),
        (lambda: CodegenValidationResult.syntax_error(frame_name="ops", message="bad"), "codegen_validation_failed"),
        (lambda: CodegenValidationResult.validation_failed(frame_name="ops", message="bad"), "codegen_validation_failed"),
        (lambda: CodegenExecutionResult.executed(frame_name="ops", result=1), None),
        (lambda: CodegenExecutionResult.validation_failed(frame_name="ops", validation_issues=("bad",)), "codegen_execution_validation_failed"),
        (lambda: CodegenExecutionResult.runtime_failed(frame_name="ops", runtime_error="boom"), "codegen_execution_runtime_failed"),
    ],
)
def test_unit_codegen_result_payloads_matrix(
        result_builder,
        expected_reason: str,
) -> None:
    result = result_builder()
    payload = result.to_payload()

    assert payload["frame_name"] == "ops"
    if expected_reason is None:
        assert payload["accepted"] is True
    else:
        assert payload["reason"] == expected_reason


@pytest.mark.parametrize(
    ("method_name", "allow_recursive_codegen", "expected_exception"),
    [
        ("validate_codegen", True, None),
        ("execute_codegen", True, None),
        ("validate_codegen", False, RuntimeError),
        ("execute_codegen", False, RuntimeError),
        ("validate_codegen", True, None),
        ("execute_codegen", False, RuntimeError),
    ],
)
def test_unit_codegen_control_surface_matrix(
        method_name: str,
        allow_recursive_codegen: bool,
        expected_exception: object,
) -> None:
    calls = []

    class _CodegenSystemDouble:
        def validate_codegen(self, code: str, *, frame_name: str):
            calls.append(("validate", code, frame_name))
            return CodegenValidationResult.validation_accepted(frame_name=frame_name)

        def execute_codegen(self, code: str, *, frame_name: str):
            calls.append(("execute", code, frame_name))
            return CodegenExecutionResult.executed(frame_name=frame_name, result=3)

        def report_validation_result(self, validation_result):
            return validation_result.to_payload()

    surface = CodegenControlSurface(
        codegen_system=_CodegenSystemDouble(),
        default_frame_name="ops",
        recursive_codegen_allowed=allow_recursive_codegen,
    )

    if expected_exception is not None:
        with pytest.raises(expected_exception):
            getattr(surface, method_name)("result = 1")
        return

    payload = getattr(surface, method_name)("result = 1")
    assert payload["frame_name"] == "ops"
    assert len(calls) == 1


@pytest.mark.parametrize(
    ("event_method_name", "result_kind", "expected_event_type"),
    [
        ("publish_validation_started", None, "codegen_validation_started"),
        ("publish_validation_finished", "validation", "codegen_validation_finished"),
        ("publish_execution_started", None, "codegen_execution_started"),
        ("publish_execution_finished", "execution", "codegen_execution_finished"),
        ("publish_validation_finished", "validation_failed", "codegen_validation_finished"),
        ("publish_execution_finished", "runtime_failed", "codegen_execution_finished"),
    ],
)
def test_unit_codegen_event_publisher_matrix(
        event_method_name: str,
        result_kind: str,
        expected_event_type: str,
) -> None:
    space = CodegenSpaceDouble()
    publisher = CodegenEventPublisher(space=space)
    context = _build_context_for_observability()

    if result_kind is None:
        getattr(publisher, event_method_name)(context)
    elif result_kind == "validation":
        getattr(publisher, event_method_name)(
            context,
            CodegenValidationResult.validation_accepted(frame_name="ops"),
        )
    elif result_kind == "validation_failed":
        getattr(publisher, event_method_name)(
            context,
            CodegenValidationResult.validation_failed(
                frame_name="ops",
                message="bad",
            ),
        )
    elif result_kind == "execution":
        getattr(publisher, event_method_name)(
            context,
            CodegenExecutionResult.executed(frame_name="ops", result=1),
        )
    else:
        getattr(publisher, event_method_name)(
            context,
            CodegenExecutionResult.runtime_failed(
                frame_name="ops",
                runtime_error="boom",
            ),
        )

    assert space.event_system.events[-1]["event_type"] == expected_event_type


@pytest.mark.parametrize(
    ("method_name", "result_kind"),
    [
        ("on_validation_started", None),
        ("on_validation_finished", "validation"),
        ("on_validation_finished", "validation_failed"),
        ("on_execution_started", None),
        ("on_execution_finished", "execution"),
        ("on_execution_finished", "runtime_failed"),
    ],
)
def test_unit_codegen_monitor_matrix(
        method_name: str,
        result_kind: str,
) -> None:
    space = CodegenSpaceDouble()
    monitor = CodegenMonitor(space=space)
    context = _build_context_for_observability()

    if result_kind is None:
        getattr(monitor, method_name)(context)
    elif result_kind == "validation":
        getattr(monitor, method_name)(
            context,
            CodegenValidationResult.validation_accepted(frame_name="ops"),
        )
    elif result_kind == "validation_failed":
        getattr(monitor, method_name)(
            context,
            CodegenValidationResult.validation_failed(
                frame_name="ops",
                message="bad",
            ),
        )
    elif result_kind == "execution":
        getattr(monitor, method_name)(
            context,
            CodegenExecutionResult.executed(frame_name="ops", result=1),
        )
    else:
        getattr(monitor, method_name)(
            context,
            CodegenExecutionResult.runtime_failed(
                frame_name="ops",
                runtime_error="boom",
            ),
        )

    assert len(space.event_system.events) == 1


def _build_context_for_observability():
    return type(
        "Context",
        (),
        {
            "transaction_id": "txn-1",
            "frame_name": "ops",
            "code_hash": "hash",
            "code": "result = 1",
        },
    )()
