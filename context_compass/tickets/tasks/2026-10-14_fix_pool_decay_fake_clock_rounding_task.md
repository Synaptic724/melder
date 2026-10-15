# Task: Fix the quiet-pool decay test that fails when its fake clock rounds one ulp short of the settle time

## Metadata
- Task ID: TASK-2026-10-14-fix_pool_decay_fake_clock_rounding
- Story: none - standalone; follows TASK-2026-10-12-make_kernel_pools_elastic (done, 0.2.8234), which added the test
- Status: review
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-14T18:13:22Z
- Updated: 2026-10-14T18:26:12Z

## Objective
`test_quiet_root_pool_decays_to_baseline_and_burst_restretches` (0.2.8234) fails in about 1% of runs: its fake clock
reaches the pool's settle time through two float additions and can land one ulp short, so the decay step the test
expects is skipped (40 != 36). The owner directed the fix ("fix the pool decay thing due to rounding stuff please",
chat 2026-10-14). Decide from the code whether the rounding belongs to the test's clock or to the pool's own time
arithmetic, fix it there, and prove the test deterministic for every clock origin.

## Ticket Contract
- ENTRY_GATE: board row `pool_decay_clock_rounding` routes here; the owner's directive is recorded; the test module
  and `AbstractElasticPool`'s pressure, settle and decay code are read in full and the finding is in Notes before any
  edit.
- EXECUTION_BOUNDARY: `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py` (its fake clock
  and the tests that advance it). `src/melder/utilities/general_base/abstract_elastic_pool.py` only if the pool's own
  arithmetic is at fault; that would be an honest src change (notch, release note, system docs, assets) and is
  confirmed in Notes first. `tests_components.md` where a measured range moves. llm_support rebuilt last (it
  bundles tests/); the asset rebuild too if src or system docs change.
- DEPENDENCIES: TASK-2026-10-12-make_kernel_pools_elastic (done); the RISK note of
  TASK-2026-10-14-fix_many_child_follows_holder (2026-10-14T16:13:01Z) and its probe
  `artifacts/many_child_registration_20261014/probe_fake_clock_rounding.py`.
- EXIT_GATE: the reproducer finds no clock origin that fails after the fix; the elastic-retention module and the
  pool unit tests pass with the GIL off and on; the checks of every rebuilt bundle print only OK lines; the owner
  accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if the fix would change the pool's decay schedule or any public behaviour;
  BLOCKER if the failure has a cause other than the clock arithmetic.

## Scope Boundaries
- In scope: the fake clock and its advances in the elastic-retention component tests; the pool's time arithmetic
  only if it is shown to be at fault; docs, notes and bundles that the change touches.
- Out of scope: the pool's retention policy (baseline 20, max 256, settle 30 minutes, 10% decay every 10 minutes),
  other flaky tests, the kernel pools' callers.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner directed the fix in chat (2026-10-14) after the RISK note reported the flake.
- from_state: in_progress
- to_state: review
- transition_reason: the test's clock starts on a whole second (test-only), the reproducer finds no failing
  origin, the pool suites pass GIL off and on (2026-10-14T18:24:15Z); acceptance and the commit are the owner's.

## Steps / Checklist
- [x] Read the test module and `AbstractElasticPool` (pressure, settle, decay, catch-up) in full; record where the
      rounding happens and which side should own the fix.
- [x] Reproduce: count the clock origins for which the test's advances miss the settle time (before the fix).
- [x] Fix at the side the finding names; docstrings and comments current.
- [x] Validate: the reproducer finds no failing origin; the module and the pool unit tests pass GIL off and on.
- [x] Docs where a measured range moves; rebuild llm_support (and assets if src or system docs changed) last.
- [x] Move to review and report to the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A deterministic `test_quiet_root_pool_decays_to_baseline_and_burst_restretches` (and any sibling that advances the
  clock the same way), the reproducer's before and after runs, rebuilt bundles.

## Files / Paths Impacted
- `tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py` (`_Clock`, `import math`)
- `src/melder/utilities/general_base/abstract_elastic_pool.py` (read only; unchanged)
- `context_compass/system_docs/tests_components.md` and its index (code-map range, handoff line)
- `llm_support/` and `src/melder/_build_assets/` (rebuilt)

## Validation
- Run on the device VM (Python 3.14.7t, GIL off and on): the reproducer over 100,000 origins (current clock 155
  failing, whole-second clock 0); the module and the six pool unit files (76 passed each way); 25 repeated module
  runs per mode (all passed). Index check of tests_components: OK. Bundle and asset checks: see Notes.
- Not run: the full tree (the change is one test module's clock); the Windows tiers and hosted CI (the owner's).

