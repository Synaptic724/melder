# Story: Preserve provider artifacts during borrower validation

CURRENT OWNER DIRECTION (2026-09-19): provider-artifact repair is active under the current model.
The broader redesign is retired. Earlier dependency/parking statements below are superseded history.
Keep tests asserting provider usability; no xfail or expected-error conversion is authorized.


## Metadata
- Story ID: STORY-2026-09-13-provider-artifact-ownership
- Epic: EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T18:14:07Z
- Updated: 2026-09-19T13:08:28Z

## User Narrative
As a provider owner, I need a borrower to compile its graph without retiring my executable artifacts,
so the original provider object remains usable before and after borrower resolution and cleanup.

## Value / MRP Alignment
Visibility must not confer lifecycle ownership. Artifact publication now follows the current pass
compilation scope while preserving the existing object model.

## Ticket Contract
- ENTRY_GATE: owner-assigned epic and linked reproduction task are routed.
- EXECUTION_BOUNDARY: Phase-5 publication and the artifact/context lifecycle it controls.
- DEPENDENCIES: accepted CommandOps consultation and original independent provider-prefix tests.
  The broader redesign prerequisite was withdrawn on 2026-09-19; its historical findings are retained.
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
- from_state: in_progress
- to_state: review
- transition_reason: native and unchanged original downstream provider acceptance pass; generated assets are current.

## Tasks
- [x] TASK-2026-09-13-repair-provider-artifact-ownership (delivered; acceptance pending):
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
- DATETIME: 2026-09-19T12:51:19Z
  TYPE: DECISION
  CLAIM: Owner retires the broader redesign and explicitly chooses to fix this artifact bug next.
    This supersedes the September 17 redesign dependency. Retain the current existing-object model
    and all corrected-behavior assertions; do not mark the seven native failures xfail.
  EVIDENCE:
  - Owner reply: Retire the broader redesign; fix the artifact bug next (Recommended).
  - tests/integration/melder/spellbook/test_provider_artifact_ownership.py:71-216
  IMPACT: Source investigation, bounded compiler repair, tests/docs/build checks are authorized.
    Native scope is provider-owned artifact publication versus borrower visibility, not object redesign.
  NEXT: Re-read the Phase-5 publication/invalidation chain, then stage the bounded patch contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

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

- DATETIME: 2026-09-19T13:08:28Z
  TYPE: FACT
  CLAIM: Child task delivers scoped artifact publication and native borrower/same-book protection.
    All nine original CommandOps provider proofs pass; docs and generated artifacts are synchronized.
  EVIDENCE:
  - tickets/tasks/2026-09-13_repair_provider_artifact_ownership_task.md
  - artifacts/provider_artifact_ownership_20260913/repair_result_20260919.md
  IMPACT: Concrete provider repair is ready for review under the retained current model.
  NEXT: Owner reviews the repair and confirms acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Provider-artifact repair delivered; all original provider proofs and native regressions pass.
The broader redesign is retired. Follow the child task's validation report; acceptance remains pending.
