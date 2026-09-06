# Task: Prove the shared-spell context publication and cleanup contract

- Completed: 2026-09-06T01:56:48Z
- Summary: Investigation and two owner-directed test skips delivered, with affected test assets refreshed. Underlying runtime repair remains deferred.

## Owner-Approved Closure
- Disposition: delivered_with_runtime_deferred
- from_state: review
- to_state: done
- transition_reason: Owner explicitly requested turning in all codex_1 tickets.
- Acceptance: Current closure is approved; it does not convert deferred work into implemented work.
- Historical plans, checklists and NEXT statements below are retained as history, not active authority.
- Closeout record: tickets/tasks/completed/2026-09-06_turn_in_codex_1_tickets_task.md
- Archived patch directory: system_docs/patches/completed/shared_context_rebuild_2026_09_05/

## Metadata
- Task ID: TASK-2026-09-05-shared-context-rebuild-race
- Epic: EPIC-2026-09-05-shared-context-rebuild-publication
- Story: none (runtime regression found during release-candidate qualification)
- Status: done
- Owner: codex
- Agent Name: codex_1
- Investigation By: workflows_1
- Priority: p1
- Created: 2026-09-05T19:09:39Z
- Updated: 2026-09-06T01:56:48Z

## Objective
Understand CounterSwitch's deque-ticket election, publication/reset ordering, and the failing test's
cleanup sequence. Prove the cause of the missing spell_codegen_creation failure before selecting a fix.

## Ticket Contract
- ENTRY_GATE: Existing certification, active route, and owner's explicit skip instruction for
  test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs.
- EXECUTION_BOUNDARY: Spell cold context retrieval, its factory/compiler publication dependencies,
  directly relevant unit/component/integration regressions, affected generated source/test assets,
  and this task's notes/artifacts. Owner additionally permits a skip marker on the controlled
  component reproduction, preserving its body, with affected generated test-bundle refresh.
  No runtime implementation or other test changes are authorized.
- DEPENDENCIES: Runtime successor epic 2026-09-05_shared_context_rebuild_publication_epic.md and
  release candidate task 2026-09-05_release_candidate_testpypi_workflow_task.md. The old
  release_matrix_concurrency_repair_2026_08_30 patch is historical input, not a selected repair.
- EXIT_GATE: Evidence-backed account of ticket election, reset/publication ordering, and cleanup;
  reproducible proof distinguishes a runtime violation from test misuse before any repair is proposed.
- FAILURE_ESCALATION: Do not conceal a runtime exception by extending timeouts, skipping Mac,
  swallowing errors, or changing public existence/cleanup semantics. Owner handles commits/pushes.

## Scope Boundaries
- In scope: exact-source root cause, CounterSwitch protocol, cleanup ownership, existing tests and proof.
- Out of scope: redesigning phase compilation, adding a hot-path/global lock, unrelated cleanup,
  scheduler fairness, credentials, branch mutation, commits, pushes, and package uploads.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Requested component case reports one skipped; test bundle refreshed and
  both asset freshness checks pass. Runtime source is unchanged.

## Steps / Checklist
- [x] Trace the original exception and distinguish teardown rendering from its cause.
- [x] Trace CounterSwitch election, deque tickets, event wakeup, advance/reset, and cleanup behavior.
- [x] Identify the context/artifact producers and consumers on the failing path.
- [x] Use existing checks and controlled execution to distinguish this failure from terminal test cleanup.
- [x] Record proven findings and unresolved design alternatives before code edits.

## Deliverables
- Protocol and failure analysis with reproducible evidence; no source/test modifications in this phase.

## Validation
- Current follow-up (2026-09-06): exact controlled component node reports 1 skipped in 0.32s.
- Selective tests-bundle regeneration succeeded; both source/repository --check commands exit 0.
- git diff --check passes. Full runtime suite: Not run for this skip-only follow-up.
- Earlier investigation evidence follows:
- 32 existing switch/factory checks pass; 20 no-GIL and 20 GIL-enabled independent cluster runs pass.
- 10 passive observer-traced runs pass. Controlled debugger pauses reproduce the original exception
  before terminal cleanup; all four conduits, Spell, artifact container, and switch have _cleaned=False.
- Runtime/test files involved match the hosted failing SHA. No source or test files were modified.

