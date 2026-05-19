import pytest

from melder.nexus.rift.codegen_system.codegen_system import CodegenSystem
from tests._codegen_system_support import (
    CodegenSpaceDouble,
    DetachedRiftProjectionOwner,
    build_codegen_projection,
)


@pytest.mark.parametrize(
    ("profile_label", "projection_kwargs", "code", "accepted"),
    [
        ("safe_local", {}, "result = 1", True),
        ("safe_import_reject", {}, "import json\nresult = 1", False),
        ("safe_dunder_reject", {}, "result = command.__dict__", False),
        ("safe_recursive_reject", {}, "result = codegen.execute_codegen('result = 1')", False),
        ("hybrid_json", {"imports_enabled": True, "allowed_import_module_roots": ("json",)}, "import json\nresult = 1", True),
        ("hybrid_reflection_reject", {"imports_enabled": True, "allowed_import_module_roots": ("inspect",)}, "from inspect import signature\nresult = signature(command.link_frame)", False),
        ("precision_math", {"imports_enabled": True, "allowed_import_module_roots": ("math",)}, "import math\nresult = math.sqrt(4)", True),
        ("precision_socket_reject", {"imports_enabled": True, "allowed_import_module_roots": ("math",)}, "import socket\nresult = 1", False),
        ("permissive_eval", {"imports_enabled": True, "allowed_import_module_roots": ("socket",), "unsafe_reflection_allowed": True, "dunder_access_allowed": True, "recursive_codegen_allowed": True}, "import socket\nresult = eval('1 + 1')", True),
        ("full_access_recursive", {"imports_enabled": True, "allowed_import_module_roots": ("importlib",), "unsafe_reflection_allowed": True, "dunder_access_allowed": True, "recursive_codegen_allowed": True}, 'import importlib\nresult = codegen.execute_codegen("result = importlib.__name__")["result"]', True),
    ]
    + [
        (
            "local_case_{0}".format(index),
            {},
            "value_{0} = {0}\nresult = value_{0}".format(index),
            True,
        )
        for index in range(10)
    ],
)
def test_component_codegen_system_validation_matrix(
        profile_label: str,
        projection_kwargs: dict,
        code: str,
        accepted: bool,
) -> None:
    _ = profile_label
    rift = DetachedRiftProjectionOwner()
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        **projection_kwargs
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)
    space.codegen_system = system

    validation_result = system.validate_codegen(code, frame_name="ops")

    assert validation_result.accepted is accepted


@pytest.mark.parametrize(
    ("projection_kwargs", "code", "accepted", "expected_result"),
    [
        ({}, "result = 1", True, 1),
        ({}, "raise ValueError('boom')", False, None),
        ({"imports_enabled": True, "allowed_import_module_roots": ("json",)}, "import json\nresult = 2", True, 2),
        ({"imports_enabled": True, "allowed_import_module_roots": ("json",)}, "import math\nresult = 2", False, None),
        ({"imports_enabled": True, "allowed_import_module_roots": ("socket",), "unsafe_reflection_allowed": True, "dunder_access_allowed": True, "recursive_codegen_allowed": True}, "import socket\nresult = eval('2 + 2')", True, 4),
        ({"imports_enabled": True, "allowed_import_module_roots": ("importlib",), "unsafe_reflection_allowed": True, "dunder_access_allowed": True, "recursive_codegen_allowed": True}, 'import importlib\nresult = codegen.execute_codegen("result = 5")["result"]', True, 5),
        ({}, "value = 7", True, None),
        ({}, "result = command.link_frame('ops')", True, "ops"),
        ({}, "result = viewer.list_nexus_frame_names()", True, ("ops",)),
        ({}, "result = type(command)", False, None),
    ]
    + [
        ({}, "result = {0} + {0}".format(index), True, index + index)
        for index in range(10)
    ],
)
def test_component_codegen_system_execution_matrix(
        projection_kwargs: dict,
        code: str,
        accepted: bool,
        expected_result: object,
) -> None:
    rift = DetachedRiftProjectionOwner()
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        **projection_kwargs
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)
    space.codegen_system = system

    execution_result = system.execute_codegen(code, frame_name="ops")

    assert execution_result.accepted is accepted
    if accepted:
        assert execution_result.result == expected_result


