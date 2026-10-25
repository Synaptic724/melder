"""Record the in-Book probe, the fan-out read and the costed designs of the notch-fan-out race (melder_0, 2026-10-25).

One all-or-nothing pass on TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout and its epic: a MEASURE
note (the in-Book probe), a FACT note (the fan-out and the gate freeze read whole at today's lines), a TRADEOFF note
(the two designs costed) and a DECISION_REQUEST note on the task; a DECISION_REQUEST note, milestone 1, Open
Questions and the resume view on the epic; the task's first two steps checked and its resume view; the race board
row to handoff; an artifact row for this folder. Source ranges are computed from the checkout's own files (whole
functions), not typed. Refuses when a file changed since it was read or a line breaks the width rule.
Usage: record_race_design_20261025.py --check | --apply
"""
import pathlib
import re
import sys
from typing import List

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

RACE = "tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md"
EPIC = "tickets/epics/2026-10-25_notch_fanout_inflight_melds_epic.md"
FOLDER = "artifacts/notch_fanout_race_20261025/"
RUNS = FOLDER + "runs/"
CONDUIT = "src/melder/aether/conduit/conduit.py"
WARD = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
BOOK = "src/melder/aether/spellbook/spellbook.py"
NOTCH = ("src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/"
         "notch_transaction_strategy.py")


def def_range(rel: str, signature: str) -> str:
    """`rel:a-b` of the whole method whose line starts with `signature` (to the next def at its indent)."""
    lines = (Record.REPO / rel).read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith(signature)]
    if len(starts) != 1:
        sys.exit(f"DEF {rel} {signature}: {len(starts)}")
    indent = len(signature) - len(signature.lstrip())
    end = starts[0] + 1
    while end < len(lines):
        line = lines[end]
        stripped = line.lstrip()
        if stripped and (len(line) - len(stripped)) <= indent and (stripped.startswith("def ") or
                                                                    stripped.startswith("class ") or
                                                                    stripped.startswith("@")):
            break
        end += 1
    while lines[end - 1].strip() == "":
        end -= 1
    return f"{rel}:{starts[0] + 1}-{end}"


def run_range(name: str) -> str:
    count = len((Record.ROOT / (RUNS + name)).read_text(encoding="utf-8").rstrip("\n").split("\n"))
    return f"context_compass/{RUNS}{name}:1-{count}"


class Pass(Record):
    @staticmethod
    def check_width(block: str, label: str) -> None:
        """As Record.check_width, also exempting a lone unbreakable path bullet (configuration_standards.md)."""
        for line in block.split("\n"):
            if len(line) <= 120 or "context_compass/" in line or line.startswith("| ") or line.startswith("|---"):
                continue
            stripped = line.strip()
            if stripped.startswith("- ") and " " not in stripped[2:]:
                continue
            sys.exit(f"WIDTH {label}: {len(line)}: {line}")

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


