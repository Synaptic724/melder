"""Append the rule-2 code-read Notes to TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
Inserts the Notes before "## Context / Handoff Summary" and sets "- Updated:"; every line within 120 characters and
ASCII; refuses when the anchor is missing or the Notes are already there. --check writes nothing.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
M = "src/melder/aether/conduit/meld/meld.py"
SB = "src/melder/aether/spellbook/spellbook.py"
CW = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
SSS = "src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The meld gate today (read whole on the 0.2.8247 tree). ConduitMeld and SpellSpaceMeld enter
    `_ensure_lineage_resolvable` only while the Book flag is up. Its structural branch runs for a lineage that is
    `unknown` or `gated`: under the rebuild window and the spell lock it reruns phases 1-4, raises
    SpellbookValidationError when the spell is broken or the lineage is still not `valid`, and otherwise gates the
    conduit verdict (`structure_changed`). Then, on every gated meld, `_check_contracts_and_force_revalidation`
    reads the callable's signature, looks each SpellContract key up in the Book's active contracted maps
    (MeldExecutionError "SpellContract could not be resolved" when one is missing) and gates the conduit verdict
    (`contract_unvalidated`), so `_ensure_resolution_resolvable` reruns phases 5-11 for every contract consumer on
    every gated meld. Phase 4 reruns for a lineage that is not `valid`; ContractProviderPresenceStrategy finds the
    provider in the same active maps, and a missing one is a warning that leaves the lineage `gated` +
    `contract_unvalidated` (not broken), a present one makes it `valid`. Phase 8 adds the provider occurrence it
    resolves through those maps and walks the provider's topology, so the provider's subgraph is part of the
    consumer's plan. A missing provider on a first meld, or after an uncontract, raises SpellbookValidationError
    ("Spellbook validation failed") from the structural branch, before the scan, and the tests assert exactly that.
  EVIDENCE:
  - src/melder/aether/conduit/meld/conduit_meld.py:576-580
  - {M}:933-988
  - {M}:1174-1244
  - {M}:1248-1309
  - {M}:1311-1379
  - {M}:1382-1426
  - {M}:1428-1474
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:56-177
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:72-247
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:930-962
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1089
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:415-488
  - tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py:135-167
  - tests/integration/melder/conduit/test_conduit_integration_spell_contract_variants.py:610-665
  IMPACT: Once a consumer is marked `gated` whenever its provider changes, the structural branch alone does the
    recheck - Phase 4 checks presence, the forced 5-11 rebuild re-resolves the provider's subgraph - and fails with
    the first-meld error; the scan and its forced rebuild are then pure cost.
  NEXT: Record which provider changes reach a consumer's state today.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Which provider changes mark a consumer today (read whole). `mark_contract_dependents_dirty` gates a Book's
    consumers of the given keys (`gated` + `contract_unvalidated`, not transitively dirty) through the per-Book
    reverse index Phase 3 topology feeds. It is called by the LINK commit hook (`_default_dirty_marker`, with the
    staged contract keys that `_try_update_staged_contract_keys` refreshes only inside a LINK transaction) and by the
    ward's `_invalidate_contract_consumers` (grant, uncontract, sever on both sides, remove-all), which also extracts
    the consumers' stored objects from the conduit store. A notch marks nobody in a borrower: after the owner's
    notch transaction ends, `Conduit._deactivate_borrowed_spell` parks the outgoing copy on every linked peer and
    `ConduitWard._emit_index_notch` parks the old copy and reactivates or adds the new one on index-link receivers.
    An index destroy (`cleanup_spell` -> `_emit_index_destroy` -> `_uncontract_member_spell`) removes an active copy
    and marks nobody either. Every path that changes a borrower's active contracted copy ends in five Book
    mutators: `_add_contracted_spell`, `_deactivate_contracted_spell`, `_reactivate_contracted_spell`,
    `_remove_contracted_spell` (its active branch) and `_clear_contracted_spells_for_conduit`; the key consumers
    declare is the copy's `Spell._key`, the normalization `SpellContract.canonical_key` lookups use. Grant marks only
    the root key, not the dependency copies `_link_spell_dependencies` adds; `_reactivate_contracted_spell` also
    registers nothing with RiskManager.
  EVIDENCE:
  - {SSS}:1541-1621
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:838-873
  - {SB}:4913-4962
  - {CW}:2682-2740
  - {CW}:2026-2039
  - {CW}:1205-1220
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/conduit/conduit.py:5853-5936
  - {CW}:2316-2431
  - {CW}:2433-2510
  - {SB}:1623-1842
  - {SB}:3155-3258
  - {SB}:3311-3469
  - src/melder/aether/spellbook/spell.py:571-577
  IMPACT: The marking rule 2 needs has one choke point, the five mutators in spellbook.py (melder_0's file), where
    a mark-only call covers notch, notch back, park, reactivate, add, remove and destroy, and the dependency copies
    grant misses; the grant, uncontract and sever paths keep their extraction.
  NEXT: Probe today's tree (monkeypatches only): follow, failure and cost with the scan, without it, and without it
    plus that marking emulated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: The meld gate today (read whole" not in text
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
