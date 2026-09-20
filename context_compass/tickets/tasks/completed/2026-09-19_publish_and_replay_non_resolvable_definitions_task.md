# Task: Publish non-resolvable graph definitions and preserve their policy on replay

## Completion
- Completed: 2026-09-20T00:25:59Z
- Summary: Delivered Nexus publication and crystal replay; integrated qualification and final follow-up repairs are retained.
- Acceptance: Owner requested turn-in, then required two repairs first; both are verified.

## Metadata
- Task ID: TASK-2026-09-19-publish-and-replay-non-resolvable-definitions
- Story: STORY-2026-09-19-discoverable-nexus-graph-and-history
- Related Story: STORY-2026-09-19-discoverable-registration-persistence
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-19T22:33:02Z
- Updated: 2026-09-20T00:25:59Z

## Objective
Complete Nexus publication and Crystallizer capture/replay using native registration capability,
descriptive socket references and existing version/identity machinery.

## Ticket Contract
- ENTRY_GATE: Owner requested completion; board routes here. Consume S5/S6 component/source routes
  and create/read patch contracts before implementation.
- EXECUTION_BOUNDARY: Nexus payload/view navigation, crystal policy capture, restore/graft forwarding,
  record compatibility, focused graph/history/replay tests and docs/assets.
- DEPENDENCIES: S2/S3 and direct admission implemented. Runtime supplied-value compatibility passes
  32 tests with ordinary constructor errors; no new argument preflight.
- EXIT_GATE: False definitions/reference relationships are visible through authorized views;
  capture/replay/graft preserve capability and existing version rules; regression checks pass.
- FAILURE_ESCALATION: No source-body identity redesign, arbitrary-object serialization, ownership
  change or invented architectural edges. Preserve unrelated work.

## Scope Boundaries
- In scope: existing descriptor/graph and record/replay consumers of the accepted native policy.
- Out of scope: custom argument preflight and pre-existing eager whole-child construction behavior.

## Steps / Checklist
- [x] Read profile/publication/view and capture/replay/record-version owners.
- [x] Create indexed patch contracts and source/test mapping.
- [x] Establish graph/capture/replay failures and implement native propagation.
- [x] Verify authorized graph/history and active/staged/legacy/graft replay.
- [x] Run focused compatibility, regenerate docs/assets and synchronize full-feature handoff.

