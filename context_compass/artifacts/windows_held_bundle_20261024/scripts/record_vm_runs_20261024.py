"""Record the VM runs of TASK-2026-10-24-windows_held_cache_bundle_test (melder_0, 2026-10-24).

One all-or-nothing pass: M3-3 (melder_3's NOTICE) consumed into Note 3 (FACT), its message deleted and its alert
cleared; Note 4 (MEASURE: the file skips as written and passes under the emulation harness, the GIL off and on, and
its tests 2-4 fail on the 0.2.8265 copy); the two checklist steps ticked, the Validation section with the owner's
Windows commands, the handoff summary and Updated; the board row to validation with its next action; melder_0's
roster row refreshed. Refuses when another message for melder_0 waits, when a file changed since it was read, when
an anchor does not match once, or when a line breaks the width rule.
Usage: record_vm_runs_20261024.py --check | --apply
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_windows_held_cache_bundle_test_task.md"
TEST = "tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py"
FOLDER = "artifacts/windows_held_bundle_20261024/"


class Pass(Record):
    """The VM-runs pass."""

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def test_range(name: str) -> str:
    """`path:a-b` of one top-level test function of the new file, from its def to its last non-blank line."""
    lines = (Record.REPO / TEST).read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith(f"def {name}(")]
    if len(starts) != 1:
        sys.exit(f"TEST {name}: {len(starts)}")
    end = starts[0] + 1
    while end < len(lines) and not (lines[end].startswith("def ") or lines[end].startswith("class ")
                                     or lines[end].startswith("@")):
        end += 1
    while lines[end - 1].strip() == "":
        end -= 1
    return f"{TEST}:{starts[0] + 1}-{end}"


def run_range(r: Pass, name: str) -> str:
    return r.whole(FOLDER + "runs/" + name)


def note(r: Pass) -> str:
    evidence = [
        test_range("test_windows_refuses_a_rename_onto_a_file_held_open"),
        test_range("test_save_waits_out_a_hold_that_ends_while_it_retries"),
        test_range("test_save_outlasted_by_a_hold_returns_false_and_keeps_the_bundle"),
        test_range("test_meld_returns_its_object_while_windows_refuses_its_cache_save"),
        r.whole(FOLDER + "scripts/windows_emulation_harness.py"),
        run_range(r, "skipped_as_written_gil0.txt"),
        run_range(r, "skipped_as_written_gil1.txt"),
        run_range(r, "emulated_gil0.txt"),
        run_range(r, "emulated_gil1.txt"),
        run_range(r, "red_on_0_2_8265_gil0.txt"),
        run_range(r, "red_on_0_2_8265_gil1.txt"),
    ]
    claim = [
        "The test file (four tests) and the Linux emulation harness are written. On a /tmp copy of the working tree",
        "at 0.2.8267 (Python 3.14.7 free-threaded): as written the four tests skip, the GIL off and on; under the",
        "harness (the retry on; a rename onto a file this process holds open refused) they pass, the GIL off and on.",
        "The premise was refused once and allowed on the first try after the close; the short hold saved on the third",
        "attempt (2 refusals, 0.031 s); the long hold returned False after 5 refusals in 0.10 s, the bundle unchanged,",
        "no temp file, one WARNING, and the next save wrote both payloads; the meld returned its object in 0.104 s",
        "through 5 refusals, the second meld saved nothing, and the later spell's save wrote the bundle with 3 plans.",
        "Under the same harness on the 0.2.8265 copy (before the fix) tests 2-4 fail with the PermissionError raised",
        "out of the save or the meld - the owner's failure - and test 1 on the REPLACE_ATTEMPTS its print reads.",
        "Windows: Not run.",
    ]
    impact = [
        "The tests' logic holds off Windows and catches the 0.2.8265 defect. Only Windows answers the premise (does",
        "open() make Windows refuse the rename), which code it raises (5 or 32) and whether a scanner adds refusals.",
    ]
    nxt = ["Hand the owner the PowerShell command in Validation; record his output as a MEASURE."]
    return r.note(r.now, "MEASURE", claim, evidence, impact, nxt, "REQUIRED", 8)


def m3_3_note(r: Pass) -> str:
    claim = [
        "M3-3 from melder_3 (NOTICE, 2026-10-24T22:40:34Z, no ACK asked): src_architecture is at its spec (its trim",
        "story closed, 5,739 -> 4,784 lines). A change landing there states today's rule and its mechanism only,",
        "puts component mechanics in the src_components entry, keeps C1 notes descriptive, adds one dated handoff",
        "entry per lane at the top and no path into context_compass in any spelling; src_components gets the same",
        "pass next (Story 2), and an agent tells melder_3 before writing it. This task writes neither document.",
    ]
    evidence = ["context_compass/tickets/stories/completed/2026-10-24_src_architecture_trim_to_spec_story.md:1-12"]
    impact = [
        "Nothing changes in this lane (tests only). A later lane of mine that writes src_architecture or",
        "src_components - a fix from the backlog drafts - follows those rules and tells melder_3 first while Story 2 runs.",
    ]
    nxt = ["Record the VM runs (Note 4)."]
    return r.note(r.now, "FACT", claim, evidence, impact, nxt, "HELPFUL", 7)


def ticket(r: Pass) -> None:
    text = r.read(TICKET)
    text = r.once(text, "  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n\n## Context / Handoff Summary\n",
                  "  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n\n" + m3_3_note(r) + "\n\n" + note(r)
                  + "\n\n## Context / Handoff Summary\n", "notes 3-4")
    text = r.once(text, "- [ ] Write the Windows-only test file and the emulation harness.\n",
                  "- [x] Write the Windows-only test file and the emulation harness.\n", "step 2")
    text = r.once(text, "- [ ] Run the file on a /tmp copy on the VM: skipped as written and passing under the harness, the "
                        "GIL off and on;\n",
                  "- [x] Run the file on a /tmp copy on the VM: skipped as written and passing under the harness, the "
                  "GIL off and on;\n", "step 3")
    old_validation = text[text.index("## Validation\n"):text.index("## Risks / Rollback Notes\n")]
    new_validation = (
        "## Validation\n"
        "- VM (Linux; Python 3.14.7 free-threaded), a /tmp copy of the working tree at 0.2.8267: as written, 4 skipped,\n"
        "  the GIL off and on; under the emulation harness, 4 passed, the GIL off and on. On the 0.2.8265 copy under the\n"
        "  harness tests 2-4 fail with the save's PermissionError (red before the fix). Note 4.\n"
        "- Windows: Not run (the owner's run).\n"
        "- Commands:\n"
        "  - Windows, PowerShell, from the repository root, where <file> is\n"
        "    tests\\integration\\melder\\conduit\\test_conduit_integration_windows_held_cache_bundle.py:\n"
        "    `.\\.venv_new\\Scripts\\python.exe -m pytest <file> -v -s`, then the same with `-X gil=1` before `-m`.\n"
        "    `.venv_new` installs melder editable from `src`, and tests/conftest.py puts `src` first on sys.path.\n"
        "  - VM: the harness's docstring\n"
        "    (context_compass/artifacts/windows_held_bundle_20261024/scripts/windows_emulation_harness.py).\n"
        "\n"
    )
    r.check_width(new_validation, "validation")
    text = r.once(text, old_validation, new_validation, "validation")
    old_summary = text[text.index("## Context / Handoff Summary\n"):text.index("## Project-Specific Additions\n")]
    new_summary = (
        "## Context / Handoff Summary\n"
        "Scope: a Windows-only test file that makes Windows refuse the cache rename for real and checks the 0.2.8266 save\n"
        "against it (Objective; the owner's ask, Note 1). State: in_progress, melder_0. The file and the Linux emulation\n"
        "harness are written; on the VM the file skips as written and passes under the harness, the GIL off and on, and\n"
        "its tests 2-4 fail on 0.2.8265 (Note 4). Windows: Not run. Next: the owner runs the commands in Validation; his\n"
        "output is recorded as a MEASURE, then the task closes (tests only: no notch, no release-note entry).\n"
        "\n"
    )
    text = r.once(text, old_summary, new_summary, "summary")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def board(r: Pass) -> None:
    text = r.read(r.BOARD)
    text = r.once(
        text,
        "| windows_held_bundle_test | in_progress | implementation | claude | melder_0 | none | Write the Windows-only "
        "test and the emulation harness, run both on a /tmp copy, hand the owner the command. |",
        "| windows_held_bundle_test | in_progress | validation | claude | melder_0 | none | The owner runs the Windows "
        "commands in the task's Validation; record his output as a MEASURE. |",
        "board row",
    )
    row = [line for line in text.split("\n") if line.startswith("| windows_held_bundle_test |")]
    if len(row) != 1:
        sys.exit(f"ROW: {len(row)}")
    stamped = re.sub(r"\| \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ \| REQUIRED \|$", f"| {r.now} | REQUIRED |", row[0])
    if stamped == row[0]:
        sys.exit("ROW STAMP: no match")
    text = r.once(text, row[0], stamped, "board stamp")
    r.stage(r.BOARD, text)


def consume_m3_3(r: Pass) -> None:
    """Delete M3-3 from the mailbox and clear its alert; refuse unless it is there exactly once as read."""
    text = r.read(r.MAILBOX)
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines)
              if line == "- TO: melder_0" and lines[i + 1] == "  FROM: melder_3"
              and lines[i + 2] == "  DATETIME: 2026-10-24T22:40:34Z" and lines[i + 4].startswith("  CLAIM: M3-3. ")]
    if len(starts) != 1:
        sys.exit(f"M3-3: {len(starts)}")
    end = starts[0] + 1
    while not (lines[end].startswith("- TO: ") or lines[end].startswith("<!-- END USER-DEFINED: messages")):
        end += 1
    if lines[end - 1] != "  ACK_REQUESTED: false":
        sys.exit("M3-3: unexpected end")
    r.stage(r.MAILBOX, "\n".join(lines[:starts[0]] + lines[end:]))
    board_text = r.read(r.BOARD)
    board_text = r.once(board_text, "- NEW MESSAGE for melder_0 (from melder_3, 2026-10-24T22:40:34Z)\n", "", "alert")
    r.stage(r.BOARD, board_text)


def roster(r: Pass) -> None:
    text = r.read(r.MAILBOX)
    messages = text[text.index("<!-- BEGIN USER-DEFINED: messages -->"):text.index("<!-- END USER-DEFINED: messages -->")]
    if re.search(r"^- TO: melder_0$", messages, flags=re.M):
        sys.exit("MAILBOX: a message for melder_0 waits; consume it first")
    rows = re.findall(r"^\| melder_0 \| claude \| \S+ \| \S+ \| active \|$", text, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROSTER: {len(rows)}")
    parts = rows[0].split(" | ")
    parts[3] = r.now
    r.stage(r.MAILBOX, r.once(text, rows[0], " | ".join(parts), "roster"))


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        sys.exit(__doc__)
    r = Pass("vm_runs_20261024")
    consume_m3_3(r)
    ticket(r)
    board(r)
    roster(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
