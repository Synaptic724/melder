"""
What the codegen room's profiles stop around Melder's core today (core-protection review, 2026-10-10).

Purpose:
    Agent code reaches the runtime through a codegen room, whose frame's codegen ACL profile decides
    what the code may import and call. The review's protected-core question depends on what those
    profiles stop today, so this file pins it in three kinds of test:
    - Characterization tests pin what works: no profile names `melder` in a deny list, so an import of
      it is refused only by the imports-off rule (safe) or by an import allowlist that leaves it out
      (hybrid, precision, permissive) and full_access accepts it; and the hybrid profile refuses
      import statements of the roots its deny list names.
    - File-posture tests pin what each profile does with files: `open` - called or only named - is
      refused under safe, hybrid and the precision overlay, and under the engine's default posture for a
      frame the room holds no projection for, and runs under permissive and full_access; `io.open`,
      `os.open` and pathlib writes follow each profile's import list. `test_safe_profile_refuses_writing_files`
      was the strict xfail for this gap (D-10) until the safe profile denied `open`.
    - One known gap is written as the contract its profiles document, under xfail(strict=True): the
      hybrid profile denies subprocess, socket and importlib, yet `__import__` loads them, also with the
      precision overlay. STRICT ON PURPOSE: when the gap is closed its test starts passing, strict turns
      that into a failure, and whoever closed it must delete the marker. Do not loosen these assertions
      to make them pass.
    Characterization, not protection: the profiles run in the same process as the code they check, so
    they are policy and defence in depth, not a security boundary, and a green run here does not mean
    the core is protected.

Runs only on 3.14t (melder package root import chain).
"""
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Iterator, Optional, Tuple

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