## Validation
- Final selected-scope results: 8055 distinct passed, one existing skipped, four existing xfails.
- 39 documentation tests and the strict 294-page build pass; site check validates 35,513 local links.
- Versioned graph selection/history/source test passes; source assets and LLM bundles regenerated.
- Full repository suite and coverage: Not run. Exact commands/reports/limits are retained below.
- Use .venv_new through uv --no-sync --offline, -X gil=0, pytest cacheprovider disabled.

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: Owner-authorized turn-in after delivered scope and reported failure repairs passed.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- PATCH_ID: non_resolvable_graph_replay_2026_09_19
- ARTIFACT_PATHS:
  - artifacts/non_resolvable_graph_replay_20260919/
  - artifacts/non_resolvable_graph_replay_20260919/validation.md
  - system_docs/patches/completed/non_resolvable_graph_replay_2026_09_19/architecture_patch.md
  - system_docs/patches/completed/non_resolvable_graph_replay_2026_09_19/component_patch_nexus.md
  - system_docs/patches/completed/non_resolvable_graph_replay_2026_09_19/component_patch_crystallizer.md
  - system_docs/patches/completed/non_resolvable_graph_replay_2026_09_19/code_description_patch_replay.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted closure; promote/archive patch contracts normally.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-19T22:33:02Z
  TYPE: FACT
  CLAIM: Nexus already passively publishes all active Spells after conjure through general profiles;
    payload enrichment can retain capability/reference metadata under existing ACL sections.
    SpellCrystal captures directly from the live Spell but omits resolvable. Restore active/staged
    binds forward other captured policy but currently lose that bool.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:495-572
  - src/melder/aether/spellbook/spellbook.py:5912-5990
  - src/melder/crystallizer/crystals/spell_crystal.py:260-294
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1907-2017
  IMPACT: Extend existing value carriers and public replay verbs, preserving ownership and ACLs.
  NEXT: Finish profile/view and record-version/graft reads, then implement the scoped regression patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:37:41Z
  TYPE: DECISION
  CLAIM: Use existing binding-payload ACL sections for capability and selected reference/base edges;
    add query-time visible incoming/outgoing navigation without a new graph registry. Crystal captures
    the native bool; five replay/graft bind sites forward it. Existing record major gating must advance
    to 2 so an older reader cannot discard False. Legacy absence stays True. No custom input preflight.
  EVIDENCE:
  - src/melder/nexus/frame_descriptor_manager.py:495-572
  - src/melder/nexus/rift/frame_viewer/view_spell.py:193-268
  - src/melder/crystallizer/persistence/record_version.py:74-174
  - src/melder/crystallizer/crystal_loader_system/graft_runner.py:372-548
  IMPACT: This is value propagation and query-time graph navigation; ordinary meld hot paths gain no work.
  NEXT: Consume indexed patch contracts and establish graph/capture/replay regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:40:58Z
  TYPE: DECISION
  CLAIM: Read and indexed the architecture, Nexus, crystal and control-flow patches. Mapping:
    capability/edges -> manager payload plus ViewSpell/FrameViewer -> real room navigation;
    native bool -> SpellCrystal describe/cleanup and five replay bind sites -> checkpoint/graft;
    compatibility -> RecordVersion major gate -> simulated old-reader refusal. New integration
    regressions use existing real-room and isolated-world cache fixtures, not mock graph assertions.
  EVIDENCE:
  - system_docs/patches/completed/non_resolvable_graph_replay_2026_09_19/architecture_patch.md:4-28
  - tests/integration/melder/aether/test_non_resolvable_graph_replay.py
  IMPACT: Implementation is bounded to existing publication and replay seams; no meld preflight.
  NEXT: Run the integration baseline, then implement only the missing native policy/graph transport.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:45:31Z
  TYPE: MEASURE
  CLAIM: Native crystal capture, active/staged/graft forwarding, record major 2, and Nexus relationship
    payload/query methods are implemented. The focused real run proves checkpoint disk reload preserves
    False and supplied consumer behavior, and an old reader refuses the new version. Two cases remain:
    codegen-room view cannot see the published definition, and live cross-frame graft hits existing
    global uniqueness. Sandbox pytest temporary-folder access failed; the same scoped run completed
    outside the sandbox with all artifacts under this task directory.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/integration.log:1-62
  - artifacts/non_resolvable_graph_replay_20260919/integration.xml:1-1
  IMPACT: Investigate current ACL/projection refresh and graft uniqueness contracts before further edits.
  NEXT: Resolve the two source-backed integration gaps, then broaden compatibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:47:32Z
  TYPE: FACT
  CLAIM: Existing Rift projections require explicit refresh after external binds. That restores node
    visibility, but the late consumer's descriptor was published before Phase3 produced its references.
    Republish through the book's existing enabled sink after successful Phase3. This is structural
    publication, not per-meld work. Graft now passes after releasing source claims before importing
    detached custody, preserving the documented process-wide uniqueness rule.
  EVIDENCE:
  - src/melder/nexus/rift/rift.py:589-629
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:900-1048
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1615-1633
  IMPACT: Add the narrowly scoped post-compilation publication hook; do not change projection or uniqueness policy.
  NEXT: Republish enabled late-compiled records and rerun graph/checkpoint/graft tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:50:16Z
  TYPE: MEASURE
  CLAIM: All four integration scenarios pass (26.11s): real Nexus incoming/reference/base navigation,
    direct refusal, checkpoint disk reload and re-emission, detached-custody active/staged graft,
    and old-reader refusal through the established major gate. Late Phase3 publication fixes the
    missing incremental reference; explicit Rift refresh and global uniqueness remain unchanged.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/integration_second.log:1-2
  - artifacts/non_resolvable_graph_replay_20260919/integration_second.xml:1-1
  IMPACT: Core graph and replay behavior is working. Next qualify compatibility and legacy/visibility edges.
  NEXT: Run affected Nexus/compiler/crystal compatibility and extend legacy/history checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T22:51:48Z
  TYPE: MEASURE
  CLAIM: Compatibility failures are native-fixture drift: 133 crystal failures/errors come from one
    DummySpell lacking resolvable; three Nexus doubles lack capability/topology, and one Phase3 book
    double lacks its native publication flag. The remaining 325 cases pass. Fixture constructors were
    read before alignment; no production fallback probes will be added. Real integration remains green.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/nexus_compat.xml:1-1
  - artifacts/non_resolvable_graph_replay_20260919/crystal_compat.xml:1-1
  - tests/mocks/crystallizer/spell_crystal_harness.py:17-39
  IMPACT: Update those existing doubles and wrap new-test imports, then rerun the same focused groups.
  NEXT: Align native fixture fields and rerun affected compatibility.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T23:02:09Z
  TYPE: MEASURE
  CLAIM: The broad compiler/runtime/Nexus run reports 7595 passed, 10 failed, one existing skip and
    one xfail. Nine failures are one earlier cache _RecordingSpell missing native resolvable, and
    one dump test expects the pre-S2 field set. Read both fixtures; align them with the delivered bool.
    The 499-case focused group already passed. The broader restore integration run is still active.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/broad.log
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:40-72
  - tests/component/melder/spellbook/test_spellbook_component_spellbook.py:1030-1099
  IMPACT: No production regression is shown by these ten failures; retain strict native runtime fields.
  NEXT: Repair these two compatibility fixtures and rerun their affected tests while completing documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T23:05:03Z
  TYPE: MEASURE
  CLAIM: The remaining cache/dump files pass all 91 cases after native-field/expected-shape updates.
    The full restore integration selection completed: 49 passed, three pre-existing graft-uniqueness
    xfails, and one stale literal record-version expectation. Update that expectation to CURRENT;
    keep the old graft tests' version assertion current so their xfails still reach the real conflict.
    New graph/history/legacy/staged/ACL cases passed in this run.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/remaining.log:1-3
  - artifacts/non_resolvable_graph_replay_20260919/replay.log
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:1577-1582
  IMPACT: No further production failure is shown by these runs. Rerun the changed assertions and source-read proof.
  NEXT: Finish targeted verification and source/docs/build synchronization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T23:26:03Z
  TYPE: MEASURE
  CLAIM: Integrated implementation is review-ready: 8055 distinct selected tests pass with one
    pre-existing skip and four pre-existing xfails. The strengthened real Nexus test also proves
    source/history access, parked version recording and updated graph links after notch, retaining
    old history. All 39 docs tests, the 294-page build and 35,513-link site check pass in the existing
    pinned docs environment. Source assets and src/tests/other bundles are regenerated.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md
  - artifacts/non_resolvable_graph_replay_20260919/version_graph.log:1-2
  - artifacts/non_resolvable_graph_replay_20260919/docs_tests_green.log
  - artifacts/non_resolvable_graph_replay_20260919/site_check.log:1-1
  IMPACT: No custom argument preflight, ownership redesign or package release was introduced.
  NEXT: Verify final asset freshness and let the owner review the integrated change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-19T23:35:30Z
  TYPE: MEASURE
  CLAIM: Final source and src/tests/other bundle freshness checks all pass with exit 0. The final
    294-page site matches sources and passes 35,513 local links; new test/helper Ruff and whitespace
    pass. The public registration example executes successfully. All scoped work is ready for review.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/check_source_final.log:1-3
  - artifacts/non_resolvable_graph_replay_20260919/check_llm_final.log:1-3
  - artifacts/non_resolvable_graph_replay_20260919/check_site_final.log:1-1
  - artifacts/non_resolvable_graph_replay_20260919/documented_example.py
  IMPACT: Generated outputs match the final source/doc/test state; no release or formal closure performed.
  NEXT: Owner reviews or turns in the completed feature.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:01:19Z
  TYPE: DECISION
  CLAIM: Owner accepted the completed feature and requested: "ok close the ticket and turn it in".
    Close this delivery task and its completed feature epic/story/task chain; retain validation
    evidence and archive promoted patch contracts. Existing backlog and other agents' work remain separate.
  EVIDENCE:
  - context_compass/attention_board.md:91-93
  - context_compass/tickets/tasks/completed/2026-09-19_publish_and_replay_non_resolvable_definitions_task.md:231-257
  IMPACT: Explicit turn-in authorizes the selected records' completion and board/artifact synchronization.
  NEXT: Verify the feature's child records and recorded evidence, then close the accepted set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T00:25:59Z
  TYPE: DECISION
  CLAIM: Owner-authorized feature turn-in is complete for this record. Both later reported failures
    are repaired: crystal test-double capability and current-run local cancellation forwarding.
    This acceptance retains ordinary Python errors, existing version rules and documented limits.
  EVIDENCE:
  - artifacts/non_resolvable_graph_replay_20260919/validation.md:1-78
  - artifacts/non_resolvable_followup_20260919/validation.md:1-50
  IMPACT: Record is done; validation evidence is retained and promoted patch contracts are archived.
  NEXT: none; reopen only for a new owner-requested change or new failure evidence.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
