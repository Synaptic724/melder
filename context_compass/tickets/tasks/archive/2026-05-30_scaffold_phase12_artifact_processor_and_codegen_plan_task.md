# Task: Scaffold Phase12 Artifact Processor And Codegen Plan

## Metadata
- Task ID: TASK-2026-05-30-scaffold-phase12-artifact-processor-and-codegen-plan
- Story: none
- Status: in_progress
- Owner: codex
- Agent Name: spellspace_0
- Priority: p0
- Created: 2026-05-30T21:27:07Z
- Updated: 2026-05-31T12:30:26Z

## Objective
Land the first real Phase 12 implementation slice by adding the compiler-owned
artifact fields, scaffolding the Phase 12 processor and codegen-plan classes,
and wiring `CompilerPhase12` / compiler facades so placeholder processor state
and placeholder codegen plans are built and stored on `SpellCompilerArtifact`.

## Ticket Contract
- ENTRY_GATE: the active Phase 12 design task and epic already define the class
  model, the ownership split, and the requirement that this slice stay scoped
  to Phase 12 only.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
  - `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
  - `src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py`
  - new Phase 12 support files under:
    - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
    - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - direct Phase 12 unit tests under
    `tests/unit/melder/spellbook/spell_compiler/phases/`
  - active ticket and patch docs for this slice
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md`
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/architecture_patch.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_spell_compiler_artifact.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_phase12_scaffold.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_spell_compiler_facade.md`
- EXIT_GATE:
  - `SpellCompilerArtifact` owns Phase 12 processor-state and codegen-plan fields
  - the Phase 12 class scaffold exists with rich docstrings
  - `CompilerPhase12` builds/stores placeholder processor state and placeholder
    codegen plan
  - `SpellCompiler` and `SpellCompilerSystem` delegate to the new scaffold
  - focused Phase 12/compiler tests are green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the scaffold requires Phase 13
  rewrites or `CreationContext` consumer changes to land coherently.

## Scope Boundaries
- In scope:
  - Phase 12 artifact fields
  - Phase 12 class scaffold
  - Phase 12 compiler wiring
  - focused unit tests for the new scaffold
- Out of scope:
  - Phase 13 emitter redesign
  - `CreationContext` consumer rewrite
  - concrete strategy-family implementation
  - broad runtime behavior changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved beginning implementation and
  asked to start with the scaffold plus plan in bounded steps.

## Steps / Checklist
- [x] Create the Phase 12 patch-doc lane and link it from this task.
- [x] Add Phase 12 artifact fields and cleanup/reset handling on `SpellCompilerArtifact`.
- [x] Scaffold `SpellCodegenModel`, `SpellArtifactProcessorBuilder`,
      `SpellArtifactProcessorStrategy`, and `SpellArtifactProcessor`.
- [x] Scaffold `SpellCodegenPlan`, `SpellCodegenPlanBuilder`, and
      `SpellCodegenPlanStrategy`.
- [x] Wire `CompilerPhase12`, `SpellCompiler`, and `SpellCompilerSystem` to
      build/store placeholder processor state and placeholder codegen plan.
- [x] Add/update focused Phase 12/compiler unit tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- one bounded Phase 12 implementation scaffold
- one compiler-owned Phase 12 processor-state field on `SpellCompilerArtifact`
- one compiler-owned Phase 12 codegen-plan field on `SpellCompilerArtifact`
- one wired `CompilerPhase12.run(...)` that stores both outputs

## Files / Paths Impacted
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py`
- `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler.py`
- `src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py`
- `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
- `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py`

## Validation
- Not run.
- Recommended commands:
  - `python -m py_compile src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py src/melder/aether/spellbook/spell_compiler/spell_compiler.py src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py`
  - `pytest -q tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py`

## Risks / Rollback Notes
- Risk: the scaffold leaks Phase 13 assumptions back into Phase 12.
- Risk: the processor state becomes a shallow profile bag instead of the full
  artifact-consuming surface the user wants.
- Rollback: remove the new Phase 12 fields/files and restore the placeholder
  no-op phase if the scaffold proves incoherent.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into Phase 13 or `CreationContext` consumer rewrites in this slice.
- [ ] No closure without acceptance confirmation and board-sync completion.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/architecture_patch.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_spell_compiler_artifact.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_phase12_scaffold.md`
  - `system_docs/patches/active/phase12_artifact_processor_and_codegen_plan_scaffold/component_patch_spell_compiler_facade.md`
  - `artifacts/2026-05-30_phase12_north_star_runtime_model.md`
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: after patch merge and closure sync

