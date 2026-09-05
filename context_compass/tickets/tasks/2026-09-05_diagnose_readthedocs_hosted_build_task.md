# Task: Diagnose the failing hosted Read the Docs site

## Metadata
- Task ID: TASK-2026-09-05-diagnose-readthedocs-hosted-build
- Story: none (owner-requested diagnosis of the existing documentation deployment)
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-05T23:16:25Z
- Updated: 2026-09-05T23:28:57Z

## Objective
Identify why the owner's Read the Docs deployment is not working and determine the concrete
correction from the actual hosted build, selected Git revision and repository configuration.

## Ticket Contract
- ENTRY_GATE: Existing certification, owner request, active route and evidence-first diagnosis.
- EXECUTION_BOUNDARY: Read the Docs public project/build state and relevant GitHub statuses;
  .readthedocs.yaml, docs configuration/dependencies/build helpers, related documentation tickets.
  Record the failure before any scoped correction; preserve unrelated runtime and workflow work.
- DEPENDENCIES: tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md and the owner's project/build URL.
- EXIT_GATE: Verified cause and concrete correction or a specific missing-access/build-data blocker;
  any local correction is validated without claiming an unexecuted hosted deployment.
- FAILURE_ESCALATION: Do not infer a green hosted build from green GitHub docs CI. Do not publish,
  change account/project visibility, store credentials, commit or push during this diagnosis.

## Scope Boundaries
- In scope: hosted failure identity, branch/version selection, repository config and build logs.
- Out of scope: runtime repair, documentation redesign, domains/account changes and other agents' work.

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: Owner confirms the latest site works. Public metadata verifies its successful
  current-prod build; the separate stable failure is traced to a configuration-less historical tag.

## Steps / Checklist
- [x] Resolve the failing project/build URL and actual symptom.
- [x] Compare hosted revision/configuration with GitHub and local build configuration.
- [x] Identify the first actionable failure and its cause.
- [x] Verify healthy latest and document stable's version-specific release requirement.
- [x] Preserve findings in ticket notes before continuing each meaningful investigation.

## Deliverables
- Evidence-backed diagnosis with the failing build/revision and an actionable correction.

## Files / Paths Impacted
- .readthedocs.yaml
- docs/conf.py
- docs/requirements.txt
- docs/requirements.lock
- Related build helpers only when the config or failure points to them.
- This ticket and its attention/mailbox state.

## Validation
- Public project metadata verifies Synaptic724/melder, prod default branch and latest default version.
- Latest RTD build 34412255 succeeded for prod f8b0de599200214cb58c79b1c0c2dc1efa08a106.
- Homepage, examples and full contents return HTTP 200; owner confirms the site looks correct.
- Stable build 34412311 selects tag 0.2.3 / 0db5ebe8f1960003766c00eeea79110fe360b750.
- Its notification says the root .readthedocs.yaml was not found. GitHub returns 404 for that
  file at tag 0.2.3 and returns the actual file at prod.
- New local docs build/tests: Not run; diagnosis used actual hosted evidence, and no RTD code changed.

## Risks / Rollback Notes
- Older hosting tickets' 404/missing-project findings are superseded by this public verification.
- Stable needs a release tag that contains the docs configuration; publication/tagging remains owner work.
- No RTD configuration or documentation source has changed for this diagnosis.

## Applicable Anti-Patterns
- [x] No claims from guessed project names or unrelated green CI.
- [x] No correction before identifying the failed hosted boundary.
- [x] No overwrite of codex_2's documentation work.

## Done Checklist
- [x] Failure identity established.
- [x] Cause and next action evidenced.
- [x] Healthy latest distinguished from stable's release-tag requirement.
- [x] Owner-facing result and board state synchronized.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none yet.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: hosted build, branch selection, Sphinx configuration and account access.
- IF_UNKNOWN: none

## Noting Behavior
- Append findings with file/range or hosted-build evidence and one concrete next step.

