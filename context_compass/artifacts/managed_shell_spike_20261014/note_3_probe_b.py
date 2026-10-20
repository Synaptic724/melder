"""MEASURE note: Probe B (a managed site inside the real emitted plan; the door shapes; the modes)."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
ART = "context_compass/artifacts/managed_shell_spike_20261014"
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe B on the 0.2.8238 working copy (`-X gil=0`, caching off). B0 captured the emitted normal plan of the
    worker shape (Manager `unique` with disposal -> Worker `many` with disposal) through the certification
    harness: the S9 body reads the Manager site as `v0 = c0._creations.get(sid0)` / `if v0 is None: v0 =
    _miss0(meld, c0)` with `c0` the owner store bound in the namespace. B1 executed that body unchanged and a
    transformed body whose Manager site reads a locked elastic `ManagedShell` instead (`v0 = sh0.acquire()`;
    the miss reserves, builds `t0()`, cancels on failure, publishes out), one Worker creation per call, the
    user's release included for the managed one: plain 166 ns per creation (3 py / 5 C calls); managed +
    `ReleaseManagedSpell.release` 715 ns (6 / 19); managed + release through the shell that dispensed it 584 ns
    (5 / 17); over 4 threads x 30k the managed cycle is 1044 ns amortized against 307 ns plain. The door shapes
    alone: the owner-store read 30 ns; `sh0.acquire()` + put_back through the shell 428 ns; `acquire` +
    `ReleaseManagedSpell.release` 521 ns; `Manager()` itself 70 ns; the whole `conduit.meld("Worker")` 337 ns.
    B2, the warm cycle per mode on the shell alone (one idle object): elastic 407 ns (shell) / 505 ns (singleton),
    with a declared `reset()` 478 / 599; limited_quantity(4) 389 / 484; queue(4, 1.0 s) 470 / 567 (its notify);
    the `with ReleaseManagedSpell.managed(...)` form costs 1067-1172 ns because it is a `contextlib.contextmanager`
    generator - a small class with `__enter__`/`__exit__` is the shape to emit instead.
  EVIDENCE:
  - {ART}/probe_plan_capture.py:1-40
  - {ART}/logs/probe_plan_capture_worker_source.txt:1-23
  - {ART}/probe_plan_shape.py:1-193
  - {ART}/logs/probe_plan_shape_run1.txt:1-11
  - {ART}/probe_door_modes.py:1-80
  - {ART}/logs/probe_door_modes_run1.txt:1-4
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1319-1381
  IMPACT: The lease costs 400-550 ns per creation over a warm `unique` read, all of it the Python-level pool verbs
    (two method calls, two leaf-lock sections, the id/dict/deque work); the one way back costs 93-100 ns more than
    a release through the known shell (the type lookup, the out-record get and the weakref check), inside the
    epic's "about 100 ns" routing budget. Pooling pays for an object that costs more than about 0.5 us to build:
    the Iris logger (74-82 us) by two orders of magnitude, a 70 ns `Manager` not at all - the mode changes nothing
    on the warm path (queue +65-80 ns for its notify). A managed site drops into the emitted plan as one more
    site shape; the plan's other sites, the many registration and the door are untouched.
  NEXT: the DECISION and DECISION_REQUEST notes (out-record representation, binding mutation paths, the door
    route and the `with` shape), then the recommendation into the epic's Decision Log.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTE, exempt=r"^  - (context_compass|src)/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] Spike on the working copy: `ManagedShell` (three modes), `ReleaseManagedSpell` (weak index, `with`), a\n",
    "- [x] Spike on the working copy: `ManagedShell` (three modes), `ReleaseManagedSpell` (weak index, `with`), a\n",
    "step2")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
print("noted", TS)
