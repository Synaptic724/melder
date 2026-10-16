"""Record the owner's race-scope decision, the follow-up task and the race test's xfail marker (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose B for the meld-vs-notch race (chat 2026-10-16, "Separate task (Recommended)", after asking
    whether it concerns all melds - it concerns only a borrower's contract consumer melded on another thread while
    its provider is being notched, GIL off). Rule 2 lands as approved; the race is
    TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (backlog, p1: one kind silently returns a
    consumer built with the SpellContract default), opened with the measurements and the mechanism and its artifact
    row. The race test carries `@pytest.mark.xfail(strict=False, raises=AssertionError, reason=...)` naming that
    task; any other failure of the test still fails it. On the scratch copy the test file then runs 13 passed plus
    the race test 2 xfailed / 3 xpassed in five GIL-off runs and 5 xpassed in five GIL-on runs. The RISK of
    14:08:56Z is settled by this decision.
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:1-229
  - {ART}/open_race_followup_task_2026_10_16.py:1-272
  - {ART}/apply_rule2_tests_race_xfail.py:1-39
  - {ART}/runs/rule2_race_xfail_gil0.txt:1-20
  - {ART}/runs/rule2_race_xfail_gil1.txt:1-20
  IMPACT: Nothing in the approved patch changes; removing the xfail marker belongs to the follow-up's exit gate.
  NEXT: Build D3 on the scratch copy (notch-back reactivation, the grant docstring, the anchored notch-back test), to
    be re-checked against conduit.py when melder_0 hands it over.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

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


out = {}
text = read(TICKET)
assert "The owner chose B for the meld-vs-notch race" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
start = text.index("Next: (1) the owner's answer on the meld-vs-notch race (DECISION_REQUEST of ")
end = text.index("after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n", start)
end += len("after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n")
new_next = ("Next: (1) D3 on the scratch copy (notch-back reactivation, the grant docstring, the anchored notch-back test);\n"
            "every other file is built and green with the GIL off and on, the race test xfail naming\n"
            "TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (owner's decision B); (2) after melder_0\n"
            "lands and hands conduit.py over: re-check D3 against it, copy the build to the real tree (baselines compared,\n"
            "apply scripts with --check) and run the suites; (3) docs, release note, one notch, closure, rebuild.\n")
text = text[:start] + new_next + text[end:]
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTE.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
out[TICKET] = text

board = read(BOARD)
row = [l for l in board.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(row) == 1, row
old_cell = ("| Owner answers the race scope (A: fold a fix in; B: land with the race test xfail and a follow-up task); "
            "then copy the build to the real tree. |")
new_cell = ("| Build D3 on the scratch copy; after melder_0 lands and hands conduit.py over, copy the build to the real "
            "tree and run the suites. |")
new_row = replace_once(row[0], old_cell, new_cell, BOARD)
stamp = [c.strip() for c in row[0].split("|")][-3]
new_row = replace_once(new_row, f"| {stamp} | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, row[0], new_row, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
