

# Task: Let a provider bound after conjure be melded directly after it was injected (resolve on first direct meld)

## Metadata
- Task ID: TASK-2026-09-30-resolve-injected-provider-on-first-direct-meld
- Epic: tickets/epics/2026-09-30_injected_dependency_direct_resolution_epic.md (work package C); follows
  tickets/tasks/completed/2026-09-30_reproduce_injected_provider_direct_meld_task.md
- Status: done
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-30T19:07:02Z
- Updated: 2026-09-30T21:18:29Z

- Completed: 2026-09-30T21:18:29Z
- Summary: Option B landed as 0.2.8215 (notched 0.2.8215): a successful target-local pass flags each owned
  dependency it compiled without a plan of its own, and the deferred lane runs the full target pass for a spell
  that is not its Phase 5 root, so a provider bound after conjure melds directly after injection. 13 component
  regressions and 14 unit tests red then green; docs, graph, release note section "Fixed: a class bound after
  conjure melds directly after it was injected", assets and LLM bundles; patch docs archived.

## Objective
Owner pick (chat, 2026-09-30): option B of the reproduce task's DECISION_REQUEST, with "before you start please
make a regression test then fix it" and "or multiple tests". A provider bound after conjure and first built as a
consumer's dependency must be meldable directly afterwards and return the instance its scope already holds. The
consumer's target-local resolution pass flags each dependency its Book owns that has no plan of its own with
`resolution_required` (the per-spell flag every meld door reads), and the deferred lane runs the spell's full
target pass (phases 5-11) when it has no Phase 5 root blueprint, keeping today's 8-11 pass otherwise. Warm melds,
conduit verdicts and the Book validation flag are unchanged; no caller step and no public trigger.

## Ticket Contract
- ENTRY_GATE: the owner's pick; this board row; the regression tests written and run red before any src edit; the
  patch docs and a mailbox NOTICE before any src edit.
- EXECUTION_BOUNDARY: src/melder/aether/spellbook/spellbook_creation_system.py (the target pass tail) and
  src/melder/aether/conduit/meld/meld.py (the deferred lane), docstrings that state the old rule, their tests, the
  system docs, graph descriptors, the release note and __version__.
- DEPENDENCIES: the reproduce task (cause, matrix, probe); the epic's relayed owner contract (no caller step).
- EXIT_GATE: the regression tests red, then green; the epic's diagnostic probe passes on the tree; the meld,
  spellbook, conduit and aether suites green; docs, graph, release note, notch 0.2.8215, assets and LLM bundles
  with --check OK.
- FAILURE_ESCALATION: a DECISION_REQUEST if the fix needs anything beyond the two files (RiskManager, verdict
  semantics, a public API); BLOCKER if the VM cannot run the suites.

