# Task: Provide read-only snapshots during in-flight transactions (deferred)

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-read-only-snapshots
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-18
- Updated: 2026-01-20

## Objective
Expose read-only snapshot views of Spellbook/Conduit state so agents can read a
consistent graph while transactions are in-flight. This is **not in MRP** and
is deferred until after admission/orchestration scaffolding is stable.

## Scope Boundaries
- In scope:
  - Snapshot API for Spellbook and Conduit state (local + contracted maps).
  - Explicit "snapshot version" identifier for observability.
  - Safe read-only access (no mutation).
- Out of scope:
  - Multi-frame snapshots (single frame only).
  - Conflict/embargo logic.
  - MRP deliverables for change-control admission.

## Steps / Checklist
- [x] Define snapshot schema (spells, lookup keys, contracted maps).
- [x] Add snapshot API on Spellbook / Conduit (read-only).
- [x] Ensure snapshots are stable across in-flight transactions.
- [x] Add basic tests for snapshot consistency.

## Deliverables
- Read-only snapshot API + tests.

## Files / Paths Impacted
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/utilities/interfaces/interfaces.py`
- `tests/unit/melder/spellbook/`

## Validation
- Not run.
- Recommended commands:
  - `pytest tests/unit/melder/spellbook/`

## Risks / Rollback Notes
- Risk: Snapshot surface becomes a de facto public API. Mitigation: document
  read-only contract and keep schema minimal.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Implemented read-only snapshots for Spellbook and Conduit.
  - `Spellbook.snapshot_state()` returns detached copies of local + contracted
    spell maps, lookup maps, and version caches, plus `snapshot_id` and
    `captured_at_ms`.
  - `Conduit.snapshot_state()` returns conduit metadata and embeds the
    Spellbook snapshot without holding the conduit lock while copying the
    spellbook state.
  - Added unit tests to verify snapshot detachment for both Spellbook and Conduit.
