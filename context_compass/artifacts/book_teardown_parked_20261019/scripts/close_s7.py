"""S7 closure: story turn-in edits, the move to completed/, attention and artifact board sync, the notch notice and
the patch folder archived (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned; melder_1, adapted from
close_s4.py). Each old text must occur exactly once; LF only; refuse an existing target. When the closed-anchor
region would pass 12 rows, the row with the oldest closed_at goes.
Usage (repository root): close_s7.py --notch 0.2.82NN --check | --apply
"""
import datetime
import os
import pathlib
import re
import sys

CC = pathlib.Path("context_compass")
NAME = "2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
STORY = CC / "tickets/stories" / NAME
DONE = CC / "tickets/stories/completed" / NAME
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
PATCH = CC / "system_docs/patches/active/book_teardown_parked_2026_10_19"
PATCH_DONE = CC / "system_docs/patches/completed/book_teardown_parked_2026_10_19"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DAY = TS[:10]
ACTIVE_REF = "tickets/stories/" + NAME
DONE_REF = "tickets/stories/completed/" + NAME
TITLE = ("# Story: book_teardown_leaves_parked_versions_uncleaned - a Book's teardown retires its parked versions "
         "too\n")

STORY_EDITS = [
    (
        TITLE + "\n## Metadata\n",
        TITLE + "\n- Completed: {TS}\n"
        "- Summary: landed and notched {N} - a Spellbook's teardown retires every parked version with the local\n"
        "  teardown `cleanup_spell`'s parked branch runs and cleans every index only parked versions hold\n"
        "  (`_cleanup_spells`), so no version of a dead Book reads live or refuses its own cleanup. S7 tests green with\n"
        "  the GIL off and on, the whole tree as the MEASURE note records; release note section \"A Spellbook's teardown\n"
        "  cleans its parked versions too\"; system documents and graph; rebuilt last. Turned in after the landing, on\n"
        "  the owner's word on the edit (2026-10-19).\n"
        "\n## Metadata\n",
    ),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        "- from_state: ready\n- to_state: in_progress\n"
        "- transition_reason: the owner scheduled the story for melder_1 (chat 2026-10-18 and 2026-10-19; DECISION\n"
        "  note); the defect is re-verified on the current tree before any change.\n",
        "- from_state: in_progress\n- to_state: done\n"
        "- transition_reason: landed at {N} and turned in after the landing (the owner's word on the edit, DECISION\n"
        "  note of 2026-10-19T01:00:17Z; closure is routine once criteria and tests are met). Before that: ready ->\n"
        "  in_progress when the owner scheduled the story for melder_1 (chat 2026-10-18 and 2026-10-19; DECISION\n"
        "  note).\n",
    ),
    (
        "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n"
        "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
        "- [x] Task: the fix with symptom-named regression tests (red on 0.2.8259, green at {N}; MEASURE notes),\n"
        "  docs, notch and the rebuild last (the rebuild follows this closure, as the contribution guide orders).\n"
        "- [x] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
    ),
    (
        "- [ ] No story-state transition without linked task-state evidence.\n"
        "- [ ] No closure while required tasks remain active or un-routed.\n"
        "- [ ] No cross-task synthesis claims without ticket-note evidence pointers.\n",
        "- [x] No story-state transition without linked task-state evidence.\n"
        "- [x] No closure while required tasks remain active or un-routed.\n"
        "- [x] No cross-task synthesis claims without ticket-note evidence pointers.\n",
    ),
    (
        "- 2026-10-19T00:51:08Z: scheduled for melder_1 on the owner's order, after S4 (DECISION note).\n",
        "- 2026-10-19T00:51:08Z: scheduled for melder_1 on the owner's order, after S4 (DECISION note).\n"
        "- 2026-10-19T01:00:17Z: the owner's word on the edit, \"Go ahead\" (DECISION note).\n"
        "- {TS}: landed at {N} and turned in (MEASURE and FACT notes).\n",
    ),
    (
        "  - system_docs/patches/active/book_teardown_parked_2026_10_19/ (architecture and Spellbook component patch)\n",
        "  - system_docs/patches/completed/book_teardown_parked_2026_10_19/ (architecture and Spellbook component patch;\n"
        "    promoted at landing, archived at turn-in)\n",
    ),
    (
        "- DISPOSITION: retain_as_reference\n- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's "
        "reproducer\n",
        "- DISPOSITION: retain_as_reference (the probe, its runs and the lane folder); promote_to_documentation (the\n"
        "  patch)\n"
        "- CLEANUP_TRIGGER: the probe was re-run at the fix and is kept as the defect's reproducer\n",
    ),
    (
        "- Published By: UNKNOWN (a local ticket file; not published)\n- Independent Review: none yet\n",
        "- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8259, edits A-C and their\n"
        "  prototype, the patch docs book_teardown_parked_2026_10_19, the regression tests, the system documents, the\n"
        "  graph prose and the release note (2026-10-19; Notes).\n"
        "- Published By: UNKNOWN (a local ticket file; not published)\n"
        "- Independent Review: none (self-checks only; closure on the owner's word on the edit, DECISION note of\n"
        "  2026-10-19T01:00:17Z)\n",
    ),
    (
        "- [ ] Work walkthrough shared with user\n"
        "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
        "- [x] Work walkthrough shared with user (the landing report, chat {DAY}, sent with this turn-in)\n"
        "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    ),
]