## Noting Behavior
- Note focus: tactical scaffold findings, ownership consequences, and the next
  concrete implementation step.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-31T12:30:26Z
  TYPE: FACT
  CLAIM: The contract analyzer now owns the last direct occurrence seam.
    `SpellOccurrenceContractAnalyzerStrategy` no longer imports or calls
    `OccurrencePlanBuilder`; it now carries analyzer-owned contract payload
    compilation logic and publishes the same
    `SpellOccurrenceContractAnalysis` artifact without proxying the old Phase 8
    builder. At this point, graph, order, instance/sharedness, and contract
    payload compilation all live directly on the 4 occurrence strategies.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:1-331
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-965
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:1-164
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:1-218
  IMPACT: The occurrence analyzer lane is now structurally honest. The next
    work is no longer "extract one more occurrence seam"; it is to assess what
    `OccurrencePlan` should become as a compatibility artifact and which
    downstream consumer should be converted next.
  NEXT: perform the assessment and identify the first downstream consumer or
    compatibility cut after the 4-strategy migration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T12:29:14Z
  TYPE: FACT
  CLAIM: The contract analyzer now owns contract payload compilation directly.
    `SpellOccurrenceContractAnalyzerStrategy` no longer imports or calls
    `OccurrencePlanBuilder`. It now carries its own
    `_compile_contract_overrides(...)`,
    `_compile_contract_overrides_for_occurrence(...)`,
    `_iter_spell_contract_defaults(...)`,
    `_resolve_spell_contract_spell_id(...)`,
    `_collect_contracted_contract_candidates(...)`,
    `_normalize_contract_override_payload(...)`,
    `_record_contract_override(...)`, and
    `_allow_missing_contract_providers(...)` logic and publishes the same
    `SpellOccurrenceContractAnalysis` artifact from analyzer-owned code.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:1-380
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1690-1906
  IMPACT: The 4 occurrence strategies now own their core seams directly:
    graph expansion, execution ordering, instance/sharedness planning, and
    contract payload compilation. The remaining role of `OccurrencePlan` is now
    compatibility/output ownership, not strategy execution ownership.
  NEXT: assess the full lane and decide which downstream consumer should be
    converted next or whether `OccurrencePlan` should become a compatibility-only
    synthesized output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T12:26:45Z
  TYPE: FACT
  CLAIM: The instance analyzer now owns instance/sharedness planning directly.
    `SpellOccurrenceInstanceAnalyzerStrategy` no longer imports or calls
    `OccurrencePlanBuilder`. It now carries its own `_is_shared_existence(...)`,
    `_occurrence_sort_key(...)`, `_build_instance_plan(...)`,
    `_instance_key_for_occurrence(...)`, and
    `_select_canonical_occurrence(...)` logic and publishes the same
    `SpellOccurrenceInstanceAnalysis` artifact from analyzer-owned code instead
    of proxying the old Phase 8 builder.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:1-218
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1622-1688
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1920-1959
  IMPACT: The analyzer now owns three real occurrence seams instead of two:
    graph expansion, execution ordering, and instance/sharedness planning.
    The remaining direct `OccurrencePlanBuilder` proxy seam is contract payload
    compilation.
  NEXT: port `_compile_contract_overrides(...)` ownership into
    `SpellOccurrenceContractAnalyzerStrategy` and stop there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T12:22:49Z
  TYPE: FACT
  CLAIM: The order analyzer now owns execution-order construction directly.
    `SpellOccurrenceOrderAnalyzerStrategy` no longer imports or calls
    `OccurrencePlanBuilder`. It now carries its own deterministic
    `_occurrence_sort_key(...)` and `_build_execution_order(...)` logic and
    publishes the same `SpellOccurrenceOrderAnalysis` artifact from analyzer-
    owned code instead of proxying the old Phase 8 builder.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:1-164
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:810-873
  IMPACT: The analyzer now owns two real occurrence seams instead of one:
    graph expansion and execution ordering. The remaining direct
    `OccurrencePlanBuilder` proxy seams are now instance/sharedness and
    contract payload compilation.
  NEXT: port `_build_instance_plan(...)` ownership into
    `SpellOccurrenceInstanceAnalyzerStrategy` without widening into contract
    payload work yet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T12:20:15Z
  TYPE: FACT
  CLAIM: The first real occurrence-plan extraction seam is now landed in the
    graph analyzer. `SpellOccurrenceGraphAnalyzerStrategy` no longer imports or
    calls `OccurrencePlanBuilder`. It now owns the graph-expansion logic
    directly, including:
    - shared-occurrence collapse decisions
    - occurrence-graph expansion
    - ordered-node extension
    - topology dependency expansion
    - DAG fallback dependency expansion
    - SpellContract dependency expansion
    - mutation override dependency rewrites
    The strategy still reuses the Phase 8 fast-key/input-signature helpers for
    parity, but the actual occurrence-graph construction is now analyzer-owned.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-965
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:663-809
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:919-1718
  IMPACT: The analyzer is no longer fully faking the migration. One real piece
    of Phase 8 ownership has moved out of `OccurrencePlanBuilder`.
  NEXT: decide whether the next graph-side cleanup should split contract-edge
    expansion and mutation-override rewriting into narrower analyzer-owned
    helpers or move directly to the order strategy extraction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T12:11:52Z
  TYPE: MEASURE
  CLAIM: The first analyzer-facade contract slice is now coherent. The
    analyzer strategy interface now requires a stable `strategy_id`, the 4
    occurrence strategies each expose the exact ids the facade chain asks for,
    and `SpellAnalyzerStrategyBuilder` now registers those strategies by
    `strategy_id` instead of by class-name strings. That means the analyzer is
    now structurally what it claims to be: a facade that asks for named
    strategies and executes them in order.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:104-135
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy.py:49-71
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy_builder.py:59-88
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:67-71
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:42-46
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:47-51
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:43-47
  IMPACT: We can now start the real extraction work without hiding behind a
    broken registry contract. The next slice can target occurrence-graph logic
    ownership directly instead of wasting another turn on facade plumbing.
  NEXT: move `_build_occurrence_graph` and `_extend_occurrence_graph_with_ordered_nodes`
    ownership out of `OccurrencePlanBuilder` and into the graph analyzer
    strategy or analyzer-owned helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T12:05:01Z
  TYPE: FACT
  CLAIM: The processor and planner builder contracts are now stripped back to
    match the analyzer-builder shape instead of returning runtime objects
    directly. `SpellArtifactProcessorStrategyBuilder` and
    `SpellCodegenPlanStrategyBuilder` are now registry holders only:
    `_load_defaults`, `get_strategy`, `get_strategies`, and
    `registered_strategy_names`. The processor-construction behavior now stays
    on `SpellArtifactProcessor`, and the plan-construction behavior now lives
    on the new `SpellCodegenPlanner` orchestrator instead of leaking out of
    the strategy builder.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-114
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-84
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-114
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-157
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-91
  IMPACT: The renamed packages no longer fake a strategy-builder contract while
    still acting like factories. Later strategy growth can now happen behind
    the same registry shape as the analyzer lane.
  NEXT: when we come back to behavior work, add real default strategies or
    explicit strategy-chain selection without putting build semantics back on
    the strategy builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T12:05:01Z
  TYPE: MEASURE
  CLAIM: Narrow syntax validation passed for the strategy-builder refactor
    slice, but the focused Phase 12 pytest ring is still blocked during module
    collection by an unrelated import-time `NameError` in
    `src/melder/aether/spellbook/bind/scan.py` where `Spellbook` is used in a
    runtime annotation without being bound.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-114
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:1-114
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-157
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-91
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-225
  - src/melder/aether/spellbook/bind/scan.py:220-220
  IMPACT: The refactor parses cleanly, but I cannot truthfully claim the
    focused pytest ring passed because collection stops before it reaches the
    touched tests.
  NEXT: leave the builder slice as-is and only touch the unrelated scan import
    bug if you want that broader collection blocker cleared explicitly.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T11:56:56Z
  TYPE: FACT
  CLAIM: The renamed builder surfaces under `artifact_processor/` and
    `codegen_planner/` are still too thin and misaligned with their own module
    names. `spell_artifact_processor_strategy_builder.py` defines
    `SpellArtifactProcessorBuilder`, and
    `spell_codegen_plan_strategy_builder.py` defines `SpellCodegenPlanBuilder`.
    Both classes are only tuple wrappers around ordered strategies and `build()`
    calls. They do not provide a real strategy-registry surface like the newer
    analyzer builder does, so the packages still lack explicit strategy
    registration/resolution semantics.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:11-85
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy_builder.py:15-136
  IMPACT: Before more concrete processor or plan strategies are added, these
    builders should become actual registry-backed strategy builders so the
    package contract matches the renamed module identity and later strategy
    growth does not collapse back into positional tuple plumbing.
  NEXT: rework both builders into registry-backed strategy builders with
    deterministic name resolution and preserve the current `build()` behavior as
    the default "use all registered strategies in order" path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T11:51:55Z
  TYPE: MEASURE
  CLAIM: The first honest cleanup slice is landed. The 4 occurrence analysis
    classes now live under `spell_analyzer/data`, `SpellCompilerArtifact` and
    the 4 occurrence strategies now import them from that package, `py_compile`
    passed for the touched files, and there are no remaining imports pointing
    at the old flat `spell_analyzer.spell_occurrence_*_analysis` paths.
    Behavior was intentionally left unchanged in this slice.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_graph_analysis.py:1-69
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_order_analysis.py:1-33
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_instance_analysis.py:1-59
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_occurrence_contract_analysis.py:1-53
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-12
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:1-9
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:1-12
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:1-9
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:7-18
  IMPACT: The analyzer now has the package boundary you asked for, and the
    remaining fake migration work is narrowed to the strategies still calling
    private `OccurrencePlanBuilder` methods rather than owning the split
    behaviors themselves.
  NEXT: choose the first real extraction slice and replace direct
    `OccurrencePlanBuilder` calls in one occurrence strategy with analyzer-owned
    helper logic while keeping parity visible.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T11:48:24Z
  TYPE: FACT
  CLAIM: The current occurrence-analyzer migration is still a parity shim, not
    a real ownership migration. The 4 occurrence analyzer strategies do split
    output artifacts, but they still call directly back into private
    `OccurrencePlanBuilder` behavior for the core work:
    `_build_occurrence_graph`, `_build_execution_order`,
    `_build_instance_plan`, and `_compile_contract_overrides`. On top of that,
    the 4 occurrence analysis classes still live flat under
    `spell_analyzer/` while the intended `spell_analyzer/data/` package is
    currently empty.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:30-137
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:23-68
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:27-109
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:24-79
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:512-548
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:663-809
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:810-881
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1622-1688
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1690-1788
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_graph_analysis.py:1-69
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_order_analysis.py:1-33
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_instance_analysis.py:1-59
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_contract_analysis.py:1-53
  IMPACT: Simply claiming Phase 8 is migrated would be false. The first honest
    cleanup slice is to move the 4 analysis data classes into the intended
    `data/` package and repair imports, while keeping the remaining
    `OccurrencePlanBuilder` extraction work explicit.
  NEXT: move the 4 occurrence analysis classes into `spell_analyzer/data`,
    update artifact and strategy imports, and leave behavior unchanged in this
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T11:21:55Z
  TYPE: FACT
  CLAIM: The new `SpellAnalyzerStrategyBuilder.load_defaults()` implementation
    is too manual. It instantiates and inserts each default occurrence
    strategy one by one instead of using one small registration path over a
    deterministic default class list, which is noisy and low-quality for a
    builder whose whole job is strategy registration.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy_builder.py:1-120
  IMPACT: The builder contract is right now, but the implementation quality is
    not. This should be cleaned before more analyzer groups are added.
  NEXT: refactor the builder to use one registration helper and one default
    strategy class loop, then rerun the focused analyzer ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T11:07:52Z
  TYPE: FACT
  CLAIM: The occurrence analyzer lane now matches the agreed shape. The old
    single occurrence strategy is gone. In its place, the analyzer now uses 4
    real strategies under the `spell_analyzer/strategies/` folder:
    - `SpellOccurrenceGraphAnalyzerStrategy`
    - `SpellOccurrenceOrderAnalyzerStrategy`
    - `SpellOccurrenceInstanceAnalyzerStrategy`
    - `SpellOccurrenceContractAnalyzerStrategy`
    `SpellAnalyzerBuilder` now owns a plain default strategy dictionary keyed
    by strategy id through a dedicated defaults loader, and
    `SpellAnalyzer.analyze_occurrence(...)` chains the 4 occurrence strategy ids
    explicitly in order against that registry.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-143
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_builder.py:1-100
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1-212
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_order_analyzer_strategy.py:1-74
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_instance_analyzer_strategy.py:1-98
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_contract_analyzer_strategy.py:1-90
  IMPACT: The analyzer now has the actual 4-strategy medium split we agreed on
    instead of one monolithic occurrence strategy plus data-object rationalization.
  NEXT: carry the same pattern forward when we split injection, patch, and
    execution-shape analysis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T11:07:52Z
  TYPE: MEASURE
  CLAIM: The corrected 4-strategy occurrence analyzer plus plain default
    registry slice passed the narrow analyzer/artifact validation ring.
    `py_compile` passed for the touched analyzer files and the focused pytest
    ring passed `34` tests with the same existing pytest cache warning only.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-179
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-248
  IMPACT: The occurrence analyzer is now stable enough to use as the template
    for later analyzer groups.
  NEXT: move to the next analyzer group only after deciding whether injection,
    patch, or execution-shape should be next.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T10:54:36Z
  TYPE: FACT
  CLAIM: The analyzer registry surface now matches the intended contract more
    closely. `SpellAnalyzerBuilder` now owns grouped default strategy
    registries in a dictionary and installs the occurrence analyzer strategy by
    default under the `occurrence` group. `SpellAnalyzer` now exposes
    `analyze_occurrence(...)` as the explicit method surface for that group
    instead of only one generic analyzer loop. The abstract strategy contract,
    the builder, and the occurrence analyzer strategy now also carry deeper
    contract-first docstrings that explain the builder/registry/analyzer split,
    the occurrence strategy's migration role, and the artifact publication
    rules.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-102
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_builder.py:1-76
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy.py:1-78
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_analyzer_strategy.py:1-283
  IMPACT: The analyzer lane now has both a real default registry entrypoint
    and clearer API/docs for how later analyzer groups should be added.
  NEXT: keep the same grouped-registry plus explicit analyzer-method pattern
    when adding injection, patch, and execution-shape analyzer groups.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T10:54:36Z
  TYPE: MEASURE
  CLAIM: The analyzer docstring/default-registry slice passed the same narrow
    validation ring. `py_compile` passed for the touched analyzer files and the
    focused pytest ring for the occurrence analyzer plus artifact lifecycle
    tests passed `34` tests with the same existing pytest cache warning only.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-124
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-248
  IMPACT: The analyzer registry/docstring cleanup is stable enough to use as
    the template for the next analyzer group.
  NEXT: move to the next analysis group only after deciding whether the next
    lane is injection, patch, or execution-shape.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T10:46:55Z
  TYPE: PLAN
  CLAIM: The next bounded slice is analyzer-default wiring plus documentation
    hardening. The occurrence analyzer lane now has the right artifact names,
    so the next step is to make `SpellAnalyzerBuilder` construct the occurrence
    analyzer strategy by default and deepen the docstrings on the occurrence
    strategy and occurrence-analysis artifact classes so the analyzer contract
    is explicit before we add later analysis lanes.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_builder.py:1-53
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_analyzer_strategy.py:1-232
  IMPACT: This makes the new analyzer lane usable out of the box and raises
    the API/documentation quality bar before more strategies land.
  NEXT: patch builder defaults, enrich docstrings, then rerun the same narrow
    validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T10:46:55Z
  TYPE: FACT
  CLAIM: The first occurrence-analysis slice no longer carries temporary
    `phase8a` artifact naming. The compiler artifact now stores proper
    long-lived occurrence-analysis surfaces:
    - `_occurrence_graph_analysis`
    - `_occurrence_order_analysis`
    - `_occurrence_instance_analysis`
    - `_occurrence_contract_analysis`
    plus the generic cache/profile companions:
    - `_occurrence_analysis_input_signature`
    - `_occurrence_analysis_fast_key`
    - `_occurrence_analysis_shape_profile`
    The analyzer artifacts and tests were updated to the same naming so this
    lane now reads like normal compiler-owned analysis rather than a temporary
    branch label.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:41-517
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_graph_analysis.py:1-37
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_order_analysis.py:1-34
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_instance_analysis.py:1-52
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_contract_analysis.py:1-47
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_analyzer_strategy.py:1-232
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-130
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-248
  IMPACT: The occurrence-analysis lane now looks like a real compiler surface
    we can keep, extend, and later consume, rather than a temporary phase-name
    placeholder.
  NEXT: continue the same naming posture for the later injection/patch/execution
    analysis slices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-31T09:37:42Z
  TYPE: FACT
  CLAIM: The first real `8a` convergence slice is landed. `SpellCompilerArtifact`
    now owns explicit `8a` occurrence-analysis slots and cleanup/reset support:
    graph, order, instance, and contract analysis artifacts plus the Phase 8a
    shape profile, input signature, and fast-key cache fields. The new
    `SpellOccurrenceAnalyzerStrategy` ports current Phase 8 through the new
    analyzer lane and splits the result into:
    - `SpellOccurrenceGraphAnalysis`
    - `SpellOccurrenceOrderAnalysis`
    - `SpellOccurrenceInstanceAnalysis`
    - `SpellOccurrenceContractAnalysis`
    It currently reuses the existing Phase 8 builder/signature/profile helpers
    for parity, but stores the split analysis artifacts on the compiler
    artifact instead of building a new model or plan.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:41-491
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_graph_analysis.py:1-85
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_order_analysis.py:1-46
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_instance_analysis.py:1-64
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_contract_analysis.py:1-58
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_occurrence_analyzer_strategy.py:1-232
  IMPACT: We now have the first parallel replacement seam for old Phase 8 that
    is split into medium-grain analyzer artifacts and can be extended without
    forcing the later model or planner to absorb raw occurrence details.
  NEXT: Decide whether the next slice is wiring this strategy into
    `SpellAnalyzerBuilder` defaults or moving immediately to the Phase 9a
    injection-analysis split with the same pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T09:37:42Z
  TYPE: MEASURE
  CLAIM: The narrow validation ring for the Phase 8a occurrence-analysis slice
    is green. `py_compile` passed for the modified artifact/analyzer/test files,
    and the focused pytest ring for the new occurrence analyzer strategy plus
    the updated artifact lifecycle tests passed `33` tests with the same
    existing pytest cache warning only.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_occurrence_analyzer_strategy.py:1-108
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler_artifact.py:1-233
  IMPACT: The new `8a` artifact slots and occurrence analyzer strategy are
    stable enough to extend in the next convergence slice.
  NEXT: Keep the next slice equally narrow instead of widening into
    multi-phase convergence all at once.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T09:29:52Z
  TYPE: FACT
  CLAIM: Current Phase 8 already exposes natural internal seams for strategy
    extraction. The builder flow is:
    1. occurrence graph expansion
    2. ordered-node extension for non-root visible nodes
    3. execution-order derivation
    4. instance/shared/canonical occurrence derivation
    5. contract-override payload compilation
    Under that, occurrence dependency collection itself breaks into:
    - topology dependency expansion
    - DAG fallback dependency expansion
    - SpellContract provider dependency expansion
    - mutation-override dependency rewrites
    So Phase 8 can be split in more than one way:
    - coarse split: one `SpellOccurrenceAnalyzerStrategy` producing one
      `SpellOccurrenceAnalysis`
    - medium split: `OccurrenceGraph`, `OccurrenceOrder`,
      `OccurrenceInstances`, `OccurrenceContracts`
    - fine split: separate strategies for topology expansion, DAG fallback,
      contract-provider analysis, mutation-override analysis, graph assembly,
      order derivation, and instance/sharedness derivation
    The medium split is the first clean target if we want multiple artifacts
    without exploding the first implementation slice.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:512-573
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:663-809
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:810-878
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1022-1207
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1583-1736
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:1738-1847
  IMPACT: We do not need to choose between "one giant phase8a blob" and "too
    many tiny strategies." The code already gives us a reasonable medium-grain
    strategy/artifact decomposition.
  NEXT: recommend the medium split and define names for the resulting Phase 8a
    artifacts before any implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T09:29:52Z
  TYPE: PLAN
  CLAIM: The next bounded convergence slice is `Phase 8a` only. The goal is to
    extend `SpellCompilerArtifact` with explicit occurrence-analysis slots,
    add one analyzer-owned occurrence analysis artifact plus one concrete
    analyzer strategy, and keep old Phase 8 alive in parallel while the new
    analyzer lane starts producing the same kind of upstream truth in a
    cleaner compiler-owned form.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-524
  IMPACT: This keeps the convergence work small and testable instead of mixing
    Phase 8a-11a together in one change.
  NEXT: patch `SpellCompilerArtifact`, add the new Phase 8a occurrence-analysis
    artifact and strategy, then validate that narrow slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T09:37:42Z
  TYPE: MEASURE
  CLAIM: The `spell_analyzer` cleanup slice is now aligned to analyzer semantics
    instead of copied processor semantics. The three files now expose only:
    - `SpellAnalyzer`
    - `SpellAnalyzerBuilder`
    - `SpellAnalyzerStrategy`
    The analyzer consumes `Spell` + `SpellCompilerArtifact`, the builder only
    carries ordered analyzer strategies, and the strategy contract is now
    `analyze(spell, artifact) -> None`. The copied processor/model assessment
    baggage is removed from that folder. A narrow `py_compile` pass on those
    three files succeeded.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-76
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_builder.py:1-53
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy.py:1-59
  IMPACT: The analyzer lane is now a clean extension seam for adding
    post-phase-7 analysis artifacts without carrying processor/model language
    or behavior into that folder.
  NEXT: wait for the next concrete analyzer artifact requirement before adding
    behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T09:29:52Z
  TYPE: FACT
  CLAIM: The intended `spell_analyzer` role is now explicit and different from
    the processor. It is the artifact-enrichment stage that runs after
    phases `1-7`: it consumes `Spell` plus the existing `SpellCompilerArtifact`,
    computes deeper analysis outputs we may need for planning later, and writes
    those analysis artifacts back onto `SpellCompilerArtifact`. It does not
    build `SpellCodegenModel` and it does not choose the final codegen plan.
  EVIDENCE:
  - user_instruction
  IMPACT: The three copied `spell_analyzer` files should be stripped back to
    analyzer semantics only: builder holds analyzer strategies, analyzer
    consumes spell + artifact, strategy mutates/enriches artifact analysis
    state. Any copied processor/model logic in that folder is wrong.
  NEXT: patch the three `spell_analyzer` files to remove processor/model
    semantics and leave them as the correct analyzer scaffolds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T09:29:52Z
  TYPE: MEASURE
  CLAIM: The narrow `spell_analyzer` rename slice is landed. The three copied
    files are now:
    - `spell_analyzer.py`
    - `spell_analyzer_builder.py`
    - `spell_analyzer_strategy.py`
    and the classes/imports/docstrings inside that folder now use
    `SpellAnalyzer`, `SpellAnalyzerBuilder`, and `SpellAnalyzerStrategy`
    consistently. No wider model/planner refactor was mixed into this slice.
    A narrow `py_compile` pass on those three files succeeded.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:1-282
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_builder.py:1-69
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer_strategy.py:1-66
  IMPACT: The new analyzer lane now has the correct local identity and can be
    used as the next narrow extension point without carrying the old processor
    names inside that directory.
  NEXT: stop at this rename slice and wait for the next concrete analyzer
    requirement before widening further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T09:29:52Z
  TYPE: FACT
  CLAIM: The new `spell_analyzer` folder currently contains a straight copy of
    the three processor surfaces, but they still carry the old
    `SpellArtifactProcessor*` names and still import the processor/strategy
    classes from `artifact_processor` instead of using local `spell_analyzer`
    identities. The folder contains only those three files and no copied model,
    which matches the requested starting point for the rename-only cleanup.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_artifact_processor.py:1-282
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_artifact_processor_builder.py:1-69
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_artifact_processor_strategy.py:1-66
  IMPACT: The next narrow code slice is just a local rename/identity cleanup:
    rename the three files/classes/imports to `SpellAnalyzer`,
    `SpellAnalyzerBuilder`, and `SpellAnalyzerStrategy` without widening into
    model or planner work.
  NEXT: patch the three `spell_analyzer` files and rename them on disk.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-31T09:09:37Z
  TYPE: FACT
  CLAIM: The live `8-11` artifacts make the replacement target clearer. Phase
    8 is not just graph counts; it produces a path-aware occurrence runtime
    selection layer: execution order, occurrence graph, instance-key planning,
    canonical shared occurrences, root instance key, and SpellContract payload
    routing. Phase 9 is the per-instance call-wiring layer: `InjectionSpec`
    stores param-source wiring, dependency keys, list aggregation, positional
    override usage, and contract payloads. Phase 10 is the override/mutation
    targeting layer: override targets grouped by TargetSpec plus specificity,
    and mutation edge rewires grouped by TargetSpec. Phase 11 is the old
    execution recipe layer: `ExecutionPlanStep` and `ExecutionPlan` carry
    creations target kind, dependency wiring, override match metadata,
    contract payload metadata, lock/register hints, and the fast/fast-transient
    arrays. So if Phase 12 is going to absorb `8-11`, it must absorb these
    four planning sections, not just a handful of scalar families.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:120-391
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:405-573
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:120-246
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:348-461
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:486-692
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:76-289
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:540-715
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:885-1081
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:83-377
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:380-1026
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:1043-1954
  IMPACT: The convergence problem is not "replace one plan object." It is
    "replace four layered planning artifacts with one cleaner processor/model
    plus planner split."
  NEXT: define the new `SpellCodegenModel` as a normalized planning IR with
    phase-8 occurrence, phase-9 injection, phase-10 patch, and phase-11
    execution-recipe sections, while still keeping it separate from the raw
    artifact bag.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T09:09:37Z
  TYPE: DECISION
  CLAIM: The current tiny `SpellCodegenModel` scaffold is too thin for the real
    replacement goal. It works as a first selector-only scaffold, but if Phase
    12 is going to converge `8-11`, the model has to become a normalized
    planning IR rather than only a family-label bag. The right split is:
    `SpellCompilerArtifact` remains the raw truth store; `SpellCodegenModel`
    becomes the distilled planning IR; `SpellCodegenPlan` becomes the chosen
    lane plan built from that IR. That means the model should grow four
    explicit normalized sections:
    - occurrence section from current Phase 8
    - injection section from current Phase 9
    - patch section from current Phase 10
    - execution-recipe section that replaces current Phase 11 step plans
    The planner can then emit a current-behavior-compatible combined plan with
    three lanes:
    - no-overrides
    - overrides
    - overrides-with-mutations
    so we can test the new mode against the current architecture before we
    delete the old phases.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:6-214
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-155
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:16-141
  - src/melder/aether/spellbook/spell_compiler/blueprints/occurrence_plan.py:120-573
  - src/melder/aether/spellbook/spell_compiler/blueprints/injection_plan.py:348-692
  - src/melder/aether/spellbook/spell_compiler/blueprints/patch_maps.py:76-1081
  - src/melder/aether/spellbook/spell_compiler/blueprints/execution_plan.py:83-1954
  IMPACT: The next implementation slice should not just append more scalar
    counters to the current model. It should redesign the model around
    normalized planning sections that can actually replace the old pipeline.
  NEXT: write the convergence model into the retained direction artifact and
    spell out the exact proposed `SpellCodegenModel` sections plus the initial
    current-compatible `SpellCodegenPlan` shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T08:06:23Z
  TYPE: MEASURE
  CLAIM: The current benchmark evidence reinforces why the new processor /
    planner stack should become authoritative instead of staying a thin layer
    above the old planning pipeline. The depth-9 hotpath benchmark measures
    per-phase conjure timings and shows that the current later compiler path is
    a major part of total conjure cost: `root_blueprints` took `13.037ms`,
    `execution_plan` took `4.708ms`, and `executor_compile` took `18.246ms`
    out of `51.567ms` total conjure time. That does not make Phase 11 alone
    the single slowest named phase in this sample, but it does show that the
    old planning/backend stack is expensive enough to justify replacing it with
    a better processor/planner model.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:49-49
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:134-147
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py:203-227
  - user_benchmark_output
  IMPACT: The scaffold should be treated as the seed of the replacement
    planning stack, not as a permanent adapter over the existing `8-11` flow.
  NEXT: update the epic and retained artifacts to state the migration model
    explicitly: extend the new processor/planner until it is authoritative,
    then replace the old `8-11` planning path and remake the current Phase 13
    emitter around the chosen plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T08:06:23Z
  TYPE: DECISION
  CLAIM: The current working migration model is now explicit: keep extending
    the new `artifact_processor` and `codegen_planner` stack properly, allow
    it to spend meaningful compiler work deriving a stronger model from earlier
    compiler truth when that produces better plan selection, and then replace
    the old `8-11` planning stack instead of letting the new model permanently
    depend on old execution-plan outputs. After that, the current Phase 13
    surface should be remade as a pure emitter over the chosen plan.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-524
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:37-240
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:35-243
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:595-880
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:80-94
  IMPACT: The next model/strategy work should not optimize around consuming the
    old `8-11` plan artifacts forever. It should optimize around becoming the
    replacement planning architecture.
  NEXT: update `SpellCodegenModel` and the first real processor strategies with
    only the selectors that matter for plan choice, while treating the old
    planning phases as temporary migration oracles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T00:00:44Z
  TYPE: FACT
  CLAIM: The runtime consumer seam is still exactly where the user has been
    pushing. `Spell` owns the compiler artifact plus the spell-owned
    `CreationContextFactory`, `CreationContext`, switch, and the remaining
    runtime-facing bits (`resolution_required`, `resolution_complete`,
    `requires_spellspace_request`, `execution_plan_dispatch_route`). The
    artifact owns the raw compiler truth through Phase 11 plus the new Phase 12
    model/plan slots. `CreationContextBuilder` is still selecting route family,
    fast-transient eligibility, no-overrides executor binding, override patch
    map binding, and override route config construction from those artifacts.
    `CreationContext` itself still owns the override specialization runtime:
    specialization cache, emitted-source/code-object caches, last-shape hot
    reuse, and override executor compile-on-miss. The compiler facades confirm
    the current orchestration order is still `1-11 -> Phase 12 scaffold ->
    Phase 13 no-overrides executor compile`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:194-228
  - src/melder/aether/spellbook/spell.py:353-377
  - src/melder/aether/spellbook/spell.py:566-679
  - src/melder/aether/spellbook/spell.py:991-1033
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:81-98
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:149-166
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:77-98
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:115-245
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:170-181
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:273-379
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:585-725
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1150-1331
  - src/melder/aether/spellbook/spell_compiler/spell_compiler.py:726-872
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:442-525
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:908-1007
  IMPACT: The next Phase 12 design move should stay artifact-first and model-
    first, but it also has to be honest about what is still downstream today:
    route selection and override-specialization logic have not been lifted yet,
    they are only scaffolded around.
  NEXT: return to the Phase 12 model discussion with the live seam in hand and
    decide which remaining selectors truly belong in `SpellCodegenModel`
    versus which downstream runtime decisions should later be absorbed by real
    processor and planner strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-31T00:00:44Z
  TYPE: FACT
  CLAIM: The current compiler already gathers a large share of the raw plan-
    selection truth before Phase 12. Phase 1, 8, 9, 10, and 11 each write
    compiler-owned shape profiles or reuse signatures onto the artifact, while
    Phase 11 is still the real execution-plan builder: it caches the
    no-overrides / overrides / overrides-with-mutations plan variants, computes
    the Phase 11 execution shape profile, stamps the dispatch route onto
    `Spell`, and stores the Phase 11 -> Phase 13 handoff signature and
    transient schema. The current Phase 12 scaffold is therefore sitting above
    a compiler that already knows most of the raw planning truth; it is not
    replacing an empty slot.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_1.py:43-155
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:45-524
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:37-240
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:35-243
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:595-880
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:80-94
  IMPACT: The next model/strategy work should treat Phase 12 as a distillation
    and plan-composition layer over already-computed compiler truth, not as a
    second raw-planning phase or a fresh artifact-mirroring layer.
  NEXT: read `creation_context`, `spell.py`, `spell_compiler_artifact.py`,
    `spell_compiler.py`, and `spell_compiler_system.py` to map which current
    downstream consumers still reinterpret that truth after Phase 11.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T23:33:41Z
  TYPE: FACT
  CLAIM: `SpellCodegenModel` is now the first real distilled model instead of a
    second artifact bag. It no longer stores raw artifact groups or spell
    metadata bags. The processor now consumes the current artifact truth and
    derives selector fields such as:
    - `build_kind`
    - `existence`
    - `route_family`
    - graph shape fields and `graph_family`
    - call shape fields and `call_shape_family`
    - override geometry fields and `override_shape_family`
    - `fast_transient_eligible`
    Existing-creation now short-circuits to `build_kind=existing_creation`
    with no construction-planning shape.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:6-211
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:15-262
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:16-210
  IMPACT: The model is now aligned to the intended role: distilled planning
    selectors only. The next strategy tranche can build on a real model instead
    of a renamed artifact mirror.
  NEXT: define exactly which of these selector fields are final and which more
    derived fields should still be added by the first real processor
    strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T23:33:41Z
  TYPE: MEASURE
  CLAIM: The distilled-model correction passed the same narrow syntax and
    focused pytest ring after the test seed was updated to provide the graph
    shape inputs the new selector model actually uses.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:46-96
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:99-160
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py:1-127
  IMPACT: The scaffold now has a stable, passing baseline for the distilled
    model before the first real strategy tranche lands.
  NEXT: move from model-shape cleanup into real processor strategy
    implementation.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T23:14:51Z
  TYPE: FACT
  CLAIM: The builder role is now corrected in live code. The processor builder
    no longer consumes artifacts or builds the model; it is now just a
    strategy-registry factory that returns a configured
    `SpellArtifactProcessor`. The processor itself now consumes the spell and
    compiler artifact, builds the `SpellCodegenModel`, and runs the processor
    strategies. The codegen plan builder now mirrors that posture on the plan
    side: it owns the ordered plan strategies and builds the plan from an
    already-finished model.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_builder.py:11-78
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:15-220
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:16-238
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:83-94
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:98-172
  IMPACT: The scaffold now matches the intended conceptual split more closely:
    builders assemble registries/factories, processors consume artifacts and
    build models, and the plan builder consumes the finished model.
  NEXT: define the exact `SpellCodegenModel` fields we actually want to keep
    and start the first real processor strategies on top of that contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T23:14:51Z
  TYPE: MEASURE
  CLAIM: The builder-role correction passed the same narrow syntax and focused
    pytest ring, and added one extra passing test for the builder-factory
    contract.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:166-172
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py:1-127
  IMPACT: The conceptual correction did not destabilize the current scaffold.
  NEXT: move to the exact model-field conversation instead of more scaffold
    role cleanup.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T22:53:32Z
  TYPE: DECISION
  CLAIM: The processor-state scaffold name is being corrected from
    `SpellCodegenModel`. The processor is
    artifact-first and is building the normalized model the planner will later
    consume, so the new name matches its real role better than the old
    state-heavy naming.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:6-171
  IMPACT: The live scaffold code, tests, and current task/patch docs need to
    switch to the new name before the next tranche defines the exact model
    fields.
  NEXT: rename the class/file/imports and repair the active scaffold docs to
    the new model name.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:48:14Z
  TYPE: DECISION
  CLAIM: The likely later compiler-phase end-state is now explicit: the current
    scaffolded Phase 12 responsibilities will eventually split into two real
    stages. The artifact processor side should likely become the new Phase 11
    because it is the precursor-to-shape normalization layer, while Phase 12
    should remain the actual codegen-plan selection/build stage. That later
    split is not part of the current scaffold slice, but it is the correct
    long-term phase map if the new model fully replaces the current
    execution-plan builder.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:730-880
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:19-86
  IMPACT: We should treat the current `artifact_processor/` and
    `codegen_planner/` split as semantically stronger than the current compiler
    phase numbering, because the numbering will likely be realigned later once
    the new model is proven.
  NEXT: Keep the implementation scaffold package names stable and avoid
    overfitting them to the current phase number while the later phase
    realignment is still ahead.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:37:52Z
  TYPE: FACT
  CLAIM: The dedicated north-star runtime artifact now actually exists on disk.
    Earlier task/epic/board links were already pointing at it, but the file
    itself had not landed. The active lane now has a real narrow runtime-target
    artifact in addition to the broader compiler-direction artifact.
  EVIDENCE:
  - codex/context_compass/artifacts/2026-05-30_phase12_north_star_runtime_model.md
  - codex/context_compass/artifact_board.md:24-25
  IMPACT: Future Phase 12 and Phase 13 work can reference the narrower
    runtime-target artifact directly instead of overloading the broader
    direction doc.
  NEXT: keep the next strategy tranche aligned to the now-real north-star
    artifact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T22:27:49Z
  TYPE: FACT
  CLAIM: The scaffold package naming is now cleaned up. The old
    `spell_compiler/phase12/` directory is gone; the processor surfaces now
    live under `spell_compiler/artifact_processor/` and the plan surfaces now
    live under `spell_compiler/codegen_planner/`. Compiler imports, tests, and
    active task/patch references were updated to the new paths, and the
    focused Phase 12/compiler ring stayed green after the move.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-171
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_builder.py:1-176
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:1-74
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-88
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-158
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:1-234
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-100
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-172
  IMPACT: The scaffold names now describe what the subsystems do instead of
    baking the phase number into the reusable package identity, which makes the
    next real strategy tranche easier to reason about.
  NEXT: implement the first concrete processor and plan strategies on top of
    the renamed scaffold.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:27:49Z
  TYPE: MEASURE
  CLAIM: The package rename and path split passed the same narrow syntax and
    focused pytest ring as the pre-rename scaffold.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-172
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py:1-127
  IMPACT: The rename did not introduce behavioral drift in the current Phase 12
    scaffold lane.
  NEXT: keep the next slice on strategy behavior rather than more structural
    cleanup.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T22:24:48Z
  TYPE: DECISION
  CLAIM: The initial Phase 12 scaffold directory should be
    split into clearer semantic packages before real strategy behavior lands.
    The processor classes are moving under `artifact_processor/` and the plan
    classes are moving under `codegen_planner/` so the directory names reflect
    what the code actually does instead of tying everything to the phase number.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:3-10
  IMPACT: This keeps the scaffold readable before the next strategy tranche and
    avoids baking "phase12" in as the long-term module identity for reusable
    compiler subsystems.
  NEXT: move the files, update imports/tests, and repair the patch/task path
    references in this active lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:10:21Z
  TYPE: FACT
  CLAIM: The current codebase already uses three successful strategy patterns
    that Phase 12 should copy rather than reinvent. First, the validation
    systems use ordered strategy registries over one shared context/result
    surface (`SpellValidationSystem`, `SpellSystemValidationSystem`). Second,
    the spell-examiner layer uses small builder/strategy objects that take one
    candidate surface and return one structured profile
    (`BindingProfileStrategy`, `ResolutionProfileStrategy`). Third, the current
    runtime specialization layer uses deterministic shape-family selection and
    cache keys (`CreationContext` override specialization cache,
    `CreationContextBuilder` route-key selection, and Phase 13's plan-signature
    no-overrides compile cache). The new Phase 12 processor and codegen-plan
    layers should deliberately combine those same ideas:
    ordered strategy registry, one shared state object, deterministic family
    ids, and cache/provenance keyed by structural shape instead of value data.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/validation/validation_system.py:61-169
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:42-176
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/binding_profile_strategy.py:17-200
  - src/melder/aether/spellbook/spell_compiler/spell_examiner/strategies/resolution_profile_strategy.py:15-57
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:115-204
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:585-708
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1171-1331
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:41-245
  IMPACT: The first real Phase 12 strategies should not be ad hoc if/else
    blobs. They should look like the repo's already-proven patterns:
    deterministic ordered strategy execution over one shared state plus one
    shaped output artifact.
  NEXT: implement the first processor and plan strategies using these exact
    traits: ordered registry, stable strategy ids, shared state mutation, and
    structural-family outputs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T22:10:21Z
  TYPE: FACT
  CLAIM: The Phase 12 scaffold docstrings are now upgraded to the richer
    contract-first standard across the new processor-state, processor,
    processor-strategy, codegen-plan, codegen-plan-builder,
    codegen-plan-strategy, and `CompilerPhase12` surfaces. The updated
    docstrings now call out ownership, lifecycle, purpose, contract, and
    later-consumer expectations instead of leaving the scaffold with thin
    placeholder text.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:6-171
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_builder.py:12-176
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:11-74
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:11-88
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-158
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:19-234
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:13-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:19-86
  IMPACT: The new Phase 12 scaffold now matches the repo's public-library
    documentation bar and is easier to reason about before the first real
    strategy tranche lands.
  NEXT: move back to real Phase 12 strategy work instead of more scaffold
    polish.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T22:10:21Z
  TYPE: MEASURE
  CLAIM: The docstring-only Phase 12 slice passed narrow syntax validation
    across the touched files.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-171
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_builder.py:1-176
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:1-74
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:1-88
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-158
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:1-234
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:1-86
  IMPACT: The docstring enrichment did not introduce syntax drift into the new
    Phase 12 scaffold.
  NEXT: keep the next slice on strategy behavior, not more scaffold repair.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-05-30T22:03:39Z
  TYPE: FACT
  CLAIM: The Phase 12 north-star runtime philosophy now has its own focused
    artifact instead of only living inside the broader execution-strategy
    direction doc. That artifact captures the intended end-state where the
    spell-owned runtime binder holds an already-chosen codegen pattern and
    concrete creations-owner surfaces, while `Meld` either takes a sealed fast
    path or jumps directly into the exact bound callable pack.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_phase12_north_star_runtime_model.md
  IMPACT: The scaffold and later strategy work now have a narrow runtime target
    artifact to reference without reopening the broader compiler-direction doc
    every time.
  NEXT: Use this artifact as the runtime target when choosing the first real
    processor and plan strategies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T22:03:39Z
  TYPE: DECISION
  CLAIM: The north-star runtime shape is now explicit. The endgame is not a
    generic late-strategy `CreationContext`. It is a spell-owned runtime binder
    that holds a solidified codegen pattern and the concrete creations-owner
    surfaces for that pattern. In that model, `Meld` either creates on a
    sealed fast path or jumps directly into the spell's exact bound runtime
    callable pack after only hard validity checks and dynamic input packing.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/artifacts/2026-05-30_execution_strategy_compiler_direction.md
  IMPACT: Future Phase 12 strategy work should optimize toward per-spell
    ownership-aware callable packs rather than preserving a generic
    context-shaped late decision model.
  NEXT: Use the next strategy tranche to classify route/storage family and lane
    family so the eventual runtime binder has a concrete pattern to bind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T21:59:25Z
  TYPE: FACT
  CLAIM: The likely long-term runtime consequence is that `CreationContext`
    should stop being treated as a generic context object and instead become a
    solidified codegen-pattern binder for one spell/runtime ownership shape.
    The compiler already knows whether a spell is `unique`,
    `unique_per_conduit`, `unique_per_spell_space`, shared-owner rooted, or
    transient-many, and ownership-transfer semantics differ across those
    families. That means the strongest future role for `CreationContext` is to
    bind the already-chosen compiled pattern plus the concrete creations owner
    surfaces for that family, not to keep re-deciding those semantics late.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:24-98
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:182-325
  - src/melder/aether/conduit/meld/conduit_meld.py:250-371
  - src/melder/aether/conduit/meld/spellspace_meld.py:269-389
  - src/melder/aether/conduit/creations/creations.py:165-366
  IMPACT: The right Phase 12/13 direction is not just "pick an executor." It
    is "pick a spell-specific ownership and codegen pattern," then let the
    runtime binder hold the exact creations surfaces and compiled callable that
    match that pattern.
  NEXT: Keep the next strategy tranche focused on route/storage family and
    ownership-sensitive codegen families so later `CreationContext` thinning
    has a real target to bind.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T21:39:27Z
  TYPE: FACT
  CLAIM: The current Phase 13 / `CreationContext` split is narrower and also
    more awkward than the eventual target. Phase 13 currently only compiles the
    no-overrides executor from either the Phase 11 plan handoff or exported IR
    payload, while `CreationContextBuilder` still selects the route key,
    transient eligibility, no-overrides executor binding, override patch map,
    and override route configs. `CreationContext` itself still owns the
    override specialization runtime: shape caching, last-executor reuse,
    source/code-object caches, and the on-demand override-executor compile path.
    So the next real Phase 12 work is to take those plan-shaping decisions out
    of `CreationContextBuilder` and enough of the override-family selection out
    of `CreationContext` that later Phase 13 can become a thinner emitter
    consumer instead of sharing the strategist burden.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_13.py:23-245
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:24-98
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:115-204
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:207-289
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:569-708
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1171-1331
  IMPACT: The first real strategy tranche should focus on route-family,
    lane-family, and override-plan-family decisions, because those are the
    biggest remaining planning responsibilities still sitting below Phase 12.
  NEXT: Define the first concrete processor/plan strategies around route
    selection, no-overrides family selection, and overrides family selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T21:39:27Z
  TYPE: FACT
  CLAIM: The first Phase 12 code slice is landed. `SpellCompilerArtifact` now
    owns `_phase12_processor_state` and `_phase12_codegen_plan` with cleanup
    and later-phase reset support. The new scaffold packages now contain
    `SpellCodegenModel`, `SpellArtifactProcessorBuilder`,
    `SpellArtifactProcessorStrategy`, `SpellArtifactProcessor`,
    `SpellCodegenPlan`, `SpellCodegenPlanBuilder`, and
    `SpellCodegenPlanStrategy`. `CompilerPhase12.run(...)` now builds/stores a
    meaningful baseline processor state and baseline codegen plan instead of
    acting as a no-op placeholder.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:97-98
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:165-166
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:453-466
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:6-171
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_builder.py:12-176
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy.py:11-74
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:11-88
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-158
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_builder.py:19-234
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan_strategy.py:13-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_12.py:14-100
  IMPACT: Phase 12 now has a real compiler-owned home in code. The next slice
    can start adding concrete processor and plan strategies without reopening
    ownership or storage questions.
  NEXT: define the first concrete processor/plan strategies and replace the
    baseline placeholder family strings with real assessed families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-30T21:39:27Z
  TYPE: MEASURE
  CLAIM: The focused Phase 12/compiler ring is green after the scaffold
    landing. Syntax validation passed for the touched compiler files and the
    narrow pytest ring passed `19` tests with one existing pytest cache
    warning.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_phase_12.py:1-172
  - tests/unit/melder/spellbook/spell_compiler/test_spell_compiler.py:1-127
  IMPACT: The scaffold is stable enough to use as the base for the next Phase
    12 strategy implementation slice.
  NEXT: move to the first real strategy tranche instead of widening the
    scaffold further.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-05-30T21:27:07Z
  TYPE: PLAN
  CLAIM: The first implementation slice is intentionally narrow. It will add
    the Phase 12 artifact fields, scaffold the processor and codegen-plan
    classes, and wire `CompilerPhase12` to build/store placeholder outputs
    without touching Phase 13 or `CreationContext` consumers yet.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/tickets/tasks/2026-05-30_define_execution_strategy_phase12_task.md
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md
  IMPACT: This keeps the first landing coherent and reviewable while still
    moving the Phase 12 contract out of docs and into code.
  NEXT: create the patch-doc lane and then patch `SpellCompilerArtifact` first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is the first real code slice for the new Phase 12 direction. It
should land the compiler-owned scaffold only: artifact fields, processor state,
processor/plan classes, and compiler wiring.
