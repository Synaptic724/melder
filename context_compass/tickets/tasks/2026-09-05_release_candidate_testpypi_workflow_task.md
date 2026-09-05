# Task: Qualify a frozen release candidate through TestPyPI before production

## Metadata
- Task ID: TASK-2026-09-05-release-candidate-testpypi-workflow
- Story: none (successor to accepted branch CI foundation)
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-05T10:25:12Z
- Updated: 2026-09-05T13:41:13Z

## Objective
Extend the promotion route to dev -> preprod -> release_candidate -> prod. Keep preprod as full
continuous validation. The selected candidate is tested through TestPyPI and identified by exact
commit, version, workflow run, and distribution hashes before final production publication.

## Ticket Contract
- ENTRY_GATE: Existing certification, this active route, and consumed patch contracts before edits.
- EXECUTION_BOUNDARY: .github workflows/scripts/ruleset payloads/branch guide; focused workflow and consumer tests;
  generated llm_support assets; this ticket and its associated coordination/artifact rows.
- DEPENDENCIES: tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md.
- EXIT_GATE: Branch gates and candidate/publication workflow are implemented and locally validated;
  owner-only setup/rollout and unexecuted external publication checks are explicitly recorded.
- FAILURE_ESCALATION: Never publish packages, commit, push, rename owner branches, or silently bypass
  candidate identity. Record missing external setup, incompatible versions, or provenance gaps.

## Scope Boundaries
- In scope: release_candidate branch routes, TestPyPI qualification, exact artifact identity,
  fresh final validation and publication linkage, regression tests, and deployment guidance.
- Owner owns the branch rename and all commits/pushes. Local release_candidate already exists.
- No automatic preprod-to-candidate advancement: candidate selection remains deliberate.
- Actual registration, trusted-publisher activation, package uploads, and dated scheduling are not
  performed by this local implementation. Their required configuration will be documented.
- Preserve other agents' source, documentation, tests, and generated outputs.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The reported working-directory failure was reproduced and repaired with an
  isolated test fixture. All 263 focused tests pass from both repository root and tests/; generated
  test assets and scoped lint pass. Production gate/workflow code is unchanged by this repair.

## Steps / Checklist
- [x] Inspect existing shared CI, branch policy, packaging, and publication contracts.
- [x] Define and consume the candidate identity, artifact, trigger, and failure contracts.
- [x] Extend branch routing and create the candidate ruleset payload.
- [x] Implement TestPyPI upload/installed-package verification and retained qualification evidence.
- [x] Require matching candidate evidence during fresh final publication.
- [x] Validate route/provenance/failure cases and workflow wiring; refresh affected assets.
- [x] Present owner setup/rollout and explicitly separate local checks from hosted execution.

## Deliverables
- Reviewed workflow/helper/test changes for the four-stage permanent-branch route.
- Durable operator instructions including TestPyPI project and GitHub environment configuration.

## Validation
- 2026-09-05T13:41:13Z repair: 263 focused tests pass from repository root and another 263 pass
  from tests/. The original test failed from tests/ before the fixture repair. Reports: cwd-root.xml,
  cwd-tests.xml in the task validation directory. Test corpus regeneration/check and scoped Ruff pass.
- 263 focused workflow/package/asset-builder tests pass on local Python 3.14t.
- All eight workflows pass actionlint 1.7.12; optional shellcheck/pyflakes were disabled.
- Scoped correctness Ruff E4/E7/E9/F and whitespace checks pass.
- A disposable snapshot of committed 81e62df62c67978fa9d06d909f803c61b9f332b0 was built with freshly
  generated snapshot assets. Real wheel/sdist verification and the isolated Windows consumer probe pass.
- Repeated snapshot builds had identical file payloads but differing tar metadata. The new normalizer
  produces identical sdist SHA256 A9ED1747F199CE9A3AF3B3DF4073EABDEFC1D9C942DDE9149F24A9C8031A0E9A.
