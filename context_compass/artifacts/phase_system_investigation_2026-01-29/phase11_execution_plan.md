# Phase 11 Investigation (Execution Plan)

## Metadata
- Created: 2026-01-29
- Updated: 2026-01-29
- Task: TASK-2026-01-29-phase11-execution-plan-investigation

## Scope
Analyze execution plan compilation, root-only behavior, and runtime consumption.

## Key Questions
- What inputs are required from Phases 8-10?
- Why is it root-only today?
- What changes are required to make every spell executable with a plan?

## Evidence
- src/melder/spellbook/spell_crafter/spell_crafter.py: SpellCrafter.run_phase_execution_plan
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py: ExecutionPlanBuilder.build
- src/melder/spellbook/spell_crafter/blueprints/execution_plan.py: ExecutionPlanStep
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py: MeldRuntime.execute
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py: MeldEngine.run_execution_plan
- src/melder/spellbook/spellbook.py: Spellbook._run_resolution_phases_for_conduit

## Findings
- Phase 11 requires a root blueprint and a Phase 8 occurrence plan. Non-root spells return without building a plan. If a root spell is missing its root blueprint, Phase 11 raises RuntimeError.
- ExecutionPlanBuilder uses the Phase 8 occurrence plan and optional Phase 9 injection plan. If the injection plan root does not match, it raises ValueError.
- ExecutionPlanBuilder converts occurrence_plan.execution_order into a flat list of ExecutionPlanStep entries, choosing action ("construct" for Existence.many, otherwise "reuse"), creation_target (owner/caller/spellspace), and whether to register instances based on existence and disposal methods.
- MeldRuntime.execute currently always calls engine.run_execution_plan(execution_plan_to_run). MeldEngine.run_execution_plan raises ValueError when execution_plan is None and raises MeldExecutionError on root mismatch.
- Spellbook._run_resolution_phases_for_conduit schedules the execution_plan phase for every local spell; non-root spells rely on the Phase 11 no-op behavior and therefore keep execution_plan_phase11 as None.

## Risks / Concerns
- Root-only Phase 11 means non-root spells can lack execution plans. When MeldRuntime always calls run_execution_plan, this becomes a hard failure.
- ExecutionPlanBuilder assumes execution_order and occurrence plan are complete; missing spell ids in spell_lookup raise ValueError.

## Unknowns
- Whether Phase 11 should be generated for non-root spells or whether runtime should switch to a different execution path for non-root resolution (design decision).
- Whether execution_plan should be rebuilt when contract dependencies change (dynamic linking).

## Next Steps
- Decide whether to expand plan generation beyond roots or to adjust runtime to fall back when execution_plan is None.
- Verify the expected runtime path for non-root meld (root-only plan vs per-spell plan).
