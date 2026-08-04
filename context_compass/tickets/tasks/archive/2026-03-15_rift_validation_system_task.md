# Task: RiftValidationSystem

## Metadata
- Task ID: TASK-2026-03-15-rift-validation-system
- Story: STORY-2026-03-15-aethericrift-v1-workspace-runtime
- Status: ready
- Owner: codex
- Priority: p0
- Created: 2026-03-15T11:59:14Z
- Updated: 2026-03-15T11:59:14Z

## Objective
Implement `RiftValidationSystem` so codegen is parsed, validated, and
classified against the declared room target model before execution.

## Ticket Contract
- ENTRY_GATE: TASK-2026-03-15-rift-space-and-target-model is complete enough
  that the validation system has a declared target universe to validate against.
- EXECUTION_BOUNDARY: validation/classification logic only; no transport layer
  and no `dynamic` materialization behavior beyond gating.
- DEPENDENCIES:
  - TASK-2026-03-15-rift-space-and-target-model
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md
  - system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md
- EXIT_GATE: syntax checks, name/member-path validation, and request
  classification work against `RiftAttribute` / `RiftMethod` and respect the
  `simple` versus `dynamic` split.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if implementation pressure tries
  to bypass the declared room target universe with ambient Python access.

## Scope Boundaries
- In scope:
  - AST parsing
  - syntax allow/deny checks
  - name/member-path validation against room registries
  - request classification
  - mode-aware validation for `simple` versus `dynamic`
- Out of scope:
  - transport protocol
  - external sentinel system
  - MutationResearch internals

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: the AR patch set now defines validation as its own
  component with clear inputs, outputs, and control-flow guidance.

## Steps / Checklist
- [ ] Implement AST parsing and syntax validation.
- [ ] Implement name/member-path validation against `RiftAttribute` / `RiftMethod`.
- [ ] Implement request classification.
- [ ] Implement mode-aware gating for `simple` versus `dynamic`.
- [ ] Implement hook execution points defined by configuration.
- [ ] Add tests for syntax rejection, invalid target/member rejection, and mode gating.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `RiftValidationSystem`
- validation and classification tests

## Files / Paths Impacted
- src/melder/aether/aetheric_rift/
- tests/

## Validation
- Not run.
- Recommended commands:
  - `pytest tests -k rift_validation -v`
  - `pytest tests -k codegen -v`

## Risks / Rollback Notes
- Risk: weak validation lets the declared room target universe collapse back
  into ambient Python behavior.
  Rollback: tighten validation and keep UNKNOWNs visible before widening syntax.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-15T11:59:14Z
  TYPE: PLAN
  CLAIM: This task turns the validation patch and code-description patch into
    the governed codegen gate for the room: parse, validate declared targets,
    classify, and enforce the `simple` versus `dynamic` split before execution.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/component_patch_rift_validation_system.md:1-30
  - codex/context_compass/system_docs/patches/active/aethericrift_v1_workspace_runtime/code_description_patch_rift_validation_and_execution.md:1-34
  IMPACT: Completing this task creates the validation boundary that keeps AR
    execution aligned with the declared room target model.
  NEXT: begin implementation after the room/target model exists.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Third implementation task for the patch-driven AR v1 stack. It implements the
governed validation/classification layer over the room target model.
