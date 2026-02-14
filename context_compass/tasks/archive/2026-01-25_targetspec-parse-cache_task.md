# Task: Add TargetSpec.parse caching

## Metadata
- Task ID: TASK-2026-01-25-targetspec-parse-cache
- Story: STORY-2026-01-25-override-mutation-fast-path
- Status: draft
- Owner:
- Priority: p2
- Created: 2026-01-25
- Updated: 2026-01-25

## Objective
Cache TargetSpec.parse results to reduce repeated parsing overhead in override
handling.

## Scope Boundaries
- In scope:
  - Cache for TargetSpec.parse inputs and outputs.
- Out of scope:
  - Override map compilation.

## Steps / Checklist
- [ ] Identify parse call sites in SpellOverrider.
- [ ] Add cache with bounded size and deterministic behavior.
- [ ] Add tests for cache hit and miss behavior.

## Deliverables
- TargetSpec.parse cache implementation.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/dag/target_spec.py
- src/melder/aether/conduit/meld/overrides/spell_overrider.py

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld/overrides -k targetspec

## Risks / Rollback Notes
- Risk: cache grows unbounded.
  Mitigation: bound cache size and clear on cleanup.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
Task created; TargetSpec.parse cache pending.
