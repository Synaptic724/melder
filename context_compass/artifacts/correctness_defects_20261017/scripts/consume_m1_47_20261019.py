"""melder_0's first pass after the second 2026-10-19 re-onboarding: M1-47 consumed into the epic.

melder_1's NOTICE M1-47 (2026-10-19T12:13:51Z): S8 is green on the mirror and waits only for melder_0's hand-over of
spellbook.py and conduit.py when S3 lands; melder_1 filed STORY-2026-10-19-notch_back_keeps_outgoing_dependencies
under the epic and asks for it to be listed in the epic's Stories. The epic gets a FACT note, the story line, a
Decision Log entry and its resume view brought up to date; the board loses the alert and the epic row's
`updated_at` moves; the mailbox loses M1-47 and refreshes melder_0's last_checked. No ACK (ACK_REQUESTED: false).
All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class ConsumeM147(Record):
    """The epic, the board and the mailbox."""

    EPIC_C = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S8 = "tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md"
    S11 = "tickets/stories/2026-10-19_notch_back_keeps_outgoing_dependencies_story.md"
    RUNS = "artifacts/failed_notch_refusal_20261018/runs"
    M147 = "2026-10-19T12:13:51Z"

    def run_range(self, name: str) -> str:
        count = len((self.ROOT / self.RUNS / name).read_text(encoding="utf-8").splitlines())
        return f"context_compass/{self.RUNS}/{name}:1-{count}"

    def epic(self) -> None:
        note = self.note(self.now, "FACT", [
            f"M1-47 consumed (melder_1, {self.M147}). S8 is green on the mirror - its 25 tests and the whole tree",
            "with the GIL off and on, and its probes show the refusal with nothing moved - and waits only for",
            "melder_0's NOTICE handing over spellbook.py and conduit.py when S3 lands; it then applies all five of its",
            "files in one pass, notches above 0.2.8261 and rebuilds for both. melder_1 filed",
            "STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (S11; ready, unassigned, p2) under this epic from",
            "S8's HYPOTHESIS note: `Spellbook._apply_notch` never writes the lineage's dependencies and a notch to a",
            "version compiled before runs no Phase 3, so after a notch back the lineage keeps the outgoing version's",
            "dependencies; a borrower's consumer that melds first is refused by the visibility check and its verdict",
            "stays `invalid` (probe H3, H4 on 0.2.8260, the GIL off and on). S11 is listed in the Stories."],
            [self.whole(self.S11),
             self.note_range(self.S8, "- DATETIME: 2026-10-19T11:59:46Z", "  TYPE: MEASURE"),
             self.note_range(self.S8, "- DATETIME: 2026-10-19T12:04:23Z", "  TYPE: MEASURE"),
             self.run_range("probe_notch_back_lineage_dependencies_0_2_8260_gil0.txt"),
             self.run_range("probe_notch_back_lineage_dependencies_0_2_8260_gil1.txt")],
            ["Eleven stories: S11 waits for the owner's scheduling and assignment; S8's landing waits for S3 and",
             "M0-211."],
            ["Land S3 (the release note, the notch 0.2.8261), then M0-211 hands spellbook.py and conduit.py to",
             "melder_1."], "REQUIRED", 8)
        self.append_notes(self.EPIC_C, [note], "epic note")
        text = self.read(self.EPIC_C)
        text = self.once(
            text,
            "  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12). Withdrawn on\n"
            "  the owner's ruling (2026-10-17): not a defect; in tickets/stories/completed/.\n\n## Tasks",
            "  remove_from_spell_index mints selects its parked version, so a graft activates it (sweep A12). Withdrawn on\n"
            "  the owner's ruling (2026-10-17): not a defect; in tickets/stories/completed/.\n"
            "- [ ] Story: STORY-2026-10-19-notch_back_keeps_outgoing_dependencies - a notch back to a version compiled\n"
            "  before leaves the outgoing version's dependencies on the lineage, so a borrower's consumer that melds first\n"
            "  is refused for good (S11; filed by melder_1 from S8's HYPOTHESIS note, 2026-10-19; ready, unassigned;\n"
            "  M1-47).\n\n## Tasks",
            "story line")
        text = self.once(
            text,
            "  time; S3 stays with melder_0, which hands spellbook.py and conduit.py to melder_1 when S3 lands (FACT\n"
            "  note).\n\n## Artifact Links",
            "  time; S3 stays with melder_0, which hands spellbook.py and conduit.py to melder_1 when S3 lands (FACT\n"
            "  note).\n"
            f"- {self.now}: M1-47 - S8 green on the mirror, waiting for S3's hand-over; melder_1 filed\n"
            "  STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (S11; ready, unassigned, p2) under this epic (FACT\n"
            "  note).\n\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 done (0.2.8256, the\n",
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed from the sweep and an eleventh\n"
            "  by melder_1 (S11, M1-47) - S9 done (0.2.8256, the\n",
            "state count")
        text = self.once(
            text,
            "  with the refusal, turned in 2026-10-18) and\n"
            "  STORY-2026-10-17-minted_index_selects_its_parked_version (p3; withdrawn: not a defect, owner 2026-10-17).\n",
            "  with the refusal, turned in 2026-10-18),\n"
            "  STORY-2026-10-17-minted_index_selects_its_parked_version (p3; withdrawn: not a defect, owner 2026-10-17)\n"
            "  and STORY-2026-10-19-notch_back_keeps_outgoing_dependencies (S11, p2; ready, unassigned; filed by\n"
            "  melder_1, M1-47).\n",
            "state list")
        text = self.once(
            text,
            "- Next: (1) melder_0 lands S3 (the notch 0.2.8261, no rebuild on the owner's word) and hands spellbook.py and\n"
            "  conduit.py to melder_1; (2) melder_1 lands S8 on top, rebuilding for both, then S1, S2 and S5 one at a\n"
            "  time (M1-45); S4, S7 and S9 landed (M1-38, M1-42, M1-44); (3) each fix with the patch gate, its notch\n"
            "  and its rebuild; (4) a fourth tranche on the owner's word.\n",
            "- Done since: M1-47 consumed - S8 green on the mirror, waiting for S3's hand-over; S11 filed by melder_1 and\n"
            f"  listed (FACT note of {self.now}).\n"
            "- Next: (1) melder_0 lands S3 (the notch 0.2.8261, no rebuild on the owner's word) and hands spellbook.py and\n"
            "  conduit.py to melder_1; (2) melder_1 lands S8 on top, rebuilding for both, then S1, S2 and S5 one at a\n"
            "  time (M1-45); S4, S7 and S9 landed (M1-38, M1-42, M1-44); (3) S11 on the owner's scheduling; (4) each\n"
            "  fix with the patch gate, its notch and its rebuild; (5) a fourth tranche on the owner's word.\n",
            "next")
        self.stage(self.EPIC_C, text)
        self.set_field(self.EPIC_C, "Updated")

    def board(self) -> None:
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| correctness_defects \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW correctness_defects: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[6] = ("Keep the record current; S3 runs on its own row, S8 then S1, S2 and S5 with melder_1 (M1-45); "
                    "S11 waits for the owner (M1-47).")
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        text = self.once(text, f"- NEW MESSAGE for melder_0 (from melder_1, {self.M147})\n", "", "alert m1-47")
        self.stage(self.BOARD, text)

    def drop_message(self, text: str, when: str, msg_id: str, ack: str) -> str:
        pattern = re.compile(r"- TO: melder_0\n  FROM: melder_1\n  DATETIME: " + re.escape(when)
                             + r"\n.*?  ACK_REQUESTED: " + ack + r"\n", re.S)
        found = pattern.findall(text)
        if len(found) != 1 or f"CLAIM: {msg_id}" not in found[0] or found[0].count("- TO:") != 1:
            sys.exit(f"MESSAGE {msg_id}: {len(found)}")
        return text.replace(found[0], "")

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        text = self.drop_message(text, self.M147, "M1-47", "false")
        rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW melder_0: {len(rows)}")
        text = text.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |")
        self.stage(self.MAILBOX, text)

    def run(self) -> None:
        self.epic()
        self.board()
        self.mailbox()
        print("EPIC FACT", self.note_range(self.EPIC_C, f"- DATETIME: {self.now}", "  TYPE: FACT"))


def main() -> None:
    record = ConsumeM147("consume_m1_47")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
