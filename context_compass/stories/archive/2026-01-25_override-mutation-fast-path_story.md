# Story: Override and mutation patch maps for fast path

## Metadata
- Story ID: STORY-2026-01-25-override-mutation-fast-path
- Epic: EPIC-2026-01-25-fast-path-meld-compiled-plans
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-25
- Updated: 2026-01-25

## User Narrative
As a power user, I want overrides and mutation overlays to use fast-path patch
maps when possible, so that most calls avoid full GraphMutator and
SpellOverrider work.

## Value / MRP Alignment
Provides a safe but faster path for overrides and mutations without changing
semantics.

## Requirements (Functional)
- Override slot map from SocketRef to plan step and parameter slot.
- Mutation patch map to rewire dependencies when mutation overrides exist.
- TargetSpec.parse caching to reduce repeated parse overhead.

## Requirements (Non-Functional)
- Preserve override and mutation semantics.
- Fall back to GraphMutator and SpellOverrider when patching is not possible.

## Scope Boundaries
- In scope:
  - Slot map compilation and patching paths.
  - TargetSpec.parse caching.
- Out of scope:
  - Full override plan variants beyond patching.

## Dependencies / Related Work
- GraphMutator and SpellOverrider
  (src/melder/aether/conduit/meld/overrides/graph_mutator.py,
   src/melder/aether/conduit/meld/overrides/spell_overrider.py).
- TargetSpec and DagTargetingEngine
  (src/melder/spellbook/spell_crafter/dag/target_spec.py,
   src/melder/spellbook/spell_crafter/dag/dag_index.py).

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-01-25-override-mutation-research - Research override and mutation patching.
- [ ] Task: TASK-2026-01-25-override-slot-map - Compile SocketRef to slot pointers.
- [ ] Task: TASK-2026-01-25-mutation-patch-map - Compile mutation patch instructions.
- [ ] Task: TASK-2026-01-25-targetspec-parse-cache - Cache TargetSpec.parse results.
- [ ] Task: TASK-2026-01-25-override-patching-tests - Add override and mutation tests.

## Acceptance Criteria
- Overrides patch into plan slots when possible.
- Mutation overrides patch when possible and fall back otherwise.
- TargetSpec.parse cache reduces repeated parsing overhead.

## Validation / Test Plan
- Not run.
- Recommended: pytest tests/unit/melder/aether/conduit/meld/overrides -k override

## UX / API / Data Notes
- Internal runtime path only.

## Risks / Mitigations
- Risk: patch maps target the wrong occurrence for Existence.many.
  Mitigation: include occurrence path in slot pointer mapping.

## Open Questions
- Do we need separate patch maps for hook-enabled plan variants?

## Decision Log
- TBD.

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Story created; override and mutation fast-path patching pending.
