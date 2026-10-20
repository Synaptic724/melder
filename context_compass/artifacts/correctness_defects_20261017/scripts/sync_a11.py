"""Record sweep A11 (checked, no story) in the epic; link the bind probe to S8; board row to sweep A12. Run with <NOW>."""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S8 = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
S9_ID = "STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions"
ART = "artifacts/correctness_defects_20261017/"
BPROBE = ART + "probes/probe_broken_late_bind.py"


def check(text: str) -> str:
    """Refuse long lines that hold no path."""
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


epic = EPIC.read_text(encoding="utf-8")
log_anchor = "  " + S9_ID + " (MEASURE note).\n"
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A11 checked, no story (a failed late bind keeps\n"
                    "  its spell by design); its precedent added to STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers\n"
                    "  (FACT notes).\n", 1)
epic = epic.replace("A1-A10 are done; nine stories filed", "A1-A11 are done; nine stories filed", 1)
old_next = ("- Next: tranche 3 (PLAN note): (1) A11 a bind whose commit validation fails; (2) A12 graft of an\n"
            "  index with parked versions; (3) NOTICE melder_1 of S9 and tell the owner.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: tranche 3 (PLAN note): (1) A12 graft of an index with parked versions; (2) NOTICE\n"
                    "  melder_1 of S9 and tell the owner (S9; S8's bind precedent).\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

s8 = pathlib.Path(S8).read_text(encoding="utf-8")
after = "  - " + ART + "runs/probe_failed_notch_commit_gil1.txt\n"
assert s8.count(after) == 1
s8 = s8.replace(after, after + "  - " + BPROBE + " (cases B2-B3: the bind precedent; FACT note)\n"
                "  - " + ART + "runs/probe_broken_late_bind_gil0.txt\n  - " + ART + "runs/probe_broken_late_bind_gil1.txt\n", 1)
s8, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, s8, count=1)
assert count == 1
check(s8)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1
row = ("| " + S8 + " | " + BPROBE + " | investigation_evidence | ready | retain_as_reference | Cases B1-B3 (a late bind whose "
       "commit fails keeps its spell; the precedent for S8's option (b)) with their runs "
       "(runs/probe_broken_late_bind_gil0.txt, _gil1.txt). | " + NOW + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A11: read a post-conjure bind whose commit validation fails whole (what the raise "
                "leaves registered), then probe. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A12: read GraftRunner whole for an index whose members include parked versions, "
              "then probe. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

EPIC.write_text(epic, encoding="utf-8")
pathlib.Path(S8).write_text(s8, encoding="utf-8")
art.write_text(a.replace(end_art, row + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("synced A11", NOW)
