import builtins
import sys
from unittest.mock import MagicMock

import pytest

from melder.crystallizer.synthetic_module import SyntheticModule
from melder.nexus.rift.command_system.codegen_command_system import (
    CodegenCommandSystem,
)


_GOOD_SOURCE = (
    "class Tool:\n"
    "    def answer(self) -> int:\n"
    "        return 42\n"
)
_BROKEN_SOURCE = "raise RuntimeError('exec boom')\n"


def _make_command_system(*, accepted: bool) -> CodegenCommandSystem:
    """
    Build one CodegenCommandSystem over a mocked engine and room.

    Contract:
        - The mocked engine's `validate_codegen_request` returns a
          (context, result) pair whose `accepted` flag is caller-chosen.
        - `report_validation_result` returns a marker payload so the verb's
          passthrough of the validator verdict is observable.
        - Room/workstation collaborators are MagicMock: the verb's envelope
          (action hooks, gate tickets, memory emission) degrades to no-ops.

    Args:
        accepted:
            Validation verdict the mocked engine reports.

    Returns:
        CodegenCommandSystem: Verb-ready command system.
    """
    engine = MagicMock()
    validation_result = MagicMock()
    validation_result.accepted = accepted
    transaction_context = MagicMock()
    transaction_context.projection = None
    engine.validate_codegen_request.return_value = (transaction_context, validation_result)
    engine.build_materialize_builtins.return_value = dict(vars(builtins))
    engine.report_validation_result.return_value = {"verdict_marker": accepted}
    command_system = CodegenCommandSystem(
        rift=MagicMock(),
        space=MagicMock(),
        workstation=MagicMock(),
        codegen_system=engine,
    )
    return command_system


@pytest.fixture(autouse=True)
def clean_materialized_modules():
    """
    Tear down any module this test file materializes, for isolation.
    """
    yield
    for name in ("codegen_probe_tool", "codegen_probe_broken"):
        module = SyntheticModule._registered_modules_by_name.get(name)
        if module is not None and not module.cleaned:
            module.cleanup()
        sys.modules.pop(name, None)


def test_accepted_source_materializes_into_a_live_module() -> None:
    """
    The Progenitor act: accepted source becomes a registered, published,
    executed, importable SyntheticModule and the payload names its identity.
    """
    command_system = _make_command_system(accepted=True)
    payload = command_system.materialize_codegen(
        _GOOD_SOURCE,
        module_name="codegen_probe_tool",
        frame_name="frame-a",
    )
    assert payload["materialized"] is True
    assert payload["module_name"] == "codegen_probe_tool"
    assert payload["module_file"] == "synthetic://codegen_probe_tool.py"
    assert "Tool" in payload["export_names"]
    assert payload["validation"] == {"verdict_marker": True}
    live = sys.modules["codegen_probe_tool"]
    assert live.__dict__["Tool"]().answer() == 42


def test_rejected_validation_refuses_without_registry_mutation() -> None:
    """
    Validation-gated contract: a rejected verdict answers with the
    validator's payload and materializes nothing.
    """
    command_system = _make_command_system(accepted=False)
    payload = command_system.materialize_codegen(
        _GOOD_SOURCE,
        module_name="codegen_probe_tool",
        frame_name="frame-a",
    )
    assert payload["materialized"] is False
    assert payload["validation"] == {"verdict_marker": False}
    assert "codegen_probe_tool" not in sys.modules
    assert "codegen_probe_tool" not in SyntheticModule._registered_modules_by_name


def test_exec_failure_tears_the_module_back_down() -> None:
    """
    R8 no-half-published law: source that raises during exec propagates the
    error AND leaves no registry entry, no sys.modules entry.
    """
    command_system = _make_command_system(accepted=True)
    with pytest.raises(RuntimeError, match="exec boom"):
        command_system.materialize_codegen(
            _BROKEN_SOURCE,
            module_name="codegen_probe_broken",
            frame_name="frame-a",
        )
    assert "codegen_probe_broken" not in sys.modules
    assert "codegen_probe_broken" not in SyntheticModule._registered_modules_by_name


def test_illegal_module_names_refuse_with_value_error() -> None:
    """
    Input contract: module_name must be dotted-identifier legal; empty
    inputs refuse the same way the sibling verbs do.
    """
    command_system = _make_command_system(accepted=True)
    with pytest.raises(ValueError):
        command_system.materialize_codegen(
            _GOOD_SOURCE,
            module_name="not-legal-name",
            frame_name="frame-a",
        )
    with pytest.raises(ValueError):
        command_system.materialize_codegen(
            "",
            module_name="fine_name",
            frame_name="frame-a",
        )


def test_verb_is_advertised() -> None:
    """
    Discoverability law: the room's presentation tuple names the new verb.
    """
    assert (
        "materialize_codegen"
        in CodegenCommandSystem._CODEGEN_COMMAND_METHOD_NAMES
    )


def test_a_loaded_module_name_is_refused_before_any_publication() -> None:
    """
    Contract (D-20, N11): an accepted materialize of a name already in `sys.modules` answers a refusal payload and
    leaves the loaded module in place; no SyntheticModule is registered.
    """
    import json

    command_system = _make_command_system(accepted=True)

    payload = command_system.materialize_codegen(
        "value = 1\n",
        module_name="json",
        frame_name="frame-a",
    )

    assert payload["materialized"] is False
    assert "already loaded" in payload["refusal"]
    assert sys.modules["json"] is json
    assert "json" not in SyntheticModule._registered_modules_by_name


def test_materialized_source_runs_with_the_engines_room_builtins() -> None:
    """
    Contract (D-20): the module's `__builtins__` is the mapping the engine builds for the room.
    """
    command_system = _make_command_system(accepted=True)
    room_builtins = command_system._require_codegen_system().build_materialize_builtins.return_value

    command_system.materialize_codegen(
        "value = 1\n",
        module_name="codegen_probe_tool",
        frame_name="frame-a",
    )

    assert sys.modules["codegen_probe_tool"].__dict__["__builtins__"] is room_builtins
