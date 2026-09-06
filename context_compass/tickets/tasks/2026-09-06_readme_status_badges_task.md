# Task: Add useful and evidence-backed README badges

## Metadata
- Task ID: TASK-2026-09-06-readme-status-badges
- Story: none (owner-requested README refinement)
- Status: review
- Owner: codex
- Agent Name: codex_1
- Priority: p2
- Created: 2026-09-06T14:28:14Z
- Updated: 2026-09-06T14:55:32Z

## Objective
Add useful README badges and establish an honest source for the requested coverage badge.

## Ticket Contract
- ENTRY_GATE: Owner requested coverage and other appropriate README badges.
- EXECUTION_BOUNDARY: README badges, runtime-test reporting helper/workflow and its CI/publish callers,
  Codecov configuration, focused workflow tests, branch guide, derived corpora and coordination.
- DEPENDENCIES: Existing public workflows; workflows_1's CI lane must remain undisturbed.
- EXIT_GATE: Added badges resolve to real evidence; no invented coverage percentage; corpus is current.
- FAILURE_ESCALATION: Ask before adding third-party reporting, permissions, secrets, or CI behavior.

## Scope Boundaries
- In scope: CI status, package badges, existing-run coverage XML and nonblocking CODECOV_TOKEN upload.
- Out of scope: service enrollment on the owner's behalf, publication, commits, pushes, runtime changes,
  new test-run triggers, minimum-coverage gates, and security-analysis tooling.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Badges/reporting are implemented and locally validated; rollout is owner-controlled.

## Steps / Checklist
- [x] Inspect actual workflow invocation, report outputs, and package metadata.
- [x] Add a compact selection of verified badges.
- [x] Owner approved live Codecov coverage and selected a repository CODECOV_TOKEN secret.
- [x] Implement and test reporting without weakening existing test or release gates.
- [x] Validate markup/targets and regenerate tests/other corpora.

## Deliverables
- A compact, useful README badge block.
- An explicit coverage decision and, if approved, a separately scoped CI integration.

## Files / Paths Impacted
- README.md
- llm_support/llm_full_other.txt
- llm_support/llm_full_other_index.md
- llm_support/manifest.json
- .github/scripts/run_runtime_tests.py
- .github/workflows/test-runtime.yml
- .github/workflows/ci.yml
- .github/workflows/python-publish.yml
- .github/BRANCH_WORKFLOW.md
- codecov.yml
- tests/unit/github_workflows/test_ci_policy.py
- tests/unit/github_workflows/test_workflow_contracts.py

## Validation
- 339 workflow tests, actionlint and scoped correctness Ruff passed.
- Codecov's validation endpoint returned Valid for codecov.yml.
- CI, monthly/lifetime downloads and typed badge URLs return valid SVG (HTTP 200).
- Tests/other corpora regenerated; all three corpus and source-asset checks pass.
- Patch indexes generated with all ranges validated; git diff --check passes.
- Hosted coverage/upload has not run here; no coverage percentage is claimed.

## Risks / Rollback Notes
- A percentage badge without a report source is misleading or broken.
- A prod-only CI badge can report no status because current CI is PR/manual, not push-driven.
- Remove only newly added badge markup if presentation is rejected; preserve all other edits.

## Applicable Anti-Patterns
- [x] No fabricated pass/coverage claims.
- [x] No changes to another agent's CI lane without coordination.
- [ ] No closure without owner acceptance.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/readme_badges_validation_20260906/
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/architecture_patch.md
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/component_patch_coverage_reporting.md
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/code_description_patch_reporting.md
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/architecture_patch_index.md
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/component_patch_coverage_reporting_index.md
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/code_description_patch_reporting_index.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Promote final decisions into the branch guide; retain patches until owner closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record measured reporting support, badge sources, the owner's coverage decision, and validation results.

