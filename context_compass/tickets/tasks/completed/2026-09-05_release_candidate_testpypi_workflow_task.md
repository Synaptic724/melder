# Task: Qualify a frozen release candidate through TestPyPI before production

## Metadata
- Task ID: TASK-2026-09-05-release-candidate-testpypi-workflow
- Story: none (successor to accepted branch CI foundation)
- Status: done
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-05T10:25:12Z
- Updated: 2026-09-05T23:53:38Z
- Completed: 2026-09-05T23:53:38Z
- Summary: Delivered TestPyPI candidate qualification, three-platform checks, exact-source production
  safeguards and final-stage CI candidate proof. Owner accepted closure; validation and rollout limits
  are retained below. Current implementation and generated assets are committed locally.

## Objective
Extend the promotion route to dev -> preprod -> release_candidate -> prod. Keep preprod as full
continuous validation. The selected candidate is tested through TestPyPI and identified by exact
commit, version, workflow run, and distribution hashes before final production publication.

## Ticket Contract
- ENTRY_GATE: Existing certification, this active route, and consumed patch contracts before edits.
- EXECUTION_BOUNDARY: .github workflows/scripts/ruleset payloads/branch guide; focused workflow and consumer tests;
  the reported aetheric-mediator concurrency component test and UnitOfWork lock test; generated llm_support assets;
  this ticket and its associated coordination/artifact rows.
- DEPENDENCIES: tickets/tasks/completed/2026-09-04_implement_branch_ci_release_validation_task.md.
  Qualification now consumes the owner-selected single-test skip disposition in
  tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md. Runtime repair is deferred; the
  previous requirement to complete its epic before release is superseded by that owner decision.
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
- from_state: review
- to_state: done
- transition_reason: Owner explicitly accepted the delivered work and requested ticket turn-in.
  Validation is recorded, patch contracts are archived and task-owned scratch has been removed.

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
- Final correction: 237 workflow tests pass; actionlint, scoped Ruff, regenerated tests/other
  corpus proofs and whitespace checks pass. The new placement regression failed before the change.
- Hosted RC run 33997179636 completed successfully for candidate 361a974973316c0ab6e9ed24b0c33b22b29ab4b6,
  including the publication job and all three installed-package probes.
- At final closure verification, local HEAD 298b8dfc1 contains the implementation and generated
  assets with no uncommitted diff. No additional hosted run of the last relocation or final PyPI
  publication was checked during ticket closure.
- Earlier validation tranches follow as historical evidence.
- 2026-09-05T18:37:46Z UnitOfWork repair: all 279 synchronization unit tests pass with PYTHON_GIL=0.
  The worker holds for 1 second, startup waits up to 5 seconds with an asserted result, and the
  existing test structure remains. Scoped Ruff, whitespace, and regenerated test-corpus proofs pass.
- 2026-09-05T18:11:50Z concurrency repair: 270 mediator unit/component cases plus two adversarial
  controls pass on Python 3.14t with PYTHON_GIL=0. Added startup delay passes; forced serialization
  is rejected with clean final bookkeeping. Scoped Ruff, whitespace, and regenerated test-corpus
  proofs pass. Full repository and hosted macOS runs were not executed for this test-only repair.
- 2026-09-05T17:31:43Z macOS setup repair: the three setup-inheritance regressions fail on the old
  job-wide settings; all 269 focused tests pass after scoping the environment to qualification steps.
  All eight workflows pass actionlint; scoped Ruff, whitespace, and regenerated tests/other proofs pass.
  Actual macOS installer execution was not performed locally; a new hosted run must verify the repair.
- 2026-09-05T17:02:19Z token repair: 266 focused workflow/package/builder tests pass on Python 3.14t.
  All eight workflows pass actionlint; scoped Ruff, whitespace, and tests/other corpus checks pass.
  GitHub secret-name metadata verifies MELDER_API_TOKEN inside pypitest; the value was not accessed.
  Candidate upload remains on RC pushes; prod only verifies earlier exact-source qualification.
- 2026-09-05T16:14:46Z Mac extension: all 14 workflow contract tests pass; eight-workflow actionlint,
  scoped Ruff, whitespace, and regenerated tests/other corpus checks pass. No macOS runtime was
  executed locally. Official setup-python artifacts include native macOS arm64 Python 3.14t.
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
- Initial RC run 33977732545 failed OIDC publishing before consumer tests; the later successful
  candidate run is recorded above. No hosted run or upload was dispatched by this agent.
- GitHub environment pypitest and its sole release_candidate branch policy are GET-verified.

## Risks / Rollback Notes
- GitHub environment/secret-name setup is verified. The token's TestPyPI issuer and project scope
  are not observable from secret metadata; the first new RC upload must prove authentication.
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
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/architecture_patch.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/component_patch_candidate.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/component_patch_publication.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/architecture_patch_index.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/component_patch_candidate_index.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/component_patch_publication_index.md
  - system_docs/patches/completed/release_candidate_testpypi_2026_09_05/code_description_patch_identity_index.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Owner-accepted closure; durable behavior is in .github/BRANCH_WORKFLOW.md.
  All eight original patch records/indexes were archived unchanged under patches/completed.
- CLEARED_SCRATCH: artifacts/release_candidate_20260905/ was deleted under its delete_on_close policy.
  Its reports, tools, package snapshot and temporary environments are historical references in Notes;
  results are preserved here. Shared-context evidence remains owned by codex_1's separate epic.

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

