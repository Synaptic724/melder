# Task: Stop a live unlink from surfacing an internal phase failure in a borrower's meld

## Metadata
- Task ID: TASK-2026-10-04-fix_live_unlink_churn_phase_error
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-04T23:11:22Z
- Updated: 2026-10-04T23:59:15Z

## Objective
The hosted macOS 3.14.8 runtime job failed test_multithreading_live_link_unlink_and_contract_churn_cycles: during a
live mutation window a borrower's meld raised PhaseExecutionError ("Phase 'injection_plan_local' encountered 1
error(s) ... RuntimeError: Occurrence spell could not be resolved from the spell lookup."), which the test treats as
an internal phase failure. Find the root cause in source, fix it so churn windows only raise the allowed errors (or
correct the test if the test is what drifted), and guard it with a regression test.

## Ticket Contract
- ENTRY_GATE: The owner's chat directive of 2026-10-04 ("we gotta fix this and repush ... fix that shit") with the
  pasted failure (1 failed, 13276 passed; macOS, CPython 3.14.8). Active board row: live_unlink_churn_phase_error.
- EXECUTION_BOUNDARY: investigation reads the failing test file and the resolution path that raises the error
  (spell_occurrence_contract_processor_strategy.py, its phase 9 callers, Meld's deferred and rebuild lanes,
  ConduitWard sever/link). Implementation starts only after the owner confirms the proposed fix. A src change here
  is concurrency-sensitive and system-impacting: patch docs under system_docs/patches/active/<id>/ first, then the
  notch, the release-note entry, system docs, and the rebuild last. No commit, push or PR.
- DEPENDENCIES: none. Shares the final assets and llm_support rebuild with ci_python_check_latest.
- EXIT_GATE: root cause evidenced from source; the owner confirms the fix; the churn test and a targeted regression
  pass repeatedly on the device VM (or Not run with the reason); touched tiers pass; asset, graph and bundle checks
  print OK; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when the fix needs a src or public-API change; BLOCKER when the race can be
  neither reproduced nor settled from source.

## Scope Boundaries
- In scope: why a live unlink, relink, uncontract or recontract lets a borrower's meld fail inside the phase
  pipeline; the smallest correct fix; a regression test.
- Out of scope: the CI workflow changes (ci_python_check_latest lane); the two XPASS Fault B tests; unrelated
  refactors.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T23:59:15Z) fixed, regression-tested red/green, documented, notched 0.2.8227 and
  tier-tested (Notes 7-11); the owner's push and acceptance remain.
- previous: draft -> in_progress: (2026-10-04T23:11:22Z) the owner's directive with failure evidence; ticket and board
  row exist before the investigation starts.

## Steps / Checklist
- [x] Read the churn harness and its allowed-error contract in the failing test.
- [x] Read the code that raises "Occurrence spell could not be resolved from the spell lookup." and trace
      its callers.
- [x] Reproduce on the device VM (forced interleaving probe, Note 4).
- [x] Classify (src: two miss sites the pass cannot classify) and settle the fix (owner pre-approved).
- [x] Patch docs, implement, regression tests (docs, notch and release note below).
- [x] Validate (Note 11); assets and llm_support rebuild is the session's last write.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root-cause note with source evidence; an owner-approved fix; a regression test; the validation record.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py
- src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py
- src/melder/__version__.py (0.2.8227)
- tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py (new)
- tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py
- tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py
- release_docs/next_version_release.md
- context_compass/system_docs/src_architecture.md, src_components.md, tests_components.md and their indexes
- context_compass/system_docs/graph/ (two processor descriptors), src_graph.md and src_graph_index.md
- context_compass/system_docs/patches/active/live_unlink_visibility_race_2026_10_04/ (three patch docs)
- generated assets and llm_support bundles (rebuilt last)

## Validation
- Device VM, CPython 3.14.7t: see Notes 9 and 11 (regression red/green, 133 targeted, unit/component/
  integration shards, docs). Not run: tests/integration/melder/crystallizer; the hosted workflows (owner).

