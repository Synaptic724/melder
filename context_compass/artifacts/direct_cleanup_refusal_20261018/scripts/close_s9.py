"""S9 closure (0.2.8256): story turn-in edits, the move to completed/, attention and artifact board sync, and the
patch folder archived. Each old text must occur exactly once; LF only; mv -n semantics (refuse an existing target).
Usage (repository root): close_s9.py --check | --apply
"""
import datetime
import os
import pathlib
import sys

CC = pathlib.Path("context_compass")
NAME = "2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md"
STORY = CC / "tickets/stories" / NAME
DONE = CC / "tickets/stories/completed" / NAME
BOARD = CC / "attention_board.md"
ARTIFACTS = CC / "artifact_board.md"
PATCH = CC / "system_docs/patches/active/direct_cleanup_refusal_2026_10_18"
PATCH_DONE = CC / "system_docs/patches/completed/direct_cleanup_refusal_2026_10_18"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ACTIVE_REF = "tickets/stories/" + NAME
DONE_REF = "tickets/stories/completed/" + NAME

STORY_EDITS = [
    (
        "# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index\n"
        "\n## Metadata\n",
        "# Story: direct_cleanup_of_active_member_orphans_parked_versions - no parked version is left on a cleaned index\n"
        "\n- Completed: " + TS + "\n"
        "- Summary: landed and notched 0.2.8256 - `Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()`\n"
        "  refuse the active version of an index that holds parked versions, as `cleanup_spell` refuses it, and all three\n"
        "  messages name the remedies (notch first, dispose the parked versions, or move them out); Book teardown is\n"
        "  unaffected. S9 tests green with the GIL off and on, the whole tree green but for S8's held red tests; release\n"
        "  note section \"A cleanup of an index's active version is refused while parked versions remain\"; system\n"
        "  documents and graph; rebuilt last. Turned in on the owner's word (2026-10-18).\n"
        "\n## Metadata\n",
    ),
    ("- Status: in_progress\n", "- Status: done\n"),
    (
        "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner scheduled the story for melder_1 (chat "
        "2026-10-18; DECISION note); the\n  defect is re-verified on the current tree before any change.\n",
        "- from_state: in_progress\n- to_state: done\n"
        "- transition_reason: landed at 0.2.8256 and turned in on the owner's word (chat 2026-10-18, \"Go (Recommended)\":\n"
        "  apply the edits, test, docs, release note, notch 0.2.8256, closure and rebuild; DECISION note of\n"
        "  2026-10-18T16:02:48Z). Before that: ready -> in_progress when the owner scheduled the story for melder_1\n"
        "  (chat 2026-10-18; DECISION note).\n",
    ),
    (
        "- [ ] Task: patch docs for the removal path; the owner's approval.\n"
        "- [ ] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last.\n"
        "- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
        "- [x] Task: patch docs for the removal path; the owner's approval (the refusal, then his word on E1-E7).\n"
        "- [x] Task: the fix with symptom-named regression tests, docs, notch and the rebuild last (0.2.8256; the\n"
        "  rebuild follows this closure, as the contribution guide orders).\n"
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
        "- None open. The owner chose the refusal (DECISION note of 2026-10-18T15:41:09Z); the exact edits still go to him\n"
        "  before any src edit.\n",
        "- None open. The owner chose the refusal (DECISION note of 2026-10-18T15:41:09Z) and gave his word on the exact\n"
        "  edits (DECISION note of 2026-10-18T16:02:48Z).\n",
    ),
    (
        "- 2026-10-18T15:41:09Z: the owner chose the refusal on all three doors, the messages naming the remedies; the hole\n"
        "  rule is withdrawn unmade (DECISION note).\n",
        "- 2026-10-18T15:41:09Z: the owner chose the refusal on all three doors, the messages naming the remedies; the hole\n"
        "  rule is withdrawn unmade (DECISION note).\n"
        "- 2026-10-18T16:02:48Z: the owner's word on the exact edits E1-E7 (\"Go\"), closure included (DECISION note).\n"
        "- " + TS + ": landed at 0.2.8256 and turned in (FACT notes).\n",
    ),
    (
        "  - system_docs/patches/active/direct_cleanup_refusal_2026_10_18/ (architecture, component)\n"
        "- DISPOSITION: retain_as_reference\n",
        "  - system_docs/patches/completed/direct_cleanup_refusal_2026_10_18/ (architecture, component; promoted at\n"
        "    landing, archived at turn-in)\n"
        "- DISPOSITION: retain_as_reference (the probe, its runs and the lane folder); promote_to_documentation (the patch)\n",
    ),
    (
        "  direct_cleanup_refusal_2026_10_18, the red tests and their runs (2026-10-18; Notes).\n",
        "  direct_cleanup_refusal_2026_10_18, the red tests and their runs, the fix at 0.2.8256 (E1-E7), the system\n"
        "  documents, the graph prose and the release note (2026-10-18; Notes).\n",
    ),
    (
        "- Independent Review: none yet\n",
        "- Independent Review: none (closure on the owner's word, DECISION note of 2026-10-18T16:02:48Z; self-checks\n"
        "  only)\n",
    ),
    (
        "- [ ] Work walkthrough shared with user\n"
        "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
        "- [x] Work walkthrough shared with user (the landing report, chat 2026-10-18, sent with this turn-in)\n"
        "- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    ),
]

HANDOFF_START = "## Context / Handoff Summary\n"
HANDOFF_END = "\n## Project-Specific Additions\n"
HANDOFF_NEW = (
    "## Context / Handoff Summary\n"
    "- Scope: the Spellbook's removal path refuses the active member of an index that holds parked versions, as\n"
    "  `cleanup_spell` does, and all three messages name the remedies (Requirements). Defect proven on 0.2.8252 and\n"
    "  re-verified on 0.2.8255 (Notes); probe and runs in Artifact Links.\n"
    "- State: done (melder_1; turned in " + TS + " on the owner's word). Landed at 0.2.8256: E1-E7 in\n"
    "  spellbook.py and spell.py (FACT note); the S9 tests green with the GIL off and on, probe D1-D3 refused, the\n"
    "  whole tree green but for S8's 18 held red tests (MEASURE note); the system documents with their indexes and\n"
    "  the graph (FACT note); the notch and the release-note section (FACT note); the rebuild follows this closure.\n"
    "  The hole rule (an index kept with parked versions and nothing active) was weighed and withdrawn by the owner\n"
    "  for the refusal (DECISION notes, the lane's notes/no_active_spell_map.md).\n"
    "- Open elsewhere: index-link borrowers on the direct doors (no ward emission; the A1 note of\n"
    "  EPIC-2026-10-17-correctness_defects); Book teardown's parked versions\n"
    "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned, S7); the remedies' filed gaps S3 and S4.\n"
    "- Next: none here; spellbook.py and spell.py go back to melder_0 for S1 (M1-38); melder_1 takes S4 next.\n"
)

BOARD_ROW_PREFIX = "| direct_cleanup_refusal | in_progress | discovery | claude | melder_1 |"
BOARD_DETAIL = (
    "- WORK_ITEM: direct_cleanup_refusal\n"
    "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
    "  RESUME_HIERARCHY:\n"
    "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
    "    - tickets/stories/2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md\n"
)
OLDEST_ANCHOR_PREFIX = "| meld_contract_scan_trace | done | melder_1 |"
ANCHORS_END = "<!-- END USER-DEFINED: closed_anchors -->\n"
NEW_ANCHOR = (
    "| direct_cleanup_refusal | done | melder_1 | " + DONE_REF + " | Landed 0.2.8256 (S9 of "
    "EPIC-2026-10-17-correctness_defects: the three cleanup calls refuse an index's active version while parked "
    "versions remain, naming the remedies); turned in on the owner's word. Next: S4 with melder_1; spellbook.py and "
    "spell.py back to melder_0 (M1-38). | " + TS + " |\n"
)
NOTCH_OLD = (
    "  scope tree; nothing renamed; TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if\n"
    "  you land after.\n### Device VM git hazard"
)
NOTCH_NEW = (
    "  scope tree; nothing renamed; TASK-2026-10-16-recheck_contract_consumers_when_provider_changes). Notch above it if\n"
    "  you land after.\n"
    "- melder_1 landed 0.2.8256 (`Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse the active\n"
    "  version of an index that holds parked versions, as `cleanup_spell` does, all three naming the remedies;\n"
    "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions). Notch above it if you land after.\n"
    "### Device VM git hazard"
)

ARTIFACT_ROW_SUFFIXES = (
    " | artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py | defect_reproducer |",
    " | artifacts/direct_cleanup_refusal_20261018/ | investigation_evidence |",
    " | system_docs/patches/active/direct_cleanup_refusal_2026_10_18/ | patch_doc |",
)
CLEARED_BEGIN = "<!-- BEGIN USER-DEFINED: cleared_artifacts -->\n"
CLEARED_NEW = (
    "| " + DONE_REF + " | system_docs/patches/completed/direct_cleanup_refusal_2026_10_18/ | promote_to_documentation | "
    "Promoted at landing (0.2.8256) to src_architecture, src_components, tests_components and tests_architecture with "
    "their indexes, and to the graph; the two patch docs (architecture, component) archived at turn-in. | " + TS + " |\n"
    "| " + DONE_REF + " | artifacts/direct_cleanup_refusal_20261018/ | retain_as_reference | Evidence of the 0.2.8256 "
    "landing: the re-runs of probe D1-D3 on 0.2.8255 and at the fix, the red and green test runs, the mirror preview "
    "and whole-tree runs, the release-note probe, the no-active-spell map and every script (apply, docs, graph prose, "
    "release note, closure); two empty logs of a background run that died with its call under "
    "runs/full_tree_0_2_8256/_to_delete/. | " + TS + " |\n"
    "| " + DONE_REF + " | artifacts/correctness_defects_20261017/probes/probe_direct_cleanup_active_member.py | "
    "retain_as_reference | S9 turned in (landed at 0.2.8256): the reproducer (D1-D3) and its runs stay in the sweep's "
    "folder, rowed under EPIC-2026-10-17-correctness_defects; its re-runs at the fix are in the lane folder. | "
    + TS + " |\n"
)


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


def story_text() -> str:
    text = STORY.read_text(encoding="utf-8")
    for index, (old, new) in enumerate(STORY_EDITS, 1):
        text = replace_once(text, old, new, "story edit %d" % index)
    text = text.replace("- Updated: ", "- Updated: ", 1)
    import re
    text, count = re.subn(r"^- Updated: \S+$", "- Updated: " + TS, text, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("story Updated")
    start = text.find(HANDOFF_START)
    end = text.find(HANDOFF_END)
    if start < 0 or end < start or text.count(HANDOFF_START) != 1:
        raise SystemExit("handoff section")
    text = text[:start] + HANDOFF_NEW + text[end:]
    return text


def board_text() -> str:
    text = BOARD.read_text(encoding="utf-8")
    text = drop_line(text, BOARD_ROW_PREFIX, "board row")
    text = replace_once(text, BOARD_DETAIL, "", "board detail")
    text = drop_line(text, OLDEST_ANCHOR_PREFIX, "oldest anchor")
    text = replace_once(text, ANCHORS_END, NEW_ANCHOR + ANCHORS_END, "anchors end")
    text = replace_once(text, NOTCH_OLD, NOTCH_NEW, "notch notice")
    return text


def artifacts_text() -> str:
    text = ARTIFACTS.read_text(encoding="utf-8")
    for suffix in ARTIFACT_ROW_SUFFIXES:
        text = drop_line(text, "| " + ACTIVE_REF + suffix, "artifact row" + suffix)
    text = replace_once(text, CLEARED_BEGIN, CLEARED_BEGIN + CLEARED_NEW, "cleared begin")
    return text


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    for path in (STORY, BOARD, ARTIFACTS):
        if b"\r\n" in path.read_bytes():
            raise SystemExit("CRLF in " + str(path))
    if DONE.exists() or PATCH_DONE.exists() or not PATCH.is_dir():
        raise SystemExit("target exists or patch folder missing")
    story, board, artifacts = story_text(), board_text(), artifacts_text()
    anchors = board.split("<!-- BEGIN USER-DEFINED: closed_anchors -->\n")[1].split(ANCHORS_END)[0]
    print("anchors:", anchors.count("\n"), "| story lines:", story.count("\n"), "| ts:", TS)
    if mode == "--apply":
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
