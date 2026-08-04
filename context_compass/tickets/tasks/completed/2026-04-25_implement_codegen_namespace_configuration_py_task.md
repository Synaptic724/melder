# Task: Implement codegen_namespace_configuration.py
- Completed: 2026-04-25T10:37:18Z
- Summary: Closed during cleanup after the explicit namespace-policy object
  landed as the contract layer ahead of live namespace assembly.

## Metadata
- Task ID: TASK-2026-04-25-implement-codegen-namespace-configuration-py
- Story: STORY-2026-04-25-codegen-system-namespace-directory
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T00:01:28Z
- Updated: 2026-04-25T10:37:18Z

## Objective
Implement `CodegenNamespaceConfiguration` as the explicit policy object for
namespace exposure.

## Ticket Contract
- ENTRY_GATE: the namespace directory story is active.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py`
- DEPENDENCIES:
  - `tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md`
  - `src/melder/aether/nexus/rift/projection/codegen_projection.py`
- EXIT_GATE: one explicit namespace configuration object exists.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if namespace configuration
  belongs in transaction context instead.

## Scope Boundaries
- In scope:
  - namespace policy object
- Out of scope:
  - live namespace dicts
  - namespace strategy execution

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: namespace configuration is a standalone concern.

## Steps / Checklist
- [ ] Implement `CodegenNamespaceConfiguration`.
- [ ] Keep it separate from the live namespace object.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- namespace configuration object

## Files / Paths Impacted
- src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py

## Validation
- Not run.

## Risks / Rollback Notes
- Risk: policy config drifts into the builder or live namespace object.
  Rollback: keep policy state here only.

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
  CLAIM: Namespace configuration should hold the policy view of what code may
    see before any live objects are exposed.
  EVIDENCE:
  - tickets/stories/2026-04-25_codegen_system_namespace_directory_story.md:1-103
  IMPACT: This file is the bridge between projection/ACL truth and live namespace assembly.
  NEXT: implement this before `CodegenNamespaceBuilder`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-04-25T10:37:18Z
  TYPE: FACT
  CLAIM: `codegen_namespace_configuration.py` is now implemented as the
    explicit namespace-policy object used by the root engine before any live
    objects are exposed into codegen execution.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:1-139
  - tickets/stories/2026-04-25_codegen_system_root_directory_story.md:109-117
  IMPACT: Namespace exposure policy is no longer implicit or smeared into the
    builder/runtime dict path.
  NEXT: keep later builtins/direct-local expansion decisions in follow-on
    namespace work rather than widening this object.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the namespace configuration object.
