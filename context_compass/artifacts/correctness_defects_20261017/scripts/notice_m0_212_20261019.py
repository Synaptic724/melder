"""M0-212 to melder_1 on the owner's word (chat 2026-10-19: "Ok pass all that info to m1"): the full report of the
handoff M0-211 pointed to - what S3 landed, what is left for melder_1, and the pre-existing items for the owner.

The content already sits in S3's handoff DECISION note and the epic's (both melder_1's tickets now, so nothing is
written to them); the message carries it with pointers. The alert goes on the attention board and melder_0's roster
row refreshes `last_checked` (no messages were addressed to melder_0) and stays departed. All-or-nothing; `--write`
flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class NoticeM0212(Record):
    """The mailbox and the alert."""

    EPIC_C = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"

    def run(self) -> None:
        text = self.read(self.MAILBOX)
        if re.search(r"^- TO: melder_0$", text, flags=re.M):
            sys.exit("a message is addressed to melder_0: consume it first")
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| departed \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | departed |")
        s3_note = self.note_range(self.S3, "- DATETIME: 2026-10-19T12:35:35Z", "  TYPE: DECISION")
        epic_note = self.note_range(self.EPIC_C, "- DATETIME: 2026-10-19T12:35:35Z", "  TYPE: DECISION")
        message = (
            "- TO: melder_1\n"
            "  FROM: melder_0\n"
            f"  DATETIME: {self.now}\n"
            "  TYPE: HANDOFF\n"
            "  CLAIM: M0-212, on the owner's word (chat 2026-10-19: \"Ok pass all that info to m1\"): the full report\n"
            "    behind M0-211. S3 at 0.2.8261: `cleanup_spell` takes a version out of every contract of its Book's root\n"
            "    conduit - index-link members and version grants - before it disposes it, and the Spellbook's own door\n"
            "    goes through the root conduit. The release-note section \"Cleaning up a spell takes it out of every\n"
            "    contract first\" carries an example that runs as written: OK on S3 with the GIL off and on; on 0.2.8260\n"
            "    its notch raises AttributeError in the borrower fan-out (probes/probe_release_note_s3.py and\n"
            "    runs/s3_fix/release_note_probe_* under artifacts/correctness_defects_20261017/). The notch is in; no\n"
            "    rebuild. Yours to do: apply S8 on S3's tree and run the whole tree there - your S8 mirror lacked S3's 13\n"
            "    tests (tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py and\n"
            "    tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py);\n"
            "    rebuild for both, setting the release note's rebuild line (it reads 0.2.8260); turn S3 in when the owner\n"
            "    says so - the patch docs to system_docs/patches/completed/cleanup_releases_contracts_2026_10_19/, the\n"
            "    story to completed/, both boards synced. Open, pre-existing and not S3's, for the owner: a direct\n"
            "    `Spell.cleanup()` and `cleanup_and_remove_spell` release no contract (probe K6); a grant of a parked\n"
            "    version adds every member id of its index to the borrower's borrowed ids and its removal drops only\n"
            "    its own (`Spellbook._add_inactive_contracted_spell`, probe K2);\n"
            "    `test_concurrent_adds_of_same_conduit_admit_exactly_one` is flaky (1 of 10 reruns fail on 0.2.8260\n"
            "    too); the graph nodes Conduit and ConduitWard stay SEMANTICS_STALE (stale at HEAD before S3, not\n"
            "    re-read). S11 (STORY-2026-10-19-notch_back_keeps_outgoing_dependencies, M1-47) is listed in the epic.\n"
            "  EVIDENCE:\n"
            f"  - {s3_note}\n"
            f"  - {epic_note}\n"
            "  ACK_REQUESTED: false")
        text = self.once(text, "\n<!-- END USER-DEFINED: messages -->",
                         "\n" + message + "\n<!-- END USER-DEFINED: messages -->", "message")
        self.stage(self.MAILBOX, text)
        board = self.read(self.BOARD)
        board = self.once(board, "\n<!-- END USER-DEFINED: alerts -->",
                          f"\n- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->",
                          "alert m0-212")
        self.stage(self.BOARD, board)
        print("EVIDENCE", s3_note, epic_note)


def main() -> None:
    record = NoticeM0212("notice_m0_212")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
