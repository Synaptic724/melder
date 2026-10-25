"""Record the 0.2.8267 re-measure of the notch-fan-out race into its task (melder_0, 2026-10-25).

One all-or-nothing pass: a MEASURE and a FACT note on the race child task, naming the rate and kinds reruns on a /tmp
copy of the 0.2.8267 tree (the GIL off and on) and confirming melder_1's mechanism still holds at today's lines; the
task's Updated field and Context / Handoff Summary; the notch_fanout_race board row's `next`. Refuses when a file
changed since it was read or a line breaks the width rule. Usage: record_race_remeasure_20261025.py --check | --apply
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

RACE = "tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md"
RUNS = "artifacts/notch_fanout_race_20261025/runs/"


class Pass(Record):
    @staticmethod
    def check_width(block: str, label: str) -> None:
        """As Record.check_width, but also exempt a lone unbreakable path bullet (`  - a/b/c.py:1-2`).

        `configuration_standards.md` exempts unbreakable tokens (paths, IDs, URLs) from the 120-char line width;
        the base helper exempts only `context_compass/` paths and table rows, so a long `src/...py:range` evidence
        bullet trips it though the contract allows it. A bullet whose content after `- ` holds no space is such a
        token.
        """
        import sys as _sys
        for line in block.split("\n"):
            if len(line) <= 120 or "context_compass/" in line or line.startswith("| ") or line.startswith("|---"):
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and " " not in stripped[2:]:
                continue
            _sys.exit(f"WIDTH {label}: {len(line)}: {line}")

    def checked_flush(self, apply: bool) -> None:
        for rel, before in self.original.items():
            if (self.ROOT / rel).read_text(encoding="utf-8") != before:
                sys.exit(f"RACE {rel}: changed since it was read; nothing written")
        for rel, text in self.staged.items():
            if "\r" in text:
                sys.exit(f"CR in {rel}")
        if not apply:
            for rel, text in self.staged.items():
                print("would write", rel, len(text.split("\n")) - 1, "lines")
            print("checked; nothing written")
            return
        self.flush()


def notes(r: Pass) -> str:
    measure = r.note(r.now, "MEASURE", [
        "Re-measured on a /tmp copy of the 0.2.8267 working tree (git 9f240166f), Python 3.14.7 free-threaded.",
        "probe_rule2_race_rate.py <tree> 20: GIL off, 10 of 20 runs end a thread with an unexpected exception (12x",
        "AttributeError \"'SpellContract' object has no attribute 'ping'\", 6x RuntimeError \"Cannot build",
        "CreationContext before spell_codegen_creation exists.\"); no meld returned B, the first meld after each race",
        "returned A. GIL on, 0 of 20. diag_race_kinds.py <tree> 400 150: GIL off, 200 of 400 runs end a thread",
        "unexpected - 265x the SpellContract AttributeError, 75x the CreationContext RuntimeError, 11x RuntimeError",
        "\"many_only manifest references unknown spell_id\", and 1x RuntimeError \"No-overrides codegen step schema",
        "references unknown spell_id\" (a sibling of the many_only kind, from the generalized/no-overrides hydrator;",
        "not seen on 2026-10-16). The race reproduces unchanged at 0.2.8267; the retired scan's MeldExecutionError",
        "melder_1 saw before rule 2 is gone, as expected."],
        [RUNS + "probe_rule2_race_rate_0_2_8267_gil0.txt:1-30",
         RUNS + "probe_rule2_race_rate_0_2_8267_gil1.txt:24-27",
         RUNS + "diag_race_kinds_0_2_8267_gil0.txt:211-216"],
        ["The race holds at the same rate on today's tree, so the design decision rests on current behaviour."],
        ["Confirm the mechanism at today's lines (next note)."], "REQUIRED", 8)
    fact = r.note(r.now, "FACT", [
        "melder_1's mechanism holds at 0.2.8267, read at today's lines. `Conduit.notch_spell` calls",
        "`mediator.end_transaction(expected_type=\"notch\", success=True)` and only THEN, outside the transaction,",
        "runs the borrower fan-out - `_deactivate_borrowed_spell(outgoing_id)`, `_activate_borrowed_spell(...)` and",
        "`ConduitWard._emit_index_notch(...)` - so a borrower meld already past its creation gate is not ordered",
        "against the park and the reactivate. The diag timelines show exactly that interleave (a meld's pass-done /",
        "ctx-built landing between deactivate and reactivate). The two sites melder_1 named are confirmed: Phase 8's",
        "`_allow_missing_contract_providers` (site a, the raw SpellContract default compiled while a copy is parked)",
        "and the many_only hydrator's `_resolve_spell_lookup`, which raises \"many_only manifest references unknown",
        "spell_id\" when a plan names a parked version (site b); the new 4th kind is the same site b in the",
        "no-overrides hydrator. The two designs (refuse at the sites, or order the fan-out under the borrowers'",
        "frozen gates) are unchanged; the whole-read of the fan-out and gates and the in-Book probe are the next",
        "tranche before the design is costed for the owner."],
        ["src/melder/aether/conduit/conduit.py:5792-5801",
         "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:321-340",
         "src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1073-1088",
         RUNS + "diag_race_kinds_0_2_8267_gil0.txt:5-35"],
        ["The fix is one of the two designs, after the owner decides; no src edit before patch docs."],
        ["Read the fan-out and the gates whole and add the in-Book probe, then cost the two designs for the owner."],
        "REQUIRED", 8)
    return measure + "\n\n" + fact


def board(r: Pass) -> None:
    text = r.read(r.BOARD)
    rows = [line for line in text.split("\n") if line.startswith("| notch_fanout_race |")]
    if len(rows) != 1:
        sys.exit(f"ROW notch_fanout_race: {len(rows)}")
    cells = rows[0].split(" | ")
    cells[6] = ("Read the fan-out and the gates whole and add the in-Book probe, then cost the two designs (refuse "
                "at the sites, or order the fan-out) for the owner; the 0.2.8267 re-measure is recorded.")
    cells[10] = r.now
    r.stage(r.BOARD, text.replace(rows[0], " | ".join(cells)))


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_race_remeasure")
    text = r.read(RACE)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + notes(r) + "\n\n## Context / Handoff Summary\n",
                  "race notes")
    old = ("Next: (1) rerun both probes and the race test on a /tmp copy, the GIL off and on; (2) write and run the "
           "in-Book\nprobe; (3) read the fan-out and the gates whole, then cost the two designs for the owner.")
    new = ("Re-measured on 0.2.8267 (Notes): the race reproduces at the same rate (GIL off 10/20 and 200/400 "
           "unexpected;\nGIL on 0), the mechanism holds at today's lines (notch fans out after end_transaction), and "
           "a 4th kind (the\nno-overrides hydrator's unknown-spell_id) joined the three. Next: read the fan-out and "
           "gates whole and add the\nin-Book probe, then cost the two designs (refuse at the sites, or order the "
           "fan-out) for the owner's decision.")
    text = r.once(text, old, new, "race summary")
    r.stage(RACE, text)
    r.set_field(RACE, "Updated")
    board(r)
    r.checked_flush(sys.argv[1] == "--apply")


if __name__ == "__main__":
    main()