- DATETIME: 2026-09-05T15:58:59Z
  TYPE: DECISION
  CLAIM: Owner requested macOS coverage. Ubuntu is the Linux runner and does not test macOS.
    Add macos-latest to test-runtime.yml and release-candidate.yml's install matrix, retaining
    Python 3.14t/GIL-off and the existing fail-closed aggregation. GitHub currently maps macos-latest
    to native Apple Silicon arm64. Build/upload jobs stay on their existing Linux runner.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:12-44
  - .github/workflows/release-candidate.yml:76-106
  - .github/scripts/testpypi_candidate.py:166-187
  - https://docs.github.com/en/actions/reference/runners/github-hosted-runners
  IMPACT: The shared runtime caller automatically adds Mac checks to normal CI and final releases;
    TestPyPI installation gains a separate native Mac result without another full source-suite run.
  NEXT: Update/read the platform patch delta, then edit both matrices, their contracts, and the guide.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T15:58:59Z
  TYPE: FACT
  CLAIM: GitHub's official Python distribution manifest lists stable 3.14.7 darwin-arm64-freethreaded
    and darwin-x64-freethreaded artifacts. setup-python documents 3.14t selection and native default
    architecture. Existing installed-wheel code already uses bin/python on non-Windows platforms.
    The revised platform patch was read: two matrix arrays map to existing parsed matrix assertions,
    while unchanged aggregate gates require every matrix member to succeed.
  EVIDENCE:
  - https://github.com/actions/python-versions/blob/main/versions-manifest.json
  - https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md
  - .github/scripts/testpypi_candidate.py:166-187
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate.md:1-19
  IMPACT: Add native macOS without interpreter fallback or a publishing-job change. Runtime
    compatibility remains a hosted-run result; this Windows session only validates configuration.
  NEXT: Apply the two matrix entries, update their existing assertions, and refresh the guide/assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T15:58:59Z
  TYPE: FACT
  CLAIM: Both runtime and installed-candidate matrices now include macos-latest. Existing parsed
    workflow contracts require the three labels, and the guide identifies native Apple Silicon.
    Shared runtime callers carry the new platform into regular CI and fresh final release checks.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:12-20
  - .github/workflows/release-candidate.yml:76-89
  - tests/unit/github_workflows/test_workflow_contracts.py:57-69
  IMPACT: A macOS failure is required evidence and cannot be silently skipped by the aggregate gate.
  NEXT: Run the existing workflow contracts/actionlint and regenerate affected document indexes/bundles.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T16:14:46Z
  TYPE: MEASURE
  CLAIM: macos-latest now participates in the shared runtime matrix and candidate install matrix.
    All 14 existing workflow contract tests pass, all eight workflows pass actionlint, scoped Ruff
    and whitespace checks pass, and regenerated tests/other bundles verify. The platform patch
    indexes were regenerated. No hosted Mac run, commit, push, or upload occurred in this extension.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:12-20
  - .github/workflows/release-candidate.yml:76-89
  - tests/unit/github_workflows/test_workflow_contracts.py:57-69
  - https://docs.github.com/en/actions/reference/runners/github-hosted-runners
  IMPACT: CI/final-release runtime checks and TestPyPI consumer checks now explicitly cover Linux,
    Windows, and native Apple Silicon macOS. Actual Mac compatibility awaits the first hosted run.
  NEXT: Owner commits/pushes the matrix extension and inspects the macOS jobs in GitHub Actions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T16:26:07Z
  TYPE: FACT
  CLAIM: Owner's hosted traceback reaches require_qualified_run and rejects its combined
    source/path/branch/status/conclusion check. Earlier source-tree and final-version checks passed.
    The message does not identify which expected field differed; current remote run evidence is needed.
  EVIDENCE:
  - .github/scripts/check_candidate_run.py:54-80
  - Owner-provided RC-to-prod CI traceback on 2026-09-05.
  IMPACT: Investigate candidate qualification first; do not remove the safety gate or infer success.
  NEXT: Read the prod PR head and its matching RC workflow run/jobs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T16:32:06Z
  TYPE: FACT
  CLAIM: Open prod PR 130 targets release_candidate commit 0c9fbe20eccc9a387cb655b753bbe0e37d2f457c.
    Candidate run 33977732545 is for that exact SHA and correct workflow/branch, but concluded failure.
    Authorization and real distribution build/install passed; TestPyPI publishing failed, installed-
    candidate jobs were skipped, and package-ready failed. The prod gate is rejecting failed qualification.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/pull/130
  - https://github.com/Synaptic724/melder/actions/runs/33977732545
  - https://github.com/Synaptic724/melder/actions/runs/33977732545/job/101337402442
  IMPACT: Fix the upstream upload failure before retrying prod CI. Do not bypass the candidate guard.
  NEXT: Inspect the failed publishing step's exact error and identify the required correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T16:32:06Z
  TYPE: FACT
  CLAIM: The RC publisher's actual failure is TestPyPI OIDC invalid-publisher: a valid GitHub token
    had no matching publisher. Its claims match our intended repository/workflow/environment:
    Synaptic724/melder, release-candidate.yml at refs/heads/release_candidate, environment pypitest.
    The TestPyPI-side saved publisher is missing/mismatched; which field differs is not visible here.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33977732545/job/101337402442
  - .github/workflows/release-candidate.yml:35-64
  IMPACT: The owner must correct the TestPyPI pending/trusted publisher and rerun RC qualification
    before retrying prod CI. No token secret or weaker release gate is the solution. The generic
    gate diagnostic should name its run and differing fields instead of hiding the upstream state.
  NEXT: Improve and test the gate diagnostic without changing qualification requirements.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T16:43:20Z
  TYPE: DECISION
  CLAIM: Owner chose API-token authentication and named the GitHub secret melder_api_token.
    Switch the TestPyPI publisher from OIDC to that environment secret in pypitest; it must be a
    TestPyPI token stored in Secrets, not a variable. Disable OIDC-only attestations and remove
    id-token permission. Add a missing-secret check so empty configuration cannot fall back to OIDC.
  EVIDENCE:
  - Owner token-authentication/name instructions on 2026-09-05, recorded here.
  - .github/workflows/release-candidate.yml:35-65
  - https://github.com/pypa/gh-action-pypi-publish
  IMPACT: This supersedes the prior OIDC setup decision. Preserve candidate validation, exact-source
    prod gates, macOS changes, and production's existing independent credential. No secret value is
    requested in chat, written to the repository, or read from the environment by the agent.
  NEXT: Update/read the authentication patch delta, then wire the secret and verify its workflow contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T16:56:08Z
  TYPE: FACT
  CLAIM: Re-entry confirms publication already triggers on pushes to release_candidate, including
    the merge from preprod. The prod CI job only checks exact-source candidate evidence; it does
    not upload. Owner reconfirmed pypitest and requested this same preprod-to-RC stage placement.
    Local publisher wiring now references secrets.melder_api_token with a missing-secret preflight,
    no id-token permission, and attestations disabled. The token change still needs local validation.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:1-83
  - .github/workflows/ci.yml:21-46
  - .github/scripts/check_candidate_run.py:99-123
  IMPACT: Keep the existing trigger boundary; clarify post-merge RC publication in the guide.
    Certification and owner authorization remain in force. No addressed mailbox message was pending.
  NEXT: Verify the authentication patch/tests and pypitest secret-name metadata, then validate locally.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T16:59:00Z
  TYPE: FACT
  CLAIM: Read-only GitHub secret-name metadata confirms MELDER_API_TOKEN exists in environment
    pypitest. Its value was not accessed. Candidate upload credentials use the secrets context,
    with explicit token mode and disabled OIDC-only attestations per the publishing action contract.
    Existing parsed workflow tests already require RC push-only/manual triggers, isolated publishing,
    all three install platforms, and prod's evidence-only check; no trigger relocation is needed.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder/environments/pypitest/secrets
  - .github/workflows/release-candidate.yml:35-83
  - tests/unit/github_workflows/test_workflow_contracts.py:144-215
  - https://github.com/pypa/gh-action-pypi-publish#advanced-release-management
  IMPACT: GitHub-side credential placement is verified; only a real hosted upload can validate the
    token's issuer/scope. Token/trigger patch contracts are consumed. Keep the exact-source prod gate.
  NEXT: Clarify post-merge RC publication in the guide, regenerate derived assets, and run focused checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:00:13Z
  TYPE: FACT
  CLAIM: The guide now distinguishes pre-merge source CI, post-merge RC upload/install checks, and
    the later prod evidence check. Token wiring and diagnostic tests were read completely before
    validation. Indexed test-map bootstrap/unit sections confirm the suite remains repository-based;
    no installed-package test rewrite or runtime source change is needed for this credential repair.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:68-103
  - tests/unit/github_workflows/test_workflow_contracts.py:144-215
  - tests/unit/github_workflows/test_candidate_publication.py:53-96
  - system_docs/tests_architecture.md:157-255
  - system_docs/tests_components.md:171-213
  IMPACT: Local changes are ready for focused qualification; source maps exclude workflow helpers,
    whose scoped contracts remain in the candidate patch and operator guide.
  NEXT: Regenerate changed patch indexes and tests/other corpora, then run the focused test/lint checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T17:02:19Z
  TYPE: MEASURE
  CLAIM: All 266 focused workflow, package-metadata, and LLM-builder tests pass on local Python 3.14t.
    All eight workflow files pass actionlint 1.7.12 with optional shellcheck/pyflakes disabled; scoped
    correctness Ruff and git diff whitespace checks pass. Regenerated tests/other corpora match
    their input/output proofs. The original exact-source prod safety gate remains intact.
  EVIDENCE:
  - artifacts/release_candidate_20260905/token-auth.xml
  - artifacts/release_candidate_20260905/validation.md
  - .github/workflows/release-candidate.yml:1-83
  - .github/scripts/check_candidate_run.py:54-124
  IMPACT: Token authentication, clearer upstream diagnostics, macOS matrices, and the guide are ready
    for owner commit. A successful hosted upload/install chain is still required before prod promotion.
  NEXT: Owner commits/promotes the updated files to release_candidate and checks RC / package-ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:24:07Z
  TYPE: HYPOTHESIS
  CLAIM: The owner-provided macOS log selected the expected darwin-arm64-freethreaded archive and
    installed it successfully, then failed at Install OpenSSL certificates with config_read_gil.
    Job-wide PYTHON_GIL=0 may be reaching a standard Python helper during setup. Runtime tests must
    still run free-threaded; inspect the upstream installer and both matrix workflows before editing.
  EVIDENCE:
  - Owner macOS setup-python v7 failure log on 2026-09-05, recorded here.
  - https://github.com/actions/python-versions/blob/main/installers/macos-pkg-setup-template.sh
  IMPACT: This is a setup boundary failure before Melder tests or TestPyPI consumer code executes.
  NEXT: Read the installer certificate invocation and all workflow PYTHON_GIL scopes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:24:07Z
  TYPE: FACT
  CLAIM: The upstream macOS installer invokes Install Certificates.command after installing the
    free-threaded interpreter. CPython's certificate script explicitly launches Python.framework's
    standard python3.14, so inherited PYTHON_GIL=0 causes the reported startup refusal. Both local
    runtime and candidate-install jobs currently set that variable job-wide; the Linux package-build
    job has the same scope. The runtime driver already checks the actual pytest process's GIL state.
  EVIDENCE:
  - https://github.com/actions/python-versions/blob/main/installers/macos-pkg-setup-template.sh
  - https://github.com/python/cpython/blob/3.14/Mac/BuildScript/resources/install_certificates.command
  - .github/workflows/test-runtime.yml:10-35
  - .github/workflows/release-candidate.yml:85-108
  - .github/scripts/run_runtime_tests.py:20-39
  IMPACT: The selected 3.14t interpreter is correct. Scope PYTHON_GIL=0 to actual qualification steps;
    do not downgrade Python, enable the GIL for tests, or disable certificate installation.
  NEXT: Read the package-build and smoke-probe boundary, then update the three workflow scopes and contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:24:07Z
  TYPE: DECISION
  CLAIM: Keep Python 3.14t and all three supported OSes. Move PYTHON_GIL=0 from job scope to the
    runtime test driver, RC probe-install step, and distribution installed-wheel probe step. Leave
    setup/dependency installation unforced. Update existing consumer assertions and add one parsed
    setup-environment regression per workflow; prove those fail on the existing three job-wide settings.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:10-35
  - .github/workflows/release-candidate.yml:85-108
  - .github/workflows/build-distributions.yml:26-60
  - .github/scripts/smoke_wheel.py:39-80
  IMPACT: Scope is the three workflows, test_workflow_contracts.py, branch guide, patch contracts,
    and their derived assets. Mapping: setup/runtime boundary -> job/step env changes -> parsed
    setup-inheritance and consumer-posture tests plus existing runtime guard tests and actionlint.
  NEXT: Read the patch delta and add/run the three setup-environment regressions before changing YAML.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:24:07Z
  TYPE: MEASURE
  CLAIM: The three new parsed setup-environment regression cases all fail on the original YAML:
    setup-python inherits PYTHON_GIL=0 in runtime, RC install, and distribution build. This reproduces
    the configuration defect without claiming that the macOS installer ran on this Windows host.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:58-73
  IMPACT: The regressions distinguish setup from runtime posture and fail before the fix.
  NEXT: Move the three env mappings to their qualification steps and update runtime-step assertions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T17:29:45Z
  TYPE: FACT
  CLAIM: All three workflow job-wide PYTHON_GIL settings are now scoped to their runtime-test or
    installed-wheel probe steps. The guide and patch contract explain the standard-Python macOS
    bootstrap boundary. Existing runtime/probe checks still validate actual GIL state and all three
    OSes remain required. No publisher, interpreter version, branch route, or source helper changed.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:10-35
  - .github/workflows/release-candidate.yml:85-108
  - .github/workflows/build-distributions.yml:26-64
  - .github/BRANCH_WORKFLOW.md:32-35
  IMPACT: Runtime policy now starts after interpreter setup. The setup regressions and runtime-step
    assertions together prove the intended boundary without dropping free-threaded qualification.
  NEXT: Regenerate patch indexes and tests/other assets, then run focused regressions and workflow lint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:31:43Z
  TYPE: MEASURE
  CLAIM: After the GIL environment scope repair, all 269 focused workflow/package/builder tests pass.
    Three new setup-inheritance regressions previously failed on the old YAML. All eight workflows
    pass actionlint 1.7.12 (optional shellcheck/pyflakes disabled); scoped correctness Ruff, whitespace,
    regenerated tests/other corpus proofs, and patch-index generation also pass. No runtime helper,
    interpreter selection, platform matrix, upload credential, or release gate changed.
  EVIDENCE:
  - artifacts/release_candidate_20260905/macos-setup.xml
  - artifacts/release_candidate_20260905/validation.md
  - tests/unit/github_workflows/test_workflow_contracts.py:58-87
  - .github/workflows/test-runtime.yml:10-36
  - .github/workflows/release-candidate.yml:85-108
  - .github/workflows/build-distributions.yml:26-62
  IMPACT: Ready for owner commit on codex_features2. This Windows check proves configuration and
    regression behavior; it does not claim that the macOS installer or the hosted matrix ran here.
  NEXT: Owner commits/pushes the repair and lets a new run execute the updated workflow on macOS.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:50:59Z
  TYPE: FACT
  CLAIM: Owner's new failure is in macos-latest job 101347496028 of run 33981528038, verified from
    GitHub metadata. The disjoint-frame test compares elapsed time to 8 * 3 * 0.003 * 0.5 = 0.036s.
    Its _run clock starts before starting eight threads and includes their startup/barrier/join work.
    Requested sleep time is therefore treated as if it were the whole transaction/scheduler cost.
    The reported 0.054374709s exceeds that threshold but does not itself prove claim serialization.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33981528038/job/101347496028
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:93-128
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:209-248
  - https://docs.python.org/3/library/time.html#time.sleep
  IMPACT: Treat this as a timing-sensitive test diagnosis, not evidence that macOS or the mediator
    cannot run concurrently. Owner asks why it appears in CI; production changes are not authorized
    by this single duration. No runtime or test implementation has changed during this diagnosis.
  NEXT: Confirm the formation-load claim contract and explain a direct overlap assertion as the repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T17:56:00Z
  TYPE: FACT
  CLAIM: The formation strategy supplies world INTENT plus an exclusive target-frame key, and
    ClaimCompatibility explicitly permits INTENT with INTENT. The reported test verifies none of
    the active-session overlap directly; its 0.5 multiplier imposes an uncalibrated 36ms deadline.
    Python documents that sleep can exceed the requested duration because of scheduling. The owner
    challenges this arbitrary cutoff; agree that it is unsuitable as the concurrency correctness gate.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/strategies/formation_load_transaction_strategy.py:104-145
  - src/melder/aether/aetheric_mediator/claim_mode.py:119-154
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:99-130
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:209-248
  - https://docs.python.org/3/library/time.html#time.sleep
  IMPACT: Recommend a post-admission barrier/event test proving all disjoint sessions coexist before
    any releases, with a generous hang timeout and explicit worker outcomes. Exact hosted scheduler
    delay was not profiled; the duration alone cannot establish a production lock defect. This turn
    is diagnosis only: no test or runtime implementation changed, and no tests were executed.
  NEXT: Replace the timing assertion with direct overlap proof when continuing the test repair.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:00:22Z
  TYPE: DECISION
  CLAIM: Owner asked whether the diagnosed test was fixed; it was not. Proceed with the previously
    explained test-only correction: post-admission rendezvous for eight distinct frame transactions,
    explicit successful worker outcomes, and cleanup proof across three rounds. The existing generous
    thread timeout remains a hang guard. Do not change mediator production behavior or raise the 36ms limit.
  EVIDENCE:
  - Owner follow-up on 2026-09-05 and previous timing diagnosis, recorded here.
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:99-248
  IMPACT: Scope is the reported test, inaccurate timing-only helper documentation, generated test
    corpus, and this ticket's tracking. Test correctness changes no runtime architecture or release gate.
  NEXT: Confirm session admission/finalization contracts, then replace the timing assertion with overlap proof.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:00:22Z
  TYPE: FACT
  CLAIM: Mediator.begin returns with claims held; leave then commit releases claims/bookkeeping.
    Finalized session objects remain caller-owned and must be cleaned after commit. ClaimTable.describe
    exposes detached scope keys and holder/mode rows. A barrier action can therefore verify all eight
    world-intent holders and all eight frame keys before any worker leaves its session.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/mediator.py:447-589
  - src/melder/aether/aetheric_mediator/mediator.py:591-700
  - src/melder/aether/aetheric_mediator/mediator.py:1092-1154
  - src/melder/aether/aetheric_mediator/transaction_session.py:619-639
  - src/melder/aether/aetheric_mediator/claim_table.py:623-649
  IMPACT: Use a bounded reusable barrier across three rounds and futures that propagate worker
    exceptions. Always finalize/clean admitted sessions and caller identities; abort the barrier on
    worker failure so peers can finish. Final public snapshots must show no claims or active bookkeeping.
  NEXT: Implement that targeted test and validate it against delayed starts and forced exclusive claims.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:00:22Z
  TYPE: MEASURE
  CLAIM: The replacement disjoint-frame test passes its first focused run. Every round waits at a
    barrier while all sessions remain open; the barrier action verifies all eight frame keys and
    eight world holders. Futures propagate worker failures; session finalization/cleanup occurs in
    finally blocks, and final snapshots require no claims or active bookkeeping. Helper docs no longer
    describe elapsed time as the only concurrency evidence. Production code remains unchanged.
  EVIDENCE:
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:209-284
  IMPACT: The arbitrary elapsed-time assertion is removed without dropping the overlap requirement.
  NEXT: Run delayed-start and forced-serialization controls, then the complete focused mediator suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:11:50Z
  TYPE: MEASURE
  CLAIM: All 272 selected checks pass: 270 mediator unit/component tests plus two disposable
    controls using the actual repaired test. Eight delayed Thread.start calls add at least 80ms and
    still pass; forcing formation loads to claim world exclusively correctly fails overlap proof.
    That failure also leaves no claims, admission registrations, or reporting activity. Scoped Ruff,
    whitespace, and regenerated tests-corpus proofs pass. JUnit includes both control cases.
  EVIDENCE:
  - artifacts/release_candidate_20260905/mediator-overlap.xml
  - artifacts/release_candidate_20260905/test_mediator_overlap_controls.py:25-66
  - tests/component/melder/aether/aetheric_mediator/test_aetheric_mediator_concurrency_component.py:213-281
  IMPACT: The fixed test tolerates scheduler delay while detecting a real serialization defect.
    Runtime/CI workflow code is unchanged. Full-repository and hosted macOS validation remain unrun
    for this repair. Disposable controls/reports are delete_on_close artifacts in the task workspace.
  NEXT: Owner commits the test and regenerated test corpus, then runs the updated CI revision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:33:09Z
  TYPE: HYPOTHESIS
  CLAIM: Owner's UnitOfWork lock test waits up to 100ms for an entered event but ignores the return;
    its worker releases the context after a 50ms sleep. The nonblocking assertion can therefore run
    before acquisition or after release. Its own successful acquire explains the subsequently locked
    repr. Verify the source before concluding whether the context manager violates mutual exclusion.
  EVIDENCE:
  - Owner-provided test_thread_safety_basic_lock_usage traceback on 2026-09-05.
  IMPACT: Preserve production locking unless source and a synchronized reproduction prove a defect.
  NEXT: Read UnitOfWork and the full target test, then coordinate holder release explicitly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:33:09Z
  TYPE: DECISION
  CLAIM: Owner explicitly chose a larger millisecond window instead of the proposed event-based
    rewrite. Keep the test structure: hold the worker context for 1 second rather than 50ms, wait
    up to 5 seconds for startup, and assert the entered wait succeeded. UnitOfWork.__enter__/__exit__
    directly acquire/release its RLock; no production locking change is needed for this repair.
  EVIDENCE:
  - Owner's "just make the ms window decent" instruction on 2026-09-05.
  - src/melder/utilities/synchronization/unit_of_work.py:280-332
  - tests/unit/melder/utilities/synchronization/test_unit_of_work.py:145-169
  IMPACT: This supersedes the handshake plan. Use the owner's timing choice and keep the patch small;
    update the existing test, run focused synchronization checks, and regenerate the test corpus.
  NEXT: Apply the longer hold/startup windows and verify the synchronization tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T18:36:58Z
  TYPE: FACT
  CLAIM: The existing UnitOfWork test now holds the worker lock for 1 second and asserts a
    successful entered event within 5 seconds. Its thread structure and lock assertions are preserved.
    The test corpus is regenerated. No handshake rewrite or production code change was made.
  EVIDENCE:
  - tests/unit/melder/utilities/synchronization/test_unit_of_work.py:145-172
  IMPACT: The owner's requested timing margin is implemented and ready for focused checks.
  NEXT: Run synchronization unit tests and check the generated test corpus.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T18:37:46Z
  TYPE: MEASURE
  CLAIM: All 279 synchronization unit tests pass on local Python 3.14t with PYTHON_GIL=0 after the
    owner-directed window increase. Scoped correctness Ruff, git diff whitespace checks, and the
    regenerated tests-corpus proof pass. The patch changes only test timing, startup-wait assertion,
    and touched test docstrings/type hints; production code and thread structure are unchanged.
  EVIDENCE:
  - artifacts/release_candidate_20260905/uow-timing.xml
  - tests/unit/melder/utilities/synchronization/test_unit_of_work.py:147-173
  IMPACT: Ready for owner commit and hosted CI. Owner explicitly chose this wider timing window;
    the proposed event-handshake rewrite was not implemented. No hosted rerun or package upload occurred.
  NEXT: Owner commits the test and regenerated test corpus, then runs the updated CI revision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T19:54:37Z
  TYPE: FACT
  CLAIM: The timing margin is committed in d9f6dbc1a. New hosted qualification fails with a missing
    codegen payload during concurrent cluster melds. The dedicated shared-context task reproduced
    that error with live conduits/Spell/switch before test teardown using debugger-controlled scheduling.
    Owner expressly requires analysis/proof before code changes. Runtime and tests remain unchanged.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md
  IMPACT: Candidate qualification remains blocked by the runtime failure; no further workflow or
    timing change should conceal it. Review the separate task's protocol evidence first.
  NEXT: Review shared context reset/publication proof before selecting a runtime change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T20:23:55Z
  TYPE: DECISION
  CLAIM: Owner assigned shared-context runtime design and code fixes to codex_1 through the new
    epic. workflows_1 retains this workflow lane and candidate/prod qualification. Earlier runtime
    timing repairs are committed; no new source/test/workflow edits are part of this handoff.
  EVIDENCE:
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:17-30
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:311-316
  IMPACT: Qualification stays blocked until a corrected runtime revision passes required checks.
    The requested mailbox handoff asks codex_1 for exact tested revision, results, performance and
    generated-asset status. workflows_1 must not overlap the assigned runtime edits.
  NEXT: Consume codex_1's runtime handoff and verify its revision through the existing CI/RC gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:07:09Z
  TYPE: FACT
  CLAIM: Consumed codex_1's 21:01:42Z acknowledgement: that agent accepted runtime ownership and
    will return revision, regression/performance evidence and source-asset status. Owner asks why
    the cluster test melds while cleanup exists. Its explicit conduit cleanup is in finally after
    _run_concurrent_melds joins every worker and asserts errors. Phase 5 separately retires context
    children during live revalidation; this is not terminal teardown of those conduits.
  EVIDENCE:
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:286-352
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-1015
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:162-213
  - src/melder/aether/spellbook/spell.py:660-686
  IMPACT: Explain final test teardown separately from live context replacement. A retired child
    remains unusable; replacement must complete before a meld consumes its new inputs. No runtime
    change or new test run is made here; codex_1 continues the assigned repair.
  NEXT: Await codex_1's qualified runtime handoff before resuming candidate qualification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:45:18Z
  TYPE: FACT
  CLAIM: Consumed codex_1's 22:42:08Z notice and verified its ticket plus the actual three-line skip
    decorator. Owner rejected/deferred runtime repair and selected pytest.skip for the single original
    cluster test, whose body remains. codex_1 reports 18 passed/1 skipped locally; no hosted or asset
    qualification is claimed. Abandoned untracked repair files are not part of the approved skip.
  EVIDENCE:
  - tickets/tasks/2026-09-05_shared_context_rebuild_race_task.md:452-485
  - tests/integration/melder/conduit/test_conduit_integration_concurrency.py:940-943
  IMPACT: Replace the workflow dependency on a repaired runtime with the owner's deferral disposition.
    Preserve the investigation and do not restore or broaden the rejected repair. Candidate publication
    still requires exact-revision CI/assets and the existing package-ready proof.
  NEXT: Verify the owner's selected committed candidate and hosted checks when supplied.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T22:45:18Z
  TYPE: FACT
  CLAIM: Owner says the reported error only indicates cleanup. The original exception is specifically
    a missing-codegen RuntimeError, raised when CreationContextBuilder.build sees its required input
    is None. The guard correctly refuses that build; this does not by itself establish whether the
    concurrent caller sequence is supported or whether the test's success expectation is appropriate.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_builder.py:103-146
  - artifacts/shared_context_race_20260905/controlled-window.json:29-51
  IMPACT: Distinguish a valid fail-fast guard from a successful meld. The printed cleaned repr is
    separate from the exception text. Do not promote the deferred scenario to either repaired runtime
    or proven-valid expected failure based solely on that guard.
  NEXT: Explain the refusal and the remaining contract question without reopening implementation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T22:58:44Z
  TYPE: FACT
  CLAIM: Owner's new prod traceback identifies candidate SHA 361a974973316c0ab6e9ed24b0c33b22b29ab4b6
    and RC run 33997179636 attempt 1 with status in_progress/conclusion None. Local gate reads
    GitHub once and fails immediately unless the latest exact-SHA RC run is already successful.
    The CI and RC workflows are separately triggered, with no dependency between their runs.
  EVIDENCE:
  - .github/scripts/check_candidate_run.py:54-99
  - .github/workflows/ci.yml:6-46
  - .github/workflows/release-candidate.yml:4-16
  IMPACT: A timing race is plausible but current remote results and job timestamps are needed.
    Local codex_features2 is at bf8f05986; only ContextCompass tracking is currently modified.
    No workflow dispatch, commit, push, merge or publication is part of this review.
  NEXT: Compare exact candidate and prod run/job metadata with their branch/PR commit identities.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:00:47Z
  TYPE: FACT
  CLAIM: GitHub GET confirms RC run 33997179636 attempt 1 now completed successfully for the exact
    reported SHA 361a974973316c0ab6e9ed24b0c33b22b29ab4b6. It started at 22:53:39Z and updated
    to success at 22:56:31Z. It is the only RC workflow run for that SHA. Open prod PR 139 selects
    that same head; its recorded update is 22:53:59Z, before RC completion.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33997179636
  - https://github.com/Synaptic724/melder/pull/139
  IMPACT: The owner's green RC is real and matches candidate identity. Original prod job timing
    remains to verify; a stale earlier failure does not imply that this successful RC was rejected.
  NEXT: Read PR 139's CI run/jobs and compare its gate timestamp with RC package-ready completion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:04:28Z
  TYPE: FACT
  CLAIM: Exact step metadata establishes the race: prod PR 139's CI run 33997196896 evaluated
    candidate readiness at 22:54:16Z; RC package-ready completed at 22:56:30Z and its run became
    successful at 22:56:31Z, 135 seconds after the failed check. RC's seven jobs all succeeded,
    including TestPyPI upload and Linux/Windows/macOS installed probes. PR 138 merged preprod
    into release_candidate at 22:53:36Z; PR 139 opened at 22:53:59Z on that exact merge commit.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33997196896/job/101389684939
  - https://github.com/Synaptic724/melder/actions/runs/33997179636/job/101389932936
  - https://github.com/Synaptic724/melder/pull/138
  - https://github.com/Synaptic724/melder/pull/139
  IMPACT: No candidate-source or merge-content mismatch: RC and prod merge preview
    768fadcbd699280cd4da5b707e5463fb11ed7f62 share tree 674b114e38fe2a396b3644ce1b8f4e31a664288f.
    The earlier gate is not refreshed by separate RC completion. Prod docs/assets/hygiene/Linux/Mac
    are green; Windows was still running at the latest read, and packages were skipped behind the
    failed branch-policy job. No hosted retry is dispatched by this review.
  NEXT: Verify retry semantics and selected-commit scope, then hand off the exact failed CI run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:09:24Z
  TYPE: DECISION
  CLAIM: Owner reran the prod check and requests moving candidate qualification toward the end.
    Put the unchanged check_candidate_run.py invocation last in the existing CI / merge-ready job,
    after require_success verifies all current dependencies. Keep branch-route validation early.
    Move actions:read and sufficient checkout history to the final job; no new status name or
    dependency-set change is needed. A still-pending RC at the final check continues to refuse.
  EVIDENCE:
  - .github/workflows/ci.yml:21-97
  - .github/scripts/ci_policy.py:89-110
  - tests/unit/github_workflows/test_workflow_contracts.py:22-40
  - tests/unit/github_workflows/test_workflow_contracts.py:202-212
  IMPACT: Exact edit scope is ci.yml, the two affected parsed workflow contracts, branch guide,
    existing candidate patch docs/indexes and tests/other corpora. Final PyPI publication guards
    remain separately enforced. No polling protocol, hosted rerun, or runtime repair is added.
  NEXT: Update/read the patch ordering contract, then prove the changed workflow regression fails early.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:09:24Z
  TYPE: FACT
  CLAIM: Git show of the owner's committed bf8f05986 includes the previously abandoned
    creation_context_rebuild.py helper and test_shared_context_rebuild_publication.py regression,
    in addition to the original cluster-test skip. They are no longer untracked as the earlier
    handoff said. No behavior claim or removal is made by this workflow pass.
  EVIDENCE:
  - src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py
  - tests/component/melder/aether/conduit/test_shared_context_rebuild_publication.py
  IMPACT: The owner should know the selected source contains more than the single-test skip.
    Keep the present workflow edit scoped; do not delete committed source or overlap codex_1's lane.
  NEXT: Include the committed-file finding in the workflow handoff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T23:11:38Z
  TYPE: PLAN
  CLAIM: Read the revised architecture, publication component and identity-flow patch in order.
    Mapping: late promotion gate -> ci.yml merge-ready steps/history/permissions -> parsed ordering
    regression; fail-closed aggregate and source identity -> existing policy/candidate negative tests;
    operator behavior -> branch guide -> other-corpus regeneration. Indexed pytest bootstrap sections
    were verified/read. Owner also requests Read the Docs diagnosis; its URL/error was asked while
    this already-authorized CI correction proceeds to completion.
  EVIDENCE:
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch.md:24-30
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication.md:15-29
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md:17-22
  IMPACT: No aggregate helper or publisher change is necessary. The final status can carry the
    mandatory proof directly; no additional check name or dependency branch is introduced.
  NEXT: Prove the updated parsed workflow contract fails against the original early gate placement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:12:44Z
  TYPE: MEASURE
  CLAIM: The revised prod-proof workflow contract fails on the original YAML because branch-policy
    still invokes the candidate lookup. One targeted case ran and failed at the intended placement
    assertion; no workflow code was changed before this negative control.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:206-236
  IMPACT: The regression detects the actual early-gate configuration behind the reported race.
  NEXT: Relocate the unchanged proof step, API permission and required checkout history to merge-ready.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T23:16:25Z
  TYPE: MEASURE
  CLAIM: Candidate proof is now the final merge-ready step after required-job aggregation, with
    actions:read and fetch-depth:2 on that job. All 237 workflow-unit cases pass on local Python
    3.14t/GIL off. The updated ordering contract failed on the old early placement. Scoped Ruff
    and actionlint pass; final publication and source-provenance helper code are unchanged.
  EVIDENCE:
  - .github/workflows/ci.yml:76-103
  - tests/unit/github_workflows/test_workflow_contracts.py:206-236
  - artifacts/release_candidate_20260905/late-candidate-proof.xml
  IMPACT: The reported early race is avoided while source tests/builds run. A genuinely pending
    or failed candidate at the final check still blocks merge. No hosted run was dispatched.
  NEXT: Regenerate patch indexes and tests/other corpora, then verify the final diff.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:21:34Z
  TYPE: MEASURE
  CLAIM: Final local verification completed: 237 workflow tests, scoped Ruff, all-workflow actionlint,
    regenerated patch indexes, tests/other corpus proofs and whitespace checks pass. The final diff
    is the approved late check plus its guide/tests/derived assets and ContextCompass tracking.
  EVIDENCE:
  - .github/workflows/ci.yml:76-103
  - artifacts/release_candidate_20260905/late-candidate-proof.xml
  - artifacts/release_candidate_20260905/validation.md
  IMPACT: Ready for owner commit. RC finishing later than the final check still causes a refusal;
    no timeout-based acceptance was introduced. Continue the separate Read the Docs diagnosis.
  NEXT: Owner commits/promotes the late-check correction and verifies the resulting hosted CI.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:48:30Z
  TYPE: DECISION
  CLAIM: Owner explicitly accepted the work and requested turning in workflows_1's tickets, then
    asked for the tickets to be read. Re-read this entire 1208-line ticket, the 187-line hosted
    diagnosis and codex_1's new release-note task. The selected closure set is these two workflows_1
    tasks only; release copy and the deferred runtime investigation retain their existing owners.
  EVIDENCE:
  - Owner instructions: "turn in your tickets please we did it"; "read the tickets in context compass".
  - tickets/tasks/2026-09-05_diagnose_readthedocs_hosted_build_task.md:1-187
  - tickets/tasks/2026-09-05_draft_ordered_disposal_docs_actions_release_task.md:1-87
  - .github/BRANCH_WORKFLOW.md:6-38
  IMPACT: Preserve validation in completed tickets, archive the eight patch records/indexes under
    patches/completed, and delete only this task's disposable release_candidate_20260905 workspace.
    Keep shared-context proof under codex_1's epic. Source/test/workflow/assets remain uncommitted
    for the owner's signing workflow; closure does not claim that final local changes were deployed.
  NEXT: Perform the contained file moves/cleanup, then synchronize boards and dependent ticket links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:53:38Z
  TYPE: FACT
  CLAIM: Owner-approved turn-in completed for the candidate workflow and hosted RTD diagnosis.
    Both task files moved to tasks/completed. All eight candidate patch records/indexes moved to
    patches/completed with unchanged SHA256 hashes. The workflow scratch directory was removed
    after containment and zero-reparse-point checks. Eight implementation/derived files retained
    their pre-cleanup hashes; no source, workflow, test or generated-asset changes were lost.
  EVIDENCE:
  - .github/workflows/ci.yml:76-103
  - .github/BRANCH_WORKFLOW.md:6-38
  - tickets/tasks/completed/2026-09-05_diagnose_readthedocs_hosted_build_task.md
  IMPACT: Completed tickets retain the validation record. Source commits/signing remain the owner's
    responsibility. The deferred runtime investigation and its retained proof are outside this closure.
  NEXT: No remaining execution in this ticket; owner retains normal commit/promotion control.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:58:10Z
  TYPE: MEASURE
  CLAIM: Closure verification passes: all nine remaining active routes resolve, closed anchors stay
    capped at twelve, no workflows_1 lane or closed-workflow artifact remains active, and codex_1's
    shared-context proof remains present. Release-draft and runtime-epic links now target the
    completed workflow/diagnosis files. Whitespace checks pass. Owner advanced local HEAD to
    298b8dfc1; .github, the workflow-contract tests and generated LLM assets have no uncommitted diff.
  EVIDENCE:
  - attention_board.md
  - artifact_board.md
  - tickets/tasks/2026-09-05_draft_ordered_disposal_docs_actions_release_task.md:73-77
  - tickets/epics/2026-09-05_shared_context_rebuild_publication_epic.md:257-262
  IMPACT: The two accepted tickets are fully turned in, with implementation preserved and shared
    evidence outside this closure untouched. workflows_1 is marked departed in the mailbox.
  NEXT: None for this closed lane.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Closed at the owner's explicit request after local delivery and validation. The final candidate proof
