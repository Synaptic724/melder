

# Task: Door-called first builds take their slot's build lock once, not twice

## Metadata
- Completed: 2026-09-26T23:01:16Z
- Closure Basis: owner turn-in in chat (~22:58Z): "Turn in both (Recommended)" for the nested slot-guard
  implementation and the build-locks discovery, with P4, P1 and the tail attribution selected for turn-in in
  the same answer; then "then please remake the assets and I'll call it".
- Summary: Door-called first builds of unique_per_conduit and spellspace roots take their build lock once
  (0.2.73): VM -3.3%/-3.6% per worker cycle, suites and soak green; docs, graph, assets and LLM bundles
  current at 0.2.74; the owner's 22:47Z Windows run is the best same-run result vs dishka (0.919x).
- Task ID: TASK-2026-09-26-remove-nested-slot-guard-take
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: done
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T21:38:23Z
- Updated: 2026-09-26T23:01:16Z

## Objective
When a creation-context door builds a slotted object for the first time, it holds the slot's build lock (the
store's slot guard, or the Spell lock for unique) across its recheck and the executor call. The site-plan executor
then takes the same lock again, re-entrantly, in its root-site miss. Remove that second take so a door-called first
build acquires its build lock once. Nothing observable may change: build-once, purge waiting for in-flight builds,
the cleaned-store refusal, lock order, the exact `created` flag of the hook lanes, and the same-thread recheck after
the children are built all stay. Target: about 0.3 us per worker cycle on the VM (-4%), measured by the discovery
prototype (tickets/tasks/2026-09-26_spellspace_build_locks_task.md:170-194).

## Ticket Contract
- ENTRY_GATE: owner go-ahead (~21:37Z): "just do it, melder_0 is done go and finish your work implement your 4%
  savings and implement everything you need to do, make it safe"; the discovery DECISION_REQUEST
  (tickets/tasks/2026-09-26_spellspace_build_locks_task.md:283-302).
- EXECUTION_BOUNDARY: patch docs before code. Code and tests are written and validated on the VM copy, then applied
  byte-identically to the device tree. Version notch above 0.2.72 and a release note; system docs and indexes
  promoted; graph descriptors refreshed for touched nodes. Artifacts under
  artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/.
- DEPENDENCIES: melder_0 owns the site-plan lowering, the door compiler and the family hydrators (NOTICE before any
  device write); melder_0's 0.2.72 lane (M0-49: assets and LLM bundles rebuilt after its docs); owner Windows run.
- EXIT_GATE: suites green on 3.14t (PYTHON_GIL=0 and 1) and the GIL build, new tests included; 30k soak flat; VM A/B
  shows the gain; byte-identical device apply; docs promoted; the owner accepts after a Windows run.
- FAILURE_ESCALATION: BLOCKER if any caller can reach the door-held plan without holding the root's build lock and
  no clean emission avoids it; CONFLICT if another agent has in-flight edits to the same files.

## Scope Boundaries
- In scope: the normal (empty key set) site plan of the many_only and generalized families when a door calls it;
  the binding of that plan to the door; tests; docstrings; patch docs; system docs.
- Out of scope: override key-set plans and override doors (unless they are the same code path); other families'
  executors; dropping the door's own guard (unsafe in hook lanes); any spellspace thread rule.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: The owner approved implementation and asked for a safe shape; the door keeps its guard.
- from_state: in_progress
- to_state: review
- transition_reason: (2026-09-26T22:41:40Z) The notch pipeline is complete (Notes 22:15:30Z to 22:41:30Z);
  the owner's Windows gauntlet run and acceptance remain.
- from_state: review
- to_state: done
- transition_reason: Owner turn-in, 2026-09-26T23:01:16Z; see the Closure Basis.

## Steps / Checklist
- [x] Read the code being changed in full (site-plan lowering, site-plan runtime, family hydrators, door routes,
      creation context) and every caller that can reach the normal plan (fast door, SpellSpace warm lane, override
      doors); FACT note.
