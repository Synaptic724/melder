# Task: Implement named lesser discovery, pool retirement and promotion

- Completed: 2026-09-23T11:55:35Z
- Summary: Owner-authorized named-lesser feature turn-in. Runtime, structural replay,
  Nexus, examples and canonical documentation are delivered; package assets remain held.
- Closure evidence: artifacts/named_lesser_finish_20260923/validation.md

## Metadata
- Task ID: TASK-2026-09-22-implement-named-lesser-directory-lifecycle
- Story: STORY-2026-09-06-named-conduit-directory-lifecycle
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-22T23:42:49Z
- Updated: 2026-09-23T11:55:35Z

## Objective
Implement the epic's first slice: optional creation-time lesser names, Cloud discovery, retirement
before pool publication and safe name transitions through the existing graduation route.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorized implementation after component and source investigation.
- EXECUTION_BOUNDARY: Conduit/Cloud acquisition, cleanup and promotion; necessary frame/Book root-name
  bridges; focused tests and documentation. Existing graduation and pool-hook behavior is preserved.
- DEPENDENCIES: Current planning task and the directory lifecycle story; scoped patch contracts.
- EXIT_GATE: Observable discovery/reuse/promotion contracts tested, unnamed return remains one
  conditional with no directory call/lock/allocation, and changes are reviewable.
- FAILURE_ESCALATION: Record real lifecycle contradictions; keep later replay/projection work separate.

## Scope Boundaries
- In: optional names in both modes; shared frame namespace; fresh/prewarmed acquisition; cleanup,
  collision, failure and promotion correctness; concise rich API/lifecycle documentation.
- Out: Crystallizer child emissions/replay, Nexus projection changes, compiler/Meld changes,
  version bump, wheel and build-asset regeneration.
- The unnamed pool route gets one direct name check. Named cleanup alone enters the directory.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Nine added named-upgrade cases and related suites pass; 122 focused tests green.

## Steps / Checklist
- [x] Read verified component/graph slices and complete changed source methods plus their collaborators.
- [x] Record local lifecycle ordering and scoped patch contracts.
- [x] Add focused behavior regressions and reproduce the missing named-lesser feature.
- [x] Implement directory/root bridges, acquisition/return and promotion naming.
- [x] Run focused regression and related component tests; document results and hot-path boundary.
- [x] Update story/epic and leave reviewable delivery; preserve build hold.

## Files / Paths Impacted
- src/melder/aether/aetheric_frame/conduit_cloud.py
- src/melder/aether/aetheric_frame/aetheric_frame.py
- src/melder/aether/conduit/conduit.py
- src/melder/aether/spellbook/spellbook.py
- tests/component/melder/aether/conduit/ (focused new naming regressions)
- Existing related Cloud and graduation tests, only where the public contract changes.

## Validation
446 related tests passed in .venv_new on Python 3.14.7. Exact command and evidence are recorded in:
- artifacts/named_lesser_directory_20260922/validation.md
- artifacts/named_lesser_directory_20260922/qualified.xml
The new component suite covers naming, pooling, concurrency, callback/disposal failures and promotion.
git diff --check passed. No full-suite, performance or coverage claim; assets remain unchanged.
Upgrade-first follow-up: nine additional cases added; 122 naming/upgrade tests passed, overlapping
the earlier set. See artifacts/named_lesser_directory_20260922/upgrade_focus.xml and validation.md.

## Risks / Rollback Notes
Cloud currently borrows root maps. Discovery must not enroll lessers as frame-owned roots or cluster
members. Name mutations must be atomic under a leaf lock without callbacks/sinks inside that lock.
Same-object promotion must not self-collide; pre-attachment failure retains the original directory.

## Applicable Anti-Patterns
- [x] No naming lock, scan or directory call on unnamed pool return.
- [x] No new work on the Meld hot path or rewrite of graduation ownership.
- [x] No generated packaged assets under the owner's hold.
- [x] No unrelated edits or overwriting other agents' changes.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/architecture_patch.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/component_patch_directory.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/component_patch_conduit.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/code_description_patch_named_lifecycle.md
  - artifacts/named_lesser_directory_20260922/validation.md
  - artifacts/named_lesser_directory_20260922/qualified.xml
- DISPOSITION: promote_to_documentation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record each complete source/implementation/validation tranche with evidence and one next step.

