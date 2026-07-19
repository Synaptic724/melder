Completed: 2026-06-12T11:58:04Z
Summary: Closed by user cleanup request with the latest compiler-structure
findings preserved in notes and handoff sections for later reuse.

# Task: Decompose Phase10 Phase11 Strategy Groups

## Metadata
- Task ID: TASK-2026-06-06-decompose-phase10-phase11-strategy-groups
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-06T18:18:17Z
- Updated: 2026-06-12T11:58:04Z

## Objective
Break up the current large phase 10 and phase 11 strategy bodies into smaller,
correctly named strategy groups, keep the current runtime handoff contract
stable, and define how discovery should select those grouped strategies before
we widen the system further.

## Parent Link
- Epic:
  `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`

## Ticket Contract
- ENTRY_GATE: the mutation cleanup lane is closed enough that the next real
  compiler work is organizational refactor on the phase 10-11 strategy chain,
  not more mutation semantics work.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spell_compiler/spell_analyzer/`
  - `src/melder/aether/spellbook/spell_compiler/artifact_processor/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_planner/`
  - `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/`
  - `src/melder/aether/conduit/meld/creation_context/creation_context_builder.py`
  - `src/melder/aether/conduit/meld/creation_context/creation_context.py`
  - `tests/unit/melder/spellbook/spell_compiler/`
  - `tests/unit/melder/aether/conduit/meld/creation_context/`
  - `tests/component/melder/spellbook/`
  - `codex/context_compass/tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md`
  - `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`
  - `tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md`
- EXIT_GATE:
  - the current phase 10 and phase 11 big strategy bodies are partitioned into
    concrete sub-strategy groups with ownership and naming rules
  - the discovery responsibilities are explicit
  - the stable runtime handoff contract to `CreationContext` is preserved
  - the first bounded implementation slice is explicit before edits widen
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the decomposition requires
  changing the current runtime handoff contract instead of preserving it.

## Scope Boundaries
- In scope:
  - phase 10 strategy grouping
  - phase 11 strategy grouping
  - discovery-system role for grouped selection
  - stable `SpellCodegenPlan` and `SpellCodegenCreation` output contract
  - `CreationContext` consumer boundary only as needed to preserve the handoff
- Out of scope:
  - mutation research
  - change-control mediator work
  - broad runtime API redesign
  - final optimization claims

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the active compiler lane to
  phase 10-11 strategy decomposition and discovery cleanup.

## Steps / Checklist
- [ ] Re-read the current phase 10 planner strategies and discovery contract.
- [ ] Re-read the current phase 11 codegen-creation strategies and discovery contract.
- [ ] Partition the large strategy bodies into concrete grouped responsibilities.
- [ ] Define the naming contract for the grouped strategies.
- [ ] Define what discovery should choose vs what ordinary sequencing should own.
- [ ] Define the first bounded implementation slice before widening into code edits.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one explicit phase 10 strategy-group map
- one explicit phase 11 strategy-group map
- one explicit discovery-role map
- one explicit first implementation slice

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "strategy_id|discover|apply|SpellCodegenPlan|SpellCodegenCreation" src/melder/aether/spellbook/spell_compiler`

## Risks / Rollback Notes
- Risk: we reorganize strategy files without a stable naming/ownership rule and
  just create smaller chaos.
- Risk: discovery gets asked to choose tiny helpers instead of real strategy
  families.