def task_notes(r: Pass) -> List[str]:
    measure = r.note(r.now, "MEASURE", [
        "The in-Book probe this task asked for, run on the /tmp copy of 0.2.8267 (the probe is new:",
        "context_compass/" + FOLDER + "probes/probe_inbook_notch_race.py): the integration file's one-Book chain",
        "(QChain -> PChain -> IDep, all `many`,",
        "dynamic, caching off) with DepB staged on IDep's index; four threads meld QChain while the main thread",
        "notches IDep 20 times between DepA and DepB, ending on DepA. GIL off: 0 of 20 runs and 0 of 100 runs end a",
        "thread with an unexpected exception (100 runs: 662272 melds returned DepA's tag, 869 DepB's, no refusals,",
        "and every first meld after the race returned DepA's). GIL on: 0 of 20. So a notch inside one Book does",
        "not race its dependents' in-flight melds; the race is specific to the borrower fan-out."],
        [run_range("probe_inbook_notch_race_0_2_8267_gil0_100runs.txt"),
         run_range("probe_inbook_notch_race_0_2_8267_gil0_20runs.txt"),
         run_range("probe_inbook_notch_race_0_2_8267_gil1_20runs.txt")],
        ["It answers the scope question the task left open (In scope: whether a notch inside one Book races the same",
         "way): it does not, so the fix concerns borrowers only."],
        ["Record why (the fan-out read, next note)."], "REQUIRED", 9)
    fact = r.note(r.now, "FACT", [
        "Read whole at 0.2.8267. The notch transaction already seals the borrowers and freezes their runtime:",
        "`NotchTransactionStrategy.build_start_plan` extends the EXCLUSIVE seal from the acting conduit to every",
        "conduit linked to it (its borrowers and providers, from the DevOps registry) and stashes exactly that set",
        "as the quiesce footprint; `on_start` quiesces each of those lineages' CreationGates (new melds park,",
        "in-flight melds drain to zero) and `on_end` reopens them at root finalize, which `end_transaction` runs.",
        "`Conduit.notch_spell` calls `end_transaction(success=True)` and only then runs the borrower fan-out",
        "(`_deactivate_borrowed_spell`, `_activate_borrowed_spell`, `ConduitWard._emit_index_notch`), so the",
        "fan-out runs with the borrowers' gates open again - the window the race lives in. In one Book everything a",
        "notch changes (the seam, the lineage marks of rule 2's D2) runs before `on_end`, which is why the in-Book",
        "probe shows nothing. The fan-out starts no transaction and touches no gate: each step takes the borrower",
        "Book's lock for the map change, releases it, then marks through SpellSystemStates (registry -> state ->",
        "RiskManager); the ward emission takes ward -> contract -> borrower Book, the order sever takes."],
        [def_range(CONDUIT, "    def notch_spell("),
         def_range(CONDUIT, "    def _deactivate_borrowed_spell("),
         def_range(CONDUIT, "    def _activate_borrowed_spell("),
         def_range(WARD, "    def _emit_index_notch("),
         def_range(NOTCH, "    def build_start_plan("),
         def_range(NOTCH, "    def on_start("),
         def_range(NOTCH, "    def on_end("),
         def_range(BOOK, "    def _deactivate_contracted_spell("),
         def_range(BOOK, "    def _reactivate_contracted_spell("),
         def_range(BOOK, "    def _mark_contract_dependents_dirty(")],
        ["The freeze that would close the window is already in place; the fan-out only runs outside it."],
        ["Cost the two designs against this (next note)."], "REQUIRED", 9)
    tradeoff = r.note(r.now, "TRADEOFF", [
        "Design 2, order the fan-out inside the frozen window: run the three fan-out calls before",
        "`end_transaction(success=True)`, while the borrowers' gates are drained. It removes all four failure kinds",
        "at their one cause, reuses the freeze already there, matches what an in-Book notch already does (0 of 100),",
        "and leaves warm melds untouched. Costs to settle in its patch doc: (i) a fan-out error inside the window",
        "ends the transaction failed while the Book's switch stands - undo the switch with the Spellbook's existing",
        "refused-notch reversal, or let it stand and raise (today a fan-out error after the window leaves the same",
        "half-state, so neither is a regression); (ii) borrowers' melds stay parked for the fan-out's duration too",
        "(a Book map change and the marks per peer; rule 2 measured the notch walk at 0.2-0.5 ms per 200",
        "dependents), only while a notch runs; (iii) a lock audit for one case - a thread holding a borrower Book's",
        "lock while melding on a sealed conduit would park at the frozen gate while the fan-out waits for that lock;",
        "(iv) the commit hooks (structural validator, dirty marker) then run after the fan-out; (v) the 0.2.8231",
        "threading note on `_emit_index_notch` and src_architecture's sequences change.",
        "Design 1, refuse at the failure sites: make each of the four kinds the clean SpellbookValidationError -",
        "Phase 8's missing-provider tolerance at meld time (conjure's link-later tolerance stays), the many_only and",
        "no-overrides hydrators' unknown-spell_id lookups (with a re-plan), `Meld._execute_admitted` after a failed",
        "rebuild, and the waiter of a failed build. It keeps the window: a meld racing a notch refuses where a meld",
        "a moment later builds the new version, which is weaker than an in-Book notch, and it is four changes in",
        "compile, hydration and meld code, each with its own tests. Recommendation: design 2."],
        [def_range(CONDUIT, "    def notch_spell("),
         def_range(NOTCH, "    def on_start(")],
        ["The owner chooses between closing the window (2) and making racing melds refuse cleanly (1)."],
        ["Put the choice to the owner (next note)."], "REQUIRED", 9)
    request = r.note(r.now, "DECISION_REQUEST", [
        "For the owner: design 2 (order the fan-out inside the notch's frozen window; recommended) or design 1",
        "(refuse cleanly at the four failure sites)? With design 2, the patch doc also proposes how a fan-out error",
        "inside the window ends (recommended: undo the switch with the existing refused-notch reversal, so a notch",
        "either stands with its borrowers moved or leaves everything as it was)."],
        [r.whole(RACE)],
        ["No src edit until the owner chooses; then patch docs, red tests, the fix, measurements, notch and rebuild."],
        ["Ask the owner."], "REQUIRED", 9)
    return [measure, fact, tradeoff, request]


