- Completed: 2026-01-21
- Summary: Improved ChangeControlManager contract hygiene by removing owned getattr usage.

# Story: Remove defensive introspection in ChangeControlManager

## Metadata
- Story ID: STORY-2026-01-21-change-control-manager-contract-hygiene
- Epic: EPIC-2026-01-21-change-control-manager-contract-hygiene
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21

## User Narrative
As a maintainer, I want ChangeControlManager to enforce owned-attribute
contracts without defensive introspection so that contract violations surface
immediately and are not silently ignored.

## Value / MRP Alignment
This keeps the change-control control plane trustworthy and aligned with the
repo's contract-first design philosophy.

## Requirements (Functional)
- Replace owned-attribute getattr usage with direct access in
  ChangeControlManager.
- Do not swallow check_cleaned exceptions in frame/conduit/spellbook resolution.
- Remove `__all__` from the module if confirmed.

## Requirements (Non-Functional)
- Keep scope limited to the single module.
- Update docstrings for any changed behavior.

## Scope Boundaries
- In scope:
  - `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- Out of scope:
  - Refactors or API changes in other change-control modules.

## Dependencies / Related Work
- Task: TASK-2026-01-21-change-control-manager-getattr-cleanup

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-21-change-control-manager-getattr-cleanup - Replace
  owned-attribute getattr usage and remove module __all__.

## Acceptance Criteria
- No owned-attribute getattr usage remains in ChangeControlManager.
- Resolution helpers use direct access and explicit None checks.
- Docstrings reflect any behavior changes (e.g., cleaned-state handling).

## Validation / Test Plan
- Not run by agent.
- User runs targeted pytest if needed.

## UX / API / Data Notes
- No user-facing API changes expected beyond stricter contract enforcement.

## Risks / Mitigations
- Risk: Stricter behavior may surface errors in callers.
  - Mitigation: Keep changes localized and document them in docstrings.

## Open Questions
- Should resolution helpers raise on cleaned frame, or return None?

## Decision Log
- 2026-01-21: Story created to remove defensive introspection in
  ChangeControlManager.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created to tighten ChangeControlManager contract behavior by removing
defensive getattr usage and optional __all__ export list.
