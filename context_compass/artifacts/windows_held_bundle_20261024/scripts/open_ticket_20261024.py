"""Open TASK-2026-10-24-windows_held_cache_bundle_test with its board and artifact rows (melder_0, 2026-10-24).

One all-or-nothing pass: the task ticket from templates/task_template.md (its boilerplate sections copied from the
template), the owner's ask as a DECISION and the PLAN read from the save path; the board row and its detail entry;
the artifact row for this folder; melder_0's roster row refreshed; M1-55 consumed into the backlog draft
document_refused_cache_save_tests, its message deleted and its alert cleared; the three backlog drafts' citations
of the fix ticket moved one line down to its Notes. Refuses when another message for
melder_0 waits, when the ticket exists, when a file changed since it was read, or when a line breaks the width rule.
Usage: open_ticket_20261024.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md"
FIX = "tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md"
DRAFT = "tickets/tasks/backlog/2026-10-24_identify_windows_cache_file_holder_task.md"
TESTS_DRAFT = "tickets/tasks/backlog/2026-10-24_document_refused_cache_save_tests_task.md"
FREQUENCY_DRAFT = "tickets/tasks/backlog/2026-10-24_cache_save_frequency_and_location_task.md"
FOLDER = "artifacts/windows_held_bundle_20261024/"
TEST = "tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py"


class Pass(Record):
    """The opening pass."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        if (self.ROOT / TICKET).exists():
            sys.exit(f"EXISTS {TICKET}; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def template_block(first: str, stop: str) -> str:
    """Return the template's lines from `first` up to, not including, `stop`, without trailing blank lines."""
    lines = (Record.ROOT / "templates/task_template.md").read_text(encoding="utf-8").split("\n")
    return "\n".join(lines[lines.index(first):lines.index(stop)]).rstrip("\n")


def template_tail(first: str) -> str:
    """Return the template from the line `first` to its end, without trailing blank lines."""
    lines = (Record.ROOT / "templates/task_template.md").read_text(encoding="utf-8").split("\n")
    return "\n".join(lines[lines.index(first):]).rstrip("\n")


def resync_draft_citations(r: Pass) -> None:
    """
    Move the three backlog drafts' citations of the fix ticket one line down, where its Notes now stand.

    The rebuild record pass (record_rebuild_20261024.py) turned the fix ticket's one-line "Rebuild last" step into two
    lines after the drafts had cited its Notes, so every cited Note now starts and ends one line lower. Each citation
    is moved only when the moved range is exactly a Note of the ticket; anything else refuses the pass.
    """
    lines = r.read(FIX).split("\n")
    start, end = lines.index("## Notes"), lines.index("## Context / Handoff Summary")
    spans = set()
    for i in range(start, end):
        if lines[i].startswith("- DATETIME: "):
            j = i + 1
            while j < end and lines[j] != "":
                j += 1
            spans.add((i + 1, j))
    pattern = re.compile(re.escape(f"context_compass/{FIX}:") + r"(\d+)-(\d+)")
    for draft in (DRAFT, TESTS_DRAFT, FREQUENCY_DRAFT):
        text = r.read(draft)

        def moved(match: "re.Match[str]") -> str:
            a, b = int(match.group(1)) + 1, int(match.group(2)) + 1
            if (a, b) not in spans:
                sys.exit(f"CITATION {draft}: {match.group(0)} moved to {a}-{b} is no Note of the fix ticket")
            return f"context_compass/{FIX}:{a}-{b}"

        text, count = pattern.subn(moved, text)
        if count == 0:
            sys.exit(f"CITATION {draft}: none found")
        print("resync", draft, count)
        r.stage(draft, text)


def consume_m1_55(r: Pass) -> None:
    """Copy M1-55 (melder_1's NOTICE to melder_0) into the backlog draft it concerns."""
    text = r.read(TESTS_DRAFT)
    fact = r.note(r.now, "FACT", [
        "M1-55 (melder_1's NOTICE, 2026-10-24T22:16:36Z, consumed here): at 0.2.8267 the tests maps count the two",
        "0.2.8266 regression modules (test_conduit_component_refused_cache_save_does_not_fail_meld.py,",
        "test_caching_system_refused_save.py) among their 863 modules, and no tests_components cluster lists them",
        "yet; melder_1's handoff entry names them. Cataloguing them is this draft's work, and the Windows-only file of",
        "TASK-2026-10-24-windows_held_cache_bundle_test joins the list when it lands."],
        ["context_compass/system_docs/tests_components.md:3914-3931"],
        ["The entries go into the clusters the tests documents name; the module counts there are already right."],
        ["The owner schedules it."], "HELPFUL", 7)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + fact + "\n\n## Context / Handoff Summary\n",
                  "draft note")
    r.stage(TESTS_DRAFT, text)
    r.set_field(TESTS_DRAFT, "Updated")


