# Task: Measure normal Melder creation against constructor inputs and overrides

- Completed: 2026-09-26T13:45:56Z
- Summary: Measured 20-25% graph throughput and eager-construction evidence. Turned in by the owner in the 2026-09-26 board cleanup (row agent updater_1);
  no further work; artifacts retained as reference.

## Metadata
- Task ID: TASK-2026-09-24-measure-melder-creation-and-overrides
- Epic: EPIC-2026-09-24-override-execution-performance
- Status: done
- Owner: codex
- Agent Name: updater_1
- Priority: p1
- Created: 2026-09-24T09:27:42Z
- Updated: 2026-09-26T13:45:56Z

## Objective
Create and run one reproducible Melder-only experiment comparing normal creation and override shapes.
Use the supplied benchmarks as bases and establish evidence for later optimization investigation.

## Ticket Contract
- ENTRY_GATE: Parent epic exists first; active attention-board row routes to this task.
- EXECUTION_BOUNDARY: New experimentation file, source/benchmark reads, measured output artifacts and
  ContextCompass notes/boards. No production runtime or API changes.
- DEPENDENCIES: Supplied shallow and override benchmark files; configured Python runtime and pytest.
- EXIT_GATE: Correctness checks, repeated timings and interpretation delivered with runnable command.
- FAILURE_ESCALATION: Record runtime/environment blockers or noncomparable workloads before conclusions.

## Scope Boundaries
- In scope: tests/experimentation/test_melder_creation_overrides_performance.py and relevant source reads.
- Out of scope: Competitor timings, production optimizations, init={} implementation and build assets.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Unified experiment, both mode measurements and constructor-count evidence are ready.
- from_state: review
- to_state: done
- transition_reason: Owner turned in this dormant row in the 2026-09-26 shared-board cleanup (all 13 dormant rows,
  2026-09-26T13:45:56Z); closed by fable_0 with board and artifact sync.

## Steps / Checklist
- [x] Read relevant benchmark bases, experiment conventions and public override call paths.
- [x] Define matched case matrix and correctness checks; record timing methodology.
- [x] Implement the unified opt-in experiment.
- [x] Run correctness/smoke checks and repeated measurements.
- [x] Record results and the next concrete investigation question.

## Deliverables
- Unified experiment with configurable iterations/repeats and no competitor dependencies.
- Raw machine-readable measurements and readable comparison with environment/source provenance.
- Source-backed observations separating proven facts from optimization hypotheses.

## Files / Paths Impacted
- tests/experimentation/test_melder_creation_overrides_performance.py
- context_compass/artifacts/override_execution_performance_20260924/
- Parent epic, this task, attention_board.md, mailbox_board.md and artifact_board.md.

## Validation
- Contract checks: 6 passed. Automatic performance run: 7 passed in 14.58 seconds.
- Dynamic performance run: 7 passed in 14.60 seconds. Source hashes stable in each run.
- Ruff passed with UP045 excluded for the role's Optional typing requirement.
- Four positional/DI shapes rejected per mode and excluded transparently from timing.
- Constructor counts independently recorded for shallow/wide/deep. Full suite/coverage: Not run.

## Risks / Rollback Notes
- No production changes. Keep timings opt-in and isolate runtime/cache state per experiment.
- Another agent is editing cache versioning; record source identity before/after measured runs.

## Applicable Anti-Patterns
- [x] No performance assertion from a single sample or incomparable work.
- [x] No timing threshold in ordinary CI tests.
- [x] No claim that the speculative init={} API exists.

## Done Checklist
- [x] Experiment correctness verified with unsupported positional cases listed.
- [x] Repeated measurements retained and interpreted.
- [x] Runtime and source provenance recorded.
- [x] Owner-facing comparison and next investigation documented in findings.md.
- [ ] Owner accepts task closure.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/override_execution_performance_20260924/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Preserve baseline for future optimization comparisons.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Matched normal/override workloads and top-level argument cost.
- IF_UNKNOWN: none

## Noting Behavior
Record each completed investigation/measurement tranche with evidence, impact and one NEXT step.

