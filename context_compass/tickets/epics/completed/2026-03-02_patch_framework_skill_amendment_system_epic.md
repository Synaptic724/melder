# Epic: Patch Framework Skill Amendment System

Completed: 2026-03-05T00:20:03Z
Summary: Domain-agnostic patch-framework skills are implemented, investigation
lanes are closed, and policy-only patch governance is established.

## Metadata
- Epic ID: EPIC-2026-03-02-patch-framework-skill-amendment-system
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-03T01:03:46Z
- Updated: 2026-03-05T00:20:03Z
- Target Window: 2026-Q1
- Related Program/Initiative: Future-state architecture and component patching

## Problem / Opportunity
Current documentation captures current-state architecture and components well, but
we do not yet have a reusable, domain-agnostic amendment system for future-state
changes. That gap causes planning duplication, weak handoff quality, and drift
between design intent and ticket execution.

## MRP Alignment (Most Reasonable Product)
This epic defines the smallest coherent patch-planning system:
- temporary architecture/component patch docs for design deltas;
- strict boundary between patch docs and execution tickets;
- explicit patch-governance coupling contract for ingress and custody flows;
- closure lifecycle that merges durable deltas into canonical docs and removes
  temporary patch docs.

## Ticket Contract
- ENTRY_GATE: active routing row exists for investigation story and artifact is linked.
- EXECUTION_BOUNDARY: investigate, define, and ticketize the patch framework only.
- DEPENDENCIES: baseline role-chain skills and framework artifact references.
- EXIT_GATE: framework contracts are documented, accepted, and decomposed into
  implementable follow-on work.
- FAILURE_ESCALATION: raise DECISION_REQUEST on unresolved boundary conflicts.

## Goals (Outcomes)
- Define `architecture_patch` and `component_patch` contracts as temporary
  first-class amendment artifacts.
- Define conditional `code_description_patch` trigger criteria.
- Define ticket-vs-patch responsibility split with anti-duplication rules.
- Define governance coupling boundaries in domain-agnostic terms.
- Define closure lifecycle from patch docs to canonical docs.

## Non-Goals (Explicit Exclusions)
- Implementing runtime features for any domain subsystem.
- Embedding project-specific runtime semantics inside reusable skill contracts.
- Rewriting canonical system docs in this investigation tranche.

## Scope Boundaries
- In scope:
  - investigation artifacts, epic/story/task planning, and routing integration;
  - framework definition for architecture/component patching and lifecycle.
- Out of scope:
  - code-level runtime implementation;
  - ticket archival/closure actions unrelated to this active epic.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: implementation and closure criteria are complete and user
  approved final closeout.

## Success Metrics
- One framework artifact defines patch taxonomy and closure rules.
- One investigation story and six tasks exist with non-overlapping scopes.
- Attention board routes to the active skill-focused investigation task.
- Artifact board links framework artifact to active story.

## Requirements (Functional + Non-Functional)
- Functional: define patch artifact taxonomy and lifecycle.
- Functional: define investigation tracks as executable tasks.
- Functional: define agnostic governance coupling boundaries.
- Non-functional: avoid ticket/artifact duplication via explicit contracts.
- Non-functional: preserve evidence-first notes and deterministic board routing.

## Constraints / Assumptions
- Existing canonical architecture/component docs remain current-state source of truth.
- Patch docs are temporary and removed after canonical merge.
- Reusable skills must remain domain-agnostic and portable.

## Dependencies / External References
- context_compass/agent_onboarding/default/general/SKILLS.MD
- context_compass/agent_onboarding/default/engineer/SKILLS.MD
- context_compass/agent_onboarding/default/design_engineer/SKILLS.MD
- artifacts/2026-03-02_patch_framework_skill_system.md

## Milestones (Track Progress)
- [x] Milestone 1: investigation framework finalized with explicit boundaries.
- [x] Milestone 2: follow-on implementation planning created for skill rollout.

## Stories (Required to Complete)
- [x] Story: STORY-2026-03-02-patch-framework-skill-investigation - investigate
      and finalize framework and skill contracts.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: complete STORY-2026-03-02-patch-framework-skill-investigation.
- [x] Task: verify lifecycle closure rule (merge then delete temporary patch docs).
- [x] Task: verify Ticket Microcycle enforcement across active lane tickets.

## Acceptance Criteria (Epic Done)
- Investigation story and all linked tasks are accepted by user.
- Patch taxonomy and ticket-boundary contracts are explicit and non-overlapping.
- Framework language remains domain-agnostic with no project-tight coupling.
- Board and artifact links remain synchronized and resumable.

## Risks / Mitigations
- Risk: process overhead from extra patch docs.
  Mitigation: strict contract that tickets own execution and patch docs own deltas.
