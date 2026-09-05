# Task: Qualify a frozen release candidate through TestPyPI before production

## Metadata
- Task ID: TASK-2026-09-05-release-candidate-testpypi-workflow
- Story: none (successor to accepted branch CI foundation)
- Status: in_progress
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-05T10:25:12Z
- Updated: 2026-09-05T10:25:12Z

## Objective
Extend the promotion route to dev -> preprod -> release_candidate -> prod. Keep preprod as full
continuous validation. The selected candidate is tested through TestPyPI and identified by exact
commit, version, workflow run, and distribution hashes before final production publication.

## Ticket Contract
- ENTRY_GATE: Existing certification, this active route, and consumed patch contracts before edits.
- EXECUTION_BOUNDARY: .github workflows/scripts/ruleset payloads/branch guide; focused workflow tests;
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
- from_state: ready
- to_state: in_progress
- transition_reason: Owner requested an automated candidate workflow, then selected a distinct
  release_candidate branch and is handling its spelling/rename.

## Steps / Checklist
- [x] Inspect existing shared CI, branch policy, packaging, and publication contracts.
- [ ] Define and consume the candidate identity, artifact, trigger, and failure contracts.
- [ ] Extend branch routing and create the candidate ruleset payload.
- [ ] Implement TestPyPI upload/installed-package verification and retained qualification evidence.
- [ ] Require matching candidate evidence during fresh final publication.
- [ ] Validate route/provenance/failure cases and workflow wiring; refresh affected assets.
- [ ] Present owner setup/rollout and explicitly separate local checks from hosted execution.

## Deliverables
- Reviewed workflow/helper/test changes for the four-stage permanent-branch route.
- Durable operator instructions including TestPyPI project and GitHub environment configuration.

## Validation
- Not run for this extension yet. Use focused pytest, actionlint, scoped correctness Ruff, actual
  local distribution smoke tests, and affected asset checks. No real package upload as validation.

## Risks / Rollback Notes
- TestPyPI account/project and trusted-publisher configuration are not verified or supplied yet.
- TestPyPI files cannot be silently replaced; retries must establish identical content or refuse.
- A prod merge commit can have a different SHA: require the selected candidate tree to match the
  production checkout and keep the existing final live tag/prod guard.
- Earlier successful candidate evidence must not qualify later branch changes or different bytes.
- Rollback branch policy, workflow callers, and required checks together through the owner's rollout.

## Applicable Anti-Patterns
- [ ] No test result applies to a different version/tree/artifact.
- [ ] No upload authority in PR/install-test jobs.
- [ ] No mutable latest-candidate lookup after a candidate has been selected for publication.
- [ ] No blind skip-existing or unverified reuse after partial upload.
- [ ] No false hosted-validation claim and no closure before owner acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/architecture_patch.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_candidate.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/component_patch_publication.md
  - system_docs/patches/active/release_candidate_testpypi_2026_09_05/code_description_patch_identity.md
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
  - src/melder/__version__.py:11-11
  IMPACT: Reuse existing checks and explicitly bind final publication to the newly qualified files.
  NEXT: Define candidate selection and artifact checks before editing workflow/helper code.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
New owner-authorized extension, separate from the two completed foundation tickets. The owner
created/renamed release_candidate; keep working on codex_features2 and leave commits/pushes to them.
Preprod keeps full shared CI. One chosen release candidate will stage on TestPyPI, verify the exact
downloaded package, and retain identity evidence needed by final publication. No implementation or
external setup/upload has occurred yet. Version choice is pending; other contract work can proceed.
