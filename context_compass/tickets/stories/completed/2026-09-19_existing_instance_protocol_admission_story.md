# Story: Validate existing-instance Protocol declarations at bind

- Completed: 2026-09-19T14:51:36Z
- Closure Basis: explicit owner request to turn in all delivered updater_0 work.
- Summary: Accepted the bounded Bind Protocol repair under the retained unique-only supplied-object model.
- Deferred work: tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md.
  Historical unchecked redesign/downstream items are deferred, not an implementation claim.


## Metadata
- Story ID: STORY-2026-09-19-existing-instance-protocol-admission
- Epic: EPIC-2026-09-13-provider-artifact-ownership-and-existing-instance-planning
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p1
- Created: 2026-09-19T11:36:38Z
- Updated: 2026-09-19T14:51:36Z

## User Narrative
As a caller binding an existing object under a Protocol spellframe, I need bind to reject a false
member declaration before another object depends on it, while preserving compatible reference injection.

## Value / MRP Alignment
Close the demonstrated admission hole using the established binding boundary and current unique-only model.

## Ticket Contract
- ENTRY_GATE: owner explicitly approved the investigated Bind repair and requested this story/epic update.
- EXECUTION_BOUNDARY: Bind admission, permanent regression tests, relevant docs and generated assets.
- DEPENDENCIES: TASK-2026-09-19-investigate-existing-instance-protocol-validation and its native evidence.
- EXIT_GATE: child implementation verified, documentation/assets synchronized, outcome presented for acceptance.
- FAILURE_ESCALATION: record any required compiler or ownership redesign separately before extending this repair.

## Requirements (Functional)
- Apply the existing direct-public-member Protocol check to class and instance/other binding profiles.
- Check the supplied value itself: instance-only callable members pass; shadowed non-callable methods fail.
- Fail with TypeError at active and inactive bind, before publication; preserve existing class diagnostics.
- Preserve exact identity through annotation, collection, SpellMap and linked SpellContract resolution.

## Requirements (Non-Functional)
- No constructor discovery/invocation for supplied values and no reflective checks added to meld.
- Keep current concrete/string grouping, callable/factory behavior and unique-only admission.
- Preserve the checker's inherited-Protocol/data-annotation/signature limitations as explicit separate scope.

## Scope Boundaries
- In scope: the existing Bind branch/helper, native controls, public/component/graph documentation and assets.
- Out of scope: lifecycle/disposal changes, new external registration, richer profiles, additional lifetimes,
  provider-artifact ownership repair and complete Python Protocol type checking.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: owner accepts turn-in of delivered scope and explicitly backlogs unperformed user-created-object work.

## Dependencies / Related Work
- tickets/epics/backlog/2026-09-13_existing_object_lifecycle_ownership_epic.md
- tickets/tasks/completed/2026-09-19_investigate_existing_instance_protocol_validation_task.md
- tickets/stories/completed/2026-09-17_existing_object_reference_blueprint_discovery_story.md

## Tasks (Implementation Checklist)
- [x] tickets/tasks/completed/2026-09-19_repair_existing_instance_protocol_admission_task.md (delivered; review pending)

## Acceptance Criteria
- Missing and non-callable required members fail during active/staged bind before and after conjure.
- Compatible ordinary, inherited and instance-only members preserve supplied identity through consumers.
- Existing class, grouping, factory and unique-only contracts remain green.
- Relevant docs and generated assets reflect the repaired admission boundary.

## Validation / Test Plan
Run retained native red cases, expanded actual-instance/staging/compiler-path regressions, then the
focused Bind and existing-instance suites. Run required asset generation and consistency checks.

## UX / API / Data Notes
No API shape change. Existing incompatible registrations now fail early with an existing-object diagnostic.

## Risks / Mitigations
Checking type(value) is insufficient; tests distinguish class members from the actual supplied surface.

## Applicable Anti-Patterns
- [ ] No full Protocol checking or ownership redesign claimed from this narrow admission repair.
- [ ] No diagnostic monkeypatch reported as production acceptance.

## Open Questions
None blocking this repair. Broader Protocol member coverage remains a separate contract decision.

## Decision Log
- Owner selects admission parity in Bind; broader existing-object redesign remains exploratory.

## Artifact Links
Artifacts are owned and indexed through the child task; investigation evidence stays with its original task.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: record source evidence before expanding the selected boundary.

## Notes
- DATETIME: 2026-09-19T11:36:38Z
  TYPE: DECISION
  CLAIM: Owner authorizes implementation of the bounded actual-instance Protocol check in Bind.
  EVIDENCE:
  - Owner request: fix this in bind, update the epic, make a story and implement.
  - artifacts/existing_instance_protocol_20260919/findings.md:111-172
  IMPACT: Materialized the Protocol story within the existing-object epic without selecting its broader model.
  NEXT: Execute the linked repair task and capture native validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T11:52:48Z
  TYPE: FACT
  CLAIM: The child task delivers actual-instance admission and permanent regressions with 334 passing
    focused checks. Documentation and source/repository build assets are current; compiler is unchanged.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-19_repair_existing_instance_protocol_admission_task.md
  - artifacts/existing_instance_protocol_repair_20260919/validation.md
  IMPACT: Story is ready for owner review within its bounded admission contract.
  NEXT: Owner reviews results and accepts closure when satisfied.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T14:51:36Z
  TYPE: DECISION
  CLAIM: Owner accepts turn-in of this delivered record. Accepted the bounded Bind Protocol repair under the retained unique-only supplied-object model.
  EVIDENCE:
  - Owner instruction to backlog user-created-object ideas and turn in all work done.
  - artifacts/updater_0_turn_in_20260919/closure_manifest.json
  IMPACT: Record closed with its historical evidence retained. Deferred requirements remain visible
    in the backlog epic; no new runtime, test, installation or release result is implied.
  NEXT: Resume deferred work only on a new explicit owner request.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with owner.
- [ ] Owner acceptance and closure sync completed.

## Noting Behavior
Record cross-task decisions here; keep tactical source and validation evidence in the child task.

## Context / Handoff Summary
CLOSED BY OWNER: delivered scope is turned in; see the completion summary at the top. Any earlier
review/resume instructions below are historical. Deferred user-created-object work is parked in the
backlog epic and does not request continued implementation.

Bounded Bind repair implemented and verified; child task holds 334-test and generated-asset evidence.
Ready for review. Broader reference/blueprint discovery remains separate and unselected here.
