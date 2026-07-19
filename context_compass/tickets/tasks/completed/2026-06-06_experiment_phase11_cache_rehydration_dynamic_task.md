Completed: 2026-06-12T11:58:04Z
Summary: Closed by user cleanup request with the recorded cache-rehydration
experiment results preserved for future reference.

# Task: Experiment Phase11 Cache Rehydration In Dynamic Mode

## Metadata
- Task ID: TASK-2026-06-06-experiment-phase11-cache-rehydration-dynamic
- Story: none
- Status: done
- Owner: codex
- Agent Name: compiler_1
- Priority: p0
- Created: 2026-06-06T19:27:58Z
- Updated: 2026-06-12T11:58:04Z

## Objective
Create a dynamic-mode experiment that exercises the compiler/runtime path
around phase-11 output reuse so we can observe what actually has to exist at
runtime after post-conjure binds land.

## Ticket Contract
- ENTRY_GATE: the compiler cache epic is active and the user explicitly asked
  for a real experiment instead of more read-only analysis.
- EXECUTION_BOUNDARY:
  - `tests/experimentation/`
  - `codex/context_compass/tickets/tasks/2026-06-06_experiment_phase11_cache_rehydration_dynamic_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/epics/2026-06-06_define_compiler_phase_artifact_directory_cache_epic.md`
  - `tickets/tasks/2026-06-06_decompose_phase10_phase11_strategy_groups_task.md`
  - `tickets/tasks/completed/2026-06-06_map_mutation_planner_phase11_convergence_task.md`
- EXIT_GATE:
  - one dynamic-mode experiment exists under `tests/experimentation/`
  - the experiment covers post-conjure bind plus creation of a spell that
    depends on newly bound siblings
  - validation status is recorded truthfully
- FAILURE_ESCALATION: raise `BLOCKER` if the runtime path needed for the
  experiment is ambiguous after direct source inspection.

## Scope Boundaries
- In scope:
  - one dynamic-mode experiment file
  - ticket/board state for this experiment lane
- Out of scope:
  - production cache implementation
  - broad compiler refactors
  - benchmark claims beyond the experiment output itself

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the lane to a dynamic-mode
  experiment under `tests/experimentation/`.

## Steps / Checklist
- [ ] Read existing experimentation patterns and dynamic-mode conjure/bind APIs.
- [ ] Define the smallest experiment that proves the post-conjure bind path.
- [ ] Implement the experiment under `tests/experimentation/`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one dynamic-mode experiment file under `tests/experimentation/`

