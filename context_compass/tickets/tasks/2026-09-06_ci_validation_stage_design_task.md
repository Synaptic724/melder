# Task: Implement full qualification at selected branch stages

## Metadata
- Task ID: TASK-2026-09-06-ci-validation-stage-design
- Story: none (owner-approved CI stage implementation)
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-06T01:04:31Z
- Updated: 2026-09-06T10:45:04Z

## Objective
Implement the agreed test policy without repeating the full runtime matrix for unchanged promotions while
preserving useful dev feedback, preprod qualification and the owner's careful final release check.

## Ticket Contract
- ENTRY_GATE: Existing certification, owner implementation approval, active route and consumed patch contracts.
- EXECUTION_BOUNDARY: CI/candidate/source-proof workflows, standalone CI policy/qualification helpers,
  focused workflow tests, branch guide, derived tests/other corpora and this task's records.
- DEPENDENCIES: Accepted candidate workflow task under tasks/completed and current GitHub workflow files.
- EXIT_GATE: Stage-specific execution and exact-tree proof are implemented, negative paths and workflow
  wiring pass local checks, and owner rollout requirements are explicit.
- FAILURE_ESCALATION: Do not treat a branch name or an unrelated green run as proof for changed contents.
  Keep actual release publication and all commit/push/signing activity under owner control.

## Scope Boundaries
- In scope: runtime suite frequency, source qualification records and safe light promotion checks.
- Out of scope: runtime fixes, new deployment services, branch renames, commits, pushes and publication.
- Owner clarified that feature pushes are not the concern; discussion concerns full suites at each stage.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Implementation, focused workflow tests, actionlint, scoped correctness lint,
  generated-asset freshness and patch-index checks are complete. Owner rollout remains pending.

## Previous Behavior (before this change)
- CI handles PRs to dev, preprod, release_candidate and prod, plus pushes to dev/preprod/prod.
- Each such CI run calls the complete unit/component/integration matrix on Linux, Windows and macOS.
- RC branch pushes already use package build, TestPyPI upload and isolated consumer probes only.
- Final publication invokes a fresh full runtime matrix before building/publishing.
- A simple feature-PR-to-final-release route can therefore launch eight full matrices, before revisions/reruns.

## Accepted Stage Policy
| Stage | Full runtime suite | Purpose |
| --- | --- | --- |
| Feature PR into dev | yes | Catch defects before integration |
| dev PR into preprod | yes | Qualify the integrated candidate and its package |
| preprod into release_candidate | no for already-qualified contents | Verify provenance, build and test the installed TestPyPI package |
| release_candidate into prod | no for already-qualified contents | Require the selected candidate, matching tree and final version |
| Final PyPI publication | yes | Preserve the owner's fresh final safety check |
| Post-merge pushes | no duplicate for an already-tested merge result | Keep necessary lightweight branch/publication checks |

Qualification reuse must bind to the actual tested contents and relevant test/build inputs.
Changed code, dependencies or qualification configuration needs another full pass. Full validation also
runs for release-fix PRs and explicit manual CI. Automatic permanent-branch CI push triggers are removed;
PR checks, RC push qualification and final publication remain the authoritative boundaries.

## Steps / Checklist
- [x] Read the current CI/runtime/candidate/publisher wiring.
- [x] Separate PR triggers from the repetition of full test execution.
- [x] Agree the stage policy and the exact evidence needed for promotion.
- [x] Implement stage flags, strict aggregation and full-run source qualification records.
- [x] Verify provenance before RC admission and retain exact-source checks before prod/publication.
- [x] Validate negative paths, regenerate assets and document rollout.

## Deliverables
- Implemented stage-to-check mapping, exact-tree proof and operator guidance for fresh qualification.

## Validation
- Final focused workflow suite: 330 passed, no failures/errors/skips; JUnit evidence linked below.
- All nine workflows pass actionlint; scoped correctness Ruff (E9,F63,F7,F82) passes.
- All repository corpora, source asset groups, three patch indexes and git diff --check pass.
- Default Ruff has 17 style/typing findings; details and policy conflicts are recorded in validation.md.
- Hosted Actions and publication have not been dispatched; the owner handles rollout and signing.

## Risks / Open Questions
- First rollout must establish a full-CI qualification artifact before lightweight promotion.
- Exact-tree reuse intentionally refuses changed contents, expired evidence or unsuccessful qualification.
- Hosted rollout remains unverified locally. The final full-suite publication check remains required.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/ci_stage_qualification_20260906/validation.md
  - artifacts/ci_stage_qualification_20260906/workflow-tests.xml
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/architecture_patch.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/architecture_patch_index.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/component_patch_ci_profiles.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/component_patch_ci_profiles_index.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/code_description_patch_source_proof.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/code_description_patch_source_proof_index.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Promote durable behavior to .github/BRANCH_WORKFLOW.md at accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record implementation and validation against the agreed stage policy, with one concrete next step.

