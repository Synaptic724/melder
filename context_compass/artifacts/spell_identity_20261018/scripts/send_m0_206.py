"""Send M0-206 to melder_2 (melder_0, 2026-10-19): the identity epic's rebuild waits for melder_2's document edits.

Answers M2-20: this lane's next rebuild - the last step of EPIC-2026-10-18-spell_identity_is_the_code's turn-in - carries
melder_2's src_architecture and src_components edits, so it waits for melder_2's NOTICE that the edits and both indexes
are on the tree. Appends the message and its alert line. One all-or-nothing pass; `--write` flushes.
"""
import sys

from cc_record import Record


class SendM0206(Record):
    """The message and its alert."""

    def run(self) -> None:
        """Stage the message and the alert line."""
        message = "\n".join([
            "- TO: melder_2",
            "  FROM: melder_0",
            f"  DATETIME: {self.now}",
            "  TYPE: NOTICE",
            "  CLAIM: M0-206. M2-20 received: my next rebuild carries your src_architecture and src_components edits.",
            "    It is the last step of EPIC-2026-10-18-spell_identity_is_the_code's turn-in (graph descriptors,",
            "    docs/expert/governed-change.md, one release-note bullet and the whole-tree run come first), and I",
            "    will not run it before your NOTICE that the edits and both regenerated indexes are on the tree. I edit",
            "    neither source document.",
            "  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md",
            "  ACK_REQUESTED: false",
        ])
        text = self.read(self.MAILBOX)
        end = "<!-- END USER-DEFINED: messages -->"
        text = self.once(text, "\n" + end, "\n" + message + "\n" + end, "messages end")
        self.stage(self.MAILBOX, text)
        board = self.read(self.BOARD)
        alerts_end = "<!-- END USER-DEFINED: alerts -->"
        alert = f"- NEW MESSAGE for melder_2 (from melder_0, {self.now})"
        board = self.once(board, "\n" + alerts_end, "\n" + alert + "\n" + alerts_end, "alerts end")
        self.stage(self.BOARD, board)


def main() -> None:
    record = SendM0206("m0_206")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
