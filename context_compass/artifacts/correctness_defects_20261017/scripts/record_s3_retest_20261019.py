"""Record S3's re-test on 0.2.8260 and the owner's rule for it (melder_0, 2026-10-19).

The owner asked for a proper test ("does something actually get left behind"); probe_index_unlink_leftovers.py
(U1-U3, GIL off and on) and its U3 traceback answer it. The owner's rule: an index removed from a contract takes
every version it shared, active and parked. S3 gets a MEASURE and a DECISION note, its requirements, acceptance,
open question, decision log, artifact links and resume view; the epic its decision log line and resume view; the
artifact board one row. All-or-nothing; `--write` flushes; without it the pass only checks.
"""
import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class RecordS3(Record):
    """S3's notes and body, the epic's lines, the artifact row."""

    CORRECTNESS = "tickets/epics/2026-10-17_correctness_defects_epic.md"
    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    FOLDER = "artifacts/correctness_defects_20261017"

    def method(self, rel: str, cls_name: str, name: str) -> str:
        tree = ast.parse((self.REPO / rel).read_text(encoding="utf-8"))
        if cls_name:
            classes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name]
            body = classes[0].body if classes else []
        else:
            body = tree.body
        hits = [n for n in body if isinstance(n, ast.FunctionDef) and n.name == name]
        if len(hits) != 1:
            sys.exit(f"FUNCTION {cls_name}.{name}: {len(hits)}")
        return f"{rel}:{hits[0].lineno}-{hits[0].end_lineno}"

    def whole_file(self, rel: str) -> str:
        count = len((self.ROOT / rel).read_text(encoding="utf-8").rstrip("\n").split("\n"))
        return f"context_compass/{rel}:1-{count}"

    def s3_body(self) -> None:
        text = self.read(self.S3)
        text = self.once(text, "  borrower's copy and its borrowed id on every index-link contract covering the index - the emission\n",
                         "  borrower's entry and its borrowed id on every index-link contract covering the index - the emission\n",
                         "req 1")
        text = self.once(
            text,
            "- After it, a borrower's unlink of the index leaves no copy or id of the lender's versions behind.\n",
            "- After it, a borrower's unlink of the index leaves no entry or id of the lender's versions behind.\n"
            "- `remove_index_from_contract` removes every record the index link filed in the borrower for the index's\n"
            "  versions - each version's entry, active or parked, its borrowed id and its member detail - a version the\n"
            "  lender disposed meanwhile included (the owner, 2026-10-19: \"removing the index from contract should remove\n"
            "  all the spells that index shared\").\n",
            "req 2")
        text = self.once(
            text,
            "- After `cleanup_spell` of a parked member while another member keeps the index: no borrower holds a copy of it,\n"
            "  active or parked, and no borrower's borrowed ids list it.\n"
            "- `remove_index_from_contract` afterwards leaves the borrower with no copy or id of the lender's versions.\n",
            "- After `cleanup_spell` of a parked member while another member keeps the index: no borrower holds an entry for\n"
            "  it, active or parked, no member detail names it, and no borrower's borrowed ids list it.\n"
            "- `remove_index_from_contract` afterwards leaves the borrower with no entry or id of the lender's versions.\n"
            "- After the lender disposes a parked version and stages the same class again, a notch to it completes on both\n"
            "  sides and the borrower melds it (probe U3; today the notch raises AttributeError in the borrower fan-out and\n"
            "  the borrower is left with no active version).\n",
            "acceptance")
        text = self.once(
            text,
            "  yes, the question above stands (FACT note).\n",
            "  yes, the question above stands (FACT note).\n"
            "  Answered (owner, 2026-10-19): yes - a bookkeeping problem; an index removed from a contract takes every\n"
            "  version it shared, active and parked (DECISION note).\n",
            "open question")
        text = self.once(
            text,
            "- 2026-10-17T20:29:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A2 (Notes).\n",
            "- 2026-10-17T20:29:03Z: filed under EPIC-2026-10-17-correctness_defects from sweep A2 (Notes).\n"
            f"- {self.now}: confirmed by the owner - an index removed from a contract takes every version it shared,\n"
            "  active and parked; re-tested on 0.2.8260, GIL off and on (MEASURE and DECISION notes).\n",
            "decision log")
        text = self.once(
            text,
            "  - artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt\n",
            "  - artifacts/correctness_defects_20261017/runs/probe_parked_cleanup_borrowers_gil1.txt\n"
            "  - artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers.py (cases U1-U3, 0.2.8260)\n"
            "  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil0.txt\n"
            "  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_gil1.txt\n"
            "  - artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers_u3_trace.py (U3's traceback)\n"
            "  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_u3_trace_gil0.txt\n",
            "artifact links")
        old_view = (
            "- Scope: `Conduit.cleanup_spell` of a parked version whose index survives removes it from every index-link borrower\n"
            "  (Requirements). Defect proven on 0.2.8251 (Notes); probe and runs in Artifact Links.\n"
            "- State: ready, unassigned; filed by melder_0 under EPIC-2026-10-17-correctness_defects. The fix sits in conduit.py,\n"
            "  which melder_1 holds; melder_1 was told by mailbox.\n"
            "- Next: (1) the owner schedules it, or melder_1 folds it into its contract work; (2) patch docs; (3) the fix, its\n"
            "  tests, docs, notch and the rebuild.\n")
        new_view = (
            "- Scope: a borrower keeps no record of a lender's version that is gone or unlinked: the lender's\n"
            "  `cleanup_spell` of a parked version removes its entry, borrowed id and member detail, and\n"
            "  `remove_index_from_contract` removes every version the index shared, active and parked (Requirements; the\n"
            "  owner's rule, 2026-10-19). Probes and runs in Artifact Links.\n"
            "- State: ready, unassigned; confirmed by the owner and re-tested on 0.2.8260, GIL off and on: the records\n"
            "  stay, and a later notch to the same class staged again raises AttributeError in the borrower fan-out and\n"
            "  leaves the borrower with no active version (MEASURE note). The fix sits in conduit.py and conduit_ward.py;\n"
            "  whether spellbook.py too (with melder_1 for S7) is for the patch.\n"
            "- Next: (1) the owner's go to take it; (2) patch docs with the exact edits for his approval; (3) the fix, its\n"
            "  tests, docs, notch and the rebuild.\n")
        text = self.once(text, old_view, new_view, "resume view")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def s3_notes(self) -> None:
        runs = f"{self.FOLDER}/runs"
        probes = f"{self.FOLDER}/probes"
        measure = self.note(self.now, "MEASURE", [
            "Re-tested on 0.2.8260 at the owner's request (probe_index_unlink_leftovers.py), GIL off and on, the same",
            "output. U1, control: `remove_index_from_contract` with nothing disposed removes every borrower record for",
            "the index - English's active entry, French's parked entry, both borrowed ids, the tracked index, the ward",
            "contract's index and member details. U2: after the lender's `cleanup_spell(French)` (English keeps the",
            "index), the borrower keeps French's parked entry holding the cleaned Spell, French's borrowed id and the",
            "ward contract's member detail for French, which the public listing and `find_contracted_spell` no longer",
            "show; `remove_index_from_contract` then removes English's records and leaves those three; `sever_link`",
            "removes them. U3: after that cleanup the lender stages French again (the same spell_id) and notches to it;",
            "the lender's switch completes (French active, its meld returns 'bonjour'), but `notch_spell` raises",
            "AttributeError in the borrower fan-out (`Conduit._activate_borrowed_spell` ->",
            "`Spellbook._activate_contract_spell` -> `_reactivate_contracted_spell` reads `spell_index` on the stale",
            "cleaned Spell), and the borrower is left with no active version (English parked; a meld of French raises",
            "KeyError). No existing test covers a borrower after a lender's parked cleanup, or an unlink after one: the",
            "unlink tests cover live members, the destroy test the sole member, the parked-cleanup tests no borrower."],
            [self.whole_file(f"{probes}/probe_index_unlink_leftovers.py"),
             self.whole_file(f"{runs}/probe_index_unlink_leftovers_gil0.txt"),
             self.whole_file(f"{runs}/probe_index_unlink_leftovers_gil1.txt"),
             self.whole_file(f"{runs}/probe_index_unlink_leftovers_u3_trace_gil0.txt"),
             self.method("src/melder/aether/conduit/conduit.py", "Conduit", "_activate_borrowed_spell"),
             self.method("src/melder/aether/spellbook/spellbook.py", "Spellbook", "_reactivate_contracted_spell"),
             self.method("tests/integration/melder/aether/conduit/test_index_link_notch_follow_integration.py", "",
                         "test_cleanup_sole_member_destroys_borrower_index_link"),
             self.method("tests/integration/melder/aether/conduit/test_spell_index_meld_and_contract_lifecycle.py", "",
                         "test_remove_index_contract_drops_borrower_index_and_member"),
             self.method("tests/integration/melder/aether/conduit/test_index_lifecycle_and_depth_integration.py", "",
                         "test_cleanup_inactive_member_leaves_index_and_active")],
            ["The leftover is real, and not only bookkeeping: it makes a later notch of the same class raise after the",
             "lender's switch, and the borrower loses its active version."],
            ["The owner's rule as requirements (DECISION note); then the owner's go for the fix."], "REQUIRED", 9)
        decision = self.note(self.now, "DECISION", [
            "The owner (chat 2026-10-19): \"inactive contracted spells that belong to another conduit should indeed be",
            "removed this is a book keeping problem\"; \"removing the index from contract should remove all the spells",
            "that index shared\"; \"all active and inactive spells properly should be removed if they are part of the",
            "index and were added by the borrowed conduit spells\". So S3 is a defect: when an index leaves a contract,",
            "every record the link filed in the borrower for its versions goes - active and parked, a version the",
            "lender disposed meanwhile included - and the lender's cleanup of a parked version leaves none behind. A",
            "sever already removes them all (U2)."],
            [self.doc_section(self.S3, "## Requirements (Functional)"),
             self.doc_section(self.S3, "## Acceptance Criteria")],
            ["The requirements and acceptance carry the rule; the story stays ready for the owner's go."],
            ["The owner's go; then the patch docs with the exact edits."], "REQUIRED", 9)
        self.append_notes(self.S3, [measure, decision], "s3 notes")

    def epic(self) -> None:
        text = self.read(self.CORRECTNESS)
        text = self.once(
            text,
            "  close, so its open questions went to the owner (DECISION note).\n\n## Artifact Links",
            "  close, so its open questions went to the owner (DECISION note).\n"
            f"- {self.now}: S3 confirmed by the owner - an index removed from a contract takes every version it\n"
            "  shared, active and parked - and re-tested on 0.2.8260: the records stay and break a later notch (S3's notes).\n"
            "\n## Artifact Links",
            "epic decision log")
        text = self.once(
            text,
            "  with melder_1 (M1-43); S3 waiting for its open question; S1, S2 and S5 waiting for the owner's word, the\n",
            "  with melder_1 (M1-43); S3 confirmed, awaiting the go; S1, S2 and S5 waiting for the owner's word, the\n",
            "epic state")
        text = self.once(
            text,
            "  M1-33); (2) S1, S2, S3 and S5 go to melder_0 once the owner answers its open questions (DECISION note of\n"
            "  2026-10-19T01:26:09Z): S3's defect status and direct call, the order against spellbook.py for S7; (3) each\n",
            "  M1-33); (2) S1, S2, S3 and S5 go to melder_0 on the owner's go (DECISION note of 2026-10-19T01:26:09Z);\n"
            "  S3 is confirmed and re-tested on 0.2.8260 (its notes), and the order against spellbook.py for S7 is open; (3) each\n",
            "epic next")
        self.stage(self.CORRECTNESS, text)
        self.set_field(self.CORRECTNESS, "Updated")

    def board(self) -> None:
        text = self.read(self.ARTIFACTS)
        anchor = ("| tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md | "
                  "artifacts/correctness_defects_20261017/probes/probe_parked_cleanup_borrowers.py |")
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(anchor)]
        if len(hits) != 1:
            sys.exit(f"ROW S3: {len(hits)}")
        row = ("| tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md | "
               "artifacts/correctness_defects_20261017/probes/probe_index_unlink_leftovers.py | defect_reproducer | ready | "
               "retain_as_reference | Cases U1 (control), U2 (what a parked cleanup leaves, then the unlink and the sever) "
               "and U3 (a later notch raises) on 0.2.8260 with their runs (runs/probe_index_unlink_leftovers_gil0.txt, "
               "_gil1.txt) and U3's traceback (probe_index_unlink_leftovers_u3_trace.py and its run); re-run at the fix. | "
               f"{self.now} | REQUIRED |")
        lines.insert(hits[0] + 1, row)
        self.stage(self.ARTIFACTS, "\n".join(lines))

    def run(self) -> None:
        self.s3_body()
        self.s3_notes()
        self.epic()
        self.board()
        print("S3 MEASURE", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: MEASURE"))
        print("S3 DECISION", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: DECISION"))


def main() -> None:
    record = RecordS3("record_s3_retest_20261019")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
