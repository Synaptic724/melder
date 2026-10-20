"""S3 (melder_0, 2026-10-19): the K1-K7 probe as a MEASURE note, the patch's consumption mapping as a PLAN note, the
story's requirements, scope, acceptance, artifact links and resume view, the artifact board rows and the board row.

Patch: system_docs/patches/active/cleanup_releases_contracts_2026_10_19/. All-or-nothing; `--write` flushes.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record


class PatchNotes(Record):
    """S3's notes and lines; the artifact board; the attention board row."""

    S3 = "tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md"
    PATCH = "system_docs/patches/active/cleanup_releases_contracts_2026_10_19"
    PROBE = "artifacts/correctness_defects_20261017/probes/probe_cleanup_contract_doors.py"
    RUNS = ("artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil0.txt",
            "artifacts/correctness_defects_20261017/runs/probe_cleanup_contract_doors_gil1.txt")
    DOCS = ("architecture_patch.md", "component_patch_conduit_cleanup_spell.md",
            "component_patch_spellbook_dispose_spell.md", "component_patch_conduit_ward_spell_disposed.md",
            "code_description_patch_cleanup_spell.md")

    def story_lines(self) -> None:
        """Requirements, scope, checklist, acceptance, artifact links, resume view."""
        text = self.read(self.S3)
        text = self.once(
            text,
            "  all the spells that index shared\").\n\n## Requirements (Non-Functional)",
            "  all the spells that index shared\").\n"
            "- Every `cleanup_spell` door - a root conduit's, a lesser conduit's, the Spellbook's own - takes the version\n"
            "  out of every contract its Book's root conduit holds before it disposes it, version grants included, and\n"
            "  drops the index links when the index goes with it (the owner's go, 2026-10-19: \"check for active\n"
            "  contracts and then cleanup\").\n\n## Requirements (Non-Functional)",
            "requirement")
        text = self.once(
            text,
            "  decision, outside any transaction, under the ward lock - as it does for `remove_from_spell_index`.",
            "  decision and before the disposal, with no Book lock held, outside any transaction, under the ward lock - as\n"
            "  the index emissions run.",
            "non-functional")
        text = self.once(
            text,
            "- In scope: `Conduit.cleanup_spell`'s emission for a disposed parked member.\n"
            "- Out of scope: what index-link borrowers hold in general (melder_1's contract work); the binding-signature stories\n"
            "  of this epic.",
            "- In scope: the contract release of every `cleanup_spell` door - index-link members, parked or active, and\n"
            "  version grants - before the disposal (patch cleanup_releases_contracts_2026_10_19).\n"
            "- Out of scope: what index-link borrowers hold in general; the binding-signature stories of this epic; the\n"
            "  direct `Spell.cleanup()` and `cleanup_and_remove_spell` doors (probe K6, recorded for the owner).",
            "scope")
        text = self.once(
            text,
            "- [ ] Task: patch docs for the emission; the owner's approval.",
            "- [x] Task: patch docs (cleanup_releases_contracts_2026_10_19); the owner's go (chat 2026-10-19).",
            "checklist")
        text = self.once(
            text,
            "  the borrower is left with no active version).\n\n## Validation / Test Plan",
            "  the borrower is left with no active version).\n"
            "- After a lender's cleanup of a granted version, parked or active, the borrower holds no entry, id or Detail\n"
            "  of it, and its meld of it fails as for a version it never held (probes K2, K3).\n"
            "- `Spellbook.cleanup_spell` and a lesser conduit's `cleanup_spell` release the contracts as the root\n"
            "  conduit's does (probes K4, K5, K7); a refused cleanup touches no contract.\n\n## Validation / Test Plan",
            "acceptance")
        text = self.once(
            text,
            "  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_u3_trace_gil0.txt\n",
            "  - artifacts/correctness_defects_20261017/runs/probe_index_unlink_leftovers_u3_trace_gil0.txt\n"
            f"  - {self.PROBE} (cases K1-K7, 0.2.8260)\n"
            f"  - {self.RUNS[0]}\n"
            f"  - {self.RUNS[1]}\n"
            f"  - {self.PATCH}/ (the patch, five docs)\n",
            "artifact links")
        text = self.once(
            text,
            "- Next: (1) the open checks - what a borrower's removal reads from the version, grants of a disposed\n"
            "  version, the direct `Spell.cleanup()`; (2) the patch docs with the exact edits; (3) the fix, its tests\n"
            "  (GIL off and on), docs, notch and the rebuild last.",
            "- Next: (1) the tests, red on 0.2.8260; (2) the src edits of patch cleanup_releases_contracts_2026_10_19;\n"
            "  (3) green with the GIL off and on, the probes, the whole tree; (4) docs, graph, release note, notch and the\n"
            "  rebuild last.",
            "next")
        self.stage(self.S3, text)
        self.set_field(self.S3, "Updated")

    def story_notes(self) -> None:
        """The MEASURE and PLAN notes."""
        probe_lines = len((self.ROOT / self.PROBE).read_text(encoding="utf-8").rstrip("\n").split("\n"))
        run_lines = [len((self.ROOT / run).read_text(encoding="utf-8").rstrip("\n").split("\n")) for run in self.RUNS]
        measure = self.note(self.now, "MEASURE", [
            "Probe K1-K7 on 0.2.8260, the GIL off and on, the same output: which contracts keep a version its lender",
            "cleans up. K1, an index link, `Conduit.cleanup_spell` of parked French: the borrower keeps French's parked",
            "entry (cleaned), its borrowed id and the lender-side Detail. K2, a version grant of parked French: the",
            "same. K3, a version grant of Solo, the sole active member of its index: the borrower keeps an active entry",
            "holding the cleaned Solo, its id and the Detail, and its meld of Solo raises AttributeError ('Spell' object",
            "has no attribute '_resolvable'). K4, the direct `Spellbook.cleanup_spell` of French under an index link: as",
            "K1. K5, the direct door on Solo under an index link on Solo's index: the borrower keeps the cleaned active",
            "entry, the id, its tracked index of the destroyed index and both Details - that door sends not even the",
            "destroy. K6, a direct `French.cleanup()`: refused, RuntimeError \"Spellbook could not resolve the requested",
            "local spell.\" (`cleanup_and_remove_spell` resolves active versions only), nothing changed - outside S3,",
            "recorded for the owner. K7, `cleanup_spell` through a lesser conduit: as K1 - the emission runs on the",
            "calling conduit's ward, which holds no contracts."],
            [f"context_compass/{self.PROBE}:1-{probe_lines}",
             f"context_compass/{self.RUNS[0]}:1-{run_lines[0]}",
             f"context_compass/{self.RUNS[1]}:1-{run_lines[1]}",
             "src/melder/aether/conduit/conduit.py:6212-6264",
             "src/melder/aether/spellbook/spellbook.py:4481-4546",
             "src/melder/aether/spellbook/spellbook.py:718-737"],
            ["The fix covers every cleanup_spell door and both contract kinds (patch",
             "cleanup_releases_contracts_2026_10_19); K6's door stays as it is."],
            ["The tests, red on 0.2.8260."], "REQUIRED", 9)
        plan = self.note(self.now, "PLAN", [
            "Patch cleanup_releases_contracts_2026_10_19 consumed - architecture, the Conduit, Spellbook and ConduitWard",
            "component patches, the code-description patch - section -> implementation -> validation: (1) ConduitWard",
            "`_emit_spell_disposed`: the walk over the root ward's contracts with `_uncontract_member_spell` -> tests for",
            "a parked index-link member and a parked and an active grant; (2) Spellbook `_dispose_spell(release_contracts=",
            "...)`, called after the decision and refusals, inside the try -> unit tests: called between the decision",
            "and the disposal, not on a refusal, the mark cleared when it raises; (3) Conduit `cleanup_spell` through",
            "the Book's root ward, `_emit_index_destroy(index_id, ())` after a destroy -> tests for a sole member's",
            "index link and a lesser conduit's call; (4) Spellbook `cleanup_spell` through the root conduit when",
            "conjured -> tests for the direct door, parked and sole; (5) the invariants (contracts first; a refusal",
            "touches none) -> the order and refusal tests; (6) migration -> red on 0.2.8260, green with the GIL off and",
            "on, probes K1-K7 and U1-U3, the related suites, the whole tree; docs, graph, release note, notch, rebuild."],
            [f"context_compass/{self.PATCH}/{name}:1-{self.lines(name)}" for name in self.DOCS],
            ["Implementation may start: the patch docs exist and are linked, and the owner gave the go."],
            ["Write the tests and run them red on 0.2.8260."], "REQUIRED", 9)
        self.append_notes(self.S3, [measure, plan], "s3 notes")

    def lines(self, name: str) -> int:
        """Line count of one patch doc."""
        return len((self.ROOT / self.PATCH / name).read_text(encoding="utf-8").rstrip("\n").split("\n"))

    def boards(self) -> None:
        """Two artifact rows; S3's attention row to implementation."""
        rows = (
            f"| {self.S3} | {self.PROBE} | defect_reproducer | active | retain_as_reference | Cases K1-K7 (which "
            f"contracts keep a disposed version, by contract kind and cleanup door) on 0.2.8260 with their runs "
            f"(runs/probe_cleanup_contract_doors_gil0.txt, _gil1.txt); re-run at the fix. | {self.now} | REQUIRED |\n"
            f"| {self.S3} | {self.PATCH}/ | patch_doc | active | promote_to_documentation | Architecture, three component "
            f"and one code-description patch for the contract release of every cleanup_spell door; the owner's go "
            f"(chat 2026-10-19). | {self.now} | REQUIRED |")
        text = self.read(self.ARTIFACTS)
        text = self.once(text, "\n<!-- END USER-DEFINED: active_artifacts -->",
                         "\n" + rows + "\n<!-- END USER-DEFINED: active_artifacts -->", "artifact rows")
        self.stage(self.ARTIFACTS, text)
        board = self.read(self.BOARD)
        found = re.findall(r"^\| parked_cleanup_contracts \|.*$", board, flags=re.M)
        if len(found) != 1:
            sys.exit(f"ROW parked_cleanup_contracts: {len(found)}")
        cells = found[0].split(" | ")
        cells[2] = "implementation"
        cells[6] = ("Write the symptom-named tests red on 0.2.8260, then the src edits of patch "
                    "cleanup_releases_contracts_2026_10_19.")
        cells[10] = self.now
        self.stage(self.BOARD, board.replace(found[0], " | ".join(cells)))


def main() -> None:
    record = PatchNotes("s3_patch_and_probe_notes_20261019")
    record.story_lines()
    record.story_notes()
    record.boards()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
