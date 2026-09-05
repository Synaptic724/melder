# Task: Analyze GitHub workflows and branch promotion

## Metadata
- Task ID: TASK-2026-09-04-github-branch-promotion-analysis
- Story: none (standalone discovery)
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-04T21:45:20Z
- Updated: 2026-09-04T22:08:19Z

## Objective
Explain the existing GitHub workflow and branch-management system, then propose a concrete process
for feature branches entering dev and dev being promoted to preprod. The owner requested analysis
and discussion before implementation.

## Ticket Contract
- ENTRY_GATE: Certified workflows_1; active attention-board route; evidence-backed discovery notes.
- EXECUTION_BOUNDARY: Read workflows, their scripts/configuration, branch history, related tickets,
  and available GitHub settings/run evidence. Write only this analysis ticket and coordination rows.
- DEPENDENCIES: Existing publish-workflow and generated-asset lanes provide release context.
- EXIT_GATE: Current flow, evidenced gaps, proposed promotion gates, and unresolved owner decisions
  are documented and presented for review.
- FAILURE_ESCALATION: Mark unavailable remote settings UNKNOWN; raise material design conflicts
  before implementation. Do not infer GitHub protection settings from workflow YAML.

## Scope Boundaries
- In scope: CI triggers, required-check suitability, branch ancestry, promotion mechanics,
  generated assets, release interaction, concurrency, and relevant GitHub branch controls.
- Out of scope: Workflow edits, branch mutations, merges, pushes, releases, publishing, settings
  changes, or taking over another agent's active work.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Concrete feature-to-dev commands, required-check enforcement, and reusable
  workflow boundaries are documented after checking the test layout and current contract tests.

## Steps / Checklist
- [x] Read current workflows and invoked scripts; map feature/dev/preprod/prod events and checks.
- [x] Inspect available branch, pull-request, protection/ruleset, and recent-run evidence.
- [x] Compare current behavior with a proposed promotion process and record tradeoffs.
- [x] Present findings and the remaining owner decisions before implementation.
- [x] Record meaningful findings in Notes before each new discovery tranche.

## Deliverables
- Evidence-backed current-state assessment and proposed branch promotion process in this ticket.
- Owner-facing explanation of concrete improvements, limitations, and implementation scope.

## Files / Paths Impacted
- context_compass/tickets/tasks/2026-09-04_github_branch_promotion_analysis_task.md
- context_compass/attention_board.md (workflows_1 route only)
- context_compass/mailbox_board.md (workflows_1 check-in only)

## Validation
- Workflow/test execution: Not run. Discovery does not dispatch CI or release operations.
- Review source logic and compare it with read-only GitHub evidence where available.

## Risks / Rollback Notes
- The working tree is shared; preserve concurrent changes and other agents' board rows.
- Local workflow content and remote protection settings may differ; identify each evidence source.
- No runtime or remote-state changes are authorized by this discovery ticket.

## Applicable Anti-Patterns
- [x] No claims about workflow behavior from trigger names alone; read the jobs and scripts.
- [x] No assumption that a green workflow is enforced as a required merge check.
- [x] No implementation or branch changes during this analysis.
- [x] No closure before owner acceptance.

## Done Checklist
- [x] Current workflow map is complete.
- [x] Proposed branch process is concrete and evidence-backed.
- [x] Unknown remote settings and owner choices are explicit.
- [x] Notes and handoff summary are current.
- [ ] Owner has confirmed acceptance.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: GitHub Actions, feature-to-dev integration, dev-to-preprod promotion.
- IF_UNKNOWN: none

## Noting Behavior
- Capture tactical findings with source ranges, impact, and one next action.
- Keep notes append-only; correct factual errors explicitly.

