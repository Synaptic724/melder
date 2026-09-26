

# Task: Door-called first builds take their slot's build lock once, not twice

## Metadata
- Task ID: TASK-2026-09-26-remove-nested-slot-guard-take
- Story: STORY-2026-09-26-gauntlet-runtime-speed
- Status: in_progress
- Owner: user
- Agent Name: melder_2
- Priority: p1
- Created: 2026-09-26T21:38:23Z
- Updated: 2026-09-26T22:15:30Z

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
- [ ] Promote docs (src_architecture, src_components, indexes); refresh graph descriptors; artifact disposition.
- [ ] Owner Windows run and acceptance.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

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
- Not run: the owner's Windows gauntlet.

## Risks / Rollback Notes
- A caller that reaches the door-held plan without the door's guard would lose build-once for the root.
- The cluster route resolves its store twice (door and plan); a leader change between the two would publish into a
  store whose guard is not held.
- The same-thread recheck after the children must stay, or a nested meld that publishes the root would be
  overwritten.
- Rollback: restore the previous emission; the version notch cold-resets any cached payloads.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No lock removed on a docstring's word: the source and concurrency tests decide.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/gauntlet_runtime_speed_20260926/nested_slot_guard/
  - system_docs/patches/active/nested_slot_guard_2026_09_26/
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
  EVIDENCE: tickets/tasks/2026-09-26_remove_nested_slot_guard_take_task.md:161-197
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

## Context / Handoff Summary
Opened on the owner's go-ahead (~21:37Z). Safe shape only: the door keeps its guard, and the plan it calls stops
taking that guard a second time. First step: read the code being changed and its callers.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
