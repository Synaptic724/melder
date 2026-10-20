"""S3's validation, recorded (melder_0, 2026-10-19): a MEASURE note with the probes at the fix and the whole tree with
the GIL off and on against melder_1's 0.2.8260 runs, the pre-existing flake and the mounted-folder slowdown; the
resume view, the board row, and the run and script folders linked from the story and rowed on the artifact board.
All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class RecordS3Validation(Record):
    """S3's MEASURE note, its links and resume view, the board rows."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    RUNS = "artifacts/correctness_defects_20261017/runs/s3_fix"
    SCRIPTS = "artifacts/correctness_defects_20261017/scripts/s3_fix"
    BASE = "artifacts/book_teardown_parked_20261019/runs/full_tree_0_2_8260"

    def run_range(self, rel: str) -> str:
        count = len((self.ROOT / rel).read_text(encoding="utf-8").splitlines())
        if count == 0:
            sys.exit(f"EMPTY {rel}")
        return f"context_compass/{rel}:1-{count}"

    def src_range(self, rel: str, cls: str, meth: str) -> str:
        import ast
        src = (self.REPO / rel).read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == meth:
                        return f"{rel}:{item.lineno}-{item.end_lineno}"
        sys.exit(f"DEF {rel} {cls}.{meth}")

    def story(self) -> None:
        runs = [f"{self.RUNS}/{name}" for name in (
            "probe_cleanup_contract_doors_fix_gil0.txt", "probe_cleanup_contract_doors_fix_gil1.txt",
            "probe_index_unlink_leftovers_fix_gil0.txt", "probe_index_unlink_leftovers_fix_gil1.txt",
            "full_tree/unit_aether_gil0.txt", "full_tree/unit_spellbook_gil0.txt", "full_tree/unit_rest_gil0.txt",
            "full_tree_mirror/unit_aether_gil1.txt", "full_tree_mirror/unit_spellbook_gil1.txt",
            "full_tree/unit_rest_melder_gil1.txt", "full_tree/unit_rest_other_gil1.txt",
            "full_tree/component_gil0.txt", "full_tree_mirror/component_gil1.txt",
            "full_tree/component_agent_text_reader_gil1.txt",
            "full_tree/integ_aether_gil0.txt", "full_tree_mirror/integ_aether_gil1.txt",
            "full_tree/integ_conduit_spellbook_gil0.txt", "full_tree_mirror/integ_conduit_spellbook_gil1.txt",
            "full_tree_mirror/integ_rest_gil0.txt", "full_tree_mirror/integ_rest_gil1.txt",
            "full_tree/exp_and_misc_gil0.txt", "full_tree/exp_and_misc_gil1.txt",
            "full_tree_mirror/cluster_concurrency_flake_reruns_gil0.txt",
            "full_tree_mirror/cluster_concurrency_flake_reruns_pre_s3_gil0.txt",
            "full_tree/integ_crystallizer_gil0_verbose.txt",
            "full_tree_mirror/pod_death_mount_vs_mirror_gil0.txt")]
        evidence = [self.run_range(rel) for rel in runs]
        evidence.append(self.run_range(f"{self.BASE}/integ_aether_gil1.txt"))
        evidence.append(self.run_range(f"{self.BASE}/unit_gil1.txt"))
        evidence.append(self.src_range("src/melder/aether/spellbook/spellbook.py", "Spellbook",
                                       "_add_inactive_contracted_spell"))
        note = self.note(self.now, "MEASURE", [
            "S3's fix validated. Probes at the fix, the GIL off and on, the same output: after K1, K2, K4, K5 and K7 the",
            "borrower holds no entry, borrowed id or Detail of the cleaned version (K5 also drops the destroyed index's",
            "link); after K3 the borrower's meld of the cleaned Solo raises KeyError \"[MELD] No spell found with",
            "spell_id\", as for a version it never held; K6 (a direct `Spell.cleanup()`) is unchanged, out of scope. U1",
            "is unchanged; after U2's cleanup no French record is left, and the unlink and the sever leave nothing; U3's",
            "notch to French staged again completes on both sides and the borrower melds it ('bonjour'). The whole tree",
            "with the GIL off and on, against melder_1's 0.2.8260 runs: unit 9691 passed, 7 failed, 3 skipped, 7",
            "xfailed (the 7 are S8's red preface tests, failing in the baseline too); component 2406 passed, 23",
            "skipped, 1 xfailed (2403 + this lane's 3); integration aether with the GIL on 833 passed, 13 failed, 5",
            "xfailed (823 + this lane's 10; the 13 are melder_1's S8 red tests - 11 in the baseline, 13 with today's",
            "test file on 0.2.8260 too), with the GIL off 832 passed and one failure more,",
            "`test_concurrent_adds_of_same_conduit_admit_exactly_one`: timing-dependent, it fails on 0.2.8260 as well",
            "(1 of 10 reruns there, 3 of 15 here, the same assertion) and calls no cleanup_spell; integration conduit",
            "and spellbook 1031 passed; integration crystallizer, live_sim, multithreading and mutation_research 398",
            "passed, 4 xfailed; experimentation 250 passed, 4 skipped. That last integration shard timed out on the",
            "mounted folder at `test_pod_death_rebuilds_the_world_from_sqlite`, whose call takes 7.86 s there and",
            "1.31 s in a /tmp mirror on 0.2.8260 and with S3 alike - the mount, not the change - so it ran in the",
            "mirror. Seen, pre-existing and not S3's: a grant of a parked version adds every member id of its index to",
            "the borrower's borrowed ids (`_add_inactive_contracted_spell`) and its removal drops only its own, so",
            "after K2 English's id stays with no English entry."],
            evidence,
            ["No regression against 0.2.8260 in either GIL mode; the acceptance criteria hold (probes K and U). The",
             "flaky cluster test and the borrowed-ids leftover are for the owner."],
            ["The system documents, their indexes and the graph; the release note; the notch."], "REQUIRED", 9)
        self.append_notes(self.S3, [note], "s3 measure")
        text = self.read(self.S3)
        text = self.once(
            text,
            "  - system_docs/patches/active/cleanup_releases_contracts_2026_10_19/ (the patch, five docs)\n",
            "  - system_docs/patches/active/cleanup_releases_contracts_2026_10_19/ (the patch, five docs)\n"
            f"  - {self.RUNS}/ (red, green, probes at the fix, the whole tree)\n"
            f"  - {self.SCRIPTS}/ (the src apply script and the record passes)\n",
            "links")
        text = self.once(
            text,
            "  when S3 lands (M1-45, M1-46, M0-210).\n",
            "  when S3 lands (M1-45, M1-46, M0-210). Validated with the GIL off and on - the probes at the fix and the\n"
            f"  whole tree against 0.2.8260 (MEASURE note of {self.now}).\n",
            "state")
        text = re.sub(
            r"- Next: \(1\) the whole tree with the GIL on, then the validation note; \(2\) docs, the graph and the release\n"
            r"  note; \(3\) the notch to 0\.2\.8261 with no rebuild",
            "- Next: (1) the system documents, their indexes, the graph and the release note; (2) the notch to\n"
            "  0.2.8261 with no rebuild", text, count=1)
        if "- Next: (1) the system documents, their indexes, the graph and the release note;" not in text:
            sys.exit("NEXT")
        text = text.replace(
            "  DECISION note of 2026-10-19T11:48:58Z); (4) a NOTICE hands spellbook.py and conduit.py to melder_1; turn-in on\n"
            "  the owner's word.\n",
            "  DECISION note of 2026-10-19T11:48:58Z); (3) a NOTICE hands spellbook.py and conduit.py to melder_1; turn-in on\n"
            "  the owner's word.\n")
        if "(3) a NOTICE hands spellbook.py" not in text:
            sys.exit("NEXT 3")
        for line in text.split("\n"):
            if ("- Next: (1) the system documents" in line or "(3) a NOTICE hands spellbook.py" in line) \
                    and len(line) > 120:
                sys.exit(f"WIDTH next: {len(line)}")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def boards(self) -> None:
        text = self.read(self.BOARD)
        rows = re.findall(r"^\| parked_cleanup_contracts \|.*$", text, flags=re.M)
        if len(rows) != 1:
            sys.exit(f"ROW parked_cleanup_contracts: {len(rows)}")
        cells = rows[0].split(" | ")
        cells[2] = "implementation"
        cells[6] = ("Write the system docs, their indexes and the graph, and the release note; then notch 0.2.8261, "
                    "no rebuild (the owner).")
        cells[10] = self.now
        text = text.replace(rows[0], " | ".join(cells))
        self.stage(self.BOARD, text)
        board = self.read(self.ARTIFACTS)
        new_rows = (
            f"| {self.S3} | {self.RUNS}/ | validation_evidence | active | retain_as_reference | The fix's red and green "
            f"runs, the probes at the fix, the whole tree with the GIL off and on, the flake and mount reruns. | "
            f"{self.now} | HELPFUL |\n"
            f"| {self.S3} | {self.SCRIPTS}/ | scripts | active | retain_as_reference | apply_src.py (the src edits) and "
            f"the record passes of the landing. | {self.now} | HELPFUL |\n")
        board = self.once(board, "<!-- END USER-DEFINED: active_artifacts -->",
                          new_rows + "<!-- END USER-DEFINED: active_artifacts -->", "artifact rows")
        self.stage(self.ARTIFACTS, board)

    def run(self) -> None:
        self.story()
        self.boards()
        print("S3 MEASURE", self.note_range(self.S3, f"- DATETIME: {self.now}", "  TYPE: MEASURE"))


def main() -> None:
    record = RecordS3Validation("record_s3_validation")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