## Notes
- DATETIME: 2026-09-04T21:45:20Z
  TYPE: PLAN
  CLAIM: Discovery covers the existing workflow system and a proposed feature/dev/preprod process;
    implementation and remote changes remain outside this ticket.
  EVIDENCE:
  - context_compass/templates/task_template.md:3-44
  IMPACT: Establishes a separate analysis lane without taking over existing release work.
  NEXT: Read the workflow inventory and establish local/remote repository context.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T21:46:49Z
  TYPE: FACT
  CLAIM: The complete .github inventory contains three workflows. Pull requests and branch pushes
    check source assets and repository assets; runtime tests and distribution checks are exclusive
    to release-published/manual publication events gated against current prod HEAD. There is no
    branch-source promotion policy or reusable pre-merge test workflow in this inventory. The current
    release matrix is two cells (Linux/Windows, Python 3.14t), not the four cells named in old tickets.
  EVIDENCE:
  - .github/workflows/build-src-assets.yml:50-114
  - .github/workflows/build-repo-assets.yml:7-51
  - .github/workflows/python-publish.yml:5-119
  IMPACT: A feature or promotion PR receives no runtime-test gate from the checked-in workflows.
    Existing publication checks can be factored into earlier CI instead of inventing a second suite.
  NEXT: Inspect live GitHub protections, branch tips, run history, and merge settings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:46:49Z
  TYPE: FACT
  CLAIM: GitHub's repository connector identifies Synaptic724/melder as public with default branch
    prod and admin permission. It returns null for merge-mode flags, so those flags remain UNKNOWN.
    Local git reports codex_features2 checked out and cached origin feature/dev/preprod/prod tips at
    bf610c2cb; cached refs are not proof of current remote tips. The shared worktree contains other
    agents' documentation and disposal work. A sandboxed gh api request failed at the local proxy.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder
  - .github/workflows/python-publish.yml:3-4
  IMPACT: prod is the verified default branch; remote protection and merge configuration still
    require direct reads. Preserve the shared checkout and all unrelated changes.
  NEXT: Read the live repository settings through an authorized read-only API call.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T21:48:58Z
  TYPE: DECISION
  CLAIM: The owner selected preprod as a continuously updated staging branch that follows dev.
    The proposal must preserve continued integration and automatic staging advancement; a frozen
    release-candidate branch is not the selected model.
  EVIDENCE:
  - Owner reply on 2026-09-04 to the preprod-purpose question, recorded in this note.
  IMPACT: Recommend a maintained dev-to-preprod promotion PR after dev CI, with validation on the
    current promotion candidate before merge; keep prod release promotion explicit.
  NEXT: Complete CI/asset behavior review and define how promotion preserves ancestry and checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:48:58Z
  TYPE: FACT
  CLAIM: Live GitHub API reads confirm codex_features2, dev, preprod, and prod all point to
    bf610c2cb403286fd23a4ca9dfdb262621e2d9a1 and all report protected=false. The repository ruleset
    list is empty. All three merge methods are allowed; auto-merge, automatic head-branch updates,
    and automatic branch deletion are disabled. Actions defaults to read permission and cannot
    approve PR reviews. Neither asset-gate variable is set. The pypi environment has no protection
    rules or deployment branch policy. No API or repository settings were changed.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder
  - https://api.github.com/repos/Synaptic724/melder/branches?per_page=100
  - https://api.github.com/repos/Synaptic724/melder/rulesets?includes_parents=true
  - https://api.github.com/repos/Synaptic724/melder/actions/permissions/workflow
  - https://api.github.com/repos/Synaptic724/melder/actions/variables
  - https://api.github.com/repos/Synaptic724/melder/environments
  IMPACT: Branches are naming conventions rather than enforced stages. Protection and stable
    required checks are foundational; publication approval is also absent from the pypi environment.
  NEXT: Inspect actual CI job/run behavior before sizing and sequencing the proposed gates.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:50:38Z
  TYPE: DECISION
  CLAIM: The owner further described preprod as the CI branch with a release candidate for a
    particular date/time. Interpret this as continuous preprod validation plus an explicitly selected
    candidate for each scheduled release. No date, version, candidate, or actual schedule was supplied.
  EVIDENCE:
  - Owner steering on 2026-09-04, recorded in this note.
  IMPACT: Keep the moving integration branch separate from release identity; a release plan must pin
    a tested SHA, version, artifacts, and time rather than resolve the latest preprod at publication.
  NEXT: Present that combined model and the current publisher changes it requires.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-04T21:50:38Z
  TYPE: FACT
  CLAIM: GitHub returned zero pull requests, and all 69 visible workflow runs were push, release,
    or GitHub dynamic dependency-graph events; none were PR runs. Release run 33345119501 failed its
    supported-test-tiers step on both platforms after the prod gate passed. Run 33345742663 later
    succeeded: its test jobs took 3m28s (Windows) and 3m31s (Linux), with the whole run about 4m52s.
    These are historical GitHub observations, not tests executed in this analysis or a timing SLA.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder/pulls?state=all&per_page=20
  - https://api.github.com/repos/Synaptic724/melder/actions/runs?per_page=100
  - https://github.com/Synaptic724/melder/actions/runs/33345119501
  - https://github.com/Synaptic724/melder/actions/runs/33345742663
  IMPACT: Runtime regressions have been detected at the release step; reusing the existing matrix
    earlier is practical enough to recommend before considering a reduced suite or merge queue.
  NEXT: Propose required PR checks and continuous staging from the existing tested job design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:50:38Z
  TYPE: FACT
  CLAIM: The repository asset builder classifies source, test, and other tracked text into corpora,
    excludes ContextCompass and its own outputs, and checks fingerprints/output/index proofs without
    writing. Workflow YAML participates in the other corpus. Source assets have their own runner.
    Parallel feature changes can require regenerating assets after integration even when source
    edits do not conflict. This is an integration requirement, not a reason for CI to write commits.
  EVIDENCE:
  - llm_support/_builder.py:63-101
  - llm_support/_builder.py:290-350
  - llm_support/_builder.py:653-702
  - src/melder/_build_assets/_build_asset_runner.py:268-366
  IMPACT: Required checks should evaluate the PR merge result, and stale outputs should be rebuilt
    on the feature branch after updating it. Workflow implementation must regenerate the other corpus.
  NEXT: Include generated-asset reconciliation in the feature-to-dev process.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:50:38Z
  TYPE: FACT
  CLAIM: GitHub documents two distinct skipped-check outcomes: a path-filtered workflow leaves a
    required check pending, while a conditionally skipped job can satisfy a required check. The
    source workflow has top-level path filtering, and both asset jobs can be disabled by variables.
    Both status-reporting jobs also share the display name gate status.
  EVIDENCE:
  - .github/workflows/build-src-assets.yml:50-97
  - .github/workflows/build-repo-assets.yml:20-37
  - https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
  - https://docs.github.com/en/pull-requests/reference/status-checks
  IMPACT: Do not blindly mark the existing job names required. Introduce an always-reported final
    merge gate that checks explicit success for every mandatory job and cannot be disabled by flags.
  NEXT: Specify stable branch gates and candidate-release invariants in the proposal.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T21:55:35Z
  TYPE: PLAN
  CLAIM: The completed proposal orders implementation as shared required PR CI and branch rules,
    continuous dev-to-preprod promotion, then fixed-candidate timed publication. It preserves asset
    generation as a contributor commit, records long-lived merge ancestry constraints, and separates
    staging movement from the identity of the scheduled release. This is a proposal, not approval
    to edit product workflows or GitHub settings.
  EVIDENCE:
  - .github/workflows/python-publish.yml:5-119
  - .github/workflows/python-publish.yml:310-346
  - https://docs.github.com/en/pull-requests/reference/pull-request-merges
  - https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
  IMPACT: The owner can choose a concrete implementation scope from the process recorded below.
    Source/workflow review and read-only GitHub inspection are complete; no CI was dispatched.
  NEXT: Review the proposed branch roles and candidate/publication approval policy with the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-04T22:03:24Z
  TYPE: PLAN
  CLAIM: The owner accepts the broad direction and asks which tests should run for feature-to-dev,
    what required CI means, and how the existing workflows should change. Continue the same analysis
    lane; this question does not select or authorize product workflow implementation yet.
  EVIDENCE:
  - .github/workflows/python-publish.yml:68-119
  - pyproject.toml:87-129
  IMPACT: Refine the proposal into concrete job boundaries, commands, and enforcement behavior.
  NEXT: Check test documentation and existing builder-test placement before finalizing the CI matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-04T22:06:11Z
  TYPE: FACT
  CLAIM: The test architecture and component indexes match their documents' line counts and
    SHA256 values. Relevant slices distinguish unit contracts, small real component wiring, and
    full runtime integration. The actual root conftest inserts the checkout source and root paths.
    tests/unit/llm_support/test_builder.py includes a workflow-shape test that explicitly requires
    the current workflow names, asset commands, action versions, and both disable-variable strings.
  EVIDENCE:
  - context_compass/system_docs/tests_architecture.md:140-316
  - context_compass/system_docs/tests_components.md:277-484
  - tests/conftest.py:1-22
  - tests/unit/llm_support/test_builder.py:337-357
  IMPACT: Use the explicit unit/component/integration directories from the existing release job.
    A deliberate workflow refactor must revise the asset workflow contract test as part of the change.
  NEXT: Present the concrete PR CI matrix and reusable-workflow adaptation below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-05T10:08:25Z
  TYPE: DECISION
  CLAIM: The owner explicitly requested turning in workflows_1's tickets. This analysis was
    implemented by TASK-2026-09-04-implement-branch-ci-release-validation and is accepted for closure.
    Its proposal and dated observations remain historical evidence; the implementation successor
    carries the delivered foundation, current rollout boundary, and final validation results.
  EVIDENCE:
  - Owner closeout instruction on 2026-09-05, recorded in the implementation successor.
  - context_compass/tickets/tasks/2026-09-04_implement_branch_ci_release_validation_task.md:298-404
  IMPACT: Turn in this analysis with the implementation ticket; there are no analysis artifacts.
  NEXT: Record completion and move the selected ticket into tickets/tasks/completed/.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

