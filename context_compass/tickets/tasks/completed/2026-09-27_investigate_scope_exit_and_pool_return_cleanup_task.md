

# Task: Investigate whether every scope exit and pool return disposes its objects

## Metadata
- Task ID: TASK-2026-09-27-investigate-scope-exit-and-pool-return-cleanup
- Story: none
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T13:54:57Z
- Updated: 2026-09-28T00:20:38Z
- Completed: 2026-09-28T00:20:38Z
- Closure Basis: owner turn-in in chat (2026-09-28): "ok cool yeah fix the problem you have yourself and
  send it, finish off your fixes and turn in the remaining things please go ahead".
- Summary: Every scope exit and pool-return path of Conduit and SpellSpace mapped from source and probes on 3.14t;
  gaps and the owner's decisions recorded. The fix shipped in the scope_exit_dispose task at 0.2.8203; this
  task changed no source and took no notch.

## Objective
Owner direction (chat, 2026-09-27): a SpellSpace used in a `with` statement must clean itself up on exit, and so
must a Conduit used in a `with` statement; manual cleanup must clean up; a Conduit returning to its pool and a
SpellSpace entering its pool must dispose every object they hold under the normal scope cleanup contract rather than
just being put back. Investigate every exit and pool-return path of Conduit (root, lesser, named) and SpellSpace
(managed, manual, pooled, permanent), including what happens when a disposal method fails, record where each path
meets or breaks the contract with source and probe evidence, and propose a fix for the owner to approve.

## Ticket Contract
- ENTRY_GATE: owner direction in chat (2026-09-27); this board row; investigation only (reads and VM probes).
- EXECUTION_BOUNDARY: read-only over src/melder/aether/conduit/ (conduit.py, conduit_pool.py, spell_space/,
  creations/, conduit_ward/ pool and cleanup paths) and src/melder/utilities/general_base/ (elastic pool, cleanable);
  system-document slices; probe scripts and logs under artifacts/scope_exit_cleanup_20260927/ run in the VM worktree.
  No src or test edits in this task.
- DEPENDENCIES:
  - tickets/tasks/completed/2026-09-27_aggregate_creations_disposal_method_failures_task.md
    (0.2.80 disposal aggregation; its DECISION_REQUEST on a SpellSpace after a disposal failure moves here).
- EXIT_GATE: every exit and pool-return path mapped (disposes what, in what order, and on a failed disposal what
  happens to the scope, its pool and registry entries, and the error the caller sees), evidenced from source and
  confirmed by probes on 3.14t; gaps recorded with a proposed fix; owner review.
- FAILURE_ESCALATION: DECISION_REQUEST where the fix needs a contract choice the owner has not made; BLOCKER when a
  path cannot be exercised.

## Scope Boundaries
- In scope: SpellSpace managed (`with`) exit, manual acquisition and cleanup, reset, pool release, overflow destroy
  and prewarm; Conduit `with` exit, lesser (named and anonymous) cleanup and pool return, root cleanup, a conduit's
  teardown of its SpellSpaces and lessers, permanent cleanup; behaviour when a disposal method raises.
- Out of scope: implementing fixes (a follow-up task after owner approval), disposal-order policy (fixed at bind),
  purge authority.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("Go investigate this stuff").
- from_state: in_progress
- to_state: review
- transition_reason: Every exit and pool-return path is mapped from source and confirmed by probes on 3.14t (GIL off
  and on); gaps and a proposed fix are recorded. Awaiting the owner's decisions.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in in chat (2026-09-28), together with the fix task.

## Steps / Checklist
- [x] Descend the docs: src_components slices for the Conduit runtime and Creations/SpellSpace, then graph slices.
- [x] Read the code paths whole: SpellSpace, SpellSpacePool, the elastic pool base, Conduit enter/exit/cleanup and
      pool paths, ConduitPool, ConduitWard pool cleanup, ConduitCreations.
- [x] Path matrix with evidence, one note per unit read.
- [x] VM probes on 3.14t (worktree equal to the device): normal and failing-disposal runs for each exit.
- [x] Findings, gaps and a proposed fix; DECISION_REQUEST where a contract choice is needed.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Path matrix, probe scripts and logs, and a proposed fix with the decisions it needs.

