# Story: Rename codex_todo to context_compass with Core/Profile Packaging

- Completed: 2026-02-14
- Summary: Completed hard-cut rename to `context_compass`, introduced
  `core/` + `profiles/` packaging, and added configurable ticket microcycle policy.

## Metadata
- Story ID: STORY-2026-02-14-context-compass-core-profile-packaging
- Epic: none (standalone)
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## User Narrative
As a maintainer, I want the planning/onboarding system to be named
`context_compass` and split into reusable `core` and `profile` layers, so it
can be shared publicly with less repo-specific coupling.

## Value / MRP Alignment
This creates a reusable documentation/process product while keeping local
execution safety.

## Requirements (Functional)
- Rename top-level folder `codex_todo` to `context_compass`.
- Add `core` and `profiles` sections that separate generic mechanics from
  repo-specific policy.
- Add a config artifact that toggles Ticket Microcycle enforcement on/off.
- Use hard transition with no backward compatibility bridge.

## Requirements (Non-Functional)
- Keep implementation simple and reviewable.
- Avoid large semantic rewrites of historical tickets.

## Scope Boundaries
- In scope:
- Documentation/system-structure changes only.
- Root bootstrap updates to point at `context_compass`.
- Out of scope:
- Runtime source code changes in `src/`.
- Test behavior changes in `tests/`.

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-02-14-context-compass-rename-and-profile-config

## Acceptance Criteria
- `context_compass/` exists with migrated content.
- Core/profile structure exists with clear usage docs.
- Config file exists with microcycle on/off switches.
- Root bootstrap file references `context_compass` paths.
- `codex_todo/` compatibility shim does not exist.

## Validation / Test Plan
- Not run.
- Validate by path checks and grep for key anchors.

## Risks / Mitigations
- Risk: stale `codex_todo` path references inside historical docs.
  Mitigation: normalize active policy references and document hard-cut transition.

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: User requested direct rename to `context_compass`, core/profile split,
    and microcycle configurability.
  EVIDENCE: user request in session (2026-02-14)
  IMPACT: Requires both filesystem migration and policy-surface updates.
  NEXT: Create implementation task and execute rename with explicit transition mode.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: Transition mode is hard-cut (no `codex_todo` compatibility bridge).
  EVIDENCE: user instruction in session (2026-02-14)
  IMPACT: Final structure stays simple and avoids dual-path maintenance.
  NEXT: Keep only `context_compass` as canonical path in onboarding/bootstrap docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User approved closure and requested story/task move to completed folders.
  EVIDENCE: user instruction in session (2026-02-14)
  IMPACT: Story is closed and ready for completed-folder move.
  NEXT: Move story and linked task to completed folders and update board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story implementation complete, accepted, and closed.
Workspace now uses `context_compass` with core/profile/config packaging and a
configurable Ticket Microcycle policy.
