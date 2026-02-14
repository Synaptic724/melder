# Task: Trim Phase 11 fast-path overhead (guards + enum churn)

## Metadata
- Task ID: TASK-2026-01-30-phase11-fastpath-trim-overhead
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Remove avoidable per-step overhead in the Phase 11 no-override execution path by
eliminating redundant guards, avoiding repeated Enum lookups, and using fully
precompiled fast-plan arrays.

## Problem / Opportunity
Profiling shows significant time in per-step property/guard overhead:
- `Spell.is_class_spell` / `Spell.is_existing_creation` and `Enum.__hash__`.
- `ExecutionPlanStep.instance_key` lookups.
- `_resolve_spell_instance_with_plan` and `_select_creations_by_target_kind` called
  on every step even when `Existence.many` does not need reuse checks.

## Context
- The Phase 11 NO_OVERRIDES_FAST plan is now active and uses array-based
  dependency indices.
- Overrides/mutation overrides remain on the existing execution path.

## MRP Alignment
This improves the core resolution fast path without changing public API
semantics or introducing new dependencies.

## Goals
- Remove per-step guards that are redundant under meld front-door validation.
- Cache Spell kind flags to avoid repeated `SpellType` enum hashing.
- Bypass reuse-resolution logic for `Existence.many` in the no-overrides fast path.
- Use fast-plan arrays for instance keys, existence, creations target kind, and
  "first result" flags to reduce dictionary/property overhead.

## Non-Goals
- No changes to override/mutation override semantics (beyond guard removal).
- No new tests in this pass (explicitly deferred by user).
- No public API changes.

## Scope Boundaries
- In scope:
  - `Spell` cached kind flags.
  - ExecutionPlan fast arrays extended for additional per-step data.
  - MeldEngine no-overrides fast path uses arrays and skips redundant guards.
  - Guard removal in override/mutation path where safe.
- Out of scope:
  - Rewriting the full reuse/locking algorithm.
  - Any changes to Phase 1–4 validation flows.

## Requirements
- Assume validation already ensures plan correctness in Phase 11.
- Remove `instance_key` and `spell is None` guards in execution loops.
- Avoid `ResolutionFrame.has_result` checks by using precomputed first-result flags.
- Preserve concurrency/locking behavior for non-`Existence.many` cases.

## Acceptance Criteria
- No-override fast path avoids `SpellType` hashing on hot calls.
- `Existence.many` steps execute without `_resolve_spell_instance_with_plan`.
- ExecutionPlan fast arrays include instance keys and creation routing metadata.
- Override/mutation paths continue to function with guards removed.

## Steps / Checklist
- [x] Create task ticket for fast-path overhead trim.
- [x] Add cached spell kind flags in `Spell` and update cleanup.
- [x] Extend ExecutionPlan fast arrays (instance keys, existence, creations target kind,
      must_register, first-result flags).
- [x] Update MeldEngine fast path to use new arrays and bypass reuse logic for
      `Existence.many`.
- [x] Remove redundant guards in override/mutation execution path.
- [x] Update docstrings for modified methods.

## Deliverables
- Updated Phase 11 fast path with reduced per-step overhead.
- Updated docstrings in touched methods.

## Files / Paths Impacted
- `src/melder/spellbook/spell.py`
- `src/melder/spellbook/spell_crafter/blueprints/execution_plan.py`
- `src/melder/aether/conduit/meld/meld_engine/meld_engine.py`

## Validation
- Not run (per user instruction).
- Recommended commands:
  - `python benchmarks/testing_other_di/profile_deep_all_di_transient_only_no_singletons.py`

## Risks / Mitigations
- Risk: Missing validation could hide incorrect plan assumptions.
  Mitigation: Keep changes confined to NO_OVERRIDES_FAST and documented.
- Risk: Removing guards exposes latent inconsistencies in rare cases.
  Mitigation: Scope guard removals to plan-driven execution loops only.

## Decision Log
- Remove redundant guards based on front-door validation guarantees.
- Prefer array-based fast path over per-step property/lookup access.

## Context / Handoff Summary
Cached Spell kind flags now avoid SpellType hashing on hot paths. Phase 11
NO_OVERRIDES_FAST plan now includes instance keys, existence, creations target
kind, must-register, and first-result flags; the no-overrides execution loop
uses these arrays, bypasses reuse logic for Existence.many, and removes
redundant guards. Override path guard checks were removed. Validation not run.
