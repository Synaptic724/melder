"""MEASURE note: Probe A (modes, the one way back) and Probe A2 (locked vs lock-free warm path)."""
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
  CLAIM: Probe A (`probe_modes.py`: the three modes and the one way back; CPython 3.14.7t, `-X gil=0`, the VM). Run 1
    failed 1 of 15 checks - a forgotten lease's dead child was not disposed, because `acquire` returned the idle
    object before draining the dead list - and cost 1594 ns per dispense+release cycle single-thread (acquire ~684,
    release ~945) and 3516 ns amortized over 4 threads x 50k; the costs were a weakref plus closure minted per lease,
    the type->shells index read under its lock, and a condition notify on every put_back. Run 2, after one
    persistent weakref per entry (a bound-method callback), the dead check outside the lock in acquire and
    put_back, a copy-on-write index read lock-free and notify only in queue mode: 15/15 ok - limited(3) never
    exceeds 3 under 8 threads (built 3); queue waits, then raises at its 0.25 s timeout, and a waiter is served by a
    release with no build; elastic builds 20 under 20 concurrent leases and caps idle at max_idle=4 (16 destroyed
    with their children); a forgotten lease is collected, its place freed and its dead child disposed on the next
    verb; double and foreign releases raise; a failing reset raises, destroys and frees the place; the `with`
    releases on exit - at 638 ns per cycle single-thread (acquire ~272, release ~628 one-shot) and 939 ns amortized
    over 4 threads. Probe A2 (`probe_cost_variants.py`, elastic, one idle object per thread, two repeats): the
    locked warm path costs 591-604 ns per cycle single-thread and 840-876 ns over 4 threads; a lock-free warm path
    (variant B: `deque.pop`/`append` and one dict store, each atomic per object on 3.14t) 474-485 ns and 724-730 ns,
    so the two leaf-lock sections cost about 115 ns per cycle single-thread and 115-145 ns under four threads.
    Variant B does not keep the shell's invariants: the destroyed flag, the elastic cap and the dead-list drain are
    read outside the lock, so an acquire or put_back racing `destroy_all` or `evict_idle` can hand out or re-idle an
    object those verbs already disposed, and idle can overshoot max_idle. A2's limited(3) check releases at once
    (peak 1), so Probe A's limited check is the one that counts.
  EVIDENCE:
  - {ART}/managed_shell.py:68-88
  - {ART}/managed_shell.py:117-143
  - {ART}/managed_shell.py:145-183
  - {ART}/managed_shell.py:185-235
  - {ART}/managed_shell.py:273-294
  - {ART}/managed_shell.py:354-389
  - {ART}/probe_modes.py:1-201
  - {ART}/probe_cost_variants.py:1-82
  - {ART}/logs/probe_modes_run1.txt:1-19
  - {ART}/logs/probe_modes_run2.txt:1-19
  - {ART}/logs/probe_cost_variants_run1.txt:1-8
  IMPACT: Against the epic's targets (about 5 us to acquire and about 1 us to return a ChannelLogger-like object;
    74-82 us for a fresh logger meld) the locked shell is an order of magnitude inside both, so the lock-free
    variant buys nothing the design needs: keep the one leaf lock (N1) and the one way back. A reuse cycle is about
    20x a warm `unique` site read (~30 ns) and about 120x cheaper than the fresh logger meld; what remains is the
    Python-level verbs themselves (type lookup, weakref check, the reset call, two lock sections).
  NEXT: Probe B on `$HOME/work/melder_cc` (0.2.8238): capture the normal plan of a Worker(many) -> Service(unique)
    root, rewrite the Service site to `sh.acquire()` with a reserve/publish miss, run it and measure acquire+release
    per creation against today's unique site read; then the hand-wired door shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(NOTE, exempt=r"^  - context_compass/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
print("noted", TS)
