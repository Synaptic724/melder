"""Record S1 and S2's source and tests applied to the repository (melder_0, 2026-10-18): one FACT note on S1."""
import sys

from cc_record import Record


class RecordLandingApplied(Record):
    A = "artifacts/spell_identity_20261018"

    def s1(self) -> None:
        note = self.note(self.now, "FACT", [
            "S1 and S2 are applied to the repository: apply_s1_s2.py (26 files edited, the two new modules copied)",
            "and tests_apply_s1_s2.py (every batch, then a new batch `new_tests`), each --check first, wrote",
            "nothing until every anchor matched, and the repository's src/ then equals the mirror's byte for byte.",
            "tests/ equals it too but for two files melder_1 committed at 0.2.8256 after the mirror was built - its",
            "S4 red tests (test_separated_version_is_known_to_its_frame_integration.py and the residency test in",
            "test_mutation_research_root.py), red by design until S4 lands. One new test module existed only in the",
            "mirror, test_spell_code_digest_libraries.py (decision B's nine tests, in both whole-tree runs): it is",
            "staged now and copied by `new_tests` with the binding manifest's tests and the component test.",
        ], [
            self.whole(self.A + "/scripts/apply_s1_s2.py"),
            self.whole(self.A + "/scripts/tests_apply_s1_s2.py"),
            self.whole(self.A + "/scripts/tests_edits_new_tests.py"),
            self.whole(self.A + "/staged/tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py"),
        ], [
            "The code and tests of the landing are in place; nothing is committed (the owner commits). The landed",
            "tree's whole run, with melder_1's S4 tests, comes with the rebuild mirror.",
        ], [
            "The docs: the patch docs promoted into the system documents, their indexes, the graph; then the",
            "notches, the release note, the closure and the rebuild.",
        ], "REQUIRED", 8)
        self.append_notes(self.S1, [note], "s1 applied")
        self.set_field(self.S1, "Updated")


def main() -> None:
    record = RecordLandingApplied("landing_applied")
    record.s1()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
