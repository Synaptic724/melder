

Completed: 2026-02-17T11:57:04Z
Summary: Closed by explicit user directive to close all currently open tickets.

# Epic: System Representation Documentation Improvement

## Metadata
- Epic ID: EPIC-2026-02-16-system-representation-documentation-improvement
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-16T21:24:22Z
- Updated: 2026-02-17T11:57:04Z
- Target Window: 2026-Q2
- Related Program/Initiative: Context Compass System Representation Standards

## Problem / Opportunity
`context_compass` represents another system, but our representation standard for
`src_architecture` and `src_components` is not yet explicit enough for
consistent discovery and extension into per-component described contexts.

## MRP Alignment (Most Reasonable Product)
The MRP is a deterministic documentation standard:
- architecture and components remain separate core docs,
- docs move to one canonical folder,
- instruction docs replace local README dependency.

This keeps representation quality high while reducing navigation overhead.

## Ticket Contract
- ENTRY_GATE: discovery lane is routed and story/task set is defined.
- EXECUTION_BOUNDARY: context_compass architecture/component docs and standards
  only.
- DEPENDENCIES: current architecture/components baselines and onboarding
  path contracts.
- EXIT_GATE: standard is documented and discovery outputs are accepted.
- FAILURE_ESCALATION: unresolved model ambiguity is raised as
  `DECISION_REQUEST`.

## Goals (Outcomes)
- Define clear system-context representation standards for context_compass.
- Keep separate `src_architecture` + `src_components` docs in one canonical
  folder.
- Include tests architecture/components docs in the same canonical folder.
- Replace folder READMEs with explicit instruction docs.

## Non-Goals (Explicit Exclusions)
- Rewriting all architecture/components content in this epic.
- Runtime code changes outside documentation standards.

## Scope Boundaries
- In scope:
- Discovery, ranking, and phased folder/path migration for architecture and
  components docs.
- Out of scope:
- Full content migration of all existing docs.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: user requested closing all tickets as done.

## Success Metrics
- Discovery/ranking story outputs created and routed.
- Staged migration story/tasks created and routed.
- Canonical system-docs folder contract documented.
- Open design questions captured for user decisions.

## Requirements (Functional + Non-Functional)
- Functional:
  - discovery of current architecture/components behavior.
  - phased migration plan for one-folder doc location.
- Non-functional:
  - flat-file markdown only.
  - evidence-backed claims and UNKNOWN-first handling.

## Constraints / Assumptions
- Constraints:
  - preserve existing architecture/components docs as current canonical baseline.
  - no external tooling dependency.
- Assumptions:
  - current docs are strong enough to improve in place without full rewrite.

## Dependencies / External References
- `context_compass/system_docs/src_architecture.md`
- `context_compass/system_docs/src_components.md`
- `context_compass/system_docs/tests_architecture.md`
- `context_compass/system_docs/tests_components.md`
- `context_compass/SKILLS.MD`
- `context_compass/agent_onboarding/default/general/skills/workflow.md`

## Milestones (Track Progress)
- [x] Milestone 1: Ranking baseline completed for `src_architecture` and
      `src_components`.
- [x] Milestone 2: Canonical `system_docs/` folder contract approved.
- [x] Milestone 3: Phase-1 file move and instruction docs completed.
- [x] Milestone 4: Phase-2 onboarding/policy path migration completed.

## Stories (Required to Complete)
- [x] Story: STORY-2026-02-16-system-representation-documentation-discovery -
      Discover current state and define standard decisions.
- [x] Story: STORY-2026-02-16-system-docs-unification-and-instruction-contract -
      Execute staged one-folder migration and instruction-contract adoption.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-02-16-system-representation-documentation-discovery.
- [x] Task: Complete story STORY-2026-02-16-system-docs-unification-and-instruction-contract.
- [x] Task: Keep attention-board routing synchronized with active migration task.
- [x] Task: Verify UNKNOWN-first evidence discipline in all migration notes.

## Acceptance Criteria (Epic Done)
- Ranking outputs for architecture/components exist.
- One-folder migration contract and staged tasks are explicit.
- User confirms migration phase completion step-by-step.

## Risks / Mitigations
- Risk: onboarding breakage from path migration.
  Mitigation: stage policy/readset rewires after file move task.
- Risk: one-shot churn.
  Mitigation: execute ticketed phases over time.

## Applicable Anti-Patterns
- [x] No one-shot broad path rewrite across all archives.
- [x] No phase advancement without user confirmation.
- [x] No closure without onboarding-gate validation evidence.

## Validation / Test Approach
- Documentation validation via evidence-backed cross-reference checks.
- No code tests required in discovery-only tranche.

## Rollout / Adoption Plan
- Run migration in phases:
  1) ranking/discovery baseline,
  2) folder contract + phase planning,
  3) file move + instruction docs,
  4) onboarding/policy path migration,
  5) optional phase-5 cleanup.

## Open Questions
- Should tests instruction docs be added now, or only src instruction docs?

## Decision Log
- 2026-02-16: Epic opened for system representation documentation improvement.
- 2026-02-16: Hard-cut migration approved; no compatibility stubs retained
  for removed `architecture/` and `components/` paths.

## Notes
- DATETIME: 2026-02-16T22:32:29Z
  TYPE: MEASURE
  CLAIM: The system-doc unification story is complete and accepted; phase
    migration tasks are turned in, and canonical `system_docs` references are
    now active in onboarding/policy docs.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-02-16_system_docs_unification_and_instruction_contract_story_completed.md:6-10
  - context_compass/tickets/tasks/completed/2026-02-16_system_docs_phase1_src_and_tests_docs_move_task_completed.md:6-10
  - context_compass/tickets/tasks/completed/2026-02-16_system_docs_phase2_onboarding_reference_migration_task_completed.md:6-10
  IMPACT: Epic can now focus on the remaining discovery/ranking lane.
  NEXT: Route active board state to the discovery story for the next
    improvement tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T21:24:22Z
  TYPE: PLAN
  CLAIM: This epic starts as discovery-only so we can define a stable standard
    before any large doc rewrite.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1-45
  - context_compass/system_docs/src_components.md:1-34
  IMPACT: We reduce rework and keep decisions grounded in current docs.
  NEXT: Create discovery story and route to first discovery task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-02-16T22:04:24Z
  TYPE: DECISION
  CLAIM: Direction changed to phased one-folder migration over time, with two
    core docs retained and explicit instruction docs replacing local READMEs.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-02-16_system_docs_unification_and_instruction_contract_story_completed.md:1-135
  - context_compass/tickets/tasks/completed/2026-02-16_system_docs_unification_discovery_and_cutover_plan_task_completed.md:1-108
  IMPACT: Epic now includes controlled migration execution instead of expanding
    into a default `src_described` layer.
  NEXT: Route active work to phase-1 discovery/cutover planning task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program direction, terminology decisions, and tranche boundaries.
- Keep tactical details in story/task notes.
- Keep notes append-only and UNKNOWN-first.

## Context / Handoff Summary
Epic now includes staged system-doc location migration with ticketed phase
controls and explicit onboarding-safety gates.