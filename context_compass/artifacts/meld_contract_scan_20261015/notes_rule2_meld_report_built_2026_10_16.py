"""Record the meld and report halves of rule 2, the build details, the cost and the race on both trees (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The meld and report halves of rule 2 are in on the scratch copy (apply scripts, each run with --check
    first), so every file but conduit.py is built. meld.py: the per-meld scan
    (`_check_contracts_and_force_revalidation` and `_iter_spell_contract_defaults`) and its imports are gone;
    `_ensure_lineage_resolvable` runs the catch-up when the spell will compile there (`_may_compile`), then the
    structural branch, then the resolution check unless the spell is flagged `resolution_required`;
    `_ensure_runtime_resolution_ready` runs the catch-up
    before its own window; the catch-up walks the plan's dependencies (`_iter_planned_dependencies`: socket targets
    and contracted providers, each at the version its lineage selects in the Book's pool) and refreshes each stale
    one (`_refresh_dependency_structure`: its window, its lock, a staleness recheck, phases 1-4 with its owner Book,
    then its own plan reset). The report: Phase 4's presence check walks snapshots and names the remedy, and
    SpellbookValidationError shows a gating warning (`GATING_WARNING_CODES`) as a spell's reason (D1-B). The ward's
    comment names the analyzer's helper. Python 3.14.7t, GIL off: the seven rule-2 files 340 passed, 1 failed (the
    meld-vs-notch race test); the suite chunks pass - unit_aether 4512, unit_sb 2578, unit_util 831, comp_aether
    1386, comp_sb 819, int_sb 647, int_mt 54, int_aether 795, int_cryst 276 and the rest - except int_conduit, 348
    passed and 1 failed, the same race test; comp_sb and int_mt passed after two test updates (next Note); exper
    ran without its benchmark module, which the scratch tree lacks (244 passed). GIL on: every chunk passes,
    int_conduit 349 with the race test.
  EVIDENCE:
  - {ART}/apply_rule2_src_meld.py:1-528
  - {ART}/apply_rule2_src_report.py:1-338
  - {ART}/apply_rule2_src_conduit_ward.py:1-25
  - {ART}/apply_rule2_tests_parity.py:1-64
  - {ART}/apply_rule2_tests_mutation_race.py:1-81
  - {ART}/runs/rule2_green_all_gil0.txt:1-52
  - {ART}/runs/rule2_scratch_suites_gil0.txt:1-25
  - {ART}/runs/rule2_scratch_suites_gil1.txt:1-21
  - {ART}/runs/rule2_scratch_int_conduit_gil0.txt:1-52
  IMPACT: The build holds on its tests in both GIL modes except the GIL-off race, which fails at today's rate (the
    race Notes below); D3's conduit.py lines and the landing remain.
  NEXT: Record the build details and the cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Build details inside the approved design (beside those of 13:24:49Z and 14:08:56Z). (1) The catch-up keeps a
    reset dependency's `requires_spellspace_request`: `clear_phase5_artifacts` sets it False, and the conduit door
    refuses a spellspace-scoped spell by that flag before the gate, so clearing it would let a direct meld of such a
    dependency through; its own next pass recomputes it. (2) A valid existing creation or non-resolvable dependency
    is refreshed but not reset - neither ever plans. (3) `_iter_planned_dependencies` reads the topology first and
    needs the Book only when one is recorded (RuntimeError "Spell has no owning Spellbook surface." otherwise).
    (4) The renderer counts a gating warning as an explanation for its restating rule, counts it with the hidden
    warnings when the spell also shows errors, and keeps "No validation error was recorded" for a spell with
    neither when no diagnostics were handed in. (5) Two tests follow the new behaviour and keep what they guard: the
    structural snapshot parity test's notch event records, in both worlds, the first meld's UnresolvedInputError
    after a notch to a class `engine: Engine` does not select (probe C4), then notches back; the mutation-during-meld
    tests mark the consumer (`mark_contract_dependents_dirty`) before their forced meld, which relied on the retired
    scan's forced pass, and still expect SpellbookValidationError.
  EVIDENCE:
  - {ART}/apply_rule2_src_meld.py:453-520
  - {ART}/apply_rule2_src_meld.py:351-421
  - {ART}/apply_rule2_src_report.py:200-268
  - {ART}/apply_rule2_tests_parity.py:1-64
  - {ART}/apply_rule2_tests_mutation_race.py:1-81
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:742-769
  - src/melder/aether/conduit/meld/conduit_meld.py:559-580
  IMPACT: The system docs state these at promotion; the two test updates are part of the change set.
  NEXT: Record the cost before and after.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Cost (probe_rule2_cost.py; "before" is the scratch tree with the seven baseline src files restored; caching
    off; Python 3.14.7t). A warm meld of the borrower's contract consumer: GIL off 1668.46 us with a 5-11 pass every
    meld -> 2.57 us with none; GIL on 1704.80 -> 2.68 us. A notch to B, then one meld: GIL off 1389 -> 2523 us (one
    pass; two structural reruns instead of one - the catch-up refreshes the provider, then the consumer reruns), the
    notch back 1684 -> 2485 us; GIL on 1628 -> 2395 and 1882 -> 2658 us. After a notch the warm consumer is back at
    2.62 us (GIL off), where today it stays at 1260 us a meld. The notch's walk with 200 dependents: GIL off 0.69 /
    0.21 ms (to P2 / back) -> 1.17 / 0.47 ms; GIL on 0.76 / 0.16 -> 1.17 / 0.40 ms.
  EVIDENCE:
  - {ART}/probe_rule2_cost.py:1-122
  - {ART}/runs/probe_rule2_cost_before_gil0.txt:1-8
  - {ART}/runs/probe_rule2_cost_after_gil0.txt:1-8
  - {ART}/runs/probe_rule2_cost_before_gil1.txt:1-8
  - {ART}/runs/probe_rule2_cost_after_gil1.txt:1-8
  IMPACT: About 650 times cheaper per warm meld of a contract consumer; each provider change costs 0.8-1.1 ms more
    (one more structural rerun) and a notch's walk 0.2-0.5 ms more at 200 dependents.
  NEXT: Record the race on both trees.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The meld-vs-notch race on both trees (the integration race: four threads meld the borrower's contract
    consumer while the lender notches its provider 20 times; GIL off unless said). Rates (probe_rule2_race_rate.py,
    20 runs a tree): 7 of 20 runs end a thread with an unexpected exception on both trees - before, 9
    MeldExecutionError (the scan's "SpellContract could not be resolved") and 8 AttributeError "'SpellContract'
    object has no attribute 'ping'"; after, 9 AttributeError and 2 RuntimeError "Cannot build CreationContext before
    spell_codegen_creation exists.". Melds: before 55 A and 68 refused, after 7688 A and 57 refused; no meld returned
    B on either tree; the first meld after the race returned A in every run. GIL on: 0 of 20 on both trees. Kinds
    (diag_race_kinds.py, 400 runs a tree, instrumented, so its timing is perturbed and its counts are not rates):
    before 257 AttributeError, 151 MeldExecutionError (the scan), 8 RuntimeError "many_only manifest references
    unknown spell_id" (the parked A) and 2 "Cannot build CreationContext"; after 242 AttributeError, 73 "Cannot build
    CreationContext", 9 "many_only manifest" and 1 "Spell creation context was not published: the selected builder
    failed". Every kind but the scan's refusal occurs on today's tree.
  EVIDENCE:
  - {ART}/probe_rule2_race_rate.py:1-97
  - {ART}/runs/probe_rule2_race_rate_before_gil0.txt:1-26
  - {ART}/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - {ART}/runs/probe_rule2_race_rate_before_gil1.txt:1-24
  - {ART}/runs/probe_rule2_race_rate_after_gil1.txt:1-24
  - {ART}/diag_race_kinds.py:1-178
  - {ART}/runs/diag_race_kinds_before_gil0.txt:193-197
  - {ART}/runs/diag_race_kinds_after_gil0.txt:209-213
  IMPACT: The race predates rule 2 and rule 2 leaves its rate as it was; it removes the scan's refusal and makes the
    internal "Cannot build CreationContext" error more frequent, because more melds pass the gate without a forced
    pass.
  NEXT: Record what each kind is.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What each race kind is (the first occurrences' timelines and tracebacks, both trees). `notch_spell` parks and
    reactivates the borrower's contracted copies after its transaction has ended (`_deactivate_borrowed_spell`,
    `_emit_index_notch`), so a consumer meld can be anywhere between its gate and its first execution when that
    happens: (a) AttributeError - a target pass ran Phase 8 while the copy was parked and, in a dynamic world,
    compiled the raw SpellContract default (`_allow_missing_contract_providers`); (b) "many_only manifest references
    unknown spell_id '<A>'" - a pass compiled its plan against A, the fan-out parked A, and the cold door's first
    hydration looked the plan's step ids up in the Book's pool, which no longer held A (`_resolve_spell_lookup`);
    (c) "Cannot build CreationContext" - a meld that had passed the gate was admitted after another meld's pass
    failed with the plan cleared (pass-done plan=False, then that meld refused), so its context build found no plan;
    (d) "was not published" - a meld waiting on that failed build. (c) settles the HYPOTHESIS recorded for the
    first diagnosis, and contradicts `_execute_admitted`'s docstring, which says a meld "never ... builds from a
    missing plan": that holds only when the rebuild it waited for succeeded.
  EVIDENCE:
  - {ART}/runs/diag_race_kinds_after_gil0.txt:61-86
  - {ART}/runs/diag_race_kinds_after_gil0.txt:87-147
  - {ART}/runs/diag_race_kinds_after_gil0.txt:148-208
  - {ART}/runs/diag_race_kinds_before_gil0.txt:134-192
  - src/melder/aether/conduit/conduit.py:5725-5751
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1088
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:320-341
  - src/melder/aether/conduit/meld/meld.py:866-929
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:68-125
  IMPACT: The four kinds are one gap - in-flight borrower melds are not ordered against a notch's fan-out - which
    rule 2's marks do not close: they make the next meld correct, not one already in flight.
  NEXT: Put the scope question to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner decides the race's scope. A: fold a fix into this patch - in-flight melds refuse with
    SpellbookValidationError, the 0.2.8227 rule for a meld racing a sever or uncontract, at the three sites (a
    provider missing in a meld-time target pass becomes a visibility failure, while conjure keeps its link-later
    tolerance; a meld admitted to a spell with no plan re-enters the gate; a hydration miss of a plan's spell id is
    treated as a stale plan); the patch docs grow first and come back for approval. B (recommended): land rule 2
    as approved with the race test marked xfail(strict=False) naming a follow-up task, opened now with this
    evidence, which also weighs moving the fan-out under the notch's frozen gates (conduit.py, where D3 edits too).
    Reasons for B: the race and every kind but the scan's predate rule 2 at the same rate; its cause is the notch's
    fan-out order, not the marks; a fix touches the compiler, the hydrators and the meld door beyond the approved
    nine components. Cost of B: until the follow-up lands, a GIL-off race shows the internal RuntimeError more often
    and the scan's MeldExecutionError no more.
  EVIDENCE:
  - {ART}/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - {ART}/runs/diag_race_kinds_after_gil0.txt:209-213
  - src/melder/aether/conduit/conduit.py:5725-5751
  IMPACT: A changes the patch and its review; B lands the approved patch and leaves a known, tracked race.
  NEXT: Ask the owner (A or B), with the numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

TICKET_PAIRS = [
    ("Next: (1) the build on every file but conduit.py: spell_system_states.py and spellbook.py are in on the scratch\n"
     "copy (2026-10-16T14:30:05Z: 31 of the 53 reds left, all meld.py's, the report's and the integration file's); then\n"
     "meld.py and the report, green with the GIL off and on, probes, and the race measured for the owner (an open RISK);\n"
     "(2) D3's conduit.py lines after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n",
     f"Next: (1) the owner's answer on the meld-vs-notch race (DECISION_REQUEST of {NOW}: A, a refusal fix\n"
     "folded into this patch, or B, landing with the race test xfail and a follow-up task); every file but conduit.py\n"
     "is built on the scratch copy and green with the GIL off and on except that test (GIL off); (2) copy the build to\n"
     "the real tree (baselines compared, apply scripts with --check) and run the suites; (3) D3's conduit.py lines\n"
     "after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n"),
]

OLD_NEXT_CELL = ("| Implement on the scratch copy (registry walk, Book marks, gate catch-up, report), every file but "
                 "conduit.py; green GIL off and on. |")
NEW_NEXT_CELL = ("| Owner answers the race scope (A: fold a fix in; B: land with the race test xfail and a follow-up "
                 "task); then copy the build to the real tree. |")


def read(path):
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("utf-8")


def replace_once(text, old, new, path):
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    return text.replace(old, new)


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


out = {}
text = read(TICKET)
assert "CLAIM: The meld and report halves of rule 2 are in on the scratch copy" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
for old, new in TICKET_PAIRS:
    text = replace_once(text, old, new, TICKET)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
out[TICKET] = text

board = read(BOARD)
row = [l for l in board.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(row) == 1, row
new_row = replace_once(row[0], OLD_NEXT_CELL, NEW_NEXT_CELL, BOARD)
new_row = replace_once(new_row, "| 2026-10-16T14:30:05Z | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, row[0], new_row, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
