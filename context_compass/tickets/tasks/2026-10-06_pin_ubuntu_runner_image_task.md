# Task: Pin CI's Linux runners to ubuntu-24.04 before ubuntu-latest moves to Ubuntu 26.04

## Metadata
- Task ID: TASK-2026-10-06-pin_ubuntu_runner_image
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-06T10:38:56Z
- Updated: 2026-10-06T10:43:14Z

## Objective
Keep CI on the Linux image it runs today. GitHub moves the ubuntu-latest label from Ubuntu 24.04 to Ubuntu
26.04 between 2026-10-19 and 2026-11-19; every Linux job here, the Linux runtime cells included, would follow it
silently. Pin ubuntu-24.04 everywhere, so moving to Ubuntu 26.04 becomes a deliberate change, like adding a Python
manifest.

## Ticket Contract
- ENTRY_GATE: The owner's report of the GitHub annotation on every Linux job (chat, 2026-10-06): "The
  ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026", with "fix this now if its a thing for
  us". Active board row: ubuntu_runner_pin.
- EXECUTION_BOUNDARY: every `runs-on: ubuntu-latest` under .github/workflows/, RuntimeMatrixPolicy.TARGETS in
  .github/scripts/python_runtime_matrix.py, tests/unit/github_workflows (matrix tests and one contract test), the
  CI guide, BRANCH_WORKFLOW.md and tests_architecture's matrix line. Windows and macOS labels stay as they are.
  History (artifacts, completed tickets) is not edited. No src/ change.
- DEPENDENCIES: none.
- EXIT_GATE: no workflow names ubuntu-latest; the Linux matrix target is ubuntu-24.04; tests/unit/github_workflows
  passes with the new contract red first; docs current; assets and llm_support rebuilt last; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST if a Linux job needs a newer image than 24.04.

## Scope Boundaries
- In scope: Linux runner labels in workflows and the runtime matrix, their tests and documentation.
- Out of scope: moving to Ubuntu 26.04; Windows and macOS labels; the speed tests (already ubuntu-24.04).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-06T10:43:14Z) every Linux job and the matrix's Linux target pinned to ubuntu-24.04 under a
  contract test; 513 passed, mutations caught, docs, assets and llm_support current (Notes 3-4).
- previous: draft -> in_progress (2026-10-06T10:38:56Z) the owner asked for the fix if it applies here; it does
  (Notes 1-2).

## Steps / Checklist
- [x] Check what the move changes for this repository (Note 1) and decide (Note 2).
- [x] Tests first and red; pin the labels; green; mutations (Note 3).
- [x] CI guide, branch guide, tests_architecture; C1 extents (Note 3).
- [x] Rebuild assets and llm_support last (Note 4).
- [ ] Owner: commit, push, accept or redirect.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Every Linux job on ubuntu-24.04, a contract test that refuses ubuntu-latest, and the docs saying why.