## Risks / Rollback Notes
- Missing a lock named by an old document does not prove a missing synchronization guarantee.
- Do not add locking to an existing fast path without a demonstrated requirement and performance rationale.
- The original full source and worker traceback need verification; platform interleavings can differ.
- No repair is selected; evaluate any proposed protocol change against the captured sequence first.

## Applicable Anti-Patterns
- [ ] No timeout workaround for missing runtime artifacts.
- [ ] No production edit from the cleaned repr alone.
- [ ] No hidden widening of the hot-path lock boundary.
- [ ] No claims of hosted or full-suite validation without execution.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/shared_context_race_20260905/owner_lifecycle_probe.py
  - artifacts/shared_context_race_20260905/owner-lifecycle-observation.json
  - artifacts/shared_context_race_20260905/validation.md
  - artifacts/shared_context_race_20260905/controlled-window.json
- LIFECYCLE_OWNER: tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md.
  This investigation borrows the two core evidence documents; the successor epic owns retention.
- CONTRACT_REFERENCES (read-only; owned by the original release-matrix task):
  - system_docs/patches/completed/release_matrix_concurrency_repair_2026_08_30/architecture_patch.md
  - system_docs/patches/completed/release_matrix_concurrency_repair_2026_08_30/component_patch_shared_spell_context.md
  - system_docs/patches/completed/release_matrix_concurrency_repair_2026_08_30/code_description_patch_shared_spell_context_rebuild.md
- DISPOSITION: retain_as_reference for core proof, under the successor epic's lifecycle.
- CLEANUP_TRIGGER: Closing this investigation must not delete the core proof or shared patch
  contracts. codex_1 adjudicates disposable reproduction outputs at accepted epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Append findings with source evidence before further investigation, implementation, or validation.

