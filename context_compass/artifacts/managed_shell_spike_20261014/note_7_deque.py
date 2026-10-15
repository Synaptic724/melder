"""MEASURE + DECISION: the owner's deque holder (chat 2026-10-14) measured; the settings live on the Spell."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK = os.path.join(CC, "tickets/tasks/2026-10-14_investigate_managed_shell_design_task.md")
EPIC = os.path.join(CC, "tickets/epics/2026-10-14_managed_spell_quantity_epic.md")
ART = "context_compass/artifacts/managed_shell_spike_20261014"
TS = now_utc()
NOTES = f"""- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Probe C, the owner's simpler shape (chat 2026-10-14): the holder is a `deque` subclass
    (`ManagedSpellQuantity`) of idle objects kept in the Creations object under the spell id, the mode and numbers
    composed from the Spell when it is created, no out-record, no identity checks; the emitted site is an inline
    `try: v = h.pop() except IndexError: v = <miss>`; release is `append` after the optional reset (elastic trims
    the oldest idle above max_idle, queue notifies). On the VM (3.14.7t, `-X gil=0`), one idle object, acquire +
    release per cycle: elastic 140 ns through `ReleaseManagedSpell` / 90 ns through the known holder (with a
    declared `reset()` 215 / 149); limited_quantity(4) 124 / 82; queue(4, 1.0 s) 265 / 239 - against 505 / 407,
    484 / 389 and 567 / 461 for the spike's `ManagedShell` (Probe B2), 3-4x cheaper, and a whole cycle now costs
    about three to five warm `unique` reads (30 ns). The checks that matter still pass: limited(3) never exceeds 3
    under 8 threads (built 3; the refusals are the limited mode's raise, 13792 of 16000), queue(1, 0.25 s) waits
    then raises at its timeout, and a waiter is served by a release (the same object, no build).
  EVIDENCE:
  - {ART}/probe_deque_holder.py:1-186
  - {ART}/logs/probe_deque_holder_run1.txt:1-7
  - {ART}/logs/probe_door_modes_run2.txt:1-4
  IMPACT: The owner's shape is both simpler and faster: the acquire is a deque pop inlined in the plan (no method
    call, no lock - `deque.pop`/`append` are atomic per object on 3.14t) and the lock exists only on the cold
    paths (the limited/queue count, the queue wait) and the elastic trim.
  NEXT: the DECISION below records the shape; the task closes on the owner's word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  AUTHOR: fable_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction (chat 2026-10-14), superseding the DECISION notes above where they differ: the Spell
    retains every managed requirement as bind options (the mode, the limit, the timeout, the idle cap, the reset
    names) - no settings object and no new composition frame; Creations composes the holder from the Spell: a new
    holder kind, `ManagedSpellQuantity(deque)`, the idle objects, with the elastic system built into the subclass
    optionally; "we don't care about identity": release appends, nothing is checked, a double release is the
    user's. What the shape still needs, all off the warm path: (1) `_built`, the strong list of every object the
    holder built, appended once at build, so `limited`/`queue` count against `len(_built)`, root teardown destroys
    idle and out objects alike (F8), and `purge(instance)` finds its object by a cold identity scan; (2) a side map
    id(object) -> its disposal-bearing `many` children, written only at build and only for objects that have any,
    read only when the object is destroyed, so the 0.2.8235/0.2.8238 rule (children die with the object they were
    built for) holds; (3) release routing by type(object) -> the one holder of that class in the normal case, and
    the meld-style target (`release(obj, target)`) when the same class is bound in two Books, raised as an ambiguity
    like meld's; (4) the holder created at `_add_owned_conduit` from the Spell so the lowering binds it as a plan
    constant like the S9 store (`h0`), and the site inlines the pop; (5) `with` as a small class holding the holder
    and the object (`__exit__` appends; 90 ns measured), returned by `conduit.managed_spell_meld("target")`.
  EVIDENCE:
  - {ART}/probe_deque_holder.py:28-91
  - {ART}/logs/probe_deque_holder_run1.txt:1-7
  - src/melder/aether/conduit/creations/creations.py:1302-1330
  - src/melder/aether/spellbook/spell.py:1558-1606
  IMPACT: The change set: one Existence member; the bind options on the Spell (fingerprinted); one `deque` subclass
    in Creations with its own dict branch in the five readers; one door template and one inline site shape; one
    Phase 6 rank entry; `ReleaseManagedSpell` as a type -> holder index; cache generation and RecordVersion bumps.
    The spike's `ManagedShell`, its entries and weakrefs are retired as reference only.
  NEXT: the owner reads this; melder_1's patch docs carry the deque shape; this task closes on the owner's word.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
LOG = f"""- 2026-10-14 (owner, chat with fable_0): the holder is a `deque` of idle objects in the Creations object under the
  spell id - `ManagedSpellQuantity(deque)`, the elastic system built in optionally - composed from the Spell, which
  retains every managed requirement as bind options; no settings object, no composition frame, no identity tracking
  ("we don't care about identity"); release appends. Measured 3-4x cheaper than the spike's shell (elastic cycle
  140 ns through ReleaseManagedSpell, 90 ns through the holder; limited 124 / 82; queue 265 / 239) with the limited
  and queue checks still passing (task MEASURE/DECISION notes of this timestamp).
"""
for block, label in ((NOTES, "notes"), (LOG, "log")):
    bad = check_line_lengths(block, exempt=r"^  - (context_compass|src|tickets)/")
    if bad:
        raise SystemExit(f"{label}: lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTES + "## Context / Handoff Summary\n", "handoff")
text = replace_once(
    text,
    "the task closes on the owner's word; melder_1's patch docs carry the corrected shape.\n",
    f"the task closes on the owner's word; melder_1's patch docs carry the deque shape of {TS} (the Spell keeps the\n"
    "requirements, `ManagedSpellQuantity(deque)` in Creations, no identity tracking; Probe C measured it).\n",
    "handoff tail")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
epic, enl = read_text(EPIC)
epic = replace_once(epic, "## Decision Log\n- 2026-10-14 (owner, chat with fable_0; ruling",
                    "## Decision Log\n" + LOG + "- 2026-10-14 (owner, chat with fable_0; ruling", "decision log head")
write_text(EPIC, epic, enl)
print("recorded", TS)
