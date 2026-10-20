"""Record the 0.2.8250 notch, NOTICE M1-21 and the release-note entry, and the pre-existing remove_index_from_contract
defect found while verifying it; resync the handoff Next and the board row (melder_1, 2026-10-16).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The notch, the NOTICE and the release-note entry are in. `__version__` read 0.2.8249 at 17:30Z and is now
    0.2.8250 (the notch script refuses any other current value). M1-21 (NOTICE, no ACK requested) went to melder_0
    with its alert line, and the standing bullet sits under "Notch notice (melder_1, 2026-10-16)" on the attention
    board. release_docs/next_version_release.md (723 -> 857 lines): header `# Melder 0.2.8250`; one section after
    the 0.2.8249 one - the story, two examples, the measured cost, two Breaking changes (a destroyed index or a
    grant parked by a notch away gives SpellbookValidationError where the scan gave MeldExecutionError; a notch's
    dependents build the new version or raise the first meld's error), the lost provider reported by name, D3, the
    fixes, the known race (not changed yet) and what stays the same; one packaging bullet; the rebuild line for
    0.2.8250. Its two code blocks are byte-identical to the blocks `release_example_rule2_2026_10_16.py` runs, which
    pass on the landed tree with the GIL off and on. The same steps without the asserts on the tree before 0.2.8250
    (the real tree with the seven pristine src files restored): the consumer follows the notch at 1558 / 1682 us a
    warm meld (GIL off / on), 2.8 / 2.8 us now; after a sever the report says "No validation error was recorded",
    and names the contract and its remedy now; `Report`, two hops from the notched `Clock`, keeps building "utc",
    and builds "local" now.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - {ART}/notch_0_2_8250_2026_10_16.py:1-26
  - context_compass/mailbox_board.md:912-922
  - context_compass/attention_board.md:176-176
  - context_compass/attention_board.md:289-293
  - {ART}/send_m1_21_2026_10_16.py:1-64
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:649-777
  - release_docs/next_version_release.md:853-857
  - {ART}/release_note_rule2_2026_10_16.py:1-175
  - {ART}/release_example_rule2_2026_10_16.py:1-111
  - {ART}/runs/release_example_rule2_2026_10_16.txt:1-14
  - {ART}/release_example_rule2_before_2026_10_16.py:1-108
  - {ART}/runs/release_example_rule2_before_2026_10_16.txt:1-36
  IMPACT: The turn-in now waits on the owner's acceptance; closure and the rebuild follow it.
  NEXT: Ask the owner to accept the landing, with the remove_index_from_contract finding below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Found while verifying the release example; pre-existing and outside this ticket's scope.
    `remove_index_from_contract` raises RuntimeError "Spell version <id> not found for conduit ID <lender>." when the
    borrower holds a parked copy of a member beside the active one (a version staged on the linked index, or the old
    version after a notch) and the hash seed orders the parked id first, and it leaves the unlink half done.
    `_remove_index_from_contract` uncontracts the members in `spells_in_index()` order - a set of version-id
    strings, ordered by the process's hash seed - and `_remove_contracted_spell` matches the active contracted copy
    by index membership, not by its own id: for the parked member's id it removes the active copy (the other
    member's), then the active member's id finds no copy and raises; the parked copy stays, and the index detail's
    cleanup and the borrower's `_remove_contracted_index` after the loop never run. Probe (English staged on the
    linked index, notched away from, French active): PYTHONHASHSEED 0-9 give the same outcome per seed on 0.2.8249
    and 0.2.8250 - seeds 3, 4, 6, 8 and 9 raise "Spell version French not found" and leave English parked - so rule 2
    neither causes nor changes it. UNKNOWN: whether an index destroy meets the same order (a cleaned index is matched
    by the copy's own id).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  - src/melder/aether/spellbook/bind/spell_index.py:274-286
  - {ART}/probe_index_uncontract_after_notch.py:1-82
  - {ART}/runs/probe_index_uncontract_after_notch_seeds_gil0.txt:1-20
  IMPACT: An agent that stages versions on a linked index and then unlinks it can meet a RuntimeError and an orphaned
    parked copy, in about half of all processes. The fix - match the active copy by its own id - changes the
    borrower Book's removal path, outside the approved patch, so it is the owner's to place.
  NEXT: Put it to the owner with the acceptance question: a backlog task (recommended) or no action.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

OLD_NEXT_START = "Next: rule 2 with D3 is applied to the real tree"
OLD_NEXT_END = "\n\n## Project-Specific Additions"
NEW_NEXT = """Next: rule 2 with D3 is applied to the real tree - 18 files, byte-identical to the fresh tree that passed every
suite chunk with the GIL off and on; the race test is xfail naming
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (the owner's decision B). The four system docs
and their indexes (rubric 83 / 83 / 83 / 77, band B) and the graph (seven nodes re-authored and accepted,
reassembled) carry it, the patch docs are archived, `__version__` is 0.2.8250 (NOTICE M1-21 sent) and the release
note carries its entry with both examples verified. Remaining, in the turn-in order: (1) the owner's acceptance,
and his call on the remove_index_from_contract finding (Notes, 17:4xZ); (2) closure and board sync; (3) the
rebuild and its checks last."""

ROW_PREFIX = "| meld_contract_scan | in_progress | implementation | claude | melder_1 | none | "
ROW_NEXT = ("Owner acceptance, and his call on the remove_index_from_contract finding; then closure and board sync, "
            "rebuild last.")


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


text = read(TICKET)
assert "The notch, the NOTICE and the release-note entry are in." not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
i = text.index(OLD_NEXT_START)
j = text.index(OLD_NEXT_END, i)
assert text.count(OLD_NEXT_START) == 1
text = text[:i] + NEW_NEXT.replace("17:4xZ", NOW[11:16] + "Z") + text[j:]
check_lengths(text, TICKET)

board = read(BOARD)
rows = [l for l in board.split("\n") if l.startswith(ROW_PREFIX)]
assert len(rows) == 1, rows
cells = rows[0].split(" | ")
assert cells[9] == "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md", cells[9]
cells[6] = ROW_NEXT
cells[10] = NOW
board = board.replace(rows[0], " | ".join(cells), 1)

print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
print(("CHECK " if CHECK else "WRITE ") + str(BOARD))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))
