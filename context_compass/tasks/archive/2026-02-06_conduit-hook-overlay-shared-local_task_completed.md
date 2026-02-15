- Completed: 2026-02-07
- Summary: Conduit hook overlay behavior was implemented, validated, and user-accepted; archived per workflow.

# Task: Conduit shared and local hook overlay model

## Metadata
- Task ID: TASK-2026-02-06-conduit-hook-overlay-shared-local
- Story: N/A
- Status: done
- Owner:
- Priority: p1
- Created: 2026-02-06
- Updated: 2026-02-06

## Objective
Implement conduit hook behavior where shared lineage hooks stay in the shared
configuration-backed map, local hooks are stored separately per conduit, and
execution order is shared hooks first then local hooks.

## Scope Boundaries
- In scope:
- Add separate local hook storage on Conduit.
- Keep shared hook map reference intact for non-local registration.
- Execute shared then local hook chains.
- Wire Meld hook map from the composed effective map.
- Update conduit hook tests for the new semantics.
- Out of scope:
- Changes to `meld.py`.
- Configuration hook registry redesign.

## Steps / Checklist
- [x] Add `_local_conduit_hooks` on Conduit.
- [x] Write local registrations into `_local_conduit_hooks`.
- [x] Keep shared registrations in `_conduit_hooks`.
- [x] Execute hooks with shared-first then local ordering.
- [x] Update tests for local overlay semantics.
- [x] Run targeted tests.

## Deliverables
- `src/melder/aether/conduit/conduit.py`
- `tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py`

## Files / Paths Impacted
- `src/melder/aether/conduit/conduit.py`
- `tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py`

## Validation
- `.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\test_conduit_configuration_and_hooks.py`
  - Result: `23 passed`
- `.venv_new\\Scripts\\python.exe -m pytest -q tests\\component\\melder\\aether\\conduit\\test_conduit_component_meld_gating.py`
  - Result: `4 passed`

## Risks / Rollback Notes
- Risk: Callers expecting local hook registration to detach shared maps now see
  overlay semantics instead.
- Rollback: Revert the two touched files listed above.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Conduit now maintains shared lineage hooks and local hooks separately.
Local registration no longer replaces shared hook maps. Effective hook order is
shared first, local second.
