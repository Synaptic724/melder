# Task: Implement full qualification at selected branch stages

## Metadata
- Task ID: TASK-2026-09-06-ci-validation-stage-design
- Story: none (owner-approved CI stage implementation)
- Status: in_progress
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-06T01:04:31Z
- Updated: 2026-09-06T09:52:00Z

## Objective
Implement the agreed test policy without repeating the full runtime matrix for unchanged promotions while
preserving useful dev feedback, preprod qualification and the owner's careful final release check.

## Ticket Contract
- ENTRY_GATE: Existing certification, owner implementation approval, active route and consumed patch contracts.
- EXECUTION_BOUNDARY: CI/candidate/source-proof workflows, standalone CI policy/qualification helpers,
  focused workflow tests, branch guide, derived tests/other corpora and this task's records.
- DEPENDENCIES: Accepted candidate workflow task under tasks/completed and current GitHub workflow files.
- EXIT_GATE: Stage-specific execution and exact-tree proof are implemented, negative paths and workflow
  wiring pass local checks, and owner rollout requirements are explicit.
- FAILURE_ESCALATION: Do not treat a branch name or an unrelated green run as proof for changed contents.
  Keep actual release publication and all commit/push/signing activity under owner control.

## Scope Boundaries
- In scope: runtime suite frequency, source qualification records and safe light promotion checks.
- Out of scope: runtime fixes, new deployment services, branch renames, commits, pushes and publication.
- Owner clarified that feature pushes are not the concern; discussion concerns full suites at each stage.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner approved implementing the proposed policy in the workflows and asked to
  continue after interrupting the initial analysis. No implementation was made in that interrupted turn.

## Current Behavior
- CI handles PRs to dev, preprod, release_candidate and prod, plus pushes to dev/preprod/prod.
- Each such CI run calls the complete unit/component/integration matrix on Linux, Windows and macOS.
- RC branch pushes already use package build, TestPyPI upload and isolated consumer probes only.
- Final publication invokes a fresh full runtime matrix before building/publishing.
- A simple feature-PR-to-final-release route can therefore launch eight full matrices, before revisions/reruns.

## Accepted Stage Policy
| Stage | Full runtime suite | Purpose |
| --- | --- | --- |
| Feature PR into dev | yes | Catch defects before integration |
| dev PR into preprod | yes | Qualify the integrated candidate and its package |
| preprod into release_candidate | no for already-qualified contents | Verify provenance, build and test the installed TestPyPI package |
| release_candidate into prod | no for already-qualified contents | Require the selected candidate, matching tree and final version |
| Final PyPI publication | yes | Preserve the owner's fresh final safety check |
| Post-merge pushes | no duplicate for an already-tested merge result | Keep necessary lightweight branch/publication checks |

Qualification reuse must bind to the actual tested contents and relevant test/build inputs.
Changed code, dependencies or qualification configuration needs another full pass. Full validation also
runs for release-fix PRs and explicit manual CI. Automatic permanent-branch CI push triggers are removed;
PR checks, RC push qualification and final publication remain the authoritative boundaries.

## Steps / Checklist
- [x] Read the current CI/runtime/candidate/publisher wiring.
- [x] Separate PR triggers from the repetition of full test execution.
- [x] Agree the stage policy and the exact evidence needed for promotion.
- [ ] Implement stage flags, strict aggregation and full-run source qualification records.
- [ ] Verify provenance before RC admission and retain exact-source checks before prod/publication.
- [ ] Validate negative paths, regenerate assets and document rollout.

## Deliverables
- Implemented stage-to-check mapping, exact-tree proof and operator guidance for fresh qualification.

## Validation
- Workflow/source inspection only. No tests or hosted runs executed for this discussion.
- No source/workflow implementation changes made.

## Risks / Open Questions
- How will later promotions prove their contents were covered by the full preprod run?
- Existing aggregation rejects skipped required tests; a future change must update that contract explicitly.
- The final full-suite run is retained in this proposal because the owner previously requested a careful
  final check. Any different final-release policy needs an explicit design decision.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/architecture_patch.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/component_patch_ci_profiles.md
  - system_docs/patches/active/ci_stage_qualification_2026_09_06/code_description_patch_source_proof.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: Promote durable behavior to .github/BRANCH_WORKFLOW.md at accepted closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record agreed policy and unresolved decisions without prematurely editing the running workflows.

