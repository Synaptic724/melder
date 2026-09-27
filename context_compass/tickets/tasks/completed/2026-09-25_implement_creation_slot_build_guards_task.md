

# Task: Implement per-slot creation build guards so store locks become leaf locks

## Metadata
- Completed: 2026-09-25T23:47:39Z
- Summary: Per-slot build guards replace store-held builds (store lock is a leaf); 8 lock-order shapes pass; cold +4-7%,
  warm 0%; canonical docs, graph and next-release note updated; patch docs archived.
- Task ID: TASK-2026-09-25-implement-creation-slot-build-guards
- Story: STORY-2026-09-25-verify-override-writer-and-contract
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-25T22:44:04Z
- Updated: 2026-09-25T23:47:39Z

## Objective
Remove the store-lock/Spell-lock deadlock by moving build-once exclusion off the Creations store
lock onto one build guard per slot, so a store lock is only held for dict reads and writes and is
never held while waiting on another lock or running user code. Measure the cost.

## Ticket Contract
- ENTRY_GATE: Owner approved implementation (2026-09-25, "go ahead and implement it"); board row
  routes here; patch docs existed under system_docs/patches/active/creation_slot_build_guards_2026_09_25/
  (archived to patches/completed/ at closure)
  and are linked below before any src/ edit.
- EXECUTION_BOUNDARY: Creations stores (creations.py, conduit_creations.py, cluster_creations.py),
  the generated-code emitters and hydrated runtimes that take store or Spell build locks, the purge
  path, the compiled-cache version constant, the deadlock regression test file, and this task's patch
  docs and artifacts. Exact file list is recorded in a PLAN note after the read pass.
- DEPENDENCIES: tickets/tasks/2026-09-25_verify_native_writer_lock_order_task.md (design, evidence);
  artifacts/melder_writer_lock_order_20260925/writer_options.md section 9 (Idea A).
- EXIT_GATE: All 7 former DEADLOCK_CASES pass as SAFE on 3.14.7t and GIL; relevant existing suites
  pass; cold/warm meld overhead measured before and after; patch docs mapped to implementation.
- FAILURE_ESCALATION: BLOCKER if a store-lock user needs build exclusion that the design cannot give
  without holding a lock across user code; DECISION_REQUEST for any public-behavior change.

## Scope Boundaries
- In scope: slot guards for every slotted existence (unique_per_conduit, unique_per_spell_space,
  lineage, cluster); unique keeps Spell._lock as its slot guard; leaf store locks; purge through the
  slot guard; publish-after-cleanup check; cache version bump; regression tests.
- Out of scope: moving unique off Spell._lock; the joint-alpha override optimization; hook
  standardization; canonical system_docs merge (closure step, after owner acceptance).

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner accepted the delivered fix on 2026-09-25 and directed closure.

## Steps / Checklist
- [x] Read every store-lock and build-lock user in full; record the exact file/symbol list (PLAN).
- [x] Write patch docs (architecture, component, code description) and link them here.
- [x] Baseline benchmark (cold and warm meld) in the VM copy on 3.14.7t.
- [x] Implement Creations slot guards, leaf publish, purge and cleanup changes.
- [x] Implement emitter/runtime changes for every family and route.
- [x] Bump the compiled-cache version so stale executors are rejected.
- [x] Move fixed cases to SAFE_CASES; add unique -> many -> unique_per_conduit case.
- [x] Run relevant suites on 3.14.7t and GIL; re-run benchmark; record MEASURE notes.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Source changes listed in the PLAN note.
- tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py (updated).
- system_docs/patches/active/creation_slot_build_guards_2026_09_25/ patch docs.
- artifacts/creation_slot_build_guards_20260925/ benchmark results.

## Files / Paths Impacted
- src/melder/aether/conduit/creations/creations.py
- src/melder/aether/conduit/creations/conduit_creations.py (docstring)
- src/melder/aether/conduit/creations/cluster_creations.py (docstring)
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py
- src/melder/utilities/caching_system/caching_system.py
- tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py
- tests/integration/melder/spellbook/test_cache_schema_version_integration.py
- tests/unit/melder/aether/conduit/creations/test_creations.py (post-cleanup publish now RuntimeError)
- tests/unit/melder/aether/conduit/creations/test_creations_slot_guard.py (new, 13 tests)

## Validation
- Run on the VM source copy (3.14.7t and 3.14.7 GIL); see MEASURE notes. Owner-side full run: Not run.
- Recommended commands:
  - python -m pytest tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py
  - python -m pytest tests/unit/melder/aether/conduit/creations tests/component/melder/aether/conduit
  - python -m pytest tests

