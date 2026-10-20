"""S4 closure: story turn-in edits, the move to completed/, attention and artifact board sync, the notch notice and
the patch folder archived (STORY-2026-10-17-minted_index_missing_from_frame_registry). Each old text must occur
exactly once; LF only; mv -n semantics (refuse an existing target). The oldest closed anchor is dropped when the
region would pass 12 rows.
Usage (repository root): close_s4.py --notch 0.2.82NN --check | --apply
"""
import datetime
import os
import pathlib
import re
import sys

CC = pathlib.Path("context_compass")
NAME = "2026-10-17_minted_index_missing_from_frame_registry_story.md"
STORY = CC / "tickets/stories" / NAME
DONE = CC / "tickets/stories/completed" / NAME
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
PATCH = CC / "system_docs/patches/active/minted_index_registry_2026_10_18"
PATCH_DONE = CC / "system_docs/patches/completed/minted_index_registry_2026_10_18"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DAY = TS[:10]
ACTIVE_REF = "tickets/stories/" + NAME
DONE_REF = "tickets/stories/completed/" + NAME
TITLE = ("# Story: minted_index_missing_from_frame_registry - the index remove_from_spell_index mints is known to the "
         "frame\n")

STORY_EDITS = [
    (
        TITLE + "\n## Metadata\n",
        TITLE + "\n- Completed: {TS}\n"
        "- Summary: landed and notched {N} - the index `remove_from_spell_index` mints is registered in the frame's\n"
        "  spell registry as `bind` registers the index it creates, the root's teardown unregisters it with the rest,\n"
        "  and residency reads its version parked until a notch. S4 tests green with the GIL off and on, the whole tree\n"
        "  as the MEASURE note records; release note section \"A version moved into an index of its own is found by its\n"
        "  spell_id\"; system documents and graph; rebuilt last. Turned in after the landing, on the owner's word on the\n"
        "  edits (2026-10-18).\n"
        "\n## Metadata\n",
    ),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        "- from_state: ready\n- to_state: in_progress\n"
        "- transition_reason: the owner scheduled the story for melder_1 (chat 2026-10-18; DECISION note); the defect\n"
        "  is re-verified on the current tree before any change.\n",
        "- from_state: in_progress\n- to_state: done\n"
        "- transition_reason: landed at {N} and turned in after the landing (the owner's word on the edits, DECISION\n"
        "  note of 2026-10-18T18:00:11Z; closure is routine once criteria and tests are met). Before that: ready ->\n"
        "  in_progress when the owner scheduled the story for melder_1 (chat 2026-10-18; DECISION note).\n",
    ),
    (
        "- [ ] Task: the fix with symptom-named regression tests (written: red on 0.2.8256, green with A-D; MEASURE\n"
        "  note), docs, notch and the rebuild last.\n"
        "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
        "- [x] Task: the fix with symptom-named regression tests (red on 0.2.8256, green at {N}; MEASURE notes),\n"
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
        "  with B and C; no new index state (DECISION and ALIGNMENT_CHECK notes).\n\n## Artifact Links (Optional)\n",
        "  with B and C; no new index state (DECISION and ALIGNMENT_CHECK notes).\n"
        "- {TS}: landed at {N} and turned in (FACT notes).\n\n## Artifact Links (Optional)\n",
    ),
    (
        "  - system_docs/patches/active/minted_index_registry_2026_10_18/ (the three patch docs)\n",
        "  - system_docs/patches/completed/minted_index_registry_2026_10_18/ (the three patch docs; promoted at landing,\n"
        "    archived at turn-in)\n",
    ),
    (
        "- DISPOSITION: retain_as_reference\n- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's "
        "reproducer\n",
        "- DISPOSITION: retain_as_reference (the probes, their runs and the lane folder); promote_to_documentation (the\n"
        "  patch)\n"
        "- CLEANUP_TRIGGER: the probes were re-run at the fix and are kept as the defect's reproducers\n",
    ),
    (
        "- Published By: UNKNOWN (a local ticket file; not published)\n- Independent Review: none yet\n",
        "- Contributions: melder_1 (synaptic_python_developer) - the re-verification on 0.2.8256, probes M4-M7 and\n"
        "  G1-G3, edits A-D and their prototypes, the patch docs minted_index_registry_2026_10_18, the regression tests,\n"
        "  the system documents, the graph prose and the release note (2026-10-18; Notes).\n"
        "- Published By: UNKNOWN (a local ticket file; not published)\n"
        "- Independent Review: none (self-checks only; closure on the owner's word on the edits, DECISION note of\n"
        "  2026-10-18T18:00:11Z)\n",
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
    "- Scope: the index `remove_from_spell_index` mints is registered in the frame's spell registry as `bind` registers\n"
    "  the index it creates, unregistered at the root's teardown with the rest, and residency reads its version parked\n"
    "  until a notch (Requirements; widened on the owner's word). Defect proven on 0.2.8251 and re-verified on\n"
    "  0.2.8256 (Notes); probes and runs in Artifact Links.\n"
    "- State: done (melder_1; turned in {TS}). Landed at {N}: edits A-D in spellbook.py, spell.py and\n"
    "  mutation_research.py (FACT note); the S4 tests green with the GIL off and on and the whole tree as the MEASURE\n"
    "  note records; the system documents with their indexes and the graph, the notch and the release-note section\n"
    "  (FACT notes); the rebuild follows this closure.\n"
    "- Open elsewhere: the binding signature an active version in a minted index takes\n"
    "  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); Book teardown's parked versions\n"
    "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, S7, next with melder_1); a restore or graft\n"
    "  of a separated version (STORY-2026-10-17-restore_drops_separated_parked_version).\n"
    "- Next: none here; spellbook.py and spell.py go back to melder_0 and mutation_research.py is released (M1-42);\n"
    "  melder_1 takes S7 next.\n"
)

