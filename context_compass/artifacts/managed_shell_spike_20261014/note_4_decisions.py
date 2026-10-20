"""DECISION and DECISION_REQUEST notes: the shell shape's remaining points, with the spike's evidence."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
ART = "context_compass/artifacts/managed_shell_spike_20261014"
SRC = "src/melder/aether"
TS = now_utc()
DECISION = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The shell shape is buildable as the owner read it, and these points are settled by the evidence. (1) The
    door route: the hot `Conduit.meld` warm lane is untouched; a managed spell gets one more emitted door template
    (read the shell from the owner store under the spell id, `acquire()`, else the plan's miss) and one more site
    shape in the lowering (`v = sh.acquire()`, bound like the S9 store constant); the plan's other sites, the many
    registration and the guard ladder do not change (Probe B: the transformed body is the plain body with one site
    swapped). (2) The miss order: `reserve()` first (limited refuses, queue waits, both before anything is built),
    then the site's children, then the object, then `publish_out(entry, object, children)`; a failed build
    `cancel()`s the place and disposes the children it built. A managed site has no slot guard - the shell is its
    guard - and its children are built before any holder's guard is taken (the 0.2.73/0.2.8235 order), so a queued
    wait never holds a store or build lock. (3) The out-record: one `ManagedEntry` per object with one persistent
    weakref (created at first publish, reused across leases; strong `item` while idle), an `_out` dict keyed by
    `id(object)`, and the identity check `entry.ref() is object` on release; a recycled id cannot match because
    the dead object's callback removed its entry before its memory could be reused, and the callback does
    bookkeeping only (count, dead list) under the shell's leaf lock, never disposal. (4) Locking: one leaf lock
    per shell; reset and disposal run outside it; the lock-free variant is rejected (115-145 ns per cycle for
    broken teardown and cap invariants, Probe A2). (5) Costs against the targets: acquire 272 ns and release
    628 ns (<5 us / <1 us), routing through the one way back +93-100 ns (<=100 ns), a reuse cycle 400-550 ns over
    a warm unique read, so pooling pays above about 0.5 us of construction and the logger case wins by two orders.
    (6) The `with`: a small class with `__enter__`/`__exit__` that releases through the shell that dispensed
    (Probe B2: the generator form costs 600 ns more); `Conduit.managed_spell_meld("target")` returns it.
    (7) Shell creation and travel: `_add_owned_conduit` is the one stamping point - conjure, post-conjure bind and
    bind_inactive, the transfer flip - so the shell is created there (adopting one already stored under the same
    id, which the fingerprint makes the same configuration) and registered in `ReleaseManagedSpell`; a transfer's
    `_move_creations` moves it as the fourth record shape through `extract_spell_creations` /
    `restore_spell_creations`, the same object, so the index and every out lease are untouched; a lesser upgrade
    keeps its stores. (8) The index: type -> tuple of shells, copy-on-write under its own leaf lock, read lock-free;
    a release scans the class's shells with one dict get each.
  EVIDENCE:
  - {ART}/managed_shell.py:68-88
  - {ART}/managed_shell.py:145-183
  - {ART}/managed_shell.py:273-294
  - {ART}/managed_shell.py:328-389
  - {ART}/logs/probe_plan_shape_run1.txt:1-11
  - {ART}/logs/probe_door_modes_run1.txt:1-4
  - {SRC}/spellbook/spellbook_creation_system.py:1350-1375
  - {SRC}/spellbook/spellbook.py:5255-5290
  - {SRC}/spellbook/spellbook.py:5590-5620
  - {SRC}/conduit/conduit_ward/transfer/transfer_of_ownership.py:1470-1545
  - {SRC}/conduit/creations/creations.py:1302-1330
  IMPACT: The minimal change set for the patch docs: one Existence member; `ManagedShell` + `ManagedQuantity` +
    `ReleaseManagedSpell` (one module); one door template; one lowering site shape; the fourth record shape in the
    five store readers; one Phase 6 rank entry; two bind keywords (`quantity`, `managed_spell_reset_methods`)
    fingerprinted only for managed bindings; one cache generation bump; RecordVersion for the quantity. No change
    to the six members or the warm lane.
  NEXT: the DECISION_REQUEST below (what only the owner can rule), then the epic's Decision Log.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Four rulings the spike cannot make. (A) F9's letter versus the weak out-record: with the weak index a
    lease nobody returns is reclaimed when its holder dies, its place freed and its `many` children disposed on
    the shell's next verb (Probe A: "forgotten lease" checks), so a leaked object no longer holds a limited place
    until root teardown - recommended, it keeps "we just trust" (no reference is held, nothing is checked at the
    user's expense) and still refuses double and foreign releases; the alternative, strong references to out
    objects, pins every leak for the root's life. (B) Binding mutation paths: on `notch` (the outgoing version)
    and `cleanup_spell` of a managed spell the shell is retired - idle objects destroyed now, out objects destroyed
    at their release, the shell dropped from the store and the index when its count reaches zero - instead of the
    slotted members' "product left alive in its slot" (0.2.8219); a rebind under the same id meanwhile gets a fresh
    shell; `purge(instance)` destroys that object and frees its place, `purge_all` is the same soft eviction
    (open question 3); recommended. (C) Injection into a slotted holder: a `unique` or per-conduit holder that
    takes a managed dependency holds the lease for its own life, so a limited or queued pool feeding such holders
    exhausts by design; recommended: allowed with no Phase 6 rule (the managed spell ranks with unique), documented
    as a lifetime lease the holder's own disposal may release, and the inspection listing names the holders' out
    objects. (D) Overrides on a managed site: refused (a dispensed object is reused by other holders), as the epic's
    (g) recommends. Independent of these, the owner's earlier defaults (a)-(j) still await their answers.
  EVIDENCE:
  - {ART}/logs/probe_modes_run2.txt:13-15
  - {SRC}/spellbook/spellbook.py:4325-4420
  - {SRC}/spellbook/spellbook.py:3824-3900
  - tickets/epics/2026-10-14_managed_spell_quantity_epic.md:238-258
  IMPACT: (A) and (B) change the shell's verbs (a `retire()` beside `evict_idle()`/`destroy_all()`, a put_back that
    destroys on a retired shell); (C) and (D) are Phase 6 and lowering rules; none changes the measured warm path.
  NEXT: report to the owner; on the rulings, melder_1's patch docs carry the shape, this task closes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
bad = check_line_lengths(DECISION, exempt=r"^  - (context_compass|src|tickets)/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + DECISION + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "- [ ] DECISION / DECISION_REQUEST notes: out-record representation, binding mutation paths, the door route.\n",
    "- [x] DECISION / DECISION_REQUEST notes: out-record representation, binding mutation paths, the door route.\n",
    "step3")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
print("noted", TS)
