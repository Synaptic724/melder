"""Re-open TASK-2026-10-24-cache_file_write_failure_fails_meld for the regression tests (melder_0, 2026-10-24).

First authorized pass after the re-onboarding: refresh melder_0's roster row, consume M1-48 (delete it, clear its
alert, carry its custody fact into the ticket), move the task ready -> in_progress under melder_0 for the owner's
"first create the regression test to catch the bug then build your plan around it", widen its boundary to the two
test files, re-add its attention_board.md row and detail entry and mark its artifact row active. All-or-nothing:
anchors match once, lines fit 120 characters, no CR, and a file that changed since it was read refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
FOLDER = "artifacts/cache_write_failure_20261024"
COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py"
UNIT = "tests/unit/melder/utilities/test_caching_system_refused_save.py"
OWNER_WORDS = '"first create the regression test to catch the bug then build your plan around it"'


class Pass(Record):
    """The re-opening pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def mailbox(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROSTER: {len(rows)}")
    text = r.once(text, rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |", "roster")
    messages = re.findall(r"^- TO: melder_0\n(?:  .*\n)+", text, flags=re.M)
    if len(messages) != 1 or "M1-48." not in messages[0]:
        sys.exit(f"MESSAGES for melder_0: {len(messages)}")
    text = r.once(text, messages[0], "", "consume M1-48")
    r.stage(r.MAILBOX, text)


def boards(r: Pass) -> None:
    board = r.read(r.BOARD)
    board = r.once(board, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-24T18:35:08Z)\n", "", "alert")
    if re.search(r"^\| cache_write_failure \|", board, flags=re.M):
        sys.exit("ROW already present")
    exit_signal = "Tests red on 0.2.8265 with runs recorded and the fix PLAN noted; the owner gives a go or redirects."
    row = ("| cache_write_failure | in_progress | implementation | claude | melder_0 | none | Write the regression "
           "tests, run them red on a /tmp copy of the tree (GIL off and on), then record the fix PLAN. | Regression "
           "tests that catch the bug today and a fix plan built around them, for the owner's go. | "
           f"{exit_signal} | {TICKET} | {r.now} | REQUIRED |")
    detail = "\n".join(["- WORK_ITEM: cache_write_failure", f"  SWITCH_TRIGGER: {exit_signal}",
                        "  RESUME_HIERARCHY:", f"    - {TICKET}"])
    board = r.once(board, "\n<!-- END USER-DEFINED: active_items -->",
                   "\n" + row + "\n<!-- END USER-DEFINED: active_items -->", "board row")
    board = r.once(board, "\n<!-- END USER-DEFINED: active_attention_details -->",
                   "\n" + detail + "\n<!-- END USER-DEFINED: active_attention_details -->", "board detail")
    r.stage(r.BOARD, board)
    arts = r.read(r.ARTIFACTS)
    old_rows = re.findall(rf"^\| {re.escape(TICKET)} \| {re.escape(FOLDER)}/ \|.*$", arts, flags=re.M)
    if len(old_rows) != 1:
        sys.exit(f"ARTIFACT ROW: {len(old_rows)}")
    new_row = (f"| {TICKET} | {FOLDER}/ | defect_reproducer | active | retain_as_reference | Probe cases A-D and "
               "the red runs of the regression tests (GIL off and on); rerun both at the fix. runs/ holds the 0.2.8265 "
               f"baselines and runs/melderops_cache_listing_20261024.txt the owner's cache folder. | {r.now} | REQUIRED |")
    arts = r.once(arts, old_rows[0], new_row, "artifact row")
    r.stage(r.ARTIFACTS, arts)


def contract(r: Pass, text: str) -> str:
    old_boundary = "\n".join([
        "- EXECUTION_BOUNDARY: documentation only - this ticket, its board row, and artifacts/cache_write_failure_20261024/",
        "  (probe, runs, scripts) with its artifact row. No change to src/, tests/, docs/ or release_docs/ (no notch, no",
        "  release-note entry, no rebuild). MelderOps (priv_commandops) is read, never written."])
    new_boundary = "\n".join([
        "- EXECUTION_BOUNDARY: this ticket, its board row, artifacts/cache_write_failure_20261024/ with its artifact row,",
        "  and, on the owner's word (chat 2026-10-24:",
        f"  {OWNER_WORDS}),",
        "  two new test files that fail until the fix:",
        f"  {COMPONENT} and",
        f"  {UNIT}. No change to src/,",
        "  docs/ or release_docs/ - a tests-only change takes no notch, release-note entry or rebuild - and the fix",
        "  waits for the owner's go. MelderOps (priv_commandops) is read, never written."])
    text = r.once(text, old_boundary, new_boundary, "boundary")
    deps = re.findall(r"^- DEPENDENCIES: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(deps) != 1:
        sys.exit(f"DEPENDENCIES: {len(deps)}")
    text = r.once(text, deps[0], "\n".join([
        "- DEPENDENCIES: none for the tests. The fix touches src/melder/utilities/caching_system/caching_system.py and",
        "  src/melder/aether/spellbook/spellbook.py (`_emit_cache_file_if_required`); melder_1 holds no src file",
        "  (M1-48, 2026-10-24), so no lane holds either today - re-read the board before the fix starts."]) + "\n",
        "dependencies")
    gates = re.findall(r"^- EXIT_GATE: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(gates) != 1:
        sys.exit(f"EXIT_GATE: {len(gates)}")
    text = r.once(text, gates[0], "\n".join([
        "- EXIT_GATE: the record round's gate is met (Notes 1-13). This round: the regression tests exist and fail on",
        "  0.2.8265 for the bug, the GIL off and on, with their runs under the artifact folder (a MEASURE); a PLAN maps",
        "  each test to a fix step; the owner has the report. The fix itself is the next round, on his go."]) + "\n",
        "exit gate")
    events = re.findall(r"^- from_state: .*\n- to_state: .*\n- transition_reason: .*\n(?:  .*\n)*", text, flags=re.M)
    if len(events) != 1:
        sys.exit(f"STATE EVENT: {len(events)}")
    text = r.once(text, events[0], "\n".join([
        "- from_state: ready",
        "- to_state: in_progress",
        "- transition_reason: the owner's word (chat 2026-10-24),",
        f"  {OWNER_WORDS};",
        "  melder_0 executes and the board row is back."]) + "\n", "state event")
    return text


def body(r: Pass, text: str) -> str:
    text = r.once(text, "- Status: ready\n", "- Status: in_progress\n", "status")
    text = r.once(text, "- Agent Name: unassigned\n", "- Agent Name: melder_0\n", "agent name")
    text = r.once(text, "- Agent Role: UNKNOWN\n", "- Agent Role: synaptic_python_developer\n", "agent role")
    text = r.once(text, "- [x] Run Ticket Microcycle during execution:\n", "\n".join([
        "- [ ] Write the regression tests (component tests through the meld doors; a unit test of the save) and run",
        "      them on a /tmp copy of 0.2.8265, the GIL off and on; record the red runs as a MEASURE.",
        "- [ ] Record the fix PLAN mapped to the tests and report it to the owner; the fix waits for his go.",
        "- [x] Run Ticket Microcycle during execution:"]) + "\n", "steps")
    text = r.once(text, "- context_compass/artifact_board.md (one active row)\n", "\n".join([
        "- context_compass/artifact_board.md (one active row)",
        f"- {COMPONENT} (new)",
        f"- {UNIT} (new)"]) + "\n", "paths")
    text = r.once(text, "- Recommended commands:\n", "\n".join([
        "- Not run yet: the regression tests (this round runs them red on a copy of the tree).",
        "- Recommended commands:",
        "  - VM, against a copy of the tree (the tests write their cache under the copy's package root):",
        "    `python -X gil=0 -m pytest -q <the two new test files under Files / Paths Impacted>`"]) + "\n",
        "validation")
    return text


def notes(r: Pass, text: str) -> str:
    lines = r.read(r.BOARD).split("\n")
    rows = [i for i, line in enumerate(lines) if line.startswith("| correctness_defects |")]
    if len(rows) != 1:
        sys.exit(f"EPIC ROW: {len(rows)}")
    epic_row = f"context_compass/attention_board.md:{rows[0] + 1}-{rows[0] + 1}"
    staged = text.split("\n")
    starts = [i for i, line in enumerate(staged) if line.startswith("- EXECUTION_BOUNDARY: ")]
    ends = [i for i, line in enumerate(staged) if line.startswith("- DEPENDENCIES: ")]
    if len(starts) != 1 or len(ends) != 1:
        sys.exit("CONTRACT LINES")
    boundary = f"context_compass/{TICKET}:{starts[0] + 1}-{ends[0] + 3}"
    decision = r.note(r.now, "DECISION", [
        "The owner's word (chat 2026-10-24):",
        f"{OWNER_WORDS}. The task moves",
        "ready -> in_progress under melder_0 and its boundary takes two new test files: component tests that",
        "meld through the doors with the save refused, and a unit test of the save itself. They are written to fail on",
        "0.2.8265 for the bug and pass once it is fixed, whichever of the DECISION_REQUEST's directions lands, so they",
        "assert the meld's and the save's outcomes, not where the tolerance sits. The refusal is injected at",
        "`os.replace` - the OS boundary every platform's CI runs through - for this test's bundle only. Tests only:",
        "no notch, no release-note entry, no rebuild; the src fix waits for the owner's go."],
        [boundary, r.note_range(TICKET, "- DATETIME: 2026-10-24T18:29:27Z", "  TYPE: DECISION_REQUEST")],
        ["The fix plan is built around tests that already fail; the src change stays behind the owner's approval."],
        ["Read the save, the meld doors and the cache-test conventions, then record the tests' PLAN."], "REQUIRED", 8)
    custody = r.note(r.now, "FACT", [
        "M1-48 (melder_1's NOTICE, 2026-10-24T18:35:08Z, consumed here): the board cleanup on the owner's word left",
        "this task, its row history and its artifact folder untouched, and melder_1 holds no src file; its correctness",
        "epic is in handoff, its S2, S5 and S11 waiting for the owner. The ticket's old hold on spellbook.py (the",
        "contract's DEPENDENCIES, Note 10's NEXT) no longer stands."],
        [epic_row, "context_compass/tickets/tasks/completed/2026-10-24_strip_old_board_and_artifact_state_task.md:28-28"],
        ["The fix can touch caching_system.py and spellbook.py without a hand-off; the board is re-read before it does."],
        ["Re-read the attention board before the fix starts."], "HELPFUL", 7)
    return r.once(text, "\n\n## Context / Handoff Summary\n",
                  "\n\n" + decision + "\n\n" + custody + "\n\n## Context / Handoff Summary\n", "notes")


def summary(r: Pass, text: str) -> str:
    sections = re.findall(r"## Context / Handoff Summary\n(?:.+\n)+", text)
    if len(sections) != 1:
        sys.exit(f"SUMMARY: {len(sections)}")
    new = "\n".join([
        "## Context / Handoff Summary",
        "Scope: the defect is documented (Notes 1-13); this round, on the owner's word (Note 14), writes regression",
        "tests that fail on 0.2.8265 for the bug and a fix plan built around them. State: in_progress, melder_0,",
        "board row back. Evidence: the write, its nine meld-door call sites, the conjure-end write and the cache",
        "location (Notes 1-3, 8); the owner's run (Note 4); probe cases A-D (Note 9). Open: the Windows cause (Note",
        "5, HYPOTHESIS: a scanner or indexer holding the just-written bundle) - verify with Process Monitor or a run",
        "with the venv excluded from real-time scanning. Holds: no src change before the owner's go; no lane holds",
        "caching_system.py or spellbook.py (Note 15, M1-48). Next: read the save, the meld doors and the cache-test",
        "conventions; record the tests' PLAN; write the two test files; run them red, the GIL off and on; then the",
        "fix PLAN mapped to the tests, reported to the owner. Answered earlier: the mediators (Notes 11-12) and a",
        "single owner module (Note 13) - CachingSystem already is it."]) + "\n"
    return r.once(text, sections[0], new, "summary")


def main() -> None:
    r = Pass("reonboard_open_tests")
    mailbox(r)
    boards(r)
    text = r.read(TICKET)
    text = contract(r, text)
    text = body(r, text)
    r.stage(TICKET, text)
    text = notes(r, r.read(TICKET))
    text = summary(r, text)
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")
    r.checked_flush()


if __name__ == "__main__":
    main()
