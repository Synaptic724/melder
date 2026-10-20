"""Rule 2's ticket after the D2 patch docs: the mapping, the approval request, the D2 scope and the handoff (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET = pathlib.Path("tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md")
CP = "context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"
P = "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation step -> validation step with D1-B, D2 and D3 decided (replaces the 10:33:55Z
    mapping). (1) component_patch_borrower_contracted_maps: `Spellbook._mark_contract_dependents_dirty` and the five
    mutators' marks after their Book lock (spellbook.py, after melder_0's handoff) -> unit tests per mutator on a real
    registry. (2) component_patch_dependent_walk: `register_index(binding_key=...)`, `_binding_key_by_index`,
    `mark_dependents_for_revalidation`, `mark_contract_dependents_dirty` walking on (spell_system_states.py); `bind`
    and `_apply_notch` pass the key, `_apply_notch` walks, its docstring and comment (spellbook.py) -> registry unit
    tests (chain, cross-Book, walk-on, idempotency, a cycle, the key's lifecycle, one publication per change).
    (3) component_patch_meld_gate: the scan, its helpers and imports removed; `_refresh_stale_dependencies` at the top
    of `_ensure_lineage_resolvable` (when the spell may compile) and of `_ensure_runtime_resolution_ready`; docstrings
    and the ward's comment (meld.py, conduit_ward.py) -> the five scan unit tests replaced, catch-up unit tests with
    lock doubles, integration melds after a notch, an index destroy and an uncontract, and probe C1-C4 and X1 as
    regressions named for their symptoms. (4) component_patch_contract_presence_report: the snapshot walk, the remedy,
    `GATING_WARNING_CODES` and the renderer -> renderer and strategy unit tests, a GIL-off race of melds and notches.
    (5) component_patch_notch_reactivation: `_activate_borrowed_spell` in `notch_spell`, the grant docstring
    (conduit.py, conduit_ward.py) -> the anchored notch-back component test. (6) code_description_patch: the lock and
    ordering points -> registry and lock doubles; the probes before and after (us per warm meld, passes and refreshes
    per change, the walk's time for a large fan-out). Then the system docs, graph descriptors, the release note (two
    Breaking items), one notch above the current version, closure, rebuild.
  EVIDENCE:
  - {CP}architecture_patch.md:1-218
  - {CP}component_patch_dependent_walk.md:1-114
  - {CP}component_patch_meld_gate.md:1-148
  - {CP}code_description_patch_contract_recheck.md:1-144
  IMPACT: The build has a mapped order once the owner approves and melder_0 hands spellbook.py over.
  NEXT: Ask the owner to approve the patch as a whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner approves the patch as a whole before any `src/` edit. It carries his decisions D1 (B), D2 (a notch
    flags everything downstream: the registry walk plus the meld's structural catch-up, both needed - mark only
    strands a dependent two hops away), D3 (reactivate and revalidate), D4 (backlog task) and D5 (wait for melder_0).
    Two behaviour changes go in the release note as Breaking: a lost provider raises SpellbookValidationError where
    the scan raised MeldExecutionError; a dependent of a notched spell builds the new version or raises the first
    meld's error where it built the old one. The same walk also rebuilds a contract consumer's dependents after a
    link, grant, uncontract or sever (a live defect: they kept a plan built without the provider).
  EVIDENCE:
  - {CP}architecture_patch.md:200-218
  IMPACT: Approval starts the build as soon as melder_0 hands spellbook.py over.
  NEXT: Present the updated patch docs to the owner and wait for his answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

HANDOFF = f"""## Context / Handoff Summary
Design phase ({NOW}): the patch docs carry the owner's decisions D1-D5 and wait for his approval of the
whole; no `src/` change before it, and the build waits for melder_0's handoff of spellbook.py (S8 landed as
0.2.8248, in review).
The story (owner, 2026-10-16): a satisfied SpellContract is not checked on every meld; a change of what a spell
resolves - its provider's notch, or (D2) a notch of anything it depends on, in its Book or another - marks it for
revalidation, so its next meld rechecks and rebuilds against the versions now active, or fails with the first meld's
error; objects already built keep what they were built with.
Design: (1) the borrower Book's five contracted-map mutators mark the copy key's consumers after their Book lock;
(2) the registry records a binding key per lineage and marks everything downstream of a notch - registry edges and
contract keys, transitively - and every contract mark walks on from its consumers; (3) the meld's per-meld scan goes;
(4) before a plan compiles, the meld refreshes the structure of every stale lineage the plan expands (with its owner
Book, under its window and lock) and resets that lineage's own plan; (5) D1-B names a lost contract; (6) D3 makes a
parked anchored copy usable again on a notch back. Cost: about 2 us a warm consumer meld instead of about 1.5 ms; per
change one refresh per stale dependency and one 5-11 pass per lineage.
Evidence: the Notes from 09:57:21Z on; probes and runs in artifacts/meld_contract_scan_20261015/
(probe_rule2_design.py, probe_rule2_lent_consumer.py, probe_in_book_dependency_notch.py,
probe_rule2_dependency_closure.py).
Patch: system_docs/patches/active/contract_recheck_on_notch_2026_10_16/
(architecture, five component patches, the code description).
Decided: D1 B; D2 fold in; D3 reactivate and revalidate; D4 TASK-2026-10-16-investigate_lent_consumer_provider_loss
(backlog); D5 wait for melder_0.
Next: (1) the owner's approval; (2) melder_0's handoff of spellbook.py; (3) the build: red tests, the change, green
with the GIL off and on, probes, docs, release note, notch, rebuild.
"""

EDITS = [
    ("""recheck, and its next meld re-validates the contract and rebuilds against the version now active, or fails with the
