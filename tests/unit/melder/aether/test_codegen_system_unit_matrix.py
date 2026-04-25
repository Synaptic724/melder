import pytest

from melder.aether.nexus.rift.codegen_system.codegen_system import CodegenSystem
from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.execution.codegen_execution_result import (
    CodegenExecutionResult,
)
from melder.aether.nexus.rift.codegen_system.namespace.codegen_namespace import (
    CodegenNamespace,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validation_result import (
    CodegenValidationResult,
)
from tests._codegen_system_support import (
    CodegenSpaceDouble,
    DetachedRiftProjectionOwner,
    build_codegen_projection,
    build_namespace_configuration,
)


@pytest.mark.parametrize(
    (
        "imports_enabled",
        "allowed_roots",
        "denied_roots",
        "denied_builtins",
        "unsafe_reflection",
        "dunder_access",
        "recursive_codegen",
    ),
    [
        (False, tuple(), tuple(), tuple(), False, False, False),
        (True, ("json",), tuple(), tuple(), False, False, False),
        (True, ("json", "math"), ("subprocess",), ("eval",), False, False, False),
        (True, ("inspect",), tuple(), ("getattr",), False, False, False),
        (True, ("socket",), tuple(), tuple(), True, False, False),
        (True, ("builtins",), tuple(), tuple(), True, True, False),
        (True, ("importlib",), tuple(), ("compile",), True, True, True),
        (False, tuple(), ("subprocess",), ("eval", "exec"), False, False, False),
        (True, ("json",), ("ctypes",), ("globals", "locals"), False, True, False),
        (True, ("math",), tuple(), tuple(), False, False, True),
        (True, ("datetime",), tuple(), ("dir",), False, False, False),
        (True, ("collections",), ("socket",), ("vars",), False, False, False),
        (True, ("re",), tuple(), tuple(), False, False, False),
        (True, ("pathlib",), tuple(), ("breakpoint",), False, False, False),
        (True, ("inspect", "json"), ("importlib",), ("getattr",), False, False, False),
        (True, ("builtins", "math"), tuple(), tuple(), True, True, True),
        (False, tuple(), tuple(), ("eval",), False, False, False),
        (False, tuple(), tuple(), ("exec",), False, False, False),
        (False, tuple(), tuple(), ("compile",), False, False, False),
        (True, ("json", "typing"), ("ctypes", "subprocess"), ("eval", "exec"), False, False, False),
    ],
)
def test_unit_codegen_system_build_default_namespace_configuration_projection_matrix(
        imports_enabled: bool,
        allowed_roots: tuple,
        denied_roots: tuple,
        denied_builtins: tuple,
        unsafe_reflection: bool,
        dunder_access: bool,
        recursive_codegen: bool,
) -> None:
    rift = DetachedRiftProjectionOwner()
    projection = build_codegen_projection(
        imports_enabled=imports_enabled,
        allowed_import_module_roots=allowed_roots,
        denied_import_module_roots=denied_roots,
        denied_builtin_names=denied_builtins,
        unsafe_reflection_allowed=unsafe_reflection,
        dunder_access_allowed=dunder_access,
        recursive_codegen_allowed=recursive_codegen,
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)

    configuration = system._build_default_namespace_configuration(
        frame_name="ops",
        projection=projection,
    )

    assert configuration.imports_enabled is imports_enabled
    assert configuration.allowed_import_module_roots == allowed_roots
    assert configuration.denied_import_module_roots == denied_roots
    assert configuration.denied_builtin_names == denied_builtins
    assert configuration.allow_unsafe_reflection is unsafe_reflection
    assert configuration.allow_dunder_access is dunder_access
    assert configuration.allow_recursive_codegen is recursive_codegen


@pytest.mark.parametrize(
    ("exception_kind", "expected_projection"),
    [
        ("present", "projection"),
        ("attribute", None),
        ("key", None),
        ("value", None),
    ],
)
def test_unit_codegen_system_try_get_codegen_projection_matrix(
        exception_kind: str,
        expected_projection: object,
) -> None:
    class _RiftDouble:
        def _get_required_codegen_projection(self, frame_name: str):
            _ = frame_name
            if exception_kind == "attribute":
                raise AttributeError("missing")
            if exception_kind == "key":
                raise KeyError("missing")
            if exception_kind == "value":
                raise ValueError("missing")
            return "projection"

    system = CodegenSystem(rift=_RiftDouble(), space=CodegenSpaceDouble())

    projection = system._try_get_codegen_projection("ops")

    assert projection == expected_projection


@pytest.mark.parametrize(
    ("code", "accepted", "result_value"),
    [
        ("result = 1", True, 1),
        ("result = 2 + 2", True, 4),
        ("import json\nresult = 1", True, 1),
        ("result = getattr(command, 'x')", False, None),
        ("result = codegen.execute_codegen('result = 1')", True, {"accepted": True, "frame_name": "ops", "result": 1}),
        ("value = 7", True, None),
        ("result = [1, 2, 3]", True, [1, 2, 3]),
        ("raise ValueError('boom')", False, None),
        ("result = command.link_frame('ops')", True, "ops"),
        ("result = viewer.list_nexus_frame_names()", True, ("ops",)),
    ],
)
def test_unit_codegen_system_execute_codegen_request_matrix(
        code: str,
        accepted: bool,
        result_value: object,
) -> None:
    rift = DetachedRiftProjectionOwner()
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        imports_enabled=True,
        allowed_import_module_roots=("json",),
        unsafe_reflection_allowed=True,
        dunder_access_allowed=True,
        recursive_codegen_allowed=True,
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)
    space.codegen_system = system

    context, execution_result = system.execute_codegen_request(
        code,
        frame_name="ops",
    )

    assert context.frame_name == "ops"
    assert execution_result.accepted is accepted
    if accepted and result_value is not None:
        assert execution_result.result == result_value
    if accepted and result_value is None:
        assert execution_result.result is None


