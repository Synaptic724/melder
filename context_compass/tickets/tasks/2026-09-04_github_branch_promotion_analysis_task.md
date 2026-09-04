# Task: Analyze GitHub workflows and branch promotion

## Metadata
- Task ID: TASK-2026-09-04-github-branch-promotion-analysis
- Story: none (standalone discovery)
- Status: in_progress
- Owner: codex
- Agent Name: workflows_1
- Priority: p1
- Created: 2026-09-04T21:45:20Z
- Updated: 2026-09-04T21:45:20Z

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
- from_state: ready
- to_state: in_progress
- transition_reason: Owner explicitly assigned workflow and branch-management analysis.

## Steps / Checklist
- [ ] Read current workflows and invoked scripts; map feature/dev/preprod/prod events and checks.
- [ ] Inspect available branch, pull-request, protection/ruleset, and recent-run evidence.
- [ ] Compare current behavior with a proposed promotion process and record tradeoffs.
- [ ] Present findings and the remaining owner decisions before implementation.
- [ ] Record meaningful findings in Notes before each new discovery tranche.

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
- [ ] No claims about workflow behavior from trigger names alone; read the jobs and scripts.
- [ ] No assumption that a green workflow is enforced as a required merge check.
- [ ] No implementation or branch changes during this analysis.
- [ ] No closure before owner acceptance.

## Done Checklist
- [ ] Current workflow map is complete.
- [ ] Proposed branch process is concrete and evidence-backed.
- [ ] Unknown remote settings and owner choices are explicit.
- [ ] Notes and handoff summary are current.
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

## Context / Handoff Summary
Owner assigned branch/workflow analysis to workflows_1. Certification and role onboarding are
complete. Begin with workflow inventory, then inspect invoked scripts and GitHub controls.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