## Risks / Rollback Notes
- A test-only change cannot affect the runtime; rollback is the test file.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/pool_decay_clock_rounding_20261014/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - the elastic pool's settle and decay arithmetic under a fake clock
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose, design, implementation, test and evidence; the
  whole ticket; initial revision 2026-10-14T18:13:22Z; evidence in Notes. The directive is the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:13:22Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Opened from the owner's directive. Known so far (RISK note of the many-child fix task): the test advances
    its fake clock by `settle - 1.0` and then by `1.0`, which for about 1% of clock origins sums one ulp short of
    `origin + settle`, so the pool sees the settle time not yet reached and skips the decay step. Which side owns the
    fix is UNKNOWN until the pool's settle and decay arithmetic is read.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-14_fix_many_child_follows_holder_task.md:276-298
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:129-161
  IMPACT: About 1% of CI runs can fail on this test today.
  NEXT: Read the test module and abstract_elastic_pool.py in full and record where the rounding happens.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:17:10Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The rounding is in the test's clock, not in the pool. The burst's misses run at the fake clock's origin C,
    so `_note_miss` sets `_next_decay_at = C + settle` in one float addition, and a return decays only when
    `now >= _next_decay_at` and `now - _last_miss_at >= settle`. The test reaches the settle time from a real-valued
    origin (`time.monotonic()`) through two additions (`+= settle - 1.0`, then `+= 1.0`), which can land one ulp
    short, so the return sees the deadline not yet reached (or the miss still inside the pressure window) and skips
    the step. With a live clock this cannot matter: time moves on and the next return decays, counting any missed
    steps. The later advances are safe: `+= interval` repeats the pool's own `now + interval` and `+= 10 * 3600.0`
    lands far past its deadline. Fix in the test: start the fake clock at a whole number of seconds at or after the
    real reading (`math.ceil(time.monotonic())`); whole numbers below 2**53 add exactly in binary64, so every advance
    and every deadline the pool computes is exact and the test still asserts the boundary itself.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:32-41
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:129-161
  - src/melder/utilities/general_base/abstract_elastic_pool.py:449-478
  - src/melder/utilities/general_base/abstract_elastic_pool.py:480-531
  - src/melder/utilities/general_base/abstract_elastic_pool.py:533-599
  IMPACT: A test-only fix: no src change, so no notch and no release-note entry (contribution guide); llm_support,
    which bundles tests/, is rebuilt last.
  NEXT: Reproduce with the real pool class over many clock origins, with the current origin and the whole-second one.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:19:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Reproduced against the real AbstractElasticPool (a minimal subclass built like the kernel pools: baseline
    20, max 256, default settle, decay and stretch) by replaying the test's sequence for 100,000 fake-clock origins
    between one minute and about a month of uptime, GIL off and on, identical results: the test's clock as written
    fails 155 origins (0.15%), always at the settle step (target 40 not 36, idle 40, no shell destroyed); landing on
    `origin + settle` in one addition from the same real-valued origin still fails 179 (the miss reads one ulp inside
    the pressure window), so the hazard is the real-valued origin, not only the two additions; a whole-second origin
    with the test's own two additions fails 0. The earlier probe's 1.1% sampled origins within 100,000 s of one
    reading; the rate depends on the clock's magnitude, never zero for a real-valued origin.
  EVIDENCE:
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/probe_decay_boundary.py:1-136
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/probe_decay_boundary_gil0.txt:1-4
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/probe_decay_boundary_gil1.txt:1-8
  IMPACT: Confirms the fix and its side: a whole-second origin in the test's `_Clock`; the pool stays as it is.
  NEXT: Edit `_Clock` (whole-second origin, docstring), then run the module and the pool unit tests GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:24:15Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Fixed in the test and validated. `_Clock` now starts on `float(math.ceil(time.monotonic()))` and its
    docstring states why (no earlier than the real reading; a whole-second origin keeps every advance and every
    deadline the pool derives from it exact); nothing else in the module changed and its CRLF endings are kept (183
    lines). The reproducer finds no failing origin for the whole-second clock (0 of 100,000, GIL off and on). The
    module and the pool unit suites (AbstractElasticPool, ConduitPool, SpellSpacePool and their multithreaded
    files) pass with the GIL off and on (76 each), and 25 repeated runs of the module pass in each mode.
    tests_components.md carries the module's remeasured code-map range and a handoff line; its index is
    regenerated and checked. No src change, so no notch and no release-note entry.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:21-21
  - tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py:33-55
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/pool_suites_after_fix.txt:1-7
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/module_repeat_after_fix.txt:1-2
  - context_compass/system_docs/tests_components.md:2114-2118
  - context_compass/system_docs/tests_components.md:2806-2810
  IMPACT: The quiet-pool test no longer depends on the clock's origin; the runtime is untouched.
  NEXT: Move to review, then rebuild llm_support (it bundles tests/) and the assets, and run both checks last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-14T18:26:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Rebuilt last. `llm_support/_builder.py --include-untracked` rewrote the tests bundle (1,083 files; src and
    other unchanged) and both checks print only OK lines: the build assets (agent documentation, bind guard, system
    documents - all current at v0.2.8235, so the asset runner had nothing to rebuild; tests_components is not one of
    its packaged documents) and the three LLM bundles. No .git/index.lock was left. The task moves to review.
  EVIDENCE:
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/llm_support_build.log:1-4
  - context_compass/artifacts/pool_decay_clock_rounding_20261014/runs/checks_after_rebuild.log:1-7
  IMPACT: The change set is complete and its generated outputs are current.
  NEXT: Owner accepts and turns the task in (closure sync, artifact disposition), or redirects.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
In review (2026-10-14). The quiet-pool decay test failed for about 0.2-1% of fake-clock origins because its clock
started at a real-valued monotonic reading, so the advance to the settle time could fall one ulp short or read the
burst's miss one ulp inside the pressure window. The pool's arithmetic is fine with a live clock and is unchanged;
the test's `_Clock` now starts on a whole second at or after the real reading, which makes every advance and every
deadline exact (reproducer: 0 failing origins of 100,000). Test-only: no notch, no release note. Owed by the owner:
acceptance and the commit of the test module, tests_components.md and its index, the rebuilt bundles and the
evidence folder.

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
