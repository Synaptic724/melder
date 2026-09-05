# Task: Implement branch CI and final release validation

## Metadata
- Task ID: TASK-2026-09-04-implement-branch-ci-release-validation
- Story: none (implementation successor to branch-promotion analysis)
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-04T22:25:15Z
- Updated: 2026-09-05T09:35:41Z

## Objective
Implement the accepted shared CI design for feature-to-dev and branch promotion, retaining fresh
tests/build verification on every final release and a last prod-head check before PyPI upload.

## Ticket Contract
- ENTRY_GATE: Certified workflows_1, board route, and the linked patch contract read and mapped.
- EXECUTION_BOUNDARY: Existing/new .github workflows, scripts, ruleset definitions and process docs;
  tests/unit/github_workflows; tests/unit/llm_support/test_builder.py; pyproject.toml test dependencies;
  generated llm_support assets.
- DEPENDENCIES: tickets/tasks/2026-09-04_github_branch_promotion_analysis_task.md.
- EXIT_GATE: Shared jobs and fail-closed merge gate are implemented; focused tests, workflow lint,
  supported local runtime suite, packaging checks, and asset checks are run or concretely blocked.
- FAILURE_ESCALATION: Preserve unrelated concurrent work. Record environment/external blockers and
  failures before widening scope. Do not activate required checks that have not reached GitHub yet.

## Scope Boundaries
- In scope: Always-reported PR checks, reusable assets/tests/distributions, branch routing, ruleset
  payloads, fresh final release checks, targeted tests, documentation, generated asset updates.
- Later rollout: Automatic promotion credentials, a specific dated candidate, and scheduled release
  publication require the foundation and actual release metadata. Keep them visible as follow-up.
- Excluded: Runtime feature changes, dependency upgrades, PyPI publication, unrelated agent edits.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: The final release-tag regression is fixed and scoped validation passes.
  Latest hardening is local for the owner's commit/push; prior hosted results apply to PR 121's baseline.

## Steps / Checklist
- [x] Author/read architecture, component, and gate-flow contracts.
- [x] Implement reusable checks and central CI with explicit failure aggregation.
- [x] Preserve release-time validation and add a last prod-head check before upload.
- [x] Add/test branch-rule definitions and document deployment ordering.
- [x] Update existing workflow contract test and regenerate affected repository assets.
- [x] Validate focused behavior, YAML/action semantics, runtime, packaging, and generated assets.
- [x] Present concrete result and any remaining GitHub rollout boundary.

## Acceptance Criteria
- Feature PRs run unit/component/integration tests on Linux/Windows Python 3.14t plus asset/hygiene checks.
- Promotion PRs add distribution and installed-wheel verification.
- Mandatory skipped/failed/cancelled checks cannot produce merge-ready success.
- Asset helper workflows never silently bypass mandatory validation through repository variables.
- Final publication runs a fresh test/build chain and rechecks prod immediately before upload.
- No workflow can publish on an ordinary PR; default CI token permissions are read-only.
- Workflow and branch policy behavior has meaningful regression tests.

## Validation
- Final review 2026-09-05: 167 focused tests pass, all seven workflows pass actionlint,
  correctness-scoped Ruff passes, and regenerated tests/other repository bundles verify.
- The new tag guard was first reproduced with a failing test, then verified for moved/deleted,
  malformed, duplicate, lightweight, and annotated-tag cases. Prod is queried after the tag.
- This final hardening is uncommitted locally and has not been run on GitHub; the hosted results
  below describe the earlier PR 121 baseline. No commits or pushes were attempted in this pass.
- Focused CI/asset-builder tests: 147 passed in the main and isolated checkouts.
- Hosted PR CI: success; Linux and Windows each report 11,109 passed, 28 skipped, 15 xfailed,
  one non-strict xpass, and a coroutine shutdown warning. CI / merge-ready succeeds.