- [x] Choose the emission shape (one door-held plan, or a guarded and a door-held variant); DECISION note.
- [x] Patch docs (architecture, component, code description) with ticket links; consumption mapping note.
- [x] Implement on the VM copy (refreshed to 0.2.72) with rich docstrings; tests for build-once under a race, the
      hook lanes' created flag, the same-thread recheck, and purge against a first build.
- [x] Suites on 3.14t (PYTHON_GIL=0 and 1) and the GIL build; 30k soak; VM A/B with probe_steps3.
- [x] NOTICE melder_0; byte-identical device apply; version notch and release note.
- [x] Promote docs (src_architecture, src_components, indexes); refresh graph descriptors; artifact disposition
      (applied at turn-in: the patch lane moves to patches/completed, the artifacts are retained).
- [x] Owner Windows run and acceptance.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- A door-held normal site plan without the nested root-site guard, bound only where the door holds that guard.
- Tests, patch docs, promoted system docs, release note, version notch.

## Files / Paths Impacted
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/
  generalized_hydrator.py
- New tests (unit emission, integration concurrency); src/melder/__version__.py and the release note; system docs,
  indexes and graph descriptors for the touched nodes.

## Validation
- VM copy, 3.14t (PYTHON_GIL=0 and 1) and the GIL build: suites green, new tests included; 30k soak flat;
  probe_steps3 A/B -3.3% (1 thread) and -3.6% (2 threads) per worker cycle (Notes 22:03:17Z, 22:07:25Z).
- Device tree at 0.2.74 (checksum-equal copy with the rebuilt assets): 42 suite runs green on 3.14t (gil 0 full
  set, gil 1 subset) and the GIL build (subset); build assets --check and LLM bundles --check OK (Note 22:41:30Z).
- Owner's Windows gauntlet, 22:47Z on 0.2.74: see the MEASURE note of 22:55:20Z.

## Risks / Rollback Notes
- A caller that reaches the door-held plan without the door's guard would lose build-once for the root.
- The cluster route resolves its store twice (door and plan); a leader change between the two would publish into a
  store whose guard is not held.
- The same-thread recheck after the children must stay, or a nested meld that publishes the root would be
  overwritten.