HANDOFF_START = "## Context / Handoff Summary\n"
HANDOFF_END = "\n## Project-Specific Additions\n"
HANDOFF_NEW = (
    "## Context / Handoff Summary\n"
    "- Scope: a Spellbook's teardown retires its parked versions and the indexes only they hold (Requirements).\n"
    "  Defect proven on 0.2.8252 and re-verified on 0.2.8259 (Notes); probe and runs in Artifact Links.\n"
    "- State: done (melder_1; turned in {TS}). Landed at {N}: edits A-C in spellbook.py\n"
    "  (PLAN and MEASURE notes); the S7 tests green with the GIL off and on and the whole tree as the MEASURE note\n"
    "  records; the system documents with their indexes and the graph, the notch and the release-note section\n"
    "  (MEASURE and FACT notes); the rebuild follows this closure.\n"
    "- Open elsewhere: the claim a notch leaves on an outgoing key outlives the Book (probe T4,\n"
    "  STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); S8 on the owner's hold.\n"
    "- Next: none here; spellbook.py and spell.py go back to melder_0 (M1-44).\n"
)

BOARD_ROW_PREFIX = "| book_teardown_parked | in_progress | implementation | claude | melder_1 |"
BOARD_DETAIL = (
    "- WORK_ITEM: book_teardown_parked\n"
    "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
    "    - tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md\n"
)
ANCHORS_BEGIN = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
ANCHORS_END = "<!-- END USER-DEFINED: closed_anchors -->\n"
NEW_ANCHOR = (
    "| book_teardown_parked | done | melder_1 | " + DONE_REF + " | Landed {N} (S7 of "
    "EPIC-2026-10-17-correctness_defects: a Spellbook's teardown retires its parked versions and cleans the indexes "
    "only they hold). Next: S8 on the owner's word; spellbook.py and spell.py back to melder_0 (M1-44). | {TS} |\n"
)
NOTCH_AFTER = (
    "  STORY-2026-10-17-minted_index_missing_from_frame_registry). Notch above it if you land after.\n"
)
NOTCH_NEW = (
    "### Notch notice (melder_1, 2026-10-19)\n"
    "- melder_1 landed {N} (a Spellbook's teardown retires its parked versions and cleans the indexes only they hold;\n"
    "  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned). Notch above it if you land after.\n"
)

ARTIFACT_ROW_SUFFIXES = (
    " | artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py | defect_reproducer |",
    " | artifacts/book_teardown_parked_20261019/ | investigation_evidence |",
    " | system_docs/patches/active/book_teardown_parked_2026_10_19/ | patch_doc |",
)
CLEARED_BEGIN = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_NEW = (
    "| " + DONE_REF + " | system_docs/patches/completed/book_teardown_parked_2026_10_19/ | promote_to_documentation | "
    "Promoted at landing ({N}) to src_architecture, src_components, tests_components and tests_architecture with "
    "their indexes, and to the graph; the two patch docs (architecture, Spellbook component) archived at turn-in. "
    "| {TS} |\n"
    "| " + DONE_REF + " | artifacts/book_teardown_parked_20261019/ | retain_as_reference | Evidence of the {N} landing: "
    "the re-run of probe T1-T5 on 0.2.8259 and on the landed tree, the prototype and its preview, the red and green "
    "test runs, the whole-tree runs, the release-note probe, the citation remap, docs, index, graph and rebuild logs, "
    "the notes and every script (open, apply, remap, docs, graph prose, release note, closure, messages). | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_book_teardown_parked.py | "
    "retain_as_reference | S7 turned in (landed at {N}): the reproducer (T1-T3, T5) and its runs stay in the sweep's "
    "folder, rowed under EPIC-2026-10-17-correctness_defects and, for T4, under the notch-signature story; its re-runs "
    "at the fix are in the lane folder. | {TS} |\n"
)


