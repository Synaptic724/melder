"""Record S1's MEASURE of the test tranche's category (b) and the rewrites it carried (melder_0, 2026-10-18).

One all-or-nothing pass: the note, the story's handoff summary, the board's row for S1, and the artifact rows
for the batch scripts and their runs.
"""
import sys

from cc_record import Record


class RecordCategoryB(Record):
    RUNS = "artifacts/spell_identity_20261018/staged/runs"
    TRIAGE = "artifacts/spell_identity_20261018/blast_radius/whole_tree_s1s2/whole_tree_triage_gil0.txt"
    APPLIER = "artifacts/spell_identity_20261018/scripts/tests_apply_s1_s2.py"
    ORDERED = "artifacts/spell_identity_20261018/scripts/tests_edits_ordered_disposal.py"
    SESSION_NOTES = Record.SESSION_NOTES + ("2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z",
                                            "2026-10-18T18:44:16Z", "2026-10-18T18:48:19Z")

    def s1(self) -> None:
        note = self.note(self.now, "MEASURE", [
            "Category (b), the retired API's tests, is done in nine of its ten files, and with it the rewrites",
            "those files held of the other categories: nine batches of tests_apply_s1_s2.py (bind, managed,",
            "fingerprint, profile_strategy, component_bind, lifecycle_hooks, inherited, ordered_disposal,",
            "resolvable_registration), applied to the /tmp mirror, close 116 of the 424 failed ids - (b) 95 of",
            "96, (c) one object registered twice 18 of 88, (d) the ordered-disposal reversed premise 1 of 2,",
            "(e) the two resolvable-registration regexes 2 of 4. The nine files and the digest's test pass, 503",
            "tests, with the GIL off and on. A staged second member is a second version of its class - a subclass",
            "with the same name, qualname and module and one class-level value more (`second_version_of`) -",
            "because staging the class itself again is refused. Left: test_ordered_disposal_replay.py (1 of (b),",
            "22 of (c)), 48 of (c) in 20 other files, 1 of (d), 2 of (e); beside them melder_1's 18 S8 baselines.",
        ], [
            f"context_compass/{self.RUNS}/tests_category_b_gil0.txt:1-4",
            f"context_compass/{self.RUNS}/tests_category_b_gil1.txt:1-2",
            self.whole(self.TRIAGE),
            self.whole(self.APPLIER),
            self.whole(self.ORDERED),
        ], [
            "74 failed ids of S1 and S2 remain before the whole tree reruns; every batch lands in the",
            "repository through the same applier, so the mirror's green is the landing's.",
        ], [
            "test_ordered_disposal_replay.py: the staged member becomes a second version of the service, the",
            "restore-policy tests assert the kept spell_ids and the reported binding changes; batch ordered_replay.",
        ], "REQUIRED", 9)
        self.append_notes(self.S1, [note], "s1 measure")
        self.set_field(self.S1, "Updated")
        text = self.read(self.S1)
        text = self.once(text, (
            "- Next: the test tranche by category - (b) the retired API's tests, (c) one object registered twice,\n"
            "  (d) the reversed premises, (e) the rest; then the whole tree with the GIL off and on, and the\n"
            "  landing pass with S2, notched above 0.2.8256.\n"), (
            f"- Done since: category (b) in nine of its ten files with the rewrites they held - 116 failed ids\n"
            f"  closed, 503 tests green with the GIL off and on (MEASURE note of {self.now}).\n"
            "- Next: test_ordered_disposal_replay.py, then (c) one object registered twice in 20 more files, (d)\n"
            "  the managed reversed premise, (e) the process-stability and two-frame tests; then the whole tree\n"
            "  with the GIL off and on, and the landing pass with S2, notched above 0.2.8256.\n"), "s1 summary")
        self.stage(self.S1, text)

    def board(self) -> None:
        text = self.read(self.BOARD)
        old_row = [line for line in text.split("\n") if line.startswith("| spell_id_code_hash |")]
        if len(old_row) != 1:
            sys.exit(f"ROW spell_id_code_hash: {len(old_row)}")
        new_row = old_row[0].replace(
            "| S1's test tranche in the mirror (406 new failures triaged, the doubles done), then the landing with S2. |",
            "| S1's test tranche in the mirror (the doubles and the retired API's tests done; 74 failed ids left), "
            "then the landing with S2. |").replace("| 2026-10-18T18:44:20Z | REQUIRED |", f"| {self.now} | REQUIRED |")
        if new_row == old_row[0] or self.now not in new_row:
            sys.exit("ROW spell_id_code_hash unchanged")
        self.stage(self.BOARD, text.replace(old_row[0], new_row))

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        lines = text.split("\n")
        epic_rows = [i for i, line in enumerate(lines) if line.startswith(
            "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | artifacts/spell_identity_20261018/ |")]
        staged_rows = [i for i, line in enumerate(lines) if line.startswith(
            "| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | "
            "artifacts/spell_identity_20261018/staged/ |")]
        if len(epic_rows) != 1 or len(staged_rows) != 1:
            sys.exit(f"ARTIFACT ROWS {len(epic_rows)} {len(staged_rows)}")
        epic = lines[epic_rows[0]]
        for old, new in (
                ("tests_apply_s1_s2.py and tests_edits_doubles.py (the test tranche's applier and its first batch, "
                 "the doubles);",
                 "tests_apply_s1_s2.py and its batches tests_edits_doubles.py, tests_edits_bind.py, "
                 "tests_edits_managed.py, tests_edits_fingerprint.py, tests_edits_profile_strategy.py, "
                 "tests_edits_component_bind.py, tests_edits_lifecycle_hooks.py, tests_edits_inherited.py, "
                 "tests_edits_ordered_disposal.py and tests_edits_resolvable_registration.py (the test tranche: "
                 "the doubles, the retired API's tests and the rewrites those files held);"),
                ("and record_whole_tree.py (recorded);",
                 "and record_whole_tree.py, record_bind_retirement.py and record_category_b.py (recorded);"),
                ("| 2026-10-18T18:44:20Z | HELPFUL |", f"| {self.now} | HELPFUL |")):
            if epic.count(old) != 1:
                sys.exit(f"EPIC ROW anchor: {old[:60]}")
            epic = epic.replace(old, new)
        staged = lines[staged_rows[0]]
        for old, new in (
                ("tests_doubles_gil0.txt).",
                 "tests_doubles_gil0.txt, tests_bind_batch_gil0/1.txt, tests_category_b_gil0/1.txt)."),
                ("| 2026-10-18T18:44:20Z | REQUIRED |", f"| {self.now} | REQUIRED |")):
            if staged.count(old) != 1:
                sys.exit(f"STAGED ROW anchor: {old[:60]}")
            staged = staged.replace(old, new)
        lines[epic_rows[0]] = epic
        lines[staged_rows[0]] = staged
        self.stage(self.ARTIFACTS, "\n".join(lines))


def main() -> None:
    record = RecordCategoryB("category_b")
    record.s1()
    record.board()
    record.artifacts()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
