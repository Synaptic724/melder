# Story: parked_versions_wired_at_conjure - a version parked before conjure melds after a notch; cache generation 21

- Completed: 2026-10-16T12:17:31Z
- Summary: landed 0.2.8248 - conjure stamps every version staged with `bind_inactive` before it, so the version melds
  after a notch for every existence; creation cache generation 21; the missing-pool message without the pre-conjure
  cause; `ManagedSpellLease` checked as built. Whole tree green in both GIL modes; release-note section "A version
  staged before `conjure` melds after a notch" (its example run); rebuild checks OK. Accepted by the owner with the
  epic (2026-10-16).

## Metadata
- Story ID: STORY-2026-10-16-parked_versions_wired_at_conjure
- Epic: EPIC-2026-10-14-managed_spell_quantity (tickets/epics/completed/2026-10-14_managed_spell_quantity_epic.md); story 8, the
  owner's follow-ups of 2026-10-16
- Status: done
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-16T00:52:02Z
- Updated: 2026-10-16T12:17:31Z

## User Narrative
As an agent staging the next version of a spell with `bind_inactive`, I want it to meld after a notch whether I staged
it before or after conjure, so that the order of my setup calls does not decide whether my world works.

## Value / MRP Alignment
A staged version is structure the Book owns, and conjure must wire every version it owns - as the comment in
`Spellbook.bind_inactive` already says it does. The fix is one loop at conjure. The cache generation moves to 21 so
bundles written before the managed codegen are retired explicitly (owner, 2026-10-16).

## Ticket Contract
- ENTRY_GATE: melder_1 reports its meld_contract_scan landing - it holds spellbook.py, transfer_of_ownership.py, five
  test files, the release note, the next notch, the rebuild and the system docs for that landing (the epic's DECISION
  note of 2026-10-16T00:21:04Z); then a component patch and the mapping note before the first `src/` edit.