@pytest.mark.parametrize(
    ("projection_kwargs", "expected_names", "denied_builtin_name"),
    [
        ({}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"imports_enabled": True}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"denied_builtin_names": ("eval", "exec")}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"allowed_import_module_roots": ("json",)}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"recursive_codegen_allowed": True}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"unsafe_reflection_allowed": True}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"dunder_access_allowed": True}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"imports_enabled": True, "allowed_import_module_roots": ("json",), "denied_builtin_names": ("eval", "exec")}, ("viewer", "workstation", "target", "command", "codegen"), "eval"),
        ({"imports_enabled": True, "allowed_import_module_roots": ("json",), "denied_builtin_names": ("compile",)}, ("viewer", "workstation", "target", "command", "codegen"), "compile"),
        ({}, ("viewer", "workstation", "target", "command", "codegen"), "getattr"),
    ]
    + [
        ({}, ("viewer", "workstation", "target", "command", "codegen"), builtin_name)
        for builtin_name in ("globals", "locals", "vars", "setattr", "delattr", "__import__", "breakpoint", "compile", "dir", "eval")
    ],
)
def test_component_codegen_system_namespace_matrix(
        projection_kwargs: dict,
        expected_names: tuple,
        denied_builtin_name: str,
) -> None:
    rift = DetachedRiftProjectionOwner()
    effective_kwargs = dict(projection_kwargs)
    if "denied_builtin_names" not in effective_kwargs:
        effective_kwargs["denied_builtin_names"] = (denied_builtin_name,)
    rift._codegen_projections_by_frame_name["ops"] = build_codegen_projection(
        **effective_kwargs
    )
    space = CodegenSpaceDouble()
    system = CodegenSystem(rift=rift, space=space)
    space.codegen_system = system

    context = system._build_transaction_context("result = 1", frame_name="ops")
    namespace = system._build_namespace(context)

    assert tuple(sorted(context.namespace_configuration.exposed_names)) == tuple(
        sorted(expected_names)
    )
    assert denied_builtin_name not in namespace.globals_dict["__builtins__"]


@pytest.mark.parametrize(
    ("mode", "code", "expected_event_count", "expected_last_event"),
    [
        ("validate", "result = 1", 2, "codegen_validation_finished"),
        ("validate", "import json\nresult = 1", 2, "codegen_validation_finished"),
        ("execute", "result = 1", 4, "codegen_execution_finished"),
        ("execute", "raise ValueError('boom')", 4, "codegen_execution_finished"),
        ("execute", "import json\nresult = 1", 4, "codegen_execution_finished"),
        ("execute", "result = codegen.execute_codegen('result = 1')", 8, "codegen_execution_finished"),
        ("validate", "global value\nvalue = 1", 2, "codegen_validation_finished"),
        ("execute", "value = 7", 4, "codegen_execution_finished"),
        ("execute", "result = command.link_frame('ops')", 4, "codegen_execution_finished"),
        ("validate", "result = viewer.list_nexus_frame_names()", 2, "codegen_validation_finished"),
    ]
    + [
        ("execute", "result = {0}".format(index), 4, "codegen_execution_finished")
        for index in range(10)
    ],
)
def test_component_codegen_system_observability_matrix(
        mode: str,
        code: str,
        expected_event_count: int,
        expected_last_event: str,
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

    if mode == "validate":
        system.validate_codegen_request(code, frame_name="ops")
    else:
        system.execute_codegen_request(code, frame_name="ops")

    assert len(space.event_system.events) == expected_event_count
    assert space.event_system.events[-1]["event_type"] == expected_last_event
