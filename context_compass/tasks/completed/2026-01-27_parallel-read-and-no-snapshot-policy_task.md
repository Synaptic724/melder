# Task: Add anti-snapshotting policy + parallel onboarding read rule

- Completed: 2026-01-27
- Summary: Added an anti-snapshotting rule and allowed parallel onboarding reads while keeping certification completion requirements intact.

## Metadata
- Task ID: TASK-2026-01-27-onboarding-parallel-read-and-no-snapshot
- Story: N/A
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-01-27
- Updated: 2026-01-27

## Objective
Add a policy rule that forbids snapshotting owned structures unless required, and update onboarding guidance to allow parallel reading of required skills while still requiring completion before certification.

## Scope Boundaries
- In scope:
  - Update banned pattern guidance to forbid unnecessary snapshotting of owned structures.
  - Clarify onboarding read order to allow parallel reading while requiring completion before certification.
- Out of scope:
  - Any runtime code changes (meld/runtime/etc.).
  - Test changes.

## Steps / Checklist
- [x] Add anti-snapshotting rule to banned patterns.
- [x] Update onboarding read-order guidance to allow parallel reading.
- [x] Review for conflicts with certification gate language and adjust if needed.
- [x] Update task handoff summary.

## Deliverables
- Updated policy docs reflecting the anti-snapshotting rule and parallel read allowance.

## Files / Paths Impacted
- context_compass/agent_onboarding/agent/general/skills/python/banned_patterns.md
- context_compass/agent_onboarding/agent/general/SKILLS.md
- context_compass/agent_onboarding/agent/general/skills/self_certification.md

## Validation
- Not run.
- Recommended commands:
  - N/A (documentation-only change)

## Risks / Rollback Notes
- Risk: conflicting onboarding rules if read-order language is not aligned.
- Rollback: revert the documentation edits.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Edits applied to banned patterns and onboarding guidance. User confirmed acceptance; ready for archive.
