# Task: Enforce Ticket Notes and Context Budget in Onboarding Policy

- Completed: 2026-02-14
- Summary: Hardened onboarding/workflow/templates with strict microcycle,
  UNKNOWN-first, and board-first evidence-routing policy; user accepted closure.

## Metadata
- Task ID: TASK-2026-02-14-onboarding-policy-ticket-note-enforcement
- Story: STORY-2026-02-14-onboarding-context-budget-and-notes
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Harden onboarding and workflow policy so agents must record findings in active
tickets while working and must use meaningful-finding discovery gates to reduce
compaction risk.

## Scope Boundaries
- In scope:
- Add and wire `context_window_budget` onboarding skill.
- Update policy docs (`AGENTS.MD`, skills, `WORKFLOW.md`) with explicit
  note-cadence + bounded-discovery rules.
- Update ticket templates with execution-note and context-budget reminders.
- Update `attention_board.md` for active routing.
- Out of scope:
- Runtime code changes.
- Test or benchmark implementation.

## Steps / Checklist
- [x] Add `context_window_budget.md` skill and include it in general onboarding read order.
- [x] Update `AGENTS.MD` with explicit bounded discovery + in-flight note requirements.
- [x] Update `ticketing.md`, `active_documentation.md`, and `WORKFLOW.md` with meaningful-finding note gates and UNKNOWN-first promotion rules.
- [x] Update epic/story/task templates with note-cadence reminders.
- [x] Update `attention_board.md` with active policy-hardening entry.
- [x] Reflect completion state in this task and linked story notes.

## Deliverables
- New onboarding skill: `context_window_budget`.
- Updated onboarding/workflow policy docs.
- Updated ticket templates enforcing in-flight note logging.

## Files / Paths Impacted
- `context_compass/agent_onboarding/agent/general/skills/context_window_budget.md`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/skills/ticketing.md`
- `context_compass/agent_onboarding/agent/general/skills/active_documentation.md`
- `context_compass/agent_onboarding/agent/general/skills/reactive_documentation.md`
- `context_compass/agent_onboarding/agent/general/skills/memory_management.md`
- `context_compass/agent_onboarding/agent/general/skills/compaction_requirements.md`
- `context_compass/agent_onboarding/agent/general/skills/context_protocol.md`
- `context_compass/agent_onboarding/agent/general/skills/system_orientation.md`
- `context_compass/agent_onboarding/agent/general/skills/agent_lifecycle.md`
- `context_compass/agent_onboarding/agent/general/skills/self_certification.md`
- `context_compass/agent_onboarding/agent/general/policies/policy_router.md`
- `context_compass/agent_onboarding/agent/engineer/skills/engineer_execution.md`
- `context_compass/agent_onboarding/agent/general/behavioral_guidelines/onboarding_summary.md`
- `context_compass/agent_onboarding/agent/general/behavioral_guidelines/agent_lifecycle_and_heartbeat.md`
- `context_compass/agent_onboarding/agent/general/behavioral_guidelines/work_intake_and_execution.md`
- `context_compass/agent_onboarding/agent/general/behavioral_guidelines/task_execution_and_validation.md`
- `context_compass/agent_onboarding/agent/engineer/examples/artifact_workflow.md`
- `context_compass/WORKFLOW.md`
- `context_compass/SKILLS.MD`
- `context_compass/CONTEXT_COMPACTION.md`
- `context_compass/README.md`
- `context_compass/00_overview.md`
- `context_compass/templates/epic_template.md`
- `context_compass/templates/story_template.md`
- `context_compass/templates/task_template.md`
- `context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "Ticket Microcycle|SCORE_0_TO_10|UNKNOWN is the default|attention_board.md" context_compass`

## Risks / Rollback Notes
- Risk: policy duplication across multiple docs can drift.
- Rollback: revert to prior wording and keep only one canonical rule source.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Policy hardening will be implemented as documentation-first updates
    spanning onboarding skills, workflow, and templates.
  EVIDENCE: context_compass/AGENTS.MD:431, context_compass/WORKFLOW.md:31, context_compass/templates/task_template.md:44
  IMPACT: Durable ticket notes become explicit execution gates, reducing context loss after compaction.
  NEXT: Patch all listed policy/template files and update attention board routing.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Current policy stack already requires notes, but cadence language is still soft in key workflow files.
  EVIDENCE: context_compass/WORKFLOW.md:31, context_compass/agent_onboarding/agent/general/skills/ticketing.md:40, context_compass/agent_onboarding/agent/general/skills/active_documentation.md:11
  IMPACT: Agents can still batch findings and drift into broad scans before writing durable state.
  NEXT: Convert cadence wording into hard-stop gates tied to meaningful findings.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Re-entry guidance is inconsistent: several onboarding/behavioral docs still route through `00_overview.md` instead of board-first ticket routing.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/context_protocol.md:12, context_compass/agent_onboarding/agent/general/skills/agent_lifecycle.md:7, context_compass/agent_onboarding/agent/engineer/skills/engineer_execution.md:30, context_compass/agent_onboarding/agent/general/behavioral_guidelines/onboarding_summary.md:23
  IMPACT: Blank-slate sessions can reopen stale summary context instead of canonical `attention_board` + ticket state.
  NEXT: Rewrite these references to make `attention_board.md` + active tickets canonical and `00_overview.md` optional.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Execution stance will default to UNKNOWN and require evidence promotion to FACT in both policy and note taxonomy.
  EVIDENCE: context_compass/AGENTS.MD:327, context_compass/WORKFLOW.md:72
  IMPACT: Prevents speculative claims from entering durable notes and implementation decisions.
  NEXT: Add explicit UNKNOWN-first wording to workflow/skills/templates and require evidence-backed promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Policy hardening patch landed across AGENTS/workflow/onboarding skills/behavioral guides/templates, including microcycle gates, UNKNOWN-first default, score-based note quality, and board-first routing.
  EVIDENCE: context_compass/AGENTS.MD:437, context_compass/WORKFLOW.md:31, context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:1, context_compass/agent_onboarding/agent/general/skills/ticketing.md:40, context_compass/templates/task_template.md:22, context_compass/agent_onboarding/agent/general/skills/context_protocol.md:12
  IMPACT: Future sessions can resume in sniper mode from ticket evidence instead of broad repo rereads.
  NEXT: Walk through the completed documentation changes with the user and confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Validation grep confirms new microcycle/score/UNKNOWN/board-first anchors are discoverable across the policy stack.
  EVIDENCE: context_compass/AGENTS.MD:435, context_compass/WORKFLOW.md:72, context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:13, context_compass/templates/task_template.md:22
  IMPACT: Future re-entry can quickly locate enforcement anchors using narrow keyword searches.
  NEXT: Present the patch summary to user for acceptance confirmation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Implementation complete; task is done and user-accepted.
Primary outcomes: strict Ticket Microcycle, meaningful-finding note gates,
UNKNOWN-first promotion, board-first routing, and updated template defaults.