CLOSED at 2026-09-20T00:25:59Z. Delivered Nexus publication and crystal replay; integrated qualification and final follow-up repairs are retained.
Final evidence and limits are in the graph/replay and follow-up validation artifacts.
No next implementation step remains in this accepted record.

### Historical pre-closure handoff
- Closure scope confirmed on 2026-09-20 UTC: the feature epic, seven required stories and nine child
  discovery/implementation tasks. The preceding standalone orientation task is outside this turn-in.
  Four promoted patch directories will move to patches/completed; nine feature artifact associations
  will move to the cleared board. Preserve the five validation directories and existing backlog.
  Qualification summary and final source/LLM/site logs were reread; all report the recorded success.

IMPLEMENTED / REVIEW. Per-version capability and typed relationships publish through Nexus; incoming/
outgoing queries filter hidden endpoints/sections. Real source/history and version-selection refresh
work. SpellCrystal captures the bool; active/staged restore and all graft binds preserve it. Existing
record major 2 rejects old readers; absent legacy bool remains True. Graphs rebuild through normal
compilation. Late Phase3 pushes updated descriptors; existing explicit Rift refresh is retained.

8055 distinct selected tests pass after targeted fixture reruns; one existing skip/four xfails remain.
39 docs tests, strict 294-page build and local-link/source checks pass. Read validation.md plus the
latest asset-check logs for exact evidence/limits. The full repository suite and coverage were not run.
S4 adds no argument preflight: ordinary Python errors and existing eager child construction remain.

Source owners: FrameDescriptorManager, ViewSpell/FrameViewer, CompilerPhase3, SpellCrystal,
RestoreEngine, GraftRunner and RecordVersion. Public docs are registration/overrides guides.
Generated source assets and LLM corpora use current workspace version 0.2.43; no package version,
release, commit or ownership policy was changed by this task. No agents; re-onboard after compaction.