- Shared local runtime run: 11,130 passed, 28 skipped, 15 xfailed, one xpassed (220.89 seconds).
- actionlint 1.7.12: all six workflows pass; optional shellcheck/pyflakes were disabled.
- Isolated correctness Ruff (E4/E7/E9/F): pass. Full personal/global style rules were not enforced;
  some request PEP 604 syntax that conflicts with the selected role's Optional/Union requirement.
- Real wheel/sdist build, archive/version checks, and isolated wheel installation smoke test: pass.
- Source/repository asset checks: pass on the isolated review branch; main LLM bundles regenerated
  against its concurrent working-tree changes. Main source manifests belong to the separate disposal lane.
- Commit cb24d33b6f30a6b76b137a3a34a8ccf6e15cf80e: SSH-signed; GitHub verification valid.
- GitHub rulesets 22307416/dev, 22307417/preprod, 22307418/prod: active; all three branches protected.
- PR: https://github.com/Synaptic724/melder/pull/121 (draft, mergeable; not merged).
- Hosted run: https://github.com/Synaptic724/melder/actions/runs/33928393747.
- Actual release publication was not dispatched.

## Risks / Rollback Notes
- Shared checkout contains concurrent docs/disposal changes; scope edits precisely.
- Latest owner instruction: the owner handles commits and pushes. Do not create further commits,
  push branches, or attempt signing/passphrase workarounds; continue with edits and validation.
- Rulesets must be activated only after their named checks are available remotely.
- This prerequisite was met and rulesets are now active. Merge PR 121 into dev, then use the normal
  promotion PRs to carry the CI foundation forward before expecting later branches to supply its checks.
- Roll back workflow callers and reusable workflows together; preserve final publication guards.
- The validation directory contains a registered Git worktree. At accepted cleanup, remove that
  worktree with git worktree remove before deleting disposable validation data; preserve the remote branch/PR.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/branch_ci_release_20260904/validation.md
  - system_docs/patches/active/branch_ci_release_2026_09_04/architecture_patch.md
  - system_docs/patches/active/branch_ci_release_2026_09_04/component_patch_ci_validation.md
  - system_docs/patches/active/branch_ci_release_2026_09_04/component_patch_release_publication.md
  - system_docs/patches/active/branch_ci_release_2026_09_04/code_description_patch_gate_flow.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Owner-accepted closure after durable decisions reach .github/BRANCH_WORKFLOW.md.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: CI, merge enforcement, final release validation.
- IF_UNKNOWN: none

## Noting Behavior
- Append evidence, impact, and one next action at each implementation/validation boundary.