def fill(text: str, notch: str) -> str:
    """Fill the notch and the timestamps."""
    return text.replace("{N}", notch).replace("{TS}", TS).replace("{DAY}", DAY)


def read_lf(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in " + str(path))
    return raw.decode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    """Replace `old` once, refusing unless it occurs exactly once."""
    count = text.count(old)
    if count != 1:
        raise SystemExit("%s: found %d times" % (label, count))
    return text.replace(old, new, 1)


def drop_line(text: str, prefix: str, label: str) -> str:
    """Drop the one line that starts with `prefix`."""
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit("%s: %d lines" % (label, len(hits)))
    del lines[hits[0]]
    return "\n".join(lines)


def story_text(notch: str) -> str:
    """The story with its turn-in edits and a new handoff summary."""
    text = read_lf(STORY)
    for index, (old, new) in enumerate(STORY_EDITS, 1):
        text = replace_once(text, old, fill(new, notch), "story edit %d" % index)
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + TS, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("story Updated")
    start = text.find(HANDOFF_START)
    end = text.find(HANDOFF_END)
    if start < 0 or end < start or text.count(HANDOFF_START) != 1:
        raise SystemExit("handoff section")
    return text[:start] + fill(HANDOFF_NEW, notch) + text[end:]


def board_text(notch: str) -> tuple:
    """The attention board with the row and detail removed, the anchor added (oldest dropped past 12)."""
    text = read_lf(BOARD)
    text = drop_line(text, BOARD_ROW_PREFIX, "board row")
    text = replace_once(text, BOARD_DETAIL, "", "board detail")
    region = text.split(ANCHORS_BEGIN)[1].split(ANCHORS_END)[0]
    rows = [line for line in region.split("\n") if line.startswith("| ")]
    dropped = None
    if len(rows) >= 12:
        dropped = min(rows, key=lambda row: row.rstrip(" |").rsplit("| ", 1)[1].strip())
        text = replace_once(text, dropped + "\n", "", "oldest anchor")
    text = replace_once(text, ANCHORS_END, fill(NEW_ANCHOR, notch) + ANCHORS_END, "anchors end")
    return replace_once(text, NOTCH_AFTER, NOTCH_AFTER + fill(NOTCH_NEW, notch), "notch notice"), dropped


def artifacts_text(notch: str) -> str:
    """The artifact board with the three active rows moved to cleared."""
    text = read_lf(ARTIFACTS)
    for suffix in ARTIFACT_ROW_SUFFIXES:
        text = drop_line(text, "| " + ACTIVE_REF + suffix, "artifact row" + suffix)
    return replace_once(text, CLEARED_BEGIN, CLEARED_BEGIN + fill(CLEARED_NEW, notch), "cleared begin")


def main() -> None:
    """Build every text; write, move and archive only with --apply."""
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--notch" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    notch = args[1]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN")
    if DONE.exists() or PATCH_DONE.exists() or not PATCH.is_dir():
        raise SystemExit("target exists or patch folder missing")
    story = story_text(notch)
    board, dropped = board_text(notch)
    artifacts = artifacts_text(notch)
    long_lines = [line for line in story.split("\n") if len(line) > 120 and " " in line.strip()]
    anchors = board.split(ANCHORS_BEGIN)[1].split(ANCHORS_END)[0]
    print("anchors:", anchors.count("\n"), "| dropped:", (dropped or "none")[:40], "| story lines:",
          story.count("\n"), "| long story lines:", len(long_lines), "| ts:", TS)
    if args[2] == "--apply":
        STORY.write_bytes(story.encode("utf-8"))
        os.rename(STORY, DONE)
        BOARD.write_bytes(board.encode("utf-8"))
        ARTIFACTS.write_bytes(artifacts.encode("utf-8"))
        os.rename(PATCH, PATCH_DONE)
        for path, text in ((DONE, story), (BOARD, board), (ARTIFACTS, artifacts)):
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch " + str(path))
        print("applied: story moved, boards synced, patch archived")


main()
