"""Close TASK-2026-10-24-windows_held_cache_bundle_test (melder_0, 2026-10-24).

One all-or-nothing pass: M1-59 (melder_1's NOTICE) consumed into the closure note, its message deleted and its alert
cleared; Note 5 (MEASURE: the owner's Windows run) and Note 6 (DECISION: the closure); the completion summary, status,
transition, checklists, validation, cleanup trigger, attribution and handoff summary; the two backlog drafts get a
FACT note each (the holder draft the measured premise, the tests-map draft its fourth file); the board row and its
detail removed and a closed anchor added (cap 12, oldest dropped first); the artifact row kept as retained; melder_0's
roster row refreshed; then the ticket moves to tickets/tasks/completed/. Refuses when another message for melder_0
waits, when a file changed since it was read, when an anchor does not match once, when the completed path exists, or
when a line breaks the width rule.
Usage: close_task_20261024.py --check | --apply
"""
import os
import pathlib
import re
import sys
from typing import List, Tuple

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md"
DONE = "tickets/tasks/completed/2026-10-24_windows_held_cache_bundle_test_task.md"
HOLDER = "tickets/tasks/backlog/2026-10-24_identify_windows_cache_file_holder_task.md"
TESTS_DRAFT = "tickets/tasks/backlog/2026-10-24_document_refused_cache_save_tests_task.md"
CUT = "tickets/tasks/completed/2026-10-24_cut_release_note_0_2_8265_task.md"
FOLDER = "artifacts/windows_held_bundle_20261024/"
TEST = "tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py"


class Pass(Record):
    """The closure pass."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        if (self.ROOT / DONE).exists():
            sys.exit(f"EXISTS {DONE}; nothing written")
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
        print("moved", TICKET, "->", DONE)


def note_spans(text: str) -> List[Tuple[int, int]]:
    """1-based (start, end) of each Note, in order."""
    lines = text.split("\n")
    spans = []
    for i, line in enumerate(lines):
        if line.startswith("- DATETIME: "):
            end = i + 1
            while end < len(lines) and lines[end] != "":
                end += 1
            spans.append((i + 1, end))
    return spans


def line_of(rel: str, needle: str, extra: int) -> str:
    """`context_compass/rel:a-b` of the one line holding `needle`, and `extra` lines after it."""
    lines = (Record.ROOT / rel).read_text(encoding="utf-8").split("\n")
    hits = [i for i, line in enumerate(lines) if needle in line]
    if len(hits) != 1:
        sys.exit(f"LINE {rel} {needle}: {len(hits)}")
    return f"context_compass/{rel}:{hits[0] + 1}-{hits[0] + 1 + extra}"


def test_whole() -> str:
    count = len((Record.REPO / TEST).read_text(encoding="utf-8").rstrip("\n").split("\n"))
    return f"{TEST}:1-{count}"


def consume_m1_59(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines)
              if line == "- TO: melder_0" and lines[i + 1] == "  FROM: melder_1"
              and lines[i + 2] == "  DATETIME: 2026-10-24T22:56:45Z" and lines[i + 4].startswith("  CLAIM: M1-59. ")]
    if len(starts) != 1:
        sys.exit(f"M1-59: {len(starts)}")
    end = starts[0] + 1
    while not (lines[end].startswith("- TO: ") or lines[end].startswith("<!-- END USER-DEFINED: messages")):
        end += 1
    if lines[end - 1] != "  ACK_REQUESTED: false":
        sys.exit("M1-59: unexpected end")
    text = "\n".join(lines[:starts[0]] + lines[end:])
    region = text[text.index("<!-- BEGIN USER-DEFINED: messages -->"):text.index("<!-- END USER-DEFINED: messages -->")]
    if re.search(r"^- TO: melder_0$", region, flags=re.M):
        sys.exit("MAILBOX: another message for melder_0 waits; consume it first")
    rows = re.findall(r"^\| melder_0 \| claude \| \S+ \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROSTER: {len(rows)}")
    parts = rows[0].split(" | ")
    parts[3] = r.now
    r.stage(r.MAILBOX, r.once(text, rows[0], " | ".join(parts), "roster"))
    board = r.read(r.BOARD)
    r.stage(r.BOARD, r.once(board, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-24T22:56:45Z)\n", "", "alert"))


def measure_note(r: Pass) -> str:
    claim = [
        "The owner's run on his Windows machine (chat 2026-10-24; .venv_new, CPython 3.14.7 free-threaded, melder",
        "editable from the working tree at 0.2.8267): the four tests pass, the GIL off and on (4 passed in 6.00 s and",
        "in 0.68 s), and every refusal is [WinError 5] (ERROR_ACCESS_DENIED), the code of his MelderOps failure. The",
        "premise holds: a rename onto a file Python's open() holds is refused, and allowed on the first try after the",
        "close. The short hold saved on the third attempt (2 refusals; 0.033 s and 0.032 s); the long hold returned",
        "False after 5 refusals in 0.104 s with the bundle unchanged, no temp file and one WARNING, and the next save",
        "wrote both payloads; the meld returned its object through 5 refusals (0.106 s and 0.105 s), the second meld",
        "saved nothing and the later spell's save wrote 3 plans. Nothing else refused a rename (0 beyond the holds').",
    ]
    evidence = [r.whole(FOLDER + "runs/windows_owner_gil0.txt"), r.whole(FOLDER + "runs/windows_owner_gil1.txt"),
                test_whole()]
    impact = [
        "On Windows the 0.2.8266 save does what the VM's emulation showed: a holder that lets go within about 100 ms",
        "costs a wait of about 30 ms, a longer one a refused save with one WARNING, never a failed meld. What held the",
        "bundle in the MelderOps run is still unnamed (TASK-2026-10-24-identify_windows_cache_file_holder).",
    ]
    nxt = ["Close the task (Note 6)."]
    return r.note(r.now, "MEASURE", claim, evidence, impact, nxt, "REQUIRED", 9)


def closure_note(r: Pass, spans: List[Tuple[int, int]]) -> str:
    claim = [
        "Closed: the EXIT_GATE is met - the file skips on the VM and passes there under the emulation harness, the",
        "GIL off and on (Note 4), and the owner's Windows run passes, the GIL off and on (Note 5). Tests only: no",
        "notch, no release-note entry, no rebuild here. M1-59 (melder_1's NOTICE, 2026-10-24T22:56:45Z, consumed",
        "here): its rebuild after the 0.2.8265 cut took the untracked file into the LLM bundles' tests corpus, every",
        "check OK. The artifact folder is retained: the harness reruns the tests' logic off Windows beside the runs.",
        "The holder draft gets the measured premise and the tests-map draft its fourth file (a FACT note each). The",
        "file stays untracked until the owner commits it.",
    ]
    evidence = [f"context_compass/{DONE}:{spans[3][0]}-{spans[4][1]}", r.whole(CUT)]
    impact = ["The lane is done; only the owner's commit of the new test file is pending."]
    nxt = ["None in this task; the two drafts wait for the owner's scheduling."]
    return r.note(r.now, "DECISION", claim, evidence, impact, nxt, "HELPFUL", 8)


def edit_ticket(r: Pass) -> None:
    text = r.read(TICKET)
    if len(note_spans(text)) != 4:
        sys.exit(f"NOTES: {len(note_spans(text))}, expected 4")
    title = "# Task: A Windows-only test shows the cache save surviving a real WinError 5"
    text = r.once(text, title + "\n\n## Metadata\n", f"""\
{title}

