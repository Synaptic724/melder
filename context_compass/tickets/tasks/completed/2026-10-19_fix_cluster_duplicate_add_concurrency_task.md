# Task: Repair the same-conduit cluster admission concurrency failure

- Completed: 2026-10-19T23:41:23Z
- Summary: Notched 0.2.8265. Cloud reserves pending admissions so one competing add succeeds,
  with recording/sharing outside the Cloud lock and retry after failed registration. Added the
  release-note section "Concurrent cluster adds admit one caller"; full runtime: 14398 passed.

## Metadata
- Task ID: TASK-2026-10-19-fix_cluster_duplicate_add_concurrency
- Story: none (standalone owner-directed CI repair)
- Status: done
- Owner: Mark
- Agent Name: expert_1
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-19T23:02:00Z
- Updated: 2026-10-19T23:45:54Z
- Patch: cluster_admission_atomic_2026_10_19

## Objective
Repair the reported cluster-concurrency failure with a deterministic regression check and preserve
the established cluster admission contract.

## Problem / Context / MRP
The owner's macOS Python 3.14.1 CI cell reports one failure: eight calls adding the same conduit to
the same cluster leave one membership and zero errors, while the test expects exclusivity errors.
The previous ManagedSpellMode repair is complete and present in the current clean base,
a2d2355dd0c64d7b277af27c6e53214e560ad7cf. This task owns this distinct failure. Correctness means
the smallest durable repair consistent with the actual admission, retry and exclusivity contracts.

## Ticket Contract
- ENTRY_GATE: Retained owner-assigned expert_1 identity and synaptic_python_developer role;
  required recovery reads and attestation complete, own roster checked in, active attention route.
- EXECUTION_BOUNDARY: The reported concurrency module, ConduitCloud admission, ConduitCluster
  membership and their direct transaction/registry collaborators; exact edits selected after diagnosis.
  Include focused regression coverage and required documentation/assets when their inputs change.
- DEPENDENCIES: Current cluster and transaction contracts. Read the historical flake evidence;
  preserve other agents' work and the earlier completed repair.
- EXIT_GATE: Source-backed diagnosis; deterministic before/after evidence; affected tests and required
  runtime tiers pass; distinct author self-review and applicable generated-asset checks recorded.
- FAILURE_ESCALATION: Record actual source-custody collision, unavailable required check, consequential
  contract ambiguity or tool denial. Hold only work depending on that gap.

## Scope Boundaries
- In scope: Reproduce the supplied failure, diagnose runtime-versus-test mismatch, make and verify
  the narrow repair, complete its local records.
- Out of scope: Other defect lanes, CI policy/dependency upgrades, public API redesign, pushes,
  merges, releases, publication, subagents and execution on another machine.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Deterministic negative/positive controls, all cluster checks, early-Python
  regressions, full runtime tiers and distinct self-review passed against unchanged qualified inputs.
  Routine closure is authorized by the owner's repair request; the final rebuild follows turn-in.

## Steps / Checklist
- [x] Recover role/backend/identity and read the supplied failure.
- [x] Trace the admission contract and record the reproduced cause.
- [x] Apply the smallest correct repair with meaningful deterministic regression coverage.
- [x] Run affected checks and the required runtime tiers; report actual limits.
- [x] Perform distinct self-review, synchronize records and close truthfully.
- [x] Use the Ticket Microcycle and record meaningful evidence before dependent work.

## Deliverables
- Focused cluster concurrency repair, without weakening the established contract.
- Retrievable diagnosis, before/after checks, runtime results and final self-review.

## Files / Paths Impacted
- tests/integration/melder/aether/test_aether_integration_cluster_transactions_concurrency.py
- tests/unit/melder/aether/test_conduit_cloud.py
- src/melder/aether/aetheric_frame/conduit_cloud.py (admission reservation, initialization/cleanup and contracts)
- src/melder/__version__.py and release_docs/next_version_release.md at landing
- Relevant test/system documents and generated assets only when changed inputs require them.
- This task and its attention, artifact and session records.

## Validation
- Final reservation implementation: 272 direct cluster checks passed; three admission schedules
  repeated twenty times each in both GIL modes (60 per mode) passed. Original-method negative
  controls fail both forced schedules with the final harness. Callback and failed-retry checks pass.