## Proposed Process (For Owner Review)

### Branch and release roles

| Surface | Responsibility | Entry and exit |
| --- | --- | --- |
| Short-lived feature branch | One scoped change, created from current dev | PR targets dev; retire after merge |
| dev | Integration of reviewed changes | Required PR CI; passing revisions feed a staging promotion PR |
| preprod | Continuously validated staging | Same-repository dev promotion only; full tests and package checks |
| Release candidate | Fixed version/SHA and verified artifacts selected from green preprod | Explicit approval and scheduled release time |
| prod | Production release history | Candidate-specific promotion and release checks; no automatic latest-preprod selection |

All ordinary contributions, including workflow edits and documentation, target dev explicitly because
GitHub's default branch is prod. A required branch-policy job refuses feature-to-preprod/prod skips.
The policy must check both the source branch and source repository for promotions, so a fork branch
named dev cannot impersonate the repository's integration branch. Exceptions for authorized release
fixes and back-merges must be explicit rather than permanently opening a direct-push bypass.

### Feature branch to dev

1. Create one branch from dev and open a PR with base=dev.
2. Run read-only CI on the proposed merge result: both asset checks, repository hygiene, and tests.
3. Start by reusing the existing two-platform Python 3.14t unit/component/integration matrix; the
   observed historical runtime is about 3.5 minutes per platform. Reduce tiers only after measuring
   actual PR feedback latency, not by assumption. Wheel/build checks can remain a staging gate.