## Files / Paths Impacted
- .github/workflows/*.yml (nine files), .github/scripts/python_runtime_matrix.py
- tests/unit/github_workflows/test_python_runtime_matrix.py, test_workflow_contracts.py
- .github/ci_cd/workflows.md, extending.md, .github/BRANCH_WORKFLOW.md
- context_compass/system_docs/tests_architecture.md, tests_components.md and their indexes

## Validation
- 2026-10-06 10:38-10:45Z, device VM, CPython 3.14.7t (Notes 3-4): tests red first (6 failed, 507 passed), then
  tests/unit/github_workflows 513 passed; two mutations caught and restored byte for byte; both tests indexes
  --check OK; build assets rebuilt and --check OK; llm_support rebuilt, --check --include-untracked and the
  tracked-only --check OK.
- Not run: a hosted run on the pinned labels (the next push).

## Risks / Rollback Notes
- Risk: GitHub retires the ubuntu-24.04 image one day; moving off it is then a deliberate, tested change.
- Rollback: restore the label from git.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: not applicable (no artifacts planned)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-10-06T10:38:56Z
  TYPE: FACT
  CLAIM: It applies here. actions/runner-images issue 14748: ubuntu-latest moves from Ubuntu 24.04.5 to 26.04.1
    between 2026-10-19 and 2026-11-19, and "Switch back to Ubuntu 24.04 by specifying the ubuntu-24.04 label".
    This repository names ubuntu-latest in 16 runs-on lines across nine workflows and as the Linux runner of the
    runtime matrix (RuntimeMatrixPolicy.TARGETS), so the 9 Linux test cells, the RC's Linux install probes and
    every helper job would change OS without a commit. setup-python's Linux builds are made per Ubuntu release
    (actions/python-versions lists 22.04, 24.04 and 26.04 files for 3.15.0 betas); whether every exact
    free-threaded release from 3.14.0 to 3.14.8 has a 26.04 build is UNKNOWN (the manifest is too large to read
    here), so a moved label could fail cells that pass today. The speed tests already pin ubuntu-24.04.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:33-37
  - .github/workflows/ci.yml:22-22
  - .github/workflows/test-runtime.yml:17-17
  - .github/workflows/release-candidate.yml:20-20
  IMPACT: Unpinned, CI changes its Linux image on GitHub's schedule; pinned, nothing moves until a commit says so.
  NEXT: Record the decision.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T10:38:56Z
  TYPE: DECISION
  CLAIM: Pin ubuntu-24.04 (today's ubuntu-latest) in every workflow and the runtime matrix; Windows and macOS keep
    their labels (no move announced). This follows the owner's request ("fix this now if its a thing for us") and
    the CI rule that nothing floats: CI already names its Python releases and pins its helper Python; a moving
    OS label is the same kind of float. A contract test refuses ubuntu-latest anywhere. Moving to 26.04 later is a
    deliberate change, tested like a new Python manifest.
  EVIDENCE:
  - context_compass/special_instructions/ci_cd_guide.md:19-20
  - .github/scripts/python_runtime_matrix.py:33-37
  IMPACT: Small, mechanical change across nine workflows, the matrix, tests and docs.
  NEXT: Write the tests first and run them red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-06T10:40:52Z
  TYPE: MEASURE
  CLAIM: Implemented and proven (device VM, CPython 3.14.7t). Tests first: test_python_runtime_matrix's eleven
    runner labels now say ubuntu-24.04 and the new contract test_linux_jobs_pin_ubuntu_24_04 searches every
    parsed workflow for ubuntu-latest and requires the matrix's Linux target to be ubuntu-24.04; red first (6
    failed, 507 passed). Then the 16 `runs-on: ubuntu-latest` lines in nine workflows and RuntimeMatrixPolicy.TARGETS
    say ubuntu-24.04 (byte replace, line endings unchanged): tests/unit/github_workflows 513 passed. Two
    mutations caught and restored byte for byte (a helper job back on ubuntu-latest; the matrix target back).
    Docs: the CI guide's extending rules (why, and how to move deliberately) and workflows page, the branch
    guide's runtime-tests contract, tests_architecture's matrix line; C1 extent test_workflow_contracts 884; both
    tests indexes regenerated and --check OK. Correction to Note 1: 16 runs-on lines in nine workflows (it said
    18 in ten).
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:33-37
  - tests/unit/github_workflows/test_workflow_contracts.py:364-386
  - .github/ci_cd/extending.md:19-22
  - .github/BRANCH_WORKFLOW.md:39-41
  IMPACT: No Linux job changes OS when the label moves; any return of ubuntu-latest fails the workflow tests.
  NEXT: Rebuild the build assets and llm_support last and run their checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T10:43:14Z
  TYPE: MEASURE
  CLAIM: Rebuilt last. The build-asset runner exited 0 in 51 s (agent documentation 462, bind guard 622, system
    documents 4, v0.2.8227) and its --check prints only OK lines; llm_support --include-untracked rewrote tests
    (1063 files) and other (402), src unchanged; --check --include-untracked and the tracked-only --check print
    only OK lines. No .git/index.lock. No src/ change, no notch, no release-note entry.
  EVIDENCE: .github/scripts/python_runtime_matrix.py:33-37
  IMPACT: Ready for the owner's commit together with the other open CI lanes.
  NEXT: Owner: commit and push; the Linux jobs run on ubuntu-24.04 from that run; accept or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Review (Notes 1-4): ubuntu-latest moves to Ubuntu 26.04 from 2026-10-19. Every Linux job (16 runs-on lines in nine
workflows) and the runtime matrix's Linux target now name ubuntu-24.04, and a contract test refuses ubuntu-latest
in any parsed workflow; the CI guide says why and how to move deliberately. 513 passed, mutations caught, docs,
assets and llm_support current. Owner-owed: commit, push, acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
