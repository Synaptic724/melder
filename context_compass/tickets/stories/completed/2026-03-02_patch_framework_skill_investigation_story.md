# Story: Investigate Patch Framework Skill Contracts

Completed: 2026-03-05T00:20:03Z
Summary: Patch-framework skills are implemented with policy-only gating and
template-based patch artifacts; investigation tasks are closed and archived.

## Metadata
- Story ID: STORY-2026-03-02-patch-framework-skill-investigation
- Epic: EPIC-2026-03-02-patch-framework-skill-amendment-system
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-03T01:03:46Z
- Updated: 2026-03-05T00:20:03Z

## User Narrative
As the project owner, I want a formal investigation story for future-state patch
documentation and reusable skill contracts so implementation can proceed with
explicit boundaries and without documentation drift.

## Value / MRP Alignment
This story creates the investigation backbone required to move from current-state
maps to implementable, agnostic patch-framework and skill contracts.

## Ticket Contract
- ENTRY_GATE: epic is in progress and framework artifact is linked.
- EXECUTION_BOUNDARY: investigation and contract-definition tasks only.
- DEPENDENCIES: EPIC-2026-03-02-patch-framework-skill-amendment-system and
  framework artifact.
- EXIT_GATE: all investigation tasks complete with accepted findings and clear
  implementation follow-ons.
- FAILURE_ESCALATION: raise DECISION_REQUEST on unresolved contract overlaps.

## Requirements (Functional)
- Investigate `architecture_patch` and `component_patch` contract definitions.
- Investigate `code_description_patch` necessity and trigger conditions.
- Investigate ticket-to-patch boundaries to prevent duplicate planning artifacts.
- Investigate patch-governance coupling boundaries in agnostic terms.
- Investigate patch lifecycle closure and cleanup mechanics.
- Investigate future-state skill additions to operationalize the framework.

## Requirements (Non-Functional)
- Keep evidence-first notes for each investigation stream.
- Keep outputs reusable across future patch sets.
- Maintain deterministic routing and artifact-link synchronization.

## Scope Boundaries
- In scope:
  - investigation tasks and synthesis outputs for framework definition;
  - explicit mapping between patch docs and existing ticket system.
- Out of scope:
  - runtime module implementation;
  - project-specific domain architecture decisions.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: implementation and policy closure are complete, and user
  approved closing this lane.

## Dependencies / Related Work
- EPIC-2026-03-02-patch-framework-skill-amendment-system
- artifacts/2026-03-02_patch_framework_skill_system.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-03-02-investigate-architecture-patch-contract - define
      architecture patch contract and template shape.
- [x] Task: TASK-2026-03-02-investigate-component-patch-contract - define
      component patch and code-description patch rules.
- [x] Task: TASK-2026-03-02-investigate-patch-ticket-boundary - define
      anti-duplication contract with ticket system.
- [x] Task: TASK-2026-03-02-investigate-patch-governance-coupling-contract -
      define agnostic ingress/control-plane boundaries.
- [x] Task: TASK-2026-03-02-investigate-patch-lifecycle-cleanup - define
      active-to-canonical lifecycle and deletion rules.
- [x] Task: TASK-2026-03-02-investigate-future-state-skillset - define skill
      additions for repeatable future-state amendment work.
- [x] Task: TASK-2026-03-03-patch-engineer-skill-docs-for-patch-framework -
      implement engineer baseline skill-document updates for patch-context handling.
- [x] Task: TASK-2026-03-03-patch-design-engineer-skill-docs-for-patch-framework -
      implement design-engineer instruction and skill-map updates for patch workflows.
- [x] Task: TASK-2026-03-03-verify-inherited-role-compatibility-after-engineer-patch -
      verify inherited role chains remain consistent after engineer baseline changes.
- [x] Document manual patch-gate validation expectations for engineer/design lanes.
- [x] Add active-lane patch artifact templates under `system_docs/patches/active/`.
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Require meaningful-finding note updates during discovery and synthesis.

## Acceptance Criteria
- All six investigation tasks produce explicit findings and recommendations.
- Patch artifact taxonomy is finalized with non-overlapping responsibilities.
- Governance coupling contract is defined without domain-specific naming.
- Lifecycle rule is explicit: patch docs are temporary and removed after merge.
- Follow-on implementation tasks are defined for engineer/design patch docs plus inherited-role verification.

