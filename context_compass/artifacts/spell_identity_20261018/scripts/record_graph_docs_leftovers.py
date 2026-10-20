"""Record the identity landing's graph and docs leftovers (melder_0, 2026-10-19).

One FACT note on the epic: the thirteen descriptors rewritten by land_graph_leftovers.py, the eighteen nodes re-read
and accepted, the graph re-extracted (--strict) and reassembled, the walker's census, Spellbook and Spell left to
melder_1's S4 landing, the corrected sentence in docs/expert/governed-change.md and the two release-note sentences
(no notch: docs and graph only). All-or-nothing; `--write` flushes.
"""
import sys

from cc_record import Record


class RecordGraphDocs(Record):
    """The FACT note."""

    RUNS = "artifacts/spell_identity_20261018/runs/graph_leftovers"

    def lines_of(self, rel: str, needle: str) -> int:
        """Return the 1-based line of the one line of a repository file that contains `needle`."""
        lines = (self.REPO / rel).read_text(encoding="utf-8").split("\n")
        hits = [i + 1 for i, line in enumerate(lines) if needle in line]
        if len(hits) != 1:
            sys.exit(f"{rel} {needle[:40]}: {hits}")
        return hits[0]

    def run(self) -> None:
        """Append the note."""
        docs = "docs/expert/governed-change.md"
        note_rel = "release_docs/next_version_release.md"
        first = self.lines_of(docs, "A lookup by spell_id is exact:")
        last = self.lines_of(docs, "version an index has active is a lookup by the index")
        guide = self.lines_of(note_rel, "governed change (`docs/expert/governed-change.md`) says the same")
        graph = self.lines_of(note_rel, "helpers and the signature reader no longer describe the retired fingerprint")
        note = self.note(self.now, "FACT", [
            "The landing's graph and docs leftovers are done; no notch (docs and graph only). Thirteen descriptors",
            "rewritten (land_graph_leftovers.py, 31 operations): the five binding profiles, their builder and",
            "InspectorUtility no longer describe the retired fingerprint, SignatureReflection's statement names display",
            "text, Bind gains its SpellCodeDigest (owns_state and an owns_lifecycle_of edge) and loses the old",
            "inspector rule, SpellCodeDigest and BindingManifest gain their remaining contract lines, and",
            "SpellbookCreationSystem, RestoreReport, GraftRunner, SpellCrystal, RecordVersion and CachingSystem name",
            "the binding hash. Each node was re-read against its source - whole files for the new modules and the four",
            "fingerprint descriptors, the landing's diff for nodes accepted at 0.2.8256 - and the eighteen were",
            "accepted. extract --strict: 593 descriptors, 0 skipped, 0 new, 0 orphaned; assemble: 593 sections, 1231",
            "nodes, 1419 edges, check OK; the walker: AUTHORED 1001, stale 221 (was 983 and 239). extract --check",
            "exits 1 on the census alone (stale > 0; 0 skipped). Spellbook and Spell stay stale for melder_1's S4",
            "landing, whose change to both files (f86f84231) its own re-read covers. docs/expert/governed-change.md",
            "said a lookup by a parked spell_id returns the active member; it now says the lookup is exact and the",
            "index's active version is a lookup by the index (checked against Conduit.get_spell_by_spell_id and",
            "Spellbook.find_spell_by_spell_id). The release note's 0.2.8253 lookup bullet and the identity bullet",
            "carry the two corrections.",
        ], [
            f"context_compass/{self.RUNS}/extract.txt:1-6",
            f"context_compass/{self.RUNS}/assemble_check.txt:1-4",
            f"context_compass/{self.RUNS}/walker_report_by_file.txt:1-8",
            f"context_compass/{self.RUNS}/accept.txt",
            f"{docs}:{first}-{last}",
            f"{note_rel}:{guide}-{guide + 1}",
            f"{note_rel}:{graph - 1}-{graph}",
        ], [
            "The graph and the expert guide describe the landed identity; the rebuild will package them.",
        ], [
            "The whole-tree run on HEAD, GIL off and on.",
        ], "REQUIRED", 8)
        self.append_notes(self.EPIC, [note], "epic graph docs")
        self.set_field(self.EPIC, "Updated")


def main() -> None:
    record = RecordGraphDocs("graph_docs_leftovers")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
