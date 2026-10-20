"""Record the owner's root-cause call on S3 (melder_0, 2026-10-19): cleaning up a spell must update the contracts.

The owner, in chat: cleaning up a spell should update the contracts; no custom rig - the cleanup goes through the
contract-removal code that exists; the active member of a multi-member index is notched away first. One DECISION
note with the source facts, the open question marked answered in part, a Decision Log line, the resume view's State
and Updated. All-or-nothing; `--write` flushes.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class RootCause(Record):
    """S3's DECISION note and lines."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"

    def run(self) -> None:
        """Stage the note and the lines."""
        text = self.read(self.S3)
        text = self.once(
            text,
            "  `Spellbook.bind_inactive`.\n- (2026-10-19) Asked of the owner",
            "  `Spellbook.bind_inactive`.\n"
            "  Answered in part (owner, 2026-10-19): cleaning up a spell updates the contracts (DECISION note);\n"
            "  routing the direct door through the conduit once conjured is proposed in the patch docs for his approval.\n"
            "- (2026-10-19) Asked of the owner",
            "open question")
        text = self.once(
            text,
            "  active and parked; re-tested on 0.2.8260, GIL off and on (MEASURE and DECISION notes).\n",
            "  active and parked; re-tested on 0.2.8260, GIL off and on (MEASURE and DECISION notes).\n"
            f"- {self.now}: the owner named the root cause - cleaning up a spell must update the contracts, through\n"
            "  the removal code that exists, no custom rig (DECISION note).\n",
            "decision log")
        text = self.once(
            text,
            "(MEASURE note). The fix sits in conduit.py and conduit_ward.py;\n"
            "  whether spellbook.py too (with melder_1 for S7) is for the patch.",
            "(MEASURE note). The fix uses the removal code that\n"
            f"  exists (DECISION note of {self.now}): conduit.py and spellbook.py, both melder_0's again (M1-44).",
            "state")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")
        measure = self.note_range(self.S3, "- DATETIME: 2026-10-19T10:17:01Z", "  TYPE: MEASURE")
        note = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19): \"cleaning up a spell should update the [...] contracts [...] isn't that",
            "the issue?\" - yes, it is the root cause; \"you better not [...] custom rig this [...], if you cleanup a",
            "spell you just remove the spell from the contract\"; \"the code exists for all this [...] the cleanup",
            "should go to conduit.remove spell from contract or whatever and properly do it, or if its one of many",
            "in the index you want to make sure you notch it and remove the spell\"; \"generally you wouldn't",
            "randomly cleanup some [...] object on an index\". Read in source: `Conduit.cleanup_spell` tells",
            "borrowers only when the index dies (`_emit_index_destroy`); `remove_from_spell_index` tells them after",
            "its move with `ConduitWard._emit_index_member_removed`, whose `_uncontract_member_spell` drops the",
            "member detail, the borrower's entry and its borrowed id, and whose docstring already lists",
            "`Conduit.cleanup_spell` as a caller. `_dispose_spell` reads the index id under the Book lock and hands",
            "it back only when the index went. `remove_spell_from_contract` cannot serve: it is the borrower's verb,",
            "needs a link transaction and refuses an index-link member. The active member of a multi-member index",
            "is already refused with the notch-first remedy (0.2.8256). The direct `Spellbook.cleanup_spell` emits",
            "nothing, not even the destroy."],
            ["src/melder/aether/conduit/conduit.py:6122-6210",
             "src/melder/aether/conduit/conduit.py:6212-6264",
             "src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517",
             "src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589",
             "src/melder/aether/conduit/conduit_ward/conduit_ward.py:3209-3251",
             "src/melder/aether/spellbook/spellbook.py:4481-4546",
             "src/melder/aether/spellbook/spellbook.py:4548-4690",
             measure],
            ["The fix is code that exists: `cleanup_spell` sends the member removal `remove_from_spell_index` sends",
             "when the index survives. With that, `remove_index_from_contract` already takes every version the index",
             "holds, active and parked (probe U1), so the unlink needs no change."],
            ["The owner's go to take S3; then the patch docs with the exact edits - the surviving index id out of",
             "`_dispose_spell`, the emission in `cleanup_spell`, the direct door routed through the conduit once",
             "conjured - for his approval."],
            "REQUIRED", 9)
        self.append_notes(self.S3, [note], "s3 note")
        print("NOTE", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: DECISION"))


def main() -> None:
    record = RootCause("record_s3_root_cause_20261019")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
