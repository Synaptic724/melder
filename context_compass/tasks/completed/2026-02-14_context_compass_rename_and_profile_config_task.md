# Task: Implement context_compass Rename, Core/Profile Split, and Microcycle Config

- Completed: 2026-02-14
- Summary: Renamed `codex_todo` to `context_compass`, added `core/` and
  `profiles/` packaging, added microcycle config, and finalized hard-cut
  transition with no compatibility shim.

## Metadata
- Task ID: TASK-2026-02-14-context-compass-rename-and-profile-config
- Story: STORY-2026-02-14-context-compass-core-profile-packaging
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-14
- Updated: 2026-02-14

## Objective
Apply a meaningful but simple migration from `codex_todo` to
`context_compass`, establish a reusable core/profile layout, and add a config
switch for Ticket Microcycle enforcement.

## Scope Boundaries
- In scope:
- Rename folder and update active bootstrap references.
- Add `core` docs for shared mechanics.
- Add `profiles` docs for repo-specific policy examples.
- Add config file with microcycle enable/disable controls.
- Out of scope:
- Runtime source code or test behavior changes.
- Full historical path rewrites across all archived tickets.

## Steps / Checklist
- [x] Add active board routing row for this migration.
- [x] Rename `codex_todo` directory to `context_compass`.
- [x] Add `context_compass/core` docs.
- [x] Add `context_compass/profiles` docs (general profile guidance).
- [x] Add `context_compass/config/context_compass_config.yaml`.
- [x] Update root bootstrap `agents.md` path references.
- [x] Hard-cut transition: no legacy compatibility bridge.
- [x] Validate key files and references with grep/path checks.

## Deliverables
- Renamed folder: `context_compass/`
- New docs: `context_compass/core/*`, `context_compass/profiles/*`
- New config: `context_compass/config/context_compass_config.yaml`
- Updated bootstrap: `agents.md`
- Hard-cut transition completed (no `codex_todo` shim)

## Validation
- Not run.
- Recommended checks:
  - `Test-Path context_compass`
  - `rg -n "context_compass|microcycle" agents.md context_compass`

## Risks / Rollback Notes
- Risk: external automation that still points at legacy `codex_todo` paths will fail.
- Rollback: move `context_compass` back to `codex_todo` and revert bootstrap.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Notes
- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Direct folder rename without bridge can invalidate historical
    `path:line` evidence pointers.
  EVIDENCE: `context_compass/attention_board.md:15`, `context_compass/attention_board.md:17`
  IMPACT: Re-entry grep/path routines may fail for legacy notes.
  NEXT: Add compatibility bridge under legacy path after rename.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: After folder rename, documentation still contains 1,100+ `codex_todo`
    references, so links and policy anchors are stale.
  EVIDENCE: `context_compass/attention_board.md:17`, `context_compass/README.md:1`
  IMPACT: Shared/public packaging remains inconsistent and path references break.
  NEXT: Run deterministic codemod replacing `codex_todo` path prefixes with
    `context_compass` across context_compass docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: FACT
  CLAIM: Deterministic codemod completed and rewrote stale path prefixes in 227
    documentation files under `context_compass/`.
  EVIDENCE: `context_compass/README.md:1`, `context_compass/attention_board.md:17`
  IMPACT: Link and grep consistency is restored for the renamed workspace.
  NEXT: Correct migration wording artifacts and add new core/profile/config files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User requested hard transition with no backward compatibility bridge.
  EVIDENCE: user instruction in session (2026-02-14)
  IMPACT: Remove `codex_todo` shim artifacts and rely only on `context_compass`.
  NEXT: Delete shim folder and update story/task/board wording to hard-cut mode.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: MEASURE
  CLAIM: Hard-cut migration is implemented: `context_compass/` exists with core/profile/config, root bootstrap points to new path, and `codex_todo` is absent.
  EVIDENCE: `agents.md:3`, `context_compass/config/context_compass_config.yaml:1`, `context_compass/core/ticket_microcycle.md:1`, `context_compass/profiles/default_general_profile.md:1`
  IMPACT: Workspace is now share-ready under a single canonical namespace.
  NEXT: Walk through changes with user and request acceptance for ticket closure.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-14
  TYPE: DECISION
  CLAIM: User approved closure and requested migration tickets be moved to completed.
  EVIDENCE: user instruction in session (2026-02-14)
  IMPACT: Task is closed and ready for completed-folder move.
  NEXT: Move task and linked story to completed folders and update board routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation complete, accepted, and closed.
Hard-cut transition is active (`context_compass` only), with core/profile/config
packaging and microcycle policy toggles documented.
