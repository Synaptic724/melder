# Task: Repair reported crystallizer and concurrent contract-churn failures

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Fixed crystal fixture capability and stale local cancellation; 394 distinct passes and 25 churn runs.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-fix-feature-turn-in-failures
- Story: STORY-2026-09-19-discoverable-registration-qualification
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-20T00:07:59Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Fix both owner-reported failures before completing the accepted feature turn-in.

## Ticket Contract
- ENTRY_GATE: Owner supplied two failures and explicitly requested their repair before closure.
  Existing onboarding/certification remains complete; the board routes this task.
- EXECUTION_BOUNDARY: The crystallizer test double and real contract-churn/cancellation paths,
  necessary regression tests, documentation/generated assets and feature turn-in records.
- DEPENDENCIES: Completed non-resolvable registration implementation and its final qualification task.
- EXIT_GATE: Both failures have source-backed diagnoses, passing focused regressions, and documented
  compatibility checks; then complete the previously requested feature turn-in.
- FAILURE_ESCALATION: Do not hide a settled-state failure with retry/xfail or weaken cancellation.
  Record any required ownership/concurrency contract change before implementing it.

## Scope Boundaries
- In scope: crystallizer dummy capability, concurrent unlink/relink validation cancellation and their callers.
- Out of scope: new ownership models, named lesser conduits, releases and unrelated repository cleanup.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Steps / Checklist
- [x] Read relevant component/test documentation and the two failing test implementations.
- [x] Reproduce and repair the crystallizer fixture mismatch.
- [x] Reproduce and diagnose cancellation across settled contract-churn phases.
- [x] Add a meaningful regression and implement the smallest source-backed correction if required.
- [x] Run affected checks and synchronize documentation/assets when inputs change.
- [x] Complete the requested feature turn-in after both repairs pass.

## Deliverables
- Corrected tests/runtime as warranted by evidence and a durable validation report.
- Completed feature closure with explicit scope and retained evidence.

## Files / Paths Impacted
- tests/unit/melder/crystallizer/test_crystallizer.py
- tests/integration/melder/multithreading/test_multithreading_link_bind_contract_features.py
- Cancellation/phase/validation owners reached through the relevant component and source graph slices.
- Feature tickets, boards and associated artifacts; source docs/build outputs only if affected.

## Validation
- 394 distinct focused tests passed, one existing asset-runner test skipped, zero failures.
- The unchanged owner churn test passed 25 fresh-process repetitions.
- Six new deterministic cases failed before repair and pass afterward on one and four workers.
- Source/repository asset freshness, new-test Ruff and whitespace checks pass.
- Full repository suite and coverage: Not run. Detailed scope and earlier diagnostics are retained in
  artifacts/non_resolvable_followup_20260919/validation.md.

## Risks / Rollback Notes
- The concurrency failure may be schedule-sensitive; preserve deterministic settled-state assertions.
- No tickets or patch directories were moved before the owner interrupted closure.
- Closure preparation changed only ticket text and mailbox metadata; existing code remains intact.

## Applicable Anti-Patterns
- [x] No defensive production fallback for an incomplete owned test double.
- [x] No masking settled-state cancellation with a retry or expected failure.
- [x] No closure before both reported failures have been handled.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/non_resolvable_followup_20260919/
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/architecture_patch.md
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/component_patch_spellbook_creation.md
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/code_description_patch_cancellation.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted feature turn-in; retain reports and reproduction evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record complete source-path findings and test outcomes before continuing into another work unit.