def main() -> None:
    if sys.argv[1:] not in (["--check"], ["--apply"]):
        sys.exit(__doc__)
    r = Pass("record_race_design")
    text = r.read(RACE)
    notes = task_notes(r)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + "\n\n".join(notes) +
                  "\n\n## Context / Handoff Summary\n", "task notes")
    text = r.once(text, "- [ ] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on 0.2.8267\n",
                  "- [x] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on 0.2.8267\n", "step 1")
    text = r.once(text, "- [ ] Read whole: `Conduit.notch_spell` and its fan-out,",
                  "- [x] Read whole: `Conduit.notch_spell` and its fan-out,", "step 2")
    start = text.index("## Context / Handoff Summary\n")
    end = text.index("\n\n## Project-Specific Additions")
    summary = """\
## Context / Handoff Summary
Scheduled 2026-10-25 under EPIC-2026-10-25-notch_fanout_inflight_melds (the owner's ask); in_progress, melder_0
(taken over from melder_1, its author; M0-222). Scope: a borrower meld in flight during a lender notch's fan-out must
end in a version or the clean SpellbookValidationError refusal, never an object built with the SpellContract default
or an internal RuntimeError. State: re-measured on 0.2.8267 - the race reproduces (GIL off 10 of 20 and 200 of 400
runs; GIL on 0), a fourth kind joined the three; a notch inside one Book does not race (0 of 100); the cause is the
fan-out running after `end_transaction` reopens the borrowers' gates, which the notch already drains for its window.
Both designs are costed (TRADEOFF note); design 2 is recommended. Waiting on: the owner's choice (DECISION_REQUEST).
Then: patch docs for the chosen design, red tests (the race test without its xfail marker), the fix, measurements,
notch and rebuild."""
    r.check_width(summary, "task summary")
    text = text[:start] + summary + text[end:]
    r.stage(RACE, text)
    r.set_field(RACE, "Updated")
    epic = r.read(EPIC)
    epic_note = r.note(r.now, "DECISION_REQUEST", [
        "Milestone 1 is met (the child task's MEASURE, FACT and TRADEOFF notes): the race reproduces at 0.2.8267,",
        "a notch inside one Book does not race, and the cause is the borrower fan-out running after the notch's",
        "frozen window reopens the borrowers' gates. For the owner: design 2 (move the fan-out inside the frozen",
        "window; recommended - one cause, the freeze already exists, warm melds untouched) or design 1 (refuse",
        "cleanly at the four failure sites; keeps the window)."],
        [r.whole(RACE)],
        ["The fix waits on this one choice."], ["Ask the owner."], "REQUIRED", 9)
    epic = r.once(epic, "\n\n## Closure Confirmation\n", "\n\n" + epic_note + "\n\n## Closure Confirmation\n",
                  "epic note")
    epic = r.once(epic, "- [ ] Milestone 1: re-measured", "- [x] Milestone 1: re-measured", "epic milestone 1")
    start = epic.index("## Open Questions\n")
    end = epic.index("\n\n## Decision Log")
    open_questions = """\
## Open Questions
- The design (DECISION_REQUEST, Notes): design 2, order the fan-out inside the notch's frozen window (recommended),
  or design 1, refuse cleanly at the four failure sites.
- Answered by measurement on 2026-10-25: a notch inside one Book does not race its dependents' in-flight melds
  (0 of 100 runs; the task's MEASURE note)."""
    r.check_width(open_questions, "epic open questions")
    epic = epic[:start] + open_questions + epic[end:]
    start = epic.index("## Context / Handoff Summary\n")
    end = epic.index("\n\n## Project-Specific Additions")
    epic_summary = """\
## Context / Handoff Summary
Scope: the in-flight borrower meld racing a lender's notch fan-out (p1), in one child task. State: in_progress,
melder_0. Milestone 1 met: the race reproduces at 0.2.8267 (GIL off 10 of 20 and 200 of 400; GIL on 0), an in-Book
notch does not race (0 of 100), and the cause is the fan-out running after the notch's frozen window ends. Waiting
on: the owner's choice of design (Notes; Open Questions). Then: patch docs, red tests, the fix, notch and rebuild."""
    r.check_width(epic_summary, "epic summary")
    epic = epic[:start] + epic_summary + epic[end:]
    r.stage(EPIC, epic)
    r.set_field(EPIC, "Updated")
    board = r.read(r.BOARD)
    rows = [line for line in board.split("\n") if line.startswith("| notch_fanout_race |")]
    if len(rows) != 1:
        sys.exit(f"ROW notch_fanout_race: {len(rows)}")
    cells = rows[0].split(" | ")
    cells[2] = "handoff"
    cells[6] = ("The owner chooses the design: 2, the fan-out inside the frozen window (recommended), or 1, refuse "
                "at the four sites.")
    cells[10] = r.now
    r.stage(r.BOARD, board.replace(rows[0], " | ".join(cells)))
    artifacts = r.read(r.ARTIFACTS)
    row = (f"| {RACE} | {FOLDER} | investigation_evidence | active | retain_as_reference | The 0.2.8267 reruns of the "
           f"race (runs/: the rate and kinds probes, the in-Book probe's 20- and 100-run captures), the in-Book probe "
           f"(probes/) and this pass (scripts/); disposition decided at closure. | {r.now} | HELPFUL |\n")
    artifacts = r.once(artifacts, "<!-- END USER-DEFINED: active_artifacts -->",
                       row + "<!-- END USER-DEFINED: active_artifacts -->", "artifact row")
    r.stage(r.ARTIFACTS, artifacts)
    consume_messages(r)
    r.checked_flush(sys.argv[1] == "--apply")


