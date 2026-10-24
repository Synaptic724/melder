"""Close TASK-2026-10-24-cache_file_write_failure_fails_meld (melder_0, 2026-10-24).

One all-or-nothing pass: the completion summary, status, transition, checklists, attribution, the closure note
(Note 32) and the handoff summary; three backlog drafts (backlog_followups_20261024.py); the board row and its
detail removed and a closed anchor added (cap 12); the artifact folder kept as the reproducer and the patch docs
cleared as promoted; then the ticket moves to tickets/tasks/completed/ and the patch folder to
system_docs/patches/completed/. Anchors match once, lines fit 120 characters (paths and table rows exempt), no CR,
no target path exists already, and a file that changed since it was read refuses the pass. The rebuild runs after.
Usage: close_task_20261024.py --check | --apply
"""
import os
import pathlib
import re
import sys
from typing import List, Tuple

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
sys.path.insert(0, str(HERE))
from cc_record import Record
import backlog_followups_20261024 as followups

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
DONE = "tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md"
PATCH = "system_docs/patches/active/cache_save_best_effort_2026_10_24"
PATCH_DONE = "system_docs/patches/completed/cache_save_best_effort_2026_10_24"
BACKLOG = {
    "tests": "tickets/tasks/backlog/2026-10-24_document_refused_cache_save_tests_task.md",
    "frequency": "tickets/tasks/backlog/2026-10-24_cache_save_frequency_and_location_task.md",
    "windows": "tickets/tasks/backlog/2026-10-24_identify_windows_cache_file_holder_task.md",
}
RUNS = "artifacts/cache_write_failure_20261024/runs/"
M1_STORY = "tickets/stories/2026-10-24_remove_many_child_holder_ownership_story.md"
CI_TASK = "tickets/tasks/2026-10-24_ci_lane_loose_ends_task.md"


class Pass(Record):
    """The closure pass."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel in (DONE, PATCH_DONE, *BACKLOG.values()):
            if (self.ROOT / rel).exists():
                sys.exit(f"EXISTS {rel}; nothing written")
        if not (self.ROOT / PATCH).is_dir():
            sys.exit(f"MISSING {PATCH}")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()
        os.rename(self.ROOT / TICKET, self.ROOT / DONE)
        os.rename(self.ROOT / PATCH, self.ROOT / PATCH_DONE)
        print("moved", TICKET, "->", DONE)
        print("moved", PATCH, "->", PATCH_DONE)


def note_spans(text: str) -> List[Tuple[int, int]]:
    lines = text.split("\n")
    start = lines.index("## Notes")
    end = lines.index("## Context / Handoff Summary")
    spans = []
    for i in range(start, end):
        if lines[i].startswith("- DATETIME: "):
            j = i + 1
            while j < end and lines[j] != "":
                j += 1
            spans.append((i + 1, j))
    return spans


def cite(spans: List[Tuple[int, int]], number: int) -> str:
    a, b = spans[number - 1]
    return f"context_compass/{DONE}:{a}-{b}"


def section(text: str, heading: str) -> Tuple[int, int]:
    """Character span of a `## ` section body (after its heading line, up to the next `## ` heading)."""
    start = text.index(heading + "\n") + len(heading) + 1
    nxt = text.index("\n## ", start) + 1
    return start, nxt


def edit_ticket(r: Pass) -> None:
    text = r.read(TICKET)
    if len(note_spans(text)) != 31:
        sys.exit(f"NOTES: {len(note_spans(text))}, expected 31")
    title = "# Task: A failed creation-cache file write fails the meld that triggered it (WinError 5 on Windows)"
    text = r.once(text, title + "\n\n## Metadata\n", f"""\
{title}

- Completed: {r.now}
- Summary: A creation-cache save the operating system refuses no longer fails a meld: `CachingSystem.emit()` returns
  a bool, saves through a per-writer temp file, retries a refused rename on Windows and logs once per bundle; the
  Book leaves its save flag cleared; `Spell.emit_cache_file()` returns False (Breaking). Notched 0.2.8266; release-note
  section "A cache file that cannot be saved no longer fails a meld". Tests green, the GIL off and on; the owner's
  Windows rerun Not run. Three follow-ups parked in tickets/tasks/backlog/. Rebuild last, after the closure.