runs after the other required CI checks; 237 focused tests and all stated local checks pass. Hosted
RC qualification was independently verified. Current local HEAD 298b8dfc1 includes the implementation
and generated assets with no uncommitted diff in those files. Patch records are archived; scratch is cleared.
The runtime deferral remains with codex_1. No new publication or hosted execution is claimed.

### Historical handoff record
Late-check correction is complete locally and in review: 237 workflow tests, actionlint, Ruff,
generated tests/other proofs and whitespace checks pass. Candidate proof runs last in merge-ready,
after all required checks. Owner commits/pushes; no hosted retry or publication was dispatched here.
The pending owner request is now routed separately to the hosted Read the Docs diagnosis task.

Owner now requests the candidate proof at the end of CI. Move its unchanged invocation to the
last step of CI / merge-ready, after dependency aggregation, with actions:read and fetch-depth:2.
Keep branch policy early and final publication guards intact. Validate parsed workflow order and
the existing negative provenance tests, then regenerate tests/other corpora and patch indexes.

Current work is reviewing owner-reported prod failure against RC run 33997179636 and candidate
361a974973316c0ab6e9ed24b0c33b22b29ab4b6. The logged state was in_progress; verify current status,
timestamps and PR/merge identity before diagnosing the disagreement with the owner's green RC.