## Notes
- DATETIME: 2026-09-05T23:16:25Z
  TYPE: UNKNOWN
  CLAIM: Owner reports Read the Docs is not working. The exact URL/build and symptom are not yet
    supplied. Requested whether this is a build failure, 404 or stale documentation while completing
    the already-authorized CI gate move. An existing RTD ticket and root YAML are available locally.
  EVIDENCE:
  - Owner's Read the Docs diagnosis request in the active conversation.
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md
  - .readthedocs.yaml
  IMPACT: Inspect the configured target and historical deployment evidence before selecting a fix.
  NEXT: Read the existing RTD handoff and current hosted build configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T23:21:34Z
  TYPE: FACT
  CLAIM: README advertises melder.readthedocs.io/en/latest. Existing hosting task records a prior
    public 404 and rejected private-dashboard read; it never verified an actual hosted build or
    connected account. Current YAML uses documented Python 3.14 and four supported custom formats,
    with local staging commands. The web reader now returns internal retrieval errors for the site
    and project, which cannot be interpreted as a fresh HTTP 404.
  EVIDENCE:
  - README.md:12-18
  - .readthedocs.yaml:1-38
  - tickets/tasks/2026-09-04_rtd_hosted_project_task.md:88-109
  - https://docs.readthedocs.com/platform/stable/config-file/v2.html#build-jobs-build
  IMPACT: No specific build/configuration failure is established. The owner's current diagnosis
    request authorizes relevant reads; first inspect public HTTP results and GitHub-linked build
    statuses without modifying account settings. The project/build URL question remains pending.
  NEXT: Check actual public endpoint responses and repository commit statuses for hosted build links.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:23:52Z
  TYPE: FACT
  CLAIM: Fresh unauthenticated HTTP reads return 200 for both the advertised latest site and the
    melder public project page. Site title is the current Melder documentation title. This supersedes
    the old 404 finding; the web-reader internal errors were not evidence of site unavailability.
    Current prod is f8b0de599200214cb58c79b1c0c2dc1efa08a106; its GitHub docs job is successful.
  EVIDENCE:
  - https://melder.readthedocs.io/en/latest/
  - https://app.readthedocs.org/projects/melder/
  - https://github.com/Synaptic724/melder/actions/runs/33997665989/job/101390909166
  IMPACT: Determine the hosted build/version and any failing subpage before changing configuration.
    Separate prod failures exist in the Ubuntu runtime and dependency-graph jobs; neither is the
    successful documentation job. The owner's precise symptom/URL is still not supplied.
  NEXT: Inspect public RTD build metadata and the advertised example/contents routes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:25:04Z
  TYPE: FACT
  CLAIM: Public RTD metadata verifies project 1190730, repository Synaptic724/melder, default branch
    prod and default version latest. Latest build 34412255 succeeded at 23:07:46Z for current prod
    f8b0de599200214cb58c79b1c0c2dc1efa08a106. Advertised homepage, examples and contents return 200.
    Newer stable build 34412311 failed at 23:13:13Z and has no recorded commit; inspect its error.
  EVIDENCE:
  - https://app.readthedocs.org/api/v3/projects/melder/
  - https://app.readthedocs.org/projects/melder/builds/34412255/
  - https://app.readthedocs.org/projects/melder/builds/34412311/
  - https://melder.readthedocs.io/en/latest/examples/index.html
  - https://melder.readthedocs.io/en/latest/contents.html
  IMPACT: Hosting is connected and latest is operational. The concrete current failure is the
    stable build, not the source docs CI or public latest deployment.
  NEXT: Read stable build failure details and the version's selected Git identifier.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T23:28:57Z
  TYPE: FACT
  CLAIM: Stable build 34412311 reports config:path:default-not-found. Stable selects tag 0.2.3,
    identifier 0db5ebe8f1960003766c00eeea79110fe360b750; that tag lacks root .readthedocs.yaml,
    while current prod contains it. Latest's successful build and public pages are verified, and
    the owner now confirms the site works and looks correct.
  EVIDENCE:
  - https://app.readthedocs.org/api/v3/projects/melder/builds/34412311/notifications/
  - https://app.readthedocs.org/api/v3/projects/melder/versions/stable/
  - https://api.github.com/repos/Synaptic724/melder/contents/.readthedocs.yaml?ref=0.2.3
  - https://api.github.com/repos/Synaptic724/melder/contents/.readthedocs.yaml?ref=prod
  - https://app.readthedocs.org/projects/melder/builds/34412255/
  IMPACT: No change to the working latest site is required. Stable must target a release containing
    the docs setup; do not move/rewrite the old tag or infer a documentation-source failure.
  NEXT: Include the docs configuration in the next owner-selected release tag and verify its stable build.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Diagnosis complete and in review; owner confirms latest works. Project is connected to the correct
repository, latest targets prod and its actual RTD build succeeded. Stable alone failed because it
selects old tag 0.2.3 without .readthedocs.yaml. No RTD source/config change or account write was made.
The next release used by stable must include the docs configuration. Do not rewrite the historical tag.
