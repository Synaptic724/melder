"""Re-onboarding check-in for melder_0 (2026-10-18, after a compaction): the roster row and the setup outcome.

The first authorized action after the re-onboarding attestation: refresh melder_0's `last_checked` on
mailbox_board.md and record this session's harness setup outcome (PRESENT) under the board's Notes, as
agent_session_state.md and harness_custom_instructions.md direct. All-or-nothing; `--write` flushes.
"""
import re
import sys

from cc_record import Record


class CheckIn(Record):
    """The roster row and the setup-outcome note."""

    ROW = r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$"
    NOTE = ("- 2026-10-18 melder_0 (session claude@2026-09-26T22:24:06Z): harness custom instructions PRESENT -\n"
            "  the Claude app's personal preferences carry the Context Compass block; no setup form shown.")

    def run(self) -> None:
        """Stage the refreshed row and the note."""
        text = self.read(self.MAILBOX)
        rows = re.findall(self.ROW, text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: found {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        if "melder_0 (session claude@2026-09-26T22:24:06Z)" not in text:
            anchor = "\n<!-- END USER-DEFINED: notes -->"
            text = self.once(text, anchor, "\n" + self.NOTE + anchor, "mailbox notes")
        self.stage(self.MAILBOX, text)


def main() -> None:
    record = CheckIn("checkin_reonboard")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
