"""Record the staged-copy cleanup of 2026-10-18 (melder_0): the runs restored, the eight duplicates deleted.

The turn-in of S1 and S2 moved all of `artifacts/spell_identity_20261018/staged/` into `_to_delete/`, but its `runs/`
holds run evidence that S1's, S2's and melder_1's minted-index story Notes cite at `staged/runs/...`. This pass
records that `runs/` went back to `staged/runs/` (`mv -n`), that the two modules and six tests - byte-identical to the
files committed in 5e3800c7a (`cmp`) - were deleted with the owner's permission (chat, 2026-10-18), and that their
citations resolve at the same relative path from the repository root. One FACT note on the epic and two artifact-board
rows. All-or-nothing; `--write` flushes.
"""
import sys

from cc_record import Record


class CleanupStaged(Record):
    """The FACT note and the artifact-board rows."""

    OLD_ROW = ("| tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md | "
               "artifacts/spell_identity_20261018/_to_delete/staged/ | delete_on_close | Moved with mv -n into "
               "_to_delete/ (deletes need the owner's permission); the modules and tests are in the repository "
               "(5e3800c7a). | 2026-10-18T23:31:15Z |")

    def board(self) -> None:
        """Replace the staged/ row with the restored runs' row and the deleted duplicates' row."""
        text = self.read(self.ARTIFACTS)
        deleted = ("| tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md | "
                   "artifacts/spell_identity_20261018/_to_delete/staged/ | delete_on_close | Deleted with the owner's "
                   "permission: the two modules and six tests, byte-identical to the files committed in 5e3800c7a "
                   "(cmp); citations into staged/src/ and staged/tests/ resolve at the same path from the "
                   f"repository root. _to_delete/ is gone. | {self.now} |")
        runs = ("| tickets/stories/completed/2026-10-18_spell_id_hashes_the_object_code_story.md | "
                "artifacts/spell_identity_20261018/staged/runs/ | retain_as_reference | Restored from _to_delete/ "
                "with mv -n: S1 and S2's run evidence (digest cases, corpus, stability, the mirror diff and smoke "
                "runs, the test batches), cited at staged/runs/ by both stories and by "
                f"STORY-2026-10-17-minted_index_missing_from_frame_registry. | {self.now} |")
        text = self.once(text, self.OLD_ROW + "\n", runs + "\n" + deleted + "\n", "staged row")
        self.stage(self.ARTIFACTS, text)

    def epic(self) -> None:
        """The FACT note."""
        lines = self.read(self.ARTIFACTS).split("\n")
        rows = [i + 1 for i, line in enumerate(lines) if "artifacts/spell_identity_20261018/staged/runs/ |" in line
                or "artifacts/spell_identity_20261018/_to_delete/staged/ |" in line]
        if len(rows) != 2:
            sys.exit(f"rows {rows}")
        note = self.note(self.now, "FACT", [
            "The staged copies are cleaned, and the run logs the turn-in parked with them are back where they are",
            "cited. S1 and S2's turn-in moved all of staged/ into _to_delete/, but staged/runs/ holds 25 files - run",
            "logs, the mirror diff and two run scripts - and S1's, S2's and melder_1's minted-index story Notes cite",
            "17 of them at staged/runs/, all missing after the move. runs/ went back with mv -n and every cited path",
            "resolves again. The two modules and six tests, compared byte for byte with the files committed in",
            "5e3800c7a (all identical), were deleted with the owner's permission, with the empty _to_delete/",
            "folders; a citation into staged/src/ or staged/tests/ resolves at the same relative path from the",
            "repository root (src/..., tests/...), and git keeps the copies at 5e3800c7a.",
        ], [
            f"context_compass/{self.ARTIFACTS}:{rows[0]}-{rows[1]}",
            "context_compass/artifacts/spell_identity_20261018/staged/runs/",
        ], [
            "The turn-in's cleanup no longer breaks evidence pointers in closed stories; nothing that was only in",
            "the staged copies is lost.",
        ], [
            "The graph leftovers: the four descriptors that still describe the retired fingerprint.",
        ], "HELPFUL", 7)
        self.append_notes(self.EPIC, [note], "epic cleanup")
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = CleanupStaged("cleanup_staged")
    record.board()
    record.epic()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
