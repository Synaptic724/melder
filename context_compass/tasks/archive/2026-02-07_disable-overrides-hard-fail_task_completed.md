Completed: 2026-02-07
Summary: Added deterministic hard-fail behavior for overrides/mutations on codegen-only runtime path.

# Task: Disable Overrides and Mutations During Codegen-Only Cutover

## Metadata
- Task ID: TASK-2026-02-07-disable-overrides-hard-fail
- Story: STORY-2026-02-07-phase12-codegen-only-cutover
- Status: done
- Owner:
- Priority: p0
- Created: 2026-02-07
- Updated: 2026-02-07

## Objective
Reject override/mutation meld calls with explicit unsupported runtime errors
until override runtime codegen is implemented.

## Scope Boundaries
- In scope:
- Runtime gating for `override_payload` and `mutation_override_payload`.
- Deterministic error messages for unsupported execution mode.
- Out of scope:
- Override codegen implementation.
- Any API redesign.

## Steps / Checklist
- [x] Add explicit runtime guard for override payloads.
- [x] Add explicit runtime guard for mutation override payloads.
- [x] Ensure error path uses `MeldExecutionError` with clear guidance.

## Deliverables
- Runtime hard-fail behavior for overrides/mutations with deterministic errors.

## Files / Paths Impacted
- `src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py`
- `src/melder/aether/conduit/meld/meld.py` (if call-site gating is required)

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py src/melder/aether/conduit/meld/meld.py`
  - `python -m pytest -q tests -k \"override and meld_runtime\"`

## Risks / Rollback Notes
- Risk: previously working override paths fail immediately.
- Mitigation: explicit error text and linked follow-up override codegen story.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
This task enforces the temporary behavior contract for the codegen-only branch:
no override/mutation runtime execution until dedicated codegen support lands.


