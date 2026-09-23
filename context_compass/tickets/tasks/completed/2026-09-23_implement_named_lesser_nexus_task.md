# Task: Integrate named lesser lifecycle with Nexus discovery

- Completed: 2026-09-23T11:55:35Z
- Summary: Owner-authorized named-lesser feature turn-in. Runtime, structural replay,
  Nexus, examples and canonical documentation are delivered; package assets remain held.
- Closure evidence: artifacts/named_lesser_finish_20260923/validation.md

## Metadata
- Task ID: TASK-2026-09-23-implement-named-lesser-nexus
- Story: STORY-2026-09-06-named-conduit-nexus-consumers
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-23T10:39:23Z
- Updated: 2026-09-23T11:55:35Z

## Objective
Keep Nexus publication, ACL-filtered discovery and command resolution consistent with named lesser
acquisition, pool retirement/reuse, promotion and structural replay.

## Ticket Contract
- ENTRY_GATE: Owner requested continuation after the remaining Nexus and qualification stages were listed.
- EXECUTION_BOUNDARY: Conduit publication seams and relevant Nexus descriptor, projection, viewer and
  command consumers; focused regression tests and source-backed patch contracts.
- DEPENDENCIES: Delivered directory/promotion and Crystallizer tasks; Nexus consumer story.
- EXIT_GATE: Named discovery returns the authorized live scope, pooled reuse has no stale name or
  parent, normal-only capabilities remain enforced and affected tests pass.
- FAILURE_ESCALATION: Record unresolved lifecycle/permission contracts; do not broaden hot paths or
  synchronously drain Rift gates from an admitted command.

## Scope Boundaries
- In: Current existing descriptor fields, same-id publication, explicit projection membership refresh,
  lesser-aware named lookup, optional creation-name forwarding and restore publication parity.
- Out: New lifetime/lease semantics, broader ACL redesign, compiler changes, package version, generated
  assets, wheel, publishing and unrelated epics.
- Preserve the single conditional on unnamed pool return and avoid new Meld-path work.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Nexus integration implemented; final affected selection passes 471 tests.

## Steps / Checklist
- [x] Read component/graph slices and the actual publication, lifecycle and lookup owners.
- [x] Select coherent pooled-record behavior and author scoped patch contracts.
- [x] Add failing public contract regressions.
- [x] Implement named lifecycle publication and authorized command resolution.
- [x] Run affected suites, record evidence and update the epic/story handoff.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py (Nexus lifecycle seams)
- src/melder/nexus/frame_descriptor_manager.py and relevant descriptor records
- src/melder/nexus/rift/command_system/ (named resolution and lesser creation wrappers)
- src/melder/nexus/rift/frame_viewer/ and projection consumers only if source proves necessary
- Focused Nexus and named-lifecycle tests
- release_docs/next_version_release.md (implemented feature summary; no version bump)

## Validation
Final affected selection: 471 passed in 12.92 seconds on Python 3.14.7. Scoped git diff --check passed.
Exact selection, intermediate failures/corrections and sandbox ACL limitation are recorded in:
- artifacts/named_lesser_nexus_20260923/validation.md
- artifacts/named_lesser_nexus_20260923/final.xml
No full-repository, coverage or benchmark claim. Build assets and package version remain unchanged.

## Risks / Rollback Notes
Published descriptors are live but allowed-id sets are compiled. Removing a record can leave a
dangling visible id; resolving a published name through a separate directory lookup can return an
unchecked replacement after name reuse. Trace and test both boundaries before changing them.

## Applicable Anti-Patterns
- [x] No additional Cloud/Nexus work on ordinary unnamed leaf pool return.
- [x] No second naming flag or generic root-capability relaxation.
- [x] No synchronous Rift refresh from an active gated command.
- [x] No generated assets under the owner's hold.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/architecture_patch.md
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/component_patch_nexus.md
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/code_description_patch_lifecycle.md
  - artifacts/named_lesser_nexus_20260923/
- DISPOSITION: promote_to_documentation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record findings after each complete call-path read, with concrete evidence and one next step.