## Notes
- DATETIME: 2026-09-04T22:25:15Z
  TYPE: DECISION
  CLAIM: Owner authorized implementation of the discussed CI adaptation and explicitly requires
    a final release validation run. The first implementation delivers that foundation without
    inventing a release date, package version, or promotion-app credential.
  EVIDENCE:
  - .github/workflows/python-publish.yml:18-119
  - context_compass/tickets/tasks/2026-09-04_github_branch_promotion_analysis_task.md:420-482
  IMPACT: Preserve fresh release qualification; early CI does not replace the final check.
  NEXT: Complete and consume the linked patch contract, then edit workflow/policy helpers.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T22:25:28Z
  TYPE: PLAN
  CLAIM: Required patch artifacts were read in architecture/component/gate-flow order. CI invariants
    map to ci_policy.py route/result tests and ci.yml; release invariants map to shared distribution
    verification, fresh reusable runtime tests, and repeated release-head checks. .venv_new provides
    Python 3.14t with pytest, PyYAML, build, and Ruff for local validation.
  EVIDENCE:
  - system_docs/patches/active/branch_ci_release_2026_09_04/architecture_patch.md:16-43
  - system_docs/patches/active/branch_ci_release_2026_09_04/code_description_patch_gate_flow.md:6-30
  IMPACT: Entry gate is satisfied; no additional approval is needed for the owner-authorized edits.
  NEXT: Implement the policy CLI and reusable workflow files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:35:51Z
  TYPE: DECISION
  CLAIM: Central CI, callable asset/runtime/distribution workflows, and fresh publication checks
    are implemented. Add PyYAML 6.0.3 (available locally) to the test-only dependency group so
    structural workflow regression tests run in hosted CI as well as this environment.
  EVIDENCE:
  - .github/workflows/ci.yml:1-82
  - .github/workflows/python-publish.yml:18-100
  - pyproject.toml:90-96
  IMPACT: Tests can prove dependency/permission/trigger structure without fragile substring-only
    assertions. No runtime dependency is added.
  NEXT: Implement and run focused negative gate/distribution tests and parsed workflow contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:43:11Z
  TYPE: MEASURE
  CLAIM: Initial focused pytest run reports 112 passed and 29 fixture-setup errors, all observed
    failures rooted in denied access to the shared pytest temp directory. Scoped Ruff reports
    style findings including UP045, which conflicts with the role's required Optional/Union syntax.
    Git diff whitespace validation passes. GitHub Actions check provider ID is verified as 15368.
  EVIDENCE:
  - tests/unit/github_workflows/test_ci_policy.py:1-260
  - https://api.github.com/repos/Synaptic724/melder/commits/bf610c2cb403286fd23a4ca9dfdb262621e2d9a1/check-runs
  IMPACT: Use a task-owned temp/cache directory rather than changing tests to hide environment
    failures. Validate correctness lint separately from conflicting global style preferences.
  NEXT: Rerun focused tests with explicit temp paths and validate Actions syntax with actionlint.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T22:45:21Z
  TYPE: MEASURE
  CLAIM: actionlint 1.7.12 (published SHA256 verified) passes all six workflow files with optional
    shellcheck/pyflakes disabled. Correctness-focused Ruff (E4/E7/E9/F, isolated) passes. The focused
    suite outside the sandbox reaches all fixtures: 140 pass; one backslash archive test fails on
    Windows because zipfile normalizes member spelling. Investigate raw-name handling before fixing.
  EVIDENCE:
  - tests/unit/github_workflows/test_distributions.py:83-99
  - .github/scripts/verify_distributions.py:70-100
  IMPACT: Environment issues are resolved by the approved unrestricted test run. The remaining
    failure is a real cross-platform archive-fixture/normalization issue, not skipped validation.
  NEXT: Correct and test raw archive-name validation, then rerun the focused suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:50:46Z
  TYPE: MEASURE
  CLAIM: Focused gate, runtime-driver, archive, parsed workflow, ruleset, and existing LLM-builder
    tests all pass: 147 passed. Raw ZIP names are now checked before Windows normalization can
    conceal backslashes/NULs. Ruleset JSON binds the stable final status to GitHub Actions ID 15368.
  EVIDENCE:
  - .github/scripts/verify_distributions.py:70-103
  - tests/unit/github_workflows/test_distributions.py:40-103
  - tests/unit/github_workflows/test_workflow_contracts.py:110-144
  IMPACT: The implemented failure gates are ready for full-runtime and real-package verification.
  NEXT: Run the supported suite and package build/smoke checks; regenerate repository assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:57:13Z
  TYPE: MEASURE
  CLAIM: Full supported local suite on Python 3.14t/GIL-off completes with 11,130 passed,
    28 skipped, 15 xfailed, and one non-strict xpass in 220.89 seconds. A shutdown warning says a
    coroutine named coro was not awaited; no test failure resulted. Real wheel/sdist build,
    archive/version verification, and isolated installed-wheel document/graph checks pass.
    The shared worktree's separate spellbook_configuration.py edit makes source asset fingerprints
    stale; it belongs to codex_1's disposal lane, not this CI patch.
  EVIDENCE:
  - artifacts/branch_ci_release_20260904/runtime.log
  - artifacts/branch_ci_release_20260904/runtime.xml
  - artifacts/branch_ci_release_20260904/build.log
  - .github/scripts/verify_distributions.py:173-195
  IMPACT: Local runtime and package behavior are validated, with the exact caveats preserved.
    An isolated branch is needed for a self-consistent CI-only diff and GitHub validation.
  NEXT: Apply only CI files and the PyYAML test dependency to an isolated dev-based worktree,
    regenerate its repository assets, and prepare the GitHub review/check run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T23:09:53Z
  TYPE: FACT
  CLAIM: Isolated branch codex/branch-ci-release-validation is based on origin/dev and contains
    only 20 CI/test/config files plus five regenerated repository artifacts. Its focused suite
    passes 147 tests and all source/repository assets verify. Commit cb24d33b6f30a6b76b137a3a34a8ccf6e15cf80e
    is pushed and GitHub reports its SSH signature verified/valid. Draft PR 121 targets dev and
    hosted CI run 33928393747 is running; asset/hygiene checks have passed.
    The key was already unlocked in Windows SSH agent; selecting Windows ssh-keygen for the one
    commit resolved Git's default-agent mismatch without disabling signing or changing saved config.
    The connector denied PR creation, so the authorized GitHub CLI connection created the draft.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/pull/121
  - https://github.com/Synaptic724/melder/commit/cb24d33b6f30a6b76b137a3a34a8ccf6e15cf80e
  - https://github.com/Synaptic724/melder/actions/runs/33928393747
  IMPACT: The exact proposed check can now be verified on GitHub before ruleset activation.
    Canonical work tracking remains this main-checkout ticket, not the review-worktree's old boards.
  NEXT: Wait for hosted CI and inspect its final check; activate reviewed rulesets only after success.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T23:21:21Z
  TYPE: MEASURE
  CLAIM: Hosted run 33928393747 succeeds on signed commit cb24d33b6. Each platform reports
    11,109 passed, 28 skipped, 15 xfailed, one non-strict xpass, and the same coroutine warning.
    The package job intentionally skips for this dev PR; the final merge-ready gate succeeds.
    After verifying that exact head/check, the reviewed rulesets were created and GET-verified:
    dev=22307416, preprod=22307417, prod=22307418. All report active and protected=true, with no
    bypass actors and CI / merge-ready bound to GitHub Actions app 15368.
  EVIDENCE:
  - https://github.com/Synaptic724/melder/actions/runs/33928393747
  - https://api.github.com/repos/Synaptic724/melder/rulesets/22307416
  - https://api.github.com/repos/Synaptic724/melder/rulesets/22307417
  - https://api.github.com/repos/Synaptic724/melder/rulesets/22307418
  - https://github.com/Synaptic724/melder/pull/121
  IMPACT: Required CI is real GitHub enforcement, not only local YAML. The new release flow still
    requires the PR to merge and be promoted to prod. Automatic staging and dated candidates remain
    the explicit next implementation layer; no release was published.
  NEXT: Owner reviews/merges draft PR 121; then promote the CI foundation and implement the next layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T23:34:29Z
  TYPE: DECISION
  CLAIM: Owner explicitly takes responsibility for commits and pushes and asks this agent not to
    attempt committing/signing. This supersedes earlier execution guidance about using Windows
    ssh-keygen. Existing signed PR 121 remains unchanged; no further commits/pushes were attempted.
    Remote codex_features2 now points to the owner's 1d300462a0334944a3a542225c016e9e9153d3fc;
    dev/preprod/prod remain at bf610c2cb and PR 121 is still open, draft, and mergeable.
  EVIDENCE:
  - Owner instruction on 2026-09-04, recorded here.
  - https://github.com/Synaptic724/melder/commit/1d300462a0334944a3a542225c016e9e9153d3fc
  - https://github.com/Synaptic724/melder/pull/121
  IMPACT: Owner controls commit/push operations. Remaining work is foundation rollout, staging
    automation, dated-candidate selection/scheduling, and optional lint/warning cleanup.
  NEXT: Explain remaining rollout steps and continue authorized edits/validation when directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T09:23:16Z
  TYPE: FACT
  CLAIM: Final review found a release-identity gap: release-head validates the tag name from the
    event but never queries the current remote tag target. A tag moved/deleted while prod stays
    unchanged can escape that check. The latest owner branch also includes the documentation job
    added by codex_2; preserve that dependency. Owner continues to handle all commits and pushes.
  EVIDENCE:
  - .github/scripts/ci_policy.py:132-159
  - .github/scripts/ci_policy.py:190-200
  - .github/workflows/ci.yml:60-73
  - https://git-scm.com/docs/git-ls-remote
  IMPACT: Add one bounded release safeguard: verify the live tag's resolved object against the
    event/checkout/prod commit, including annotated-tag peeling. Do not add new automation layers.
  NEXT: Reproduce moved-tag acceptance with a boundary-mocked CLI test, then implement the guard.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:29:22Z
  TYPE: MEASURE
  CLAIM: A boundary-mocked regression reproduces the gap: with a moved remote tag and unchanged
    event/checkout/prod SHAs, release-head exits zero. The test expected refusal and fails on the
    existing implementation. No actual tag, branch, commit, or remote state was changed.
  EVIDENCE:
  - tests/unit/github_workflows/test_ci_policy.py:191-214
  - .github/scripts/ci_policy.py:190-200
  IMPACT: The final pass has one evidenced release correctness fix rather than speculative polish.
  NEXT: Require live tag identity, add annotated/deleted-tag coverage, and rerun focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:35:41Z
  TYPE: MEASURE
  CLAIM: Final hardening passes 167 focused tests, correctness Ruff E4/E7/E9/F, and actionlint on
    all seven current workflows. Regenerated tests and other LLM corpora verify. The live tag is
    queried read-only with ls-remote; annotated tags use the peeled target. Missing/moved/ambiguous
    tag evidence refuses publication, and prod remains the last remote identity read.
    The documentation gate added by codex_2 is preserved. Generated other-corpus updates also reflect
    the current tracked documentation tree; they are not a runtime source-code change.
  EVIDENCE:
  - .github/scripts/ci_policy.py:132-210
  - .github/scripts/ci_policy.py:237-250
  - tests/unit/github_workflows/test_ci_policy.py:196-286
  - .github/workflows/python-publish.yml:85-95
  IMPACT: The CI foundation is ready for owner commit/push. Further promotion/scheduling features
    belong to the next layer; no additional feature work is needed to finish this foundation.
  NEXT: Owner commits/pushes the local final guard and follows the PR/promotion rollout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
