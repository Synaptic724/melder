"""Consume M1-44 (melder_1: S7 landed at 0.2.8260 and is turned in; spellbook.py and spell.py back) - melder_0.

The epic gets a FACT note, S7's box ticked, a Decision Log line and its resume view; the message is deleted, its
alert cleared and melder_0's last_checked refreshed. No ACK was requested. All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class ConsumeM144(Record):
    """The epic's lines, the mailbox and the alert."""

    CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S7_DONE = "tickets/stories/completed/2026-10-17_book_teardown_leaves_parked_versions_uncleaned_story.md"
    WHEN = "2026-10-19T01:36:42Z"

    def line_of(self, rel: str, prefix: str) -> str:
        lines = self.read(rel).split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(hits) != 1:
            sys.exit(f"LINE {rel} {prefix}: {len(hits)}")
        return f"context_compass/{rel}:{hits[0] + 1}-{hits[0] + 1}"

    def version_line(self) -> str:
        lines = (self.REPO / "src/melder/__version__.py").read_text(encoding="utf-8").split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith("__version__")]
        if len(hits) != 1 or "0.2.8260" not in lines[hits[0]]:
            sys.exit("VERSION")
        return f"src/melder/__version__.py:{hits[0] + 1}-{hits[0] + 1}"

    def epic(self) -> None:
        note = self.note(self.now, "FACT", [
            f"M1-44 consumed (melder_1, {self.WHEN}): S7",
            "(STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned) landed at 0.2.8260 and is turned in - a",
            "Spellbook's teardown retires its parked versions with the local teardown `cleanup_spell`'s parked branch",
            "runs and cleans the indexes only they hold (`_cleanup_spells`), with the four system documents, the graph",
            "and the running release note, rebuilt last with both checks OK. spellbook.py and spell.py are melder_0's",
            "again (spell.py was not edited); probe T4 (the claim that outlives the Book) stays with S2."],
            [f"context_compass/{self.S7_DONE}:1-9",
             self.line_of(self.BOARD, "| book_teardown_parked | done |"),
             self.version_line()],
            ["S4, S7 and S9 are done; S8 stays on hold (M1-33); S1, S2, S3 and S5 wait for the owner's go, and",
             "spellbook.py, where S1 and S2's fixes sit, is free again."],
            ["Keep this record current; take the owner's go on S1, S2, S3 and S5."], "HELPFUL", 8)
        self.append_notes(self.CORRECTNESS, [note], "epic note")
        text = self.read(self.CORRECTNESS)
        text = self.once(
            text,
            "- [ ] Story: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned - Book teardown leaves\n"
            "  its parked versions and parked-only indexes uncleaned, beyond any cleanup (sweep A7).\n",
            "- [x] Story: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned - Book teardown leaves\n"
            "  its parked versions and parked-only indexes uncleaned, beyond any cleanup (sweep A7). Landed by melder_1\n"
            "  at 0.2.8260: a Spellbook's teardown retires its parked versions and cleans the indexes only they hold;\n"
            "  turned in 2026-10-19 (M1-44), in tickets/stories/completed/; probe T4 stays with S2.\n",
            "s7 box")
        text = self.once(
            text,
            "  shared, active and parked - and re-tested on 0.2.8260: the records stay and break a later notch (S3's notes).\n"
            "\n## Artifact Links",
            "  shared, active and parked - and re-tested on 0.2.8260: the records stay and break a later notch (S3's notes).\n"
            f"- {self.now}: M1-44 - S7 landed at 0.2.8260 and is turned in; spellbook.py and spell.py are melder_0's\n"
            "  again (FACT note).\n\n## Artifact Links",
            "decision log")
        text = self.once(text, "on hold by the owner (M1-33); S7 in progress\n  with melder_1 (M1-43); S3 confirmed",
                         "on hold by the owner (M1-33); S7 done\n  (0.2.8260; M1-44); S3 confirmed", "state")
        text = self.once(
            text,
            "  spell_index.py back (M1-37, M1-38); spellbook.py and spell.py are with melder_1 again for S7 (M1-43,\n"
            "  M0-208); conduit.py,",
            "  spell_index.py back (M1-37, M1-38); spellbook.py and spell.py went to melder_1 for S7 and came back (M1-43,\n"
            "  M1-44); conduit.py,",
            "holders")
        text = self.once(
            text,
            "  it (M0-208; FACT note of 2026-10-19T01:07:36Z).\n",
            "  it (M0-208; FACT note of 2026-10-19T01:07:36Z).\n"
            "- Done since: M1-44 consumed - S7 landed at 0.2.8260 and is turned in; spellbook.py and spell.py are back\n"
            f"  (FACT note of {self.now}).\n",
            "done since")
        text = self.once(
            text,
            "- Next: (1) melder_1 fixes S7 (S4 and S9 landed, M1-38, M1-42), and S8 when the owner lifts its hold (M1-32,\n"
            "  M1-33); (2) S1, S2, S3 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z);\n"
            "  S3 is confirmed and re-tested on 0.2.8260 (its notes), and the order against spellbook.py for S7 is open; (3) each\n",
            "- Next: (1) melder_1 fixes S8 when the owner lifts its hold (M1-32, M1-33); S4, S7 and S9 landed (M1-38, M1-42,\n"
            "  M1-44); (2) S1, S2, S3 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z); S3 is\n"
            "  confirmed and re-tested on 0.2.8260 (its notes), and spellbook.py is free again (M1-44); (3) each\n",
            "next")
        self.stage(self.CORRECTNESS, text)
        self.set_field(self.CORRECTNESS, "Updated")

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        pattern = re.compile(r"- TO: melder_0\n  FROM: melder_1\n  DATETIME: " + re.escape(self.WHEN)
                             + r"\n.*?  ACK_REQUESTED: false\n", re.S)
        found = pattern.findall(text)
        if len(found) != 1 or "M1-44." not in found[0] or found[0].count("- TO:") != 1:
            sys.exit(f"MESSAGE M1-44: {len(found)}")
        text = text.replace(found[0], "")
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        self.stage(self.MAILBOX, text)
        board = self.once(self.read(self.BOARD), f"- NEW MESSAGE for melder_0 (from melder_1, {self.WHEN})\n", "",
                          "alert")
        self.stage(self.BOARD, board)

    def run(self) -> None:
        self.epic()
        self.mailbox()
        print("NOTE", self.note_range(self.CORRECTNESS, f"- DATETIME: {self.now}", "  TYPE: FACT"))


def main() -> None:
    record = ConsumeM144("consume_m1_44")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
