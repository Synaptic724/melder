

# Task: Optimize bind/conjure hot path (phases 1-11 + bind lane)

- Completed: 2026-06-13T00:35:00Z
- Summary: Bind + phases 1-11 hot path mined and validated. Warm setup 16.2 -> 8.4ms
  (-48%), warm conjure 11.5 -> 5.2ms (-55%), bind 4.5 -> 3.3ms, cold import
  237.7 -> 165.8ms, end-to-end warm process setup ~262 -> ~175ms. Cuts: AOT/JIT knob
  removal, ULID vendoring, phase-10/11 lazy imports, phase-2.5 dead-capture removal,
  phase-1 requirements borrow, v4 fingerprint (closed ctor-edit cache-staleness hole),
  phase-3 candidate index, phase-11 row memo (single-builder canonical), phase-4
  strategy pass-memos. 2,309 tests green in touched surface; remaining repo reds
  belong to mediator/spellspace lanes. Fresh profile confirms no quadratics remain;
  residual warm cost is real phase work + scheduler floor.

## Metadata
- Task ID: TASK-2026-06-12-optimize-bind-conjure-hotpath-phases-1-11
- Story: none (standalone performance lane)
- Status: done
- Owner: claude
- Agent Name: compiler_strategy_0
- Priority: p1
- Created: 2026-06-12T20:21:15Z
- Updated: 2026-06-13T00:35:00Z

## Objective
Drive melder process-setup and per-conjure cost down through evidence-backed cuts in the
bind lane and compiler phases 1-11, without touching parallel-agent lanes (phase
scheduler / UnitOfWork, transaction mediator, meld front door, pools/spellspace).

## Ticket Contract
- ENTRY_GATE: active `attention_board.md` row routes to this ticket; latest note carries
  the current measure baseline and next single step.
- EXECUTION_BOUNDARY: `src/melder/aether/spellbook/bind/`, `src/melder/aether/spellbook/
  spell_compiler/` (phases, examiner, requirements finder, codegen lanes),
  `src/melder/aether/spellbook/spellbook_creation_system.py`, `src/melder/utilities/helpers/`,
  matching unit/component/integration tests, and `benchmarks/testing_other_di/` harnesses.
- DEPENDENCIES: scheduler/UnitOfWork lane (other agent) shares conjure wall-time; mediator
  lane owns the 10 known change-control test failures; pools lane owns the spellspace
  cross-clear failure.
- EXIT_GATE: user confirms acceptance (benchmarks re-run green deltas, suites green except
  known parallel-lane failures) before status moves to done.
- FAILURE_ESCALATION: record `CONFLICT`/`BLOCKER` note if a cut requires touching an
  excluded lane file or changes a public contract (fingerprint schema, cache layout).

## Scope Boundaries
- In scope: bind reflection/fingerprint lane, compiler phases 1-11 bodies, conjure cache
  classification, import-cost reduction for these subsystems, benchmark instrumentation.
- Out of scope: `phase_scheduler.py`, `unit_of_work.py`, transaction mediator / change
  control, `meld.py`/`conduit_meld.py` runtime door logic, spell_space/pools/creations,
  nexus ACL deferral (flagged, not approved).

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: user accepted closure after the final profile review confirmed no
  remaining quadratics in phases 1-7 and all validation runs were green
  ("yeah go ahead and do that stuff", 2026-06-13).

## Steps / Checklist
- [x] Strip AOT/JIT `full_ahead_of_time_compilation` knob from src/tests/benches.
- [x] Build bind->conjure->resolution cycle benchmark + pytest wrapper.
- [x] Vendor ULID; lazy-load phase-10/11 codegen imports; meld.py import deferral.
- [x] Remove write-only phase-2.5 IR capture from phases 2/3/4/5.
- [x] Reuse bind-time requirements in phase 1 (borrow + ownership flag).
- [x] v4 fingerprint: ctor signature in, source preview out (lazy property).
- [ ] Investigate phase-3 annotation matching (1,827 `_matches_annotation` calls/pass).
- [ ] Task #9: phase-11 row-builder churn (enum .value + pickle.dumps, cold path).
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Faster warm/cold setup with unchanged contracts (cache skip, validation gating).
- `benchmarks/testing_other_di/profile_bind_conjure_cycle.py` + pytest wrapper.
- Persistent-gauntlet degradation-bucket mode with GC instrumentation.

