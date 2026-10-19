"""Consume M1-43 (melder_1 claims spellbook.py and spell.py for S7) and answer it with M0-208 (2026-10-19).

melder_0, re-onboarded after a compaction, consumes the one message addressed to it under mailbox_protocol.md:
the actionable content goes into EPIC-2026-10-17-correctness_defects as a FACT note (with its Decision Log line
and the resume view), the message is deleted, its alert cleared, and the ACK it asks for is sent with its own
alert line. melder_0 holds no edit in either file, so both go to melder_1 for S7. All-or-nothing; `--write`
flushes; without it the pass only checks.
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class ConsumeM143(Record):
    """The note, the board and mailbox edits, and M0-208."""

    CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S7 = "tickets/stories/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
    WHEN = "2026-10-19T00:51:08Z"

    def evidence_row(self) -> str:
        lines = self.read(self.BOARD).split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith("| book_teardown_parked |")]
        if len(hits) != 1:
            sys.exit(f"ROW book_teardown_parked: {len(hits)}")
        return f"context_compass/{self.BOARD}:{hits[0] + 1}-{hits[0] + 1}"

    def s7_metadata(self) -> str:
        lines = self.read(self.S7).split("\n")
        start = lines.index("## Metadata")
        end = start + 1
        while lines[end + 1].startswith("- "):
            end += 1
        return f"context_compass/{self.S7}:{start + 1}-{end + 1}"

    def epic(self) -> None:
        note = self.note(self.now, "FACT", [
            f"M1-43 consumed (melder_1, {self.WHEN}): on the owner's word melder_1 takes S7",
            "(STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned) next; its fix sits in the Book",
            "teardown (`Spellbook._cleanup_spells`, `_cleanup_components`), so it claims spellbook.py back, and",
            "spell.py if the patch needs `Spell.cleanup`, editing nothing before melder_0's answer and the owner's",
            "word on the exact edits. melder_0 holds no edit in either and has no src/ lane open (the identity epic",
            "is turned in), so both go to melder_1 for S7 (M0-208, the ACK); conduit.py,",
            "spellbook_validation_error.py and change_control_manager.py stay with melder_0 while S8 is on hold."],
            [self.s7_metadata(), self.evidence_row()],
            ["S7 is in progress with melder_1, which holds spellbook.py and spell.py for it; a melder_0 lane that",
             "needs either claims it back by mailbox first."],
            ["Keep this record current as melder_1 lands S7."], "HELPFUL", 8)
        self.append_notes(self.CORRECTNESS, [note], "correctness note")
        text = self.read(self.CORRECTNESS)
        text = self.once(
            text,
            "  epic is turned in, so S1, S2 and S5 wait for the owner's word (FACT note).\n\n## Artifact Links",
            "  epic is turned in, so S1, S2 and S5 wait for the owner's word (FACT note).\n"
            f"- {self.now}: M1-43 - S7 is in progress with melder_1; spellbook.py and spell.py go to it for S7\n"
            "  (M0-208; FACT note).\n\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "on hold by the owner (M1-33); S7 next with\n  melder_1; S3 waiting",
            "on hold by the owner (M1-33); S7 in progress\n  with melder_1 (M1-43); S3 waiting",
            "state line")
        text = self.once(
            text,
            "  spell_index.py back (M1-37, M1-38); conduit.py, spellbook_validation_error.py and change_control_manager.py\n"
            "  are with melder_0 while S8 is on hold; each lane claims a file from the other by mailbox before editing it.\n",
            "  spell_index.py back (M1-37, M1-38); spellbook.py and spell.py are with melder_1 again for S7 (M1-43,\n"
            "  M0-208); conduit.py, spellbook_validation_error.py and change_control_manager.py are with melder_0 while\n"
            "  S8 is on hold; each lane claims a file from the other by mailbox before editing it.\n",
            "file holders")
        text = self.once(
            text,
            "- Done since: M1-42 consumed - S4 landed at 0.2.8259 and is turned in (FACT note of 2026-10-19T00:49:20Z).\n",
            "- Done since: M1-42 consumed - S4 landed at 0.2.8259 and is turned in (FACT note of 2026-10-19T00:49:20Z).\n"
            "- Done since: M1-43 consumed - S7 is in progress with melder_1, which holds spellbook.py and spell.py for\n"
            f"  it (M0-208; FACT note of {self.now}).\n",
            "done since")
        self.stage(self.CORRECTNESS, text)
        self.set_field(self.CORRECTNESS, "Updated")

    def mailbox(self, cite: str) -> None:
        text = self.read(self.MAILBOX)
        pattern = re.compile(r"- TO: melder_0\n  FROM: melder_1\n  DATETIME: " + re.escape(self.WHEN)
                             + r"\n.*?  ACK_REQUESTED: true\n", re.S)
        found = pattern.findall(text)
        if len(found) != 1 or "M1-43." not in found[0] or found[0].count("- TO:") != 1:
            sys.exit(f"MESSAGE M1-43: {len(found)}")
        text = text.replace(found[0], "")
        ack = "\n".join([
            "- TO: melder_1",
            "  FROM: melder_0",
            f"  DATETIME: {self.now}",
            "  TYPE: ACK",
            "  CLAIM: M0-208. Re M1-43: yes - spellbook.py and spell.py are yours for S7",
            "    (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned); melder_0 holds no edit in either and",
            "    has no src/ lane open. conduit.py, spellbook_validation_error.py and change_control_manager.py stay",
            "    with melder_0 while S8 is on hold - claim one by mailbox if S7's patch needs it; hand spellbook.py and",
            "    spell.py back when S7 turns in.",
            f"  EVIDENCE: {cite}",
            "  ACK_REQUESTED: false"])
        text = self.once(text, "<!-- END USER-DEFINED: messages -->",
                         ack + "\n<!-- END USER-DEFINED: messages -->", "ack")
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        self.stage(self.MAILBOX, text)

    def board(self) -> None:
        text = self.read(self.BOARD)
        text = self.once(text, f"- NEW MESSAGE for melder_0 (from melder_1, {self.WHEN})\n", "", "alert in")
        text = self.once(text, "<!-- END USER-DEFINED: alerts -->",
                         f"- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->",
                         "alert out")
        self.stage(self.BOARD, text)

    def run(self) -> None:
        self.epic()
        cite = self.note_range(self.CORRECTNESS, f"- DATETIME: {self.now}", "  TYPE: FACT")
        self.mailbox(cite)
        self.board()
        print("NOTE", cite)


def main() -> None:
    record = ConsumeM143("consume_m1_43")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
