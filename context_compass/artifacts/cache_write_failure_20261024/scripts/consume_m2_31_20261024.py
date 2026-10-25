"""Consume M2-31 after the re-onboarding (melder_0, 2026-10-24).

melder_2's NOTICE M2-31 (no ACK requested) says its CI set is in the working tree and its lane is closed, and that
the llm_support bundles wait for the last of the two in-flight landings. This pass refreshes melder_0's roster row,
carries the facts into the task's Notes, deletes the message and clears its alert. All-or-nothing: anchors match
once, lines fit 120 characters, no CR, and a file that changed since it was read refuses the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
CI_TASK = "tickets/tasks/completed/2026-10-24_ci_python_315_and_release_test_rerun_task.md"


class Pass(Record):
    """The consumption pass."""

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
    if len(messages) != 1 or "M2-31." not in messages[0]:
        sys.exit(f"MESSAGES for melder_0: {len(messages)}")
    text = r.once(text, messages[0], "", "consume M2-31")
    r.stage(r.MAILBOX, text)


def board(r: Pass) -> None:
    text = r.read(r.BOARD)
    text = r.once(text, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-24T20:35:02Z)\n", "", "alert")
    r.stage(r.BOARD, text)


def ticket(r: Pass) -> None:
    board_lines = r.read(r.BOARD).split("\n")
    anchors = [i for i, line in enumerate(board_lines) if line.startswith("| ci_python_315 | done |")]
    if len(anchors) != 1:
        sys.exit(f"CI ANCHOR: {len(anchors)}")
    measure = r.note_range(CI_TASK, "- DATETIME: 2026-10-24T20:35:02Z", "  TYPE: MEASURE")
    fact = r.note(r.now, "FACT", [
        "M2-31 (melder_2's NOTICE, 2026-10-24T20:35:02Z, consumed here): melder_2's 23-file CI set is in the owner's",
        "working tree on his word and its lane is closed - .github/ (the 3.14.9, 3.15.0 and 3.15.1 manifests",
        "untracked), tests/unit/github_workflows/test_workflow_contracts.py, tests_architecture.md, tests_components.md",
        "and their indexes. melder_2 did not rebuild the llm_support bundles: by its MEASURE the tree carries this",
        "lane's fix and melder_1's removal in flight (src changes, four tracked test files deleted) and the builder",
        "refuses a missing tracked path, so the last of the two landings rebuilds, the three untracked manifests in."],
        [measure, f"context_compass/{r.BOARD}:{anchors[0] + 1}-{anchors[0] + 1}"],
        ["Note 22's hold is over: the tests_* docs are on disk as landed; this lane still leaves them alone (its",
         "boundary) and files their entries for its new tests as a follow-up. The rebuild step becomes \"the last",
         "landing rebuilds\": if melder_1 has not landed when this lane's turn-in is done, this lane reads the builder,",
         "hands the rebuild (with --include-untracked) to melder_1's landing in its NOTICE and does not rebuild over",
         "unfinished work. The F6 unit failure that waited on the pip pin is rerun on the current tree at closure."],
        ["F5: fix the system-doc edit script's failed anchor (its run stopped before writing) and apply it."],
        "REQUIRED", 8)
    text = r.once(r.read(TICKET), "\n\n## Context / Handoff Summary\n", "\n\n" + fact + "\n\n## Context / Handoff Summary\n",
                  "note")
    r.check_width(text, "ticket")
    r.stage(TICKET, text)
    r.set_field(TICKET, "Updated")


def main() -> None:
    r = Pass("consume_m2_31")
    mailbox(r)
    board(r)
    ticket(r)
    r.checked_flush()


if __name__ == "__main__":
    main()
