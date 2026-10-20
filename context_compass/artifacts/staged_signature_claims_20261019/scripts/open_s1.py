"""Open melder_1's S1 lane (STORY-2026-10-17-staged_version_releases_active_signature).

The story moves ready -> in_progress with its DECISION note; the attention board gains the row and its detail
entry, the artifact board the lane folder's row. No file claim: melder_0 has departed and handed every file to
melder_1 (M0-211). LF only; every anchor found once; read back. Usage: open_s1.py --check | --apply
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
BOARD = ROOT / "attention_board.md"
ARTIFACTS = ROOT / "artifact_board.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
TICKET = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order puts this story with melder_1 now. He lifted S8's hold with "melder_1 fixes S8, then S1,
    S2 and S5, one at a time" (M1-45, M1-46), and after S8 landed and was turned in he said "So if you know how to
    implement try doing a few small ones you have space" (chat 2026-10-19). S1 is the smallest: one seam,
    `Spellbook._destroy_spell_index`, and the arguments its two callers pass. melder_0 has departed and handed
    every file to melder_1 (M0-211), so spellbook.py needs no claim. Before any src edit: the defect is re-verified
    on 0.2.8262 (the probe of 2026-10-17 calls `find_spell_by_id`, gone since 0.2.8253, so it is rewritten for the
    current names), the seam is re-read whole, the patch is written and linked, and the regression tests are red.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1147-1169
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1223-1239
  - src/melder/aether/spellbook/spellbook.py:4654-4699
  IMPACT: The ENTRY_GATE's scheduling and assignment are met and the board row exists; the patch and the red tests
    remain before the first src edit.
  NEXT: Re-run the claims cases (C1-C4, C6, rewritten for 0.2.8262) with the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""

STORY_EDITS = (
    ("- Status: ready\n", "- Status: in_progress\n"),
    ("- Agent Name: unassigned\n", "- Agent Name: melder_1\n"),
    ("- Agent Role: UNKNOWN\n", "- Agent Role: synaptic_python_developer\n"),
    ("- Updated: 2026-10-17T21:55:46Z\n", "- Updated: %s\n" % NOW),
    ("- from_state: draft\n- to_state: ready\n"
     "- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).\n",
     "- from_state: ready\n- to_state: in_progress\n"
     "- transition_reason: the owner scheduled the story for melder_1 (M1-45; chat 2026-10-19: \"try doing a few\n"
     "  small ones\"; DECISION note); the defect is re-verified on the current tree before any change.\n"),
    ("- 2026-10-17T21:55:46Z: the open question settled by the owner's answer on the notch-signature story: the minimal\n"
     "  fix (DECISION note).\n",
     "- 2026-10-17T21:55:46Z: the open question settled by the owner's answer on the notch-signature story: the minimal\n"
     "  fix (DECISION note).\n"
     "- %s: scheduled for melder_1 on the owner's order, after S8 (DECISION note).\n" % NOW),
    ("  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt\n",
     "  - artifacts/correctness_defects_20261017/runs/probe_graft_parked_members_gil1.txt\n"
     "  - artifacts/staged_signature_claims_20261019/ (melder_1's lane: re-runs, scripts, notes)\n"),
    ("- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in\n"
     "  spellbook.py, which melder_1 holds until its rule-2 closure.\n"
     "- Next: (1) the owner schedules it; (2) patch docs for `_destroy_spell_index`; (3) the fix, its tests, docs, notch\n"
     "  and the rebuild.\n",
     "- State: in_progress (melder_1), discovery: scheduled on the owner's order after S8 (DECISION note); filed by\n"
     "  melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in spellbook.py, which melder_1 holds.\n"
     "- Next: (1) re-run C1-C4 and C6 on 0.2.8262 and re-read the seam whole; (2) the patch, linked here; (3) red\n"
     "  regression tests, the fix, docs, notch and the release note; the rebuild comes once, last in the pass.\n"),
    ("\n## Closure Confirmation\n", "\n" + NOTE + "\n## Closure Confirmation\n"),
)

ROW = ("| staged_signature_claims | in_progress | discovery | claude | melder_1 | none | Re-run C1-C4 and C6 on 0.2.8262 "
       "and re-read `_destroy_spell_index` whole; then the patch and red tests. | Staging, moving or disposing a "
       "parked version leaves every other spell's binding signature and Book route in place. | The fix lands with "
       "tests, docs and notch (the rebuild last in the pass), or the owner redirects. | %s | %s | REQUIRED |\n"
       % (TICKET, NOW))
DETAIL = ("- WORK_ITEM: staged_signature_claims\n"
          "  SWITCH_TRIGGER: The fix lands with tests, docs and notch (the rebuild last in the pass), or the owner "
          "redirects.\n"
          "  RESUME_HIERARCHY:\n"
          "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
          "    - %s\n" % TICKET)
ART_ROW = ("| %s | artifacts/staged_signature_claims_20261019/ | investigation_evidence | active | retain_as_reference | "
           "melder_1's lane: the claims cases rewritten for 0.2.8262 and their runs, scripts and notes drafts; the "
           "fix's red and green runs land here. | %s | HELPFUL |\n" % (TICKET, NOW))


def load(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def insert_before(text: str, marker: str, block: str, name: str) -> str:
    """Insert `block` before the one `marker` in `text`."""
    if text.count(marker) != 1:
        raise SystemExit("%s: marker found %d times: %s" % (name, text.count(marker), marker))
    return text.replace(marker, block + marker)


def main() -> None:
    """Prepare every edit, then write with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    story = load(STORY)
    for old, new in STORY_EDITS:
        if story.count(old) != 1:
            raise SystemExit("story anchor found %d times: %r" % (story.count(old), old[:60]))
        story = story.replace(old, new)
    for line in story.split("\n") + DETAIL.split("\n"):
        stripped = line.strip()
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]):
            if line in NOTE or line in DETAIL or any(line in new for _, new in STORY_EDITS):
                raise SystemExit("line over 120: " + line)
    board = insert_before(load(BOARD), "<!-- END USER-DEFINED: active_items -->", ROW, "board")
    board = insert_before(board, "<!-- END USER-DEFINED: active_attention_details -->", DETAIL, "board")
    arts = insert_before(load(ARTIFACTS), "<!-- END USER-DEFINED: active_artifacts -->", ART_ROW, "artifacts")
    print("ready:", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (BOARD, board), (ARTIFACTS, arts)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied")


main()
