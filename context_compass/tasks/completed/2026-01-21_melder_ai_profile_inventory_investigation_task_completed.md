- Completed: 2026-01-22
- Summary: Documented current AI profile schema, provenance gaps, and required inventory expansions.

# Task: Investigate AI profile inventory gaps

## Metadata
- Task ID: TASK-2026-01-21-melder-ai-profile-inventory-investigation
- Story: STORY-2026-01-21-melder-ai-profile-inventory
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22

## Objective
Inventory current SpellAIProfile outputs and identify the gaps for full
inventory, provenance, and dunder inclusion.

## Scope Boundaries
- In scope:
  - Current AI profile generation in spell_examiner inspectors/strategies.
  - Existing provenance fields (file, line offsets, previews).
  - Member shapes for callables vs properties/data.
- Out of scope:
  - Code changes.

## Steps / Checklist
- [x] Record current SpellAIProfile schema and members map shape.
- [x] Identify missing provenance fields and where to source them.
- [x] Identify dunder filtering paths and proposed invariant changes.
- [x] List required schema changes for properties/data members.

## Deliverables
- Investigation notes added to the task Context / Handoff Summary.
- Scope update artifact linked for implementation reference.

## Files / Paths Impacted
- Documentation only (this task ticket).

## Validation
- Not run (investigation-only).

## Risks / Rollback Notes
- Risk: Some members are uninspectable.
  - Mitigation: note where nulls/flags are required.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Verification status (2026-01-22):
  - Verified AI profile gating and construction path in SpellExaminer.ai_profile_for_spell.
  - Verified AIProfileStrategy defaults show_dunders=False and builds SpellAIProfile from binding/resolution profiles plus ClassInspector/MethodInspector outputs.
  - Verified BindingProfileStrategy dunder filtering (dataclass __init__ exception) and origin file/source preview fields.
  - Verified ClassInspector member inventory shape, dunder filtering, property_details, and preview-only provenance fields.
  - Verified MethodInspector preview-only provenance fields and uninspectable flag handling.
  - Verified ClassProfile/MethodProfile/SpellAIProfile fields match the summary below.
- Scope update: `context_compass/artifacts/ai_profile_inventory_ticket_update.md` (object-level inventory additions: properties/descriptors, instance attributes, dynamic attribute signals, docstrings).
- Current AI profile shape: `SpellAIProfile` holds `spell`, `binding_profile`, `resolution_profile`, optional `class_profile`/`callable_profile`, and `metadata` dict. `SpellExaminer.ai_profile_for_spell(...)` builds via `AIProfileStrategy` with `show_dunders=False` by default. (`src/melder/spellbook/spell_crafter/spell_examiner/spell_examiner.py`, `src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py`, `src/melder/spellbook/spell_crafter/spell_examiner/profiles/ai_profile.py`)
- Dunder filtering: `AIProfileStrategy` and `BindingProfileStrategy` default `show_dunders=False`; `ClassInspector._members` filters dunders except dataclass `__init__`. (`src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py`, `src/melder/spellbook/spell_crafter/spell_examiner/strategies/binding_profile_strategy.py`, `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py`)
- Provenance today is preview-only: `ClassInspector` captures `file`, `source_line_offset`, `source_preview` (first 5 lines). `MethodInspector` captures `file`, `preview` (first 5 lines), `src_offset`. No `end_line` or full source text; `ClassProfile`/`MethodProfile` only store preview/offset. (`src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py`, `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/method_inspector.py`, `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/profiles/class_profile.py`, `src/melder/spellbook/spell_crafter/spell_examiner/inspectors/profiles/method_profile.py`)
- Member inventory shape: `ClassInspector` emits `members` map entries with `kind`, `callable`, `property`, `signature`, `parameters`, `property_details`, and `src_line` for callables. Non-callables stay as raw member dicts; `AIProfileStrategy` only lifts `callable` members into `MethodProfile`. (`src/melder/spellbook/spell_crafter/spell_examiner/inspectors/class_inspector.py`, `src/melder/spellbook/spell_crafter/spell_examiner/strategies/ai_profile_strategy.py`)
- Missing fields vs desired ticket: docstrings, end_line/full source, per-member provenance for non-callables, readable/writable flags for properties, and tool-shaped records for attributes. Derived summaries/tags are not present today.
- Constraint: user policy says AI profiles should not be used atm; keep future work gated/disabled in runtime consumers until explicitly approved.
