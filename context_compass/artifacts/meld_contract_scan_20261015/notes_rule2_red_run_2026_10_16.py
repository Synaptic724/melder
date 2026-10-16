"""Record the rule-2 red run, two build details and the race finding; move the board row on (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"
AN = "src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py"
SS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red run of the new and changed tests on the scratch tree (the real tree at 0.2.8248, which already carries
    melder_0's `notch_spell(spell_id=...)`, plus the tests; Python 3.14.7t, GIL off): 53 failed, 288 passed over
    seven files, each failure for its intended reason. The registry walk 17 of 17 (no `binding_key`, no
    `mark_dependents_for_revalidation`); the Book marks 4 (2 guards pass); the meld gate 14 (3 guards pass); the
    report, strategy and Phase 4 tests 7 (1 guard passes); the new integration file 11 of 14 - a 5-11 pass on every
    warm meld, a notch leaves the consumer `valid`, an index destroy raises the scan's MeldExecutionError, a version
    uncontract gives the generic report, C1 and C3 keep the old Dep, C2 raises "many_only manifest references
    unknown spell_id", C4 builds the old Dep, the link regression and X1 raise AttributeError "'SpellContract' object
    has no attribute 'ping'". S3 and S6 pass through today's scan and stay as guards. Two findings: releasing an
    index link leaves the consumer `valid` and still building the released provider (`_remove_index_from_contract`
    ends in the borrower's `_remove_contracted_spell`, which marks nobody - rule 2's mark covers it); and the file
    first notched through `find_spell_by_id(<parked id>)`, which answers with the active member (a no-op notch), so
    it names a version by `spell_id=` (the probes passed the parked Spell object).
  EVIDENCE:
  - {ART}/runs/rule2_red_all_gil0.txt:1-60
  - {ART}/runs/rule2_integration_red_gil0.txt:1-112
  - {ART}/staged_tests/test_conduit_integration_notch_revalidation.py:1-589
  - {ART}/staged_tests/test_spell_system_states_dependent_walk.py:1-377
  - {ART}/runs/probe_index_uncontract_today_gil0.txt:1-8
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2215-2266
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2484-2510
  - src/melder/aether/spellbook/spellbook.py:3311-3414
  IMPACT: The red set is complete and every red is one rule 2 owns; the build can start. Index uncontract joins the
    live defects the marks fix (with index destroy and the link-time dependents).
  NEXT: Implement spell_system_states.py (binding key, walk, walk-on) on the scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Two build details inside the approved design. (1) `mark_dependents_for_revalidation` calls `check_cleaned()`
    before it takes the registry lock and again under it, so a walk on a cleaned registry raises Cleanable's
    RuntimeError "SpellSystemStates has already been cleaned. " - the registry's docstring promises that for every
    public method, and its cleanup deletes the maps and the lock the walk reads. (2) `_clear_contracted_spells_for_
    conduit` marks each active copy's `_make_spell_key(spellframe, spell_name, binding_name)`, the key
    `_add_contracted_spell` files the copy under in the lookup map, so the mark names exactly the keys the clear drops.
  EVIDENCE:
  - src/melder/utilities/general_base/cleanable.py:129-144
  - {SS}:209-319
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/spellbook/spellbook.py:3416-3469
  IMPACT: The walk's and the clear's tests pin these; the system docs state them at promotion.
  NEXT: Implement spell_system_states.py on the scratch copy.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: RISK
  CLAIM: A meld racing a lender's notch can return a contract consumer built with its raw SpellContract default, today
    and after rule 2. In a dynamic world Phase 8 tolerates a missing provider (`_allow_missing_contract_providers` is
    True, `_resolve_spell_contract_spell_id` returns None, `_apply_spell_contract_dependencies` adds no dependency, so
    the plan passes the default) - the link-later rule for conjure. A pass that reaches Phase 8 while a concurrent
    notch has the borrower's copy parked therefore compiles the default. The GIL-off race test (four meld threads
    against 20 notches) sees AttributeError "'SpellContract' object has no attribute 'ping'" in about one run of
    four today. Rule 2 moves the presence check into Phase 4 but cannot close the window: Phase 4 and Phase 8 run
    apart, and the park's mark only makes the next meld rebuild. The analyzer is outside the approved patch.
  EVIDENCE:
  - {AN}:1060-1088
  - {AN}:1135-1196
  - {AN}:1226-1240
  - {ART}/runs/rule2_integration_red_gil0.txt:92-98
  IMPACT: The race test may stay red after the build; whether a meld-time refusal (a missing provider in a target
    pass recorded as a visibility failure, so the meld raises SpellbookValidationError) joins this patch is the
    owner's call.
  NEXT: Measure the race after the build, then put the scope question to the owner with the numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

TICKET_PAIRS = [
    ("Next: (1) the build on every file but conduit.py: red tests, the change, green with the GIL off and on, probes\n"
     "(patch and code re-read at 2026-10-16T13:24:49Z); (2) D3's conduit.py lines after melder_0's HANDOFF, then docs,\n"
     "release note, one notch, rebuild.\n",
     "Next: (1) the build on every file but conduit.py: the change, green with the GIL off and on, probes (the red\n"
     f"tests ran at {NOW}: 53 red, each for its reason; the meld-vs-notch race is an open RISK for the owner);\n"
     "(2) D3's conduit.py lines after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n"),
]

OLD_ROW_NEXT = ("| Write the red tests on the scratch copy (walk, marks, gate and catch-up, report, C1-C4 and X1), every "
                "file but conduit.py. |")
NEW_ROW_NEXT = ("| Implement on the scratch copy (registry walk, Book marks, gate catch-up, report), every file but "
                "conduit.py; green GIL off and on. |")


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
assert "CLAIM: Red run of the new and changed tests on the scratch tree" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
for old, new in TICKET_PAIRS:
    text = replace_once(text, old, new, TICKET)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTE.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
out[TICKET] = text

board = read(BOARD)
row = [l for l in board.split("\n") if l.startswith("| meld_contract_scan |")]
assert len(row) == 1, row
new_row = replace_once(row[0], OLD_ROW_NEXT, NEW_ROW_NEXT, BOARD)
new_row = replace_once(new_row, "| 2026-10-16T13:24:49Z | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, row[0], new_row, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
