# component_patch_spellbook_conjure

## Metadata
- Patch ID: conjure_validation_warnings_2026_09_26
- Component: Spellbook Core (conjure) and SpellbookCreationSystem
- Status: promoted to src_components and archived 2026-09-26T10:12:55Z
- Owner: user (implementation: melder_0)
- Created: 2026-09-26T09:19:49Z
- Updated: 2026-09-26T09:19:49Z

## Component Purpose and Boundary
- Current boundary: conjure preparation always reports UNRESOLVED_INPUT warnings as one INFO line.
- Target boundary: conjure preparation reports Phase-4 warnings only for a public conjure that asked.

## Before/After Behavior Summary
- Before: `_prepare_spellbook_for_conjure` runs structural phases, then `_report_unresolved_inputs`
  logs "Conjure: N unresolved input(s) ... : Spell.param -> Type, ..." at INFO on every conjure that has
  unresolved inputs, on every route (public, Nexus, restore, upgrade).
- After: `_prepare_spellbook_for_conjure(..., validation_warnings=False)` runs structural phases and,
  only when True, calls `_report_validation_warnings`. That collects warning-severity issues from each
  owned Spell's `validation_result_phase4` (book order, then issue order), groups them by code in
  first-seen order and logs one WARNING event:
  "Conjure validation warnings (N):" then one line per code "  CODE (n): entry; entry".
  Entry: UNRESOLVED_INPUT -> "Spell.param -> ExpectedType"; issues with details["parameter_name"] ->
  "Spell.param"; others -> "Spell". Nothing is logged when there are no warnings.

## Interface Deltas
- Inputs: `Spellbook.conjure(..., validation_warnings: bool = False)`;
  `SpellbookCreationSystem(..., validation_warnings: bool)`;
  `SpellbookCreationSystem._prepare_spellbook_for_conjure(..., validation_warnings: bool = False)`.
- Outputs: at most one WARNING log event per conjure; return values unchanged.
- Error semantics: unchanged. The reporter raises nothing for well-formed issues.

## State and Lifecycle Deltas
- Owned state changes: SpellbookCreationSystem gains the `_validation_warnings` slot (a bool).
- Lifecycle/cleanup changes: `cleanup()` deletes `_validation_warnings` with the other inputs.

## Failure Mode Deltas
- New failure mode: none.
- Removed failure mode: none (the INFO line was reporting only).
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The report runs after `run_structural_phases` and before resolution phases, while Phase-4 results
   are still attached to the spells.
2. `_conjure_existing_conduit` keeps calling `_prepare_spellbook_for_conjure` without the keyword.

## Validation Expectations
- Component: default conjure with an unresolved input logs no conjure report at any level.
- Component: `conjure(validation_warnings=True)` logs one WARNING event listing UNRESOLVED_INPUT and
  REQUIRED_HOLE groups with counts and entries.
- Component: upgrade_to_normal of a book with unresolved inputs logs no conjure report.
- Unit: reporter grouping/order/entry rendering over stub spells; silent when no warnings.
- Evidence target: tests/component/melder/spellbook/test_spellbook_component_unresolved_input.py.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none (owner approved the shape; Phase-6 diagnostics stay out of scope).

## Context / Handoff Summary
- What changed: opt-in, grouped Phase-4 warning report on the public conjure only.
- Remaining risks: users who relied on the 0.2.54 INFO line must pass validation_warnings=True.
- Next entrypoint: src/melder/aether/spellbook/spellbook_creation_system.py:_prepare_spellbook_for_conjure.
