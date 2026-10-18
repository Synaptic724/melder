"""Consume M1-38 (melder_1, 2026-10-18T17:07:19Z): S9 landed as 0.2.8256 with the refusal; spellbook.py and spell.py
are back. One all-or-nothing pass over the mailbox, the attention board, the artifact board, the correctness epic,
the identity epic and its S1/S2 stories (melder_0, 2026-10-18)."""
import sys
from typing import List

from cc_record import Record


class ConsumeM138(Record):
    CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    FAMILY = Record.FAMILY + (CORRECTNESS,)
    SESSION_NOTES = Record.SESSION_NOTES + ("2026-10-18T15:15:34Z",)
    S9_DONE = ("tickets/stories/completed/"
               "2026-10-17_direct_cleanup_of_active_member_orphans_parked_versions_story.md")

    def mailbox(self) -> None:
        text = self.read(self.MAILBOX)
        lines = text.split("\n")
        starts = [i for i in range(len(lines) - 2)
                  if lines[i] == "- TO: melder_0" and lines[i + 1] == "  FROM: melder_1"
                  and lines[i + 2] == "  DATETIME: 2026-10-18T17:07:19Z"]
        if len(starts) != 1:
            sys.exit(f"M1-38 block: {len(starts)}")
        end = starts[0]
        while lines[end] != "  ACK_REQUESTED: false":
            end += 1
        if "M1-38." not in "\n".join(lines[starts[0]:end + 1]):
            sys.exit("M1-38 block does not carry M1-38")
        del lines[starts[0]:end + 1]
        text = "\n".join(lines)
        text = self.once(text, "| melder_0 | claude | 2026-09-26T22:24:06Z | 2026-10-18T16:45:29Z | active |",
                         f"| melder_0 | claude | 2026-09-26T22:24:06Z | {self.now} | active |", "roster")
        self.stage(self.MAILBOX, text)

    def board(self) -> None:
        text = self.read(self.BOARD)
        text = self.once(text, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T17:07:19Z)\n", "", "alert")
        rows = [
            ("| Keep the record current as melder_1 fixes S9, then S4 and S7; S8 waits for the owner (M1-33). |",
             "| Keep the record current as melder_1 fixes S4, then S7; S8 waits for the owner (M1-33). |",
             "2026-10-18T14:14:10Z"),
            ("| S1 and S2 built in a /tmp working mirror until S9 (0.2.8256) hands back spell.py and spellbook.py; "
             "then the landing pass. |",
             "| S1 and S2 finished in the /tmp working mirror (S9 landed as 0.2.8256; spell.py and spellbook.py are "
             "back, M1-38); then the landing pass. |", "2026-10-18T16:32:46Z"),
            ("| S1 built in a /tmp working mirror; the landing with S2 after S9 (0.2.8256). |",
             "| S1 finished in the /tmp working mirror; then the landing with S2 (S9 landed as 0.2.8256). |",
             "2026-10-18T16:32:46Z"),
            ("| S2 (the manifest, the cache keys, the crystal's record) built with S1 in the /tmp mirror; the landing "
             "after S9. |",
             "| S2 (the manifest, the cache keys, the crystal's record) finished with S1 in the /tmp mirror; then the "
             "landing (S9 landed as 0.2.8256). |", "2026-10-18T16:32:46Z"),
        ]
        lines = text.split("\n")
        for old, new, stamp in rows:
            hits = [i for i, line in enumerate(lines) if old in line]
            if len(hits) != 1:
                sys.exit(f"ROW {old[:40]}: {len(hits)}")
            row = lines[hits[0]].replace(old, new)
            if row.count(f"| {stamp} |") != 1:
                sys.exit(f"ROW STAMP {stamp}")
            lines[hits[0]] = row.replace(f"| {stamp} |", f"| {self.now} |")
        self.stage(self.BOARD, "\n".join(lines))

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        old = ("cc_record.py (the shared record helper) and record_s1_s2_mirror_build.py (the digest and the manifest "
               "recorded); probes/, runs/, blast_radius/ and staged/ are rowed under S1. | 2026-10-18T17:05:55Z |")
        new = ("cc_record.py (the shared record helper), record_s1_s2_mirror_build.py (the digest and the manifest "
               "recorded) and reflow_long_blocks.py (long note lines re-wrapped); apply_common.py, edits_spell.py, "
               "edits_bind.py and apply_s1_s2.py (the all-or-nothing applier and S1 and S2's edit lists); "
               "consume_m1_38.py (M1-38 consumed); probes/, runs/, blast_radius/ and staged/ are rowed under S1. | "
               f"{self.now} |")
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines) if old in line]
        if len(hits) != 1 or not lines[hits[0]].startswith("| "):
            sys.exit(f"scripts row: {len(hits)}")
        lines[hits[0]] = lines[hits[0]].replace(old, new)
        self.stage(self.ARTIFACTS, "\n".join(lines))

    def correctness(self) -> None:
        rel = self.CORRECTNESS
        text = self.read(rel)
        text = self.once(text, (
            "- [ ] Story: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions - a direct cleanup\n"
            "  of an index's active member leaves its parked versions on a cleaned index (sweep A10). melder_1 is fixing it\n"
            "  on the owner's rule of 2026-10-18 (M1-35): the cleaned active version leaves its index with nothing active and\n"
            "  `cleanup_spell`'s refusal goes (patch direct_cleanup_refusal_2026_10_18, being rewritten; M1-33); S4 and S7\n"
            "  follow with melder_1, one at a time (M1-32).\n"), (
            "- [x] Story: STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions - a direct cleanup\n"
            "  of an index's active member leaves its parked versions on a cleaned index (sweep A10). Landed by melder_1\n"
            "  at 0.2.8256 with the refusal the owner chose (M1-37): all three cleanup calls refuse the active member of\n"
            "  an index that holds parked versions, naming the remedies; turned in 2026-10-18 (M1-38), in\n"
            "  tickets/stories/completed/. S4 and S7 follow with melder_1, one at a time (M1-32).\n"), "S9 entry")
        text = self.once(text, (
            "  melder_1 holds spell_index.py too, released by M0-197 (FACT note).\n\n## Artifact Links (Optional)\n"), (
            "  melder_1 holds spell_index.py too, released by M0-197 (FACT note).\n"
            f"- {self.now}: M1-38 - S9 landed at 0.2.8256 with the refusal the owner chose (M1-37) and is turned in;\n"
            "  the hole rule of the 15:15:34Z entry did not land (FACT note).\n\n## Artifact Links (Optional)\n"),
            "decision log")
        text = self.once(text, (
            "- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 in_progress with melder_1\n"
            "  (M1-33); S8 blocked, on hold by the owner (M1-33); S4 and S7 next with melder_1; S3 waiting for its open\n"),
            ("- State: in_progress (melder_0), handoff. A1-A12 are done; ten stories filed - S9 done (0.2.8256, the\n"
             "  refusal; M1-38); S8 blocked, on hold by the owner (M1-33); S4 next with melder_1, then S7; S3 waiting for its open\n"),
            "state")
        text = self.once(text,
                         "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (p2) and\n",
                         "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions (p2; done: landed at 0.2.8256\n"
                         "  with the refusal, turned in 2026-10-18) and\n", "state S9")
        text = self.once(text, (
            "  The owner's order is parallel (M1-30, M1-32): melder_1 holds spellbook.py, spell.py and spell_index.py for S9\n"
            "  until it lands (M1-33, M0-195, M1-35, M0-197); conduit.py, spellbook_validation_error.py and\n"
            "  change_control_manager.py are back with melder_0 while S8 is on hold; each lane claims a file from the other by\n"
            "  mailbox before editing it.\n"), (
            "  The owner's order is parallel (M1-30, M1-32): S9 landed and melder_1 handed spellbook.py, spell.py and\n"
            "  spell_index.py back (M1-37, M1-38); conduit.py, spellbook_validation_error.py and change_control_manager.py\n"
            "  are with melder_0 while S8 is on hold; each lane claims a file from the other by mailbox before editing it.\n"),
            "state files")
        text = self.once(text, (
            "- Next: (1) melder_1 fixes S9, then S4 and S7, one at a time, and S8 when the owner lifts its hold (M1-32,\n"
            "  M1-33);"), (
            f"- Done since: M1-38 consumed - S9 landed at 0.2.8256 with the refusal (FACT note of {self.now}).\n"
            "- Next: (1) melder_1 fixes S4, then S7, one at a time (S9 landed, M1-38), and S8 when the owner lifts its\n"
            "  hold (M1-32, M1-33);"), "next")
        self.stage(rel, text)
        self.set_field(rel, "Updated")
        note = self.note(self.now, "FACT", [
            "M1-38 from melder_1 (2026-10-18T17:07:19Z, NOTICE), consumed. S9",
            "(STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions) landed at 0.2.8256 and is turned",
            "in, rebuilt last with both checks OK. It took the refusal, the owner's choice once he reopened the rule",
            "(M1-36, M1-37): `cleanup_spell`, `Spellbook.cleanup_and_remove_spell` and a direct `Spell.cleanup()` refuse",
            "the active version of an index that holds parked versions, change nothing and name the remedies (notch to a",
            "parked version first, dispose the parked versions, or move them out); Book teardown is unaffected. The hole",
            "rule this epic's FACT note of 2026-10-18T15:15:34Z records (M1-35) did not land: sweep A10's \"refused by",
            "design\" stands, now on all three calls. melder_1 takes S4 next; spellbook.py, spell.py and spell_index.py",
            "are melder_0's again."], [
            f"context_compass/{self.S9_DONE}:1-9",
            "src/melder/aether/spellbook/spellbook.py:602-781",
            "context_compass/system_docs/src_architecture.md:1126-1152"], [
            "S9 is done; the defects left with melder_1 are S4 and S7 (S8 on hold); the record of sweep A10 reads with",
            "this note, not the 15:15:34Z one."], [
            "Keep this record current as melder_1 lands S4."], "REQUIRED", 8)
        self.append_notes(rel, [note], "correctness note")
        # The 15:15:34Z note cites sweep A10's MEASURE note at 665-694, stale before this pass (the note stood
        # at 670-699): point it at where the note stands now.
        a10 = self.note_range(rel, "- DATETIME: 2026-10-17T21:36:36Z", "  TYPE: MEASURE")
        text = self.read(rel)
        self.stage(rel, self.once(text, "context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:665-694",
                                  a10, "A10 citation"))
        print("A10 citation ->", a10)

    def identity(self) -> None:
        rel = self.EPIC
        text = self.read(rel)
        text = self.once(text, (
            "  melder_0 writes the files these stories touch and announces each landing by mailbox (M0-193); since M1-33\n"
            "  melder_1 holds spellbook.py, spell.py and spell_index.py for\n"
            "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions until it lands (released, M0-195 and\n"
            "  M0-197; S8 is on hold), and melder_0 claims a file back by message before editing it.\n"), (
            "  melder_0 writes the files these stories touch and announces each landing by mailbox (M0-193); melder_1\n"
            "  held spellbook.py, spell.py and spell_index.py for\n"
            "  STORY-2026-10-17-direct_cleanup_of_active_member_orphans_parked_versions until it landed as 0.2.8256 and\n"
            "  handed them back (M1-37, M1-38); each lane claims a file from the other by message before editing it.\n"),
            "dependencies")
        text = self.once(text, (
            "  melder_0 writes the files these stories touch and says so by mailbox before each landing (M0-193). Since M1-33\n"
            "  S8 is on hold and melder_1 holds spellbook.py, spell.py and spell_index.py for S9 of\n"
            "  EPIC-2026-10-17-correctness_defects until it lands (M1-34, M0-195, M1-35, M0-197); conduit.py,\n"
            "  spellbook_validation_error.py and change_control_manager.py are free. The next notch is above 0.2.8255, or\n"
            "  above S9's if it lands first.\n"), (
            "  melder_0 writes the files these stories touch and says so by mailbox before each landing (M0-193). S8 is\n"
            "  on hold (M1-33); S9 of EPIC-2026-10-17-correctness_defects landed as 0.2.8256 and melder_1 handed\n"
            "  spellbook.py, spell.py and spell_index.py back (M1-37, M1-38); conduit.py, spellbook_validation_error.py\n"
            "  and change_control_manager.py are free. The next notches are above 0.2.8256: S1's, then S2's, each with\n"
            "  its release-note entry.\n"), "constraints")
        text = self.once(text, (
            "  moving (DECISION note).\n\n## Artifact Links (Optional)\n"), (
            "  moving (DECISION note).\n"
            f"- {self.now}: M1-38 consumed - S9 landed as 0.2.8256 with the refusal; spellbook.py and spell.py are back\n"
            "  (FACT note).\n\n## Artifact Links (Optional)\n"), "identity decision log")
        text = self.once(text, (
            "  S9 of EPIC-2026-10-17-correctness_defects takes the refusal and lands first as 0.2.8256 (M1-37;\n"
            "  melder_1's DECISION note of 2026-10-18T16:02:48Z); melder_1 hands spellbook.py and spell.py back by\n"
            "  message after its rebuild, and S1 and S2 notch above it; spell_index.py and conduit.py are melder_0's.\n"), (
            "  S9 of EPIC-2026-10-17-correctness_defects took the refusal and landed first as 0.2.8256 (M1-37, M1-38);\n"
            "  spellbook.py, spell.py, spell_index.py and conduit.py are melder_0's, and S1 and S2 notch above 0.2.8256.\n"),
            "identity state")
        text = self.once(text, (
            "- Next: (1) S1 and S2 built in a /tmp working mirror while S9 lands; (2) the landing pass - red tests, src,\n"), (
            f"- Done since: M1-38 consumed - S9 landed as 0.2.8256; spellbook.py and spell.py are back (FACT note of\n"
            f"  {self.now}).\n"
            "- Next: (1) S1 and S2 finished in the /tmp working mirror (profiles, cache keys, record, statements); (2) the\n"
            "  landing pass - red tests, src,\n"), "identity next")
        self.stage(rel, text)
        self.set_field(rel, "Updated")
        note = self.note(self.now, "FACT", [
            "M1-38 from melder_1 (2026-10-18T17:07:19Z, NOTICE), consumed. S9 of EPIC-2026-10-17-correctness_defects",
            "landed at 0.2.8256 and is turned in, rebuilt last with both checks OK; spellbook.py and spell.py are",
            "melder_0's again, as spell_index.py and conduit.py already were (M1-37). S9's src edits were its E1-E7 in",
            "those two files and the notch: `cleanup_and_remove_spell`'s refusal and docstring, `_dispose_spell`'s",
            "refusal text and `cleanup_spell`'s docstring, and `Spell.cleanup`'s Raises entry - none of S1's or S2's",
            "edit sites; the mirror's spell.py and spellbook.py are byte-identical to the repository's (diff -rq), so",
            "edits_spell.py's check run holds for the repository. Outside src the landing re-reads what S9 changed: the",
            "four system documents and their indexes, the spellbook.json and spell.json graph descriptors (accepted)",
            "and the graph, and the running release note (header 0.2.8256, a new section, the packaging lines). The",
            "next notches are above 0.2.8256."], [
            f"context_compass/{ConsumeM138.S9_DONE}:1-9",
            "src/melder/__version__.py:12-12",
            "src/melder/aether/spellbook/spellbook.py:602-781",
            "release_docs/next_version_release.md:1-3"], [
            "S1 and S2's spell.py and spellbook.py edits go into the repository at the landing; the mirror moves to",
            "0.2.8256 (its __version__, build assets and release note) before the apply."], [
            "Sync the mirror to 0.2.8256; then edits_profiles.py."], "REQUIRED", 8)
        self.append_notes(rel, [note], "identity note")

    def stories(self) -> None:
        text = self.read(self.S1)
        text = self.once(text, (
            "  note of 2026-10-18T15:01:53Z); the patches are updated for B and strict uniqueness before the code. spellbook.py\n"
            "  and spell.py are melder_1's for S9 and asked for (M0-196); their order waits for the owner's pick in S9\n"
            "  (M1-36, M1-37).\n"), (
            "  note of 2026-10-18T15:01:53Z); the patches are updated for B and strict uniqueness before the code. S9\n"
            "  landed as 0.2.8256 and spellbook.py and spell.py are back (M1-38; the epic's FACT note of\n"
            f"  {self.now}).\n"), "S1 state")
        text = self.once(text, (
            "- Next: S1 built in a /tmp working mirror; the landing pass with S2 once melder_1 hands back spell.py and\n"
            "  spellbook.py after S9 (0.2.8256; M1-37).\n"), (
            "- Next: S1 finished in the /tmp working mirror (the profiles, the statements); then the landing pass with S2,\n"
            "  notched above 0.2.8256.\n"), "S1 next")
        self.stage(self.S1, text)
        self.set_field(self.S1, "Updated")
        text = self.read(self.S2)
        text = self.once(text,
                         "  2026-10-18T16:18:35Z); spell.py comes back from melder_1 after S9 lands as 0.2.8256 (M1-37).\n",
                         "  2026-10-18T16:18:35Z); spell.py is back since S9 landed as 0.2.8256 (M1-38).\n", "S2 state")
        text = self.once(text,
                         "- Next: S2 built with S1 in a /tmp working mirror; the landing pass once spell.py is back.\n",
                         "- Next: S2 finished with S1 in the /tmp working mirror (the cache keys, the crystal's record); then\n"
                         "  the landing pass.\n", "S2 next")
        self.stage(self.S2, text)
        self.set_field(self.S2, "Updated")


def main() -> None:
    record = ConsumeM138("m1_38")
    record.mailbox()
    record.board()
    record.artifacts()
    record.correctness()
    record.identity()
    record.stories()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