## Files / Paths Impacted
- `tests/experimentation/`
- `codex/context_compass/tickets/tasks/2026-06-06_experiment_phase11_cache_rehydration_dynamic_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Ran:
  - `.venv_new\Scripts\python.exe -m pytest -q -s tests/experimentation/test_dynamic_post_conjure_bind_dependency_revalidation_experiment.py`
  - `.venv_new\Scripts\python.exe -m pytest -q -s tests/experimentation/test_creation_context_cache_asset_experiment.py`
  - `.venv_new\Scripts\python.exe -m pytest -q -s tests/experimentation/test_creation_context_override_cache_asset_experiment.py`
- Result:
  - `3 passed total across the targeted experiments; each run emitted a PytestCacheWarning only`
- Recommended commands:
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_dynamic_post_conjure_bind_dependency_revalidation_experiment.py`
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_creation_context_cache_asset_experiment.py`
  - `.venv_new\\Scripts\\python.exe -m pytest -q -s tests/experimentation/test_creation_context_override_cache_asset_experiment.py`

## Risks / Rollback Notes
- Risk: the experiment accidentally proves a narrower runtime seam than the
  actual post-conjure bind/revalidation path.
- Rollback: keep the experiment isolated in `tests/experimentation/` and avoid
  touching production code.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No production-code edits in this task.
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
  - dynamic-mode conduit conjure with no initial spells
  - post-conjure bind of dependency siblings
  - runtime creation of a target spell that depends on those siblings
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-06T19:27:58Z
  TYPE: PLAN
  CLAIM: The first experiment should target the concrete edge case the user is
    worried about: conjure a dynamic conduit with no initial spells, bind new
    spells after conjure, and then create one spell that depends on the newly
    bound siblings. That is the smallest runtime slice that can reveal whether
    phase-11-only reuse survives post-conjure structural changes.
  EVIDENCE:
  - user_instruction
  IMPACT: This keeps the experiment pinned to the real cache-boundary concern
    instead of drifting into generic benchmarking.
  NEXT: inspect the existing experimentation style and the exact dynamic-mode
    conjure/bind path before writing the experiment file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:24:08Z
  TYPE: FACT
  CLAIM: The runtime has two materially different paths. If a spell lineage is
    already valid, phase-11 output is enough for the hot path because
    `CreationContextBuilder` only consumes the phase-11 handoff. But if a
    spell becomes dirty or gated, `Meld` reruns structural phases 1-4 first,
    then local foundational phases 5-7 for the target/root closure, and only
    then reruns deferred phases 8-11. That means a post-conjure bind can force
    real upstream recompilation for the affected closure.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:495-532
  - src/melder/aether/spellbook/spellbook.py:3805-3845
  - src/melder/aether/spellbook/spellbook_creation_system.py:1540-1632
  - src/melder/aether/spellbook/spellbook_creation_system.py:1664-1748
  - src/melder/aether/spellbook/spell.py:1006-1030
  - src/melder/aether/spellbook/spellbook.py:2776-2858
  IMPACT: The experiment has to distinguish "fresh hot path after valid phase11"
    from "post-conjure bind changed closure so upstream phases rerun." Without
    that distinction the result would be misleading for cache-boundary design.
  NEXT: inspect the existing post-conjure bind component tests and then write a
    dynamic-mode experiment that targets the closure-changing case directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:24:08Z
  TYPE: FACT
  CLAIM: The repo already covers some nearby behavior, but not the exact
    experiment lane we need. Existing component tests prove that post-conjure
    bind is allowed in dynamic mode and that passive Nexus publication updates,
    while separate component coverage proves the real `CreationContext`
    override lane works against live phase8-11 artifacts. What is still missing
    is a dedicated experiment for: conjure empty dynamic conduit -> bind new
    provider/provider/consumer trio -> create the consumer -> inspect what
    upstream compiler state had to exist or be rebuilt.
  EVIDENCE:
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:354-387
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:1100-1133
  - tests/component/melder/spellbook/test_spellbook_component_spell_crafter.py:1482-1548
  IMPACT: The new experiment should fill a real gap instead of duplicating
    existing gating or override assertions.
  NEXT: implement the dynamic-mode experiment file under `tests/experimentation/`
    using the existing experiment/test support helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:24:08Z
  TYPE: MEASURE
  CLAIM: The dynamic-mode experiment ran successfully and showed a more specific
    lifecycle than the worst-case read-only model. In the exact path
    `conjure empty -> bind provider/provider/consumer -> meld consumer`,
    all three late-bound spells already had phases 1-4 materialized before the
    first meld. The first meld then attached phase-5 rooted artifacts to the
    whole closure (`provider_a`, `provider_b`, `consumer`), while phase 8-11
    artifacts appeared only on the target consumer. After that first meld, the
    structural phase-1-to-phase-4 objects had already been cleaned back off the
    artifacts, leaving phase-5 rooted state on the providers and full phase-11
    state on the consumer.
  EVIDENCE:
  - tests/experimentation/test_dynamic_post_conjure_bind_dependency_revalidation_experiment.py:136-196
  - src/melder/aether/spellbook/spellbook.py:2751-2763
  - src/melder/aether/conduit/meld/meld.py:491-580
  IMPACT: The hot-path cache story is stronger than the earlier worst-case
    concern. A late bind in dynamic mode is already front-loading phases 1-4
    before the first creation, so the remaining heavy first-create cost for
    this scenario is mostly foundational/rooted work plus target-only deferred
    8-11 planning.
  NEXT: report the experiment result to the user and decide whether the next
    experiment should compare first-create cost with and without a synthetic
    phase-11 rehydration path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T19:56:25Z
  TYPE: PLAN
  CLAIM: The next bounded slice is an intentionally narrow cache-rehydration
    experiment. Instead of trying to persist the full compiler world, we will
    export a minimal creation-context-facing cache asset from one already-built
    spell, briefly add a cache loader to `creation_context.py`, null the live
    phase-11/context state after conjure, and verify that a reloaded generic
    `CreationContext` can still create the spell through the conduit without
    repopulating the compiler artifact.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-265
  - src/melder/aether/conduit/meld/creation_context/creation_context_factory.py:178-265
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:1-170
  IMPACT: This gives us a real feasibility check for a restart-style
    rehydration seam without yet widening into full persistent-cache design.
  NEXT: patch `creation_context.py` with cache export/load helpers and add a
    single-spell dynamic-mode experiment under `tests/experimentation/`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:06:37Z
  TYPE: MEASURE
  CLAIM: The narrowed cache-rehydration experiment succeeded. We exported a
    saved no-overrides creation-context-facing asset, cleared the live
    `CreationContext`, set `spell._compiler_artifact = None`, reloaded a
    generic `CreationContext` from the saved asset, published it back onto the
    spell, and then `conduit.meld(...)` still created the spell successfully.
    The printed snapshots showed:
    - before clear: live phase-11 + live cached context present
    - after clear: no compiler artifact and no cached context
    - after load: still no compiler artifact, but generic cached context
      published and switch reopened
  EVIDENCE:
  - tests/experimentation/creation_context_cache_asset_playground.py:1-292
  - tests/experimentation/test_creation_context_cache_asset_experiment.py:1-190
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-303
  IMPACT: This proves the runtime seam is narrower than the full compiler
    artifact object. For the single-spell no-overrides path, a saved
    creation-context-facing executor package can survive clearing the spell's
    compiler artifact and still drive `conduit.meld(...)` through a generic
    rehydrated `CreationContext`.
  NEXT: decide whether the next experiment should widen this to dependent
    multi-spell no-overrides graphs or to override-bearing graphs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:17:09Z
  TYPE: MEASURE
  CLAIM: The override-bearing cache-asset experiment also succeeded after
    aligning the root spell to `Existence.many` so the second override call was
    not rejected by the shared-instance guard. We saved a concrete override
    shape asset, cleared the live compiler artifact and cached context,
    reloaded a generic `CreationContext` from the saved asset, and then
    `conduit.meld(..., spell_override=...)` still produced the consumer with
    the overridden dependency value.
  EVIDENCE:
  - tests/experimentation/creation_context_cache_asset_playground.py:1-558
  - tests/experimentation/test_creation_context_override_cache_asset_experiment.py:1-194
  - src/melder/aether/conduit/meld/creation_context/creation_context.py:1-303
  IMPACT: The experiment layer now shows both major runtime doors are
    rehydratable from saved creation-context-facing assets:
    - single-spell no-overrides
    - override-bearing `many` root
    That is a much stronger signal that the real cache boundary can live at the
    creation-context-facing output instead of at the broader compiler artifact.
  NEXT: decide whether the next slice should widen this to multi-spell cached
    roots or turn the experiment seam into a first real cached-conjure design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T20:32:21Z
  TYPE: PLAN
  CLAIM: The next off-topic experiment is to force-clear structural phase-1-to-phase-4
    artifacts after a dynamic late bind and then see whether meld still
    recovers. The requested coverage is:
    - one late-bound standalone spell
    - one late-bound dependency pair where the root depends on the sibling
    The key variable is whether clearing the stored phase-1-to-phase-4
    artifacts alone is enough to break the runtime, or whether meld/runtime
    state still reconstructs what it needs.
  EVIDENCE:
  - user_instruction
  IMPACT: This will tell us whether the current runtime depends on the cached
    structural artifact objects themselves, or only on the spell/system-state
    side effects those phases previously wrote.
  NEXT: implement the forced-clear experiment under `tests/experimentation/`
    and run it for both the 1-spell and 2-spell scenarios.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-06-06T21:09:46Z
  TYPE: MEASURE
  CLAIM: Fully cleaning a late-bound dependency spell object is a different
    story from partially clearing its phase artifacts. In a dynamic-conjure /
    late-bind provider+consumer scenario, calling `provider_spell.cleanup()`
    left the cleaned provider object still present in `spellbook._spell_id_pool`.
    The next `conduit.meld(consumer_id)` then failed during local rooted work
    with `PhaseExecutionError`, whose inner failure was
    `AttributeError: 'Spell' object has no attribute '_compiler_artifact'`.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:393-494
  - src/melder/aether/spellbook/spellbook.py:604-612
  - src/melder/aether/conduit/meld/meld.py:720-753
  IMPACT: Partial phase cleanup is resilient because spell/system side effects
    survive, but full spell cleanup is not safe while the cleaned spell object
    is still reachable from the live spell pools. The runtime then trips over
    that cleaned dependency during local rooted recompilation.
  NEXT: report the exact failure mode to the user and, if useful later,
    isolate which registry should evict cleaned spell objects to make this path
    deterministic.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns one isolated dynamic-mode experiment under
`tests/experimentation/` to exercise the post-conjure bind path against the
phase-11 cache-boundary question.
