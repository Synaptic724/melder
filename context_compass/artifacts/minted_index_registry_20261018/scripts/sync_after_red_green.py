"""Bring S4's Tasks, handoff and board row current after the red/green MEASURE note (melder_1).

(1) The story's Tasks: the patch-doc task done, the fix task's tests noted; (2) its Context / Handoff Summary's State
and Next bullets; (3) the attention board's minted_index_registry row (blocker, next, updated_at). LF only, anchors
once, lines within 120 characters, every write read back. Usage: --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
BOARD = ROOT / "attention_board.md"
TS = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

OLD_TASKS = (
    "- [ ] Task: patch docs for the seam, the teardown and residency.\n"
    "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n"
)
NEW_TASKS = (
    "- [x] Task: patch docs for the seam, the teardown and residency (linked; PLAN note).\n"
    "- [ ] Task: the fix with symptom-named regression tests (written: red on 0.2.8256, green with A-D; MEASURE\n"
    "  note), docs, notch and the rebuild last.\n"
)
STATE_START = "- State: in_progress (melder_1), implementation. The owner's word is given"
NEXT_START = "- Next: (1) the patch docs"
NEW_STATE_NEXT = (
    "- State: in_progress (melder_1), implementation. The owner's word is given (DECISION note of\n"
    "  2026-10-18T18:00:11Z): A follows bind's registration (guard and call), with B and C, and D a docstring; no new\n"
    "  index state (ALIGNMENT_CHECK notes). The patch docs are linked (Artifact Links) and mapped to steps and tests\n"
    "  (PLAN note). The regression tests are in the repository: red on 0.2.8256, green with A-D in a /tmp mirror whose\n"
    "  whole tree passes but for S8's 18 held red tests, GIL off and on (MEASURE note); the edits to land are\n"
    "  runs/s4_preview_0_2_8256_abcd.diff in the lane folder. No src edit yet: spellbook.py and spell.py come back\n"
    "  from melder_0 when S1 and S2 of EPIC-2026-10-18-spell_identity_is_the_code land (M0-199, M1-40);\n"
    "  mutation_research.py is held.\n"
    "- Next: (1) melder_0's handover; then re-check A-D's anchors and the tests on the landed tree and apply A-D;\n"
    "  (2) the tests green in the repository, the whole tree in a mirror and the probes, GIL off and on; (3) system\n"
    "  documents with their indexes and the graph, the release note, the next free notch, closure, the rebuild last,\n"
    "  the files handed back.\n"
)
ROW = re.compile(r"^\| minted_index_registry \| in_progress \| implementation \| claude \| melder_1 \| none \| .*$", re.M)
NEW_ROW = ("| minted_index_registry | in_progress | implementation | claude | melder_1 | spellbook.py and spell.py with "
           "melder_0 until S1 and S2 land (M1-40) | Apply A-D on the landed tree once melder_0 hands the files back; "
           "the red tests turn green, then docs, notch, rebuild. | The index remove_from_spell_index mints is in the "
           "frame's spell registry, so its version is found and granted by spell_id. | The fix lands with tests, "
           "docs, notch and rebuild, or the owner redirects. | "
           "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md | %s | REQUIRED |" % TS)


def read_lf(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def main() -> None:
    """Prepare both files; write them with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    for block in (NEW_TASKS, NEW_STATE_NEXT):
        for line in block.split("\n"):
            if len(line) > 120:
                raise SystemExit("line over 120 chars (%d): %s" % (len(line), line))
    story = read_lf(STORY)
    if story.count(OLD_TASKS) != 1:
        raise SystemExit("tasks anchor found %d times" % story.count(OLD_TASKS))
    story = story.replace(OLD_TASKS, NEW_TASKS)
    start = story.index(STATE_START)
    end = story.index("\n\n", story.index(NEXT_START)) + 1
    if story.count(STATE_START) != 1 or story.count(NEXT_START) != 1:
        raise SystemExit("handoff anchors not unique")
    story = story[:start] + NEW_STATE_NEXT + story[end:]
    story, count = re.subn(r"^- Updated: \S+$", "- Updated: " + TS, story, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("no Updated line")
    board = read_lf(BOARD)
    if len(ROW.findall(board)) != 1:
        raise SystemExit("board row found %d times" % len(ROW.findall(board)))
    board = ROW.sub(lambda _match: NEW_ROW, board)
    print("story: tasks and handoff ready; board: row ready")
    if sys.argv[1] == "--apply":
        for path, text in ((STORY, story), (BOARD, board)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied (%s)" % TS)


main()
