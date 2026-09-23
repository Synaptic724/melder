# Task: Add local hook setters, registration and modification tracking

- Completed: 2026-09-22T19:50:34Z
- Summary: Stable root baselines, local/shared hook controls and cleanup-before-pool restoration
  accepted with 2102 passing tests, two existing skips and measured overhead. Documentation promoted.

## Metadata
- Task ID: TASK-2026-09-22-add-local-hook-setters-and-tracking
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-22T09:57:45Z
- Updated: 2026-09-22T19:50:34Z
- Related discovery: TASK-2026-09-22-investigate-pooled-conduit-hook-reset

## Current Authorization
Owner accepted the pool/root-hook proposal and its rare-mutation/simple-bool constraints: implement
now. This supersedes the earlier first-slice-only exclusions. Cover Conduit/Meld APIs, stable root
baselines, lesser and both SpellSpace lease paths, graduation hook attachment, tests and measurement.
No build assets or unrelated hook families. Source version stays 0.2.45.

## Objective
Implement the approved Conduit/Meld hook controls, stable root baselines and pool restoration.
Track temporary Meld references with a bool and use existing locks only on rare mutation/reset paths.
Qualify lesser and manual/managed SpellSpace reuse without changing ordinary Meld execution.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested these runtime additions. Patch contracts before source edits.
- EXECUTION_BOUNDARY: Conduit/Meld registration, setter, flags/properties, initialization/cleanup,
  focused tests and documentation. Benchmark flag/count/mutex reads without changing runtime behavior.
- DEPENDENCIES: Existing local/lineage rules and method-only mutation contract; source/test map reads.
- EXIT_GATE: New methods and flags tested; concurrency contract explicit; source review ready.
- FAILURE_ESCALATION: Raise conflicts with the accepted shared/local model; do not expand hook families.

## Accepted Implementation Details
- Normal roots own stable native hook dictionaries, copied from configuration even when empty.
- Public registration defaults to local/additive; setters replace supplied families. Shared writes
  are explicit and root-only. Keep internal reference installation separate from shared mutation.
- Preserve lifecycle event shadowing and Meld local-map copy semantics. Empty local lifecycle
  entries reveal inherited events; empty local Meld replacement mutes its effective map until reset.
- Track Meld divergence with a bool, including Spaces borrowing an owner-local map. Pool return
  restores only when that bool is set; Spaces re-adopt customized owner maps at acquisition.
- Use existing locks on rare mutation/reset work. No new ordinary-Meld checks/locks/scans/copies.
- The proposed configuration-has-hooks diagnostic bit is not a reset authority: current shared
  contents may change after initialization. Avoid adding an unused flag just to detect emptiness.

## Scope Boundaries
- In scope: Conduit.set_conduit_hooks, Meld.register_meld_hooks, local-copy tracking, stable root
  publication, lesser/Space lease boundaries and graduation baseline integration.
- Out of scope: broad hook framework/IDs, Bind changes, configuration flag polling and generated assets.
- Direct list/dict mutation is unsupported. Do not add mutation scans or proxies.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepted turn-in; canonical contracts promoted and package hold preserved separately.

Latest release-document follow-up:
- from_state: in_progress
- to_state: review
- transition_reason: Requested release entry added and reread; scoped whitespace check passes.

## Work
- [x] Measure simple no-change reads in the user's free-threaded environment.
- [x] Record patch contract and map its sections to source/tests.
- [x] Implement local registration/setter/flags with rich contracts and cleanup.
- [x] Run focused tests and inspect the source changes before reporting.

## Validation
Final affected run: 2102 passed, two pre-existing owner-deferred skips. Seventy-three new parameterized
cases qualify pool restoration, public controls, concurrency, disposal order, callback release and
automatic warm-door recovery. New test lint, fatal runtime/test lint and scoped whitespace checks pass.
Pre-repair evidence retains the original 17 failures and four later prewarm failures. Before/after
pool measurements and source/asset preservation proofs are in the implementation artifact folder.
Use .venv_new with uv, offline/no-sync and Python -X gil=0.
Prove additive versus replacement behavior, parent-map isolation, flags, method-only tracking,
cleanup and unchanged ordinary Meld hook dispatch. No generated assets before owner code approval.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/local_hook_tracking_20260922/
  - artifacts/pool_hook_implementation_20260922/
  - artifacts/pool_hook_implementation_20260922/source_review.md
  - system_docs/patches/completed/pool_hook_baselines_2026_09_22/
  - artifacts/recent_finished_turn_in_20260922/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none

