- Completed: 2026-01-22
- Summary: Implemented structure profile models, builder/tooling helpers, and unit tests.

# Task: Implement structure profiles and AI-facing tools

## Metadata
- Task ID: TASK-2026-01-21-melder-structure-profiles-tools-implementation
- Story: STORY-2026-01-21-melder-structure-profiles-tools
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-21
- Updated: 2026-01-22

## Objective
Implement structure profile generation and AI-facing tool outputs with
provenance-tagged fuzzy hints.

## Scope Boundaries
- In scope:
  - Profile classes and generators for frame/conduit/spellbook scope.
  - Tool query surfaces for related spells, clusters, and paths.
- Out of scope:
  - AethericRift exposure and ACL enforcement.

## Blockers
- None. Investigation task completed.

## Steps / Checklist
- [x] Implement structure profile classes (non-dataclass, value-only rule).
- [x] Wire truth sources and derived hint generation.
- [x] Implement tool query surfaces with provenance and confidence.
- [x] Add tests for profile generation and tool outputs.

## Deliverables
- Structure profile implementation and tool query outputs in core structure profile modules.
- Unit tests covering spell record extraction and tooling queries.

## Files / Paths Impacted
- `src/melder/aether/structure_profiles/structure_profile_models.py`
- `src/melder/aether/structure_profiles/structure_profile_builder.py`
- `tests/unit/melder/aether/structure_profiles/test_structure_profile_builder.py`

## Validation
- User reported passing:
  - `pytest tests/unit/melder/aether/structure_profiles/test_structure_profile_builder.py`

## Risks / Rollback Notes
- Risk: Derived hints mislead without provenance.
  - Mitigation: enforce provenance/confidence on outputs.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Implemented structure profile models (`StructureHint`, `SpellStructureRecord`,
  `ConduitStructureProfile`, `FrameStructureProfile`) and builder/tooling helpers.
  (`src/melder/aether/structure_profiles/structure_profile_models.py`,
  `src/melder/aether/structure_profiles/structure_profile_builder.py`)
- Builder snapshots AethericFrame/Conduit state, emits dependency/sockets from
  `SpellSystemState` + `SpellLocalTopology`, and adds derived hints with provenance.
  (`src/melder/aether/structure_profiles/structure_profile_builder.py`)
- Tooling exposes describe/related/path/subsystem/recommendation queries and
  returns defensive copies to avoid mutating stored records.
  (`src/melder/aether/structure_profiles/structure_profile_builder.py`)
- Tests cover spell record extraction, dependency-path/related-spells tooling,
  and describe_spell_structure copy behavior.
  (`tests/unit/melder/aether/structure_profiles/test_structure_profile_builder.py`)