FINAL REVIEW 2026-09-05: the CI foundation is ready. A local final hardening additionally checks the
live remote release tag before the last prod check. 167 focused tests, seven workflow lint checks,
correctness Ruff, and tests/other bundle checks pass. These latest changes are uncommitted in the
main checkout; PR 121 and its historical review-worktree still contain the earlier baseline.
Owner handles commits and pushes. No more feature additions are recommended for this foundation.

Earlier implementation is available in draft PR 121 from codex/branch-ci-release-validation to dev.
Signed commit cb24d33b6f30a6b76b137a3a34a8ccf6e15cf80e is GitHub-verified. Hosted CI is green on both
platforms, and all three branch rulesets are active. Main-checkout source manifests reflect a
separate in-progress configuration lane; the isolated CI branch is self-consistent and all its
asset checks pass. Main code/test/config changes and regenerated LLM bundles remain available locally.

Review checkout: context_compass/artifacts/branch_ci_release_20260904/review-worktree.
Canonical work tracking is THIS ticket in the main checkout; ignore that checkout's historical boards.
Final release behavior: fresh tests/assets/build, then distribution identity and prod-head checks
after environment admission and immediately before upload. LATEST OWNER CONSTRAINT: owner handles
commits and pushes. Do not attempt further commits, pushes, or signing workarounds. The earlier
Windows SSH signing notes are historical, not permission to continue committing.
Owner's codex_features2 push is confirmed at 1d300462a0334944a3a542225c016e9e9153d3fc.
Next: review/merge PR 121 and carry the foundation through promotion PRs. Automated dev-to-preprod
management and dated-candidate release scheduling remain the next layer and need their configuration.
