"""Close TASK-2026-10-15-make_meld_state_checks_follow_spell_state on the owner's acceptance (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC now> [--check]
Completion summary, Status/Updated, the State Transition Event, the anti-pattern and Done checklists, the cleanup
trigger, the acceptance Note and the handoff summary, in place; the move to tickets/tasks/completed/ is a separate
`mv -n`. Anchors must occur exactly once; new lines stay within 120 characters and ASCII; --check writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
PATH = pathlib.Path("context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
DONE = "context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"
SUCCESSOR_ID = "TASK-2026-10-16-recheck_contract_consumers_when_provider_changes"
SUCCESSOR = "context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"

SUMMARY = f"""
- Completed: {NOW}
- Summary: Rule 1 landed, notched 0.2.8247: a lineage whose selected version was bound resolvable=False carries
  `SpellState.non_resolvable`, and RiskManager's Book validation flag leaves it out, so one Protocol or abstract
  definition no longer sends every meld of its Book through the validation gate (15-16 us -> 0.3-0.7 us a warm
  meld). Release-note section: "A non-resolvable definition no longer sends every meld of its Book through
  validation". The owner accepted it; rule 2 (check a contract only when the consumer's state calls for it, and
  recheck consumers on a notch) moved to {SUCCESSOR_ID}.
"""

TRANSITION_OLD = """## State Transition Event
- from_state: in_progress
- to_state: blocked
"""
TRANSITION_NEW = f"""## State Transition Event
- from_state: blocked
- to_state: done
- transition_reason: the owner accepted rule 1 as landed in 0.2.8247 (chat 2026-10-16: asked "shall I mark rule 1
  accepted and close its ticket, then open rule 2 as its own ticket on this story?", he answered "yees sure thats
  good"). The EXIT_GATE's rule-2 conditions move by his direction (Note 2026-10-16T09:30:40Z) to the successor
  {SUCCESSOR_ID}; board and artifact rows are synced.
- prior: in_progress -> blocked (2026-10-16T01:50:42Z), the text below:
- from_state: in_progress
- to_state: blocked
"""

CLEANUP_OLD = "- CLEANUP_TRIGGER: none left - the patch docs are archived; the artifact folder stays as the lane's evidence\n"
CLEANUP_NEW = (f"- CLEANUP_TRIGGER: none left - the patch docs are archived; the artifact folder stays as evidence, rowed under\n"
               f"  the successor {SUCCESSOR_ID}\n")

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner acceptance (chat 2026-10-16): asked "shall I mark rule 1 accepted and close its ticket, then open rule
    2 as its own ticket on this story? It would start with the design docs for your approval, with no source changes
    until you approve them", he answered "yees sure thats good". Rule 1 is accepted as landed in 0.2.8247 and this
    ticket closes. Rule 2 - the EXIT_GATE's contract-check conditions, settled in principle in the Note of
    2026-10-16T09:30:40Z - moves to the successor
    {SUCCESSOR_ID}, which starts with patch docs for his approval and
    changes no source before it. The artifact folder is rowed under the successor as its evidence; the patch lane
    stays archived.
  EVIDENCE:
  - {DONE}:{{DIRECTION_RANGE}}
  - {DONE}:{{EXIT_RANGE}}
  - {SUCCESSOR}
  IMPACT: Rule 1 is done and accepted; nothing of it remains open.
  NEXT: None here; rule 2 continues in the successor.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""

HANDOFF_NEW = f"""## Context / Handoff Summary
Closed (done, {NOW}): the owner accepted rule 1 as landed in 0.2.8247. `register_index` writes
`SpellState.non_resolvable` from the selected version's `Spell.resolvable` (bind, notch, the transfer flip and its
rollback pass it) and mirrors it in the registry's published `non_resolvable_index_ids`; RiskManager's Book flag
leaves flagged lineages out with one subset test, and `register_index` re-publishes the validity when the flag
changes on a lineage already gated. Tests A (34), B (11), C (the stub) and D (9) are in the tree; all 23 chunks
passed with the GIL off and on; a warm meld in a Book with a definition 15.1 -> 0.26 us (automatic), 16.4 -> 0.73
us (dynamic). The four system docs and their indexes, the graph, the release note, the notch notice, the archived
patch lane (system_docs/patches/completed/meld_state_gate_2026_10_15/), rubric 83 / 83 / 83 / 77 (B), and the
assets and LLM bundles rebuilt for 0.2.8247 with both checks OK. melder_0 has its files back (M1-19).
Rule 2 continues in {SUCCESSOR_ID}: a satisfied contract needs no
per-meld check, a notch marks the key's consumers for a recheck (mark only) so a notched version's new `__init__`
is re-resolved; patch docs first, for the owner's approval; spellbook.py (melder_0's) needs a handoff for the build.
Recorded, not fixed (outside this change): the notch-swap KeyError race, the stale spellbook.py and
transfer_of_ownership.py citations named in src_components' handoff, TransferOfOwnership's unverified graph node.
Not run: coverage.
"""


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:70], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw
text = raw.decode("ascii")
text = replace_once(text, "- Status: blocked\n", "- Status: done\n")
text = replace_once(text, "- Updated: 2026-10-16T01:58:17Z\n", f"- Updated: {NOW}\n" + SUMMARY)
text = replace_once(text, TRANSITION_OLD, TRANSITION_NEW)
for item in ("No status transition without evidence-backed transition reason.",
             "No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.",
             "No closure without delegated acceptance or reserved-owner disposition and board-sync completion.",
             "Steps complete and checked off", "Deliverables produced and linked", "Documentation updated (if needed)",
             "Validation status recorded",
             "Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)",
             "Notes quality maintained (`SCORE_0_TO_10` >=",
             "Applicable anti-pattern checks are clear or escalated with evidence.",
             "Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded",
             "Board sync completed for successor routing or closure anchor update."):
    text = replace_once(text, f"- [ ] {item}", f"- [x] {item}")
text = replace_once(text, CLEANUP_OLD, CLEANUP_NEW)
start = text.index("## Context / Handoff Summary\n")
end = text.index("\n## Project-Specific Additions")
text = text[:start] + HANDOFF_NEW + text[end:]
text = replace_once(text, "\n\n## Context / Handoff Summary\n", "\n" + NOTE + "\n## Context / Handoff Summary\n")
lines = text.split("\n")
direction = next(i for i, l in enumerate(lines, 1) if l == "- DATETIME: 2026-10-16T09:30:40Z")
direction_end = next(i for i, l in enumerate(lines, 1) if i > direction and l.startswith("  SCORE_0_TO_10:"))
exit_gate = next(i for i, l in enumerate(lines, 1) if l.startswith("- EXIT_GATE:"))
text = text.replace("{DIRECTION_RANGE}", f"{direction}-{direction_end}").replace("{EXIT_RANGE}",
                                                                                   f"{exit_gate}-{exit_gate + 2}")
old_lines = set(raw.decode("ascii").split("\n"))
too_long = [l for l in text.split("\n") if len(l) > 120 and l not in old_lines]
assert not too_long, too_long
if not CHECK:
    PATH.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written", "direction note", direction, direction_end, "exit gate", exit_gate)