- Rollback: keep this pass design-only until the first implementation slice is
  explicit and reviewable.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening into broad runtime API changes in this task.
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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - phase 10 planner strategy grouping
  - phase 11 codegen creation strategy grouping
  - discovery-system role cleanup
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: strategy ownership, discovery responsibility, and bounded next slices.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-06T18:18:17Z
  TYPE: PLAN
  CLAIM: The current runtime handoff contract is finally stable enough to stop
    touching the hot path and reorganize behind it. The next real work is to
    split the large phase 10 and phase 11 strategy bodies into smaller, named
    groups and make discovery select actual strategy families instead of
    leaving monolithic generalized passes in place.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:1-260
  - codex/context_compass/tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md:1-180
  - codex/context_compass/tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md:1237-1288
  IMPACT: This lets the next compiler work stay architectural and organizational
    instead of slipping back into mutation cleanup or more hot-path churn.
  NEXT: map the current phase 10 planner and phase 11 creation strategies into
    concrete subgroups and decide which of those groups discovery should own.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T18:24:31Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The first expansion family after the current runtime-handoff cleanup
    should be a true solo strategy. The big code is still concentrated in phase
    11, but the formal split should span phases 9-11:
    - phase 9 keeps sectioned model truth
    - phase 10 chooses the plan family
    - phase 11 emits the concrete runtime family
    The solo family is the smallest useful specialized target because it can
    model one root spell with no downstream spell construction fanout while
    still varying by existence/reuse route.
  EVIDENCE:
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:15-255
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-533
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-283
  IMPACT: We should not start by widening the runtime contract again. We should
    define one new formal family that discovery can target cleanly, then grow
    from there.
  NEXT: map the solo family across phase 9 model signals, phase 10 plan
    selection, and phase 11 emitted runtime shape before any code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T18:31:42Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The immediate formalization target is not a new family yet. It is the
    phase 9-11 contract itself. The user clarified the desired split:
    - phase 9 computes processor-owned truth about graph shape, size, and
      other structural/runtime-relevant signals
    - phase 10 consumes that truth, runs discovery, and chooses the planning
      family plus candidate codegen approach (for example unrolled, recursive,
      or other experimentally validated shapes)
    - phase 11 consumes the chosen plan family, runs codegen discovery, and
      builds the final `no_overrides_executor` and `overrides_executor`
    The key point is that the phase-10 plan should not be shaped around the
    final two executors directly. It should be shaped around the chosen
    structure/codegen family, with phase 11 responsible for turning that chosen
    family into the final runtime doors.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:151-255
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-274
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-72
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-69
  IMPACT: The first decomposition pass should formalize the phase boundary and
    ownership model before introducing any new plan families. That keeps the
    later family expansion aligned to the right contract.
  NEXT: define the exact responsibilities and artifact contract for phase 9,
    phase 10, and phase 11 under this clarified direction, then map the current
    big strategies into that model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:00:03Z
  TYPE: FACT
  CLAIM: The first formalization slice is now implemented on the discovery
    seam. Phase 10 discovery no longer means only "which planner strategy id";
    it now also declares the selected `plan_family_id` plus the candidate
    codegen styles phase 11 is allowed to consider. Phase 11 discovery now
    chooses one concrete `selected_codegen_style_id` from the plan-side
    candidate set and passes that through as creation provenance. The runtime
    contract did not widen: `SpellCodegenCreation` still exposes only
    `no_overrides_executor` and `overrides_executor`, and the chosen style is
    recorded in metadata only.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-25
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:1-84
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-119
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:1-22
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-70
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-114
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:1-69
  IMPACT: The phase split is now explicit in code:
    - phase 9 computes truth
    - phase 10 chooses the plan family and candidate codegen styles
    - phase 11 chooses the concrete codegen style and builds the final two
      runtime doors
    That gives us the right formal seam before we break the big strategies into
    smaller grouped implementations.
  NEXT: break the current generalized phase 10 and phase 11 strategy bodies
    into smaller named groups while preserving this new discovery/ownership
    contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:00:03Z
  TYPE: MEASURE
  CLAIM: The focused phase 10-11 discovery/planner/creation test surface is
    green after the formalization slice. The direct validation ring was:
    - `test_codegen_plan_discovery_core.py`
    - `test_spell_codegen_planner_core.py`
    - `test_codegen_creation_discovery_core.py`
    - `test_codegen_creation_core.py`
    - `test_codegen_discovery_pipeline_component.py`
    using `.venv_new\\Scripts\\python.exe -m pytest ... -q`, and it passed
    `37 passed`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-178
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-183
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-237
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-503
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-177
  IMPACT: The formal split is pinned down well enough to start reorganizing the
    big strategies without guessing at the discovery contract.
  NEXT: map the exact sub-strategy groups inside the current generalized phase
    10 and phase 11 bodies and pick the first bounded extraction slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:43:29Z
  TYPE: FACT
  CLAIM: The current compiler/runtime seam is now clear in code. Phases 8-11
    themselves are thin façade wrappers; the real phase logic sits in the
    analyzer/processor/planner/codegen-creation systems behind them. The
    runtime handoff is also narrow and direct: `SpellCodegenCreation` exposes
    only `no_overrides_executor` and `overrides_executor`, `CreationContextBuilder`
    consumes those, and `CreationContext` compiles the direct hooks/no-hooks
    runtime doors. The remaining big phase-11 chunk is the fat
    `SpellGeneralCreationContextCodegenCreationStrategy`, which still owns the
    override runtime specialization/caching logic that used to live in the old
    `CreationContext`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:20-98
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:16-74
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:16-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-87
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:20-156
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:21-130
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-61
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:12-123
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:22-265
  - src/melder/aether/conduit/meld/conduit_meld.py:13-551
  - src/melder/aether/conduit/meld/spellspace_meld.py:15-549
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:34-709
  IMPACT: The upcoming phase 10-11 decomposition should not spend effort on the
    wrapper phase files. The real split point is inside the planner strategy
    body and the phase-11 creation strategy chain, while the
    `SpellCodegenCreation -> CreationContextBuilder -> CreationContext`
    contract should stay fixed.
  NEXT: map the current planner body and the fat phase-11 finalizer into
    smaller named groups, then choose the first extraction slice behind the
    fixed runtime handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:51:58Z
  TYPE: DECISION
  CLAIM: The current decomposition target is now explicit enough to name the
    first real strategy groups. Phase 10 should formalize around:
    - plan family discovery
    - plan shell bootstrap
    - no-overrides lane build
    - overrides lane build
    - plan finalization/provenance
    The current generalized plan strategy still collapses the two lane-build
    responsibilities into one body, while discovery and plan-shell bootstrap
    already exist separately. Phase 11 should formalize around:
    - creation discovery
    - shared route/setup facts
    - no-overrides executor build
    - overrides static-input packaging
    - overrides runtime specialization build
    - final CreationContext handoff write
    The existing generalized phase-11 chain already has the first four pieces,
    but the fat `general_creation_context_codegen_creation` strategy still
    collapses the last two into one file.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:21-130
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:8-46
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:13-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-71
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:13-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:20-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:24-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:34-709
  IMPACT: We can now remodel by extraction instead of by vague cleanup. The
    safe first split is phase 10, because it is compiler-only, has no runtime
    handoff pressure, and lets phase 11 consume cleaner lane responsibilities
    before we split the fat override runtime finalizer.
  NEXT: update the umbrella epic with this named group map and lock the first
    bounded extraction slice as phase-10 lane/finalization breakup before the
    larger phase-11 override-runtime split.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:55:05Z
  TYPE: FACT
  CLAIM: The discovery objects are now carrying 2 distinct kinds of decisions,
    and that split matters. Phase 10 discovery is not just "which planner
    strategy id"; it currently chooses:
    - one selected planner strategy id
    - one `plan_family_id`
    - one bounded tuple of `candidate_codegen_style_ids`
    Phase 11 discovery then consumes the model+plan pair and chooses:
    - one ordered tuple of creation strategy ids
    - one concrete `selected_codegen_style_id`
    So the current formal seam is: phase 10 chooses the planning family and
    the allowed style set, while phase 11 chooses the concrete style and the
    strategy chain that materializes it.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:6-28
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy.py:12-46
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_system.py:13-73
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:8-46
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:6-24
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy.py:15-49
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_system.py:16-77
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-71
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/fallback_no_overrides_codegen_creation_discovery_strategy.py:13-47
  IMPACT: This means discovery should stay coarse. Phase 10 discovery should
    not start picking helper-sized planner pieces, and phase 11 discovery
    should not start picking every tiny override-runtime helper. Discovery is
    for family/style and ordered chain choice, not micro-step scheduling.
  NEXT: keep the current discovery object contracts fixed while we split the
    planner and phase-11 strategy bodies underneath them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:58:28Z
  TYPE: DECISION
  CLAIM: The discovery seam is now documented at the code level as well as the
    ticket level. The planner discovery docs now explicitly say phase 10 owns
    planning-family selection plus the bounded style allow-list, while phase 11
    discovery docs now explicitly say phase 11 owns the concrete style choice
    and ordered creation chain without widening the runtime contract. The
    `SpellCodegenPlan` and `SpellCodegenCreation` docstrings were tightened to
    match that split.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:6-30
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_strategy.py:12-48
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery_system.py:13-64
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:8-39
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:6-23
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:6-26
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy.py:15-47
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_system.py:16-61
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-39
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-23
  IMPACT: The next decomposition work can now treat this split as documented
    contract rather than chat-only intent, which lowers the risk of drifting
    phase 10 discovery into style choice or drifting phase 11 into runtime
    contract expansion.
  NEXT: keep the discovery contracts fixed and move the next bounded refactor
    into phase-10 lane/finalization breakup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:05:17Z
  TYPE: FACT
  CLAIM: The current phase-11 normalization problem is not discovery first; it
    is the strategy-step contract. `CodegenCreationSystem` already executes an
    ordered strategy batch selected by discovery, but the batch currently has
    no explicit intermediate build-state object. Because of that, step outputs
    are being tunneled through `SpellCodegenCreation.metadata` using private
    scratch keys such as `_resolve_route_key`, `_no_overrides_base_executor`,
    `_override_targeting`, `_override_plan_signature`, `_override_plan_rows`,
    `_override_spell_lookup`, and `_override_baseline_executor`. The fat
    `general_creation_context_codegen_creation` strategy then pops those scratch
    fields back out and still owns the hidden override-runtime step graph:
    payload split, target grouping, specialization cache lookup, emitted-source
    caching, code-object caching, and override executor compilation. The
    so-called compiler helper modules in the phase-11 root are already the
    backend step surfaces:
    - `generalized_no_overrides_codegen_creation_compiler.py`
    - `generalized_overrides_codegen_creation_compiler.py`
    - `spell_override_targeting_codegen_creation.py`
    but they are not modeled as explicit batch steps in the strategy contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy.py:14-42
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:44-65
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:60-100
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:66-118
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:61-133
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:204-776
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:119-176
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:22-419
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:47-252
  IMPACT: The correct first normalization for phase 11 is to introduce an
    explicit build-state surface for ordered creation steps, not to widen
    discovery or widen `SpellCodegenCreation`. Once build-state exists, the
    helper compiler modules can be represented as real strategy steps instead
    of hidden helper calls tunneled through metadata.
  NEXT: define the phase-11 build-state object and the step categories it must
    carry, then decide whether to extend `SpellCodegenStrategy` itself or add a
    second step-strategy contract beneath the current batch system.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:14:34Z
  TYPE: DECISION
  CLAIM: The current flat phase-11 strategy pattern is the wrong abstraction.
    Discovery should select one **family strategy** for the chosen phase-10
    plan family, and that family strategy should own an explicit ordered batch
    of named internal steps plus one explicit build-state object. In other
    words:
    - phase 11 discovery chooses the family strategy
    - the family strategy runs the step batch
    - the step batch builds the final `SpellCodegenCreation`
    This means the current root-level phase-11 helper/compiler files are in the
    wrong place when they are family-specific. The root phase-11 directory
    should keep only shared contracts/system/discovery/output surfaces, while
    each family gets its own folder with:
    - one family strategy
    - one build-state object
    - one ordered set of named step objects/modules
    For the current `generalized` family, the explicit step categories should
    be:
    - setup / route facts
    - no-overrides executor build
    - override targeting artifact build
    - override route-input packaging
    - override baseline executor build
    - override runtime specialization build
    - final output write
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy.py:14-30
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:13-95
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:6-24
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-39
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_creation_context_setup_codegen_creation_strategy.py:13-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_no_overrides_codegen_creation_strategy.py:20-122
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_generalized_overrides_codegen_creation_strategy.py:24-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:34-709
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:1-176
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:1-419
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:1-252
  IMPACT: The next phase-11 remodel should not keep pretending that every
    micro-step is a peer top-level strategy selected by discovery. The real
    normalization target is a family package with explicit internal step order
    and explicit intermediate build state.
  NEXT: write the concrete folder/contract shape for one family package
    (`generalized`) and decide whether the current `SpellCodegenStrategy`
    interface becomes the family-strategy interface or stays as the inner
    step-level contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:24:02Z
  TYPE: DECISION
  CLAIM: The concrete folder split is now tighter. The phase-11 root should
    keep only:
    - discovery contracts/systems/builders
    - the family-strategy interface
    - the creation-system facade
    - the final `SpellCodegenCreation` output object
    - optional `shared_strategy_assets/` only for code that is genuinely
      reused across multiple families
    The current helper compiler modules are **not** generic enough to stay at
    the phase-11 root:
    - `generalized_no_overrides_codegen_creation_compiler.py`
    - `generalized_overrides_codegen_creation_compiler.py`
    These belong under the `generalized` family package because they compile
    the generalized family's executor shapes. The current
    `spell_override_targeting_codegen_creation.py` should also move under the
    generalized family unless and until another family proves it is shared.
    `shared_strategy_assets/` is valid, but it should stay narrow and hold only
    truly cross-family helpers, not family-specific compilers hidden under a
    generic name.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:57-1875
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:22-2979
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:47-252
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:13-39
  IMPACT: This keeps the root phase-11 directory clean and prevents the next
    normalization pass from recreating the same problem one level down with a
    fake shared folder that is really just a generalized dump.
  NEXT: formalize the exact `generalized` package contents and the minimal
    allowed contents of `shared_strategy_assets/` before changing code layout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T21:37:22Z
  TYPE: PLAN
  CLAIM: The migration seam is now explicit enough to implement without
    widening the runtime contract. The safe move is:
    - keep `SpellCodegenCreation -> CreationContextBuilder -> CreationContext`
      fixed
    - make discovery choose one generalized family facade id
    - make the builder register that family facade plus the existing fallback
      no-overrides public strategy
    - move generalized compiler/artifact code under the `generalized` family
      package
    - keep compatibility wrappers at the old import paths so direct tests and
      experimentation surfaces do not break during the migration
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/spell_general_creation_context_codegen_creation_strategy.py:1-709
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-123
  - src/melder\aether\conduit\meld\creation_context\creation_context.py:1-313
  IMPACT: This gives us a real phase-11 family abstraction while keeping core
    runtime behavior and existing import surfaces stable during the move.
  NEXT: implement the generalized family package, switch generalized discovery
    to the family id, and leave shim modules at the old paths for compatibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T21:49:13Z
  TYPE: MEASURE
  CLAIM: The generalized phase-11 migration is now landed and the focused
    compiler test ring is green. Generalized planner output now resolves to
    one family facade id, the builder registers that family facade plus the
    fallback no-overrides public strategy, the generalized family has a real
    state object plus ordered internal steps, and the moved compiler/artifact
    modules remain reachable through compatibility shims at the old import
    paths.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_state.py:1-87
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-79
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:1-63
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-209
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-520
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:1-1280
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-182
  IMPACT: The public phase-11 abstraction is now family-oriented instead of a
    4-step generalized chain, but the `SpellCodegenCreation ->
    CreationContextBuilder -> CreationContext` runtime seam and the old import
    paths stay intact during the migration.
  NEXT: walk the migrated generalized family layout with the user and decide
    whether the next slice should normalize fallback into its own family or
    continue breaking the generalized family internals into more granular
    reusable shared assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T21:57:52Z
  TYPE: DECISION
  CLAIM: The previous pass stopped too early and left compatibility wrappers at
    the old top-level compiler/artifact paths. The user explicitly rejected
    shims and backwards-compatibility surfaces for this migration. The only
    compliant correction is to delete those old wrapper files immediately and
    retarget every remaining import to the family-local generalized package in
    the same pass so there is one live abstraction path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_no_overrides_codegen_creation_compiler.py:1-7
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/generalized_overrides_codegen_creation_compiler.py:1-7
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_override_targeting_codegen_creation.py:1-7
  - tests/experimentation/creation_context_cache_asset_playground.py:22-37
  - src/melder/aether/conduit/meld/creation_context/old_creation_context.py:22-25
  IMPACT: The migration is not actually done until the wrapper layer is gone.
    Leaving it in place preserves exactly the hidden compatibility path the
    user does not want.
  NEXT: remove the wrapper files, rewrite the remaining imports to the
    generalized family-local paths, and rerun the focused compiler test ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T22:01:22Z
  TYPE: MEASURE
  CLAIM: The wrapper layer is now removed. The old top-level generalized
    compiler/artifact files and the old top-level generalized strategy wrapper
    files were deleted, the remaining imports were retargeted to the
    generalized family-local modules or the new fallback strategy file, and the
    focused phase-11 compiler ring is green again.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/generalized_codegen_creation_strategy.py:1-76
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/fallback_no_overrides/fallback_no_overrides_codegen_creation_strategy.py:1-58
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-79
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-209
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-539
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:1-1280
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:1-182
  IMPACT: The migration now has one real family abstraction path and no shim
    or wrapper fallback layer in `codegen_creation_system`.
  NEXT: review whether the next slice should migrate the fallback no-overrides
    path into a fuller family package or start extracting truly shared assets
    out of generalized.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T22:35:58Z
  TYPE: FACT
  CLAIM: Phase 10 is not structurally broken the way phase 11 was. The public
    phase-10 contract is already in the right shape:
    - discovery emits `selected_strategy_id`, `plan_family_id`, and
      `candidate_codegen_style_ids`
    - planner records those directly on `SpellCodegenPlan`
    - there is only one real top-level generalized plan strategy body today
    The next useful phase-10 extension point for `many_only` and `solo` is
    therefore discovery plus selective branching inside the generalized plan
    strategy, not a large family-package migration first.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-26
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-130
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:1-58
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-257
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1-2031
  IMPACT: We do not need to over-normalize phase 10 first. We can add
    `many_only` and `solo` plan-family/style signals at discovery time and
    keep the runtime seam untouched while phase 11 later consumes those
    signals.
  NEXT: inspect whether `SpellCodegenModel` already exposes enough data to
    detect `many_only` and `solo` directly, then define the exact discovery
    rules and the minimal generalized-plan branching needed to output those
    two paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T23:09:36Z
  TYPE: PLAN
  CLAIM: The next bounded slice is to enrich the new phase-8 existence section
    with `has_disposal_methods` per spell and aggregate disposal-aware counts
    in the same visible-spell walk. That keeps the producer responsibility in
    phase 8, keeps the phase-9 model section data-only, and gives later
    phase-10 discovery enough truth to distinguish `many_only` with and
    without disposal bookkeeping pressure.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py:1-23
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:132-192
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py:1-55
  IMPACT: This extends the raw existence capture in the right layer without
    pushing planner logic into phase 8 or forcing phase 10 to rediscover
    disposal posture from live spell objects.
  NEXT: add `has_disposal_methods` to the phase-8 row dataclass, add
    disposal-aware aggregate counts, expose the updated section through phase 9,
    and rerun the focused analyzer/processor/compiler ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T23:27:12Z
  TYPE: PLAN
  CLAIM: The next phase-10 discovery slice is now explicit. We will add 2
    category selectors first and keep the rest of phase 10 stable:
    - `solo` wins whenever the visible spell set size is exactly 1
    - `many_only` applies when the visible spell set size is greater than 1
      and every spell in the phase-9 existence-occurrence section has
      `Existence.many`
    Discovery should emit those categories through
    `selected_strategy_id`, `plan_family_id`, and
    `candidate_codegen_style_ids`, while phase 10 consumes only model-owned
    facts rather than reopening live spellbook/runtime surfaces.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-26
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/generalized_codegen_plan_discovery_strategy.py:1-43
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-130
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-299
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py:1-30
  IMPACT: This keeps phase 10 responsible for category selection only and
    prevents phase-10 discovery from re-deriving raw existence/disposal truth
    from the spellbook again.
  NEXT: implement `solo` and `many_only` discovery strategies plus the 2 new
    phase-10 planner strategy ids they target, then leave phase 11 unchanged
    for the next slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T23:36:00Z
  TYPE: MEASURE
  CLAIM: Phase 8 and phase 9 now expose disposal-aware existence distribution
    truth in the right layers. Phase 8 captures one immutable
    `SpellExistenceOccurrenceAnalysis` with:
    - `spell_id`
    - `existence`
    - `has_disposal_methods`
    plus aggregate existence counts, `(existence, has_disposal_methods)` counts,
    root existence, and total spell count. Phase 9 now publishes that payload
    onto `SpellCodegenModel` as `existence_occurrence_shape`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/data/spell_existence_occurrence_analysis.py:1-30
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:132-204
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_codegen_model.py:1-299
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/strategies/spell_existence_occurrence_processor_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor_strategy_builder.py:1-137
  IMPACT: Phase 10 discovery can now choose `solo` and `many_only` from a
    data-only model section instead of reopening live spell objects or
    rebuilding existence/disposal facts from raw graph/runtime sections.
  NEXT: implement the phase-10 `solo` and `many_only` discovery strategies and
    matching planner strategy ids against `existence_occurrence_shape`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T08:40:54Z
  TYPE: FACT
  CLAIM: The earlier compiler picture was missing the weight of phases 4-7 and
    overstating phases 8-11 as if they were still the heavy planning path.
    Phase 4 is the structural validity gate into `SpellSystemStates`, Phase 5
    is the rooted-system builder, Phase 6 is the system validator, and Phase 7
    is the change-control revalidation bridge. By contrast, phases 8-11 are now
    thin wrappers over analyzer, processor, planner, and codegen-creation
    systems.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_4.py:56-145
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:458-615
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:109-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:55-231
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:20-100
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:16-74
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:16-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-87
  IMPACT: Phase-10 and phase-11 family work must stay grounded in the fact that
    the modern compiler front is analyzer -> processor -> planner -> creation
    packaging, while phases 4-7 still own the structural, rooted, validation,
    and change-control foundations those later families depend on.
  NEXT: keep later `solo` and `many_only` phase-11 design honest to the
    phase-4/5/6/7 prerequisites instead of treating phase 10 and 11 as
    standalone planning islands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T08:40:54Z
  TYPE: FACT
  CLAIM: The current runtime seam is tighter than the earlier ticket state
    captured. `CreationContextBuilder` only accepts the spell-static phase-11
    handoff (`no_overrides_executor`, `overrides_executor`, and route metadata),
    while `CreationContext` keeps only runtime gate waiting and the direct
    hooks/no-hooks dispatch doors. That means phase-11 family work should
    produce better spell-static packaging, not push more planning back into the
    runtime binder.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:12-123
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:22-313
  - codex/context_compass/tickets/epics/2026-05-30_right_size_execution_strategy_compiler_outputs_epic.md:707-740
  - codex/context_compass/tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md:20-57
  IMPACT: The bounded compiler lane remains valid only if phase-11
    specialization continues to collapse into `SpellCodegenCreation` and keeps
    `CreationContext` thin. Any new family should change emitted spell-static
    executors first, not widen the runtime seam again.
  NEXT: design `solo` and `many_only` phase-11 families so they terminate in
    the same two-door `SpellCodegenCreation` contract and reuse the existing
    builder/context seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:03:36Z
  TYPE: FACT
  CLAIM: Phase 10 is not actually family-complete yet. The `solo` and
    `many_only` phase-10 strategies currently only change discovery/category
    identity; both still instantiate the same generalized no-overrides and
    overrides lane builders directly. So the next required phase-10 slice is
    real dedicated lane building, not more category plumbing.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_codegen_plan_strategy.py:19-69
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1047
  IMPACT: If we move into phase 11 now, `solo` and `many_only` would still be
    planner-thin aliases over generalized lane emission. That would make later
    phase-11 families start from fake distinct plan families instead of real
    planner divergence.
  NEXT: inspect `SpellGeneralizedCodegenPlanBuilder` and split out dedicated
    solo and many-only lane builders so phase 10 emits real family-specific
    lane plans before phase-11 family work starts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:07:29Z
  TYPE: DECISION
  CLAIM: The first completion slice for phase 10 is now implemented. Instead of
    routing the `solo` and `many_only` strategies straight into
    `SpellGeneralizedCodegenPlanBuilder`, the planner now has dedicated
    `SpellSoloCodegenPlanBuilder` and `SpellManyOnlyCodegenPlanBuilder`
    surfaces. They still reuse the common generalized lane synthesis internally,
    but they enforce family-specific preconditions at the builder boundary and
    stamp family metadata onto the resulting lane plans.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1314
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-61
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-296
  IMPACT: Phase 10 is no longer just category detection plus generalized lane
    wrappers. It now has real dedicated builder surfaces for the two new
    families, which is enough to hand a truthful family boundary into phase 11.
  NEXT: run the focused phase-10 planner/discovery tests and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:08:11Z
  TYPE: MEASURE
  CLAIM: The first focused validation pass failed for a test-only reason, not a
    planner-lane regression. The new strategy-wiring tests reused
    `_ProcessorStateProbe`, but that test double did not implement
    `section_names()`, which the real strategy bodies still record into plan
    metadata.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:30-43
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:259-337
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:37-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:39-61
  IMPACT: The lane-builder refactor itself is not disproved. The immediate fix is
    to make the planner test probe match the real model contract before rerunning
    the same focused validation ring.
  NEXT: add `section_names()` to `_ProcessorStateProbe` and rerun the focused
    planner/discovery tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:08:51Z
  TYPE: MEASURE
  CLAIM: The dedicated phase-10 lane-builder slice is now validated. The focused
    planner/discovery ring passed after adding real solo and many-only builder
    surfaces and fixing the planner test probe to match the real model
    interface.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1314
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_solo_codegen_plan_strategy.py:19-59
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-61
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_plan_discovery_core.py:1-241
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:1-300
  IMPACT: Phase 10 is now genuinely complete for this milestone: detection,
    family ids, and dedicated lane-builder surfaces all exist and are covered by
    the focused planner/discovery ring.
  NEXT: move into phase 11 and add real `solo` and `many_only` creation-family
    discovery and strategy surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:11:40Z
  TYPE: FACT
  CLAIM: Phase 11 still does not consume the new phase-10 families. Creation
    discovery only recognizes generalized planner output, and the codegen
    strategy registry only exposes the generalized family plus the fallback
    no-overrides path. So `solo` and `many_only` are real phase-10 plan
    families now, but not real phase-11 creation families yet.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/generalized_codegen_creation_discovery_strategy.py:14-66
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy_builder.py:1-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-99
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:57-112
  IMPACT: The next compiler slice is definitely phase 11. Nothing else in phase
    10 is blocking it now; the gap is that phase-11 discovery and strategy
    execution still collapse every new family back into generalized creation.
  NEXT: inspect the generalized family steps and define the smallest real phase-11
    insertion point for dedicated `solo` and `many_only` creation families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:15:34Z
  TYPE: FACT
  CLAIM: Phase 11 now has real `solo` and `many_only` family surfaces. The
    creation-discovery registry now claims the two new phase-10 planner ids,
    the codegen strategy registry now exposes `solo_codegen_creation` and
    `many_only_codegen_creation`, and each new family owns its own strategy and
    state class while reusing the current shared step machinery.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/solo_codegen_creation_discovery_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/many_only_codegen_creation_discovery_strategy.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery_strategy_builder.py:1-96
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/spell_codegen_strategy_builder.py:1-111
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_strategy.py:1-83
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_strategy.py:1-84
  IMPACT: Phase 11 no longer collapses every non-fallback family back into
    generalized discovery. The next question is validation quality, not whether
    the family ids exist.
  NEXT: run the focused phase-11 discovery/creation test ring and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:16:23Z
  TYPE: MEASURE
  CLAIM: The focused phase-11 discovery/creation ring is green after the new
    family insertion. The codegen-creation discovery tests and creation-system
    contract tests now pass with the dedicated `solo` and `many_only` creation
    families registered.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-551
  IMPACT: The compiler now has real phase-11 family consumption for the new
    phase-10 plan families. The remaining work is refinement of those families,
    not the basic discovery/registration seam.
  NEXT: decide whether the next slice is deeper family-specific step divergence
    for `solo` / `many_only` or closure of the current milestone.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:35:41Z
  TYPE: FACT
  CLAIM: The first solo phase-11 implementation tranche is now in code. The
    seam-only solo family was replaced with solo-owned state, solo-owned setup,
    no-overrides, overrides, and finalize steps, plus solo-owned no-overrides
    and overrides compilers that work route-family-first over one visible root
    spell instead of depending on generalized step plans.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py:1-46
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_strategy.py:1-81
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:1-102
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_no_overrides_codegen_creation_step.py:1-79
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_overrides_codegen_creation_step.py:1-62
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:1-45
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:1-145
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:1-157
  IMPACT: Solo is no longer just a discovery id plus generalized strategy
    shell. It now has a real family-owned build path and is the first clean
    example for later shared-structure extraction.
  NEXT: run the focused phase-11 and creation-context validation ring for the
    new solo family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:37:56Z
  TYPE: MEASURE
  CLAIM: The focused solo phase-11 ring is green. The new solo family passes
    phase-11 discovery/creation tests and the creation-context builder route
    metadata tests, so the solo-owned family path is now live and compatible
    with the existing thin runtime seam.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-600
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-155
  IMPACT: Solo is the first real specialized phase-11 family beyond generalized.
    The remaining work is refinement and expansion, not basic family existence.
  NEXT: decide whether to harden the solo family further by splitting more route-
    specific behavior, or move to many-only with the solo pattern now visible.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:41:03Z
  TYPE: DECISION
  CLAIM: The obvious solo-family defensive guards are now removed. The
    compile-time solo steps no longer `None`-check `root_spell` or
    `resolve_route_key`, and the solo compilers no longer guard the shared
    route fallback with extra runtime raises. The family now relies on the
    compiler contract that the root spell and route are already known when
    phase 11 runs.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:1-76
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_no_overrides_codegen_creation_step.py:1-67
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_overrides_codegen_creation_step.py:1-50
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:1-40
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:1-133
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:1-166
  IMPACT: The solo family is cleaner and more honest to the compiler contract.
    It still preserves real runtime validation for user payloads such as bad
    `__args__`, but it stops pretending the compiler forgot its own root spell.
  NEXT: continue with either deeper solo route specialization or the first real
    many-only family build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:42:12Z
  TYPE: RISK
  CLAIM: The user reports that the solo-family implementation is not actually
    working end-to-end despite the focused ring staying green. That means the
    current narrow validation surface was insufficient and the next step is a
    broader compiler plus `creation_context` test ring before any more code
    changes.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_strategy.py:1-81
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:1-133
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:1-166
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:1-123
  IMPACT: We should assume the bug is in an uncovered integration seam until the
    broader ring proves otherwise.
  NEXT: run a wider spell-compiler and `creation_context` test suite, capture the
    first failing surface, then fix the real contract break instead of patching
    blindly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:43:00Z
  TYPE: CONFLICT
  CLAIM: The wider validation ring exposed a real phase-10 regression introduced
    by the dedicated lane-builder refactor. The generalized helper methods like
    `_creation_target_for_existence`, `_extract_param_keys`,
    `_occurrence_for_instance_key`, and `_build_fast_transient_plan` are no
    longer available on `SpellGeneralizedCodegenPlanBuilder`, so planner tests
    and component runs fail during `patch_maps`.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_spell_generalized_codegen_lane_plan_core.py:204-390
  - tests/component/melder/spellbook/spell_compiler/test_spell_codegen_pipeline_component.py:136-136
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:618-618
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1011-1314
  IMPACT: The workspace is not in a clean state until the generalized builder
    regains those helper methods and the wider compiler ring goes green again.
  NEXT: fix the generalized lane-builder class layout, then rerun the same wider
    compiler and `creation_context` test suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T09:48:02Z
  TYPE: FACT
  CLAIM: The generalized lane-builder regression is fixed. The rerun wider ring
    dropped from 20 failures to 1. The remaining failure is a metadata-compat
    seam in the generalized phase-11 no-overrides step: the component path still
    expects `_no_overrides_executor_signature`, while the generalized step only
    writes `no_overrides_executor_signature`.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spell_compiler_component_system.py:703-703
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:51-76
  - src/melder/aether/spellbook/spell_compiler/phases/shared_compiler_executions.py:1374-1412
  IMPACT: The remaining break is narrow and phase-11-local. After aliasing the
    underscore metadata key back onto the generalized path, the wider ring should
    tell us whether anything else is still wrong.
  NEXT: add `_no_overrides_executor_signature` alongside the current
    generalized metadata key and rerun the same wider validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: FACT
  CLAIM: The current solo phase-11 emit boundary is still too coarse. Solo
    setup resolves the emitted path from `spell_codegen_model.route_family`,
    and the processor currently collapses `unique`,
    `unique_per_conduit_cluster`, and `unique_per_conduit_lineage` into the
    same `"shared"` route family. That is acceptable for the runtime binder,
    but it is the wrong abstraction for the solo phase-11 compiler because the
    user wants exact emitted paths per root existence, not one shared solo
    closure bucket.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:40-50
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:128-143
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-182
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-233
  IMPACT: The next safe compiler-only optimization slice is to keep
    `CreationContext` route metadata coarse for the binder, but derive a second
    exact solo emit key from the root existence and compile exact per-existence
    closures from that key.
  NEXT: add an exact solo emit key to family state, switch the solo compilers
    to that key, and emit explicit closures for `unique`,
    `unique_per_conduit`, `unique_per_spell_space`, cluster, lineage, `many`,
    and `existing_creation`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: MEASURE
  CLAIM: The first exact-emit-key validation pass failed for a test-double
    reason, not a production-contract regression. The focused solo creation
    test builds a synthetic runtime record with `spell` and
    `has_disposal_methods` only; it does not include `existence`, so the new
    exact-key resolver raised on the test probe instead of on real model data.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:617-654
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:86-99
  IMPACT: The compiler-side exact emit-key change is still valid. The setup
    step just needs a truthful fallback to `runtime_record.spell.existence`
    when the test probe does not carry the processor-owned `existence` field.
  NEXT: patch the solo setup step fallback and rerun the same focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: FACT
  CLAIM: The same synthetic solo test probe is shallower than the real runtime
    model in two places: it omits `runtime_record.existence` and also omits
    `runtime_record.spell.existence`. The production contract still has exact
    existence on the processor/runtime record; only the synthetic probe needs a
    final fallback to `spell_codegen_model.route_family` when no exact
    existence field exists at all.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:623-641
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:90-102
  IMPACT: The fallback should be widened only enough for shallow test probes,
    without changing the real production preference order of exact existence
    first, route-family last.
  NEXT: add the final route-family fallback in the solo setup step and rerun
    the focused ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:12:58Z
  TYPE: FACT
  CLAIM: Solo phase-11 now emits from an exact solo emit key instead of the
    coarse route-family bucket. Setup still keeps the coarse `resolve_route_key`
    for the runtime binder, but it now derives `solo_emit_key` from the exact
    root existence when real model data is present, and the solo no-overrides
    and overrides compilers now compile explicit closure families for:
    `many`, `unique_per_conduit`, `unique_per_spell_space`, `unique`,
    `unique_per_conduit_cluster`, `unique_per_conduit_lineage`, and
    `existing_creation`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py:20-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:35-105
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:29-40
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-241
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-256
  IMPACT: Solo phase-11 is no longer lying about `unique`, cluster, and
    lineage as one emitted `shared` bucket. The compiler now owns exact
    existence-specific output while leaving the runtime binder contract alone.
  NEXT: use the harness to compare the exact-existence compiler output against
    the prior route-family-bucketed solo baseline and decide which exact solo
    lifetime still has the most cold-path waste.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:12:58Z
  TYPE: MEASURE
  CLAIM: The focused phase-11/runtime ring is green after the exact-emit-key
    change (`28 passed`). The experiment harness also reran cleanly and the new
    solo exact-existence baseline is:
    - `many`
      - `no_ns`: `172.520`
      - `meld_cold_ns`: `745.480`
      - `ov_ns`: `374.740`
    - `unique`
      - `no_ns`: `449.880`
      - `meld_cold_ns`: `1049.020`
      - `ov_ns`: `610.320`
    - `unique_per_conduit_cluster`
      - `no_ns`: `450.920`
      - `meld_cold_ns`: `1053.040`
      - `ov_ns`: `640.640`
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-654
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-155
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:739-993
  IMPACT: The compiler-side exact-path split is now the live baseline for solo
    optimization work. Future solo tuning can compare exact lifetimes instead
    of one shared emitted bucket.
  NEXT: inspect the remaining cold-create cost in the exact `unique`,
    `unique_per_conduit`, and spellspace solo closures, not the old shared
    route bucket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:20:06Z
  TYPE: FACT
  CLAIM: The current solo emitted closures still carry single-use local aliases
    for creations registration methods inside the hot path. That is not the
    right optimization pattern here because one local alias assignment plus one
    call is just extra work when the method is used once.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:39-173
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:33-252
  IMPACT: The next compiler-side cleanup is to remove those single-use local
    method aliases while keeping the exact per-existence solo emit split.
  NEXT: patch the solo compilers to call the creations methods directly, then
    rerun the harness and focused phase-11/runtime ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:23:20Z
  TYPE: DECISION
  CLAIM: The remaining shared owner-creation builder helpers in the solo
    compilers are the wrong abstraction even if they are compile-time only. The
    user wants exact per-existence emitted closures, so the next compiler fix is
    to remove the shared helper builders entirely and inline duplicate
    `unique`, cluster, and lineage closures directly in the solo compilers.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:149-239
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:162-255
  IMPACT: This keeps the solo phase-11 output aligned to exact emitted needs
    instead of letting compiler-side helper abstraction leak back into the hot
    path design.
  NEXT: remove the shared helper builders and inline exact per-existence owner
    closures, then rerun the harness and focused phase-11/runtime ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:23:20Z
  TYPE: DECISION
  CLAIM: The next bigger compiler move is now explicit: the route-specific
    runtime door should move into phase 11 for both `solo` and `generalized`,
    not stay split between phase-11 inner executors and `CreationContext`
    outer route wrappers. The target is that phase 11 emits the final
    no-overrides and overrides runtime doors for the selected family, while
    `CreationContext` shrinks toward gate handling plus direct dispatch.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-84
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:60-160
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:499-882
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:29-42
  IMPACT: The remaining ABI and exact-shape problems do not resolve cleanly by
    micro-optimizing closures. They resolve by changing ownership: phase 11
    must emit the actual runtime door, not only the inner create helper.
  NEXT: inspect the smallest refactor slice that moves one family's full route
    wrapper from `creation_context_codegen` into phase 11 while keeping the
    `SpellCodegenCreation` two-door handoff intact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:55:55Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: The current route-wrapper ownership split is now concrete. Today
    phase 11 emits the inner family executors, `CreationContextBuilder`
    passes `resolve_route_key` and `fast_transient_no_overrides_enabled`, and
    `creation_context_codegen.py` still emits the outer route-specific runtime
    doors for both no-overrides and overrides. So moving "all that shit" into
    phase 11 means moving the route wrappers, not just the inner create
    helpers. The tradeoff is now explicit:
    - if we keep the current 2-callable handoff
      (`no_overrides_executor`, `overrides_executor`), phase 11 can absorb a
      lot more route logic but `CreationContext` still has to own some hook/no-hook
      adaptation
    - if we want `CreationContext` to become almost literally one call, the
      handoff likely has to widen to 4 final runtime doors
      (hooks/no-hooks x no-overrides/overrides)
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-84
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:60-160
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:499-882
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:42-309
  IMPACT: The next architecture choice is not a micro-optimization question.
    It is a contract question: whether to keep the narrow 2-door handoff and
    accept some remaining adapter work in `CreationContext`, or widen phase 11
    output so the runtime binder becomes almost just gate + call.
  NEXT: keep the current handoff for now and treat the smallest safe future
    slice as "move no-overrides route wrappers into phase 11 first" before any
    decision about widening the output contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T14:56:24Z
  TYPE: FACT
  CLAIM: The live compiler/runtime seam is still split at the final route
    decision layer. Phase 11 now owns family discovery, plan-family/style
    selection, and the narrow `SpellCodegenCreation` handoff, but the runtime
    still recompiles the final hook/no-hook route wrappers from
    `resolve_route_key` inside `CreationContext` and
    `creation_context_codegen.py`. So the remaining work is not "make phase 11
    exist"; it is to pull the final route-specific wrapper ownership out of
    `CreationContext` and into the phase-11 output while preserving the current
    2-door handoff unless we intentionally widen that contract later.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-87
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:20-101
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:6-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:43-106
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:186-378
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-84
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:65-160
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:241-313
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-188
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:195-765
  IMPACT: This pins the exact migration target. If we want phase 11 to own the
    final runtime decision-making, generalized no-overrides and overrides route
    wrapper logic are the main extraction targets, while dynamic gate handling
    in `CreationContext` should stay runtime-owned.
  NEXT: separate the remaining runtime-owned policy from the still-compiler-owned
    route-wrapper logic by inspecting `creation_context_codegen.py` and the
    generalized phase-11 compilers for each route-specific branch they still
    own.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The solo family handoff into `CreationContext` is now exact enough to
    name the remaining split cleanly. Solo phase 11 already owns the root-only
    executor bodies: `SoloCreationContextSetupStep` resolves both the coarse
    `resolve_route_key` and the exact `solo_emit_key`, the no-overrides and
    overrides solo steps compile exact per-existence root executors, and the
    solo finalizer publishes those 2 executors plus `resolve_route_key`,
    `solo_emit_key`, and `fast_transient_no_overrides_enabled` onto
    `SpellCodegenCreation`. But `CreationContextBuilder` only consumes the 2
    executors, `resolve_route_key`, and the transient flag; it ignores
    `solo_emit_key`. Then `CreationContext.__init__` recompiles the 4 final
    hook/no-hook runtime doors from `resolve_route_key` through
    `creation_context_codegen.py`. So solo already moved exact emit selection
    into phase 11, but the final outer route-wrapper ownership still sits in
    `CreationContext`, not in the phase-11 output.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:85-109
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_strategy.py:35-83
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/solo_codegen_creation_state.py:15-57
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:28-56
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_creation_context_setup_step.py:83-105
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_no_overrides_codegen_creation_step.py:30-73
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_overrides_codegen_creation_step.py:30-60
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:27-44
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:37-85
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:65-168
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-188
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:195-765
  IMPACT: This gives us the exact migration rule for solo and generalized
    alike. If we want phase 11 to own the final decision-making, the next thing
    to pull is the outer route-wrapper compilation that still happens from
    `resolve_route_key` inside `CreationContext`, not the inner exact
    per-existence executor bodies that solo already owns.
  NEXT: map which of the current `creation_context_codegen.py` wrapper branches
    are pure route-shape decisions versus true runtime-only policy, then pick
    the first branch we can move into phase-11 output without widening the
    current 2-door contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: PLAN
  CLAIM: The first implementation slice is now pinned: phase 11 should publish
    the final no-hooks and hooks runtime doors, and `CreationContext` should
    stop recompiling those doors from route metadata. The migration will keep
    the emitted logic the same by reusing the current `creation_context_codegen`
    compile helpers, but it will move their call sites into the phase-11
    finalizers for the solo/generalized families. `CreationContextBuilder` will
    switch to consuming those final outputs directly, while existing-creation and
    cache rehydration keep local synthesis where phase-11 output does not exist.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:27-44
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:43-106
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:117-168
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:48-85
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:4-188
  IMPACT: This keeps the behavior stable while moving the final route-wrapper
    ownership out of runtime and into the compiler output, which is the cacheable
    layer the user wants.
  NEXT: patch `SpellCodegenCreation`, the solo/generalized phase-11 finalizers,
    and `CreationContext`/builder together so the runtime seam remains coherent.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: DECISION
  CLAIM: The active slice is narrower now. The user explicitly redirected the
    work away from the broader `CreationContext` ownership migration and onto a
    single concrete requirement: make the solo family emit cached codegen
    instead of returning handwritten closures. So this pass should touch only
    the solo no-overrides and solo overrides compiler files plus the focused
    compiler tests that prove source/code-object emission and cache use.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-120
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:4-140
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:1-260
  IMPACT: This keeps the pass reviewable and avoids reopening the broader
    runtime seam while still fixing the cache-hostile solo compiler behavior.
  NEXT: replace the handwritten solo closures with emitted source/code-object
    compilation, then add focused unit coverage that the solo compilers call the
    executor cache path and preserve current behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The solo compiler slice is now landed without reopening the broader
    runtime seam. `solo_no_overrides_codegen_creation_compiler.py` and
    `solo_overrides_codegen_creation_compiler.py` no longer return handwritten
    closures. They now emit literal per-lane source strings, compile through
    `get_or_compile_executor_code(...)`, and bind spell-static values through
    the exec namespace. The emitted behavior stays the same lane-by-lane:
    `many`, `unique_per_conduit`, `unique_per_spell_space`,
    `existing_creation`, `unique`, cluster, and lineage all still register and
    invoke exactly as before, but the code object is now cacheable.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:8-211
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:11-198
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:278-366
  IMPACT: Solo phase 11 now has cacheable emitted codegen output without any of
    the broader `CreationContext` ownership churn from the aborted pass.
  NEXT: if we continue this lane, the next step is either the same literal
    codegen treatment for `many_only` or the broader generalized/final-runtime
    ownership migration, but this solo slice itself is complete.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: MEASURE
  CLAIM: The focused solo compiler ring is green after the emit-codegen
    rewrite. The direct compiler file plus the existing solo strategy output
    tests both passed:
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py`
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py`
    using `.venv_new\\Scripts\\python.exe -m pytest ... -q`, and the runs
    passed `43` and `13` tests respectively. The only output was the existing
    pytest cache warning.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:278-366
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:596-660
  IMPACT: The solo emit path is validated as cache-backed without destabilizing
    the existing solo family contract.
  NEXT: no further work is required for the solo-only emit-codegen slice unless
    the user wants the same treatment applied to additional families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The next compiler-owned cleanup target is now explicit: phase 10
    already emits the `many_only` family, but phase 11 still routes that family
    through generalized creation machinery, and `fast_transient` is still owned
    by the generalized setup/no-overrides path instead of by a dedicated
    many-only phase-11 family. The current split is:
    - phase 10 discovery emits `plan_family_id="many_only"` and
      `candidate_codegen_style_ids=("generalized_many_only",)`
    - `SpellGeneralizedManyOnlyCodegenPlanStrategy` already uses the dedicated
      `SpellManyOnlyCodegenPlanBuilder`
    - `ManyOnlyCodegenCreationStrategy` is still only a family id over the
      generalized phase-11 steps
    - `GeneralizedCreationContextSetupStep` still derives
      `fast_transient_no_overrides_enabled` from `route_key == "many"` plus
      `no_overrides_plan.fast_transient_plan is not None`
    - `GeneralizedNoOverridesCodegenCreationStep` still builds transient schema
      and no-overrides signatures for that path
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:15-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/strategies/spell_generalized_many_only_codegen_plan_strategy.py:19-60
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:1548-1592
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2004-2065
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/many_only_codegen_creation_discovery_strategy.py:17-60
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_strategy.py:35-85
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_creation_context_setup_step.py:27-49
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:33-80
  IMPACT: `fast_transient` is still conceptually in the wrong family. As long
    as many-only phase 11 reuses generalized setup/no-overrides steps, we
    cannot remove the builder/transient bool from the generalized path cleanly
    or give `many_only` a truthful phase-11 identity.
  NEXT: create a dedicated many-only phase-11 no-overrides path that owns the
    transient specialization and related metadata, leaving generalized without
    that branch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: PLAN
  CLAIM: The first safe many-only extraction plan is compiler-only and keeps the
    runtime seam stable:
    1. Add a dedicated `ManyOnlyCodegenCreationState` surface for many-only-only
       no-overrides metadata, including the transient specialization facts.
    2. Replace generalized setup/no-overrides reuse inside
       `ManyOnlyCodegenCreationStrategy` with dedicated many-only steps.
    3. Move transient/no-overrides setup ownership from
       `GeneralizedCreationContextSetupStep` / `GeneralizedNoOverrides...Step`
       into new many-only setup/no-overrides steps.
    4. Introduce a dedicated many-only no-overrides compiler that emits codegen
       directly for the many-only lane, just like the new solo compiler pass.
    5. Leave overrides on generalized machinery for the first slice unless the
       emitted many-only no-overrides shape proves we also need a dedicated
       many-only overrides path immediately.
    6. Update focused discovery/creation/core tests to prove:
       - `many_only` still discovers correctly
       - many-only phase 11 no longer depends on generalized transient setup
       - generalized no longer owns the many fast-transient branch
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_strategy.py:49-85
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_creation_context_setup_step.py:27-49
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:33-80
  IMPACT: This gives us a narrow extraction order that removes `fast_transient`
    from generalized without reopening `CreationContext` or the broader final
    route-wrapper migration in the same pass.
  NEXT: inspect the existing many-only state/tests and then patch the many-only
    phase-11 family in that order: state -> steps -> compiler -> tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The many-only phase-11 family is now real instead of a generalized
    alias. `ManyOnlyCodegenCreationStrategy` no longer imports generalized step
    classes; it now owns a dedicated many-only state object plus dedicated
    setup/no-overrides/overrides/finalize steps under the `many_only` family
    directory. The many-only setup step now owns
    `fast_transient_no_overrides_enabled` directly, and the generalized setup
    and generalized no-overrides/finalize steps no longer derive or advertise
    the fast-transient branch.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_strategy.py:1-85
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/many_only_codegen_creation_state.py:1-64
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_creation_context_setup_step.py:1-49
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_no_overrides_codegen_creation_step.py:1-80
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_overrides_codegen_creation_step.py:1-118
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:1-117
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_creation_context_setup_step.py:27-48
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:33-80
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:101-116
  IMPACT: `fast_transient` is no longer conceptually stuck under generalized
    phase 11. Many-only now has its own family-local ownership surface for that
    branch, which is the prerequisite for later removing the transient bool
    from the `CreationContext` builder/runtime seam.
  NEXT: inspect whether the many-only no-overrides compiler itself now needs the
    same explicit emit-codegen treatment we gave solo, or whether the existing
    duplicated generalized compiler body is sufficient for the next pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: MEASURE
  CLAIM: The focused many-only/compiler ring is green after the family split and
    generalized fast-transient removal. The direct validation ring was:
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py`
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py`
    - `tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py`
    - `tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py`
    using `.venv_new\\Scripts\\python.exe -m pytest ... -q`, and the runs
    passed `15`, `10`, `9`, and `6` tests respectively. The only output was
    the existing pytest cache warning.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:311-374
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:147-192
  - tests/unit/melder/spellbook/spell_compiler/test_spell_codegen_planner_core.py:299-338
  - tests/component/melder/spellbook/spell_compiler/test_codegen_discovery_pipeline_component.py:85-129
  IMPACT: The many-only family split is stable enough to continue into the next
    compiler-only extraction without reopening phase-10 discovery or the
    broader runtime seam.
  NEXT: decide whether the next bounded slice is a dedicated many-only
    emit-codegen pass or the builder/runtime seam cleanup that removes the
    transient bool after many-only fully owns it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The copied many-only family no longer leaks generalized phase-11
    symbols. The bad cross-family helper call in
    `many_only_finalize_creation_context_step.py` was removed, and the
    many-only compilers now use local `ManyOnlyCodegenPlanTargetKind` /
    `ManyOnlyCodegenPlanCallMode` names instead of importing or emitting
    generalized-named constants in the many-only codegen surface. The
    many-only no-overrides compiler also stopped rediscovering whether steps
    are `Existence.many`; it now trusts the phase-10/plan contract and uses
    the presence of `fast_transient_plan` as the only transient compile switch.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:520-560
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:1-55
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:230-295
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:680-760
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:460-490
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:580-610
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1888-1905
  IMPACT: The many-only family is now internally coherent enough to continue
    as a true family instead of a generalized copy that still talks about the
    wrong strategy everywhere.
  NEXT: the remaining real work is functional, not naming cleanup: either make
    the many-only no-overrides compiler a hand-written emitted codegen path
    like solo, or move into the builder/runtime seam cleanup now that ownership
    is correct.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: DECISION
  CLAIM: The many-only compiler contract is now pinned by user clarification:
    `no_overrides` may not rediscover whether the lane is many-only and should
    use planner/model truth directly, but it still must branch on disposal
    presence because `many` results with disposal methods must be registered.
    `overrides` is different: it is still allowed to inspect existence/runtime
    shape because arbitrary override payloads can force different runtime
    behavior that phase 10 did not collapse away.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/data/spell_generalized_codegen_lane_plan.py:2203-2238
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_creation_context_setup_step.py:27-47
  IMPACT: The current pass must remove many-family rediscovery only from the
    many-only no-overrides compiler path. It must not flatten the overrides path
    into a fake always-many route that ignores valid override-sensitive runtime
    distinctions.
  NEXT: finish stripping no-overrides-only existence rediscovery from the
    many-only compiler helpers while preserving the disposal-registration split,
    and leave the overrides path existence checks intact.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T15:01:45Z
  TYPE: FACT
  CLAIM: The many-only no-overrides compiler now follows the clarified family
    contract. It no longer checks whether runtime steps are `Existence.many`
    to decide whether the family is valid, and it no longer carries generalized
    target-kind/call-mode names in its compiler surface. The no-overrides path
    now trusts the phase-10/plan contract for family membership and keeps only
    the disposal-registration split plus the existing-creation singleton branch
    inside `_construct_spell_instance(...)`. That remaining existence branch is
    not rediscovering many-only; it is the local call-target contract for a
    spell object that may still be an existing creation.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:255-295
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:749-837
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:913-920
  IMPACT: The no-overrides compiler now matches the intended ownership model:
    no many-family rediscovery, but still enough local information to register
    disposal-bearing `many` results correctly and handle existing-creation
    targets honestly.
  NEXT: the next remaining compiler-only cleanup is to decide whether many-only
    should get the same hand-written emitted-codegen treatment as solo or
    whether the current duplicated generalized compiler body is sufficient for
    the next runtime-seam slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:34:42Z
  TYPE: MEASURE
  CLAIM: The active many-only phase-11 no-overrides path is materially slower
    than the older generalized fast-transient path on the user benchmark
    surface. User-reported `test_shallow_all.py::test_threaded_di_stress_per_graph`
    results show the prior generalized fast path at about `135030 / 114325 /
    126784 / 27406` steps-per-second for `shallow / wide / diamond / deep`,
    while the current many-only path is about `123611 / 83684 / 111919 / 6220`.
    The regression is largest on `wide` and catastrophic on `deep`, which
    means the current many-only transient path is not preserving the old fast
    transient structure closely enough.
  EVIDENCE:
  - user_instruction
  - benchmarks/testing_other_di/test_shallow_all.py:2038-2112
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_creation_context_setup_step.py:27-46
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:1-1436
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1-1755
  IMPACT: The many-only family split is functionally correct but performance-
    regressed enough that it is not acceptable as-is. The optimization target
    is now concrete: recover the generalized transient fast-path shape inside
    the many-only family without dragging back generalized-only checks and
    branching we already removed.
  NEXT: trace the exact `fast_transient_plan` flow from the planner into the
    generalized no-overrides compiler, then compare that emitted shape against
    the current many-only no-overrides compiler and remove the extra work that
    does not belong in the dedicated many-only path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:41:16Z
  TYPE: FACT
  CLAIM: The live discovery rules are wired correctly for a true all-`many`
    visible spell set, but the stock `test_shallow_all.py` benchmark graphs the
    user quoted are not currently hitting the `many_only` family at all. Phase
    10 many-only discovery only claims models where the visible spell count is
    greater than one and every visible spell is `Existence.many`. The benchmark
    builder still binds spellspace roots as `Existence.unique_per_spell_space`
    before binding the rest as `Existence.many`, so the runtime probe for
    `shallow`, `wide`, `diamond`, and `deep` still landed on
    `plan_family_id="generalized"` and `selected_strategy_ids=("generalized_codegen_creation",)`.
    Those same probes also showed `fast_transient_plan is not None` on the
    generalized no-overrides lane while the emitted executor still came from
    the step-plan path (`<melder_no_overrides_codegen_creation_step_executor>`),
    not the transient executor path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/strategies/many_only_codegen_plan_discovery_strategy.py:1-48
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/strategies/many_only_codegen_creation_discovery_strategy.py:1-49
  - benchmarks/testing_other_di/test_shallow_all.py:1213-1270
  - benchmarks/testing_other_di/test_shallow_all.py:1603-1678
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:35-70
  IMPACT: We should not confuse the benchmark regression with proof that the
    stock benchmark is already exercising the many-only family. Right now the
    benchmark numbers the user quoted are only comparable to the many-only lane
    if the run was forced or the benchmark graph posture was changed to an
    all-`many` visible set. The live default benchmark still lands on
    generalized, and generalized is currently leaving its transient plan
    unused.
  NEXT: decide whether to optimize the dedicated many-only family under a
    forced/all-many benchmark surface, or first restore transient execution on
    the generalized default benchmark lane so the quoted baseline is actually
    represented in the live code again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:58:10Z
  TYPE: FACT
  CLAIM: The generalized no-overrides phase-11 path now actually consumes
    `fast_transient_plan` again, and `CreationContextBuilder` no longer needs
    the transient-selection bool to pick the runtime shape. The generalized
    no-overrides step now builds `transient_schema` from
    `no_overrides_plan.fast_transient_plan` and passes that through to the
    generalized compiler, generalized finalization now reports transient
    availability from the plan instead of hard-coding `False`, and the builder
    stopped reading `fast_transient_no_overrides_enabled` from
    `SpellCodegenCreation.metadata`. Runtime probes against the benchmark
    `wide` and `deep` graphs now show the generalized no-overrides executor
    compiling as `<melder_no_overrides_codegen_creation_transient_executor>`
    instead of the old step-plan executor.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_no_overrides_codegen_creation_step.py:35-70
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/steps/generalized_finalize_creation_context_step.py:93-113
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-80
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:1437-1510
  IMPACT: The default generalized benchmark lane can now hit the transient
    executor without widening the `CreationContext` builder/runtime seam or
    teaching the builder which no-overrides flavor phase 11 selected.
  NEXT: validate the generalized fast-transient path on the benchmark surface
    the user cares about, then return to the dedicated many-only family only if
    the generalized default path is no longer the bottleneck.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:34:03Z
  TYPE: PLAN
  CLAIM: The active implementation slice is now narrower than the earlier
    recursive experiment idea. Before testing a recursive many path, we are
    stripping the remaining existence-driven logic out of the live
    `many_only` family. The no-overrides compiler should trust the family
    contract completely and emit one of 2 disposal-specialized paths:
    fully disposal-free or disposal-aware. The overrides compiler will keep
    override/runtime mechanics, but it should get the same disposal-shape split
    instead of paying generic disposal checks everywhere.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:603-1094
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1788-2260
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:3038-3122
  IMPACT: This keeps the next pass inside the many-only family itself and
    gives the harness a fairer compiler target after the family stops carrying
    generalized-style existence and disposal branching.
  NEXT: patch many-only no-overrides first, then patch overrides disposal-shape
    emission, then rerun the forced-family harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:38:12Z
  TYPE: FACT
  CLAIM: The many-only no-overrides compiler now trusts the family contract
    instead of carrying leftover existence-driven runtime behavior. The live
    no-overrides step-plan emitter no longer constructs each step twice, no
    longer hydrates or branches on existence in the many-only path, and now
    forks the emitted executor by disposal posture:
    - disposal-free path: no registration code emitted
    - disposal-aware path: direct `add_many_creations(...)` emission only for
      steps whose spells declare disposal methods
    The many-only overrides path also now uses the shape-specialized emitted
    source for its empty/baseline executor instead of the generic override
    source path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:246-333
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py:687-876
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_overrides_codegen_creation_step.py:92-149
  IMPACT: The many-only family is now much closer to a truthful many-only
    compiler surface instead of a generic generalized fork carrying dead
    existence logic and wasted work.
  NEXT: use the forced-family harness numbers from this pass to decide whether
    the next optimization target is remaining many-only override cost or a
    deeper planner/compiler shape change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:38:12Z
  TYPE: MEASURE
  CLAIM: The focused validation ring stayed green and the forced-family harness
    moved the live many-only row in the right direction. Validation:
    - `tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py`
      -> `15 passed`
    - `tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py`
      -> `1 passed`
    Updated forced `many` row:
    - generalized:
      - `no_ns=493.820`
      - `meld_cold_ns=918.460`
      - `ov_ns=1292.300`
    - many_only:
      - `no_ns=424.380`
      - `meld_cold_ns=798.720`
      - `ov_ns=1297.860`
    Ratios (`many_only / generalized`):
    - `no=0.859382`
    - `cold=0.869630`
    - `ov=1.004302`
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-1
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:619-1011
  IMPACT: The many-only compiler slice improved the no-overrides and cold meld
    surfaces materially enough to beat generalized on the forced `many` row,
    but overrides are still effectively at parity/slightly worse.
  NEXT: inspect the remaining many-only overrides path if we want the whole
    many row to beat generalized cleanly on every measured surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:45:41Z
  TYPE: FACT
  CLAIM: The forced-family harness itself was still slightly unfair on the
    `many` row: many-only was being timed on a legal two-visible-spell
    all-`many` setup, but generalized was still being timed on a one-visible-
    spell setup. The harness now binds the same extra visible `many` spell for
    the generalized forced `many` row too, so the generalized versus many-only
    comparison is finally apples-to-apples on the visible graph shape.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:365-406
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:798-923
  IMPACT: The `many` row is now a cleaner strategy-family comparison instead of
    mixing a one-visible-spell generalized case against a two-visible-spell
    many-only case.
  NEXT: use the corrected `many` row as the baseline for any further many-only
    overrides tuning.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:45:41Z
  TYPE: MEASURE
  CLAIM: After the harness fairness correction, the forced `many` row still
    favors the current many-only no-overrides path over generalized while
    leaving overrides slightly behind:
    - generalized:
      - `no_ns=478.600`
      - `meld_cold_ns=927.000`
      - `ov_ns=1372.040`
    - many_only:
      - `no_ns=374.660`
      - `meld_cold_ns=781.720`
      - `ov_ns=1412.060`
    Ratios (`many_only / generalized`):
    - `no=0.782825`
    - `cold=0.843279`
    - `ov=1.029168`
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:619-1011
  IMPACT: The many-only disposal-specialized refactor is still a real win on
    the no-overrides surfaces under a fairer `many` comparison. The remaining
    gap is isolated to overrides.
  NEXT: if we continue, focus only on the many-only overrides executor body and
    keep the no-overrides path frozen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T19:49:20Z
  TYPE: FACT
  CLAIM: The remaining `many_only` gap is concentrated in the shape-specialized
    overrides emitter, not the planner or the no-overrides path. The current
    many-only shape source still carries generalized-style runtime structure:
    route-kind fields, existence-driven branch metadata, existing-instance
    guard semantics, and generic helper plumbing that the all-`many` family
    does not need. Since phase 10 already guarantees the family is all many
    and bind rules already force existing-object spells to `Existence.unique`,
    the many-only overrides shape path can collapse to:
    - caller-creations only
    - callable/value invoke only
    - no reuse/existing-instance path
    - disposal-free vs disposal-aware registration only
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:564-609
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1788-2475
  - src/melder/aether/spellbook/bind/bind.py:476-510
  IMPACT: The next safe iteration is to rewrite only the many-only
    shape-specialized overrides source around the true many-only contract,
    leaving planner selection and the no-overrides win untouched.
  NEXT: simplify the many-only overrides shape source to all-many caller-creations
    semantics and rerun the harness; rollback the overrides compiler file if the
    `ov_ns` row regresses.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:04:14Z
  TYPE: MEASURE
  CLAIM: The many-only overrides-only rewrite is a successful harness-backed
    improvement and should be retained. The shape-specialized overrides path
    now collapses to the true all-`many` contract (caller-creations only, no
    reuse/existing-instance path, disposal-free vs disposal-aware registration
    only). On the fair forced `many` row:
    - before this override rewrite:
      - generalized `ov_ns=1372.040`
      - many_only `ov_ns=1412.060`
      - ratio `1.029168`
    - after this override rewrite:
      - generalized `ov_ns=1263.580`
      - many_only `ov_ns=1298.040`
      - ratio `1.027272`
    The no-overrides and cold meld wins stayed intact:
    - generalized `no_ns=505.600`, `meld_cold_ns=945.880`
    - many_only `no_ns=400.260`, `meld_cold_ns=795.860`
    - ratios `no=0.791653`, `cold=0.841396`
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1808-1868
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:2221-2475
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:619-1011
  IMPACT: The many-only family is now better on the no-overrides and cold meld
    surfaces and less bad on overrides under the fair all-`many` harness. The
    remaining override gap is much smaller and isolated.
  NEXT: checkpoint this overrides improvement, then inspect whether the
    remaining `ov_ns` gap comes from the override targeting/apply path or from
    the emitted override executor body itself.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:16:08Z
  TYPE: FACT
  CLAIM: The next many-only investigation target is now narrower than the
    whole overrides path. A direct probe on the fair forced-`many` setup shows:
    - override-targeting apply cost is nearly identical
      - generalized `167.16ns`
      - many_only `171.74ns`
    - emitted override source shape is nearly identical
      - generalized `63` lines / `2662` chars
      - many_only `64` lines / `2697` chars
    - the larger measured gap appears inside the direct override executor body
      more than in target application
      - generalized direct override executor `1076.34ns`
      - many_only direct override executor `1161.09ns`
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:564-609
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:564-609
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1808-2475
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1808-2150
  IMPACT: The next likely wins are in the emitted override executor body
    itself, not in override-targeting/apply or broad plan-family selection.
  NEXT: inspect the generalized-vs-many emitted override body line-by-line for
    one-step targeted override and remove any remaining extra work from the
    many-only executor body only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T20:18:58Z
  TYPE: MEASURE
  CLAIM: The latest body-level many-only overrides trim is another retained
    improvement. The direct change was small: stop emitting the unused
    `spell_id_{step_index}` local on disposal-free many-only override shapes.
    The focused unit ring stayed green, and the fair forced-`many` harness now
    reports:
    - generalized:
      - `no_ns=458.100`
      - `meld_cold_ns=907.880`
      - `ov_ns=1217.240`
    - many_only:
      - `no_ns=375.960`
      - `meld_cold_ns=776.460`
      - `ov_ns=1271.840`
    Ratios (`many_only / generalized`):
    - `no=0.820694`
    - `cold=0.855245`
    - `ov=1.044856`
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1833-1844
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-1
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:619-1011
  IMPACT: The many-only lane is still winning on no-overrides and cold meld,
    and the override row keeps moving on tiny executor-body trims. There is
    still iteration headroom in the emitted many-only override body itself.
  NEXT: continue body-level generalized-vs-many comparison for the one-step
    targeted override path and keep only changes that improve `ov_ns` without
    giving back the no-overrides wins.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the next compiler refactor lane after the mutation cleanup.
The runtime handoff to `CreationContext` is treated as stable for now; the work
here is to reorganize phase 10 and phase 11 strategies into smaller, better
named groups and make discovery choose real strategy families before we expand
the system further.
