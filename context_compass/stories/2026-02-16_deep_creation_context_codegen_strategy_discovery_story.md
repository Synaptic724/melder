# Story: Deep CreationContext Codegen Strategy Discovery

## Metadata
- Story ID: STORY-2026-02-16-deep-creation-context-codegen-strategy-discovery
- Epic: EPIC-2026-02-15-creationcontext-phase12-codegen-optimization
- Status: in_progress
- Owner: codex
- Priority: p1
- Created: 2026-02-16
- Updated: 2026-02-16

## User Narrative
As a runtime/codegen maintainer, I want deep structural analysis of
`creation_context_codegen.py`, so that we optimize code generation strategy
rather than only tuning runtime micro-branches.

## Value / MRP Alignment
This discovery lane targets generator architecture quality:
- template explosion risk,
- compile/exec lifecycle strategy,
- emitted-source reuse opportunities.

## Requirements (Functional)
- Audit template compile topology and route-key matrix depth.
- Identify high-confidence structural opportunities with measurable hypotheses.
- Document keep/defer risks before any implementation patching.

## Requirements (Non-Functional)
- No public API changes in this story.
- Evidence-first findings only; unknowns remain explicit.

## Scope Boundaries
- In scope:
- `src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py`
- Template selection, emitted-source construction, and compile strategy.
- Out of scope:
- Runtime behavior changes in `creation_context.py`.
- Non-CreationContext Phase12 emitters.

## Dependencies / Related Work
- `context_compass/epics/2026-02-15_creationcontext_phase12_codegen_optimization_epic.md`
- `context_compass/tasks/completed/2026-02-15_optimize_phase12_creationcontext_codegen_wave1_task.md`

## Tasks (Implementation Checklist)
- [ ] Map current template matrix and specialization dimensions.
- [ ] Quantify compile-time template fan-out and identify dedupe opportunities.
- [ ] Propose 2-3 deep strategy options with tradeoffs (lazy compile, merged templates, code-object caching).
- [ ] Define validation experiment plan for selected option.

## Acceptance Criteria
- Story documents at least three deep codegen findings with concrete evidence.
- At least two non-superficial strategy candidates are defined with tradeoffs.
- A measurable next-step experiment plan is recorded.

## Validation / Test Plan
- Discovery-only: no runtime edits in this story.
- Validation command recommendations for follow-on implementation:
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_fast_graphs_cprofile.py -q -s`
  - `$env:PYTHONPATH='src'; .\.venv_new\Scripts\python.exe -m pytest benchmarks/testing_other_di/test_melder_overrides_graphs_cprofile.py -q -s`

## Risks / Mitigations
- Risk: overfitting strategy to source shape without compile-frequency evidence.
  Mitigation: keep compile-frequency as explicit UNKNOWN until measured.
- Risk: reducing template count may reintroduce runtime branching.
  Mitigation: preserve branch-depth constraints as a non-functional gate.

## Open Questions
- What is the actual compile frequency of CreationContext templates per session?
- Which template dimensions can be merged without runtime regression?

## Decision Log
- 2026-02-16: Story opened per user direction to run deeper codegen discovery (not superficial or medium-level tuning).

## Notes
- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: CreationContext codegen compiles emitted template source through `compile(..., "exec")` + `exec(...)` for both overrides-only and no-overrides-only paths.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-315, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:329-358
  IMPACT: Compile strategy is dynamic-source based; deep optimization can target compile lifecycle and source reuse.
  NEXT: quantify fan-out and candidate compile-caching shapes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Module-level template constants compile a large static matrix of route/return/fast-mode combinations at import time.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1015
  IMPACT: Startup/import-time compile fan-out is a deep strategic lever not targeted by runtime micro-slices.
  NEXT: classify which matrix dimensions are semantically required versus mergeable.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: FACT
  CLAIM: Emitted template source is assembled as string line arrays and joined per template factory generation.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:372-420
  IMPACT: Structural source normalization/deduplication can be applied without changing public APIs.
  NEXT: draft candidate source-shape simplification options and expected performance impact vectors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATE: 2026-02-16
  TYPE: UNKNOWN
  CLAIM: Runtime compile-frequency and cache-hit behavior for CreationContext templates under real workloads is not yet measured.
  EVIDENCE: src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:289-315, src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:873-1015
  IMPACT: We cannot prioritize lazy-compile versus precompile strategy confidently without frequency data.
  NEXT: define instrumentation plan to measure compile invocations and first-use latency.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user

## Context / Handoff Summary
Deep discovery opened for `creation_context_codegen.py` focusing on compile
topology, template fan-out, and emitted-source strategy. Next step is option
design with measurable hypotheses before implementation.