- Rollback: restore the previous emission; the version notch cold-resets any cached payloads.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No lock removed on a docstring's word: the source and concurrency tests decide.

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
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/
  - system_docs/patches/completed/nested_slot_guard_2026_09_26/
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: task closure; the owner confirms retention.

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
- DATETIME: 2026-09-26T21:38:23Z
  TYPE: PLAN
  CLAIM: Order of work: read the code being changed and every caller of the normal plan; choose the emission shape;
    patch docs; implement and test on the VM copy; suites, soak, A/B; NOTICE and byte-identical apply; notch,
    release note, docs, graph. The door keeps its guard in every lane.
  EVIDENCE:
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:235-281
  - tickets/tasks/2026-09-26_spellspace_build_locks_task.md:283-302
  IMPACT: Implementation is owner-approved; the safe shape is fixed, the file list waits on the read.
  NEXT: Read site_plan_lowering.py in full.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:38:34Z
  TYPE: FACT
  CLAIM: M0-49 consumed (melder_0, 21:36:14Z). The device tree is at 0.2.72: compiler passes on the meld-time path
    iterate a copy of spellbook._spell_id_pool. The system-document view fixtures leave a live Aether, and the
    registration-guard test sets up its own. Assets and LLM bundles are rebuilt for 0.2.72 after melder_0's docs.
    This change notches above 0.2.72.
  EVIDENCE:
  - tickets/tasks/2026-09-26_snapshot_phase5_live_spell_pool_task.md:1-20
  - src/melder/__version__.py:12-12
  IMPACT: The VM copy must be refreshed to 0.2.72 before any change. The device apply waits until melder_0's
    0.2.72 asset rebuild has landed, so the notch lands after it.
  NEXT: Read site_plan_lowering.py in full.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T21:46:50Z
  TYPE: FACT
  CLAIM: Who reaches the normal plan, and under which lock. Read in full: site_plan_lowering.py,
    site_plan_override_runtime.py and generalized_hydrator.py; the door routes in creation_runtime_door_compiler.py.
    - The normal plan (SitePlanOverrideRuntime.execute_normal) is reached only through doors that hold the root's
      build lock. The no-overrides hooks and instance doors hold it (the route store's slot guard, or the Spell lock
      for unique). The override door holds the same guard and reaches the plan through its dispatcher fallbacks
      (overrides None, or a key set with no winner). The opt-in specializer deopts into it from inside a door compiled
      for the same route. The many_only family's roots are all many and take no guard. Tests call it directly,
      single-threaded.
    - For the "unique_per_conduit" and "spellspace" routes, the door and the plan read the root's store from the same
      meld attribute (_conduit_creations, _spellspace_creations). Each is assigned once in Meld.__init__, and no user
      code runs between the two reads, so the plan's root guard is the RLock the door already holds. "lineage" is
      repointed at lesser link and upgrade; "cluster" re-resolves its store per call; "unique" holds the Spell lock
      while the plan may take the owner store's slot guard. None of those three is provably the same lock.
    - The route family comes straight from the root spell's existence. Emitted plan code is cached in process only,
      and the cached manifests do not encode the lock shape, so no creation-cache generation bump is needed.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:182-205
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_override_runtime.py:322-384
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:267-411
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/hydration/generalized_hydrator.py:622-649
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-694
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:697-881
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1276-1377
  - src/melder/aether/conduit/meld/meld.py:305-320
  - src/melder/aether/conduit/conduit.py:383-383
  - src/melder/aether/conduit/conduit.py:2215-2215
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:127-150
  - src/melder/aether/spellbook/spell_compiler/executor_code_cache.py:26-45
  IMPACT: The root guard can be dropped from the normal plan exactly where the door holds the same lock: the
    unique_per_conduit and spellspace routes, which are the per-scope builds the gauntlet pays for every cycle.
    Unique, lineage and cluster roots are built once per process, lineage or cluster, so leaving them alone costs
    nothing measurable.
  NEXT: DECISION note on the emission shape and file list; then patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:46:50Z
  TYPE: DECISION
  CLAIM: Emission shape and files.
    - SitePlanLowering.emit and SitePlanEmission take door_route_key (default None). In normal mode only, the root
      site's miss omits its "with guard:" line when (door_route_key, root existence) is ("unique_per_conduit",
      unique_per_conduit) or ("spellspace", unique_per_spell_space). The recheck under the door's lock, construction,
      publication and every other site's guard are unchanged.
    - SitePlanOverrideRuntime takes door_route_key (default None) and passes it to the normal plan only; override
      key-set plans keep their root guard. The generalized hydrator passes its manifest route key. The many_only
      hydrator is unchanged (all-many roots, no guard).
    - With no route key, or any other route, the guard stays. The safe behaviour is the default for any future caller.
    - Unchanged: the door compiler, creations.py, override plans, the specializer.
    - Tests are new files only: a unit test of the emitted lock discipline (door-held root, kept guards, the recheck)
      and an integration test of concurrent first melds (conduit and shared spellspace) with build-once and exact
      created-hook counts.
  EVIDENCE: tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md:168-204
  IMPACT: Three production files, all melder_0's lane; NOTICE M2-8 before any device write.
  NEXT: Patch docs under system_docs/patches/active/nested_slot_guard_2026_09_26/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T21:48:42Z
  TYPE: PLAN
  CLAIM: Patch docs written and consumed in order (architecture, component, code description); the mapping is
    patch section -> implementation -> validation.
    - I1, I3 -> SitePlanEmission gets the eligibility flag; _emit_miss drops the root guard only when it is set
      -> unit tests: door-held root without a guard; lineage, cluster, unique, no-route roots with one.
    - I2 -> the root recheck stays in the door-held miss -> unit: a root published during a child build is
      returned; integration: nested same-thread override meld.
    - I4 -> SitePlanOverrideRuntime forwards door_route_key to the normal plan only; the generalized hydrator
      passes its route key -> unit: override plans keep the root guard; call sites reviewed (FACT 21:46:50Z).
    - I5 -> no other emission change -> integration: concurrent first melds (conduit, shared spellspace) build
      once and fire created hooks once; lock-order deadlock and purge suites.
    No unknowns remain in the patch docs for the target code path.
  EVIDENCE:
  - system_docs/patches/active/nested_slot_guard_2026_09_26/architecture_patch.md:1-66
  - system_docs/patches/active/nested_slot_guard_2026_09_26/component_patch_spellcompiler_site_plans.md:1-47
  - system_docs/patches/active/nested_slot_guard_2026_09_26/code_description_patch_site_plan_root_guard.md:1-37
  IMPACT: The patch-framework entry gate is met; implementation may start on the VM copy.
  NEXT: Edit site_plan_lowering.py in work72.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:56:48Z
  TYPE: DECISION
  CLAIM: Implemented on the VM copy (work72 = device 0.2.72 plus the change), per the patch docs.
    - site_plan_lowering.py: emit and SitePlanEmission take door_route_key. The class constant
      DOOR_HELD_ROOT_EXISTENCE maps "unique_per_conduit" -> unique_per_conduit and "spellspace" ->
      unique_per_spell_space. _emit_miss leaves out the root's "with guard" only when the flag is set and keeps the
      recheck. A door route key outside normal mode raises RuntimeError.
    - site_plan_override_runtime.py: door_route_key (default None) goes to the normal plan only.
    - generalized_hydrator.py: _build_site_plan_runtime(route_key=...) passes it. The file's CRLF line endings are
      preserved.
    - Emitted normal plans: with "spellspace" and a spellspace root, the root miss has no guard and its child
      misses keep theirs. With no route, or a mismatched one, the source is unchanged.
    - New tests: tests/unit/.../shared_assets/test_site_plan_door_held_root.py (15; 14 red on the base tree, where
      the keyword is unknown and the root takes its guard) and
      tests/integration/melder/conduit/test_conduit_integration_door_held_first_build.py (5; green on base and
      change). Their spells run through the site-plan executor with the door-held root (checked by inspecting the
      hydrated misses).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/src.diff:1-355
  - system_docs/patches/active/nested_slot_guard_2026_09_26/code_description_patch_site_plan_root_guard.md:1-37
  IMPACT: Ready for validation. Not run yet: full suites, soak, A/B.
  NEXT: Run the suites on work72 and base72 (3.14t gil 0 and 1, GIL build) in the background and compare.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T21:57:59Z
  TYPE: FACT
  CLAIM: M0-50 consumed (melder_0, 21:49:31Z, re M2-8). 0.2.72 is complete on the device: src fix, canonical
    docs, graph, build assets and LLM bundles. melder_0 has no edits in flight on the three files and only edits
    tests_architecture/tests_components now, which are not packaged and not in the asset fingerprints. The device
    copies of the three files are byte-identical to the base of this change (sha256). The VM trees predate his
    asset rebuild: only src/melder/_build_assets manifests and payloads differ.
  EVIDENCE:
  - tickets/tasks/2026-09-26_snapshot_phase5_live_spell_pool_task.md:227-248
  - tickets/tasks/2026-09-26_snapshot_phase5_live_spell_pool_task.md:253-264
  IMPACT: Device apply is unblocked. The notch pipeline for 0.2.73 follows his 0.2.72 sequence: canonical docs and
    C1 re-measure, indexes --check, graph extract/accept/assemble, the asset runner on a work copy carrying
    context_compass/system_docs and then on the device (byte-equal, CRLF kept), and LLM bundles with
    --include-untracked.
  NEXT: Finish the suite comparison, refresh both VM trees from the device (assets), then the soak and A/B.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:03:17Z
  TYPE: MEASURE
  CLAIM: Suites on the VM copy with the change (work72) are green on free-threaded 3.14t with PYTHON_GIL=0 and 1
    and on the GIL build: spellbook unit (2194) / component (776) / integration (583), conduit integration (273,
    the 5 new included), multithreading (42, lock-order deadlock scenarios included), aether unit/component/
    integration, utilities, crystallizer, mutation_research and live_sim. The only failures are the 3 build-asset
    tests (live-version stamp, system-document entries), and they fail identically on the unchanged copy: both copies
    predate melder_0's 0.2.72 asset rebuild. The 15 new unit tests fail on the unchanged tree (keyword unknown, root
    takes its guard); the 5 integration tests pass on both, as regression guards should.
  EVIDENCE: artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/suites_vm.txt:1-46
  IMPACT: No behavioural regression across the suites that cover melds, doors, purge, pools and lock order.
  NEXT: 30k soak (base and change), then the probe_steps3 A/B at 1 and 2 threads.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:07:25Z
  TYPE: MEASURE
  CLAIM: The implemented change saves what the prototype did. probe_steps3 worker_a, 11 interleaved rounds per
    tree, medians of per-run 95%-trimmed means:
    - 1 thread: steps 7,071 -> 6,839 ns (-232, -3.3%), wall/cycle 8,413 -> 8,182 (-2.7%). First builds: outer_1st
      -78, marker_1st -72, root_build -87. Lifecycle unchanged (2,542 -> 2,533).
    - 2 threads: steps 9,651 -> 9,299 (-352, -3.6%), wall 11,472 -> 11,230 (-2.1%). First builds -121/-96/-113.
    - Per first build this matches the prototype (-77/-73/-89 at 1 thread).
    30k soak (gauntlet-shaped, 3 new threads per iteration): the change's rerun is flat. worker_a medians are
    11,623/11,662 ns over the first and last 10 windows (base 12,211/12,247), and RSS stays within base's range
    (max 83.3 vs 87.9 MB). The first change run stepped up at window 21 in every lane and in wall/iter at once. That
    was environmental, and it did not recur.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/ab_steps3_vm.txt:1-45
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/soak_30k_vm.txt:1-100
  IMPACT: VM gates met: suites green, soak flat, gain confirmed. Owner's Windows run is the authoritative number.
  NEXT: NOTICEs for the 0.2.73 notch; byte-identical device apply of the three src files and two test files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:15:30Z
  TYPE: FACT
  CLAIM: Applied to the device tree byte-identically at 22:07Z (sha256 equal to the validated VM copy, after a check
    that the device copies still equalled the validated base): site_plan_lowering.py (1501 lines),
    site_plan_override_runtime.py (405) and generalized_hydrator.py (758, CRLF kept), plus the two new test files.
    NOTICEs M2-9, M2-10 and M2-11 went to melder_0, melder_1 and fable_0 (22:07:45-47Z). __version__ is 0.2.73
    (CRLF kept). The release note carries the 0.2.73 header, a "Faster first builds of per-conduit and SpellSpace
    objects" section and the packaging bullets; the 0.2.73 asset and LLM-bundle line is written ahead of that rebuild.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/apply_nested.py:1-36
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:98-110
  - release_docs/next_version_release.md:560-583
  IMPACT: The change is live in the device tree at 0.2.73. Open gates: canonical docs and indexes, graph, build assets
    (their manifests stamp the version, so the build-asset tests fail until the rebuild), LLM bundles, the owner's run.
  NEXT: Promote src_architecture.md (invariant, meld step 4, C1 re-measure, sources, handoff), then src_components.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:24:10Z
  TYPE: FACT
  CLAIM: Canonical docs promoted, then re-read against the source (door routes, SitePlanEmission, the runtime and
    the hydrator, Meld.__init__ store attributes, Creations.cleanup/add_creation, the specializer's deopt).
    - src_architecture: a new operational invariant "Door-held first builds (2026-09-26, 0.2.73)", one added
      sentence each in Meld Resolution step 4 and the "Override key-set plans" invariant, C1 re-measured
      (site_plan_lowering 1435 -> 1501, site_plan_override_runtime 384 -> 405, verified 22:18:53Z), the generalized
      hydrator added to Information Sources, and a handoff entry.
    - src_components: "Door-held roots" under Slot build guards (Creations and SpellSpace), a Meld Resolution
      concurrency bullet, the SpellCompiler "Door-held root" bullet, the same C1 re-measure, and a handoff entry.
      generalized_hydrator.py is in no Key Files list, so it has no core C1 entry; it was already a source.
    - Both indexes regenerated; --check OK (3044 and 9841 lines). Content preservation: the only baseline lines
      missing afterwards are the six re-measured C1 fields (end_line, loc, verified_at of the two entries).
      Package-path hits are 9 and 11 before and after (pre-existing, same lines), with no absolute paths. Citation
      bounds recipe: 0 problems. The rubric was not re-scored for this additive promotion.
  EVIDENCE:
  - system_docs/src_architecture.md:699-703
  - system_docs/src_architecture.md:875-890
  - system_docs/src_architecture.md:968-981
  - system_docs/src_architecture.md:2800-2802
  - system_docs/src_components.md:2724-2729
  - system_docs/src_components.md:3061-3064
  - system_docs/src_components.md:3558-3568
  - system_docs/src_components.md:9552-9555
  IMPACT: Docs describe 0.2.73. The graph still has the pre-change line numbers for the three files, and the build
    assets embed the docs, so both must be rebuilt next.
  NEXT: extract_graph.py --strict; re-read and accept the changed nodes; assemble; --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:27:30Z
  TYPE: FACT
  CLAIM: Graph refreshed for 0.2.73. extract_graph.py --strict (3.14.7) rc 0 with no skipped files. The node changes
    in this lane's files: SitePlanEmission (moved 715 -> 731, new span), SitePlanLowering and SitePlanOverrideRuntime
    (new spans), GeneralizedHydratedExecutors (line only). The three stale class nodes were re-read against the
    source, each got one responsibility for the door route key (SitePlanEmission also owns
    _root_guard_held_by_door), and they were accepted. Census stale 199 -> 196; assemble and --check are clean (27517
    lines, 584 sections). Other descriptor changes: source hashes of __version__ and the nine build-asset modules
    (changed by the 0.2.72 asset rebuild after that graph pass; they lag again after this one). Seven melder_0
    descriptors that the extractor only re-serialized (indent 2 -> 1, JSON-equal) were restored byte for byte.
  EVIDENCE:
  - system_docs/src_graph.md:7856-7961
  - system_docs/src_graph.md:7963-8023
  - system_docs/src_graph.md:8468-8530
  - system_docs/src_graph_index.md:201-214
  IMPACT: The graph describes 0.2.73. The build assets embed src_architecture, src_components and the graph, so they
    are rebuilt from these documents next.
  NEXT: Asset runner on a fresh work copy with context_compass/system_docs, then on the device (byte-equal, CRLF kept).
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:31:00Z
  TYPE: FACT
  CLAIM: M0-51 and M0-54 consumed (melder_0, 22:15:35Z and 22:18:01Z). tests_architecture and tests_components
    already list the two new test files (the Spellbook Compiler Unit Cluster and the Conduit Integration Cluster),
    so no tests-doc edit is needed in this lane. Since 22:18Z __version__ is 0.2.74 (test maps and the
    order-independent guard test, no src change). The release header and asset line say 0.2.74, and the 0.2.73
    section stays. Owner, via melder_0's closure note: "I'll regen the assets with the other agent". So this lane
    rebuilds the build assets and LLM bundles once, stamped 0.2.74, covering both notches.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_refresh_tests_system_docs_task.md:250-264
  - tickets/tasks/completed/2026-09-26_refresh_tests_system_docs_task.md:266-272
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:583-589
  IMPACT: The asset runner stamps v0.2.74; its --check expects 0.2.74.
  NEXT: Asset runner on the w73 work copy (device src at 0.2.74 plus system_docs), then the build-asset tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:31:00Z
  TYPE: RISK
  CLAIM: An empty .git/index.lock (0 bytes, 22:21:52Z) sits on the device beside an index rewritten at 22:21:50Z,
    four minutes after the owner's 22:17Z commit. This lane ran no git command in that window, and neither the
    graph nor the index tools call git. The VM cannot remove it (the connected folder refuses deletes). If no git
    process owns it, the owner's next git write fails until it is deleted on Windows.
  EVIDENCE: attention_board.md:146-149
  IMPACT: Could block the owner's commits; nothing in this lane depends on git.
  NEXT: Report it to the owner in the hand-over; keep running git only read-only with GIT_OPTIONAL_LOCKS=0.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T22:34:30Z
  TYPE: MEASURE
  CLAIM: Build assets rebuilt at v0.2.74. The runner ran on w73 (device src at 0.2.74 plus system_docs, checksum
    compared): agent documentation 460 entries, bind guard 619 (unchanged), system documents 4 entries. Outputs were
    converted to CRLF like the committed files, and --check is OK. On w73 these pass on 3.14t (gil 0) and the GIL
    build: tests/unit/melder/build_assets 116, test_package_version_metadata 4, test_system_documents 25,
    test_system_document_view 84. On the device the runner wrote the first two manifests and the section index,
    then failed in the system-documents builder: write_payloads unlinks the old payloads first, and the connected
    folder refuses deletes (PermissionError; nothing was deleted and no temporary file remained). The remaining five
    outputs were copied from w73 by overwrite. All eight device files are byte-equal to w73 and CRLF, and --check
    is OK (v0.2.74, schema 2.0.0, key match). A backup of the previous device files is in the VM. Content moved:
    the version stamp and source keys, the architecture and components payloads, their section index, and the
    adjacency rows for SitePlanEmission and GeneralizedHydratedExecutors.
  EVIDENCE:
  - src/melder/_build_assets/_build_asset_runner.py:246-362
  - src/melder/_build_assets/_system_documents/_builder.py:542-626
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:1-60
  IMPACT: Assets carry the 0.2.73 docs and graph at 0.2.74. As after 0.2.72, the graph descriptors of the nine
    asset modules and __version__ lag one rebuild (their hashes are embedded in the graph payload).
  NEXT: LLM bundles with --include-untracked, then --check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T22:41:30Z
  TYPE: MEASURE
  CLAIM: LLM bundles and the final suites at 0.2.74.
    - LLM bundles: llm_support/_builder.py --include-untracked with GIT_OPTIONAL_LOCKS=0 wrote src (576 files),
      tests (1018) and other (370) plus manifest.json. --check is OK both with and without --include-untracked:
      no untracked file exists outside context_compass, and the owner's 22:17Z commit already tracks the new tests.
    - Final suites on w73, a checksum-equal copy of the device tree at 0.2.74 with the rebuilt assets: 42 suite runs,
      all rc 0. On 3.14t PYTHON_GIL=0, the full set: spellbook unit, component and integration; conduit
      integration; multithreading; aether unit, component and integration; utilities; crystallizer; mutation
      research; live_sim; the top-level unit tests; build assets. On PYTHON_GIL=1 and the GIL build, the
      concurrency subset plus the top-level unit tests and build assets. The three build-asset tests that failed on
      the stale 0.2.72 copies now pass (260 passed, 1 skipped).
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/suites_final_0274_vm.txt:1-51
  - llm_support/manifest.json:1-20
  IMPACT: The notch pipeline is complete: code, tests, soak, A/B, device apply, 0.2.73 docs, graph, assets and LLM
    bundles (stamped 0.2.74 with melder_0's notch). Only the owner's Windows gauntlet run and acceptance remain.
  NEXT: Hand over to the owner: summary, VM numbers, the index.lock RISK, and a request for the Windows run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T22:55:20Z
  TYPE: MEASURE
  CLAIM: Owner Windows run at 22:47Z: 30k iterations, 3 threads, free-threaded, tree at 0.2.74 with the change in.
    Same-run ratios, with the afternoon 30k runs on 0.2.68 and 0.2.70 in brackets:
    - hot_scopes/s melder/dishka 0.919 (0.859, 0.857), the best so far; per-iteration time 1.09x dishka (1.16x, 1.17x).
      melder/DI is 0.910 (0.929, 0.919), inside its afternoon range.
    - Request-scope part of each cycle (the harness's "active" figure, request_total only), melder/dishka by lane:
      request 1.064 (0.997, 1.035), worker_a 0.934 (0.852, 0.905), worker_b 1.134 (1.012, 1.073).
    - Whole cycles (outer scope included; 1 us print resolution): melder 20/15/15 us, dishka 19/13/14 (afternoon
      20/15/14 vs 18/12/12). Melder's outer-scope create and cleanup still cost more per cycle (2+2 us vs 1+0).
    - Threaded-phase gap +0.130 ms per iteration: about +0.03 in the lane that bounds the iteration (worker_b, 30
      cycles) and about +0.10 outside the measured cycles (lane wake-up and loop, thread exit and join), each +/-0.03.
      Afternoon: +0.06 in cycles and +0.115 to +0.119 outside.
    - Caveat: this run is slower and noisier for every library. Dishka's threaded phase is 1.101 ms (0.962 at
      20:05Z) and its iteration p99 is 4.8 ms (1.9), and the outside-cycle gap, which this change cannot touch, also
      narrowed. The run agrees with the VM's -3.3% to -3.6% per worker cycle but cannot isolate an effect that size.
    - Melder max iteration 13.4 ms (turn-0 first use, as attributed); setup 203 ms; end cleanup 19.3 ms.
  EVIDENCE:
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_2247_30k_0274.txt:41-54
  - artifacts/gauntlet_runtime_speed_20260926/owner_run_20260926_2247_ratios.txt:1-63
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1244-1330
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:1376-1397
  IMPACT: The owner run supports the change and shows no regression. Most of the remaining gap to dishka sits outside
    the scope cycles (the tail task's thread-exit attribution); inside them it is Melder's outer-scope lifecycle.
  NEXT: Owner acceptance and turn-in of this task and the build-locks discovery task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T23:01:16Z
  TYPE: DECISION
  CLAIM: Closed on the owner's turn-in (see the Closure Basis); acceptance given.
  EVIDENCE: tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md:6-12
  IMPACT: The ticket moves to its completed folder; board and artifact rows are synced in the same pass.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
In review. Done: a CreationContext door keeps its root's build lock, and for unique_per_conduit and
unique_per_spell_space roots the normal site plan it calls no longer takes that lock a second time. Other
lifetimes, child sites and override plans are unchanged. Code and tests are applied byte-identically and
committed by the owner (22:17Z). __version__ went 0.2.72 -> 0.2.73, and melder_0's notch took it to 0.2.74. The
release note has its own section. src_architecture and src_components are promoted with indexes, the graph is
accepted and assembled, and the build assets and LLM bundles are rebuilt at 0.2.74. VM: -3.3% (1 thread) and
-3.6% (2 threads) per worker cycle, soak flat, suites green. Owner's Windows run (22:47Z, 0.2.74): best same-run
ratio vs dishka so far (hot_scopes/s 0.919x), consistent with the gain; that run was noisy. Open: owner acceptance;
at turn-in the patch lane moves to patches/completed. RISK: an empty .git/index.lock (22:21:52Z) not made by this
lane.
Closed 2026-09-26T23:01:16Z on the owner's turn-in. Patch lane archived to
system_docs/patches/completed/nested_slot_guard_2026_09_26/.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