## Notes
- DATETIME: 2026-09-23T10:56:00Z
  TYPE: MEASURE
  CLAIM: Related run has 198 passes and one stale fixture failure: the frame-summary unit test
    mutates root maps without publishing the now-separate Cloud name. It now calls the actual
    directory registration seam. Added explicit ACL denial, lesser-capability, concurrent cycle,
    failed-first-publication, disabled-publication and both-driver restore/publication regressions.
  EVIDENCE:
  - artifacts/named_lesser_nexus_20260923/related_1.xml:1-1
  - tests/unit/melder/aether/test_nexus_passive_ingest.py:131-172
  - src/melder/aether/aetheric_frame/conduit_cloud.py:269-318
  IMPACT: This is test setup drift from stage 1, not a runtime summary defect. New tests finish the
    selected contract matrix; no unrelated runtime change or generated asset is introduced.
  NEXT: Run focused and affected suites including real checkpoint replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:55:30Z
  TYPE: MEASURE
  CLAIM: Runtime integration is implemented. First patched run has 23 passes and two race-test
    failures: hard cleanup can leave an old Ward traversal reference whose guarded name read raises
    the existing cleaned RuntimeError. The getter correctly refuses it; the tests now accept both
    documented unavailable/cleaned errors instead of requiring only ValueError.
  EVIDENCE:
  - artifacts/named_lesser_nexus_20260923/focused_1.xml:1-1
  - src/melder/nexus/rift/command_system/command_system.py:251-292
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:1219-1242
  IMPACT: No need to broaden this lane into Ward teardown. Named lifecycle publication, same-ID
    views and both named getters are working; restore and related-suite compatibility remain.
  NEXT: Add remaining restore/ACL/failure controls, then qualify the affected suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:55:00Z
  TYPE: MEASURE
  CLAIM: Initial 25-case regression run has 15 expected failures and 10 passes. Failures reproduce
    stale prewarmed/reused names, stale frame Cloud summaries, missing retirement publication,
    root-only command resolution and missing name forwarding. Advisory post-created failures are
    detected through observed outcomes. Codegen lacks has_conduit_name, so its shared assertions
    must use the supported list_conduit_names surface after the earlier failure is repaired.
  EVIDENCE:
  - artifacts/named_lesser_nexus_20260923/red.xml:1-1
  - tests/component/melder/aether/conduit/test_named_lesser_nexus_lifecycle.py:48-193
  - tests/integration/melder/aether/test_named_lesser_nexus_commands.py:35-165
  IMPACT: Source changes are now justified by behavioral reproductions. Disable pytest's optional
    cache provider on following runs to avoid existing workspace cache-permission noise.
  NEXT: Implement the publication/identity patches and rerun this focused matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:52:00Z
  TYPE: PLAN
  CLAIM: All three scoped patches are read. Acquisition/retirement sections map to real Nexus
    record and frame-summary regressions; identity resolution maps to capability/codegen commands
    and stale-name/ACL tests. Retained pooled records preserve current projection membership;
    permanent deletion continues requiring explicit refresh. No new observer on anonymous cycles.
  EVIDENCE:
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/architecture_patch.md:1-34
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/component_patch_nexus.md:1-26
  - system_docs/patches/completed/named_lesser_nexus_2026_09_23/code_description_patch_lifecycle.md:1-27
  IMPACT: Entry gates are satisfied. Tests use real records/runtime and inject only publication
    failures or a deterministic lookup race at the relevant boundary.
  NEXT: Add and run focused red regressions before changing runtime source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:49:00Z
  TYPE: DECISION
  CLAIM: Retain published named-scope IDs on soft return as unnamed pooled records. Existing
    projections borrow descriptors but keep detached allowed-ID sets; new IDs and permanent removal
    retain explicit projection refresh. Named acquisition publishes under its existing child lock
    before post-created callbacks. Named resolution will resolve the published authorized ID, then
    reject a changed live name; it must not perform a second lookup by name.
  EVIDENCE:
  - src/melder/nexus/rift/projection/view_projection.py:14-152
  - src/melder/nexus/rift/frame_viewer/view_frame.py:2182-2303
  - src/melder/nexus/rift/command_system/command_system.py:194-250
  - src/melder/nexus/rift/command_system/capability_command_system.py:198-237
  - src/melder/aether/conduit/conduit.py:606-670
  - src/melder/aether/conduit/conduit.py:2519-2763
  IMPACT: Use an explicit private pooled publication option to build cleared value payloads before
    unlinking. Failed publication keeps the scope owned for retry; only existing records may be
    retired this way. Refresh the frame summary after Cloud removal, then clear the live name and
    detach. Unnamed return remains unchanged. Anonymous pooled cycles are not newly observed.
  NEXT: Create/read the scoped patch contracts and add public lifecycle/command regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:39:23Z
  TYPE: DECISION
  CLAIM: Owner requests continuation. Stages 1 and 2 remain delivered in review; start Nexus
    integration and preserve the build-asset hold. Existing discovery recommends retained unnamed
    pooled records and explicit refresh for new membership; verify against current source.
  EVIDENCE:
  - tickets/epics/completed/2026-09-06_named_lesser_conduit_discovery_epic.md:13-27
  - tickets/tasks/completed/2026-09-22_refresh_named_lesser_conduit_plan_task.md:133-142
  - Owner's current continue instruction.
  IMPACT: One bounded implementation lane; no rework of completed naming or structural replay.
  NEXT: Read relevant component/graph slices and publication/lookup source.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T11:01:16Z
  TYPE: MEASURE
  CLAIM: Final affected selection passes 471 tests after explicit private-argument mock updates
    and hard-summary-failure qualification. Named lifecycle/command/restore integration is delivered
    in review. Release notes summarize it; no runtime process remains running.
  EVIDENCE:
  - artifacts/named_lesser_nexus_20260923/final.xml:1-1
  - artifacts/named_lesser_nexus_20260923/validation.md:1-80
  - release_docs/next_version_release.md:5-45
  IMPACT: Remaining epic work is documentation/graph/example promotion and acceptance. Build assets
    remain held; no package version bump or full-repository/coverage claim.
  NEXT: Continue the final validation/docs story from the three implementation patch sets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Stage 3 is implemented and in review. Final affected run: 471 passed. Named acquisition publishes
within the existing child lock before post-created callbacks; named return publishes cleared pooled
values for an existing record before unlinking. Live name/parent survive soft sink failure for retry.
Hard summary failure logs and continues teardown. No new anonymous return or Meld-path work.
Both named command getters resolve the authorized published ID and refuse a changed live name;
capability forwards name= at creation. Existing ACLs, lesser restrictions and explicit refresh remain.
Both restore drivers publish fresh hierarchy correctly. No tests/processes remain running.
Release notes are updated. Next is the qualification story: canonical maps/graph, runnable examples,
documentation review and eventual owner turn-in. Build generation remains explicitly held.

## Closure Transition
- from_state: review
- to_state: done
- transition_reason: Owner requested full finish and turn-in; qualification is complete.
