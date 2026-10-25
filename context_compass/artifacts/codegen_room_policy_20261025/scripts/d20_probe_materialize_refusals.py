"""D-20 probe (melder_0, 2026-10-25): what materialize_codegen answers for the review's cases, and what it leaves.

The review's probe_materialize.py and probe_materialize_fail.py assume the materialize succeeds (they read the
injected module back), so after D-20 they stop at their first refused case. This probe reports, per profile, the
verb's answer for each case and whether sys.modules and the parent attribute are unchanged. Process-local only.
Usage: PYTHONPATH=<tree>/src:<tree> python d20_probe_materialize_refusals.py
"""
import importlib
import sys

from tests._codegen_system_support import create_codegen_rift, create_enabled_nexus, reset_runtime_singletons


def materialize(profile_name, module_name, code):
    reset_runtime_singletons()
    nexus = create_enabled_nexus()
    rift = create_codegen_rift(nexus)
    conduit = rift.create_nexus_frame(frame_name="ops")
    change = nexus.get_frame_acl_builder("ops").begin_codegen_change(reason="d20_probe")
    change.use_profile(profile_name)
    change.commit_change()
    rift.create_frame_link("ops")
    try:
        return rift.space.command_system.materialize_codegen(code, module_name=module_name, frame_name="ops")
    finally:
        conduit.cleanup()
        reset_runtime_singletons()


def state(name):
    parent, _, child = name.rpartition(".")
    holder = sys.modules.get(parent) if parent else None
    return sys.modules.get(name), (getattr(holder, child, None) if holder is not None else None)


for name in ("melder.aether.spellbook.bind.bind", "csv", "json", "pytest"):
    importlib.import_module(name)
for profile in ("safe", "hybrid", "full_access"):
    for name in ("melder.aether.spellbook.bind.bind", "melder.injected_probe", "csv", "json", "pytest"):
        before = state(name)
        payload = materialize(profile, name, "Bind = None\n")
        after = state(name)
        print("[%s] %s: materialized=%s | unchanged=%s | refusal=%s" % (
            profile, name, payload["materialized"], after[0] is before[0] and after[1] is before[1],
            payload.get("refusal")))
try:
    materialize("hybrid", "d20_probe_pkg.child", "value = 1\nraise ValueError('probe')\n")
except ValueError as error:
    print("[hybrid] failed materialize raised:", error)
print("residue after the failed materialize:", sorted(n for n in sys.modules if n.startswith("d20_probe_pkg")))
