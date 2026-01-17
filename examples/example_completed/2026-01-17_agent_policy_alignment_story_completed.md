# Story: Codify agent policy stance and documentation standards

- Completed: 2026-01-17
- Summary: Updated agent policy stance and added doc standards plus supporting skills docs.

## Metadata
- Story ID: STORY-2026-01-17-agent-policy-alignment
- Epic: EPIC-2026-01-17-agent-policy-alignment
- Status: done
- Owner:
- Priority: p0
- Created: 2026-01-17
- Updated: 2026-01-17

## User Narrative
As a maintainer, I want the agent policy docs to enforce a team-oriented, MRP-first,
non-handwavy communication standard so the system remains coherent after context loss.

## Value / MRP Alignment
This story defines the durable core for how the agent behaves and documents the system.
It prevents shallow or inconsistent behavior that would lead to rework.

## Requirements (Functional)
- Add team/partner stance, direct technical tone, and professional baseline comparisons.
- Make recommendations conditional on real tradeoffs or explicit user requests.
- Encode the MRP definition and clearly disallow MVP (MLP allowed for UI contexts only).
- Add a `codex_todo/skills/` folder with supporting policy docs.
- Add doc quality standards to `src_architecture.md` and `src_components.md`.

## Requirements (Non-Functional)
- ASCII only; no formatting churn.
- Reference the new skills docs from AGENTS and SKILLS.

## Scope Boundaries
- In scope:
  - `codex_todo/AGENTS.MD`, `codex_todo/SKILLS.MD`
  - `codex_todo/skills/` new docs
  - `codex_todo/architecture/src_architecture.md`
  - `codex_todo/components/src_components.md`
- Out of scope:
  - Runtime code changes
  - Tests or CI updates

## Dependencies / Related Work
- `codex_todo/WORKFLOW.md`
- `codex_todo/CONTEXT_COMPACTION.md`

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-17-agent-policy-docs - Update AGENTS/SKILLS + add skills docs.
- [x] Task: TASK-2026-01-17-doc-standards-update - Add doc standards to architecture/components.

## Acceptance Criteria
- AGENTS and SKILLS reflect the new stance, tone, and MRP-only strategy.
- New skills docs exist and are referenced.
- Architecture and components docs include explicit documentation quality standards.

## Validation / Test Plan
- Not run (documentation-only).

## UX / API / Data Notes
- No runtime behavior changes.

## Risks / Mitigations
- Risk: policy duplication. Mitigation: reference skills docs instead of duplicating content.

## Open Questions
- None.

## Decision Log
- 2026-01-17: Create skills folder for policy extensions.

## Context / Handoff Summary
- Completed. Policies updated, skills docs created, and doc standards added to architecture/components.
