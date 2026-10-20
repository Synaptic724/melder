"""The owner's rulings on the four DECISION_REQUEST points and the class merge (chat 2026-10-14), task and epic."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
EPIC = os.path.join(CC, "tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
TASK_REL = "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md"
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner ruled on the DECISION_REQUEST (chat, 2026-10-14) and corrected its model: Melder is a living
    runtime - tools are built on the fly, stored in conduits, rebuilt six times with the newest kept, and the whole
    scope is destroyed when it is done - so objects that are out "maybe are still being used" and nothing polices
    them. (A) Out-record: a plain dict of STRONG references keyed by id(object) (the record exists only so a release
    finds the shell it came from among the roots managing that class and the count comes back down); the weak
    record is withdrawn - F9 stands as written, an unreleased object holds its place until the scope is torn down,
    and the scope teardown is the reclaim. (B) Notch and cleanup_spell destroy nothing: the outgoing version's shell
    stays in the root's store under its id, its out objects keep working and come back to it, and a rebind under
    the same id meets that shell (same configuration, the quantity is fingerprinted); only scope teardown or the
    owner's purge disposes anything; no `retire` verb (consistent with 0.2.8219's "product left alive in its
    slot"). (C) Injection: slots do not matter; a holder built once keeps its injected managed object for its own
    life and whoever disposes the holder (or the scope teardown) releases it, never Melder on its behalf; no Phase 6
    rule, withdrawn. (D) Overrides on a managed site are allowed: the supplied object is used for that construction,
    the key-set plan skips the site, no lease is taken and nothing stored is replaced (the "stored shared instance"
    refusal does not apply to a dispenser); the epic's default (g) is reversed. (E) `ManagedShell` and
    `ManagedQuantity` merge into one class: `ManagedShell.elastic()` / `.limited_quantity(n)` /
    `.queue(n, timeout_seconds)` is the inert bind-time declaration (mode and numbers; hashed into the fingerprint and
    recorded), and each root owning the binding keeps a live copy in its store. The warm path measured in the
    MEASURE notes is unchanged by (A)-(E): the strong record is the same dict get as the weak one minus the weakref
    check.
  EVIDENCE:
  - {TASK_REL}:325-355
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:99-128
  - src/melder/aether/spellbook/spellbook.py:3824-3965
  IMPACT: The change set shrinks: one class instead of two, no weakref or callback, no retirement verbs, no Phase 6
    or override rule for managed sites; F5 (double and foreign release refused) and F8/F9 stand as the epic wrote
    them; open questions 3 (purge with no instance destroys the idle objects, out objects come back as usual) and 6
    are answered by these rulings.
  NEXT: the owner reads the corrected shape; this task closes on his word and melder_1's patch docs carry it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
LOG = f"""- 2026-10-14 (owner, chat with fable_0; ruling on the investigation task's four points): the out-record holds strong
  references (F9 as written: an unreleased object holds its place until the scope is torn down; no weak record);
  notch and cleanup_spell destroy nothing - the old version's shell and its objects stay until the scope is destroyed
  or purged; injection into any holder is a lease the holder keeps for its life (no Phase 6 rule); overrides on a
  managed site are allowed - the supplied object is used for that construction and no lease is taken (reverses
  default (g)); `ManagedShell` and `ManagedQuantity` are one class (the bind-time declaration and the per-root live
  shell). The owner's model: "sometimes you don't care about old objects ... you've made the same tool 6 times and the
  newest version is the one you like, you then destroy the whole scope"; objects that are out "maybe are still being
  used".
"""
for block, label in ((NOTE, "note"), (LOG, "log")):
    bad = check_line_lengths(block, exempt=r"^  - (context_compass|src|tickets)/")
    if bad:
        raise SystemExit(f"{label}: lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "tree. Resume: the owner's rulings go to the epic's Decision Log (melder_1's patch docs follow), then this\n"
    "task closes.\n",
    f"tree. The owner's rulings of {TS} (strong out-record, nothing destroyed on notch or cleanup_spell, no\n"
    "injection or override rule, one class) are in the latest DECISION note and the epic's Decision Log. Resume:\n"
    "the task closes on the owner's word; melder_1's patch docs carry the corrected shape.\n",
    "handoff tail")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
epic, enl = read_text(EPIC)   # re-read immediately before the edit; additive, anchored
epic = replace_once(epic, "## Decision Log\n- 2026-10-14 (fable_0, TASK-2026-10-14-investigate_managed_shell_design)",
                    "## Decision Log\n" + LOG + "- 2026-10-14 (fable_0, TASK-2026-10-14-investigate_managed_shell_design)",
                    "decision log head")
write_text(EPIC, epic, enl)
check, _ = read_text(EPIC)
assert check.count(LOG) == 1
print("rulings recorded", TS)
