"""Close tranche 3 in the epic's resume view (M0-185 sent, the owner told); board row to the owner's answers. <NOW>."""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
epic = EPIC.read_text(encoding="utf-8")
old_done = ("- Done since: the owner told of S1-S5 and their questions, then of S6-S8, their questions and the S2/S4\n"
            "  widenings (chat); melder_1 told of the six stories whose fixes sit in its files (M0-181, M0-182, M0-184).\n")
assert epic.count(old_done) == 1
epic = epic.replace(old_done, (
    "- Done since: the owner told of S1-S5, then S6-S8, then S9-S10 with their questions, the widenings and S8's\n"
    "  bind precedent (chat); melder_1 told of the eight stories whose fixes sit in its files (M0-181, M0-182,\n"
    "  M0-184, M0-185).\n"), 1)
old_next = ("- Next: (1) NOTICE melder_1 (M0-185) of S9, S10 and the S1/S5 widenings; (2) tell the owner of\n"
            "  S9-S10, S10's question and S8's bind precedent; (3) the owner's answers on the open questions.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, (
    "- Next: (1) the owner's answers on the open questions of S2, S5, S6, S8 and S10 (each story's Open Questions);\n"
    "  (2) a fourth tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S10 with its hand-back.\n"), 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
assert not [line for line in epic.splitlines() if len(line) > 120 and "/" not in line]

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
row_re = re.compile(r"^\| correctness_defects \| in_progress \| discovery \| claude \| melder_0 \| none \| NOTICE melder_1 "
                    r"\(M0-185\) of S9, S10 and the S1/S5 widenings, then tell the owner of S9-S10 and S10's question\. \|"
                    r"(.*)\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| \S+ \| REQUIRED \|$", re.M)
found = row_re.findall(b)
assert len(found) == 1, found
b = row_re.sub(lambda m: ("| correctness_defects | in_progress | handoff | claude | melder_0 | none | Owner answers the open "
                          "questions of S2, S5, S6, S8 and S10; then a fourth sweep tranche on the owner's word. |"
                          + m.group(1) + "| tickets/epics/2026-10-17_correctness_defects_epic.md | " + NOW
                          + " | REQUIRED |"), b, count=1)
EPIC.write_text(epic, encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("synced", NOW)
