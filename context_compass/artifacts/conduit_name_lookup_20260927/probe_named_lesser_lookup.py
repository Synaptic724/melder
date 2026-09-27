"""
Repro probe for TASK-2026-09-27-trace-get-conduit-by-name-named-lesser-lookup (melder_0).

Question: does Aether.get_conduit_by_name find a live NAMED LESSER scope, in both runtime
modes, and does the frame's ConduitCloud find it?

Run from a scratch directory against a snapshot copy of src (keeps __melder_cache__ and
bytecode out of the repository):
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<snapshot parent of melder> python3.14t probe_named_lesser_lookup.py
"""
import sys

import melder as md


class ProbeServiceAuto:
    """Trivial bound class for the automatic-mode frame."""


class ProbeServiceDyn:
    """Trivial bound class for the dynamic-mode frame. A second class is needed because binding the
    SAME class into a second frame's Spellbook raised "Spell ID collision detected" (first run,
    2026-09-27); that behaviour is outside this probe's question and recorded as UNKNOWN."""


def attempt(label, fn, expected=None):
    """Print one lookup outcome: the value, identity against `expected`, or the raised error."""
    try:
        value = fn()
    except Exception as exc:
        print("    %-34s RAISES %s: %s" % (label, type(exc).__name__, exc))
        return None
    suffix = ""
    if expected is not None:
        suffix = "  (is expected object: %s)" % (value is expected)
    print("    %-34s %r%s" % (label, value if not hasattr(value, "_id") else "<Conduit %s>" % value._name, suffix))
    return value


def run(frame_name, dynamic, service):
    """Build root -> named lesser -> named nested lesser in one frame and probe every lookup."""
    print("== frame=%s dynamic=%s" % (frame_name, dynamic))
    book = md.Spellbook(aetheric_frame=frame_name)
    book.bind(spell=service, existence=md.Existence.unique)
    root = book.conjure(dynamic=dynamic, name="root_" + frame_name)
    group = root.create_lesser_conduit(name="group_" + frame_name)
    subgroup = group.create_lesser_conduit(name="subgroup_" + frame_name)
    aether = md.Aether()
    cloud = aether.get_conduit_cloud(frame_name)
    for scope in (root, group, subgroup):
        name = scope._name
        print("  name=%s state=%s" % (name, scope._conduit_state.name))
        attempt("Aether.get_conduit_by_name", lambda: aether.get_conduit_by_name(name, frame_name), scope)
        attempt("Aether.find_conduit_id_by_name", lambda: aether.find_conduit_id_by_name(name, frame_name))
        attempt("Aether.has_conduit_name", lambda: aether.has_conduit_name(name, frame_name))
        attempt("ConduitCloud.get_conduit_by_name", lambda: cloud.get_conduit_by_name(name), scope)
    attempt("Aether.list_conduit_names", lambda: aether.list_conduit_names(frame_name))
    attempt("ConduitCloud.list_conduit_names", lambda: cloud.list_conduit_names())
    retired = subgroup._name
    subgroup.cleanup()
    print("  after subgroup.cleanup() (named lesser returned to its pool):")
    attempt("ConduitCloud.get_conduit_by_name", lambda: cloud.get_conduit_by_name(retired))
    attempt("ConduitCloud.list_conduit_names", lambda: cloud.list_conduit_names())


if __name__ == "__main__":
    gil = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    print("python", sys.version.split()[0], "gil_enabled", gil, "melder", md.__version__)
    run("probe_auto", dynamic=False, service=ProbeServiceAuto)
    run("probe_dyn", dynamic=True, service=ProbeServiceDyn)
