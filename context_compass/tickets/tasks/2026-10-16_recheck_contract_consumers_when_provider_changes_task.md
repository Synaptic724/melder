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
- Updated: 2026-10-17T21:36:47Z

## Objective
Rule 2 of the owner's 2026-10-15 direction, settled in principle on 2026-10-16: a spell's own state decides when the
SpellContract check runs. A satisfied contract is not checked again on every meld; a change of the provider a
consumer resolves - a notch above all, because a notched version's `__init__` may differ - marks that consumer for a
recheck, and its next meld re-validates the contract and rebuilds against the version now active, or fails with the
error a first meld would give. Objects already built keep their provider (mark only). D2 (owner, 2026-10-16): a notch
also flags for revalidation every spell that depends on the notched one, in its Book or another. Design first: patch
docs for the owner's approval, and no `src/` edit before it.

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
  melder_0's lanes: spellbook.py and transfer_of_ownership.py released to melder_1 at 2026-10-16T12:33:09Z; conduit.py
  held by TASK-2026-10-16-public_notch_target_for_staged_versions until it lands (D3's lines wait).
- EXIT_GATE: a meld of a spell whose state needs no contract check makes no signature scan and forces no rebuild; a
  contract consumer follows its lender's notch (notch back, park, reactivate and destroy included) by a recheck at
  its next meld and fails with the first-meld error when the new version cannot be resolved for it; every spell that
  depends on a notched one follows it the same way, two hops away and across Books included; objects already
  built keep their provider; the suites pass with the GIL off and on; the cost is measured; docs, notch, rebuild;
  the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for each design choice the owner has not made; CONFLICT if a provider change
  cannot reach its consumers' state without a new state or a hot-path read; BLOCKER for D3's conduit.py lines while
  melder_0's notch-target task holds conduit.py.

## Scope Boundaries
- In scope: `Meld._ensure_lineage_resolvable` and its contract check; the producers of a contract consumer's
  `gated` and `contract_unvalidated` state; every path that changes a borrower Book's active contracted copy (a
  lender's notch and notch back, parking and reactivating a version-anchored copy, add, remove and destroy); (D2) the
  registry's downstream walk at a notch and from every contract mark, and the meld's structural catch-up of the stale
  dependencies a plan expands.
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
- [x] Write the patch docs; get the owner's approval; get melder_0's handoff of spellbook.py.
- [x] Red tests, the change, green suites (GIL off and on), measurement.
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
  - system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/ (the seven patch docs, archived at promotion)
  - system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/ (the removal fix's three patch docs)
  - system_docs/patches/active/find_spell_by_spell_id_2026_10_17/ (the exact spell_id lookup's seven patch docs)
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

- DATETIME: 2026-10-16T12:26:59Z
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
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:1-218
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_dependent_walk.md:1-114
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/component_patch_meld_gate.md:1-148
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/code_description_patch_contract_recheck.md:1-144
  IMPACT: The build has a mapped order once the owner approves and melder_0 hands spellbook.py over.
  NEXT: Ask the owner to approve the patch as a whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T12:26:59Z
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
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:201-218
  IMPACT: Approval starts the build as soon as melder_0 hands spellbook.py over.
  NEXT: Present the updated patch docs to the owner and wait for his answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:41:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: File custody moved (the boards and melder_0's ticket, read after re-onboarding). The owner accepted
    EPIC-2026-10-14-managed_spell_quantity at 12:17:31Z, and melder_0 took its next task,
    TASK-2026-10-16-public_notch_target_for_staged_versions. Its custody DECISION (2026-10-16T12:33:09Z) releases
    spellbook.py and transfer_of_ownership.py to melder_1 now and holds conduit.py until that task lands, because
    it edits `Conduit.notch_spell` too: a `spell_id=` keyword resolved through `Spellbook._get_owned_spell`, and
    target checks before the transaction (exactly one of `spell` and `spell_id`, a version the Book owns, a member
    of the index passed). It leaves the notch window and the fan-out lines as they are and rebinds the resolved
    target to `spell`, so D3's diff applies with at most a context shift. It asked the owner to relay the handoff
    (its Codex bridge does not connect); melder_1 read it in the ticket.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:252-272
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:229-251
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:23-38
  - context_compass/attention_board.md:229-229
  IMPACT: D5's spellbook.py condition is met: once the owner approves, every file but conduit.py can be built;
    D3's two conduit.py changes (`_activate_borrowed_spell` and its call in `notch_spell`) follow melder_0's
    landing, and the change set still lands in one notch. The patch's owner column, migration order and D5 lines
    now say so.
  NEXT: Ask the owner to approve the patch and that order.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T12:57:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner approved the patch as a whole and the build started (chat 2026-10-16: he chose "Approve, wait
    for melder_0", then wrote "btw you can start" and "melder_0 looks like hes done his thing"). melder_0 has not
    landed its notch-target change - its board row is active, `__version__` is 0.2.8248 and conduit.py changed at
    12:49:03Z - so the build follows the order the patch records: every file but conduit.py now, D3's conduit.py
    lines after melder_0 hands conduit.py back, one notch at the end. The owner also switched
    `agent_communication.backend` to `mailbox` ("talk to melder_1 in the mailbox please and switch the mailbox on in
    this context_compass yaml I'll tell melder_0"; melder_1 is this agent, so read as melder_0). Mail consumed (13):
    11 NOTICEs of 2026-09-26 to 2026-09-28 (notch and file-claim notices, all superseded by 0.2.8248); M0-175 (ACK
    of M1-18 and M1-19, nothing open); M0-176 (HANDOFF: spellbook.py and transfer_of_ownership.py are melder_1's;
    conduit.py stays melder_0's until its task lands, its `_notch_spell` call and fan-out lines unchanged, so D3's
    diff only shifts; it filed TASK-2026-10-16-notch_seam_checks_incoming_before_parking, a backlog draft for
    `_apply_notch`'s park-before-check order that it says fits D2). melder_1 answered with M1-20 (ACK).
  EVIDENCE:
  - context_compass/config/context_compass_config.yaml:122-123
  - context_compass/system_docs/patches/active/contract_recheck_on_notch_2026_10_16/architecture_patch.md:144-156
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:255-274
  - context_compass/tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md:339-358
  - context_compass/tickets/tasks/backlog/2026-10-16_notch_seam_checks_incoming_before_parking_task.md:14-34
  - src/melder/aether/conduit/conduit.py:5622-5629
  - src/melder/__version__.py:12-12
  IMPACT: The design gate is closed for every file but conduit.py. The seam task stays outside this patch unless the
    owner adds it (it edits `_apply_notch`, which D2 edits too). special_instructions/codex_mcp.md still directs MCP
    messaging and conflicts with the YAML; flagged to the owner, not edited.
  NEXT: Re-read the patch in its read order and the code it changes, whole, then write the red tests on a scratch
    copy of the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T13:24:49Z
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
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:209-322
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1623-1679
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1135-1225
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1844-1866
  IMPACT: The build follows the patch with these five details; the system docs state them when the patch is
    promoted.
  NEXT: Write the red tests on the scratch copy: the registry walk, the Book marks, the gate and the catch-up, the
    report, and the C1-C4 and X1 regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T14:08:56Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_red_all_gil0.txt:1-60
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_integration_red_gil0.txt:1-112
  - context_compass/artifacts/meld_contract_scan_20261015/staged_tests/test_conduit_integration_notch_revalidation.py:1-589
  - context_compass/artifacts/meld_contract_scan_20261015/staged_tests/test_spell_system_states_dependent_walk.py:1-377
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_today_gil0.txt:1-8
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2215-2266
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2484-2510
  - src/melder/aether/spellbook/spellbook.py:3311-3414
  IMPACT: The red set is complete and every red is one rule 2 owns; the build can start. Index uncontract joins the
    live defects the marks fix (with index destroy and the link-time dependents).
  NEXT: Implement spell_system_states.py (binding key, walk, walk-on) on the scratch copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T14:08:56Z
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
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:209-319
  - src/melder/aether/spellbook/spellbook.py:3155-3214
  - src/melder/aether/spellbook/spellbook.py:3416-3469
  IMPACT: The walk's and the clear's tests pin these; the system docs state them at promotion.
  NEXT: Implement spell_system_states.py on the scratch copy.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T14:08:56Z
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
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1088
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1135-1196
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1226-1240
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_integration_red_gil0.txt:92-98
  IMPACT: The race test may stay red after the build; whether a meld-time refusal (a missing provider in a target
    pass recorded as a visibility failure, so the meld raises SpellbookValidationError) joins this patch is the
    owner's call.
  NEXT: Measure the race after the build, then put the scope question to the owner with the numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T14:30:05Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_states.py:1-372
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_spellbook.py:1-454
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_doubles.py:1-58
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_after_states_spellbook_gil0.txt:1235-1267
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_after_states_spellbook_gil0.txt:1192-1234
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_states_spellbook_green_gil0.txt:1-17
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_scratch_marks_gil0.txt:1-11
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_today_gil0.txt:1-8
  IMPACT: Half the build holds on its own tests, and the index uncontract now reaches its consumer's state; the
    meld gate still scans and has no catch-up, so the integration reds stay until meld.py lands.
  NEXT: Write apply_rule2_src_meld.py (scan out, the catch-up in) and run test_meld.py with the GIL off.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The meld and report halves of rule 2 are in on the scratch copy (apply scripts, each run with --check
    first), so every file but conduit.py is built. meld.py: the per-meld scan
    (`_check_contracts_and_force_revalidation` and `_iter_spell_contract_defaults`) and its imports are gone;
    `_ensure_lineage_resolvable` runs the catch-up when the spell will compile there (`_may_compile`), then the
    structural branch, then the resolution check unless the spell is flagged `resolution_required`;
    `_ensure_runtime_resolution_ready` runs the catch-up
    before its own window; the catch-up walks the plan's dependencies (`_iter_planned_dependencies`: socket targets
    and contracted providers, each at the version its lineage selects in the Book's pool) and refreshes each stale
    one (`_refresh_dependency_structure`: its window, its lock, a staleness recheck, phases 1-4 with its owner Book,
    then its own plan reset). The report: Phase 4's presence check walks snapshots and names the remedy, and
    SpellbookValidationError shows a gating warning (`GATING_WARNING_CODES`) as a spell's reason (D1-B). The ward's
    comment names the analyzer's helper. Python 3.14.7t, GIL off: the seven rule-2 files 340 passed, 1 failed (the
    meld-vs-notch race test); the suite chunks pass - unit_aether 4512, unit_sb 2578, unit_util 831, comp_aether
    1386, comp_sb 819, int_sb 647, int_mt 54, int_aether 795, int_cryst 276 and the rest - except int_conduit, 348
    passed and 1 failed, the same race test; comp_sb and int_mt passed after two test updates (next Note); exper
    ran without its benchmark module, which the scratch tree lacks (244 passed). GIL on: every chunk passes,
    int_conduit 349 with the race test.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_meld.py:1-528
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_report.py:1-338
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_conduit_ward.py:1-25
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_parity.py:1-64
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_mutation_race.py:1-81
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_green_all_gil0.txt:1-52
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_scratch_suites_gil0.txt:1-25
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_scratch_suites_gil1.txt:1-21
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_scratch_int_conduit_gil0.txt:1-52
  IMPACT: The build holds on its tests in both GIL modes except the GIL-off race, which fails at today's rate (the
    race Notes below); D3's conduit.py lines and the landing remain.
  NEXT: Record the build details and the cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Build details inside the approved design (beside those of 13:24:49Z and 14:08:56Z). (1) The catch-up keeps a
    reset dependency's `requires_spellspace_request`: `clear_phase5_artifacts` sets it False, and the conduit door
    refuses a spellspace-scoped spell by that flag before the gate, so clearing it would let a direct meld of such a
    dependency through; its own next pass recomputes it. (2) A valid existing creation or non-resolvable dependency
    is refreshed but not reset - neither ever plans. (3) `_iter_planned_dependencies` reads the topology first and
    needs the Book only when one is recorded (RuntimeError "Spell has no owning Spellbook surface." otherwise).
    (4) The renderer counts a gating warning as an explanation for its restating rule, counts it with the hidden
    warnings when the spell also shows errors, and keeps "No validation error was recorded" for a spell with
    neither when no diagnostics were handed in. (5) Two tests follow the new behaviour and keep what they guard: the
    structural snapshot parity test's notch event records, in both worlds, the first meld's UnresolvedInputError
    after a notch to a class `engine: Engine` does not select (probe C4), then notches back; the mutation-during-meld
    tests mark the consumer (`mark_contract_dependents_dirty`) before their forced meld, which relied on the retired
    scan's forced pass, and still expect SpellbookValidationError.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_meld.py:453-520
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_meld.py:351-421
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_report.py:200-268
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_parity.py:1-64
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_mutation_race.py:1-81
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:742-769
  - src/melder/aether/conduit/meld/conduit_meld.py:559-580
  IMPACT: The system docs state these at promotion; the two test updates are part of the change set.
  NEXT: Record the cost before and after.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Cost (probe_rule2_cost.py; "before" is the scratch tree with the seven baseline src files restored; caching
    off; Python 3.14.7t). A warm meld of the borrower's contract consumer: GIL off 1668.46 us with a 5-11 pass every
    meld -> 2.57 us with none; GIL on 1704.80 -> 2.68 us. A notch to B, then one meld: GIL off 1389 -> 2523 us (one
    pass; two structural reruns instead of one - the catch-up refreshes the provider, then the consumer reruns), the
    notch back 1684 -> 2485 us; GIL on 1628 -> 2395 and 1882 -> 2658 us. After a notch the warm consumer is back at
    2.62 us (GIL off), where today it stays at 1260 us a meld. The notch's walk with 200 dependents: GIL off 0.69 /
    0.21 ms (to P2 / back) -> 1.17 / 0.47 ms; GIL on 0.76 / 0.16 -> 1.17 / 0.40 ms.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_cost.py:1-122
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_cost_before_gil0.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_cost_after_gil0.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_cost_before_gil1.txt:1-8
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_cost_after_gil1.txt:1-8
  IMPACT: About 650 times cheaper per warm meld of a contract consumer; each provider change costs 0.8-1.1 ms more
    (one more structural rerun) and a notch's walk 0.2-0.5 ms more at 200 dependents.
  NEXT: Record the race on both trees.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The meld-vs-notch race on both trees (the integration race: four threads meld the borrower's contract
    consumer while the lender notches its provider 20 times; GIL off unless said). Rates (probe_rule2_race_rate.py,
    20 runs a tree): 7 of 20 runs end a thread with an unexpected exception on both trees - before, 9
    MeldExecutionError (the scan's "SpellContract could not be resolved") and 8 AttributeError "'SpellContract'
    object has no attribute 'ping'"; after, 9 AttributeError and 2 RuntimeError "Cannot build CreationContext before
    spell_codegen_creation exists.". Melds: before 55 A and 68 refused, after 7688 A and 57 refused; no meld returned
    B on either tree; the first meld after the race returned A in every run. GIL on: 0 of 20 on both trees. Kinds
    (diag_race_kinds.py, 400 runs a tree, instrumented, so its timing is perturbed and its counts are not rates):
    before 257 AttributeError, 151 MeldExecutionError (the scan), 8 RuntimeError "many_only manifest references
    unknown spell_id" (the parked A) and 2 "Cannot build CreationContext"; after 242 AttributeError, 73 "Cannot build
    CreationContext", 9 "many_only manifest" and 1 "Spell creation context was not published: the selected builder
    failed". Every kind but the scan's refusal occurs on today's tree.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_race_rate.py:1-97
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil1.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil1.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/diag_race_kinds.py:1-178
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_before_gil0.txt:193-197
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:209-213
  IMPACT: The race predates rule 2 and rule 2 leaves its rate as it was; it removes the scan's refusal and makes the
    internal "Cannot build CreationContext" error more frequent, because more melds pass the gate without a forced
    pass.
  NEXT: Record what each kind is.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What each race kind is (the first occurrences' timelines and tracebacks, both trees). `notch_spell` parks and
    reactivates the borrower's contracted copies after its transaction has ended (`_deactivate_borrowed_spell`,
    `_emit_index_notch`), so a consumer meld can be anywhere between its gate and its first execution when that
    happens: (a) AttributeError - a target pass ran Phase 8 while the copy was parked and, in a dynamic world,
    compiled the raw SpellContract default (`_allow_missing_contract_providers`); (b) "many_only manifest references
    unknown spell_id '<A>'" - a pass compiled its plan against A, the fan-out parked A, and the cold door's first
    hydration looked the plan's step ids up in the Book's pool, which no longer held A (`_resolve_spell_lookup`);
    (c) "Cannot build CreationContext" - a meld that had passed the gate was admitted after another meld's pass
    failed with the plan cleared (pass-done plan=False, then that meld refused), so its context build found no plan;
    (d) "was not published" - a meld waiting on that failed build. (c) settles the HYPOTHESIS recorded for the
    first diagnosis, and contradicts `_execute_admitted`'s docstring, which says a meld "never ... builds from a
    missing plan": that holds only when the rebuild it waited for succeeded.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:61-86
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:87-147
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:148-208
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_before_gil0.txt:134-192
  - src/melder/aether/conduit/conduit.py:5725-5751
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1088
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:320-341
  - src/melder/aether/conduit/meld/meld.py:866-929
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:68-125
  IMPACT: The four kinds are one gap - in-flight borrower melds are not ordered against a notch's fan-out - which
    rule 2's marks do not close: they make the next meld correct, not one already in flight.
  NEXT: Put the scope question to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T15:19:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner decides the race's scope. A: fold a fix into this patch - in-flight melds refuse with
    SpellbookValidationError, the 0.2.8227 rule for a meld racing a sever or uncontract, at the three sites (a
    provider missing in a meld-time target pass becomes a visibility failure, while conjure keeps its link-later
    tolerance; a meld admitted to a spell with no plan re-enters the gate; a hydration miss of a plan's spell id is
    treated as a stale plan); the patch docs grow first and come back for approval. B (recommended): land rule 2
    as approved with the race test marked xfail(strict=False) naming a follow-up task, opened now with this
    evidence, which also weighs moving the fan-out under the notch's frozen gates (conduit.py, where D3 edits too).
    Reasons for B: the race and every kind but the scan's predate rule 2 at the same rate; its cause is the notch's
    fan-out order, not the marks; a fix touches the compiler, the hydrators and the meld door beyond the approved
    nine components. Cost of B: until the follow-up lands, a GIL-off race shows the internal RuntimeError more often
    and the scan's MeldExecutionError no more.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:209-213
  - src/melder/aether/conduit/conduit.py:5725-5751
  IMPACT: A changes the patch and its review; B lands the approved patch and leaves a known, tracked race.
  NEXT: Ask the owner (A or B), with the numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T15:55:55Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner chose B for the meld-vs-notch race (chat 2026-10-16, "Separate task (Recommended)", after asking
    whether it concerns all melds - it concerns only a borrower's contract consumer melded on another thread while
    its provider is being notched, GIL off). Rule 2 lands as approved; the race is
    TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (backlog, p1: one kind silently returns a
    consumer built with the SpellContract default), opened with the measurements and the mechanism and its artifact
    row. The race test carries `@pytest.mark.xfail(strict=False, raises=AssertionError, reason=...)` naming that
    task; any other failure of the test still fails it. On the scratch copy the test file then runs 13 passed plus
    the race test 2 xfailed / 3 xpassed in five GIL-off runs and 5 xpassed in five GIL-on runs. The RISK of
    14:08:56Z is settled by this decision.
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:1-229
  - context_compass/artifacts/meld_contract_scan_20261015/open_race_followup_task_2026_10_16.py:1-272
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_race_xfail.py:1-39
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_race_xfail_gil0.txt:1-20
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_race_xfail_gil1.txt:1-20
  IMPACT: Nothing in the approved patch changes; removing the xfail marker belongs to the follow-up's exit gate.
  NEXT: Build D3 on the scratch copy (notch-back reactivation, the grant docstring, the anchored notch-back test), to
    be re-checked against conduit.py when melder_0 hands it over.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T16:13:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_0's HANDOFF (M0-177, consumed): TASK-2026-10-16-public_notch_target_for_staged_versions landed as
    0.2.8249 and is closed - `notch_spell`, `add_to_spell_index` and `remove_from_spell_index` take `spell_id=` (the
    owner's extension went into the same notch) - and conduit.py is melder_1's; rule 2's notch goes above 0.2.8249.
    melder_0 runs the rebuild last and then holds no file; its closed-anchor row says "Rebuilt last, both checks
    OK". Its FYI: spellbook.py's `_notch_spell` and `_apply_notch` docstrings say the notch claims the Book INTENT,
    while the notch strategy's seal (`_seal_scope_keys`) claims every listed spellbook and conduit and the binding
    key EXCLUSIVE - a stale docstring in a file rule 2 edits, corrected with the landing. Messaging stays the
    mailbox (codex_mcp off by the owner).
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-10-16_public_notch_target_for_staged_versions_task.md:1-20
  - src/melder/aether/spellbook/spellbook.py:3775-3838
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:239-269
  - context_compass/attention_board.md:212-212
  IMPACT: D5's last condition is met: D3 can land, so the whole change set lands in one notch; the real-tree copy
    waits only for melder_0's rebuild to finish, so that rebuild does not pick up half of rule 2.
  NEXT: Confirm melder_0's rebuild is done, compare the baselines with the real tree, refresh the scratch copy from
    it and re-apply the build there with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T16:13:44Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_conduit_d3.py:1-107
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_conduit_ward_d3.py:1-48
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_d3.py:1-100
  - context_compass/artifacts/meld_contract_scan_20261015/staged_tests/test_conduit_integration_notch_revalidation.py:419-489
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_d3_red_gil0.txt:1-22
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_d3_green_file.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_d3_scratch_suites_gil0.txt:1-21
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_d3_scratch_suites_gil1.txt:1-21
  IMPACT: The whole approved change set is built and green on the scratch copy; what remains is the copy onto the
    current real tree, its suites, then docs, release note, notch, closure and rebuild.
  NEXT: Refresh the scratch copy from the real tree and re-apply every apply script with --check first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T16:13:44Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_conduit_d3.py:24-107
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_tests_d3.py:1-100
  - src/melder/aether/conduit/conduit.py:280-310
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  IMPACT: The system docs state (1)-(3) at promotion; the patch's validation line is met in substance.
  NEXT: Refresh the scratch copy from the real tree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T16:39:05Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rule 2 is applied to the real tree (on melder_0's 0.2.8249 landing), not yet notched, documented or
    rebuilt. After melder_0's rebuild the scratch copy was refreshed from the real tree and the fourteen apply
    scripts re-run on it in the recorded order, each with --check first, the last the docstring correction melder_0
    reported in M0-177 (`_notch_spell` and `_apply_notch` now say the notch runs inside the transaction the Conduit
    admits and its seal is EXCLUSIVE, not spellbook INTENT); the two staged test files copied in. That fresh tree
    passed every suite chunk with the GIL off and on: unit_aether 4528, unit_sb 2578, unit_util 831, comp_aether
    1386, comp_sb 819, int_conduit 350 plus the race test (xfailed with the GIL off, xpassed with it on), int_sb 647,
    int_mt 54, int_aether 805, int_cryst 276, unit_cryst 607, comp_cryst 110, unit_mr 277, comp_mr 40, int_mr 67,
    comp_util 41 (23 skipped), unit_top 146, unit_build 116, int_live 1, unit_arch 18, exper 250 (4 skipped),
    unit_gh 491, unit_llm 28 (five chunks rerun after the repository folders they read were copied into the fresh
    tree, as the run file notes). The same scripts then applied to the real tree, --check first: its 18 changed
    files (7 src, 9 changed tests, 2 new tests) are byte-identical to the fresh tree, and a content compare of src/
    and tests/ finds no other difference either way. Real-tree smoke (the two new files and test_meld.py): 135
    passed and the race test xfailed with the GIL off, 135 passed and xpassed with it on. The real tree's suites
    were not rerun beyond that smoke: its src/ and tests/ are the fresh tree's byte for byte. `__version__` is
    still 0.2.8249; no git index lock.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_fresh_suites_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_fresh_suites_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rule2_landed_smoke.txt:1-2
  - context_compass/artifacts/meld_contract_scan_20261015/apply_rule2_src_spellbook_notch_seal_doc.py:1-46
  - src/melder/aether/spellbook/spellbook.py:3844-3915
  - src/melder/aether/conduit/conduit.py:5750-5758
  - src/melder/aether/conduit/conduit.py:6267-6310
  - src/melder/__version__.py:12-12
  IMPACT: The approved change set is in place on the real tree and green; turn-in remains: the system docs and
    their indexes, the graph, the patch promotion, the release note, the notch, NOTICE M1-21, closure, rebuild last.
  NEXT: Write the system docs (src_architecture, src_components, tests_architecture, tests_components) and
    regenerate their indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T17:11:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The four system documents carry rule 2, D1-B, D2 and D3 (0.2.8250), read back from disk with every index
    regenerated and `--check` OK. src_architecture (4696 -> 4854 lines, 62 sections): the Architecture Summary, the
    Meld-Time Validation Gate (steps 8-9) and SpellIndex Mutation Entry (steps 5-6) sequences, a new operational
    invariant (the marks, the downstream walk, D3, the catch-up, cost and lock order), four failure modes (two
    Breaking, one fixed, the known race), the code map (five extents remeasured, two files added), the sources and
    a handoff entry. src_components (11695 -> 11848, 154 sections): dated paragraphs in Spellbook Core, Conduit
    Runtime, ConduitWard and Contracts, Meld Resolution Runtime and SpellCompiler and Validation Pipeline, the Meld
    Runtime Gating and SpellSystemStates Registry C2 entries, the gate and notch flows, seven extents remeasured, the
    sources and a handoff entry. Every numeric citation into the seven changed src files (19 and 26) was remapped
    line by line against the pristine tree with difflib, all exact. tests_components (3584 -> 3697, 69 sections):
    the walk's unit file and the notch-revalidation integration file catalogued as key files with code-map records,
    the Book marks, the gate's catch-up, the report and the explicit mark named in their clusters, four records
    remeasured, counts recounted; it also corrects counts the 0.2.8248-0.2.8249 entries left behind (unit spellbook
    157 -> 158, integration spellbook 50 -> 51, the core section's 838 test modules, a core set of 252 while the
    catalog held 256); the core set is now 258 paths, equal to the code map. tests_architecture (973 -> 988, 32
    sections): the recount, the known race as a non-strict xfail under Failure Modes, a source and a handoff entry.
    After the tests script, one phrase of the walk bullet (a contract cycle) was corrected and two of its lines
    rewrapped by hand on disk. Checks: no package or absolute path; no new line over 120 characters; content
    preservation - every changed or removed baseline multiset entry (51 / 57 / 3 / 23) is a remapped citation, a
    remeasured extent, a recount or a sentence the new text rewrites; the in-bounds recipe over the src pair's 1416
    citations reports only the two bare file names in the 0.2.8247 handoff prose (known).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1104-1148
  - context_compass/system_docs/src_architecture.md:2109-2151
  - context_compass/system_docs/src_architecture.md:4332-4343
  - context_compass/system_docs/src_components.md:11312-11322
  - context_compass/system_docs/tests_components.md:952-986
  - context_compass/system_docs/tests_components.md:3471-3484
  - context_compass/system_docs/tests_architecture.md:592-598
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_src_architecture_rule2_2026_10_16.py:1-395
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_src_components_rule2_2026_10_16.py:1-329
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_tests_rule2_2026_10_16.py:1-314
  - context_compass/artifacts/meld_contract_scan_20261015/remap_citations_rule2_2026_10_16.py:1-73
  - context_compass/artifacts/meld_contract_scan_20261015/runs/docs_preservation_rule2_2026_10_16.txt:1-138
  - context_compass/artifacts/meld_contract_scan_20261015/runs/citation_bounds_rule2_2026_10_16.txt:1-3
  IMPACT: The documentation half of the turn-in is done; the graph, the patch promotion, the release note, the
    notch, NOTICE M1-21, the owner's acceptance, closure and the rebuild remain.
  NEXT: Re-extract the graph with --strict, re-read the stale nodes of the seven changed files and accept or rewrite
    their prose, then assemble.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T17:11:57Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rubric scores, from disk after the index rebuilds (self-scored; no independent reviewer), unchanged from the
    0.2.8247 and 0.2.8249 passes: src_architecture 83 (B) - fidelity 4, contract 5, depth 4, addressability 4, join
    4, mirror 4; src_components 83 (B) - 4, 5, 4, 4, 4, 4; tests_architecture 83 (B) - 4, 5, 4, 4, 4, 4;
    tests_components 77 (B) - 4, 4, 3, 4, 4, 4. Basis: src_architecture was re-read whole after this session's
    compaction; in the other three the sections this landing wrote were re-read from disk, and the src_components
    claims spot-checked against the source (`Conduit._activate_borrowed_spell`, `Meld._may_compile`,
    `Meld._is_stale`) hold; the unchanged remainder keeps the earlier judgment. The measurable half (the same
    script, rerun): one H1 each, no duplicate indexed name, no unclosed heading, contracts complete and in order, no
    portability or absolute-path hit, 162 / 36 / 234 / 258 code-map records complete with every extent equal to its
    file today, every Key Files path resolving. Why not 5: fidelity - both src meld-flow diagrams still name
    "Phase12 Compiled Executors" and some older one-line failure modes carry no citation; depth - those lines and
    four src_components entries with thin fields (PhaseScheduler); addressability - container H2s that hold only
    sub-headings; join - 148 of 162, 36 of 36, 221 of 234 and 240 of 258 verified_at stamps carried forward
    although every extent measured equal today; mirror - each pair shares its contract and adds different
    non-contract sections. tests_components contract 4: a Table of Contents and a Component Template sit among its
    sections; depth 3: its Mock Fixture Corpus entry has five thin fields.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/rubric_checks_rule2_2026_10_16.txt:1-52
  - context_compass/artifacts/meld_contract_scan_20261015/rubric_checks_2026_10_16.py:1-173
  - context_compass/system_docs/src_architecture.md:4116-4116
  - context_compass/system_docs/src_components.md:11051-11051
  - context_compass/system_docs/src_architecture.md:743-743
  - context_compass/system_docs/src_components.md:5818-5891
  - context_compass/system_docs/tests_components.md:156-189
  - context_compass/system_docs/tests_components.md:650-739
  - src/melder/aether/conduit/conduit.py:6267-6310
  - src/melder/aether/conduit/meld/meld.py:1353-1425
  - context_compass/agent_onboarding/default/design_engineer/policies/system_document_quality_rubric.md:43-54
  IMPACT: All four documents stay band B and usable as inputs; their weak points predate this landing.
  NEXT: Re-extract the graph with --strict and read its drift report.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T17:29:50Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The graph and the patch promotion carry the landing. `extract_graph.py --strict` on Python 3.14.7t: 591
    descriptors, 1227 nodes, 451 of 451 `specializes` targets resolved, skipped 0, new 0, orphaned 0. The authored
    prose of the seven nodes this change touches was re-read against their source and edited where it described the
    retired scan or missed a new duty (`graph_semantics_rule2_2026_10_16.py`, authored fields only, each edit
    refusing an unexpected old value): SpellSystemStates (the binding key per lineage and the downstream walk;
    `_binding_key_by_index` owned), Meld (the recheck replaces the scan's signature read; the catch-up),
    ContractProviderPresenceStrategy (the snapshot walk; the remedy), SpellbookValidationError (a gating warning
    shown as the reason), Spellbook (the contracted-map marks; the notch's binding key and walk), Conduit
    (`_activate_borrowed_spell`), ConduitWard (a version grant's copy); then all seven were accepted. Walker:
    SEMANTICS_STALE 148 -> 141 and AUTHORED 1070 -> 1077 of 1232 nodes (9 unsemantic, 5 retired); the 141 left
    predate this landing, and the packages of the seven changed files that still show a stale node show only nodes
    outside them. `assemble_graph.py`: src_graph.md 28075 lines, 591 sections, 1227 nodes, 1415 edges, index 618
    lines, every range verified against its header; `--check` the same with no writes. The seven patch docs
    (architecture, five component, one code description) moved with `mv -n` from patches/active/ to
    patches/completed/contract_recheck_on_notch_2026_10_16/; the artifact board's seven active patch rows became one
    cleared promote_to_documentation row, and the ticket's Artifact Links name the archived folder.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/extract_graph_rule2_2026_10_16.txt:1-46
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_walker_report_rule2_2026_10_16.txt:1-111
  - context_compass/artifacts/meld_contract_scan_20261015/graph_semantics_rule2_2026_10_16.py:1-140
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_accept_rule2_2026_10_16.txt:1-9
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_walker_report_after_accept_rule2_2026_10_16.txt:1-109
  - context_compass/artifacts/meld_contract_scan_20261015/runs/assemble_graph_rule2_2026_10_16.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/runs/assemble_graph_check_rule2_2026_10_16.txt:1-4
  - context_compass/artifacts/meld_contract_scan_20261015/sync_patch_promotion_rule2_2026_10_16.py:1-58
  - context_compass/system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/architecture_patch.md:1-224
  - context_compass/artifact_board.md:103-103
  IMPACT: Every documentation surface the patch framework names is current; what remains is the notch, NOTICE M1-21,
    the release-note entry, the owner's acceptance, closure and the rebuild last.
  NEXT: Read `__version__` again and notch it to 0.2.8250; send NOTICE M1-21 to melder_0 through the mailbox.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T17:46:56Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The notch, the NOTICE and the release-note entry are in. `__version__` read 0.2.8249 at 17:30Z and is now
    0.2.8250 (the notch script refuses any other current value). M1-21 (NOTICE, no ACK requested) went to melder_0
    with its alert line, and the standing bullet sits under "Notch notice (melder_1, 2026-10-16)" on the attention
    board. release_docs/next_version_release.md (723 -> 857 lines): header `# Melder 0.2.8250`; one section after
    the 0.2.8249 one - the story, two examples, the measured cost, two Breaking changes (a destroyed index or a
    grant parked by a notch away gives SpellbookValidationError where the scan gave MeldExecutionError; a notch's
    dependents build the new version or raise the first meld's error), the lost provider reported by name, D3, the
    fixes, the known race (not changed yet) and what stays the same; one packaging bullet; the rebuild line for
    0.2.8250. Its two code blocks are byte-identical to the blocks `release_example_rule2_2026_10_16.py` runs, which
    pass on the landed tree with the GIL off and on. The same steps without the asserts on the tree before 0.2.8250
    (the real tree with the seven pristine src files restored): the consumer follows the notch at 1558 / 1682 us a
    warm meld (GIL off / on), 2.8 / 2.8 us now; after a sever the report says "No validation error was recorded",
    and names the contract and its remedy now; `Report`, two hops from the notched `Clock`, keeps building "utc",
    and builds "local" now.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/artifacts/meld_contract_scan_20261015/notch_0_2_8250_2026_10_16.py:1-26
  - context_compass/mailbox_board.md:912-922
  - context_compass/attention_board.md:176-176
  - context_compass/attention_board.md:289-293
  - context_compass/artifacts/meld_contract_scan_20261015/send_m1_21_2026_10_16.py:1-64
  - release_docs/next_version_release.md:1-3
  - release_docs/next_version_release.md:649-777
  - release_docs/next_version_release.md:853-857
  - context_compass/artifacts/meld_contract_scan_20261015/release_note_rule2_2026_10_16.py:1-175
  - context_compass/artifacts/meld_contract_scan_20261015/release_example_rule2_2026_10_16.py:1-111
  - context_compass/artifacts/meld_contract_scan_20261015/runs/release_example_rule2_2026_10_16.txt:1-14
  - context_compass/artifacts/meld_contract_scan_20261015/release_example_rule2_before_2026_10_16.py:1-108
  - context_compass/artifacts/meld_contract_scan_20261015/runs/release_example_rule2_before_2026_10_16.txt:1-36
  IMPACT: The turn-in now waits on the owner's acceptance; closure and the rebuild follow it.
  NEXT: Ask the owner to accept the landing, with the remove_index_from_contract finding below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T17:46:56Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Found while verifying the release example; pre-existing and outside this ticket's scope.
    `remove_index_from_contract` raises RuntimeError "Spell version <id> not found for conduit ID <lender>." when the
    borrower holds a parked copy of a member beside the active one (a version staged on the linked index, or the old
    version after a notch) and the hash seed orders the parked id first, and it leaves the unlink half done.
    `_remove_index_from_contract` uncontracts the members in `spells_in_index()` order - a set of version-id
    strings, ordered by the process's hash seed - and `_remove_contracted_spell` matches the active contracted copy
    by index membership, not by its own id: for the parked member's id it removes the active copy (the other
    member's), then the active member's id finds no copy and raises; the parked copy stays, and the index detail's
    cleanup and the borrower's `_remove_contracted_index` after the loop never run. Probe (English staged on the
    linked index, notched away from, French active): PYTHONHASHSEED 0-9 give the same outcome per seed on 0.2.8249
    and 0.2.8250 - seeds 3, 4, 6, 8 and 9 raise "Spell version French not found" and leave English parked - so rule 2
    neither causes nor changes it. UNKNOWN: whether an index destroy meets the same order (a cleaned index is matched
    by the copy's own id).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  - src/melder/aether/spellbook/bind/spell_index.py:274-286
  - context_compass/artifacts/meld_contract_scan_20261015/probe_index_uncontract_after_notch.py:1-82
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_after_notch_seeds_gil0.txt:1-20
  IMPACT: An agent that stages versions on a linked index and then unlinks it can meet a RuntimeError and an orphaned
    parked copy, in about half of all processes. The fix - match the active copy by its own id - changes the
    borrower Book's removal path, outside the approved patch, so it is the owner's to place.
  NEXT: Put it to the owner with the acceptance question: a backlog task (recommended) or no action.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T18:23:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner accepted the rule 2 landing (chat 2026-10-16, "Accept (Recommended)"). On the remove_index_from_
    contract defect he first answered "no lets fix it if you want to melder_0 is done", then, after the explanation,
    opened a discussion instead: after a notch, should the unlink not remove the borrower's inactive copy rather than
    the current one, and how do ownership transfers and contracts affect each other ("thats also an important
    question"). The closure waits for that discussion, because the transfer reading below found a gap in rule 2's own
    coverage. A batch of his earlier messages (D1-D5, "btw you can start", the mailbox switch) was delivered again
    in this exchange; all of them were acted on before and need nothing new.
  EVIDENCE: context_compass/artifacts/meld_contract_scan_20261015/runs/release_example_rule2_2026_10_16.txt:1-14
  IMPACT: Rule 2 is accepted; its closure and rebuild follow the owner's call on the transfer gap.
  NEXT: Put the findings below to the owner and take his direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T18:23:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What a failed unlink leaves (the defect of the FACT above, probed under PYTHONHASHSEED 3 and 0 on 0.2.8250):
    with English parked and French active, the failing order removes French's active copy under English's id, then
    raises for French; the contract no longer links the index, but the borrower Book still tracks it and still holds
    English parked. A second `remove_index_from_contract` returns normally and drops the tracking, yet English stays
    parked for good: the per-version loop runs only while the contract still lists the index. Seed 0 (French first)
    removes both copies cleanly.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272
  - context_compass/artifacts/meld_contract_scan_20261015/probe_index_uncontract_retry.py:1-73
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_retry_gil0.txt:1-16
  IMPACT: A retry hides the failure and keeps the orphan, so the fix belongs in the removal itself: each version
    removes its own copy (the active slot only when that copy is the version, else the parked map).
  NEXT: Discuss with the owner which copy a removal takes after a notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T18:23:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: How an ownership transfer meets contracts today (code read whole; probe on 0.2.8250, GIL off; the transfer
    code predates rule 2). Borrowers of the moved spell: (1) a version grant under the default `force_unshare=True`
    is removed, and the consumer's next meld names the lost contract - as documented; (2) an index link under the
    default is NOT removed: `_unshare_everywhere` removes borrower details one spell at a time, the ward refuses that
    for an index-link member ("cannot be removed on its own. Use remove_index_from_contract") and the transfer
    swallows the refusal, so the borrower keeps its index link and copy from the OLD owner and its consumer keeps
    building the provider; (3) `force_unshare=False` never repoints a grant or a link: `_repoint_borrowers` calls
    `_add_spell_to_contract` on the new owner's ward with the borrower as `conduit`, the roles reversed, so the
    ownership check refuses every time ("is not owned by this conduit, cannot contract it"), the refusal is
    swallowed, and the borrower stays on the old owner's contract while the new owner gains an empty link. The new
    owner: (4) it can meld the moved spell but cannot stage a version on its index - the flip adds the id to the new
    Book's `_spells_by_id` and pool but not its owned-id set `_spell_ids`, which `_apply_add_to_index` checks
    ("target index ... is not owned by this spellbook"), and the source drops it from its own, so neither Book lists
    it. The moved spell as a consumer: (5) its contracts stay with its old conduit pair; on the new owner its first
    meld names the missing contract (stewardship, not a working setup), and preflight's dependency check cannot see
    it, because a SpellContract is a key, not a dependency edge. From the code only: a target that borrowed the
    spell from the source loses that borrowed copy before the flip (`_unshare_target_conduit_contract`).
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:367-509
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:567-624
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1004-1052
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1507
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1808-1905
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1907-1978
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1779-1842
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1844-1952
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3189-3240
  - src/melder/aether/spellbook/spellbook.py:1251-1300
  - src/melder/aether/spellbook/spellbook.py:4089-4155
  - src/melder/aether/conduit/conduit.py:4264-4340
  - context_compass/artifacts/meld_contract_scan_20261015/probe_transfer_and_contracts.py:1-163
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_transfer_and_contracts_gil0.txt:1-71
  - context_compass/artifacts/meld_contract_scan_20261015/probe_transfer_unshare_refusal.py:1-44
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_transfer_unshare_refusal_gil0.txt:1-7
  - context_compass/artifacts/meld_contract_scan_20261015/probe_transfer_repoint_refusal.py:1-42
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_transfer_repoint_refusal_gil0.txt:1-3
  IMPACT: A transfer silently leaves index-link borrowers on an owner that no longer owns the spell, the repoint
    option does nothing, and the receiving agent cannot continue the stage -> notch loop on the object it received;
    each is pre-existing and outside rule 2's approved patch except the gap in the next Note.
  NEXT: Put the transfer findings and the design question (what borrowers should get after a transfer) to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T18:23:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: CONFLICT
  CLAIM: A gap in rule 2's own coverage, missed in its build: the transfer flip calls `unregister_index` (which drops
    the lineage's binding key) and then `register_index` without `binding_key=`, so after a transfer the registry
    holds no key for the moved lineage (probe: "registry binding key=None"). The downstream walk finds a lineage's
    SpellContract consumers only through that key, so until the moved lineage is notched or bound again, a notch of
    something it depends on does not mark its borrowers' consumers. src_architecture's rule-2 invariant says
    `register_index(binding_key=...)` records one key per lineage; after a transfer it does not. The five Book
    mutators still mark by the copy's own key, so direct provider changes are covered. Fix: pass
    `binding_key=spell_obj._key` in the flip's `register_index` and in its rollback.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1507
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:470-482
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:973-1036
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1147-1222
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_transfer_and_contracts_gil0.txt:1-71
  IMPACT: The accepted change set misses one path its invariant claims; the owner decides whether the fix joins rule
    2 before its closure or the transfer follow-up.
  NEXT: Ask the owner, with the transfer findings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T18:46:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner corrected melder_1's reading of his unlink question (chat 2026-10-16: "no I never said drop
    what are you saying, dude you really don't understand melder"). He never proposed that a notch drop a
    borrower's old copy; melder_1 invented that reading, and it contradicts the model: a notch only moves which
    version of an index is active, versions coexist, and an index link holds a copy of every member (the active
    one in the active maps, the others parked). His point stands as he made it: after a notch, an unlink must
    remove the contracted inactive spell for the inactive version, not the current spell - each version's
    removal takes that version's own copy.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:10-25
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  IMPACT: The fix is the owner's rule as stated; parked copies stay by design. No src edit before he directs it.
  NEXT: Answer the owner with his point restated and the code read below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T18:46:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: `_remove_contracted_spell` re-read whole on 0.2.8250. Asked to remove one version, it scans the
    borrower's ACTIVE map for an index that lists that version as a member (`spell_id in idx._spells_in_index`)
    and removes that index's active copy, whichever version it is; only when no active entry matches does it
    look in the parked map. A cleaned index is matched by the copy's own id instead. So it takes the wrong copy
    whenever it is asked for a parked version while another version of the same live index is active on that
    borrower - the unlink after a notch (reproduced) is that call - and an index destroy is not affected:
    `_emit_index_destroy` runs on the cleaned index (this resolves the UNKNOWN of 17:46:56Z). Removing an
    active copy of a live index also discards every member id of the index from the borrower's
    `_contracted_spell_ids`, parked members' included; what reads those ids for a parked copy is UNKNOWN. The
    fix the owner's rule gives: match the active entry by its own id for a live index too, else the parked
    map, and discard only the removed version's id.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2389-2402
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517
  IMPACT: The fix sits in that one Book method, so every caller gets it, and the unlink's half-done state and
    orphaned parked copy go with it. It edits spellbook.py, which melder_1 holds; the owner places it.
  NEXT: Take the owner's direction on placing it (before rule 2's closure, or with the transfer follow-up).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T18:46:51Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-178 consumed (QUESTION from melder_0, 2026-10-16T18:37:02Z, ACK requested). The owner asked
    melder_0 (chat 2026-10-16) to replace "version id" by hand with spell_id or the spell index id where it
    relates to a spell index, wording only. It touches docstrings and comments in spellbook.py (28),
    spell_system_states.py (12), conduit_ward.py (9), conduit.py (8) and meld.py (4), some tests,
    src_architecture, src_components and tests_components, graph descriptors and the release note; melder_0
    edits none of them until melder_1 releases them. melder_1 answered with M1-22 (ACK): nothing is free yet.
    Held until rule 2's closure and rebuild: __version__.py; spellbook.py, spell_system_states.py, meld.py,
    conduit.py, conduit_ward.py, contract_provider_presence_strategy.py and spellbook_validation_error.py;
    transfer_of_ownership.py; rule 2's 11 test files (the nine the apply_rule2_tests_*.py scripts edit and the
    two new ones); the four system docs and their indexes; the seven graph descriptors with src_graph.md and its
    index; the release note.
  EVIDENCE:
  - context_compass/attention_board.md:187-187
  - context_compass/mailbox_board.md:912-922
  IMPACT: Rule 2's closure and rebuild now also gate melder_0's wording lane; the owner's direction on the open
    findings sets when the files come free.
  NEXT: After rule 2's rebuild, send melder_0 a NOTICE releasing the held files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T20:59:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner (chat 2026-10-16): the contract must be kept up to date with the changes that occur - when a
    spell goes inactive, that should show - and he asked for the unlink defect as an example. What is recorded
    today (read whole): the borrower Book keeps each borrowed copy, by version id, in exactly one of two lists,
    active (`_contracted_spells_by_id` with the index-keyed and lookup maps) or inactive
    (`_inactive_contracted_spells`); a notch moves the outgoing copy to inactive (`_deactivate_contracted_spell`)
    and the incoming one to active (`_reactivate_contracted_spell`, `_ensure_contracted_active`). On the ward
    side an index link's `IndexDetail.selected_spell_id` follows the active version (`update_selected` in
    `_emit_index_notch`), but the per-version `Detail` rows carry version, permission, reason and sources and no
    active/inactive state. `_remove_contracted_spell` consults neither by version. The owner decides whether the
    contract's per-version row should carry the state too, or the removal reads the Book's lists, which already
    show it.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/contract/details.py:14-247
  - src/melder/aether/conduit/conduit_ward/contract/details.py:249-404
  - src/melder/aether/conduit/conduit_ward/contract/contract.py:99-124
  - src/melder/aether/spellbook/spellbook.py:1623-1774
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  IMPACT: The removal fix needs no new state; a state field on the contract row is a design addition that every
    notch fan-out would have to keep in step with the Book's lists.
  NEXT: The owner's answer on the contract row; no src edit before it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T21:00:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M0-179 consumed (NOTICE from melder_0, 18:56:42Z, no ACK requested): before M1-22 arrived it had
    reworded one docstring line of transfer_of_ownership.py (1798, "The managed version id."), has put it back,
    and keeps that file and __version__.py on its list of files it waits for; its wording landed only in files
    nobody holds (112). Checked read-only (GIT_OPTIONAL_LOCKS=0, no index lock): transfer_of_ownership.py's blob
    equals HEAD's, HEAD being the owner's commit 192482b4c (2026-10-16 19:47Z, "Update version to 0.2.8250 ..."),
    and the file keeps rule 1's `resolvable=` arguments at the flip and its rollback, so nothing of melder_1's
    lanes was lost. The owner has committed 0.2.8250; rule 2's closure and the rebuild are still open.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1000-1003
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1486-1490
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1790-1802
  IMPACT: transfer_of_ownership.py is as melder_1 left it; the binding-key fix, if the owner places it, applies
    to the committed file. melder_0's 112 reworded files are outside rule 2's set; the last rebuild of the day
    covers them.
  NEXT: Answer the owner on the contract state and the unlink example; release files by NOTICE after the rebuild.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T21:22:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner approved the removal fix (chat 2026-10-16, "yeah sure this makes sense", answering "Want me
    to make the change now, with a test that runs the unlink with each version going first?"; his rule: "you
    remove that spell if its not active, you look in inactive, thats it"). `Spellbook._remove_contracted_spell`
    removes the copy of exactly the version it is asked for: the active copy only when that copy IS the version,
    otherwise the parked copy, and it raises only when the Book holds neither; rule 2's mark stays on an active
    removal. It joins this ticket as its own source change with its own notch (0.2.8251 if `__version__` still
    reads 0.2.8250 at landing). The existence set `_contracted_spell_ids` keeps today's handling: it is
    index-level by design (both add paths record every member id of the index) and only `snapshot_state` and the
    per-conduit key checks read it; melder_1's earlier word that the fix would discard only the removed id is
    withdrawn, and the owner was told before any edit. One existing test asserts the old behaviour - it removes a
    member id that has no copy and expects the active copy gone - and is changed to remove the active copy by its
    own id. The patch gate applies (a contract-removal behaviour change with a src_architecture failure-mode
    entry): patch docs under system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/ come before
    the src edit. Still the owner's, untouched: the contract row's active/inactive state, transfers vs contracts,
    and rule 2's binding-key gap on the transfer path.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3344-3463
  - src/melder/aether/spellbook/spellbook.py:3178-3247
  - src/melder/aether/spellbook/spellbook.py:3249-3291
  - src/melder/aether/spellbook/spellbook.py:1989-2046
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2221-2272
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2389-2438
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2491-2517
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2557-2589
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2770-2900
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3189-3330
  - tests/component/melder/spellbook/test_spellbook_component_contracts.py:379-418
  IMPACT: Every caller asks for one version's copy - the index unlink, destroy and member removal (through
    `_uncontract_member_spell`), a root's dependency fallout (`_remove_root_from_contracts`) and a version
    uncontract (`_remove_spell_from_contract`) - so each now gets that copy, and the unlink completes in either
    member order instead of raising in about half of all processes.
  NEXT: Write the patch docs and link them; then the red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T21:24:21Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch docs for the removal fix are written and linked (patch id
    contracted_copy_removal_by_version_2026_10_16: architecture, one component, one code description), read in
    the gate's order. Mapping, patch section -> implementation -> validation: architecture Invariants (one
    version, one copy) -> the active-entry match in `Spellbook._remove_contracted_spell` by the copy's own
    `spell_id`, the parked branch and its raise unchanged -> the unit tests (parked removal beside an active
    version; a copyless member id raises and keeps the active copy); component Before/after -> the same method
    and the one component test that asserted the old match -> that test removing the active copy by its own id;
    component Validation (integration) -> the unlink after a notch with each member first, order forced ->
    both copies gone, the index untracked, nothing raised; code description Control flow 5 -> rule 2's mark
    kept on the active branch -> the existing rule 2 unit tests stay green. Unknowns: none for the target path.
  EVIDENCE:
  - context_compass/system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/architecture_patch.md:1-44
  - context_compass/system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/component_patch_borrower_contracted_removal.md:1-35
  - context_compass/system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/code_description_patch_remove_contracted_spell.md:1-22
  IMPACT: The patch gate's entry checklist is met; the src edit waits only on the red tests.
  NEXT: Write the red tests and run them on the current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T21:36:02Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red on the unchanged src (0.2.8250), GIL off, scratch tree /tmp/cc_res/removal/tree (the real tree
    plus apply_removal_tests_2026_10_16.py): 5 failed, 21 passed - exactly the five cases the fix is for. Unit:
    removing parked sid-1 removed the active sid-2 copy; a copyless member id did not raise (it took the
    active copy); the parked-first order raised "Spell version sid-2 not found". Integration (public calls):
    the unlink after a notch, parked member first, raised "Spell version <new> not found for conduit ID
    <owner>"; removing the old version's grant (by its Spell) took the new version's active copy. The
    active-first orders and the component file, with its updated test, pass on the old src as predicted.
    Found on the way, outside the fix: `add_spell_to_contract` and `remove_spell_from_contract` by `spell_id=`
    of a parked version raise "Provided spell_id ... does not match inspected ID ..." (their argument check
    resolves a parked id to the index's active member, as `notch_spell` did before 0.2.8249); the grant test
    passes the Spell object it kept while the version was active.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/apply_removal_tests_2026_10_16.py:1-291
  - context_compass/artifacts/meld_contract_scan_20261015/runs/removal_red_gil0.txt:1-20
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  IMPACT: The tests fail for the defect and pass for harmless orders; the src change can go in.
  NEXT: Apply the one-method change on the scratch tree and rerun these tests, then the suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T21:48:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The removal fix is in the real tree, byte-identical to the scratch tree it was tested on.
    `Spellbook._remove_contracted_spell` matches the active copy only by the copy's own `spell_id` (for a live
    or a cleaned index alike) and falls back to the version's parked copy, raising as before when neither
    exists; its docstring says so and the stale matching comment is rewritten (the diff: one docstring
    paragraph, the loop, two comments). Tests: three unit tests in test_spellbook.py (one parametrized), two
    integration tests in test_spell_index_meld_and_contract_lifecycle.py (one parametrized, the member order
    fixed through `SpellIndex.spells_in_index`), and the component test that asserted the old match now
    removes the active copy by its own id. The apply script rewrote the two CRLF test files with LF;
    fix_crlf_removal_tests_2026_10_16.py put CRLF back on every line in both trees, so their diffs are the 11
    and 100 lines of the change.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3344-3470
  - context_compass/artifacts/meld_contract_scan_20261015/apply_removal_src_2026_10_16.py:1-98
  - context_compass/artifacts/meld_contract_scan_20261015/apply_removal_tests_2026_10_16.py:1-291
  - context_compass/artifacts/meld_contract_scan_20261015/fix_crlf_removal_tests_2026_10_16.py:1-39
  IMPACT: Every caller - unlink, destroy, member removal, dependency fallout, version uncontract - now gets the
    copy of the version it names.
  NEXT: The system docs, the graph and the release note; then the notch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T21:48:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Green. The five red cases pass (26 targeted, GIL off and on), and the three touched files pass whole
    after the CRLF restore (193, both modes). Every suite chunk of the tree passes with the GIL off and on
    (unit_sb 2582 with the four new unit cases, int_aether 808 with the three new ones) but one test that was
    already failing and that this change does not touch: unit_top's
    `test_generated_build_assets_are_stamped_for_the_live_version`, because the generated assets still carry
    0.2.8249 while `__version__` is 0.2.8250 - rule 2's rebuild is still pending and the last rebuild fixes it.
    int_conduit's rule-2 race test is a non-strict xfail and xpassed in both modes (the known race, not this
    change). probe_index_uncontract_after_notch.py with PYTHONHASHSEED 0-9 now unlinks clean on every seed -
    no copy, active or parked, and an empty existence set; seeds 3, 4, 6, 8 and 9 raised before.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/removal_green_files.txt:1-5
  - context_compass/artifacts/meld_contract_scan_20261015/runs/removal_suites_gil0.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/removal_suites_gil1.txt:1-23
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_after_notch_seeds_fixed_gil0.txt:1-11
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_index_uncontract_after_notch_seeds_gil0.txt:1-20
  IMPACT: The change is validated; the turn-in steps follow.
  NEXT: Promote the patch docs into the system docs and regenerate their indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T22:18:36Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The removal fix's docs, release note and notch are in. The three patch docs are promoted:
    src_architecture gains the invariant "One version, one copy" and the failure mode "Fixed in 0.2.8251",
    its code map remeasures spellbook.py (7766 lines) and every numeric citation into spellbook.py below the
    method moved seven lines (the two settle-then-inherit inner citations, stale since an earlier lane, now
    point at :6971-6983 and :6984); src_components gains the Spellbook Core contract and the ConduitWard
    member loop; tests_components names the new unit, component and integration tests and adds the
    lifecycle file's code-map record; the three indexes are regenerated and check OK. The release note reads
    "# Melder 0.2.8251" with the section "Unlinking an index after a notch removes every version's copy";
    its example runs clean on the fixed src for PYTHONHASHSEED 0-9 with the GIL off and on, and fails on
    0.2.8250's src for 6 of the 10 seeds (1, 3, 4, 5, 7, 8; a first wording said five, corrected before the
    notch). `__version__` is 0.2.8251, and NOTICE M1-23 told melder_0 to notch above it and to recheck its
    held spellbook.py decisions (the file grew seven lines inside the method).
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1104-1118
  - context_compass/system_docs/src_architecture.md:2124-2135
  - context_compass/system_docs/src_architecture.md:2864-2879
  - context_compass/system_docs/src_architecture.md:4361-4367
  - context_compass/system_docs/src_components.md:348-360
  - context_compass/system_docs/src_components.md:3207-3213
  - context_compass/system_docs/src_components.md:11333-11336
  - context_compass/system_docs/tests_components.md:1178-1182
  - context_compass/system_docs/tests_components.md:1495-1497
  - context_compass/system_docs/tests_components.md:1670-1674
  - context_compass/system_docs/tests_components.md:3305-3311
  - release_docs/next_version_release.md:779-805
  - src/melder/__version__.py:12-12
  - context_compass/mailbox_board.md:912-923
  - context_compass/artifacts/meld_contract_scan_20261015/land_docs_removal_2026_10_16.py:1-244
  - context_compass/artifacts/meld_contract_scan_20261015/release_note_removal_2026_10_16.py:1-76
  - context_compass/artifacts/meld_contract_scan_20261015/release_example_removal_2026_10_16.py:1-45
  - context_compass/artifacts/meld_contract_scan_20261015/runs/release_example_removal_2026_10_16.txt:1-41
  - context_compass/artifacts/meld_contract_scan_20261015/fix_seed_wording_2026_10_16.py:1-56
  - context_compass/artifacts/meld_contract_scan_20261015/notch_0_2_8251_2026_10_16.py:1-40
  - context_compass/artifacts/meld_contract_scan_20261015/send_m1_23_2026_10_16.py:1-63
  IMPACT: 0.2.8251 is documented, noted for users and notched; the graph and the turn-in steps remain.
  NEXT: Re-extract the two changed descriptors, author and accept the Spellbook node, reassemble the graph.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T22:18:36Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The graph carries 0.2.8251. spellbook.json and __version__.json were re-extracted from the real src
    (only the two source hashes and the Spellbook node's span changed; no other descriptor touched), the
    Spellbook node gained a 24th responsibility - it removes a borrowed copy by the spell_id it is given, the
    active copy only when that copy's own spell_id is it, otherwise the parked copy, raising when it holds
    neither - and, re-read against `_remove_contracted_spell`, was accepted (graph_walker rewrote the
    descriptor at indent 2, as every accept does). Reassembled: src_graph.md is 28076 lines (sha bb75f8dc),
    its index verified; the only differences from the 17:17Z assembly are the two source hashes and the new
    responsibility line. The device VM rebooted at about 22:05Z and wiped /tmp: the scratch trees and
    baselines under /tmp/cc_res/removal are gone. Nothing in the repository was lost (the scripts and runs are
    in the artifact folder), and no scratch is left to delete.
  EVIDENCE:
  - context_compass/system_docs/src_graph.md:15736-15845
  - context_compass/system_docs/src_graph_index.md:9-18
  - context_compass/system_docs/graph/melder/aether/spellbook/spellbook.json:1-462
  - context_compass/artifacts/meld_contract_scan_20261015/graph_semantics_removal_2026_10_16.py:1-50
  - src/melder/aether/spellbook/spellbook.py:3344-3470
  IMPACT: Every system document and the graph carry the fix; what remains is the owner's direction on the open
    items, the closure, the rebuild and the release NOTICE to melder_0.
  NEXT: Ask the owner how to place the open items (the contract row's state, transfers vs contracts, the
    transfer binding-key gap, the spell_id grant check) before the closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T23:03:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner found the explanation of the four open items too superficial (chat 2026-10-16) and asked
    to talk them through with the real objects instead of examples. His own reading: (1) after a transfer the
    moved spell, what it depends on and what depends on it should be flagged for revalidation; (2) borrowers
    should be flagged the same way; (3) unclear; (4) we already settled checking active then inactive, and
    resolution happens only from active spells. Nothing is decided; no src edit before his direction.
  EVIDENCE: context_compass/artifacts/meld_contract_scan_20261015/probe_owner_objects_2026_10_16.py:1-254
  IMPACT: The closure waits for this discussion; the probe below answers each item with object dumps.
  NEXT: Walk the owner through the object dumps, item by item, and take his direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T23:03:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: probe_owner_objects (0.2.8251, a copy of src, GIL off and on alike). Lender: Bang (Mark-index) and
    English(mark: Mark) (Greeter-index); borrower: Banner with SpellContract(Greeter, "greeter"), index links
    to both. notch: the lender notches Mark to Dot, the walk marks Greeter-index by edge (impacted) and Banner by
    its contract pair ("greeter", "greeter"), and Banner melds HELLO. (rebuilt). transfer: the lender first
    moves English to a third root; the flip unregisters the lineage and registers a NEW state, so Greeter-index
    has no edges either way (Mark-index lists no dependents) and no pair (None); Banner is not flagged; the
    contract keeps its index rows and the borrower its copies (the swallowed refusal); after the same notch
    nothing is marked and Banner melds HELLO! - the old Mark. So the gap is the whole registry record, not
    the pair alone (the 'two lines' estimate was wrong). `_gate_transfer_impacts` dirties conduits through
    `mark_conduit_dirty`, a flag no meld path reads (`ConduitResolutionState.is_dirty` has no caller).
    contract: a notch changes IndexDetail.selected_spell_id and moves the Book's copies between active and
    parked; Detail rows never change, so a version grant's contract shows nothing when its version is parked.
    lookup: find_spell_by_id and get_spell_by_id answer the parked French with the active English,
    _get_owned_spell answers French; add_spell_to_contract(spell_id=French) refuses ("does not match inspected
    ID"); given the French Spell, the borrower holds a parked copy, Banner cannot resolve it (no active
    provider), and after the notch to French Banner melds BONJOUR!. Aside: `_contracted_spell_ids` lists every
    member of the index even for a one-version grant.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_notch_gil0.txt:1-37
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_transfer_gil0.txt:1-69
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_contract_gil0.txt:1-46
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_lookup_gil0.txt:1-24
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1383-1507
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:719-757
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1147-1259
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:973-1036
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1581-1603
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - src/melder/aether/spellbook/spellbook.py:3323-3341
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  IMPACT: A transfer silently disconnects the moved spell from rule 2 until it is recompiled and notched again,
    and nobody downstream of it through a contract is flagged; the fix is a transfer that keeps the record and
    flags what depends on the moved spell, which is the owner's (1) and (2).
  NEXT: Put the dumps to the owner item by item; take his direction before any src edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T13:17:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Contract rows (answers the DECISION_REQUEST of 2026-10-16T20:59:43Z). The owner (chat 2026-10-17):
    Contracts and Details do not need to know whether a version is active or inactive - that is the
    Spellbook's responsibility; a contract is about lending a spell, not observing it; what matters is that
    active/inactive checks and ownership transfer are handled properly. No state field is added to Detail or
    IndexDetail; the borrower Book's active and parked maps stay the only record of a copy's state, and every
    lookup of a borrowed or owned version checks both (as the 0.2.8251 removal does).
  EVIDENCE: src/melder/aether/conduit/conduit_ward/contract/details.py:14-404
  IMPACT: Item 3 is closed with no change.
  NEXT: None for this item.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T13:17:34Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: ALIGNMENT_CHECK
  CLAIM: The owner's notification model (chat 2026-10-17, his words: SpellSystemStates has nothing to do with
    contracts; when a notch happens the spell, its dependencies and its upstream reliances must be notified as
    dirty; a contract change distributes the notification into the impacted spells, which then run their
    resolution, and that updates SpellSystemStates; marking through SpellSystemStates blends responsibility).
    Where the code routes contract notification through SpellSystemStates today: (a) every borrower Book
    finds the spells that use a changed copy through the per-Book index `_contract_dependents_by_spellbook`,
    there since at least 2026-05-19 (0d0f1bc94); (b) rule 2's D2 walk (`mark_dependents_for_revalidation`,
    called by `_apply_notch`) crosses into other Books through the pair map `_binding_key_by_index` that
    0.2.8250 added (192482b4c), and it marks every Book's users of the pair, even Books that do not borrow
    the spell. The notch's own fan-out to borrowers already runs through the contracts (the conduit's links).
    Open with the owner: what 'its dependencies' covers; whether (b), and (a), are reworked so the contract
    side routes the notification; the borrowers after a transfer; the grant's exact lookup.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:973-1036
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1697-1788
  - src/melder/aether/spellbook/spellbook.py:3906-4061
  - src/melder/aether/spellbook/spellbook.py:5089-5143
  - src/melder/aether/conduit/conduit.py:5622-5759
  - src/melder/aether/conduit/conduit.py:6236-6310
  IMPACT: The transfer fix follows his model (notify the impacted spells through the contracts; no registry
    record kept by the transfer), and it may reshape rule 2's landed D2 walk, which is his call.
  NEXT: Confirm the reading with the owner and take his direction on the open points before any src edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T18:04:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: What `get_spell_by_id` looks up (the chain read whole on 0.2.8251, answering the owner's questions of
    2026-10-17: "is it searching spell_ids or index_ids?" and "that might be get_spell_from_index_by_id"). Every
    search key is the spell_id; the index's own id (the ULID `SpellIndex._id`) is never searched. Aether asks the
    frame: `find_conduit_id_for_spell` walks `_spell_registry` (conduit id -> its SpellIndex objects) and asks each
    `SpellIndex.has_spell(spell_id)`, membership in `_spells_in_index`, the set of member spell ids, parked ones
    included. The owner Book's `find_spell_by_id` then reads `_spells_by_id[spell_id]` (active versions), else
    `_inactive_spells[spell_id]` (parked), takes that Spell's `spell_index` and returns `_spells[spell_index]`, the
    index's active Spell - the read `Conduit.get_spell_by_index_id` ends with (`Spellbook.get_spell_by_index_id`
    finds the index whose `id` is the given ULID, then `_find_spell` reads `_spells`). So for an active spell_id it
    returns that spell; for a parked one, the active spell of its index: get_spell_by_id(French) is English (trace,
    GIL off and on). The owner's reading holds - it behaves as "the spell of the index that holds this spell_id" -
    and the name does not say so ("the name sucks"). For scoping only (a search, not read): 9 call sites of
    `get_spell_by_id` in src (conduit.py 1, conduit_ward.py 4, transfer_of_ownership.py 4) and one error message,
    7 of `find_spell_by_id` besides the chain itself, 84 test files naming either.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3193-3233
  - src/melder/aether/spellbook/spellbook.py:2894-2927
  - src/melder/aether/spellbook/spellbook.py:2694-2726
  - src/melder/aether/aether.py:2505-2544
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1288-1307
  - src/melder/aether/spellbook/bind/spell_index.py:106-113
  - src/melder/aether/spellbook/bind/spell_index.py:288-321
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - src/melder/aether/conduit/conduit.py:3235-3277
  - src/melder/aether/spellbook/spellbook.py:2268-2305
  - src/melder/aether/spellbook/spellbook.py:2181-2197
  - src/melder/aether/spellbook/spellbook.py:2221-2242
  - context_compass/artifacts/meld_contract_scan_20261015/probe_owner_objects_2026_10_16.py:248-286
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_trace_gil0.txt:1-18
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_trace_gil1.txt:1-18
  IMPACT: The grant's refusal of a parked spell_id is this lookup doing what it was built for; changing its name or
    what it returns is a public-API decision (both Conduit lookups are Public API). The probe gained a trace mode
    (one docstring line, `mode_trace`, its dispatch), so the 23:03:24Z note's range 1-254 now ends inside it.
  NEXT: Put the choice below to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-17T18:04:14Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner decides what `get_spell_by_id` / `find_spell_by_id` become. A: return the spell with exactly that
    spell_id, active or parked - what the name says, and what `_get_owned_spell` already reads in one Book - while
    a caller that wants the index's active spell asks the index (`get_spell_by_index_id`); B: keep the behaviour and
    rename it to say it returns the active spell of the spell_id's index; C: keep both and change only the grant and
    ungrant check (`ConduitWard._check_spell_id_and_spell`) to look up the exact spell. A and B change public API, so
    every caller is read first to see which answer it needs; C touches one method. No src edit before his answer.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - src/melder/aether/spellbook/spellbook.py:3323-3341
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  IMPACT: His answer fixes item 4 (the spell_id grant) and whether it grows into a lookup change of its own.
  NEXT: Wait for the owner's choice; the other open items (transfers, the notification route) stay as recorded.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T19:15:03Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Why the lookup answers English for French (the owner asked, chat 2026-10-17). The grant's check runs in the
    borrower's ConduitWard (`Conduit.add_spell_to_contract` -> `ConduitWard._add_spell_to_contract` ->
    `_check_spell_id_and_spell`), which calls `get_spell_by_id` on the borrower Conduit; that reaches the lender's
    Spellbook as `find_spell_by_id(French)`, which finds the French Spell in `_inactive_spells` and then returns
    `_spells[French's index]` - the index's active spell, English - because the method is built to resolve any id of
    a lineage to the version live now (its docstring's purpose). It always did: at 0.2.8228 (git 3d184cac6) it walked
    `_spells` (index -> active spell) and returned the active spell of the first index whose `has_spell` held the
    id; 0.2.8229 kept that answer and changed only how it is read. The grant needs the exact version, so the check
    uses a lookup built for another question.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:6806-6890
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1472-1568
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_owner_objects_lookup_gil0.txt:1-24
  IMPACT: The fix belongs in the check (C), not in `find_spell_by_id`, unless the owner wants the lookup changed.
  NEXT: The owner's answer on the check fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T19:18:26Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Proof test, at the owner's request (chat 2026-10-17: "can you prove it in a test?"), kept in the lane's
    artifact folder, not in tests/: six tests on a copy of 0.2.8251's src, 6 passed with the GIL off and on. With
    English bound active and French staged by `bind_inactive` on the same index: the ids differ and the Book holds a
    French Spell parked under French's id; `get_spell_by_id(French's id)` on the lender and the borrower and
    `find_spell_by_id(French's id)` each return the English Spell object (`.spell is English`, English's id);
    `find_spell_by_id` finds French in `_inactive_spells` and returns `_spells[its index]`;
    `add_spell_to_contract(spell_id=French's id)` raises "Provided spell_id '<French>' does not match inspected ID
    '<English>'."; given the French Spell object it returns True; after a notch to French, English's id returns the
    French Spell. A value printout of the same world shows each answer's class and id.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/proof_tests/test_parked_spell_id_lookup_proof.py:1-141
  - context_compass/artifacts/meld_contract_scan_20261015/runs/proof_parked_spell_id_lookup_gil0.txt:1-14
  - context_compass/artifacts/meld_contract_scan_20261015/runs/proof_parked_spell_id_lookup_gil1.txt:1-14
  - context_compass/artifacts/meld_contract_scan_20261015/runs/proof_parked_spell_id_lookup_values_gil0.txt:1-11
  IMPACT: The lookup's answer for a parked spell_id is proven on the running code, not only read.
  NEXT: The owner's answer on fixing the grant check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T19:41:06Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-17, after the proof test), superseding the A/B/C request of 18:04:14Z:
    a lookup by spell_id returns the spell that owns that spell_id - active or parked - or nothing / not found
    (find_* returns None, get_* raises, the 2026-10-11 rule). It never answers with the spell_index's active spell:
    the index's active spell and a spell_id's own spell are separate things, and a lookup that swaps one for the
    other is no longer looking up a spell_id - it returns made-up data. The swap is a broken contract, not an
    intended lineage answer. Fix it where it is written, and find every other place the same swap is written:
    report the origins (code that itself turns a spell_id into its index and hands back that index's active
    spell or copy), not methods that only call a broken lookup.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - context_compass/artifacts/meld_contract_scan_20261015/proof_tests/test_parked_spell_id_lookup_proof.py:1-141
  IMPACT: Option A of 18:04:14Z, applied to every origin. `Spellbook.find_spell_by_id` and
    `Conduit.get_spell_by_id` change for a parked spell_id (Breaking, public); every caller that relied on the swap
    is read before the fix; the patch gate applies before any src edit. The 19:15:03Z note's IMPACT line ("the fix
    belongs in the check (C)") is overruled.
  NEXT: Read-only sweep for the origins of the swap, each method read whole; report them to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T19:49:27Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The origins of the spell_id -> index -> active-spell swap, each read whole on 0.2.8251 (the code that
    itself turns a spell_id into its index and answers with that index's active spell or copy):
    (1) `Spellbook.find_spell_by_id` finds the parked Spell under the id (`_inactive_spells`), then returns
    `_spells[its index]`; (2) `Spellbook._find_contracted_spell_by_id` finds the parked borrowed copy, then returns
    `spell_map[its index]`, and for an id the Book holds no copy of walks the contracted map and returns the active
    copy of any index listing the id; (3) the contract row `Detail` (one granted version) states "where they
    disagree, the index resolves the current head", and `Detail.has_spell` answers by index membership, so the row
    for one version says yes for every member; (4) `ConduitWard._get_spell_in_contracts` takes the row granted for
    the id and returns `_find_contracted_spell(row.spell_index)`, and walks rows by index membership; (5)
    `ConduitWard._get_all_spells_in_contracts` resolves each granted row by its index and reports the active copy
    under that copy's own id; (6) `ConduitWard._validate_contracts_and_define` checks each row by its index's active
    copy and falls back to (2). On purpose and named for it: `Meld._current_in_pool` (0.2.8250) returns the active
    Spell of the lineage a recorded version id belongs to - the catch-up's lineage question, asked with a spell_id
    as the handle. Same mix-up in the other direction, not lookups: `_add_contracted_spell`,
    `_clear_contracted_spells_for_conduit` and `_destroy_detached_link_contract` file or drop a borrowed copy under
    `spell.spell_index.selected_spell_id` instead of `spell.spell_id`; they only see active copies, so the ids
    match, except possibly between a lender's notch and its fan-out (UNKNOWN, untested). Every other method named
    earlier only calls one of the six (the `get_spell_by_id` chain, `get_spell_permissions`,
    `find_contracted_spell`, `_get_spells_in_contract_by_conduit`, `_check_spell_id_and_spell`, the transfer and
    dependency-walk resolutions, `CommandSystem.get_spell_by_id`, the Rift `get_spell_in_contracts` commands, the
    public Conduit contract listings). Exact lookups of the right shape exist: `_get_owned_spell` (active, then
    parked) and `Meld._resolve_spell_by_id`. The graft runner already hit the swap (TRIAGE 2026-07-12: adoption
    self-notched) and was routed around it through `_get_owned_spell`. History (git -S): the contract-side swaps
    come from b5d4ce835 (2025-11-18); the find_spell_by_id swap predates 0.2.8229, where melder_1 kept it and
    documented it as the contract; melder_1 added the parked-copy swap to (2) in 0.2.8231.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - src/melder/aether/spellbook/spellbook.py:3036-3088
  - src/melder/aether/conduit/conduit_ward/contract/details.py:1-211
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3571-3644
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3463-3567
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3881-3939
  - src/melder/aether/conduit/meld/meld.py:1555-1584
  - src/melder/aether/spellbook/spellbook.py:3178-3247
  - src/melder/aether/spellbook/spellbook.py:3473-3545
  - src/melder/aether/spellbook/spellbook.py:3693-3744
  - src/melder/aether/spellbook/spellbook.py:3323-3342
  - src/melder/aether/conduit/meld/meld.py:2151-2186
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:491-579
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:3648-3703
  - src/melder/aether/conduit/conduit.py:3280-3333
  - src/melder/aether/conduit/conduit.py:4177-4219
  IMPACT: The fix is these six; the callers that rely on the swap today (a transfer or a dependency grant given a
    parked spell_id, the contract listing's contents) need the owner's word before the code changes.
  NEXT: Report the origins to the owner, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:00:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's rule (chat 2026-10-17): two separate things, never blended. Sharing a SpellIndex
    (`add_index_to_contract`, the `IndexDetail` row keyed by the index) follows whichever spell the index has
    active; sharing a spell by id (`add_spell_to_contract(spell_id=...)`, the `Detail` row keyed by that spell_id)
    is exactly that spell. Likewise a lookup by spell id (the SHA bind / bind_inactive return;
    `find_spell_by_id`, `get_spell_by_id`) returns that spell or nothing, and only a lookup by index id (the
    index's ULID; `get_spell_by_index_id`) returns the index's active spell.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3193-3277
  - src/melder/aether/conduit/conduit.py:6806-6921
  - src/melder/aether/spellbook/bind/spell_index.py:104-113
  - src/melder/aether/conduit/conduit_ward/contract/details.py:1-211
  IMPACT: Origins 3-6 (19:49:27Z) are this blend on the contract side: the spell-by-id row (`Detail`) is resolved
    through its index as if it were an index share. The fix resolves a `Detail` by its spell_id and keeps index
    resolution for `IndexDetail` only.
  NEXT: The owner's go-ahead on the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:22:39Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The owner's direction (chat 2026-10-17): fix origin 1 only - rename `Spellbook.find_spell_by_id` to
    `find_spell_by_spell_id`, make it return the spell that owns the spell_id (active, else parked, else None), say
    so in the docstrings, update what depends on it; origins 2-6 wait. Patch docs written and linked (patch id
    find_spell_by_spell_id_2026_10_17; read order architecture, then the five component patches). Mapping, patch
    section -> implementation -> validation: I1 (spellbook lookup) -> the method's body and docstring,
    `_get_spell_by_id_via_aether` -> the method's component tests, reworked for the exact answer and renamed with
    it; I2 (Conduit lookups) -> `get_spell_by_id` and `get_spell_permissions` docstrings -> integration: lender and
    borrower lookups of the parked spell_id, permissions per version, unknown id ValueError; I3 (explicit index
    step) -> `Conduit._resolve_transfer_spell`, `ConduitWard._transfer_spell_ownership`, the two ward dependency
    walks, `TransferOfOwnership._resolve_spell`, `_deps_resolvable_on_target`, `_transfer_owned_dependencies` ->
    guards green on 0.2.8251 and after: a transfer by the parked spell_id, a dependency grant and a transfer with
    include_dependencies after the dependency's notch; ward grant check (no code change) -> grant and ungrant by the
    parked spell_id; renamed call sites -> the restore, graft, Rift command and ambiguity suites; I4 locks -> each
    explicit step takes one Book lock with no other lock held (read at each call site), suites GIL off and on;
    I5 -> no emitted code or cache reads the name (search of src). Tests' renamed calls by a recorded script.
  EVIDENCE:
  - context_compass/system_docs/patches/active/find_spell_by_spell_id_2026_10_17/architecture_patch.md:1-73
  - src/melder/aether/spellbook/spellbook.py:2052-2131
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2902-2988
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:528-554
  IMPACT: The order keeps the tree from handing a parked Spell to a transfer or a dependency grant at any point.
  NEXT: Red tests on a scratch copy of 0.2.8251.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T20:37:49Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Mailbox, consumed at re-onboarding. M0-180 (melder_0, QUESTION, 19:50:33Z): the owner told melder_0 to turn
    in his wording ticket now; its free part is in the owner's commits 192482b4c and 5ac69ab51 with no notch of its
    own. melder_1 grants melder_0 one write of `src/melder/__version__.py` (one notch above what it reads), one bullet
    in the release note's "Packaging and documentation" section and the rebuild, ahead of this lane; melder_1 writes
    neither file until melder_0's NOTICE says it is done, and fix #1 takes the number next at its landing (the
    contribution guide: a notch is read at landing, never reserved). The rest of the M1-22 hold stands. M0-181
    (NOTICE, FYI, 20:29:21Z): melder_0's read-only correctness sweep filed three stories whose fixes sit in files
    this lane holds - STORY-2026-10-17-staged_version_releases_active_signature and
    STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (spellbook.py), and
    STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (conduit.py, contract side; melder_0 suggests folding it
    into this lane's rework). Noted there, not filed: after conjure a direct `Spellbook.bind_inactive` or
    `cleanup_spell` skips the borrower emissions the Conduit facades send.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_spell_id_wording_near_spell_index_task.md:1-440
  - context_compass/tickets/epics/2026-10-17_correctness_defects_epic.md:1-462
  - context_compass/tickets/stories/2026-10-17_staged_version_releases_active_signature_story.md:1-211
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:1-193
  - context_compass/tickets/stories/2026-10-17_parked_cleanup_leaves_borrower_copies_story.md:1-184
  IMPACT: `__version__.py` and the release note may change under this lane before fix #1 lands: both are re-read
    right before fix #1's notch and release-note edits. The three stories are outside fix #1 (owner: fix #1 only);
    the conduit.py one goes to the owner with the other mismatches after fix #1.
  NEXT: ACK to melder_0 (M1-24), then the board row, then fix #1's apply script on the scratch work tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T20:38:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Mailbox M0-182 (melder_0, NOTICE, 20:37:09Z), copied before consumption: the index
    `remove_from_spell_index` mints is never registered in the frame's spell registry (`_apply_remove_from_index`
    makes no `_register_single_spell_index` call), so `find_conduit_id_for_spell` misses a version there, parked or
    notched active, and `Conduit.get_spell_by_id` / `get_conduit_by_spell_id` raise "not found in any conduit"
    before the Book is asked. Filed by melder_0 as STORY-2026-10-17-minted_index_missing_from_frame_registry
    (probe M1-M3 in artifacts/correctness_defects_20261017/); its scope leaves what the Book answers to this
    lane's fix #1. Fix #1 changes the Book step only, so that lookup still raises for such a version after fix #1:
    a frame-registry defect, outside fix #1 (owner: fix #1 only), told to the owner with fix #1's report.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md:1-185
  IMPACT: Fix #1's tests stay on the bound index (no index move), where the frame step finds the version; the
    patch docs' non-goals name the minted-index case as pre-existing.
  NEXT: Delete M0-180..M0-182, clear their alerts, ACK M0-180 (M1-24), then the board row.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T20:53:48Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's answer to the open rename question (chat 2026-10-17: "yeah use get_spell_by_spell_id"):
    `Conduit.get_spell_by_id` becomes `Conduit.get_spell_by_spell_id`, folded into fix #1, with no alias for the
    old name (the no-fallback rule, as for `find_spell_by_spell_id`). Scope it adds: the src callers
    (`ConduitWard._check_spell_id_and_spell`, the two dependency walks, `_transfer_spell_ownership`;
    `TransferOfOwnership._resolve_spell`, `_deps_resolvable_on_target`, `_transfer_owned_dependencies`,
    `_dirty_dependencies`; `Conduit._resolve_transfer_spell` and the notch target's error message), the docstrings
    that name it, 29 test files, agents/MELDER_AGENT_OPERATIONS.md:454, the system docs and the release note
    (Breaking). Asked, not decided: whether the Rift room command of the same name (`CommandSystem.get_spell_by_id`,
    `StaticCommandSystem.get_spell_by_id`, its ACL action name) is renamed too; it is left as it is until he says.
    The internal `Spellbook._get_spell_by_id_via_aether` keeps its name (not asked).
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:3193-3233
  - src/melder/nexus/rift/command_system/command_system.py:835-891
  - src/melder/nexus/rift/command_system/static_command_system.py:511-547
  IMPACT: Breaking for every caller of `Conduit.get_spell_by_id`; the patch docs' non-goal "no rename of
    `Conduit.get_spell_by_id`" is replaced by the rename before the apply script runs.
  NEXT: Update the patch docs, then the apply script with both renames.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:15:54Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Mailbox M0-183 (melder_0, NOTICE, 2026-10-17T21:00:59Z, re M1-24), copied before consumption: melder_0
    notched 0.2.8252 ("version id" named as the spell_id in the docstrings and comments of 113 files nobody held;
    IdentityMixingStrategy's diagnostic), added one bullet before the rebuild line of the release note's "Packaging
    and documentation" section and rebuilt (both checks OK). `src/melder/__version__.py` and
    `release_docs/next_version_release.md` are this lane's to write again, and fix #1 notches above 0.2.8252. The
    rewording of the files this lane holds waits in TASK-2026-10-17-spell_id_wording_in_held_files (backlog) for this
    lane's release NOTICE.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/tasks/completed/2026-10-16_spell_id_wording_near_spell_index_task.md:1-484
  - context_compass/tickets/tasks/backlog/2026-10-17_spell_id_wording_in_held_files_task.md
  IMPACT: Fix #1's notch is read at its landing (0.2.8253 unless another lane notches first); its release-note
    section is added after re-reading the note; the closing NOTICE releases the held files to melder_0's task.
  NEXT: Delete M0-183 and clear its alert; then record the owner's "update it all" decision.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-17T21:24:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-17: "dude update it all bro if its there and misunderstood then update
    it"), with melder_1's reading sent back to him: the Rift room command is renamed too -
    `CommandSystem.get_spell_by_id` and `StaticCommandSystem.get_spell_by_id` become `get_spell_by_spell_id`, with
    the action name the command gate and memory record and the advertised command list - and wherever one of these
    lookups swaps a spell_id for its index's spell, it returns exactly that spell. Origins 2-6 (19:49:27Z) still
    wait for him. The internal `Spellbook._get_spell_by_id_via_aether` keeps its name (not asked).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/command_system.py:404-435
  - src/melder/nexus/rift/command_system/command_system.py:835-891
  - src/melder/nexus/rift/command_system/static_command_system.py:511-547
  IMPACT: Breaking for every caller of the room command's old name; the non-goal "the Rift room command keeps its
    name" in the patch docs is replaced, and a component patch for the Rift command lookups is added before any
    Rift edit.
  NEXT: Record the Rift swaps found, then update the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:24:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The Rift room lookups, read whole on today's tree (src unchanged since 0.2.8251 but for melder_0's notch and
    rebuild): (a) `CommandSystem.get_spell_by_source_id` takes the published record the source id names, then
    resolves its index (`_get_spell_by_index_id_locked(record.spell_index_id)` ->
    `owner_conduit.get_spell_by_index_id`) and returns the spell the index has active - for a projection that still
    lists a version a notch has parked (projections refresh explicitly), the version now active instead of the one
    named; (b) `StaticCommandSystem.get_spell_by_source_id` and (c) `StaticCommandSystem.get_spell_by_id` turn the
    record or the spell_id into its index and return the live object of whichever published record of that index
    melds first (`owner.meld_existing_spell(spell=record.spell_id)` over every record of the index), not the one
    named; (d) `CommandSystem.get_spell_by_id` answers through the owner Book's `find_spell_by_id` and is exact once
    the Book lookup is. Exact already: `CommandSystem.get_spell_permissions` (delegates to the Conduit),
    `StaticCommandSystem.describe_spell_status_by_id` and `_by_source_id` (records with that spell_id). Outside
    src: ten UX examples and `docs/expert/bind-hooks.md:49` call the old names, and two expert examples teach and
    assert the old answer - expert 17 ("Every public spell_id->object lookup ... resolves any lineage spell_id to
    ... the currently ACTIVE member"; `resolved_from_parked_id.spell_id == v1_id`) and expert 26
    (`conduit.get_spell_by_id(staged).spell_id == v1`); `UX_and_AIX_experiences/pytest_examples` runs every example.
    `04_expert/_concept_map.txt:794` is a dated retraction record (history; left as written).
  EVIDENCE:
  - src/melder/nexus/rift/command_system/command_system.py:292-364
  - src/melder/nexus/rift/command_system/command_system.py:758-798
  - src/melder/nexus/rift/command_system/command_system.py:835-891
  - src/melder/nexus/rift/command_system/static_command_system.py:160-253
  - src/melder/nexus/rift/command_system/static_command_system.py:255-291
  - src/melder/nexus/rift/command_system/static_command_system.py:358-415
  - src/melder/nexus/rift/command_system/static_command_system.py:511-547
  - UX_and_AIX_experiences/04_expert/17_notch_swapping_a_live_object.py:1-171
  - UX_and_AIX_experiences/04_expert/26_codegen_create_modify_iterate.py:170-240
  IMPACT: (a)-(c) are made exact in this change (owner: "update it all"); (d) follows the Book. The two examples are
    corrected to the exact answer with their renamed calls, the smallest edit that keeps them true and green; the
    exact before/after goes to the owner in the report.
  NEXT: Update the patch docs, then write edits_rift.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-17T21:36:47Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Correction to (a) of the 21:24:30Z FACT: a capability room's projection is not a stale snapshot after a
    notch. Probe on the 0.2.8251 tree (GIL off): with PricingV1 active and PricingV2 parked, the room's published
    records list PricingV1 only; right after `notch_spell` to PricingV2, with no refresh, they list PricingV2 only
    (the notch swaps the record in the live descriptor the projection reads); the room answers PricingV2 by its
    spell_id, its source id and its index, and refuses PricingV1's spell_id and source id ("was not found in
    frame"). Nexus publishes the version an index has active, so through the rooms the index-path answers of (a)-(c)
    agree with the version named in a settled frame; the change still routes each lookup by spell_id or source id
    to the version named (owner: "update it all"), and the parenthetical about stale projections is withdrawn from
    the patch docs, the new docstrings and the tests.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/spell_id_lookup/probes/probe_rift_projection_after_notch.py:1-63
  - context_compass/artifacts/meld_contract_scan_20261015/spell_id_lookup/runs/probe_rift_projection_after_notch_base_gil0.txt:1-9
  IMPACT: The Rift integration test checks the real publication - active answered three ways, parked refused - and
    the unit tests with doubles pin the exactness (a record naming a version other than the index's active one).
  NEXT: Re-create the work tree, apply the src edits with the Rift edits, run the test codemod and install the new
    tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Current state (2026-10-17T20:39:13Z): this ticket has landed two source changes; fix #1 of the spell_id lookups is in progress.
- 0.2.8250, rule 2 with D1-D5 (owner-accepted, Notes 18:23Z; in the owner's commit 192482b4c): a satisfied
  SpellContract is not checked on every meld; a change of what a spell resolves marks it for revalidation (the
  borrower Book's five contracted-map mutators; a notch's downstream walk, D2); the meld refreshes stale
  dependencies before a plan compiles; a lost provider is named with its remedy (D1-B); a notch back makes a
  parked version grant active again (D3). Release-note section "A satisfied `SpellContract` is not checked on
  every meld; a notch reaches every spell that depends on the notched one".
- 0.2.8251, the removal fix (owner-approved, Notes 21:22Z): `Spellbook._remove_contracted_spell` removes
  exactly the copy of the spell_id it is given, so an index unlink after a notch completes in any member order.
  Release-note section "Unlinking an index after a notch removes every version's copy".
Both carry tests (green with the GIL off and on), system docs with their indexes, the graph and the release note.
Patch docs: system_docs/patches/completed/contract_recheck_on_notch_2026_10_16/ (archived) and
system_docs/patches/active/contracted_copy_removal_by_version_2026_10_16/ (promoted; archive at closure).
Open, the owner's: whether a contract's per-version row carries active/inactive state (Notes 20:59Z); what
borrowers get after an ownership transfer - index links and the repoint option are refused silently (18:23Z);
rule 2's binding-key gap on the transfer flip (18:23Z; fix: pass binding_key=spell_obj._key in its
register_index and rollback); the spell_id lookups - the owner's rule (2026-10-17, Notes 19:41Z, 20:00Z): a
spell_id lookup returns that spell or nothing, never the index's active spell; the six origins are found (Notes
19:49Z). IN PROGRESS, fix #1 only (owner's go-ahead, PLAN 20:22Z): `find_spell_by_id` renamed
`find_spell_by_spell_id` and exact, its transfer and dependency callers given an explicit index step; patch docs
system_docs/patches/active/find_spell_by_spell_id_2026_10_17/; red tests in place. Origins 2-6 and the three
decisions (a transfer given a parked spell_id, the dependency grant walk, parked grants in the contract listing)
wait for the owner after fix #1; it ends the parked spell_id grant refusal (21:36Z). Mailbox (Notes 20:37Z,
20:38Z): melder_0 notches first (M1-24 grants it); his three stories in held files and the minted-index registry
go to the owner with fix #1's report. Decided: contract rows carry no active/inactive state (2026-10-17). Filed: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout (its race
test is xfail) and TASK-2026-10-16-investigate_lent_consumer_provider_loss.
Next: (1) fix #1 - the apply script on the scratch work tree, red -> green with the GIL off and on, the suites,
then the repo, docs, release note and its notch (after melder_0's, M1-24); (2) the owner's direction on the open
items; (3) the closure - summary naming 0.2.8250, 0.2.8251 and fix #1's notch and their release-note sections, the
patch docs archived, board and artifact sync; (4) the rebuild last, both checks OK; (5) a NOTICE releasing the files
melder_0 waits for (Notes 18:46Z).
Evidence: the Notes from 09:57:21Z on; artifacts/meld_contract_scan_20261015/.

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
