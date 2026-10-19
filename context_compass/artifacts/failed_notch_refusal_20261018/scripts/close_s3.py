"""S3 turn-in (melder_1, on the owner's word, chat 2026-10-19: "turn in tickets that you can"): story turn-in edits,
the move to completed/, attention and artifact board sync and the patch folder archived
(STORY-2026-10-17-parked_cleanup_leaves_borrower_copies, landed at 0.2.8261 by melder_0; adapted from close_s8.py, no
notch notice - melder_0 posted 0.2.8261's). Each old text must occur exactly once; LF only; refuse an existing
target. When the closed-anchor region would pass 12 rows, the row with the oldest closed_at goes. Two lines this
script first wrote past 120 characters (the Decision Log entry and the handoff State line) were reflowed in the
story right after the apply; the strings below are the reflowed text.
Usage (repository root): close_s3.py --notch 0.2.8261 --check | --apply
"""
import datetime
import os
import pathlib
import re
import sys

CC = pathlib.Path("context_compass")
NAME = "2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
STORY = CC / "tickets/stories" / NAME
DONE = CC / "tickets/stories/completed" / NAME
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
PATCH = CC / "system_docs/patches/active/cleanup_releases_contracts_2026_10_19"
PATCH_DONE = CC / "system_docs/patches/completed/cleanup_releases_contracts_2026_10_19"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DAY = TS[:10]
ACTIVE_REF = "tickets/stories/" + NAME
DONE_REF = "tickets/stories/completed/" + NAME
TITLE = ("# Story: parked_cleanup_leaves_borrower_copies - disposing a parked version removes its copy from index-link "
         "borrowers\n")

STORY_EDITS = [
    (
        TITLE + "\n## Metadata\n",
        TITLE + "\n- Completed: {TS}\n"
        "- Summary: landed and notched {N} by melder_0 - every `cleanup_spell` door takes a version out of every\n"
        "  contract of its Book's root conduit (index-link members and version grants, with the borrower's entry and\n"
        "  borrowed id) before it disposes it, and the Spellbook's own door goes through the root conduit once\n"
        "  conjured. 13 tests red on 0.2.8260 and green with the GIL off and on, and the whole tree with S8 applied on\n"
        "  this tree; release-note section \"Cleaning up a spell takes it out of every contract first\"; system\n"
        "  documents and graph; the rebuild comes last in this pass, with S8's 0.2.8262. Turned in by melder_1 on the\n"
        "  owner's word (chat 2026-10-19: \"turn in tickets that you can\").\n"
        "\n## Metadata\n",
    ),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        "- from_state: ready\n- to_state: in_progress\n"
        "- transition_reason: the owner's go (chat 2026-10-19); melder_0 takes the fix (DECISION note).\n",
        "- from_state: in_progress\n- to_state: done\n"
        "- transition_reason: landed at {N} by melder_0, handed to melder_1 (DECISION note of 2026-10-19T12:35:35Z) and\n"
        "  turned in on the owner's word (chat 2026-10-19: \"turn in tickets that you can\"; the epic's DECISION note).\n"
        "  Before that, ready -> in_progress: the owner's go (chat 2026-10-19); melder_0 took the fix (DECISION note).\n",
    ),
    (
        "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
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
        "- 2026-10-19T12:35:35Z: handed to melder_1 with every ticket melder_0 held, on the owner's word (DECISION note).\n",
        "- 2026-10-19T12:35:35Z: handed to melder_1 with every ticket melder_0 held, on the owner's word (DECISION note).\n"
        "- {TS}: turned in by melder_1 on the owner's word, after S8 landed on this tree (0.2.8262); the\n"
        "  rebuild for both comes last in this pass (FACT notes).\n",
    ),
    (
        "  - system_docs/patches/active/cleanup_releases_contracts_2026_10_19/ (the patch, five docs)\n",
        "  - system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/ (the patch, five docs; promoted at\n"
        "    landing, archived at turn-in)\n",
    ),
    (
        "- DISPOSITION: retain_as_reference\n- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's "
        "reproducer\n",
        "- DISPOSITION: retain_as_reference (the probes, their runs, the fix's runs and scripts); promote_to_documentation\n"
        "  (the patch)\n"
        "- CLEANUP_TRIGGER: the probes were re-run at the fix and are kept as the defect's reproducers\n",
    ),
    (
        "- Published By: UNKNOWN (a local ticket file; not published)\n- Independent Review: none yet\n",
        "- Contributions: melder_0 (synaptic_python_developer) - the probes, the patch docs\n"
        "  cleanup_releases_contracts_2026_10_19, the src edits and 13 tests, the system documents, the graph prose, the\n"
        "  release note and the notch 0.2.8261 (2026-10-19; Notes); melder_1 (synaptic_python_developer) - the whole tree\n"
        "  with S8 applied on this tree and the turn-in (2026-10-19; Notes).\n"
        "- Published By: UNKNOWN (a local ticket file; not published)\n"
        "- Independent Review: none (self-checks only; closure on the owner's word, chat 2026-10-19)\n",
    ),
    (
        "- [ ] Work walkthrough shared with user\n"
        "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
        "- [x] Work walkthrough shared with user (the turn-in report, chat {DAY}, with S8's)\n"
        "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    ),
]

