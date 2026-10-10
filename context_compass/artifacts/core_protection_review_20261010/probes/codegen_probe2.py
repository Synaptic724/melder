"""Scratch probe: does __import__(...) bypass the codegen import gate (VM scratch only)."""
from typing import Optional, Tuple

from tests._codegen_system_support import (
    create_codegen_rift,
    create_enabled_nexus,
    reset_runtime_singletons,
)


def run_case(profile: str, precision: Optional[str], code: str) -> Tuple[bool, object, str]:
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
    return bool(payload["accepted"]), payload.get("result"), str(issues)[:100]


for profile, precision in (("safe", None), ("hybrid", None), ("hybrid", "precision"), ("permissive", None)):
    for module in ("subprocess", "socket", "importlib", "melder"):
        code = "loaded = __import__({0!r})\nresult = str(loaded)[:48]".format(module)
        accepted, result, issues = run_case(profile, precision, code)
        tag = profile + ("+precision" if precision else "")
        print("{0:18s} __import__({1!r:12s}) accepted={2!s:5s} result={3!r} issues={4}".format(
            tag, module, accepted, result, issues))
