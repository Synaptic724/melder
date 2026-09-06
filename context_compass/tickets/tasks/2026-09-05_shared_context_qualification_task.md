# Task: Qualify shared-context safety, performance and generated documentation

## Metadata
- Task ID: TASK-2026-09-05-shared-context-qualification
- Story: STORY-2026-09-05-shared-context-safety
- Status: ready
- Owner: codex
- Agent Name: codex_1
- Priority: p1
- Created: 2026-09-05T21:17:10Z
- Updated: 2026-09-05T21:17:10Z

## Objective
Qualify the accepted protocol repair against the parent epic, measure its actual fast/cold cost,
refresh source docs/assets, and hand exact runtime evidence to workflows_1. Covers epic S4.

## Ticket Contract
- ENTRY_GATE: Protocol-repair task supplies a coherent implementation and passing focused cases.
- EXECUTION_BOUNDARY: Relevant suites, repeat/concurrency qualification, performance probes,
  canonical source/test docs, graph descriptors and generated source/LLM assets.
- DEPENDENCIES: TASK-2026-09-05-shared-context-protocol-repair and parent epic acceptance matrix.
- EXIT_GATE: Exact local evidence, current assets/docs, explicit hosted limits and runtime handoff.
- FAILURE_ESCALATION: Do not claim an unavailable platform or performance result; report failures.

## Scope Boundaries
- In scope: qualification of this runtime change only.
- Out of scope: workflow edits, disabling required checks, commits/pushes/signing/uploads.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Qualification scope is defined; execution awaits the protocol repair.

## Steps / Checklist
- [ ] Run focused unit/component/integration suites and repeated original cluster case.
- [ ] Run the supported local suite using the repository CI runner.
- [ ] Measure unchanged baseline versus repair: automatic warm, dynamic, cache and cold paths.
- [ ] Update affected canonical documents/descriptors and regenerate source/LLM assets.
- [ ] Map every epic criterion to evidence or an explicit limitation.
- [ ] Send exact tested revision/files, results, assets and hosted requirements to workflows_1.

## Validation
Not run. Baseline and changed results must include platform, interpreter/GIL mode, command and status.
Linux/macOS/hosted runner success is not implied by local Windows qualification.

## Risks / Rollback Notes
Keep baseline/changed measurement environments identical; avoid cache-state or interpreter confounds.
Preserve unrelated agent changes during regeneration and report the final tested tree precisely.

## Applicable Anti-Patterns
- [ ] No zero-overhead claim without measurements.
- [ ] No full-suite or hosted pass inferred from focused tests.
- [ ] No asset regeneration before semantic source/docs changes are settled.

## Done Checklist
- [ ] All local qualification outcomes and remaining hosted work are explicit.
- [ ] Runtime handoff sent; owner acceptance obtained before closure.
- [ ] Boards and artifacts synchronized.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: add scoped measurement/test output paths when created.
- DISPOSITION: retain_as_reference for core reports; delete_on_close for disposable scratch.
- CLEANUP_TRIGGER: Parent-accepted closure after report preservation.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Every measured claim includes the exact command, environment, output and next action.

## Notes
- DATETIME: 2026-09-05T21:17:10Z
  TYPE: PLAN
  CLAIM: Qualify only after the atomic producer/reader fix; no local or hosted pass is claimed yet.
  EVIDENCE:
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:253-298
  IMPACT: Keep runtime implementation separate from release/workflow ownership.
  NEXT: Consume the protocol-repair result once its controlled tests pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task is ready but not running. It owns evidence, performance and source docs/assets, not the
workflow rollout. The parent epic carries the complete success criteria and original CI pointers.
