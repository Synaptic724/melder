

# Task: Skip the dead OVERRIDES lane-plan build on override-free graphs

## Metadata
- Task ID: TASK-2026-06-13-skip-dead-overrides-plan-build
- Story: none (perf lane, evidence: post-phase-8-cut synth-200 profile)
- Status: paused
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-13T05:20:00Z
- Updated: 2026-06-13T05:20:00Z

## Objective
Post-phase-8-cut profile (synth-200, cold conjure 0.331s profiled, down from
0.658s) ranks phase 11 (0.073s) and phase 10 (0.056s) as the top cold-lane
costs. Root finding: `SpellGeneralizedCodegenPlanStrategy.apply` builds BOTH
plan variants per spell unconditionally -- `_build_lane_plan_from_model` runs
400x for 200 spells. On override-free graphs (the common case; gauntlet and
synth both) the OVERRIDES plan is dead weight: ~half of phase-10 build cost,
a share of the 1,664 `build_phase11_step_ir_row` calls and 2,000
`_pickle.dumps` (10/spell). Goal: build the overrides plan only when the
graph can actually use it.

## Ticket Contract
- ENTRY_GATE: board row routes here.
- EXECUTION_BOUNDARY: codegen_planner (strategy + lane-plan data +
  SpellCodegenPlan container) and ONLY the consumers of `overrides_plan`
  (manifest compilers, cache staging/rehydration, runtime override
  targeting). No scheduler/UnitOfWork/dev_ops/conduit files.
- DEPENDENCIES: phase-8 memo lane (closed).
- EXIT_GATE: consumer inventory documented; chosen strategy implemented;
  unit + component suites green; synth sweep shows the phase-10/11 drop.
- FAILURE_ESCALATION: BLOCKER if runtime override hot-swap REQUIRES a
  prebuilt overrides plan even on override-free graphs (would force the
  lazy-build option or kill the lane).

## Scope Boundaries
- In scope: conditional/lazy overrides-plan construction + consumer guards.
- Out of scope: changing override semantics, mutation_research behavior,
  manifest row formats, cache schema.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user directed "continue looking for ops"; profile
  evidence recorded.

## Steps / Checklist
- [ ] Inventory `overrides_plan` consumers (manifest compilers, caching
      staging + rehydration, runtime targeting/hot-swap) with evidence lines.
- [ ] Decide: (A) skip-build + None with consumer guards, (B) lazy build on
      first access (thread-safe thunk; verify model lifetime outlives plan
      access), or (C) alias to no_overrides_plan if consumers only read
      shared rows. Decision gated on the inventory.
- [ ] Implement + test drift; user validation.

## Validation
- Not run.

## Applicable Anti-Patterns
- [ ] No blind cut before the consumer inventory (override hot-swap is a
      real runtime feature; correctness outranks the ~20-30ms).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: true (next session should start from the
  consumer inventory step; this ticket carries the full evidence).

## Noting Behavior
- Note focus: consumer inventory evidence, decision rationale.

## Notes
- DATETIME: 2026-06-13T05:20:00Z
  TYPE: MEASURE
  CLAIM: Post-phase-8-cut synth-200 cold-conjure profile ranking (profiled
    0.331s): pickle.dumps 2000 calls/0.025s; _build_lane_plan_from_model
    400 calls (2 per spell -- the smoking gun)/0.035s cum;
    build_phase11_step_ir_row 1664/0.013s; check_cleaned 77,810 calls
    (389/spell, 0.006s self -- guard chatter, noted but NOT a target: the
    user's deterministic-cleanup discipline is a feature); cancellation
    is_set 15,429; lazy codegen imports inside first conjure 0.037s (by
    design -- import-wall tradeoff, intentional). NO remaining full-pool
    scans: sorted fell 162,688 -> 9,673, dict.get 211k -> 52k. Phase cum:
    p11 0.073 / p10 0.056 / p8 0.052 / p9 0.041. Static sweep confirms the
    validation strategies are all pass-cached (binding_resolution_cycle
    pool walk is error-path-only) and phases 9-11 iterate bounded
    occurrence graphs -- the residual exponent ~1.48 is mostly this doubled
    plan build plus per-spell constants, not a hidden pool scan.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:54-64
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1066-1070
  - benchmarks/testing_other_di/bind_conjure_cycle_profile.txt:153-252
  IMPACT: estimated -20-30ms cold conjure at 200 spells; proportional at
    any N; zero warm-lane effect (phase 10 never runs warm).
  NEXT: inventory `overrides_plan` consumers (grep overrides_plan across
    src + manifest compilers + caching system), then pick A/B/C.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T05:50:00Z
  TYPE: FACT
  CLAIM: Consumer inventory (grep `overrides_plan`, src-wide). THREE consumer
    classes: (1) cache staging `spell_codegen_creation_cache.py:178-192` is
    ALREADY None-tolerant -- skips the overrides subpackage when the plan is
    None; (2) per-family overrides codegen-creation steps consume plan rows
    (many_only_overrides_codegen_creation_step.py:66-173 and generalized
    siblings); (3) finalize creation-context steps HARD-REQUIRE the plan
    (many_only_finalize_creation_context_step.py:60-67 raises on None)
    because they unconditionally build the overrides EXECUTOR backing
    runtime override hot-swap. Conclusion: option A (skip+None) requires
    relaxing the finalize contract to build the overrides executor only
    when override targeting is live; option B (lazy thunk) preserves the
    hot-swap-anytime contract at the cost of keeping the model (or enough
    of it) alive past phase 10. The choice is a SEMANTIC decision about the
    override hot-swap contract -- escalated to the user, not made
    unilaterally.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:178-192
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:59-74
  IMPACT: decision input complete; ~20-30ms cold @200 still on the table.
  NEXT: user picks A (override-free graphs lose pre-armed hot-swap
    executors; they'd be built on first targeting event) or B (lazy build,
    contract preserved, lifetime work needed). Then implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T06:10:00Z
  TYPE: DECISION
  CLAIM: PARKED by user direction. The cut requires a semantic decision on
    the override hot-swap contract (pre-armed vs first-use build) that the
    user is not ready to make, and the savings are cold-lane-only and
    cache-amortized -- weakest risk/reward on the board. The consumer
    inventory (note above) is complete and remains the resume point.
    Compiler lane redirected to the construction-lane handoff from
    compiler_builder_0 (executor body, 76% of per-cycle meld cost).
  EVIDENCE:
  - tickets/tasks/completed/2026-06-12_warm_meld_fixed_cost_trim_task.md:278-302
  IMPACT: no code touched; zero rollback needed.
  NEXT: none until the user decides the hot-swap contract question.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Evidence-complete, implementation NOT started. Start at the consumer
inventory. The profile report lives at
benchmarks/testing_other_di/bind_conjure_cycle_profile.txt (synth-200,
post-phase-8-cut).
