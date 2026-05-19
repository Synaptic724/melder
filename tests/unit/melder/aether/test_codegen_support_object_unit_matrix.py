import pytest

from melder.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.nexus.rift.codegen_system.namespace.codegen_namespace_configuration import (
    CodegenNamespaceConfiguration,
)
from melder.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)


@pytest.mark.parametrize(
    ("accepted", "reason", "issues", "expected_payload_keys"),
    [
        (True, "codegen_validation_accepted", tuple(), {"accepted", "frame_name", "reason"}),
        (False, "codegen_validation_failed", ("bad",), {"accepted", "frame_name", "reason", "validation_issues"}),
        (False, "codegen_validation_failed", ("bad", "worse"), {"accepted", "frame_name", "reason", "validation_issues"}),
        (True, None, tuple(), {"accepted", "frame_name"}),
        (False, None, tuple(), {"accepted", "frame_name"}),
        (True, "ok", tuple(), {"accepted", "frame_name", "reason"}),
        (False, "bad", tuple(), {"accepted", "frame_name", "reason"}),
        (False, "bad", ("x",), {"accepted", "frame_name", "reason", "validation_issues"}),
        (True, "accepted", tuple(), {"accepted", "frame_name", "reason"}),
        (False, "failed", ("x", "y", "z"), {"accepted", "frame_name", "reason", "validation_issues"}),
        (True, "accepted", tuple(), {"accepted", "frame_name", "reason"}),
        (False, "failed", ("issue",), {"accepted", "frame_name", "reason", "validation_issues"}),
        (False, "failed", tuple(), {"accepted", "frame_name", "reason"}),
        (True, None, tuple(), {"accepted", "frame_name"}),
        (False, None, ("issue",), {"accepted", "frame_name", "validation_issues"}),
    ],
)
def test_unit_codegen_validation_result_payload_matrix(
        accepted: bool,
        reason: str,
        issues: tuple,
        expected_payload_keys: set,
) -> None:
    result = CodegenValidationResult(
        accepted=accepted,
        frame_name="ops",
        reason=reason,
        validation_issues=issues,
    )

    payload = result.to_payload()

    assert set(payload.keys()) == expected_payload_keys
    assert payload["accepted"] is accepted
    assert payload["frame_name"] == "ops"


@pytest.mark.parametrize(
    ("accepted", "reason", "issues", "runtime_error", "result_value", "expected_payload_keys"),
    [
        (True, None, tuple(), None, 1, {"accepted", "frame_name", "result"}),
        (True, None, tuple(), None, None, {"accepted", "frame_name"}),
        (False, "codegen_execution_validation_failed", ("bad",), None, None, {"accepted", "frame_name", "reason", "validation_issues"}),
        (False, "codegen_execution_runtime_failed", tuple(), "boom", None, {"accepted", "frame_name", "reason", "runtime_error"}),
        (False, "codegen_execution_runtime_failed", ("bad",), "boom", None, {"accepted", "frame_name", "reason", "validation_issues", "runtime_error"}),
        (True, "executed", tuple(), None, [1, 2], {"accepted", "frame_name", "reason", "result"}),
        (False, "runtime_failed", tuple(), "ValueError: boom", None, {"accepted", "frame_name", "reason", "runtime_error"}),
        (True, None, tuple(), None, {"x": 1}, {"accepted", "frame_name", "result"}),
        (False, None, tuple(), None, None, {"accepted", "frame_name"}),
        (False, "failed", tuple(), None, None, {"accepted", "frame_name", "reason"}),
        (True, None, tuple(), None, "ok", {"accepted", "frame_name", "result"}),
        (False, "failed", ("x",), None, None, {"accepted", "frame_name", "reason", "validation_issues"}),
        (False, "failed", tuple(), "boom", None, {"accepted", "frame_name", "reason", "runtime_error"}),
        (True, "executed", tuple(), None, 0, {"accepted", "frame_name", "reason", "result"}),
        (True, "executed", tuple(), None, None, {"accepted", "frame_name", "reason"}),
    ],
)
def test_unit_codegen_execution_result_payload_matrix(
        accepted: bool,
        reason: str,
        issues: tuple,
        runtime_error: str,
        result_value: object,
        expected_payload_keys: set,
) -> None:
    result = CodegenExecutionResult(
        accepted=accepted,
        frame_name="ops",
        reason=reason,
        validation_issues=issues,
        runtime_error=runtime_error,
        result=result_value,
    )

    payload = result.to_payload()

    assert set(payload.keys()) == expected_payload_keys
    assert payload["accepted"] is accepted
    assert payload["frame_name"] == "ops"


