# Task: Persist and replay named lesser conduit structure

- Completed: 2026-09-23T11:55:35Z
- Summary: Owner-authorized named-lesser feature turn-in. Runtime, structural replay,
  Nexus, examples and canonical documentation are delivered; package assets remain held.
- Closure evidence: artifacts/named_lesser_finish_20260923/validation.md

## Metadata
- Task ID: TASK-2026-09-23-implement-named-lesser-crystallizer
- Story: STORY-2026-09-06-named-conduit-crystallizer-contract
- Epic: EPIC-2026-09-06-named-lesser-conduit-discovery
- Status: done
- Owner: codex
- Agent Name: updater_0
- Priority: p2
- Created: 2026-09-23T00:27:25Z
- Updated: 2026-09-23T11:55:35Z

## Objective
Extend Crystallizer's structural record and normal public-verb replay to active named lesser scopes.
Preserve names, actual parent hierarchy and shared Book ownership, never prior Creations/object state.

## Ticket Contract
- ENTRY_GATE: Owner said continue after explicit pool and upgrade verification.
- EXECUTION_BOUNDARY: Conduit named-only emit/retire seams; conduit crystal and record/remove/fold;
  formation closure, shared restore logic, validation/versioning and focused regressions.
- DEPENDENCIES: Delivered stage-1 naming and upgrade work; current discovery story/source trace.
- EXIT_GATE: Active/released/reused names capture/fold/replay with both drivers and fresh ids;
  unnamed return retains its one name conditional; errors unwind without misidentifying children as roots.
- FAILURE_ESCALATION: Stop on an unresolved ownership or replay ambiguity; keep Nexus separate.

## Scope Boundaries
- In: Dynamic recorded scopes, named descendants under necessary unnamed ancestry, active profile,
  sealed history, same-id reuse, promotion, formations and reader compatibility.
- Out: Nexus changes, application-object serialization, new Existence rules, global transaction
  redesign, package version bump, build assets, wheel or publishing.
- Preserve unnamed acquisition/return and Meld performance. Named branches may perform record work.
- Preserve passive emissions: the recorder does not reach into live runtime objects.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Structural recording/replay implemented; final affected rerun passes 330 tests.

## Steps / Checklist
- [x] Read Crystallizer component slices, subsystem philosophy and current source owners.
- [x] Specify ancestry retention, remove/fold, versioning and shared replay contracts in scoped patches.
- [x] Add meaningful capture/release/reuse and replay regressions.
- [x] Implement child-aware readers/removal before enabling named child emitters.
- [x] Verify both drivers, failure unwind, formations, compatibility and unchanged unnamed behavior.
- [x] Record evidence and update the story/epic for review; keep build hold.

## Files / Paths Impacted
- src/melder/aether/conduit/conduit.py (named lifecycle only)
- src/melder/aether/conduit/conduit_ward/conduit_ward.py (retain failed child ownership before pooling)
- src/melder/crystallizer/crystals/conduit_crystal.py
- src/melder/crystallizer/crystallizer.py (facade)
- src/melder/crystallizer/persistence/ (record, removal, capture and version)
- src/melder/crystallizer/crystal_loader_system/ (fold, admission, shared replay)
- src/melder/crystallizer/crystal_analysis/preflight/ (structural integrity)
- src/melder/crystallizer/crystal_analysis/conduit_hierarchy.py (shared detached hierarchy interpretation)
- Focused Crystallizer and conduit component/integration tests.

## Validation
Final affected rerun: 330 passed. Broad run: 1253 passed, 3 xfailed and one invalid new policy test;
that test and its unsupported replay assumption were corrected, then the affected rerun passed.
Counts overlap. Exact commands/outcomes: artifacts/named_lesser_crystallizer_20260923/validation.md.
git diff --check passed. No package-version/Nexus/build-asset changes, full-repository run or coverage claim.

## Resolved Contracts / Practical Limits
- Required unnamed ancestry is value-only support inside surviving named records; it needs no own
  live record or unnamed cleanup probe. Both drivers coalesce shared support and rebuild parents first.
- Record schema 3.0.0 fences root-only readers; valid older root input stays readable.
- Emit/remove/re-emit chronology, deep snapshot detachment and promotion lifetime are tested.
- Failed child/record retirement keeps soft cleanup owned and retryable; hard teardown remains best-effort.
- Public lesser creation always uses default policy; only normal roots may change policy. The earlier
  support-policy-drift hypothesis is disproven; no live revision counter or propagation machinery was added.
- Live restore requires caller quiescence of pooled scope lifecycles; existing LoadGate drains transactions.
- Nexus integration and canonical documentation/graph promotion remain later epic stages. Assets are held.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/architecture_patch.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/component_patch_record.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/component_patch_replay.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/code_description_patch_lifecycle.md
  - artifacts/named_lesser_crystallizer_20260923/validation.md
  - artifacts/named_lesser_crystallizer_20260923/final_focused.xml
