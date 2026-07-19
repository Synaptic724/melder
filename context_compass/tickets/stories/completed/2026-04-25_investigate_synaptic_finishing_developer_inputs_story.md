# Story: Investigate Synaptic Finishing Developer Inputs
- Completed: 2026-04-26T15:08:08Z
- Summary: Closed after the role-creation and finishing-skill inputs were
  mapped and turned into the implementation basis for the new role lane.

## Metadata
- Story ID: STORY-2026-04-25-investigate-synaptic-finishing-developer-inputs
- Epic: EPIC-2026-04-25-synaptic-finishing-developer-role-foundation
- Status: done
- Owner: codex
- Agent Name: codex_modder_1
- Priority: p0
- Created: 2026-04-25T21:57:49Z
- Updated: 2026-04-26T15:08:08Z

## User Narrative
As the role designer, I want the new finishing role grounded in the current
role system and current documentation/testing skill surfaces, so that the role
is real and not a shallow rename.

## Value / MRP Alignment
This story prevents a fake overlay. It makes the role foundation evidence-based
before we author the role docs and register the profile.

## Ticket Contract
- ENTRY_GATE: epic exists and the role-design lane is routed.
- EXECUTION_BOUNDARY:
  - current profile-creation docs
  - current `engineer` and `synaptic_python_developer` role surfaces
  - current architecture/components/graph consumption requirements
  - this story and linked investigation task
- DEPENDENCIES:
  - `PROFILE_CLASS_CREATION_GUIDE.md`
  - `agent_onboarding/default/engineer/SKILLS.MD`
  - current `synaptic_python_developer` overlay docs
- EXIT_GATE: investigation findings explicitly define how the new role should
  be wired and what skill surfaces it must include.
- FAILURE_ESCALATION: raise `BLOCKER` if current role mechanics are too
  ambiguous to safely add a new user-defined profile.

## Requirements (Functional)
- Identify how a new role must be registered.
- Identify which current docs/testing skills should be reused or expanded.
- Identify where current engineer behavior is insufficient for mandatory
  finishing-role system-context reads.

## Requirements (Non-Functional)
- Evidence-backed.
- Compact enough to drive implementation without guesswork.

## Scope Boundaries
- In scope:
  - role-creation mechanics
  - current overlay structure
  - current documentation/testing skill inventory
- Out of scope:
  - authoring the new role docs themselves
  - config edits
  - board or patch-artifact wiring beyond this story's own state

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user requested explicit investigation before and
  during implementation, so the investigation story must be active first.

## Dependencies / Related Work
- TASK-2026-04-25-investigate-role-creation-and-finishing-skill-surface

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-investigate-role-creation-and-finishing-skill-surface
  - audit role wiring and source skill surfaces
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Require meaningful-finding note updates during discovery/implementation.

## Acceptance Criteria
- The role-creation wiring contract is explicit.
- The source overlay files to copy/expand are explicit.
- The mandatory system-context readset for the finishing role is explicit.

## Validation / Test Plan
- Not run.
- Validation is document reread and evidence consistency only.

## UX / API / Data Notes
- No user-facing runtime API changes.
- This story feeds a role/onboarding API change only.

## Risks / Mitigations
- Risk: investigation is too shallow and misses required wiring.
  Mitigation: include config, role-map, engineer, and current overlay evidence.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should the finishing role carry its own examples now or reference the current
  synaptic examples initially?

## Decision Log
- Investigation will use the current `synaptic_python_developer` overlay as the
  structural starting point, not the QA role.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: The new finishing role should inherit from `engineer`, not from
    `general`, because it needs the full engineering baseline before it adds
    deeper documentation and test-finishing behavior.
  EVIDENCE:
  - context_compass/PROFILE_CLASS_CREATION_GUIDE.md:137-159
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:25-43
  IMPACT: The new role should be a child overlay of `engineer`, not a parallel
    replacement.
  NEXT: document the existing source overlay we should copy and deepen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-25T21:57:49Z
  TYPE: FACT
  CLAIM: `synaptic_python_developer` already groups the exact surface we need
    to mine for this role: docstrings, comments, and a pytest-centered testing
    stack.
  EVIDENCE:
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:17-40
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md:15-55
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/testing/testing_overview.md:17-120
  IMPACT: The finishing role can reuse the proven overlay split while focusing
    it much more tightly on documentation and test depth.
  NEXT: create the investigation task and the implementation story/task set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to prove the new role design against the current profile
system before implementation begins. It should end with clear, file-backed
answers about inheritance, registration, skill reuse, and mandatory readset
design.
