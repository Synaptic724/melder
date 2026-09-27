

# Task: Implement the Aether conduit lookup API - root renames, any-conduit lookups, Cloud listing, migration, notch

## Metadata
- Task ID: TASK-2026-09-27-implement-aether-conduit-lookup-api
- Story: all eleven stories of EPIC-2026-09-27-aether-conduit-lookup-api (one change set, one 0.01 notch)
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p1
- Created: 2026-09-27T10:41:49Z
- Updated: 2026-09-27T12:18:07Z

## Objective
Land the owner-approved API in one change: the eight root-only Aether lookups become `*_root_*` names; the reused
`get_conduit_by_name` answers over NAMED scopes and `get_conduit_by_id` over LIVE conduits, both frame-scoped with
`aetheric_frame_name: str = "default"`; one shared frame resolver raises TypeError for a non-string frame and every
not-found error names the searched frame; `ConduitCloud.list_conduits()` returns a NAMED snapshot; every recorded
usage migrates (TransferOfOwnership stays root-only; the CommandSystem and StaticFrameViewer copies collapse into
`get_conduit_by_id`); tests, docs, system docs, graph, release note and one 0.01 notch.

## Ticket Contract
- ENTRY_GATE: owner approval (chat 2026-09-27, "go ahead and implement all this"); patch docs written under
  `system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/`, linked here, read in order and mapped in
  Notes before any src edit; board row routes here.
- EXECUTION_BOUNDARY: src/melder/aether/aether.py (lookup family, frame resolver);
  src/melder/aether/aetheric_frame/conduit_cloud.py (list_conduits); src/melder/nexus/rift/command_system/
  command_system.py (_get_conduit_by_id_locked); src/melder/nexus/rift/frame_viewer/static_frame_viewer.py
  (_get_owner_conduit); src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py
  (_collect_impacted_conduit_ids); the surveyed tests and benchmark; one new regression test file; ConduitCloud
  tests; docs/intermediate/scopes.md; system docs, indexes and graph; the release note; `__version__`.
- DEPENDENCIES: epic decisions (Notes of tickets/epics/2026-09-27_aether_conduit_lookup_api_epic.md); NOTICEs
  to the active agents before the notch.
- EXIT_GATE: regression test red on 0.2.78 and green after; affected suites green on 3.14t and GIL; survey recount
  shows no retired name in hand-written code; docs, indexes and graph current; notch and release note; owner
  acceptance.
- FAILURE_ESCALATION: DECISION_REQUEST when a usage needs behaviour other than the approved design; BLOCKER when
  the graph or asset tooling cannot run on the device tree.

## Scope Boundaries
- In scope: everything in EXECUTION_BOUNDARY.
- Out of scope: Nexus and FrameViewer methods that share these names (their own semantics), named-lesser
  lifecycle, build-asset and LLM-bundle regeneration unless a suite requires it (then raise it).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner instruction in chat, 2026-09-27 ("yeah go ahead and implement all this please").

## Steps / Checklist
- [x] Patch docs (architecture, components, code description for the LIVE walk); linked; mapping note.
      (Patch docs are not indexed, as in the archived lanes.)
- [x] VM worktree; baseline of the affected suites on unmodified 0.2.78.
- [x] Regression test first (red on 0.2.78).
- [x] Implement src changes; migrate every surveyed usage; unit and ConduitCloud tests.
- [x] Suites green on 3.14t and GIL; byte-identical apply to the device tree.
- [x] Promote patch docs into src_components, src_architecture and tests_components; indexes; graph.
- [ ] scopes.md; release note; `__version__` 0.01 notch; NOTICEs; survey recount.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The API change, migrated usages, tests, docs, promoted system docs, graph, release note and notch.

## Files / Paths Impacted
- See EXECUTION_BOUNDARY; exact list with line ranges in the PLAN note before src edits.

## Validation
- Not run.
- Recommended commands: in the PLAN note.

## Risks / Rollback Notes
- Rollback is a revert of one change set; the rename is a hard break, so all in-repo callers move in it.
- The LIVE walk must not iterate live ward dicts (two-lock guard, free-threaded build).

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.
- [ ] No behaviour claim cited to a search hit; every range covers the logic that was read.
- [ ] No drive-by refactors outside the listed methods.

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
  - system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/
  - artifacts/aether_conduit_lookup_api_impl_20260927/
