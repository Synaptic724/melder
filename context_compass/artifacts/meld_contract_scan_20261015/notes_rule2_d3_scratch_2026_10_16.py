"""Record D3 built on the scratch copy, with its red, green and suite runs and its build details (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
ART = "context_compass/artifacts/meld_contract_scan_20261015"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D3 is built on the scratch copy (its conduit.py from before melder_0's add/remove extension; to be re-checked
    against the released file). conduit.py: `notch_spell` calls the new `_activate_borrowed_spell` after the
    deactivate fan-out and before `_emit_index_notch`; the method walks the ward's links and calls each peer Book's
    `_activate_contract_spell`, which reactivates a parked copy of the incoming version through
    `_reactivate_contracted_spell` (rule 2's mark) and is a no-op otherwise; `notch_spell`'s docstring and comment
    say so. conduit_ward.py: the grant's docstring describes the version copy (active while its version is active,
    parked otherwise, reactivated on a notch back; a grant of a parked version activates on its notch) and
    `_emit_index_notch` names both fan-outs. Two tests in the integration file: a notch back reactivates a version
    grant (the consumer then builds A with one 5-11 pass, an object built before keeps A, a linked peer that never
    borrowed A gains no provider) and a grant of a parked version activates on the notch to it. Red before the src
    change: both fail at the D3 step with the lost-contract SpellbookValidationError. Green: the file 15 passed and
    the race test xpassed, GIL off and on; every suite chunk passes in both modes (int_conduit 350 passed, the race
    test xfailed with the GIL off and xpassed with it on; exper without its benchmark module, 244).
  EVIDENCE:
  - {ART}/apply_rule2_src_conduit_d3.py:1-107
  - {ART}/apply_rule2_src_conduit_ward_d3.py:1-48
  - {ART}/apply_rule2_tests_d3.py:1-100
  - {ART}/staged_tests/test_conduit_integration_notch_revalidation.py:419-489
  - {ART}/runs/rule2_d3_red_gil0.txt:1-22
  - {ART}/runs/rule2_d3_green_file.txt:1-4
  - {ART}/runs/rule2_d3_scratch_suites_gil0.txt:1-21
  - {ART}/runs/rule2_d3_scratch_suites_gil1.txt:1-21
  IMPACT: The whole approved change set is built and green on the scratch copy; what remains is the copy onto the
    current real tree, its suites, then docs, release note, notch, closure and rebuild.
  NEXT: Refresh the scratch copy from the real tree and re-apply every apply script with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: D3 build details. (1) `_activate_borrowed_spell` carries no None guards: the ward is assigned at the
    conduit's construction and deleted at its cleanup, a peer's Book is fixed at its construction, and
    `check_cleaned()` runs first (the deactivate twin's guards are dead and are left as they are - no drive-by
    change). (2) The D3 tests sit in the integration file beside the other notch scenarios, not in a component file
    as the patch's validation line says: they need two Books, a link and a grant, the helpers that file holds. (3)
    The parked-grant test passes the parked Spell object (`_get_owned_spell`), because `get_spell_by_id` answers a
    parked id with the active member and the grant then refuses the id mismatch. (4) The first green run failed in
    the bystander check: the bystander's Consumer is bound under the binding "bystander" and was melded by class
    (KeyError for frame 'consumer', binding '__default__'); the test now melds it by its id. The red run's failures
    were earlier in both tests and stand.
  EVIDENCE:
  - {ART}/apply_rule2_src_conduit_d3.py:24-107
  - {ART}/apply_rule2_tests_d3.py:1-100
  - src/melder/aether/conduit/conduit.py:280-310
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  IMPACT: The system docs state (1)-(3) at promotion; the patch's validation line is met in substance.
  NEXT: Refresh the scratch copy from the real tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
"""


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


text = read(TICKET)
assert "D3 is built on the scratch copy" not in text
lines = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(lines) == 1, lines
text = text.replace(lines[0], f"- Updated: {NOW}", 1)
anchor = "\n## Context / Handoff Summary\n"
text = replace_once(text, anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, TICKET)
check_lengths(text, TICKET)
print(("CHECK " if CHECK else "WRITE ") + str(TICKET), len(text.split("\n")))
if not CHECK:
    TICKET.write_bytes(text.encode("utf-8"))
