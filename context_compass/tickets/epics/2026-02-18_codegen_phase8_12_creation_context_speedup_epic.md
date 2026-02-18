# Epic: Codegen Phase 8-12 and Creation Context Throughput Acceleration

## Metadata
- Epic ID: EPIC-2026-02-18-codegen-phase8-12-creation-context-speedup
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-02-18T18:54:05Z
- Updated: 2026-02-18T18:54:05Z
- Target Window: 2026-Q1
- Related Program/Initiative: Codegen performance hardening

## Problem / Opportunity
Current codegen runtime cost is concentrated in the Phase 8-12 pipeline and in
creation-context execution paths used by fast and override routes. We need a
single coordinated lane that discovers hotspots holistically, then executes
phase-specific optimization tranches without breaking behavior contracts.

## MRP Alignment (Most Reasonable Product)
MRP outcome is a stable, repeatable optimization workflow that improves
throughput while preserving correctness and existing public contracts. The
minimum durable system includes:
- one active benchmark protocol with pinned P-core support,
- weighted scoring that prioritizes cProfile signal (75%) over wall time (25%),
- phase-scoped stories/tasks that can be executed independently.

## Ticket Contract
- ENTRY_GATE: active routing lane points to discovery task and epic story tree is created.
- EXECUTION_BOUNDARY: Phase 8-12 + creation_context codegen performance only.
- DEPENDENCIES: benchmark runner, p-core affinity helper, phase8-12 code paths.
- EXIT_GATE: all phase stories accepted and benchmark score gates satisfied.
- FAILURE_ESCALATION: raise DECISION_REQUEST on gate conflicts or scope growth.

## Goals (Outcomes)
- Build one evidence-backed discovery map for Phase 8-12 and creation_context.
- Establish story/task execution plan for each phase before implementation.
- Enforce weighted validation policy: 75% cProfile, 25% time.
- Track fast and override route means/medians for before/after comparisons.

## Non-Goals (Explicit Exclusions)
- No implementation edits in this planning tranche.
- No benchmark protocol replacement outside current runner surfaces.
- No public API changes.

## Scope Boundaries
- In scope:
  - `src/melder/spellbook/spell_crafter/spell_crafter.py` phase8-12 surfaces
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
  - `benchmarks/p_core_affinity/p_core_affinity.py`
  - phase12 executor blueprints
- Out of scope:
  - unrelated subsystem optimizations
  - architecture rewrites unrelated to phase8-12 codegen

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user requested a new active epic lane for codegen speedup.

## Success Metrics
- Holistic discovery note set completed with phase-by-phase evidence.
- Story/task tree exists for phases 8, 9, 10, 11, and 12.
- Validation plan explicitly requires weighted score gates:
  - cProfile weight: 0.75
  - time weight: 0.25
- Route metrics include means and medians for fast/override lanes.

## Requirements (Functional + Non-Functional)
- Functional:
  - produce hotspot inventory for phases 8-12 and creation_context execution,
  - define implementation sequence and guardrails per phase,
  - define per-story validation checklist and pass criteria.
- Non-functional:
  - preserve existing behavior and public contracts,
  - keep all tasks reviewable and phase-scoped,
  - keep benchmark runs deterministic via pinned core affinity.

## Constraints / Assumptions
- Benchmark runner currently reports route medians and weighted regression.
- Weighted routes default to root and override lanes.
- Means may require explicit aggregation additions in execution tasks.

## Dependencies / External References
- `benchmarks/testing_other_di/run_codegen_benchmark_deltas.py`
- `benchmarks/p_core_affinity/p_core_affinity.py`
- `src/melder/spellbook/spell_crafter/spell_crafter.py`
- `src/melder/aether/conduit/meld/creation_context/creation_context.py`

## Milestones (Track Progress)
- [ ] Milestone 1: holistic discovery map completed with evidence.
- [ ] Milestone 2: phase stories/tasks finalized and approved for execution.
- [ ] Milestone 3: implementation tranches complete and benchmark gates pass.

## Stories (Required to Complete)
- [ ] Story: STORY-2026-02-18-phase8-occurrence-plan-speedup
- [ ] Story: STORY-2026-02-18-phase9-injection-plan-speedup
- [ ] Story: STORY-2026-02-18-phase10-patch-map-speedup
- [ ] Story: STORY-2026-02-18-phase11-execution-plan-speedup
- [ ] Story: STORY-2026-02-18-phase12-creation-context-speedup

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-02-18-phase8-12-holistic-codegen-discovery
- [ ] Task: TASK-2026-02-18-phase8-occurrence-plan-optimization
- [ ] Task: TASK-2026-02-18-phase9-injection-plan-optimization
- [ ] Task: TASK-2026-02-18-phase10-patch-map-optimization
- [ ] Task: TASK-2026-02-18-phase11-execution-plan-optimization
- [ ] Task: TASK-2026-02-18-phase12-creation-context-optimization
- [ ] Task: Verify Ticket Microcycle enforcement across active tickets/stories/tasks.

## Acceptance Criteria (Epic Done)
- All five phase stories are accepted with closed tasks.
- Discovery produced one holistic hotspot map and ranked execution order.
- Validation rules are implemented and used for each optimization tranche.
- Weighted score report (75/25) and mean/median route metrics are present.

## Risks / Mitigations
- Risk: optimize wrong phase due to partial discovery.
  - Mitigation: complete holistic discovery before implementation.
- Risk: benchmark noise produces false improvement/regression.
  - Mitigation: pin P-cores and preserve identical sample/warmup counts.
- Risk: weighted policy drift.
  - Mitigation: enforce 0.75/0.25 config in validation tasks.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story-level evidence.
- [ ] No closure while required stories are incomplete or unaccepted.
- [ ] No program claims without source evidence from story/task notes.

## Validation / Test Approach
- Planning tranche: Not run.
- Execution tranche (future): use benchmark runner with pinned P-cores and
  weighted comparison against baseline.

## Rollout / Adoption Plan
- Discovery first, no code edits.
- Execute phase tasks in priority order after user approval.
- Re-run weighted benchmark comparisons after each tranche.

## Open Questions
- Should weighted route set also include `warm_spellspace_ns` and `warm_mixed_ns`?
- Should mean metrics be persisted in report schema v3 or a v4 extension?

## Decision Log
- 2026-02-18T18:54:05Z: Opened new epic lane for phase8-12 holistic speedup.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: epic closure

## Notes
- DATETIME: 2026-02-18T18:54:05Z
  TYPE: FACT
  CLAIM: Benchmark runner already enforces weighted scoring inputs with default
    75% cProfile and 25% time and includes root/override routes in defaults.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:353-359
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1100-1229
  IMPACT: Execution tasks can enforce user weighting policy without replacing
    benchmark infrastructure.
  NEXT: complete holistic discovery for phase8-12 and creation_context hotspots.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-02-18T18:54:05Z
  TYPE: PLAN
  CLAIM: Execute discovery as one cross-phase pass, then run phase-scoped
    implementation tasks with weighted validation gates.
  EVIDENCE:
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:810-840
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:1258-1346
  IMPACT: We avoid premature optimization and preserve traceability from
    hotspot evidence to implementation tranche.
  NEXT: populate story/task discovery findings with phase-level evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
Epic lane is open and routed for a discovery-first pass across phase8-12 and
creation_context codegen performance. Phase stories/tasks are created to stage
execution after user approval.
