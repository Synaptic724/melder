"""Record S2's MEASURE of the ordered-disposal replay rewrite (melder_0, 2026-10-18). One all-or-nothing pass:
the note, S2's handoff summary and its board row."""
import sys

from cc_record import Record


class RecordOrderedReplay(Record):
    RUNS = "artifacts/spell_identity_20261018/staged/runs"
    BATCH = "artifacts/spell_identity_20261018/scripts/tests_edits_ordered_replay.py"
    REPLAY = "tests/integration/melder/crystallizer/test_ordered_disposal_replay.py"
    SESSION_NOTES = Record.SESSION_NOTES + ("2026-10-18T17:51:07Z", "2026-10-18T18:08:26Z", "2026-10-18T18:40:11Z",
                                            "2026-10-18T18:44:16Z", "2026-10-18T18:48:19Z", "2026-10-18T19:11:29Z")

    def s2(self) -> None:
        note = self.note(self.now, "MEASURE", [
            "The ordered-disposal replay asserts S2's restore report end to end: a Book restored under another",
            "disposal policy keeps both members' spell_ids (none enters the identity map), reports each member's",
            "binding change - recorded and live hash, live equal to the restored spell's `binding_hash` - and",
            "resolves the requested parked selection and the regranted contract; a restore under the recorded",
            "policy reports no binding change. The captured index's staged member is a second version of the",
            "service (`StagedDisposalService`, module level, bound under the service's address), because staging",
            "the service again is refused; restore and graft import it by module and qualname. Two tests that",
            "asserted translated ids are renamed for what they assert now (`..._under_another_policy_...`).",
            "Batch ordered_replay (15 edits) closes the file's 23 failed ids: 23 pass, the GIL off and on.",
        ], [
            f"context_compass/{self.RUNS}/tests_ordered_replay_gil0.txt:1-1",
            f"context_compass/{self.RUNS}/tests_ordered_replay_gil1.txt:1-1",
            self.whole(self.BATCH),
            f"context_compass/{self.RUNS}/mirror_s1s2_src.diff:1597-1877",
        ], [
            "S2's restore contract (record 4.3.0: kept ids, binding changes reported, never a shortfall) is",
            "under test; S2's remaining failure is the managed reversed premise (d).",
        ], [
            "With S1's tranche: (c) in the 20 other files, then (d) and (e).",
        ], "REQUIRED", 8)
        self.append_notes(self.S2, [note], "s2 measure")
        self.set_field(self.S2, "Updated")
        text = self.read(self.S2)
        text = self.once(text, (
            "- Next: S1's test tranche (categories b-e), which carries S2's remaining tests (the ordered-disposal\n"
            "  replay's binding changes); then the landing pass with S1.\n"), (
            f"- Done since: the ordered-disposal replay rewritten - kept ids and the reported binding changes,\n"
            f"  23 green with the GIL off and on (MEASURE note of {self.now}).\n"
            "- Next: S1's test tranche (the rest of (c), then (d) and (e)), which carries S2's last failure (the\n"
            "  managed reversed premise); then the landing pass with S1.\n"), "s2 summary")
        self.stage(self.S2, text)

    def board(self) -> None:
        text = self.read(self.BOARD)
        rows = [line for line in text.split("\n") if line.startswith("| binding_manifest_hash |")]
        if len(rows) != 1:
            sys.exit(f"ROW binding_manifest_hash: {len(rows)}")
        new = rows[0].replace(
            "| S2's doubles green in the mirror; the rest of the tranche with S1, then the landing with S1. |",
            "| S2's doubles and the ordered-disposal replay green in the mirror; the rest of the tranche with S1, "
            "then the landing with S1. |").replace("| 2026-10-18T18:44:20Z | REQUIRED |", f"| {self.now} | REQUIRED |")
        if new == rows[0] or self.now not in new:
            sys.exit("ROW binding_manifest_hash unchanged")
        self.stage(self.BOARD, text.replace(rows[0], new))


def main() -> None:
    record = RecordOrderedReplay("ordered_replay")
    record.s2()
    record.board()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