- DISPOSITION: promote_to_documentation (patch lane); retain_as_reference (implementation evidence: suite logs,
  shard runner, apply scripts)
- CLEANUP_TRIGGER: task closure (promote, then archive the patch lane; keep the evidence folder)

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
- DATETIME: 2026-09-27T10:41:49Z
  TYPE: DECISION
  CLAIM: Owner approved implementation of the whole epic (chat, 2026-09-27), including the shared frame resolver for
    all ten lookups (TypeError for a non-string frame) and not-found errors that name the searched frame. One change
    set, one 0.01 notch above the version current at landing (0.2.78 now).
  EVIDENCE: tickets/epics/2026-09-27_aether_conduit_lookup_api_epic.md
  IMPACT: Implementation may start once the patch-doc entry gate is met.
  NEXT: Read the patch-doc contracts and an archived patch lane, then write this lane's patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T10:46:28Z
  TYPE: FACT
  CLAIM: Change-surface facts beyond the public-name survey. (1) The private root-id helper `_get_conduit_by_id`
    is also called by Aether._get_conduit_by_spell_id and twice by StaticCommandSystem, all to reach a spell's
    OWNER conduit (roots only, since lessers own nothing); integration tests call both private helpers. (2)
    ConduitWard._get_lesser_conduit is also used by Conduit.get_lesser_conduit; hard teardown deletes a
    conduit's `_conduit_ward` (lesser and root paths) but never `_id`; the ward unit test uses `_conduit_ward =
    None` as a leaf. (3) CommandSystem reports a missing frame through _get_required_runtime_frame ('Aetheric
    frame X does not exist.') and a missing id as "Conduit id 'X' was not found in frame 'Y'." (4) dict.copy()
    is atomic on 3.14.7t (0.2.72 probe: 0 failures in 20,000 rounds against 19,981 for live iteration). (5)
    Asset-currency tests exist (tests/unit/melder/build_assets, test_package_version_metadata,
    test_system_documents), so the notch and doc edits likely need the asset rebuild in this lane.
  EVIDENCE:
  - src/melder/aether/aether.py:1984-2022
  - src/melder/nexus/rift/command_system/static_command_system.py:206-224
  - src/melder/nexus/rift/command_system/static_command_system.py:628-635
  - src/melder/aether/conduit/conduit.py:5453-5470
  - src/melder/aether/conduit/conduit.py:827-845
  - src/melder/aether/conduit/conduit.py:949-968
  - tests/unit/melder/aether/conduit/conduit_ward/test_conduit_ward.py:606-617
  - src/melder/nexus/rift/command_system/command_system.py:1679-1695
  - context_compass/tickets/tasks/completed/2026-09-26_snapshot_phase5_live_spell_pool_task.md:187-200
  IMPACT: Adds three private-helper migrations (root-only), fixes the walk at its source in ConduitWard
    (snapshot per level, skip a scope whose ward was deleted), and keeps CommandSystem's two error messages
    exact.
  NEXT: Write the patch docs (architecture, five components, ward-walk code description).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T10:48:24Z
  TYPE: PLAN
  CLAIM: Patch docs written, linked and read in order (architecture -> five components -> ward-walk code
    description). Mapping, patch section -> implementation step -> validation step:
    - ConduitWard snapshot walk -> ConduitWard._get_lesser_conduit copies each level, skips deleted wards ->
      new deterministic mutation-during-walk and deleted-ward unit tests (red on 0.2.78), existing walk tests.
    - ConduitCloud list_conduits -> new method under the leaf lock -> Cloud unit tests (identity, anonymous and
      returned scopes absent, cleaned raises).
    - Aether resolver + ROOT renames -> `_resolve_lookup_frame`, eight `*_root_*` methods, private helpers renamed,
      `_get_conduit_by_spell_id` on the root helper -> migrated test_aether.py tests, TypeError over all ten,
      retired-name absence test.
    - Aether NAMED/LIVE -> reused `get_conduit_by_name` (Cloud) and `get_conduit_by_id` (root map snapshot + ward
      walk) -> unit delegation tests; integration regression file (automatic/dynamic, nested, anonymous, returned,
      custom and default frame), red on 0.2.78.
    - Callers -> TransferOfOwnership and StaticCommandSystem on root names; CommandSystem and StaticFrameViewer on
      the LIVE lookup with their messages kept -> transfer, Nexus command and viewer suites unchanged and green.
    - Docs/version -> src_components, src_architecture, tests_components, indexes, graph, scopes.md, release note
      breaking-change bullets, one 0.01 notch -> index --check, graph verification, asset-currency suites.
    Work runs in a VM worktree; the device tree receives byte-identical files after green suites.
  EVIDENCE:
  - context_compass/system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/architecture_patch.md:28-44
  - context_compass/system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/architecture_patch.md:54-60
  - context_compass/system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/architecture_patch.md:64-73
  IMPACT: Entry gate satisfied (patch docs exist, linked, mapped); src edits may start in the worktree.
  NEXT: Build the VM worktree and baseline the affected suites on unmodified 0.2.78.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:15:21Z
  TYPE: MEASURE
  CLAIM: Baseline on unmodified 0.2.78 (wt_base; src and tests byte-identical to the device tree): 3.14.7t with
    PYTHON_GIL=0 over the whole tests/ tree (13,001 collected) is green except one environment-only collection
    error (tests/unit/github_workflows/test_workflow_contracts.py imports PyYAML, absent from the VM venv). The
    3.14.7 GIL build is green on the affected subset (aether unit/integration/component, component spellbook,
    conduit and crystallizer integration, asset-currency and llm_support tests). The device VM ends background
    jobs with each call, so suites run as per-call shards (run_shards.sh). Worktree $HOME/wt matches the device
    tree (src, tests, benchmarks, docs, release_docs, llm_support: 0 differences).
  EVIDENCE:
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/suites_baseline_0278_vm.txt:3-41
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/run_shards.sh:1-22
  IMPACT: A post-change failure anywhere but test_workflow_contracts.py is this change's; the GIL venv
    ($HOME/.venv314, pytest 9.1.1) serves the GIL runs.
  NEXT: Re-read the patch lane, then write the regression test and prove it red on wt_base.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T11:19:00Z
  TYPE: MEASURE
  CLAIM: The new regression file (13 tests) run against unmodified 0.2.78 is red for the MF7 symptoms: 12 fail -
    named lessers raise 'Conduit with name group-lookups not found.' from the root-only lookup; anonymous and
    nested lessers raise 'Conduit with signature <id> not found.'; the *_root_* names do not exist; None and 7 as a
    frame produce "Aetheric frame 'None' does not exist." after a KeyError; not-found messages name no frame;
    ConduitCloud has no list_conduits. The missing-custom-frame guard passes (contract unchanged by design).
  EVIDENCE:
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/regression_red_0278_vm.txt:1-55
  - tests/integration/melder/aether/test_aether_named_lesser_lookup.py:1-145 (VM worktree; lands with the change)
  IMPACT: The file proves each approved behaviour change; it must be green after the change on 3.14t and GIL.
  NEXT: Implement the ConduitWard snapshot walk and ConduitCloud.list_conduits in the worktree.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T11:20:31Z
  TYPE: PLAN
  CLAIM: Step 1 implemented in the worktree (migration order 1, additive): ConduitWard._get_lesser_conduit walks
    `self._lesser_conduits.copy()` per level and skips a child whose `_conduit_ward` was deleted (AttributeError),
    keeping the None-leaf check; ConduitCloud.list_conduits() returns `tuple(self._named_conduits.values())` under
    the Cloud lock, placed after list_conduit_names. Both with contract docstrings. Edits go through a
    line-ending-preserving helper because the files mix CRLF and LF (apply script kept in the VM, filed at apply).
  EVIDENCE:
  - context_compass/system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/code_description_patch_conduit_ward_and_contracts.md:6-34
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1220-1268 (worktree)
  - src/melder/aether/aetheric_frame/conduit_cloud.py:578-610 (worktree)
  IMPACT: The LIVE lookup can delegate to the ward walk; unit tests for both follow with the test tranche.
  NEXT: Aether: frame resolver, eight *_root_* methods, NAMED and LIVE lookups, spell-owner helper.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T11:23:14Z
  TYPE: MEASURE
  CLAIM: Step 2 implemented in the worktree (migration order 2): `Optional` added to the typing import;
    `_resolve_lookup_frame` (TypeError for a non-str frame, else `_get_existing_frame`); eight `*_root_*` methods
    (count/has now read the registry directly instead of building the id list, same answers;
    `find_root_conduit_id_by_name -> Optional[str]`); NAMED `get_conduit_by_name` delegating to the frame Cloud
    and re-raising with the frame named; LIVE `get_conduit_by_id` over `_find_live_conduit` (root-map copy, then
    each root ward's snapshot walk); private `_get_root_conduit_by_name` / `_get_root_conduit_by_id` with
    frame-naming messages; `_get_conduit_by_spell_id` resolves owners through the root helper. With steps 1-2,
    the regression file goes from 12 red to 13 green on 3.14t.
  EVIDENCE:
  - src/melder/aether/aether.py:1643-2107 (worktree: resolver, root family, NAMED, LIVE, walk helper)
  - src/melder/aether/aether.py:2135-2215 (worktree: private root helpers)
  - src/melder/aether/aether.py:2217-2256 (worktree: spell-owner helper)
  - context_compass/system_docs/patches/active/aether_conduit_lookup_api_2026_09_27/component_patch_aether_singleton.md:11-26
  IMPACT: Old names no longer exist on Aether, so the four src callers and the surveyed tests must move now.
  NEXT: Migrate TransferOfOwnership, StaticCommandSystem, CommandSystem and StaticFrameViewer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T11:40:21Z
  TYPE: MEASURE
  CLAIM: Steps 3-4 done in the worktree and green. Callers: TransferOfOwnership sweeps list_root_conduit_ids /
    get_root_conduit_by_id (comment records the root-only ruling); StaticCommandSystem resolves spell owners with
    get_root_conduit_by_id; CommandSystem._get_conduit_by_id_locked delegates to Aether.get_conduit_by_id and keeps
    its frame error and "Conduit id 'I' was not found in frame 'F'." (now chained); StaticFrameViewer returns
    Aether.get_conduit_by_id or None. Tests: 17 files (surveyed sites plus fakes the call-site survey could not
    see - FakeAether methods, SimpleNamespace `_aether` stubs, monkeypatch strings in test_nexus.py and the
    static/transfer suites); new: regression file (13), resolver TypeError over all ten lookups x3, retired-name
    absence x8, NAMED/LIVE unit tests, Cloud list_conduits x2, ward snapshot and deleted-ward tests (both red on
    0.2.78: RuntimeError 'dictionary changed size during iteration', AttributeError), CommandSystem missing-frame
    mapping. Results: 3.14t PYTHON_GIL=0 whole tree green (only the PyYAML collection error, as in the baseline);
    PYTHON_GIL=1 and the GIL build green on the affected subsets; gauntlet parity benchmark 5 passed.
  EVIDENCE:
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/suites_post_change_vm.txt:3-43
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/change.diff:1-2042
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/apply/apply_callers.py:1-226
  IMPACT: The change set is complete for src and tests; next is the device-tree apply, docs and the notch.
    Deliberately kept: tests/unit/melder/aether/conduit/conftest.py:202-203 and test_conduit_contracts.py:877 set
    `_get_conduit_by_id` / `_get_conduit_by_name` on a MagicMock Aether stub that no code path reads (the peer
    lookup under test uses the frame Cloud, conduit.py:6798-6845); pre-existing dead setup, reported, not edited.
    Also observed: the device tree's benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py changed at
    11:39Z (another writer); this lane does not touch it.
  NEXT: NOTICE the active agents, then copy the 24 changed files to the device tree after checking each target
    still equals the baseline copy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T11:41:29Z
  TYPE: FACT
  CLAIM: NOTICEs M0-55/56/57 sent to melder_1, fable_0 and melder_2 (alert lines added). The 24 changed files were
    copied from the worktree to the device tree after checking each device file still equalled the baseline copy
    (and the new regression file did not exist); every copy then compared byte-identical (cmp). The device tree
    now differs from the worktree only in benchmarks/testing_other_di/test_persistent_runtime_gauntlet.py, the
    other writer's 11:39Z edit this lane does not touch.
  EVIDENCE:
  - context_compass/mailbox_board.md:161-194
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/change.diff:1-2042
  IMPACT: The API change is live in the owner's tree at 0.2.78 until the notch; docs, graph and release note next.
  NEXT: Read the design_engineer authoring instructions, then promote the patch lane into the system docs.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-27T11:47:40Z
  TYPE: FACT
  CLAIM: Patch lane promoted after reading the src_components, src_architecture and tests_components authoring
    instructions (on-demand trigger). src_components: Aether C3 responsibilities/invariants/failure modes, Cloud
    listing in AethericFrame Services, the snapshot walk in ConduitWard concurrency, the Nexus getter wording, a
    new C2 "Subcomponent: Aether Conduit Lookups", C2 Cloud/transfer/viewer/command-system lines, a new "Flow: Aether
    Conduit Lookup by Name or Id", seven C1 ranges remeasured, and citations this lane shifted
    (transfer_of_ownership.py:951/1442 -> 953/1444, conduit_ward.py:2483-2537 -> 2508-2562, the Cloud's stale :547
    -> :720). src_architecture: boundary bullet, "Conduit lookup coverage" invariant, failure-mode bullet, "Conduit
    Lookup Coverage" diagram (ASCII + Mermaid), C1 ranges, handoff entry. tests_components: regression file in the
    Aether Integration Cluster with a C1 entry, command-direct range, handoff entry. Content-preservation diff shows
    only the replaced lines; no package paths added; indexes regenerated and --check OK (147/56/65 sections);
    the citation recipe reports no missing or out-of-bounds range.
  EVIDENCE:
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/apply/apply_docs.py:1-368
  - context_compass/agent_onboarding/default/design_engineer/skills/src_components_instructions.md:303-378
  IMPACT: Canonical docs describe 0.2.79 behaviour. Observed, not fixed (pre-existing, outside this lane):
    src_components cites conduit_ward.py:799/973 and :957-975 for SafeGuard sites that now sit at 834/1008.
  NEXT: Regenerate the graph descriptors for the seven changed modules on a VM copy and reassemble.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T11:54:05Z
  TYPE: MEASURE
  CLAIM: `__version__` 0.2.78 -> 0.2.79 (device and worktree); release note header 0.2.79 plus a section "Aether
    finds any conduit by name or id; root-only lookups carry root names" with Breaking-change bullets (its code
    example was run against the worktree: named lesser by name, anonymous lesser by id, frame-naming ValueError,
    TypeError for None, AttributeError for a retired name); docs/intermediate/scopes.md gains the Aether paragraph.
    Graph: re-extracted on a VM copy (583 descriptors, --strict, 0 skipped), one responsibility added to each of
    the seven changed nodes, the three nodes this lane made stale (TransferOfOwnership, StaticCommandSystem,
    StaticFrameViewer) re-read and accepted, stale count back to the pre-lane 145, reassembled (27,524 lines,
    584 sections, index verified). 18 of the 25 rewritten descriptors changed only in the mechanical tier from
    other lanes' earlier source edits (version, build assets, compiler phases, validation strategies). With the
    synced docs, the asset-currency set is green except test_generated_build_assets_are_stamped_for_the_live_version:
    the build assets are stamped 0.2.78.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - release_docs/0.2.77.md:1-3
  - release_docs/0.2.77.md:25-67
  - context_compass/artifacts/aether_conduit_lookup_api_impl_20260927/apply/apply_graph_semantics.py:1-50
  IMPACT: One owner decision remains - the build-asset (and LLM-bundle) rebuild for 0.2.79 that the version-stamp
    test needs; this task scoped it as "raise it" and earlier lanes rebuilt only on the owner's word.
  NEXT: Ask the owner whether to rebuild the build assets and LLM bundles for 0.2.79 now.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T12:11:14Z
  TYPE: DECISION
  CLAIM: Owner decision (chat, 2026-09-27, answering the rebuild question): rebuild the build assets AND the LLM
    bundles for 0.2.79 in this lane, update the release note's asset line, rerun the asset-currency suites and the
    full tree, then report. This lifts the Scope Boundaries exclusion of asset and bundle regeneration, which the
    previous note raised. Taken after the post-compaction REONBOARD (self-certified as melder_0 per the owner's
    standing instruction); the question itself was asked before the re-onboard, a slip reported to the owner.
  EVIDENCE: context_compass/tickets/tasks/2026-09-27_implement_aether_conduit_lookup_api_task.md:324-346
  IMPACT: The version-stamp test can go green; the builders write generated files (build assets under
    src/melder/_build_assets, the llm_support bundles) that must be built from the synced 0.2.79 docs and graph.
  NEXT: Read _build_asset_runner.py and llm_support/_builder.py in full, plus the procedure the 0.2.74 rebuild
    used, before running either builder.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-27T12:16:35Z
  TYPE: PLAN
  CLAIM: Both builders read in full; rebuild plan. (1) The asset runner discovers _agent_documentation,
    _bind_guard and _system_documents. The first two hash and harvest every src/melder .py; the third verifies the
    architecture, components and graph documents against their indexes, then writes a section index, three payload
    modules, the graph adjacency module and the manifest. write_payloads unlinks the old payloads first, which the
    connected folder refuses (the 0.2.74 lane hit it), so the runner runs in the VM worktree, whose src .py files
    and system docs equal the device's (diff at 12:12Z; only test .melc caches differ). Its eight outputs are
    converted to CRLF like the committed files (all eight are CRLF on the device) and copied back after re-checking
    that the device inputs and outputs did not move. (2) llm_support/_builder.py needs .git and reads the working
    tree, so it runs on the device with GIT_OPTIONAL_LOCKS=0 (git ls-files only); it writes through a temporary
    file and os.replace, no delete. The only untracked, non-ignored file outside context_compass is this lane's
    regression test, so --include-untracked adds exactly that file, and a plain --check reports the tests corpus
    stale until the owner commits it. (3) Another writer's edits to two benchmark gauntlet files (11:52Z) enter
    only the LLM "other" corpus, as they stand at build time. Then: release note (lookup coverage in the packaged
    system-documents bullet; asset line 0.2.78 -> 0.2.79), asset-currency suites on 3.14t and GIL, full tree on
    3.14t.
  EVIDENCE:
  - src/melder/_build_assets/_build_asset_runner.py:246-362
  - src/melder/_build_assets/_system_documents/_builder.py:374-435
  - src/melder/_build_assets/_system_documents/_builder.py:542-627
  - src/melder/_build_assets/_system_documents/_builder.py:974-1002
  - llm_support/_builder.py:222-242
  - llm_support/_builder.py:243-312
  - llm_support/_builder.py:703-766
  - context_compass/tickets/tasks/completed/2026-09-26_remove_nested_slot_guard_take_task.md:436-477
  IMPACT: The version-stamp test turns green without deletes on the device. The LLM bundles describe the working
    tree at build time, including one untracked file and another lane's edits.
  NEXT: Run the asset runner in the worktree, convert to CRLF, --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-27T12:18:07Z
  TYPE: MEASURE
  CLAIM: Build assets rebuilt at v0.2.79. In the worktree the runner wrote agent documentation (460 entries), bind
    guard (619, unchanged) and system documents (4; no pair refused); the eight outputs were converted to CRLF and
    --check was OK (schema 2.0.0, key match). Before copying, the device's src .py files and the six system-document
    files still equalled the worktree and its eight outputs still equalled the VM backup (asset_backup_0278). After
    copying, all eight compare byte-equal and the device --check is OK. What moved: version stamps and source keys;
    the architecture and components proofs (3044 -> 3087 and 9841 -> 9913 lines) and the graph's (27517 -> 27524);
    the section index (784 -> 787 sections: the lookup-coverage diagram, the Aether Conduit Lookups subcomponent and
    the lookup flow); the payload texts. Graph adjacency changed only its version stamp (no edge moved).
  EVIDENCE:
  - src/melder/_build_assets/_system_documents/manifest/system_documents_manifest.py:1-82
  - src/melder/_build_assets/_system_documents/manifest/system_documents_index.py:1-818
  - src/melder/_build_assets/_bind_guard/manifest/bind_guard_manifest.py:1-641
  IMPACT: The version-stamp test's input is current. As after the 0.2.72 and 0.2.74 rebuilds, the graph descriptors
    of the eight asset modules lag one rebuild (their source hashes sit inside the graph payload).
  NEXT: LLM bundles on the device: --include-untracked with GIT_OPTIONAL_LOCKS=0, then --check with and without it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Implementation lane opened 2026-09-27 for the whole epic. Next: patch docs (entry gate), then a VM worktree, a red
regression test, the src change and migrations, suites on 3.14t and GIL, docs, graph, release note and notch.

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
