"""Row S1's probes on artifact_board.md and widen the epic's scripts row (melder_0, 2026-10-18).

Run from context_compass/: python3 artifacts/spell_identity_20261018/scripts/sync_s1_artifact_rows.py <UTC stamp>
"""
import pathlib
import sys

STAMP = sys.argv[1]
BOARD = pathlib.Path("artifact_board.md")
text = BOARD.read_text(encoding="utf-8")
old_scripts = (
    "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | artifacts/spell_identity_20261018/ | "
    "investigation_evidence | active | retain_as_reference | The epic's scripts: open_epic.py (the epic and its "
    "stories), fix_open_epic.py and sync_ranges.py (re-wraps, evidence ranges, M1-28), wrap_long_lines.py, "
    "turn_in_sync.py (S6's turn-in and the routing). | 2026-10-18T12:06:53Z | HELPFUL |"
)
new_scripts = (
    "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | artifacts/spell_identity_20261018/ | "
    "investigation_evidence | active | retain_as_reference | The epic's scripts: open_epic.py (the epic and its "
    "stories), fix_open_epic.py and sync_ranges.py (re-wraps, evidence ranges, M1-28), wrap_long_lines.py, "
    "turn_in_sync.py (S6's turn-in and the routing), record_owner_calls.py (calls 1-3 and 5), record_s1_measure.py "
    "and sync_s1_artifact_rows.py (S1's MEASURE note and rows); probes/ and runs/ are rowed under S1. | "
    f"{STAMP} | HELPFUL |"
)
new_row = (
    "| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | artifacts/spell_identity_20261018/probes/ | "
    "investigation_evidence | active | retain_as_reference | The code digest v2 prototype (code_digest_v2.py), cases "
    "E01-E34 (probe_code_digest_cases.py) and the src/melder corpus and cost probe (probe_code_digest_corpus.py), "
    "with their runs under runs/ (hash seeds 1 and 2, GIL 0 and 1); S1's tests start here. | "
    f"{STAMP} | REQUIRED |"
)
assert text.count(old_scripts) == 1
text = text.replace(old_scripts, new_scripts + "\n" + new_row)
BOARD.write_text(text, encoding="utf-8")
print("artifact board synced", STAMP)
