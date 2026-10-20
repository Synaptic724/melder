"""Record S1's docs sweep and what it found outside S1 (melder_0, 2026-10-18).

S1 gets a FACT note (five pages corrected - glossary, troubleshooting, the inspection walkthrough, configuration
and the README's Frame Boundaries section - and the disposal sentence beside the configuration edit) and a FACT
note on a stale sentence outside this landing (governed-change.md on parked spell_id lookups, stale since
0.2.8253). The handoffs of S1, S2 and the epic and the board's three rows name the next step. All-or-nothing;
`--write` flushes.
"""
import re
import sys

from record_ux_sweep import RecordUxSweep


class RecordDocsSweep(RecordUxSweep):
    """The docs sweep, recorded."""

    SCRIPTS = "artifacts/spell_identity_20261018/scripts"
    DOCS_RUNS = "artifacts/spell_identity_20261018/runs/docs_sweep"

    def sweep_note(self) -> str:
        """The five pages and the disposal sentence."""
        return self.note(self.now, "FACT", [
            "The user docs no longer teach the retired identity rule (rewrite_docs_identity.py, one all-or-nothing",
            "pass; each page keeps its CRLF, README.md its mixed endings region by region). The glossary's Aetheric",
            "frame entry says frame isolation does not namespace spell identity, and a new Spell ID entry defines it",
            "(the object's code; nothing from the bind call; the binding has its own hash); the troubleshooting row",
            "reads \"One class is refused in a second world or under a second name\" with its cause; the inspection",
            "walkthrough's step 1 follows advanced 02 (a cache class per world at one address); configuration says a",
            "receiving policy keeps the spell ID and changes the binding hash, listed under the restore's",
            "`binding_changes`; the README's Frame Boundaries section - which the docs site renders as the",
            "advanced/worlds chapter - binds a class per world and names the per-frame regime. Beside the replay",
            "edit, configuration's disposal sentence said a failing method stops the object's remaining methods;",
            "since 0.2.80 every declared method runs and the failures are raised together as one ExceptionGroup",
            "once the store's cleanup ends (fix_docs_disposal_sentence.py). melder_2 was told first (M0-203); none of",
            "the pages is one of its six. The docs checks (unit tests, check, build -W, check_site) run over the",
            "whole change before the rebuild.",
        ], [
            self.whole(self.SCRIPTS + "/rewrite_docs_identity.py"),
            self.whole(self.SCRIPTS + "/fix_docs_disposal_sentence.py"),
            self.whole(self.DOCS_RUNS + "/docs_identity.diff"),
            self.lines_of("docs/reference/glossary.md", "   Aetheric frame", "so one class bound in two frames"),
            self.lines_of("docs/reference/glossary.md", "   Spell ID", "how it is bound has its own binding hash"),
            self.lines_of("docs/reference/troubleshooting.md", "| One class is refused in a second world",
                          "| One class is refused in a second world"),
            self.lines_of("docs/advanced/inspection-walkthrough.md", "1. Build two isolated cache worlds",
                          "Compare the instances"),
            self.lines_of("docs/intermediate/configuration.md", "Existing scope/key/bucket teardown order",
                          "the restore report lists that binding"),
            self.lines_of("README.md", "Bind a distinct class in each world", "spell IDs are then unique per frame."),
            "src/melder/aether/conduit/creations/creations.py:326-399",
            "src/melder/aether/conduit/creations/creations.py:401-449",
        ], [
            "A reader of the docs site meets the same rule the code enforces: a class per world, or the per-frame",
            "regime; a binding_name never makes one class two spells.",
        ], [
            "The tests system documents and the source follow-ups.",
        ], "HELPFUL", 8)

    def stale_note(self) -> str:
        """The stale sentence found outside this landing."""
        return self.note(self.now, "FACT", [
            "Found by the docs sweep, outside S1 and left as found: docs/expert/governed-change.md says \"a lookup",
            "by a parked spell_id returns the currently active member\" - true until 0.2.8253, when",
            "`Spellbook.find_spell_by_spell_id` (and the Conduit lookup through it) became exact: a parked",
            "spell_id answers the parked version itself, never its index's active member. The page belongs to the",
            "governed-change chapter, not to this sweep's five, and M0-203 named only those; it goes to the owner",
            "with the landing report.",
        ], [
            self.lines_of("docs/expert/governed-change.md", "Promotion is `notch_spell(spell_index=...",
                          "spell_id: a lookup by a parked spell_id returns the currently active member."),
            self.span("src/melder/aether/spellbook/spellbook.py", "    def find_spell_by_spell_id("),
        ], [
            "A reader of that chapter expects a parked spell_id lookup to answer the active version and would",
            "notch or meld the wrong one; the code answers the version the spell_id names.",
        ], [
            "Name it in the landing report; the owner decides who corrects it.",
        ], "HELPFUL", 7)

    def handoffs(self) -> None:
        """S1, S2 and the epic: what is done and the next step."""
        replacements = (
            (self.S1, "- Next: the docs sweep (melder_2 told first), the tests system documents and the source\n"
                      "  follow-ups, the graph, the notches, the release note, the closure, the rebuild last.\n",
             f"- Done since: the docs sweep - five pages and the README section (FACT notes of {self.now}).\n"
             "- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n"
             "  note, the docs checks, the closure, the rebuild last.\n"),
            (self.S2, "- Next: with S1 - the docs sweep, the tests system documents, the graph, the notches, the release\n"
                      "  note, the closure, the rebuild last.\n",
             "- Next: with S1 - the tests system documents, the graph, the notches, the release note, the docs\n"
             "  checks, the closure, the rebuild last.\n"),
            (self.EPIC, "- Next: the docs sweep, the tests system documents and the source follow-ups, the graph, the\n"
                        "  notches, the release note, the closure, the rebuild last; then a NOTICE hands\n",
             f"- Done since: the docs sweep (S1's FACT notes of {self.now}).\n"
             "- Next: the tests system documents and the source follow-ups, the graph, the notches, the release\n"
             "  note, the docs checks, the closure, the rebuild last; then a NOTICE hands\n"),
        )
        for rel, old, new in replacements:
            self.stage(rel, self.once(self.read(rel), old, new, f"handoff {rel}"))
            self.set_field(rel, "Updated")

    def board(self) -> None:
        """The three routing rows: the next step and the time."""
        text = self.read(self.BOARD)
        rows = {
            "spell_identity_is_the_code": "The tests system documents and the src follow-ups, the graph, the notches, the "
                                          "release note, the docs checks, the closure; the rebuild last.",
            "spell_id_code_hash": "With S2: the tests system documents, the graph, the notches, the release note, the "
                                  "docs checks, the closure, the rebuild last (examples and docs swept).",
            "binding_manifest_hash": "With S1: the tests system documents, the graph, the notches, the release note, the "
                                     "docs checks, the closure, the rebuild last.",
        }
        for item, nxt in rows.items():
            found = re.findall(rf"^\| {item} \| .*\|$", text, flags=re.M)
            if len(found) != 1:
                sys.exit(f"ROW {item}: {len(found)}")
            cells = found[0].split(" | ")
            if len(cells) != 12:
                sys.exit(f"ROW {item}: {len(cells)} cells")
            cells[6] = nxt
            cells[10] = self.now
            text = text.replace(found[0], " | ".join(cells))
        self.stage(self.BOARD, text)

    def run(self) -> None:
        """Stage the notes, the handoffs and the rows."""
        self.append_notes(self.S1, [self.sweep_note(), self.stale_note()], "s1 docs sweep")
        self.handoffs()
        self.board()


def main() -> None:
    record = RecordDocsSweep("docs_sweep")
    record.run()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
