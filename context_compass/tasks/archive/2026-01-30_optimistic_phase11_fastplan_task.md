# Task: Implement optimistic-style Phase 11 fast plan (no overrides)

## Metadata
- Task ID: TASK-2026-01-30-optimistic-phase11-fastplan
- Story:
- Status: in_progress
- Owner:
- Priority: p1
- Created: 2026-01-30
- Updated: 2026-01-30

## Objective
Add a compact, optimistic-style Phase 11 plan for no-override/no-mutation execution that uses array-based dependency indices and a tight loop, while preserving SpellContract payload semantics.

## Problem / Opportunity
Current Phase 11 execution still builds per-step kwargs maps even when no overrides or mutations are present. This adds measurable overhead (microseconds per meld) and prevents reaching the optimistic plan baseline.

## Context
- We already forked a no-override execution path in MeldRuntime and MeldEngine.
- Overrides and mutation overrides remain in the existing path for now.
- SpellContract payloads must still apply; treat contract providers like normal spells.

## MRP Alignment
This improves the core resolution path without changing public API semantics or adding new dependencies.

## Goals
- Compile an optimistic-style array plan for NO_OVERRIDES_FAST.
- Execute that plan in a tight loop when no overrides or mutations are present.
- Preserve SpellContract payload application during execution.

## Non-Goals
- Do not change override or mutation override behavior.
- Do not change public API shape.
- Do not add tests for this pass (explicitly deferred by user).

## Scope Boundaries
- In scope:
  - ExecutionPlan builds compact arrays for no-overrides plan.
  - MeldEngine uses fast arrays in the no-overrides execution path.
  - MeldRuntime routes no-overrides/no-mutations to the fast arrays.
- Out of scope:
  - Override/mutation optimized plan.
  - Any changes to validation or Phase 1-4 behavior.

## Requirements
- Use Phase 1 parameter order as positional dependency order.
- Assume SpellContract providers exist when building the plan.
- Apply contract payloads during execution (no defensive checks).
- Keep existing override/mutation path unchanged.

## Acceptance Criteria
- No-override/no-mutation melds execute using array-based plan when available.
- Override and mutation override paths behave as before.
- Contract payloads still apply to the correct spell steps.

## Steps / Checklist
- [x] Extend ExecutionPlan with optional fast arrays for NO_OVERRIDES_FAST.
- [x] Build fast arrays in ExecutionPlanBuilder for NO_OVERRIDES_FAST.
- [x] Execute fast arrays in MeldEngine.run_execution_plan_no_overrides.
- [x] Keep override/mutation path unchanged.
- [x] Update docstrings for touched methods.

## Deliverables
- Fast-plan arrays compiled and executed for no-overrides/no-mutations.
- Docstrings updated for modified methods.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py

## Validation
- Not run (per user request).
- Recommended commands:
  - pytest -q

## Risks / Mitigations
- Risk: positional ordering mismatch for DI parameters. Mitigation: use Phase 1 parameter order.
- Risk: contract payload application in fast path diverges from existing path. Mitigation: reuse plan-time payloads and merge at execution.

## Decision Log
- Keep overrides and mutation overrides on the existing execution path for now.
- SpellContract providers are treated as normal spells in the plan.

## Context / Handoff Summary
Implemented optimistic-style array plan for no-overrides/no-mutations and routed the no-override path to it. Contract payloads are applied in the fast path; override/mutation paths stay unchanged. Updated OccurrencePlan contract handling to treat SpellContract providers as required during plan build.