@pytest.mark.parametrize(
    ("code", "frame_name", "metadata"),
    [
        ("result = 1", "ops", {}),
        ("value = 7", "ops", {"team": "ops"}),
        ("result = [1, 2, 3]", "ops", {"surface": "codegen"}),
        ("result = {'x': 1}", "finance", {"owner_space_id": "space-2"}),
        ("result = 'ok'", "ops", {}),
        ("result = 2 + 2", "alpha", {"alpha": 1}),
        ("result = True", "beta", {"flag": True}),
        ("result = None", "gamma", {"meta": "x"}),
        ("result = 9", "ops", {}),
        ("result = 10", "ops", {"sequence": 10}),
        ("result = 11", "ops", {"sequence": 11}),
        ("result = 12", "ops", {"sequence": 12}),
        ("result = 13", "ops", {"sequence": 13}),
        ("result = 14", "ops", {"sequence": 14}),
        ("result = 15", "ops", {"sequence": 15}),
    ],
)
def test_unit_codegen_transaction_context_round_trip_matrix(
        code: str,
        frame_name: str,
        metadata: dict,
) -> None:
    configuration = CodegenNamespaceConfiguration.create_default(frame_name=frame_name)
    namespace = CodegenNamespace(configuration=configuration, locals_dict={"result": 1})
    context = CodegenTransactionContext(
        frame_name=frame_name,
        code=code,
        metadata=metadata,
    )

    context.set_namespace_configuration(configuration)
    context.set_namespace(namespace)
    context.set_projection("projection")

    assert context.frame_name == frame_name
    assert context.code == code
    assert context.metadata == metadata
    assert context.namespace_configuration is configuration
    assert context.namespace is namespace
    assert context.projection == "projection"


@pytest.mark.parametrize(
    ("locals_dict", "expected_result", "metadata"),
    [
        ({}, None, {}),
        ({"result": 1}, 1, {}),
        ({"result": "ok"}, "ok", {"mode": "text"}),
        ({"result": [1, 2]}, [1, 2], {}),
        ({"value": 7}, None, {}),
        ({"result": {"x": 1}}, {"x": 1}, {"shape": "dict"}),
        ({"result": None}, None, {}),
        ({"result": 2.5}, 2.5, {}),
        ({"result": True}, True, {}),
        ({"result": False}, False, {}),
        ({"result": ("x",)}, ("x",), {}),
        ({"result": {"nested": {"x": 1}}}, {"nested": {"x": 1}}, {}),
        ({}, None, {"empty": True}),
        ({"value": 1}, None, {"missing": "result"}),
        ({"result": "final"}, "final", {"marker": "done"}),
    ],
)
def test_unit_codegen_namespace_round_trip_matrix(
        locals_dict: dict,
        expected_result: object,
        metadata: dict,
) -> None:
    configuration = CodegenNamespaceConfiguration.create_default(frame_name="ops")
    namespace = CodegenNamespace(
        configuration=configuration,
        globals_dict={"__builtins__": {}},
        locals_dict=locals_dict,
        metadata=metadata,
    )

    returned_metadata = namespace.metadata
    returned_metadata["extra"] = True

    assert namespace.get_result() == expected_result
    assert namespace.metadata != returned_metadata
