"""melder_0 takes S3 on the owner's go (2026-10-19): the story, the epic, the board row and M0-209.

The owner, in chat: "sure go ahead and fix this [...] at least you can check for active contracts and then cleanup".
S3 moves ready -> in_progress with melder_0; a DECISION note records the go and the order he named (contracts
first, then the disposal); the epic's lines follow; the attention board gets S3's row and detail; melder_1 is told
which files melder_0 writes (M0-209). All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class TakeS3(Record):
    """S3 taken: story, epic, board, mailbox."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    EPIC_C = "tickets/epics/2026-10-17_correctness_defects_epic.md"

    def story(self) -> None:
        """Metadata, transition, the DECISION note, Decision Log and the resume view."""
        text = self.read(self.S3)
        text = self.once(text, "- Status: ready\n", "- Status: in_progress\n", "status")
        text = self.once(text, "- Agent Name: unassigned\n- Agent Role: UNKNOWN\n",
                         "- Agent Name: melder_0\n- Agent Role: synaptic_python_developer\n", "agent")
        text = self.once(
            text,
            "- from_state: draft\n- to_state: ready\n"
            "- transition_reason: the defect is proven on 0.2.8251 by a probe in fresh worlds, GIL off and on (Notes).\n",
            "- from_state: ready\n- to_state: in_progress\n"
            "- transition_reason: the owner's go (chat 2026-10-19); melder_0 takes the fix (DECISION note).\n",
            "transition")
        text = self.once(
            text,
            "  the removal code that exists, no custom rig (DECISION note).\n",
            "  the removal code that exists, no custom rig (DECISION note).\n"
            f"- {self.now}: the owner's go; melder_0 takes the fix - the contracts that hold the version first, then\n"
            "  the disposal (DECISION note).\n",
            "decision log")
        text = self.once(text, "- State: ready, unassigned; confirmed by the owner",
                         "- State: in_progress, melder_0 (the owner's go, 2026-10-19); confirmed by the owner", "state")
        text = self.once(
            text,
            "- Next: (1) the owner's go to take it; (2) patch docs with the exact edits for his approval; (3) the fix, its\n"
            "  tests, docs, notch and the rebuild.",
            "- Next: (1) the open checks - what a borrower's removal reads from the version, grants of a disposed\n"
            "  version, the direct `Spell.cleanup()`; (2) the patch docs with the exact edits; (3) the fix, its tests\n"
            "  (GIL off and on), docs, notch and the rebuild last.",
            "next")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")
        prior = self.note_range(self.S3, "- DATETIME: 2026-10-19T10:41:53Z", "  TYPE: DECISION")
        note = self.note(self.now, "DECISION", [
            "The owner's go (chat 2026-10-19): \"sure go ahead and fix this [...] at least you can check for active",
            "contracts and then cleanup\". melder_0 takes S3. The fix in his order: `Conduit.cleanup_spell` finds the",
            "contracts that hold the version and removes it from them through the removal that exists",
            "(`ConduitWard._emit_index_member_removed` -> `_uncontract_member_spell`, the call `remove_from_spell_index`",
            "makes), then the Book disposes it; when the index goes with it, the destroy as today. The direct",
            "`Spellbook.cleanup_spell` takes the same path through its root conduit once conjured (proposed in the reply",
            "the go answered). Open before the patch: what a borrower's removal reads from the version (the destroy",
            "runs it after the disposal today); a version grant (`add_spell_to_contract`) of a version the lender",
            "disposes; the direct `Spell.cleanup()`."],
            [prior, "src/melder/aether/conduit/conduit.py:6212-6264"],
            ["S3 is in progress with melder_0; the patch gate applies (the cleanup's contract emissions are a",
             "cross-component contract)."],
            ["Read `Spellbook._remove_contracted_spell` and the grant path, probe a disposed version's grant, then",
             "write the patch docs."],
            "REQUIRED", 9)
        self.append_notes(self.S3, [note], "s3 note")

    def epic(self) -> None:
        """The epic's story line, Decision Log, State, Done-since and Next."""
        text = self.read(self.EPIC_C)
        text = self.once(
            text,
            "  its copy and id with index-link borrowers, past their own unlink (sweep A2).\n",
            "  its copy and id with index-link borrowers, past their own unlink (sweep A2). In progress with melder_0 on\n"
            "  the owner's go (2026-10-19).\n",
            "story line")
        text = self.once(
            text,
            "  again (FACT note).\n\n## Artifact Links",
            "  again (FACT note).\n"
            f"- {self.now}: the owner's go for S3 - cleanup_spell removes a version from every contract that holds it,\n"
            "  then disposes it; melder_0 takes it (S3's DECISION note).\n\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "  (0.2.8260; M1-44); S3 confirmed, awaiting the go; S1, S2 and S5 waiting for the owner's word, the\n"
            "  identity epic they waited for (EPIC-2026-10-18-spell_identity_is_the_code) being turned in with its S3-S5\n"
            "  parked (M1-32); S6 done; S10 withdrawn:\n",
            "  (0.2.8260; M1-44); S3 in progress with melder_0 on the owner's go (2026-10-19); S1, S2 and S5 waiting\n"
            "  for the owner's word, the identity epic they waited for (EPIC-2026-10-18-spell_identity_is_the_code)\n"
            "  being turned in with its S3-S5 parked (M1-32); S6 done; S10 withdrawn:\n",
            "state")
        text = self.once(
            text,
            "- Next: (1) melder_1 fixes S8 when the owner lifts its hold",
            f"- Done since: the owner gave S3 its go; melder_0 takes it (S3's DECISION note of {self.now}).\n"
            "- Next: (1) melder_1 fixes S8 when the owner lifts its hold",
            "done since")
        text = self.once(
            text,
            "  M1-44); (2) S1, S2, S3 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z); S3 is\n"
            "  confirmed and re-tested on 0.2.8260 (its notes), and spellbook.py is free again (M1-44); (3) each\n",
            f"  M1-44); (2) S3 is in progress with melder_0 on the owner's go (S3's DECISION note of {self.now});\n"
            "  S1, S2 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z); (3) each\n",
            "next")
        self.stage(self.EPIC_C, text)
        self.set_field(self.EPIC_C, "Updated")

    def board(self) -> None:
        """S3's row and detail; the epic row's next; the alert for M0-209."""
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| correctness_defects \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW correctness_defects: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[6] = "Keep the record current while S3's fix runs on its own row; S8 is melder_1's (M1-33)."
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        row = (f"| parked_cleanup_contracts | in_progress | discovery | claude | melder_0 | none | Close the open checks, "
               f"then write the patch docs for cleanup_spell's contract removal. | cleanup_spell removes a version from "
               f"every contract that holds it, then disposes it; the direct door takes the same path. | The fix lands "
               f"with tests, docs, notch and rebuild, or the owner redirects. | "
               f"tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md | {self.now} | REQUIRED |")
        text = self.once(text, "\n<!-- END USER-DEFINED: active_items -->",
                         "\n" + row + "\n<!-- END USER-DEFINED: active_items -->", "row")
        detail = ("- WORK_ITEM: parked_cleanup_contracts\n"
                  "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
                  "  RESUME_HIERARCHY:\n"
                  "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
                  "    - tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md")
        text = self.once(text, "\n<!-- END USER-DEFINED: active_attention_details -->",
                         "\n" + detail + "\n<!-- END USER-DEFINED: active_attention_details -->", "detail")
        text = self.once(text, "\n<!-- END USER-DEFINED: alerts -->",
                         f"\n- NEW MESSAGE for melder_1 (from melder_0, {self.now})\n<!-- END USER-DEFINED: alerts -->",
                         "alert")
        self.stage(self.BOARD, text)

    def mailbox(self) -> None:
        """M0-209 to melder_1."""
        text = self.read(self.MAILBOX)
        message = (
            "- TO: melder_1\n"
            "  FROM: melder_0\n"
            f"  DATETIME: {self.now}\n"
            "  TYPE: NOTICE\n"
            "  CLAIM: M0-209. The owner gave S3 its go (chat 2026-10-19); melder_0 takes\n"
            "    STORY-2026-10-17-parked_cleanup_leaves_borrower_copies: `Conduit.cleanup_spell` removes the version from\n"
            "    every contract that holds it, through the member removal that exists, before the Book disposes it, and\n"
            "    the direct `Spellbook.cleanup_spell` takes the same path. melder_0 writes conduit.py, spellbook.py and,\n"
            "    if the patch needs it, conduit_ward.py (all three with melder_0 already) and takes one notch above\n"
            "    0.2.8260 at landing - notch above it if you land after. Tell melder_0 before editing them.\n"
            "  EVIDENCE: context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md\n"
            "  ACK_REQUESTED: false")
        text = self.once(text, "\n<!-- END USER-DEFINED: messages -->",
                         "\n" + message + "\n<!-- END USER-DEFINED: messages -->", "message")
        self.stage(self.MAILBOX, text)


def main() -> None:
    record = TakeS3("take_s3_20261019")
    record.story()
    record.epic()
    record.board()
    record.mailbox()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
