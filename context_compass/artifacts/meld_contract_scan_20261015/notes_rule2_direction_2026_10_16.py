"""Record the owner's direction on rule 2 (items (2)-(3)) and refresh the resume view (melder_1, 2026-10-16).

usage (from the repository root): python <this script> <UTC now> [--check]
One DECISION Note before the handoff summary; the handoff's Holds and Next lines. Anchors must occur exactly once;
new lines stay within 120 characters and ASCII; --check writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
PATH = pathlib.Path("context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md")
T = "context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner direction on rule 2 (chat 2026-10-16), settling items (2)-(3) of the design request in principle:
    "so question if spellcontract exists and its satisfied we're good but if notch happens it should be rechecked
    isn't that the story we should land on?", then, asked mark-only or also dropping stored consumer objects:
    "marking makes sense thats the point we want to make sure we can still resolve it because the init might change
    for a notched spell". The story: a satisfied SpellContract needs no per-meld check; a notch (and any other change
    of the borrower's active contracted copy: notch back, park, reactivate, add, remove) marks the key's consumers
    `gated` + `contract_unvalidated`, so their next meld re-validates the contract and rebuilds their plan against the
    version now active - its new `__init__` and dependencies included - and fails with the error a first meld would
    give when that version cannot be resolved for them. Mark only: objects already built keep their provider. Not yet
    confirmed by the owner: rule 1's acceptance and closure, and rule 2 as its own successor ticket.
  EVIDENCE:
  - {T}:181-212
  - {T}:213-232
  - {T}:233-257
  IMPACT: Rule 2's design is settled in principle; building it needs patch docs, the owner's approval of them and a
    handoff of spellbook.py from melder_0 for the borrower-side marking (its contracted-map mutators).
  NEXT: The owner confirms rule 1's acceptance and closure and a successor ticket for rule 2 on this story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HOLDS_OLD = """Holds: the owner's acceptance of rule 1 (reserved); items (2)-(3) (the contract check; a borrower SpellContract
consumer costs about 2 ms a meld) await his answer. M1-19 (mailbox) hands melder_0 back the four call-site lines
"""
HOLDS_NEW = """Holds: the owner's acceptance of rule 1 (reserved). Items (2)-(3) are settled in principle (Note {NOW}):
a satisfied contract needs no per-meld check, and a notch marks the key's consumers for a recheck (mark only), so
a notched version's new `__init__` is re-resolved; the build waits for a successor ticket the owner has not yet
confirmed (a borrower SpellContract consumer still costs about 2 ms a meld). M1-19 (mailbox) hands melder_0 back
the four call-site lines
"""
NEXT_OLD = """folder kept as reference); (2) the owner's answer on items (2)-(3) opens a successor task or retires them.
"""
NEXT_NEW = """folder kept as reference); (2) a successor task for rule 2 on the settled story: patch docs for the owner's approval,
then the build, with a handoff of spellbook.py from melder_0.
"""


def replace_once(text, old, new):
    assert text.count(old) == 1, (old[:70], text.count(old))
    return text.replace(old, new)


raw = PATH.read_bytes()
assert b"\r" not in raw
text = raw.decode("ascii")
text = replace_once(text, HOLDS_OLD, HOLDS_NEW.replace("{NOW}", NOW))
text = replace_once(text, NEXT_OLD, NEXT_NEW)
text = replace_once(text, "\n\n## Context / Handoff Summary\n", "\n" + NOTE + "\n## Context / Handoff Summary\n")
old_lines = set(raw.decode("ascii").split("\n"))
too_long = [l for l in text.split("\n") if len(l) > 120 and l not in old_lines]
assert not too_long, too_long
if not CHECK:
    PATH.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written")