## Notes
- DATETIME: 2026-09-05T19:09:39Z
  TYPE: FACT
  CLAIM: Hosted macos-latest job 101359508941 at SHA a116ec22cd89cc148c719847ac83662078cd87e6
    raises a missing CreationContext input, not a barrier timeout. The cluster test collects worker
    exceptions, then its finally block cleans all four conduits before pytest renders argument reprs.
    Spell's docstring and the earlier accepted patch promise a cold-path spell RLock, but current
    _get_or_build_creation_context calls the factory without that lock. Factory/history checks remain.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33986010784/job/101359508941
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-353
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-1015
  - src/melder/aether/spellbook/spell.py:750-791
  IMPACT: The cleaned repr is post-failure teardown evidence; it does not establish premature cleanup.
    The absent documented synchronization is a concrete regression candidate to reproduce.
  NEXT: Read the factory/publication path and the lock's Git history, then identify a deterministic test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:09:39Z
  TYPE: FACT
  CLAIM: CreationContextFactory performs switch-based builder election without the spell lock;
    CreationContextBuilder reads the compiler artifact and raises the exact reported error when its
    codegen payload is absent. Current Spell cold retrieval also lacks the lock. Git blame dates the
    unlocked implementation before the August synchronization contract; the reason the expected code
    is missing is not established. The remedy must protect cold builds against phase invalidation,
    not add sleeps. Existing factory tests contain a controlled-lock helper worth checking.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:750-791
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:103-146
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_factory.py:145-145
  IMPACT: Factory election protects builders from each other; it does not protect their inputs from
    a simultaneous phase rebuild. Read the existing regression and phase owner before editing.
  NEXT: Inspect the deterministic lock regression and phase-5-to-11 lock ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:21:58Z
  TYPE: DECISION
  CLAIM: Owner explicitly stopped lock implementation and requires understanding the switch's deque-
    ticket protocol and cleanup evidence before code changes. The previous lock hypothesis was
    premature: documentation/source disagreement is not itself proof that the live election protocol
    is insufficient. Git status confirms only ContextCompass tracking/artifacts changed; source/tests
    are untouched. Analyze the switch first and present proof, not a preselected locking repair.
  EVIDENCE:
  - Owner's analysis-only instruction on 2026-09-05.
  - src/melder/utilities/synchronization/counter_switch.py
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  IMPACT: Historical patch files are leads, not authority to implement. No source/test additions or
    lock changes are authorized in this investigation phase.
  NEXT: Read CounterSwitch and its tests, then map every factory/reset/cleanup transition against it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:21:58Z
  TYPE: FACT
  CLAIM: CounterSwitch uses deque cardinality as state, not one ticket per active reader. selector
    claims 0 -> 1 under its own lock, followers at 1 wait on an Event, and states >=2 return directly.
    advance mutates tickets without that claim lock; the Event means not-pending and is also set at 0.
    Existing tests explicitly allow a pending follower to return 0 after advance(-1). Terminal cleanup
    is different: it deletes all slots and requires callers already quiescent. Phase-5 setters clear
    compiled outputs and call Spell._cleanup_creation_context, which resets this live latch to 0.
  EVIDENCE:
  - src/melder/utilities/synchronization/counter_switch.py:155-198
  - src/melder/utilities/synchronization/counter_switch.py:255-341
  - tests/unit/melder/utilities/synchronization/test_counter_switch.py:81-111
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-213
  - src/melder/aether/spellbook/spell.py:660-686
  IMPACT: Analyze builder election separately from compiled-input readiness and actual object teardown.
    No primitive bug or required additional lock has been concluded. No code has changed.
  NEXT: Run existing latch/factory tests and repeated existing cluster tests while tracing admission gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:21:58Z
  TYPE: MEASURE
  CLAIM: All 32 existing CounterSwitch/live-cleanup/factory cases pass on local Python 3.14t with
    PYTHON_GIL=0. The first repeated-node pytest command deduplicated its arguments and ran only one
    cluster case; that one passed, so this is not a 20-run result. Source tracing shows the spell-index
    CreationGate ticket is acquired inside context execution, after context retrieval/build. The outer
    Conduit gate surrounds Meld, but is a separate admission surface whose sharing must be checked.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/switch-contracts.xml
  - artifacts/shared_context_race_20260905/cluster-repeat.xml
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:263-309
  - src/melder/aether/conduit/meld/conduit_meld.py:357-384
  - src/melder/aether/conduit/conduit.py:4070-4106
  IMPACT: Normal latch behavior passes its existing contracts. No source/test code has changed, and
    no runtime defect has been experimentally isolated yet. Repeat with actual separate invocations.
  NEXT: Repeat the unchanged cluster test and inspect outer-gate admission and phase publication.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:21:58Z
  TYPE: MEASURE
  CLAIM: Twenty separate invocations of the unchanged two-cluster integration case pass on local
    Windows 3.14t with PYTHON_GIL=0. An initial report-argument syntax error ran no tests and was
    corrected before these twenty invocations. CreationGate is a different deque: it counts admitted
    operations and allows concurrent holders while enabled. The per-spell-index gate is entered after
    context retrieval. CodegenCreationSystem publishes its artifact only after its strategy chain.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/cluster-attempt-1.xml
  - artifacts/shared_context_race_20260905/cluster-attempt-20.xml
  - src/melder/utilities/synchronization/creation_gate.py:349-415
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:263-309
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:61-128
  IMPACT: No reproduced local failure yet. The admission ticket count is not mutual exclusion between
    all live meld calls. Continue diagnosis under alternate scheduling without changing implementation.
  NEXT: Run the same test in a GIL-enabled diagnostic mode and inspect captured worker state on failure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:40:39Z
  TYPE: MEASURE
  CLAIM: A further twenty separate runs of the unchanged cluster test pass with the GIL enabled
    as a scheduling diagnostic. This does not reproduce the hosted no-GIL failure. Ordinary contract
    tests and repetition therefore do not establish a fix. The remaining useful proof is a debugger
    observation of existing calls: ticket state, codegen input, and cleaned flags before teardown.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/gil-cluster-attempt-1.xml
  - artifacts/shared_context_race_20260905/gil-cluster-attempt-20.xml
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-692
  IMPACT: Source/tests remain unchanged. Temporary trace hooks will observe existing execution and
    emit data only; no monkeypatched method, extra lock, inserted sleep, or proposed repair.
  NEXT: Trace the unchanged test and preserve the first original worker exception with live-object flags.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:50:36Z
  TYPE: MEASURE
  CLAIM: Ten debugger-observed runs of the unchanged test also pass. Traces show the normal
    phase-5 reset to latch 0, phase-11 codegen publication, then factory selector 0 -> 1 -> 2.
    Ordinary scheduling did not overlap the owner read with the peer's reset window. Owner raised
    premature cleanup/test misuse as an alternative; test-finally cleanup follows worker joins.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/trace-attempt-1.json
  - artifacts/shared_context_race_20260905/trace-attempt-10.json
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:344-351
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:1007-1015
  IMPACT: Next proof uses debugger pauses at existing source boundaries, without changing any object
    fields or methods. Stop the diagnostic child at the original exception to capture flags before
    test teardown; this is an instrumented scheduling experiment, not a passing full-test claim.
  NEXT: Pause the owner before context read and the peer after phase 5, then capture original failure state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:54:37Z
  TYPE: MEASURE
  CLAIM: A debugger-controlled interleaving of the unchanged test reproduces the exact original
    missing-codegen RuntimeError on Windows 3.14t with the GIL disabled. Owner pauses before its
    readiness read; peer completes normal phase 5 and pauses before phase 11. Its cleanup/reset leaves
    live owners with context=None, codegen=None, latch=0. The owner resumes, legitimately claims
    ticket 1, and the original builder raises. All four conduits, Spell, compiler artifact container,
    and CounterSwitch have _cleaned=False. The diagnostic child stops before terminal test teardown.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/controlled-window.json
  - artifacts/shared_context_race_20260905/validation.md
  - src/melder/aether/conduit/meld/conduit_meld.py:357-384
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-692
  IMPACT: This proves the error can come from a live reset/publication window, without test-finally
    cleanup or a failed leader election. It does not prove that another lock is required. Source/test
    content matches CI SHA a116ec22cd89cc148c719847ac83662078cd87e6 for the traced files. No code changed.
  NEXT: Review the protocol evidence with the owner before selecting any implementation change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T20:01:37Z
  TYPE: PLAN
  CLAIM: Owner asks how to fix the proven window. Proposed design is one owned rebuild lifecycle:
    mark affected contexts pending before retiring old inputs, keep that ownership through phase
    rebuilding, publish the complete new context and codegen input before opening readiness, and
    explicitly release failed waiters. Simply replacing reset-to-0 with reset-to-1 is insufficient:
    phase 11 currently publishes only the codegen artifact, so the rebuild owner must take an explicit
    context-publication path rather than waiting on its own selector ticket.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/controlled-window.json
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:88-139
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:269-339
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:263-309
  IMPACT: Preserve the ready-state lookup without a new mutex. Existing admission tickets must cover
    context acquisition/use so old readers can drain before cleanup; avoid double-ticket/self-drain
    deadlocks if moving the current index-gate admission earlier. Overlapping writers, affected
    dependency spells, and failure wakeups are design requirements before implementation. This is a
    proposal, not a verified patch or a claim of unchanged measured performance. No source/test edits.
  NEXT: Review producer-owned rebuild/publication and reader-lifetime requirements with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T20:23:55Z
  TYPE: DECISION
  CLAIM: Owner requested a detailed runtime epic assigned to codex_1 and a mailbox handoff telling
    that agent to take it on. This investigation is transferred as review-state evidence; its
    historical findings remain attributed to workflows_1. Runtime implementation belongs to the
    successor epic, while workflows_1 retains workflow and release qualification responsibility.
  EVIDENCE:
  - tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md:17-30
  - artifacts/shared_context_race_20260905/controlled-window.json:29-51
  IMPACT: Core proof is retained under the epic and must survive investigation closure. The proposed
    mechanism remains open to codex_1's evidence-backed design; this task has made no runtime edits.
  NEXT: codex_1 consumes the successor epic and creates the required implementation work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:05:49Z
  TYPE: FACT
  CLAIM: codex_1 read the core proof and current latch/factory/context/phase implementations.
    CounterSwitch elects at idle but is not a reader count. Factory builder failure currently has
    no latch-abort path. Context execution acquires the index ticket after retrieval. Phase 5
    invalidates every spell in the selected dependency scope, not just the requested root; phase 11
    publishes codegen output but does not open context readiness itself. The current components
    document still describes the historical Spell lock and must not select the repair.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/controlled-window.json:6-51
  - src/melder/utilities/synchronization/counter_switch.py:255-341
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:293-339
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:233-309
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-360
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-692
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:77-127
  - system_docs/src_components.md:2514-2552
  IMPACT: Proposal must reconcile admission, scoped producer ownership and failure wakeup together.
    Current HEAD is 6fe5972f91c0fc40cff324e1040886d0fcc230ba; source/tests are unmodified in git status.
    No tests have been run by codex_1 for this new lane. Owner approval is required before code.
  NEXT: Trace Spell ownership/reset and the two Meld doors plus phase orchestration for a bounded proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:12:05Z
  TYPE: FACT
  CLAIM: The source trace confirms a wider scope mismatch: local Phase 5 invalidates the target
    and its dependency closure, while the local plan scheduler runs phases 8-11 on the target only.
    The Spellbook phase-run lock covers each scheduler run, not the entire foundational-plus-plan
    operation. Both Meld doors retrieve the context before its dynamic index admission. Spell reset
    deletes context slots and returns the latch to idle; a captured reference is not lifetime safety.
    The real cluster helper joins all workers before its final cleanup, matching the handoff proof.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:308-360
  - src/melder/aether/spellbook/spellbook_creation_system.py:1541-1635
  - src/melder/aether/spellbook/spellbook_creation_system.py:1852-1894
  - src/melder/aether/spellbook/spellbook_creation_system.py:2229-2295
  - src/melder/aether/conduit/meld/conduit_meld.py:357-458
  - src/melder/aether/conduit/meld/spellspace_meld.py:367-454
  - src/melder/aether/spellbook/spell.py:659-686
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-351
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-1015
  IMPACT: A pending-only switch tweak cannot be the complete repair: dependencies need a defined
    completion path, and active readers/builders must finish before their context is retired.
  NEXT: Review the producer-owned, admission-covered repair direction with the owner before code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:17:16Z
  TYPE: DECISION
  CLAIM: Owner rejected the broad implementation, rolled tracked code back, and now authorizes
    narrow discovery only. Owning Spellbook cleanup is terminal: no resurrection or revalidation of
    its dead Spells is permitted. Determine the owning book's actual state and cleanup caller at the
    original failure before classifying the test or choosing another repair. Earlier proof did not
    capture the owning Spellbook's cleanup flag.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/controlled-window.json:6-51
  - Owner's rollback, lifecycle clarification and discovery-only permission on 2026-09-05.
  IMPACT: No source/test edits, skips, implementation or asset regeneration. Tracked src/tests have
    no diff; two untracked files from the rejected attempt remain and are excluded from this discovery.
    They are creation_context_rebuild.py and test_shared_context_rebuild_publication.py. Do not delete
    or reuse them without owner direction. Earlier implementation contracts are superseded as authority.
  NEXT: Observe original cluster-test owner-book state, cleanup calls and the peer's revalidation reason.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:17:16Z
  TYPE: FACT
  CLAIM: Spellbook.cleanup sets its own _cleaned=True before entering component/spell teardown.
    A false owning-book flag at the original builder exception can therefore distinguish this case
    from terminal owner cleanup. Normal Conduit teardown drops resolution state and then cleans its
    owned Spellbook. Owner also asks whether missing/broken dependencies gate their surviving users,
    remain invalid, or unlink; inspect propagation separately from the original cluster schedule.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:358-387
  - src/melder/aether/spellbook/spellbook.py:535-579
  - src/melder/aether/conduit/conduit.py:835-869
  IMPACT: Prior false Spell/container flags alone were not a complete owner-state observation.
    No runtime fix is selected; the diagnostic must capture book flags and cleanup call order directly.
  NEXT: Observe original test owner lifecycle, then inspect dependency-removal propagation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:23:33Z
  TYPE: MEASURE
  CLAIM: The original cluster test completed under observer-only controlled scheduling and failed
    with the exact missing-codegen RuntimeError. Diagnostic control succeeded. At sequence 7 the
    owning Spellbook was uncleaned and still registered the identical Spell; Spell cleanup-request
    flag, Spell cleaned flag and all four Conduit/Spellbook cleaned flags were false. First terminal
    Conduit cleanup was sequence 8; the owning Spellbook cleanup was sequence 11 and Spell cleanup 12.
    The earlier context cleanup stack runs through Phase5._set_spell_system_index_phase5, not book death.
    Both peer resolution branches reported unknown with no prior change reason.
  EVIDENCE:
  - artifacts/shared_context_race_20260905/owner-lifecycle-observation.json:1-234
  - artifacts/shared_context_race_20260905/owner-lifecycle-observation.json:235-425
  - artifacts/shared_context_race_20260905/owner_lifecycle_probe.py
  IMPACT: This reproduction is not a meld after terminal owning-book cleanup. It establishes one
    valid failing interleaving on unchanged tracked source, not frequency or a selected repair.
    Python 3.14.0 free-threading / Windows / GIL off; pytest 1 failed in 0.74s, expected diagnostic failure.
  NEXT: Finish the source trace for dependency removal, invalid/gated propagation and contract unsharing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:27:07Z
  TYPE: FACT
  CLAIM: Dependency removal has an existing invalidation path. unregister_index computes reverse
    impact closure before deletion; surviving dependants become gated/impacted_by_dependency.
    RiskManager marks referencing books validation-required. Phase 6 records invalid conduit/root
    verdicts for visibility errors or reachable phase-4-broken spells. Normal Meld rejects invalid,
    disabled and cleaned verdicts; only unknown/gated enters revalidation. Validation records verdicts,
    not unlink operations. Normal Conduit teardown separately calls Ward cleanup to sever contracts
    before cleaning its owned book. Structural Spell.is_broken and conduit resolution invalidity are
    separate layers; do not describe every compilation exception as one universal broken flag.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:571-634
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:743-832
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:582-609
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:410-436
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:624-655
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:289-319
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:434-507
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:214-268
  - src/melder/aether/conduit/meld/meld.py:833-891
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:250-343
  IMPACT: A missing dependency does not require resurrecting its destroyed Spell. Its surviving
    consumer is a distinct object whose resolution can be invalid. Do not add auto-unlink behavior
    or assert every early phase exception persists is_broken without further specific evidence.
  NEXT: Discuss these existing lifecycle/validation boundaries with the owner; no runtime edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:27:07Z
  TYPE: MEASURE
  CLAIM: Four existing focused tests passed on Windows Python 3.14.0 free-threading, GIL off.
    Missing-contract and contract-restoration integration cases: 2 passed in 0.34s. Dependency
    unregister propagation and real owner-Conduit cleanup cases: 2 passed in 0.33s. Invoked via
    .venv_new/Scripts/python.exe -m pytest with the four explicit node ids and -q -p no:cacheprovider.
    Separately, the controlled original cluster test intentionally reproduced 1 failure in 0.74s.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_resolution_validation.py:110-234
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py:199-228
  - tests/integration/melder/conduit/test_conduit_integration_lifecycle.py:172-218
  - artifacts/shared_context_race_20260905/owner-lifecycle-observation.json:1-234
  IMPACT: These are scoped checks, not a full-suite pass or proof of all deletion/early-phase error
    paths. HEAD remains 6fe5972f91c0fc40cff324e1040886d0fcc230ba; tracked src/tests have no diff.
    The two rejected-attempt untracked files remain untouched and were not collected/imported.
  NEXT: Owner reviews discovery; the remaining original-case question is peer validation versus shared
    context invalidation, not terminal Spellbook death. No implementation is selected or authorized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:40:45Z
  TYPE: DECISION
  CLAIM: Owner explicitly requests pytest skip for only the original two-cluster test, superseding
    deletion, comment-out and cleanup-test redesign alternatives. Restore the complete original body
    and add a descriptive skip marker. This is owner-directed deferral, not a runtime repair claim.
  EVIDENCE:
  - Owner instruction: "wait just flag it as skip".
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-1016
  IMPACT: No production changes, no replacement test and no broader exception allowance. Earlier
    comment-out was tested: remaining module cases passed 18/18. Recheck after restoring the body.
  NEXT: Add the single skip marker and verify this module reports 18 passed and one explicit skip.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:42:08Z
  TYPE: MEASURE
  CLAIM: Original test body restored unchanged and marked pytest.skip at owner direction. Final
    tracked test diff is exactly three added decorator lines. Target module reports 18 passed,
    1 skipped in 0.64s on Windows Python 3.14t; git diff --check passed. Runtime source is unchanged.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-943
  IMPACT: Only this case is deferred; no broad exception allowance, replacement test or runtime fix.
    No commit/push or full-suite/repository-asset qualification is claimed. Abandoned untracked helper
    and regression from the rejected attempt remain untouched; they are not part of this skip change.
  NEXT: Owner reviews/commits the skip; workflows_1 receives the changed release disposition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:42:41Z
  TYPE: FACT
  CLAIM: Owner now supplied the separate active component reproduction and asks why it fails.
    The test warms the owner, pauses the peer after real Phase5.run_local, starts the owner,
    then requires both calls to succeed. Phase 5 clears shared codegen inputs and the Spell
    context; Spell cleanup resets CounterSwitch to 0. The selector elects a builder from 0,
    while CreationContextBuilder refuses a constructed Spell whose codegen payload is None.
    Phase 11 later publishes that payload. Per-conduit validity and shared-context readiness
    are different: a valid owner returns before the revalidation lock; cold context retrieval
    currently delegates to the factory without taking the spell lock. The pasted failure alone
    does not identify which caller raised because the test appends bare exceptions to one list.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:26-159
  - src/melder/aether/conduit/meld/meld.py:833-893
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:600-693
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:365-396
  - src/melder/aether/spellbook/spell.py:659-687
  - src/melder/aether/spellbook/spell.py:750-792
  - src/melder/utilities/synchronization/counter_switch.py:298-342
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:294-339
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-153
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:60-126
  IMPACT: This is deliberate overlap, not terminal fixture cleanup or a failure-rate measurement.
    The test asserts waiting/success rather than permitting an unavailable-input refusal. That
    contract must not be treated as implicit authorization to redesign the compiler. The Spell
    retrieval docstring and src_components still describe a cold-path lock absent from source.
    No source/test change or new experiment has been made; no new tests were run.
  NEXT: Explain the current readiness gap and the test's stronger expectation to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:43:44Z
  TYPE: FACT
  CLAIM: The active component reproduction is a new codex_1 regression from the rejected repair
    attempt. Its originating task records a known-red run at 2026-09-05T21:40:09Z. Git history
    shows the test first committed in bf8f05986 at 2026-09-05T16:42:51-06:00. It is separate
    from the original cluster test that was explicitly skipped. Owner reports all three builds
    now fail this added reproduction; no new local run or source/test disposition is made here.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-05_shared_context_protocol_repair_task.md:106-121
  - git log --follow -- tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:68-159
  IMPACT: Explain this as a leftover known-red reproduction, not three newly diagnosed platform
    faults. Recommend opt-in experimental placement while repair is deferred; do not silently
    alter the test or implement the rejected runtime changes.
  NEXT: Owner selects disposition of this exact added component test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:45:09Z
  TYPE: DECISION
  CLAIM: Owner says "yeah put skip on this one too", authorizing only a pytest skip on
    test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs. Preserve the full fixture
    and test body. Verify the exact case is skipped and refresh its generated test corpus.
  EVIDENCE:
  - Owner instruction in current conversation.
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:68-159
  IMPACT: This is explicit deferral, not a concurrency fix or an experiment implementation.
  NEXT: Add the single skip decorator and run the exact pytest node.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:45:42Z
  TYPE: MEASURE
  CLAIM: Added exactly three decorator lines to the controlled component test; its body and
    fixture are unchanged. Running the exact node on .venv_new Python reports one skipped,
    with the owner-deferral reason, in 0.32 seconds (exit 0).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:68-70
  - git diff -- tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py
  - .venv_new/Scripts/python.exe -m pytest tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py::test_owner_meld_waits_for_peer_rebuild_before_using_context_inputs -q -rs -p no:cacheprovider
  IMPACT: Exact requested case is deferred; no runtime repair or unrelated skip was added.
  NEXT: Refresh only the LLM tests corpus and verify repository/source freshness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:45:55Z
  TYPE: MEASURE
  CLAIM: Selective repository regeneration rewrote the tests corpus (807 files) and its proofs.
    The builder was invoked with --corpus tests; no source/other corpus regeneration was requested.
  EVIDENCE:
  - .venv_new/Scripts/python.exe llm_support/_builder.py --corpus tests (exit 0)
  IMPACT: The skip edit is represented in the committed-test bundle expected by CI.
  NEXT: Check both asset families and final diff hygiene.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T00:46:06Z
  TYPE: MEASURE
  CLAIM: Exact requested test is skipped, with body and fixture intact. Both source and repository
    freshness checks pass at 0.2.36, and diff hygiene passes. Product diff is four files:
    three skip-decorator lines plus the generated tests bundle, tests index, and shared manifest.
    No runtime source, workflow, version, or other test was edited. No commits or pushes occurred.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:68-70
  - .venv_new/Scripts/python.exe llm_support/_builder.py --check (exit 0)
  - .venv_new/Scripts/python.exe src/melder/_build_assets/_build_asset_runner.py --check (exit 0)
  - git -c core.whitespace=cr-at-eol diff --check (exit 0)
  - git diff --stat -- tests llm_support src
  IMPACT: Owner-directed deferral is implemented without reintroducing the rejected runtime repair.
    The original skipped cluster case remains unchanged. Existing scratch deletion was preserved.
  NEXT: Owner reviews the exact skip and generated test-asset changes before committing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T01:56:48Z
  TYPE: DECISION
  CLAIM: Owner turns in this ticket with disposition delivered_with_runtime_deferred.
    Investigation and two owner-directed test skips delivered, with affected test assets refreshed. Underlying runtime repair remains deferred.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-06_turn_in_codex_1_tickets_task.md
  - Recorded delivery, validation and owner decisions in this ticket.
  IMPACT: Work item is closed; no source, test, remote or publication action is implied.
  NEXT: none; future implementation requires a new owner-approved lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Latest owner instruction implemented (2026-09-06T00:46:06Z): the added controlled component