- EXECUTION_BOUNDARY: `SpellbookCreationSystem.define_conduit_into_spells` (conjure's owner wiring) and whatever U12
  shows the post-conjure path also does; `CachingSystem` generation history (21); new unit and integration tests;
  src_architecture, src_components, the tests docs, their indexes and the graph; README or docs lines that tell users
  to stage versions after conjure; the release note; one notch; the rebuild last.
- DEPENDENCIES: melder_1's landing (TASK-2026-10-15-make_meld_state_checks_follow_spell_state); S1-S7.
- EXIT_GATE: a version parked before conjure melds after a notch for unique, unique_per_conduit, many and
  managed_spell_quantity (and the existing-object and callable families, per U12) exactly as one parked after conjure
  does; cache generation 21 retires older bundles; green in both GIL modes; non-managed emitted plans byte-identical;
  docs, release note, notch and both rebuild checks OK; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if wiring parked versions at conjure changes anything beyond them (an active
  spell's behaviour, a spell id, a record); CONFLICT if the post-conjure `bind_inactive` path and the conjure path
  disagree on what wiring a parked version means (U12).

## Requirements (Functional)
- Conjure wires every parked version the Book owns that has no owner yet, exactly as a post-conjure `bind_inactive`
  does (`Spell._add_owned_conduit` with the root's id, name, store, dynamic flag, gate controller and caching
  posture); a managed parked version gets its pool.
- After a notch, the parked version's first meld builds, for every existence.
- Cache generation 21, with its history entry naming the managed codegen (0.2.8245).

## Requirements (Non-Functional)
- Active versions, spell ids and records unchanged; non-managed emitted plans byte-identical.
- No new lock edge: the loop runs under the Book lock, as the active-version loop does.

## Scope Boundaries
- In scope: the conjure wiring, the cache generation, tests, docs, the release note, the notch, the rebuild, and a
  check that `ManagedSpellLease` works as built (the owner kept it as it is, 2026-10-16).
- Out of scope: the review items the owner kept as built (activation hooks on every meld from the pool, F9 as widened,
  override objects outside the count, the no-move release ambiguity); any change to `ManagedSpellLease`.

## State Transition Event
- from_state: blocked
- to_state: done
- transition_reason: the owner accepted the epic and its stories (chat, 2026-10-16: "I accept your managed spell stuff
  and continue onto the next stuff please"); notched 0.2.8248, rebuilt and checked, every EXIT_GATE item recorded in
  the Notes.
- prior: in_progress -> blocked (2026-10-16T11:45:26Z): S8's work is done and notched 0.2.8248 - the conjure loop,
  generation 21, the message, the whole tree green in both GIL modes, `ManagedSpellLease` checked as built, the system
  docs and graph, the release note (its example run in both GIL modes) and the patch lane archived; the rebuild runs
  last, after these records. The EXIT_GATE's remaining item is the owner's acceptance, a reserved decision. Unblock:
  the owner accepts or redirects. The board row reads `review`.
- prior: blocked -> in_progress (2026-10-16T09:20:01Z): melder_1 landed 0.2.8247 (assets and bundles rebuilt, both
  checks OK) and handed back the four call-site lines and five test doubles, so the release note, the next notch, the
  rebuild and the system docs were free; the owner said "fix bind_inactive" (chat, 2026-10-16) and kept
  `ManagedSpellLease` as it is, asking that it be checked to work.
- prior: draft -> blocked: approved by the owner on 2026-10-16 ("bind_inactive should behave the same before and after
  conjure"; "you can bump the cache"); blocked until melder_1 reported its landing, because the release note, the
  next notch, the rebuild and the system docs were its for that landing.

## Dependencies / Related Work
- EPIC-2026-10-14-managed_spell_quantity: Open Questions and the owner's rulings (Decision Log, 2026-10-16).
- TASK-2026-10-15-make_meld_state_checks_follow_spell_state (melder_1) lands first.

## Tasks (Implementation Checklist)
- [x] Read the conjure wiring, the post-conjure `bind_inactive` branch, `_apply_notch` and the restore engine's staged
      replay whole; settle U12.
- [x] Component patch doc and the mapping note.
- [x] Red tests (each existence: parked before conjure, notch, meld), the loop, then green in both GIL modes.
- [x] Cache generation 21.
- [x] `ManagedSpellLease` works as built: its tests and the component `with` tests in both GIL modes, and a probe of
      the `with` release on exit and on exception, `ReleaseManagedSpell().managed(obj)` and release-once.
- [x] Docs (the failure mode "Stage versions after conjure" is a fixed defect), the release note (its example run in
      both GIL modes) and the notch 0.2.8248; the patch lane archived.
- [x] Rebuild last: the asset runner and the LLM bundles, each with `--check` (six OK lines).
- [x] Enforce Ticket Microcycle across all linked tasks.
- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- probes/probe_owner_questions.py Q1 prints "meld works" for every existence without its probe-only patch.
- Every EXIT_GATE item recorded.

## Validation / Test Plan
- New unit and integration tests; the spellbook unit tree, the conduit integration tree and the crystallizer restore
  suites in both GIL modes; the non-managed emission comparison; both rebuild checks.

## UX / API / Data Notes
- No API change: a world staged before conjure now works.

## Risks / Mitigations
- A parked existing-object version must not be registered as live before it is notched in -> the conjure loop does
  exactly what the post-conjure path does (U12).
- Restored and grafted worlds stage their members after conjure, so they took the wired path already (U12 FACT
  note) -> their suites run as regression checks.

## Applicable Anti-Patterns
- [x] No story-state transition without linked task-state evidence.
- [x] No closure while required tasks remain active or un-routed (S8 moves to review, not to done).
- [x] No cross-task synthesis claims without ticket-note evidence pointers.
- [x] No `src/` edit before the component patch and the mapping note exist (patch 09:42Z, mapping 09:43:47Z,
      first `src/` edit after the red run).

## Open Questions
- U12 (UNKNOWN): does a post-conjure `bind_inactive` of an existing object, or a notch to it, register the object in
  the store? The conjure loop must do what that path does. Evidence targets: `Spellbook.bind_inactive`'s post-conjure
  branch, `Spellbook._apply_notch`, `SpellbookCreationSystem.define_conduit_into_spells`.
- Settled by the owner (2026-10-16): `ManagedSpellLease` stays as built; this story checks that it works (Decision
  Log).

## Decision Log
- 2026-10-16 (owner, chat with melder_0): "I accept your managed spell stuff and continue onto the next stuff please" - S8 accepted with the epic; on this story's finding: "just use
  the private version if its inside the public call thats reasonable" (TASK-2026-10-16-public_notch_target_for_staged_versions).
- 2026-10-16 (owner, chat with melder_0): "no these are all fine, fix bind_inactive, 1. is fine leave it as is but
  just do make sure it works fine" - build this story now; `ManagedSpellLease` stays as built and is checked here.
- 2026-10-16 (owner, chat with melder_0): fix it - "so really bind_inactive should behave the same before and after
  conjure like it should work right?"; bump the cache - "you can bump the cache because codegen also requires that
  you properly modify it if it requires modifications".

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/parked_versions_wired_at_conjure_2026_10_16/architecture_patch.md
  - system_docs/patches/completed/parked_versions_wired_at_conjure_2026_10_16/component_patch_spellbook_creation_system.md
  - system_docs/patches/completed/parked_versions_wired_at_conjure_2026_10_16/component_patch_caching_system.md
  - system_docs/patches/completed/parked_versions_wired_at_conjure_2026_10_16/component_patch_site_plan_runtime_helpers.md
  - artifacts/managed_spell_quantity_20261015/ (probes/probe_owner_questions.py, runs/owner_questions_gil0.txt; this
    story's probes, runs and scripts)
- DISPOSITION: promote_to_documentation (patch docs); retain_as_reference (artifacts)
- CLEANUP_TRIGGER: the patch docs are promoted and archived at landing; the artifacts stay as the epic's evidence

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - conjure's owner wiring of parked versions
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T00:52:02Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T00:52:02Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The defect, measured on 0.2.8246 (probe Q1, dynamic world): conjure wires only the active versions
    (`define_conduit_into_spells` walks `_spells`) and a notch wires nothing, so a version parked with
    `bind_inactive` before conjure has no CreationContextFactory, and its first meld after a notch raises
    RuntimeError "Spell has no configured CreationContextFactory." for unique, unique_per_conduit, many and managed
    alike. Parked after conjure it melds; with a probe-only loop over `_inactive_spells` at conjure all four meld.
    `bind_inactive`'s comment says pre-conjure parked spells "are wired at conjure like pre-conjure active spells".
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/owner_questions_gil0.txt:1-13
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_owner_questions.py:37-92
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1382
  - src/melder/aether/spellbook/spellbook.py:5292-5306
  IMPACT: The fix is the loop the comment describes, and the probe is the acceptance check.
  NEXT: On melder_1's landing report, read the first task's paths whole and settle U12.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T09:20:01Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: S8 started on 0.2.8247 (melder_1's landing: rebuilt, both checks OK, its patch lane archived, custody of
    spellbook.py, transfer_of_ownership.py and the five test doubles handed back). Order: (1) read whole the
    post-conjure `bind_inactive` branch, `_apply_notch`, `define_conduit_into_spells`, the restore engine's staged
    replay and the cache generation history, and settle U12; (2) the patch lane (architecture and component patches)
    and the mapping note; (3) red tests per existence, the conjure loop, green in both GIL modes; (4) cache generation
    21; (5) verify `ManagedSpellLease` works (the owner kept it as it is: "make sure it works fine"); (6) docs, graph,
    release note, notch 0.2.8248, rebuild last.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - context_compass/tickets/tasks/2026-10-15_make_meld_state_checks_follow_spell_state_task.md:1039-1057
  - context_compass/tickets/stories/2026-10-16_parked_versions_wired_at_conjure_story.md:51-61
  IMPACT: The story's entry gate holds except the patch docs and the mapping note, which come before the first
    `src/` edit.
  NEXT: Read the post-conjure `bind_inactive` branch and `_apply_notch` whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T09:37:24Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: U12 is settled, read whole on 0.2.8247. A post-conjure `bind_inactive` wires the parked version with the
    one stamp an active post-conjure bind uses (`Spell._add_owned_conduit`: the root's id, name and store, its dynamic
    flag and gate controller, the Book's caching posture; a managed version gets its pool there) and nothing else - no
    `_register_to_creations` for an existing object, no `resolution_required` write, no risk-manager, index or Nexus
    registration. `_apply_notch` stamps and registers nothing: it parks and promotes, re-registers the index gated,
    sets `resolution_required` False and gates the promoted id. An existing-object version melds from
    `spell.user_created_object` in every door and executor, never from the store, so its store row only feeds teardown
    disposal and transfer rows. So the conjure loop over `_inactive_spells` is that stamp alone, same arguments as the
    active loop, skipping a version that already has an owner store, with no registration: a parked existing object is
    not registered as live before its notch, as on the post-conjure path. Both loaders stage after conjure
    (`RestoreEngine._bind_one_staged` refuses without a conduit and calls `conduit.bind_inactive`; GraftRunner
    requires a conjured host), so restored and grafted worlds already take the stamped path - the story's Risks line
    saying they "take the fixed path too" is wrong; their suites still run as regression checks. Text the fix makes
    stale: the missing-pool MeldExecutionError ("... a version staged with bind_inactive before conjure and notched in
    after it ... or stage the version after conjure"), its two tests, `bind_inactive`'s comment (it becomes true),
    `_migrate_inactive_members`' docstring and comment, two test docstrings, and the S6 release-note line. UNKNOWN until
    probed: a notched-in existing-object version is registered in no store by either path, so its disposal methods
    may not run at root teardown.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1382
  - src/melder/aether/spellbook/spellbook.py:5096-5348
  - src/melder/aether/spellbook/spellbook.py:5419-5745
  - src/melder/aether/spellbook/spellbook.py:3826-3967
  - src/melder/aether/spellbook/spell.py:1661-1717
  - src/melder/aether/spellbook/spell.py:1044-1087
  - src/melder/aether/conduit/conduit.py:1733-1774
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:155-234
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/creation_runtime_door_compiler.py:498-696
  - src/melder/aether/conduit/meld/conduit_meld.py:733-890
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2201-2269
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:432-489
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:543-569
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1589-1649
  - release_docs/next_version_release.md:310-310
  IMPACT: The patch is one loop plus generation 21 and the stale texts; no CONFLICT between the two paths, so the
    story's FAILURE_ESCALATION does not fire. The existing-object teardown question goes to the probe, then a backlog
    task if it holds.
  NEXT: Write the patch lane (architecture patch, component patches for SpellbookCreationSystem and CachingSystem).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T09:40:38Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The UNKNOWN of the U12 note is closed - no teardown gap. probes/probe_s8_existing_object_teardown.py (gil=0,
    a dynamic root, an existing object bound active with disposal_method_names=["close"], a second one staged after
    conjure and notched in): the notched-in object melds, is in no store before or after the meld, and teardown
    closes neither object - because Bind resolves disposal names only for a class binding profile, so an
    existing-object spell carries none (`disposal_method_names` is [] and `has_disposal_methods` False even when
    names are passed) and its store row never runs a disposal. Skipping registration for a parked existing object at
    conjure, as the post-conjure path does, therefore changes no disposal; no backlog task is opened.
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s8_existing_object_teardown.py:1-68
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_existing_object_teardown_gil0.txt:1-2
  - src/melder/aether/spellbook/bind/bind.py:754-772
  IMPACT: The conjure loop is the stamp alone, with nothing left open behind it.
  NEXT: Write the patch lane (architecture patch, then the component patches).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-16T09:43:47Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: The patch lane parked_versions_wired_at_conjure_2026_10_16 is written and linked (architecture patch; component
    patches for SpellbookCreationSystem, CachingSystem and SitePlanRuntimeHelpers; no code-description patch: one loop
    under a lock conjure already holds). Mapping, patch section -> implementation -> validation: (1) invariant 1 and
    the SpellbookCreationSystem "After" -> a second loop over `_inactive_spells` in `define_conduit_into_spells`,
    inside the same Book-lock block, the active loop's `_add_owned_conduit` arguments, log and continue on a failure,
    no registration and no resolution flag -> new unit file (stamp arguments, a parked existing object not registered,
    the flag untouched, a raising stamp logged) and new integration file (unique, unique_per_conduit, many, managed,
    an existing object and a function, staged before vs after conjure, meld after a notch), probe Q1 without its
    patch; (2) invariant 2 -> the active loop untouched -> the existing define_conduit tests; (3) invariant 3 -> nothing
    to build -> integration: a staged id is not meldable before its notch in both staging moments; (4) invariant 4 ->
    no new lock -> review and the direct-cleanup lock-order component tests; (5) invariant 5 -> no plan or bind code
    touched -> spellbook unit, conduit integration and crystallizer restore suites in both GIL modes; (6) the
    CachingSystem patch -> history 21 "managed_spell_lease_codegen" and its comment -> the cache-schema integration
    test expecting 21; (7) the SitePlanRuntimeHelpers patch -> the new message and docstring -> its two lowering
    tests; (8) the comment-only edits (`bind_inactive`, `_migrate_inactive_members`) -> review. Then the
    `ManagedSpellLease` check, docs, graph, release note, notch, closure and the rebuild last.
  EVIDENCE:
  - context_compass/system_docs/patches/active/parked_versions_wired_at_conjure_2026_10_16/architecture_patch.md:1-106
  - context_compass/system_docs/patches/active/parked_versions_wired_at_conjure_2026_10_16/component_patch_spellbook_creation_system.md:1-71
  - context_compass/system_docs/patches/active/parked_versions_wired_at_conjure_2026_10_16/component_patch_caching_system.md:1-37
  - context_compass/system_docs/patches/active/parked_versions_wired_at_conjure_2026_10_16/component_patch_site_plan_runtime_helpers.md:1-29
  IMPACT: The story's entry gate is complete; `src/` edits may start after the red tests.
  NEXT: Write the red tests (unit, integration, the cache-schema expectation, the two message assertions) and run them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T09:50:18Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The change is in and its own tests went red, then green. Red on 0.2.8247 with the GIL off: 37 failed, 71
    passed - six unit tests (no parked stamp), eight integration cases (every family staged before conjure fails its
    meld after the notch with "Spell has no configured CreationContextFactory.", the store check and the managed pool
    check), the 21 cache-schema cases (the history lacks 21) and the two message assertions; the staged-after controls
    and the not-meldable-by-id cases passed. Then: `define_conduit_into_spells` stamps `_inactive_spells` after the
    active loop under the same Book lock (docstring Contract and Threading updated); `CACHE_VERSION_HISTORY[21] =
    "managed_spell_lease_codegen"` with its comment; the missing-pool message now reads "... its owner root was torn
    down, or its owner store holds no pool for this version. Meld it through a live root that owns it."; comments in
    `bind_inactive` and `_migrate_inactive_members` and two test docstrings say a version staged before conjure is
    wired at conjure. CRLF kept in the two CRLF files (spellbook_creation_system.py +37 and caching_system.py +8 lines
    by the CR-insensitive diff). Green: 108 passed with the GIL off and on. Acceptance: probe Q1 without its probe-only
    patch prints "stamped before notch=True; meld works -> ServiceB" for unique, unique_per_conduit, many and managed
    staged before conjure; Q2, Q4 and Q5 print what they printed before.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1332-1419
  - src/melder/utilities/caching_system/caching_system.py:190-219
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:543-571
  - src/melder/aether/spellbook/spellbook.py:5293-5300
  - src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:1589-1652
  - tests/unit/melder/spellbook/test_spellbook_creation_system_parked_versions.py:1-366
  - tests/integration/melder/spellbook/test_spellbook_integration_parked_before_conjure.py:1-250
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_red_gil0.txt:1-1442
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_green_new_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_green_new_gil1.txt:1-11
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_owner_questions_after_gil0.txt:1-13
  IMPACT: The acceptance check holds; what is left before docs is the whole tree in both GIL modes and the
    `ManagedSpellLease` check.
  NEXT: Collect fresh test-id lists and run the whole tree (unit, component, integration, experiments) in shards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T11:00:56Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The whole tree is green in both GIL modes with the change, and `ManagedSpellLease` works as built (the
    owner's "make sure it works fine"). runs/s8_validation_index.md indexes every run log (scripts/
    s8_validation_index.py): the unit aether and spellbook trees 7035 passed per mode; the rest of the unit tree 2508
    passed, 3 skipped, 7 xfailed of 2518 ids; component 2396 passed, 23 skipped, 1 xfailed of 2420; integration (the
    crystallizer restore and graft suites among them) 2165 passed, 9 xfailed, 2 xpassed, 2 skipped of 2178;
    experiments 250 passed, 4 skipped of 254 - identical outcomes with the GIL off and on, every collected id
    accounted for, and the skip, xfail and xpass counts the ones S6 recorded (the xpasses are two DI validation fault
    tests). The lease: its unit file, the release registry's, the managed component file and the two managed
    integration files, 94 passed per mode; probes/probe_s8_managed_spell_lease.py, 8 of 8 cases per mode - `with`
    gives the object back on exit (reused, its reset run once) and on an exception (which propagates),
    `ReleaseManagedSpell().managed(obj)` releases that object, a lease releases once (a second release does nothing,
    `.object` and `with` raise after it), limited_quantity(1) reuses its one object, a release after root teardown
    raises the torn-down RuntimeError, `managed_spell_meld` of a unique spell is refused before anything is melded,
    and a version staged before conjure, notched in, leases and returns through `with`. Not run, by scope: an
    emission capture - the lowering's change is the text of a helper the plans call (`_raise_missing_managed_pool`,
    bound into a plan's namespace), so no plan text moves - and a benchmark (conjure's cold path only). Hosted CI and
    coverage: Not run (the owner's).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_validation_index.md:1-64
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_validation_index.py:1-82
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s8_managed_spell_lease.py:1-204
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_managed_spell_lease_gil0.txt:1-9
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_managed_spell_lease_gil1.txt:1-9
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_lease_suites_gil0.txt:1-3
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_lease_suites_gil1.txt:1-11
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s6_validation_index.md:21-29
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1121-1125
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:1894-1902
  IMPACT: The EXIT_GATE's test items hold (green in both GIL modes; non-managed plans unchanged because no emitting
    code changed); what is left is documentation, the graph, the release note, the notch, closure and the rebuild.
  NEXT: The board row's next, then promote the patch lane into src_architecture.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T11:20:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The patch lane is promoted into the four system documents and the graph (scripts/s8_docs_architecture.py,
    s8_docs_components.py, s8_docs_tests.py, s8_graph_semantics.py; s8_replace.py for one rewrap), every claim re-read
    against this tree first (`Spell._add_owned_conduit` resets the context, configures the factory and ensures a
    managed pool; Bind resolves disposal names only for a ClassBindingProfile). src_architecture: the boot and conjure
    sequences and the pipeline diagram, a new invariant "Parked versions are wired at conjure", the transfer
    invariant (every parked member stamped; only a raising stamp leaves one unstamped), the managed-lease invariant
    (generation 21), two failure modes (the missing-pool text; the pre-conjure staging gap as fixed in 0.2.8248), five
    code-map extents (spellbook.py 7618, spellbook_creation_system.py 3545, site_plan_lowering.py 2121,
    transfer_of_ownership.py 2158, caching_system.py 900), the settle-then-inherit citations three lines down
    (6793-6836, 7049) and a handoff entry. src_components: a dated Spellbook Core entry and the cache's generation 21,
    the conjure pipeline (spellbook_creation_system.py now its key file), the conjure flow, Managed Spell Pools'
    lifecycle, Ownership Transfer, the managed sites' message, four extents, and every citation the 0.2.8247 entry
    listed as stale, re-pointed at its code (7412-7433 with :7423, :288, 5893-5898, 5422-5438, :6725, the SafeGuard
    pair :960 and :1451) with the `_phase_run_lock` site S8 moved (2123-2151, :2151). tests_components: the two new
    files as key files with Protects lines and code-map records, three records remeasured (883, 484, 174 lines), the
    suites' module counts recounted (unit 505 of 508 `.py`, component 166 of 168, integration 167 of 174; 838), core
    set 252 equal to the code map; tests_architecture: the inventory and a handoff entry. All four indexes regenerated
    with `--check` OK; the citation recipe finds nothing in src_architecture and, in src_components, only the two bare
    file names of the 0.2.8247 entry's own stale list (no path to resolve). Graph: extracted with --strict (591
    descriptors, nothing skipped); S8 moved three nodes AUTHORED against 0.2.8247 (SpellbookCreationSystem,
    SitePlanRuntimeHelpers, Spellbook), which got the lane's facts and were accepted after their changed hunks were
    read; CachingSystem and TransferOfOwnership, stale since before this lane, got the facts and stay unaccepted;
    re-extracted and assembled (28066 lines, 591 sections verified, 1227 nodes, 1415 edges); walker AUTHORED 1074,
    SEMANTICS_STALE 144, UNSEMANTIC 9, RETIRED 5 - the counts before the lane; src_components' 373 Key Files
    citations (221 paths) resolve against the graph.
  EVIDENCE:
  - context_compass/system_docs/src_architecture.md:1038-1058
  - context_compass/system_docs/src_architecture.md:4087-4096
  - context_compass/system_docs/src_components.md:348-359
  - context_compass/system_docs/src_components.md:11061-11071
  - context_compass/system_docs/tests_components.md:1109-1115
  - context_compass/system_docs/tests_components.md:1564-1571
  - context_compass/system_docs/tests_components.md:3307-3315
  - context_compass/system_docs/tests_architecture.md:884-888
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_docs_architecture.py:1-149
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_docs_components.py:1-145
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_docs_tests.py:1-157
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_graph_semantics.py:1-83
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_graph_accept_apply.txt:1-5
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_graph_extract_after.txt:1-46
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_graph_assemble.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_graph_walker_after.txt:1-10
  - context_compass/artifacts/meld_contract_scan_20261015/runs/graph_accept_2026_10_16.txt:1-7
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s7_graph_census_after.txt:30-100
  - src/melder/aether/spellbook/spell.py:1661-1717
  - src/melder/aether/spellbook/bind/bind.py:755-772
  IMPACT: Docs and graph describe 0.2.8248's behaviour; what remains is the epic's Build Specification, the release
    note, the notch, the patch lane's archive, the move to review and the rebuild.
  NEXT: Correct the epic's Build Specification (B3, B7, B8, B12) for S8.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T11:39:55Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Notched 0.2.8248 (`__version__` read 0.2.8247 at landing, melder_1's notch the newest) and the running
    release note carries S8 (scripts/s8_notch_release_note.py, then three exact replacements): the header, a new
    section "A version staged before `conjure` melds after a notch" before Packaging, the S6 transfer line (a version
    staged before conjure carries an owner record), the managed pool sentence (every version, the parked ones since
    0.2.8248), a generation-21 bullet in the leasing list and the packaging lines. Running the example caught a
    wrong first draft: a bare `md.Spellbook()` refuses `bind_inactive` before conjure ("bind_inactive requires a
    dynamic Spellbook posture ..."), because a fresh frame is not dynamic until its first `conjure(dynamic=True)`
    settles it (`Spellbook._is_dynamic_posture` reads the frame posture). The section now says so and its example
    joins a world an earlier `conjure(dynamic=True)` settled. probes/probe_s8_release_note_example.py runs the
    section's block verbatim, doing the commented notch through `Spellbook._get_owned_spell` - no public call
    returns a parked version's Spell (`notch_spell` needs the Spell; `find_spell_by_id` answers a parked id with the
    live one) - and checks the bullets. Both GIL modes: the meld after the notch is a ReportServiceV2; a meld of the
    staged id before it raises KeyError "[MELD] No spell found with spell_id: ..."; a managed version staged before
    conjure has no pool before conjure, one after it (`describe(cls)` names its spell id), leases after the notch
    and is idle again after the release (count 1, idle 1).
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/next_version_release.md:533-579
  - release_docs/next_version_release.md:310-311
  - release_docs/next_version_release.md:379-382
  - release_docs/next_version_release.md:470-472
  - release_docs/next_version_release.md:641-645
  - src/melder/aether/spellbook/spellbook.py:5275-5282
  - src/melder/aether/spellbook/spellbook.py:3714-3729
  - src/melder/aether/conduit/conduit.py:5622-5710
  - src/melder/aether/spellbook/spellbook.py:2029-2108
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s8_notch_release_note.py:1-93
  - context_compass/artifacts/managed_spell_quantity_20261015/probes/probe_s8_release_note_example.py:1-120
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_release_note_example_gil0.txt:1-4
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_release_note_example_gil1.txt:1-8
  IMPACT: The note's example runs as written. The missing public lookup of a parked version (the README's
    stage-notch-meld sketch passes an undefined `spell_v2`; docs/expert/governed-change.md stops its lesson before
    the notch for that reason) goes to a backlog task for the owner's design call.
  NEXT: The board notch notice, then archive the patch lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-16T11:50:05Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The rebuild ran last, after the code, tests, docs, graph, release note, notch, the patch lane's archive and
    the move to review. The asset runner wrote the agent-documentation (468 entries), bind-guard (628 entries) and
    system-documents (4 entries) manifests for 0.2.8248 (1 min 15 s), and its `--check` printed three OK lines. The
    LLM builder (`--include-untracked`; S8's two new test files are untracked) rewrote the src (583 files), tests
    (1119) and other (404) corpora, and its `--check` printed three OK lines. The session dropped while the asset
    runner ran; its log shows the run finished (three WROTE lines and the timing) before the check started. The
    ticket and board edits after the rebuild are outside both builders' inputs: the system-documents builder ingests
    context_compass/system_docs only, and the LLM builder excludes context_compass/. Not run: hosted CI and coverage
    (the owner's).
  EVIDENCE:
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_rebuild_assets.txt:1-7
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_rebuild_assets_check.txt:1-7
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_llm_support.txt:1-8
  - context_compass/artifacts/managed_spell_quantity_20261015/runs/s8_llm_support_check.txt:1-7
  - src/melder/_build_assets/_system_documents/_builder.py:110-110
  IMPACT: S8's EXIT_GATE holds except the owner's acceptance; this lane's files are free for melder_1's rule-2
    landing.
  NEXT: The owner accepts S1-S8 and the epic, or redirects.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-16T12:17:31Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: S8 closes: the owner accepted the epic and its stories (chat, 2026-10-16: "I accept your managed spell stuff
    and continue onto the next stuff please"). Reserved-owner disposition: accepted. The owner also ruled on this
    story's finding ("just use the private version if its inside the public call thats reasonable"): `notch_spell`
    resolves a staged version by its id through the Book's internal lookup, built next in
    TASK-2026-10-16-public_notch_target_for_staged_versions.
  EVIDENCE:
  - context_compass/attention_board.md:222-224
  IMPACT: The lane is closed and its files are free.
  NEXT: none for this story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Closure Confirmation
- [x] Work walkthrough shared with user (2026-10-16T11:49:54Z, the owner report)
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: S8 - conjure wires versions parked before it; cache generation 21; tests, docs, release note, notch, rebuild.
- State: done - landed 0.2.8248 and accepted by the owner with the epic (2026-10-16); the evidence is in the
  Notes above.
- Follow-up: the public notch target for staged versions (TASK-2026-10-16-public_notch_target_for_staged_versions),
  ruled on by the owner and next in line.
- Limits: hosted CI and coverage are the owner's (Not run).

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
