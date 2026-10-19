"""Open melder_1's S7 lane (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).

The story moves ready -> in_progress with its DECISION note, the attention board gains the row and its detail entry,
the artifact board the lane folder's row, and melder_0 gets M1-43 (the file claim) with its alert. LF only; every
anchor found once; read back. Usage (from anywhere): open_s7.py --check | --apply
"""
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
BOARD = ROOT / "attention_board.md"
ARTIFACTS = ROOT / "artifact_board.md"
MAILBOX = ROOT / "mailbox_board.md"
NOW = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
TICKET = "tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's order puts this story with melder_1 now. Of the correctness fixes he gave melder_1 (chat
    2026-10-18: "do the ones without open questions please" - S9, S4 and S7 - with "go over them again before you
    make changes and let him know"), S9 landed at 0.2.8256 and S4 at 0.2.8259; on S4's report he said "lets move on"
    (chat 2026-10-19). S8 stays on his hold. So S7 is re-verified on 0.2.8259 and its teardown path re-read whole
    before any change; the patch (a component patch for the Book teardown) and the exact edits go to the owner
    before the first src edit; spellbook.py is claimed from melder_0 by message (M1-43), nothing edited before his
    answer. S4 touched the same teardown (the root's teardown now unregisters parked versions' indexes), so the
    probe is re-read against it.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:908-928
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md:1-12
  - src/melder/aether/spellbook/spellbook.py:2695-2736
  IMPACT: The ENTRY_GATE's scheduling and assignment are met; the board row exists; the patch, the owner's word
    on the edits and the file claim remain before any src edit.
  NEXT: Re-run probe T1-T5 on 0.2.8259 with the GIL off and on; re-read Spellbook teardown whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""

STORY_EDITS = (
    ("- Status: ready\n", "- Status: in_progress\n"),
    ("- Agent Name: unassigned\n", "- Agent Name: melder_1\n"),
    ("- Agent Role: UNKNOWN\n", "- Agent Role: synaptic_python_developer\n"),
    ("- Updated: 2026-10-17T21:13:35Z\n", "- Updated: %s\n" % NOW),
    ("- from_state: draft\n- to_state: ready\n"
     "- transition_reason: the defect is proven on 0.2.8252 by a probe with the GIL off and on (Notes).\n",
     "- from_state: ready\n- to_state: in_progress\n"
     "- transition_reason: the owner scheduled the story for melder_1 (chat 2026-10-18 and 2026-10-19; DECISION\n"
     "  note); the defect is re-verified on the current tree before any change.\n"),
    ("- 2026-10-17T21:13:35Z: filed under EPIC-2026-10-17-correctness_defects from sweep A7 (Notes).\n",
     "- 2026-10-17T21:13:35Z: filed under EPIC-2026-10-17-correctness_defects from sweep A7 (Notes).\n"
     "- %s: scheduled for melder_1 on the owner's order, after S4 (DECISION note).\n" % NOW),
    ("  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt\n",
     "  - artifacts/correctness_defects_20261017/runs/probe_book_teardown_parked_gil1.txt\n"
     "  - artifacts/book_teardown_parked_20261019/ (melder_1's lane: re-runs, scripts, notes)\n"),
    ("- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in\n"
     "  spellbook.py, which melder_1 holds.\n"
     "- Next: (1) the owner's scheduling; (2) patch docs; (3) the fix, its tests, docs, notch and the rebuild.\n",
     "- State: in_progress (melder_1), discovery: scheduled on the owner's order after S4 (DECISION note); filed by\n"
     "  melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in spellbook.py, claimed from melder_0\n"
     "  (M1-43).\n"
     "- Next: (1) re-run probe T1-T5 on 0.2.8259 and re-read the Book teardown whole; (2) the patch and the exact\n"
     "  edits for the owner; (3) the fix, its tests, docs, notch and the rebuild last.\n"),
    ("\n## Closure Confirmation\n", "\n" + NOTE + "\n## Closure Confirmation\n"),
)

ROW = ("| book_teardown_parked | in_progress | discovery | claude | melder_1 | none | Re-run probe T1-T5 on 0.2.8259 "
       "and re-read the Book teardown whole; then the patch and the exact edits for the owner. | A Book's teardown "
       "retires its parked versions and the indexes only they hold. | The fix lands with tests, docs, notch and "
       "rebuild, or the owner redirects. | %s | %s | REQUIRED |\n" % (TICKET, NOW))
DETAIL = ("- WORK_ITEM: book_teardown_parked\n"
          "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
          "  RESUME_HIERARCHY:\n"
          "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
          "    - %s\n" % TICKET)
ART_ROW = ("| %s | artifacts/book_teardown_parked_20261019/ | investigation_evidence | active | retain_as_reference | "
           "melder_1's lane: the re-run of probe T1-T5 on 0.2.8259, scripts and notes drafts; the fix's red and green "
           "runs and rebuild logs land here. | %s | HELPFUL |\n" % (TICKET, NOW))
MESSAGE = f"""- TO: melder_0
  FROM: melder_1
  DATETIME: {NOW}
  TYPE: QUESTION
  CLAIM: M1-43. On the owner's word I take S7 (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned)
    next. Its fix sits in spellbook.py (the Book teardown: `_cleanup_spells`, `_cleanup_components`), so I claim
    spellbook.py back for it - and spell.py too if the patch needs `Spell.cleanup`. May I have them? I edit
    nothing before your answer and the owner's word on the exact edits; re-verification and the patch come first.
  EVIDENCE: context_compass/{TICKET}
  ACK_REQUESTED: true
"""
ALERT = f"- NEW MESSAGE for melder_0 (from melder_1, {NOW})\n"


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
    for line in (NOTE + MESSAGE).split("\n"):
        stripped = line.strip()
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]):
            raise SystemExit("line over 120: " + line)
    board = insert_before(load(BOARD), "<!-- END USER-DEFINED: active_items -->", ROW, "board")
    board = insert_before(board, "<!-- END USER-DEFINED: active_attention_details -->", DETAIL, "board")
    board = insert_before(board, "<!-- END USER-DEFINED: alerts -->", ALERT, "board")
    arts = insert_before(load(ARTIFACTS), "<!-- END USER-DEFINED: active_artifacts -->", ART_ROW, "artifacts")
    mailbox = insert_before(load(MAILBOX), "<!-- END USER-DEFINED: messages -->", MESSAGE, "mailbox")
    print("ready:", NOW)
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (BOARD, board), (ARTIFACTS, arts), (MAILBOX, mailbox)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied")


main()