reproduction also has an explicit pytest skip. Exact node verification: 1 skipped; body unchanged.
The three affected LLM tests files were regenerated and both asset checks pass. No runtime fix,
experiment, commit, or push. Previous explanation and investigation history follows.

2026-09-06 explanation-only follow-up: current CI failure is the separate component reproduction,
not the original skipped cluster case. It forces overlapping peer validation and owner context
retrieval, then asserts wait-and-succeed. Current source has no cold Spell lock despite stale
docstrings. Owner is considering an opt-in experiment; neither an experiment nor runtime repair
has been implemented or run in this follow-up. See the newest note before historical material.

Latest owner decision: original cluster test is retained with a pytest skip marker. Its module
passes 18 tests and explicitly skips this one. Runtime repair remains rejected/deferred. No further
test changes or source changes are authorized by this disposition.

Latest state: review after discovery-only work on 2026-09-05T22:27:07Z. The owning book was alive
and still registered the exact Spell at the reproduced exception; final cleanup followed. Four
existing dependency-validation/cleanup tests passed. No tracked source/test changes were made.
Implementation remains rejected/blocked; do not reconstruct the old patch from historical notes.

Historical handoff follows; it does not override the latest discovery-only owner authority.
Owner transferred runtime ownership to codex_1 through
tickets/epics/completed/2026-09-05_shared_context_rebuild_publication_epic.md.
This task remains the review-state investigation input. codex_1 selects and validates the repair
under that epic; workflows_1 stays on workflows and candidate qualification. The epic owns retention
of controlled-window.json and validation.md, so closing this task cannot remove the proof.

