"""Scratch probe: which codegen profiles let agent code read or write files (VM scratch only)."""
import pathlib
import sys
from typing import Optional, Tuple

from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)

OUT = pathlib.Path(sys.argv[1]).resolve()
CORE_FILE = pathlib.Path(sys.argv[2]).resolve()


def run_case(profile: str, precision: Optional[str], label: str, code: str) -> Tuple[bool, object, str]:
    reset_runtime_singletons()
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    container = nexus._frame_acl_manager._get_required_frame_acl_container("ops")
    builder = container.frame_acl_builder.begin_codegen_change(reason="probe")
    builder.use_profile(profile)
    if precision is not None:
        builder.use_precision_profile(precision)
    builder.commit_change()
    rift.create_frame_link("ops")
    try:
        payload = rift.space.command_system.execute_codegen(code, frame_name="ops")
    finally:
        conduit.cleanup()
        reset_runtime_singletons()
    issues = payload.get("validation_issues") or payload.get("error") or ""
    return bool(payload["accepted"]), payload.get("result"), str(issues)[:110]


cases = []
for profile, precision in (("safe", None), ("hybrid", None), ("hybrid", "precision"),
                           ("permissive", None), ("full_access", None)):
    tag = profile + ("+precision" if precision else "")
    write_target = OUT / ("open_write_" + tag + ".txt")
    cases.append((profile, precision, "open-write",
                  "handle = open({0!r}, 'w')\nhandle.write('x')\nhandle.close()\nresult = 1".format(str(write_target)),
                  write_target))
    cases.append((profile, precision, "open-read-core",
                  "handle = open({0!r})\nresult = len(handle.read())\nhandle.close()".format(str(CORE_FILE)),
                  None))
    path_target = OUT / ("pathlib_write_" + tag + ".txt")
    cases.append((profile, precision, "pathlib-write",
                  "import pathlib\npathlib.Path({0!r}).write_text('y')\nresult = 1".format(str(path_target)),
                  path_target))
    cases.append((profile, precision, "import-melder", "import melder\nresult = melder.__name__", None))
    cases.append((profile, precision, "import-subprocess", "import subprocess\nresult = subprocess.__name__", None))

for profile, precision, label, code, target in cases:
    accepted, result, issues = run_case(profile, precision, label, code)
    wrote = target.exists() if target is not None else None
    tag = profile + ("+precision" if precision else "")
    print("{0:22s} {1:18s} accepted={2!s:5s} wrote={3!s:5s} result={4!r} issues={5}".format(
        tag, label, accepted, wrote, result, issues))
