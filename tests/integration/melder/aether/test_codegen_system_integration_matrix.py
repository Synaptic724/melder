import inspect

import pytest

from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)


@pytest.fixture(autouse=True)
def _isolated_runtime() -> None:
    reset_runtime_singletons()
    yield
    reset_runtime_singletons()


def _build_codegen_space(
        *,
        profile_name: str,
        precision_profile_name: str = None,
):
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    builder = container.frame_acl_builder.begin_codegen_change(
        reason="integration_matrix",
    )
    builder.use_profile(profile_name)
    if precision_profile_name is not None:
        builder.use_precision_profile(precision_profile_name)
    builder.commit_change()
    rift.create_frame_link("ops")
    return nexus, rift, conduit, rift.space


VALIDATION_CASES = [
    ("safe", None, "result = 1", True, None),
    ("safe", None, "import json\nresult = 1", False, "Import statements are not allowed"),
    ("safe", None, "result = command.__dict__", False, "Dunder attribute access '__dict__'"),
    ("safe", None, "result = codegen.execute_codegen('result = 1')", False, "Recursive codegen call 'codegen.execute_codegen'"),
    ("safe", None, "result = mystery", False, "Name 'mystery' is not available"),
    ("hybrid", None, "import json\nresult = 1", True, None),
    ("hybrid", None, "import inspect\nresult = 1", True, None),
    ("hybrid", None, "result = type(command)", False, "Reflection helper 'type'"),
    ("hybrid", None, "result = getattr(command, 'x')", False, "Builtin 'getattr'"),
    ("hybrid", None, "result = viewer.list_nexus_frame_names()", True, None),
    ("hybrid", "precision", "import math\nresult = math.sqrt(4)", True, None),
    ("hybrid", "precision", "import json\nresult = 1", True, None),
    ("hybrid", "precision", "import inspect\nresult = 1", False, "Import root 'inspect' is not allowed"),
    ("hybrid", "precision", "import socket\nresult = 1", False, "Import root 'socket' is not allowed"),
    ("permissive", None, "import socket\nresult = eval('1 + 1')", True, None),
    ("permissive", None, "result = type(command)", True, None),
    ("permissive", None, "result = codegen.execute_codegen('result = 2')['result']", True, None),
    ("full_access", None, "import importlib\nresult = importlib.__name__", True, None),
    ("full_access", None, "result = codegen.execute_codegen('result = 3')['result']", True, None),
    ("full_access", None, "result = getattr(command, '__class__').__name__", True, None),
]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "code", "accepted", "message_fragment"),
    VALIDATION_CASES,
)
def test_integration_codegen_validate_matrix(
        profile_name: str,
        precision_profile_name: str,
        code: str,
        accepted: bool,
        message_fragment: str,
) -> None:
    _, _, conduit, space = _build_codegen_space(
        profile_name=profile_name,
        precision_profile_name=precision_profile_name,
    )
    try:
        result = space.command_system.validate_codegen(code, frame_name="ops")
    finally:
        conduit.cleanup()

    assert result["accepted"] is accepted
    if accepted:
        return
    assert message_fragment in result["validation_issues"][0]


EXECUTION_CASES = [
    ("safe", None, "result = 1", True, 1),
    ("safe", None, "value = 7", True, None),
    ("safe", None, "import json\nresult = 1", False, None),
    ("safe", None, "result = command.__dict__", False, None),
    ("safe", None, "raise ValueError('boom')", False, None),
    ("hybrid", None, "import json\nresult = 1", True, 1),
    ("hybrid", None, "result = viewer.list_nexus_frame_names()", True, ["ops"]),
    ("hybrid", None, "result = type(command)", False, None),
    ("hybrid", None, "result = getattr(command, 'x')", False, None),
    ("hybrid", None, "result = command.link_frame('ops')", True, None),
    ("hybrid", "precision", "import math\nresult = math.sqrt(9)", True, 3.0),
    ("hybrid", "precision", "import inspect\nresult = 1", False, None),
    ("hybrid", "precision", "import socket\nresult = 1", False, None),
    ("hybrid", "precision", "result = 2 + 2", True, 4),
    ("permissive", None, "import socket\nresult = eval('2 + 2')", True, 4),
    ("permissive", None, "result = type(command).__name__", True, "CodegenCommandSystem"),
    ("permissive", None, "result = codegen.execute_codegen('result = 4')['result']", True, 4),
    ("full_access", None, "import importlib\nresult = importlib.__name__", True, "importlib"),
    ("full_access", None, "result = codegen.execute_codegen('result = 5')['result']", True, 5),
    ("full_access", None, "result = getattr(command, '__class__').__name__", True, "CodegenCommandSystem"),
]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "code", "accepted", "expected_result"),
    EXECUTION_CASES,
)
def test_integration_codegen_execute_matrix(
        profile_name: str,
        precision_profile_name: str,
        code: str,
        accepted: bool,
        expected_result: object,
) -> None:
    _, _, conduit, space = _build_codegen_space(
        profile_name=profile_name,
        precision_profile_name=precision_profile_name,
    )
    try:
        result = space.command_system.execute_codegen(code, frame_name="ops")
    finally:
        conduit.cleanup()

    assert result["accepted"] is accepted
    if accepted:
        if expected_result is None:
            assert "result" not in result
        else:
            assert result["result"] == expected_result