## Files / Paths Impacted
- `src/melder/aether/spellbook/bind/bind.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/profiles/binding_profile.py`
- `src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py` (and 2/3/4/5/10/11)
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
- `src/melder/aether/spellbook/spellbook_creation_system.py`
- `src/melder/utilities/helpers/ulid_factory.py` (+13 ULID call sites)
- `src/melder/aether/conduit/meld/meld.py` (import deferral only)
- `benchmarks/testing_other_di/` (cycle profiler, persistent gauntlet buckets)
- Tests: spellbook unit suites, compiler phase suites, bind suites.

## Validation
- Run by user 2026-06-12: `tests/unit/melder/spellbook` 2007 passed (1 xfail);
  `tests/integration tests/component` 2243 passed, 11 failed (all parallel-lane:
  10 mediator API drift, 1 spellspace cross-clear).
- Recommended commands:
  - `.venv_new\Scripts\python.exe -m pytest tests/unit/melder/spellbook -q`
  - `.venv_new\Scripts\python.exe benchmarks\testing_other_di\profile_bind_conjure_cycle.py`

## Risks / Rollback Notes
- v4 fingerprint invalidates all existing `.melc` bundles once (intended; schema prefix).
- Borrowed requirements share one object between profile and artifact; ownership guarded
  by `_requirements_borrowed` (artifact never cleans borrowed state).
