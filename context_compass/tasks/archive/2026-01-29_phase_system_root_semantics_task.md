# Task: Investigate phase system root semantics vs meld targets

## Metadata
- Task ID: TASK-2026-01-29-phase-system-root-semantics
- Story: STORY-2026-01-29-phase-11-meld-runtime
- Status: in_progress
- Owner:
- Priority: p0
- Created: 2026-01-29
- Updated: 2026-01-29

## Objective
Identify why non-root spells cannot run Phase 11 execution plans and propose a durable fix that makes any meld target executable without runtime planning duplication.

## Scope Boundaries
- In scope:
  - Analyze how Phase 5 roots are computed and how that affects Phase 8–11 artifacts.
  - Map the current failure path (meld -> runtime -> engine) when execution_plan is missing.
  - Propose resolution paths (compile per-spell plans vs on-demand plans vs expand roots).
- Out of scope:
  - Implementing the fix.
  - Updating tests/benchmarks.

## Steps / Checklist
- [ ] Trace root selection for Phase 5 blueprints in SpellCrafter and system builders.
- [ ] Trace Phase 8–11 artifact compilation rules and identify when plans are skipped.
- [ ] Trace meld runtime/engine execution plan usage and failure conditions.
- [ ] Propose resolution options with tradeoffs (perf, memory, correctness).
- [ ] Recommend a primary path and define follow-up tasks.

## Deliverables
- Investigation summary with evidence-backed root cause.
- Proposed resolution plan (phases + runtime/engine changes) with risks.

## Files / Paths Impacted
- src/melder/spellbook/spell_crafter/system/spell_system_adjacency_builder.py
- src/melder/spellbook/spell_crafter/system/spell_system_root_blueprint_builder.py
- src/melder/spellbook/spell_crafter/spell_crafter.py
- src/melder/spellbook/spellbook.py
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py

## Validation
- Not run.
- Recommended commands:
  - pytest benchmarks/testing_other_di/test_conduit_integration_perf_conjure_meld.py -q

## Risks / Rollback Notes
- Changing root semantics could expand Phase 5–11 work and impact conjure time.
- Execution plan generation for every spell could increase memory usage.
- On-demand compilation risks reintroducing runtime planning paths.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Acceptance criteria reviewed with user and confirmed

## Context / Handoff Summary
- Root blueprints are currently built only for structural roots computed as `all_spell_ids - all_dependency_ids` (SpellSystemAdjacencyBuilder: root_spell_ids). Non-root spells do not receive Phase 5 root blueprints.
- Phase 8–11 compilation is a no-op for non-roots; Phase 11 requires a root blueprint and Phase 8 plan (SpellCrafter.run_phase_execution_plan).
- MeldRuntime currently unconditionally calls MeldEngine.run_execution_plan(execution_plan_phase11); if plan is None, execution fails early.
- This causes meld of non-root spells (e.g., config/logger dependencies) to fail even though they are valid meld targets.
