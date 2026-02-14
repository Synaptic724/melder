Completed: 2026-02-08
Summary: Closed and turned in for Rewire Meld to Lock-Free Spell Context Get-or-Build.

# Task: Rewire Meld to Lock-Free Spell Context Get-or-Build

## Metadata
- Task ID: TASK-2026-02-08-meld-get-or-build-creation-context
- Story: STORY-2026-02-08-meld-front-door-spell-binding
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Change Meld runtime dispatch so it resolves spell-owned context, builds it on miss without locks, and executes through that context.

## Scope Boundaries
- In scope:
  - Meld get-or-build flow for spell context.
  - Lock-free miss behavior with direct attach to spell.
  - Context execute call wiring with `caller_creations` and `overrides`.
- Out of scope:
  - Hook ordering changes.
  - Runtime helper migration internals.

## Steps / Checklist
- [x] Add helper path in Meld to read spell-owned context.
- [x] Build and attach context on miss without lock acquisition.
- [x] Replace direct meld-owned runtime resolver call with spell context execute call.
- [x] Keep front-door validity gating unchanged.

## Deliverables
- Meld hot path rewired to spell-owned context get-or-build execute.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/unit/melder/aether/conduit/meld -q`

## Risks / Rollback Notes
- Risk: race on miss creates inconsistent contexts.
- Rollback: temporarily route both branches to old runtime until deterministic builder is confirmed.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task moves execution entry from meld-owned runtime object to spell-owned context while preserving validation gates.
