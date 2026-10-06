

# Task: Implement noncreating frame lookups and read-only accessors, one notch

## Metadata
- Task ID: TASK-2026-09-29-implement-frame-lookups-and-read-accessors
- Story: STORY-2026-09-29-frame-lookups-and-read-accessors
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-29T21:21:34Z
- Updated: 2026-09-29T22:27:57Z

- Completed: 2026-09-29T22:27:57Z
- Summary: Aether.find_frame / get_frame / list_frame_names (never create a frame) and read-only
  AethericFrame.shared_spellbook_configuration, `frozen` on both configurations, SpellbookConfiguration.aether_frame
  and Conduit.spellbook landed with 27 tests (suites green); notched 0.2.8208; release-note section "Look up
  frames without creating them". Turned in by owner directive before the system-doc pass (backlog task) and
  with the rebuild waived: build assets stamped 0.2.8208, LLM bundles stale.

## Objective
Add `Aether.find_frame`, `Aether.get_frame` and `Aether.list_frame_names` (noncreating, "default" included) and the
read-only accessors that replace MelderOps' other private reads (frame-wide shared book configuration, freeze
state of frame and book configurations, a book configuration's frame, a conduit's Spellbook). Owner direction
(chat, 2026-09-29): "ok lets do it go ahead and add this make an epic and implement and notch the version".

## Ticket Contract
- ENTRY_GATE: this board row; investigation notes and patch docs (host_read_surface_2026_09_29) before any source
  edit; sole-writer NOTICE to the active agents before the first source edit.
- EXECUTION_BOUNDARY: additions only in src/melder/aether/aether.py, aetheric_frame/aetheric_frame.py,
  aetheric_frame/aetheric_frame_configuration.py, spellbook/configuration/spellbook_configuration.py and
  conduit/conduit.py; new test files; src_architecture, src_components (+ tests docs if they list test files)
  and indexes; graph descriptors of the touched nodes; the release note; `__version__`; assets and bundles last.
- DEPENDENCIES: STORY-2026-09-29-frame-lookups-and-read-accessors.
- EXIT_GATE: red-then-green tests; meld/conduit and package suites green on 3.14t; both portability checks clean;
  indexes current; graph assembled with touched nodes read and accepted (or recorded stale with reason); notch and
  release note; assets and bundles rebuilt with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if an accessor's natural contract differs from the private read it
  replaces; BLOCKER if a lookup cannot be made noncreating without changing existing callers.

## Scope Boundaries
- In scope: the objective above.
- Out of scope: existing lookup semantics, frame creation/cleanup, Melder's own private registry readers,
  priv_commandops, the parked retirement/attribution story.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner directive in chat (2026-09-29) to add the release note, keep the version and turn in.

## Steps / Checklist
- [x] Read the registry, lock and accessor sources; record the design facts.
- [x] Patch docs (architecture + one component patch per changed component); consumption mapping note.
- [x] Red tests, then the additions; green; suites.
- [x] Release note and notch done; docs, indexes and graph moved to the backlog task; bundles waived by the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The three lookups and the accessors with rich docstrings; tests; promoted docs; notch; rebuilt assets.

## Files / Paths Impacted
- Exact list in the PLAN note before edits.

## Validation
- Red on 0.2.8207 (22 new tests), then green on 0.2.8208; the 27 new tests pass on 3.14t GIL off/on,
  the GIL build and the device tree. VM copy: tests/unit 8279 passed (1 expected stamp failure, since fixed by
  the asset rebuild), integration + component 4223 passed. Coverage: Not run.