- Full unit/component/integration driver: 14398 passed, 28 skipped, 17 xfailed, 3 xpassed in 709.50 s,
  exit 0 on Python 3.14.7 free-threaded with exact CI pins and GIL checked off before/after pytest.
- All six focused regression cases also pass on Python 3.14.0 and 3.14.2 with -X gil=0.
- Coverage: Not measured. The pre-existing unawaited-coro shutdown warning remains.
- Hosted macOS/Python 3.14.1 rerun: Not run; the supplied failure is reported evidence.

## Risks / Rollback Notes
- A start barrier does not guarantee overlap at a membership decision. Preserve intentional retries
  and distinguish same-cluster repetition from admission to two different clusters.
- Keep reversible edits scoped to this task; no global runtime, host or permission changes.

## Applicable Anti-Patterns
- [x] No implementation or validation from an unevidenced behavioral assumption.
- [x] No test skip, sleep-based repair or relaxed assertion hiding a real invariant failure.
- [x] No false independent-review or hosted-matrix claim.
- [x] No closure before actual acceptance evidence and board synchronization.

## Done Checklist
- [x] Steps and acceptance criteria complete.
- [x] Required checks and self-review recorded against final files.
- [x] Relevant documentation/index/assets current.
- [x] Notes preserve evidence, limits and compaction usefulness of at least the configured floor.
- [x] Retention and board closure synchronized.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/cluster_duplicate_add_20261019/
  - system_docs/patches/completed/cluster_admission_atomic_2026_10_19/architecture_patch.md
  - system_docs/patches/completed/cluster_admission_atomic_2026_10_19/component_patch_conduit_cloud.md
  - system_docs/patches/completed/cluster_admission_atomic_2026_10_19/code_description_patch_conduit_cloud.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Applied at closure: eight task-owned cache/staging/temp directories removed;
  logs, XML, receipts, original-method control and document baselines retained. Patch contracts
  promoted into the canonical maps and archived with their indexes.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: same-cluster admission, concurrent exclusivity and deterministic scheduling
- IF_UNKNOWN: none

## Noting Behavior
- Tactical source findings, exact evidence, immediate impact and one concrete next action.
- Preserve historical Notes; record meaningful changed findings before dependent work.

## Contribution Attribution
- Ticket/Work Author(s): expert_1; synaptic_python_developer; local diagnosis, repair and verification.
- Published By: local files only; no remote publication.
- Independent Review: none; expert_1 performed a distinct author self-review of the final diff and evidence.