error a first meld would give. Objects already built keep their provider (mark only). Design first: patch docs for
the owner's approval, and no `src/` edit before it.""",
     """recheck, and its next meld re-validates the contract and rebuilds against the version now active, or fails with the
error a first meld would give. Objects already built keep their provider (mark only). D2 (owner, 2026-10-16): a notch
also flags for revalidation every spell that depends on the notched one, in its Book or another. Design first: patch
docs for the owner's approval, and no `src/` edit before it."""),
    ("""  contract consumer follows its lender's notch (notch back, park, reactivate and destroy included) by a recheck at
  its next meld and fails with the first-meld error when the new version cannot be resolved for it; objects already""",
     """  contract consumer follows its lender's notch (notch back, park, reactivate and destroy included) by a recheck at
  its next meld and fails with the first-meld error when the new version cannot be resolved for it; every spell that
  depends on a notched one follows it the same way, two hops away and across Books included; objects already"""),
    ("""  lender's notch and notch back, parking and reactivating a version-anchored copy, add, remove and destroy).""",
     """  lender's notch and notch back, parking and reactivating a version-anchored copy, add, remove and destroy); (D2) the
  registry's downstream walk at a notch and from every contract mark, and the meld's structural catch-up of the stale
  dependencies a plan expands."""),
    ("""  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_notch_reactivation.md
""",
     """  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_notch_reactivation.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_dependent_walk.md
"""),
]

text = TICKET.read_bytes().decode("ascii")
anchor = "\n## Context / Handoff Summary\n"
assert text.count(anchor) == 1
assert "CLAIM: Patch section -> implementation step -> validation step with D1-B, D2 and D3 decided" not in text
for old, new in EDITS:
    assert text.count(old) == 1, old
    text = text.replace(old, new, 1)
updated = [l for l in text.split("\n") if l.startswith("- Updated: ")]
assert len(updated) == 1
text = text.replace(updated[0], f"- Updated: {NOW}", 1)
text = text.replace(anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, 1)
start = text.index("## Context / Handoff Summary\n")
end = text.index("\n## Project-Specific Additions\n")
text = text[:start] + HANDOFF.rstrip("\n") + "\n" + text[end:]
too_long = [l for l in text.split("\n") if len(l) > 120 and not (l.startswith("  - ") and " " not in l[4:])]
assert not too_long, too_long
text.encode("ascii")
if not CHECK:
    TICKET.write_bytes(text.encode("ascii"))
print("checked" if CHECK else "written", len(text.split("\n")), "lines")
