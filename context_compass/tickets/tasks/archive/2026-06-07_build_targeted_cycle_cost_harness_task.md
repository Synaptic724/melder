# Task: Build Targeted Cycle Cost Harness

## Metadata
- Task ID: TASK-2026-06-07-build-targeted-cycle-cost-harness
- Story: none
- Epic: EPIC-2026-06-07-optimize-meld-hotpath
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p0
- Created: 2026-06-07T12:41:06Z
- Updated: 2026-06-07T12:58:23Z

## Objective
Create a dedicated experimentation harness under `tests/experimentation/` that
isolates cycle costs for:
- pooled lesser conduit create/cleanup,
- pooled spellspace enter/exit,
- front-door meld on top of those scopes.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new harness in
  `tests/experimentation/` targeted at lesser conduit, spellspace, and meld
  cycle costs.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/conduit_pool.py`
  - `src/melder/aether/conduit/spell_space/`
  - `src/melder/aether/conduit/meld/`
  - `benchmarks/testing_other_di/test_melder_gauntlet.py`
  - `benchmarks/testing_other_di/test_real_world_gauntlet.py`
  - `codex/context_compass/tickets/tasks/2026-06-07_build_targeted_cycle_cost_harness_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
  - `tickets/tasks/2026-06-07_run_real_world_gauntlet_baseline_task.md`
  - `tickets/tasks/2026-06-07_reduce_lesser_conduit_pooled_cycle_cost_task.md`
  - `tests/experimentation/melder_spellspace_cycle_testbench.py`
- EXIT_GATE:
  - one dedicated targeted harness exists under `tests/experimentation/`,
  - the harness measures lesser, spellspace, and meld surfaces separately,
  - the harness runs and prints usable baseline output.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the harness needs broader
  runtime debug seams than are justified by the current benchmark evidence.

## Scope Boundaries
- In scope:
  - new experimentation harness file
  - cycle-specific timing breakdowns
  - reuse of ideas from existing gauntlet and spellspace benches
- Out of scope:
  - production runtime optimization edits
  - unrelated benchmark suites
  - replacing the existing gauntlet or forced-family harness

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a dedicated harness in
  `tests/experimentation/` for the current cycle-cost targets.

## Steps / Checklist
- [ ] Define the minimal benchmark shapes and measured surfaces.
- [ ] Implement the targeted harness under `tests/experimentation/`.
- [ ] Run the harness and capture baseline output.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one targeted cycle-cost harness in `tests/experimentation/`
- one baseline run from that harness

## Files / Paths Impacted
- `tests/experimentation/`
- `codex/context_compass/tickets/tasks/2026-06-07_build_targeted_cycle_cost_harness_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Run:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py`
  - Result: `1 passed, 1 warning in 0.37s`
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py`
  - Result: `1 passed, 1 warning in 0.32s`
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/<new_harness_file>.py`

## Risks / Rollback Notes
- Risk: create a harness that still mixes lesser/spellspace/meld cost too much
  to guide optimization.
- Risk: overfit the harness to one benchmark shape and lose comparability with
  the gauntlet.
- Rollback: keep the new harness additive and leave the existing gauntlet
  untouched.