- Repository tests/other bundles were regenerated and their exact fingerprint/output checks pass.
- Source assets were stale during the initial workflow pass; read-only checks on 2026-09-05T13:41:13Z
  now report all three current after the other lane's work. This repair did not rewrite source assets.
- TestPyPI upload/OIDC and hosted Linux/Windows candidate qualification: Not run. No package uploaded.
- GitHub environment pypitest and its sole release_candidate branch policy are GET-verified.

## Risks / Rollback Notes
- Owner reports TestPyPI setup ready. GitHub environment is verified; TestPyPI-side pending/trusted
  publisher binding still needs the first real workflow run to prove end-to-end authentication.
- TestPyPI files cannot be silently replaced; retries must establish identical content or refuse.
- A prod merge commit can have a different SHA: require the selected candidate tree to match the
  production checkout and keep the existing final live tag/prod guard.
- Earlier successful candidate evidence must not qualify later branch changes or different bytes.
- Rollback branch policy, workflow callers, and required checks together through the owner's rollout.

## Applicable Anti-Patterns
- [x] No test result applies to a different version/tree/artifact.
- [x] No upload authority in PR/install-test jobs.
- [x] No mutable branch-tip lookup substitutes a different candidate for the fixed prod merge parent.
- [x] No blind skip-existing or unverified reuse after partial upload.
- [x] No false hosted-validation claim and no closure before owner acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/release_candidate_20260905/validation.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch_index.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate_index.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication_index.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity_index.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Owner-accepted closure after promotion into .github/BRANCH_WORKFLOW.md;
  preserve original patch records under patches/completed.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: candidate identity, TestPyPI round-trip, production artifact promotion.
- IF_UNKNOWN: none

## Noting Behavior
- Append findings and their evidence before changing execution scope or starting validation.

