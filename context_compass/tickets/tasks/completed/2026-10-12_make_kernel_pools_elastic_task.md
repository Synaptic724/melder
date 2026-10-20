# Task: Make the kernel pools elastic - retained idle follows demand and decays when quiet

## Metadata
- Task ID: TASK-2026-10-12-make_kernel_pools_elastic
- Story: none - directly under EPIC-2026-10-05-melder_services_and_pools
- Status: done
- Owner: user
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-12T19:00:57Z
- Updated: 2026-10-12T21:14:45Z

- Completed: 2026-10-12T21:14:45Z
- Summary: Landed, notched 0.2.8234: SpellSpacePool and ConduitPool keep what a burst needed, up to 256, and decay to 20
  when quiet; the owner's native big test shows no regression at 20 threads and a 3-22x shorter return tail past
  20; release note 'Lesser conduits and spellspaces past 20 are kept and reused, then let go when quiet'.
  Accepted and turned in by the owner 2026-10-12; evidence kept.

## Objective
`AbstractElasticPool` keeps what demand needs and lets it go when demand falls: the retained target (`target_idle`)
follows the load the pool actually saw, up to `max_idle`, and decays toward `baseline_idle` on a clock once no
shortage has happened for a while, trimming the surplus. `SpellSpacePool` and `ConduitPool` use it with a real range,
so a burst of more than 20 concurrent scopes stops rebuilding and destroying expensive conduit and spellspace shells
every cycle. Proven before landing with melder_gauntlet runs (1-3 threads before and after, loads past the 20 retained
shells) and a 20-thread maximum test on the owner's machine before and after the code change, with no hot-path
regression.

## Ticket Contract
- ENTRY_GATE: the board row `elastic_pool_retention` routes here; the owner's direction is in the epic Decision Log
  (2026-10-12); patch docs exist and are linked before any edit to `src/` in the working tree.
- EXECUTION_BOUNDARY: `src/melder/utilities/general_base/abstract_elastic_pool.py`,
  `src/melder/aether/conduit/spell_space/spell_space_pool.py`, `src/melder/aether/conduit/conduit_pool.py`, the pool
  construction and prewarm sites in `src/melder/aether/conduit/conduit.py`, their docstrings; the tests that pin the
  old algorithm or set pool policy fields; benchmark runners under this task's artifacts; system docs, graph
  descriptors, the release note, the version notch, assets and bundles.
- DEPENDENCIES: `benchmarks/testing_other_di/test_melder_gauntlet.py` and `melder_gauntlet_support.py` (workload);
  the pooled-spell design in the epic (tickets/epics/2026-10-05_melder_services_and_pools_epic.md) reuses this
  elastic system.
