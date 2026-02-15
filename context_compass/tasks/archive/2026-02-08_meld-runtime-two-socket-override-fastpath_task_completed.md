Completed: 2026-02-08
Summary: Added deterministic two-socket no-sort fast path for runtime override target/shape collection with output and sort-bypass tests.

# Task: MeldRuntime Two-Socket Override Shape Fast Path

## Metadata
- Task ID: TASK-2026-02-08-meld-runtime-two-socket-override-fastpath
- Story: STORY-2026-02-08-codegen-meld-runtime-optimization-wave
- Status: done
- Owner:
- Priority: p2
- Created: 2026-02-08
- Updated: 2026-02-08

## Objective
Reduce override-shape collection overhead for two-socket payloads by applying a
manual ordering fast path instead of general sort allocation.

## Scope Boundaries
- In scope:
- Add a `len == 2` fast path in `_collect_override_targets_and_socket_shape`.
- Preserve deterministic grouping and socket-shape ordering semantics.
- Add tests for deterministic two-entry output and sort-bypass behavior.
- Run targeted + broad regressions.
- Out of scope:
- Any changes to shape-key structure or override semantics.

## Steps / Checklist
- [x] Add two-socket ordering fast path in runtime collection helper.
- [x] Add deterministic + sort-bypass tests for two-socket payloads.
- [x] Run targeted + broad regressions.

## Deliverables
- Reduced overhead for two-target override payloads.
- Regression coverage proving deterministic and no-sort two-socket path behavior.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`

## Validation
- Ran:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`
- Result:
  - MeldRuntime suite passed (`51 passed`).
  - Extended regression suite passed (`189 passed`).
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py`
  - `python -m pytest -q tests/unit/melder/aether/conduit/meld/test_meld.py tests/unit/melder/aether/conduit/meld/meld_context/test_meld_context.py tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py`

## Risks / Rollback Notes
- Risk: manual ordering predicate mismatch could break deterministic order guarantees.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This pass extends runtime override target/shape fast-path handling from single-
socket payloads to two-socket payloads while preserving deterministic ordering.