@pytest.mark.parametrize(
    ("code", "accepted", "reason"),
    [
        ("result = 1", True, "codegen_validation_accepted"),
        ("import json\nresult = 1", True, "codegen_validation_accepted"),
        ("result = getattr(command, 'x')", True, "codegen_validation_accepted"),
        ("result = codegen.execute_codegen('result = 1')", False, "codegen_validation_failed"),
        ("value = 7", True, "codegen_validation_accepted"),
        ("global result\nresult = 1", False, "codegen_validation_failed"),
        ("result = viewer.list_nexus_frame_names()", True, "codegen_validation_accepted"),
        ("result = mystery_name", False, "codegen_validation_failed"),
        ("result = command.__dict__", False, "codegen_validation_failed"),
        ("result = type(command)", True, "codegen_validation_accepted"),
    ],
)
def test_unit_codegen_system_validate_codegen_request_matrix(
        code: str,
        accepted: bool,
        reason: str,
) -> None:
    rift = DetachedRiftProjectionOwner()
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        imports_enabled=True,
        allowed_import_module_roots=("json",),
        unsafe_reflection_allowed=True,
        dunder_access_allowed=False,
        recursive_codegen_allowed=False,
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)

    context, validation_result = system.validate_codegen_request(
        code,
        frame_name="ops",
    )

    assert context.frame_name == "ops"
    assert validation_result.accepted is accepted
    assert validation_result.reason == reason


