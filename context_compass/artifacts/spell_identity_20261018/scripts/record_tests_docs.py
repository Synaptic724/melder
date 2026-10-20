"""Record S1 and S2's tests system documents and the source follow-ups (melder_0, 2026-10-18).

A MEASURE note on S1 (the four documents: what changed, the gates run, the rubric scores read from the files on disk
after the index rebuild), a pointer note on S2, the handoffs of S1, S2 and the epic, and the three board rows' next
cells. All-or-nothing; `--write` flushes.
"""
import re
import sys

from docs_common import DocsRecord


class RecordTestsDocs(DocsRecord):
    """The notes, handoffs and board rows of the docs pass."""

    A = "artifacts/spell_identity_20261018/scripts"

    def s1_note(self) -> str:
        return self.note(self.now, "MEASURE", [
            "The tests system documents carry S1 and S2 and the source documents their follow-ups. tests_components:",
            "the four unit and one component test modules, the ordered-disposal replay and the `version_of` support",
            "module as key files with code-map records and bullets saying what each protects; the retired fingerprint's",
            "three spellbook bullets rewritten to the code digest; the harness's binding hash; cache generation 23;",
            "counts from disk (857 test modules); every code-map range checked against disk, 21 re-stamped (19 rewritten",
            "files; `test_mutation_research_root.py` and `test_spell_managed_quantity_stamp.py` had drifted); the core",
            "set is 272 paths, equal to the code map (the 0.2.8256 entry said 264 where the file held 265).",
            "tests_architecture: the inventory, the support module in the evidence, responsibilities, C2 and map (37",
            "paths), a one-object invariant, the xfail evidence remapped to 626-675. src_architecture: the build parity",
            "and -O rule in the identity invariant, the patch-release UNKNOWN, the release-after-teardown failure mode",
            "corrected (the not-managed ValueError; the torn-down RuntimeError only through a lease or a raced",
            "release). src_components: decision B's lookup rule and the same correction. Gates: all four indexes",
            "--check current; portability and absolute-path greps empty; CR 0; every cited test path exists; the",
            "preservation diffs remove only the replaced counts, re-stamped extents, appended notes and the corrected",
            "sentences. Rubric (from the files on disk): tests_components 86 (B; Fidelity 4 - clusters outside this",
            "lane not re-read against their tests), tests_architecture 84 (B; Depth 4), src_architecture 88 (B;",
            "Fidelity 4 - the patch-release claim UNKNOWN), src_components 87 (B; Depth 4 per entry).",
        ], [
            self.whole(self.A + "/land_docs_tests_comp.py"),
            self.whole(self.A + "/land_docs_tests_arch.py"),
            self.whole(self.A + "/land_docs_src_followups.py"),
            self.doc_block(self.TESTS_COMP, "2026-10-18 spell identity is the code (0.2.8257-0.2.8258; S1 and S2"),
            self.doc_block(self.TESTS_ARCH, "2026-10-18 spell identity is the code (0.2.8257-0.2.8258): the inventory"),
            self.doc_block(self.ARCH, "2026-10-18 follow-ups to the identity landing"),
            self.doc_block(self.COMP, "2026-10-18 follow-ups to the identity landing"),
            "src/melder/aether/conduit/creations/creations.py:362-379",
            "src/melder/aether/conduit/creations/release_managed_spell.py:540-553",
            "src/melder/aether/conduit/creations/managed_spell_quantity.py:589-590",
            "src/melder/aether/spellbook/bind/spell_code_digest.py:1170-1193",
            "src/melder/aether/spellbook/bind/spell_code_digest.py:1252-1305",
        ], [
            "The four system documents are current for the landing; the graph, the notches, the release note, the",
            "docs checks, the closure and the rebuild remain.",
        ], [
            "The graph: extract --strict, the two new modules' descriptors, assemble, the walker report.",
        ], "REQUIRED", 8)

    def s2_note(self) -> str:
        return self.note(self.now, "FACT", [
            "S2's half of the tests documents landed with S1's (S1's MEASURE note of this time): the binding manifest's",
            "and the crystal's binding-hash tests, the ordered-disposal replay's binding changes, the managed binding's",
            "three binding hashes, the harness's binding hash and cache generation 23.",
        ], [
            self.doc_block(self.TESTS_COMP, "2026-10-18 spell identity is the code (0.2.8257-0.2.8258; S1 and S2"),
        ], [
            "S2's documents are current with S1's.",
        ], [
            "With S1: the graph, the notches, the release note, the docs checks, the closure, the rebuild last.",
        ], "HELPFUL", 7)

    def handoff(self, rel: str, old_next: str, done: str, new_next: str) -> None:
        text = self.read(rel)
        text = self.once(text, old_next, done + new_next, f"handoff {rel}")
        self.stage(rel, text)
        self.set_field(rel, "Updated")

    def board(self, row: str, nxt: str) -> None:
        text = self.read(self.BOARD)
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(f"| {row} | ")]
        if len(hits) != 1:
            sys.exit(f"ROW {row}: {len(hits)}")
        cells = lines[hits[0]].split(" | ")
        if len(cells) != 12:
            sys.exit(f"ROW {row}: {len(cells)} cells")
        cells[6] = nxt
        cells[10] = self.now
        lines[hits[0]] = " | ".join(cells)
        self.stage(self.BOARD, "\n".join(lines))


def main() -> None:
    record = RecordTestsDocs("tests_docs_record")
    record.append_notes(record.S1, [record.s1_note()], "s1 docs")
    record.append_notes(record.S2, [record.s2_note()], "s2 docs")
    nxt = "- Next: the graph, the notches, the release note, the docs checks, the closure, the rebuild last.\n"
    record.handoff(record.S1,
                   "- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n"
                   "  note, the docs checks, the closure, the rebuild last.\n",
                   f"- Done since: the tests system documents and the source follow-ups (MEASURE note of {record.now}).\n",
                   nxt)
    record.handoff(record.S2,
                   "- Next: with S1 - the tests system documents, the graph, the notches, the release note, the docs\n"
                   "  checks, the closure, the rebuild last.\n",
                   f"- Done since: the tests system documents (FACT note of {record.now}).\n",
                   "- Next: with S1 - the graph, the notches, the release note, the docs checks, the closure, the\n"
                   "  rebuild last.\n")
    record.handoff(record.EPIC,
                   "- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n",
                   f"- Done since: the tests system documents and the source follow-ups (S1's MEASURE note of "
                   f"{record.now}).\n",
                   "- Next: the graph, the notches, the release\n")
    record.board("spell_identity_is_the_code", "The graph, the notches, the release note, the docs checks, the closure; "
                 "the rebuild last.")
    record.board("spell_id_code_hash", "With S2: the graph, the notches, the release note, the docs checks, the "
                 "closure, the rebuild last (examples, docs and system documents done).")
    record.board("binding_manifest_hash", "With S1: the graph, the notches, the release note, the docs checks, the "
                 "closure, the rebuild last.")
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