## Files / Paths Impacted
- None in src/ or tests/. Ticket, boards, artifacts/scope_exit_cleanup_20260927/.

## Validation
- Probes run on 3.14.7t with PYTHON_GIL=0 and 1 in the VM worktree (equal to the device tree):
  `PYTHONPATH=src:. python context_compass/artifacts/scope_exit_cleanup_20260927/probe_scope_exit.py`
  Logs: artifacts/scope_exit_cleanup_20260927/probe_gil0.txt and probe_gil1.txt.
- Test suites: Not run (no src or test change in this task). Coverage: Not run.

## Risks / Rollback Notes
- Read-only lane; probes run in the VM worktree, never in the owner's tree.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No behaviour claim cited to a search hit; every range covers the logic that was read.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/scope_exit_cleanup_20260927/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: task closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-27T13:54:57Z
  TYPE: DECISION
  CLAIM: Owner direction (chat, 2026-09-27), in reply to the SpellSpace DECISION_REQUEST: a SpellSpace must clean up
    when used in a `with` statement, and a Conduit likewise; manual cleanup must happen; a Conduit returning to its
    pool and a SpellSpace entering its pool must dispose everything they hold under the normal scope cleanup
    contract instead of simply going back into the pool. "Go investigate this stuff." The A/B/C choice waits for
    this investigation; no src change until the owner approves a fix.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_aggregate_creations_disposal_method_failures_task.md:344-369
  IMPACT: The question widens from one SpellSpace failure path to every scope exit and pool return of both types.
  NEXT: Verify the components index and slice the Conduit runtime and Creations/SpellSpace entries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T14:03:02Z
  TYPE: FACT
  CLAIM: Exit and pool-return paths, from a full read (probes next). SpellSpace `with`: `enter_spellspace()` pops an
    untracked shell from the pool and pushes it on this thread's stack; `__exit__` LIFO-pops it, then
    `recycle_from_managed_context()` clears the space's own store (every disposal-bearing object, newest first, via
    `reset_for_pool_unlocked` -> `clear_all`), restores temporary hooks and releases it to the pool. That store
    holds unique_per_spell_space objects and disposal-bearing `many` melded through the space; broader lifetimes
    live in conduit, root, leader or Spell stores by design, and `many` without disposal methods is untracked.
    Manual `create_spellspace()` + `cleanup()` does the same through `_cleanup_for_pool_reuse` plus a registry
    discard. On success every SpellSpace path disposes what the space owns. On a disposal failure the store is
    already swapped empty, but the ExceptionGroup skips the hook reset and pool release: a managed space is dropped
    uncleaned; a manual one stays registered (a second cleanup() finishes it); conduit pool return logs the failure
    instead of raising and drops the space; the permanent lane stops before its Meld cleanup. If the LIFO pop fails,
    recycle never runs and the space's objects are never disposed.
    Conduit `with`: `__enter__`/`__exit__` acquire and release the conduit lock only - no disposal and no pool
    return - the lock-context convention Spellbook, Aether, AethericFrame, ConduitWard and SpellIndex share; two
    tests pin it (a meld after the block must still work).
    Lesser pool return (`cleanup()` -> `_prepare_for_pool`): Spaces (this thread's stack plus the registry; failures
    logged only), then its own store (a failure raises; the lesser stays attached and unpooled for retry), then its
    descendants, then hooks and the pool - a parent disposes before its children, the reverse of permanent teardown
    (ward and children first, then Spaces, then its own store; every disposal failure logged, never raised).
    Managed Spaces active on other threads are invisible to conduit cleanup: `drain()` reads this thread only.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:233-411
  - src/melder/aether/conduit/conduit.py:566-705
  - src/melder/aether/conduit/conduit.py:722-985
  - src/melder/aether/conduit/conduit.py:1074-1234
  - src/melder/aether/conduit/conduit.py:1561-1616
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:251-462
  - src/melder/aether/conduit/creations/creations.py:1073-1168
  - src/melder/aether/conduit/spell_space/spell_space_thread_state.py:219-289
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:185-288
  - src/melder/aether/conduit/conduit_pool.py:123-161
  - src/melder/utilities/general_base/abstract_elastic_pool.py:192-345
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/solo/compilers/solo_no_overrides_codegen_creation_compiler.py:80-175
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:460-481
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py:109-135
  IMPACT: The normal SpellSpace exit already meets the owner's contract; the gaps are the failure paths, Space
    failures swallowed on conduit return and teardown, the parent-before-child order on pool return, and
    `with conduit`, which is not a lifecycle scope at all.
  NEXT: Record the SpellSpace document contradictions, then probe every path on the VM worktree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:03:02Z
  TYPE: CONFLICT
  CLAIM: The SpellSpace documents contradict the source on what a finished scope still accepts. The SpellSpace,
    SpellSpacePool and SpellSpaceMeld docstrings and src_architecture say a space melds only while it is the
    ACTIVE scope and that `reset()` clears it and bumps a version so a stale handle fails. The source has no
    `reset()` and no version, and `SpellSpace.meld` checks neither `_cleaned` nor the stack (SpellSpaceMeld: "does
    not depend on the conduit's active spellspace stack"). A handle kept after `with` exit can still meld into the
    pooled shell; those objects are disposed only when that shell's next lease ends. Separately, SpellSpaceMeld.meld
    says `many` routes to the owner conduit's store, while the emitted executors put disposal-bearing `many` in
    the space's own store, which is what gives it disposal at space exit.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:76-95
  - src/melder/aether/conduit/spell_space/spell_space.py:455-568
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:33-56
  - src/melder/aether/conduit/meld/spellspace_meld.py:63-68
  - src/melder/aether/conduit/meld/spellspace_meld.py:297-304
  - context_compass/system_docs/src_architecture.md:811-811
  - context_compass/system_docs/src_architecture.md:1237-1237
  - context_compass/system_docs/src_architecture.md:1333-1333
  IMPACT: "Properly cleans up" also needs a finished space to refuse further use; today only the docs promise it.
  NEXT: Probe a stale-handle meld after `with` exit together with the other paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T14:03:02Z
  TYPE: PLAN
  CLAIM: One probe script (artifacts/scope_exit_cleanup_20260927/probe_scope_exit.py), run on 3.14.7t with the GIL
    off and on in the VM worktree after checking it equals the device tree. Cases: P1 managed `with` exit, normal
    (space, many and conduit objects; pool idle count); P2 managed exit with a failing `close` (group, other objects,
    pool, cleaned state); P3 stale handle melds after exit, then the next lease; P4 manual cleanup normal, failing,
    retry; P5 `with lesser:`; P6 lesser pool return normal with an open manual Space and a named child (disposal
    order); P7 lesser return with a failing Space object (raised or logged, Space pooled or dropped); P8 lesser
    return with a failing own object, then retry; P9 root cleanup with failing objects (raised or logged); P10 a
    lesser cleaned inside its own managed Space.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:1-40
  IMPACT: Every claim in the FACT note gets a behavioural check before any fix is proposed.
  NEXT: Write the probe and verify the worktree matches the device.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T14:07:44Z
  TYPE: MEASURE
  CLAIM: Probes on 3.14.7t, GIL off and on (identical results), worktree equal to the device tree.
    P1 managed `with` exit disposes the space's objects newest first (many, then space-scoped), leaves the
    conduit-scoped object alone and returns the shell; the next lease gets the same shell.
    P2 a failing `close` on managed exit raises the group (cause chained) after attempting every object, and the
    shell is neither returned to the pool nor cleaned (idle 0 -> 0, store empty, Meld live).
    P3 a handle kept after exit melds a new space-scoped object into the idle shell; the next lease of that shell is
    SERVED that object, built by the earlier request, and disposes it at its own exit.
    P4 manual cleanup: normal disposes and pools; failing raises, stays registered and unpooled; a second cleanup()
    pools it. P5 `with lesser:` disposes nothing; a meld after the block works; only cleanup() disposes.
    P6 lesser pool return disposes its open Space, then its own object, then its named child's (parent before
    child); both pooled. P7 a failing object in a lesser's open Space: cleanup() returns normally, the failure is
    only logged, the lesser is pooled and the Space dropped uncleaned. P8 a failing own object: the group is raised,
    the lesser stays attached and unpooled, a retry pools it. P9 root cleanup with failing Space and conduit objects
    raises nothing, logs two errors and attempts every disposal. P10 a lesser cleaned inside its own managed Space
    disposes the Space's object, then the `with` exit raises SpellSpaceScopeError "stack corruption".
  EVIDENCE:
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_scope_exit.py:1-423
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_gil0.txt:1-59
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_gil1.txt:1-63
  IMPACT: Every FACT and CONFLICT claim holds in behaviour; the normal exits are right, the failure, order,
    stale-handle and `with conduit` gaps are real.
  NEXT: Record the proposed fix and the owner decisions it needs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:07:44Z
  TYPE: DECISION_REQUEST
  CLAIM: Proposed fix, one lane at 0.2.81 with patch docs and red tests first. Recommended defaults:
    1. Every exit finishes its cleanup when a disposal method fails, then raises every failure as one group:
       SpellSpaces (managed exit, manual cleanup, a conduit's Spaces) reset hooks and go back to their pool clean
       (or are destroyed, if preferred), lessers finish their pool return, and permanent teardown raises after
       finishing instead of only logging. The store is emptied before any method runs, so a disposal failure
       leaves nothing to retry; failed named-record publication keeps today's retain-for-retry.
    2. Lesser pool return cleans descendants first, then its Spaces, then its own store (permanent teardown order).
    3. A released SpellSpace refuses meld and purge (a flag set on lease and cleared on release), closing the P3
       leak while the shell is idle; an owner cleaned inside its own managed Space no longer makes the block exit
       raise "stack corruption". Isolation after the shell is re-leased needs the active-stack check (a thread-local
       read per meld) or a per-lease wrapper (an allocation per cycle); measure before choosing.
    4. `with conduit:` stays a lock: as a teardown it would destroy a root at block exit and break the lock-context
       convention two tests pin. Add `with conduit.enter_lesser_conduit(name=None) as lesser:`, which returns the
       lesser to its pool on exit - the Conduit twin of enter_spellspace().
    5. Correct the stale SpellSpace documents (reset, version, active scope, many routing).
    Owner decisions: (a) cleanup() raising after a full teardown when disposal failed (today conduit paths only
    log; frame teardown swallows conduit errors with a bare `pass` and would need a log line; the 0.2.80
    integration test that expects no raise moves with it); (b) the new method's name; (c) the active-stack check
    now or after measuring.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:233-411
  - src/melder/aether/conduit/conduit.py:606-705
  - src/melder/aether/conduit/conduit.py:1561-1616
  - src/melder/aether/aetheric_frame/aetheric_frame.py:289-297
  - tests/integration/melder/conduit/test_conduit_integration_disposal_failures.py:82-94
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_gil0.txt:1-59
  IMPACT: No src change until the owner approves; the fix lane starts from these decisions.
  NEXT: Owner approves, edits or redirects the proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:14:12Z
  TYPE: DECISION
  CLAIM: Owner replies (chat) to the DECISION_REQUEST. (a) Yes: `with` means dispose, as a .NET `using` does -
    cleanup finishes even when disposal raises, the errors still float up, and a lesser still goes back into its
    pool (item 1 with re-pooling, not destruction). (b) `enter_lesser_conduit` is an acceptable name. (c) The owner
    expects meld to refuse a finished space the way it refuses a cleaned one: that is a released flag checked in
    meld and purge (one bool, like `check_cleaned`), because a recycled space is pooled, not cleaned, so `_cleaned`
    stays False; no thread-local active-scope check. Open: whether `with conduit:` itself becomes dispose (the
    owner's "same with conduit if we have a with statement" and the `using` analogy point that way) and whether
    `enter_lesser_conduit` is still wanted then - asked in chat.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:245-276
  IMPACT: Items 1, 2, 3 (flag only) and 5 are decided; item 4's shape waits on one answer.
  NEXT: Ask the `with conduit` question, then open the fix lane with patch docs and red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:14:26Z
  TYPE: DECISION
  CLAIM: Owner constraint (chat): "make sure you run benchmarks on your changes too ... don't just mod shit and break
    my fastpath". The fix lane measures the hot paths it touches - managed SpellSpace scope cycle and warm spellspace
    meld, lesser create/cleanup cycle, conduit warm meld - before and after the change on 3.14t, same harness, same
    machine, with the numbers recorded before any claim of no regression.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:1-20
  IMPACT: A change that slows a fast path is not done even when its tests pass.
  NEXT: Find the owner's benchmark harness and the gauntlet baselines before writing the fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:20:34Z
  TYPE: FACT
  CLAIM: Double cleanup corrupts both pools today. Calling cleanup() twice on a manual SpellSpace or on a lesser
    returns it to its pool twice, and the next two acquisitions hand out the SAME object as two scopes (probe, 3.14t).
    Nothing guards it: lesser soft cleanup never checks for the pooled state and SpellSpace cleanup checks only
    `_cleaned`, which a recycled space never sets. With `with` meaning dispose, an explicit cleanup() inside the
    block followed by the exit becomes ordinary use, so idempotent soft cleanup is a precondition of that change.
    Test impact of `with conduit` becoming dispose, by AST scan of 3,185 files (src, tests, benchmarks, examples,
    docs; BOM-safe): exactly two `with <conduit>` statements, both the tests that pin the lock behaviour.
  EVIDENCE:
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_double_cleanup.py:1-55
  - context_compass/artifacts/scope_exit_cleanup_20260927/probe_double_cleanup_gil0.txt:1-4
  - src/melder/aether/conduit/conduit.py:566-643
  - src/melder/aether/conduit/spell_space/spell_space.py:266-288
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:460-481
  - tests/integration/melder/conduit/test_conduit_integration_public_api.py:109-135
  IMPACT: The fix must make soft cleanup of a pooled or released scope a no-op; in-repo test churn for the `with`
    change is two tests plus new coverage, not a broad rewrite.
  NEXT: Put the strategy discussion to the owner before building.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T14:20:34Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner wants to discuss `with` as full scope cleanup, leaning to dispose semantics and an
    `enter_lesser_conduit` that creates a lesser ready for `with`. Options for that method: A plain (it creates like
    create_lesser_conduit; `with` on any conduit disposes; a lesser goes back to its pool, a root is torn down);
    B managed (also pushes the lesser on a per-thread active stack like spellspaces, enabling an implicit current
    scope lookup and LIFO checks, at a push/pop per cycle). Recommendation A. Also: `with` on a manual SpellSpace
    should dispose instead of raising "stack corruption"; when the block and the cleanup both fail, keep Python's
    chaining (the cleanup group rises with the block's error as its context), as SpellSpace exit does today.
    Package: dispose semantics, finish-then-raise cleanup, children first, idempotent soft cleanup, released-space
    refusal, docs and a Breaking release-note entry, gauntlet benchmarks before and after.
  EVIDENCE:
  - context_compass/artifacts/gauntlet_runtime_speed_20260926/vm_runs/per_cycle_baseline.txt:1-30
  - benchmarks/testing_other_di/test_melder_gauntlet.py:146-209
  - src/melder/aether/conduit/spell_space/spell_space.py:213-264
  IMPACT: Build starts only after the owner settles A or B and the package.
  NEXT: Owner discussion in chat.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T20:35:13Z
  TYPE: FACT
  CLAIM: Found while working another lane, and relevant to the open `with` discussion: every Cleanable already has
    `using_cleanup()`, a separate context manager whose `__enter__` returns the object and whose exit calls
    `cleanup()` at most once and never suppresses the block's exception - but SWALLOWS any exception cleanup()
    raises (`except Exception: pass`). So `with lesser.using_cleanup() as lesser:` is a dispose scope today (a
    lesser goes back to its pool, a root is torn down) that drops disposal failures instead of letting them float
    up, while `with conduit:` stays the lock. It shares the double-cleanup fault: an explicit cleanup() inside the
    block plus the exit pools a lesser twice.
  EVIDENCE: src/melder/utilities/general_base/cleanable.py:187-295
  IMPACT: One more option for the owner: keep `with conduit:` as the lock and make `using_cleanup()` (or an
    enter_lesser_conduit() built on it) the dispose scope - only after it stops swallowing cleanup errors, which
    changes that helper for every Cleanable; any option still needs idempotent soft cleanup.
  NEXT: Raise it with the owner in the `with` discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:29:26Z
  TYPE: FACT
  CLAIM: Rechecked for the `with` decision after the frame-descriptor lane. `Conduit.__enter__`/`__exit__` are
    still the bare lock pair and have no internal user: conduit.py takes `self._lock` directly everywhere, and the
    earlier AST scan found only the two tests that pin the lock. `Cleanable.using_cleanup()` has no caller in src or
    tests (definition and docstrings only), so making it raise changes no in-repo behaviour. Versioning moved since
    the proposal: the fix lane takes the next 0.0001 notch above 0.2.82 at landing (the contribution guide), not
    0.2.81, and its release-note entry leads with Breaking change if `with conduit:` stops being a lock.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1561-1616
  - src/melder/utilities/general_base/cleanable.py:187-295
  - context_compass/special_instructions/agent_contribution_guide.md:15-39
  IMPACT: Turning `with conduit:` into dispose touches no src caller; the known test churn stays the two lock tests
    plus the 0.2.80 integration test that expects conduit cleanup not to raise.
  NEXT: Put the open calls to the owner: `with conduit:` as dispose, enter_lesser_conduit plain or managed,
    using_cleanup; then open the fix task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T21:31:36Z
  TYPE: DECISION
  CLAIM: Owner answers (chat, question card) close the discussion. (1) `with conduit:` disposes: at block exit a
    lesser returns to its pool and a root is torn down; Spellbook, Aether and frames keep `with` as a lock; the two
    lock tests change and the release note says Breaking change. (2) `enter_lesser_conduit()` is plain (option A):
    it makes a lesser for use in `with`, no per-thread stack. (3) `using_cleanup()` stops swallowing cleanup errors.
    Settled earlier and unchanged: cleanup finishes then raises every failure; a lesser still re-pools; children
    before parents on pool return; a released SpellSpace refuses meld and purge (one flag); soft cleanup of a
    pooled or released scope is a no-op; block and cleanup both failing keep Python's chaining; SpellSpace docs
    corrected; hot-path benchmarks before and after. The build is its own task, one notch above 0.2.82.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_investigate_scope_exit_and_pool_return_cleanup_task.md:245-385
  IMPACT: Every contract choice the fix needs is made; this investigation's deliverable is complete.
  NEXT: Open the fix task, read the code paths whole again, write the patch docs, then red tests and baselines.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T00:20:38Z
  TYPE: FACT
  CLAIM: Turned in with the fix task on the owner's directive: moved to tasks/completed, board row removed and
    anchored, attention details pruned, probe artifacts retained as reference.
  EVIDENCE: context_compass/attention_board.md:1-60
  IMPACT: The lane is closed; nothing here is routed any more.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Closed 2026-09-28 with the fix task (0.2.8203), which built the proposal below as decided.
Investigation done; no src change. Normal exits already dispose everything a scope owns (SpellSpace `with`, manual
cleanup, lesser pool return, root teardown). Gaps, all confirmed by probes: a disposal failure leaves a SpellSpace
dropped or half-destroyed and conduit paths only log it; lesser pool return disposes a parent before its children;
a released SpellSpace still accepts melds and the next lease is served the stale object; `with conduit:` is a lock,
not a scope; SpellSpace docs promise reset/version/active-scope checks the source lacks. The DECISION_REQUEST note
holds the proposed fix (one lane at 0.2.81) and decisions (a)-(c). Next: owner decision, then the fix lane.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