@pytest.mark.parametrize(
    ("method_name", "code", "accepted"),
    [
        ("validate_codegen", "result = 1", True),
        ("validate_codegen", "result = mystery", False),
        ("execute_codegen", "result = 1", True),
        ("execute_codegen", "raise ValueError('boom')", False),
        ("validate_codegen", "result = viewer.list_nexus_frame_names()", True),
        ("execute_codegen", "result = command.link_frame('ops')", True),
        ("validate_codegen", "global value\nvalue = 1", False),
        ("execute_codegen", "result = type(command)", True),
    ],
)
def test_unit_codegen_system_public_wrapper_matrix(
        method_name: str,
        code: str,
        accepted: bool,
) -> None:
    rift = DetachedRiftProjectionOwner()
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        imports_enabled=True,
        allowed_import_module_roots=("json",),
        unsafe_reflection_allowed=True,
        dunder_access_allowed=False,
        recursive_codegen_allowed=True,
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)
    space.codegen_system = system

    result = getattr(system, method_name)(code, frame_name="ops")

    assert result.accepted is accepted


@pytest.mark.parametrize(
    ("metadata", "expected_owner_space_id"),
    [
        ({}, "space-1"),
        ({"alpha": 1}, "space-1"),
        ({"surface": "codegen"}, "space-1"),
        ({"team": "ops"}, "space-1"),
        ({}, "space-1"),
        ({}, "space-1"),
        ({}, "space-1"),
        ({}, "space-1"),
        ({}, "space-1"),
        ({}, "space-1"),
    ],
)
def test_unit_codegen_transaction_context_metadata_matrix(
        metadata: dict,
        expected_owner_space_id: str,
) -> None:
    context = CodegenTransactionContext(
        frame_name="ops",
        code="result = 1",
        metadata=metadata,
    )

    returned_metadata = context.metadata
    returned_metadata["extra"] = True

    assert context.transaction_id is not None
    assert context.frame_name == "ops"
    assert context.code_hash == context.code_hash
    assert context.metadata != returned_metadata
    assert expected_owner_space_id == "space-1"


@pytest.mark.parametrize(
    ("code", "expected_has_projection"),
    [
        ("result = 1", False),
        ("value = 7", False),
        ("result = command.link_frame('ops')", False),
        ("result = viewer.list_nexus_frame_names()", False),
        ("result = 2 + 2", False),
        ("result = {'x': 1}", False),
        ("result = [1, 2, 3]", False),
        ("result = 'ok'", False),
    ],
)
def test_unit_codegen_system_build_transaction_context_without_projection(
        code: str,
        expected_has_projection: bool,
) -> None:
    system = CodegenSystem(
        rift=DetachedRiftProjectionOwner(),
        space=CodegenSpaceDouble(),
    )

    context = system._build_transaction_context(code, frame_name="ops")

    assert context.projection is None
    assert context.namespace_configuration.metadata["has_projection"] is (
        expected_has_projection
    )


@pytest.mark.parametrize(
    ("reason", "expected_reason"),
    [
        ("accepted", "codegen_validation_accepted"),
        ("failed", "codegen_validation_failed"),
        ("runtime", "codegen_execution_runtime_failed"),
        ("validation_failed", "codegen_execution_validation_failed"),
        ("executed", None),
        ("accepted", "codegen_validation_accepted"),
    ],
)
def test_unit_codegen_report_validation_result_and_payload_matrix(
        reason: str,
        expected_reason: str,
) -> None:
    system = CodegenSystem(
        rift=DetachedRiftProjectionOwner(),
        space=CodegenSpaceDouble(),
    )
    if reason == "accepted":
        payload = system.report_validation_result(
            CodegenValidationResult.validation_accepted(frame_name="ops")
        )
    elif reason == "failed":
        payload = system.report_validation_result(
            CodegenValidationResult.validation_failed(
                frame_name="ops",
                message="bad",
            )
        )
    elif reason == "runtime":
        payload = CodegenExecutionResult.runtime_failed(
            frame_name="ops",
            runtime_error="boom",
        ).to_payload()
    elif reason == "validation_failed":
        payload = CodegenExecutionResult.validation_failed(
            frame_name="ops",
            validation_issues=("bad",),
        ).to_payload()
    else:
        payload = CodegenExecutionResult.executed(
            frame_name="ops",
            result=1,
        ).to_payload()

    if expected_reason is None:
        assert payload["accepted"] is True
    else:
        assert payload["reason"] == expected_reason