def test_integration_codegen_generated_definition_getsource_fails_but_binding_persists() -> None:
    nexus, rift, conduit, space = _build_codegen_space(
        profile_name="full_access",
    )
    code = """
import inspect
conduit = command.get_conduit_by_name("root", frame_name="ops")

class GeneratedService:
    def __init__(self) -> None:
        self.value = 7

    def read(self) -> int:
        return self.value

conduit.begin_transaction("bind")
try:
    spell_id = conduit.bind(
        spell=GeneratedService,
        existence="unique",
        permissions="create",
        spellframe="generated_runtime",
        binding_name="generated_service",
    )
finally:
    conduit.end_transaction("bind")

result = inspect.getsource(GeneratedService)
""".strip()

    try:
        execute_result = space.command_system.execute_codegen(
            code,
            frame_name="ops",
        )
        spell_id = conduit.find_spell_id(
            "generated_runtime",
            "GeneratedService",
            "generated_service",
        )
        spell = conduit.get_spell_by_id(spell_id, "ops")
        outside_error = None
        try:
            inspect.getsource(spell.spell)
        except Exception as exc:
            outside_error = "{0}: {1}".format(exc.__class__.__name__, exc)
    finally:
        conduit.cleanup()

    assert execute_result["accepted"] is False
    assert execute_result["reason"] == "codegen_execution_runtime_failed"
    assert "built-in class" in execute_result["runtime_error"]
    assert spell.spell_name == "GeneratedService"
    assert spell.binding_name == "generated_service"
    assert spell.spellframe == "generated_runtime"
    assert spell.spell_type.name == "SPELL_WITH_BINDING_NAME_WITH_SPELLFRAME"
    assert outside_error is not None
    assert "built-in class" in outside_error


def test_integration_codegen_can_bind_generated_reference_and_use_it_afterward() -> None:
    nexus, rift, conduit, space = _build_codegen_space(
        profile_name="full_access",
    )
    code = """
conduit = command.get_conduit_by_name("root", frame_name="ops")

class GeneratedService:
    def __init__(self) -> None:
        self.value = 7

    def read(self) -> int:
        return self.value

conduit.begin_transaction("bind")
try:
    spell_id = conduit.bind(
        spell=GeneratedService,
        existence="unique",
        permissions="create",
        spellframe="generated_runtime",
        binding_name="generated_service",
    )
finally:
    conduit.end_transaction("bind")

result = spell_id
""".strip()

    try:
        execute_result = space.command_system.execute_codegen(
            code,
            frame_name="ops",
        )
        spell_id = conduit.find_spell_id(
            "generated_runtime",
            "GeneratedService",
            "generated_service",
        )
        creation = conduit.meld(
            spell="GeneratedService",
            spellframe="generated_runtime",
            binding_name="generated_service",
        )
        repeated_creation = conduit.meld(
            spell="GeneratedService",
            spellframe="generated_runtime",
            binding_name="generated_service",
        )
    finally:
        conduit.cleanup()

    assert execute_result["accepted"] is True
    assert execute_result["result"] == spell_id
    assert creation.__class__.__name__ == "GeneratedService"
    assert creation.read() == 7
    assert repeated_creation is creation