- EXIT_GATE: gauntlet evidence before and after (1-3 threads; loads above 20 concurrent shells; the 20-thread maximum
  on the owner's machine) with no hot-path regression; new tests red on the base and green on the candidate; the full
  tree green on the cut; docs, graph, assets and bundles current; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST when the fix costs measurable time on the 1-3 thread gauntlet, when the
  retained memory at `max_idle` is material, or when a public signature would have to change.

## Scope Boundaries
- In scope: the stretch and decay algorithm of `AbstractElasticPool`; wiring it into `SpellSpacePool` and
  `ConduitPool`; their sizes; tests, benchmarks and docs for it.
- Out of scope: the pooled-spell existence (epic); a release into a retired pool (the separate doc/code gap recorded in
  the epic); the melder_gauntlet 1-3 thread cap in `test_melder_gauntlet.py` (a separate runner covers more threads).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner asked for the fix with a speed-test-first sequence (epic Decision Log 2026-10-12).
- from_state: in_progress
- to_state: review
- transition_reason: 0.2.8234 landed (src, tests, docs, graph, release note, notch, assets and bundles) and the owner's
  native 20-thread before/after run is recorded (2026-10-12); acceptance, commit and push are the owner's.
- from_state: review
- to_state: done
- transition_reason: (2026-10-12T21:14:45Z) the owner turned in every finished melder_1 ticket (chat 2026-10-12: "just close everything you finished");
  git add -A (the new component test, the archived patch folder, the evidence folder), commit, push, the Windows tiers and hosted CI remain the owner's.

## Steps / Checklist
- [x] Record the workload, the tests that pin the old algorithm and the machine limits.
- [x] Patch docs (architecture, components, code description) linked here.
- [x] Baseline: melder_gauntlet with many iterations, 1-3 threads, on a copy of the current tree.
- [x] Prototype the fix on a scratch copy; unit-test it; measure 1-3 threads and loads above 20 concurrent shells.
- [x] Show the owner the whole fix and the numbers.
- [x] Prepare the big test; 20-thread maximum baseline on the owner's machine before the code change.
- [x] Land: src, tests (red on base, green on cand), full tree, docs, graph, release note, notch, assets, bundles.
- [x] Re-run the big test after the code change and report.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The fixed elastic pool and the two kernel pools using it, with tests and docs.
- Gauntlet evidence before and after, and the big-test runner.

## Files / Paths Impacted
- src/melder/utilities/general_base/abstract_elastic_pool.py
- src/melder/aether/conduit/spell_space/spell_space_pool.py
- src/melder/aether/conduit/conduit_pool.py
- src/melder/aether/conduit/conduit.py
- tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py
- tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool_multithreaded.py
- tests/component/melder/aether/conduit/test_kernel_pool_elastic_retention.py (new)
- tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py
- tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py
- src/melder/__version__.py and release_docs/next_version_release.md (0.2.8234)

## Validation
- Gauntlet on the VM: 1-3 threads base vs candidate within noise; 24-64 threads the churn is gone (Notes 19:31Z,
  19:53Z).
- New tests red on 0.2.8233 (21 failed / 102 passed) and green on the candidate (123 passed), GIL off and on; 20
  repeats green; full tree on the scratch candidate, GIL off: every chunk green (Note 20:29:00Z).
- Post-landing suites on the working tree, GIL off: 2,144 passed (Note 20:30:41Z).
- The owner's native big test, 0.2.8233 vs 0.2.8234: no regression at 20 threads, retention past 20, the return
  tail 3-22x shorter (Note 2026-10-12T21:01:31Z).
- Assets and llm_support rebuilt and checked, OK lines only (Note 2026-10-12T21:04:38Z).
- Full tree on the landed working tree, Windows tiers and hosted CI: Not run (owner's).

## Risks / Rollback Notes
- Retained shells hold memory up to `max_idle` until the decay clock lets them go; sizes are chosen from measurement.
- A clock read on returns while more than `baseline_idle` objects are idle; measured before landing.
- Rollback: revert the three pool modules and the size literals; no data format, cache or record changes.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
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
- [x] Acceptance criteria reviewed with user and confirmed (owner turn-in, 2026-10-12)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/elastic_pool_retention_20261012/ (benchmark runners, run logs, the prototype and its diff)
  - artifacts/melder_object_pools_20261011/ (the probes and simulation that found the problem)
  - system_docs/patches/completed/elastic_pool_retention_2026_10_12/ (architecture, two component and one code
    description patch; promoted and archived at landing)
- DISPOSITION: retain_as_reference (evidence); promote_to_documentation (patch docs, archived at landing)
- CLEANUP_TRIGGER: evidence decided at turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - elastic retention of the kernel pools
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-12T19:00:57Z
  TYPE: FACT
  CLAIM: Starting point. melder_gauntlet: each scope cycle takes a lesser from the root's ConduitPool, melds in it,
    enters one spellspace on that lesser (the lesser's own SpellSpacePool), melds, exits and returns the lesser, so the
    root pool sees one lesser per running thread; `test_melder_gauntlet.py` caps MELDER_GAUNTLET_THREADS at 3, while
    `melder_gauntlet_support.run_gauntlet_once` already spreads more threads over the three lanes. The old algorithm
    is pinned by tests (`test_abstract_elastic_pool.py` asserts percent stretch per miss and decay per overflow) and
    two tests set pool policy fields directly (`_target_idle`, `_max_idle`). The owner's machine runs the work in a
    2-vCPU, 3 GB Linux VM, so 20 threads are oversubscribed there.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:35-71
  - benchmarks/testing_other_di/test_melder_gauntlet.py:144-211
  - benchmarks/testing_other_di/melder_gauntlet_support.py:633-744
  - tests/unit/melder/utilities/data_structures/test_abstract_elastic_pool.py:181-381
  - tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py:205-214
  - tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py:277-326
  IMPACT: Loads above 20 concurrent shells need a runner past the 3-thread cap; the test changes are part of the fix.
  NEXT: Write the patch docs for the new retention algorithm, then baseline the gauntlet on a copy of the tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T19:17:31Z
  TYPE: MEASURE
  CLAIM: Calibration on the VM (2 vCPU, Python 3.14.7t, gil=0) against a byte-identical scratch copy of 0.2.8233,
    through the new runner (any thread count; per-run JSON with the root pools' describe() at cleanup): 50
    iterations at 1 thread ran 500 hot scopes, median 0.446 ms per iteration, 13,562 scopes/s; at 3 threads 3,250
    scopes, median 1.688 ms, 33,214 scopes/s. Shell costs (tracemalloc on, so times run high): a lesser shell holds
    6.7 KiB, builds in 78.5 us and tears down in 6.2 us; a spellspace shell holds 1.3 KiB, 19.6 us and 1.9 us.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/calib_0.2.8233.jsonl:1-2
  - context_compass/artifacts/elastic_pool_retention_20261012/gauntlet_runner.py:1-142
  - context_compass/artifacts/elastic_pool_retention_20261012/probe_shell_memory.py:1-68
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/probe_shell_memory_base.txt:1-4
  IMPACT: 50 iterations take well under a second, so thousands per run fit the VM's time limit; keeping 256 idle
    lessers costs about 1.7 MiB per root, so the retained memory is not material.
  NEXT: Finish the scratch candidate (prewarm docstrings, version wording), record it, then run base vs candidate.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T19:18:55Z
  TYPE: PLAN
  CLAIM: The fix, prototyped on a scratch copy (no edit to the tree). AbstractElasticPool keeps its public signature;
    a miss records pressure (`_note_miss`); a return that leaves more than `baseline_idle` idle enters the elastic
    band (`_rebalance_after_return`, lock-free unless something must change): under pressure (a miss within the
    settle time) it stretches the target to the idle count (+`stretch_percent` headroom, now default 0) up to
    `max_idle`; once settled, decay lowers it 10% of the stretched value per 600 s with catch-up after a long quiet
    period; surplus is trimmed oldest-first, one decay step per return, destroyed outside the lock. The fast path
    (append, compare with `baseline_idle`) has no clock read and no lock. SpellSpacePool and ConduitPool call
    `_note_miss` on a miss and the band on return; their size becomes baseline 20, max 256 (was 20/20); docstrings,
    the prewarm contracts and the corrected cleanup note go with it. A fake-clock probe on the root ConduitPool shows
    it: a burst of 50 keeps 50 (the base keeps 20 and destroys 30), a repeat builds nothing (base: 30 built, 30
    destroyed), decay starts after 30 quiet minutes (50 -> 45 -> 40 -> 35), catches up to 20 after hours, and the
    next burst stretches back; over the timeline 80 built / 30 destroyed against the base's 110 / 90.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/abstract_elastic_pool.py:325-376
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/abstract_elastic_pool.py:446-562
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/apply_elastic.py:1-270
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/src_elastic.diff:1-739
  - context_compass/artifacts/elastic_pool_retention_20261012/probe_retention_decay.py:1-101
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/probe_retention_decay_base.txt:1-15
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/probe_retention_decay_cand.txt:1-15
  IMPACT: In melder_gauntlet the root ConduitPool sees one lesser per thread and each lesser's SpellSpacePool one
    space, so up to 20 threads base and candidate behave alike (the speed check); above 20 the base destroys and
    rebuilds (threads - 20) lessers at each iteration boundary and the candidate keeps them (the retention check).
  NEXT: Run base vs candidate interleaved at 1, 2 and 3 threads with thousands of iterations, then 24-64 threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T19:21:19Z
  TYPE: MEASURE
  CLAIM: Instrumented gauntlet (50 iterations; counters under one lock, so not timed) on the VM's 2 vCPUs: the
    root ConduitPool's peak of lessers out at once reaches the thread count (24 at 24 threads, 48 at 48). The base
    (20/20) built 30 lessers at 24 threads and 336 at 48 - 10 and 316 rebuilt and destroyed after the first 20 -
    because each time more than 20 were out the extras were destroyed on return; the candidate built 24 and 48
    once and reused them for all 26,000 and 52,000 scope cycles. Each rebuilt lesser also rebuilt its spellspace.
    With 2 cores the base churns less than (threads - 20) per iteration, so a machine with more cores churns more.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/instrumented_t24_t48_50iters.jsonl:1-4
  - context_compass/artifacts/elastic_pool_retention_20261012/gauntlet_runner.py:26-82
  IMPACT: Confirms the retention problem in the real workload and that the candidate removes it; the timing
    comparison runs uninstrumented. A background job does not survive a device shell call, so runs go in
    foreground batches under the 180 s limit.
  NEXT: Time base vs candidate at 1, 2 and 3 threads, 15,000 iterations per run, three interleaved rounds.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T19:31:15Z
  TYPE: MEASURE
  CLAIM: Speed at 1-3 threads, base 0.2.8233 vs candidate, VM 3.14.7t gil=0: four interleaved rounds (two base
    first, two candidate first) of 15,000 iterations per run. Candidate/base, scope cycles per second: 1 thread
    1.002, 2 threads 0.994, 3 threads 0.985; iteration median 0.999, 1.004, 1.014. Run-to-run spread is 2-4% and
    the tree that runs second in a pair is slower, so these are within noise; at 3 threads the outer-create p99
    is 42 vs 25 us, preemption-dominated on 2 cores (3 workers + main). Single-thread micro-benchmark of the pool
    paths, median of 5 runs x 9 repeats: lesser cycle 1,005 vs 1,013 ns, spellspace cycle 332 vs 329 ns, raw
    ConduitPool take+return 82.4 vs 82.0 ns, raw SpellSpacePool acquire+release 110.4 vs 112.7 ns - identical.
    In the elastic band (40 idle, candidate only) a return costs 55-60 ns more (137.7 and 173.0 ns): the clock read.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/phaseA_t1-3_15000iters.jsonl:1-24
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/phaseA_summary.txt:1-42
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/pool_paths_micro.jsonl:1-10
  - context_compass/artifacts/elastic_pool_retention_20261012/bench_pool_paths.py:1-88
  - context_compass/artifacts/elastic_pool_retention_20261012/summarize_runs.py:1-57
  IMPACT: No hot-path regression at 1-3 threads (the FAILURE_ESCALATION trigger did not fire). The only new cost
    is about 60 ns per return while more than 20 shells are idle, against ~85 us per lesser the base rebuilds.
  NEXT: Time base vs candidate at 24, 32, 48 and 64 threads, four interleaved rounds.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T19:53:55Z
  TYPE: MEASURE
  CLAIM: Past the 20 retained shells, VM 2 vCPU, four interleaved rounds per thread count (2,500 / 2,000 / 1,300 /
    1,000 iterations at 24 / 32 / 48 / 64 threads, about 1.3M scope cycles per run). Candidate/base, scope cycles
    per second: 1.025, 1.008, 1.033, 0.988; iteration median 0.979, 0.991, 0.973, 1.015; iteration p95 0.961,
    0.988, 0.945, 1.001. The lesser return's p99 (outer cleanup) drops from 33 / 15 / 14 us to 5.4 / 4.7 / 5.2 us
    at 32 / 48 / 64 threads. The root pool ends with target and idle equal to the thread count (24, 32, 48, 64)
    against 20 on the base. Instrumented: the base rebuilds and destroys 0.2, 1.2, 6.3 and 10.7 lessers per
    iteration at 24, 32, 48 and 64 threads; the candidate none after its first burst.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/phaseB_t24-64.jsonl:1-32
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/phaseB_summary.txt:1-56
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/instrumented_t24-64.jsonl:1-8
  IMPACT: Retention works in the real workload and removes the churn; on 2 cores the churn is only 2-3% of an
    iteration, so throughput moves within noise (-1 to +3%) while the return-path tail improves 3-6x. More cores
    put more lessers out at once, so the owner's machine is where the throughput difference shows.
  NEXT: Send the owner the whole fix and the numbers; prepare the big test (20 threads, maximum load) and record
    its baseline on the current tree before the code change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T20:06:26Z
  TYPE: MEASURE
  CLAIM: Big-test baseline on the current tree's source (0.2.8233; the scratch base is byte-identical to the working
    tree, checked with diff -rq), VM: three 20-thread runs of 8,000 iterations (3.4M scope cycles each) gave 50,895,
    41,096 and 40,468 scope cycles/s (iteration median 8.23 / 9.96 / 10.33 ms; peak RSS 0.8 GB); the ladder past
    retention gave 39,780 / 39,123 / 37,048 / 34,514 scopes/s at 24 / 32 / 48 / 64 threads. The root pool held 20
    in every run. The VM is shared: its load average read 10.7 / 8.9 / 8.6 with none of these runs active (other
    sessions' work is hidden by the sandbox), and throughput fell 20% between the first and second run.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/big_before_0.2.8233_vm.jsonl:1-7
  - context_compass/artifacts/elastic_pool_retention_20261012/big_test.py:1-70
  IMPACT: Absolute VM numbers drift with other sessions' load, so the after-change test must interleave the kept
    base copy with the landed tree; the owner's native run (big_test.py --phase before/after) is the clean one.
  NEXT: Write the patch docs (architecture, component, code description) and link them, then the unit tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T20:29:00Z
  TYPE: FACT
  CLAIM: Three refinements to the prototype, found while writing its tests (diff and patch docs updated). (1) A
    fixed-capacity pool (max_idle == baseline_idle) keeps the old return: evict the oldest idle object, no clock read,
    no lock - two existing ConduitPool tests pin this by making the clock raise. (2) Under pressure only objects above
    max_idle are trimmed: concurrent returns can grow the deque between a stretch and its trim, and trimming against
    the just-stretched target destroyed shells a burst had built. (3) A destroy that raises inside a batched trim
    propagates as before, and the detached objects after it go back to the oldest end of the idle deque (a finally),
    so none is dropped undestroyed.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/abstract_elastic_pool.py:480-599
  - tests/unit/melder/aether/conduit/test_conduit_pool.py:121-166
  - tests/unit/melder/aether/conduit/test_conduit_pool_multithreaded.py:167-200
  - context_compass/system_docs/patches/active/elastic_pool_retention_2026_10_12/code_description_patch_abstract_elastic_pool.md:1-37
  IMPACT: Fixed pools cost exactly what they did; elastic retention keeps a racing burst whole; trims cannot leak.
  NEXT: Record the red/green and full-tree results, then the patch-to-implementation mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T20:29:00Z
  TYPE: MEASURE
  CLAIM: Tests for the new contract, installed on scratch copies by install_tests.py: 13 new unit tests and the
    describe expectation in test_abstract_elastic_pool.py, the band and burst tests in the multithreaded file, a new
    component file (repeat bursts of lessers and spellspaces past 20, the 256 cap, settle/decay/catch-up/re-stretch on
    the root pool with a fake clock, prewarm past 20), and the pool fields two tests set. On 0.2.8233 the selection
    gives 21 failed / 102 passed (GIL off and on); on the candidate 123 passed (both), and 20 repeats of the
    concurrency-bearing files pass. Full tree on the candidate, GIL off: every chunk green (unit 9,046 incl. 821
    utilities; component 2,338 incl. 1,328 aether; integration 2,068; experimentation 250); the first unit_gh and
    exper runs failed only on files the scratch copy lacked (.readthedocs.yaml, the benchmarks package), green once
    present.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/install_tests.py:1-140
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/tests_elastic.diff:1-770
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/newtests_red_gil0.log:1-425
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/newtests_cand_gil0.log:1-3
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/newtests_cand_repeats.log:1-1
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/full_tree_cand/summary_cand_gil0.txt:1-25
  IMPACT: The candidate meets the EXIT_GATE's test half before it touches the working tree.
  NEXT: Write the patch-to-implementation mapping, then copy src and tests into the working tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T20:29:18Z
  TYPE: PLAN
  CLAIM: Patch-to-implementation-to-validation mapping (patch docs read in order: architecture, the two component
    patches, the code description). Architecture invariants 1-6 and the code description's steps 1-6 and edge cases
    -> abstract_elastic_pool.py -> the unit tests, one per step or edge (miss, burst, headroom, cap, trim without
    pressure, settle, decay step, catch-up, floor, postponed decay, re-stretch, fixed capacity, destroy failure) and
    the two multithreaded ones. Conduit Runtime patch -> conduit_pool.py and conduit.py (sizes 20/256, prewarm
    docstrings) -> test_conduit_pool*, test_named_lesser_directory_lifecycle and the new component file. Creations and
    SpellSpace patch -> spell_space_pool.py -> the spell_space unit tests and the component file. Interface deltas
    (no public signature change, describe() keys kept) -> test_conduit_pool's describe test. Landing copies the four
    src files and five test files from the tested candidate into the tree byte for byte, after checking the tree still
    equals the scratch base; then post-landing pool and component runs on the tree, docs, graph, release note, notch
    0.2.8234, patch archive, assets and llm_support, and the big test after the change.
  EVIDENCE:
  - context_compass/system_docs/patches/active/elastic_pool_retention_2026_10_12/architecture_patch.md:1-67
  - context_compass/system_docs/patches/active/elastic_pool_retention_2026_10_12/component_patch_conduit_runtime.md:1-29
  - context_compass/system_docs/patches/active/elastic_pool_retention_2026_10_12/component_patch_creations_and_spellspace.md:1-24
  - context_compass/system_docs/patches/active/elastic_pool_retention_2026_10_12/code_description_patch_abstract_elastic_pool.md:1-37
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/src_elastic.diff:1-775
  - context_compass/artifacts/elastic_pool_retention_20261012/prototype/tests_elastic.diff:1-770
  IMPACT: The ENTRY_GATE is met (patch docs exist, are linked, and are mapped); the src edit can land.
  NEXT: Copy the candidate's src and test files into the working tree and run the pool suites there.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T20:30:41Z
  TYPE: FACT
  CLAIM: Landed in the working tree: the four src files (abstract_elastic_pool.py, spell_space_pool.py, conduit_pool.py,
    conduit.py) and five test files (the two elastic-pool unit files, the named-lesser component test, the
    experimentation harness, and the new test_kernel_pool_elastic_retention.py) copied from the tested candidate and
    checked byte-identical, after confirming the tree still matched the scratch base. The 0.2.8233 originals are kept
    under prototype/before_0.2.8233/ so a native before-run stays possible. Post-landing on the tree (GIL off): the
    elastic-pool unit tests, every unit and component conduit test and the harness - 2,144 passed.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/post_landing_gil0.log:1-31
  - src/melder/utilities/general_base/abstract_elastic_pool.py:480-599
  - src/melder/aether/conduit/conduit.py:349-368
  IMPACT: The source change is in place; docs, graph, release note, notch, archive and rebuild follow.
  NEXT: Update src_architecture, src_components and tests_components with their indexes, then the graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T20:55:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Docs, graph, release note, notch and patch archive for 0.2.8234 are in place (written 20:31-20:41Z, before
    the compaction). src_architecture gains the Operational Invariant, the four pool files' measured extents and
    notes, the sources and a handoff paragraph; src_components gains the Conduit Runtime and Creations and SpellSpace
    paragraphs and a handoff; tests_components gains the two clusters' bullets and the new component file; the three
    indexes were regenerated. Seven graph nodes were re-read against source and accepted, and the graph reassembled
    (27,739 lines, 614-line index, all 587 ranges verified; --check clean). The release note carries the section and
    the 0.2.8234 rebuild line, `__version__` is 0.2.8234, the four patch docs sit under patches/completed with both
    boards pointing there, and the notch notice is on the attention board.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:923-941
  - context_compass/system_docs/src_architecture.md:2910-2923
  - context_compass/system_docs/src_architecture.md:3584-3589
  - context_compass/system_docs/src_components.md:2671-2683
  - context_compass/system_docs/src_components.md:3122-3129
  - context_compass/system_docs/tests_components.md:1101-1105
  - context_compass/system_docs/tests_components.md:1170-1172
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/accept_0_2_8234.log:1-14
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/assemble_check_0_2_8234.log:1-4
  - release_docs/next_version_release.md:121-144
  - src/melder/__version__.py:12-12
  - context_compass/attention_board.md:314-316
  IMPACT: All of 0.2.8234 but the asset/bundle rebuild and the after-change test is landed; the rebuild stays last.
  NEXT: Once the owner's native after phase ends (it imports from this tree), rebuild assets and llm_support with
    --check, then run the VM after-test against the kept 0.2.8233 base.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T21:01:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The owner's native big test (Windows, Python 3.14.7, gil=0): before = 0.2.8233 (a %TEMP% copy of the tree with
    the four 0.2.8233 pool files, version string 0.2.8233), after = the landed 0.2.8234 tree; 3 rounds each, the two
    phases run one after the other, not interleaved. Candidate/base, mean of 3 runs, scope cycles per second: 20
    threads 1.021 (iteration median 0.971, p99 0.992); past retention 24 / 32 / 48 / 64 threads 0.947 / 1.041 / 0.973
    / 1.025 (iteration p99 0.996 / 0.958 / 0.991 / 0.995). Within one tree the runs spread 9-13%, so every throughput
    ratio is inside noise (geometric mean of the five 1.001). The lesser return's p99 falls from 47 / 63 / 73 / 408 us
    to 15 / 15 / 16 / 18 us at 24 / 32 / 48 / 64 threads and is unchanged at 20 (15.8 vs 15.7 us). The root pool
    ends with target = idle = 24 / 32 / 48 / 64 (max 256) against 20 on the base, and 20 / 20 at 20 threads.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/big_before_native_owner.jsonl:1-15
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/big_after_native_owner.jsonl:1-15
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/big_native_owner_summary.txt:1-70
  IMPACT: The EXIT_GATE's 20-thread maximum before and after is met on the owner's machine: no regression, retention
    works, the return tail is 3-22x shorter. Throughput past 20 does not move beyond noise because the shells the
    base rebuilt are a small share of an iteration. The VM after-test would add nothing the native pair lacks.
  NEXT: Rebuild assets and llm_support with --check, then move the ticket to review and report.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-12T21:04:38Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Rebuilt last for 0.2.8234, after the owner's native after phase had finished: the build assets (agent
    documentation 462 entries, bind guard 622, system documents 4, all stamped v0.2.8234) and the llm_support bundles
    with --include-untracked (src 579, tests 1,081, other 404 files). Both --check runs print only OK lines, and no
    .git/index.lock was left. The owner's big_before.jsonl and big_after.jsonl at the repository root are copied into
    runs/; .jsonl is not a bundled extension, so the builder skipped them.
  EVIDENCE:
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/build_assets_0_2_8234.log:1-3
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/build_assets_check_0_2_8234.log:1-3
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/llm_support_0_2_8234.log:1-4
  - context_compass/artifacts/elastic_pool_retention_20261012/runs/llm_support_check_0_2_8234.log:1-3
  - llm_support/_builder.py:40-56
  IMPACT: The landing is complete; what remains is the owner's: git add of the new files, commit, push, Windows tiers,
    hosted CI, and acceptance.
  NEXT: Move the ticket and its board row to review/handoff and report to the owner.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-12T21:12:30Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Owner turn-in directive, chat 2026-10-12: "you can close the tickets and call it", then "all your tickets
    all of them were reviewed turn them all in" and "just close everything you finished". The set is every finished
    melder_1 ticket routed on the board: the 15 review tasks of 2026-10-04 to 2026-10-11 (CI/CD lanes and the
    0.2.8223-0.2.8233 landings) and this task. The services-and-pools epic is not finished (its pooled_spell design
    and five asks are open) and stays open; backlog tickets are not in the set. Per ticket: a completion summary
    naming the notch and release-note section, review -> done, a move to tickets/tasks/completed/; the three patch
    folders still under patches/active (meldercache_suffix, spellmap_binding_name_case, live_unlink_visibility_race;
    promoted at landing) are archived, evidence folders are kept as reference, and board rows, details and anchors
    are synced.
  EVIDENCE:
  - context_compass/attention_board.md:192-213
  - context_compass/artifact_board.md:89-104
  IMPACT: Owner-owed items (commits, pushes, Windows tiers, hosted CI) stay recorded in each closure note.
  NEXT: Apply the scripted turn-in, then verify the boards and the asset and bundle checks.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Opened 2026-10-12 from the pools epic at the owner's request: make the kernel pools' retention elastic (follow
demand, decay when quiet), proven with gauntlet runs before and after. Landed at 0.2.8234: AbstractElasticPool
stretches to the idle count a return sees while a miss happened in the last 30 minutes (up to max_idle), then
decays 10% per 10 minutes with catch-up, trimming oldest-first outside the lock; SpellSpacePool and ConduitPool
are 20/256 (were 20/20); a fixed-capacity pool keeps the old eviction. Evidence: VM runs at 1-3 and 24-64 threads,
new tests red/green and the full tree in scratch, 2,144 post-landing tests, the owner's native 20-thread
before/after (no regression, retention works, return tail 3-22x shorter), docs, graph, release note and notch,
assets and bundles checked. Owner-owed: git add -A (the new component test, the archived patch folder, this task's
evidence folder), commit and push, Windows tiers and hosted CI, acceptance. Next: the owner accepts or redirects;
the pooled-spell design then resumes in the epic.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