Latest disposition: owner deferred/rejected runtime repair and selected pytest.skip for only the
original two-cluster integration test. codex_1's 22:42:08Z mailbox notice is consumed; that agent
reports 18 passed/1 skipped for the module, with the original test body retained. No new runtime
repair, asset qualification or hosted release qualification is established by that result.

workflows_1 retains workflows and release qualification under this explicit deferral. Verify the
owner's selected committed revision, its generated assets and required CI/RC package-ready checks.
Do not treat abandoned untracked repair files as approved candidate contents or restore the rejected
implementation. The shared-context investigation remains open as deferred evidence.

The following paragraphs preserve earlier local validation and rollout history. Their historical
"ready for owner commit" statements are superseded by the committed status recorded above.

Latest local repair is the owner-requested small UnitOfWork test change: worker hold 50ms -> 1 second,
startup wait 100ms -> 5 seconds, and an assertion that startup signaled. Existing thread/test structure
is preserved; no event-handshake rewrite or production code change. All 279 synchronization unit tests
pass with PYTHON_GIL=0, plus scoped Ruff, whitespace, and regenerated tests-corpus proofs. Ready for
owner commit and hosted CI. The prior mediator overlap repair was already committed at this intake.

The disjoint-frame timing failure is now fixed locally on codex_features2. The test requires eight
concurrently held frame claims and eight world holders at a barrier in each of three rounds, with
future results carrying worker failures and deterministic session/identity cleanup. The arbitrary
36ms upper bound is gone; the existing generous timeout serves only as a stuck-rendezvous guard.
270 mediator unit/component cases plus two adversarial controls pass with PYTHON_GIL=0. Added startup
delay succeeds; forced world-exclusive serialization fails the test as required and leaves no live
bookkeeping. Scoped Ruff, whitespace, and regenerated test-corpus checks pass. No runtime/workflow code,
commit, push, or package upload was performed. The owner commits the changed test and derived assets.
The first hosted macOS run of this replacement and the full repository suite remain unexecuted locally.
The prior GIL-scope repair is committed in 335981247.

