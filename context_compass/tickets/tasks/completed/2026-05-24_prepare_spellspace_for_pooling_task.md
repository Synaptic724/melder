# Task: Prepare SpellSpace For Pooling
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-24-prepare-spellspace-for-pooling
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T13:00:07Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Prepare `SpellSpace` for pooled reuse by removing dead state and then splitting
cleanup into a soft reusable lane and a permanent destructive lane.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/conduit/spell_space/spell_space_pool.py`
  - `src/melder/aether/conduit/conduit.py`
  - `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py`
  - `tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py`
  - `tests/unit/melder/aether/conduit/**spellspace*`
  - `tests/component/melder/aether/conduit/**spellspace*`
  - `tests/integration/melder/conduit/**spellspace*`
  - `tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - current `SpellSpace` lifecycle contract
  - current pool base under `utilities/general_base/abstract_elastic_pool.py`
  - current conduit spellspace entry/exit behavior
- EXIT_GATE:
  - dead `SpellSpace.version` state is removed
  - spellspace lifecycle has a clear reusable cleanup lane and a permanent
    destroy lane
  - focused spellspace tests pass
- FAILURE_ESCALATION: raise `BLOCKER` if the current `SpellSpace` lifecycle
  cannot be split into reusable vs permanent cleanup without widening scope
  into conduit runtime changes first.

## Scope Boundaries
- In scope:
  - direct `SpellSpace` runtime cleanup semantics
  - conduit-owned spellspace pool acquisition and teardown
  - spellspace/pool unit tests
  - spellspace/pool component tests
  - spellspace/pool integration tests
  - removal of unused version state
- Out of scope:
  - elastic policy tuning
  - lesser conduit pooling
  - unrelated spellspace refactors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested removing dead `SpellSpace`
  version state first, then continuing toward pooled cleanup semantics.

## Steps / Checklist
- [ ] Remove dead `SpellSpace.version` runtime state and align direct tests.
- [ ] Design the split between reusable cleanup and permanent cleanup.
- [ ] Implement the narrow `SpellSpace` lifecycle split.
- [ ] Run focused spellspace tests.
- [ ] Summarize the resulting spellspace pooling seam.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- narrowed `SpellSpace` runtime state
- direct spellspace cleanup-lane implementation
- focused validation result

## Files / Paths Impacted
- `src/melder/aether/conduit/spell_space/spell_space.py`
- `tests/unit/melder/aether/conduit/spell_space/test_spell_space.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space.py`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\meld\test_meld.py -k spellspace`
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_lifecycle.py -k spellspace`

## Risks / Rollback Notes
- Risk: current `SpellSpace.cleanup()` is called from both user-facing and
  conduit teardown paths, so a split lifecycle can break root cleanup if the
  permanent lane is not explicit.
  Rollback: keep permanent cleanup explicit and narrow; do not change conduit
  teardown until the `SpellSpace` contract is stable.
- Risk: test expectations may still encode the current version counter.
  Rollback: update only direct spellspace tests; do not widen into unrelated
  tests unless runtime evidence forces it.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drive-by refactors outside direct spellspace lifecycle scope.
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
- CLEANUP_TRIGGER: user-directed after the spellspace pooling seam is accepted

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-24T13:00:07Z
  TYPE: PLAN
  CLAIM: The user wants the spellspace pooling seam started from the lowest-risk
    cut: remove dead `SpellSpace.version` state first, then split cleanup into
    reusable vs permanent lanes without dragging conduit pooling in yet.
  EVIDENCE:
  - user_request: current thread
  IMPACT: The immediate slice is `SpellSpace` runtime cleanup semantics, not
    full pool wiring.
  NEXT: verify whether `version` has any runtime consumers beyond direct
    spellspace tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:00:07Z
  TYPE: FACT
  CLAIM: `SpellSpace.version` is dead runtime state. The only direct usages are
    inside `spell_space.py` itself and the direct unit file
    `test_spell_space.py`; no conduit, creations, meld, or other runtime path
    reads it.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:51-51
  - src/melder/aether/conduit/spell_space/spell_space.py:97-97
  - src/melder/aether/conduit/spell_space/spell_space.py:147-155
  - src/melder/aether/conduit/spell_space/spell_space.py:198-214
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:123-162
  IMPACT: We can remove the version field/property and keep the change tightly
    scoped to `SpellSpace` and its direct tests.
  NEXT: remove `version` from runtime and align only the direct spellspace test
    file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:01:58Z
  TYPE: DECISION
  CLAIM: The direct `SpellSpace` cleaned-state guards are out of contract for
    this lane. The user explicitly wants no `check_cleaned()` surface on
    `SpellSpace`, and the direct unit failures after version removal are only
    coming from tests that still assert the old nanny-state behavior.
  EVIDENCE:
  - user_request: current thread
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:164-180
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:237-253
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:257-278
  - src/melder/aether/conduit/spell_space/spell_space.py:134-195
  IMPACT: The right cut is to remove the remaining `SpellSpace`
    `check_cleaned()` calls and delete or relax only the direct tests that were
    asserting them.
  NEXT: strip `check_cleaned()` from `SpellSpace` and remove the direct
    post-cleanup guard tests from `test_spell_space.py`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:02:56Z
  TYPE: MEASURE
  CLAIM: The narrow `SpellSpace` contract cut is landed and green. `SpellSpace`
    no longer exposes the dead `version` surface or `check_cleaned()` fail-fast
    behavior, and the direct spellspace tests plus spellspace edgecase
    integration file were aligned to the simpler cleanup contract.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:39-195
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:108-285
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py:52-170
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py`
  IMPACT: The spellspace object is now simpler and no longer carries dead
    generation state or nanny-state cleaned guards, which is the right base
    before splitting cleanup into reusable versus permanent lanes.
  NEXT: implement the two cleanup lanes on `SpellSpace` for pooled reuse versus
    permanent destruction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:12:07Z
  TYPE: MEASURE
  CLAIM: The pool-aware `SpellSpace` seam is landed and green. `SpellSpace`
    now supports two cleanup lanes: normal `cleanup()` returns to an attached
    `SpellSpacePool`, while `permanent_cleanup()` forces the destructive lane.
    The concrete `SpellSpacePool` now lives beside `SpellSpace` and reuses the
    abstract elastic pool base from `utilities/general_base`.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:1-220
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:1-119
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:1-286
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py`
  IMPACT: SpellSpace now has the concrete reusable-vs-permanent cleanup seam
    needed before conduit-side pool acquisition and root teardown wiring.
  NEXT: wire `Conduit.create_spellspace()` and conduit teardown onto
    `SpellSpacePool` and `SpellSpace.permanent_cleanup()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:20:05Z
  TYPE: FACT
  CLAIM: The current pool seam still has 3 real runtime bugs: `SpellSpace`
    constructor now requires a pool but `Conduit.create_spellspace()` still
    constructs without one, `SpellSpacePool.prepare_object()` still tries to
    pass rebinding args even though the pool is conduit-local, and the reusable
    lane wrongly marks the object cleaned.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:49-119
  - src/melder/aether/conduit/spell_space/spell_space.py:133-171
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:59-95
  - src/melder/aether/conduit/conduit.py:633-657
  IMPACT: The next cut must wire the conduit-owned pool, remove rebinding from
    `SpellSpace`, and keep pooled spellspaces live on the soft cleanup lane.
  NEXT: patch `SpellSpace`, `SpellSpacePool`, and `Conduit.create_spellspace()`
    / conduit spellspace teardown together, then rerun focused spellspace tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:23:55Z
  TYPE: MEASURE
  CLAIM: The conduit-owned spellspace pool wiring is now green. `SpellSpace`
    keeps fixed conduit-owned collaborators, soft cleanup stays live and
    returns to the pool, permanent cleanup destroys the object, and
    `Conduit.create_spellspace()` now acquires from the conduit-local pool
    while conduit spellspace teardown uses the permanent lane.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:1-211
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:1-109
  - src/melder/aether/conduit/conduit.py:18-18
  - src/melder/aether/conduit/conduit.py:116-117
  - src/melder/aether/conduit/conduit.py:282-289
  - src/melder/aether/conduit/conduit.py:601-613
  - src/melder/aether/conduit/conduit.py:649-649
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:1-371
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py:1-170
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:334-812
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\test_conduit_lifecycle.py -k spellspace`
  IMPACT: The spellspace pooling seam now matches the intended conduit-local
    ownership model and no longer pays the incorrect rebinding / cleaned-state
    costs from the earlier cut.
  NEXT: decide whether to stop at spellspace pooling or carry the same shape
    into a conduit-local lesser-conduit pool.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:30:06Z
  TYPE: FACT
  CLAIM: The current live `SpellSpace` cleanup order is still wrong even after
    the pool cut: soft cleanup is releasing to the pool inside the lock before
    it decides the lane, and `_cleanup_for_pool_reuse()` is still duplicating
    registry removal already done by `cleanup()`.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:87-105
  - src/melder/aether/conduit/spell_space/spell_space.py:129-138
  IMPACT: The next correction is just cleanup order and duplicate-work removal;
    the constructor and collaborator wiring do not need to widen for that fix.
  NEXT: move soft-lane pool release outside the lock and remove registry
    discard from `_cleanup_for_pool_reuse()`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:38:52Z
  TYPE: DECISION
  CLAIM: The user wants the spellspace lifecycle collapsed further: no public
    `reset()` surface, one reusable cleanup helper, one destructive cleanup
    helper, and `cleanup()` itself as the only public router between those
    lanes under the existing permanent-cleanup bool.
  EVIDENCE:
  - user_request: current thread
  - src/melder/aether/conduit/spell_space/spell_space.py:87-154
  IMPACT: The next cut removes the redundant reset-style surfaces and pushes
    the reset/destroy split behind `cleanup()`, with test updates only where
    they still target the deleted public `reset()` API.
  NEXT: remove `SpellSpace.reset()`, collapse reusable cleanup into one private
    helper, update `SpellSpacePool`, and align direct spellspace tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T13:48:33Z
  TYPE: DECISION
  CLAIM: The user widened the acceptance bar from “spellspace pooling seam
    works” to concrete coverage counts on the pool+spellspace lane:
    at least 30 unit tests, 10 component tests, and 5 integration tests that
    exercise spellspace/pool behavior.
  EVIDENCE:
  - user_request: current thread
  IMPACT: The next slice is no longer just runtime correctness; it now includes
    explicit test-count expansion across unit/component/integration surfaces.
  NEXT: inventory the current spellspace/pool test counts by tier, then add
    the missing focused tests until the requested coverage counts are met.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:03:00Z
  TYPE: FACT
  CLAIM: Current spellspace/pool test counts are `26 unit / 5 component / 8 integration`,
    so the remaining gap to the requested bar is `+4 unit` and `+5 component`.
    The existing integration count already exceeds the requested `5`, and the
    current integration files exercise the pooled spellspace path through
    `Conduit.create_spellspace()` / `enter_spellspace()`.
  EVIDENCE:
  - tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py:61-437
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:127-311
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py:91-235
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py:57-161
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_hooks.py:55-284
  IMPACT: The next implementation slice can stay tightly scoped to adding `4`
    unit tests and `5` component tests without widening the integration layer.
  NEXT: add 4 focused unit tests around spellspace pool edges and 5 component
    tests around conduit-local pool ownership and permanent cleanup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:05:43Z
  TYPE: MEASURE
  CLAIM: The requested spellspace/pool test-count bar is now met and exceeded:
    `30 unit / 10 component / 8 integration`. The added tests cover the
    direct `SpellSpacePool` collaborator contract, conduit-local pool reuse,
    permanent destruction, idle pooled teardown, and conduit-owned pooled
    spellspace collaborator stability.
  EVIDENCE:
  - tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py:61-437
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:127-311
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:1-145
  - tests/component/melder/aether/conduit/test_conduit_component_spellspace_creations.py:91-337
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_edgecases.py:57-161
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_hooks.py:55-284
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space_pool.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\component\melder\aether\conduit\test_conduit_component_spellspace_creations.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\conduit\spell_space\test_spell_space.py tests\integration\melder\conduit\test_conduit_integration_spellspace_edgecases.py tests\integration\melder\conduit\test_conduit_integration_spellspace_hooks.py tests\unit\melder\aether\conduit\test_conduit_lifecycle.py -k spellspace`
  IMPACT: The spellspace/pool lane now has the requested direct test density
    across unit, component, and integration tiers without widening into
    unrelated runtime areas.
  NEXT: review whether you want to stop at spellspace pooling or carry the same
    ownership model into lesser-conduit pooling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:08:05Z
  TYPE: FACT
  CLAIM: There is already one real spellspace multi-thread integration surface
    in `test_conduit_integration_spellspace_additional.py`, and it now
    exercises the pool path indirectly because `enter_spellspace()` acquires
    through `Conduit.create_spellspace()`, which now delegates to the
    conduit-local `SpellSpacePool`.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_additional.py:60-111
  - src/melder/aether/conduit/conduit.py:633-649
  IMPACT: The multi-thread angle is already covered at least once, but adding
    one explicit pooled reuse assertion after concurrent use will make that
    coverage direct instead of incidental.
  NEXT: add one focused multi-thread integration test that uses concurrent
    spellspaces and then asserts pooled spellspace ids are reused afterward.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:10:25Z
  TYPE: FACT
  CLAIM: The explicit multi-thread spellspace run exposed a real regression in
    `SpellSpaceThreadState`, not in the pool seam itself. `_SpellSpaceLocal`
    currently declares `__slots__ = ("spellspace_stack",)`, and on
    `threading.local` subclasses that slot is shared rather than thread-local,
    so one worker thread can overwrite the other thread's active spellspace
    stack and trigger `SpellSpace stack corruption detected while exiting`.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:6-27
  - src/melder/aether/conduit/conduit.py:712-726
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_spellspace_additional.py -k context_isolation_across_threads -vv`
  IMPACT: The thread-local holder must drop `__slots__` so `spellspace_stack`
    is truly per-thread before any multi-thread spellspace-pool claim is
    trustworthy.
  NEXT: remove `__slots__` from `_SpellSpaceLocal` and rerun the spellspace
    multi-thread integration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:10:56Z
  TYPE: MEASURE
  CLAIM: The spellspace multi-thread integration file is now green again
    (`5 passed`) after removing `__slots__` from `_SpellSpaceLocal`. That fix
    restored true thread-local spellspace stacks, and the file now covers both
    the existing two-thread spellspace isolation path and the explicit pooled
    spellspace id reuse path after concurrent worker-thread use.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:6-24
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_additional.py:60-202
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\conduit\test_conduit_integration_spellspace_additional.py`
  IMPACT: The spellspace/pool lane now has a real multi-thread check that goes
    through the pool path and verifies thread-local spellspace isolation at the
    same time.
  NEXT: no further multi-thread gap remains on the spellspace pooling lane
    unless you want a heavier stress-style multi-thread loop.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T14:16:48Z
  TYPE: FACT
  CLAIM: The failing `test_cleanup_spellspaces_flushes_stack` assertion is test
    drift, not a runtime bug. `_cleanup_spellspaces()` now uses
    `permanent_cleanup()` for stack and registry spellspaces, so a `MagicMock`
    fixture there must assert `space.permanent_cleanup.called`, not
    `space.cleanup.called`.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:598-611
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:1414-1434
  IMPACT: Only the stale assertion needs to change; the runtime spellspace
    teardown path is already aligned to the permanent lane.
  NEXT: patch the stale assertion and rerun the focused unit file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to prepare `SpellSpace` for pooling by first removing dead
runtime state and then splitting cleanup into reusable and permanent lanes.