## Notes
- DATETIME: 2026-09-22T09:57:45Z
  TYPE: PLAN
  CLAIM: Owner requested Conduit setting, Meld local registration and modified flags, then proposed
    spellbook_configuration_hooks_set to distinguish empty from configured baselines. Public hook
    mutation is the supported seam. Compare count/bool/mutex cost before making a speed claim.
  EVIDENCE:
  - Owner's API/flag request and subsequent mutex/count question.
  - src/melder/aether/conduit/conduit.py:1657-1711
  - src/melder/aether/conduit/meld/meld.py:1264-1307
  IMPACT: Code/test work is authorized for this slice; broad standardization and generators remain held.
  NEXT: Run the small read-cost measurement and select mutation/read locking boundaries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T10:13:25Z
  TYPE: MEASURE
  CLAIM: The retained read-cost run used Python 3.14.7 free-threaded with GIL disabled, seven
    repeats of one million calls each. Median ns/call: flag 18.44; dict truth 23.32; len(dict)>0
    27.90; uncontended RLock-protected read 84.93; false flag bypassing lock 22.17. These include
    wrapper-call overhead and measure one thread without contention, not Melder throughput.
  EVIDENCE:
  - artifacts/local_hook_tracking_20260922/read_cost.json:1-29
  - artifacts/local_hook_tracking_20260922/read_cost.py
  IMPACT: This measurement does not support replacing a simple flag/count read with a mutex for
    speed. It does not decide correctness or justify a new lock on ordinary meld execution.
  NEXT: Complete the owner's requested pool/SpellSpace and bind-graduation investigation first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T16:20:59Z
  TYPE: DECISION
  CLAIM: Owner approves implementation after clarifying the hot-path concern. Root propagation and
    pool restoration join the earlier API/flag scope. Choose additive registration and replacement
    of supplied families; explicit shared mutation is normal-root-only. Retain existing local
    lifecycle shadowing and Meld copied-map behavior. Internal adoption remains reference binding.
  EVIDENCE:
  - Owner's latest acceptance: "yeah your good send it".
  - artifacts/pool_hook_propagation_20260922/proposal.md
  IMPACT: Implement one coherent ownership/reset change, preserving graduation's independent Book.
    No build assets, source version changes or new ordinary-Meld synchronization are authorized.
  NEXT: Record patch contracts and baseline pool measurements before source edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T16:27:19Z
  TYPE: MEASURE
  CLAIM: Pre-edit pool benchmark captured seven repeats of 20,000 cycles per case on Python 3.14t,
    GIL disabled. Empty medians: lesser 1313.9 ns, manual Space 680.2 ns, managed Space 404.7 ns;
    seeded: 1623.7/668.1/403.7 ns. Seventeen new cases fail before repair, reproducing callback
    leakage, stale pooled Spaces, retained temporary callback objects and missing shared APIs.
  EVIDENCE:
  - artifacts/pool_hook_implementation_20260922/pool_before.json
  - artifacts/pool_hook_implementation_20260922/red.log
  - system_docs/patches/completed/pool_hook_baselines_2026_09_22/architecture_patch.md
  - system_docs/patches/completed/pool_hook_baselines_2026_09_22/component_patch_runtime.md
  - system_docs/patches/completed/pool_hook_baselines_2026_09_22/code_description_patch_pool.md
  IMPACT: Patch contracts consumed. Map root isolation/publication to shared-update tests; map bool
    tracking/reset and Space acquisition to lease/weak-reference tests; map adoption to graduation
    regression compatibility. All ordinary Meld entrypoints remain untouched.
  NEXT: Implement baseline ownership, rare mutation APIs and bool-gated lease restoration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-22T16:36:40Z
  TYPE: FACT
  CLAIM: Initial source patch implements root-owned maps, validated registration/setter controls,
    bool-gated lesser/Space reset and baseline rebinding during graduation. Reentry review found a
    further idle-publication path: prewarm_spellspaces releases newly acquired Spaces without their
    reset path, so prewarming under owner-local hooks can strand temporary maps after owner reset.
  EVIDENCE:
  - src/melder/aether/conduit/meld/meld.py:1273-1466
  - src/melder/aether/conduit/conduit.py:548-571
  - src/melder/aether/conduit/conduit.py:1101-1145
  - src/melder/aether/conduit/spell_space/spell_space.py:305-409
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:146-210
  - src/melder/aether/spellbook/spellbook.py:6797-6828
  IMPACT: Qualify prewarming as an idle boundary too. Initial patch remains unvalidated; no assets
    or version changes. Source maps are leads predating this patch; source contracts were reread.
  NEXT: Add the prewarm regression and run the initial pool plus graduation tests before repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T16:39:00Z
  TYPE: MEASURE
  CLAIM: Initial post-patch run passes 111 cases; four additional prewarm regressions fail exactly
    on the previous lease's temporary callback firing. Both configuration modes and both acquisition
    doors reproduce it. The original 17 red pool tests and graduation suites pass in this run.
  EVIDENCE:
  - artifacts/pool_hook_implementation_20260922/initial.log:1-43
  - tests/component/melder/aether/conduit/test_pooled_hook_baselines.py:186-217
  IMPACT: Restore modified prewarm maps before direct idle publication. Local copying also needs a
    shallow mapping snapshot on its rare mutation path: root publication can alter the shared dict
    while a different Meld localizes. Snapshot only there; dispatch and pool common paths stay cheap.
  NEXT: Repair prewarm publication, typing/docstrings and rare-path copying; qualify the affected suites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T16:43:00Z
  TYPE: MEASURE
  CLAIM: Affected suites pass 1712 cases with one existing skip. Thirty-four failures are confined
    to three Space test doubles lacking the new baseline fields, four tests expecting configuration
    map aliasing, and five discovery cases intentionally asserting the repaired leakage/partial-write
    behavior. The prewarm regressions pass after reset was added before its direct idle publication.
  EVIDENCE:
  - artifacts/pool_hook_implementation_20260922/affected.log
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space.py:39-61
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool.py:30-51
  - tests/unit/melder/aether/conduit/spell_space/test_spell_space_pool_multithreaded.py:32-51
  - tests/experimentation/test_runtime_hook_discovery_experiment.py:94-237
  IMPACT: Update faithful test doubles and convert old defect characterizations to corrected
    expectations. No runtime compatibility guards for incomplete mocks. Add focused control,
    concurrency, disposal-order and terminal callback-release coverage.
  NEXT: Update those tests and run the affected suite plus the unchanged-cycle benchmark.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T16:49:00Z
  TYPE: MEASURE
  CLAIM: Affected suite now passes 1792 cases with one pre-existing skip. New control tests cover
    root authority, invalid replacement, disposal ordering, terminal release and concurrent writers.
    Pool medians after repair: empty lesser/manual/managed 1332.87/710.16/446.375 ns; seeded
    1678.195/706.39/443.265 ns. Empty-path increases are 19/30/42 ns, approximately 1.4/4.4/10.3%.
  EVIDENCE:
  - artifacts/pool_hook_implementation_20260922/affected_repaired.log
  - artifacts/pool_hook_implementation_20260922/pool_before.json
  - artifacts/pool_hook_implementation_20260922/pool_after.json
  - tests/component/melder/aether/conduit/test_runtime_hook_controls.py:1-397
  IMPACT: Common pool operations add only bool reads, with no new lock on unchanged leases.
    These are single-thread empty-cycle microbenchmarks, not full application throughput. Final
    review will remove empty local event entries so clearing retains the native no-hooks fast guard.
    Fatal source lint passed; the new test file needs two import-style corrections.
  NEXT: Finish clear-path review, private-conjure/fast-pool integration and preservation checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T16:52:18Z
  TYPE: MEASURE
  CLAIM: Final qualification passes 2102 tests with two existing owner-deferred shared-context skips.
    Seventy-three new cases cover accepted controls, pooling, graduation compatibility, concurrency,
    disposal and six automatic warm-door add/clear scenarios. Empty local event lists are omitted so
    clear returns to the existing fast lane. Scoped lint/whitespace pass. All 26 packaged assets,
    both concrete Meld execution files and source version 0.2.45 remain byte-identical to baseline.
  EVIDENCE:
  - artifacts/pool_hook_implementation_20260922/final.log:1-31
  - artifacts/pool_hook_implementation_20260922/final.xml
  - artifacts/pool_hook_implementation_20260922/lint.log:1-2
  - artifacts/pool_hook_implementation_20260922/preservation.json
  - artifacts/pool_hook_implementation_20260922/source_review.md
  IMPACT: Source review is ready. Pool overhead is measured and disclosed; no new lock/check enters
    ordinary Meld execution. Canonical map/descriptor promotion and generation remain held for review.
  NEXT: Owner reviews the bounded source implementation and chooses whether to release generation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T17:04:17Z
  TYPE: PLAN
  CLAIM: Owner confirms cleanup must finish before pool return and requests these changes in the
    next release draft. Add the fixed lifecycle order, checkout-time owner selection, shared/local
    controls and recorded qualification to the existing 0.2.45 draft.
  EVIDENCE:
  - release_docs/next_version_release.md:1-179
  - artifacts/pool_hook_implementation_20260922/source_review.md:6-85
  - Owner's release-change request after lifecycle confirmation.
  IMPACT: Documentation-only follow-up; runtime, version and build assets remain unchanged.
  NEXT: Add and reread the pool-hook release section.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T17:06:04Z
  TYPE: FACT
  CLAIM: The 0.2.45 draft now includes the pool-hook repair: disposal/reset before idle publication,
    current-owner hook selection on SpellSpace acquisition, runtime control examples, local/shared
    semantics and prior 2102-test qualification. Existing graduation and purge sections are preserved.
  EVIDENCE:
  - release_docs/next_version_release.md:5-68
  IMPACT: Owner's release-document request is complete. Changed prose was reread and whitespace
    checked. No new runtime tests were run for this documentation-only addition; version/assets stay held.
  NEXT: Continue from owner review or the next selected work item.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-22T19:39:53Z
  TYPE: DECISION
  CLAIM: Owner requests closing recent work actually finished. Selected closure set: pool-hook epic,
    pool discovery and implementation tasks, the 0.2.43 release-document task and benchmark selector
    repair. The latter's distinct frozen-configuration finding remains a separate backlog item.
  EVIDENCE:
  - Owner's current turn-in instruction.
  - artifacts/pool_hook_implementation_20260922/source_review.md
  - tickets/tasks/completed/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md
  - tickets/tasks/completed/2026-09-19_repair_benchmark_spell_id_lookup_task.md
  IMPACT: Acceptance is supplied. Promote pool contracts and archive the three patches before closure.
    Broader hook standardization remains deferred in its existing backlog task. Named-lesser/recovery
    proposals, other agents' older work and packaged generation are not part of this closure set.
  NEXT: Promote the bounded pool ownership/reset contracts into canonical documentation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-22T19:45:53Z
  TYPE: DECISION
  CLAIM: Owner-accepted pool work is ready for closure. Canonical architecture/components and five
    descriptors now carry stable map ownership, mutation controls, both Space routes, prewarming,
    disposal-before-reset and graduation baseline adoption. Documentation indexes/graph are refreshed.
  EVIDENCE:
  - artifacts/recent_finished_turn_in_20260922/documentation_receipt.json
  - artifacts/pool_hook_implementation_20260922/source_review.md
  - system_docs/src_architecture.md
  - system_docs/src_components.md
  IMPACT: Existing source/test/performance qualification remains the delivery evidence; no runtime
    code changes or test reruns during archival. Three patch contracts are archived after promotion.
  NEXT: none for implementation; packaging remains on its separate held task.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed by owner instruction. Canonical contracts are promoted and original patches archived.
The existing broad standardization backlog and separate package-generation hold remain in force.

Implementation and qualification are complete for Conduit/Meld controls, root-owned stable maps,
lesser return, manual/managed/prewarmed Space restoration and graduation baseline adoption. Read
artifacts/pool_hook_implementation_20260922/source_review.md for exact semantics, source pointers,
performance costs and test evidence. Final result is 2102 passed/two existing skips; 73 new cases.
No source work remains in this bounded slice. Hold all generated/build assets and version at 0.2.45.
The owner-requested pool-hook release entry is recorded in release_docs/next_version_release.md.
Do not reopen broad hook standardization, Bind semantics or the completed graduation ownership repair.