## Notes
- DATETIME: 2026-09-20T00:07:59Z
  TYPE: FACT
  CLAIM: The owner reported missing _DummySpell.resolvable during crystal construction and a
    PhaseExecutionError wrapping OperationCancelledError at after_relink_a in the concurrent churn test.
    The second diagnosis is not yet known; it must not be treated as harmless test drift.
  EVIDENCE:
  - artifacts/non_resolvable_followup_20260919/owner_contract_churn.txt:1-286
  - artifacts/non_resolvable_followup_20260919/owner_crystallizer.txt:1-179
  IMPACT: Feature closure waits for these repairs. Earlier successful selected tests remain historical evidence.
  NEXT: Read the relevant indexed component and test sections, then reproduce both failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:09:01Z
  TYPE: MEASURE
  CLAIM: The initial focused run reproduces the crystal failure exactly: one failed, ten passed.
    _DummySpell omits native resolvable while SpellCrystal requires that live-Spell contract.
    The concurrent churn case passed once, so its failure is schedule-sensitive and still unresolved.
  EVIDENCE:
  - tests/unit/melder/crystallizer/test_crystallizer.py:14-32
  - artifacts/non_resolvable_followup_20260919/baseline.log
  - artifacts/non_resolvable_followup_20260919/baseline.xml:1-1
  IMPACT: Add the default True capability to the test double; do not weaken crystal capture.
  NEXT: Correct the fixture and trace the churn test's validation/cancellation ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:10:10Z
  TYPE: FACT
  CLAIM: Local foundational registration captures scheduler.cancel_event in args before
    run_all_phases replaces the run signal. UnitOfWork receives the new event, but the Phase-5/6
    callable receives the old one. A previous aborted run therefore reaches local validation as
    already cancelled. The existing _phase_run_lock serializes runs; changing locks is unnecessary.
    The crystallizer fixture correction passes all seven root tests.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1847-1892
  - src/melder/aether/spellbook/spellbook_creation_system.py:2079-2189
  - src/melder/utilities/synchronization/phase_scheduler.py:914-976
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:169-174
  - artifacts/non_resolvable_followup_20260919/crystallizer_green.log:1-2
  IMPACT: Bind cancellation to the local unit's phase factory, after run scope creation. No meld
    fast-path work or cancellation suppression is needed.
  NEXT: Add deterministic previous-failure recovery and current-run cancellation regressions, then fix wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:14:55Z
  TYPE: DECISION
  CLAIM: Six deterministic real-pool regressions fail before the fix: prior-failure recovery and
    current-run cancellation inside each local Phase-5/6 callable, on one and four workers.
    Read/indexed the three patch contracts. Map their current-event invariant to the single-phase
    factory and the two cancellation-aware registrations; preserve every other phase and scheduler rule.
  EVIDENCE:
  - artifacts/non_resolvable_followup_20260919/cancellation_red_ready.log
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/architecture_patch.md:5-24
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/component_patch_spellbook_creation.md:3-19
  - system_docs/patches/completed/local_phase_cancellation_2026_09_19/code_description_patch_cancellation.md:3-18
  IMPACT: Both stale cancellation and missed current cancellation are evidenced, so the bounded wiring fix is ready.
  NEXT: Implement deferred event forwarding and rerun both owner files plus the new regression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:16:42Z
  TYPE: MEASURE
  CLAIM: Deferred event forwarding passes all six deterministic cancellation cases, both owner
    files and related creation-system/synchronization tests: 358 passed. The unchanged live-churn
    case also passes 25 fresh-process repetitions. The repair adds no steady-state meld work.
    Source component prose calling the scheduler one-shot was stale; full scheduler source confirms
    persistent pool/per-run signal behavior, now documented alongside local event binding.
  EVIDENCE:
  - artifacts/non_resolvable_followup_20260919/focused_green.log:1-6
  - artifacts/non_resolvable_followup_20260919/churn_summary.log:1-1
  - src/melder/utilities/synchronization/phase_scheduler.py:914-976
  IMPACT: Both reported failure causes are repaired and tested. Documentation/build synchronization remains.
  NEXT: Refresh the affected descriptor, component index and source/repository assets, then finish turn-in.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Fixed crystal fixture capability and stale local cancellation; 394 distinct passes and 25 churn runs.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
Both failures are repaired. Final qualification: 394 distinct passes, one asset-runner skip, and 25
fresh-process churn passes. New tests prove previous-run recovery and current-run cancellation.
Source assets and src/tests/other bundles pass final freshness checks. Complete the already requested
turn-in: feature epic, seven stories, nine original tasks plus this repair task; archive five patch
directories and retain validation evidence. No source work remains for these failures.

Earlier entry context: owner requested two repairs before closure. All feature
tickets and patch directories remain at active paths. Reuse completed onboarding in this uninterrupted
session; REONBOARD after compaction. No agents. Final source version was 0.2.43 in prior asset checks.
