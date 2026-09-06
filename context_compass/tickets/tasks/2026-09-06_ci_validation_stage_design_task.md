# Task: Agree which branch stages need full runtime qualification

## Metadata
- Task ID: TASK-2026-09-06-ci-validation-stage-design
- Story: none (owner-requested CI policy discussion)
- Status: in_progress
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-06T01:04:31Z
- Updated: 2026-09-06T01:04:31Z

## Objective
Agree a test policy that avoids repeating the full runtime matrix for unchanged promotions while
preserving useful dev feedback, preprod qualification and the owner's careful final release check.

## Ticket Contract
- ENTRY_GATE: Existing certification, this active route and the owner's request to discuss the policy.
- EXECUTION_BOUNDARY: Read-only workflow analysis, discussion and this task's coordination records.
  No workflow, test, ruleset or publication edits during this design discussion.
- DEPENDENCIES: Accepted candidate workflow task under tasks/completed and current GitHub workflow files.
- EXIT_GATE: Owner agrees the full-suite stages, lighter promotion checks and qualification-reuse rule.
- FAILURE_ESCALATION: Do not treat a branch name or an unrelated green run as proof for changed contents.
  Keep actual release publication and all commit/push/signing activity under owner control.

## Scope Boundaries
- In scope: runtime suite frequency and the distinct purpose of each promotion stage.
- Out of scope: runtime fixes, new deployment services, branch renames and trigger changes not agreed.
- Owner clarified that feature pushes are not the concern; discussion concerns full suites at each stage.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Owner asks to reconsider repeated full tests after preprod and explicitly wants discussion.

## Current Behavior
- CI handles PRs to dev, preprod, release_candidate and prod, plus pushes to dev/preprod/prod.
- Each such CI run calls the complete unit/component/integration matrix on Linux, Windows and macOS.
- RC branch pushes already use package build, TestPyPI upload and isolated consumer probes only.
- Final publication invokes a fresh full runtime matrix before building/publishing.
- A simple feature-PR-to-final-release route can therefore launch eight full matrices, before revisions/reruns.

## Proposed Stage Policy (Not Yet Accepted)
| Stage | Full runtime suite | Purpose |
| --- | --- | --- |
| Feature PR into dev | yes | Catch defects before integration |
| dev PR into preprod | yes | Qualify the integrated candidate and its package |
| preprod into release_candidate | no for already-qualified contents | Verify provenance, build and test the installed TestPyPI package |
| release_candidate into prod | no for already-qualified contents | Require the selected candidate, matching tree and final version |
| Final PyPI publication | yes | Preserve the owner's fresh final safety check |
| Post-merge pushes | no duplicate for an already-tested merge result | Keep necessary lightweight branch/publication checks |

Qualification reuse must bind to the actual tested contents and relevant test/build inputs.
Changed code, dependencies or qualification configuration needs another full pass. This is a proposed
three-full-matrix policy, not an implemented skip or an assertion that current proof checks cover all stages.

## Steps / Checklist
- [x] Read the current CI/runtime/candidate/publisher wiring.
- [x] Separate PR triggers from the repetition of full test execution.
- [ ] Agree the stage policy and the exact evidence needed for promotion.
- [ ] Only then specify the bounded implementation and regression checks.

## Deliverables
- Agreed stage-to-check mapping and an explicit rule for invalidating prior qualification.

## Validation
- Workflow/source inspection only. No tests or hosted runs executed for this discussion.
- No source/workflow implementation changes made.

## Risks / Open Questions
- How will later promotions prove their contents were covered by the full preprod run?
- Existing aggregation rejects skipped required tests; a future change must update that contract explicitly.
- The final full-suite run is retained in this proposal because the owner previously requested a careful
  final check. Any different final-release policy needs an explicit design decision.

## Artifact Links
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none.

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

## Context / Handoff Summary
Discussion only. Owner is satisfied that feature activity is PR-triggered; the question is excessive
full-suite repetition. Proposed full runs at feature-to-dev, dev-to-preprod and actual final publication;
lighter RC/prod promotions and no duplicate post-merge suites for already-qualified contents.
No policy is accepted yet and no workflow implementation has changed.
