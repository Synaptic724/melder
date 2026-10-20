"""Append the rule-2 probe Notes to TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
Inserts the Notes before "## Context / Handoff Summary" and sets "- Updated:"; prose lines within 120 characters
(an evidence line holding one path may run long) and ASCII; refuses a missing anchor or a second insertion.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
A = "context_compass/artifacts/meld_contract_scan_20261015/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Design probe on the 0.2.8247 tree (Python 3.14.7t, GIL off and on, same results; monkeypatches only, caching
    off), three modes: today; the scan removed; the scan removed with the five Book mutators marking the copy's key
    (mark only, the rule-2 emulation). A borrower SpellContract consumer of an index-linked provider: today it
    follows a notch, a notch back and a repeat notch (B, A, B) at 1470-1650 us a warm meld (a scan and a 5-11 pass
    every meld); with the scan removed it never follows (A every time, and after an index destroy it still builds
    the destroyed provider); with the marking it is `gated` + `contract_unvalidated` after each notch, follows B, A,
    B with one 5-11 pass per change and none on warm melds, at 1.8-2.0 us. A notch to a version whose `__init__`
    cannot be resolved raises the UnresolvedInputError the first meld of that version raises, today and with the
    marking. An index destroy, and a notch away from a version-anchored grant, raise today the scan's
    MeldExecutionError ("SpellContract could not be resolved. Missing contracted provider for key ... on param
    'service'"); with the marking they raise the first meld's error for a missing provider, SpellbookValidationError
    "... Consumer: - No validation error was recorded for this spell; its validity is invalid, gated or disabled. 1
    warning not shown". A unique consumer keeps its stored object after a notch and builds the new version after a
    purge, today and with the marking. A notch back never restores a version-anchored copy in any mode (it stays
    parked; `_activate_contract_spell` has no caller). When the lender notches the provider's own dependency (also
    index-linked), the consumer fails today (its forced rebuild meets the provider's stale topology) and with the
    marking keeps building the provider over the old dependency (the consumer declares the provider's key only).
  EVIDENCE:
  - {A}runs/probe_rule2_design_gil0.txt:1-106
  - {A}runs/probe_rule2_design_gil1.txt:5-110
  - {A}probe_rule2_design.py:1-382
  IMPACT: The marking makes rule 2 hold for the provider's own versions at about 1/800 of today's warm cost, and
    every failure is the first meld's; the price is a weaker message for a lost provider (the first meld's message,
    which names no contract), and the provider's subgraph stays outside the marking.
  NEXT: Check the dependency case without contracts, in one Book.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The dependency case is not a contract problem. In one dynamic Book with no links, after the Book notches a
    `many` dependency Dep to Dep2(Dep), the `many` consumer P(dep: Dep) stays `valid` and is not rebuilt: melded
    before the notch it keeps building Dep (d1); never melded before it, it fails on every meld with RuntimeError
    "many_only manifest references unknown spell_id '<Dep's old version id>'" - the plan compiled at conjure names
    a version the notch took out of the pool. Same tree, GIL off.
  EVIDENCE:
  - {A}runs/probe_in_book_dependency_notch_gil0.txt:1-8
  - {A}probe_in_book_dependency_notch.py:1-62
  IMPACT: A consumer does not follow a notch of what it resolves through a dependency, in its own Book or across a
    contract; that is a separate defect for the owner to place, not part of rule 2's marking.
  NEXT: Write the patch docs with the decisions the owner has to make.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: Design probe on the 0.2.8247 tree" not in text
updated = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(updated) == 1
text = text.replace(updated[0], f"- Updated: {NOW}", 1)
text = text.replace(anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, 1)
# A path is an unbreakable token (configuration_standards.md): an evidence line holding one path may run long.
too_long = [l for l in text.split("\n") if len(l) > 120 and not (l.startswith("  - ") and " " not in l[4:])]
assert not too_long, too_long
text.encode("ascii")
if not CHECK:
    TICKET.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written", len(text.split("\n")), "lines")
