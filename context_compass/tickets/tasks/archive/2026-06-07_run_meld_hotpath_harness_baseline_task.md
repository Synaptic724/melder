# Task: Run Meld Hotpath Harness Baseline

## Metadata
- Task ID: TASK-2026-06-07-run-meld-hotpath-harness-baseline
- Story: none
- Epic: EPIC-2026-06-07-optimize-meld-hotpath
- Status: in_progress
- Owner: codex
- Agent Name: tester_0
- Priority: p0
- Created: 2026-06-07T12:11:50Z
- Updated: 2026-06-07T12:15:22Z

## Objective
Run the existing forced-family harness unchanged, map the real runtime hot path
around it, and record the baseline numbers for the new meld-hotpath
optimization epic.

## Ticket Contract
- ENTRY_GATE: the user explicitly said the job is to run the current harness,
  not modify it, and created a new epic for meld-hotpath optimization.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/meld/`
  - `src/melder/aether/conduit/creations/`
  - `src/melder/aether/conduit/spell_space/`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - `tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py`
  - `codex/context_compass/tickets/tasks/2026-06-07_run_meld_hotpath_harness_baseline_task.md`
  - `codex/context_compass/tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
  - `tickets/tasks/2026-06-07_experiment_forced_phase10_phase11_creation_context_harness_task.md`
  - `system_docs/src_architecture.md`
  - `system_docs/src_components.md`
  - `system_docs/readable_src_graph.json`
- EXIT_GATE:
  - the harness has been run unchanged,
  - baseline measurement output is recorded,
  - the runtime hot-path layers are summarized with evidence.
- FAILURE_ESCALATION: raise `BLOCKER` if the harness cannot be run unchanged or
  if the runtime fails before the existing experiment surface can measure.

## Scope Boundaries
- In scope:
  - read the named runtime files
  - run the existing harness unchanged
  - record baseline numbers and hot-path attribution
- Out of scope:
  - edits to the harness file
  - runtime optimization edits
  - unrelated compiler or cache lanes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the active work into a new
  baseline task under the meld-hotpath optimization epic.

## Steps / Checklist
- [ ] Read the live runtime chain around `conduit.meld(...)`.
- [ ] Record one evidence-backed hot-path note before validation.
- [ ] Run the existing harness unchanged.
- [ ] Capture the baseline measurement output in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one baseline harness run
- one hot-path attribution summary tied to source evidence

