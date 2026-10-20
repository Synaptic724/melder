"""S8 closure: story turn-in edits, the move to completed/, attention and artifact board sync, the notch notice and
the patch folder archived (STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers; melder_1, adapted from
close_s7.py). Each old text must occur exactly once; LF only; refuse an existing target. When the closed-anchor
region would pass 12 rows, the row with the oldest closed_at goes.
Usage (repository root): close_s8.py --notch 0.2.82NN --check | --apply
"""
import datetime
import os
import pathlib
import re
import sys

CC = pathlib.Path("context_compass")
NAME = "2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
STORY = CC / "tickets/stories" / NAME
DONE = CC / "tickets/stories/completed" / NAME
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
PATCH = CC / "system_docs/patches/active/failed_notch_refusal_2026_10_18"
PATCH_DONE = CC / "system_docs/patches/completed/failed_notch_refusal_2026_10_18"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DAY = TS[:10]
ACTIVE_REF = "tickets/stories/" + NAME
DONE_REF = "tickets/stories/completed/" + NAME
TITLE = ("# Story: failed_notch_keeps_switch_without_borrowers - a notch that fails its commit leaves no half-made "
         "switch\n")

STORY_EDITS = [
    (
        TITLE + "\n## Metadata\n",
        TITLE + "\n- Completed: {TS}\n"
        "- Summary: landed and notched {N} - a notch whose incoming version fails its structural check is refused with\n"
        "  nothing moved: `Spellbook._notch_spell` checks the version inside the notch window and, when the check\n"
        "  fails, puts the structure back before it raises, so the lender and its borrowers stay on the outgoing\n"
        "  version, which is left gated for revalidation; `SpellbookValidationError` takes a one-line `preface`. 25\n"
        "  tests green with the GIL off and on, the whole tree as the MEASURE note records; release-note section \"A\n"
        "  notch whose new version fails its check is refused, and nothing moves\"; system documents and graph; the\n"
        "  rebuild comes last in this pass. Turned in on the owner's word (chat 2026-10-19: \"turn in tickets that you\n"
        "  can\").\n"
        "\n## Metadata\n",
    ),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        "- from_state: blocked\n- to_state: in_progress\n"
        "- transition_reason: the owner asked for proof that the half-switch happens (chat 2026-10-19; DECISION note of\n",
        "- from_state: in_progress\n- to_state: done\n"
        "- transition_reason: landed at {N} and turned in on the owner's word (chat 2026-10-19: \"Yes do s8\", then \"turn\n"
        "  in tickets that you can\"; DECISION notes). Before that, blocked -> in_progress: the owner asked for proof that\n"
        "  the half-switch happens (chat 2026-10-19; DECISION note of\n",
    ),
    (
        "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n"
        "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
        "- [x] Task: the fix with symptom-named regression tests (red on 0.2.8260, green at {N}; MEASURE notes), docs,\n"
        "  notch and the rebuild last (the rebuild follows the closures of this pass, as the contribution guide orders).\n"
        "- [x] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
    ),
    (
        "  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Not\n"
        "  run: no fix exists yet.\n",
        "  `test_a_notch_refused_at_commit_leaves_borrowers_on_the_lenders_version`; GIL off and on; the probe re-run. Run\n"
        "  at the fix: 25 tests green with the GIL off and on and the probes re-run (MEASURE notes of 2026-10-19).\n",
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
        "- 2026-10-17T22:12:58Z: the owner answered the open question - (a): refuse with nothing moved (DECISION note).\n",
        "- 2026-10-17T22:12:58Z: the owner answered the open question - (a): refuse with nothing moved (DECISION note).\n"
        "- 2026-10-18: the patch docs approved by the owner, then his hold on the edit list (DECISION notes).\n"
        "- 2026-10-19T11:07:22Z: the owner's go - \"it should roll back properly\" (DECISION note).\n"
        "- 2026-10-19T12:46:57Z: the owner's \"Yes do s8\" - land S8 on S3's tree, then turn it in (DECISION note).\n"
        "- {TS}: landed at {N} and turned in (MEASURE and FACT notes).\n",
    ),
    (
        "  - system_docs/patches/active/failed_notch_refusal_2026_10_18/ (architecture, 2 component, code-description)\n",
        "  - system_docs/patches/completed/failed_notch_refusal_2026_10_18/ (architecture, 2 component, code-description;\n"
        "    promoted at landing, archived at turn-in)\n",
    ),
    (
        "- DISPOSITION: retain_as_reference\n- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's "
        "reproducer\n",
        "- DISPOSITION: retain_as_reference (the probes, their runs and the lane folder); promote_to_documentation (the\n"
        "  patch)\n"
        "- CLEANUP_TRIGGER: the probe was re-run at the fix and is kept as the defect's reproducer\n",
    ),
    (
        "- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8255, the patch docs\n"
        "  failed_notch_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes).\n"
        "- Published By: UNKNOWN (a local ticket file; not published)\n- Independent Review: none yet\n",
        "- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8255, the patch docs\n"
        "  failed_notch_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes); the rollback in\n"
        "  spellbook.py, the error's preface, the docstrings, the system documents, the graph prose and the release note\n"
        "  (2026-10-19; Notes).\n"
        "- Published By: UNKNOWN (a local ticket file; not published)\n"
        "- Independent Review: none (self-checks only; closure on the owner's word, chat 2026-10-19)\n",
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
    "- Scope: a notch whose incoming version fails its commit check is refused with nothing moved - the lender and its\n"
    "  borrowers stay on the outgoing version (Requirements; the owner's answer (a)). Defect proven on 0.2.8252\n"
    "  (Notes); probe and runs in Artifact Links.\n"
    "- State: done (melder_1; turned in {TS}). Landed at {N} on S3's tree: the check inside the notch\n"
    "  window and the reversal in spellbook.py, the error's `preface`, docstrings in conduit.py and the change-control\n"
    "  validator; 25 tests green with the GIL off and on and the whole tree as the MEASURE note records; the system\n"
    "  documents with their indexes, the graph, the notch and the release-note section (FACT note); the rebuild comes\n"
    "  last in this pass, after S3's turn-in and any small fixes.\n"
    "- Open elsewhere: S11 (STORY-2026-10-19-notch_back_keeps_outgoing_dependencies), the owner's call; the seam's own\n"
    "  refusal inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking); melds in flight during\n"
    "  a notch's fan-out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout).\n"
    "- Next: none here.\n"
)