## Metadata
""", "summary")
    text = r.once(text, "- Status: in_progress\n", "- Status: done\n", "status")
    a, b = section(text, "## State Transition Event")
    text = text[:a] + """\
- from_state: in_progress (implementation)
- to_state: done
- transition_reason: the EXIT_GATE is met but for its last item, the rebuild, which the turn-in order runs after
  this closure (Note 32): 0.2.8266 landed with the regression and new tests green and the full trees run, the GIL
  off and on (Note 26); the patch docs consumed (Notes 23, 27) and promoted, with the system docs, graph, release
  note and notch (Notes 29, 30); the NOTICEs sent (Note 31). Routine closure under the owner's go (Note 21).

""" + text[b:]
    text = r.once(text, "- [ ] F5: src_architecture and src_components", "- [x] F5: src_architecture and src_components",
                  "step F5")
    text = r.once(text, "- [ ] Closure: summary, move to completed/", "- [x] Closure: summary, move to completed/",
                  "step closure")
    text = r.once(text, """\
  Failures: the CI manifest test that waits for melder_2's pip pin, and 29 in melder_1's untracked
  red-by-design files, the same set without this change.
""", """\
  Failures: the CI manifest test that waits for melder_2's pip pin, and 29 in melder_1's untracked
  red-by-design files, the same set without this change.
- Run at closure (Note 32): the CI manifest test file (test_python_runtime_matrix.py) passes on a /tmp copy of the
  working tree at 0.2.8266 (melder_2's set in), 63 of 63, the GIL off and on. The 29 in melder_1's files are green
  with its change (its MEASURE, 2026-10-24T20:57:42Z: its six files 156 passed, the full suite 0 failed).
""", "validation")
    a, b = section(text, "## Applicable Anti-Patterns")
    text = text[:a] + text[a:b].replace("- [ ] ", "- [x] ") + text[b:]
    a, b = section(text, "## Done Checklist")
    body = text[a:b].replace("- [ ] ", "- [x] ").replace("- [x] Steps complete and checked off",
                                                          "- [ ] Steps complete and checked off")
    text = text[:a] + body + text[b:]
    text = r.once(text, """\
  - system_docs/patches/active/cache_save_best_effort_2026_10_24/ (five patch docs and their indexes)
""", """\
  - system_docs/patches/completed/cache_save_best_effort_2026_10_24/ (five patch docs and their indexes; moved
    there at closure)
""", "artifact path")
    text = r.once(text, """\
- CLEANUP_TRIGGER: kept as the defect's reproducer; rerun at the fix, then disposed with the fix's turn-in.
  The patch docs are promoted into src_architecture and src_components at turn-in and their folder
  moves to system_docs/patches/completed/.
""", """\
- CLEANUP_TRIGGER: applied at closure (Note 32): the artifact folder is retained as the defect's reproducer (the
  probe, its runs at 0.2.8265 and at the fix, the scripts of the lane); the patch docs are promoted into
  src_architecture and src_components and their folder moved to system_docs/patches/completed/.
""", "cleanup trigger")
    text = r.once(text, """\
  runs; 2026-10-24; the Notes below. Tests: the two regression test files (Note 16's PLAN, Note 17's
  runs); 2026-10-24.
""", """\
  runs; 2026-10-24; the Notes below. Tests: the two regression test files (Note 16's PLAN, Note 17's
  runs); 2026-10-24. Implementation: the fix in caching_system.py, spellbook.py and spell.py with its unit tests
  (Note 24); the patch docs, the system documents, the graph descriptors, the release note and the notch
  (Notes 23, 27, 29, 30); 2026-10-24.
""", "attribution")
    r.stage(TICKET, text)


def edit_board(r: Pass) -> int:
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| cache_write_failure \|.*\n", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"BOARD ROW: {len(rows)}")
    board = r.once(board, rows[0], "", "row")
    board = r.once(board, """\
- WORK_ITEM: cache_write_failure
  SWITCH_TRIGGER: 0.2.8266 landed with tests green, docs and release note done, assets rebuilt and the ticket closed.
  RESUME_HIERARCHY:
    - tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md
