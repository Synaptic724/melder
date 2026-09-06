# Task: Repair shared-context producer and reader coordination together

## Metadata
- Task ID: TASK-2026-09-05-shared-context-protocol-repair
- Story: STORY-2026-09-05-shared-context-safety
- Status: blocked
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-05T21:17:10Z
- Updated: 2026-09-05T21:17:10Z

## Objective
Turn the retained live-owner reproduction into controlled regressions and implement one coherent
input rebuild/context publication/active-reader lifetime protocol. Covers epic S1-S3 atomically.

## Ticket Contract
- ENTRY_GATE: Owner-approved direction, current source evidence and active attention route.
- EXECUTION_BOUNDARY: Spell context lifecycle, factory/publication, both Meld doors, phase orchestration,
  directly required coordination helpers, and focused regressions. Runtime edits require patch contracts.
- DEPENDENCIES: Parent epic, original investigation, and retained controlled-window proof.
- EXIT_GATE: Original forced window is repaired; dependency overlap, admitted-reader lifetime,
  failure/cancellation, cache/deferred/existing-instance paths pass controlled checks.
- FAILURE_ESCALATION: Stop before weakening CI, adding fast-path locks, widening public semantics,
  or treating unresolved ownership as an implementation assumption.

## Scope Boundaries
- In scope: exact surfaces listed in the parent proposal and directly required private helpers/tests.
- Out of scope: CounterSwitch rewrite, workflows, credentials, commits, pushes and publication.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner authorizes the proposed source repair and regression execution.

## Steps / Checklist
- [x] Consume original proof and current CounterSwitch/factory/Spell/context/phase-5/phase-11 code.
- [ ] Finalize affected-scope ownership, reader admission and failure semantics in patch contracts.
- [ ] Add a real-meld schedule-controlled regression; demonstrate failure on unchanged runtime.
- [ ] Implement admitted acquisition and producer-owned publication/retirement as one change.
- [ ] Cover failures, overlapping scopes, acquired readers, cold/cache/deferred and independent spells.
- [ ] Append implementation and verification evidence before handing to qualification.

## Deliverables / Files
- Targeted component regression under `tests/component/melder/aether/conduit/`.
- Spell, context factory/context, Meld doors/base and affected phase orchestration.
- Private coordination helper only when required by the verified ownership contract.
- Patch contracts under `system_docs/patches/active/shared_context_rebuild_2026_09_05/`.

## Validation
- Not run by codex_1 yet. Earlier workflows_1 measurements remain attributed in original evidence.
- Start with the existing cluster case and controlled component regressions on Python 3.14t, GIL off.
- Exercise success, failure and teardown, not a test-mandated Spell mutex or fixed delay.

## Risks / Rollback Notes
- Phase 5 clears dependency contexts while target-local plans currently rebuild only the root.
- Root-first lock ownership and scheduler ownership differ; avoid lock inversion across dependencies.
- Moving admission around validation can make a rebuilding caller drain itself; forbid that ordering.
- Keep new/changed behavior localized and revertable through an ordinary reviewed reverse patch.

## Applicable Anti-Patterns
- [ ] No defensive snapshot/guard without a concrete correctness contract.
- [ ] No incomplete publication, stranded pending latch, or retired-context use.
- [ ] No timing-only proof, CI relaxation, or unmeasured performance assurance.

## Done Checklist
- [ ] Protocol and implementation match; focused regressions pass with exact evidence.
- [ ] Qualification task receives file/revision and remaining-verification pointers.
- [ ] Owner acceptance and closure synchronization completed.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/architecture_patch.md
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/component_patch_spell_context.md
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/component_patch_meld_runtime.md
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/component_patch_compiler.md
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/code_description_patch_context_protocol.md
  - artifacts/shared_context_race_20260905/controlled-window.json
  - artifacts/shared_context_race_20260905/validation.md
- DISPOSITION: retain_as_reference; original proof remains owned by parent epic.
- CLEANUP_TRIGGER: Parent-accepted closure only. Patch links added before runtime edits.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Append tactical source findings and measurements, with exact evidence and one next step.

## Notes
- DATETIME: 2026-09-05T21:17:10Z
  TYPE: FACT
  CLAIM: Baseline HEAD is 6fe5972f91c0fc40cff324e1040886d0fcc230ba. Git comparison reports no src/tests
    changes from the failing CI revision a116ec22cd89cc148c719847ac83662078cd87e6. The working tree
    contains coordination/proof files only; no runtime or test edits have been made by codex_1.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md:293-360
  - artifacts/shared_context_race_20260905/controlled-window.json:6-51
  IMPACT: The retained reproduction applies to current source; start from the proven window.
  NEXT: Finish the scope/publication contract and add the controlled real-meld regression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:40:09Z
  TYPE: MEASURE
  CLAIM: Baseline selection passed 32 tests on .venv_new Python 3.14.0 free-threading, GIL off
    (CounterSwitch + CreationContextFactory + original two-cluster case). The new controlled real-meld
    regression fails on unchanged runtime with the exact missing-codegen RuntimeError in 0.46s.
    Its first fixture used ordinary unique linking and did not trigger local phase 5; corrected to
    the original cluster existence/sharing/election boundary before treating the run as a reproduction.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py:1-164
  - artifacts/shared_context_race_20260905/controlled-window.json:29-43
  IMPACT: Original failure is now a permanent deterministic public-path regression. No runtime source
    is changed. Global py -3.14t lacks pytest; .venv_new is the working test interpreter. Baseline
    emitted one pytest-cache permission warning; the red run used -p no:cacheprovider to avoid that I/O.
  NEXT: Complete scope/ownership patch contracts, then repair the producer/reader boundary and rerun red test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T21:40:09Z
  TYPE: DECISION
  CLAIM: Required patch contracts were authored and read in architecture -> components -> control-flow
    order. Map Spell context patch to gate/failure fields and factory abort tests; Meld patch to a
    shared admitted execution helper and both-door ticket/lifetime tests; compiler patch to one rare
    affected-scope writer window and original-gap/dependency-overlap regressions. CounterSwitch is unchanged.
  EVIDENCE:
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/architecture_patch.md:1-55
  - system_docs/patches/active/shared_context_rebuild_2026_09_05/code_description_patch_context_protocol.md:1-28
  IMPACT: Runtime implementation entry gate is satisfied for this bounded attempt; nested/teardown,
    failure and performance verification remain required before qualification or any completion claim.
  NEXT: Add the rare writer scope and wire admitted context access plus producer publication together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:17:16Z
  TYPE: DECISION
  CLAIM: Owner rejected and rolled back the implementation attempt. This task is stopped;
    implementation is not authorized. Discovery resumes under the original investigation task.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md
  IMPACT: Do not reconstruct the rejected patch or treat its temporary contracts as approved design.
  NEXT: Await source-led lifecycle findings and a new explicit owner decision before any runtime edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner approved trying the proposal and running tests. CounterSwitch stays unchanged. The design
must cover reader lifetime and every invalidated dependency, not merely prevent one builder error.
Source maps were read via verified indexes; current source investigation is recorded in predecessor.