HANDOFF_START = "## Context / Handoff Summary\n"
HANDOFF_END = "\n## Project-Specific Additions\n"
HANDOFF_NEW = (
    "## Context / Handoff Summary\n"
    "- Scope: a borrower keeps no record of a lender's version that is gone or unlinked (Requirements; the owner's\n"
    "  rule, 2026-10-19). Probes and runs in Artifact Links.\n"
    "- State: done (melder_1; turned in {TS}). Landed at {N} by melder_0: every `cleanup_spell`\n"
    "  door takes the version out of every contract of its Book's root conduit before it disposes it (FACT and\n"
    "  MEASURE notes); handed to melder_1 (DECISION note of 2026-10-19T12:35:35Z), which ran the whole tree with S8\n"
    "  applied on this tree and turned the story in on the owner's word; the rebuild for both comes last in this pass.\n"
    "- Open for the owner, not this story's: K6 (the direct doors release no contract), K2 (a parked grant's borrowed\n"
    "  ids), the timing-dependent `test_concurrent_adds_of_same_conduit_admit_exactly_one`, and the SEMANTICS_STALE\n"
    "  graph nodes Conduit and ConduitWard (FACT note of the M0-212 consumption).\n"
    "- Next: none here.\n"
)

BOARD_ROW_PREFIX = "| parked_cleanup_contracts | in_progress | handoff | claude | melder_1 |"
BOARD_DETAIL = (
    "- WORK_ITEM: parked_cleanup_contracts\n"
    "  SWITCH_TRIGGER: The fix lands with tests, docs and the notch (melder_1's S8 landing rebuilds), or the owner\n"
    "    redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
    "    - tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md\n"
)
ANCHORS_BEGIN = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
ANCHORS_END = "<!-- END USER-DEFINED: closed_anchors -->\n"
NEW_ANCHOR = (
    "| parked_cleanup_contracts | done | melder_0, melder_1 | " + DONE_REF + " | Landed {N} by melder_0 (S3 of "
    "EPIC-2026-10-17-correctness_defects: every cleanup_spell door takes a version out of every contract first); "
    "turned in by melder_1 on the owner's word. Next: small fixes; the rebuild last. | {TS} |\n"
)

SWEEP = " | artifacts/correctness_defects_20261017/"
ARTIFACT_ROW_SUFFIXES = (
    SWEEP + "probes/probe_parked_cleanup_borrowers.py | defect_reproducer |",
    SWEEP + "probes/probe_index_unlink_leftovers.py | defect_reproducer |",
    SWEEP + "probes/probe_cleanup_contract_doors.py | defect_reproducer |",
    " | system_docs/patches/active/cleanup_releases_contracts_2026_10_19/ | patch_doc |",
    SWEEP + "runs/s3_fix/ | validation_evidence |",
    SWEEP + "scripts/s3_fix/ | scripts |",
    SWEEP + "probes/probe_release_note_s3.py | release_note_probe |",
)
CLEARED_BEGIN = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_NEW = (
    "| " + DONE_REF + " | system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/ | "
    "promote_to_documentation | Promoted at landing ({N}, melder_0) to src_architecture, src_components, "
    "tests_components and tests_architecture with their indexes, and to the graph; the five patch docs (architecture, "
    "three component, one code-description) archived at turn-in. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/runs/s3_fix/ | retain_as_reference | Evidence of the "
    "{N} landing: the red and green runs, the probes at the fix, the whole tree with the GIL off and on, the flake "
    "and mount reruns, the docs, index, graph and release-note logs. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/scripts/s3_fix/ | retain_as_reference | apply_src.py "
    "and the record passes of the {N} landing. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_release_note_s3.py | retain_as_reference "
    "| The {N} release note's example, run as written: OK on the fix with the GIL off and on, AttributeError on "
    "0.2.8260. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_cleanup_contract_doors.py | "
    "retain_as_reference | S3 turned in (landed at {N}): cases K1-K7 and their runs stay in the sweep's folder, "
    "rowed under EPIC-2026-10-17-correctness_defects; K2 and K6, open for the owner, are recorded in the story. | "
    "{TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers.py | "
    "retain_as_reference | S3 turned in: cases U1-U3, U3's traceback and their runs stay in the sweep's folder as "
    "the defect's reproducer. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py | "
    "retain_as_reference | S3 turned in: cases P1 and P2 and their runs stay in the sweep's folder as the defect's "
    "first reproducer. | {TS} |\n"
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
    return replace_once(text, ANCHORS_END, fill(NEW_ANCHOR, notch) + ANCHORS_END, "anchors end"), dropped


def artifacts_text(notch: str) -> str:
    """The artifact board with the seven active rows moved to cleared."""
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