""", "", "detail")
    anchor = (f"| cache_write_failure | done | melder_0 | {DONE} | Notched 0.2.8266: a cache save the OS refuses no "
              f"longer fails a meld; three follow-ups in backlog; rebuild after closure. | {r.now} |\n")
    board = r.once(board, "<!-- END USER-DEFINED: closed_anchors -->", anchor + "<!-- END USER-DEFINED: closed_anchors -->",
                   "anchor")
    region = board[board.index("<!-- BEGIN USER-DEFINED: closed_anchors -->"):
                   board.index("<!-- END USER-DEFINED: closed_anchors -->")]
    count = len([line for line in region.split("\n") if line.startswith("| ")])
    if count > 12:
        sys.exit(f"ANCHORS: {count} > 12")
    r.stage(r.BOARD, board)
    lines = board.split("\n")
    return lines.index(anchor.rstrip("\n")) + 1


def edit_artifacts(r: Pass) -> None:
    text = r.read(r.ARTIFACTS)
    folder = re.findall(r"^\| tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task\.md \| "
                        r"artifacts/cache_write_failure_20261024/ \|.*\n", text, flags=re.M)
    patch = re.findall(r"^\| tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task\.md \| "
                       r"system_docs/patches/active/cache_save_best_effort_2026_10_24/ \|.*\n", text, flags=re.M)
    if len(folder) != 1 or len(patch) != 1:
        sys.exit(f"ARTIFACT ROWS: {len(folder)}, {len(patch)}")
    text = r.once(text, folder[0], (
        f"| {DONE} | artifacts/cache_write_failure_20261024/ | defect_reproducer | retained | retain_as_reference | "
        "The defect's reproducer (probes/probe_cache_emit_failure.py, cases A-D) with its runs on 0.2.8265 and at the "
        "fix (runs/probe_*, runs/f6_*), the regression tests' red runs and the lane's scripts; rerun the probe if the "
        f"cache save path changes. | {r.now} | HELPFUL |\n"), "folder row")
    text = r.once(text, patch[0], "", "patch row")
    text = r.once(text, "<!-- END USER-DEFINED: cleared_artifacts -->", (
        f"| {DONE} | {PATCH_DONE}/ | promote_to_documentation | Promoted into src_architecture and src_components at "
        f"0.2.8266 (the task's Note 29); the folder moved from patches/active/ at closure. | {r.now} |\n"
        "<!-- END USER-DEFINED: cleared_artifacts -->"), "cleared row")
    r.stage(r.ARTIFACTS, text)


def stage_backlog(r: Pass, spans: List[Tuple[int, int]]) -> None:
    ranges = {f"note{n}": cite(spans, n) for n in (3, 4, 5, 10, 21, 22, 28)}
    notes = followups.notes(r.now, ranges)
    texts = {"tests": followups.tests_docs(r.now, notes["tests"]),
             "frequency": followups.frequency_location(r.now, notes["frequency"]),
             "windows": followups.windows_holder(r.now, notes["windows"])}
    for key, rel in BACKLOG.items():
        r.check_width(texts[key], key)
        r.stage(rel, texts[key])


def close_note(r: Pass, anchor_line: int) -> None:
    def whole(rel: str) -> str:
        count = len(r.read(rel).rstrip("\n").split("\n"))
        return f"context_compass/{rel}:1-{count}"
    decision = r.note(r.now, "DECISION", [
        "Closure. The EXIT_GATE is met but for the rebuild, which runs after this pass: F1-F3 landed as 0.2.8266",
        "(Note 24) with the nine regression tests and the new unit tests green and the full unit, component and",
        "integration trees run, the GIL off and on (Note 26); the patch docs consumed (Notes 23, 27) and promoted, with",
        "the graph, release note and notch (Notes 29-30); the NOTICEs sent (Note 31). The one F6 failure outside",
        "melder_1's files, the CI manifest test that waited on melder_2's pip pin, passes on a /tmp copy of the working",
        "tree, 63 of 63, the GIL off and on; the 29 in melder_1's files are green with its change (its MEASURE).",
        "Acceptance: routine completion under the owner's go (Note 21), which took the plan's turn-in; no independent",
        "review was requested. Not run: the owner's MelderOps rerun on Windows. Follow-ups parked as backlog drafts:",
        "document_refused_cache_save_tests, cache_save_frequency_and_location and identify_windows_cache_file_holder.",
        "Board row and detail removed, closed anchor added; the artifact folder kept as the reproducer; the patch docs",
        "promoted and their folder moved to system_docs/patches/completed/ (Notes 23 and 27 cite them under",
        "patches/active/, where they stood then). The rebuild runs last, after this pass: the src of both lanes and",
        "melder_1's renamed tests are committed (0fddab923 and fa397480e, 20:42Z), this lane's documents, graph, notch",
        "and release note too (3bedd65bb, 21:06Z), and git status lists no missing tracked path, so the builder's",
        "refusal does not apply; melder_1 holds its document edits until the rebuild has run (its Note of 21:17:38Z),",
        "and melder_2's CI edits in flight (M2-32, no src) are packaged as they stand, for the next landing's rebuild",
        "to cover as M2-32 says (Notes 28 and 31)."],
        [f"context_compass/{RUNS}closure_runtime_matrix_gil0.txt:1-4",
         f"context_compass/{RUNS}closure_runtime_matrix_gil1.txt:1-4",
         r.note_range(M1_STORY, "- DATETIME: 2026-10-24T20:57:42Z", "  TYPE: MEASURE"),
         r.note_range(M1_STORY, "- DATETIME: 2026-10-24T21:17:38Z", "  TYPE: FACT"),
         r.note_range(CI_TASK, "- DATETIME: 2026-10-24T21:25:11Z", "  TYPE: PLAN"),
         whole(BACKLOG["tests"]), whole(BACKLOG["frequency"]), whole(BACKLOG["windows"]),
         f"context_compass/{r.BOARD}:{anchor_line}-{anchor_line}"],
        ["The lane is turned in but for the rebuild; melder_1 (0.2.8267), then melder_3, edit the shared documents",
         "next, and the owner's next commit takes this closure's records, the three drafts, the moved patch folder and",
         "the rebuilt assets."],
        ["Rebuild last: the asset runner and its --check; the llm_support builder with --include-untracked and its",
         "--check; record the MEASURE here."], "REQUIRED", 9)
    text = r.read(TICKET)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + decision + "\n\n## Context / Handoff Summary\n",
                  "note")
    a, b = section(text, "## Context / Handoff Summary")
    text = text[:a] + """\
