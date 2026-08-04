# Task: Investigate conduit and spellspace pool reset cost
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-29-investigate-conduit-and-spellspace-pool-reset-cost
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-29T21:49:36Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Read the current lesser-conduit pool return/reuse path and the spellspace
reset/reuse path, then map exactly what state is reset, cleared, detached,
or retained so we can explain why pooled runtime churn is still expensive.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an investigation-first read of
  conduit reset-for-pool and spellspace reset behavior before any optimization
  patching starts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/conduit_pool.py`
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - `src/melder/aether/conduit/creations/creations.py`
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  - directly implicated synchronization helpers only when needed to explain the
    reset path
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/epics/2026-05-24_reusable_lesser_runtime_pooling_epic.md`
  - `tickets/tasks/2026-05-24_prepare_spellspace_for_pooling_task.md`
  - `tickets/tasks/2026-05-24_start_conduit_pool_task.md`
  - `tickets/tasks/2026-05-26_investigate_conduit_spellspace_spellbook_guard_and_lock_bloat_task.md`
- EXIT_GATE: the exact conduit reset-for-pool and spellspace reset/reuse steps
  are summarized with source evidence, and the likely expensive operations are
  separated from the merely necessary ones.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if explaining reset cost
  truthfully requires widening into broader meld/compiler/runtime hot-path work.

## Scope Boundaries
- In scope:
  - lesser conduit `_prepare_for_pool()` and reuse path
  - spellspace cleanup/reset and reuse path
  - ward detach/reset behavior
  - creations reset behavior directly invoked by the pool return path
  - retained gate/state behavior only as needed to explain reset cost
- Out of scope:
  - runtime optimization edits
  - benchmark redesign
  - unrelated dev-ops cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly redirected the lane to conduit and
  spellspace pool reset cost investigation.

