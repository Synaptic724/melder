# Task: Add frame-key metadata to local topology

## Metadata
- Task ID: TASK-2026-01-18-melder-frame-dependency-metadata
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-18

## Objective
Capture frame/binding metadata for **frame-sensitive** sockets (single-frame and
collection DI) so SpellSystemStates can build a spellbook-scoped dependency
index for targeted revalidation.

## Scope Boundaries
- In scope: SpellSocketDescriptor metadata, Phase 2-3 wiring, SpellSystemStates-local
  dependency index inputs, tests.
- Out of scope: changes to runtime meld execution or contract-link semantics.

## Steps / Checklist
- [x] Extend SpellSocketDescriptor to store `dependency_key` for NORMAL sockets (frame_key, binding_key).
- [x] Populate metadata during Phase 3 local frame build for single/collection/SpellMap sockets.
- [x] Ensure SpellSystemStates can derive spellbook-scoped dependency indices from local topology.
- [x] Add tests that assert dependency_key capture for list[Frame] and SpellMap(frame=...).

## Deliverables
- Updated topology metadata in `SpellLocalTopology`.
- Tests covering dependency_key capture for frame-sensitive sockets.

## Files / Paths Impacted
- `src/melder/spellbook/spell_crafter/topology/spell_local_topology.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `tests/integration/melder/spellbook/`

## Validation
- Not run after latest fixes.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_spell_crafter.py`

## Risks / Rollback Notes
- Risk: Incorrect key normalization. Mitigation: reuse SpellInputUtils and add tests.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Implemented dependency_key capture in SpellLocalTopology sockets and
  Phase 3 wiring, plus SpellSystemStates indexing hooks. Added integration
  assertions for dependency_key in collection and single sockets.
