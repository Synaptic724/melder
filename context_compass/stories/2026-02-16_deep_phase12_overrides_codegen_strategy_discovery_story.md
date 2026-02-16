# Story: Deep Phase12 Overrides Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-phase12-overrides-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`phase12_overrides_executor.py`, so we improve override codegen strategy beyond
the hotspots already optimized in wave-1.

## Value / MRP Alignment
This discovery lane targets deeper generator decisions:
- compile pipeline shape (source/code-object/exec),
- shape-metadata inference complexity,
- inline kwargs/invoke emission scale and duplication.

## Requirements (Functional)
- Map core override compile pipeline and source-path alternatives.
- Identify generator complexity centers not addressed by prior slices.
- Propose deep strategy options with risk/benefit tradeoffs.

## Requirements (Non-Functional)
- Discovery-only in this story.
- Maintain UNKNOWN labeling for unevidenced cache-usage/frequency claims.

## Scope Boundaries
- In scope:
- `src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py`
- Core compile flow, shape-source emission, and prefilter cache hooks.
- Out of scope:
- No-overrides emitter internals.
- Public runtime contract changes.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [ ] Analyze core compile flow and source/code-object reuse boundaries.
- [ ] Quantify complexity of shape-metadata and inline kwargs/invoke emitters.
- [ ] Define strategy candidates (shape-family partitioning, generated-function size control, metadata precomputation lanes).
- [ ] Define benchmark/validation plan for follow-on implementation.

## Acceptance Criteria
- At least three deep findings documented with evidence.
- At least two strategy candidates documented with tradeoffs.
- Clear follow-on experiment plan recorded.

## Validation / Test Plan
- Discovery-only for this story.
- Follow-on validation commands (for implementation):
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook/spell_crafter/blueprints/test_phase12_overrides_executor.py -q`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`

## Risks / Mitigations
- Risk: reducing generated complexity could regress override correctness.
  Mitigation: keep root/override precedence contracts as non-negotiable gates.
- Risk: large emitter refactors lose reviewability.
  Mitigation: structure follow-on work into small strategy-specific slices.

## Open Questions
- Which parts of override generation dominate compile time vs runtime?
- Are prefilter caches effectively used by compile call sites today?

## Decision Log
- 2026-02-16: Story opened per user direction for deep overrides codegen strategy discovery.

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Core override compile flow supports source and code-object paths, builds per-step override targets, and executes compiled code with generated namespace binding.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:337-433
  IMPACT: Strategy work can target compile pipeline decisions (source reuse, code-object reuse, prefilter reuse) in addition to emitted runtime code shape.
  NEXT: map where compile callers can safely pass reusable caches/code objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Shape-source path performs heavy per-row metadata inference (existence resolution, callable/existing/disposal flags, target-count heuristics) before emitting specialized source.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:609-748, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:751-848
  IMPACT: Metadata inference complexity is a deep pre-emit optimization surface distinct from runtime helper micro-tuning.
  NEXT: evaluate metadata precomputation and reuse strategy candidates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Override emitter inlines large kwargs/invoke logic blocks, including dependency-missing error construction and positional-args decode paths, across generated step bodies.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:983-1490, src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:1540-1689
  IMPACT: Generated-function size and duplication are likely major strategic levers for further performance/maintainability gains.
  NEXT: define code-size control options (split emitters, helper extraction for cold/error paths, shape-family partitioning).
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Step-target prefilter logic supports external caches for per-step target tuples and path metadata.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587
  IMPACT: Compile-time reuse strategy can extend this cache model if call sites consistently pass stable cache keys/objects.
  NEXT: trace call sites to determine real cache utilization patterns.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Effective cache-hit rates for `prefilter_step_targets_cache` and `prefilter_path_metadata_cache` in production-like compile flows are not yet measured.
  EVIDENCE: src/melder/spellbook/spell_crafter/blueprints/phase12_overrides_executor.py:2516-2587
  IMPACT: Cache-expansion strategy cannot be prioritized confidently without usage measurements.
  NEXT: instrument compile call sites to capture cache usage and hit rate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep overrides discovery opened with evidence on compile pipeline, shape
metadata complexity, inline emitter size, and prefilter cache hooks. Next step
is strategy option ranking and measurement design.