Latest repair: job-wide PYTHON_GIL=0 reached the standard Python used by macOS's certificate helper
during setup-python. Runtime tests, RC installation, and distribution builds now scope that variable
to their test/probe steps only. Python 3.14t, all three OSes, and actual-process GIL checks remain.
The three setup-environment regressions failed before the fix; 269 focused tests now pass, together
with actionlint, scoped Ruff, whitespace, regenerated corpus proofs, and updated patch indexes.
A fresh hosted run after owner commit/push must verify macOS installation; it was not executed here.

Local changes are verified and ready for owner commit on codex_features2. The owner selected explicit
TestPyPI API-token authentication using melder_api_token in the pypitest environment. GitHub metadata
confirms MELDER_API_TOKEN exists there; its value was never accessed. Only the upload job references
it. No id-token permission or OIDC attestations remain. Production keeps its separate PYPI_API_TOKEN.

The upload was already at the requested stage: a preprod -> release_candidate PR runs required source
CI; merging starts the RC build -> TestPyPI upload -> Linux/Windows/macOS installed-package probes.
RC -> prod only checks the earlier successful exact-source RC run alongside its required CI.
Fresh final production validation and its live tag/prod check remain required before the PyPI upload.

The owner's failed RC run 33977732545 (PR 130 source 0c9fbe20eccc9a387cb655b753bbe0e37d2f457c) failed
with OIDC invalid-publisher. The diagnostic now identifies the inspected run, attempt, and differing
fields. An old run uses old workflow YAML: adding a secret or rerunning that old OIDC run alone does
not deploy this fix. Commit/promote the new YAML through dev -> preprod -> release_candidate, wait for
RC / package-ready, then rerun an already-failed prod PR check. The agent does not commit, push, or upload.

Token-repair evidence: 266 focused tests passed; all eight workflows passed actionlint; scoped Ruff,
whitespace, and regenerated tests/other corpus proofs passed. The working-directory test repair and real
Windows wheel/archive checks are recorded above. No new hosted upload/install or Mac run was dispatched.
Token validity/scope awaits that new hosted run; secret metadata proves placement only.

Version stays explicitly committed in src/melder/__version__.py. Stable and rcN versions are supported;
rcN must be finalized and requalified before prod. Existing package bytes cannot be replaced under the
same TestPyPI filename. Candidate fixes remain reviewed release-fix/* changes and return to dev.
Token wiring and the original macOS matrix were committed in 1fc53c523. The local environment-scope
repair, its tests/guide, and derived assets belong in the owner's next commit.
Apply candidate branch rules after CI rollout; checked-in JSON alone does not activate protection.
Dates/scheduling remain future work. Preserve all unrelated lanes; this task is blocked on runtime qualification.