BOARD_ROW_PREFIX = "| minted_index_registry | in_progress | implementation | claude | melder_1 |"
BOARD_DETAIL = (
    "- WORK_ITEM: minted_index_registry\n"
    "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
    "    - tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md\n"
)
ANCHORS_BEGIN = "<!-- BEGIN USER-DEFINED: closed_anchors -->\n"
ANCHORS_END = "<!-- END USER-DEFINED: closed_anchors -->\n"
NEW_ANCHOR = (
    "| minted_index_registry | done | melder_1 | " + DONE_REF + " | Landed {N} (S4 of "
    "EPIC-2026-10-17-correctness_defects: the index remove_from_spell_index mints is registered with the frame as bind "
    "registers its new one, unregistered at the root's teardown; residency reads its version parked). Next: S7 with "
    "melder_1; spellbook.py and spell.py back to melder_0 (M1-42). | {TS} |\n"
)
NOTCH_AFTER = (
    "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions). Notch above it if you land after.\n"
)
NOTCH_NEW = (
    "- melder_1 landed {N} (the index `remove_from_spell_index` mints is registered with the frame as `bind` registers\n"
    "  the index it creates and leaves with its root; residency reads its version parked until a notch;\n"
    "  STORY-2026-10-17-minted_index_missing_from_frame_registry). Notch above it if you land after.\n"
)