4. Require an always-reported final check such as ci / merge-ready, plus branch-policy. It must
   inspect every mandatory dependency result explicitly and fail on failure, cancellation, or an
   unexpected skip. Do not require a path-filtered workflow or a warning-only gate-status job.
5. Require PRs, successful checks, resolved discussions, and an up-to-date integration result.
   Block force pushes and deletion of permanent branches. Choose reviewer counts to fit the team;
   requiring an independent human review can deadlock a sole maintainer's own PR.
6. Prefer squash for disposable feature branches when one PR is one change. Start the next feature
   from current dev; do not reuse a squashed feature branch indefinitely.

CI remains check-only. Updating a feature branch can combine source changes whose generated corpus
is stale despite a clean Git merge. Regenerate source assets and then repository assets on the
feature branch, stage new inputs so the builder sees them, and commit the regenerated outputs.
Never hand-merge bundle content or let a privileged PR workflow commit it after the fact.

### dev to preprod

1. A successful trusted dev run opens or refreshes one same-repository dev-to-preprod promotion PR.
2. Full runtime tests, asset verification, distribution-boundary checks, version agreement, and a
   clean wheel-install smoke test validate the current promotion result. CI carries no PyPI secret.
3. Auto-merge is appropriate for continuous staging only after these required checks pass. Updates
   to dev supersede an older candidate; the merge operation must target the head SHA that passed.