TESTS_DRAFT = "tickets/tasks/backlog/2026-10-24_document_refused_cache_save_tests_task.md"
EPIC_A = "tickets/epics/2026-10-25_codegen_room_policy_defects_epic.md"
STORY_M1 = "tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md"
STORY_M2 = "tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md"


def note_containing(r: Pass, rel: str, needle: str) -> str:
    """`context_compass/rel:a-b` of the one structured Note whose text contains `needle`."""
    lines = r.read(rel).split("\n")
    spans = []
    for i, line in enumerate(lines):
        if line.startswith("- DATETIME: "):
            end = i + 1
            while end < len(lines) and lines[end] != "" and not lines[end].startswith("## "):
                end += 1
            if needle in "\n".join(lines[i:end]):
                spans.append((i + 1, end))
    if len(spans) != 1:
        sys.exit(f"NOTE {rel} containing {needle}: {len(spans)}")
    return f"context_compass/{rel}:{spans[0][0]}-{spans[0][1]}"


def consume_messages(r: Pass) -> None:
    """Consume M1-61 and M2-39 (both NOTICE to melder_0, no ACK asked): notes first, then delete and clear."""
    mailbox = r.read(r.MAILBOX)
    region = mailbox[mailbox.index("<!-- BEGIN USER-DEFINED: messages -->"):
                     mailbox.index("<!-- END USER-DEFINED: messages -->")]
    mine = re.findall(r"^- TO: melder_0\n(?:  .*\n)+", region, flags=re.M)
    m1 = [m for m in mine if "CLAIM: M1-61." in m]
    m2 = [m for m in mine if "CLAIM: M2-39." in m]
    if len(mine) != 2 or len(m1) != 1 or len(m2) != 1:
        sys.exit("MESSAGES for melder_0 other than M1-61 and M2-39 wait: read them first; nothing written")
    race_fact = r.note(r.now, "FACT", [
        "M1-61 (melder_1's NOTICE, 2026-10-25T00:40:05Z, consumed here), answering M0-222: melder_1 holds none of",
        "conduit.py, conduit_ward.py, meld.py or the hydrators. Its S2 story",
        "(STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, research now) may later need conduit.py's",
        "`remove_from_spell_index` besides spellbook.py and spell_index.py, and melder_1 will ask before touching",
        "conduit.py. This task's design 2 edits `Conduit.notch_spell` in the same file: whichever lands second",
        "re-reads the file and remaps its citations."],
        [note_containing(r, STORY_M1, "M0-222")],
        ["conduit.py is free for this task's fix today; the two lanes coordinate before either edits it."],
        ["Before a conduit.py edit, check melder_1's board row and ask."], "HELPFUL", 7)
    text = r.read(RACE)
    text = r.once(text, "\n\n## Context / Handoff Summary\n", "\n\n" + race_fact +
                  "\n\n## Context / Handoff Summary\n", "M1-61 note")
    r.stage(RACE, text)
    epic_fact = r.note(r.now, "FACT", [
        "M2-39 (melder_2's NOTICE, 2026-10-25T00:40:40Z, consumed here): melder_2 turned in",
        "STORY-2026-10-24-testpypi_trusted_publishing_and_provenance (no src, no notch; its completion summary), and",
        "reports tests_components and tests_architecture updated with their indexes regenerated, the asset and",
        "bundle rebuild to follow.",
        "So the custody this epic recorded from M2-38 has ended: tests_components.md is free for this epic's fixes",
        "(re-read it before editing, and after melder_2's rebuild lands)."],
        ["context_compass/" + STORY_M2 + ":1-8"],
        ["A fix's tests_components entry no longer waits on melder_2."],
        ["Re-read tests_components.md at the first fix's test-doc step."], "HELPFUL", 7)
    epic = r.read(EPIC_A)
    epic = r.once(epic, "\n\n## Closure Confirmation\n", "\n\n" + epic_fact + "\n\n## Closure Confirmation\n",
                  "M2-39 epic note")
    r.stage(EPIC_A, epic)
    r.set_field(EPIC_A, "Updated")
    draft_fact = r.note(r.now, "FACT", [
        "M2-39 (melder_2's NOTICE, 2026-10-25T00:40:40Z; also recorded in",
        "EPIC-2026-10-25-codegen_room_policy_defects): after melder_2's recount of the tests maps at its turn-in,",
        "test_conduit_integration_windows_held_cache_bundle.py is in no tests_components cluster yet (melder_2's",
        "2026-10-25 handoff entry names it). Cataloguing it is this draft's work, with the two 0.2.8266 modules",
        "M1-55 named; tests_components.md is free now that melder_2 has turned in."],
        ["context_compass/" + STORY_M2 + ":1-8"],
        ["The draft's scope is confirmed by the latest recount; recount the tiers at pickup."],
        ["The owner schedules it."], "HELPFUL", 7)
    draft = r.read(TESTS_DRAFT)
    draft = r.once(draft, "\n\n## Context / Handoff Summary\n", "\n\n" + draft_fact +
                   "\n\n## Context / Handoff Summary\n", "M2-39 draft note")
    r.stage(TESTS_DRAFT, draft)
    r.set_field(TESTS_DRAFT, "Updated")
    mailbox = r.once(mailbox, m1[0], "", "M1-61 consumed")
    mailbox = r.once(mailbox, m2[0], "", "M2-39 consumed")
    rows = re.findall(r"^\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| \S+ \| active \|$", mailbox, flags=re.M)
    if len(rows) != 1:
        sys.exit(f"ROW melder_0: {len(rows)}")
    r.stage(r.MAILBOX, mailbox.replace(rows[0], f"| melder_0 | claude | 2026-09-26T22:24:06Z | {r.now} | active |"))
    board = r.read(r.BOARD)
    board = r.once(board, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-25T00:40:05Z)\n", "", "alert M1-61")
    board = r.once(board, "- NEW MESSAGE for melder_0 (from melder_2, 2026-10-25T00:40:40Z)\n", "", "alert M2-39")
    r.stage(r.BOARD, board)


if __name__ == "__main__":
    main()