## Notes
- DATETIME: 2026-09-06T01:04:31Z
  TYPE: FACT
  CLAIM: CI always calls test-runtime for the four PR destinations and three permanent-branch push
    triggers. That reusable workflow runs all three tiers on all three platforms. RC pushes alone
    are already package-only; the extra runtime runs occur in promotion PR CI and branch-push CI.
    Owner clarified that PR triggers themselves are fine and asks to discuss suite frequency.
  EVIDENCE:
  - .github/workflows/ci.yml:6-15
  - .github/workflows/ci.yml:55-65
  - .github/workflows/test-runtime.yml:12-36
  - .github/scripts/run_runtime_tests.py:19-40
  - .github/workflows/release-candidate.yml:28-34
  - .github/workflows/python-publish.yml:63-74
  IMPACT: Reduce repeated full qualification rather than misdiagnosing a feature-push trigger.
  NEXT: Discuss full suites at dev, preprod and final publication, with lighter exact-content promotions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T09:52:00Z
  TYPE: DECISION
  CLAIM: Owner approved the three-checkpoint policy and asked to continue implementation. Use a
    tiny full-CI qualification artifact binding run/attempt, event/PR identity and actual checkout
    tree. A source-proof reusable workflow selects verified full CI, downloads through the official
    action and checks the record. Light preprod-to-RC PRs and RC push admission require this proof.
    Release-fix/manual CI remain full; prod consumes exact successful RC evidence.
  EVIDENCE:
  - Owner instructions: "ok go ahead and update this stuff, properly in the workflows"; "ok continue".
  - .github/workflows/ci.yml:6-103
  - .github/scripts/ci_policy.py:89-110
  - .github/scripts/check_candidate_run.py:54-123
  IMPACT: Removing full jobs alone would break strict aggregation and lose qualification. Update
    profiles and aggregation together. Remove duplicate CI push triggers; keep the existing final
    publication matrix. Add bounded waiting only for legitimately pending RC evidence so a fast
    prod PR does not recreate the earlier timing race. Owner retains all commits/pushes/publication.
  NEXT: Consume the patch contracts and verify GitHub artifact/PR association interfaces before edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:01:16Z
  TYPE: FACT
  CLAIM: Stage flags/strict aggregation, bounded pending-RC waiting, full-source JSON records and
    the read-only source-verification workflow are implemented. RC build/publish now depend on
    source proof; full CI alone records qualification. Official download-artifact v8 supports a
    specific immutable artifact ID with run-id/repository/token, so no custom archive downloader
    or credential-forwarding redirect handler is needed. Scoped correctness Ruff passes.
  EVIDENCE:
  - .github/scripts/ci_policy.py
  - .github/scripts/ci_qualification.py
  - .github/scripts/check_candidate_run.py
  - .github/workflows/verify-source-qualification.yml
  - https://raw.githubusercontent.com/actions/download-artifact/v8/README.md
  IMPACT: Implementation is not yet qualified. Verify actual merged-PR API shape, then test all
    profiles, record identity, failed/expired evidence, changed attempts and bounded wait behavior.
  NEXT: Validate source-selection API assumptions and update focused regression coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-06T10:03:32Z
  TYPE: FACT
  CLAIM: Actual GitHub data confirms preprod commit a4de3adc maps to merged PR 137 with expected
    head/base merge parents. Its successful CI run 33986010784 attempt 2 has pull_requests=[] after
    closure. Therefore run.pull_requests cannot be required to identify a historical full run.
    Select the latest exact head/ref/event run and require its downloaded record to prove the
    original PR number, base/head IDs and tree; mismatched records refuse rather than falling back.
  EVIDENCE:
  - https://api.github.com/repos/Synaptic724/melder/commits/a4de3adc1cbcab4a58486b1d5ee68d41e3f01dbf/pulls
  - https://github.com/Synaptic724/melder/actions/runs/33986010784
  IMPACT: Fix this real API assumption before validation; the record provides event identity that
    GitHub's historical run association omits. Ambiguous/mismatched history needs fresh manual CI.
  NEXT: Update selection and regression cases for empty historical PR associations.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Implementation approved. Current checkout f10b63f61 has no new implementation diff from the interrupted
turn; the old scratch .gitignore deletion is existing cleanup. Implement profiles plus trusted full-CI
tree records, lightweight RC/prod gates and no duplicate push CI, with release-fix/manual full checks.
Use official artifact download across runs; retain final publication tests and bounded pending-RC wait.