ARTIFACT_ROW_SUFFIXES = (
    " | artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py | defect_reproducer |",
    " | artifacts/correctness_defects_20261017/probes/probe_research_residency_moves.py | defect_reproducer |",
    " | artifacts/minted_index_registry_20261018/ | investigation_evidence |",
    " | system_docs/patches/active/minted_index_registry_2026_10_18/ | patch_doc |",
)
CLEARED_BEGIN = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_NEW = (
    "| " + DONE_REF + " | system_docs/patches/completed/minted_index_registry_2026_10_18/ | promote_to_documentation | "
    "Promoted at landing ({N}) to src_architecture, src_components, tests_components and tests_architecture with "
    "their indexes, and to the graph; the three patch docs (architecture, two component) archived at turn-in. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/minted_index_registry_20261018/ | retain_as_reference | Evidence of the {N} landing: "
    "the re-runs of probes M1-M3 and V1-V4 on 0.2.8256 and at the fix, the new probes M4-M7 and G1-G3, the "
    "prototypes of A-C, the previews, the red and green test runs, the whole-tree runs, the release-note probe and "
    "block run, the rebuild logs, the notes and every script (apply, docs, graph prose, release note, citation remap, "
    "closure, messages). | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_minted_index_registry.py | "
    "retain_as_reference | S4 turned in (landed at {N}): the reproducer (M1-M3) and its runs stay in the sweep's "
    "folder, rowed under EPIC-2026-10-17-correctness_defects; its re-runs at the fix are in the lane folder. | {TS} |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_research_residency_moves.py | "
    "retain_as_reference | S4 turned in (landed at {N}): the residency reproducer (V1-V4) and its runs stay in the "
    "sweep's folder, rowed under EPIC-2026-10-17-correctness_defects; its re-runs at the fix are in the lane folder. "
    "| {TS} |\n"
)


def fill(text: str, notch: str) -> str:
    return text.replace("{N}", notch).replace("{TS}", TS).replace("{DAY}", DAY)


def read_lf(path: pathlib.Path) -> str:
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in " + str(path))
    return raw.decode("utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit("%s: found %d times" % (label, count))
    return text.replace(old, new, 1)


def drop_line(text: str, prefix: str, label: str) -> str:
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit("%s: %d lines" % (label, len(hits)))
    del lines[hits[0]]
    return "\n".join(lines)


def story_text(notch: str) -> str:
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


def board_text(notch: str) -> str:
    text = read_lf(BOARD)
    text = drop_line(text, BOARD_ROW_PREFIX, "board row")
    text = replace_once(text, BOARD_DETAIL, "", "board detail")
    region = text.split(ANCHORS_BEGIN)[1].split(ANCHORS_END)[0]
    rows = [line for line in region.split("\n") if line.startswith("| ")]
    if len(rows) >= 12:
        text = replace_once(text, ANCHORS_BEGIN + rows[0] + "\n", ANCHORS_BEGIN, "oldest anchor")
    text = replace_once(text, ANCHORS_END, fill(NEW_ANCHOR, notch) + ANCHORS_END, "anchors end")
    return replace_once(text, NOTCH_AFTER, NOTCH_AFTER + fill(NOTCH_NEW, notch), "notch notice")


def artifacts_text(notch: str) -> str:
    text = read_lf(ARTIFACTS)
    for suffix in ARTIFACT_ROW_SUFFIXES:
        text = drop_line(text, "| " + ACTIVE_REF + suffix, "artifact row" + suffix)
    return replace_once(text, CLEARED_BEGIN, CLEARED_BEGIN + fill(CLEARED_NEW, notch), "cleared begin")


def main() -> None:
    args = sys.argv[1:]
    if len(args) != 3 or args[0] != "--notch" or args[2] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    notch = args[1]
    if not re.fullmatch(r"0\.2\.82\d\d", notch):
        raise SystemExit("--notch must read 0.2.82NN")
    if DONE.exists() or PATCH_DONE.exists() or not PATCH.is_dir():
        raise SystemExit("target exists or patch folder missing")
    story, board, artifacts = story_text(notch), board_text(notch), artifacts_text(notch)
    long_lines = [line for line in story.split("\n") if len(line) > 120 and " " in line.strip()]
    anchors = board.split(ANCHORS_BEGIN)[1].split(ANCHORS_END)[0]
    print("anchors:", anchors.count("\n"), "| story lines:", story.count("\n"), "| long story lines:",
          len(long_lines), "| ts:", TS)
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
