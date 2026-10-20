"""Record rule 2 applied to the real tree (fresh-tree suites, real-tree smoke) and resync the board row (melder_1).

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
  CLAIM: Rule 2 is applied to the real tree (on melder_0's 0.2.8249 landing), not yet notched, documented or
    rebuilt. After melder_0's rebuild the scratch copy was refreshed from the real tree and the fourteen apply
    scripts re-run on it in the recorded order, each with --check first, the last the docstring correction melder_0
    reported in M0-177 (`_notch_spell` and `_apply_notch` now say the notch runs inside the transaction the Conduit
    admits and its seal is EXCLUSIVE, not spellbook INTENT); the two staged test files copied in. That fresh tree
    passed every suite chunk with the GIL off and on: unit_aether 4528, unit_sb 2578, unit_util 831, comp_aether
    1386, comp_sb 819, int_conduit 350 plus the race test (xfailed with the GIL off, xpassed with it on), int_sb 647,
    int_mt 54, int_aether 805, int_cryst 276, unit_cryst 607, comp_cryst 110, unit_mr 277, comp_mr 40, int_mr 67,
    comp_util 41 (23 skipped), unit_top 146, unit_build 116, int_live 1, unit_arch 18, exper 250 (4 skipped),
    unit_gh 491, unit_llm 28 (five chunks rerun after the repository folders they read were copied into the fresh
    tree, as the run file notes). The same scripts then applied to the real tree, --check first: its 18 changed
    files (7 src, 9 changed tests, 2 new tests) are byte-identical to the fresh tree, and a content compare of src/
    and tests/ finds no other difference either way. Real-tree smoke (the two new files and test_meld.py): 135
    passed and the race test xfailed with the GIL off, 135 passed and xpassed with it on. The real tree's suites
    were not rerun beyond that smoke: its src/ and tests/ are the fresh tree's byte for byte. `__version__` is
    still 0.2.8249; no git index lock.
  EVIDENCE:
  - {ART}/runs/rule2_fresh_suites_gil0.txt:1-26
  - {ART}/runs/rule2_fresh_suites_gil1.txt:1-23
  - {ART}/runs/rule2_landed_smoke.txt:1-2
  - {ART}/apply_rule2_src_spellbook_notch_seal_doc.py:1-46
  - src/melder/aether/spellbook/spellbook.py:3844-3915
  - src/melder/aether/conduit/conduit.py:5750-5758
  - src/melder/aether/conduit/conduit.py:6267-6310
  - src/melder/__version__.py:12-12
  IMPACT: The approved change set is in place on the real tree and green; turn-in remains: the system docs and
    their indexes, the graph, the patch promotion, the release note, the notch, NOTICE M1-21, closure, rebuild last.
  NEXT: Write the system docs (src_architecture, src_components, tests_architecture, tests_components) and
    regenerate their indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

OLD_SUMMARY_HEAD = """Build phase (2026-10-16T12:57:39Z): the owner approved the patch as a whole (D1-D5) and said start. melder_0 released
spellbook.py and transfer_of_ownership.py (2026-10-16T12:33:09Z) and still holds conduit.py for its
TASK-2026-10-16-public_notch_target_for_staged_versions, so every file but conduit.py is built first and D3's
conduit.py lines follow melder_0's HANDOFF (asked in M1-20). Messaging is the mailbox (owner, 2026-10-16).
"""
NEW_SUMMARY_HEAD = """Turn-in phase (2026-10-16T16:37Z): the owner approved the patch as a whole (D1-D5) on 2026-10-16. melder_0 released
spellbook.py and transfer_of_ownership.py at 12:33:09Z and conduit.py with its 0.2.8249 landing (M0-177, 16:13Z), so
every file of the change set is melder_1's. Messaging is the mailbox (owner, 2026-10-16).
"""
OLD_SUMMARY_NEXT_START = "Next: (1) D3 on the scratch copy"
OLD_SUMMARY_NEXT_END = "\n\n## Project-Specific Additions"
NEW_SUMMARY_NEXT = """Next: rule 2 with D3 is applied to the real tree - 18 files, byte-identical to the fresh tree that passed every
suite chunk with the GIL off and on; the race test is xfail naming
TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (the owner's decision B). Remaining, in the
turn-in order: (1) the system docs (src_architecture, src_components, tests_architecture, tests_components) with
their indexes, the graph descriptors, the patch docs promoted; (2) the release note, one notch above 0.2.8249 and
NOTICE M1-21; (3) closure and board sync, then the rebuild and its checks last."""

ROW_PREFIX = "| meld_contract_scan | in_progress | implementation | claude | melder_1 | none | "
ROW_NEXT = ("Write the system docs and indexes, the graph and the release note; then the notch above 0.2.8249, "
            "NOTICE, closure, rebuild last.")


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
assert "Rule 2 is applied to the real tree (on melder_0's 0.2.8249 landing)" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
text = replace_once(text, OLD_SUMMARY_HEAD, NEW_SUMMARY_HEAD, TICKET)
i = text.index(OLD_SUMMARY_NEXT_START)
j = text.index(OLD_SUMMARY_NEXT_END, i)
assert text.count(OLD_SUMMARY_NEXT_START) == 1
text = text[:i] + NEW_SUMMARY_NEXT + text[j:]
check_lengths(text, TICKET)

board = read(BOARD)
rows = [l for l in board.split("\n") if l.startswith(ROW_PREFIX)]
assert len(rows) == 1, rows
cells = rows[0].split(" | ")
# cells: [| work_item, status, mode, owner, agent_name, blocker, next, outcome, exit_signal, ticket, updated_at, reread |]
assert cells[9] == "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md", cells[9]
cells[6] = ROW_NEXT
cells[10] = NOW
board = board.replace(rows[0], " | ".join(cells), 1)

print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
print(("CHECK " if CHECK else "WRITE ") + str(BOARD))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
    BOARD.write_bytes(board.encode("utf-8"))
