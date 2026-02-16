# Story: Deep Phase12 No-Overrides Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-phase12-no-overrides-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`phase12_no_overrides_executor.py`, so we improve generated-executor quality
instead of repeatedly pushing low-yield runtime micro-slices.

## Value / MRP Alignment
This lane targets emitter architecture and generated function shape:
- compile lifecycle,
- executor size/branch density,
- transient-vs-step-plan generation strategy.

## Requirements (Functional)
- Map compile/execution path for no-overrides emitters.
- Identify deep generated-shape costs (signature width, branch fan-out, per-step boilerplate).
- Propose strategy alternatives with explicit tradeoffs.

## Requirements (Non-Functional)
- Discovery-only, no runtime contract changes in this story.
- Keep UNKNOWN discipline for unevidenced runtime-frequency claims.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py`
- Step-plan and transient unrolled emitter paths.
- Out of scope:
- Overrides emitter internals.
- Non-codegen runtime API changes.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [ ] Quantify step-plan generated function growth versus plan size.
- [ ] Evaluate transient unrolled signature strategy and dependency-array prebind model.
- [ ] Define candidate generator strategies (shape-family split, cold-path extraction, selective helper fallback).
- [ ] Produce validation experiment plan and keep/revert criteria.

## Acceptance Criteria
- At least three deep findings are documented with evidence.
- At least two new strategy candidates are recorded with tradeoffs.
- A concrete experiment plan is documented for follow-on implementation.

## Validation / Test Plan
- Discovery-only in this story.
- Follow-on validation lanes (for implementation):
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_no_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Risks / Mitigations
- Risk: emitter simplification may increase runtime branching.
  Mitigation: preserve shape-specialization principles as hard constraints.
- Risk: optimization bias from benchmark noise.
  Mitigation: keep frozen-checkpoint deltas and repeated-cadence gates.

## Open Questions
- What plan sizes trigger generated-function quality degradation?
- Should transient and step-plan paths share more emitter infrastructure?

## Decision Log
- 2026-02-16: Story opened per user direction for deeper no-overrides codegen discovery.

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: No-overrides emitters compile generated source using `compile(..., "exec")` + `exec(...)` and require `_phase12_executor` to be callable.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:438-466
  IMPACT: Compile lifecycle strategy is a first-class optimization target, not just runtime helper internals.
  NEXT: evaluate whether code-object reuse/caching can reduce repeated compile overhead safely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Step-plan source emits one large monolithic executor with per-step locals and nested existence/lock routing blocks in generated code.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:469-520, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:523-725
  IMPACT: Generated-function size and branch density likely scale with step count, making code-shape strategy critical.
  NEXT: build size/branch metrics per generated executor to rank structural strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Transient unrolled source emits a very wide signature with many dependency arrays and an unrolled call-expression block with per-step exception index tracking.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:1257-1421
  IMPACT: Signature width and emitted-call expansion are deep strategic dimensions that were not the focus of prior micro-optimizations.
  NEXT: compare alternate unrolled-shape strategies (segmenting, split executors, cold-path helper extraction).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Current production compile frequency for step-plan vs transient emitters is not yet measured.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:55-147, src/melder/spellbook/spell_crafter/blueprints/phase12_no_overrides_executor.py:151-238
  IMPACT: Prioritization between compile-lifecycle and generated-runtime shape improvements remains uncertain without frequency data.
  NEXT: define instrumentation plan for compile path frequency and executor reuse rate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep no-overrides discovery opened with initial evidence on compile path, step
emitter size/branch density, and transient unrolled signature strategy. Next
step is option ranking with measurable hypotheses.