The investigation was analysis only. No runtime/test code was added or changed, no lock was
introduced, and no methods/object fields were monkeypatched. The proposed producer-owned rebuild
lifecycle is a design option, not a selected patch. Read the epic's reader-lifetime, cache, failure,
affected-spell and performance requirements before implementing.

Proof now exists: debugger pauses in the original public cluster test expose phase 5's normal live
cleanup/reset before phase 11 publication. The owner sees latch 0, correctly claims 1, and the real
builder raises because the compiled input is None. All four Conduits, Spell, artifact container, and
CounterSwitch are uncleaned at that instant. This rules out terminal test teardown for the reproduced
path; it does not rule out every unrelated cleanup bug. The original CI-relevant files match the
failing hosted SHA a116ec22cd89cc148c719847ac83662078cd87e6.

Existing checks: 32 switch/factory tests, 20 independent no-GIL cluster runs, 20 GIL-enabled diagnostic
runs, and 10 passive traced runs passed. The controlled child was intentionally stopped at the real
exception before test teardown, so it is not a completed test-suite result or frequency measurement.

CounterSwitch's election itself followed its contract. The caller reset to idle while replacement
phase inputs were unavailable. codex_1 now owns how rebuilding/publication participates in the
ticket/lifecycle protocol, including pending-builder failure recovery. Do not resurrect the old lock
patch by default; owner expressly requires proof before code and protects the existing fast path.
Only ContextCompass tracking and diagnostic data were modified by this investigation.
