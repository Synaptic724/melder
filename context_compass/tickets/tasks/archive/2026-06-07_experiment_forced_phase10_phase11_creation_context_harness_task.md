# Task: Experiment Forced Phase10 Phase11 CreationContext Harness

## Metadata
- Task ID: TASK-2026-06-07-experiment-forced-phase10-phase11-creation-context-harness
- Story: none
- Epic: EPIC-2026-06-02-explore-topdown-compiler-strategy-harness
- Status: in_progress
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-07T10:02:44Z
- Updated: 2026-06-07T12:09:10Z

## Objective
Build an experimentation harness under `tests/experimentation/` that runs the
compiler normally through phase 9, force-selects phase-10 and phase-11 families,
builds a real `CreationContext`, and compares generalized versus solo creation
resolution speed on the same graph.

## Ticket Contract
- ENTRY_GATE: the user explicitly redirected the compiler lane toward a forced
  experimentation harness instead of further production architecture changes.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - `codex/context_compass/tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-02_explore_topdown_compiler_strategy_harness_epic.md`
  - `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `tests/experimentation/test_creation_context_cache_asset_experiment.py`
  - `tests/experimentation/test_creation_context_override_cache_asset_experiment.py`
- EXIT_GATE:
  - one experiment harness exists under `tests/experimentation/`
  - the harness runs phases 1-9 normally
  - the harness force-selects phase 10 and phase 11 families explicitly
  - the harness records at least one generalized vs solo timing comparison
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the harness cannot force the
  family seams cleanly without introducing production-only debug surfaces.

## Scope Boundaries
- In scope:
  - one forced family-selection experimentation harness
  - direct experiment-only forcing of plan and creation families
  - timing `CreationContext` resolution speed
  - task/board state for this experiment lane
- Out of scope:
  - production forcing APIs
  - permanent compiler debug configuration
  - broad production refactors outside experiment support

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a harness that unwinds the
  compiler and forces phase-10/phase-11 values before timing resolution.

## Steps / Checklist
- [ ] Inspect the current experimentation helpers and direct forcing seams.
- [ ] Define the smallest generalized-vs-solo comparison harness.
- [ ] Implement the harness under `tests/experimentation/`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one experimentation harness file under `tests/experimentation/`
- one recorded generalized vs solo timing result

## Files / Paths Impacted
- `tests/experimentation/`
- `codex/context_compass/tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/<new_harness_file>.py`

## Risks / Rollback Notes
- Risk: the harness accidentally benchmarks discovery plumbing instead of the
  actual `CreationContext` resolution seam.
- Risk: experiment-only forcing drifts from the real compiler contract.
- Rollback: keep the forcing local to `tests/experimentation/` and avoid
  production debug surfaces in this slice.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No production forcing surface in this task unless explicitly approved.
- [ ] No benchmark claims without the actual harness output recorded.

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
  - force phase-10 plan family for experiments
  - force phase-11 creation family for experiments
  - time `CreationContext` resolution
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-07T12:09:10Z
  TYPE: PLAN
  CLAIM: The user explicitly redirected this lane from general harness follow-up
    into a hot-path attribution pass for real meld execution. The immediate
    read set is the live runtime chain the user named:
    `meld.py`, `conduit.py`, `creation_context.py`, `creations.py`,
    `spell_space.py`, the live `spellbook.py`, and the forced-family harness.
  EVIDENCE:
  - user_instruction
  - codex/context_compass/attention_board.md:22-22
  IMPACT: The next useful result is not another table-format tweak. It is an
    evidence-backed map of where the front-door `conduit.meld(...)` time is
    spent relative to the emitted `CreationContext` seam, followed by a harness
    run interpreted against that boundary.
  NEXT: read the named runtime files, map the hot path through
    `Conduit -> Meld -> CreationContext -> Creations/SpellSpace/Spellbook`,
    then rerun the forced-family harness with that attribution in hand.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:02:44Z
  TYPE: PLAN
  CLAIM: The first harness slice should stay narrow and honest: run phases 1-9
    normally, force phase-10 and phase-11 family choices locally inside the
    experiment, build the real `CreationContext`, and time the resolution path
    there instead of timing the full compiler every run.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-113
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-112
  IMPACT: This keeps the benchmark targeted on the runtime creation seam while
    avoiding premature production debug/forcing features.
  NEXT: inspect the current experimentation helpers and implement the smallest
    generalized-vs-solo comparison harness under `tests/experimentation/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:02:44Z
  TYPE: FACT
  CLAIM: We do not need a production debug switch to force the comparison. The
    harness can unwind at the phase-9 boundary, build `SpellCodegenPlan`
    directly with forced phase-10 family metadata, then build
    `SpellCodegenCreation` directly with forced phase-11 family ids and style
    metadata before passing the result into the real `CreationContextBuilder`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:1-113
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:1-112
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/codegen_plan_discovery_system/codegen_plan_discovery.py:1-31
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_discovery_system/codegen_creation_discovery.py:1-25
  IMPACT: The harness can stay experiment-local and compare forced family
    outputs without introducing a permanent production forcing API first.
  NEXT: implement the harness file around that direct forced plan/creation seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:07:50Z
  TYPE: FACT
  CLAIM: The first harness implementation is now in `tests/experimentation/`.
    It binds one-spell `Existence.many` roots, conjures normally so phase-9
    truth is real, force-builds phase-10 and phase-11 outputs directly through
    the real strategy builders, rebuilds `CreationContext`, and then times
    generalized versus solo `execute_no_hooks(...)` on both no-overrides and
    root-overrides paths.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-305
  IMPACT: The experiment now measures the actual creation seam we care about
    without requiring a production forcing API.
  NEXT: run the harness directly and record the first generalized-vs-solo timing output.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:08:37Z
  TYPE: MEASURE
  CLAIM: The first harness run produced one usable result and one harness-shape
    failure. The forced overrides comparison already ran and printed timings,
    but the no-overrides comparison hit an emitted generalized no-overrides
    executor edge case for the root-only class scenario (`IndexError` inside
    the generated step executor). That means the harness should switch the
    no-overrides scenario to a callable `many` root so we measure the intended
    fast creation seam instead of tripping over that class-shape edge case.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:252-326
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:405-439
  IMPACT: The experiment direction is still valid, but the no-overrides scenario
    needs to be reshaped before the comparison is trustworthy.
  NEXT: change the no-overrides scenario to a callable `many` root and rerun the
    same harness file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:11:50Z
  TYPE: MEASURE
  CLAIM: The harness now runs cleanly and produced the first two results.
    1. No-overrides, one visible `unique_per_conduit` root:
       - forced generalized path still fails in the harness with
         `IndexError: list index out of range`
       - forced solo path measured `612.33 ns/iter`
    2. Overrides, one visible `many` root:
       - forced generalized path measured `1187.565 ns/iter`
       - forced solo path measured `645.805 ns/iter`
       - solo/generalized ratio: `0.5438060232492536`
    The no-overrides scenario is still useful because it proves a real
    generalized root-only edge case while the solo path already works there.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-545
  IMPACT: We now have a real experiment seam for comparing forced families.
    The first measurable result says solo is materially faster than generalized
    on the current root-overrides `many` scenario, while generalized still has a
    root-only no-overrides edge case in this forced harness shape.
  NEXT: decide whether to harden the generalized root-only no-overrides path for
    a fairer comparison, or move straight into many-only harness scenarios using
    the same forcing pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:16:25Z
  TYPE: FACT
  CLAIM: The generalized no-overrides failure is a harness invalidation bug, not
    evidence that the generalized no-overrides family itself is broken. The
    harness currently forces generalized, then forces solo on the same spell
    artifact before timing generalized. That cleanup path replaces and cleans the
    previous forced plan and creation artifact, so the already-built generalized
    `CreationContext` can end up holding closures over cleared plan-owned data.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:61-107
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:203-235
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_plan.py:63-89
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation/spell_codegen_creation.py:46-63
  IMPACT: The no-overrides comparison is not trustworthy until the harness stops
    building both forced families on the same artifact before measuring the first.
  NEXT: change the harness to time generalized first, then rebuild the artifact
    for solo afterward and rerun the same experiment file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:17:25Z
  TYPE: MEASURE
  CLAIM: The corrected harness now has clean generalized-vs-solo numbers for
    both forced scenarios:
    1. No-overrides, one visible `unique_per_conduit` root:
       - generalized: `1077.265 ns/iter`
       - solo: `647.75 ns/iter`
       - solo/generalized ratio: `0.6012912328907`
    2. Overrides, one visible `many` root:
       - generalized: `1264.275 ns/iter`
       - solo: `655.935 ns/iter`
       - solo/generalized ratio: `0.5188230408732276`
    The earlier generalized no-overrides failure was only the harness
    invalidating the generalized plan/creation artifact before timing it.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-549
  IMPACT: We now have the first clean forced-family comparison at the real
    `CreationContext` seam, and solo is materially faster than generalized in
    both tested solo scenarios.
  NEXT: decide whether to expand the same harness across more solo existences
    (`shared`, `spellspace`, `existing_creation`) or move on to a many-only
    forced-family harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:20:30Z
  TYPE: DECISION
  CLAIM: The next harness slice is now explicitly narrowed. Instead of mixing
    overrides and no-overrides, the experiment should focus only on solo graphs
    on the no-overrides path and compare generalized versus solo across the solo
    route-family matrix. The initial matrix should cover:
    - `many`
    - `unique_per_conduit`
    - `unique_per_spell_space`
    - one representative shared route (`Existence.unique`)
    Shared-cluster and shared-lineage can stay out for now because they collapse
    to the same runtime `shared` route family in the current processor/runtime
    seam.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:128-143
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:43-48
  IMPACT: The harness will produce a table that is cleaner, more targeted, and
    easier to compare than the mixed override/no-override experiment.
  NEXT: rewrite the experiment file to emit a solo-only no-overrides table with
    at least 1000 timed iterations per scenario.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:22:43Z
  TYPE: MEASURE
  CLAIM: The solo-only no-overrides matrix is now running and printing a table.
    With `10000` timed iterations and `1000` warmup iterations per scenario, the
    current forced generalized vs solo results are:
    - `solo_many_no_overrides`
      - generalized: `489.210 ns/iter`
      - solo: `149.610 ns/iter`
      - ratio: `0.305820`
    - `solo_unique_per_conduit_no_overrides`
      - generalized: `996.120 ns/iter`
      - solo: `598.890 ns/iter`
      - ratio: `0.601223`
    - `solo_spellspace_no_overrides`
      - generalized: `1098.860 ns/iter`
      - solo: `721.020 ns/iter`
      - ratio: `0.656153`
    - `solo_shared_unique_no_overrides`
      - generalized: `113.880 ns/iter`
      - solo: `98.560 ns/iter`
      - ratio: `0.865472`
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-403
  IMPACT: We now have the first clean solo-only table across the main route
    families, and solo is faster than generalized in every currently measured
    solo no-overrides scenario.
  NEXT: decide whether to extend the same table to shared-cluster/shared-lineage
    representatives, or move to a many-only matrix next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:30:58Z
  TYPE: FACT
  CLAIM: The exact-existence expansion exposed a harness-specific shared-route
    bug. For shared categories, the harness builds the forced context with an
    owner-creations override, but then restores `spell._owner_creations`
    immediately afterward. The solo shared-route compiler still consults
    `spell._owner_creations` at call time, so the measurement falls back onto
    the conduit store instead of the fresh owner probe and quickly hits
    duplicate-registration errors.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:217-239
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:418-444
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:63-85
  IMPACT: The exact-existence matrix is valid in direction, but shared-category
    rows need the owner-probe override to stay live through measurement.
  NEXT: keep the forced owner-creations override alive for shared-category
    measurements and rerun the exact-existence matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:32:00Z
  TYPE: FACT
  CLAIM: `existing_creation` is a true boundary exception for this harness.
    It bypasses phases 8-11, so there is no phase-9 model and no forced
    phase-10/phase-11 family seam to compare there. That means the
    exact-existence table should still include `existing_creation`, but it needs
    an explicit `phase10_11_bypassed` note instead of fake generalized-vs-solo
    numbers.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:39-71
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:43-100
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:66-99
  IMPACT: The matrix can still be complete by category without lying about
    comparability where the compiler seam does not exist.
  NEXT: adjust the harness table formatter and row logic so `existing_creation`
    is included with an explicit note and no forced family timings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:33:17Z
  TYPE: MEASURE
  CLAIM: The exact solo existence matrix is now running cleanly with both
    no-overrides and overrides columns. With `5000` timed iterations and `1000`
    warmup iterations per comparable scenario, the current forced generalized vs
    solo results are:
    - `many`
      - no-overrides:
        - generalized: `474.740 ns/iter`
        - solo: `253.840 ns/iter`
        - ratio: `0.534693`
      - overrides:
        - generalized: `1266.400 ns/iter`
        - solo: `787.220 ns/iter`
        - ratio: `0.621620`
    - `unique_per_conduit`
      - no-overrides:
        - generalized: `1063.100 ns/iter`
        - solo: `688.520 ns/iter`
        - ratio: `0.647653`
      - overrides:
        - generalized: `2314.680 ns/iter`
        - solo: `976.260 ns/iter`
        - ratio: `0.421769`
    - `unique_per_spell_space`
      - no-overrides:
        - generalized: `1201.740 ns/iter`
        - solo: `712.960 ns/iter`
        - ratio: `0.593273`
      - overrides:
        - generalized: `2511.700 ns/iter`
        - solo: `1068.420 ns/iter`
        - ratio: `0.425377`
    - `unique`
      - no-overrides:
        - generalized: `1255.360 ns/iter`
        - solo: `810.580 ns/iter`
        - ratio: `0.645695`
      - overrides:
        - generalized: `2232.460 ns/iter`
        - solo: `1037.140 ns/iter`
        - ratio: `0.464573`
    - `unique_per_conduit_cluster`
      - no-overrides:
        - generalized: `1390.140 ns/iter`
        - solo: `760.120 ns/iter`
        - ratio: `0.546794`
      - overrides:
        - generalized: `2332.440 ns/iter`
        - solo: `1037.760 ns/iter`
        - ratio: `0.444925`
    - `unique_per_conduit_lineage`
      - no-overrides:
        - generalized: `1338.740 ns/iter`
        - solo: `778.400 ns/iter`
        - ratio: `0.581442`
      - overrides:
        - generalized: `2596.720 ns/iter`
        - solo: `1211.820 ns/iter`
        - ratio: `0.466673`
    - `existing_creation`
      - marked `phase10_11_bypassed`
      - no forced phase-10/phase-11 comparison exists there because that path
        does not produce a phase-9 model or phase-10/phase-11 artifact seam.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-751
  IMPACT: The harness now tests exact solo existence categories instead of
    collapsing them into one `shared` bucket, and solo is faster than generalized
    in every currently comparable solo existence scenario.
  NEXT: decide whether to extend the matrix to more solo spell-shape variants
    (method/lambda/existing-object direct path) or move on to a many-only
    exact-category matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:42:59Z
  TYPE: PLAN
  CLAIM: The next harness refinement is to add real meld-front-door timings for
    the solo exact-existence matrix. The clean first slice is no-overrides meld
    timing per comparable existence category, keeping the existing
    `CreationContext.execute_no_hooks(...)` numbers alongside it instead of
    replacing them.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/conduit.py:812-848
  - src/melder/aether/conduit/spell_space/spell_space.py
  IMPACT: This will distinguish “construction seam speed” from “actual meld
    front-door speed” for the same forced family choices.
  NEXT: add meld no-overrides timing columns to the exact-existence matrix and
    rerun the harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:44:13Z
  TYPE: MEASURE
  CLAIM: The exact solo existence matrix now includes real **meld** no-overrides
    timings alongside the existing creation-seam and overrides-seam timings.
    With `5000` timed iterations and `1000` warmup iterations per comparable
    scenario, the current table is:
    - `many`
      - creation seam:
        - generalized: `533.520 ns/iter`
        - solo: `220.940 ns/iter`
        - ratio: `0.414118`
      - meld front door:
        - generalized: `803.220 ns/iter`
        - solo: `507.700 ns/iter`
        - ratio: `0.632081`
      - overrides seam:
        - generalized: `1267.120 ns/iter`
        - solo: `741.300 ns/iter`
        - ratio: `0.585027`
    - `unique_per_conduit`
      - creation seam:
        - generalized: `1073.440 ns/iter`
        - solo: `710.240 ns/iter`
        - ratio: `0.661649`
      - meld front door:
        - generalized: `431.580 ns/iter`
        - solo: `396.260 ns/iter`
        - ratio: `0.918161`
      - overrides seam:
        - generalized: `2394.940 ns/iter`
        - solo: `989.220 ns/iter`
        - ratio: `0.413046`
    - `unique_per_spell_space`
      - creation seam:
        - generalized: `1184.520 ns/iter`
        - solo: `771.740 ns/iter`
        - ratio: `0.651521`
      - meld front door:
        - generalized: `401.640 ns/iter`
        - solo: `450.520 ns/iter`
        - ratio: `1.121701`
      - overrides seam:
        - generalized: `2484.160 ns/iter`
        - solo: `1079.700 ns/iter`
        - ratio: `0.434734`
    - `unique`
      - creation seam:
        - generalized: `1354.220 ns/iter`
        - solo: `751.840 ns/iter`
        - ratio: `0.555183`
      - meld front door:
        - generalized: `527.680 ns/iter`
        - solo: `484.960 ns/iter`
        - ratio: `0.919042`
      - overrides seam:
        - generalized: `2437.340 ns/iter`
        - solo: `1040.060 ns/iter`
        - ratio: `0.426719`
    - `unique_per_conduit_cluster`
      - creation seam:
        - generalized: `1316.440 ns/iter`
        - solo: `774.260 ns/iter`
        - ratio: `0.588147`
      - meld front door:
        - generalized: `443.480 ns/iter`
        - solo: `456.520 ns/iter`
        - ratio: `1.029404`
      - overrides seam:
        - generalized: `2418.920 ns/iter`
        - solo: `1037.760 ns/iter`
        - ratio: `0.428994`
    - `unique_per_conduit_lineage`
      - creation seam:
        - generalized: `1401.660 ns/iter`
        - solo: `776.000 ns/iter`
        - ratio: `0.553629`
      - meld front door:
        - generalized: `421.200 ns/iter`
        - solo: `401.020 ns/iter`
        - ratio: `0.952089`
      - overrides seam:
        - generalized: `2478.980 ns/iter`
        - solo: `1187.480 ns/iter`
        - ratio: `0.478996`
    - `existing_creation`
      - marked `phase10_11_bypassed`
      - no forced phase-10/phase-11 comparison exists there because that path
        bypasses the model/plan/creation seam.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:1-878
  IMPACT: The harness now distinguishes construction-seam speed from actual meld
    front-door speed for the exact solo existence categories, not just the
    coarser route-family buckets.
  NEXT: decide whether to add meld-overrides timings too, or move on to a
    many-only exact-category matrix next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T10:58:13Z
  TYPE: DECISION
  CLAIM: The harness output format itself now needs correction. The current table
    is wide-format and hides the concrete strategy identity in column position.
    The next slice is to normalize the output into one row per concrete strategy
    with explicit phase-10 and phase-11 strategy ids, so the printed result
    states exactly which strategy built each spell.
  EVIDENCE:
  - user_instruction
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:489-576
  IMPACT: The benchmark values are already useful, but the current presentation
    obscures strategy identity and makes the result harder to audit.
  NEXT: reshape the table printer to emit one row per strategy and rerun the
    harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:05:59Z
  TYPE: CONFLICT
  CLAIM: The current single `meld` column is misleading for reuse-oriented solo
    categories. It is mostly timing the warm reuse path (lookup + gate + return
    existing creation), not the full create path that the solo family is meant
    to optimize. That is why a few rows make solo look slower than generalized.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:545-595
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:536-623
  IMPACT: The harness needs to split meld timing into `cold_create_meld` and
    `warm_reuse_meld` so the front-door benchmark stops conflating creation and
    reuse costs.
  NEXT: rewrite the harness meld measurement to output separate cold-create and
    warm-reuse columns, then rerun the exact solo existence matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The system reread pins the harness boundary more sharply. Real
    compiler work is front-loaded into phases 1-7, while phases 8-11 are now
    thin wrappers over analyzer -> processor -> planner -> codegen creation.
    At runtime, `CreationContextBuilder` binds one spell-static
    `SpellCodegenCreation` into `CreationContext`, and
    `CreationContext.execute_no_hooks(...)` is the direct emitted-executor
    seam. `Conduit.meld(...)` measures a broader surface because it adds
    lookup normalization, cache hits on input resolution, structural and
    conduit-local validity gates, change-control gating, and creation-gate
    ticketing before the same creation-context execution path. `ConduitMeld`
    and `SpellSpaceMeld` share that same `Meld` base and mainly diverge by
    which creations store they pass into the creation-context call.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:458-615
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_6.py:325-473
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:55-235
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:20-100
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:16-74
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:16-76
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:17-87
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-86
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:241-313
  - src/melder/aether/conduit/conduit.py:2743-2850
  - src/melder/aether/conduit/meld/meld.py:466-679
  - src/melder/aether/conduit/meld/conduit_meld.py:96-247
  - src/melder/aether/conduit/meld/spellspace_meld.py:107-260
  IMPACT: The harness should keep treating `execute_no_hooks(...)` as the
    emitted creation-codegen benchmark and treat meld timing as a separate
    front-door benchmark. It also means forced-family experiments should stay
    anchored after real phase-9 truth instead of trying to fake earlier rooted
    compiler work.
  NEXT: compare the current harness columns against this boundary and decide
    whether the next refinement is a cleaner front-door split
    (`meld_existing_spell(...)`/warm reuse) or direct solo-codegen
    optimization work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The current solo emitted executors still pay helper-dispatch and
    per-call branch costs even when route, existence, and disposal posture are
    fixed at compile time. Both solo compilers route through helper layers like
    `_resolve_creations_for_route`, `_register_solo_instance`, and the root
    invoke helpers instead of emitting per-route specialized closures. That is
    especially wasteful on the hot solo `many` cold-create path because the
    fast lane is already root-only and does not need generic route plumbing.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-139
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-174
  IMPACT: The next optimization slice should not be in `CreationContext` or the
    harness. It should specialize the solo emitted closures themselves so route
    and registration behavior are fixed in the emitted function body instead of
    re-decided every call.
  NEXT: rewrite the solo compilers to emit route-specialized closures with
    prebound call targets, spell ids, and disposal payloads, then rerun the
    harness and compare the cold-create many path first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The first solo optimization tranche is now implemented in the
    no-overrides compiler. The route helper chain is gone from the emitted hot
    path. Instead, the compiler now emits route-specialized closures with
    prebound `call_target`, `spell_id`, and disposal payloads. The key cold
    many case now has two simpler shapes:
    - transient fast path returns the root call target directly
    - non-fast many with no disposal methods returns a signature-compatible
      create-only closure that skips creations resolution and registration
      entirely
    Caller-owned and shared-owner routes are likewise specialized so the
    per-call `resolve_route_key` and `existence` branches are removed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-182
  IMPACT: The harness should show whether helper-dispatch removal materially
    lowers the solo cold-create no-overrides numbers, especially on `many`.
  NEXT: run the solo existence harness and a focused codegen-creation test ring
    to verify the optimization and capture the new cold-path numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: MEASURE
  CLAIM: The solo no-overrides specialization pass is now validated and the
    harness numbers moved in the right direction. After replacing the generic
    helper chain with route-specialized closures in the solo no-overrides
    compiler, the exact-existence harness reported:
    - `many`
      - `no_ns`: `205.340 -> 180.140`
      - `meld_cold_ns`: `937.960 -> 744.680`
    - `unique_per_conduit`
      - `no_ns`: `743.620 -> 418.340`
      - `meld_cold_ns`: `1430.700 -> 1070.060`
    - `unique_per_spell_space`
      - `no_ns`: `707.960 -> 403.520`
      - `meld_cold_ns`: `1664.540 -> 1105.060`
    - `unique`
      - `no_ns`: `791.960 -> 474.720`
      - `meld_cold_ns`: `1681.420 -> 1075.060`
    The focused phase-11/runtime ring also stayed green (`28 passed`).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-182
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:425-993
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-600
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-155
  IMPACT: The solo emitted no-overrides code really was leaving speed on the
    table. The next meaningful optimization target is either the solo overrides
    compiler or the warm-reuse front-door path, not the harness presentation.
  NEXT: inspect the solo overrides compiler for the same helper-dispatch
    pattern and decide whether to optimize that next or pivot back to a
    dedicated warm-reuse benchmark slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The same specialization pattern is now implemented in the solo
    overrides compiler. The emitted override closures are route-specialized,
    prebind the root call target and static disposal metadata, and collapse
    the old creations-resolution and registration helper chain out of the hot
    override path.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-235
  IMPACT: The next validation pass should show whether override hot-path cost
    falls in the same way the no-overrides path did, without changing the
    front-door meld semantics.
  NEXT: rerun the harness and the focused phase-11/runtime ring to capture the
    post-overrides-specialization numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: MEASURE
  CLAIM: The overrides specialization pass is also validated and it cut the
    solo override hot path dramatically. The rerun harness reported:
    - `many`
      - `ov_ns`: `743.020 -> 380.540`
    - `unique_per_conduit`
      - `ov_ns`: `964.440 -> 619.280`
    - `unique_per_spell_space`
      - `ov_ns`: `1003.760 -> 658.100`
    - `unique`
      - `ov_ns`: `993.480 -> 728.400`
    - `unique_per_conduit_cluster`
      - `ov_ns`: `1105.060 -> 631.760`
    - `unique_per_conduit_lineage`
      - `ov_ns`: `1045.840 -> 612.980`
    The focused phase-11/runtime ring stayed green again (`28 passed`), so the
    specialization did not break the spell-static creation contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-233
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:484-993
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-600
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-155
  IMPACT: Solo is now materially leaner on both emitted no-overrides and
    emitted overrides paths. The next likely bottleneck for the solo lane is
    no longer generic helper dispatch inside the solo compilers.
  NEXT: inspect whether the remaining cold-start cost now lives in
    `CreationContext` outer templates or in spell invocation/creations method
    dispatch for the still-slower shared and spellspace routes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The next cold-path cost seam is the outer `CreationContext` wrapper
    layer for the `many` route. Even after specializing the solo compilers,
    `CreationContext` was still compiling and calling one extra route-template
    function for `many` no-overrides and overrides despite the fact that
    `many` never reuses and the compiler already fixed the route. The context
    now binds direct `many`-route closures instead of the generic emitted
    templates for that route.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:14-90
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:102-194
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:522-533
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:668-670
  IMPACT: The harness should show whether removing the extra context wrapper
    layer moves the solo `many` cold path again, especially `no_ns`,
    `meld_cold_ns`, and `ov_ns`.
  NEXT: rerun the harness and focused creation-context/compiler ring, then
    compare the updated `many` row against the already-specialized compiler
    baseline.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The remaining `many` no-hooks optimization is family-specific, not
    route-generic. Generalized still needs the stricter three-arg executor
    contract, but solo many-route executors are already compatible with direct
    no-hooks invocation. So the next clean cut is to let
    `CreationContextBuilder` trust solo family metadata and mark only that
    path as direct-call-safe instead of weakening the generalized contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_no_overrides_codegen_creation_step.py:48-72
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/steps/solo_finalize_creation_context_step.py:34-40
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:54-70
  IMPACT: We can shave the remaining solo `many` no-hooks wrapper cost without
    changing the generalized executor contract or widening the runtime seam.
  NEXT: thread a solo-only direct-call flag from builder metadata into
    `CreationContext`, rerun the harness, and compare the `many` no-hooks and
    override rows again.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: FACT
  CLAIM: The solo-only direct-call metadata path is now implemented. The
    builder reads the solo family `creation_context_strategy` metadata and
    enables direct no-hooks invocation only for solo `many`, while generalized
    still keeps the stricter wrapper path. That means the optimization is
    compiler-trusted and family-local rather than a broad runtime contract
    relaxation.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:54-89
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:76-194
  IMPACT: The next harness run should tell us whether eliminating the final
    no-hooks wrapper layer for solo `many` moves the hot path again without
    affecting generalized behavior.
  NEXT: rerun the harness and focused creation-context/compiler ring, then
    compare the updated solo `many` no-hooks and override rows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: DECISION
  CLAIM: The solo-only direct-call bypass inside `CreationContext` was tested
    and then removed. It did not produce a clean enough follow-on win over the
    already-specialized solo compiler path to justify the extra family-local
    runtime branching. The final retained optimization is therefore the
    compiler-side route-specialized solo executors, not an additional
    `CreationContext` bypass.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:14-126
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-84
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:6-182
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:6-233
  IMPACT: The retained state is simpler and keeps the hot-path speedup where it
    was actually proven: in the emitted solo executors themselves.
  NEXT: use the current harness numbers as the new baseline and inspect the
    remaining cold-start cost in shared/spellspace routes rather than adding
    more family-local `CreationContext` branching.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: FACT
  CLAIM: There is still a small but real compiler-side tax left in the solo
    emitted closures themselves. Several closures assign unused runtime
    parameters to `_` before doing real work, and the create/register paths
    still do repeat attribute lookups that can be collapsed into the emitted
    closure body more tightly.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:39-177
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:33-177
  IMPACT: The next compiler-side iteration should stay in phase 11 and trim
    instruction count inside the emitted solo closures rather than widening the
    runtime binder again.
  NEXT: remove the unused-arg assignment noise and tighten creation-method
    dispatch inside the solo emitted closures, then rerun the harness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: FACT
  CLAIM: The next solo compiler-side trim is now implemented. The hot emitted
    closures no longer waste instructions assigning unused runtime args to `_`,
    and the create/register paths now take local method handles
    (`add_creation`, `add_many_creations`) inside the closure body instead of
    repeating longer attribute dispatch chains.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:34-177
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_overrides_codegen_creation_compiler.py:29-177
  IMPACT: This keeps the optimization strictly inside phase-11 emitted solo
    code and gives the harness one more clean compiler-side iteration to test.
  NEXT: rerun the harness and focused phase-11/runtime ring to see whether the
    smaller emitted closure bodies move the cold-path numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: BLOCKER
  CLAIM: The harness is currently blocked by an unrelated fresh-conjure
    runtime bug, not by the solo compiler changes. On a clean runtime boot,
    `SpellbookCreationSystem.define_conduit_into_spells(...)` references
    `Spellbook._aether` without a live runtime import, which raises
    `NameError` during harness conjure.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:553-580
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:378-386
  IMPACT: Compiler-side measurement cannot proceed on fresh harness runs unless
    we either patch the runtime bug or shim the missing symbol inside the
    experiment.
  NEXT: keep the runtime layer untouched and add an experiment-local harness
    shim for the missing `Spellbook` symbol so the phase-11 compiler iteration
    can still be measured.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:55:57Z
  TYPE: FACT
  CLAIM: The unique/shared reuse check is not redundant with `meld(...)`.
    `Conduit.meld(...)` and `ConduitMeld.meld(...)` do not prefetch the live
    creation for `unique`, `shared`, or `unique_per_conduit` before they enter
    the route executor. The first actual existence/reuse guard for those
    lifetimes happens inside the emitted `CreationContext` route body, where it
    does `get_creation(...)` and then rechecks under a lock before creating.
    So removing that check would not be an optimization; it would change
    semantics and allow duplicate construction on lifetimes that are supposed
    to reuse.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2743-2850
  - src/melder/aether/conduit/meld/conduit_meld.py:96-247
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:534-611
  IMPACT: The next safe optimization for unique/shared is not "remove the
    existence check." That check is the actual correctness gate, especially in
    this no-GIL threading model.
  NEXT: keep the reuse check and look for compiler-side reductions in the
    create branch after the miss, or separate cold-create benchmarking from
    warm-reuse benchmarking for those lifetimes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T11:30:19Z
  TYPE: MEASURE
  CLAIM: Final retained benchmark state after the second optimization pass:
    - compiler-side solo specialization remains in place
    - focused phase-11/runtime ring stayed green (`28 passed`)
    - current harness run reports:
      - `many`
        - `no_ns`: `214.960`
        - `meld_cold_ns`: `822.900`
        - `ov_ns`: `419.160`
      - `unique_per_conduit`
        - `no_ns`: `420.260`
        - `meld_cold_ns`: `1071.240`
        - `ov_ns`: `621.320`
      - `unique`
        - `no_ns`: `453.800`
        - `meld_cold_ns`: `1062.200`
        - `ov_ns`: `644.700`
    The harness remains somewhat noisy run-to-run on front-door columns, but
    the large emitted-codegen win over generalized is still stable.
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:739-993
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_core.py:1-600
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_discovery_core.py:1-254
  - tests/unit/melder/aether/conduit/meld/creation_context/test_creation_context_builder.py:1-155
  IMPACT: We now have a cleaner stopping point for this pass: the retained
    solo compiler optimizations are real, and the next bottleneck hunt should
    move to remaining route-specific cold-start work rather than more wrapper
    bypass experiments.
  NEXT: inspect shared and spellspace cold-create paths to see whether the next
    real cost is lock/reuse probing, creations-store dispatch, or call-target
    invocation shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:12:58Z
  TYPE: MEASURE
  CLAIM: The harness now reflects the exact-existence solo emit split instead
    of the old shared-route bucket for singleton-like lifetimes. Current solo
    rows are:
    - `many`
      - `no_ns`: `172.520`
      - `meld_cold_ns`: `745.480`
      - `ov_ns`: `374.740`
    - `unique_per_conduit`
      - `no_ns`: `466.140`
      - `meld_cold_ns`: `1086.600`
      - `ov_ns`: `628.140`
    - `unique_per_spell_space`
      - `no_ns`: `439.880`
      - `meld_cold_ns`: `1147.900`
      - `ov_ns`: `612.120`
    - `unique`
      - `no_ns`: `449.880`
      - `meld_cold_ns`: `1049.020`
      - `ov_ns`: `610.320`
    - `unique_per_conduit_cluster`
      - `no_ns`: `450.920`
      - `meld_cold_ns`: `1053.040`
      - `ov_ns`: `640.640`
    - `unique_per_conduit_lineage`
      - `no_ns`: `450.720`
      - `meld_cold_ns`: `1053.800`
      - `ov_ns`: `627.840`
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:739-993
  IMPACT: The harness is now comparing exact solo compiler outputs instead of
    the old route-family-bucketed singleton path.
  NEXT: compare the remaining singleton-like rows against each other and target
    the highest cold-create row next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first forced-family experimentation harness. The immediate
goal is to compare generalized versus solo resolution speed at the
`CreationContext` seam, not to redesign production discovery or add a permanent
debug forcing surface.