4. Validate the resulting preprod revision and publish its check/build record. Only this verified
   revision is eligible for candidate selection. A new in-flight or failed revision is not green.
5. Use merge commits for promotion between permanent branches; do not repeatedly squash/rebase
   dev into preprod. Keep promoted hotfix/release changes flowing back to dev, and never rewrite
   permanent history merely to make branch tips identical.

Strict up-to-date protection and merge commits need a deliberate synchronization policy: a target
merge commit is not automatically present on dev. Either support merge-back synchronization, or
serialize promotion to the sole allowed source and validate the current merge result without the
strict ancestry requirement. Do not enable strict mode blindly and create a perpetual update loop.
If synchronization automation is used, tree-identical history-only changes must not create endless
promotion PRs. A merge queue is a later option after verifying repository eligibility and adding
merge_group triggers; it is not required to solve the current absence of PR gates.

For unattended promotion, use a narrowly scoped GitHub App identity or explicit authenticated
dispatch design. Current GitHub documentation says GITHUB_TOKEN-created/updated PR workflows enter
an approval-required state for opened/synchronize/reopened, while most other token-created events
do not trigger another run. An App token can permit automatic PR CI. A design that assumes normal
push/PR event propagation from every bot action can leave a promotion waiting indefinitely.

### Dated release candidates

The release plan needs a release ID, package version, candidate SHA, successful validation run ID,
artifact IDs and digests, approved state, release date/time with an explicit timezone, and retained
artifacts lasting beyond that date. No actual schedule or version has been selected in this task.

- Select a green preprod revision and record its immutable identity; keep preprod moving afterward.
- Prepare and verify the distributable artifacts before the publication window. Record every change
  of candidate as a new candidate with new checks rather than silently moving a tag or pointer.
- A candidate-specific release branch/PR can provide the controlled path to prod while later preprod
  work accumulates. The publisher must identify the nominated candidate, never the latest preprod.
- A merge into prod may create a different commit SHA or tree. Verify the merge result explicitly:
  either qualify/build that exact result, or prove the promoted tree equals the candidate tree and
  retain the candidate artifact provenance. Do not claim an old SHA's checks validate changed content.
- Serialize production promotion/publication and recheck candidate identity immediately before
  publishing. A changed prod base, revoked approval, missing artifacts, or stale checks blocks the
  release and requires a new qualification decision.
- Decide whether RC means an internal candidate build of the final version or an actual Python
  prerelease version. A 0.x.yrc1 wheel cannot become 0.x.y merely by changing a GitHub tag; final
  version/asset changes require a fresh build and validation.
- Keep release approval ahead of the scheduled window if automatic timed publication is desired.
  Requiring a human at publication time makes the time conditional on that approval.
