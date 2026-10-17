"""Record the owner report and M0-184 in the epic's resume view; set the board row to sweep A10. Run with <NOW>."""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
epic = EPIC.read_text(encoding="utf-8")
old_done = ("- Done since: the owner told what was filed and the two open questions (chat); melder_1 told of the four\n"
            "  stories whose fixes sit in its files (M0-181, M0-182; it carries them to the owner with its fix #1).\n")
assert epic.count(old_done) == 1
epic = epic.replace(old_done, (
    "- Done since: the owner told of S1-S5 and their questions, then of S6-S8, their questions and the S2/S4\n"
    "  widenings (chat); melder_1 told of the six stories whose fixes sit in its files (M0-181, M0-182, M0-184).\n"), 1)
old_next = ("- Next: (1) NOTICE melder_1 (M0-184) of S7, S8 and the A7/A8 widenings; (2) tell the owner of\n"
            "  S6-S8, their open questions and the widenings; (3) plan the next tranche (PLAN note).\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, (
    "- Next: tranche 3 (PLAN note): (1) A10 cleanup_spell of an active version with parked siblings; (2) A11 a bind\n"
    "  whose commit validation fails; (3) A12 graft of an index with parked versions.\n"), 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| NOTICE melder_1 (M0-184) of the teardown and failed-notch stories and the two widenings, "
                "then tell the owner of S6-S8 and their questions. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A10: read the active branch of _dispose_spell and Conduit.cleanup_spell whole for an "
              "active version with parked siblings, then probe. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)
EPIC.write_text(epic, encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("synced", NOW)
