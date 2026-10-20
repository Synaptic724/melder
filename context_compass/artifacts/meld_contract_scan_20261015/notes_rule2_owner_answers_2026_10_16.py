"""Append the owner's answers and the dependency-notch explanation to rule 2's ticket (melder_1).

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
  TYPE: DECISION
  CLAIM: The owner's answers (chat 2026-10-16). D1: option B ("B is fine"). D4: an investigation task ("make a task
    for investigation"), opened as TASK-2026-10-16-investigate_lent_consumer_provider_loss in the backlog. D5:
    "melder_0 is still working on things" - the landing waits for melder_0 (S8 landed as 0.2.8248 at 11:25Z and is
    in review). D2: the owner asked what the defect is and stated the rule - "if the spell being notched is a
    dependency for something else it should flag their spells for revalidation". D3: "it shouldn't restore it it
    should mark it for revalidation" - whether the parked version-anchored copy comes back (with its consumers
    marked) or stays parked (consumers marked, then failing for want of a provider) is to be confirmed.
  EVIDENCE:
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:139-159
  IMPACT: The report change (B) is settled; D2 and D3 are open; the build waits for melder_0 either way.
  NEXT: Explain the dependency-notch defect from the source and the probe, and confirm D2's scope and D3's meaning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Why a dependency notch does not reach its dependents (read whole). Phase 3 records each spell's resolved
    constructor dependencies in the registry (`update_dependencies`: the dependency's state gains the consumer as a
    direct dependent). A notch re-registers the notched lineage (`register_index` -> `mark_structural_change`) and
    `invalidate_spell` marks it again - the notched lineage only, although `_apply_notch`'s comment says "so
    dependents revalidate". The registry's closure walk, `compute_impact_closure`, which gates every downstream
    lineage (`impacted_by_dependency`), runs when a definition is removed (`unregister_index`) and in an ownership
    transfer, never at a notch. So a dependent stays `valid` with a plan that names the old version: built before,
    it keeps building the old dependency; never built, it fails on every meld with RuntimeError "many_only manifest
    references unknown spell_id '<old id>'" (probe, one Book). A SpellContract consumer is further out: it declares
    the provider's key, not an edge to the provider, so even the closure would not reach it (probe S5).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1023-1219
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:721-782
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:783-884
  - {S}aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:994-1104
  - {S}spellbook/spellbook.py:3826-3968
  - {S}spellbook/spell.py:1593-1660
  - {S}conduit/conduit_ward/transfer/transfer_of_ownership.py:719-757
  - {A}runs/probe_in_book_dependency_notch_gil0.txt:1-8
  - {A}runs/probe_rule2_design_gil0.txt:1-106
  IMPACT: The owner's rule - a notch flags whatever depends on the notched spell - needs the closure at a notch
    (in-Book and across Books by dependency edges) plus rule 2's contract mark for every impacted lineage that a
    Book lends (contract consumers have no edge); the same mark-for-revalidation mechanism as rule 2.
  NEXT: Ask the owner whether rule 2 takes this in or it becomes its own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: Why a dependency notch does not reach its dependents (read whole)." not in text
updated = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(updated) == 1
text = text.replace(updated[0], f"- Updated: {NOW}", 1)
text = text.replace(anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, 1)
too_long = [l for l in text.split("\n") if len(l) > 120 and not (l.startswith("  - ") and " " not in l[4:])]
assert not too_long, too_long
text.encode("ascii")
if not CHECK:
    TICKET.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written", len(text.split("\n")), "lines")
