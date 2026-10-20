"""
What the codegen room's profiles stop around Melder's core today (core-protection review, 2026-10-10).

Purpose:
    Agent code reaches the runtime through a codegen room, whose frame's codegen ACL profile decides
    what the code may import and call. The review's protected-core question depends on what those
    profiles stop today, so this file pins it in two kinds of test:
    - Characterization tests pin what works: no profile names `melder` in a deny list, so an import of
      it is refused only by the imports-off rule (safe) or by an import allowlist that leaves it out
      (hybrid, precision, permissive) and full_access accepts it; and the hybrid profile refuses
      import statements of the roots its deny list names.
    - Two known gaps are written as the contract their profiles document, under xfail(strict=True):
      the safe profile documents that it denies writes, yet agent code writes files with the `open`
      builtin; the hybrid profile denies subprocess, socket and importlib, yet `__import__` loads them,
      also with the precision overlay. STRICT ON PURPOSE: when a gap is closed its test starts
      passing, strict turns that into a failure, and whoever closed it must delete the marker. Do not
      loosen these assertions to make them pass.
    Characterization, not protection: the profiles run in the same process as the code they check, so
    they are policy and defence in depth, not a security boundary, and a green run here does not mean
    the core is protected.

Runs only on 3.14t (melder package root import chain).
"""
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Optional, Tuple

import pytest

from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)

if TYPE_CHECKING:
    from melder.aether.conduit.conduit import Conduit
    from melder.nexus.rift.command_system.codegen_command_system import CodegenCommandSystem


@pytest.fixture(autouse=True)
def isolated_runtime() -> Iterator[None]:
    """
    Run each test against fresh runtime singletons.

    Yields:
        None.
    """
    reset_runtime_singletons()
    yield
    reset_runtime_singletons()


def _codegen_room(
        profile_name: str,
        precision_profile_name: Optional[str] = None,
) -> Tuple[Conduit, CodegenCommandSystem]:
    """
    Open a codegen room on frame "ops" governed by one standard codegen profile.

    Args:
        profile_name: Standard codegen profile (safe, hybrid, permissive or full_access).
        precision_profile_name: Optional precision overlay applied on top of the profile.

    Returns:
        Tuple[Conduit, CodegenCommandSystem]: The frame's root conduit (the caller cleans it) and the
            room's command system.
    """
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    codegen_change = nexus.get_frame_acl_builder("ops").begin_codegen_change(
        reason="core_boundary",
    )
    codegen_change.use_profile(profile_name)
    if precision_profile_name is not None:
        codegen_change.use_precision_profile(precision_profile_name)
    codegen_change.commit_change()
    rift.create_frame_link("ops")
    return conduit, rift.space.command_system


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted", "message_fragment"),
    [
        ("safe", None, False, "Import statements are not allowed"),
        ("hybrid", None, False, "Import root 'melder' is not allowed"),
        ("hybrid", "precision", False, "Import root 'melder' is not allowed"),
        ("permissive", None, False, "Import root 'melder' is not allowed"),
        ("full_access", None, True, None),
    ],
)
def test_importing_melder_is_refused_unless_the_profile_is_full_access(
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
        message_fragment: Optional[str],
) -> None:
    """
    Contract: an `import melder` statement is refused by the import gate under every standard
    profile but full_access - by the imports-off rule under safe and by the import allowlists
    elsewhere, since no profile lists `melder` as a denied root.
    """
    conduit, command_system = _codegen_room(profile_name, precision_profile_name)
    try:
        result = command_system.validate_codegen("import melder\nresult = 1", frame_name="ops")
    finally:
        conduit.cleanup()

    assert result["accepted"] is accepted
    if message_fragment is not None:
        assert message_fragment in result["validation_issues"][0]


@pytest.mark.parametrize(
    "module_name",
    ["subprocess", "socket", "importlib", "ctypes", "asyncio", "builtins"],
)
def test_hybrid_refuses_import_statements_of_its_denied_roots(module_name: str) -> None:
    """
    Contract: the hybrid profile's import gate refuses an import statement of each root on its
    deny list, naming the root.
    """
    conduit, command_system = _codegen_room("hybrid")
    try:
        result = command_system.validate_codegen(
            "import {0}\nresult = 1".format(module_name),
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert result["accepted"] is False
    assert "Import root '{0}' is not allowed".format(module_name) in result["validation_issues"][0]


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "OPEN: no codegen profile denies the open builtin - the runtime __builtins__ is the full "
        "builtins dict minus the profile's deny list, and no validator strategy inspects open or "
        "non-dunder method calls - so agent code in a safe room writes any file the process can "
        "write, although the safe profile documents that it denies writes. Core-protection review, "
        "Note 10. STRICT ON PURPOSE: when the gap is closed this test passes, strict turns that "
        "into a failure, and whoever closed it deletes this marker."
    ),
)
def test_safe_profile_refuses_writing_files(tmp_path: Path) -> None:
    """
    Contract (documented, not yet met): code run in a room under the safe profile cannot write a
    file - the request is refused and nothing is written.
    """
    target = tmp_path / "written_by_codegen.txt"
    conduit, command_system = _codegen_room("safe")
    try:
        result = command_system.execute_codegen(
            "handle = open({0!r}, 'w')\nhandle.write('x')\nhandle.close()\nresult = 1".format(
                str(target)
            ),
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert result["accepted"] is False
    assert not target.exists()


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "OPEN: the import gate reads import statements only, and the compiler denies __import__ only "
        "when imports are off, so __import__ loads the roots the hybrid profile (and the precision "
        "overlay) deny. Core-protection review, Note 11. STRICT ON PURPOSE: when the gap is closed "
        "this test passes, strict turns that into a failure, and whoever closed it deletes this "
        "marker."
    ),
)
@pytest.mark.parametrize(
    ("precision_profile_name", "module_name"),
    [
        (None, "subprocess"),
        (None, "socket"),
        (None, "importlib"),
        ("precision", "subprocess"),
    ],
)
def test_hybrid_refuses_dynamic_imports_of_its_denied_roots(
        precision_profile_name: Optional[str],
        module_name: str,
) -> None:
    """
    Contract (documented, not yet met): a root the hybrid profile denies cannot be loaded by a
    `__import__` call either - the request is refused at validation.
    """
    conduit, command_system = _codegen_room("hybrid", precision_profile_name)
    try:
        result = command_system.validate_codegen(
            "loaded = __import__({0!r})\nresult = 1".format(module_name),
            frame_name="ops",
        )
    finally:
        conduit.cleanup()

    assert result["accepted"] is False
