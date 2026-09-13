# Story: Preserve provider artifacts during borrower validation

## Metadata
- Story ID: STORY-2026-09-13-provider-artifact-ownership
- Epic: EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning
- Status: in_progress
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-13T18:14:07Z

## User Narrative
As a provider owner, I need a borrower to compile its graph without retiring my executable artifacts,
so the original provider object remains usable before and after borrower resolution and cleanup.

## Value / MRP Alignment
Visibility must not confer lifecycle ownership. Repair native ownership at the publication boundary.

## Ticket Contract
- ENTRY_GATE: owner-assigned epic and linked reproduction task are routed.
- EXECUTION_BOUNDARY: Phase-5 publication and the artifact/context lifecycle it controls.
- DEPENDENCIES: accepted CommandOps consultation and original independent provider-prefix tests.
- EXIT_GATE: native regressions and original GraphCache/PolicyEngine proofs pass with unchanged inputs.
- FAILURE_ESCALATION: raise any unresolved owner-versus-borrower scope decision before patching.

## Requirements
- Preserve provider Spell, unique object, data, compiled artifacts and owner visibility.
- Cover repeated validation, two borrowers, consumer resolution and consumer cleanup.
- Do not recompile provider canonical state under a borrower merely to replace invalidated data.
- Preserve real GraphCache/PolicyEngine acceptance tests and independent final prefix probes.

## Scope Boundaries
- In scope: publication/invalidation ownership and focused native/downstream verification.
- Out of scope: Optional/default changes, named conduits, publication or downstream environment replacement.

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: updater_0 accepted the owner-authorized repair assignment.

## Tasks
- [ ] TASK-2026-09-13-repair-provider-artifact-ownership:
  tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md

## Acceptance Criteria
- All eight original provider-prefix cases and the full original linked-provider test pass.
- Repeated/two-borrower validation preserves identity, retained state and provider usability.
- Source and regression evidence demonstrate coherent ownership; no validation bypasses.

## Validation / Test Plan
Reproduce natively, then repair and run ownership/contract regressions. Coordinate original downstream
acceptance through the CommandOps lead with a verified local package; never replace his environment silently.

## Risks / Mitigations
Shared Spell references make apparently local setter calls destructive to the provider; read the full
publication and teardown chain before selecting a change.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record design uncertainty before implementation.

## Notes
- DATETIME: 2026-09-13T18:14:07Z
  TYPE: FACT
  CLAIM: Current CompilerPhase5 byte hash matches the accepted installed-0.2.40 consultation.
    The implementation task owns native reproduction and patch selection.
  EVIDENCE:
  - tickets/epics/2026-09-13_provider_artifact_ownership_and_existing_instance_planning_epic.md:116-143
  - ../../priv_commandops/context_compass/tickets/tasks/2026-09-13_native_provider_runtime_expert_review_task.md
  IMPACT: No known source drift in the diagnosed publication mechanism; execution still needs reproduction.
  NEXT: Follow the linked task's reproduction and ownership trace.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active native ownership repair. Consult the linked task for tactical evidence and original test identities.
