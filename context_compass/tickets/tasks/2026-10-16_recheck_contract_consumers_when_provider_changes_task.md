# Task: Recheck SpellContract consumers when their provider changes, instead of on every gated meld

## Metadata
- Task ID: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes
- Story: none - standalone; successor of TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done, rule 1
  landed as 0.2.8247), carrying its rule 2 by the owner's direction of 2026-10-16
- Status: in_progress
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-16T09:46:14Z
- Updated: 2026-10-16T12:14:33Z

## Objective
Rule 2 of the owner's 2026-10-15 direction, settled in principle on 2026-10-16: a spell's own state decides when the
SpellContract check runs. A satisfied contract is not checked again on every meld; a change of the provider a
consumer resolves - a notch above all, because a notched version's `__init__` may differ - marks that consumer for a
recheck, and its next meld re-validates the contract and rebuilds against the version now active, or fails with the
error a first meld would give. Objects already built keep their provider (mark only). Design first: patch docs for
the owner's approval, and no `src/` edit before it.

## Ticket Contract
- ENTRY_GATE: the board row routes this task; the contract check and every path that changes a borrower Book's active
  contracted copy are read whole on today's tree and recorded; the patch docs under
  system_docs/patches/active/contract_recheck_on_notch_2026_10_16/ exist, are linked and are
  approved by the owner before any `src/` edit; melder_0 hands over spellbook.py before it is edited.
- EXECUTION_BOUNDARY: design phase: read-only on `src/`; probes under artifacts/meld_contract_scan_20261015/; the
  patch docs. After approval: the files the approved design names (expected: Meld's gate, the borrower Book's
  contracted-map mutators, the contract marking in SpellSystemStates), their tests, system docs, the release note,
  the notch and the rebuild.
- DEPENDENCIES: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (done: its findings, probes and rule 1);
  melder_0's lanes (spellbook.py and transfer_of_ownership.py are its files: no edit without a handoff).
- EXIT_GATE: a meld of a spell whose state needs no contract check makes no signature scan and forces no rebuild; a
  contract consumer follows its lender's notch (notch back, park, reactivate and destroy included) by a recheck at
  its next meld and fails with the first-meld error when the new version cannot be resolved for it; objects already
  built keep their provider; the suites pass with the GIL off and on; the cost is measured; docs, notch, rebuild;
  the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each design choice the owner has not made; CONFLICT if a provider change
  cannot reach its consumers' state without a new state or a hot-path read; BLOCKER while spellbook.py is not handed
  over.

## Scope Boundaries
- In scope: `Meld._ensure_lineage_resolvable` and its contract check; the producers of a contract consumer's
  `gated` and `contract_unvalidated` state; every path that changes a borrower Book's active contracted copy (a
  lender's notch and notch back, parking and reactivating a version-anchored copy, add, remove and destroy).
- Out of scope: rule 1 (done, 0.2.8247); the compiler's own contract scans; dropping stored consumer objects on a
  notch (owner: mark only); managed_spell_quantity work; MelderOps code.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner split rule 2 off TASK-2026-10-15-make_meld_state_checks_follow_spell_state and
  directed this successor (chat 2026-10-16: "yees sure thats good" to opening it on the settled story, design docs
  first).

## Steps / Checklist
- [x] Re-read whole on today's tree: the meld gate's contract check, Phase 4's contract presence check, the contract
      marking (`mark_contract_dependents_dirty`) and its callers, a lender notch's fan-out to borrowers and the
      borrower Book's contracted-map mutators; record what reaches a consumer's state and what does not.
- [ ] Write the patch docs; get the owner's approval; get melder_0's handoff of spellbook.py.
- [ ] Red tests, the change, green suites (GIL off and on), measurement.
- [ ] Docs, release note, notch, rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Approved patch docs; then the change with tests, docs, notch and rebuild.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md
- context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/ (patch docs)
- context_compass/artifacts/meld_contract_scan_20261015/ (probes and runs, shared with the predecessor)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - artifacts/meld_contract_scan_20261015/probe_design_baseline.py (the borrower contract consumer: gate entries,
    scans and microseconds per meld) and a probe that notches the lender and melds the consumer
  - the meld, conduit, spellbook and dev-ops suites with the GIL off and on

## Risks / Rollback Notes
- Today the per-meld scan hides the missing marking: removed alone, a consumer kept getting the old version after
  its lender notched (measured 2026-10-15). The marking lands with the removal, never after it.