## Risks / Rollback Notes
- Stale compiled executors in __melder_cache__ would keep the old locking: bump the cache version.
- Store-lock users that relied on "holding the store excludes in-flight builds" (cleanup, transfer,
  pool reset) must be re-audited; publish-after-cleanup must be rechecked under the leaf lock.
- Rollback: revert the listed files; the regression file flips back to strict xfail.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No store lock held across user code or another lock acquisition after the change.
- [ ] No performance claim without a measured before/after.

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
  - system_docs/patches/completed/creation_slot_build_guards_2026_09_25/architecture_patch.md
  - system_docs/patches/completed/creation_slot_build_guards_2026_09_25/component_patch_creations.md
  - system_docs/patches/completed/creation_slot_build_guards_2026_09_25/component_patch_creation_codegen.md
  - system_docs/patches/completed/creation_slot_build_guards_2026_09_25/code_description_patch_creations.md
  - artifacts/creation_slot_build_guards_20260925/
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Owner acceptance; patch deltas merge into src_architecture/src_components.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: Creations slot guards; leaf store locks.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-25T22:44:04Z
  TYPE: DECISION
  CLAIM: Owner approved implementing Idea A. Recorded interpretation of the approval, which followed
    melder_0's recommendation: guards live on the store (map spell_id -> RLock), applied to every
    store, not only root/leader stores. unique keeps Spell._lock as its slot guard because a unique
    spell has exactly one slot (its owner store) and that lock already has the required shape; moving
    it off Spell._lock stays out of scope. Owner concern: overhead - measure before and after.
  EVIDENCE:
  - artifacts/melder_writer_lock_order_20260925/writer_options.md:151-213
  - tickets/tasks/2026-09-25_verify_native_writer_lock_order_task.md:409-435
  IMPACT: Fixes scope for the read pass and the patch docs.
  NEXT: Read every store-lock and build-lock user in full, starting with creations.py.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T22:49:31Z
  TYPE: FACT
  CLAIM: Read pass complete. (1) Meld._lock guards only hooks, cleanup and lazy compiler-system init,
    never a build, so the section-9 "Meld RLock scope" unknown is closed. (2) Every build-once site holds
    the STORE lock across construction: 8 door sites (per_conduit/spellspace/lineage/cluster x no-overrides
    and overrides), and plan-step sites in the generalized no-overrides, generalized overrides (shape and
    generic emitters), many_only overrides (dead non-many branches) and manifest no-overrides emitters.
    Unique sites already use Spell._lock and only touch the store briefly. (3) Registration funnels through
    Creations.add_creation/add_many_creations everywhere EXCEPT the manifest emitter, which writes the two
    dicts directly; its disposal-bearing many append runs with NO lock - a pre-existing first-use race of
    the kind add_many_creations fixed as BUG-073. (4) add_creation takes no lock and relies on the caller's
    store lock. (5) The creation cache persists compiled code, so emitted-source changes need a cache
    version bump (the schema test pins the version table). (6) Hydration/specialization locks are held
    only while compiling, never across an executor call.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:304-345
  - src/melder/aether/conduit/meld/meld.py:1245-1300
  - src/melder/aether/conduit/creations/creations.py:320-416
  - src/melder/aether/conduit/creations/creations.py:429-521
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:497-871
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_no_overrides_codegen_creation_compiler.py:871-1143
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_overrides_codegen_creation_compiler.py:1818-2481
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:1935-2170
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:280-722
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:170-240
  - src/melder/utilities/caching_system/caching_system.py:100-140
  - tests/integration/melder/spellbook/test_cache_schema_version_integration.py:12-44
  IMPACT: The change is mechanical at each site (store lock -> slot guard around check/build; register
    self-locks), plus Creations gains the guard table, a self-locking publish with a cleaned check, and
    guarded purge. The manifest many race is fixed by routing it through add_many_creations.
  NEXT: Write the PLAN (exact files/symbols) and the patch docs, then take a baseline benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T22:49:31Z
  TYPE: PLAN
  CLAIM: Exact change set. Creations (creations.py): add `_slot_guards` + `slot_guard(spell_id)` (lock-free
    get, atomic setdefault on miss); add_creation/add_many_creations take the leaf lock and refuse a
    cleaned store (dispose the orphan, raise RuntimeError); purge takes the slot guard for slotted
    non-unique existences (unique keeps Spell._lock, many none); cleanup keeps `_lock` as a documented
    tombstone and deletes `_slot_guards`; docstrings updated. Door compiler: 8 `X._lock` sites ->
    `X.slot_guard(_spell_id)`. Emitters: every `with creations_i._lock:` that spans a check+construct ->
    `with creations_i.slot_guard(spell_id_i):` in generalized no-overrides, generalized overrides (shape +
    generic), many_only overrides, manifest no-overrides; manifest register -> add_creation /
    add_many_creations. Unique branches unchanged. caching_system.py: version 10
    "creation_slot_build_guards". Tests: deadlock file (7 cases to SAFE, new unique -> many -> per_conduit
    case); cache schema test expected table (+10). conduit_creations/cluster_creations: docstrings only.
  EVIDENCE: tickets/tasks/2026-09-25_implement_creation_slot_build_guards_task.md:1-40
  IMPACT: Bounded, reviewable set; no public API change; warm path untouched.
  NEXT: Patch docs under system_docs/patches/active/creation_slot_build_guards_2026_09_25/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T22:50:59Z
  TYPE: PLAN
  CLAIM: Patch docs written and read in order (architecture -> components -> code description).
    Mapping: architecture invariants (leaf store lock, one build lock per slot) -> creations.py slot_guard,
    self-locking publish, guarded purge -> validated by the 7 flipped regression cases + purge tests;
    component_patch_creation_codegen -> door compiler + 4 emitters -> validated by existing meld/override/
    manifest suites; code_description step 5 (cleaned publish) -> add_creation -> new unit check;
    rollout step 4 -> caching_system version 10 -> cache schema test. Owner behavior note carried: a
    reset racing an in-flight build now publishes into the fresh store.
  EVIDENCE:
  - system_docs/patches/active/creation_slot_build_guards_2026_09_25/architecture_patch.md:1-88
  - system_docs/patches/active/creation_slot_build_guards_2026_09_25/code_description_patch_creations.md:1-58
  IMPACT: Patch-framework entry gate satisfied; implementation may begin after the baseline benchmark.
  NEXT: Baseline benchmark in the VM copy on 3.14.7t and GIL.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T22:52:15Z
  TYPE: MEASURE
  CLAIM: Baseline (current source, VM copy, 2 vCPUs, trivial constructors = worst case for relative lock
    cost), median ns/op on 3.14.7t [GIL]: warm per_conduit meld 343 [313]; many control 439 [399]; lesser
    create+4 cold builds+return 2404 [3473]; spellspace cycle with 4 cold builds 1592 [2921]; purge+rebuild
    per_conduit root 2256 [1943]; purge+rebuild unique 2051 [1799]; 8-thread spellspace cycle 1722 [1420];
    8-thread lesser cycle 3331 [2167]. A second 3.14t run agrees within 3%.
  EVIDENCE:
  - artifacts/creation_slot_build_guards_20260925/bench_before_314t.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_before_314t_run2.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_before_314gil.json:1-45
  - artifacts/creation_slot_build_guards_20260925/slot_guard_bench.py:1-170
  IMPACT: The owner's overhead question gets a same-machine, same-script before/after comparison.
  NEXT: Implement Creations changes (creations.py).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T23:00:54Z
  TYPE: MEASURE
  CLAIM: Implementation applied per the PLAN (8 files in src/, 2 test files). Regression file on the VM
    copy: 12 passed on 3.14.7t (3 repeat runs) and on 3.14.7 GIL, about 2.5s per run (was ~22s of
    deadlock timeouts). Same test file against the pre-change source (HEAD versions of the 7 edited
    src files): 8 failed, 4 passed - the 7 original shapes report MeldDeadlockDetected and the new
    unique -> many -> unique_per_conduit case blocks the competitor at the per-conduit step until
    thread A's gate times out. The new case therefore discriminates old from new locking.
    Remaining `creations._lock` uses in emitters are all leaf (reads under Spell._lock, unique and
    many registration wrappers).
  EVIDENCE:
  - tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py:1-540
  - src/melder/aether/conduit/creations/creations.py:1-1098
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:497-880
  IMPACT: The deadlock is fixed for every pinned shape on both builds.
  NEXT: Full test suite on 3.14.7t (running), then GIL, then the after-benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: MEASURE
  CLAIM: Overhead, same script, median ns/op, 3.14.7t before -> first cut -> final: spellspace cycle
    (4 cold builds) 1596 -> 2264 (+42%) -> 1694 (+6.2%); lesser cycle 2425 -> 3082 -> 2515 (+3.7%);
    purge+rebuild per_conduit root 2227 -> 2537 -> 2376 (+6.7%); warm meld 342 -> 341 (0%); unique purge
    +rebuild -0.7%; 8-thread lesser cycle -7.2%; 8-thread spellspace cycle +5.6%. GIL (vs the stable
    second baseline): lesser +3.4%, spellspace +4.5%, per_conduit purge+rebuild +5.5%, warm -1.9%. First
    cut cost came from the store lock inside add_creation (~58 ns) and slot_guard() calls; primitive
    timings: `with RLock` ~45 ns, method call ~13 ns over an inline dict get. Final: lock-free publish
    for entries without disposal methods, inline guard hit in emitted code. Trivial constructors = worst
    case; ~25 ns per cold slotted build remains, warm path unchanged.
  EVIDENCE:
  - artifacts/creation_slot_build_guards_20260925/bench_before_314t.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_first_cut_314t.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_after3_314t_r1.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_after3_314t_r2.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_before_314gil_run2.json:1-45
  - artifacts/creation_slot_build_guards_20260925/bench_after3_314gil_r2.json:1-45
  - artifacts/creation_slot_build_guards_20260925/prim_bench.py:1-60
  - src/melder/aether/conduit/creations/creations.py:455-531
  IMPACT: Answers the owner's overhead concern with measurements: single-digit percent on cold builds
    only, none on warm melds, lower contention under threads.
  NEXT: Record suite results; move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: MEASURE
  CLAIM: Suites on the VM copy with final code, 3.14.7t and 3.14.7 GIL: tests/unit/melder/aether 4124
    passed; tests/component 1998 passed; tests/experimentation 252 passed; remaining tests/unit: 21
    failures, the identical set the pre-change source produces (environment: architecture_and_design
    docs tool, build-asset/version stamping; github_workflows and llm_support not collectable in the VM);
    tests/integration 1922 passed on 3.14t with failures only in
    test_conduit_integration_concurrency.py, which fails intermittently on the PRE-change source too
    (same RuntimeError "Cannot build CreationContext before spell_codegen_creation exists"; 1-5 of 18 per
    run on both sources). Test doubles updated for the new store surface: codegen compilers core stub,
    experimentation fresh-creations probe; purge component tests now observe the slot guard.
  EVIDENCE:
  - tests/unit/melder/spellbook/spell_compiler/test_codegen_creation_compilers_core.py:441-470
  - tests/component/melder/aether/conduit/test_conduit_component_purge.py:580-735
  - tests/experimentation/test_forced_phase10_phase11_creation_context_comparison_harness.py:88-150
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-354
  IMPACT: No regression attributable to the change; one pre-existing concurrency flake found.
  NEXT: Owner review of the diff and numbers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-25T23:28:41Z
  TYPE: RISK
  CLAIM: Pre-existing, unrelated to store locks: concurrent first melds sometimes raise "Cannot build
    CreationContext before spell_codegen_creation exists" (test_conduit_integration_concurrency.py, both
    builds, before and after this change). A context-build race on first resolution; not investigated.
  EVIDENCE: tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-354
  IMPACT: A real user-facing race on cold concurrent melds; separate lane.
  NEXT: Owner decides whether to open an investigation task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-25T23:47:39Z
  TYPE: DECISION
  CLAIM: Owner accepted the implementation ("I accept it, looks good"). Closure: patch deltas merged into
    src_architecture (Operational Invariants, Meld sequence, Failure Modes, C1, handoff) and src_components
    (Creations and SpellSpace, Meld Resolution Runtime incl. the corrected Meld RLock claim, Meld Execution
    Flow, purge flow, Spellbook cache note, C1, handoff); both indexes regenerated and checked; 9 graph
    descriptors refreshed (authored prose updated for Creations and the door compiler; 8 nodes accepted
    after reading), src_graph reassembled; patch docs archived to system_docs/patches/completed/creation_slot_build_guards_2026_09_25; next-release note added.
  EVIDENCE:
  - system_docs/src_architecture.md:839-852
  - system_docs/src_components_index.md:1-40
  - system_docs/patches/completed/creation_slot_build_guards_2026_09_25/architecture_patch.md:1-88
  - ../release_docs/next_version_release.md:5-29
  IMPACT: Work is closed; remaining follow-ups are owner-selected (flake investigation, packaged assets).
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done 2026-09-25T23:47:39Z. Build-once exclusion lives in per-slot guards (`Creations.slot_guard`; unique keeps Spell._lock);
the store lock is a leaf; cache generation 10. Owner accepted. Canonical docs, graph and the next-release
note carry the change; patch docs archived under system_docs/patches/completed/. Open follow-ups for the
owner: the pre-existing concurrent-context flake (RISK note), packaged hardcopy document assets not rebuilt,
next_version_release.md header still reads 0.2.51 while __version__ is 0.2.52.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