- DISPOSITION: promote_to_documentation

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Keep current source findings, decisions and validation here after each complete boundary trace.

## Notes
- DATETIME: 2026-09-23T00:25:25Z
  TYPE: DECISION
  CLAIM: Owner confirms pool handling and directs continuation after the named-upgrade follow-up.
    Stage 2 is structural Crystallizer persistence/replay; no application-instance state or Nexus work.
  EVIDENCE:
  - Owner's current continue instruction following the pool clarification.
  - tickets/stories/completed/2026-09-06_named_conduit_crystallizer_contract_story.md
  - tickets/tasks/completed/2026-09-22_implement_named_lesser_directory_lifecycle_task.md
  IMPACT: Begin source-backed persistence design and implementation while preserving the one-check
    unnamed pool path. No new certification or repeated approval request is needed.
  NEXT: Read the component/philosophy slices and the record/capture/fold owners.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:30:35Z
  TYPE: FACT
  CLAIM: ConduitCrystal is currently root-only and copies configuration dictionaries shallowly.
    PersistenceProfile owns flat replace-on-emit twins, journals final-payload windows and has no
    conduit-only removal. Formation capture currently selects only its conduit anchor and Book.
    RecordVersion is 2.0.0 with newer-major refusal. The V3 record must remain passive and not reach
    into live objects or loader/analysis owners.
  EVIDENCE:
  - src/melder/crystallizer/crystals/conduit_crystal.py:8-306
  - src/melder/crystallizer/persistence/persistence_profile.py:230-332
  - src/melder/crystallizer/persistence/persistence_profile.py:436-525
  - src/melder/crystallizer/persistence/persistence_profile.py:1028-1307
  - src/melder/crystallizer/persistence/record_version.py:76-181
  - artifacts/2026-07-09_crystallizer_philosophy_v3.md:43-120
  IMPACT: Add a mirrored conduit removal/capture/fold lane and explicit child topology. Nested
    value payloads need real detachment. Ancestry retention must not demand unnamed cleanup probes.
  NEXT: Read shared fold/replay and facade/system emission paths before choosing the ancestry carrier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:39:19Z
  TYPE: DECISION
  CLAIM: Required unnamed ancestry will be plain value rows owned inside the named lesser twin's
    lineage_ancestors payload. No independently retained unnamed record or cleanup probe is needed.
    A shared stateless analysis helper will expand/validate support for preflight and shared per-Book
    replay. Schema major 3 fences old root-only readers. Live restore requires scope quiescence.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_profile.py:1028-1307
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1086-1318
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1739-1880
  - src/melder/crystallizer/persistence/persistence_crystal.py:78-191
  - src/melder/crystallizer/persistence/persistence_crystal.py:347-412
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/architecture_patch.md
  IMPACT: Same-id removal/reuse uses the existing journal contract. Nested payloads must be deeply
    detached at twin/checkpoint boundaries. Normal teardown also removes its recorded id to cover
    a promotion failure after Book attachment but before emitting the replacement root twin.
  NEXT: Read the scoped patches, add record/topology regressions and implement reader/removal support.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:43:06Z
  TYPE: MEASURE
  CLAIM: Scoped patches have been read and mapped: record patch -> removal/capture/fold tests;
    payload ownership -> twin/checkpoint mutation-isolation tests; replay patch -> hierarchy helper
    and both-driver integration tests; lifecycle patch -> named-only emit/retire and promotion tests.
    The first ten record regressions all fail on the expected missing removal, shallow detachment
    and old-reader acceptance. No runtime source has changed yet in stage 2.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/record_red.xml
  - tests/unit/melder/crystallizer/persistence/test_named_conduit_record_lifecycle.py
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/architecture_patch.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/component_patch_record.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/component_patch_replay.md
  - system_docs/patches/completed/named_lesser_crystallizer_2026_09_23/code_description_patch_lifecycle.md
  IMPACT: New nested ancestry exposes a real detachment defect in the existing shallow checkpoint
    surface; fixing it enforces the stated immutable/detached contract at the serialization boundary.
  NEXT: Implement record removal, deep value detachment and major-3 reader fencing before child emissions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:43:37Z
  TYPE: FACT
  CLAIM: Record groundwork is implemented: conduit-only removal now reaches facade/system/profile,
    capture emits a conduit_removed tombstone, and fold removes that id. Twin/checkpoint nested values
    are deeply detached at input/export boundaries. RecordVersion is 3.0.0; package version is unchanged.
    Named runtime emission is deliberately not enabled until the hierarchy reader/replayer is ready.
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py
  - src/melder/crystallizer/persistence/persistence_system.py
  - src/melder/crystallizer/persistence/persistence_profile.py
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py
  - src/melder/crystallizer/crystals/conduit_crystal.py
  - src/melder/crystallizer/persistence/persistence_crystal.py
  - src/melder/crystallizer/persistence/record_version.py
  IMPACT: Removal cannot evict the borrowed Book. New nested ancestry cannot mutate sealed history
    through returned dictionaries; readers written for schema major 2 reject the new envelope.
  NEXT: Run the record regressions and related pure persistence tests before adding hierarchy replay.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:52:08Z
  TYPE: MEASURE
  CLAIM: Record groundwork passes 61 tests. Hierarchy reader and formation closure are now wired:
    ConduitHierarchy expands only surviving carriers, validates shared support and orders parents;
    its preflight strategy blocks malformed child bundles. Restore explicitly selects roots and
    uses its shared per-Book body for lesser replay. Formations include the named subtree/ancestors.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/record.xml
  - src/melder/crystallizer/crystal_analysis/conduit_hierarchy.py
  - src/melder/crystallizer/crystal_analysis/preflight/conduit_hierarchy_strategy.py
  - src/melder/crystallizer/crystal_analysis/preflight/persistence_analyzer.py
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py
  - src/melder/crystallizer/persistence/persistence_profile.py
  IMPACT: Reader/removal paths are present before runtime named emissions. Both drivers preserve
    their existing Book unit and rollback stack. The package version/build hold remains unchanged.
  NEXT: Run hierarchy/record/restore unit suites, then add real named capture/replay integration proofs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T00:58:34Z
  TYPE: MEASURE
  CLAIM: Reader/record/restore unit qualification passes 106 tests. Real integration now reproduces
    missing named emission: 8 fail and 3 pass. Two sandbox attempts failed before test bodies because
    pytest-created temporary folders had access-denied ACLs; the scoped elevated run used a verified
    fresh workspace temp directory and reached the expected feature failures.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/readers.xml
  - artifacts/named_lesser_crystallizer_20260923/integration_red_elevated.xml
  - tests/integration/melder/crystallizer/test_named_lesser_persistence.py
  IMPACT: Reader readiness is verified before enabling writers. Continue using fresh verified
    workspace temp directories for cache integration; do not delete earlier test evidence.
  NEXT: Enable named-only emit/retire and promotion cleanup, then rerun the integration matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T01:01:19Z
  TYPE: FACT
  CLAIM: Named emission is enabled inside the existing attachment/child lock after Cloud publication.
    Ancestor rows are root-to-parent values. Pool return retires the record inside its existing name
    conditional before Cloud/name/idle retirement. Normal cleanup removes its identity before Book
    eviction, covering failed promotion with an old lesser twin. Permanent recording errors are
    logged while resource/discovery teardown continues; soft return remains retryable.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py
  - src/melder/crystallizer/crystallizer.py
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py
  IMPACT: Only normal roots emit at construction; named lesser emission waits for attachment.
    Accepted own-scope policy changes re-emit through the normal public setter. Live-restore
    documentation now states the required scope-lifecycle quiescence without adding global gates.
  NEXT: Run real named capture/replay integration and preserve the unchanged unnamed-path regressions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T09:47:10Z
  TYPE: MEASURE
  CLAIM: Real capture/replay integration plus the named directory/upgrade suites pass 56 tests.
    Both restore drivers recreate shared unnamed ancestry and named nesting; released carriers are
    absent from later history; reused ids restore only their new name/parent; formations retain
    required ancestry; promotion records and cleanup agree. The unnamed recording-spy test passes.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/integration_1.xml
  - tests/integration/melder/crystallizer/test_named_lesser_persistence.py
  IMPACT: The main structural path is working. Remaining qualification covers partial-replay
    unwind, recording failure boundaries, off/automatic controls and the broader Crystallizer suite.
  NEXT: Add those focused failure/control cases, then run broader compatibility qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T09:55:22Z
  TYPE: FACT
  CLAIM: Three new failure regressions reproduce a lifetime defect. The current named return detaches
    before record retirement, so a sink failure orphans a still-named scope. Ward soft teardown also
    suppresses child cleanup failure and returns the ancestor idle, dropping the failed child's owner.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/failures_1.xml
  - src/melder/aether/conduit/conduit.py:596-633
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-434
  IMPACT: Named retirement needs child cleanup -> record/Cloud retirement -> own detach. Extract the
    existing child-cleanup loop for named reuse and aggregate failures before ancestor detachment.
    Keep the existing no-children Ward fast path and exactly one name branch in Conduit pool return.
  NEXT: Apply that bounded Conduit/Ward failure-order fix and rerun the focused failure/pool suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:00:03Z
  TYPE: FACT
  CLAIM: Named return now completes descendants, retires record/Cloud, then detaches itself. Ward
    soft teardown aggregates child failures before ancestor detachment and retains failed owners.
    Its no-children fast path is unchanged. Added off/automatic recording, policy replay, fresh-scope
    skip-existing, partial replay unwind and emission failure cases for qualification.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:596-657
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-459
  - tests/integration/melder/crystallizer/test_named_lesser_persistence.py
  IMPACT: This closes the three reproduced orphan/pool failures without adding a directory or
    recorder call to unnamed leaf return. Hard teardown retains its existing best-effort contract.
  NEXT: Run the full Crystallizer test trees plus affected naming, upgrade, pool and Ward suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:08:30Z
  TYPE: HYPOTHESIS
  CLAIM: Shared unnamed support may carry different valid policy snapshots when its public policy
    changes between named-child emissions. The current helper refuses any support-policy disagreement,
    which could reject a legal recorded world. Root/Book/parent/name conflicts must still refuse.
  EVIDENCE:
  - src/melder/crystallizer/crystal_analysis/conduit_hierarchy.py:138-192
  - src/melder/aether/conduit/conduit.py:Conduit.set_new_policy
  - src/melder/aether/conduit/conduit.py:Conduit._recorded_lineage_ancestors
  IMPACT: Reproduce after the running broad suite finishes. If confirmed, the record's existing
    journal sequence can identify the latest support observation without adding state or checks
    to live unnamed scopes; do not choose a policy from arbitrary dictionary order.
  NEXT: Finish the current suite before changing source, then run the bounded policy-snapshot repro.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-23T10:10:41Z
  TYPE: MEASURE
  CLAIM: Broad qualification completed with 1253 passed, 3 xfailed and one failed new policy test.
    Source confirms public lesser creation passes default policy and Ward rejects policy changes
    unless normal. The failed test assumed an unsupported public operation. This also disproves the
    earlier hypothesis about valid support-policy drift: live lesser policy cannot change that way.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/suite_1.xml
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:615-701
  - src/melder/aether/conduit/conduit.py:Conduit.create_lesser_conduit
  - tests/integration/melder/crystallizer/test_named_lesser_persistence.py:424-436
  IMPACT: Remove the unnecessary policy setter re-emission added by this task. Keep normal-root
    replay unchanged and refuse nondefault child/support policies at hierarchy admission. Replace
    the bad test with a capability-preservation regression and add malformed-policy unit cases.
  NEXT: Make that correction and rerun affected integration/reader suites; retain broad-run evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T10:23:35Z
  TYPE: MEASURE
  CLAIM: Final affected qualification passes 330 tests after preserving default-only lesser policy.
    The earlier broad run had 1253 passed, 3 xfailed and the now-corrected unsupported-policy test.
    Named capture/retire/history/reuse, both drivers, formations, promotion and failure ownership are
    implemented. No new work enters unnamed leaf recording or Meld; no generated assets changed.
  EVIDENCE:
  - artifacts/named_lesser_crystallizer_20260923/final_focused.xml
  - artifacts/named_lesser_crystallizer_20260923/suite_1.xml
  - artifacts/named_lesser_crystallizer_20260923/validation.md
  - src/melder/aether/conduit/conduit.py:406-503
  - src/melder/aether/conduit/conduit.py:597-657
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:381-461
  IMPACT: Stage 2 is ready for review. Record schema is 3.0.0 while package version stays 0.2.47.
    Nexus and final canonical documentation/examples remain separate; no ticket turn-in yet.
  NEXT: Review this delivery, then continue the Nexus consumer story when selected.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Stage 2 is implemented and in review. Named twins own detached ancestor values; removal/folding drops
support with its final carrier. Shared ConduitHierarchy/preflight rejects invalid child structure and
nondefault lesser policy. Both restore drivers rebuild roots explicitly, then their shared-Book
lesser hierarchy with fresh ids and no saved application objects. Formations preserve required ancestry.
Soft record/descendant cleanup failures keep ownership and prevent pool return. Unnamed leaf return
still uses one name conditional and no recorder/directory calls. Record schema is 3.0.0; package 0.2.47.
Final affected rerun: 330 passed. Broad run and bounded correction are documented without inflated counts.
No tests/processes remain running. Use fresh verified workspace temp directories and scoped elevation
for disk tests (sandbox pytest ACL issue). Nexus and canonical doc/graph/example promotion remain next;
build assets are held. No new policy counters or policy-changing behavior were added.

## Closure Transition
- from_state: review
- to_state: done
- transition_reason: Owner requested full finish and turn-in; qualification is complete.