## Notes
- DATETIME: 2026-09-24T09:27:42Z
  TYPE: PLAN
  CLAIM: Build a single Melder-only experiment using the supplied benchmark bases. Measure the
    reported slowdown before deciding whether top-level initialization needs a separate path.
  EVIDENCE:
  - Owner's current unified-experiment request.
  IMPACT: Work is limited to experimentation and investigation; no runtime optimization is approved yet.
  NEXT: Read the two benchmark bases and identify their Melder fixtures, call shapes and timing controls.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T09:31:57Z
  TYPE: FACT
  CLAIM: The supplied normal Melder benchmark binds graph nodes as Existence.many. The override
    suite instead treats solo as an existing unique object, uses flat a/l0 keys for shallow/wide,
    **leaf for diamond and an eight-edge path for deep. Its timed worker also performs clock/event
    checks, periodic validation and GC; the normal single-call timer uses a fixed iteration loop.
    The available .venv_new runtime is CPython 3.14.7 free-threaded with GIL disabled.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all.py:1171-1274
  - benchmarks/testing_other_di/test_shallow_all.py:1708-1752
  - benchmarks/testing_other_di/test_overrides_all.py:255-319
  - benchmarks/testing_other_di/test_overrides_all.py:546-765
  - .venv_new/pyvenv.cfg:1-5
  IMPACT: A unified loop must isolate transient creation, existing-object retrieval and override
    shapes. Reuse the base graph classes without executing competitor builders; add a scalar-root
    case where overriding its default preserves constructor work exactly.
  NEXT: Read public override dispatch and normalization, then implement the matched experiment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:34:56Z
  TYPE: DECISION
  CLAIM: Use solo/scalar/shallow/wide/diamond/deep transient graphs, warm public meld calls and
    matched fixed-loop samples. Separate None, empty dict/tuple, flat root mappings, full root
    positional inputs and nested selectors. Reused/fresh payloads distinguish caller allocation.
    Include direct Python root construction only as a labeled lower-bound control, not a Melder API.
    Source confirms empty dict misses the initial warm door before normalizing to None; tuples
    allocate a list plus __args__ mapping. No init={} or arbitrary constructor kwargs API exists.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:4417-4570
  - src/melder/aether/conduit/meld/conduit_meld.py:359-435
  - src/melder/aether/conduit/meld/conduit_meld.py:472-543
  - src/melder/aether/conduit/meld/meld.py:1506-1581
  IMPACT: The matrix can identify fast-door loss and separate payload handling from nested execution.
    Timing is opt-in, repeated with rotating order, with assertions and GC collection outside samples.
  NEXT: Implement and smoke-test the unified file, then run the full measured matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:40:15Z
  TYPE: FACT
  CLAIM: The unified experiment now defines six transient graph shapes, explicit root/nested/empty
    payload cases, contract checks, optional repeated timings and JSON/Markdown output. It preserves
    raw samples and source fingerprints, and never calls a competitor builder or changes runtime code.
  EVIDENCE:
  - tests/experimentation/test_melder_creation_overrides_performance.py:1-444
  - context_compass/artifacts/override_execution_performance_20260924/experiment.md:1-38
  IMPACT: Implementation is ready for correctness qualification. Timing and performance results are not yet claimed.
  NEXT: Run the experimental contract checks and scoped lint before timed sampling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T09:41:59Z
  TYPE: MEASURE
  CLAIM: Initial contract run passed solo/scalar and failed shallow positional root arguments:
    ShallowRootAB receives a positionally supplied a plus a generated keyword a. This case cannot
    be timed as successful override creation. Initial lint requested PEP 604 despite the selected
    role's Optional/Union requirement; retain that policy and exclude only lint rule UP045.
  EVIDENCE:
  - context_compass/artifacts/override_execution_performance_20260924/contracts.log:1-130
  - context_compass/artifacts/override_execution_performance_20260924/lint.log:1-100
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2677-2738
  IMPACT: Preserve this input-semantics observation without modifying production. Known positional
    duplicate-argument failures will be listed explicitly as rejected cases and excluded from timings;
    all other unexpected errors continue to fail the experiment.
  NEXT: Add transparent rejection reporting, fix import/style findings and rerun contract qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:43:36Z
  TYPE: MEASURE
  CLAIM: All six graph contract checks pass after known positional/DI rejections were separated
    from successful measured calls. Scoped Ruff passes with UP045 excluded to retain the role's
    required Optional typing. No production source changed. Performance has not yet been measured.
  EVIDENCE:
  - context_compass/artifacts/override_execution_performance_20260924/contracts_recheck.log:1-2
  - context_compass/artifacts/override_execution_performance_20260924/lint_recheck.log:1-1
  IMPACT: The successful call matrix is ready for timing, with rejection details kept visible in reports.
  NEXT: Run the automatic-frame repeated performance matrix and inspect source stability and sample spread.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-24T09:44:10Z
  TYPE: MEASURE
  CLAIM: Seven-test automatic run passes with stable runtime/source hashes and GIL disabled.
    Original fresh-map overrides measure 24.6% normal throughput shallow, 23.4% wide, 21.3%
    diamond and 20.4% deep. Scalar root input is 57.3%; empty dict retains 74-99% depending on
    graph size. Reused maps barely change the graph-override penalty. Four positional/DI cases
    are explicitly reported rejected and receive no timing value.
  EVIDENCE:
  - context_compass/artifacts/override_execution_performance_20260924/automatic/results.md:1-66
  - context_compass/artifacts/override_execution_performance_20260924/automatic/results.json
  - context_compass/artifacts/override_execution_performance_20260924/automatic_run.log
  IMPACT: The reported approximately fivefold gap is reproduced under one controlled harness.
    A root-only input specialization is worth investigating, but payload allocation is not enough
    to explain the result. Root-all deep input remains nearly as slow as nested overrides.
  NEXT: Count actual fixture constructor calls with separate profiling to test whether root-supplied
    dependencies avoid descendant construction; do not mix profiler timing with throughput figures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:46:59Z
  TYPE: MEASURE
  CLAIM: Separate cProfile constructor counting confirms that root-supplied inputs do not prune
    descendant construction in these cases. Normal, empty tuple, one root input, all root inputs
    and original override each execute 3 fixture constructors shallow, 9 wide and 511 deep per
    operation. Profiling used 128 warmed calls per case; source hashes remained stable.
  EVIDENCE:
  - context_compass/artifacts/override_execution_performance_20260924/constructor_counts.json
  - context_compass/artifacts/override_execution_performance_20260924/count_constructors.py:1-60
  IMPACT: Even both supplied top-level deep branches still incur all 511 constructor calls.
    This provides a concrete next investigation target: root-input specialization and descendant
    execution pruning, including disposal/hook semantics. Profiler elapsed times are not benchmark figures.
  NEXT: Qualify the optional dynamic-mode matrix separately, then deliver the baseline and investigation targets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-24T09:48:20Z
  TYPE: MEASURE
  CLAIM: Dynamic comparison also passes seven tests with stable source and GIL disabled. Original
    override throughput versus dynamic normal is 36.1% shallow, 30.7% wide, 30.5% diamond and 20.9%
    deep. Baseline findings and reproducible commands are recorded; production remains unchanged.
  EVIDENCE:
  - context_compass/artifacts/override_execution_performance_20260924/dynamic/results.json
  - context_compass/artifacts/override_execution_performance_20260924/dynamic_run.log
  - context_compass/artifacts/override_execution_performance_20260924/findings.md
  IMPACT: The first requested experiment is ready for owner review. The epic's next investigation
    is generated root-input execution and eager descendant construction, before an init={} API decision.
  NEXT: Review the baseline, then trace the generated many-only override executor and pruning semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Unified experiment and baseline are ready for review. Read artifacts/override_execution_performance_20260924/findings.md.
Automatic graph overrides reproduce 20-25% of normal throughput; dynamic ratios are also recorded.
All deep root inputs still construct 511 nodes. Four positional/DI cases are explicitly rejected.
No production changes. Continue the epic with source investigation of root-input specialization,
descendant construction and the semantics a possible init={} path would need to preserve.