- A consumer plan built for one provider version must not run against another; the recheck is that guard, so every
  path that changes the borrower's active copy must mark.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/meld_contract_scan_20261015/
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_borrower_contracted_maps.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_meld_gate.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_contract_presence_report.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_notch_reactivation.md
  - system_docs/patches/active/contract_recheck_on_notch_2026_10_16/code_description_patch_contract_recheck.md
- DISPOSITION: retain_as_reference (the folder); promote_to_documentation (the patch docs)
- CLEANUP_TRIGGER: at closure the patch docs are promoted into the system docs and archived under
  system_docs/patches/completed/; the folder stays as the lane's evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - which provider changes must mark a SpellContract consumer, and how the meld check reads that state
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; the whole ticket;
  initial revision 2026-10-16T09:46:14Z; the direction is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none

## Notes
- DATETIME: 2026-10-16T09:46:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Starting point, as read and measured on 2026-10-15 (the predecessor's Notes; not yet re-read on today's
    tree, so no design claim rests on it yet). Phase 3 records each SpellContract socket per Book (key ->
    consumer lineages); Phase 4 marks a consumer `gated` + `contract_unvalidated` while its provider is missing
    and clears the flag when present; link, grant, uncontract, sever and remove-all gate the key's consumers.
    Phase 9 bakes the provider's spell id into the consumer's plan. A lender's notch, or parking a
    version-anchored copy, ends in the borrower Book's contracted-map mutators, which mark nobody; the meld's
    unconditional scan forces a 5-11 rebuild of every contract consumer on every gated meld and so hides that.
    Measured then: a borrower contract consumer 2663 / 2354 us a meld (GIL off / on), 2.0 / 1.9 us with the scan
    removed, and with the scan removed alone the consumer kept getting version A after its lender notched to B.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:197-228
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:229-248
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_design_baseline_gil0.txt:1-21
  IMPACT: The marking is the precondition of the removal; the two land together.
  NEXT: Re-read the gate's contract check and every path that changes a borrower's active contracted copy, whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T09:46:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-16), recorded in the predecessor: a satisfied SpellContract needs no
    per-meld check; a notch "should be rechecked"; mark only ("marking makes sense thats the point we want to make
    sure we can still resolve it because the init might change for a notched spell"). He accepted rule 1 and
    directed this successor, design docs first ("yees sure thats good").
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:249-273
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1054-1076
  - context_compass/tickets/tasks/completed/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1077-1096
  IMPACT: The story is settled; the patch docs carry its mechanics for his approval, and no `src/` changes before.
  NEXT: The first checklist step: the code reads, recorded as Notes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T09:57:21Z
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
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/conduit/meld/meld.py:1174-1244
  - src/melder/aether/conduit/meld/meld.py:1248-1309
  - src/melder/aether/conduit/meld/meld.py:1311-1379
  - src/melder/aether/conduit/meld/meld.py:1382-1426
  - src/melder/aether/conduit/meld/meld.py:1428-1474
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
- DATETIME: 2026-10-16T09:57:21Z
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
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1541-1621
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:838-873
  - src/melder/aether/spellbook/spellbook.py:4913-4962
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2682-2740
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2026-2039
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1205-1220
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/conduit/conduit.py:5853-5936
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2431
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2433-2510
  - src/melder/aether/spellbook/spellbook.py:1623-1842
  - src/melder/aether/spellbook/spellbook.py:3155-3258
  - src/melder/aether/spellbook/spellbook.py:3311-3469
  - src/melder/aether/spellbook/spell.py:571-577
  IMPACT: The marking rule 2 needs has one choke point, the five mutators in spellbook.py (melder_0's file), where
    a mark-only call covers notch, notch back, park, reactivate, add, remove and destroy, and the dependency copies
    grant misses; the grant, uncontract and sever paths keep their extraction.
  NEXT: Probe today's tree (monkeypatches only): follow, failure and cost with the scan, without it, and without it
    plus that marking emulated.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T10:03:14Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil0.txt:1-106
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil1.txt:5-110
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_design.py:1-382
  IMPACT: The marking makes rule 2 hold for the provider's own versions at about 1/800 of today's warm cost, and
    every failure is the first meld's; the price is a weaker message for a lost provider (the first meld's message,
    which names no contract), and the provider's subgraph stays outside the marking.
  NEXT: Check the dependency case without contracts, in one Book.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T10:03:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The dependency case is not a contract problem. In one dynamic Book with no links, after the Book notches a
    `many` dependency Dep to Dep2(Dep), the `many` consumer P(dep: Dep) stays `valid` and is not rebuilt: melded
    before the notch it keeps building Dep (d1); never melded before it, it fails on every meld with RuntimeError
    "many_only manifest references unknown spell_id '<Dep's old version id>'" - the plan compiled at conjure names
    a version the notch took out of the pool. Same tree, GIL off.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_in_book_dependency_notch_gil0.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/probe_in_book_dependency_notch.py:1-62
  IMPACT: A consumer does not follow a notch of what it resolves through a dependency, in its own Book or across a
    contract; that is a separate defect for the owner to place, not part of rule 2's marking.
  NEXT: Write the patch docs with the decisions the owner has to make.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T10:24:14Z
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
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1541-1621
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:383-451
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:400-427
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:613-737
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:608-640
  - src/melder/aether/spellbook/spellbook.py:6036-6042
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2510
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/conduit/conduit.py:5907-5936
  IMPACT: The mark can sit in the mutators, after their Book lock, with no new lock and no cycle.
  NEXT: Read how a lost provider is reported at meld.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T10:24:14Z
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
    - plus a remedy in the warning; the scan's five unit tests are replaced whichever option the owner takes.
  NEXT: Probe a consumer lent to a second Book.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T10:24:14Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py:1-121
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil0.txt:1-63
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil1.txt:5-67
  - src/melder/aether/aetheric_frame/lookup_container.py:91-127
  IMPACT: Rule 2 holds for lent consumers that keep their provider. A Book-local provider loss under a lent consumer
    is a pre-existing gap the scan does not close (per-Book visibility against a frame-wide state and a per-spell
    plan); it stays outside rule 2 and goes to the owner as a finding.
  NEXT: Record the version-anchored grant's documented behaviour against the code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T10:24:14Z
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
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1844-1866
  - src/melder/aether/conduit/conduit.py:5694-5709
  - src/melder/aether/conduit/conduit.py:5907-5936
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2316-2380
  - src/melder/aether/spellbook/spellbook.py:1782-1807
  - src/melder/aether/spellbook/spellbook.py:3216-3258
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil0.txt:1-106
  IMPACT: For the owner: wire the notch-back reactivation the docstrings describe (a mirror of the deactivate
    fan-out in `notch_spell`), and correct the grant docstring either way.
  NEXT: Write the patch docs and the decision requests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T10:33:55Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation step -> validation step, for after the owner's approval (D1-D5 may trim
    it). (1) component_patch_borrower_contracted_maps: `Spellbook._mark_contract_dependents_dirty` and the five
    mutators' marks after their Book lock (spellbook.py, after melder_0's handoff) -> unit tests per mutator on a
    real registry (a mark when conjured, none before conjure or for a parked copy, the Book lock free) and the
    component coverage matrix. (2) component_patch_meld_gate: the scan, its two helpers and their imports removed,
    the docstrings and the ward's comment updated (meld.py, conduit_ward.py) -> the five scan unit tests replaced,
    integration melds after a notch, an index destroy and an uncontract. (3) component_patch_contract_presence_report:
    the strategy's snapshot walk, and with D1-B its message and the renderer -> renderer and strategy unit tests, a
    GIL-off race of melds against notches. (4) component_patch_notch_reactivation, with D3: `_activate_borrowed_spell`
    in `notch_spell` and the grant docstring (conduit.py, conduit_ward.py) -> the anchored notch-back component test.
    (5) code_description_patch_contract_recheck: the lock and ordering points -> a registry double that asserts the
    Book lock is free, and the probes before and after (us per warm meld, passes per change). Then the system docs
    (src_architecture's gate sequence, an invariant, a failure mode and the code map; src_components' Meld,
    Spellbook and Conduit sections; the tests docs), graph descriptors, the release note, the notch above S8's,
    closure, rebuild.
  EVIDENCE:
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:1-163
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/code_description_patch_contract_recheck.md:1-95
  IMPACT: The build has a mapped order the moment the owner approves; nothing in `src/` changes before.
  NEXT: The owner's review of the patch docs and decisions D1-D5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T10:33:55Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner decides before any `src/` edit: D1 the message for a lost provider - A keep the first meld's
    generic message, B (recommended) SpellbookValidationError shows the gating SPELL_CONTRACT_MISSING_PROVIDER warning,
    with a remedy, as the spell's reason (type and first line unchanged), C a failure-path scan raising
    MeldExecutionError (it changes the first meld's error too; not recommended); D2 keep the provider's dependencies
    out of rule 2 and open a task for the dependency-notch defect, which exists in one Book too (recommended); D3
    wire the notch-back reactivation of parked version-anchored copies that the docstrings describe (recommended),
    and correct the grant docstring either way; D4 a lent consumer's Book-local provider loss to its own task, or
    accepted as is; D5 land after melder_0's S8 (0.2.8248) with melder_0's handoff of spellbook.py. Approving the
    patch as a whole starts the build.
  EVIDENCE:
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:139-159
  IMPACT: Each answer fixes a part of the change set; without D5 the five mutators cannot be edited.
  NEXT: Present the patch docs and these decisions to the owner and wait for his answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T11:46:26Z
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
- DATETIME: 2026-10-16T11:46:26Z
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
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:721-782
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:783-884
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:994-1104
  - src/melder/aether/spellbook/spellbook.py:3826-3968
  - src/melder/aether/spellbook/spell.py:1593-1660
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:719-757
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_in_book_dependency_notch_gil0.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil0.txt:1-106
  IMPACT: The owner's rule - a notch flags whatever depends on the notched spell - needs the closure at a notch
    (in-Book and across Books by dependency edges) plus rule 2's contract mark for every impacted lineage that a
    Book lends (contract consumers have no edge); the same mark-for-revalidation mechanism as rule 2.
  NEXT: Ask the owner whether rule 2 takes this in or it becomes its own task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T11:50:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner decided D2 and D3 (chat 2026-10-16, answering the explanation above). D2: fold the dependency
    notch into rule 2 - a notch flags for revalidation every spell that depends on the notched one, in its Book
    through the dependency walk and in other Books through the contract consumers of an impacted provider (owner:
    "if the spell being notched is a dependency for something else it should flag their spells for revalidation").
    D3: on a notch back, the borrower's parked copy of the incoming version becomes usable again and its consumers
    are marked, so their next meld revalidates and rebuilds; built objects are untouched. D1 (B), D4 (the backlog
    investigation task) and D5 (wait for melder_0) stand.
  EVIDENCE:
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:139-159
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_notch_reactivation.md:1-70
  IMPACT: The patch grows a component for the notch's dependent walk; it goes back to the owner for approval before
    any `src/` edit, and the build still waits for melder_0.
  NEXT: Read how a resolution pass treats a dependency whose own lineage is stale (the transitive case), then write
    the D2 component patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:09:19Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How a dependent's resolution pass reads its dependencies (read whole). A target pass (Phases 5-7 local,
    then 8-11) never reruns a dependency's structural phases. Phase 5 builds the target's scope from the frame-wide
    registry: each lineage's current id and the direct dependency version ids its own last Phase 3 recorded; an id
    that is no longer current (a version a notch parked) is dropped from the scope. Phase 8 expands every
    dependency occurrence from the topology that dependency's own last Phase 3 registered (normal sockets carry
    resolved version ids; contract sockets resolve through the melding Book's contracted maps). Phase 3 refreshes
    only its own spell's registry entries and leaves the plan, the CreationContext and the Phase 5 artifacts alone.
    So after a notch of Dep, a dependent Q two hops away (Q -> P -> Dep) compiles P's stale topology: the lookup of
    Dep's parked version misses, the pass records a visibility failure that sets every scoped spell (Q and P)
    `invalid` for the conduit, and the gate's resolution branch raises on an `invalid` verdict without rerunning -
    Q stays refused there until something gates it again. The deferred lane (`resolution_required`) runs 8-11 over
    the spell's existing Phase 5 artifacts when it is its own Phase 5 root, and the full 5-11 pass otherwise.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1722-1835
  - src/melder/aether/spellbook/spellbook_creation_system.py:2411-2576
  - src/melder/aether/spellbook/spellbook_creation_system.py:2599-2660
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:222-264
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:628-729
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_adjacency_builder.py:31-95
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:924-1014
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1225
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:1193-1318
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:771-822
  - src/melder/aether/conduit/meld/meld.py:933-988
  - src/melder/aether/conduit/meld/meld.py:1006-1102
  - src/melder/aether/conduit/meld/meld.py:1248-1309
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_design_gil0.txt:26-31
  IMPACT: Marking the closure is not enough for a dependent two hops away: before a plan compiles, every stale
    lineage it expands needs its structure refreshed, and a refreshed dependency's own plan must be reset so no
    door serves the old one.
  NEXT: Probe the chain in one Book and across Books with the closure emulated, with and without a meld-time
    structural catch-up.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:14:33Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: D2 probe (0.2.8248 tree, Python 3.14.7t, GIL off and on, same results; monkeypatches only). A chain
    Q -> P -> Dep in one Book with Dep bound under a Protocol and notched to another implementer, and the same
    across Books (the lender's P and Dep index-linked into a Book whose Consumer holds a SpellContract on P's key
    and whose User depends on Consumer). Today and with rule 2 alone: Q keeps building the old Dep when it was
    melded before the notch, otherwise fails with RuntimeError "many_only manifest references unknown spell_id";
    P's first meld fails with the visibility error naming Dep's parked version; across Books the User is broken
    from the start (AttributeError "'SpellContract' object has no attribute 'ping'": linking marked Consumer, not
    User, whose conjure-time plan built Consumer with its SpellContract default). With the notch marking its
    closure (registry edges plus contract keys; a mutator's mark walks on from the consumers it marks), mark only:
    P follows (one 5-11), User works before the notch, but Q fails with that visibility error and then stays
    refused ("No validation error was recorded") even after P is rebuilt; across Books User and Consumer stay
    refused too. With a meld-time catch-up added (every stale lineage the plan expands gets phases 1-4 with its
    owner Book under its rebuild window and lock, then its own plan reset and `resolution_required`): Q follows
    with one refresh and one 5-11, the next melds take the fast door, P's own meld then runs its full pass, and the
    Book flag comes down; across Books User, Consumer and the lender's P follow (two refreshes). A notch to a class
    the kind rule does not select for `dep: Dep` gives Q and P the first meld's UnresolvedInputError "PClass.dep
    expects Dep, but nothing registered provides it", not the old version. The borrower's flag stays up for a
    reason present before any meld: its conduit holds index-linked copies it never resolved.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_dependency_closure.py:1-367
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_dependency_closure_gil0.txt:1-173
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_dependency_closure_gil1.txt:5-177
  IMPACT: D2 needs both halves: the closure mark (from the notch and from rule 2's marks) and the catch-up before a
    plan compiles; marking alone strands a dependent two hops away. The walk also fixes a live defect: a contract
    consumer's dependents kept a plan built without the provider after a link or grant.
  NEXT: Write the D2 component patch and update the architecture and code-description patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Design phase (2026-10-16T10:33:55Z): the patch docs are written and wait for the owner's approval; no `src/` change
before it. The story (owner, 2026-10-16): a satisfied SpellContract is not checked on every meld; a change of the
provider a consumer resolves - a lender's notch above all, since a notched version's `__init__` may differ - marks
the key's consumers `gated` + `contract_unvalidated`, so their next meld re-validates the contract and rebuilds
against the version now active, or fails with the first-meld error; objects already built keep their provider.
Design: the borrower Book's five contracted-map mutators mark through `mark_contract_dependents_dirty` once their
Book lock is released; the meld's per-meld scan goes; the gate's structural branch is the recheck - one 5-11 pass
per change, shared by every conduit, about 2 us a warm meld instead of about 1.5 ms.
Evidence: the Notes from 09:57:21Z on, and the probes and runs in artifacts/meld_contract_scan_20261015/
(probe_rule2_design.py, probe_rule2_lent_consumer.py, probe_in_book_dependency_notch.py).
Patch: system_docs/patches/active/contract_recheck_on_notch_2026_10_16/
(architecture, three component patches, the notch-reactivation patch, the code description).
Open for the owner: D1 the lost-provider message (B recommended); D2 the dependency notch outside rule 2 (its own
task); D3 the notch-back reactivation of version-anchored copies (recommended); D4 a lent consumer's Book-local
provider loss (its own task); D5 the landing after S8 with melder_0's handoff of spellbook.py.
Next: (1) the owner's approval and decisions; (2) melder_0's handoff of spellbook.py once S8 (0.2.8248) lands;
(3) the build: red tests, the change, green with the GIL off and on, probes, docs, release note, notch, rebuild.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
