"""Record the end of S1 and S2's test tranche, the whole tree's rerun and bind's cost (melder_0, 2026-10-18).

One all-or-nothing pass: S1's MEASURE notes (the tranche and the whole tree; bind's cost) and RISK note, its two
task lines and handoff summary; S2's FACT note and handoff summary; the epic's handoff summary; the three board
rows; the artifact rows of the epic's scripts and S1's probes, staged files and blast radius.
"""
import sys
from typing import List, Tuple

from cc_record import Record


class RecordTrancheDone(Record):
    A = "artifacts/spell_identity_20261018"
    RUN2 = A + "/blast_radius/whole_tree_s1s2_run2"
    RUNS = A + "/staged/runs"
    COST = A + "/runs/bind_cost"
    SESSION_NOTES = Record.SESSION_NOTES + (
        "2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z", "2026-10-18T18:44:16Z",
        "2026-10-18T18:44:20Z", "2026-10-18T18:48:19Z", "2026-10-18T19:11:29Z", "2026-10-18T19:17:19Z")

    def tranche_note(self) -> str:
        return self.note(self.now, "MEASURE", [
            "The test tranche is done in the mirror: batches ordered_replay, one_object_a and one_object_b of",
            "tests_apply_s1_s2.py close the last 74 failed ids - (b) 1; (c) 70, one object registered twice, by a",
            "class of its own where a test only needs a second spell, `version_of` (a subclass with the same name,",
            "qualname and module and one class-level value more) where the name matters, a module-level class where",
            "a restore or graft imports the version, and per-frame spell ids where one class lives in two roots; (d)",
            "1, a managed binding keeps its spell_id and moves its binding hash; (e) 2, the process-stability child",
            "and the two-frame conjure. Batch A's files pass 114 tests and batch B's 113, the GIL off and on. The",
            "whole tree on the mirror (14,645 tests: unit 9,707, component 2,427, integration 2,257,",
            "experimentation 254) then fails the same 18 ids with the GIL off and on, all melder_1's S8 tests - red",
            "on the 0.2.8255 baseline and on hold with the owner (M1-33); S9's 7 from that baseline pass at",
            "0.2.8256. Run 2 counts 52 ids fewer than run 1: 89 gone (the retired API's tests and renamed ones), 37",
            "new (successors, renames and the binding-hash tests).",
        ], [
            self.whole(self.RUN2 + "/summary.txt"),
            self.whole(self.RUN2 + "/failed_gil0.txt"),
            self.whole(self.RUN2 + "/failed_gil1.txt"),
            self.whole(self.RUN2 + "/id_diff_run1_run2.txt"),
            self.whole(self.A + "/blast_radius/whole_tree_s1s2/base_8255_failed.txt"),
            f"context_compass/{self.RUNS}/tests_one_object_a_gil0.txt:1-1",
            f"context_compass/{self.RUNS}/tests_one_object_a_gil1.txt:1-1",
            f"context_compass/{self.RUNS}/tests_one_object_b_gil0.txt:1-1",
            f"context_compass/{self.RUNS}/tests_one_object_b_gil1.txt:1-1",
            self.whole(self.A + "/scripts/tests_edits_one_object_a.py"),
            self.whole(self.A + "/scripts/tests_edits_one_object_b.py"),
            self.whole(self.A + "/staged/tests/_spell_identity_test_support.py"),
        ], [
            "S1 and S2 are green in the mirror end to end, and every batch lands through the same applier, so the",
            "landing's tree is the mirror's; the exit gate's last item, bind's cost, is the next note.",
        ], [
            "The landing pass: apply_s1_s2.py and tests_apply_s1_s2.py on the repository (--check, then the run),",
            "with a copy batch for the two new tests no batch copies; then the notches, the docs and the rebuild.",
        ], "REQUIRED", 9)

    def cost_files(self) -> List[str]:
        files = [self.whole(self.A + "/probes/probe_bind_cost.py"),
                 self.whole(self.A + "/probes/probe_bind_cost_profile.py")]
        for world in ("gauntlet", "synth200"):
            for side in ("before", "after"):
                for run in (("gil0_r1", "gil0_r2", "gil1_r1") if world == "gauntlet" else ("gil0_r1", "gil0_r2")):
                    files.append(self.whole(f"{self.COST}/{world}_{side}_{run}.txt"))
        files.append(self.whole(self.COST + "/profile_bind_before_gil0.txt"))
        files.append(self.whole(self.COST + "/profile_bind_after_gil0.txt"))
        return files

    def cost_note(self) -> str:
        return self.note(self.now, "MEASURE", [
            "Bind's cost before (0.2.8256) and after (S1 and S2), through the benchmark's own cycle",
            "(profile_bind_conjure_cycle.run_cycle, caching disabled, no meld sweep - its sweep fails at 0.2.8256,",
            "before and after alike), 20 cycles a run: the gauntlet's 29 classes bind in 5.9-6.2 ms before and",
            "7.8-8.0 ms after with the GIL off (6.3 and 7.9 ms with it on), one bind's median 194-200 us before and",
            "249-253 us after, +55 us; 200 generated classes bind in 38.6-39.4 ms before and 46.5-48.0 ms after,",
            "187-189 us a bind before and 225 us after, +37 us. Conjure is unchanged (12.3-12.7 ms; 60.8-61.8 ms),",
            "so setup grows about 10% (18.6 to 20.4 ms) and 9% (100 to 109 ms); a meld reads none of it. The",
            "profile puts the difference in `SpellCodeDigest.spell_id`: `Bind._bind_logic` takes 0.150 s before",
            "and 0.225 s after over 580 profiled binds, spell_id 0.077 s of it; the binding profile costs the same",
            "before and after. The code memo is per Bind, so each new Spellbook digests every class's code again.",
        ], self.cost_files(), [
            "The exit gate's measurement is made: +37 to +55 us a bind, once per registration; melds unchanged.",
        ], [
            "The landing pass (the tranche note's NEXT); the cost is the owner's to weigh (RISK note).",
        ], "REQUIRED", 9)

    def risk_note(self) -> str:
        return self.note(self.now, "RISK", [
            "Bind costs 20-31% more after S1 (+37 to +55 us a class, setup +9-10%) because the spell_id now reads",
            "every function's code. Two remedies, unmeasured and not in this landing: a code memo shared by every",
            "Spellbook (owned by Aether, weakly keyed by code object), so a class bound again in a new Book",
            "digests nothing; and hashing incrementally instead of joining text. How much each recovers is UNKNOWN.",
        ], [
            self.whole(self.COST + "/profile_bind_after_gil0.txt"),
            self.whole(self.COST + "/gauntlet_after_gil0_r1.txt"),
            self.whole(self.COST + "/synth200_after_gil0_r1.txt"),
        ], [
            "A world binding a few hundred classes pays a few milliseconds more at setup; a process that builds",
            "Books often pays it for every Book.",
        ], [
            "Land as measured unless the owner says otherwise; told in chat with the numbers.",
        ], "HELPFUL", 8)

    def s1(self) -> None:
        self.append_notes(self.S1, [self.tranche_note(), self.cost_note(), self.risk_note()], "s1 notes")
        self.set_field(self.S1, "Updated")
        text = self.read(self.S1)
        text = self.once(text, "- [ ] Task: red regression tests from P1-P10 and I1-I9.\n",
                         "- [x] Task: red regression tests from P1-P10 and I1-I9 (staged/tests; green on the mirror, "
                         "GIL off and on).\n", "s1 task tests")
        text = self.once(text, "- [ ] Task: implement and measure bind's cost.\n",
                         f"- [ ] Task: implement and measure bind's cost (measured, MEASURE note of {self.now}; "
                         "lands with S2).\n", "s1 task cost")
        text = self.once(text, (
            "- Next: test_ordered_disposal_replay.py, then (c) one object registered twice in 20 more files, (d)\n"
            "  the managed reversed premise, (e) the process-stability and two-frame tests; then the whole tree\n"
            "  with the GIL off and on, and the landing pass with S2, notched above 0.2.8256.\n"), (
            "- Done since: the tranche finished - the ordered-disposal replay (S2's MEASURE note of\n"
            "  2026-10-18T19:17:19Z), then (c), (d) and (e) in 20 files - and the whole tree green but melder_1's 18\n"
            f"  S8 tests, the GIL off and on (MEASURE note of {self.now}).\n"
            "- Done since: bind's cost measured - +37 to +55 us a bind, setup +9-10%, conjure and melds unchanged\n"
            f"  (MEASURE and RISK notes of {self.now}).\n"
            "- Next: the landing pass with S2 - src and tests into the repository, docs, the notches (read at\n"
            "  landing, above 0.2.8256), the release note, the rebuild last.\n"), "s1 summary")
        self.stage(self.S1, text)

    def s2(self) -> None:
        note = self.note(self.now, "FACT", [
            "S2's last failure is closed: the managed reversed premise is rewritten (batch one_object_b) - the same",
            "class bound unique, managed and managed with a limit is one spell_id and three bindings, each with its",
            "own binding hash (`test_a_managed_binding_keeps_the_spell_id_and_moves_the_binding_hash`). With the",
            "tranche done, the whole tree on the mirror fails only melder_1's 18 S8 tests, the GIL off and on (S1's",
            f"MEASURE note of {self.now}).",
        ], [
            self.whole(self.A + "/scripts/tests_edits_one_object_b.py"),
            f"context_compass/{self.RUNS}/tests_one_object_b_gil0.txt:1-1",
            f"context_compass/{self.RUNS}/tests_one_object_b_gil1.txt:1-1",
            self.whole(self.RUN2 + "/summary.txt"),
        ], [
            "S2's tests are green in the mirror; it lands with S1.",
        ], [
            "The landing pass with S1.",
        ], "REQUIRED", 8)
        self.append_notes(self.S2, [note], "s2 note")
        self.set_field(self.S2, "Updated")
        text = self.read(self.S2)
        text = self.once(text, (
            "- Next: S1's test tranche (the rest of (c), then (d) and (e)), which carries S2's last failure (the\n"
            "  managed reversed premise); then the landing pass with S1.\n"), (
            "- Done since: the managed reversed premise rewritten - one spell_id, three binding hashes - and the\n"
            f"  whole tree green but melder_1's 18 S8 tests, the GIL off and on (FACT note of {self.now}).\n"
            "- Next: the landing pass with S1 - src and tests into the repository, docs, notches, the rebuild last.\n"),
            "s2 summary")
        self.stage(self.S2, text)

    def epic(self) -> None:
        self.set_field(self.EPIC, "Updated")
        text = self.read(self.EPIC)
        text = self.once(text, (
            "- Next: (1) the test tranche - the retired API's tests, one object registered twice, the reversed\n"
            "  premises, the rest - then the whole tree with the GIL off and on; (2) the landing pass - src,\n"
            "  green, docs, notches, the rebuild last.\n"), (
            "- Done since: the test tranche finished in the mirror and the whole tree green but melder_1's 18 S8\n"
            "  tests, the GIL off and on; bind's cost measured, +37 to +55 us a bind (S1's MEASURE and RISK notes\n"
            f"  of {self.now}).\n"
            "- Next: the landing pass - src and tests into the repository, docs, notches, the release note, the\n"
            "  rebuild last; then M0-201 hands spellbook.py and spell.py back to melder_1 (M1-40).\n"),
            "epic summary")
        self.stage(self.EPIC, text)

    def row(self, text: str, prefix: str, pairs: List[Tuple[str, str]]) -> str:
        rows = [line for line in text.split("\n") if line.startswith(prefix)]
        if len(rows) != 1:
            sys.exit(f"ROW {prefix[:70]}: {len(rows)}")
        new = rows[0]
        for old, replacement in pairs:
            if new.count(old) != 1:
                sys.exit(f"ROW anchor {prefix[:40]}: {old[:60]}")
            new = new.replace(old, replacement)
        return text.replace(rows[0], new)

    def board(self) -> None:
        text = self.read(self.BOARD)
        text = self.row(text, "| spell_identity_is_the_code |", [
            ("| The test tranche in the /tmp mirror (the retired API, one object twice, the reversed premises), then "
             "the whole tree (GIL off and on) and the landing pass. |",
             "| The landing pass of S1 and S2 (src and tests into the repository, docs, notches, the rebuild last); "
             "the tranche and the whole tree are green in the mirror. |"),
            ("| 2026-10-18T18:44:20Z | REQUIRED |", f"| {self.now} | REQUIRED |")])
        text = self.row(text, "| spell_id_code_hash |", [
            ("| S1's test tranche in the mirror (the doubles and the retired API's tests done; 74 failed ids left), "
             "then the landing with S2. |",
             "| The landing with S2 (the tranche done; the whole tree green but S8's 18, GIL off and on; bind's cost "
             "measured). |"),
            ("| 2026-10-18T19:11:29Z | REQUIRED |", f"| {self.now} | REQUIRED |")])
        text = self.row(text, "| binding_manifest_hash |", [
            ("| S2's doubles and the ordered-disposal replay green in the mirror; the rest of the tranche with S1, "
             "then the landing with S1. |",
             "| The landing with S1 (S2's tests green in the mirror; the whole tree green but S8's 18). |"),
            ("| 2026-10-18T19:17:19Z | REQUIRED |", f"| {self.now} | REQUIRED |")])
        self.stage(self.BOARD, text)

    def artifacts(self) -> None:
        text = self.read(self.ARTIFACTS)
        s1_row = "| tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | "
        text = self.row(text, "| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | "
                              "artifacts/spell_identity_20261018/ |", [
            ("tests_edits_ordered_disposal.py and tests_edits_resolvable_registration.py (the test tranche: the "
             "doubles, the retired API's tests and the rewrites those files held);",
             "tests_edits_ordered_disposal.py, tests_edits_resolvable_registration.py, tests_edits_ordered_replay.py, "
             "tests_edits_one_object_a.py and tests_edits_one_object_b.py (the test tranche: the doubles, the retired "
             "API's tests, one object registered twice, the reversed premises and the rest);"),
            ("and record_whole_tree.py, record_bind_retirement.py and record_category_b.py (recorded);",
             "and record_whole_tree.py, record_bind_retirement.py, record_category_b.py, record_ordered_replay.py and "
             "record_tranche_done.py (recorded);"),
            ("| 2026-10-18T19:11:29Z | HELPFUL |", f"| {self.now} | HELPFUL |")])
        text = self.row(text, s1_row + "artifacts/spell_identity_20261018/probes/ |", [
            ("S1's tests start here. | 2026-10-18T13:42:22Z | REQUIRED |",
             "S1's tests start here; the bind-cost probes (probe_bind_cost.py, probe_bind_cost_profile.py) and their "
             "runs (runs/bind_cost/: the gauntlet and 200 classes, before and after, and the profiles). | "
             f"{self.now} | REQUIRED |")])
        text = self.row(text, s1_row + "artifacts/spell_identity_20261018/staged/ |", [
            ("the component test of spell identity) and runs/",
             "the component test of spell identity, and the support module `_spell_identity_test_support.py` with "
             "`version_of`) and runs/"),
            ("tests_bind_batch_gil0/1.txt, tests_category_b_gil0/1.txt). Deleted once",
             "tests_bind_batch_gil0/1.txt, tests_category_b_gil0/1.txt, tests_ordered_replay_gil0/1.txt, "
             "tests_one_object_a_gil0/1.txt, tests_one_object_b_gil0/1.txt). Deleted once"),
            ("| 2026-10-18T19:11:29Z | REQUIRED |", f"| {self.now} | REQUIRED |")])
        text = self.row(text, s1_row + "artifacts/spell_identity_20261018/blast_radius/ |", [
            ("the landing rewrites the tests by that triage. | 2026-10-18T18:44:20Z | REQUIRED |",
             "the landing rewrites the tests by that triage; whole_tree_s1s2_run2/ holds the rerun after the tranche "
             "(18 failed ids with the GIL off and on, all melder_1's S8 tests; the runs, the ids and their difference "
             f"from the first run). | {self.now} | REQUIRED |")])
        self.stage(self.ARTIFACTS, text)


def main() -> None:
    record = RecordTrancheDone("tranche_done")
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