## Risks / Rollback Notes
- Additions only; rollback is a revert of one change set.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No graph acceptance without reading the node's source against its prose (no graph work in this lane).

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (release note; system docs parked in the backlog task)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive to turn in)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/host_read_surface_20260929/
  - system_docs/patches/completed/host_read_surface_2026_09_29/
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch lane)
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
- DATETIME: 2026-09-29T21:21:34Z
  TYPE: FACT
  CLAIM: Lane opened on the owner's direction (chat, 2026-09-29). Starting facts from the discussion: frames are
    born by `Aether._ensure_frame` (get-or-create) from Spellbook construction, Nexus managed creation and
    crystallizer restore; every public frame-scoped Aether call resolves through `_get_existing_frame`, which
    creates "default" when missing; the first frame freezes the Aether configuration. MelderOps' observer reads
    `Aether._aetheric_frames` under the Aether lock and five other private surfaces. `__version__` reads 0.2.8207
    (workflows_0), so this lane's notch is expected to be 0.2.8208, read again at landing.
  EVIDENCE:
  - src/melder/aether/aether.py:1075-1190
  - src/melder/aether/aether.py:1611-1641
  - src/melder/aether/aether.py:2325-2385
  - src/melder/aether/spellbook/spellbook.py:288-292
  - src/melder/__version__.py:12-12
  IMPACT: The lookups must bypass `_get_existing_frame`; everything else is a read-only accessor.
  NEXT: Read the Aether class header, locks and cleanup, then each accessor's source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:25:01Z
  TYPE: FACT
  CLAIM: Design facts from the source. Aether's `_lock` is the one class-level RLock for construction and registry
    writes (no instance lock); `_aetheric_frames` holds every frame, "default" included, and is deleted at
    cleanup after `_cleaned` is set, so `check_cleaned()` must come first. A frame is detached from the registry
    only at the END of its own cleanup, so a registered frame can already read `cleaned`. `_detach_cleaned_frame`
    calls into Nexus while holding the Aether lock (order Aether -> Nexus), so a lookup that took the Aether lock
    would add an inverse edge for any future Nexus caller; one `dict.get` and one `dict.copy()` need no lock.
    `frame._configuration` is bound only when the frame posture shares the rich configuration (first bind
    wins), which is exactly the condition MelderOps checks. `_frozen` exists on both configurations with no public
    read (only root configurations expose `frozen`). `SpellbookConfiguration._aether_frame` is fixed at
    construction and Spellbook refuses a supplied configuration naming another frame. `Conduit._spellbook` is the
    conjuring Book for a root, the shared Book for a lesser, and is rebound by `upgrade_to_normal`.
  EVIDENCE:
  - src/melder/aether/aether.py:113-135
  - src/melder/aether/aether.py:136-251
  - src/melder/aether/aether.py:253-337
  - src/melder/aether/aether.py:405-465
  - src/melder/aether/aetheric_frame/aetheric_frame.py:230-273
  - src/melder/aether/spellbook/spellbook.py:5946-6004
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:407-480
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:120-218
  - src/melder/aether/spellbook/spellbook.py:5605-5625
  - src/melder/aether/conduit/conduit.py:280-310
  - src/melder/aether/spellbook/spellbook.py:6810-6835
  IMPACT: Lookups can be lock-free and noncreating; every accessor mirrors an existing private read exactly.
  NEXT: PLAN note with exact files and symbols, then the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T21:26:32Z
  TYPE: PLAN
  CLAIM: melder_0 writes every file below; additions only in source. (1) aether.py: `find_frame(name) ->
    Optional[AethericFrame]`, `get_frame(name) -> AethericFrame` (ValueError with the existing "Aetheric frame 'X'
    does not exist." prefix, TypeError for a non-string) and `list_frame_names() -> tuple[str, ...]`, sharing one
    private helper; no lock, no plane claim, no creation, cleaned-but-registered frames count as absent. (2)
    aetheric_frame.py: `shared_spellbook_configuration` (the bound rich configuration while the posture shares
    it, else None). (3) aetheric_frame_configuration.py and spellbook_configuration.py: read-only `frozen`; (4)
    spellbook_configuration.py: read-only `aether_frame`. (5) conduit.py: read-only `spellbook`. (6) New tests:
    tests/integration/melder/aether/test_aether_frame_lookups.py and
    tests/unit/melder/aether/test_configuration_read_accessors.py, red before the source edits. (7) Docs:
    src_architecture, src_components, tests_components (+ indexes), docs/intermediate/scopes.md; patch lane
    host_read_surface_2026_09_29 first (architecture + aether_singleton, aetheric_frame_services,
    spellbook_configuration, conduit_runtime). (8) Graph: extract, author the five touched nodes, accept those
    that were AUTHORED before the edit, assemble. (9) `__version__` read at landing (expect 0.2.8208), release
    note section and rebuild line; NOTICE the number. (10) Assets and bundles last, both checks OK.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-09-29_implement_frame_lookups_and_read_accessors_task.md:16-19
  - context_compass/agent_onboarding/default/engineer/skills/patch_framework_gating.md:11-34
  - context_compass/special_instructions/agent_contribution_guide.md:15-39
  - context_compass/special_instructions/agent_contribution_guide.md:75-87
  IMPACT: No runtime behaviour changes; eight existing private reads (six in MelderOps) gain public replacements.
  NEXT: Write the patch docs, record the consumption mapping, then NOTICE the file claims.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:28:02Z
  TYPE: DECISION
  CLAIM: Patch lane host_read_surface_2026_09_29 written and read in the required order (architecture, then the
    four component patches). Mapping: architecture invariants (no creation, no lease, no new lock) -> lookups
    without a lock via one `dict.get` / one `dict.copy()` -> tests that a fresh world gains no frame and no
    Aether configuration; aether_singleton interface/error deltas -> find/get/list plus one private helper ->
    absent/None/ValueError/TypeError/cleaned tests and a concurrent create-and-list test;
    aetheric_frame_services -> `shared_spellbook_configuration` and posture `frozen` -> sharing on/off and
    settle tests; spellbook_configuration -> `frozen` and `aether_frame` -> unit tests; conduit_runtime ->
    `Conduit.spellbook` -> root and lesser tests. No unknowns in the patch; entry gate met once NOTICE is sent.
  EVIDENCE:
  - context_compass/system_docs/patches/active/host_read_surface_2026_09_29/architecture_patch.md:1-69
  - context_compass/system_docs/patches/active/host_read_surface_2026_09_29/component_patch_aether_singleton.md:1-56
  IMPACT: Implementation scope is fixed to the patch boundaries.
  NEXT: NOTICE the file claims, then write the red tests.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:30:54Z
  TYPE: MEASURE
  CLAIM: Red on 0.2.8207 before any source edit: 22 of 22 new tests fail (15 integration, 7 unit), every one with
    AttributeError for a call this lane adds (find_frame, get_frame, list_frame_names, shared_spellbook_
    configuration via get_frame, both `frozen` reads, aether_frame, Conduit.spellbook). 3.14t, PYTHON_GIL=0.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_20260929/red_0_2_8207.txt:1-51
  - tests/integration/melder/aether/test_aether_frame_lookups.py:1-196
  - tests/unit/melder/aether/test_configuration_read_accessors.py:1-80
  IMPACT: The tests pin the patch contracts; the source additions come next.
  NEXT: Add the Aether lookups, then the four accessors, then rerun.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:34:49Z
  TYPE: FACT
  CLAIM: Source landed as planned (apply script in the lane's artifact dir; each file keeps its line endings,
    all parse): Aether.find_frame / get_frame / list_frame_names plus `_find_registered_frame` (no lock, no
    creation, cleaned frames absent); AethericFrame.shared_spellbook_configuration; `frozen` on
    AethericFrameConfiguration and SpellbookConfiguration; SpellbookConfiguration.aether_frame; Conduit.spellbook.
    The 22 new tests pass on 3.14t with the GIL off and on (one test fixed: it mutated the idempotent 'disposal'
    key; it now changes a non-idempotent property). `__version__` read 0.2.8207 at landing and set to 0.2.8208 at
    21:34:06Z; NOTICE M0-98..100 sent.
  EVIDENCE:
  - src/melder/aether/aether.py:1687-1835
  - src/melder/aether/aetheric_frame/aetheric_frame.py:591-624
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1500-1522
  - src/melder/aether/spellbook/configuration/spellbook_configuration.py:219-269
  - src/melder/aether/conduit/conduit.py:1910-1937
  - src/melder/__version__.py:12-12
  - context_compass/artifacts/host_read_surface_20260929/green_new_tests.txt:1-7
  IMPACT: The public surface exists; validation suites, docs, graph and release note remain.
  NEXT: Run the Aether/meld/conduit and package suites on 3.14t and the GIL build.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:41:43Z
  TYPE: MEASURE
  CLAIM: Suites on the device tree at 0.2.8208 (3.14t, GIL off): unit aether 4119 passed; integration+component
    aether 2007 passed, 1 xfailed; unit spellbook 2206 passed (a first run failed 3 method-inspector tests
    because Python loaded Windows-compiled __pycache__ with C:\ paths; with a VM-only PYTHONPYCACHEPREFIX they
    pass). Component spellbook 740 passed and 36 errored, all in cache/snapshot tests whose setup clears old
    cache folders with shutil.rmtree: the connected folder refuses deletes (os.unlink -> Operation not
    permitted). No test touches the new calls; the run created no new files under src/melder/tests.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_20260929/suites_device_0_2_8208.txt:1-16
  IMPACT: No regression attributable to this lane so far; the 36 need a tree where deletes are allowed.
  NEXT: Rerun the spellbook component suite on a VM copy of the repository, then docs, graph and release note.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T21:53:44Z
  TYPE: MEASURE
  CLAIM: On a VM copy of the device tree (deletes allowed, fresh bytecode), 3.14t GIL off: tests/unit 8279 passed,
    3 skipped, 7 xfailed, 1 failed (the stamped-assets test, expected until the rebuild); integration + component
    4223 passed, 25 skipped, 5 xfailed, 2 xpassed (pre-existing XPASS); the spellbook component suite that hit the
    refused deletes on the device tree passes 776/776. Five tests added on the owner's "add some tests": a lookup
    does not stand in for creation (the first Spellbook still seals the configuration), the not-found line is
    logged, find/list during create-and-clean churn never raise, a second Book adopts the reported shared
    configuration, and `Conduit.spellbook` follows `upgrade_to_normal`. The 27 new tests pass on 3.14t GIL off
    and on, the GIL build and the device tree.
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_20260929/suites_vm_0_2_8208.txt:1-10
  - tests/integration/melder/aether/test_aether_frame_lookups.py:201-275
  IMPACT: No regression; only the asset rebuild (last step) is owed for the stamped-assets test.
  NEXT: Read the authoring instructions, then update src_architecture, src_components and tests_components.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T22:08:47Z
  TYPE: FACT
  CLAIM: Re-onboarded after a compaction (self-certified 21:59:27Z). Preservation baselines of src_architecture,
    src_components and tests_components captured before any edit (multisets plus copies). The landed source was
    re-read and matches the patch contracts. Finding: this lane's insertions shift 13 existing `path:line`
    citations in the two src documents: aether.py +149 from 1687, aetheric_frame.py +35 from 591,
    aetheric_frame_configuration.py +24 from 1500, spellbook_configuration.py +52 from 219, conduit.py +29 from
    1910. Each remaps exactly (checked at the new lines: notch/add/remove transaction starts, the link isinstance
    check, bind_frame_configuration, freeze, the SafeGuard pair, find_index_for_spell).
  EVIDENCE:
  - context_compass/artifacts/host_read_surface_20260929/docs/preservation/src_architecture_before.txt:1-10
  - context_compass/system_docs/src_architecture.md:425-427
  - context_compass/system_docs/src_architecture.md:864-864
  - context_compass/system_docs/src_architecture.md:1271-1271
  - context_compass/system_docs/src_components.md:469-469
  - context_compass/system_docs/src_components.md:984-984
  - context_compass/system_docs/src_components.md:1227-1227
  - context_compass/system_docs/src_components.md:1267-1267
  - context_compass/system_docs/src_components.md:2543-2543
  - context_compass/system_docs/src_components.md:5185-5204
  - context_compass/system_docs/src_components.md:9478-9478
  - src/melder/aether/aether.py:1687-1835
  - src/melder/aether/conduit/conduit.py:1910-1938
  IMPACT: The doc pass must remap those citations as well as add the new contracts, or they point at wrong code.
  NEXT: Owner redirected mid-turn (22:05Z): build the 0.2.8208 wheel, install it into the MelderOps env and raise
    MelderOps' Melder floor, tracked in its own task; this doc pass resumes after it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-29T22:27:57Z
  TYPE: FACT
  CLAIM: Release note written: header `# Melder 0.2.8208` and the section "Look up frames without creating them"
    before "Packaging and documentation" (the three lookups, what they never do, borrowed references, the four
    read accessors, a runnable example, what stays the same). The example runs as written against the installed
    0.2.8208 wheel and prints ('ops',). No packaging bullet: no packaged document changed and the bind-guard
    count stays 619. The rebuild line is left at 0.2.8207 because the LLM bundles were not rebuilt.
  EVIDENCE:
  - release_docs/next_version_release.md:1-1
  - release_docs/next_version_release.md:108-151
  - context_compass/artifacts/host_read_surface_20260929/release_example.py:1-11
  IMPACT: Users of 0.2.8208 can find the new calls; the notch has its release-note entry.
  NEXT: Turn in on the owner's directive.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-29T22:27:57Z
  TYPE: DECISION
  CLAIM: Owner directive (chat, 2026-09-29, about 22:22Z): "add the details to the new release and keep the version
    update then turn in your shit don't rebuild assets". Turned in with __version__ kept at 0.2.8208 and the
    MelderOps floor kept at >=0.2.8208. Not done in this lane, and parked in the backlog task: src_architecture,
    src_components and tests_components (plus indexes), the 13 shifted citations, scopes.md and the graph. The
    patch lane is archived without promotion. Build assets are stamped 0.2.8208 (rebuilt for the wheel before the
    directive; asset --check OK after the release note); the LLM bundles are STALE (src, tests, other) and the
    owner waived their rebuild, so the next lander rebuilds them.
  EVIDENCE:
  - context_compass/tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md
  - context_compass/system_docs/patches/completed/host_read_surface_2026_09_29/architecture_patch.md:1-75
  - context_compass/artifacts/host_read_surface_20260929/turn_in_asset_check.log:1-3
  - context_compass/artifacts/host_read_surface_20260929/turn_in_llm_check.log:1-6
  IMPACT: The lane closes with the API, tests, notch and release note delivered and the documentation gap tracked.
  NEXT: none.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Turned in 2026-09-29T22:27:57Z on the owner's directive. Delivered: the three noncreating frame lookups and four read
accessors with rich docstrings, 27 tests, notch 0.2.8208 (21:34:06Z, NOTICE M0-98..100), the release-note
section, and (in the wheel task) the 0.2.8208 wheel installed in MelderOps' env. Open, parked: the
system-doc/graph/scopes promotion and the 13 shifted citations
(tickets/tasks/backlog/2026-09-29_promote_host_read_surface_into_system_docs_task.md); the atomic retirement
story stays in stories/backlog for the owner. LLM bundles stale by the owner's waiver.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
