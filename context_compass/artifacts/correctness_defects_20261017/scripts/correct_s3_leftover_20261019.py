"""Correct S3's claim that nothing removes the borrowing Book's leftover entries (melder_0, 2026-10-19).

The owner asked what exactly is left behind; read in source: two entries in the borrowing conduit's Spellbook, and
a sever of the link, a remove-all and the Book's teardown remove them - only the index unlink misses them. A FACT
note on S3 corrects the story's "nothing removes it" and names both entries. All-or-nothing; `--write` flushes.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class CorrectS3(Record):
    """S3's correction note."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
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

    def run(self) -> None:
        book = "src/melder/aether/spellbook/spellbook.py"
        ward = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
        evidence = [self.method(book, "Spellbook", "_detach_link_contract"),
                    self.method(book, "Spellbook", "_clear_contracted_spells_for_conduit"),
                    self.method(ward, "ConduitWard", "_remove_contract"),
                    self.p2_range()]
        note = self.note(self.now, "FACT", [
            "Correction, read in source on the owner's question (chat 2026-10-19). What stays behind is two entries",
            "in the borrowing conduit's Spellbook: `_inactive_contracted_spells[<lender conduit id>][<version id>]`,",
            "holding the lender's own Spell object for the version, already cleaned; and the version id in",
            "`_contracted_spell_ids[<lender conduit id>]`. No object a spell built, no Creations entry. They are not",
            "stuck - this story's \"nothing removes it\" is wrong: a sever of the link (`ConduitWard._remove_contract`",
            "-> `Spellbook._detach_link_contract`, which pops the borrower's whole bucket for that lender, the parked",
            "map and the id set included), a remove-all (`_clear_contracted_spells_for_conduit`, which clears them",
            "too) and the borrowing Book's teardown remove them; only the index unlink (`remove_index_from_contract`)",
            "leaves them. No meld reads them (`find_contracted_spell` answers None, P2). Whether the stale id",
            "disturbs a later grant of the same spell_id is UNKNOWN (not probed)."],
            evidence,
            ["By the owner's rule that leftovers are the owning agent's to clean up, and with a sever clearing these,",
             "S3 is a tidy-up of Melder's own record at most; withdrawal is recommended to the owner."],
            ["The owner's word: withdraw S3, or keep it as a tidy-up of the index unlink."], "REQUIRED", 8)
        self.append_notes(self.S3, [note], "s3 correction")
        self.set_field(self.S3, "Updated")
        print("NOTE", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: FACT"))


def main() -> None:
    record = CorrectS3("correct_s3_leftover_20261019")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