- Use a due-release check that is idempotent and records outcomes, with a manual retry/dispatch path.
  GitHub Actions scheduling is best-effort: jobs can be delayed/dropped, run from the default branch,
  and may disable after public-repository inactivity. It is a target-time mechanism, not an exact
  clock-time guarantee. Default UTC or a supported IANA timezone must be explicit.
- Distinguish package upload success from GitHub-release publication so retries cannot duplicate or
  misreport a partially completed release. Never rebuild different bytes under an already released
  package version.

### Reuse and changes to existing workflows

| Current file or setting | Proposed change |
| --- | --- |
| build-src-assets.yml | Reuse checker in always-reported PR CI; remove disable switches from mandatory merge gating |
| build-repo-assets.yml | Keep check-only semantics; reuse checker and avoid duplicate push/PR work |
| python-publish.yml | Extract reusable validation/build steps; publisher consumes the nominated candidate artifacts |
| New branch-policy/CI orchestration | Enforce target/source routes and one stable final required status |
| New dev-to-preprod orchestration | Maintain one promotion PR with scoped credentials and verified event propagation |
| New candidate/scheduled-release orchestration | Record SHA/version/digests/time, qualify candidate, serialize and audit publication |
| GitHub branch rulesets | Require PRs/checks; block force pushes/deletion; choose intentional bypass/reviewer policy |
| pypi environment | Define release approval/branch restrictions for the selected candidate design |

The current source-workflow comment suggests per-ref concurrency removes duplicate push/PR runs,
but push refs and PR merge refs are different. Prefer PR validation plus selected permanent-branch
push validation, rather than heavy CI on every feature push and again on its PR. Use unique check
names; both current workflows call their reporting job gate status. Add explicit timeouts and
permissions when the workflows are refactored.

The current publisher checks event SHA against prod only at job start and retains build artifacts
for seven days. Its unqualified release-published trigger and manual dispatch have no candidate or
schedule input. Candidate publishing must add explicit identity/version/approval policy rather than
simply adding cron to that workflow. Keep the ordinary PR path read-only and secret-free.

### Rollout and remaining decisions

1. Implement shared PR CI and unique final checks; observe their actual names and outcomes on a PR.
2. Enable corresponding dev/preprod/prod rulesets after the checks are available; verify a failing
   PR blocks and a valid PR merges. Keep existing publisher protection while this is introduced.
3. Add continuous staging promotion and verify updates, cancellation, ancestry, and bot-triggered CI.
4. Add candidate selection and a dry-run scheduled release path, then integrate PyPI publication.

Pending owner decisions for implementation: candidate approval authority, automatic publication
versus publication-time approval, the concrete release time/version, and whether RC artifacts should
be published publicly as prerelease packages. None blocks this discovery recommendation.

## Concrete Feature-to-dev CI Adaptation (Owner Follow-up)

The recommended first required suite is the existing supported runtime matrix: Python 3.14t on
Linux and Windows, with unit, component, and integration tests in each matrix job:

```text
python -m pytest -q tests/unit tests/component tests/integration
```

Run independent jobs in parallel: branch-policy, source-asset check, repository-asset check,
repository hygiene, and the runtime matrix. Add one final merge-ready job with an unconditional
dependency-result evaluation. Its success means every mandatory job for this PR actually succeeded.
If tests fail, dependencies cancel, or a mandatory job is unexpectedly skipped, merging stays blocked.
The proposed workflow must run on every relevant PR; do not hide it behind top-level path filters.

| Check | Initial feature-to-dev posture | Purpose |
| --- | --- | --- |
| Unit tests | Required, Linux and Windows 3.14t | Class/function contracts and regression behavior |
| Component tests | Required, same matrix | Small real collaborator slices |
| Integration tests | Required, same matrix | Cross-subsystem and concurrency-related runtime interactions |
| Supported runtime check | Required in test execution | Verify free-threaded build and intended GIL state, beyond version alone |
| Source assets | Required | Existing source build-asset runner --check |
| Repository assets | Required | Existing llm_support builder --check |
| Repository hygiene | Required | Existing case-collision check, useful across Linux and Windows |
| Branch policy | Required | Contributions target dev and promotions use authorized source/base pairs |
| Ruff and mypy | Baseline first, then enforce agreed checks | Configured development tools; current clean baseline not measured here |
| Distribution build/install | Required for preprod and candidate qualification | Packaging boundary/version checks and installed-wheel smoke test |