def notes(r: Pass) -> str:
    decision = r.note(r.now, "DECISION", [
        "The owner's ask (chat 2026-10-24), answering the offer of a Windows-only test that holds the bundle open:",
        "\"dude add it to my machine and see what happens I can run whatever commands you want\". This task adds",
        "that test file and nothing else - tests only, so no notch and no release-note entry - and records the",
        "owner's run on Windows here. The fix's open HYPOTHESIS (what held the bundle in his MelderOps run) stays",
        "with the backlog draft identify_windows_cache_file_holder: this test makes its own holder."],
        [r.note_range(FIX, "- DATETIME: 2026-10-24T18:25:58Z", "  TYPE: HYPOTHESIS"), r.whole(DRAFT)],
        ["The 0.2.8266 save gets checked against a refusal Windows itself raises, which the VM cannot raise."],
        ["Record the PLAN read from the save path and the existing refused-save tests."], "REQUIRED", 8)
    plan = r.note(r.now, "PLAN", [
        "Read at 0.2.8267: `emit()` writes the envelope to `<bundle>.<pid>.<thread id>.tmp` and renames it onto the",
        "bundle with `Path.replace` (that is `os.replace`); while `RETRY_REFUSED_RENAME` (True on win32) a",
        "PermissionError is retried up to `REPLACE_ATTEMPTS` (5) with sleeps of 0.01 s times the attempt number",
        "(0.1 s in all), then the save logs once at WARNING, removes its temp file and returns False with its",
        "payloads kept. The premise, UNKNOWN until test 1 runs on Windows: Python's open() there shares read and",
        "write but not delete, so a handle it holds on the bundle makes that rename fail as the owner's run failed.",
        "The file's four tests - Windows-only (skipif), marked integration, nothing injected; a spy on os.replace",
        "only counts and passes through - each print their refusal codes and timings for the owner's run:",
        "(1) a rename onto a held bundle raises PermissionError and succeeds once the handle closes;",
        "(2) a hold the spy releases after two refused attempts: the save returns True with the new payload;",
        "(3) a hold over the whole save: False after exactly REPLACE_ATTEMPTS refusals, the bundle byte-identical,",
        "no temp file, one WARNING; the next save after the hold writes both payloads;",
        "(4) a dynamic root's bundle held while a spell bound after conjure is first melded: the meld returns its",
        "object, its save refused REPLACE_ATTEMPTS times; after the hold a later spell's save writes both plans.",
        "On the VM they skip as written; a harness in this task's artifact folder runs them with the retry on and",
        "a rename onto a file this process holds open refused (read from /proc/self/fd), the GIL off and on."],
        ["src/melder/utilities/caching_system/caching_system.py:762-804",
         "src/melder/utilities/caching_system/caching_system.py:948-1063",
         "src/melder/utilities/caching_system/caching_system.py:263-271",
         "tests/unit/melder/utilities/test_caching_system_refused_save.py:1-485",
         "tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py:1-434"],
        ["Each test names what it shows on a real refusal, so the owner's output reads as the answer to his question."],
        ["Write the test file and the harness; run both on a /tmp copy, the GIL off and on."], "REQUIRED", 8)
    return decision + "\n\n" + plan


