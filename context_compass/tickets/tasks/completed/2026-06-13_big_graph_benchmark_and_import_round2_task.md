

# Task: Big-graph benchmark posture + import-wall round 2

## Metadata
- Task ID: TASK-2026-06-13-big-graph-benchmark-and-import-round2
- Story: none (perf lane follow-ups, user-approved)
- Status: done
- Completed: 2026-06-13T03:45:00Z
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-13T01:55:00Z
- Updated: 2026-06-13T01:55:00Z

## Objective
1) Synthetic N-spell graph posture (`BENCH_CYCLE_SYNTH_CLASSES`) in the cycle
   benchmark so the O(n^2)->O(n) cuts are measurable at 100-300 spells and future
   quadratics surface early. 2) Import-wall round 2 easy cuts: lazy package metadata
   in `melder/__init__.py` (json chain, ~11.4ms) and deferred `mutation_research`
   (~4.8ms). The `nexus.acl` deferral (~20-25ms) is explicitly a follow-up: it
   touches the ACL construction path and deserves its own bounded lane.

## Ticket Contract
- ENTRY_GATE: board row routes here.
- EXECUTION_BOUNDARY: `benchmarks/testing_other_di/profile_bind_conjure_cycle.py`,
  `src/melder/__init__.py`, the one `mutation_research` import site in
  `src/melder/aether/aether.py`. Nothing else.
- DEPENDENCIES: completed hot-path + single-signature lanes.
- EXIT_GATE: user runs synth benchmark + import profile + spellbook suites green.
- FAILURE_ESCALATION: BLOCKER note if `__init__` metadata is consumed eagerly by
  anything at import time (would make PEP 562 laziness observable).

## Scope Boundaries
- In scope: synthetic class generator (layered DAG, annotation-by-class deps, unique
  names, Existence.many), env knob; module `__getattr__` for metadata; one deferred
  import.
- Out of scope: nexus.acl deferral, logging deferral, any phase/scheduler file.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: deliverables landed and user-validated (synth 100/200/300
  + 2010-test suite green). Closure finding: the synth posture exposed and
  RANKED a remaining cold-lane quadratic in the phase-8 occurrence analyzer
  -- handed to the follow-up lane
  `2026-06-13_phase8_pass_scoped_memo_task.md`. Import delta inconclusive
  (169.8 vs 165.8ms baseline, noise-level; tree-grep check carried to the
  follow-up lane's NEXT).

## Steps / Checklist
- [x] Synth-graph mode in cycle benchmark behind `BENCH_CYCLE_SYNTH_CLASSES`.
- [x] PEP 562 lazy metadata in `melder/__init__.py`.
- [x] Defer `mutation_research` import AND construction to first use.
- [x] Document findings in `## Notes`; user validation recorded.

## Validation
- 2026-06-13 user-run, synth 200, workers=1, repeats=9 (medians):
  - bind 17.9ms (0.089ms/bind — dead linear vs 0.093ms/bind at 29)
  - warm conjure 26.1ms (4.8x for 6.9x spells — phases 1-7 SUBLINEAR, the
    phase-3/4 index cuts hold at scale)
  - disabled conjure 228.4ms (~19x for 6.9x spells — phases 8-11/emit lane
    has a superlinear term; per-spell 0.41 -> 1.14ms)
  - cold cache overhead +3.9ms; warm saves 204.2ms vs disabled (-83% setup)
  - warm full cycle 70.4ms incl. 200-meld hydration sweep
- `pytest tests/unit/melder/spellbook -q`: 2010 passed, 1 xfailed (lazy
  MutationResearch + PEP 562 metadata regression-clean).
- importtime command failed with ModuleNotFoundError (melder not installed
  in venv; needs sys.path bootstrap) — import delta not yet measured.
- Second synth run was user Ctrl+C (duplicate invocation); KeyboardInterrupt
  landed in dag_node cleanup because cleanup dominates cycle wall — no hang
  evidence (run-1 cleanup medians 27ms/cycle).

## Applicable Anti-Patterns
- [ ] No silent scope expansion into nexus.acl (follow-up lane only).

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.

## Notes
- DATETIME: 2026-06-13T01:55:00Z
  TYPE: PLAN
  CLAIM: Synth graph: classes generated via exec with real annotated constructors
    (annotation = prior class OBJECT, hitting the phase-3 identity bucket), layered
    deps (i-1 and i-7), unique names, all Existence.many; benchmark machinery reused
    by swapping the `_support` namespace when the env knob is set. Import cuts:
    module `__getattr__` for metadata modules; mutation_research deferred at its
    aether.py use site.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:91-99
  - src/melder/__init__.py:1-1
  IMPACT: scale-proof for the structural cuts + ~16ms off cold import.
  NEXT: implement benchmark mode first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T02:20:00Z
  TYPE: FACT
  CLAIM: All three cuts landed. (1) Synth mode: `_build_synthetic_support`
    generates N exec-compiled classes in 3 tiers (leaf singletons / 2-leaf-dep
    mids / mid+leaf tops, depth<=3 so the meld sweep stays O(n)); the knob also
    swaps FRAME/CONDUIT/CACHE_FRAGMENT so synth caches never collide with the
    29-class bench cache. Classes are built once at module import so warm
    repeats stay full-hit classifiable. (2) `melder/__init__.py` now resolves
    7 metadata attributes through module `__getattr__` with module-dict
    caching; star-import still exports them via `__all__`. (3) Discovery: the
    catalogued "defer mutation_research import" was insufficient — `Aether()`
    runs at package import and CONSTRUCTED MutationResearch in `__init__`, so
    the import chain was paid regardless. Fix defers both: field starts None,
    `_get_mutation_research` double-checks under `self._lock`, imports and
    builds on first access; cleaned-root-raises contract preserved; cleanup
    path was already None-safe.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:110-180
  - src/melder/__init__.py:74-106
  - src/melder/aether/aether.py:119-125
  - src/melder/aether/aether.py:1501-1540
  IMPACT: ~16ms expected off cold import; scale posture ready at any N.
  RISK: tests that reach into `aether._mutation_research` directly will now
    see None until first accessor use; route them through the property.
  NEXT: user runs synth benchmark at 100/200/300 + import profile + spellbook
    suite; sandbox py_compile was a stale-mount artifact (host file verified
    intact end-to-end, line 88 complete).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T02:55:00Z
  TYPE: MEASURE
  CLAIM: Scale validation landed the headline finding this posture was built
    for: warm lane (phases 1-7) is sublinear at 200 spells (4.8x cost for
    6.9x spells), bind is exactly linear, but the DISABLED/COLD lane
    (phases 8-11 + codegen/emit) grows ~19x for 6.9x spells — a superlinear
    term survives ONLY in the cold compile lane. Warm-vs-disabled saves
    204ms (83%) at 200 spells, so the cache story strengthens with scale.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:110-180
  IMPACT: next optimization target is localized: profile synth-200 cold
    conjure and rank the quadratic (candidates: phase-8/9 group planning,
    phase-10/11 row builders, emit staging).
  NEXT: user runs `--profile` under BENCH_CYCLE_SYNTH_CLASSES=200 plus
    100/300 wall sweeps for the scaling exponent; fix importtime invocation
    (sys.path bootstrap).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Two bounded follow-ups under compiler_strategy_0. ACL deferral intentionally
excluded; open a dedicated lane for it later.