## Notes
- DATETIME: 2026-10-19T23:02:00Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The owner reports one failed assertion, len(errors) >= 1 with errors=[], after same-conduit
    concurrent adds; final membership is correct. The GitHub page could not be fetched by the web tool
    (cache miss); no new hosted result is claimed. Historical records mention this exact flake.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/reported_failure.txt:1-16
  IMPACT: Read the production contract and historical explanation before choosing a runtime or test fix.
  NEXT: Read the cluster component/graph slices and complete admission implementation units.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T23:03:56Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Runtime defect: Cloud checks membership before add_member without a shared critical section;
    the cluster adds to a set and the DevOps registry adds both indexes without exclusivity checks.
    Concurrent empty reads therefore permit repeated success, and can put one conduit in two clusters.
    Serialize cluster lookup, root check, eligibility and member registration under the existing Cloud
    RLock, then release it before handle_join. Preserve the established refusal and its message.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:869-914
  - src/melder/aether/conduit/conduit_cluster.py:429-444
  - src/melder/aether/conduit/conduit_cluster.py:539-606
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:468-505
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1171-1208
  - tests/integration/melder/aether/test_aether_integration_cluster_membership_transactions.py:519-549
  IMPACT: This repairs the code's contract; the flaky test must become deterministic, not relax its oracle.
    The prior S3 and exact-lookup tasks recorded the same baseline flake; neither owned its repair.
    Patch architecture/component/control-flow contracts map admission to the one Cloud critical section;
    forced same/two-cluster schedules verify one success and seven refusals, and broader tests verify
    handle_join remains outside that lock. No new state, transaction, dependency or public API is added.
  NEXT: Capture the ordinary baseline, then force all competing empty reads and confirm red results.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:06:51Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Before source changes, the forced same-cluster schedule admits all eight calls (zero
    errors), and the forced two-cluster schedule leaves the conduit in both clusters. The natural
    schedule also exposes a second success (six errors rather than seven). The sharing-lock-scope
    control passes. Initial unchanged-test invocation passed one case; repeated exact node arguments
    were deduplicated by pytest and are not forty trials.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/forced_red.log:1-23
  - context_compass/artifacts/cluster_duplicate_add_20261019/forced_red.xml:1-2
  - context_compass/artifacts/cluster_duplicate_add_20261019/baseline.log:1-3
  IMPACT: Current source violates both duplicate-refusal and one-cluster exclusivity. Patch contracts
    have been read in architecture -> component -> control-flow order; their admission window maps
    to Cloud.add_conduit_to_cluster, and their exclusion of sharing maps to the new observer control.
    Three race cases replace the original one (the original natural schedule is retained); forced
    discovery uses the real pre-resolved cluster, and all membership/index/share work remains real.
  NEXT: Apply the narrow Cloud admission critical section, then rerun these four checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:07:12Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The narrow critical section is implemented. All four focused checks pass on Python 3.14.7
    free-threaded with -X gil=0: natural contention, forced same-cluster admission, forced two-cluster
    admission and the sharing observer. No other runtime method was changed; the message is preserved.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/conduit_cloud.py:869-925
  - context_compass/artifacts/cluster_duplicate_add_20261019/forced_green.log:1-3
  - context_compass/artifacts/cluster_duplicate_add_20261019/forced_green.xml:1-2
  IMPACT: The forced reproductions are green without skips or a relaxed oracle. Broader verification,
    repeat runs, contribution notch, documentation/graph updates and final asset checks remain.
  NEXT: Run all direct cluster tests and repeated admission schedules before the final notch/runtime suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T23:09:08Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: All 270 direct cluster tests pass. The three admission schedules each pass twenty repeats
    with the GIL off and twenty with it on (60 executed cases per mode, 140 other collected cases
    deselected per repeat command). Read the current 0.2.8264 and notched 0.2.8265 for this source
    change; added "Concurrent cluster adds admit one caller" to the running release note.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/cluster_suite.log:1-6
  - context_compass/artifacts/cluster_duplicate_add_20261019/repeat_gil0.log:1-3
  - context_compass/artifacts/cluster_duplicate_add_20261019/repeat_gil1.log:1-12
  - src/melder/__version__.py:12-12
  IMPACT: Repeated schedules and surrounding cluster operations are green; full runtime qualification
    will run at the final notch, then generated assets will be rebuilt after documentation and closure.
  NEXT: Synchronize the relevant document/graph records and launch the full runtime tiers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-19T23:14:40Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Final lock review found an outward call inside add_member: _emit_cluster_record calls
    Crystallizer.emit, which can stream through a user store handler. The initial critical section
    therefore holds the Cloud lock across a recording callback. The sharing observer alone does
    not verify this additional callback path; the initial repair needs refinement before acceptance.
  EVIDENCE:
  - src/melder/aether/conduit/conduit_cluster.py:373-415
  - src/melder/aether/conduit/conduit_cluster.py:429-444
  - src/melder/crystallizer/crystallizer.py:1619-1672
  - src/melder/crystallizer/asset_management/asset_management_system.py:994-1036
  IMPACT: Add a recording-boundary observer, then reserve a pending conduit id under the Cloud lock
    and release the lock before registration/recording. Clear the reservation in finally. This keeps
    atomic admission in one class without a new registry API or a Cloud-to-cluster lock hold.
  NEXT: Prove the callback regression on the initial repair and update the patch contracts accordingly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:14:40Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The new callback control fails on the initial repair (membership recording cannot complete
    a Cloud read from another thread); sharing and failed-registration retry controls pass. Replace
    the lock-across-add design with a Cloud-owned pending-id reservation. Its check/set is atomic
    under the existing Cloud RLock; registration and sharing happen outside it. Finally releases
    the reservation after add_member returns or raises. This supersedes the earlier lock-window design.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/callback_red.log:1-26
  - system_docs/patches/completed/cluster_admission_atomic_2026_10_19/code_description_patch_conduit_cloud.md:6-18
  IMPACT: One new ephemeral set keeps the fix in ConduitCloud with no API or registry change, and
    avoids holding Cloud while record emission calls user code. Same task/notch 0.2.8265. Patch
    architecture/component/control-flow records are reconciled before the revised implementation.
  NEXT: Apply the reservation, rerun all cluster checks and validate the updated forced schedules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:24:32Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Final reservation implementation passes 272 cluster tests and 60 repeated admission cases
    per GIL mode. The final harness against only the original admission method fails both forced
    schedules, confirming its detection. Four document indexes and the graph were refreshed; baseline
    multisets account for every old line except the intended metadata/count replacements. Test core
    union and map both contain 282 paths. Only the Cloud and version descriptors were replaced from
    staged extraction; unrelated stale/unverified authored nodes were preserved.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_cluster_suite.log:1-6
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_repeat_gil0.log:1-3
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_repeat_gil1.log:1-12
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_harness_original_method.log:1-19
  - context_compass/artifacts/cluster_duplicate_add_20261019/documentation_verification.json:1-36
  IMPACT: Candidate assets/bundles are current at 0.2.8265 for the full runtime qualification's stamp
    checks. They will be rebuilt/checked again after closure as the contribution guide requires.
    The full local driver was accepted and started through the supported per-command escalation
    route: prior sandboxed asyncio loopback tests stalled. No host configuration, ACL or account
    change was made. Qualification inputs record 32 changed code/test/doc/generated hashes.
  NEXT: Follow the full runtime run to completion, finish the distinct self-review and close/rebuild.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:41:23Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Accept this repair under the owner's assignment after distinct author self-review. The full
    driver exited 0: 14398 passed, 28 skipped, 17 xfailed and 3 xpassed; all six new/strengthened cases
    appear as passes in its JUnit. The 32 qualified input hashes and base revision remain unchanged.
    Each of the six focused cases also passes on local Python 3.14.0 and 3.14.2. The final diff keeps
    the API/error text, guards claim publication atomically, clears claims on registration failure,
    releases Cloud before callbacks/transactions and cleans the new owned set. The initial callback
    issue was caught during review and corrected. This is self-review, not independent review.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/verification_receipt.json:1-75
  - context_compass/artifacts/cluster_duplicate_add_20261019/qualification_inputs.json:1-60
  - context_compass/artifacts/cluster_duplicate_add_20261019/full_runtime.log:1-203
  - context_compass/artifacts/cluster_duplicate_add_20261019/floor_3140.xml:1-2
  - context_compass/artifacts/cluster_duplicate_add_20261019/patch_3142.xml:1-2
  IMPACT: Required local criteria are met; hosted macOS/3.14.1 remains unrun, and no coverage number is
    claimed. Scoped documentation preservation, indexes, joins and changed extents passed; untouched
    document/source areas were not resurveyed. Known whole-entry/exit rollback/teardown semantics stay
    outside this repair. No pushes, releases, agents or other machines were used. Evidence retained,
    temporary artifacts removed, patch contracts promoted/archived and routing closed in this pass.
  NEXT: Run the post-closure asset/bundle rebuild and checks as the final hand-back step.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-10-19T23:45:54Z
  AUTHOR: expert_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Post-closure asset and LLM rebuilds/checks exited 0: all three package assets are current at
    0.2.8265 and all three bundle fingerprints/output proofs match. Every one of the 32 qualification
    input hashes remains unchanged. Completed ticket/board routing, twelve-anchor cap, six-file patch
    archive and removal of all eight temporary directories were verified; retained evidence remains.
  EVIDENCE:
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_assets_check.log:1-4
  - context_compass/artifacts/cluster_duplicate_add_20261019/final_bundles_check.log:1-4
  - context_compass/artifacts/cluster_duplicate_add_20261019/verification_receipt.json:1-79
  IMPACT: The complete local repair is ready for hand-back; no required local work remains.
  NEXT: None. Hosted macOS/Python 3.14.1 qualification remains an explicitly unrun environment.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Completed at 0.2.8265 on a2d2355d plus the local delta. Pending-id reservations enforce one admission;
recording/sharing hold no Cloud lock and failed registration releases the reservation. Original-method
controls fail, final cluster/repeat/early-Python checks pass, and full runtime qualification passes
14398 cases with exit 0 and unchanged inputs. Distinct self-review complete. Four canonical maps and
their indexes plus the scoped graph are current; patches archived and temporary files removed.
Post-closure asset/bundle rebuilds and checks passed with every qualified input hash unchanged.
No required local work remains. Hosted macOS/3.14.1 remains unrun.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