## Files / Paths Impacted
- `codex/context_compass/tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md`
- `codex/context_compass/tickets/tasks/2026-06-07_run_meld_hotpath_harness_baseline_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Run:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py`
  - Result: `1 passed, 1 warning in 1.23s`
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py`

## Risks / Rollback Notes
- Risk: the baseline gets polluted by harness edits instead of runtime truth.
- Risk: the front-door/runtime boundary is described too vaguely to guide the
  next optimization slice.
- Rollback: keep this task read-and-measure only; defer runtime changes to a
  successor task.

## Applicable Anti-Patterns
- [ ] No harness modification in this task.
- [ ] No validation claims without an actual run.
- [ ] No optimization conclusions without both source evidence and measurement.

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
  - front-door `conduit.meld(...)` cost
  - emitted `CreationContext` seam cost
  - unchanged harness baseline
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-07T12:15:22Z
  TYPE: MEASURE
  CLAIM: The unchanged harness baseline is now recorded under the new epic.
    Key results:
    - `many`
      - `no_ns`: generalized `480.080`, solo `180.720`
      - `meld_cold_ns`: generalized `1078.220`, solo `749.840`
      - `ov_ns`: generalized `1245.260`, solo `368.300`
    - `unique_per_conduit`
      - `no_ns`: generalized `1069.260`, solo `516.660`
      - `meld_cold_ns`: generalized `1699.740`, solo `1049.180`
      - `meld_warm_ns`: generalized `397.860`, solo `415.980`
      - `ov_ns`: generalized `2185.920`, solo `606.400`
    - `unique_per_spell_space`
      - `no_ns`: generalized `1108.860`, solo `480.460`
      - `meld_cold_ns`: generalized `1767.360`, solo `1053.760`
      - `meld_warm_ns`: generalized `431.500`, solo `394.120`
      - `ov_ns`: generalized `2285.700`, solo `617.200`
    - `unique`
      - `no_ns`: generalized `1337.960`, solo `482.580`
      - `meld_cold_ns`: generalized `1923.100`, solo `1041.380`
      - `meld_warm_ns`: generalized `390.520`, solo `440.980`
      - `ov_ns`: generalized `2586.180`, solo `600.360`
    - `unique_per_conduit_cluster`
      - `no_ns`: generalized `1383.680`, solo `473.520`
      - `meld_cold_ns`: generalized `2935.860`, solo `1091.640`
      - `meld_warm_ns`: generalized `459.540`, solo `422.000`
      - `ov_ns`: generalized `2329.020`, solo `634.440`
    - `unique_per_conduit_lineage`
      - `no_ns`: generalized `1372.840`, solo `506.000`
      - `meld_cold_ns`: generalized `1952.160`, solo `1055.960`
      - `meld_warm_ns`: generalized `403.300`, solo `404.120`
      - `ov_ns`: generalized `2265.440`, solo `805.940`
    - `existing_creation`
      - `phase10_11_bypassed`
  EVIDENCE:
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:430-994
  IMPACT: The baseline is now stable enough to choose real optimization work
    from measured bottlenecks instead of from benchmark-shape intuition.
  NEXT: identify the first runtime target from the current split between large
    `execute_no_hooks` wins and narrower or parity-level `meld_warm_ns` results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:15:22Z
  TYPE: FACT
  CLAIM: The baseline says the first optimization target should be the meld
    front door, not the harness and not the already-fast emitted solo seam.
    Solo already beats generalized decisively on `no_ns` and `ov_ns`, but the
    `meld_cold_ns` gap is much narrower and `meld_warm_ns` is near parity or
    slightly worse on some routes. That means the next likely costs are lookup,
    gate/revalidation, creations-store dispatch, or warm-reuse path behavior
    above the emitted executor.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2743-2857
  - src/melder/aether/conduit/meld/conduit_meld.py:96-247
  - src/melder/aether/conduit/meld/spellspace_meld.py:107-260
  - src/melder/aether/conduit/meld/meld.py:466-762
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:241-313
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:430-994
  IMPACT: The successor optimization task should attack front-door runtime
    layers first, because that is where the measured gap has most room left.
  NEXT: choose whether the first optimization slice is cold-create front-door
    work (`many` / shared routes) or warm-reuse path work.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:14:31Z
  TYPE: FACT
  CLAIM: The runtime hot path splits cleanly into two layers. The narrow inner
    seam is `CreationContextBuilder.build(...) -> CreationContext.execute_no_hooks(...)`
    plus the emitted route-specific executor selected from
    `creation_context_codegen.py`. The broader front door is
    `Conduit.meld(...) -> ConduitMeld/SpellSpaceMeld.meld(...) -> Meld`
    lookup normalization, input-resolution cache, creation-gate ticketing,
    structural/re-resolution gating, and caller-creations selection before the
    same creation-context executor is invoked.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:2743-2857
  - src/melder/aether/conduit/meld/conduit_meld.py:96-247
  - src/melder/aether/conduit/meld/spellspace_meld.py:107-260
  - src/melder/aether/conduit/meld/meld.py:466-762
  - src/melder/aether/conduit/meld/meld.py:1037-1357
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:27-86
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:241-313
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:54-97
  - src/melder/aether/conduit/meld/creation_context/creation_context_codegen.py:430-760
  - src/melder/aether/spellbook/spellbook.py:3958-4014
  IMPACT: The unchanged harness can now be read correctly: `execute_no_hooks`
    measures the emitted creation seam, while `conduit.meld(...)` measures that
    same seam plus the front-door lookup, gate, and revalidation layers.
  NEXT: run the unchanged harness and record the current baseline output for the
    new meld-hotpath epic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-07T12:11:50Z
  TYPE: PLAN
  CLAIM: The user explicitly redirected the work into a new epic and said the
    immediate job is to run the current harness, not modify it. The first task
    therefore stays read-only on runtime source and benchmark surface: attribute
    the hot path, then execute the unchanged harness.
  EVIDENCE:
  - user_instruction
  - tickets/epics/2026-06-07_optimize_meld_hotpath_epic.md:1-134
  IMPACT: This task must not drift into harness edits or early runtime patches.
  NEXT: record the front-door vs creation-seam hot-path map, then run the
    harness command exactly as-is.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the baseline measurement slice for the new meld-hotpath
optimization epic. The harness is a fixed benchmark surface here; the task's
job is to understand the runtime path around it and capture current numbers
unchanged.
