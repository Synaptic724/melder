"""Record the registry and Book halves of rule 2 on the scratch copy, with their runs (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
BOARD = pathlib.Path("attention_board.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

NOTE = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The registry and Book halves of rule 2 are in on the scratch copy (apply scripts, each run with --check
    first). spell_system_states.py: `register_index(binding_key=...)` records the selected version's normalized
    (frame_key, binding_key) per lineage (`_binding_key_by_index`; None keeps it, a non-pair raises TypeError,
    `unregister_index` and cleanup drop it); `mark_dependents_for_revalidation` walks registry edges and contract keys
    from the seeds (check_cleaned before and under the lock); `mark_contract_dependents_dirty` walks on from the
    consumers it gates. spellbook.py: bind and `_apply_notch` pass `spell._key`, `_apply_notch` walks from the notched
    lineage, and the five contracted-map mutators mark the changed active copy's key after their Book lock through
    `_mark_contract_dependents_dirty`; four test doubles take `binding_key`. Python 3.14.7t, GIL off: the seven red
    files now 31 failed, 310 passed (53 before) - the registry walk (17) and the Book marks (4) pass; what is left
    is meld.py's (14), the report's (7) and the integration file's (10, the scan and no catch-up yet; the race test
    failed this run with three AttributeErrors "'SpellContract' object has no attribute 'ping'"). The surrounding
    suites pass: dev_ops unit and component, test_spellbook.py and the two Book component files, 1082. The index
    uncontract the owner asked about (chat 2026-10-16): with the marks the consumer is `gated` +
    `contract_unvalidated` after `remove_index_from_contract` and its meld refuses with SpellbookValidationError
    (the generic text until D1-B lands); before them it stayed `valid` and built the released ImplA.
  EVIDENCE:
  - {ART}/apply_rule2_src_states.py:1-372
  - {ART}/apply_rule2_src_spellbook.py:1-454
  - {ART}/apply_rule2_tests_doubles.py:1-58
  - {ART}/runs/rule2_after_states_spellbook_gil0.txt:1235-1267
  - {ART}/runs/rule2_after_states_spellbook_gil0.txt:1192-1234
  - {ART}/runs/rule2_states_spellbook_green_gil0.txt:1-17
  - {ART}/runs/probe_index_uncontract_scratch_marks_gil0.txt:1-11
  - {ART}/runs/probe_index_uncontract_today_gil0.txt:1-8
  IMPACT: Half the build holds on its own tests, and the index uncontract now reaches its consumer's state; the
    meld gate still scans and has no catch-up, so the integration reds stay until meld.py lands.
  NEXT: Write apply_rule2_src_meld.py (scan out, the catch-up in) and run test_meld.py with the GIL off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

TICKET_PAIRS = [
    ("Next: (1) the build on every file but conduit.py: the change, green with the GIL off and on, probes (the red\n"
     "tests ran at 2026-10-16T14:08:56Z: 53 red, each for its reason; the meld-vs-notch race is an open RISK for the owner);\n"
     "(2) D3's conduit.py lines after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n",
     "Next: (1) the build on every file but conduit.py: spell_system_states.py and spellbook.py are in on the scratch\n"
     f"copy ({NOW}: 31 of the 53 reds left, all meld.py's, the report's and the integration file's); then\n"
     "meld.py and the report, green with the GIL off and on, probes, and the race measured for the owner (an open RISK);\n"
     "(2) D3's conduit.py lines after melder_0's HANDOFF, then docs, release note, one notch, rebuild.\n"),
]


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
assert "CLAIM: The registry and Book halves of rule 2 are in on the scratch copy" not in text
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
new_row = replace_once(row[0], "| 2026-10-16T14:08:56Z | REQUIRED |", f"| {NOW} | REQUIRED |", BOARD)
board = replace_once(board, row[0], new_row, BOARD)
out[BOARD] = board

for path, content in out.items():
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