## Notes
- DATETIME: 2026-09-06T01:04:31Z
  TYPE: FACT
  CLAIM: CI always calls test-runtime for the four PR destinations and three permanent-branch push
    triggers. That reusable workflow runs all three tiers on all three platforms. RC pushes alone
    are already package-only; the extra runtime runs occur in promotion PR CI and branch-push CI.
    Owner clarified that PR triggers themselves are fine and asks to discuss suite frequency.
  EVIDENCE:
  - .github/workflows/ci.yml:6-15
  - .github/workflows/ci.yml:55-65
  - .github/workflows/test-runtime.yml:12-36
  - .github/scripts/run_runtime_tests.py:19-40
  - .github/workflows/release-candidate.yml:28-34
  - .github/workflows/python-publish.yml:63-74
  IMPACT: Reduce repeated full qualification rather than misdiagnosing a feature-push trigger.
  NEXT: Discuss full suites at dev, preprod and final publication, with lighter exact-content promotions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T09:52:00Z
  TYPE: DECISION
  CLAIM: Owner approved the three-checkpoint policy and asked to continue implementation. Use a
    tiny full-CI qualification artifact binding run/attempt, event/PR identity and actual checkout
    tree. A source-proof reusable workflow selects verified full CI, downloads through the official
    action and checks the record. Light preprod-to-RC PRs and RC push admission require this proof.
    Release-fix/manual CI remain full; prod consumes exact successful RC evidence.
  EVIDENCE:
  - Owner instructions: "ok go ahead and update this stuff, properly in the workflows"; "ok continue".
  - .github/workflows/ci.yml:6-103
  - .github/scripts/ci_policy.py:89-110
  - .github/scripts/check_candidate_run.py:54-123
  IMPACT: Removing full jobs alone would break strict aggregation and lose qualification. Update
    profiles and aggregation together. Remove duplicate CI push triggers; keep the existing final
    publication matrix. Add bounded waiting only for legitimately pending RC evidence so a fast
    prod PR does not recreate the earlier timing race. Owner retains all commits/pushes/publication.
  NEXT: Consume the patch contracts and verify GitHub artifact/PR association interfaces before edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:01:16Z
  TYPE: FACT
  CLAIM: Stage flags/strict aggregation, bounded pending-RC waiting, full-source JSON records and
    the read-only source-verification workflow are implemented. RC build/publish now depend on
    source proof; full CI alone records qualification. Official download-artifact v8 supports a
    specific immutable artifact ID with run-id/repository/token, so no custom archive downloader
    or credential-forwarding redirect handler is needed. Scoped correctness Ruff passes.
  EVIDENCE:
  - .github/scripts/ci_policy.py
  - .github/scripts/ci_qualification.py
  - .github/scripts/check_candidate_run.py
  - .github/workflows/verify-source-qualification.yml
  - https://raw.githubusercontent.com/actions/download-artifact/v8/README.md
  IMPACT: Implementation is not yet qualified. Verify actual merged-PR API shape, then test all
    profiles, record identity, failed/expired evidence, changed attempts and bounded wait behavior.
  NEXT: Validate source-selection API assumptions and update focused regression coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:03:32Z
  TYPE: FACT
  CLAIM: Actual GitHub data confirms preprod commit a4de3adc maps to merged PR 137 with expected
    head/base merge parents. Its successful CI run 33986010784 attempt 2 has pull_requests=[] after
    closure. Therefore run.pull_requests cannot be required to identify a historical full run.
    Select the latest exact head/ref/event run and require its downloaded record to prove the
    original PR number, base/head IDs and tree; mismatched records refuse rather than falling back.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder/commits/a4de3adc1cbcab4a58486b1d5ee68d41e3f01dbf/pulls
  - https://github.com/Synaptic724/melder/actions/runs/33986010784
  IMPACT: Fix this real API assumption before validation; the record provides event identity that
    GitHub's historical run association omits. Ambiguous/mismatched history needs fresh manual CI.
  NEXT: Update selection and regression cases for empty historical PR associations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:16:55Z
  TYPE: MEASURE
  CLAIM: All 19 parsed workflow checks and scoped correctness Ruff pass. The first broader run
    reports 260 passed and 66 setup errors because the sandbox cannot access pytest-of-Mark under
    the Windows user temp directory. This is not a full pass. Oversized-input test IDs were named
    explicitly to prevent pytest from expanding a 64 KiB fixture into failure-report names.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py
  - tests/unit/github_workflows/test_source_qualification.py
  IMPACT: Rerun unchanged test scope outside the sandbox with a fresh task-owned temporary directory.
  NEXT: Execute all workflow unit tests with isolated temp storage and retain the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T10:22:31Z
  TYPE: MEASURE
  CLAIM: All 325 workflow-unit tests pass outside the Windows sandbox with isolated task temp
    storage. This includes profile/skip requirements, full-record roundtrip across different merge
    SHAs, closed-PR association handling, manual/release-fix paths, bad/expired/changed evidence,
    pending-RC deadlines and preserved final publisher checks.
  EVIDENCE:
  - artifacts/ci_stage_qualification_20260906/workflow-tests.xml
  - tests/unit/github_workflows/test_source_qualification.py
  - tests/unit/github_workflows/test_candidate_publication.py
  IMPACT: Functional unit validation passes. Complete workflow lint, operator guidance and derived
    assets; verify the current artifact action's single-file download contract before finalizing.
  NEXT: Check artifact transfer semantics and update the branch guide for the new stage policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:35:43Z
  TYPE: FACT
  CLAIM: Consumed closure notices from codex_1 and codex_2. They report their owned tickets closed
    with no competing CI edits or asset regeneration. The runtime cases remain explicitly deferred,
    not repaired. Artifact action v7 defaults to ZIP archive mode, preserving the run/attempt name
    and qualification.json path; v8 downloads the selected ID with digest mismatch treated as failure.
  EVIDENCE:
  - tickets/tasks/completed/2026-09-06_turn_in_codex_1_tickets_task.md
  - artifacts/2026-09-06_codex_2_ticket_closure.md
  - https://raw.githubusercontent.com/actions/upload-artifact/v7/action.yml
  - https://raw.githubusercontent.com/actions/download-artifact/v8/README.md
  IMPACT: Qualification transfer semantics are verified against official action definitions.
    Actionlint passes all nine workflows; guide and added boundary regressions are ready for final
    validation. A task-local ignore file keeps temporary test/tool files out of commits and discovery.
  NEXT: Run final workflow tests and regenerate the affected repository corpora and patch indexes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:41:01Z
  TYPE: MEASURE
  CLAIM: The final focused JUnit report contains 330 tests, zero failures/errors/skips and 1.119s
    suite time. Current HEAD is 9ab23f6f6; the owner has committed the workflow/helper implementation.
    Remaining working edits include the guide and added source-proof/workflow regressions. RC is a
    deliberate preprod-to-RC promotion: the RC branch push triggers TestPyPI, not a preprod push.
  EVIDENCE:
  - artifacts/ci_stage_qualification_20260906/workflow-tests.xml:1-1
  - .github/workflows/release-candidate.yml:1-40
  - .github/workflows/ci.yml:1-12
  IMPACT: Focused behavior validation is complete. Preserve owner commits and unrelated cleanup;
    finish the derived corpus/index updates before handing over the change.
  NEXT: Regenerate the tests/other corpora and all three patch indexes, then verify freshness.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:41:01Z
  TYPE: FACT
  CLAIM: Rebuilt the affected repository corpora: tests contains 808 inputs, other contains 354;
    the shared manifest was refreshed. All three patch indexes were generated with their 17
    section ranges checked against the source headings.
  EVIDENCE:
  - artifacts/ci_stage_qualification_20260906/validation.md:11-14
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/architecture_patch_index.md:10-37
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/component_patch_ci_profiles_index.md:10-35
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/code_description_patch_source_proof_index.md:10-35
  IMPACT: Derived outputs now include the final workflow tests and operator guidance.
  NEXT: Verify all corpus/source-asset and patch-index checks, then prepare owner review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T10:44:00Z
  TYPE: MEASURE
  CLAIM: All repository corpora, source assets and three patch indexes pass freshness checks.
    An additional default Ruff invocation reports 17 style/typing findings, including Optional
    syntax required by the role and intentional ValueError boundary contracts. This is distinct
    from the earlier passing scoped correctness lint; no default-Ruff-clean claim is made.
  EVIDENCE:
  - artifacts/ci_stage_qualification_20260906/validation.md:13-21
  - .github/scripts/ci_qualification.py:27-32
  - .github/scripts/ci_policy.py:28-32
  IMPACT: Derived-output gates pass. Retain the established boundary contracts and avoid unrelated
    formatting or typing-policy changes while closing out this workflow task.
  NEXT: Complete scoped correctness lint and inspect the final diff for implementation gaps.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-06T10:45:04Z
  TYPE: DECISION
  CLAIM: The workflow task is ready for owner review. Final source/workflow review confirms full
    checks at dev/preprod and final publication, exact-tree evidence for unchanged promotions,
    full release-fix/manual paths and dedicated TestPyPI qualification after an RC branch push.
    Scoped Ruff E9,F63,F7,F82 and git diff --check pass. Generated assets/indexes are current.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:5-141
  - .github/workflows/ci.yml:1-135
  - .github/workflows/python-publish.yml:60-116
  - artifacts/ci_stage_qualification_20260906/validation.md:1-24
  IMPACT: No remaining implementation step is identified. Owner must commit remaining guide/tests/
    generated files, promote through dev/preprod and observe the first hosted proof/artifact run.
  NEXT: Owner reviews and rolls out the qualified workflow change; ticket closure awaits acceptance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Stage-specific CI, strict result aggregation, full-CI source records, lightweight RC/prod proof and
bounded pending-RC waiting are implemented. Final publication still runs full validation. All 330
focused tests, actionlint, scoped correctness Ruff, generated-asset and patch-index checks pass.
Default Ruff style/typing findings are recorded separately; no blanket lint-clean claim is made.
The guide documents initial qualification, exact-tree refusal, release fixes and bounded RC waiting.
The task is in review. The owner signs/commits/pushes and validates hosted rollout. No hosted workflow
or publication was dispatched. Close and apply artifact dispositions only after owner acceptance.