## Applicable Anti-Patterns
- [ ] No production optimization edits in this task.
- [ ] No benchmark claims without a run.
- [ ] No harness complexity that obscures the specific cycle surfaces.

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
  - lesser pooled cycle
  - spellspace pooled cycle
  - meld front-door cycle
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-07T12:58:23Z
  TYPE: MEASURE
  CLAIM: The deeper pooled-lifecycle breakdown harness now isolates the internal
    substeps inside the lesser and spellspace steady-state cycles:
    - pooled lesser:
      - acquire total: `2140.267 ns`
      - cleanup total: `3885.900 ns`
      - `ConduitPool.create_object`: `446.567 ns`
      - `ConduitWard._link_lesser_conduit`: `889.433 ns`
      - `Conduit._prepare_for_pool`: `3723.467 ns`
      - `Conduit._cleanup_spellspaces_for_pool`: `507.500 ns`
      - lesser `Creations.reset_for_pool`: `460.200 ns`
      - `ConduitWard._detach_for_pool`: `769.700 ns`
      - `ConduitPool.return_lesser_conduit`: `351.067 ns`
      - acquire residual: `804.267 ns`
      - prepare residual: `1635.000 ns`
      - cleanup residual: `162.433 ns`
    - pooled spellspace:
      - enter total: `3311.433 ns`
      - exit total: `3790.133 ns`
      - `AbstractElasticPool.acquire`: `1365.367 ns`
      - `SpellSpacePool.prepare_object`: `304.467 ns`
      - `SpellSpaceThreadState.get`: `446.133 ns`
      - `SpellSpaceThreadState.set`: `537.667 ns`
      - `SpellSpace.cleanup`: `2353.833 ns`
      - `SpellSpace._cleanup_for_pool_reuse`: `1087.000 ns`
      - spellspace `Creations.reset_for_pool`: `497.267 ns`
      - `SpellSpacePool.release`: `348.767 ns`
      - enter residual: `962.267 ns`
      - exit residual: `452.500 ns`
      - cleanup residual: `918.067 ns`
      - cleanup-for-pool residual: `589.733 ns`
  EVIDENCE:
  - tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py:1-495
  - pooled_breakdown_harness_run_output
  IMPACT: The pooled lifecycle costs are no longer a black box.
    - lesser: the dominant cleanup bucket is `Conduit._prepare_for_pool`, and
      the biggest unmeasured interior cost still sits inside that method rather
      than in `Creations.reset_for_pool`, ward detach, or pool return alone.
    - spellspace: total cost is split between pool acquire, thread-local
      stack get/set, and cleanup; the cleanup side still has real residual cost
      after `reset_for_pool` and pool release, so registry/flag/wrapper work is
      not trivial.
  NEXT: investigate the unmeasured interior work inside
    `Conduit._prepare_for_pool` and the threadstate/context-manager overhead in
    `enter_spellspace` / `cleanup`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:58:23Z
  TYPE: FACT
  CLAIM: Based on the deeper breakdown, the first runtime-edit priority should
    stay on pooled lifecycle rather than meld:
    1. lesser `prepare_for_pool` residual (`~1.64us`) is the single biggest
       unexplained bucket in the whole pooled cycle path,
    2. spellspace enter/exit also pays nearly `1.0us` of non-pool,
       non-threadstate wrapper cost on enter and about `0.92us` of cleanup
       wrapper residual,
    3. warm meld remains cheaper than both pooled lifecycle totals.
  EVIDENCE:
  - tests/experimentation/test_targeted_pooled_cycle_breakdown_harness.py:1-495
  - tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py:1-502
  IMPACT: The next investigation/edit slice should start with
    `Conduit._prepare_for_pool` and only then move to spellspace
    context-manager/threadstate cleanup work.
  NEXT: open the next task against `Conduit._prepare_for_pool` substep
    decomposition and optimization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:46:04Z
  TYPE: MEASURE
  CLAIM: The new targeted harness now runs cleanly and produced the first
    separated baseline:
    - pooled lesser cycle:
      - acquire: `1171.800 ns`
      - cleanup: `1710.333 ns`
      - total: `2882.133 ns`
    - pooled spellspace cycle:
      - enter: `1597.000 ns`
      - exit: `1429.733 ns`
      - total: `3026.733 ns`
    - meld on persistent lesser:
      - `unique_per_conduit`
        - cold: `2322.833 ns`
        - warm: `463.933 ns`
      - `shared_unique`
        - cold: `3246.767 ns`
        - warm: `439.967 ns`
      - `many`
        - cold only: `1830.200 ns`
    - meld on persistent spellspace:
      - `unique_per_spell_space`
        - cold: `2997.267 ns`
        - warm: `397.633 ns`
  EVIDENCE:
  - tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py:1-502
  - targeted_harness_run_output
  IMPACT: The split is now explicit. Warm front-door meld is comparatively
    cheap (`~0.40-0.46us`). The bigger steady-state costs are:
    - pooled lesser cycle (`~2.88us`)
    - pooled spellspace cycle (`~3.03us`)
    - cold shared/spellspace meld (`~3.00-3.25us`)
    So the first real optimization pressure is not warm meld. It is pooled
    lifecycle and cold shared/spellspace create paths.
  NEXT: choose whether to attack pooled spellspace/lesser lifecycle first or
    the colder shared/spellspace meld path first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:46:04Z
  TYPE: FACT
  CLAIM: The harness confirms the gauntlet map. `many` cold meld is already the
    cheapest direct create route in this targeted surface (`1830.200 ns`), while
    `shared_unique` and `unique_per_spell_space` are the expensive front-door
    create routes because they still pay reuse-probe and locking behavior on top
    of the emitted executor. The pooled lifecycle surfaces are also large enough
    to matter on every gauntlet cycle.
  EVIDENCE:
  - tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py:355-502
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:430-760
  - src/melder/aether/conduit/conduit.py:336-379
  - src/melder/aether/conduit/spell_space/spell_space.py:113-159
  IMPACT: The next optimization order should likely be:
    1. pooled spellspace / lesser lifecycle,
    2. cold shared + spellspace meld path,
    3. unique_per_conduit cold meld.
    `many` warmless create does not look like the first target.
  NEXT: open the next runtime-edit task against the chosen top target.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:42:51Z
  TYPE: FACT
  CLAIM: The harness shape is now explicit. It should keep the broad gauntlet
    ideas but split the surfaces apart instead of timing them together:
    - metric group A: pooled lesser cycle only
      `create_lesser_conduit() -> cleanup()`
    - metric group B: pooled spellspace cycle only on one persistent lesser
      `enter_spellspace() -> exit`
    - metric group C: front-door meld only on persistent scopes
      - `unique_per_conduit` cold and warm on one persistent lesser
      - `unique_per_spell_space` cold and warm on one persistent spellspace
      - `unique` cold and warm on shared owner-creations
      - `many` cold-create only
    The key design rule is to keep persistent lesser/spellspace objects alive
    during meld-only timing so lifecycle cost does not bleed into the meld
    numbers.
  EVIDENCE:
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-410
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-281
  - src/melder/aether/conduit/conduit.py:1632-1765
  - src/melder/aether/conduit/spell_space/spell_space.py:113-199
  IMPACT: The new harness can answer three distinct questions with one file:
    pooled lesser cost, pooled spellspace cost, and isolated meld cost.
  NEXT: implement the new harness file under `tests/experimentation/` and run
    it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:41:06Z
  TYPE: PLAN
  CLAIM: The user explicitly wants a dedicated cycle-cost harness under
    `tests/experimentation/`, separate from both the broad gauntlet and the
    phase10/11 forced-family harness. The harness should isolate three surfaces:
    pooled lesser conduit cycles, pooled spellspace cycles, and front-door meld
    cycles on top of those scopes.
  EVIDENCE:
  - user_instruction
  - tests/experimentation/melder_spellspace_cycle_testbench.py:1-410
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1172-1570
  - tickets/tasks/2026-06-07_run_real_world_gauntlet_baseline_task.md:1-260
  IMPACT: The next useful deliverable is a narrow benchmark surface that can
    guide runtime optimization more directly than the broad gauntlet.
  NEXT: define the benchmark shapes and measured surfaces, then implement the
    new harness file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the new additive experimentation harness for cycle-cost work. It
should separate lesser, spellspace, and meld costs more cleanly than the broad
gauntlet.
