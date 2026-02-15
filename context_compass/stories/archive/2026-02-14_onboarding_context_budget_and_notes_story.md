# Story: Harden Onboarding for Context Budget and Ticket Notes

- Completed: 2026-02-14
- Summary: Onboarding policy stack now enforces meaningful-finding
  investigate->document loops, UNKNOWN-first evidence promotion, and board-first
  routing; closure accepted.

## Metadata
- Story ID: STORY-2026-02-14-onboarding-context-budget-and-notes
- Epic: none (standalone)
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a repository maintainer, I want onboarding to enforce incremental discovery
and mandatory ticket-note logging, so that agents can resume correctly after
compaction without re-scanning large parts of the repo.

## Value / MRP Alignment
This protects the core delivery loop by making durable ticket context the
source of truth instead of fragile session memory.

## Requirements (Functional)
- Add explicit onboarding policy for context-window budgeting.
- Require ticket `## Notes` updates for each meaningful finding during discovery and implementation.
- Update ticket templates to remind agents to log findings during execution.

## Requirements (Non-Functional)
- Keep guidance short, deterministic, and enforceable.
- Avoid introducing new process branches that conflict with existing policies.

## Scope Boundaries
- In scope:
- `context_compass/AGENTS.MD` policy hardening for ticket notes + bounded discovery.
- General onboarding skill updates and ordering updates.
- `WORKFLOW.md` and ticket template updates.
- Out of scope:
- Code/runtime optimization implementation.
- Architecture/component behavioral changes.

## Dependencies / Related Work
- `context_compass/AGENTS.MD`
- `context_compass/agent_onboarding/agent/general/SKILLS.md`
- `context_compass/agent_onboarding/agent/general/skills/active_documentation.md`
- `context_compass/agent_onboarding/agent/general/skills/ticketing.md`
- `context_compass/WORKFLOW.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-onboarding-policy-ticket-note-enforcement - Add context-budget policy and note-cadence hardening across onboarding/workflow/templates.

## Acceptance Criteria
- New onboarding skill exists for bounded discovery (`context_window_budget`).
- `AGENTS.MD` and ticket/workflow skills explicitly require incremental notes during discovery.
- Epic/story/task templates include a reminder to record in-flight findings.

## Validation / Test Plan
- Documentation-only validation by reading updated policy and template files.
- Validation status reported as "Not run" for executable checks.

## UX / API / Data Notes
- No runtime/API/data changes.

## Risks / Mitigations
- Risk: duplicated policy language causes drift.
  Mitigation: reference existing `active_documentation` and `WORKFLOW.md` rules.

## Open Questions
- None. Meaningful-finding gates are now the primary cadence rule; optional
  file-count expansion guard remains in policy (`>10 files` requires confirmation).

## Decision Log
- 2026-02-14: Track onboarding hardening as standalone policy story to keep
  this work reviewable and compaction-safe.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Active ticket notes are already required by policy but not explicit
    enough about tranche-by-tranche discovery logging.
  EVIDENCE: context_compass/AGENTS.MD:436, context_compass/WORKFLOW.md:31, context_compass/agent_onboarding/agent/general/skills/active_documentation.md:10
  IMPACT: Agents can still drift into broad scans before logging durable notes.
  NEXT: Add explicit bounded-discovery and note-cadence requirements in onboarding docs and templates.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: `attention_board.md` is already canonical in compaction policy, but multiple onboarding docs still prioritize `00_overview.md`.
  EVIDENCE: context_compass/CONTEXT_COMPACTION.md:8, context_compass/agent_onboarding/agent/general/skills/context_protocol.md:12, context_compass/agent_onboarding/agent/general/behavioral_guidelines/agent_lifecycle_and_heartbeat.md:12
  IMPACT: Re-entry behavior is not deterministic across documentation surfaces.
  NEXT: Normalize all onboarding references to board-first routing and ticket-first detail storage.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Microcycle enforcement will be meaningful-finding driven, not LOC-driven, with hard stop gates between investigation tranches.
  EVIDENCE: context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:13, context_compass/WORKFLOW.md:31
  IMPACT: Slower but higher-fidelity execution that is resilient to compaction and large policy payloads.
  NEXT: Patch AGENTS/workflow/skills/templates to require `Investigate -> Document` loops for each meaningful finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Story deliverables were implemented across policy/docs/templates, including board-first routing alignment and UNKNOWN-first + note-score enforcement.
  EVIDENCE: context_compass/AGENTS.MD:437, context_compass/WORKFLOW.md:72, context_compass/agent_onboarding/agent/general/skills/context_window_budget.md:1, context_compass/agent_onboarding/agent/engineer/skills/engineer_execution.md:22, context_compass/templates/story_template.md:34
  IMPACT: Onboarding and execution workflows now encode compaction-safe memory discipline as hard requirements.
  NEXT: Review the outcome with the user and confirm acceptance criteria.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Cross-doc keyword validation confirms consistent anchor presence for microcycle, unknown-default stance, note scoring, and board-first routing.
  EVIDENCE: context_compass/AGENTS.MD:435, context_compass/WORKFLOW.md:73, context_compass/agent_onboarding/agent/general/skills/ticketing.md:40, context_compass/templates/task_template.md:22
  IMPACT: Story acceptance can be evaluated quickly with repeatable grep checks instead of broad re-reading.
  NEXT: Walk user through changed files and request acceptance confirmation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story implementation is complete, done, and user-accepted.
Policy stack now enforces meaningful-finding microcycles, UNKNOWN-first claims,
board-first routing, and richer ticket note schemas for compaction-safe reentry.
