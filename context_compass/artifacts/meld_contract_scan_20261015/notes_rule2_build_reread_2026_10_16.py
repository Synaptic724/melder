"""Record the build re-read and its implementation details; move the board row on (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
AN = "src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py"
SS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Re-read after re-onboarding: the patch in its read order and the code it changes, whole, on the 0.2.8248
    tree (the scratch copy matches the real tree for every file the build touches). The code sites are as the patch
    records. Five build details, inside the approved design: (1) the gate's catch-up runs when the spell will compile
    there - its lineage `unknown` or `gated` or unregistered, or its lineage `valid` and its effective verdict
    `unknown` or `gated`; a `resolution_required` spell compiles in the deferred lane, which every door runs right
    after the gate and which runs its own catch-up first, so the gate does not walk for it twice; (2) a stale existing
    creation is refreshed structurally but its plan is not reset - it never plans, the rule
    `flag_dependencies_without_own_plan` already applies; (3) no guard for a cleaned topology - the registry cleans
    topologies only in its own cleanup (frame teardown), and Phase 8 reads them unguarded; (4) a NORMAL target and a
    contracted provider are both taken to their lineage's current version in the compiling Book's pool, as Phase 8
    resolves a contract through `spell_index.selected_spell_id`, so a stale map entry never gets an old version
    refreshed; (5) the grant docstring moves to D3's step, because it describes the notch-back reactivation that
    D3's conduit.py lines add.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/conduit/meld/meld.py:1006-1074
  - src/melder/aether/conduit/meld/conduit_meld.py:576-580
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-528
  - src/melder/aether/spellbook/spellbook_creation_system.py:1907-1976
  - {SS}:209-322
  - {SS}:1623-1679
  - {AN}:1135-1225
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1844-1866
  IMPACT: The build follows the patch with these five details; the system docs state them when the patch is
    promoted.
  NEXT: Write the red tests on the scratch copy: the registry walk, the Book marks, the gate and the catch-up, the
    report, and the C1-C4 and X1 regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
"""

TICKET_PAIRS = [
    ("Next: (1) re-read the patch and the code it changes; (2) the build on every file but conduit.py: red tests, the\n"
     "change, green with the GIL off and on, probes; (3) D3's conduit.py lines after melder_0's HANDOFF, then docs,\n"
     "release note, one notch, rebuild.\n",
     "Next: (1) the build on every file but conduit.py: red tests, the change, green with the GIL off and on, probes\n"
     f"(patch and code re-read at {NOW}); (2) D3's conduit.py lines after melder_0's HANDOFF, then docs,\n"
     "release note, one notch, rebuild.\n"),
]

OLD_ROW_NEXT = ("| Re-read the patch and the code it changes, then write the red tests on a scratch copy (every file but "
                "conduit.py). |")
NEW_ROW_NEXT = ("| Write the red tests on the scratch copy (walk, marks, gate and catch-up, report, C1-C4 and X1), every "
                "file but conduit.py. |")


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
assert "CLAIM: Re-read after re-onboarding: the patch in its read order" not in text
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
new_row = replace_once(new_row, "| 2026-10-16T12:57:39Z | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, row[0], new_row, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
