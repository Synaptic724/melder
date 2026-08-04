# Task: Patch Design Engineer Skill Docs For Patch Framework

Completed: 2026-03-04T02:02:54Z
Summary: Design-engineer now includes deep, agnostic patch-contract skills for
architecture, component, and conditional code-description artifacts.

## Metadata
- Task ID: TASK-2026-03-03-patch-design-engineer-skill-docs-for-patch-framework
- Story: STORY-2026-03-02-patch-framework-skill-investigation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-03-03T12:39:19Z
- Updated: 2026-03-04T02:02:54Z

## Objective
Update `design_engineer` skill documents so architecture/component patch
contracts are handled explicitly and consistently in design workflows.

## Ticket Contract
- ENTRY_GATE: skillset investigation findings identify design_engineer patch targets.
- EXECUTION_BOUNDARY: design_engineer skill-map and instruction-doc updates only.
- DEPENDENCIES: TASK-2026-03-02-investigate-future-state-skillset findings.
- EXIT_GATE: design docs include explicit patch-workflow instructions and linkage.
- FAILURE_ESCALATION: raise DECISION_REQUEST if patch instructions conflict with
  existing architecture/components instruction contracts.

## Scope Boundaries
- In scope:
  - design_engineer skill map adjustments for patch workflows;
  - instruction-doc updates for architecture_patch/component_patch usage;
  - architecture context artifact set updates for patch docs.
- Out of scope:
  - engineer baseline edits;
  - runtime implementation tasks.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: design-engineer patch-contract skill split is implemented,
  validated, and accepted for closure routing.

## Steps / Checklist
- [x] Update `agent_onboarding/default/design_engineer/SKILLS.MD` with patch-context trigger/read guidance.
- [x] Patch `design_engineer_execution.md` to include patch-contract deliverables and ticket linkage.
- [x] Patch `src_architecture_instructions.md` with patch-input/merge expectations.
- [x] Patch `src_components_instructions.md` with component patch and code-description trigger guidance.
- [x] Patch `architecture_contexts.md` artifact list to include active patch docs.
- [x] Add dedicated design patch build skill: `patch_framework_design.md`.
- [x] Run Ticket Microcycle during execution.
- [x] Document each meaningful finding in `## Notes` before continuing.

## Deliverables
- Updated design_engineer skill docs.
- Evidence-backed mapping from design workflow steps to patch artifacts.

## Files / Paths Impacted
- context_compass/agent_onboarding/default/design_engineer/SKILLS.MD
- context_compass/agent_onboarding/default/design_engineer/skills/design_engineer_execution.md
- context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md
- context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md
- context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md
- context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md
- context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md
- context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md
- context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md

## Validation
- Ran:
  - `rg -n "patch_framework_design|system_docs/patches/active|architecture_patch|component_patch|code_description_patch|patch lane" context_compass/agent_onboarding/default/design_engineer/SKILLS.MD context_compass/agent_onboarding/default/design_engineer/skills/design_engineer_execution.md context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md`

## Risks / Rollback Notes
- Risk: design instructions become overloaded and lose readability.
  Rollback: keep patch content as concise trigger-based additions.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >= `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/2026-03-02_patch_framework_skill_system.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: when patch-framework skill implementation closes.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-03-03T12:39:19Z
  TYPE: PLAN
  CLAIM: Design-engineer instruction docs currently target canonical `system_docs/*` outputs, but do not yet define explicit patch-document workflow integration.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:11-20
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:11-20
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md:8-12
  IMPACT: Without these updates, patch-framework design work lacks deterministic role guidance and can drift into ad-hoc process.
  NEXT: implement focused patch-workflow additions across the listed design_engineer files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-03T12:50:25Z
  TYPE: DECISION
  CLAIM: Execution is routed to design_engineer docs now that engineer consumption gates are in place, so the framework build contract can be made explicit at design layer.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-03-03_patch_engineer_skill_docs_for_patch_framework_task.md:118-140
  - context_compass/attention_board.md:30-30
  IMPACT: Design and implementation roles are now sequenced correctly: engineer consumes gated framework, design_engineer builds/maintains framework contracts.
  NEXT: patch design_engineer SKILLS and instruction docs with required patch-framework build and merge rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-03T12:52:06Z
  TYPE: FACT
  CLAIM: Design-engineer baseline now includes a dedicated patch-framework design skill and explicit patch-doc requirements across execution, architecture instructions, component instructions, and architecture context artifacts.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:28-28
  - context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:1-51
  - context_compass/agent_onboarding/default/design_engineer/skills/design_engineer_execution.md:11-58
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:24-109
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:24-107
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md:13-31
  IMPACT: Design role now formally builds and governs patch contracts before engineer execution, completing the required role split.
  NEXT: execute inherited-role compatibility verification task for engineer-chain consumers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-03T12:52:06Z
  TYPE: MEASURE
  CLAIM: Validation grep confirmed patch-framework design terms and paths are present across all targeted design_engineer docs.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:28-28
  - context_compass/agent_onboarding/default/design_engineer/skills/design_engineer_execution.md:11-58
  - context_compass/agent_onboarding/default/design_engineer/skills/src_architecture_instructions.md:24-109
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:24-107
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_contexts.md:13-31
  - context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:22-40
  IMPACT: Design-layer gating coverage is complete enough to proceed to inherited-role compatibility verification.
  NEXT: route active execution to TASK-2026-03-03-verify-inherited-role-compatibility-after-engineer-patch.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9
- DATETIME: 2026-03-03T12:57:55Z
  TYPE: FACT
  CLAIM: Design-engineer baseline now has explicit, decoupled contract skills for architecture, component, and conditional code-description patch authoring, with orchestration wired through `patch_framework_design`.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:28-31
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md:1-43
  - context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:5-71
  IMPACT: Framework building is now deeply specified and reusable while remaining domain-agnostic; engineer consumption can rely on deterministic artifact contracts.
  NEXT: rerun inherited-role compatibility checks for the updated engineer baseline and story/epic synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-03-04T02:02:54Z
  TYPE: DECISION
  CLAIM: Task is closed after user acceptance; design-engineer contract-skill
    implementation is complete and archived.
  EVIDENCE:
  - context_compass/agent_onboarding/default/design_engineer/SKILLS.MD:25-49
  - context_compass/agent_onboarding/default/design_engineer/skills/patch_framework_design.md:5-71
  - context_compass/agent_onboarding/default/design_engineer/skills/architecture_patch_contracts.md:1-45
  - context_compass/agent_onboarding/default/design_engineer/skills/component_patch_contracts.md:1-43
  - context_compass/agent_onboarding/default/design_engineer/skills/code_description_patch_contracts.md:1-45
  IMPACT: Patch-contract authoring is now explicit, reusable, and decoupled from
    domain implementation vocabulary.
  NEXT: keep story-level routing active for remaining framework closure steps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements design_engineer documentation changes so patch-contract
design flows are explicit, repeatable, and aligned to canonical architecture docs.