- Phase-2.5 capture helpers retained as future incremental-recompile seam.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No edits inside excluded parallel-agent lanes (scheduler, mediator, pools, meld door).

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: MEASURE
  CLAIM: Session-cumulative wall deltas (29-class gauntlet workload, gil=disabled): warm
    setup 16.2ms -> 9.5ms, warm conjure 11.5ms -> 6.2ms, bind 4.5ms -> 3.2ms, cold import
    237.7ms -> 165.8ms; real-world gauntlet setup 206ms -> 167.6ms.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:1-42
  - benchmarks/testing_other_di/bind_conjure_cycle_profile.txt:1-1
  IMPACT: the "200ms setup wall" is broken; remaining warm-conjure cost is phase bodies
    plus scheduler territory (other agent's lane).
  NEXT: re-run `--profile` after next cut to re-rank warm-conjure attribution.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: FACT
  CLAIM: Phase-2.5 codegen IR capture was write-only (no production reader) and discarded
    by `reset_phase2_5_codegen_ir` at end of each pass; the 7 eager call sites in phases
    2/3/4/5 were removed; capture helpers remain as a future seam.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:266-376
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:238-246
  IMPACT: removed 146 captures / 1,168 pickles / 3,796 hash updates per resolution pass on
    every posture; warm conjure dropped ~2.5ms.
  NEXT: none (landed; tests flipped to guard against reintroduction).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: FACT
  CLAIM: v4 fingerprint replaces first-5-lines source preview (docstring-sensitive,
    ctor-blind, only source-file IO on bind path) with `str(inspect.signature(cls))`;
    closes latent staleness hole where ctor edits could leave spell_id unchanged and let
    stale cache bundles full-hit.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:420-452
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:84-100
  IMPACT: bind -28%; all pre-v4 `.melc` bundles invalidate once by design.
  NEXT: none (landed; both hash-contract directions guarded in test_bind.py).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: FACT
  CLAIM: Phase 1 now borrows bind-time requirements (`spell.profile.resolution_profile.
    requirements`) with staleness guard on `spell_id` and ownership flag
    `_requirements_borrowed`, so conjure no longer re-reflects constructors.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:139-230
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:122-128
  IMPACT: removed 29 build_requirements + 87 inspect.signature calls per resolution pass,
    including deferred target-spell revalidation.
  NEXT: none (landed).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: RISK
  CLAIM: Two parallel-lane test-failure groups are NOT this lane's regressions: 10
    mediator/change-control failures (tests call `configure(change_control_mode=...)`,
    API absent in working tree) and 1 nested-spellspace cross-clear (scope D exit wipes
    scope C store; pools/spellspace files heavily rewritten uncommitted).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_fast_meld_door.py:711-717
  - src/melder/aether/conduit/spell_space/spell_space.py:1-1
  IMPACT: cross-clear is a correctness hole in nested scopes; needs the pools-lane owner.
  NEXT: user routes the cross-clear to the pools lane (or assigns it here explicitly).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-06-12T20:21:15Z
  TYPE: PLAN
  CLAIM: Next investigation tranche is phase-3 annotation matching: 1,827
    `_matches_annotation` + 63 `_resolve_single_by_annotation` calls per warm pass
    (candidate scan during binding resolution); after that, task-#9 phase-11 row-builder
    churn (cold path only).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:177-177
  - benchmarks/testing_other_di/bind_conjure_cycle_profile.txt:1-1
  IMPACT: largest remaining warm-conjure item inside this lane's boundary.
  NEXT: read `_build_local_frame_dag` candidate-scan loop and measure match-cache options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T20:48:00Z
  TYPE: FACT
  CLAIM: All four phase-3 resolvers full-scan `_spell_id_pool` once per dependency:
    `_resolve_single_by_annotation`, `_resolve_collection_by_annotation`, and both
    `_resolve_spellmap_default` branches iterate `_iter_all_spells` and apply per-spell
    predicates whose inputs (spell_name, spellframe, spell object, spell_type,
    binding_name) are pass-invariant. 63 single-resolves x 29 spells = the observed
    1,827 `_matches_annotation` calls per warm pass.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:283-290
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:336-343
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:402-419
  IMPACT: O(deps x spells) scan is the largest remaining warm-conjure item in this lane;
    scales quadratically with graph size, so the win grows for bigger user graphs.
  NEXT: implement pass-scoped candidate index (plan note below).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T20:48:00Z
  TYPE: PLAN
  CLAIM: Mirror the phase-4 `validation_pass_cache` plumb for phase 3: create
    `resolution_pass_cache` in `phase_local_frame_factory` (cf. validation factory's
    pass-scoped memo), thread through `run_phase_local_frame`, and build one lazy
    candidate index per pass: string buckets (spell_name, str-frame, class-frame
    `__name__`), identity buckets (`id(spell.spell)`, `id(frame)`), spellmap
    frame+binding bucket. Exactness guard: while building, mark `eq_risky=True` if any
    spell/frame type overrides `__eq__` (beyond str/type/object defaults); when risky,
    resolvers use the original full scan so custom-`__eq__` matching and
    multiple-candidate error semantics stay byte-identical. Deferred target-spell paths
    pass None and keep current behavior.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:2620-2650
  - src/melder/aether/spellbook/spellbook_creation_system.py:2652-2690
  IMPACT: 1,827 predicate calls collapse to ~63 dict lookups + one 29-spell index build
    per pass; no contract change on any error path.
  NEXT: thread the cache through spell_compiler_system -> spell_compiler ->
    CompilerPhase3.run, then implement the index in compiler_phase_3.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:05:00Z
  TYPE: FACT
  CLAIM: Phase-3 candidate index implemented. `phase_local_frame_factory` creates a
    pass-scoped `resolution_pass_cache`; threaded through `run_phase_local_frame`
    (system -> compiler -> CompilerPhase3.run) into `_build_local_frame_dag`. Index
    buckets: ann_str (spell_name / str-frame / class-frame name), ident (spell + frame
    identity), frame buckets reserved. `eq_risky` guard disables the index when any
    spell/frame type overrides `__eq__` (beyond str/type/object). Indexed lookups
    replicate scan dict semantics exactly, including first-insert-position /
    last-value-wins for version lineages sharing one SpellIndex. SpellMap resolver
    deliberately stays on the scan path (rare shape, inline `==` predicates). Deferred
    target-spell callers pass no cache and keep scan behavior.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:253-450
  - src/melder/aether/spellbook/spellbook_creation_system.py:2639-2662
  IMPACT: warm-pass annotation matching drops from 1,827 predicate calls to ~63 bucket
    lookups + one 29-entry index build; benefit scales with graph size.
  NEXT: user validation: phase-3 unit suite, full spellbook suites, cycle benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:25:00Z
  TYPE: MEASURE
  CLAIM: Candidate index validated. Warm conjure 6.18 -> 5.57ms median, warm setup
    9.50 -> 8.83ms, warm full cycle 16.39 -> 15.55ms; disabled conjure 20.6 -> 19.4ms
    and cold 21.7 -> 20.8ms (phase 3 runs on every posture). Suites: 2006/2007 unit
    passed; one drift in the compiler delegation test (phase-3 expectation lacked
    `resolution_pass_cache: None`, mirroring the existing phase-4 kwarg) fixed in the
    same pass. Integration/component: same 11 parallel-lane failures, nothing new.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py:138-139
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:1-42
  IMPACT: session-cumulative warm setup 16.2 -> 8.8ms (-46%); warm conjure
    11.5 -> 5.6ms (-52%, shared with compiler_builder_0's scheduler v2).
  NEXT: user re-runs the unit suite to confirm the delegation-test fix; then task #9
    (phase-11 row-builder churn, cold path) is the next tranche in this lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T21:55:00Z
  TYPE: FACT
  CLAIM: Task-#9 slice implemented. Phase-11 rows were rebuilt up to 3x per lane per
    cold pass (finalize step, conjure-end cache export, override specialization);
    rows are now memoized on `SpellGeneralizedCodegenLanePlan` (two slots: no-meta /
    with-meta) behind `SharedCompilerExecutions.get_phase11_step_ir_rows`, with
    getattr/setattr fallback so foreign plan families and stubs keep fresh-build
    behavior. The manifest's `CodegenCreationSchemaHelpers` stack is deliberately NOT
    routed through the memo (separate builder surface; sharing one memo could
    silently change manifest content if the builders drift). Latent footgun fixed:
    `_enrich_phase11_row` mutated shared rows in place against its own contract;
    enrichment now copies per call.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1004-1055
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:494-499
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/manifest/generalized_manifest.py:251-292
  IMPACT: cold-pass row churn (and its pickle/freeze cost) drops by roughly the
    duplication factor in the SharedCompilerExecutions lane; retired private helpers
    (`_build_override_plan_rows`, `_build_steps_rows`) remain defined but uncalled.
  NEXT: user validation: spell_compiler + spellbook suites, cache integration suite,
    cycle benchmark (cold posture is the one to watch).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T22:40:00Z
  TYPE: FACT
  CLAIM: Correction to the 21:55 note: there is only ONE phase-11 row-builder stack in
    the codegen lane. The cache export, finalize step, and overrides step all import
    `CodegenCreationSchemaHelpers` UNDER THE ALIAS `SharedCompilerExecutions`, which the
    user's validation run exposed (AttributeError in the overrides-step unit test). Fix:
    `get_phase11_step_ir_rows` relocated onto `CodegenCreationSchemaHelpers` (canonical),
    removed from the phases module (its builder is a legacy twin with zero production
    callers; NOTE comment left in place), and the manifest's two row builds now share the
    memo via zip+per-row enrich-on-copy — duplication is 4x -> 1x per lane.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/codegen_creation_schema_helpers.py:221-270
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation_cache.py:53-53
  IMPACT: the cross-stack-drift risk I designed around does not exist among these
    consumers; memo now provably serves one builder.
  NEXT: user re-runs unit suite (overrides-step test) + cycle benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T22:40:00Z
  TYPE: RISK
  CLAIM: Benchmark drift between runs is concentrated where plan_group executes: cold
    conjure 20.8 -> 22.9ms and disabled 19.4 -> 20.5ms medians, while warm (plan_group
    skipped) moved only +0.26ms. compiler_builder_0's PLAN_GROUP_CHUNK_MULTIPLIER=2
    landed between the runs, measured at workers=5; the cycle benchmark runs workers=1,
    where extra chunks are pure dispatch/latch overhead. My row memo cannot add cost
    (it only removes builds) and the new overrides-step path was not exercised by the
    gauntlet (no crash pre-fix). Hypothesis owner: scheduler lane.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:97-98
  - codex/context_compass/attention_board.md:27-27
  IMPACT: workers=1 cold-path regression ~+1-2ms if confirmed; suggest gating the
    multiplier by worker count (multiplier=1 when workers==1).
  NEXT: user runs cycle benchmark with BENCH_CYCLE_WORKERS=5 as discriminator; route
    confirmation to compiler_builder_0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T23:05:00Z
  TYPE: MEASURE
  CLAIM: Task-#9 validated: 2,308 spellbook unit+integration tests green including the
    overrides-step test (alias fix confirmed). Workers=1: warm setup 8.73ms / warm
    conjure 5.41ms (best numbers hold). Workers=5 discriminator: cold conjure 11.19ms
    and disabled 9.73ms (excellent — chunking wins where tuned), while workers=1
    cold/disabled remain ~+1-1.6ms over pre-multiplier baseline. Hypothesis confirmed
    directionally: the multiplier overhead is workers=1-only; recommend the scheduler
    lane gates PLAN_GROUP_CHUNK_MULTIPLIER to 1 when workers==1. Bonus finding: warm
    setup barely parallelizes (8.73 -> 8.45ms at w=5), so warm is now serial-floor +
    bind dominated; cold setup at w=5 is 14.5ms.
  EVIDENCE:
  - benchmarks/testing_other_di/profile_bind_conjure_cycle.py:97-98
  - codex/context_compass/attention_board.md:27-27
  IMPACT: lane backlog fully mined. Session totals (w=1 medians): warm setup
    16.2 -> 8.7ms (-46%), warm conjure 11.5 -> 5.4ms (-53%), bind 4.5 -> 3.3ms,
    import 237.7 -> 165.8ms, end-to-end warm process setup ~262 -> ~175ms.
  NEXT: lane idle pending user direction; ticket ready for acceptance walk-through
    when the user wants to close it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T23:30:00Z
  TYPE: FACT
  CLAIM: Phases 1-7 review tranche opened. Static sweep: four phase-4 per-spell
    strategies do full-pool work per spell (O(n^2) per pass): circular_dependency,
    contract_provider_presence, dangling_dependency, duplicate_spell_name. The
    pass-scoped `validation_pass_cache` is already threaded into their context
    (task-#10 plumb); they simply do not use it yet. Phase-6 strategies iterate
    frame-wide once each (O(n)) — lower priority.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:1-1
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py:1-1
  IMPACT: same shape as the phase-3 index win; candidate shared artifacts: name->ids
    map, pool id-set, contract_key->providers map, shared dependency graph.
  NEXT: fresh `--profile` (user) to weight the four; read each strategy and design the
    shared artifacts before any edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T23:55:00Z
  TYPE: FACT
  CLAIM: Phase-4 O(n^2) tranche implemented: three per-spell strategies now memoize
    their pass-invariant artifacts in the existing `validation_pass_cache` —
    duplicate_spell_name (name->collisions map), circular_dependency (frame adjacency;
    deps final after phase-3 group barrier), contract_provider_presence
    (contract_key->provider-ids map; store guarded so a None-spellbook context can
    never poison the cache). dangling_dependency was a false positive (already O(deps)
    dict lookups). All three fall back to the original per-spell scans when no pass
    cache is supplied (deferred single-spell paths). Issue content and ordering are
    byte-identical on every path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/duplicate_spell_name_strategy.py:79-110
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/circular_dependency_strategy.py:70-90
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/contract_provider_presence_strategy.py:89-115
  IMPACT: phase-4 pool scans drop from 3x29 full builds to 3 builds per pass; warm and
    cold both benefit (validation runs on every posture).
  NEXT: user validation: spellbook unit suites + cycle benchmark; fresh `--profile`
    afterward to re-rank what remains in phases 1-7.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-13T00:25:00Z
  TYPE: MEASURE
  CLAIM: Phase-4 memo tranche validated: 2,309 green; warm conjure 5.41 -> 5.21ms,
    warm setup 8.38ms (cold medians this run were machine-noise contaminated; mins
    consistent with prior baselines). Fresh `--profile` shows NO remaining quadratics
    in phases 1-7: phase-3 index live (1 build, 63 lookups), phase-4 walks on shared
    graphs, remaining warm cost = real work (phase-3 dag/topology, phase-5
    `_overlay_sockets_and_index` 0.002s self under profiler, phase-4 strategy walks)
    + scheduler floor + chatter (2,160 cancel checks, 8,320 check_cleaned, 1,718
    RLock cycles ~= 0.5-1ms real combined). Cold-stage profile carries the deferred
    phase-10/11 module imports (~34ms inflated, one-time per process, by design).
    UNKNOWN: cold `build_phase11_step_ir_row` count unchanged at 492 pre/post memo —
    plausibly many_only/solo-family plans (no memo slots) or the pre-fix duplication
    lived across the twin builder classes; cold-only, low value, not investigated.
  EVIDENCE:
  - benchmarks/testing_other_di/bind_conjure_cycle_profile.txt:1-1
  IMPACT: phases 1-7 are mined at this graph size; further cuts are micro
    (chatter/overlay) with rising risk. Index/memo wins compound on larger graphs.
  NEXT: recommend acceptance walk-through + commit; future perf lanes: bigger-graph
    benchmark (100-300 spells), import-wall round 2 if cold-start optics matter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Active perf lane owned by `compiler_strategy_0` (executor: claude / Cowork). Landed this
session: AOT/JIT knob removal, cycle benchmark suite, gauntlet degradation buckets, ULID
vendoring, phase-10/11 lazy imports, phase-2.5 capture removal, phase-1 requirements
borrow, v4 fingerprint. Suites green except 11 known parallel-lane failures (mediator,
spellspace). Next single step: phase-3 annotation-matching investigation. Excluded lanes:
scheduler/UnitOfWork, mediator, meld door, pools/spellspace, nexus ACL deferral.