## Steps / Checklist
- [ ] Read conduit pool-return and reuse surfaces.
- [ ] Read spellspace cleanup/reset and reuse surfaces.
- [ ] Read ward detach/reset and creations reset surfaces those paths invoke.
- [ ] Map exact reset operations in execution order.
- [ ] Separate probable cost centers from required lifecycle work.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one evidence-backed conduit pool reset sequence
- one evidence-backed spellspace reset sequence
- one evidence-backed list of likely expensive reset steps

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-29_investigate_conduit_and_spellspace_pool_reset_cost_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "_prepare_for_pool|cleanup_spellspaces|reset_non_spellspace_for_pool|_detach_for_pool|create_spellspace|cleanup\\(|permanent_cleanup|return_lesser_conduit|release\\(" src/melder/aether/conduit`

## Risks / Rollback Notes
- Risk: some reset work that looks expensive may still be essential to preserve
  correct lineage or instance-state isolation between pooled reuses.
- Rollback: keep the investigation strictly descriptive and do not collapse
  steps together without proving contract equivalence.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No optimization edits before the reset sequence is explicit.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: reset-step order, retained state, and concrete cost implications.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-29T21:49:36Z
  TYPE: PLAN
  CLAIM: The user wants a concrete reset-cost map, not another generic pooling
    opinion. The right cut is to read the actual conduit pool-return path,
    spellspace reset path, and the directly invoked ward/creations helpers, then
    write out the ordered reset work before talking about optimization.
  EVIDENCE:
  - user_instruction
  - tickets/epics/2026-05-24_reusable_lesser_runtime_pooling_epic.md:1-144
  IMPACT: The next step is source-first lifecycle mapping, not code changes.
  NEXT: open the exact reset/reuse methods in conduit, spellspace, ward, and
    creations, then record the first concrete sequence finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-29T21:51:09Z
  TYPE: FACT
  CLAIM: The current pooled lesser reset path is front-loaded inside
    `Conduit._prepare_for_pool()` and it does real work in this order:
    1. `_cleanup_spellspaces_for_pool()`
       - copies the active spellspace stack
       - calls `space.cleanup()` on every active spellspace
       - clears the thread-state stack
       - iterates the full registered spellspace set and calls `space.cleanup()`
         again on every registered spellspace
    2. `Creations.reset_non_spellspace_for_pool()`
       - takes the creations lock
       - walks both `_creations` and `_disposable_creations`
       - filters out every non-dict entry into temporary dicts
       - pops those entries out of the live registries
       - runs `_dispose_disposable_registry(...)` on the disposable half
    3. `ConduitWard._detach_for_pool()`
       - snapshots all lesser children
       - recursively calls `cleanup()` on each child lesser
       - reacquires the ward lock
       - removes this conduit from the parent’s lesser map
       - clears `_parent_conduit` and the local child map
       - clears `parent_conduit_id` on the conduit identity metadata
    4. marks conduit and ward state as `pooled_lesser`
    5. clears local conduit hooks
    6. returns the shell through `ConduitPool.return_lesser_conduit(...)`

    The current pooled spellspace reset/reuse path is smaller:
    - `SpellSpace.cleanup()` routes to `_cleanup_for_pool_reuse()` unless
      permanent cleanup was requested
    - `_cleanup_for_pool_reuse()` clears spellspace-scoped instances through
      `Creations.clear_spellspace_instances(self._id)` and removes the object
      from the registry
    - `SpellSpacePool.release(...)` just returns the object to idle or destroys it
    - on reuse, `SpellSpacePool.prepare_object(...)` only re-adds the object to
      the registry
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:359-379
  - src/melder/aether/conduit/conduit.py:382-414
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:343-382
  - src/melder/aether/conduit/creations/creations.py:559-585
  - src/melder/aether/conduit/spell_space/spell_space.py:95-133
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:73-106
  - src/melder/aether/conduit/conduit_pool.py:93-119
  IMPACT: Conduit reset is expensive because it is still doing recursive
    subtree cleanup, full spellspace flushing, registry pops, and disposable
    teardown before the shell even reaches the pool. Spellspace reset itself is
    comparatively narrow; the heavy part is the conduit-level wrapper work
    around it.
  NEXT: separate the likely hot cost centers from the truly necessary reset
    steps and summarize which pieces are structural versus obviously heavy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-29T21:52:21Z
  TYPE: FACT
  CLAIM: The likely cost centers are now clearer. The spellspace lane itself is
    comparatively small:
    - `SpellSpace.cleanup()` clears one spellspace bucket through
      `Creations.clear_spellspace_instances(self._id)`, unregisters from the
      spellspace registry, and then returns the shell to `SpellSpacePool`
    - reuse only re-adds the shell to the registry in `SpellSpacePool.prepare_object()`

    The heavy work is on the conduit side:
    - `_cleanup_spellspaces_for_pool()` may call `SpellSpace.cleanup()` for
      every active and still-registered spellspace in the conduit
    - `Creations.reset_non_spellspace_for_pool()` walks the full plain and
      disposable creation registries, splits entries by scope, and may run user
      disposal methods through `_dispose_disposable_registry(...)`
    - `ConduitWard._detach_for_pool()` recursively cleans every child lesser
      conduit before clearing the local parent/child links

    So the conduit reset is expensive not because pool handout is heavy, but
    because pool return is still doing:
    1. spellspace flush
    2. creations registry split/pop/disposal
    3. recursive subtree cleanup
    before the shell can go idle.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:95-133
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:59-84
  - src/melder/aether/conduit/creations/creations.py:136-175
  - src/melder/aether/conduit/creations/creations.py:511-540
  - src/melder/aether/conduit/creations/creations.py:559-585
  - src/melder/aether/conduit/conduit.py:359-379
  - src/melder/aether/conduit/conduit.py:382-414
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:343-382
  IMPACT: If we are losing badly on conduit pooling, the first suspects are
    recursive child cleanup and creations disposal churn, not spellspace reuse
    bookkeeping by itself.
  NEXT: summarize the conduit-vs-spellspace reset split for the user and point
    at the most likely heavy steps before proposing any rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-29T22:10:24Z
  TYPE: FACT
  CLAIM: `test_persistent_runtime_gauntlet.py` is not a separate Melder runtime
    implementation; it is a persistent-thread wrapper around existing gauntlet
    ops. For `lib == "melder"`, it ultimately delegates to
    `test_melder_gauntlet._build_runtime_melder()`, and that Melder builder
    still exercises pooled lesser and spellspace churn on every hot cycle:
    - `outer_create_ns` measures `conduit.create_lesser_conduit()`
    - `request_create_ns` measures `lesser.enter_spellspace()`
    - `request_cleanup_ns` measures exiting that spellspace context
      (`request_cm.__exit__(...)`)
    - `outer_cleanup_ns` measures `lesser.cleanup()`
    The persistent benchmark only avoids rebuilding singleton/root runtime and
    worker threads every iteration; it does not avoid lesser/spellspace
    create/reset churn inside the request and worker lanes.
  EVIDENCE:
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py:413-489
  - benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py:555-555
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1135-1141
  - benchmarks/testing_other_di/test_melder_gauntlet.py:72-181
  - benchmarks/testing_other_di/test_melder_gauntlet.py:200-284
  IMPACT: This file is directly relevant to the reset-cost question because the
    lane metrics already split lesser cleanup (`outer_cleanup_ns`) from
    spellspace cleanup (`request_cleanup_ns`). If Melder is losing badly here,
    it is still paying pooled lesser and spellspace reset cost on the hot path,
    not just one final benchmark teardown.
  NEXT: explain the benchmark semantics to the user and tie the measured lane
    timers back to the reset sequences already mapped from conduit and
    spellspace code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to explain the actual reset work on pooled lesser conduits and
pooled spellspaces before any performance fix is chosen.