Closed 2026-10-24, notched 0.2.8266 (release-note section "A cache file that cannot be saved no longer fails a
meld"). Delivered: a creation-cache save the operating system refuses no longer fails a meld - `CachingSystem.emit()`
returns a bool, saves through a per-writer temp file, retries a refused rename on Windows for about 100 ms and logs
once per bundle; the Book's save seam leaves its flag cleared after a refusal; `Spell.emit_cache_file()` returns
False (Breaking; the owner's D2). Evidence: the defect and probe (Notes 1-13), the regression tests red on 0.2.8265
(Note 17), the fix (Note 24), F6 (Note 26), the documents, graph, release note and notch (Notes 29-30), the NOTICEs
(Note 31), closure (Note 32). The src and tests are in the owner's commit 0fddab923 and the documents, graph,
version and release note in 3bedd65bb; this closure's records, the three drafts, the moved patch folder and the
rebuilt assets are in the working tree for his next commit. Not run: the owner's MelderOps rerun on Windows. Open:
the Windows holder (Note 5, HYPOTHESIS). Follow-ups, parked as backlog drafts:
TASK-2026-10-24-document_refused_cache_save_tests, TASK-2026-10-24-cache_save_frequency_and_location and
TASK-2026-10-24-identify_windows_cache_file_holder. Last step: the asset and LLM rebuild with both checks, recorded
in the Note after closure.

""" + text[b:]
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    apply = sys.argv[1] == "--apply"
    r = Pass("close_task")
    edit_ticket(r)
    spans = note_spans(r.read(TICKET))
    stage_backlog(r, spans)
    anchor_line = edit_board(r)
    edit_artifacts(r)
    close_note(r, anchor_line)
    r.checked_flush(apply)


if __name__ == "__main__":
    main()
