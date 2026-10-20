"""Record the examples' rewrite on S1, its turn on S2 and the epic, and refresh the three routing rows (melder_0).

S1 gets a MEASURE note: rewrite_ux_examples.py applied to a fresh mirror copy of the repository's examples and run
with the GIL off and on (only the 4 rows outside identity red), then applied to the repository byte for byte. The
handoffs of S1, S2 and the epic and the board's three rows of this landing name the next step, the docs sweep.
All-or-nothing; `--write` flushes.
"""
import re
import sys

from record_ux_sweep import RecordUxSweep


class RecordUxRewrite(RecordUxSweep):
    """The examples' rewrite, recorded."""

    SCRIPTS = "artifacts/spell_identity_20261018/scripts"

    def measure_note(self) -> str:
        """The rewrite as applied, its runs and the repository's copy."""
        ux = self.UX
        return self.note(self.now, "MEASURE", [
            "The examples' rewrite is in the repository (rewrite_ux_examples.py, one all-or-nothing pass over 15",
            "files, each kept CRLF). Six lessons bind one class per world or Book: advanced 02 a subclass per tenant",
            "at one address (spellframe \"tenant\", binding_name \"cache\"), advanced 16 DynamicPayload, expert 11 a",
            "Ledger subclass per frame, intermediate 31 BareService, intermediate 37 OtherLedger; expert 16's `_pair`",
            "binds nothing and its two posture refusals print one sentence, as before. The probes follow: lesson",
            "02's row asserts both halves (one class in two worlds refused at the second conjure; a class per world",
            "at one address, one singleton each), a new row pins the per-frame regime in a reset world (one class,",
            "one spell_id, two singletons), the with-book row binds AfterWith, the config and cloud rows bind",
            "classes of their own, and the three identity contract rows are flipped and renamed (same name with",
            "other code: two spells; one class rebound by binding_name or spellframe: refused at bind). The text",
            "that taught the retired rule is rewritten: beginner 18, 24 and 30, expert 13 and 26, and AGENTS.md (its",
            "divergence flag closed into the identity law). Run on a fresh copy of the repository's examples",
            "(melder_2's 42-48 included) with clean caches: 4 failed and 623 passed, the GIL off and on - exactly",
            "the 4 rows outside identity (beginner 39, expert 37's header, the expert probe",
            "two_visible_spells_may_not_share_a_name, the intermediate probe",
            "upgrade_to_normal_keeps_creations_and_registers); lesson 31 prints the exception types 0.2.8256 printed",
            "(KeyError, RuntimeError, RuntimeError, ValueError). The repository's 15 files were byte-identical to",
            "the mirror's originals when the same script wrote them, and the two examples trees are identical after.",
        ], [
            self.whole(self.SCRIPTS + "/rewrite_ux_examples.py"),
            self.whole(self.RUNS + "/ux_rewrite_gil0.txt"),
            self.whole(self.RUNS + "/ux_rewrite_gil1.txt"),
            self.whole(self.RUNS + "/ux_rewrite.diff"),
            self.span(ux + "/03_advanced/02_frames_as_worlds.py", "def main() -> None:"),
            self.span(ux + "/04_expert/16_rewiring_a_running_world.py", "def _pair("),
            self.span(ux + "/pytest_examples/test_advanced_probes.py",
                      "def test_probe_frames_isolate_instances_but_not_identity("),
            self.span(ux + "/pytest_examples/test_advanced_probes.py",
                      "def test_probe_per_frame_spell_ids_let_one_class_live_in_two_worlds("),
            self.span(ux + "/pytest_examples/test_contract_probes.py",
                      "def test_probe_same_name_different_internals_are_two_spells("),
            self.span(ux + "/pytest_examples/test_contract_probes.py",
                      "def test_probe_same_class_rebind_is_refused_at_bind("),
            self.span(ux + "/pytest_examples/test_contract_probes.py",
                      "def test_probe_same_class_rebind_across_spellframes_is_refused_at_bind("),
            self.lines_of(ux + "/AGENTS.md", "SPELL IDENTITY IS THE CODE (0.2.8257)", "the flag is closed."),
        ], [
            "The examples teach S1's contract and are red only where they were at 0.2.8256; the docs site renders",
            "the rewritten lesson text (TIER, GOAL and SURFACE EXERCISED are what its catalog reads).",
        ], [
            "The docs sweep: a NOTICE to melder_2 naming the docs/ files and the README section, then",
            "docs/advanced/worlds.md and the other candidates corrected to S1.",
        ], "REQUIRED", 9)

    def handoffs(self) -> None:
        """S1, S2 and the epic: what is done and the next step."""
        s1 = self.read(self.S1)
        s1 = self.once(s1, (
            "- Next: the examples rewritten and run (GIL off and on), the tests system documents and the\n"
            "  source follow-ups, the docs sweep, the graph, the notches, the release note, the closure, the\n"
            "  rebuild last.\n"), (
            "- Done since: the examples rewritten and run - 4 failed and 623 passed with the GIL off and on,\n"
            f"  the 4 rows outside identity - and applied to the repository (MEASURE note of {self.now}).\n"
            "- Next: the docs sweep (melder_2 told first), the tests system documents and the source\n"
            "  follow-ups, the graph, the notches, the release note, the closure, the rebuild last.\n"), "s1 handoff")
        self.stage(self.S1, s1)
        s2 = self.read(self.S2)
        s2 = self.once(s2, (
            "- Next: with S1 - the examples rewritten, the tests system documents, the graph, the notches, the\n"
            "  release note, the closure, the rebuild last.\n"), (
            f"- Done since: the examples rewritten with S1 (S1's MEASURE note of {self.now}).\n"
            "- Next: with S1 - the docs sweep, the tests system documents, the graph, the notches, the release\n"
            "  note, the closure, the rebuild last.\n"), "s2 handoff")
        self.stage(self.S2, s2)
        epic = self.read(self.EPIC)
        epic = self.once(epic, (
            "- Next: the examples swept and run, the tests system documents and the source follow-ups, the\n"
            "  graph, the notches, the release note, the closure, the rebuild last; then a NOTICE hands\n"), (
            f"- Done since: the examples rewritten and run (S1's MEASURE note of {self.now}).\n"
            "- Next: the docs sweep, the tests system documents and the source follow-ups, the graph, the\n"
            "  notches, the release note, the closure, the rebuild last; then a NOTICE hands\n"), "epic handoff")
        self.stage(self.EPIC, epic)
        for rel in (self.S1, self.S2, self.EPIC):
            self.set_field(rel, "Updated")

    def board(self) -> None:
        """The three routing rows of this landing: the next step and the time."""
        text = self.read(self.BOARD)
        rows = {
            "spell_identity_is_the_code": "The docs sweep, then the tests system documents and the src follow-ups, the graph, "
                                          "the notches, the release note, the closure; the rebuild last.",
            "spell_id_code_hash": "With S2: the docs sweep, the tests system documents, the graph, the notches, the "
                                  "release note, the closure, the rebuild last (the examples are rewritten and run).",
            "binding_manifest_hash": "With S1: the docs sweep, the tests system documents, the graph, the notches, the "
                                     "release note, the closure, the rebuild last.",
        }
        for item, nxt in rows.items():
            found = re.findall(rf"^\| {item} \| .*\|$", text, flags=re.M)
            if len(found) != 1:
                sys.exit(f"ROW {item}: {len(found)}")
            cells = found[0].split(" | ")
            # | work_item | status | mode | owner | agent_name | blocker | next | outcome | exit | ticket | at | reread |
            cells[6] = nxt
            cells[10] = self.now
            text = text.replace(found[0], " | ".join(cells))
        self.stage(self.BOARD, text)

    def run(self) -> None:
        """Stage the note, the handoffs and the rows."""
        self.append_notes(self.S1, [self.measure_note()], "s1 ux rewrite")
        self.handoffs()
        self.board()


def main() -> None:
    record = RecordUxRewrite("ux_rewrite")
    record.run()
    record.resync()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
