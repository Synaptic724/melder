"""Append the rule-2 design-input Notes to TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1).

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
S = "src/melder/aether/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The marking path's locks (read whole). `mark_contract_dependents_dirty` holds the registry lock across its
    loop; `set_validity` takes the state lock and releases it before the RiskManager callback; RiskManager takes its
    own lock only to snapshot and update its sets, reads the published non-resolvable set with no lock and sets the
    Book's flag with a plain attribute write. Nothing under the registry, state or RiskManager lock takes a ward,
    contract, conduit or Book lock. A mark called from the five mutators after their Book lock is released therefore
    adds edges only into the registry - from the owner's ward lock where `_emit_index_notch` and
    `_emit_index_destroy` (through `_uncontract_member_spell`) call the receiver's mutators - and cannot close a
    cycle. The event raises the Book flag in every conduit bucket that holds the consumer's lineage.
  EVIDENCE:
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1541-1621
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:383-451
  - {S}aetheric_frame/dev_ops/risk_manager/risk_manager.py:400-427
  - {S}aetheric_frame/dev_ops/risk_manager/risk_manager.py:613-737
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:608-640
  - {S}spellbook/spellbook.py:6036-6042
  - {S}conduit/conduit_ward/conduit_ward.py:2316-2510
  - {S}conduit/conduit.py:5622-5710
  - {S}conduit/conduit.py:5907-5936
  IMPACT: The mark can sit in the mutators, after their Book lock, with no new lock and no cycle.
  NEXT: Read how a lost provider is reported at meld.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How a lost provider is reported (read whole). The gate's structural branch raises
    `SpellbookValidationError([spell])`, no diagnostics, when the rerun leaves the lineage not `valid`. The renderer
    shows Phase-4 issues of severity error and Phase-6 errors; it only counts warnings ("1 warning not shown"), and a
    spell with no error gets "No validation error was recorded for this spell; its validity is invalid, gated or
    disabled.". Phase 4 gates a lineage on exactly one warning, SPELL_CONTRACT_MISSING_PROVIDER, whose message names
    the parameter and the key but no remedy. Tests pin the generic line, the warning count, the scan's
    MeldExecutionError and `_iter_spell_contract_defaults`.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:163-258
  - src/melder/utilities/custom_exceptions/spellbook_validation_error.py:301-348
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:147-177
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:214-228
  - tests/unit/melder/utilities/custom_exceptions/test_spellbook_validation_error.py:231-243
  - tests/integration/melder/spellbook/test_spellbook_integration_validation_report.py:129-143
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1608-1719
  - tests/unit/melder/aether/conduit/meld/test_meld.py:1776-1808
  IMPACT: Naming the lost contract (option B) is a renderer change - the gating warning shown as the spell's reason
    - plus a remedy in the warning; the scan's four unit tests are replaced whichever option the owner takes.
  NEXT: Probe a consumer lent to a second Book.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Lent consumers (probe, 0.2.8247 tree, Python 3.14.7t, GIL off and on, same results). A SpellContract consumer
    lent from its owner Book O to a Book T, both index-linking the lender's provider: with the marking it follows a
    lender notch in both Books with one 5-11 pass in all - its CreationContext is per spell, so the first Book to meld
    rebuilds it for both; today every meld in both Books pays the scan and a 5-11 pass. When T alone loses the
    provider (drops its index link, or severs its link to the lender), T keeps building the lent consumer with the
    old provider through the fast door, today and with the marking: T's flag goes down (the lent lineage is valid and
    T's provider copy is unregistered), so the scan never runs there. One contract key has at most one provider
    lineage per frame: bind refuses a second active spell on a spellframe/binding signature (a first probe attempt,
    a second lender of the same key, hit that refusal).
  EVIDENCE:
  - {A}probe_rule2_lent_consumer.py:1-121
  - {A}runs/probe_rule2_lent_consumer_gil0.txt:1-63
  - {A}runs/probe_rule2_lent_consumer_gil1.txt:5-67
  - src/melder/aether/aetheric_frame/lookup_container.py:91-127
  IMPACT: Rule 2 holds for lent consumers that keep their provider. A Book-local provider loss under a lent consumer
    is a pre-existing gap the scan does not close (per-Book visibility against a frame-wide state and a per-spell
    plan); it stays outside rule 2 and goes to the owner as a finding.
  NEXT: Record the version-anchored grant's documented behaviour against the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: A version-anchored grant's docstring disagrees with the code. `_add_spell_to_contract` says it "contracts the
    SpellIndex lineage" and that "on mutation, the lineage will advance, and lookups will resolve to the new
    version"; but a notch parks the anchored copy on every linked peer (`_deactivate_borrowed_spell`), only
    index-link contracts move to the new version (`_emit_index_notch`, whose docstring says version-anchored
    borrowers are left to the deactivate fan-out), and nothing reactivates the parked copy when a notch back makes
    its version active again: `_add_inactive_contracted_spell` says the owning Conduit drives
    `_activate_contract_spell` at a notch, and that method has no caller. Probe S2: the anchored consumer loses its
    provider after a notch and does not get it back on the notch back, in every mode.
  EVIDENCE:
  - {S}conduit/conduit_ward/conduit_ward.py:1844-1866
  - {S}conduit/conduit.py:5694-5709
  - {S}conduit/conduit.py:5907-5936
  - {S}conduit/conduit_ward/conduit_ward.py:2316-2380
  - {S}spellbook/spellbook.py:1782-1807
  - {S}spellbook/spellbook.py:3216-3258
  - {A}runs/probe_rule2_design_gil0.txt:1-106
  IMPACT: For the owner: wire the notch-back reactivation the docstrings describe (a mirror of the deactivate
    fan-out in `notch_spell`), and correct the grant docstring either way.
  NEXT: Write the patch docs and the decision requests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: The marking path's locks (read whole)." not in text
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