## Notes
- DATETIME: 2026-09-06T14:28:14Z
  TYPE: FACT
  CLAIM: README already has PyPI, Python versions, license, hosted docs and downloads badges.
    CI runs three OS targets on Python 3.14t. Its runner writes JUnit but passes no coverage flags,
    and the workflow uploads only runtime.xml; no Codecov/Coveralls integration exists in these files.
    Package metadata declares zero runtime dependencies and a shipped py.typed marker.
  EVIDENCE:
  - README.md:16-20
  - .github/workflows/ci.yml:1-10
  - .github/workflows/test-runtime.yml:10-43
  - .github/scripts/run_runtime_tests.py:20-40
  - pyproject.toml:71-71
  - pyproject.toml:151-152
  IMPACT: CI status, zero dependencies and typed-package badges have concrete local support.
    A live coverage percentage needs report generation/upload, not just another image URL.
  NEXT: Ask whether to integrate Codecov while adding the already-supported README badges.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:33:23Z
  TYPE: DECISION
  CLAIM: Owner approved live Codecov integration and asked about account/API-key requirements.
    Use GitHub OIDC in a separate reporting job after the existing three-platform matrix succeeds.
    Tests remain contents-read-only; only reporting gets id-token write, forwarded by both callers.
    Retain coverage XML alongside JUnit in separate artifacts; upload failure remains nonblocking.
    No new suite trigger or coverage threshold. Final-release reports map to the already-verified
    prod branch; the prod badge populates after a prod report. Fork PRs retain XML but skip OIDC upload.
  EVIDENCE:
  - Owner approval: "Yes, set up live Codecov coverage".
  - .github/scripts/run_runtime_tests.py:20-40
  - .github/workflows/test-runtime.yml:1-43
  - .github/workflows/python-publish.yml:19-71
  - https://github.com/codecov/codecov-action#using-oidc
  - https://about.codecov.io/pricing/
  IMPACT: Preserve workflows_1's stage policy and all existing dirty changes. Codecov signup/repo
    authorization is an owner step; no API key is required for the chosen OIDC route.
  NEXT: Consume the small reporting patch contract, then implement and validate its exact scope.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:42:29Z
  TYPE: DECISION
  CLAIM: Owner logged into Codecov and prefers token authentication like PyPI. Use the repository
    Actions secret CODECOV_TOKEN, not a GitHub environment and not OIDC. Supersedes the auth choice
    above. Consumed the three patch contracts; runner section maps to optional-argument tests,
    workflow section to parsed-YAML permission/artifact/failure tests, and setup to the branch guide.
  EVIDENCE:
  - Owner: "I'd probably use an env token tbh if its like pypi" and CODECOV_TOKEN secret question.
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/architecture_patch.md:1-29
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/component_patch_coverage_reporting.md:1-28
  - system_docs/patches/active/readme_coverage_badges_2026_09_06/code_description_patch_reporting.md:1-19
  IMPACT: No id-token write permission, new environment, or publishing-credential change is needed.
    Missing token warns and skips reporting; it must not fall back to tokenless upload.
  NEXT: Implement the token-based reporting contract, badges, and focused regression tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:48:28Z
  TYPE: FACT
  CLAIM: Optional coverage generation, explicit caller token forwarding and isolated reporting are
    implemented. Missing token warns/skips; failed tests skip uploads; all three same-run XML files
    are required to avoid partial-matrix reporting. No OIDC permissions or publishing environment
    changed. Owner reports the secret added. Added CI, coverage and typed badges; retained zero
    dependencies as prose and added lifetime downloads beside monthly downloads at the owner's request.
  EVIDENCE:
  - .github/scripts/run_runtime_tests.py:20-50
  - .github/workflows/test-runtime.yml:1-112
  - .github/workflows/ci.yml:62-68
  - .github/workflows/python-publish.yml:62-67
  - README.md:16-25
  - https://pepy.tech/pepy-api
  IMPACT: Ready for focused validation. Hosted coverage remains unverified until owner rollout.
  NEXT: Run workflow regression tests and actionlint, then refresh affected corpus proofs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:52:23Z
  TYPE: MEASURE
  CLAIM: All 339 focused workflow tests pass (1.31s) and actionlint passes all workflows.
    CI, monthly downloads, lifetime downloads and typed badge endpoints return HTTP 200 and
    parse as SVG. Owner reports CODECOV_TOKEN configured. Marked only codecov.yml intent-to-add
    so the tracked-file asset generator includes it; no content was staged and no commit/push ran.
  EVIDENCE:
  - artifacts/readme_badges_validation_20260906/workflow-tests.xml
  - tests/unit/github_workflows/test_ci_policy.py:485-511
  - tests/unit/github_workflows/test_workflow_contracts.py:107-182
  - codecov.yml:1-6
  - Public endpoint validation command (HTTP 200, XML parsed)
  IMPACT: Local reporting and gate contracts pass. No coverage percentage or hosted upload is claimed.
  NEXT: Regenerate tests/other corpora and patch indexes, then hand off the owner-controlled rollout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T14:55:32Z
  TYPE: MEASURE
  CLAIM: Codecov YAML validation returned Valid. Regenerated tests (808 inputs) and other (355
    inputs); all corpus/source-asset checks pass. Patch indexes validate all ranges. Scoped Ruff
    E9/F63/F7/F82 and git diff --check pass. No new triggers, thresholds or runtime changes.
  EVIDENCE:
  - artifacts/readme_badges_validation_20260906/validation.md:1-15
  - .github/workflows/test-runtime.yml:1-105
  IMPACT: Ready for owner rollout; no actual hosted coverage upload or percentage is claimed.
  NEXT: Owner promotes changes and observes a normal run or manually runs Runtime tests on prod.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Added CI, coverage, typed and lifetime-download badges; monthly downloads remains. Zero dependencies
stays prose only. Existing tests emit XML; a separate nonblocking job uses repository CODECOV_TOKEN.
Owner reports the secret saved. All 339 focused tests, lint, Codecov YAML and generated checks pass.
No commits/pushes or hosted upload. Only codecov.yml is intent-to-add for generator discovery.
Owner promotes changes; a normal final release or manual Runtime tests on prod seeds its badge.
