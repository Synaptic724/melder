"""Record the S1+S2 whole-tree run on the /tmp mirror and its triage (S1's MEASURE, S2's FACT), the doubles batch, the
handoffs, the board rows and the artifact rows (melder_0, 2026-10-18). One all-or-nothing pass."""
import sys

from cc_record import Record


class RecordWholeTree(Record):
    TREE = "artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2"
    SCRIPTS = "artifacts/spell_identity_20261018/scripts"
    RUNS = "artifacts/spell_identity_20261018/staged/runs"
    SESSION_NOTES = Record.SESSION_NOTES + ("2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z")

    def s1(self) -> None:
        note = self.note(self.now, "MEASURE", [
            "The whole tree on the /tmp mirror with S1 and S2 (0.2.8256, the two new modules and the new tests; GIL",
            "off; 14,697 tests: unit 9,759, component 2,428, integration 2,256, experimentation 254) fails 424. 18",
            "are melder_1's S8 tests, red on the 0.2.8255 baseline too and on hold with the owner (M1-33); 406 are",
            "new. By category (whole_tree_triage.py over the failed ids and their first errors): (a) 213 test",
            "doubles and pins of what S2 changed - the fake Spells of the crystal harness and the snapshot tests have",
            "no `binding_hash`, and PAYLOAD_FORMAT 2, generation 23 and RecordVersion 4.3.0 moved the pins; (b) 96",
            "tests of the retired API - `Bind.sha256_profile` (47 of test_bind.py's 48), the profiles'",
            "`fingerprint_repr` and `spell_id_inspector`'s old keywords; (c) 88 tests that register one object",
            "twice, now refused (24 files, test_ordered_disposal_replay.py 22); (d) 2 reversed premises (a resolved",
            "disposal order or a managed binding no longer changes the spell_id); (e) 4 others (the cross-process",
            "stability test, two resolvable regexes, a two-frame conjure); 3 failed only because the mirror lacked",
            "repository files, copied in since. The blast radius counted 101 (triage.md) because it ran the identity",
            "change with the old API and pins in place; categories (a) and (b) are what it could not see. The",
            "doubles are rewritten (tests_edits_doubles.py: the harness and seven test files): those files and the",
            "new binding-hash test pass, 350 tests.",
        ], [
            self.whole(self.TREE + "/whole_tree_triage_gil0.txt"),
            self.whole(self.TREE + "/failed_gil0.txt"),
            self.whole(self.TREE + "/base_8255_failed.txt"),
            self.whole(self.SCRIPTS + "/whole_tree_triage.py"),
            self.whole(self.SCRIPTS + "/tests_edits_doubles.py"),
            self.whole(self.RUNS + "/tests_doubles_gil0.txt"),
        ], [
            "The tranche is four times the blast radius; (b) to (e) remain: (b) retires the tests of the removed",
            "API onto their successors or converts them, (c) gives each test one registration per object or makes",
            "it a refusal test, (d) asserts the binding hash moves where the spell_id used to, (e) one at a time.",
        ], [
            "Category (b): read test_bind.py's `sha256_profile` tests and map each to its successor before",
            "retiring it.",
        ], "REQUIRED", 9)
        self.append_notes(self.S1, [note], "s1 note")
        text = self.read(self.S1)
        text = self.once(text,
                         "- Next: the red tests in the mirror (the digest's cases first); then the 101 moved tests, the whole tree\n"
                         "  with the GIL off and on, and the landing pass with S2, notched above 0.2.8256.\n",
                         "- Done since: the whole tree run on the mirror and triaged - 424 failures, 18 of them melder_1's S8\n"
                         f"  baseline; the doubles rewritten and green (MEASURE note of {self.now}).\n"
                         "- Next: the test tranche by category - (b) the retired API's tests, (c) one object registered twice,\n"
                         "  (d) the reversed premises, (e) the rest; then the whole tree with the GIL off and on, and the\n"
                         "  landing pass with S2, notched above 0.2.8256.\n", "s1 next")
        self.stage(self.S1, text)
        self.set_field(self.S1, "Updated")

    def s2(self) -> None:
        note = self.note(self.now, "FACT", [
            "S2's share of the whole-tree run (S1's MEASURE note of this time): 213 failing tests faked or pinned",
            "what S2 changed - the fake Spells of the crystal harness, the crystallizer tests and the structural",
            "snapshot tests had no `binding_hash`, and the pins of PAYLOAD_FORMAT (2), the cache generation history",
            "(23, \"binding_manifest_keys\") and RecordVersion (4.3.0; 4.1-4.3 records readable) had moved.",
            "tests_edits_doubles.py rewrites them: the fakes take a binding hash derived from their spell_id, and",
            "two new structural-key tests prove the key and the world stamp follow the binding hash under one",
            "spell_id. The ten files with the new test_spell_crystal_binding_hash.py pass, 350 tests, GIL off.",
        ], [
            self.whole(self.SCRIPTS + "/tests_edits_doubles.py"),
            self.whole(self.RUNS + "/tests_doubles_gil0.txt"),
            "context_compass/artifacts/spell_identity_20261018/staged/tests/unit/melder/crystallizer/"
            "test_spell_crystal_binding_hash.py:1-79",
        ], [
            "S2's own tests are green in the mirror; its remaining failures are the ordered-disposal replay's",
            "(category c, 22), whose restores now report binding changes, and the reversed premises (d).",
        ], [
            "With S1's tranche: categories (b) to (e), the replay rewrite among them.",
        ], "REQUIRED", 8)
        self.append_notes(self.S2, [note], "s2 note")
        text = self.read(self.S2)
        text = self.once(text,
                         "- Next: the red tests in the mirror (the manifest, the cache keys and stamp, the record and its restore);\n"
                         "  then the landing pass with S1.\n",
                         f"- Done since: the doubles of S2's fields and pins rewritten and green in the mirror (FACT note of\n"
                         f"  {self.now}).\n"
                         "- Next: S1's test tranche (categories b-e), which carries S2's remaining tests (the ordered-disposal\n"
                         "  replay's binding changes); then the landing pass with S1.\n", "s2 next")
        self.stage(self.S2, text)
        self.set_field(self.S2, "Updated")

    def epic(self) -> None:
        text = self.read(self.EPIC)
        text = self.once(text,
                         "- Next: (1) the red tests in the mirror - the digest's cases, the manifest, the cache keys, the record -\n"
                         "  then the 101 moved tests and the whole tree with the GIL off and on; (2) the landing pass - src,\n"
                         "  green, docs, notches, the rebuild last.\n",
                         "- Done since: the whole tree run with S1 and S2 in the mirror - 406 new failures in five categories,\n"
                         f"  the 213 doubles fixed (S1's MEASURE note of {self.now}).\n"
                         "- Next: (1) the test tranche - the retired API's tests, one object registered twice, the reversed\n"
                         "  premises, the rest - then the whole tree with the GIL off and on; (2) the landing pass - src,\n"
                         "  green, docs, notches, the rebuild last.\n", "epic next")
        self.stage(self.EPIC, text)
        self.set_field(self.EPIC, "Updated")

    @staticmethod
    def once_row(text: str, old: str, new: str, label: str) -> str:
        """Replace one table-row fragment; table rows are exempt from the width cap."""
        if text.count(old) != 1:
            sys.exit(f"ROW ANCHOR {label}: found {text.count(old)}")
        return text.replace(old, new)

    def row(self, text: str, item: str, old: str, new: str) -> str:
        lines = text.split("\n")
        hits = [i for i, line in enumerate(lines) if line.startswith(f"| {item} |")]
        if len(hits) != 1 or lines[hits[0]].count(old) != 1:
            sys.exit(f"ROW {item}: {len(hits)}")
        cells = lines[hits[0]].replace(old, new).split(" | ")
        cells[-2] = self.now
        lines[hits[0]] = " | ".join(cells)
        return "\n".join(lines)

    def board(self) -> None:
        text = self.read(self.BOARD)
        text = self.row(text, "spell_identity_is_the_code",
                        "S1 and S2 applied in the /tmp mirror; the red tests there, then the moved tests and the whole tree "
                        "(GIL off and on), then the landing pass.",
                        "The test tranche in the /tmp mirror (the retired API, one object twice, the reversed premises), "
                        "then the whole tree (GIL off and on) and the landing pass.")
        text = self.row(text, "spell_id_code_hash",
                        "S1 applied in the /tmp mirror with S2; its red tests (the digest's cases), then the landing with S2.",
                        "S1's test tranche in the mirror (406 new failures triaged, the doubles done), then the landing "
                        "with S2.")
        text = self.row(text, "binding_manifest_hash",
                        "S2 applied in the /tmp mirror with S1; its red tests (manifest, cache keys, record), then the "
                        "landing with S1.",
                        "S2's doubles green in the mirror; the rest of the tranche with S1, then the landing with S1.")
        self.stage(self.BOARD, text)

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        text = self.once_row(text,
                         "record_mirror_apply.py (S1 and S2 applied to the mirror, recorded); probes/, runs/, blast_radius/ "
                         "and staged/ are rowed under S1. | 2026-10-18T17:51:07Z | HELPFUL |",
                         "record_mirror_apply.py (S1 and S2 applied to the mirror, recorded); consume_m1_39.py and "
                         "consume_m1_40.py (M1-39 and M1-40 consumed, M0-199 and M0-200 sent); tests_apply_s1_s2.py and "
                         "tests_edits_doubles.py (the test tranche's applier and its first batch, the doubles); "
                         "first_error_kinds.py, whole_tree_triage.py and resumable_pytest_shard.py (the whole-tree run and "
                         "its triage) and record_whole_tree.py (recorded); probes/, runs/, blast_radius/ and staged/ are "
                         f"rowed under S1. | {self.now} | HELPFUL |", "scripts row")
        text = self.once_row(text,
                         "and the mirror's S1 and S2 src diff and smoke (mirror_s1s2_src.diff, mirror_smoke_s1s2*). Deleted "
                         "once the modules are in src/. | 2026-10-18T17:51:07Z | REQUIRED |",
                         "and the mirror's S1 and S2 src diff and smoke (mirror_s1s2_src.diff, mirror_smoke_s1s2*); tests/ "
                         "holds the new test files for the landing (the digest's and the manifest's unit tests, the "
                         "crystal's binding hash, the component test of spell identity) and runs/ their green and red runs "
                         "(tests_s1s2_new_*, red_component_spell_identity_repo_gil0.txt, tests_doubles_gil0.txt). Deleted "
                         f"once the modules and tests are in the repository. | {self.now} | REQUIRED |", "staged row")
        text = self.once_row(text,
                         "the probes of the `__annotate_func__` rule and S3's slot reuse with their runs; the landing "
                         "rewrites the tests from triage.md. | 2026-10-18T16:24:12Z | REQUIRED |",
                         "the probes of the `__annotate_func__` rule and S3's slot reuse with their runs; whole_tree_s1s2/ "
                         "holds the whole tree on the mirror with S1 and S2 (424 failed ids, their first errors, the "
                         "0.2.8255 baseline's failures, the triage by category, the runs gzip'd); the landing rewrites the "
                         f"tests by that triage. | {self.now} | REQUIRED |", "blast row")
        self.stage(self.ARTIFACTS, text)


def main() -> None:
    record = RecordWholeTree("whole_tree")
    record.s1()
    record.s2()
    record.epic()
    record.board()
    record.artifacts()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