## Notes
- DATETIME: 2026-09-22T23:47:31Z
  TYPE: FACT
  CLAIM: Current Cloud lookup aliases root maps; clusters directly consume the root-id map. Pool
    return already holds the conduit lock, disposes stores, detaches descendants, restores hooks and
    publishes idle last. Name retirement can be one conditional immediately before pooled status.
    Graduation keeps its original directory entry until final root admission, so pre-attachment
    rollback can leave that entry untouched; both Book name checks must allow the same identity.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:108-210
  - src/melder/aether/aetheric_frame/conduit_cloud.py:321-626
  - src/melder/aether/aetheric_frame/aetheric_frame.py:340-412
  - src/melder/aether/conduit/conduit.py:518-578
  - src/melder/aether/conduit/conduit.py:2087-2305
  - src/melder/aether/conduit/conduit.py:2395-2591
  - src/melder/aether/spellbook/spellbook.py:6635-6858
  IMPACT: Own a separate named directory in Cloud; retain root storage for cluster/DevOps ownership.
    Named publication belongs with the narrow parent attachment window; no new Meld checks.
    Existing component/graph claims that Cloud owns _registry and that lesser labels are impossible
    are stale and must be corrected in the scoped documentation delta.
  NEXT: Complete creation-system admission and test orientation, then record the patch and regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T23:42:49Z
  TYPE: DECISION
  CLAIM: Owner authorizes implementation after deeper component/source reads. Unnamed pool return
    must stay quick: one name check, with all unregister/name-reset work conditional on a name.
  EVIDENCE:
  - Owner's current implementation request and hot-path constraint.
  - tickets/epics/completed/2026-09-06_named_lesser_conduit_discovery_epic.md:32-79
  - tickets/tasks/completed/2026-09-22_refresh_named_lesser_conduit_plan_task.md
  IMPACT: Stage 1 is executable; Crystallizer/Nexus remain later stories and assets remain held.
  NEXT: Read verified lifecycle component/graph slices and actual directory/pool code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T23:50:43Z
  TYPE: PLAN
  CLAIM: Scoped patch contracts have been authored and read. Directory contract maps to owned
    name/id maps and frame bridges; lifecycle contract maps to conditional pool retirement and
    named attachment; promotion contract maps to a temporary name claim and the two Book probes.
  EVIDENCE:
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/architecture_patch.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/component_patch_directory.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/component_patch_conduit.md
  - system_docs/patches/completed/named_lesser_directory_2026_09_22/code_description_patch_named_lifecycle.md
  IMPACT: Tests will assert public lookup/reuse/collision behavior, real promotion rollback and
    disposal ordering. A forbidden-directory spy will prove unnamed return enters no Cloud work.
  NEXT: Add and run the focused red naming regressions, then implement these mapped boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T23:53:38Z
  TYPE: MEASURE
  CLAIM: The initial 27-case component suite reports 25 failures and 2 passes before implementation.
    Missing name API/directory mutation methods explain the feature failures. One two-root setup
    exposed a test-helper mismatch when reapplying caching defaults to a frozen frame; the fixture
    now configures only a newly created frame and inherits settled posture for subsequent roots.
  EVIDENCE:
  - artifacts/named_lesser_directory_20260922/red.xml
  - tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py
  - tests/_frame_posture_test_support.py:32-82
  IMPACT: Feature failures are reproduced through real root/lesser wiring; no runtime patch yet.
  NEXT: Implement the scoped Cloud/root bridge and lesser acquisition/return/promotion changes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:00:29Z
  TYPE: FACT
  CLAIM: Source now separates named discovery from frame roots, publishes both acquisition paths,
    and retires named scopes before pooled state/idle publication. Unnamed return adds exactly one
    direct _name conditional. Promotion reserves its target, keeps the original alias through setup,
    and uses same-identity Cloud probes before Book attachment; root registration exchanges aliases.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py
  - src/melder/aether/aetheric_frame/aetheric_frame.py
  - src/melder/aether/conduit/conduit.py
  - src/melder/aether/spellbook/spellbook.py
  IMPACT: Initial implementation matches the scoped patch. Cloud unit fixtures now publish names
    through the lifecycle seam instead of treating direct root-map mutation as named publication.
  NEXT: Run focused named-lifecycle and Cloud unit regressions; investigate actual failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:02:00Z
  TYPE: MEASURE
  CLAIM: Initial patched run passes 55 of 57 focused cases. The two failures were invalid test
    injection points: normal conjure hooks also suppress callback exceptions. This corrects the
    earlier planning assumption that ordinary hook errors propagate. Tests now fail actual phase
    and registration-tail seams, preserving advisory callbacks. Additional tests cover callback
    visibility/cleanup, parent teardown, real disposal failure and absence of Cloud locking unnamed.
  EVIDENCE:
  - artifacts/named_lesser_directory_20260922/focused.xml
  - src/melder/aether/spellbook/spellbook_creation_system.py:1280-1318
  - tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py
  IMPACT: No runtime hook behavior changes are needed. Failure regressions now exercise actual
    pre/post attachment aborts; the name-claim check occurs inside a genuine phase failure.
  NEXT: Run expanded naming, Cloud, pool, hook and graduation tests together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:07:33Z
  TYPE: MEASURE
  CLAIM: The 403-test related run passed. Review then found a named-only publication edge: a lesser
    parent can be returned by an activation callback without becoming _cleaned. Named acquisition
    now rejects pooled parents at entry and attachment. Three added cases cover those two paths and
    root-registration failure after Book attachment. Two more old unit expectations that discarded
    names are updated to preserve labels while refusing root/early-directory publication.
  EVIDENCE:
  - artifacts/named_lesser_directory_20260922/related_final.xml
  - src/melder/aether/conduit/conduit.py:2447-2691
  - tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:382-440
  IMPACT: The extra parent checks exist only on named acquisition. Unnamed pool return still has
    just the one name conditional; build assets and Meld remain unchanged.
  NEXT: Run the final expanded related set and perform focused change review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:09:14Z
  TYPE: MEASURE
  CLAIM: Final qualification passes 446 tests across naming, Cloud, pools, hooks, graduation, frame
    and Aether. Source review confirms pool return adds one _name conditional and named-only
    unregister/clear, with no change to Meld or ConduitPool. Packaged assets remain unchanged.
  EVIDENCE:
  - artifacts/named_lesser_directory_20260922/qualified.xml
  - artifacts/named_lesser_directory_20260922/validation.md
  - src/melder/aether/conduit/conduit.py:549-584
  - src/melder/aether/aetheric_frame/conduit_cloud.py:222-354
  - src/melder/aether/aetheric_frame/aetheric_frame.py:339-420
  - src/melder/aether/spellbook/spellbook.py:6635-6863
  IMPACT: Stage 1 is ready for owner review. Later Crystallizer/Nexus integration and final canonical
    documentation/graph promotion remain catalogued; no ticket closure or version/build change.
  NEXT: Review the stage-1 delivery, then take the Crystallizer story when selected.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:17:16Z
  TYPE: DECISION
  CLAIM: Owner directs us to finish upgrade-to-normal naming before progressing to Crystallizer.
    Existing tests cover same/new names, collisions, phase rollback and post-attachment cleanup.
    Additional proofs target former-parent teardown, original-name reuse, gate-admission failure,
    successful retry and named promotion under shared frame configuration.
  EVIDENCE:
  - Owner's current correction to manage upgrade first.
  - src/melder/aether/conduit/conduit.py:2111-2335
  - src/melder/aether/aetheric_frame/conduit_cloud.py:242-354
  - tests/component/melder/aether/conduit/test_named_lesser_directory_lifecycle.py:267-345
  IMPACT: Keep work on the existing directory task. The interrupted step read stories only;
    Crystallizer and Nexus source remain unchanged. No broader lifecycle redesign is authorized.
  NEXT: Add the focused named-promotion ownership/failure regressions and run the upgrade suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:21:01Z
  TYPE: MEASURE
  CLAIM: Upgrade-first follow-up passes 122 naming/upgrade tests, including nine added cases.
    Promotion survives former-parent/root cleanup and owns a usable new pool. Reusing the old
    name is safe when the promoted root cleans. Gate failure releases claims, preserves admission
    and permits retry. Named promotion preserves separate Book/hooks and disposal ownership under
    both local and frame-wide configuration. No further runtime patch was needed.
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_named_lesser_upgrade_to_normal.py:17-140
  - artifacts/named_lesser_directory_20260922/upgrade_focus.xml
  - artifacts/named_lesser_directory_20260922/validation.md
  IMPACT: Named upgrade is explicitly verified before any persistence work. The 122-test set
    overlaps the previous 446; do not sum those counts. Crystallizer/Nexus/assets remain untouched.
  NEXT: Report named upgrade verification and retain later stages for the owner's next direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Latest direction and result: finish named upgrade first. Nine additional cases now prove former-parent
cleanup, old-name reuse, early gate failure/retry and shared-configuration behavior; 122 focused tests
pass. No new runtime change was needed. Report this result before advancing to Crystallizer.

Stage 1 is implemented and in review. API: create_lesser_conduit(logger=None, *, name=None).
Cloud owns named maps and upgrade claims; frame/cluster root maps stay separate. Return adds one
name check and retires named discovery before idle publication. Promotion handles same/new names,
pre-attachment rollback and normal cleanup after attachment. 446 related tests pass; receipt above.
Crystallizer/Nexus remain later stories. Canonical map/graph promotion stays in review/qualification;
the scoped patch and docstrings carry current contracts. No build assets or package version changed.
Unrelated pre-existing artifact deletions and updater_1 review edits remain outside this task.

## Closure Transition
- from_state: review
- to_state: done
- transition_reason: Owner requested full finish and turn-in; qualification is complete.
