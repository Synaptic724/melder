# Task: Fast-path phases 5-11 by removing guards and snapshots

## Metadata
- Task ID: TASK-2026-01-30-fast-path-phase5-11
- Story:
- Status: draft
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Remove defensive runtime guards and snapshot usage in phases 5-11 so the phase pipeline trusts prior validation and runs as a fast path.

## Scope Boundaries
- In scope:
  - Phases 5-11: remove redundant validation/None checks and defensive snapshots.
  - Trust live data structures in phase pipeline and builders.
  - Update docstrings/comments touched to match new contracts.
  - Update architecture/components docs if phase boundaries or invariants change.
- Out of scope:
  - Tests (explicitly deferred by user for this pass).
  - Diagnostics snapshots (Spellbook/Conduit/dev-ops) unless explicitly re-scoped.

## Steps / Checklist
- [ ] Identify Phase 5-11 guard clauses and snapshot paths (Phase 5 adjacency snapshot, phase builders, meld runtime/engine).
- [ ] Propose the minimal fast-path changes and confirm scope before edits.
- [ ] Implement removals of guards and snapshot usage in phases 5-11.
- [ ] Update docstrings/comments for touched functions to reflect fast-path contracts.
- [ ] Update architecture/components docs if phase lifecycle/invariants changed.
- [ ] Record validation status (tests not run per user request).

## Deliverables
- Phase 5-11 code paths no longer perform defensive guards or snapshotting.
- Updated docstrings/comments for touched methods.
- Architecture/components docs updated if contracts/invariants changed.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py
- src/melder/spellbook/spell_crafter/system/spell_system_adjacency_snapshot.py
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- src/melder/spellbook/spell_crafter/blueprints/occurrence_plan.py
- src/melder/spellbook/spell_crafter/blueprints/injection_plan.py
- src/melder/spellbook/spell_crafter/blueprints/patch_maps.py
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Validation
- Not run (per user request).
- Recommended commands:
  - pytest -q

## Risks / Rollback Notes
- Removing guards may surface latent invariants or invalid states if upstream validation regresses.
- Snapshot removal may expose concurrent mutation risks; verify ownership/locking contracts before removal.
- Rollback: reintroduce guards/snapshots in the specific phase method that fails.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
User requested Phase 5-11 fast-path: remove defensive runtime guards and snapshot usage, trusting meld validation. Tests deferred for now. Scope excludes diagnostics snapshots unless re-scoped.