BOARD_ROW_PREFIX = "| failed_notch_refusal | in_progress | implementation | claude | melder_1 |"
BOARD_DETAIL = (
    "- WORK_ITEM: failed_notch_refusal\n"
    "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
    "    - tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md\n"
)
ANCHORS_BEGIN = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
ANCHORS_END = "<!-- END USER-DEFINED: closed_anchors -->\n"
NEW_ANCHOR = (
    "| failed_notch_refusal | done | melder_1 | " + DONE_REF + " | Landed {N} (S8 of "
    "EPIC-2026-10-17-correctness_defects: a notch whose incoming version fails its structural check is refused with "
    "nothing moved, its borrowers untouched). Next: S3's turn-in, then small fixes; the rebuild last. | {TS} |\n"
)
NOTCH_AFTER = "  melder_1's S8 landing rebuilds for both. Notch above it if you land after.\n"
NOTCH_NEW = (
    "### Notch notice (melder_1, 2026-10-19, S8)\n"
    "- melder_1 landed {N} (a notch whose incoming version fails its structural check is refused with nothing moved\n"
    "  and its borrowers untouched; `SpellbookValidationError` takes a one-line `preface`;\n"
    "  STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers). Notch above it if you land after.\n"
)

ARTIFACT_ROW_SUFFIXES = (
    " | artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py | defect_reproducer |",
    " | artifacts/correctness_defects_20261017/probes/probe_broken_late_bind.py | investigation_evidence |",
    " | artifacts/failed_notch_refusal_20261018/ | investigation_evidence |",
    " | system_docs/patches/active/failed_notch_refusal_2026_10_18/ | patch_doc |",
)
CLEARED_BEGIN = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_NEW = (
    "| " + DONE_REF + " | system_docs/patches/completed/failed_notch_refusal_2026_10_18/ | promote_to_documentation | "
    "Promoted at landing ({N}) to src_architecture, src_components, tests_components and tests_architecture with their "
    "indexes, and to the graph; the four patch docs (architecture, two component, one code-description) archived at "
    "turn-in. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/failed_notch_refusal_20261018/ | retain_as_reference | Evidence of the {N} landing: "
    "the re-runs of probe N1-N3, the proofs (plain, two reasons, the marks), the red and green test runs, the whole "
    "tree on the mirror and on S3's tree, the release-note probe, the citation remap, docs, index and graph logs, the "
    "notes and every script (open, apply, remap, docs, graph prose, release note, closure, messages); S11's reproducer "
    "in it stays rowed under that story. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_failed_notch_commit.py | "
    "retain_as_reference | S8 turned in (landed at {N}): the reproducer (N1-N3) and its runs stay in the sweep's "
    "folder, rowed under EPIC-2026-10-17-correctness_defects; its re-runs at the fix are in the lane folder. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_broken_late_bind.py | "
    "retain_as_reference | S8 turned in: cases B1-B3 (a late bind whose commit fails keeps its spell, the precedent "
    "the owner's answer departed from) and their runs stay in the sweep's folder. | {TS} |\n"
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
    """The artifact board with the four active rows moved to cleared."""
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
