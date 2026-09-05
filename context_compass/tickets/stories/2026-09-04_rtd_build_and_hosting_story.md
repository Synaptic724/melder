# Story: Make documentation builds, previews, versions, and downloads reproducible

## Metadata
- Story ID: STORY-2026-09-04-rtd-build-and-hosting
- Epic: EPIC-2026-09-04-readthedocs-documentation
- Epic Path: ../epics/2026-09-04_readthedocs_documentation_epic.md
- Status: blocked
- Owner: codex
- Agent Name: codex_2
- Priority: p1
- Created: 2026-09-04T21:36:46Z
- Updated: 2026-09-05T14:13:38Z

## User Narrative
As a maintainer, I can review a documentation change before release and publish consistent versions
and downloads using the same proven build inputs as local development.

## Value / MRP Alignment
Make publishing a repeatable release process with identifiable source/version inputs and useful reader features.

## Ticket Contract
- ENTRY_GATE: S1-S7 content/build contracts available; intended hosted project/repository identified; task routed.
- EXECUTION_BOUNDARY: .readthedocs.yaml, docs CI, dependency pins, offline builders, build/host integration,
  version/source/canonical links, redirects, and maintainer runbook.
- DEPENDENCIES: S1 local command; S2 catalog; S3-S7 content; account/repository access at hosting setup.
- EXIT_GATE: Local/CI/preview parity, versions/search/download behavior, and setup evidence are recorded.
- FAILURE_ESCALATION: Record unavailable account access, dependency/network issues, or unsupported features.

## Requirements (Functional)
- CI and RTD call the same docs assembly/build command and pinned dependency set as local development.
- Use supported Python 3.14 for docs; keep 3.14t example verification a separate job.
- Build warning-aware HTML and validate public input selection, links, artifacts, and package version.
- Configure the intended Git integration and PR previews; verify the preview and available visual diff.
- Provide version switching, accurate development/old-version notices, and consistent source-revision links.
- Use hosted search-as-you-type with a working local/offline Sphinx search route.
- Publish complete HTML download plus a clearly scoped four-level PDF/ePub handbook.
- Configure canonical URLs and verify sitemap/version links; maintain redirect mappings for moved pages.
- Document project settings, rebuild/release steps, pin refresh, and failed-build recovery.

## Requirements (Non-Functional)
- No docs dependencies in Melder runtime requirements; no generated-site writes into canonical source.
- No secret/working-record content in artifacts; account changes occur only within authorized setup scope.
- Build output/version must be traceable to a commit. Missing access remains UNKNOWN, not assumed configured.

## Scope Boundaries
- In scope: hosted/CI build integration and publishing features over the completed content system.
- Out of scope: runtime changes, paid-plan purchases, invented credentials, or retroactive tag modification.

## State Transition Event
- from_state: in_progress
- to_state: blocked
- transition_reason: Local pipeline, formats, and recovery procedure are verified; actual hosted
  setup/build verification is blocked on project identity/access.

## Dependencies / Related Work
S9 validates the complete release and owns final launch acceptance after this pipeline is demonstrated.

## Tasks (Implementation Checklist)
- [ ] [Implement docs CI parity, RTD configuration, and offline outputs](../tasks/2026-09-04_rtd_ci_and_offline_task.md)
- [ ] [Verify and configure the intended Read the Docs project](../tasks/2026-09-04_rtd_hosted_project_task.md)
- [ ] Align local/CI/RTD inputs and requirements; add the docs workflow and RTD configuration.
- [ ] Verify project ownership/repository/branch, Git integration, and a real PR preview.
- [ ] Implement/test version identity, search integration, source links, canonical URL, and redirects.
- [ ] Build/review offline formats and write the maintainer/recovery runbook.

## Acceptance Criteria
- [ ] Local and CI builds use the same command/configuration and a recorded compatible dependency set.
- [ ] A real hosted preview is built from the intended commit and can be reviewed before release.
- [ ] Version menu, notices, source links, canonical URL, and sitemap agree on the intended versions.
- [ ] Search works hosted and through the local/offline route.
- [ ] Downloads render correctly, disclose their contents/version, and preserve all four level names.
- [ ] Old-link redirects resolve correctly; unbuildable historical tags are not advertised as supported.
- [ ] Setup/release/recovery steps are reproducible and contain no credentials.

