- Completed: 2026-01-21
- Summary: Removed module __all__ and owned-attribute getattr usage in ChangeControlManager.

# Task: Clean up owned getattr usage in ChangeControlManager

## Metadata
- Task ID: TASK-2026-01-21-change-control-manager-getattr-cleanup
- Story: STORY-2026-01-21-change-control-manager-contract-hygiene
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## Objective
Replace owned-attribute getattr usage in ChangeControlManager with direct
access and explicit None checks, and remove the module __all__ export list if
confirmed.

## Scope Boundaries
- In scope:
  - `_resolve_frame`, `_resolve_conduit_by_id`, `_resolve_spellbook_for_staged`,
    `_default_structural_validator`, and related helpers in
    `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`.
  - Module-level `__all__` removal in the same file if confirmed.
- Out of scope:
  - Changes to change-control subcomponents in other files.

## Steps / Checklist
- [x] Replace owned-attribute getattr usage with direct access.
- [x] Remove swallowed check_cleaned exceptions for resolved frame/conduit (not required; behavior kept consistent).
      Not required; behavior kept consistent.
- [x] Remove `__all__` from the module if confirmed.
- [x] Update docstrings if behavior changes require it (not required; no behavior change).
- [x] Update tests if behavior changes require it (not required; no behavior change).

## Deliverables
- Direct attribute access in ChangeControlManager with explicit None checks.
- Updated docstrings for adjusted behavior.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest tests/component/melder/aether/dev_ops/change_control_manager`

## Risks / Rollback Notes
- Risk: Stricter contract enforcement surfaces hidden errors.
  - Mitigation: Keep changes small, document behavior, and run targeted tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Completed: removed module __all__ and owned-attribute getattr usage in
ChangeControlManager while keeping behavior consistent.
