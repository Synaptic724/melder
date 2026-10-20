"""Record the graph pass and the notches of S1 and S2 (melder_0, 2026-10-18). All-or-nothing; `--write` flushes."""
import sys

from docs_common import DocsRecord


class RecordGraphNotch(DocsRecord):
    """S1's and S2's notes and handoffs after the graph and the notches."""

    A = "artifacts/spell_identity_20261018/scripts"
    G = "system_docs/graph/melder/aether/spellbook/bind"

    def s1_note(self) -> str:
        return self.note(self.now, "FACT", [
            "The graph and the notches. Graph: extract --strict (593 descriptors, skipped 0) and assemble (593",
            "sections, 1231 nodes, every range verified, --check current); the four nodes of spell_code_digest.py and",
            "binding_manifest.py authored (unsemantic 13 -> 9) and the four statements in bind.json that described the",
            "retired fingerprint rewritten; none accepted - they report SEMANTICS_STALE until re-verified. Still stale",
            "prose about the retired fingerprint: binding_profile, binding_profile_strategy, inspector_utility and",
            "signature_reflection (their `fingerprint_repr` fields are gone from src). Notch: S1 is 0.2.8257, S2",
            "0.2.8258 (`__version__` 0.2.8258, read 0.2.8256 at landing); the running note's header and rebuild line",
            "name 0.2.8258, the Breaking S1 section and the S2 section sit before `## Packaging and documentation`, the",
            "bind-guard count reads 630, two packaging bullets (system documents, examples and docs) sit above",
            "melder_2's chapter bullet, which stays directly above the rebuild line; the board's notch notice says so.",
        ], [
            self.whole(self.A + "/land_graph_s1s2.py"),
            self.whole(self.A + "/notch_and_release_note.py"),
            self.whole(self.G + "/spell_code_digest.json"),
            self.whole(self.G + "/binding_manifest.json"),
            "src/melder/__version__.py:12-12",
            "release_docs/next_version_release.md:1-3",
        ], [
            "The source landing carries its version; what remains is the docs checks, the closure and the rebuild.",
            "The four stale fingerprint descriptors are a graph follow-up, not a landing blocker (the walker flags them).",
        ], [
            "The docs checks over both lanes' docs, then the closure, then the rebuild.",
        ], "REQUIRED", 8)

    def s2_note(self) -> str:
        return self.note(self.now, "FACT", [
            "S2 notched 0.2.8258 with S1's 0.2.8257 (S1's FACT note of this time); the running note's S2 section,",
            "\"A spell's binding is a manifest with its own hash\", names the two read-only properties, both cache tiers'",
            "key, record 4.3.0 and the restore report's binding_changes.",
        ], [
            "release_docs/next_version_release.md:1-3",
        ], [
            "S2's source is versioned and documented for users.",
        ], [
            "With S1: the docs checks, the closure, the rebuild last.",
        ], "HELPFUL", 7)


def main() -> None:
    record = RecordGraphNotch("graph_notch_record")
    record.append_notes(record.S1, [record.s1_note()], "s1 graph notch")
    record.append_notes(record.S2, [record.s2_note()], "s2 notch")
    for rel, old, new in (
        (record.S1, "- Next: the graph, the notches, the release note, the docs checks, the closure, the rebuild last.\n",
         f"- Done since: the graph, the notch (0.2.8257) and the release note (FACT note of {record.now}).\n"
         "- Next: the docs checks, the closure, the rebuild last.\n"),
        (record.S2, "- Next: with S1 - the graph, the notches, the release note, the docs checks, the closure, the\n"
                    "  rebuild last.\n",
         f"- Done since: notched 0.2.8258 with S1's 0.2.8257 (FACT note of {record.now}).\n"
         "- Next: with S1 - the docs checks, the closure, the rebuild last.\n"),
        (record.EPIC, "- Next: the graph, the notches, the release\n",
         f"- Done since: the graph, the notches (0.2.8257, 0.2.8258) and the release note (S1's FACT note of "
         f"{record.now}).\n- Next: the docs checks, the release\n"),
    ):
        record.stage(rel, record.once(record.read(rel), old, new, f"handoff {rel}"))
        record.set_field(rel, "Updated")
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
