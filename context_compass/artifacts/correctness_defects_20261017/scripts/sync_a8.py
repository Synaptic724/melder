"""Record sweep A8: link the residency probe to the minted-index story, log it on the epic, point the row at A9.

Run from context_compass/ with <NOW>. Every edit is checked in memory before anything is written.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
ART = "artifacts/correctness_defects_20261017/"
S4 = "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
S4_ID = "STORY-2026-10-17-minted_index_missing_from_frame_registry"
S7_ID = "STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned"
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
PROBE = ART + "probes/probe_research_residency_moves.py"
RUN0 = ART + "runs/probe_research_residency_moves_gil0.txt"
RUN1 = ART + "runs/probe_research_residency_moves_gil1.txt"


def check(text: str) -> str:
    """Refuse long lines that hold no path."""
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


story = pathlib.Path(S4).read_text(encoding="utf-8")
after = "  - " + ART + "runs/probe_minted_index_registry_gil1.txt\n"
assert story.count(after) == 1
story = story.replace(after, after + "  - " + PROBE + " (cases V2-V3: residency_view; FACT note)\n  - " + RUN0
                      + "\n  - " + RUN1 + "\n", 1)
story, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, story, count=1)
assert count == 1
check(story)

epic = EPIC.read_text(encoding="utf-8")
log_anchor = ("  " + S7_ID + " and widened\n"
              "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (MEASURE note).\n")
assert epic.count(log_anchor) == 1
epic = epic.replace(log_anchor, log_anchor + "- " + NOW + ": sweep A8 checked, no story; widened\n  " + S4_ID
                    + " (residency_view; MEASURE note).\n", 1)
old_state = "- State: in_progress (melder_0), discovery. A1-A7 are done; seven stories filed (ready, unassigned):\n"
assert epic.count(old_state) == 1
epic = epic.replace(old_state, "- State: in_progress (melder_0), discovery. A1-A8 are done; seven stories filed (ready, unassigned):\n", 1)
old_s4 = "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2),\n"
assert epic.count(old_s4) == 1
epic = epic.replace(old_s4, "  STORY-2026-10-17-minted_index_missing_from_frame_registry (p2; MutationResearch residency\n"
                    "  misses the version too, A8),\n", 1)
old_next = ("- Next: (1) A8 the views of moved and separated versions (MutationResearch residency, Nexus);\n"
            "  (2) tell the owner of the sixth and seventh stories, the sixth's question and the A7 widening.\n")
assert epic.count(old_next) == 1
epic = epic.replace(old_next, "- Next: (1) A9 what a notch whose commit validation fails leaves behind (A8 MEASURE note);\n"
                    "  (2) tell the owner of the sixth and seventh stories, the sixth's question and the A7/A8 widenings.\n", 1)
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
check(epic)

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
assert a.count(end_art) == 1
row = ("| " + S4 + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases V2-V3 (residency_view of "
       "a version in a minted index) with their runs (runs/probe_research_residency_moves_gil0.txt, _gil1.txt); "
       "re-run at the fix. | " + NOW + " | HELPFUL |\n")

board = pathlib.Path("attention_board.md")
b = board.read_text(encoding="utf-8")
old_row_next = ("| Sweep A8: read MutationResearch residency and Nexus publication whole for moved and separated "
                "versions, then probe. |")
assert b.count(old_row_next) == 1
b = b.replace(old_row_next, "| Sweep A9: read the notch transaction's commit path whole and probe what a notch whose "
              "commit validation fails leaves behind. |", 1)
row_re = re.compile(r"^(\| correctness_defects \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$", re.M)
assert len(row_re.findall(b)) == 1
b = row_re.sub(lambda m: m.group(1) + NOW + m.group(2), b, count=1)

pathlib.Path(S4).write_text(story, encoding="utf-8")
EPIC.write_text(epic, encoding="utf-8")
art.write_text(a.replace(end_art, row + end_art, 1), encoding="utf-8")
board.write_text(b, encoding="utf-8")
print("synced A8", NOW)