- Completed: {r.now}
- Summary: A Windows-only test file checks the 0.2.8266 cache save against a rename Windows itself refuses. On the
  owner's machine (Python 3.14.7 free-threaded, the GIL off and on) all four tests pass and every refusal is
  [WinError 5], his MelderOps code: a hold that ends within the retries is waited out, a longer one leaves the save
  refused and logged and the meld unaffected. Tests only: no notch, no release-note entry; melder_1's rebuild took
  the file into the LLM bundles. The emulation harness and the runs are kept in the artifact folder.

## Metadata
""", "summary")
    text = r.once(text, "- Status: in_progress\n", "- Status: done\n", "status")
    text = r.once(text, """\
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "dude add it to my machine and see what happens I can run
  whatever commands you want"; melder_0 writes the test and hands him the command.
""", """\
- from_state: in_progress (validation)
- to_state: done
- transition_reason: the EXIT_GATE is met (Notes 4-5): the file skips on the VM and passes under the emulation
  harness, the GIL off and on, and passes on the owner's Windows machine, the GIL off and on. Routine closure of the
  owner's ask (Note 1); tests only (Note 6).
""", "transition")
    a, b = text.index("## Steps / Checklist\n"), text.index("## Deliverables\n")
    text = text[:a] + text[a:b].replace("- [ ] ", "- [x] ") + text[b:]
    a, b = text.index("## Applicable Anti-Patterns\n"), text.index("## Done Checklist\n")
    text = text[:a] + text[a:b].replace("- [ ] ", "- [x] ") + text[b:]
    a, b = text.index("## Done Checklist\n"), text.index("## Artifact Links (Optional)\n")
    text = text[:a] + text[a:b].replace("- [ ] ", "- [x] ") + text[b:]
    text = r.once(text, "- Windows: Not run (the owner's run).\n",
                  "- Windows, the owner's machine (chat 2026-10-24): 4 passed, the GIL off and on; every refusal [WinError 5]\n"
                  "  (Note 5).\n", "validation")
    text = r.once(text, "- CLEANUP_TRIGGER: kept at closure: the harness runs the Windows-only tests' logic off Windows, "
                        "beside the runs.\n",
                  "- CLEANUP_TRIGGER: applied at closure (Note 6): the folder is retained - the harness reruns the "
                  "Windows-only\n  tests' logic off Windows, beside the VM and Windows runs.\n", "cleanup")
    text = r.once(text, """\
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, tests and evidence; this ticket, the test
  file and the harness; 2026-10-24.