- Risk: skill definitions drift back into domain-coupled language.
  Mitigation: explicit agnostic boundary checks in task deliverables.

## Applicable Anti-Patterns
- [x] No epic-state transition without story-level evidence.
- [x] No closure while required stories are incomplete or unaccepted.
- [x] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Validate required tickets/artifacts exist and are linked consistently.
- Validate board routing and artifact-board associations are coherent.
- Validate each task maps to one investigation stream.

## Rollout / Adoption Plan
- Run investigation story to finalize framework and skill inventory.
- Create follow-on implementation tasks for concrete skill creation and validation.
- Apply framework to future-state patch sets after user acceptance.

## Open Questions
- Should `code_description_patch` be mandatory for all changed components or
  only high-complexity control-flow/state transitions?
- Should patch lifecycle cleanup remain manual policy or become scripted tooling?

## Decision Log
- 2026-03-03: use temporary patch docs for design deltas and tickets for execution state.
- 2026-03-03: keep skill contracts domain-agnostic and reusable across projects.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-03-02_patch_framework_skill_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: after framework investigation closes and canonical docs are updated.

## Notes
- DATETIME: 2026-03-03T12:30:00Z
  TYPE: DECISION
  CLAIM: Epic has been renamed and rewritten to remove legacy domain-specific framing and enforce agnostic patch-skill boundaries.
  EVIDENCE:
  - context_compass/tickets/epics/2026-03-02_patch_framework_skill_amendment_system_epic.md:1-22
  - context_compass/tickets/stories/2026-03-02_patch_framework_skill_investigation_story.md:1-35
  IMPACT: This epic now tracks portable framework/skill work rather than domain-coupled architecture direction.
  NEXT: align linked story/tasks text with the same agnostic contract language.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-03T12:39:19Z
  TYPE: FACT
  CLAIM: Impact analysis confirms the primary implementation surface is engineer/design_engineer skill files, with inherited-role blast radius requiring verification across platform, qa, security, and user-defined engineer overlays.
  EVIDENCE:
  - context_compass/agent_onboarding/default/engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/platform_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/qa_engineer/SKILLS.MD:9-9
  - context_compass/agent_onboarding/default/security_engineer/SKILLS.MD:9-9
  - context_compass/config/context_compass_config.yaml:4-4
  IMPACT: Epic rollout needs explicit sequencing: patch engineer/design docs first, then run inherited-role compatibility checks before closure.
  NEXT: add implementation tasks for engineer/doc patching, design instruction patching, and transitive-role verification under the active story.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-03T12:57:55Z
  TYPE: FACT
  CLAIM: Implementation tranche now delivers deep, domain-agnostic patch skill contracts and hard engineer consumption gates, with transitive-role compatibility revalidated after the deeper split.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md:1-43
  - context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/engineer/skills/patch_artifact_consumption.md:1-63
  - context_compass/tickets/tasks/completed/2026-03-03_verify_inherited_role_compatibility_after_engineer_patch_task.md:1-40
  IMPACT: Epic goals are now backed by implemented role skills, not just planned contracts.
  NEXT: complete user walkthrough and confirm closure criteria for the story and implementation tasks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-04T02:05:40Z
  TYPE: FACT
  CLAIM: Post-acceptance rollout includes closure of all three 2026-03-03
    implementation tasks and active-lane patch templates under policy-only
    patch governance.
  EVIDENCE:
  - context_compass/tickets/tasks/completed/2026-03-03_patch_engineer_skill_docs_for_patch_framework_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-03_patch_design_engineer_skill_docs_for_patch_framework_task.md:1-20
  - context_compass/tickets/tasks/completed/2026-03-03_verify_inherited_role_compatibility_after_engineer_patch_task.md:1-20
  - context_compass/system_docs/patches/active/_template_patch_id/architecture_patch.md:1-52
  IMPACT: Epic implementation lane now has governance docs and practical
    template scaffolding for repeated patch lanes.
  NEXT: decide final closure path for remaining investigation tasks under this epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-05T00:20:03Z
  TYPE: DECISION
  CLAIM: Epic is closed after story/task completion and board-sync preparation.
  EVIDENCE:
  - context_compass/tickets/stories/completed/2026-03-02_patch_framework_skill_investigation_story.md:1-25
  - context_compass/tickets/tasks/completed/2026-03-02_investigate_future_state_skillset_task.md:1-25
  - context_compass/attention_board.md:25-60
  IMPACT: Patch-framework skill amendment lane is complete and can transition to
    archived program state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic closure complete. Domain-agnostic patch-framework skills and policy
contracts are now established for design and engineer roles.