## Notes
- DATETIME: 2026-09-05T10:25:12Z
  TYPE: DECISION
  CLAIM: Owner steered TestPyPI automation onto a separate release_candidate branch, keeping
    preprod for comprehensive testing/version checks. Corrected spelling is release_candidate;
    git branch confirms that local branch exists. The working checkout remains codex_features2.
    Version policy was asked asynchronously: recommended staging uses the intended final version,
    while an actual rc1/rc2 version would require a distinct final build and qualification.
  EVIDENCE:
  - Owner steering and branch-renaming messages on 2026-09-05, recorded here.
  - .github/scripts/ci_policy.py:16-90
  - .github/workflows/ci.yml:6-83
  IMPACT: Add one deliberate candidate stage; do not turn it into another continuously moving preprod.
  NEXT: Complete the candidate artifact/provenance contract and record the implementation mapping.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:25:12Z
  TYPE: FACT
  CLAIM: Shared CI already runs runtime tests/docs/assets/hygiene and builds distributions for
    preprod/prod. Packaging verifies source/metadata/generated-manifest version agreement and a
    clean installed-wheel smoke probe. Publication currently rebuilds and publishes its own run's
    artifacts, with no TestPyPI candidate-evidence requirement. The package version is 0.2.3.
  EVIDENCE:
  - .github/scripts/verify_distributions.py:79-184
  - .github/scripts/smoke_wheel.py:6-35
  - .github/workflows/python-publish.yml:18-109
  - src/melder/__version__.py:12-12
  IMPACT: Reuse existing checks and explicitly bind final publication to the newly qualified files.
  NEXT: Define candidate selection and artifact checks before editing workflow/helper code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T10:35:26Z
  TYPE: FACT
  CLAIM: The owner reports TestPyPI ready and asks for the trigger, installed-package testing,
    version/tag policy, and professional release flow before publisher wiring. tests/conftest.py
    explicitly inserts src and the repository root into sys.path, so running that suite unchanged
    after pip installation can still test checkout code. Keep it for source validation and add a
    small consumer suite executed outside the checkout, without this conftest or editable installs.
  EVIDENCE:
  - tests/conftest.py:1-22
  - .github/scripts/smoke_wheel.py:6-35
  - UX_and_AIX_experiences/01_beginner/01_hello_meld.py:20-33
  - UX_and_AIX_experiences/01_beginner/10_explicit_cleanup.py:16-30
  IMPACT: Consumer tests should verify installed origin/version, public binding/resolution/lifecycle,
    and packaged data on both supported OSes. They complement the source suite.
  NEXT: Present the concrete trigger and version/tag contract before resolving publisher wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:35:26Z
  TYPE: PLAN
  CLAIM: With a dedicated candidate branch, recommend explicit rcN package versions for repeated
    candidates (illustrative 0.2.4rc1, 0.2.4rc2), followed by an explicit final version (0.2.4).
    Source version remains authoritative and assets are regenerated with each version change;
    a Git tag labels a commit and never rewrites package metadata. Pushes to release_candidate can
    trigger TestPyPI independently of GitHub Release events. The final-version candidate must be
    built and qualified again before prod can publish identical retained final-version files.
    This clarifies the earlier same-files recommendation: rcN files are never renamed to final.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - .github/scripts/verify_distributions.py:166-194
  - https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push
  - https://packaging.python.org/en/latest/specifications/version-specifiers/#pre-releases
  - https://pypi.org/help/#file-name-reuse
  IMPACT: Version policy remains a visible design choice. Existing identical uploads may be verified
    and reused; changed artifacts must get a new candidate version rather than blind skip-existing.
    Finalization/fixes need a reviewed path on the frozen candidate, with changes carried back to dev.
  NEXT: Resolve the pending version-model choice and update the draft patch contract before code edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:42:25Z
  TYPE: FACT
  CLAIM: Source CI installs Melder editable and the root conftest puts src first. Some existing
    package tests are reusable against an installed package: the metadata/asset tests locate files
    through melder.__file__. Workflow-contract tests intentionally read repository .github files.
    Preprod already runs an isolated locally built wheel probe; TestPyPI therefore adds publication,
    index retrieval, and exact downloaded-file identity coverage rather than another source suite.
    Full-suite installed-target compatibility has not been executed or established in this review.
  EVIDENCE:
  - tests/conftest.py:1-22
  - tests/unit/melder/test_package_version_metadata.py:22-114
  - tests/unit/github_workflows/test_workflow_contracts.py:12-21
  - .github/workflows/test-runtime.yml:29-35
  - .github/workflows/build-distributions.yml:53-68
  IMPACT: Prefer reusing a small relevant consumer contract set plus version/hash/import-origin checks;
    do not duplicate the full test suite solely because the same wheel passed through TestPyPI.
  NEXT: Explain the distinct source, installed-wheel, and index-round-trip guarantees to the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T10:42:25Z
  TYPE: FACT
  CLAIM: Current test_version_is_well_formed rejects canonical rcN spelling such as 0.2.4rc1:
    its optional suffix must begin with dot, dash, or plus. An explicit RC-version policy will
    require correcting this contract test alongside the version pipeline, not merely adding YAML.
  EVIDENCE:
  - tests/unit/melder/test_package_version_metadata.py:4-19
  - https://packaging.python.org/en/latest/specifications/version-specifiers/#pre-releases
  IMPACT: The proposed candidate-version format has a concrete existing-suite integration requirement.
  NEXT: Include RC version acceptance/rejection cases if the owner selects rcN package versions.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-05T10:42:25Z
  TYPE: FACT
  CLAIM: Consumed codex_1's notice: ordered-disposal runtime is in review with 2,797 selected tests
    passing, while configuration transport, crystal capture/restore/graft ordering, canonical docs,
    and final generated assets remain pending. Those runtime results are not full release qualification.
  EVIDENCE:
  - tickets/tasks/2026-09-04_ordered_disposal_creations_task.md
  IMPACT: Preserve that lane and require complete candidate qualification after its remaining work.
  NEXT: Continue this CI design discussion without treating partial runtime evidence as release-ready.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-05T10:50:07Z
  TYPE: DECISION
  CLAIM: Owner explicitly approved the slimmed-down implementation and selected pypitest as the
    GitHub environment. Create release-candidate.yml for branch pushes plus manual retries, reuse
    package build verification, and run only small installed-package checks after TestPyPI upload.
    Keep source tests in preprod and fresh final production tests. Do not build a cross-run artifact
    promotion engine or duplicate the full source suite in TestPyPI qualification.
  EVIDENCE:
  - Owner approval and environment selection on 2026-09-05, recorded here.
  - .github/workflows/build-distributions.yml:28-68
  - .github/scripts/smoke_wheel.py:6-35
  IMPACT: This supersedes the larger draft contract's retained-artifact production publisher.
    The committed package version is used unchanged (stable or rcN); no automatic version rewrite.
    Require the candidate workflow's successful exact source revision before prod promotion/release;
    production still builds and verifies its own fresh final distribution.
  NEXT: Update/read the slim patch contracts and implement the named workflow, helpers, and tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-05T10:50:07Z
  TYPE: PLAN
  CLAIM: The revised patch contracts were read in architecture/component/control-flow order.
    Mapping: branch boundaries -> ci_policy.py and ci.yml -> route/parsed-workflow regressions;
    TestPyPI identity/retries -> testpypi_candidate.py and release-candidate.yml -> network/process
    boundary tests; consumer contract -> smoke_wheel.py -> a real local installed-wheel probe;
    final source provenance -> check_candidate_run.py plus CI/publication steps -> exact-SHA/tree,
    failed/forged-run tests. Final runtime/build validation stays in the existing publisher.
  EVIDENCE:
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch.md:11-32
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md:3-23
  IMPACT: Entry/read/mapping gates are satisfied for the approved slim implementation.
  NEXT: Implement the workflow and its scoped helpers, then validate their negative paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T10:50:07Z
  TYPE: FACT
  CLAIM: The slim workflow/helper implementation is written. release-candidate.yml binds pypitest
    only to its OIDC upload job; Linux/Windows probes use the exact run/attempt distributions and a
    hash-required TestPyPI download. Branch policy now includes the candidate stage and release-fix/*
    preparation route. Prod checks consume exact-source successful candidate evidence while keeping
    the existing fresh production tests/build and final tag/prod guard. Focused regressions are added.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:1-122
  - .github/scripts/testpypi_candidate.py:1-195
  - .github/scripts/check_candidate_run.py:1-115
  IMPACT: Ready for local validation; no hosted workflow, upload, commit, or push has been performed.
  NEXT: Run the focused regression suite and lint, then exercise a real local installed wheel.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T11:12:03Z
  TYPE: MEASURE
  CLAIM: The sandboxed focused run reached 257 collected cases but Windows denied pytest's
    task-local temporary directory and teardown. This is an environment failure, not a passing
    suite. Correctness Ruff found two unused imports; both were removed before the retry.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_publication.py:1-292
  - .github/scripts/check_candidate_run.py:1-115
  IMPACT: Rerun the same focused scope outside the sandbox, preserving the tests and their assertions.
  NEXT: Execute the focused suite with a new task-owned temporary directory and record the result.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-09-05T11:16:03Z
  TYPE: MEASURE
  CLAIM: Focused validation passes 257 tests outside the Windows sandbox. Scoped correctness Ruff
    passes. The official actionlint 1.7.12 archive was checksum-verified. A read-only GitHub request
    returned 404 for pypitest. Shared source-asset checks report stale agent-documentation and bind
    manifests from the ongoing runtime lane; system-document assets remain current.
  EVIDENCE:
  - artifacts/release_candidate_20260905/focused.xml
  - .github/workflows/release-candidate.yml:1-121
  - https://api.github.com/repos/Synaptic724/melder/environments/pypitest
  IMPACT: Preserve other agents' source/assets. Validate the real package in a disposable committed
    snapshot with regenerated local assets, and create the owner-named publishing environment.
  NEXT: Lint all workflows and build/test the isolated local package snapshot.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-05T11:21:24Z
  TYPE: FACT
  CLAIM: GitHub pypitest environment was created and GET-verified with one custom deployment
    policy: branch release_candidate (policy ID 59177914). No other branch/tag is allowed and no
    PyPI secret was created. All eight current workflows pass checksum-verified actionlint 1.7.12
    with optional shellcheck/pyflakes disabled. Real-package build needs the same Windows sandbox
    exception as pytest; the unrestricted build is running against a disposable source snapshot.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder/environments/pypitest
  - https://api.github.com/repos/Synaptic724/melder/environments/pypitest/deployment-branch-policies
  - .github/workflows/release-candidate.yml:35-45
  IMPACT: The owner's TestPyPI publisher can now name pypitest and release-candidate.yml exactly.
    The environment configuration does not dispatch a workflow or upload a package.
  NEXT: Verify the built snapshot wheel with the actual isolated consumer probe.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-09-05T11:30:33Z
  TYPE: MEASURE
  CLAIM: The real snapshot wheel/sdist pass archive/version validation and the isolated Windows
    Python 3.14t consumer scenario. A repeated same-commit build yields identical wheel bytes but
    different sdist bytes. Tar comparison proves identical member names and contents; 171 members
    differ only in time/PAX metadata. SOURCE_DATE_EPOCH alone does not stabilize this backend's sdist.
  EVIDENCE:
  - artifacts/release_candidate_20260905/build.log
  - artifacts/release_candidate_20260905/build-retry.log
  - .github/workflows/build-distributions.yml:49-55
  IMPACT: A normal retry could conflict with immutable TestPyPI files despite unchanged source.
    Normalize only sdist archive metadata before verification/upload; preserve every member's bytes.
  NEXT: Add/test deterministic sdist normalization and compare both real archives after normalization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T11:41:57Z
  TYPE: MEASURE
  CLAIM: Final verification passes 263 focused tests, all eight workflow definitions in actionlint,
    correctness Ruff, and repository tests/other asset checks. The real installed Windows wheel
    passes metadata, packaged documents/graph, and public runtime/cleanup checks. Both normalized
    real source archives have identical hashes with unchanged member payloads. Final GitHub GETs
    verify pypitest permits exactly release_candidate. No actual TestPyPI upload was dispatched.
  EVIDENCE:
  - artifacts/release_candidate_20260905/focused.xml
  - artifacts/release_candidate_20260905/validation.md:8-20
  - https://api.github.com/repos/Synaptic724/melder/environments/pypitest/deployment-branch-policies
  IMPACT: Code and environment setup are concrete and reviewable. The owner's pending/trusted
    publisher on TestPyPI must match the named workflow/environment; OIDC needs no stored secret.
    Existing production authentication still references PYPI_API_TOKEN.
  NEXT: Owner includes these local changes in the next commit and promotes when runtime work/assets are ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-09-05T13:35:25Z
  TYPE: FACT
  CLAIM: The reported prerelease-rejection test replaces assignment(), but Python first evaluates
    Path('src/melder/__version__.py').read_text(...) before calling that replacement. The test therefore
    still reads a real relative source file. Earlier checks from repository root concealed that
    dependency. Reproduce from tests/, then isolate the test's version input without weakening the gate.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_publication.py:91-114
  - .github/scripts/check_candidate_run.py:98-111
  IMPACT: This is a test-isolation defect in the added regression, not TestPyPI/OIDC authentication.
  NEXT: Reproduce the two parameter cases from tests/ before changing their setup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T13:35:25Z
  TYPE: FACT
  CLAIM: Consumed codex_1's 11:49 notice that replay work would move source/tests and refresh assets.
    That notice is historical: the current board now routes that feature to end-to-end review and
    records its owner-facing validation outcome. Preserve all unrelated work while fixing this test.
  EVIDENCE:
  - tickets/tasks/2026-09-04_ordered_disposal_crystal_replay_task.md
  - tickets/tasks/2026-09-04_ordered_disposal_end_to_end_validation_task.md
  IMPACT: Scope this repair to workflow tests and their generated test corpus.
  NEXT: Reproduce the owner-reported working-directory failure.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-05T13:35:25Z
  TYPE: MEASURE
  CLAIM: Running the original parameterized test from tests/ reproduces the exact reported result:
    the tree-mismatch case passes and the prerelease case raises FileNotFoundError before its parser
    mock can run (1 failed, 1 passed). No production script or release behavior needs changing.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_publication.py:91-114
  - .github/scripts/check_candidate_run.py:98-111
  IMPACT: Replace the parser-only mock with a real minimal version-file fixture in a temporary
    checkout and explicitly enter that directory. Retain the Git/network boundary mocks and assertions.
  NEXT: Apply that isolated test setup and verify the focused suite from both launch directories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T13:41:13Z
  TYPE: MEASURE
  CLAIM: The repaired test creates its own temporary src/melder/__version__.py and changes into
    that fixture directory, exercising the real parser while mocking only Git/network boundaries.
    All 263 focused tests pass from repository root and from tests/. Scoped Ruff and generated test
    corpus checks pass. Read-only source-asset checks now report all three assets current.
  EVIDENCE:
  - tests/unit/github_workflows/test_candidate_publication.py:91-124
  - artifacts/release_candidate_20260905/cwd-root.xml
  - artifacts/release_candidate_20260905/cwd-tests.xml
  IMPACT: The test no longer depends on the IDE's launch directory. The production scripts/workflows
    are unchanged; the small test repair and its derived test corpus are ready for owner commit.
  NEXT: Owner reruns the original IDE test and includes this repair in the next commit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The accepted slim implementation is complete locally and in review on codex_features2. Candidate
pushes call release-candidate.yml: authorize -> package build -> OIDC TestPyPI upload -> two-platform
isolated consumer checks -> fail-closed package-ready. Full source tests remain in normal CI/final
publication. Exact-source candidate proof gates prod PRs and both production publication boundaries.

GitHub pypitest exists with only release_candidate allowed (deployment policy 59177914). TestPyPI
publisher values: project melder, owner Synaptic724, repository melder, release-candidate.yml, pypitest.
No environment variables/API-token secrets are needed for that OIDC publisher, including its first upload.
The existing production publisher still references PYPI_API_TOKEN; its auth was not migrated here.

Version remains explicitly committed in src/melder/__version__.py; stable and rcN versions are supported.
Finalize an RC via reviewed release-fix/* changes and requalify its final version before prod. Source
archive metadata is normalized so same-source timestamps do not break immutable-upload retries.
The owner has committed the original workflow implementation. The latest working-directory repair
changes only the candidate unit test and its generated test corpus/manifest; it remains local.

263 focused tests, eight-workflow actionlint, scoped Ruff, real Windows installed-wheel verification,
real archive identity checks, and tests/other generated-asset checks pass. Actual TestPyPI/OIDC and
hosted Linux/Windows runs were not dispatched here. The 13:41 repair passes all 263 focused tests from
both repository root and tests/. Shared source manifests now verify current after the other lane's
work. Preserve that lane and all unrelated edits.

Owner handles all commits/pushes. Include the local test-isolation repair in the next commit.
No upload happens from codex_features2. Promote via dev -> preprod -> release_candidate,
then verify the new candidate workflow. Apply the candidate ruleset payload after its CI rollout;
the JSON file alone does not activate protection. Dates/scheduling remain future work.
