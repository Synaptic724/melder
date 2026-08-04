# Epic: Expand Nexus Frame Authoring Test Surface
- Completed: 2026-04-25T21:59:28Z
- Summary: Closed after the Nexus frame authoring test program delivered a
  review-backed matrix of 139 unit, 42 component, and 42 integration executed
  cases, satisfying the requested test-surface targets.

## Metadata
- Epic ID: EPIC-2026-04-20-expand-nexus-frame-authoring-test-surface
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T16:45:16Z
- Updated: 2026-04-25T21:59:28Z
- Target Window: 2026-Q2
- Related Program/Initiative: Nexus frame authoring contract hardening

## Problem / Opportunity
The Nexus frame authoring subsystem was introduced and then tightened through
several follow-on fixes:
- stale `Nexus` helpers were removed
- Nexus-managed frames were forced to dynamic/AI-native/Rift-enabled posture
- frame registries and collaborator seams were moved toward interface-based
  typing

But the current dedicated test surface for
`NexusFrameManager`, `NexusFrameBuilder`, and `NexusFrameConfiguration` is still
thin. The user explicitly wants a full review of these objects and a large,
high-signal test matrix, split into unit, component, and integration stories.

## MRP Alignment (Most Reasonable Product)
The MRP is not a token-heavy count chase or filler coverage. It is:
- one explicit review lane over the three Nexus frame authoring objects
- one unit story that locks down object-level contracts and failure behavior
- one component story that proves small real wiring slices around authoring
  and publication
- one integration story that proves real runtime behavior through Nexus/Rift
  entrypoints

That is the smallest trustworthy way to turn this subsystem into a stable
public-library surface.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested an epic-first planning step for the
  Nexus frame authoring review and test expansion lane.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus_frame_manager.py`
  - `src/melder/aether/nexus/nexus_frame_builder.py`
  - `src/melder/aether/nexus/nexus_frame_configuration.py`
  - directly related tests under `tests/unit/melder/aether/`,
    `tests/component/melder/aether/`, and `tests/integration/melder/aether/`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-20_review_and_expand_nexus_frame_authoring_tests_task.md`
  - `tickets/tasks/2026-04-20_enforce_dynamic_only_nexus_frame_manager_contract_task.md`
  - `tickets/tasks/2026-04-20_remove_stale_nexus_state_methods_task.md`
- EXIT_GATE: the review findings are explicit and the three required stories are
  accepted with their requested high-signal test surfaces.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested counts force
  low-value filler tests or widen beyond the Nexus frame authoring subsystem.

## Goals (Outcomes)
- Review the current Nexus frame authoring objects from a contract-quality
  perspective.
- Build a large unit test surface over object-level behavior.
- Build a real component test surface over small wired slices.
- Build a real integration test surface over runtime authoring behavior.
- Keep the added tests high-signal and contract-driven.

## Non-Goals (Explicit Exclusions)
- Repo-wide test count inflation unrelated to Nexus frame authoring.
- Lower Melder runtime semantics outside the Nexus frame authoring lane.
- Broad Nexus or AR architectural redesign beyond review-proven issues.

## Scope Boundaries
- In scope:
  - `NexusFrameManager`
  - `NexusFrameBuilder`
  - `NexusFrameConfiguration`
  - directly supporting Nexus/Rift frame-authoring seams
- Out of scope:
  - unrelated `Nexus` managers
  - codegen execution design
  - non-Nexus frame publication subsystems unless directly required by tests

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: the linked Nexus frame authoring test task delivered the
  requested 120/40/40 split and the user directed closure for tickets whose
  work is already finished.

## Success Metrics
- Unit story reaches at least 120 meaningful test cases.
- Component story reaches at least 40 meaningful test cases.
- Integration story reaches at least 40 meaningful test cases.
- Review findings are documented before the large test expansion begins.

## Requirements (Functional + Non-Functional)
- Tests must stay attached to real contracts, lifecycle rules, topology modes,
  failure paths, rollback behavior, and publication semantics.
- No filler assertions purely to inflate counts.
- Validation reporting remains truthful.
- Touched docstrings must stay accurate as the review expands coverage.

## Constraints / Assumptions
- Existing test helpers may need to be refactored or expanded to support the
  requested counts without copy-paste sludge.
- The current authoring task already exists and may be reused as a tactical
  lane once the stories are accepted.
- UNKNOWN remains the default for any review claim not backed by source
  evidence.

## Dependencies / External References
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-04-20_review_and_expand_nexus_frame_authoring_tests_task.md`
- `src/melder/aether/nexus/nexus_frame_manager.py`
- `src/melder/aether/nexus/nexus_frame_builder.py`
- `src/melder/aether/nexus/nexus_frame_configuration.py`

## Milestones (Track Progress)
- [ ] Milestone 1: review findings are documented and accepted as the basis for test expansion
- [ ] Milestone 2: unit test story reaches its requested high-signal count target
- [ ] Milestone 3: component test story reaches its requested high-signal count target
- [ ] Milestone 4: integration test story reaches its requested high-signal count target

## Stories (Required to Complete)
- [ ] Story: STORY-2026-04-20-expand-nexus-frame-authoring-unit-test-surface
- [ ] Story: STORY-2026-04-20-expand-nexus-frame-authoring-component-test-surface
- [ ] Story: STORY-2026-04-20-expand-nexus-frame-authoring-integration-test-surface

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: align review findings with the existing authoring test task
- [ ] Task: verify high-signal count totals across unit/component/integration suites
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- The three stories exist and are accepted.
- The test count targets requested by the user are met.
- The resulting test surface remains contract-driven rather than filler-driven.

## Risks / Mitigations
- Risk: counts drive filler tests.
  Mitigation: tie each new case to a real branch, lifecycle edge, topology
  rule, or contract failure.
- Risk: the lane widens into unrelated Nexus cleanup.
  Mitigation: keep the epic explicitly scoped to the frame authoring objects.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Focused validation rings per story plus cumulative count tracking.
- No claims about coverage percentages unless the user runs and reports them.

## Rollout / Adoption Plan
- Review first.
- Unit story second.
- Component story third.
- Integration story fourth.

## Open Questions
- Whether the current tactical task should become the unit-story anchor or be
  split further after the review note set lands.

## Decision Log
- 2026-04-20T16:45:16Z: use one epic with three stories because the user
  explicitly required epic-first planning before implementation.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-20T16:45:16Z
  TYPE: PLAN
  CLAIM: The test expansion lane should be split by test class, not by object,
    because the user asked for separate unit, component, and integration
    planning before execution.
  EVIDENCE:
  - user_instruction: "make an EPIC first"
  - user_instruction: "make a story for the unit tests, component tests, and integration tests"
  IMPACT: The next step is story creation and then a pause, not immediate test
    generation.
  NEXT: create the three stories and stop for user review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This epic owns the review and test expansion lane for Nexus frame authoring.