## Validation / Test Plan
- Validate each task output maps to one investigation stream and one follow-on action.
- Validate epic/story/task and artifact links are consistent.
- Validate board routing points to this story or active child task.

## UX / API / Data Notes
- This story defines process and documentation contracts, not runtime APIs.
- Outputs feed follow-on implementation ticketing for skill creation.

## Risks / Mitigations
- Risk: process overhead from patch docs.
  Mitigation: strict boundary that tickets own execution and patch docs own deltas.
- Risk: scope drift back to project-specific coupling semantics.
  Mitigation: enforce agnostic naming and boundary checks in each task.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed.
- [x] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- Should `code_description_patch` be required for every changed component or
  only high-complexity components?

## Decision Log
- 2026-03-03: investigation runs as six bounded tasks to prevent mixed-scope analysis.
- 2026-03-03: framework/skill language is domain-agnostic by default.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-03-02_patch_framework_skill_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: after follow-on implementation planning accepts outputs.

## Notes
- DATETIME: 2026-03-03T12:30:00Z
  TYPE: DECISION
  CLAIM: Story has been renamed and rewritten to remove legacy domain-specific naming and keep investigation scope portable.
  EVIDENCE:
  - context_compass/tickets/stories/2026-03-02_patch_framework_skill_investigation_story.md:1-34
  - context_compass/tickets/epics/2026-03-02_patch_framework_skill_amendment_system_epic.md:1-19
  IMPACT: Linked tasks can now produce reusable skills/contracts without embedding domain-specific semantics.
  NEXT: align the coupling task text to the same agnostic boundary language.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-03T12:39:19Z
  TYPE: FACT
  CLAIM: Role-impact investigation shows direct patch targets are engineer and design_engineer skill docs, while platform/qa/security and user-defined engineer overlays are transitive verification lanes because they inherit engineer baseline skills.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/platform_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/qa_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/security_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/user_defined/synaptic_python_developer/SKILLS.MD:10-10
  IMPACT: Story execution should prioritize engineer/design skill patch points first, then run compatibility checks for inheriting roles.
  NEXT: decompose concrete implementation tasks for engineer baseline patching, design-engineer instruction patching, and transitive-role compatibility verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-03T12:57:55Z
  TYPE: FACT
  CLAIM: Skill implementation now includes deep, domain-agnostic contract files for `architecture_patch`, `component_patch`, and conditional `code_description_patch`, plus engineer-side artifact consumption gating as a required baseline behavior.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:28-31
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md:1-43
  - context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:33-33
  - context_compass/agent_onboarding/default/engineer/skills/patch_artifact_consumption.md:1-63
  IMPACT: The story now has a concrete skill-system implementation rather than only an investigation output.
  NEXT: walk through acceptance with user and decide whether to mark the three 2026-03-03 implementation tasks complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-04T02:05:40Z
  TYPE: FACT
  CLAIM: User accepted implementation tranche; three 2026-03-03 tasks are
    closed/moved to completed, manual patch-gate validation expectations are
    documented, and active-lane patch templates are available.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-03-03_patch_engineer_skill_docs_for_patch_framework_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-03_patch_design_engineer_skill_docs_for_patch_framework_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-03_verify_inherited_role_compatibility_after_engineer_patch_task.md:1-20
  - context_compass/system_docs/patches/active/README.md:1-25
  - context_compass/system_docs/patches/active/_template_patch_id/architecture_patch.md:1-52
  IMPACT: Framework rollout now includes policy-level gating and reusable
    template scaffolding for repeated patch lanes.
  NEXT: decide whether to close this story now or continue remaining 2026-03-02 investigation tasks first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-05T00:20:03Z
  TYPE: DECISION
  CLAIM: Story is closed after completing and archiving all linked investigation
    and implementation tasks under policy-only gating.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_architecture_patch_contract_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_component_patch_contract_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_patch_ticket_boundary_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_patch_governance_coupling_contract_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_patch_lifecycle_cleanup_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_future_state_skillset_task.md:1-20
  IMPACT: Story acceptance criteria and closure checks can be finalized.
  NEXT: close the parent epic and sync board routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Story closure complete. Patch-framework skills are implemented and documented as
policy-first contracts with active-lane templates for repeatable patch planning.
