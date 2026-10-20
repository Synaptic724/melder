"""Record the owner's direction of 2026-10-19 on EPIC-2026-10-17-correctness_defects and S3's wording (melder_0).

The owner, asked whether to turn the epic in: "no finish them if your close to finishing them what open questions
do you have?"; on S3: a spell cannot have a copy, and "cleaning up the spell object has nothing to do with the
things it created ... only when we cleanup the scope do we clear objects they made". The epic gets a DECISION note
(no turn-in; none of S1, S2, S3, S5 is close; the open questions asked), its Decision Log line and its Next; S3 gets
a FACT note saying what its "copy" is (the borrowing Book's contract entry, read in source) and the question asked.
All-or-nothing; `--write` flushes; without it the pass only checks.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class OwnerDirection(Record):
    """The epic's DECISION note and S3's FACT note."""

    CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S1 = "tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md"
    S2 = "tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    S5 = "tickets/stories/2026-10-17_restore_drops_separated_parked_version_story.md"
    RUN = "artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil0.txt"

    def method(self, rel: str, cls_name: str, name: str) -> str:
        tree = ast.parse((self.REPO / rel).read_text(encoding="utf-8"))
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name]
        hits = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name == name] if classes else []
        if len(hits) != 1:
            sys.exit(f"METHOD {cls_name}.{name}: {len(hits)}")
        return f"{rel}:{hits[0].lineno}-{hits[0].end_lineno}"

    def p2_range(self) -> str:
        lines = self.read(self.RUN).rstrip("\n").split("\n")
        starts = [i for i, line in enumerate(lines) if line.startswith("P2 ")]
        if len(starts) != 1:
            sys.exit("P2")
        return f"context_compass/{self.RUN}:{starts[0] + 1}-{len(lines)}"

    def s3(self) -> None:
        book = "src/melder/aether/spellbook/spellbook.py"
        evidence = [self.method(book, "Spellbook", "_add_contracted_spell"),
                    self.method(book, "Spellbook", "_add_inactive_contracted_spell"),
                    self.method("src/melder/aether/conduit/conduit.py", "Conduit", "cleanup_spell"),
                    self.p2_range()]
        note = self.note(self.now, "FACT", [
            "\"Copy\" in this story is the borrowing Spellbook's contract entry - not a second spell and not an",
            "object the spell built. `Spellbook._add_contracted_spell` files the lender's own Spell object by",
            "reference (`spell_map[spell_index] = spell`) with its key and adds the index's member ids to the",
            "borrowed ids; `_add_inactive_contracted_spell` files a parked version the same way in the parked map.",
            "The finding is that entry and id staying in the borrowing Book after the lender's `cleanup_spell` of",
            "the version, the entry pointing at the cleaned Spell, past the borrower's own unlink (probe P2). No",
            "object is involved: the owner's rule (chat 2026-10-19) is that cleaning up a spell never disposes what",
            "it built - \"only when we cleanup the scope do we clear objects they made\". The owner was asked",
            "whether such a leftover entry is a defect, and if so whether a direct `Spellbook.cleanup_spell` must",
            "clear it too."],
            evidence,
            ["The story's wording read as a duplicated spell or as objects; it is Melder's own record in the",
             "borrowing Book."],
            ["Record the owner's answers here; re-scope or withdraw the story by them."], "REQUIRED", 8)
        self.append_notes(self.S3, [note], "s3 note")
        text = self.read(self.S3)
        old = "  `Spellbook.bind_inactive`.\n\n## Decision Log\n"
        new = ("  `Spellbook.bind_inactive`.\n"
               "- (2026-10-19) Asked of the owner after his correction that no copy or object is involved: is a\n"
               "  borrowing Book's contract entry left pointing at a version the lender cleaned up a defect at all? If\n"
               "  yes, the question above stands (FACT note).\n\n## Decision Log\n")
        text = self.once(text, old, new, "s3 open question")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def epic(self) -> None:
        evidence = [self.doc_section(self.S3, "## Open Questions"),
                    self.doc_section(self.S1, "## Context / Handoff Summary"),
                    self.doc_section(self.S2, "## Context / Handoff Summary"),
                    self.doc_section(self.S5, "## Context / Handoff Summary"),
                    self.doc_section("system_docs/src_architecture.md",
                                     "### Runtime Model: Structure Is the Contract")]
        note = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19), asked how to turn the epic in: \"no finish them if your close to finishing",
            "them what open questions do you have?\" - the epic stays open and melder_0 finishes the stories it can.",
            "melder_0 answered that none of S1, S2, S3 or S5 is close - each a defect proven on 0.2.8251 with a",
            "reproducer and no fix written; the probe re-run on 0.2.8259, patch docs, the owner's go, the fix with",
            "tests, docs, a notch and the rebuild remain - and asked: S3, is a borrowing Book's contract entry left",
            "pointing at a cleaned-up version a defect, and must a direct `Spellbook.cleanup_spell` clear it too;",
            "S1 and S2, whose fixes sit in spellbook.py (with melder_1 for S7, M0-208), after S7 or first; which",
            "stories melder_0 takes and in what order (S3 and S5 can start now). The owner's rules, stated with it:",
            "cleaning up a spell never disposes the objects it built - only a scope's cleanup does - and \"the",
            "creations the spell creates are decoupled from the spell that makes it\": after an ownership transfer",
            "the objects created before are not the spell's, the Creations responsible for them having changed (the",
            "Runtime Model of src_architecture says the same)."],
            evidence,
            ["No turn-in; the four stories wait for the owner's answers, then go to melder_0 one at a time with",
             "the patch gate."],
            ["Take the owner's answers; then re-run the first story's probe on 0.2.8259."], "REQUIRED", 8)
        self.append_notes(self.CORRECTNESS, [note], "epic note")
        text = self.read(self.CORRECTNESS)
        text = self.once(
            text,
            "  (M0-208; FACT note).\n\n## Artifact Links",
            "  (M0-208; FACT note).\n"
            f"- {self.now}: the owner kept the epic open - melder_0 finishes the stories it is close to; none is\n"
            "  close, so its open questions went to the owner (DECISION note).\n\n## Artifact Links",
            "decision log")
        text = self.once(
            text,
            "M1-33); (2) S3 after the owner answers its open question; S1, S2 and S5 on the owner's word, the identity\n"
            "  epic they waited for being turned in; (3) each fix",
            "M1-33); (2) S1, S2, S3 and S5 go to melder_0 once the owner answers its open questions (DECISION note of\n"
            f"  {self.now}): S3's defect status and direct call, the order against spellbook.py for S7; (3) each fix",
            "next")
        self.stage(self.CORRECTNESS, text)
        self.set_field(self.CORRECTNESS, "Updated")

    def run(self) -> None:
        self.s3()
        self.epic()
        print("S3", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: FACT"))
        print("EPIC", self.note_range(self.CORRECTNESS, f"- DATETIME: {self.now}", "  TYPE: DECISION"))


def main() -> None:
    record = OwnerDirection("record_owner_direction_20261019")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