""", """\
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, tests and evidence; this ticket, the test
  file and the harness; 2026-10-24.
- Evidence: the Windows runs by Mark (the owner) on his machine, pasted in chat 2026-10-24 (Note 5).
""", "attribution")
    # The notes go in last among the edits above them, so the closure note's citation of Notes 4-5 counts the
    # completion summary, the validation, cleanup and attribution lines already in place.
    text = r.once(text, "  NEXT: Hand the owner the PowerShell command in Validation; record his output as a MEASURE.\n"
                        "  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n\n## Context / Handoff Summary\n",
                  "  NEXT: Hand the owner the PowerShell command in Validation; record his output as a MEASURE.\n"
                  "  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n\n" + measure_note(r) + "\n\n## Context / Handoff Summary\n",
                  "note 5")
    spans = note_spans(text)
    text = r.once(text, "  SCORE_0_TO_10: 9\n\n## Context / Handoff Summary\n",
                  "  SCORE_0_TO_10: 9\n\n" + closure_note(r, spans) + "\n\n## Context / Handoff Summary\n", "note 6")
    a, b = text.index("## Context / Handoff Summary\n"), text.index("## Project-Specific Additions\n")
    text = text[:a] + """\
## Context / Handoff Summary
Done (Note 6): the Windows-only test file is in tests/integration/melder/conduit/ (untracked until the owner
commits it) and passes on the owner's Windows machine, the GIL off and on, with [WinError 5] on every refusal
(Note 5); the emulation harness and the runs stay in the artifact folder. Open elsewhere, as drafts: the MelderOps
holder (TASK-2026-10-24-identify_windows_cache_file_holder) and the tests-map entries
(TASK-2026-10-24-document_refused_cache_save_tests).

""" + text[b:]
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def edit_holder(r: Pass) -> None:
    text = r.read(HOLDER)
    claim = [
        "Measured on the owner's machine (TASK-2026-10-24-windows_held_cache_bundle_test, its Note 5): a handle that",
        "Python's open() holds - it does not share delete access - makes Windows refuse a rename onto the bundle with",
        "[WinError 5], the code of the MelderOps failure, on every attempt while it is held; the 0.2.8266 retry waits",
        "out a hold that ends within it (2 refusals, 0.033 s), and a longer one leaves the save refused with one",
        "WARNING while the meld returns its object. Any holder without FILE_SHARE_DELETE explains the failure; which",
        "process held melderops.meldercache is still unmeasured.",
    ]
    evidence = [r.whole(FOLDER + "runs/windows_owner_gil0.txt"), test_whole()]
    impact = ["The HYPOTHESIS's mechanism is confirmed; the Steps only have to name the holder and its hold time",
              "against the budget of about 100 ms."]
    note = r.note(r.now, "FACT", claim, evidence, impact, ["The owner's MelderOps rerun (Steps)."], "REQUIRED", 8)
    text = r.once(text, "  SCORE_0_TO_10: 7\n\n## Context / Handoff Summary\n",
                  "  SCORE_0_TO_10: 7\n\n" + note + "\n\n## Context / Handoff Summary\n", "holder note")
    text = r.once(text, """\
Draft, parked: the owner's rerun on Windows to name the holder behind WinError 5 (Objective); the fix makes the
refusal harmless either way. Evidence: the FACT note above and Notes 4-5 of the fix ticket.
""", """\
Draft, parked: the owner's rerun on Windows to name the holder behind WinError 5 (Objective); the fix makes the
refusal harmless either way, and a Windows-only test measured the mechanism (the second FACT note). Evidence: the
FACT notes above and Notes 4-5 of the fix ticket.
""", "holder summary")
    r.stage(HOLDER, text)
    r.set_field(HOLDER, "Updated")


def edit_tests_draft(r: Pass) -> None:
    text = r.read(TESTS_DRAFT)
    text = r.once(text, """\
  left cleared, no retry until cache is staged again), the explicit save (True when written, False when refused,
  through `Spell.emit_cache_file()` too) and the conjure-end save.
""", """\
  left cleared, no retry until cache is staged again), the explicit save (True when written, False when refused,
  through `Spell.emit_cache_file()` too) and the conjure-end save;
- tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py - four Windows-only
  integration tests (TASK-2026-10-24-windows_held_cache_bundle_test, after 0.2.8267; skipped elsewhere): the save
  against a rename Windows itself refuses while the bundle is held open - the premise, a hold that ends within the
  retries, one that outlasts them, and a meld through a refused save.