def test_safe_profile_refuses_writing_files(tmp_path: Path) -> None:
    """
    Contract: code run in a room under the safe profile that writes a file with `open` is refused, and
    nothing is written. This was the strict xfail for defect D-10 (core-protection review, Note 10) until
    the safe profile denied `open`.
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


def _execute_in_room(
        profile_name: str,
        precision_profile_name: Optional[str],
        code: str,
        *,
        frame_name: str = "ops",
) -> Dict[str, object]:
    """
    Execute one request in a fresh codegen room on frame "ops" and clean the room up.

    Args:
        profile_name: Standard codegen profile of frame "ops".
        precision_profile_name: Optional precision overlay applied on top of the profile.
        code: Room code to execute.
        frame_name: Frame the request names. The room links "ops" only, so any other name runs under the
            engine's default posture for a frame without a projection.

    Returns:
        Dict[str, object]: The room's execution payload.
    """
    conduit, command_system = _codegen_room(profile_name, precision_profile_name)
    try:
        return command_system.execute_codegen(code, frame_name=frame_name)
    finally:
        conduit.cleanup()


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted"),
    [
        ("safe", None, False),
        ("hybrid", None, False),
        ("hybrid", "precision", False),
        ("permissive", None, True),
        ("full_access", None, True),
    ],
)
def test_open_writes_a_file_only_under_permissive_and_full_access(
        tmp_path: Path,
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
) -> None:
    """
    Contract (D-10): a call to `open` that writes a file is refused under safe, hybrid and the precision
    overlay - by the builtin gate, naming `open`, with nothing written - and runs under permissive and
    full_access, whose file posture is open by design.
    """
    target = tmp_path / "written_by_codegen.txt"
    payload = _execute_in_room(
        profile_name,
        precision_profile_name,
        "handle = open({0!r}, 'w')\nhandle.write('x')\nhandle.close()\nresult = 1".format(str(target)),
    )

    assert payload["accepted"] is accepted
    if accepted:
        assert target.read_text() == "x"
    else:
        assert "Builtin 'open' is not allowed in this codegen mode." in payload["validation_issues"][0]
        assert not target.exists()


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted"),
    [
        ("safe", None, False),
        ("hybrid", None, False),
        ("hybrid", "precision", False),
        ("permissive", None, True),
        ("full_access", None, True),
    ],
)
def test_open_reads_a_file_only_under_permissive_and_full_access(
        tmp_path: Path,
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
) -> None:
    """
    Contract (D-10): a call to `open` that reads a file is refused where `open` is denied, naming `open`, and
    returns the file's text under permissive and full_access.
    """
    source = tmp_path / "read_by_codegen.txt"
    source.write_text("kept")
    payload = _execute_in_room(
        profile_name,
        precision_profile_name,
        "handle = open({0!r})\nresult = handle.read()\nhandle.close()".format(str(source)),
    )

    assert payload["accepted"] is accepted
    if accepted:
        assert payload["result"] == "kept"
    else:
        assert "Builtin 'open' is not allowed in this codegen mode." in payload["validation_issues"][0]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name"),
    [
        ("safe", None),
        ("hybrid", None),
        ("hybrid", "precision"),
    ],
)
def test_a_bare_reference_to_open_is_refused_where_open_is_denied(
        profile_name: str,
        precision_profile_name: Optional[str],
) -> None:
    """
    Contract (D-10): where `open` is denied, naming it without calling it (`reader = open`) is refused too - by
    name resolution, because `open` is no longer an available builtin - so it cannot be called under another name.
    """
    conduit, command_system = _codegen_room(profile_name, precision_profile_name)
    try:
        result = command_system.validate_codegen("reader = open\nresult = 1", frame_name="ops")
    finally:
        conduit.cleanup()

    assert result["accepted"] is False
    assert "Name 'open' is not available in the codegen namespace." in result["validation_issues"][0]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted", "message_fragment"),
    [
        ("safe", None, False, "Import statements are not allowed"),
        ("hybrid", None, False, "Import root 'io' is not allowed"),
        ("hybrid", "precision", False, "Import root 'io' is not allowed"),
        ("permissive", None, True, None),
        ("full_access", None, True, None),
    ],
)
def test_io_open_writes_a_file_only_where_the_import_list_admits_io(
        tmp_path: Path,
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
        message_fragment: Optional[str],
) -> None:
    """
    Contract (D-10 file posture): `io.open` writes a file only where the import gate admits `io` - permissive
    and full_access; safe refuses every import and hybrid and the precision overlay leave `io` off their lists.
    """
    target = tmp_path / "written_by_codegen.txt"
    payload = _execute_in_room(
        profile_name,
        precision_profile_name,
        "import io\nhandle = io.open({0!r}, 'w')\nhandle.write('x')\nhandle.close()\nresult = 1".format(
            str(target)
        ),
    )

    assert payload["accepted"] is accepted
    assert target.exists() is accepted
    if message_fragment is not None:
        assert message_fragment in payload["validation_issues"][0]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted", "message_fragment"),
    [
        ("safe", None, False, "Import statements are not allowed"),
        ("hybrid", None, False, "Import root 'os' is not allowed"),
        ("hybrid", "precision", False, "Import root 'os' is not allowed"),
        ("permissive", None, True, None),
        ("full_access", None, True, None),
    ],
)
def test_os_open_writes_a_file_only_where_the_import_list_admits_os(
        tmp_path: Path,
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
        message_fragment: Optional[str],
) -> None:
    """
    Contract (D-10 file posture): `os.open` writes a file only where the import gate admits `os` - permissive
    and full_access; safe refuses every import and hybrid and the precision overlay leave `os` off their lists.
    """
    target = tmp_path / "written_by_codegen.txt"
    payload = _execute_in_room(
        profile_name,
        precision_profile_name,
        (
            "import os\n"
            "descriptor = os.open({0!r}, os.O_WRONLY | os.O_CREAT, 0o600)\n"
            "os.write(descriptor, b'x')\n"
            "os.close(descriptor)\n"
            "result = 1"
        ).format(str(target)),
    )

    assert payload["accepted"] is accepted
    assert target.exists() is accepted
    if message_fragment is not None:
        assert message_fragment in payload["validation_issues"][0]


@pytest.mark.parametrize(
    ("profile_name", "precision_profile_name", "accepted", "message_fragment"),
    [
        ("safe", None, False, "Import statements are not allowed"),
        ("hybrid", None, False, "Import root 'pathlib' is not allowed"),
        ("hybrid", "precision", False, "Import root 'pathlib' is not allowed"),
        ("permissive", None, True, None),
        ("full_access", None, True, None),
    ],
)
def test_pathlib_writes_a_file_only_where_the_import_list_admits_pathlib(
        tmp_path: Path,
        profile_name: str,
        precision_profile_name: Optional[str],
        accepted: bool,
        message_fragment: Optional[str],
) -> None:
    """
    Contract (D-10 file posture, the owner's option B): a pathlib write runs only where the import gate admits
    `pathlib` - permissive and full_access; safe refuses every import, and hybrid and the precision overlay leave
    `pathlib` off their lists, so hybrid code cannot write files through `pathlib.Path` either.
    """
    target = tmp_path / "written_by_codegen.txt"
    payload = _execute_in_room(
        profile_name,
        precision_profile_name,
        "import pathlib\npathlib.Path({0!r}).write_text('x')\nresult = 1".format(str(target)),
    )

    assert payload["accepted"] is accepted
    assert target.exists() is accepted
    if message_fragment is not None:
        assert message_fragment in payload["validation_issues"][0]


@pytest.mark.parametrize("profile_name", ["safe", "full_access"])
def test_a_request_naming_a_frame_without_a_projection_cannot_open_files(
        tmp_path: Path,
        profile_name: str,
) -> None:
    """
    Contract (D-10): a request naming a frame the room holds no projection for runs under the engine's default
    posture, which denies what safe denies - `open` included - whatever profile the room's linked frame carries.
    """
    target = tmp_path / "written_by_codegen.txt"
    payload = _execute_in_room(
        profile_name,
        None,
        "handle = open({0!r}, 'w')\nhandle.write('x')\nhandle.close()\nresult = 1".format(str(target)),
        frame_name="frame_without_projection",
    )

    assert payload["accepted"] is False
    assert "Builtin 'open' is not allowed in this codegen mode." in payload["validation_issues"][0]
    assert not target.exists()
