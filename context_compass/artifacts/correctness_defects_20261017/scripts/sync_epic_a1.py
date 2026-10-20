"""Sync EPIC-2026-10-17-correctness_defects and the artifact board after sweep A1's two stories were written.

(file_stories_a1.py wrote both stories, then stopped on one long line in the epic's resume view before touching the
epic or the board; this finishes its last two steps.)  Run from context_compass/ with <NOW>.
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-17_correctness_defects_epic.md")
S1 = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
S2 = "tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
S1_ID = "STORY-2026-10-17-staged_version_releases_active_signature"
S2_ID = "STORY-2026-10-17-notch_moves_signature_by_incoming_key_only"
PROBE = "artifacts/correctness_defects_20261017/probes/probe_signature_claims.py"
assert pathlib.Path(S1).exists() and pathlib.Path(S2).exists()

epic = EPIC.read_text(encoding="utf-8")
old_stories = "## Stories (Required to Complete)\n- none yet; one per confirmed defect.\n"
assert epic.count(old_stories) == 1
epic = epic.replace(old_stories, "## Stories (Required to Complete)\n- [ ] Story: " + S1_ID + " - staging, moving or\n"
                    "  disposing a parked version drops the binding signature of the active spell keyed like it (sweep A1).\n"
                    "- [ ] Story: " + S2_ID + " - a notch moves signatures by the\n"
                    "  incoming key alone: a parked version keeps its claim, or an active spell's key is taken (sweep A1).\n", 1)
log_line = re.search(r"(?m)^- \S+: opened on the owner's direction \(DECISION note\)\.\n", epic).group(0)
epic = epic.replace(log_line, log_line + "- " + NOW + ": sweep A1 filed " + S1_ID + " and\n  " + S2_ID
                    + " (MEASURE note).\n", 1)
start = epic.index("## Context / Handoff Summary\n") + len("## Context / Handoff Summary\n")
end = epic.index("\n## Project-Specific Additions", start)
view = ("- Scope: correctness defects - structure Melder records wrong or leaves stuck - by the owner's rulings (DECISION\n"
        "  note); read-only; one story per confirmed defect; melder_1's lane excluded.\n"
        "- State: in_progress (melder_0), discovery. Sweep A1 done: two defects filed, both binding-signature claims -\n"
        "  " + S1_ID + " (p1) and\n  " + S2_ID + " (p2, one open question). Their fixes sit in\n"
        "  spellbook.py (melder_1's until its rule-2 closure).\n"
        "- Next: (1) sweep A2, cleanup_spell of a parked version (PLAN note); (2) A3-A5 in order; (3) tell the owner\n"
        "  what was filed.\n")
epic = epic[:start] + view + epic[end:]
epic, count = re.subn(r"(?m)^- Updated: \S+$", "- Updated: " + NOW, epic, count=1)
assert count == 1
long = [line for line in epic.splitlines() if len(line) > 120 and "/" not in line]
assert not long, long
EPIC.write_text(epic, encoding="utf-8")

art = pathlib.Path("artifact_board.md")
a = art.read_text(encoding="utf-8")
end_art = "<!-- END USER-DEFINED: active_artifacts -->"
rows = ""
for path, cases in ((S1, "C1-C4, C6"), (S2, "C5, C7")):
    rows += ("| " + path + " | " + PROBE + " | defect_reproducer | ready | retain_as_reference | Cases " + cases
             + " with their runs (runs/probe_signature_claims_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW
             + " | HELPFUL |\n")
assert a.count(end_art) == 1 and S1 not in a and S2 not in a
art.write_text(a.replace(end_art, rows + end_art, 1), encoding="utf-8")
print("synced epic and artifact board", NOW)