## Validation / Test Plan
Final local rendering passes at 294 pages and 35,499 links with exact lesson/helper bytes. All 36 docs
tests pass. The final 107-page PDF, 62-document ePub, 948-file HTML archive, and all-format staging
are verified. Local canonical/version simulation passes; actual hosted behavior remains unverified.

## UX / API / Data Notes
Recommended stable default starts with the first accepted docs-bearing release. latest tracks the selected
public branch. Confirm exact branch/project mapping before applying dashboard settings.

## Risks / Mitigations
RTD service settings and feature availability are external state. Core navigation must work without
optional paid analytics. Existing tags may lack docs configuration; support is an explicit release decision.

## Open Questions
Project ownership, chosen public branch, optional custom domain, compatible pins, and offline build costs.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/2026-09-04_readthedocs_site_blueprint.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Parent epic closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: CI/RTD parity, previews, releases, search, downloads
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-04T21:36:46Z
  TYPE: PLAN
  CLAIM: S8 owns the reproducible publication pipeline and supported RTD features after the content
    stories are complete. Local files cannot substitute for verification of actual hosted settings.
  EVIDENCE:
  - artifacts/2026-09-04_readthedocs_site_blueprint.md:226-292
  - https://docs.readthedocs.com/platform/stable/config-file/v2.html
  - https://docs.readthedocs.com/platform/stable/pull-requests.html
  IMPACT: Readers get coherent versions and downloads, while maintainers can review changes before launch.
  NEXT: Open the build/hosting implementation task after S1-S7 deliver their contracts and content.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T08:58:00Z
  TYPE: FACT
  CLAIM: CI/RTD parity and native handbook builders are implemented; source-link validation and final
    offline packaging remain in the active task. The owner is creating the Read the Docs project.
  EVIDENCE:
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md:46-66
  - Owner RTD website setup instruction on 2026-09-05.
  IMPACT: Local validation and owner account setup can progress independently; no hosted success is claimed.
  NEXT: Complete local format/link validation and obtain the project URL/branch from the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-05T09:41:40Z
  TYPE: FACT
  CLAIM: The CI/offline task reached review: fresh-reference regression fixed, normal HTML and all
    local formats/staging validated, source/repository assets current, and prominent README routes added.
  EVIDENCE:
  - artifacts/2026-09-05_rtd_local_build_validation.md:1-62
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md:1-71
  IMPACT: Local pipeline evidence is available for the owner-created RTD project. S8 cannot close until
    the actual hosted project, previews, versions, search, canonical links, and downloads are verified.
  NEXT: Confirm the owner's project URL and chosen docs-bearing branch/revision for hosted verification.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-05T14:13:38Z
  TYPE: FACT
  CLAIM: Final local pipeline work is in review, including PDF identifier wrapping, consistent
    highlighting, and published-regression recovery instructions. All output/asset proofs pass.
    Hosted verification remains blocked; simulation and staging are explicitly labeled local.
  EVIDENCE:
  - artifacts/2026-09-05_rtd_final_quality_audit.md
  - tickets/tasks/2026-09-04_rtd_ci_and_offline_task.md
  IMPACT: The remaining S8 boundary is actual project/build access and live feature verification.
  NEXT: Continue the hosted-project task after the owner supplies its URL/branch and read authorization.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Applicable Anti-Patterns
- [ ] No assumed account configuration, unsupported version claims, or mismatched build inputs.
- [ ] No deployment secrets committed with docs configuration.

## Closure Confirmation
- [ ] Pipeline/preview walkthrough accepted; tasks and board synchronized before final launch review.

## Noting Behavior
Record exact pins, build revisions, service settings without secrets, feature verification, and recovery steps.

## Context / Handoff Summary
CI/RTD configuration and handbook builders are implemented and locally validated; the CI/offline task
is in review. The owner is adding the RTD project. The project URL/branch and hosted behavior
remain to be verified. S9 still owns integrated launch acceptance; all commits/pushes remain owner-only.
Final local qualification is recorded in the S9 audit; source/lesson bytes are unchanged between
the tested 20123b8a and built 0e8e66e4 commits. Final docs presentation/runbook edits await owner commit.
