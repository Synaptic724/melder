import ast

import pytest

from melder.aether.nexus.rift.codegen_system.codegen_transaction_context import (
    CodegenTransactionContext,
)
from melder.aether.nexus.rift.codegen_system.validation.codegen_validator import (
    CodegenValidator,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_ast_structure_strategy import (
    CodegenAstStructureStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_attribute_access_strategy import (
    CodegenAttributeAccessStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_builtin_policy_strategy import (
    CodegenBuiltinPolicyStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_import_policy_strategy import (
    CodegenImportPolicyStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_name_resolution_strategy import (
    CodegenNameResolutionStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_recursive_control_strategy import (
    CodegenRecursiveControlStrategy,
)
from melder.aether.nexus.rift.codegen_system.validation.strategies.codegen_reflection_policy_strategy import (
    CodegenReflectionPolicyStrategy,
)
from tests._codegen_system_support import build_namespace_configuration


def _context(
        code: str,
        **configuration_kwargs,
) -> CodegenTransactionContext:
    return CodegenTransactionContext(
        frame_name="ops",
        code=code,
        namespace_configuration=build_namespace_configuration(
            frame_name="ops",
            **configuration_kwargs,
        ),
    )


AST_STRUCTURE_INVALID_CASES = [
    ("async def run():\n    return 1", "Async function definitions"),
    ("async def run():\n    await other()", "Async function definitions"),
    ("await other()", "await expressions"),
    ("async for item in items:\n    result = item", "async for statements"),
    ("async with lock:\n    result = 1", "async with statements"),
    ("global result\nresult = 1", "global statements"),
    ("def outer():\n    value = 1\n    def inner():\n        nonlocal value\n        return value", "nonlocal statements"),
]


@pytest.mark.parametrize(
    ("code", "message_fragment"),
    AST_STRUCTURE_INVALID_CASES,
)
def test_unit_codegen_ast_structure_strategy_rejects_invalid_shapes(
        code: str,
        message_fragment: str,
) -> None:
    strategy = CodegenAstStructureStrategy()
    context = _context(code)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is not None
    assert result.accepted is False
    assert message_fragment in result.validation_issues[0]


@pytest.mark.parametrize(
    "code",
    [
        "result = 1",
        "def helper(x: int) -> int:\n    return x + 1\nresult = helper(2)",
        "class Helper:\n    value: int\n\nresult = Helper",
        "try:\n    result = 1\nexcept ValueError:\n    result = 2",
        "values = [item for item in range(3)]\nresult = values",
    ],
)
def test_unit_codegen_ast_structure_strategy_accepts_normal_python_shapes(
        code: str,
) -> None:
    strategy = CodegenAstStructureStrategy()
    context = _context(code)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is None


IMPORT_POLICY_CASES = [
    ("import json\nresult = 1", {}, False, "Import statements are not allowed"),
    ("from math import sqrt\nresult = sqrt(4)", {}, False, "Import-from statements are not allowed"),
    (
        "import json\nresult = 1",
        {"imports_enabled": True, "allowed_import_module_roots": ("json",)},
        True,
        None,
    ),
    (
        "import math\nresult = 1",
        {"imports_enabled": True, "allowed_import_module_roots": ("json",)},
        False,
        "Import root 'math' is not allowed",
    ),
    (
        "import subprocess\nresult = 1",
        {"imports_enabled": True, "denied_import_module_roots": ("subprocess",)},
        False,
        "Import root 'subprocess' is not allowed",
    ),
    (
        "from .math import sqrt\nresult = sqrt(4)",
        {"imports_enabled": True, "allowed_import_module_roots": ("math",)},
        False,
        "Relative imports are not allowed",
    ),
    (
        "from math import *\nresult = 1",
        {"imports_enabled": True, "allowed_import_module_roots": ("math",)},
        False,
        "Wildcard imports are not allowed",
    ),
]


@pytest.mark.parametrize(
    ("code", "configuration_kwargs", "accepted", "message_fragment"),
    IMPORT_POLICY_CASES
    + [
        (
            "import {0}\nresult = 1".format(module_name),
            {"imports_enabled": True, "allowed_import_module_roots": (module_name,)},
            True,
            None,
        )
        for module_name in (
            "json",
            "math",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "re",
            "statistics",
            "typing",
        )
    ]
    + [
        (
            "import {0}\nresult = 1".format(module_name),
            {"imports_enabled": True, "denied_import_module_roots": (module_name,)},
            False,
            "Import root '{0}' is not allowed".format(module_name),
        )
        for module_name in (
            "socket",
            "subprocess",
            "ctypes",
            "importlib",
            "builtins",
            "asyncio",
            "inspect",
            "http",
            "ssl",
            "pickle",
        )
    ],
)
def test_unit_codegen_import_policy_strategy_matrix(
        code: str,
        configuration_kwargs: dict,
        accepted: bool,
        message_fragment: str,
) -> None:
    strategy = CodegenImportPolicyStrategy()
    context = _context(code, **configuration_kwargs)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    if accepted:
        assert result is None
        return
    assert result is not None
    assert result.accepted is False
    assert message_fragment in result.validation_issues[0]


@pytest.mark.parametrize(
    "builtin_name",
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
        "breakpoint",
        "__import__",
    ),
)
def test_unit_codegen_builtin_policy_strategy_rejects_denied_builtins(
        builtin_name: str,
) -> None:
    strategy = CodegenBuiltinPolicyStrategy()
    code = "result = {0}()".format(builtin_name)
    if builtin_name not in ("globals", "locals", "vars", "dir", "breakpoint", "__import__"):
        code = "{0}('value')".format(builtin_name)
    if builtin_name == "breakpoint":
        code = "breakpoint()"
    if builtin_name == "__import__":
        code = "__import__('json')"
    context = _context(code, denied_builtin_names=(builtin_name,))

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is not None
    assert result.accepted is False
    assert "Builtin '{0}' is not allowed".format(builtin_name) in (
        result.validation_issues[0]
    )


@pytest.mark.parametrize(
    "builtin_name",
    ("len", "sum", "min", "max", "sorted", "range", "print"),
)
def test_unit_codegen_builtin_policy_strategy_ignores_allowed_builtins(
        builtin_name: str,
) -> None:
    strategy = CodegenBuiltinPolicyStrategy()
    code = "result = {0}([1, 2, 3])".format(builtin_name)
    if builtin_name == "range":
        code = "result = list(range(3))"
    if builtin_name == "print":
        code = "print('x')"
    context = _context(code, denied_builtin_names=("eval",))

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is None


NAME_RESOLUTION_ALLOWED_CASES = [
    "viewer.list_nexus_frame_names()",
    "workstation.bind_object('x', 1)",
    "command.link_frame('ops')",
    "result = codegen",
    "result = 1",
    "value = 1\nresult = value",
    "def helper() -> int:\n    return 1\nresult = helper()",
    "def helper(value: int, prefix: str = 'ok') -> str:\n    return '{0}:{1}'.format(prefix, value)\nresult = helper(2)",
    "class Helper:\n    pass\nhelper = Helper()\nresult = helper",
    "class Helper:\n    def run(self, value: int) -> int:\n        return value\nhelper = Helper()\nresult = helper.run(3)",
    "import json\nresult = json.dumps({'x': 1})",
    "from math import sqrt\nresult = sqrt(4)",
]


@pytest.mark.parametrize("code", NAME_RESOLUTION_ALLOWED_CASES)
def test_unit_codegen_name_resolution_strategy_accepts_known_names(
        code: str,
) -> None:
    strategy = CodegenNameResolutionStrategy()
    context = _context(
        code,
        imports_enabled=True,
        allowed_import_module_roots=("json", "math"),
    )

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is None


@pytest.mark.parametrize(
    ("code", "unknown_name"),
    [
        ("result = mystery", "mystery"),
        ("viewer.list_nexus_frame_names()\nresult = hidden_name", "hidden_name"),
        ("alias = unknown\nresult = alias", "unknown"),
        ("result = math.sqrt(4)", "math"),
        ("result = imported_name", "imported_name"),
        ("result = reflection_helper", "reflection_helper"),
    ]
    + [
        ("result = unknown_name_{0}".format(index), "unknown_name_{0}".format(index))
        for index in range(20)
    ],
)
def test_unit_codegen_name_resolution_strategy_rejects_unknown_names(
        code: str,
        unknown_name: str,
) -> None:
    strategy = CodegenNameResolutionStrategy()
    context = _context(code)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is not None
    assert result.accepted is False
    assert "Name '{0}' is not available".format(unknown_name) in (
        result.validation_issues[0]
    )


@pytest.mark.parametrize(
    ("code", "message_fragment"),
    [
        ("result = command.__dict__", "Dunder attribute access '__dict__'"),
        ("result = viewer.__class__", "Dunder attribute access '__class__'"),
        ("result = workstation.__mro__", "Dunder attribute access '__mro__'"),
        ("value = object()\nresult = value.__dict__", "Dunder attribute access '__dict__'"),
        ("class Helper:\n    pass\nresult = Helper.__bases__", "Dunder attribute access '__bases__'"),
        ("def run():\n    return command.__getattribute__('x')", "Dunder attribute access '__getattribute__'"),
    ],
)
def test_unit_codegen_attribute_access_strategy_rejects_dunder_access(
        code: str,
        message_fragment: str,
) -> None:
    strategy = CodegenAttributeAccessStrategy()
    context = _context(code)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is not None
    assert result.accepted is False
    assert message_fragment in result.validation_issues[0]


@pytest.mark.parametrize(
    "code",
    [
        "result = command.link_frame",
        "class Helper:\n    value = 1\nresult = Helper.value",
        "result = workstation.bind_object",
        "value = object()\nresult = value.attr",
        "result = viewer.list_nexus_frame_names",
    ],
)
def test_unit_codegen_attribute_access_strategy_accepts_non_dunder_access(
        code: str,
) -> None:
    strategy = CodegenAttributeAccessStrategy()
    context = _context(code, allow_dunder_access=False)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is None


REFLECTION_REJECT_CASES = [
    ("result = getattr(command, 'x')", "Reflection helper 'getattr'"),
    ("result = setattr(command, 'x', 1)", "Reflection helper 'setattr'"),
    ("result = delattr(command, 'x')", "Reflection helper 'delattr'"),
    ("result = dir(command)", "Reflection helper 'dir'"),
    ("result = globals()", "Reflection helper 'globals'"),
    ("result = locals()", "Reflection helper 'locals'"),
    ("result = vars()", "Reflection helper 'vars'"),
    ("result = type(command)", "Reflection helper 'type'"),
    ("import inspect\nresult = inspect.signature(command.link_frame)", "Reflection helper 'inspect.signature'"),
    ("import inspect as i\nresult = i.getmembers(command)", "Reflection helper 'i.getmembers'"),
    ("from inspect import signature\nresult = signature(command.link_frame)", "Reflection helper 'signature'"),
    ("import importlib\nresult = importlib.import_module('math')", "Reflection helper 'importlib.import_module'"),
    ("import builtins\nresult = builtins.globals()", "Reflection helper 'builtins.globals'"),
    ("helper = getattr\nresult = helper(command, 'x')", "Reflection helper 'helper'"),
]


@pytest.mark.parametrize(
    ("code", "message_fragment"),
    REFLECTION_REJECT_CASES
    + [
        (
            "import inspect as alias_{0}\nresult = alias_{0}.signature(command.link_frame)".format(index),
            "Reflection helper 'alias_{0}.signature'".format(index),
        )
        for index in range(10)
    ]
    + [
        (
            "from inspect import signature as sig_{0}\nresult = sig_{0}(command.link_frame)".format(index),
            "Reflection helper 'sig_{0}'".format(index),
        )
        for index in range(10)
    ],
)
def test_unit_codegen_reflection_policy_strategy_rejects_reflection_helpers(
        code: str,
        message_fragment: str,
) -> None:
    strategy = CodegenReflectionPolicyStrategy()
    context = _context(
        code,
        imports_enabled=True,
        allowed_import_module_roots=("inspect", "importlib", "builtins"),
        allow_unsafe_reflection=False,
    )

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is not None
    assert result.accepted is False
    assert message_fragment in result.validation_issues[0]


@pytest.mark.parametrize(
    "code",
    [
        "result = getattr(command, 'x')",
        "import inspect\nresult = inspect.signature(command.link_frame)",
        "from inspect import signature\nresult = signature(command.link_frame)",
        "result = type(command)",
        "import importlib\nresult = importlib.import_module('math')",
    ],
)
def test_unit_codegen_reflection_policy_strategy_accepts_when_enabled(
        code: str,
) -> None:
    strategy = CodegenReflectionPolicyStrategy()
    context = _context(
        code,
        imports_enabled=True,
        allowed_import_module_roots=("inspect", "importlib", "builtins", "math"),
        allow_unsafe_reflection=True,
    )

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    assert result is None


@pytest.mark.parametrize(
    ("code", "accepted"),
    [
        ("result = codegen.execute_codegen('result = 1')", False),
        ("result = codegen.validate_codegen('result = 1')", False),
        ("alias = codegen\nresult = alias.execute_codegen('result = 1')", True),
        ("helper = codegen.execute_codegen\nresult = helper('result = 1')", True),
        ("result = command.link_frame('ops')", True),
        ("result = 1", True),
    ]
    + [
        (
            "result = codegen.execute_codegen('result = {0}')".format(index),
            False,
        )
        for index in range(6)
    ],
)
def test_unit_codegen_recursive_control_strategy_matrix(
        code: str,
        accepted: bool,
) -> None:
    strategy = CodegenRecursiveControlStrategy()
    context = _context(code, allow_recursive_codegen=False)

    result = strategy.validate(context, ast.parse(code, mode="exec"))

    if accepted:
        assert result is None
        return
    assert result is not None
    assert result.accepted is False
    assert "Recursive codegen call" in result.validation_issues[0]


@pytest.mark.parametrize(
    ("code", "accepted", "reason"),
    [
        ("result = 1", True, "codegen_validation_accepted"),
        ("import json\nresult = 1", True, "codegen_validation_accepted"),
        ("result = getattr(command, 'x')", False, "codegen_validation_failed"),
        ("result = command.__dict__", False, "codegen_validation_failed"),
        ("global x\nx = 1", False, "codegen_validation_failed"),
        ("def helper(x: int) -> int:\n    return x + 1\nresult = helper(2)", True, "codegen_validation_accepted"),
        ("result = unknown_name", False, "codegen_validation_failed"),
        ("result = codegen.execute_codegen('result = 1')", False, "codegen_validation_failed"),
    ]
    + [
        (
            "result = builtin_{0}".format(index),
            False,
            "codegen_validation_failed",
        )
        for index in range(5)
    ],
)
def test_unit_codegen_validator_matrix(
        code: str,
        accepted: bool,
        reason: str,
) -> None:
    validator = CodegenValidator()
    context = _context(
        code,
        imports_enabled=True,
        allowed_import_module_roots=("json",),
        denied_builtin_names=("builtin_0", "builtin_1", "builtin_2", "builtin_3", "builtin_4"),
    )

    result = validator.validate(context)

    assert result.accepted is accepted
    assert result.reason == reason
