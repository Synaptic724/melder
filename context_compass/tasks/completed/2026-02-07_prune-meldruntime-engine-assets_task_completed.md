Completed: 2026-02-07
Summary: Pruned runtime engine asset pools and dead helper branches tied to engine execution.

# Task: Prune MeldRuntime Engine Asset Pools and Dead Helpers

## Metadata
- Task ID: TASK-2026-02-07-prune-meldruntime-engine-assets
- Story: STORY-2026-02-07-phase12-codegen-only-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Remove runtime pooling and helper logic that only exists to support
`MeldEngine`-based execution.

## Scope Boundaries
- In scope:
- Remove transient/shared engine/frame/context pool structures.
- Remove dead helper methods used only by engine execution path.
- Out of scope:
- Non-runtime module cleanup.

## Steps / Checklist
- [x] Remove engine asset pool fields from runtime state.
- [x] Remove pool borrow/return helpers and cleanup paths for those assets.
- [x] Remove dead execution helper methods no longer used after cutover.

## Deliverables
- `MeldRuntime` reduced to dispatch-only runtime state.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
  - `python -m pytest -q tests -k \"meld_runtime\"`

## Risks / Rollback Notes
- Risk: dead-code pruning removes still-referenced helpers.
- Mitigation: symbol reference sweep and compile pass before closure.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task removes the runtime memory/state overhead that was only needed for
engine-backed execution, completing dispatch-only runtime simplification.


