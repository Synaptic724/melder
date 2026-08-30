# Task: Upgrade the Python package publication workflow

## Metadata
- Task ID: TASK-2026-08-30-upgrade-python-publish-workflow
- Story: none
- Status: review
- Owner: cowork
- Agent Name: codex_1
- Priority: p0
- Created: 2026-08-30T15:55:48Z
- Updated: 2026-08-30T16:04:06Z

## Objective
Replace the minimal publication workflow with a release-gated Melder pipeline that
tests Python 3.14 runtimes, validates durable build assets and distributions, and
publishes to PyPI through OIDC only when the event commit is current `prod` HEAD.

## Ticket Contract
- ENTRY_GATE: Owner approved upgrading the existing staged workflow after comparison
  with the ContextCompass reference.
- EXECUTION_BOUNDARY: `.github/workflows/python-publish.yml` plus this task and
  attention-board routing only.
- DEPENDENCIES: Existing `pyproject.toml` dependency groups, build-asset runner,
  supported unit/component/integration test tiers, and PyPI trusted publishing.
- EXIT_GATE: Workflow is structurally validated; prod gate, test matrix, distribution
  checks, isolated install smoke, and OIDC publish job are all present.
- FAILURE_ESCALATION: Stop on ambiguity in the PyPI environment name or on any
  validation result that requires changing package/runtime behavior.

## Scope Boundaries
- In scope:
  - exact current-prod commit gate for release and manual dispatch
  - Python 3.14 and 3.14t tests on Ubuntu and Windows
  - build-asset, wheel/sdist, version/tag, and installed-wheel verification
  - current official action major upgrades
  - OIDC-only PyPI publishing through the existing `pypi` environment
- Out of scope:
  - publishing a release
  - changing PyPI or GitHub environment configuration
  - changing package source, tests, versions, or dependencies
  - copying ContextCompass-specific payload/CLI checks

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: The owner approved the tailored workflow upgrade.

## Steps / Checklist
- [x] Replace the minimal workflow with the tailored release pipeline.
- [x] Validate trigger/gate, job dependencies, action versions, and embedded scripts.
- [x] Inspect the exact diff and report remaining GitHub/PyPI configuration requirements.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- A production-ready `python-publish.yml` for Melder.

## Files / Paths Impacted
- `.github/workflows/python-publish.yml`
- `context_compass/attention_board.md`
- This task.

## Validation
- YAML structure and workflow semantic assertions: pass.
- Embedded Python syntax: pass (two heredocs).
- Real wheel/sdist verifier rehearsal: pass.
- Isolated installed-wheel runtime/document smoke: pass.
- Build-asset check and diff hygiene: pass.

## Risks / Rollback Notes
- A mismatched GitHub environment name breaks PyPI OIDC after all earlier jobs pass.
- A release workflow not present on GitHub's default branch may not receive release events.
- The prod gate intentionally rejects releases for tags not pointing at current prod HEAD.

## Applicable Anti-Patterns
- [x] No publishing on every prod push.
- [x] No API-token fallback unless explicitly requested.
- [x] No ContextCompass-specific wheel assertions.
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from UNKNOWN or HYPOTHESIS.
- [ ] No closure without acceptance confirmation and board sync.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverable produced
- [x] Validation status recorded
- [x] Unknown-first discipline followed
- [x] Notes quality maintained
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - GitHub Actions publication safety
  - PyPI trusted publishing
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: workflow decisions, validation evidence, and one-step continuation.
- Keep notes append-only and evidence-backed.

## Notes
- DATETIME: 2026-08-30T16:04:06Z
  TYPE: MEASURE
  CLAIM: Generated rehearsal and egg-info directories were removed. Final diff
    hygiene passes, and the upgraded workflow is the only product-facing change.
    The previously staged empty workflow entry must be replaced with this validated
    346-line version before commit.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-346`
  IMPACT: The repository is ready for an exact workflow/tracking commit with no
    generated validation residue.
  NEXT: Stage the validated workflow plus its task/board route and create one local
    commit; do not publish or push.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T16:02:24Z
  TYPE: MEASURE
  CLAIM: Real local rehearsal passes. The embedded verifier accepts a fresh
    599-file wheel and 603-file sdist at version 0.1.2, proving bounded contents,
    required assets, metadata, and source/asset version agreement. An isolated
    wheel install verifies all four system documents and the 1,224-node,
    1,452-edge graph surface.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:111-327`
  IMPACT: The complex release-build assertions execute successfully rather than
    merely compiling. No upload or external publication occurred.
  NEXT: Remove only generated rehearsal/egg-info directories, then inspect the
    final diff and move the task to review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T16:00:41Z
  TYPE: MEASURE
  CLAIM: Structural validation passes: YAML parses with the exact two triggers
    and five-job dependency graph; the 3.14/3.14t cross-platform matrix, action
    majors, OIDC-only publish contract, prod gate, and required checks are all
    present. Both embedded Python heredocs compile, all build assets are current,
    and diff hygiene passes.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-346`
  IMPACT: Workflow structure and embedded code syntax are valid. Runtime archive
    assertions still need execution against a real local build.
  NEXT: Build wheel/sdist locally and execute the workflow's distribution verifier
    and installed-wheel smoke logic against them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-08-30T15:58:44Z
  TYPE: BLOCKER
  CLAIM: The tailored workflow is implemented, and the first diff check finds
    only one formatting defect: an extra blank line at end of file. No semantic
    validation has run yet.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:347-347`
  IMPACT: Remove the trailing blank line before parsing and semantic checks.
  NEXT: Fix EOF formatting, then validate YAML structure and workflow contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-08-30T15:55:48Z
  TYPE: DECISION
  CLAIM: Keep release/manual triggers and OIDC-only publishing, but add an exact
    current-prod commit gate; test 3.14 and 3.14t on Linux/Windows; validate Melder
    build assets, distributions, version agreement, and installed-wheel behavior.
  EVIDENCE:
  - `.github/workflows/python-publish.yml:1-54`
  - `pyproject.toml:1-246`
  IMPACT: The upgraded workflow will refuse non-prod releases and prevent a green
    build from publishing incomplete or internally inconsistent archives.
  NEXT: Replace the workflow in one scoped edit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
The tailored workflow is implemented and locally rehearsed. It publishes only when
the event commit equals current prod HEAD, tests CPython 3.14 and 3.14t on Linux and
Windows, verifies Melder distributions/assets/versions, installs the wheel, and uses
OIDC-only PyPI publication. GitHub's default branch must contain this workflow, and
the existing `pypi` environment name must match Melder's PyPI trusted publisher.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