## Scope Boundaries
- In scope: option B; regression tests over the reproduce task's matrix plus unit tests of the flag and the lane.
- Out of scope: option A (truthful verdicts at local Phase 6), a public validation trigger, MelderOps
  revalidation (work package D, after the owner's wheel delivery).

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: (2026-09-30T21:18:29Z) the owner's directive in chat ("you can
  close that epic if its done"), after work package D revalidated the installed wheel in MelderOps.
  Earlier: in_progress -> review (2026-09-30T20:21:24Z): option B landed as 0.2.8215, its regression and unit tests red,
  then green; the system docs, graph, release note and patch archive followed, and the assets and LLM
  bundles were rebuilt last (--check OK); the owner's turn-in remains. Earlier: draft -> in_progress
  (2026-09-30T19:07:02Z) on the owner's pick; ticket, board row and artifact rows created before the
  regression tests.

## Steps / Checklist
- [x] Regression tests over the matrix (named and unnamed lesser, root, sibling lessers, unique and many providers,
      a root holding a spell at conjure, system caching on, the SpellSpace door; controls provider first and binds
      before conjure), run red.
- [x] Patch docs and the mailbox NOTICE.
- [x] Unit tests for the flag and the deferred lane, run red.
- [x] Implement B (target-pass tail flags; the deferred lane runs the full pass without a Phase 5 root).
- [x] Green: new tests, meld, spellbook, conduit and aether suites; the epic's probe.
- [x] System docs, graph descriptors, release note, one notch, assets and LLM bundles last.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The regression tests, source change B with unit tests, patch docs promoted into the system docs, release note,
  notch.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook_creation_system.py and src/melder/aether/conduit/meld/meld.py (logic);
  src/melder/aether/spellbook/spellbook.py and
  src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py (comments that state the old lane
  rule); src/melder/__version__.py.
- tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py (new),
  tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py (new),
  tests/unit/melder/aether/conduit/meld/test_meld.py and
  tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py (updated).
- System docs, graph descriptors, release note.

## Validation
- Red (2026-09-30T19:21:20Z, VM mirror at 0.2.8214, Python 3.14.7 free-threaded, GIL off): the
  regression file, 11 failed and 2 passed (the controls); every failure is the direct service meld.
- Green (2026-09-30T19:46:23Z, VM mirror at 0.2.8215): the 153 new and touched tests with GIL off and on; the full suite
  13287 passed, 32 skipped, 12 xfailed, 2 xpassed (pre-existing), 1 failed (the build-asset stamp, refreshed
  by the rebuild at the end); the epic's probe passes in every variant (runs_0_2_8215/).
- After the rebuild (2026-09-30T20:21:24Z): asset --check OK (device), LLM --check OK (device, --include-untracked); the
  package-root unit files with the stamp test, build_assets and the agent-text reader component test in the
  mirror: 280 passed, 24 skipped. Coverage: Not run.
- Recommended commands:
  - cd ~/wt2_new && timeout 170 python -X gil=0 -m pytest -q -p no:cacheprovider --tb=short \
    tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py

## Risks / Rollback Notes
- A dependency flagged and then given its own plan by another path pays one redundant pass on its first direct
  meld (correct, one compile). Rollback: revert the two edits; the flag and the lane are internal.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No src edit before the red regression tests, the patch docs and the NOTICE.
- [x] No removal of the builder guard, no catch-and-retry.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed (owner directive to close the epic)
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/injected_provider_first_direct_meld_20260930/
  - artifacts/injected_provider_direct_meld_20260930/
  - system_docs/patches/completed/injected_provider_first_direct_meld_2026_09_30/ (archived at landing)
- DISPOSITION: retain_as_reference (the two artifact folders); promote_to_documentation (the patch docs:
  promoted and archived 2026-09-30).
- CLEANUP_TRIGGER: the owner's turn-in of this ticket.

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
- DATETIME: 2026-09-30T19:07:02Z
  TYPE: DECISION
  CLAIM: Owner pick (chat): option B, regression tests first ("make a regression test then fix it", "or multiple
    tests"). Re-read on 0.2.8214 before the tests: the failure still reproduces (diagnostic fails; provider-first
    and binds-before-conjure pass). The meld doors enter the validation lane only while the Book flag is raised,
    then call the deferred lane when the spell's resolution_required is set; _execute_admitted re-enters the
    deferred lane while that flag is set; the deferred lane runs only phases 8-11, which skip a spell without a
    Phase 5 root blueprint; the full target pass has one runtime caller (the validation lane); the builder refuses
    a constructed spell whose codegen payload is None; local Phase 6 stamps every node of the pass's index valid.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-30_reproduce_injected_provider_direct_meld_task.md:246-277
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs_0_2_8214/diagnostic_cacheoff.txt:1-1
  - src/melder/aether/conduit/meld/conduit_meld.py:558-562
  - src/melder/aether/conduit/meld/spellspace_meld.py:524-528
  - src/melder/aether/conduit/meld/meld.py:826-891
  - src/melder/aether/conduit/meld/meld.py:893-948
  - src/melder/aether/conduit/meld/meld.py:966-1019
  - src/melder/aether/conduit/meld/meld.py:1141-1202
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1825
  - src/melder/aether/spellbook/spellbook_creation_system.py:2323-2355
  - src/melder/aether/spellbook/spellbook_creation_system.py:2740-2779
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:69-152
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_system.py:644-684
  - src/melder/aether/spellbook/spell_compiler/system/spell_system_validation_system.py:220-267
  IMPACT: B needs two edits: flag the pass's plan-less owned dependencies at the target pass tail, and route a
    flagged spell without a Phase 5 root blueprint through the full target pass in the deferred lane.
  NEXT: Write the component regression tests over the matrix and run them red in the VM mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:14:32Z
  TYPE: FACT
  CLAIM: Mailbox after re-onboarding: fable_0's F0-6 (QUESTION, ACK requested) reports one melder_0 message
    deleted unread after it read through M0-139; the numbering places it as M0-142 (18:58:51Z), the per-frame
    lane's turn-in NOTICE (M0-143 and M0-144 carried the same text to muse_0 and melder_2). Resent as ACK
    M0-145; nothing in it touches this lane. This lane's sole-writer NOTICEs start at M0-146 (fable_0, muse_0,
    melder_2). The priv_commandops mailbox holds no message for melder_0.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-30_record_and_restore_per_frame_spell_worlds_task.md:17-21
  - mailbox_board.md:819-830
  IMPACT: Every active agent holds the per-frame release before this lane claims meld.py and
    spellbook_creation_system.py; the message numbering stays continuous.
  NEXT: Write the component regression tests over the reproduce matrix and run them red in the VM mirror.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-30T19:21:20Z
  TYPE: MEASURE
  CLAIM: The regression tests are written and red on 0.2.8214 (VM mirror, Python 3.14.7 free-threaded, GIL off):
    13 cases in 11 functions, 11 failed and 2 passed. Every failure is the reported error - "Cannot build
    CreationContext before spell_codegen_creation exists." from CreationContextBuilder.build - raised by the
    first direct service meld after a consumer meld that succeeded, in: a named lesser, an unnamed lesser, the
    root, sibling lessers, a unique provider, a many provider, a root holding a spell at conjure, system caching
    cold and warm, and the SpellSpace door with the consumer melded through the conduit or the space. The two
    controls pass: the service melded before its consumer, and the pair bound before conjure. The cached cases
    remove the conjure cache folders they wrote (none left in the mirror). No src change; no notch.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py:52-172
  - tests/component/melder/aether/conduit/test_conduit_component_injected_provider_direct_meld.py:174-286
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/regression_red.log:25-37
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/regression_red_tb_short.log:3-12
  IMPACT: The SpellSpace door and a warm conduit bundle fail the same way, so the fix must serve both meld
    doors and does not depend on the conjure cache; the controls pin that option B leaves the orders that
    already worked unchanged.
  NEXT: Re-read the fix's code path in full, then write the patch docs (architecture, meld runtime, compiler
    target pass, deferred-lane code description) and send NOTICE M0-146..148.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:31:23Z
  TYPE: PLAN
  CLAIM: Patch docs written (patch id below) and read in order (architecture, the two component patches, the
    code description); NOTICE M0-146..148 claims the lane's files. Mapping, patch section -> implementation ->
    validation: (1) target pass tail -> new static SpellbookCreationSystem.flag_dependencies_without_own_plan,
    called on the success path of run_resolution_phases_for_target_spell after the scoped cleanup -> a new unit
    file (flag and skip matrix, the write under the dependency's lock, called on success only), and the fastpath
    stub gains the _spell_id_pool the success path now reads; (2) deferred lane routing and the code description
    -> Meld._ensure_runtime_resolution_ready sends a spell that is neither an existing creation nor its Phase 5
    root through the full pass and checks its verdict -> four new lane tests in test_meld.py, and its two
    deferred-lane tests make their spell a Phase 5 root; (3) the invariants -> the component regression file
    (red) turns green, then the epic's probe. Comment-only edits where a comment gives "the deferred lane cannot
    compile it" as a reason: spellbook.py (notch and bind) and creation_context_rebuild.py.
  EVIDENCE:
  - system_docs/patches/active/injected_provider_first_direct_meld_2026_09_30/architecture_patch.md:1-59
  - system_docs/patches/active/injected_provider_first_direct_meld_2026_09_30/component_patch_spellcompiler_target_pass.md:1-44
  - system_docs/patches/active/injected_provider_first_direct_meld_2026_09_30/component_patch_meld_resolution_runtime.md:1-40
  - system_docs/patches/active/injected_provider_first_direct_meld_2026_09_30/code_description_patch_first_direct_meld.md:1-37
  - src/melder/aether/spellbook/spellbook.py:3804-3813
  - src/melder/aether/spellbook/spellbook.py:5390-5393
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:140-169
  IMPACT: Four src files - two with logic, two with comments only - each change mapped to a patch section and a
    test; nothing outside the declared boundary (no verdict, RiskManager or public API change).
  NEXT: Write the unit tests for the flag helper and the deferred lane, and run them red in the VM mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:37:49Z
  TYPE: MEASURE
  CLAIM: Unit tests written and red on 0.2.8214 (VM mirror, GIL off): the new flag file, test_meld.py and the
    fastpath file together give 14 failed, 126 passed. Red as intended: 11 flag tests (no
    SpellbookCreationSystem.flag_dependencies_without_own_plan yet, and the target pass flags nothing on
    success) and 3 lane tests (a spell without a Phase 5 root still gets the 8-11 pass; a full pass that
    leaves an invalid verdict or raises is never reached). Green guards: the two failure-path flag tests, the
    existing-creation lane test, the four deferred-lane tests now pinned to a Phase 5 root, the whole fastpath
    file with its stub's new _spell_id_pool.
  EVIDENCE:
  - tests/unit/melder/spellbook/test_spellbook_creation_system_dependency_flags.py:120-283
  - tests/unit/melder/aether/conduit/meld/test_meld.py:2100-2113
  - tests/unit/melder/aether/conduit/meld/test_meld.py:2258-2389
  - tests/unit/melder/spellbook/test_spellbook_creation_system_resolution_fastpath.py:90-107
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/unit_red.log:1-48
  IMPACT: Every behaviour option B adds is pinned before the source edit; the fix is done when these 14 and
    the 11 component regressions pass with the rest of the suites.
  NEXT: Apply the source edits to the VM mirror (meld.py, spellbook_creation_system.py, the comments in
    spellbook.py and creation_context_rebuild.py, __version__ 0.2.8215) and run the new tests green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:46:23Z
  TYPE: MEASURE
  CLAIM: Option B landed on the device tree at 2026-09-30T19:44:38Z, byte-identical to the VM mirror where it was
    validated; __version__ 0.2.8214 -> 0.2.8215 (read at landing). flag_dependencies_without_own_plan runs on
    the success path of run_resolution_phases_for_target_spell; _ensure_runtime_resolution_ready sends a
    flagged spell that is neither an existing creation nor its Phase 5 root through the full target pass and
    checks its verdict (_requires_own_target_pass, _raise_unless_resolution_valid); the comments in
    spellbook.py and creation_context_rebuild.py no longer give the old lane as a reason. Green in the VM
    (3.14.7t): the 153 new and touched tests with GIL off and on; the full suite in six runs, 13287 passed,
    32 skipped, 12 xfailed, 2 xpassed (both pre-existing Fault B xpasses), 1 failed -
    test_generated_build_assets_are_stamped_for_the_live_version, the stamp the final rebuild refreshes. The
    epic's probe on 0.2.8215 passes every variant (diagnostic with cache off, cold and warm; resident; root;
    unnamed lesser; unique; many; siblings isolated; both controls): after the consumer meld the provider
    reads resolution_required True with no plan, and its direct meld returns the consumer's instance.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:1654-1765
  - src/melder/aether/spellbook/spellbook_creation_system.py:1838-1908
  - src/melder/aether/conduit/meld/meld.py:966-1086
  - src/melder/aether/spellbook/spellbook.py:3804-3815
  - src/melder/aether/spellbook/spellbook.py:5392-5399
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py:140-173
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/green_new_tests_vm.log:1-4
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/green_new_tests_vm_gil1.log:1-12
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/suite_unit_rest_vm.log:1-41
  - context_compass/artifacts/injected_provider_direct_meld_20260930/runs_0_2_8215/diagnostic_cacheoff.txt:1-1
  IMPACT: The epic's diagnostic passes on source; what remains is the system docs, the graph, the release
    note and the rebuild, which also clears the one stamp failure.
  NEXT: Promote the patch docs into src_architecture, src_components and tests_components, update the graph
    descriptors and the release note, then rebuild the assets and LLM bundles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T19:56:47Z
  TYPE: FACT
  CLAIM: Citation audit before the docs pass: the system docs cite line numbers in three files this lane
    changed. The landing shifts spellbook.py by +2 after line 3811 and +6 after 5392, spellbook_creation_system.py
    by +6/+11/+83 after 1667/1753/1825, and meld.py by up to +67 after 1019 - but most spellbook.py and meld.py
    citations were already stale at 0.2.8214 (2 to 14 lines, and meld.py's "every self._lock site" ranges no
    longer held its lock sites). Checked by symbol against the landed files: the notch, add and remove entries
    and seams (3650/3701/3843/3876/4019/4051), the admits comment (3686), _conjured reads (667, 725),
    _settle_or_inherit_conjure_mode (6516-6559), conjure's effective-mode line (6772), _run_structural_phases
    (7135, precondition 7146), the cache-emit re-check (1055-1066), the configuration-mismatch log (5615-5621),
    bind (5176-5188), the conduit property (6448); _run_scheduler_with_phases (2055, its lock 2083); meld.py lock
    sites (276, 377, 1481-1679), the dirty-root raise (1167-1175), _gated_validation_required (1134).
    Citations into untouched regions (spellbook_creation_system.py 242-260, 517-544, 616-723, 1253-1292) hold.
  EVIDENCE:
  - system_docs/src_architecture.md:428-442
  - system_docs/src_architecture.md:1272-1332
  - system_docs/src_components.md:458-468
  - system_docs/src_components.md:528-548
  - system_docs/src_components.md:3326-3331
  - src/melder/aether/spellbook/spellbook.py:3650-4136
  - src/melder/aether/spellbook/spellbook.py:6516-6559
  - src/melder/aether/spellbook/spellbook_creation_system.py:2054-2096
  - src/melder/aether/conduit/meld/meld.py:1134-1204
  IMPACT: The docs pass remeasures every citation into the touched files, not only the ones this landing
    moved; citations into other files stay out of scope.
  NEXT: Apply the docs pass to src_architecture, src_components and tests_components and regenerate their
    indexes.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T20:07:21Z
  TYPE: MEASURE
  CLAIM: Docs pass, part 1: src_architecture (meld-time gate step 5, the invariant, the failure mode, the code
    map, remeasured citations, the handoff entry) and src_components (the rebuild-window producers, a dated
    "Injected dependencies" block and a lazy-validation bullet in Meld Resolution Runtime, a Phase-5 publication
    bullet in SpellCompiler, the Meld Runtime Gating contract, step 4 of the meld-time flow, the code-map
    extents of spellbook.py and meld.py, the handoff entry) carry option B; both indexes --check OK. The
    src_components edit ran before this session's re-onboarding (disclosed in the attestation). Re-verified: it
    had put the new block between the rebuild-window EVIDENCE and a trailing unresolved-input EVIDENCE bullet,
    so the block now follows that bullet and the old adjacency is restored. Every line citation into
    spellbook.py, spellbook_creation_system.py and meld.py in the four system docs was re-checked by symbol on
    the landed files (spellbook.py 267, 286, 667, 725, 1055-1066, 3650-4136, 5176, 5615-5621, 6448, 6516-6559,
    6772, 7135/7146; the creation system 2055-2083; meld.py 24-27, 276-377, 1134, 1167-1175, 1481-1679). The
    added text names no tooling path.
  EVIDENCE:
  - system_docs/src_architecture.md:728-743
  - system_docs/src_architecture.md:909-923
  - system_docs/src_architecture.md:1398-1402
  - system_docs/src_components.md:3194-3198
  - system_docs/src_components.md:3220-3245
  - system_docs/src_components.md:3514-3520
  - system_docs/src_components.md:3709-3720
  - system_docs/src_components.md:6112-6127
  - system_docs/src_components.md:6933-6942
  IMPACT: The two source documents describe the landed behaviour; tests_components (the two new test files),
    the graph descriptors, the release note, the patch archive and the rebuild remain.
  NEXT: Add the new component and unit test files to tests_components (Protects bullets, Key Files, code map,
    counts) and regenerate its index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T20:11:25Z
  TYPE: MEASURE
  CLAIM: Docs pass, part 2: tests_components carries the lane's two new files - a Protects bullet and a Key File
    in the Spellbook Runtime And Binding Unit Cluster (the target-pass flags; the deferred-lane rows in the aether
    tree's test_meld.py named there) and in the Aether Component Cluster (the first direct meld across scopes,
    lifetimes, caching and the SpellSpace door, with both controls) - plus measured code-map entries; the C1 core
    set is the key-file union again at 204 paths and the index --check is OK. Remeasured tier counts had drifted
    with earlier lanes' files, now corrected: unit 468 test modules among 471 .py (was 462/465; aether 186,
    crystallizer 46, spellbook 142, utilities 52), component 149/151 (was 141/143; aether 65, spellbook 72),
    integration 149/156 (was 142/149; aether 38 outside rift, conduit 36, crystallizer 15, spellbook 48), 766
    CI-tier modules in all (was 745); the other stated counts were checked and hold.
  EVIDENCE:
  - system_docs/tests_components.md:949-978
  - system_docs/tests_components.md:1121-1152
  - system_docs/tests_components.md:2020-2024
  - system_docs/tests_components.md:2231-2235
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/apply/apply_docs_tests.py:1-177
  IMPACT: The three system documents are done; tests_architecture's own tier counts (unit 465 .py) lag too, a
    pre-existing gap outside this lane's documents.
  NEXT: Re-extract the graph descriptors for meld.py and spellbook_creation_system.py with --strict, author the
    Meld and SpellbookCreationSystem responsibilities, accept those nodes, then reassemble and verify the index.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T20:15:34Z
  TYPE: MEASURE
  CLAIM: Graph: the extractor (--strict, Python 3.14.7, 584 descriptors, skipped 0, orphaned 0) refreshed the
    mechanical tier (SpellbookCreationSystem lists flag_dependencies_without_own_plan among its public methods);
    one authored responsibility each on Meld (the deferred lane's routing and verdict check) and
    SpellbookCreationSystem (the success-path flag, under the dependency's spell lock); the extractor re-run
    normalized the two descriptors and src_graph.md was reassembled (27569 lines, all 584 ranges verified, index
    line count and hash recomputed and equal, no tooling path). The CreationContextRebuild and Spellbook prose
    still holds (neither states the old lane rule). As in earlier lanes the touched nodes are not accepted: they
    stay SEMANTICS_STALE with the rest of the pre-existing census (204 stale, 9 unsemantic).
  EVIDENCE:
  - system_docs/src_graph.md:5517-5600
  - system_docs/src_graph.md:15430-15500
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/apply/apply_graph_semantics.py:1-42
  IMPACT: The generated graph names the lane's two behaviours; the release note, the patch archive and the
    rebuild remain.
  NEXT: Add the release-note section and bump the header to 0.2.8215, then archive the patch docs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-30T20:17:20Z
  TYPE: MEASURE
  CLAIM: Release note and patch archive: release_docs/next_version_release.md reads "# Melder 0.2.8215" and gains
    "Fixed: a class bound after conjure melds directly after it was injected" (symptom, cause in user terms, the
    example, what stays the same) before Packaging and documentation, which gains a system-documents bullet and
    the rebuild line for 0.2.8215; CRLF kept (335 lines, 335 CR). The example ran as written in the VM mirror
    (Python 3.14.7t, GIL off): the direct meld returns the consumer's instance (True, value 7). The four patch
    docs moved with mv -n to system_docs/patches/completed/injected_provider_first_direct_meld_2026_09_30/; the
    artifact board row and this task's Artifact Links point there, and the PLAN note's patch citations
    (19:31:23Z) now resolve under patches/completed/ with the same line ranges.
  EVIDENCE:
  - release_docs/next_version_release.md:282-306
  - release_docs/next_version_release.md:308-335
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/release/release_example.py:1-23
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/apply/apply_release_note.py:1-59
  - system_docs/patches/completed/injected_provider_first_direct_meld_2026_09_30/architecture_patch.md:1-59
  - artifact_board.md:67-67
  IMPACT: Everything before the rebuild is in place; the rebuild is the last write of the lane.
  NEXT: Sync the system docs and release note into the VM mirror, run the asset runner there, copy the assets
    back, run the asset --check on the device, then the LLM builder with --check.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-30T20:21:24Z
  TYPE: MEASURE
  CLAIM: Rebuild, last: the system docs and the release note were copied byte-for-byte into the VM mirror, the
    asset runner wrote the three manifests there at v0.2.8215 (bind guard 619 entries, unchanged; 460 agent
    documentation entries; 4 system documents), copy_back_assets.py copied the 8 changed manifest and payload
    files to the device keeping CRLF, and the device's asset --check prints OK for all three. The LLM builder on
    the device (--include-untracked, GIT_OPTIONAL_LOCKS=0) rewrote the src, tests and other bundles and its
    --check prints OK for all three; no .git/index.lock was left. After the rebuild the mirror passes the
    package-root unit files with the stamp test, build_assets and the agent-text reader component test: 280
    passed, 24 skipped - the one failure of the landing run is gone.
  EVIDENCE:
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/rebuild_assets_vm.log:1-3
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/copy_back_assets.log:1-8
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/check_assets_device.log:1-3
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/rebuild_llm_device.log:1-4
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/check_llm_device.log:1-3
  - context_compass/artifacts/injected_provider_first_direct_meld_20260930/runs/post_rebuild_package_root_vm.log:1-6
  IMPACT: The lane is complete on the tree at 0.2.8215 and waits on the owner's review and turn-in; work
    package D (MelderOps revalidation) follows the owner's wheel delivery.
  NEXT: Owner reviews and turns in this task; then D on the owner's wheel delivery.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-30T21:18:29Z
  TYPE: DECISION
  CLAIM: Turned in on the owner's directive (chat): "you can close that epic if its done". Work package D
    rebuilt and installed the 0.2.8215 wheel in MelderOps' environments and the epic's unchanged diagnostic
    passes on it (red on 0.2.8212 in the same env), so the acceptance this task waited on is met; the board
    rows move to closed anchors and the artifact rows to cleared. melder_0 releases M0-146..148.
  EVIDENCE:
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_0_2_8215.log:1-14
  - context_compass/artifacts/wheel_0_2_8215_20260930/diagnostics_control_0_2_8212.log:1-15
  IMPACT: Option B is delivered and closed; nothing of this lane remains open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Turned in 2026-09-30T21:18:29Z on the owner's directive after work package D.
Opened 2026-09-30T19:07:02Z on the owner's pick (option B, regression tests first). Regression and unit tests
went red, then green; option B landed at 2026-09-30T19:44:38Z as 0.2.8215 (NOTICE M0-149..151), the full suite
and the epic's probe green in the VM. The docs pass (src_architecture, src_components, tests_components), the
graph, the release note section, the patch archive and the rebuild followed; asset and LLM --check OK.
In review since 2026-09-30T20:21:24Z (NOTICE M0-152..154): the owner's turn-in remains; work package D (MelderOps
revalidation) waits on the owner's wheel delivery. melder_0 stays the only writer of the lane's files until
the turn-in.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