def ticket(r: Pass) -> str:
    parts = [
        "# Task: A Windows-only test shows the cache save surviving a real WinError 5",
        "",
        "## Metadata",
        "- Task ID: TASK-2026-10-24-windows_held_cache_bundle_test",
        "- Story: none (standalone; a follow-up of TASK-2026-10-24-cache_file_write_failure_fails_meld)",
        "- Status: in_progress",
        "- Owner: Mark",
        "- Agent Name: melder_0",
        "- Agent Role: synaptic_python_developer",
        "- Priority: p2",
        f"- Created: {r.now}",
        f"- Updated: {r.now}",
        "",
        "## Objective",
        """\
The owner's ask (chat 2026-10-24, after the 0.2.8266 fix): "dude add it to my machine and see what happens I can
run whatever commands you want". The fix's tests inject the rename refusal, because Linux never refuses a rename for
sharing. This task adds a Windows-only integration test file that makes Windows refuse it for real: it holds the
bundle open with Python's open(), which on Windows does not share delete access, so a rename onto it fails as the
owner's MelderOps run failed (PermissionError [WinError 5]). On that real refusal it checks the premise (Windows
refuses the rename), a hold that ends while the save retries (the save waits it out), a hold that outlasts the
retries (the save returns False, the bundle stays as it was, no temp file is left, one WARNING) and a meld whose
save is refused (it returns its object, and a later save writes what was kept). The owner runs it on his machine;
his output is recorded here.""",
        "",
        "## Ticket Contract",
        f"""\
- ENTRY_GATE: this task's board row; the save path and the existing refused-save tests read and recorded first.
- EXECUTION_BOUNDARY: one new test file,
  {TEST}; this ticket, its board
  row, {FOLDER} (the Linux emulation harness and the runs) and its artifact row. No src
  change, no notch, no release-note entry: tests only.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266); the backlog drafts
  identify_windows_cache_file_holder (the MelderOps holder) and document_refused_cache_save_tests (the tests map).
- EXIT_GATE: the file is collected and skipped on the VM and passes there under the emulation harness, the GIL off
  and on; the owner's Windows run recorded; the ticket closed with board and artifact sync.
- FAILURE_ESCALATION: CONFLICT when Windows does not refuse the rename while the handle is held (the fix's
  hypothesis would be wrong); DECISION_REQUEST when a refusal on the owner's machine outlasts the retries in the
  short-hold case, or any test fails there.""",
        "",
        "## Scope Boundaries",
        """\
- In scope: the Windows-only test file; its emulated run on the VM; the owner's run on Windows and its record.
- Out of scope: src and the retry budget (a finding that calls for a change gets a task of its own); naming what
  held the bundle in the owner's MelderOps run (TASK-2026-10-24-identify_windows_cache_file_holder, backlog).""",
        "",
        "## State Transition Event",
        """\
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "dude add it to my machine and see what happens I can run
  whatever commands you want"; melder_0 writes the test and hands him the command.""",
        "",
        "## Steps / Checklist",
        """\
- [x] Read the save path (`CachingSystem.emit` and its helpers) and the refused-save tests; record the PLAN.
- [ ] Write the Windows-only test file and the emulation harness.
- [ ] Run the file on a /tmp copy on the VM: skipped as written and passing under the harness, the GIL off and on;
      record the MEASURE.
- [ ] Hand the owner the command; record his Windows output as a MEASURE.
- [ ] Closure: summary, move to completed/, board and artifact sync; the tests-map entry joins the backlog draft
      document_refused_cache_save_tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.""",
        "",
        "## Deliverables",
        f"""\
- {TEST} (four Windows-only tests).
- The VM runs (skipped; emulated) and the owner's Windows run, recorded here.""",
        "",
        "## Files / Paths Impacted",
        f"""\
- {TEST} (new)
- context_compass/{TICKET}
- context_compass/attention_board.md (this task's row)
- context_compass/artifact_board.md (one row)
- context_compass/{FOLDER}""",
        "",
        "## Validation",
        """\
- Not run.
- Recommended commands:
  - VM, a /tmp copy of the tree: `python -X gil=0 -m pytest -q <the file>` (skipped), then the same with the
    harness (`-p windows_emulation_harness`, its folder on PYTHONPATH).
  - Windows, from the repository root: `uv run pytest <the file> -v -s`""",
        "",
        "## Risks / Rollback Notes",
        """\
- Windows may report the refusal as [WinError 32] rather than [WinError 5]; both are PermissionError, which the
  retry catches; the tests assert PermissionError and print the code.
- A scanner on the owner's machine may add refusals of its own; the short-hold test asserts at least the two it
  makes and prints every count.
- The meld test writes under the package's default cache folder, as the component tests do, and removes its frame
  folder afterwards, best-effort.""",
        "",
        """\
## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.
- [ ] No src or retry-budget change in this task; a finding that calls for one gets a task of its own.""",
        "",
        template_block("## Done Checklist", "## Artifact Links (Optional)"),
        "",
        template_block("## Artifact Links (Optional)", "- ARTIFACTS_REQUIRED: true | false"),
        "",
        f"""\
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - {FOLDER}scripts/
  - {FOLDER}runs/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: kept at closure: the harness runs the Windows-only tests' logic off Windows, beside the runs.""",
        "",
        """\
## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none""",
        "",
        template_block("## Noting Behavior", "## Contribution Attribution"),
        "",
        """\
## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose, tests and evidence; this ticket, the test
  file and the harness; 2026-10-24.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested""",
        "",
        "## Notes",
        notes(r),
        "",
        "## Context / Handoff Summary",
        """\
Scope: a Windows-only test file that makes Windows refuse the cache rename for real and checks the 0.2.8266 save
against it (Objective; the owner's ask, Note 1). State: in_progress, melder_0; the PLAN is recorded (Note 2).
Next: write the file and the emulation harness, run both on a /tmp copy, hand the owner the command.""",
        "",
        template_tail("## Project-Specific Additions"),
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("open_windows_held")
    mailbox = r.read(r.MAILBOX)
    region = mailbox[mailbox.index("<!-- BEGIN USER-DEFINED: messages -->"):
                     mailbox.index("<!-- END USER-DEFINED: messages -->")]
    mine = re.findall(r"^- TO: melder_0\n(?:  .*\n)+", region, flags=re.M)
    if len(mine) != 1 or "FROM: melder_1\n  DATETIME: 2026-10-24T22:16:36Z" not in mine[0] \
            or "CLAIM: M1-55." not in mine[0]:
        sys.exit("MESSAGES for melder_0 other than M1-55 wait: read them first; nothing written")
    mailbox = r.once(mailbox, mine[0], "", "M1-55 consumed")
    resync_draft_citations(r)
    consume_m1_55(r)
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", mailbox, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW melder_0: {len(rows)}")
    r.stage(r.MAILBOX, mailbox.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |"))
    text = ticket(r)
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    board = r.read(r.BOARD)
    exit_signal = "The owner's Windows run recorded and the task closed, or the owner redirects."
    row = (f"| windows_held_bundle_test | in_progress | implementation | claude | melder_0 | none | Write the "
           f"Windows-only test and the emulation harness, run both on a /tmp copy, hand the owner the command. | A "
           f"Windows-only test checks the 0.2.8266 cache save against a real WinError 5 on the owner's machine. | "
           f"{exit_signal} | {TICKET} | {r.now} | REQUIRED |\n")
    board = r.once(board, "<!-- END USER-DEFINED: active_items -->", row + "<!-- END USER-DEFINED: active_items -->",
                   "row")
    detail = (f"- WORK_ITEM: windows_held_bundle_test\n  SWITCH_TRIGGER: {exit_signal}\n  RESUME_HIERARCHY:\n"
              f"    - {TICKET}\n")
    board = r.once(board, "<!-- END USER-DEFINED: active_attention_details -->",
                   detail + "<!-- END USER-DEFINED: active_attention_details -->", "detail")
    board = r.once(board, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-24T22:16:36Z)\n", "", "alert")
    r.stage(r.BOARD, board)
    artifacts = r.read(r.ARTIFACTS)
    artifact_row = (f"| {TICKET} | {FOLDER} | test_harness | active | retain_as_reference | The Linux emulation "
                    f"harness for the Windows-only held-bundle tests (scripts/) and the VM and Windows runs (runs/); "
                    f"kept at closure to rerun the tests' logic off Windows. | {r.now} | HELPFUL |\n")
    artifacts = r.once(artifacts, "<!-- END USER-DEFINED: active_artifacts -->",
                       artifact_row + "<!-- END USER-DEFINED: active_artifacts -->", "artifact row")
    r.stage(r.ARTIFACTS, artifacts)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
