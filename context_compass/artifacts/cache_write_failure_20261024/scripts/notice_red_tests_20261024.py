"""Tell the active agents the two new regression test files are red by design (melder_0, 2026-10-24).

Sends M0-213 to melder_2 (running the suite on 3.15) and M0-214 to melder_1, each with its alert line, and refreshes
melder_0's roster row. All-or-nothing: anchors match once, no CR, and a board that changed since it was read refuses
the pass.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

TICKET = "context_compass/tickets/tasks/2026-10-24_cache_file_write_failure_fails_meld_task.md"
COMPONENT = "tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py"
UNIT = "tests/unit/melder/utilities/test_caching_system_refused_save.py"


class Pass(Record):
    """The notice pass."""

    def checked_flush(self) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        self.flush()


def message(r: Pass, to: str, seq: int, extra: str) -> str:
    return "\n".join([
        f"- TO: {to}",
        "  FROM: melder_0",
        f"  DATETIME: {r.now}",
        "  TYPE: NOTICE",
        f"  CLAIM: M0-{seq}. Two new regression test files (tests only, untracked; the owner's word) fail by design on",
        "    0.2.8265 - 9 failures, the GIL off and on - until the cache-save fix lands on the owner's go:",
        f"    {COMPONENT}",
        f"    and {UNIT}.",
        f"    {extra}",
        f"  EVIDENCE: {TICKET} (Notes 14-20)",
        "  ACK_REQUESTED: false"])


def main() -> None:
    r = Pass("notice_red_tests")
    mailbox = r.read(r.MAILBOX)
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", mailbox, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROSTER: {len(rows)}")
    mailbox = r.once(mailbox, rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |", "roster")
    first = message(r, "melder_2", 213, "Expect them red in your suite runs; no src file changed.")
    second = message(r, "melder_1", 214, "Expect them red in a suite run before then; no src file changed.")
    mailbox = r.once(mailbox, "<!-- BEGIN USER-DEFINED: messages -->\n<!-- END USER-DEFINED: messages -->",
                     "<!-- BEGIN USER-DEFINED: messages -->\n" + first + "\n" + second
                     + "\n<!-- END USER-DEFINED: messages -->", "messages")
    r.stage(r.MAILBOX, mailbox)
    board = r.read(r.BOARD)
    alerts = (f"- NEW MESSAGE for melder_2 (from melder_0, {r.now})\n"
              f"- NEW MESSAGE for melder_1 (from melder_0, {r.now})\n")
    board = r.once(board, "<!-- BEGIN USER-DEFINED: alerts -->\n<!-- END USER-DEFINED: alerts -->",
                   "<!-- BEGIN USER-DEFINED: alerts -->\n" + alerts + "<!-- END USER-DEFINED: alerts -->", "alerts")
    r.stage(r.BOARD, board)
    r.checked_flush()


if __name__ == "__main__":
    main()
