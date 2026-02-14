Completed: 2026-02-14
Summary: Reduced override-lane cache-hit overhead by shape-first specialization lookup, deferring grouped target collection/compile to cache misses with no semantic changes.

# Task: Optimize Meld Override Shape Hotpath

## Metadata
- Task ID: TASK-2026-02-13-meld-override-shape-hotpath
- Story: STORY-2026-02-13-optimize-meld-paths
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-02-13
- Updated: 2026-02-14

## Objective
Reduce targeted-override overhead in `CreationContext` shape collection and
specialization lookup while preserving override correctness.

## Scope Boundaries
- In scope:
- Override payload normalization and socket-shape collection path.
- Specialization cache lookup/compile path for override executors.
- Tests for targeted/root-args override behavior.
- Out of scope:
- Non-override no-hooks/no-overrides lane changes.
- New override semantics.

## Steps / Checklist
- [x] Inspect current override shape-building flow for avoidable allocations/sorting.
- [x] Define optimized shape-key build and map-grouping path.
- [x] Implement optimization with clear invariants and comments.
- [x] Add/adjust tests for override behavior and cache reuse.

## Deliverables
- Faster targeted override specialization path in `CreationContext`.
- Regression-safe tests for override routes.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`
- `tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
- `tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`

## Validation
- Run:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py`
    - Result: `13 passed`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py`
    - Result: `18 passed`
  - `python -m pytest -q tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`
    - Result: `7 passed`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/meld_runtime/test_meld_runtime.py tests/unit/melder/aether/conduit/meld/meld_engine/test_meld_engine_2.py tests/integration/melder/spellbook/test_spellbook_integration_overrides.py`
    - Result: `38 passed`

## Risks / Rollback Notes
- Risk: shape-key instability causing cache misses or incorrect executor reuse.
- Rollback: restore current `_collect_override_targets_and_socket_shape` path.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Implemented a cache-hit short-circuit for override specialization lookup in
`CreationContext._execute_with_overrides` while preserving shape-key and compile
contracts:
- Added shape-only helper `_collect_override_socket_shape(...)` and used it to
  build specialization keys before grouped target collection.
- Added cache-first lookup on `_override_specialization_cache`; grouped target
  collection and compile now run only on cache miss.
- Preserved existing `_collect_override_targets_and_socket_shape(...)` API and
  semantics.
- Added tests covering shape-helper parity and cache-hit bypass behavior.
User confirmed acceptance and directed progression to the next ticket.
