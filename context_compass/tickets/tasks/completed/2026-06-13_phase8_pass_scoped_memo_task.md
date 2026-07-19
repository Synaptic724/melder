

# Task: Phase-8 pass-scoped memo (kill the cold-lane O(n^2))

## Metadata
- Task ID: TASK-2026-06-13-phase8-pass-scoped-memo
- Story: none (perf lane, evidence: synth-200 profile)
- Status: done
- Completed: 2026-06-13T04:40:00Z
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p1
- Created: 2026-06-13T03:40:00Z
- Updated: 2026-06-13T03:40:00Z

## Objective
Remove the dominant cold-lane quadratic found by the synth-graph benchmark:
`SpellOccurrenceGraphAnalyzerStrategy` rebuilt the full-pool spell walk and
the graph-wide topology/contract signature rows once PER SPELL (162,688
sorted calls, 211k dict gets, ~40% of cold conjure at 200 spells; disabled
conjure scaling exponent ~1.6-1.8 across 100/200/300). Memoize both in one
pass-scoped `analysis_pass_cache` dict, same lifetime contract as the
phase-3/phase-4 pass caches.

## Ticket Contract
- ENTRY_GATE: board row routes here; evidence in prior ticket MEASURE note.
- EXECUTION_BOUNDARY: occurrence analyzer strategy + analyzer + strategy base
  + compiler_phase_8 + spell_compiler + spell_compiler_system facades +
  the two creation-system plan factories + drifted unit test. NO scheduler /
  UnitOfWork / dev_ops / conduit files.
- DEPENDENCIES: synth benchmark mode (landed, prior ticket).
- EXIT_GATE: user re-runs synth 100/200/300 (exponent should drop toward ~1)
  + spellbook unit suite + component compiler suites green.
- FAILURE_ESCALATION: BLOCKER note if cached-graph reuse semantics change
  (fast key/signature tuple layout MUST stay byte-identical).

## Scope Boundaries
- In scope: pass-cache plumb + memoization + fast-key/signature dedupe.
- Out of scope: phase 9/10/11 internals, emit staging, scheduler chunking.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: fully validated. Disabled conjure -55% @200 spells
  (228.4->101.9ms) and -60% @300 (470.2->185.9ms); scaling exponent
  1.78->1.48; warm/bind/29-class regression-free; unit 2010 + component 391
  green. Residual milder superlinear term (~40ms headroom @300) noted for a
  future lane: phase 9-11 row work is the candidate set -- profile-first
  via synth-200 `--profile` cold-conjure attribution.

## Steps / Checklist
- [x] Strategy: memoize `phase8_spell_walk` + `phase8_graph_shape_rows`;
      split root-specific rows into `_build_root_blueprint_rows`; dedupe the
      twin fast-key/input-signature builders over one shared shape helper.
- [x] Plumb `analysis_pass_cache` (default None, fresh-build fallback):
      strategy base / analyzer / phase 8 / spell_compiler /
      spell_compiler_system; per-pass dict created in
      `phase_occurrence_plan_factory` + `phase_plan_group_factory`.
- [x] Test drift: direct fast-key call in
      test_spell_occurrence_analyzer_strategy.py routed through
      `_build_graph_shape_rows` (assertion tuple unchanged).
- [x] User validation round 1 (benchmarks + component suite green; 3 unit
      stub drifts fixed).
- [x] Unit suite re-run green (2010 passed, 1 xfailed).

## Validation
- 2026-06-13 user-run round 1:
  - Component suite: 391 passed.
  - Unit suite: 2007 passed, 3 signature-drift failures in MY surfaces
    (_AnalyzerStub, _StrategyProbe, phase-8 delegation expectation) -- all
    fixed (stub kwargs + `{"analysis_pass_cache": None}` expectation, same
    shape as the phase-3/4 lines). Re-run pending.
  - Synth 200: disabled conjure 228.4 -> 101.9ms (-55%); setup 246.3 -> 120.8.
  - Synth 300: disabled conjure 470.2 -> 185.9ms (-60%); setup 494.6 -> 210.8.
  - 200->300 conjure ratio 2.06x -> 1.82x (exponent ~1.78 -> ~1.48): the
    dominant quadratic is dead; a milder superlinear residual remains
    (candidates: phase 9-11 row work, first-meld manifest path).
  - No regressions: warm conjure unchanged (26.0 @200 / 37.9 @300), bind
    unchanged, 29-class warm setup 7.7ms, cold cache overhead @300 fell
    +12.3 -> +5.1ms.
  - Carried import check CLOSED: importtime tree shows zero
    mutation_research and zero __architecture__ rows; both deferrals work.
    Residual json (1.5ms) arrives via a different importer.

## Applicable Anti-Patterns
- [ ] No invalidation protocol on the pass dict (lifetime IS the pass).
- [ ] Key/signature tuple layout unchanged (cache-reuse correctness).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.

## Notes
- DATETIME: 2026-06-13T03:40:00Z
  TYPE: FACT
  CLAIM: Implementation landed. Three pass-invariant computations now build
    once per pass: the sorted full-pool spell walk (rows + occurrence rows +
    existence counts + a spell_id->existence dict for O(1) per-spell
    root_existence), and the graph-shape rows (topology + contracted +
    system_state) shared by fast key AND input signature -- which also
    removed ~110 lines of duplicated builder code. Safety: shared payloads
    are immutable tuples; SpellExistenceOccurrenceAnalysis is frozen and
    SpellOccurrenceGraphAnalysis.cleanup only dels its REFERENCE (verified),
    so cross-artifact sharing cannot poison; failures are never cached;
    worker races are benign (identical values, last write wins). Target-
    local revalidation path (single spell) left cache-less by design.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:134-180
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:342-433
  - src/melder/aether/spellbook/spellbook_creation_system.py:2800-2816
  - src/melder/aether/spellbook/spellbook_creation_system.py:3016-3030
  IMPACT: phase 8 falls to O(n) per pass on signature inputs; expected to
    remove the bulk of the cold-lane superlinearity (228ms disabled conjure
    at 200 spells should drop substantially).
  NEXT: user runs unit + component suites and the synth sweep; also still
    open from the prior lane: one importtime tree grep to confirm
    json/mutation_research no longer load at import.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Same proven pass-cache pattern as tasks #10/#22, applied to phase 8. The
sandbox mount truncates large host files (recurring artifact) -- all
verification host-side via Grep; user pytest is the gate.
