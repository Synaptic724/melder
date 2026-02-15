- Completed: 2026-01-22
- Summary: Implemented full AI profile inventory/provenance and added coverage for method profile provenance fields.

# Task: Implement full AI profile inventory and provenance

## Metadata
- Task ID: TASK-2026-01-21-melder-ai-profile-inventory-implementation
- Story: STORY-2026-01-21-melder-ai-profile-inventory
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22

## Objective
Implement unfiltered AI profile inventory, full provenance capture, and
first-class member records for non-callables.

## Scope Boundaries
- In scope:
  - AI profile strategy, inspectors, and profile schemas.
  - Full source capture with start/end lines when available.
  - Properties/descriptors, instance attributes, and dynamic attribute signals.
- Out of scope:
  - Downchain ACL filtering.
  - Identity/lineage/spellbook context.
  - Capability semantics and policy decisions.
  - Size/perf controls or storage strategy.
  - Cross-object topology or dependency graphs.

## Blockers
- None. Investigation task completed.

## Steps / Checklist
- [x] Force AI profile show_dunders=True at entrypoint.
- [x] Capture full source text with start/end lines for classes and members.
- [x] Add tool-shaped member records for properties/descriptors/data attributes.
- [x] Ensure provenance keys are consistent across members.
- [x] Capture docstrings for class/member/property/descriptor records.
- [x] Add instance attribute inventory for instance-bound objects.
- [x] Record dynamic attribute access signals when present.
- [x] Add tests for dunders, properties, and builtins.

## Deliverables
- Updated SpellAIProfile output with full inventory and provenance.
- Implementation scoped by `context_compass/artifacts/README.md`.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/method_inspector.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py`
- `src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py`
- `tests/unit/melder/spellbook/spell_crafter/spell_examiner/inspectors/test_class_inspector.py`
- `tests/unit/melder/spellbook/spell_crafter/spell_examiner/inspectors/test_method_inspector.py`
- `tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py`

## Validation
- User reported passing:
  - `pytest tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py`

## Risks / Rollback Notes
- Risk: Source capture fails for builtins/extension types.
  - Mitigation: null source fields with flags.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Ensured AI profiles force dunder visibility at the SpellExaminer entrypoint
  and keep AI profiles gated by configuration.
  (`src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py`)
- ClassInspector and MethodInspector provide full provenance, docstrings,
  property/descriptor details, and dynamic-access flags for member records.
  (`src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py`,
  `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/method_inspector.py`)
- AIProfileStrategy now passes full provenance and docstring fields into
  class member MethodProfiles and collects instance-member inventories.
  (`src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py`)
- Added a strategy test to assert method profiles include provenance fields.
  Existing inspector tests cover dunders, properties, and builtins.
  (`tests/unit/melder/spellbook/spell_crafter/spell_examiner/strategies/test_ai_profile_strategy.py`,
  `tests/unit/melder/spellbook/spell_crafter/spell_examiner/inspectors/test_class_inspector.py`,
  `tests/unit/melder/spellbook/spell_crafter/spell_examiner/inspectors/test_method_inspector.py`)
