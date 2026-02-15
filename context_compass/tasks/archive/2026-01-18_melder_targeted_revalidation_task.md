# Task: Targeted revalidation for frame-based dependencies

## Metadata
- Task ID: TASK-2026-01-18-melder-targeted-revalidation
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: complete
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-18

## Objective
Use frame-sensitive dependency metadata to mark only impacted **spellbook-owned**
spells dirty when new bindings or contracted spells appear, enabling targeted
revalidation without cross-conduit contamination.

## Scope Boundaries
- In scope: SpellSystemStates dirty propagation, bind/scan hooks, contracted-spell
  triggers, targeted revalidation tests.
- Out of scope: changing DI resolution semantics or link/unlink behavior.

## Steps / Checklist
- [x] Add SpellSystemStates-local dependency indices keyed by spellbook id and frame/binding keys.
- [x] On end_binding_transaction, mark only impacted local lineages dirty.
- [x] On contracted-spell additions, mark only consumer spellbook lineages dirty.
- [x] Add integration tests showing list[Frame] updates after revalidation and no cross-conduit bleed.

## Deliverables
- Targeted dirty propagation for frame-sensitive sockets (spellbook-owned scope).
- Integration tests for targeted revalidation and contracted-spell scope.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/spell_system_states/spell_system_states.py`
- `src/melder/spellbook/spellbook.py`
- `tests/integration/melder/spellbook/`

## Validation
- Not run after latest fixes.
- Recommended commands:
  - `pytest tests/integration/melder/spellbook/test_spellbook_integration_post_conjure_bind_snapshot.py`

## Risks / Rollback Notes
- Risk: Over-marking dirty lineages reduces performance. Mitigation: require frame/binding match
  and keep scope to spellbook-owned lineages only.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded

## Context / Handoff Summary
- Implemented spellbook-scoped collection indices, post-conjure dirty marking
  for binding transactions, and contracted-spell gating. Added integration
  tests for spellbook isolation and contracted list consumers.