Required CI is the combination of (1) jobs that report named status checks and (2) a GitHub ruleset
that requires those checks before a PR can merge into dev. Running jobs alone does not enforce it.
Configure the stable final check and branch-policy as required, require a PR, block force pushes and
branch deletion, and avoid broad bypass permissions. New PR commits require fresh success. When dev
has moved, validate against the updated base through the chosen up-to-date/merge-result policy.
Human review is a separate setting; choose it to match the actual maintainer model.

Concrete workflow decomposition (proposed files, not implemented):

- ci.yml: PR entrypoint and job orchestration; calls reusable checks, runs branch-policy/hygiene,
  then reports merge-ready. Run on PRs targeting dev/preprod/prod and selected permanent-branch
  pushes; cancel superseded PR runs and keep validation permissions read-only.
- build-src-assets.yml: keep the existing runner command, add workflow_call and retain manual
  dispatch. Remove the overlapping automatic triggers after ci.yml takes ownership. Mandatory
  invocations must not obey BUILD_SRC_ASSETS_GATE=off.
- build-repo-assets.yml: same callable/manual shape; keep --check and contents:read. Mandatory
  invocations must not obey BUILD_REPO_ASSETS_GATE=off.
- test-runtime.yml: extract the existing Python 3.14t Linux/Windows job once and call it from CI and
  release validation. Preserve explicit test paths and add readable test-result artifacts.
- build-distributions.yml: extract release-build validation for use by preprod and release/candidate
  qualification. Keep package verification and wheel smoke commands shared rather than copied.
- python-publish.yml: retain release authorization and PyPI environment isolation, call shared
  validation/build units, then evolve toward the nominated-candidate artifact contract in the
  earlier proposal. Ordinary feature PRs never get a publishing step or its environment secret.

Use same-repository reusable-workflow references so the called logic comes from the revision being
reviewed. Shared hygiene/distribution-check scripts can replace the large inline shell/Python blocks
when extracted, so the release and CI variants cannot drift. Update the existing builder test to
assert the new callable/read-only/fail-closed contract, not obsolete global-disable behavior.

Do not add a blanket coverage percentage or performance benchmark threshold before measuring a
baseline. The immediate improvement is meaningful tests becoming enforced at the integration
boundary. Any later change-aware skipping must still produce a truthful final required check.

No tests, linters, or workflows were run in this follow-up; this is configuration/source analysis.

## Reference Links

- GitHub repository snapshot endpoints are listed in the Notes above.
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/pull-requests/reference/pull-request-merges
- https://docs.github.com/en/pull-requests/reference/status-checks
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
- https://docs.python.org/3.14/howto/free-threading-python.html

## Context / Handoff Summary
Analysis is ready for owner review. The three existing workflows are asset checks plus a prod-only
publication pipeline. Live GitHub confirms no PR history, no protected branches, and no rulesets.
Owner wants continuous preprod CI and a release candidate associated with a specific release time.
Recommended order: PR CI and protection, automatic staging promotion, then fixed-candidate timed
publication. Product files, branches, GitHub settings, and CI runs were not changed or dispatched.
The owner follow-up is answered by Concrete Feature-to-dev CI Adaptation: all three test tiers on
Linux/Windows 3.14t, both asset checks, hygiene, branch-policy, and one stable final merge gate.
Existing asset workflows become callable; runtime and packaging jobs are extracted for shared use.
Ruff/mypy clean baselines remain unmeasured; workflow-shape tests must change with the intended design.
Next: discuss this concrete CI adaptation and select implementation scope, then create the patch contract.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