""", "objective")
    text = r.once(text, "- In scope: the three files' entries in both tests documents.\n",
                  "- In scope: the four files' entries in both tests documents.\n", "scope")
    text = r.once(text, "meld-door tests; write the three entries.\n", "meld-door tests; write the four entries.\n",
                  "step")
    text = r.once(text, "- The three entries in tests_components,", "- The four entries in tests_components,",
                  "deliverables")
    claim = [
        "The Windows-only file landed (untracked until the owner commits it): four integration tests, skipped off",
        "Windows and passing on the owner's machine, the GIL off and on; melder_1's rebuild took it into the LLM",
        "bundles' tests corpus (M1-59). It is the Objective's fourth entry. With it the integration tier holds one",
        "`test_*.py` module more than the tests documents' last recount (178 among 185 `.py` files; 863 in the three",
        "tiers), so the counts are recounted at pickup.",
    ]
    evidence = [test_whole(),
                line_of("system_docs/tests_components.md", "178 `test_*.py` modules among 185 `.py` files", 1),
                line_of("system_docs/tests_architecture.md", "the three tiers' 863 `test_*.py`", 1)]
    impact = ["The draft's scope grows by one file and the two documents' module counts by one."]
    note = r.note(r.now, "FACT", claim, evidence, impact, ["The owner schedules it."], "REQUIRED", 7)
    text = r.once(text, "  SCORE_0_TO_10: 7\n\n## Context / Handoff Summary\n",
                  "  SCORE_0_TO_10: 7\n\n" + note + "\n\n## Context / Handoff Summary\n", "tests note")
    text = r.once(text, """\
Draft, parked: the entries for the three refused-save test files of 0.2.8266 (Objective). Waits for the owner's
scheduling and for the shared tests documents to be free. Evidence: the FACT note above and the fix ticket.
""", """\
Draft, parked: the entries for the three refused-save test files of 0.2.8266 and the Windows-only test file that
followed (Objective). Waits for the owner's scheduling and for the shared tests documents to be free. Evidence: the
FACT notes above and the fix ticket.
""", "tests summary")
    r.check_width(text, "tests draft")
    r.stage(TESTS_DRAFT, text)
    r.set_field(TESTS_DRAFT, "Updated")


def edit_board(r: Pass) -> None:
    board = r.read(r.BOARD)
    rows = re.findall(r"^\| windows_held_bundle_test \|.*\n", board, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"BOARD ROW: {len(rows)}")
    board = r.once(board, rows[0], "", "row")
    board = r.once(board, """\
- WORK_ITEM: windows_held_bundle_test
  SWITCH_TRIGGER: The owner's Windows run recorded and the task closed, or the owner redirects.
  RESUME_HIERARCHY:
    - tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md
""", "", "detail")
    anchor = (f"| windows_held_bundle_test | done | melder_0 | {DONE} | Windows-only test of the 0.2.8266 cache save: "
              f"4 passed on the owner's machine, the GIL off and on, [WinError 5] on every refusal; tests only. | "
              f"{r.now} |\n")
    board = r.once(board, "<!-- END USER-DEFINED: closed_anchors -->", anchor + "<!-- END USER-DEFINED: closed_anchors -->",
                   "anchor")
    begin = board.index("<!-- BEGIN USER-DEFINED: closed_anchors -->")
    end = board.index("<!-- END USER-DEFINED: closed_anchors -->")
    region = board[begin:end]
    anchors = [line for line in region.split("\n") if line.startswith("| ")]
    while len(anchors) > 12:
        oldest = anchors.pop(0)
        print("dropping the oldest anchor:", oldest[:100])
        board = r.once(board, oldest + "\n", "", "drop anchor")
    r.stage(r.BOARD, board)


def edit_artifacts(r: Pass) -> None:
    text = r.read(r.ARTIFACTS)
    rows = re.findall(r"^\| tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task\.md \| "
                      r"artifacts/windows_held_bundle_20261024/ \|.*\n", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ARTIFACT ROW: {len(rows)}")
    text = r.once(text, rows[0], (
        f"| {DONE} | {FOLDER} | test_harness | retained | retain_as_reference | The Linux emulation harness for the "
        "Windows-only held-bundle tests (scripts/) with the VM runs, the red runs on 0.2.8265 and the owner's Windows "
        f"runs (runs/); rerun the harness if the cache save path changes. | {r.now} | HELPFUL |\n"), "artifact row")
    r.stage(r.ARTIFACTS, text)


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("close_windows_held")
    consume_m1_59(r)
    edit_ticket(r)
    edit_holder(r)
    edit_tests_draft(r)
    edit_board(r)
    edit_artifacts(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
