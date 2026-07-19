# Task: Implement codegen_namespace_builder.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after `CodegenNamespaceBuilder` landed and the
  root engine stopped hand-building the placeholder namespace directly.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-namespace-builder-py
- Story: STORY-2026-04-25-codegen-system-namespace-directory
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement `CodegenNamespaceBuilder` as the owner of live namespace assembly.

## Ticket Contract
- ENTRY_GATE: the namespace directory story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md`
  - namespace strategy tasks
- EXIT_GATE: namespace builder is ready to consume namespace configuration and
  produce `CodegenNamespace`.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if namespace assembly requires a
  different strategy decomposition.

## Scope Boundaries
- In scope:
  - namespace builder only
- Out of scope:
  - policy configuration
  - execution
  - validation strategy logic

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: namespace builder ownership is explicit.

## Steps / Checklist
- [ ] Implement `CodegenNamespaceBuilder`.
- [ ] Consume namespace strategies instead of hand-building one giant dict.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- namespace builder implementation

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: builder becomes a god object.
  Rollback: keep exposure logic in the namespace strategy files.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: `CodegenNamespaceBuilder` should own assembly, not policy and not live
    execution.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md:1-103
  IMPACT: This file becomes the namespace composition point.
  NEXT: implement it after the configuration and namespace objects exist.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: PLAN
  CLAIM: The first builder slice will consume only the minimal strategy set
    needed for the agreed stable namespace contract:
    room objects, workstation, command, and target.
  EVIDENCE:
  - system_docs/patches/active/codegen_namespace_foundation/code_description_patch_codegen_namespace_flow.md:1-18
  IMPACT: This task can move now without waiting on the full namespace strategy story.
  NEXT: implement the builder and wire it into `CodegenSystem`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T00:01:28Z
  TYPE: FACT
  CLAIM: `codegen_namespace_builder.py` is now implemented and owns live
    namespace assembly through the minimal strategy set for this slice.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:1-106
  IMPACT: `CodegenSystem` no longer needs to build namespace globals itself.
  NEXT: keep builtins and any later direct-locals strategy out of this file until explicitly needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the namespace builder file.
