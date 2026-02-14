# Task: Audit meld runtime/engine vs SpellCrafter phases 1-10 (remove remaining runtime responsibilities)

## Metadata
- Task ID: TASK-2026-01-28-phase8-10-migration-audit
- Story: N/A
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-01-28
- Updated: 2026-01-28

## Problem / Opportunity
Phase 1-10 responsibilities are split across SpellCrafter phases, meld runtime, and meld engine. We need a focused, evidence-based audit to identify duplicated or misplaced responsibilities and define which phase should own each behavior so meld runtime/engine stay lean.

## Context
Investigation targets (evidence required):
- SpellCrafter phases 1-10 wiring and phase outputs.
  - src/melder/spellbook/spell_crafter/spell_crafter.py
  - src/melder/spellbook/spell_crafter/blueprints/
- Meld runtime and meld engine responsibilities during resolution.
  - src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
  - src/melder/aether/conduit/meld/meld_engine/meld_engine.py

Known migration regressions:
- UNKNOWN: Contract precedence drift due to stale Phase 8 plan. (investigate context_compass/tasks/completed/ and recent failures)
- UNKNOWN: Override error semantics drift. (investigate meld runtime/engine + phase outputs)
- UNKNOWN: Mutation override gating behavior drift. (investigate meld runtime/engine + phase outputs)

## MRP Alignment
Phases should own compilation work; meld runtime/engine should consume artifacts without re-deriving them. This reduces hot-path overhead and centralizes behavior in compile phases.

## Goals
- Identify remaining runtime/engine computations that should move into phases 1-10.
- Ensure phase artifacts are complete and correctly invalidated for the behaviors they own.
- Remove redundant runtime/engine recomputation without changing behavior.

## Non-Goals
- No behavior changes beyond aligning with the existing pre-migration semantics.
- No refactors outside the meld/phase pipeline.

## Requirements
- Audit must be evidence-based (file + symbol references).
- Any proposed changes must preserve current semantics unless explicitly approved.
- Record findings in an audit document under context_compass/artifacts.

## Acceptance Criteria
- Audit report lists each remaining runtime/engine responsibility and the phase that should own it.
- Audit report maps each duplicated behavior to a phase owner (or marks UNKNOWN with evidence target).
- Implementation plan is updated with concrete file/symbol changes.
- All remaining migration gaps are tracked as follow-up tasks or implemented.

## Scope Boundaries
- In scope:
  - Meld runtime/engine responsibilities related to phases 1-10.
  - SpellCrafter phases 1-10 compilation boundaries and outputs.
- Out of scope:
  - Phase 1-10 behavior changes (this is investigation only).

## Steps / Checklist
- [ ] Inventory meld runtime/engine compile-time work still happening in runtime.
- [ ] Map each responsibility to Phase 1-10 artifact ownership.
- [ ] Identify duplicated behaviors between phases and runtime/engine.
- [ ] Identify missing invalidation paths for phase artifacts.
- [ ] Draft implementation plan with file-level changes.

## Deliverables
- Migration audit report with evidence references.
- Follow-up tasks for each migration gap (or implementation if approved).

## Files / Paths Impacted
- UNKNOWN (audit-driven). Likely:
  - src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
  - src/melder/aether/conduit/meld/meld_engine/meld_engine.py
  - src/melder/spellbook/spell_crafter/spell_crafter.py
  - src/melder/spellbook/spell_crafter/blueprints/
  - context_compass/artifacts/meld_engine_phase_migration_audit/phase_migration_audit.md

## Validation
- Not run.
- Recommended commands:
  - pytest tests/unit/melder/aether/conduit/meld -k "runtime"

## Risks / Rollback Notes
- Risk: Missing a runtime responsibility causes behavior drift.
- Rollback: Restore runtime computation for affected responsibility.

## Decision Log
- 2026-01-28: User requested a complete migration audit for remaining runtime responsibilities.
- 2026-01-28: Scope expanded to phases 1-10 and includes meld engine; add dedicated audit document.

## Unknowns
- Exact list of remaining runtime/engine responsibilities (audit required).
- Which phases (1-10) should own each duplicated behavior (audit required).

## Context / Handoff Summary
Audit started. Evidence gathered from meld runtime/engine and SpellCrafter phases 8-10 artifacts; initial duplication candidates identified (occurrence planning, contract override compilation, override targeting, mutation rewiring). Next: complete phase-by-phase map for phases 1-10 and finish the duplication/ownership table in the audit doc with file+symbol evidence.