## Risks / Rollback Notes
- Risk: the race may only show under hosted timing. Mitigation: settle it from source and force the interleaving
  in a targeted test where possible.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/live_unlink_visibility_race_2026_10_04/architecture_patch.md
  - system_docs/patches/active/live_unlink_visibility_race_2026_10_04/component_patch_target_resolution_pass.md
  - system_docs/patches/active/live_unlink_visibility_race_2026_10_04/code_description_patch_target_pass_visibility.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: on acceptance, promote into src_architecture and src_components and archive the folder
  under system_docs/patches/completed/.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-04T23:11:22Z
  TYPE: PLAN
  CLAIM: The error text is raised in the phase 9 occurrence-contract processor strategy. Read the test's churn
    harness and allowed-error rule first, then that strategy and the callers that run it during a meld, then try a
    repeated run on the device VM. The failure arrived after stable_0 printed, so it hit a mutation step, where
    borrower A expects success or an allowed error.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:206-206
  IMPACT: Fixes the reading order; no claim about the cause is made yet (UNKNOWN).
  NEXT: Read the churn harness and _assert_allowed_live_mutation_error in the failing test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-04T23:15:08Z
  TYPE: FACT
  CLAIM: The failing step is during_unlink_a: the mutator calls owner.sever_link(borrower_a) while borrower A's
    worker melds its SpellContract consumer, and the test allows success or RuntimeError/MeldExecutionError/
    SpellbookValidationError there but rejects PhaseExecutionError. The phase 9 contract processor looks every
    occurrence spell up in the LIVE spellbook._spell_id_pool and raises RuntimeError on a miss; the sever pops
    the peer's borrowed spells from that pool (Phase 3 destroy, under the Spellbook lock) with nothing that
    excludes an in-flight resolution pass, and only afterwards invalidates the contract consumers. So a pass
    whose earlier phases saw the provider can miss it in phase 9, and the scheduler reports the miss as an
    internal PhaseExecutionError.
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py:309-330
  - tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py:998-1035
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:54-102
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:180-208
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1078-1233
  - src/melder/aether/spellbook/spellbook.py:3492-3537
  IMPACT: The phase 9 miss is reachable whenever the pool loses a spell between the pass's phases; which
    interleaving the hosted run hit (stale structural DAG vs a mid-pass pop) is still UNKNOWN.
  NEXT: Read _invalidate_contract_consumers and the meld-time resolution lane, then try a repeated run here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:24:47Z
  TYPE: FACT
  CLAIM: Every meld of a SpellContract consumer forces its resolution verdict to gated and reruns the target
    pass (5-11) under its rebuild window and spell lock, without the Spellbook lock. The target passes already
    turn a plan-phase PhaseExecutionError into a visibility failure (invalid verdicts plus
    visibility_gap_dependency_filtered diagnostics, so the meld raises SpellbookValidationError) - but only for
    KeyError entries. The analyzer and the instance processor miss with KeyError (subscript); the phase 9 contract
    and runtime processors miss with RuntimeError, so their misses escape as PhaseExecutionError.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:893-949
  - src/melder/aether/conduit/meld/meld.py:1208-1269
  - src/melder/aether/conduit/meld/meld.py:1271-1340
  - src/melder/aether/spellbook/spellbook_creation_system.py:1683-1794
  - src/melder/aether/spellbook/spellbook_creation_system.py:1797-1865
  - src/melder/aether/spellbook/spellbook_creation_system.py:2538-2619
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:39-103
  IMPACT: The design already has the right outcome for this race (a validation failure the next meld recovers
    from); two strategies just report the miss with a type the pass cannot classify.
  NEXT: Reproduce deterministically by severing at fixed points inside the pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:24:47Z
  TYPE: MEASURE
  CLAIM: Device VM, uv CPython 3.14.7t: a probe (owner + borrower, dynamic, the test's SpellContract consumer)
    severs the link in a helper thread at a fixed point of the borrower's meld-time pass and joins it. Before the
    phase 9 contract processor: PhaseExecutionError('injection_plan_local' ... RuntimeError: Occurrence spell could
    not be resolved from the spell lookup.) - the hosted failure, reproduced every run. Before the phase 9 runtime
    processor: the same with 'SpellRuntimeProcessorStrategy could not resolve spell_id'. Before phase 9 as a
    whole: SpellbookValidationError (the instance processor's KeyError is converted). Before phases 5, 6, 7 or 8:
    success with the SpellContract placeholder. Before phases 10 or 11: RuntimeError from hydration at context
    build ('many_only manifest references unknown spell_id'), outside the scheduler. The next meld after every
    case raised SpellbookValidationError.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:294-591
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:321-343
  IMPACT: Exactly two windows produce the internal PhaseExecutionError, both the RuntimeError miss sites; every
    other window already ends in an error or result the churn test allows.
  NEXT: Decide the fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:24:47Z
  TYPE: DECISION
  CLAIM: The owner approved the fix ahead of the proposal (chat, 2026-10-04: "just fix it its all good"). Fix at
    the target-pass boundary rather than per strategy: when a plan-phase failure leaves a spell of the pass's
    Phase 5 scope missing from the live _spell_id_pool, the pass records the visibility failure for those ids as
    it does for KeyError misses; a failure with nothing missing still re-raises. Rejected: retyping the two
    processors' misses as KeyError (pins a test to RuntimeError, loses the message on the conjure path, and leaves
    any future strategy free to reintroduce the gap); a lock between passes and pool writers (passes are
    lock-free by design since the 2026-09-26 pool-read rule). The rule runs only on the failure path.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1755-1782
  - src/melder/aether/spellbook/spellbook_creation_system.py:1838-1858
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:493-493
  IMPACT: A meld racing a sever or uncontract fails with the SpellbookValidationError a later meld would get; the
    churn test's allowed set holds. Patch gate: failure-mode change in a concurrency-sensitive path, so patch docs
    first (architecture, component, code description).
  NEXT: Write the patch docs, then implement in spellbook_creation_system.py with unit and integration tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:25:59Z
  TYPE: PLAN
  CLAIM: Patch docs written and read in order (architecture, component, code description). Mapping: invariants
    and code-description steps 2-4 -> a failure-path helper _collect_missing_dependency_ids used by both
    target-local passes in place of _extract_missing_dependency_ids -> unit tests for the helper and both
    passes; the 'after' behaviour -> an integration regression that forces the sever before each phase 9 miss
    site and checks SpellbookValidationError then recovery; migration step 4 -> system docs, graph, notch
    0.2.8227, release note; step 5 -> assets and bundles last. No unknowns left in the patch docs.
  EVIDENCE:
  - context_compass/system_docs/patches/active/live_unlink_visibility_race_2026_10_04/architecture_patch.md:1-41
  - context_compass/system_docs/patches/active/live_unlink_visibility_race_2026_10_04/component_patch_target_resolution_pass.md:1-28
  - context_compass/system_docs/patches/active/live_unlink_visibility_race_2026_10_04/code_description_patch_target_pass_visibility.md:1-23
  IMPACT: The patch gate is satisfied; implementation stays inside spellbook_creation_system.py and tests.
  NEXT: Implement the helper and its two call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:37:57Z
  TYPE: DECISION
  CLAIM: Notes 5 and 6 are superseded. The boundary rule was implemented and failed the probe: the pass's Phase 5 scope
    held only the consumer, because a SpellContract provider enters the plan at Phase 8 through the contracted
    lookup, not through the Phase 5 DAG, so the scope check found nothing missing. It was reverted byte for byte.
    The fix reports the two misses the way the analyzer and the instance processor already do: KeyError whose
    args[0] is the missing spell id, with the old text kept as args[1] so conjure-path summaries stay readable.
    The one unit test that pinned RuntimeError is updated (the miss is still a hard failure, now a KeyError).
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1683-1794
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-298
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:39-115
  IMPACT: Two strategies change, spellbook_creation_system.py does not; the patch docs are rewritten to match.
  NEXT: Record the implementation and its validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:37:57Z
  TYPE: FACT
  CLAIM: Implemented: SpellOccurrenceContractProcessorStrategy._compile_contract_overrides_for_occurrence and
    SpellRuntimeProcessorStrategy.process raise KeyError(spell_id, message) for a spell absent from the pool,
    with Raises sections that state why. Tests: the runtime-processor miss test expects KeyError and args[0];
    a contract-processor miss test; an _extract_missing_dependency_ids test for the two-argument KeyError; and
    the integration regression, which forces a sever or an uncontract to finish just before either processor
    (4 cases), expects SpellbookValidationError, then restores the contract and melds again.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_occurrence_contract_processor_strategy.py:185-298
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_runtime_processor_strategy.py:39-115
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:428-458
  - tests/unit/melder/spellbook/spell_compiler/test_spell_strategy_migrations.py:518-536
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:655-667
  - tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py:1-325
  IMPACT: Every forced window now ends in an error the churn test allows.
  NEXT: Record the validation runs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:37:57Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t, pytest -p no:cacheprovider -o addopts="": the new regression is 4 passed
    with the fix and 4 failed with the two strategy files restored to their pre-fix bytes (then restored to the
    fixed bytes, cmp clean). Touched and neighbouring tests (strategy migrations, contract scanner failure types,
    resolution fast path, dependency flags, resolution-validation component and integration, the whole
    multithreading integration directory): 133 passed in 78.4s. The churn test alone: 26 runs, 26 passed. The
    probe with the uncontract mutation also ended in SpellbookValidationError; on the old code it raised
    PhaseExecutionError and left the next meld failing with 'Cannot build CreationContext before
    spell_codegen_creation exists'. Not run yet: the full tiers (after the docs and the notch).
  EVIDENCE:
  - tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py:287-325
  - tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py:794-1069
  IMPACT: The fix is proven red/green on the exact window the hosted run hit, and covers the uncontract lane.
  NEXT: Rewrite the patch docs, then system docs, graph, notch 0.2.8227 and the release note.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-04T23:44:34Z
  TYPE: FACT
  CLAIM: Documented and notched: src_architecture (failure mode, the compiler pool-read invariant, handoff),
    src_components (SpellCompiler failure mode, the FORWARDREF citation remapped from 219-258 to 373-413 because
    the contract processor grew, handoff) and tests_components (multithreading cluster) with their three indexes
    regenerated and checked; both processor nodes carry the miss rule and were re-read and accepted; the graph
    reassembled (587 ranges verified). __version__ is 0.2.8227, the running note has the Fixed section and the
    rebuild line, the board carries the notch notice. The patch docs were rewritten to the KeyError fix.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1531-1538
  - context_compass/system_docs/src_components.md:4181-4190
  - release_docs/next_version_release.md:527-542
  - src/melder/__version__.py:12-12
  IMPACT: Everything but the CI lane and the final rebuild is in place for this ticket.
  NEXT: Assets and llm_support rebuild after the CI lane's edits (last write of the session).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:59:15Z
  TYPE: MEASURE
  CLAIM: Tiers on the device VM, CPython 3.14.7t, after the notch: tests/unit 8938 passed, 3 skipped, 7 xfailed,
    1 failed - test_generated_build_assets_are_stamped_for_the_live_version, expected until the assets are rebuilt
    for 0.2.8227 (the last write; rerun reported in chat); tests/component 2293 passed, 23 skipped, 1 xfailed;
    integration spellbook+aether+live_sim+mutation_research 1454 passed, 2 skipped, 1 xfailed, 2 xpassed;
    integration conduit+multithreading 329 passed; docs unittest OK and build_docs check OK (301 pages). Not run:
    tests/integration/melder/crystallizer (longer than one device call; it never reaches the changed miss paths).
  EVIDENCE:
  - tests/integration/melder/multithreading/test_contract_mutation_during_meld_resolution_integration.py:287-325
  IMPACT: No regression outside the expected version stamp.
  NEXT: Assets and llm_support rebuild (last write); then the owner pushes and accepts; on acceptance promote the
    patch docs and close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Fixed (Notes 2-11): a borrower's meld that raced a link sever or an uncontract hit a Phase 9 pool miss reported
as RuntimeError, which the target pass could not classify, so the meld raised PhaseExecutionError. Both Phase 9
miss sites now raise KeyError(spell_id, message); the pass records a visibility failure and the meld raises
SpellbookValidationError, then recovers when the contract returns. Regression forced red/green, tiers pass, docs,
graph, patch docs, notch 0.2.8227 and release note done. Owner-owed: push and acceptance; then promote the patch
docs (system_docs/patches/active/live_unlink_visibility_race_2026_10_04/) and close.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
