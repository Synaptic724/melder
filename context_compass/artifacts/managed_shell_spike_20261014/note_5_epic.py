"""The epic (melder_1's lane, additive): a Decision Log entry and a DECISION note carrying the spike's result."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
EPIC = os.path.join(CC, "tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
TASK_REL = "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md"
ART = "context_compass/artifacts/managed_shell_spike_20261014"
TS = now_utc()
LOG = f"""- 2026-10-14 (fable_0, TASK-2026-10-14-investigate_managed_shell_design): the shell shape measured on the 0.2.8238
  working copy - the three modes and the one way back pass a 15-check stress probe under 3.14t; inside a real emitted
  plan a managed site costs 400-550 ns per creation over a warm `unique` read (acquire ~272 ns, release ~628 ns,
  routing through `ReleaseManagedSpell` +93-100 ns), against 74-82 us for a fresh logger meld; the warm meld lane,
  the other sites and the many registration are untouched. Recommended for the patch docs: one Existence member,
  one shell module (`ManagedShell`, `ManagedQuantity`, `ReleaseManagedSpell`), one door template, one lowering site
  shape, the fourth record shape in the five store readers, one Phase 6 rank entry, two bind keywords, a cache
  generation and RecordVersion bump; one leaf lock per shell (the lock-free variant rejected); a weak out-record
  with one persistent weakref per object; `with` as a small class released through the dispensing shell. Owner
  rulings requested (the task's DECISION_REQUEST): the weak out-record against F9's letter, retiring the shell on
  notch and cleanup_spell, injection into slotted holders as a lifetime lease, overrides refused.
"""
NOTE = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The investigation task's result (its MEASURE and DECISION notes): the owner's shell shape holds against
    0.2.8238 with the minimal change set named in the Decision Log entry of this date, and the measured costs sit
    inside the success metrics (acquire 272 ns and release 628 ns against about 5 us and 1 us; routing +93-100 ns
    against about 100 ns; a reuse cycle 400-550 ns over a warm unique read; the logger case wins by two orders).
    Four rulings are the owner's: the weak out-record (F9), shell retirement on notch and cleanup_spell (and purge
    with no instance as the same soft eviction, Q3), lifetime leases into slotted holders, overrides refused (Q6).
    The patch docs stay in this lane (melder_1); the task moves to review for the owner.
  EVIDENCE:
  - {TASK_REL}:187-355
  - {ART}/logs/probe_modes_run2.txt:1-19
  - {ART}/logs/probe_plan_shape_run1.txt:1-11
  IMPACT: Milestone 1 can close on the owner's rulings plus defaults (a)-(j); Milestone 2's patch docs have a
    measured shape to describe.
  NEXT: Owner rules on the four points and (a)-(j); then the patch docs and the first story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
for block, label in ((LOG, "log"), (NOTE, "note")):
    bad = check_line_lengths(block, exempt=r"^  - (context_compass|tickets)/")
    if bad:
        raise SystemExit(f"{label}: lines over cap: {bad}")
text, nl = read_text(EPIC)   # re-read immediately before the edit (melder_1's file; additive, anchored)
text = replace_once(text, "## Decision Log\n- 2026-10-14 (chat with fable_0): the simplest path",
                    "## Decision Log\n" + LOG + "- 2026-10-14 (chat with fable_0): the simplest path", "decision log head")
text = replace_once(text, "\n## Closure Confirmation\n", "\n" + NOTE + "## Closure Confirmation\n", "closure heading")
write_text(EPIC, text, nl)
check, _ = read_text(EPIC)
assert check.count(LOG) == 1 and check.count(NOTE) == 1
print("epic updated", TS, "newline", repr(nl))
