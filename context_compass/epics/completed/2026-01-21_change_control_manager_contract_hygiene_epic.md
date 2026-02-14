- Completed: 2026-01-21
- Summary: Closed ChangeControlManager contract hygiene cleanup (owned getattr removal).

# Epic: Change-Control Manager Contract Hygiene

## Metadata
- Epic ID: EPIC-2026-01-21-change-control-manager-contract-hygiene
- Status: completed
- Owner:
- Priority: p2
- Created: 2026-01-21
- Updated: 2026-01-21
- Target Window: 2026-Q1
- Related Program/Initiative: Change-control maintenance

## Problem / Opportunity
ChangeControlManager uses defensive getattr checks for owned attributes and
swallows cleaned-state errors during frame resolution. This hides contract
violations and conflicts with the repo policy that owned code should not use
defensive introspection.

## MRP Alignment (Most Reasonable Product)
Tightening contract enforcement keeps change-control behavior predictable and
reduces silent failure modes in dynamic workflows.

## Goals (Outcomes)
- Replace owned-attribute getattr/hasattr usage with direct access and explicit
  None checks where appropriate.
- Stop swallowing check_cleaned failures in frame/conduit resolution helpers.
- Keep scope limited to ChangeControlManager hygiene without refactoring other
  modules.

## Non-Goals (Explicit Exclusions)
- Re-architecting change-control workflows or admission behavior.
- Refactoring other change-control subcomponents beyond the target file.
- Changing public API shapes outside the module's existing behavior.

## Scope Boundaries
- In scope:
  - Remove owned-attribute getattr usage in
    `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`.
  - Remove the module-level `__all__` export list in the same file if confirmed.
  - Update docstrings where behavior changes (e.g., cleaned-state handling).
- Out of scope:
  - Changes to orchestrator, conflict manager, embargo manager, or transaction
    manager logic.
  - Any changes in `SpellSystemStates` or `AethericFrame` beyond direct access.

## Success Metrics
- No owned-attribute getattr/hasattr usages remain in ChangeControlManager.
- Behavior is deterministic and cleaned-state violations are visible.
- Targeted tests (if any) pass when run by the user.

## Requirements (Functional + Non-Functional)
- Direct attribute access for owned attributes; no defensive introspection.
- Explicit, documented behavior when frame/conduit/spellbook references are
  missing or cleaned.
- Preserve existing functionality outside the intended contract enforcement.

## Constraints / Assumptions
- Work runs in inactive mode (no git commands).
- Docstring/comment standards apply to all touched methods.

## Dependencies / External References
- `context_compass/AGENTS.MD` (attribute access rule)
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`

## Milestones (Track Progress)
- [x] Milestone 1: Tickets created and approved.
- [x] Milestone 2: Owned-attribute getattr cleanup completed.
- [x] Milestone 3: Validation run by user (if required).

## Stories (Required to Complete)
- [x] Story: STORY-2026-01-21-change-control-manager-contract-hygiene - Remove
  defensive introspection in ChangeControlManager.

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: Complete story STORY-2026-01-21-change-control-manager-contract-hygiene

## Acceptance Criteria (Epic Done)
- All owned-attribute getattr usage removed from ChangeControlManager.
- Cleaned-state violations are no longer silently swallowed.
- User confirms acceptance criteria and closes tickets.

## Risks / Mitigations
- Risk: Behavior becomes stricter and exposes previously masked errors.
  - Mitigation: Document behavior changes and keep scope narrow.

## Validation / Test Approach
- Targeted pytest selection by user if behavior changes touch tests.

## Rollout / Adoption Plan
- Apply change-control hygiene in one module, then re-evaluate.

## Open Questions
- Should cleaned-state checks raise immediately or return None in resolution
  helpers?

## Decision Log
- 2026-01-21: Start change-control manager contract hygiene to remove owned
  getattr usage.

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Context / Handoff Summary
Epic created to remove defensive getattr usage and tighten contract enforcement
in ChangeControlManager.
