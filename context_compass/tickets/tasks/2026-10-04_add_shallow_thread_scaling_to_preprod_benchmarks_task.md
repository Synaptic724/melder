# Task: Run the shallow thread-scaling benchmark in the dev-to-preprod benchmark CI

## Metadata
- Task ID: TASK-2026-10-04-add_shallow_thread_scaling_to_preprod_benchmarks
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-04T11:52:50Z
- Updated: 2026-10-04T12:52:00Z

## Objective
Add benchmarks/testing_other_di/test_shallow_all_thread_scaling.py to the benchmarks that run when a
dev-to-preprod pull request is pushed, beside real-world-gauntlet and persistent-runtime-gauntlet,
and fix the extra 'l' in its file name (on disk it is test_shallow_all_thread_scalling.py today).

## Ticket Contract
- ENTRY_GATE: Scope approved by the owner's chat directives of 2026-10-04 (add the benchmark to the
  dev-to-preprod benchmarks, fix the extra l, finish the work now). Active board row:
  shallow_thread_scaling_ci.
- EXECUTION_BOUNDARY: .github/workflows/ci.yml, the new
  .github/workflows/shallow-all-thread-scaling.yml, .github/scripts/ci_policy.py (GAUNTLET_JOBS and
  its docstring), .github/BRANCH_WORKFLOW.md, the three tests/unit/github_workflows files that
  hard-code the gauntlet job lists, the rename of the benchmark file, and the generated llm_support
  bundles. No src/ change, no version notch, no commit, push or PR.
- DEPENDENCIES: Precedents: tickets/tasks/completed/2026-10-03_real_world_gauntlet_ci_task.md and
  the persistent gauntlet series. Other lanes also rebuild the generated bundles, so the rebuild
  runs last.
- EXIT_GATE: Workflow, ci.yml, ci_policy.py, tests and branch guide agree; the YAML parses and the
  inline Python compiles; the contract tests run or are reported Not run; bundles regenerated or the
  blocker recorded; the owner accepts.
- FAILURE_ESCALATION: Record BLOCKER if the device shell, a Python 3.14 environment or a builder
  fails, or if the shared tree is mid-change when the bundles are rebuilt.

## Scope Boundaries
- In scope: rename the benchmark file; one reusable workflow (three OSes, one fresh GIL-off pytest
  process per library); the ci.yml job and its merge-ready dependency; the CIPolicy.GAUNTLET_JOBS
  entry; the test and branch-guide updates.
- Out of scope: the hosted three-OS run (the owner's), benchmark logic changes, src/ changes,
  commits, pushes, PRs.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T12:52:00Z) implementation and validation are complete (Notes 7-9); the owner's
  acceptance, staging of the rename and the hosted three-OS run remain.
- previous: draft -> in_progress (2026-10-04T11:58:17Z), on the owner's chat directives of 2026-10-04.

## Steps / Checklist
- [x] Investigate the CI wiring, the benchmark's output contract and the isolation evidence (Notes 1-3).
- [x] Rename the benchmark file with mv -n on the device (no git mv, no git add).
- [x] Add .github/workflows/shallow-all-thread-scaling.yml.
- [x] Add the ci.yml job and its merge-ready dependency; add the job to CIPolicy.GAUNTLET_JOBS.
- [x] Update the three workflow test files and add contract tests for the new workflow.
- [x] Update .github/BRANCH_WORKFLOW.md.
- [x] Validate and report only what actually ran.
- [x] Regenerate the llm_support bundles last, then run their --check.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Renamed benchmark file; new reusable workflow; ci.yml job; GAUNTLET_JOBS entry; updated tests;
  updated branch guide; regenerated bundles; honest validation report.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_shallow_all_thread_scalling.py
  (renamed to test_shallow_all_thread_scaling.py)
- .github/workflows/shallow-all-thread-scaling.yml (new)
- .github/workflows/ci.yml
- .github/scripts/ci_policy.py
- .github/BRANCH_WORKFLOW.md
- tests/unit/github_workflows/test_ci_policy.py
- tests/unit/github_workflows/test_source_qualification.py
- tests/unit/github_workflows/test_workflow_contracts.py
- llm_support/ generated bundles (rebuilt, never hand-edited)

## Validation
- 2026-10-04 12:50-12:51Z, device VM, uv CPython 3.14.7 free-threaded, pytest 9.1.1, PyYAML 6.0.3:
  - python -m pytest tests/unit/github_workflows -q -p no:cacheprovider: 475 passed (Note 8).
  - python llm_support/_builder.py --include-untracked: UNCHANGED src, tests, other, manifest.json.
  - python llm_support/_builder.py --check --include-untracked: OK src, tests, other (Note 9).
- Not run: the owner's .venv314t run on Windows; the hosted three-OS workflow run (owner);
  python src/melder/_build_assets/_build_asset_runner.py --check (no src/ change).

## Risks / Rollback Notes
- Risk: the workflow cannot be run here; only the owner's hosted three-OS run proves it. Mitigation:
  mirror the two existing benchmark workflows, read the benchmark's own configuration, and validate
  the printed results per library.
- Rollback: delete the workflow and the ci.yml job, and restore GAUNTLET_JOBS and the tests.

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
- DATETIME: 2026-10-04T11:58:17Z
  TYPE: FACT
  CLAIM: Adding a dev-to-preprod benchmark touches six coupled places: the ci.yml job, the
    merge-ready needs list, CIPolicy.GAUNTLET_JOBS, the hard-coded job lists in three workflow test
    files, the branch guide, and the generated bundles. A contract test requires merge-ready needs
    to equal REQUIRED_JOBS plus packages, so ci.yml and ci_policy.py must change together.
  EVIDENCE:
  - .github/workflows/ci.yml:73-81
  - .github/workflows/ci.yml:104-106
  - .github/scripts/ci_policy.py:23-26
  - .github/scripts/ci_policy.py:135-148
  - tests/unit/github_workflows/test_workflow_contracts.py:36-36
  - tests/unit/github_workflows/test_ci_policy.py:15-15
  - tests/unit/github_workflows/test_source_qualification.py:101-101
  IMPACT: Missing any one of them fails CI / merge-ready or a contract test, so the change is one
    coordinated edit.
  NEXT: Record the benchmark's output contract and the isolation evidence.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:58:17Z
  TYPE: FACT
  CLAIM: The benchmark prints one config line and one result line per thread count. It reports
    gil=<status> but never asserts it, accepts thread counts 1 to 5 through DI_THREAD_COUNTS and the
    per-count duration through DI_DURATION_S, and picks libraries through DI_LIBS. A failed worker
    is re-raised, so a result line with errors above zero never prints.
  EVIDENCE:
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:81-81
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:93-93
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:110-113
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:140-147
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:284-284
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:328-329
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:348-356
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:366-366
  - benchmarks/testing_other_di/test_shallow_all_thread_scalling.py:373-380
  - benchmarks/testing_other_di/test_shallow_all.py:651-658
  IMPACT: The workflow must verify gil=disabled, the thread list, steps above zero and errors equal
    to zero from the printed lines; a format change in the benchmark needs a workflow change.
  NEXT: Check the isolation evidence for how many processes to use.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:58:17Z
  TYPE: FACT
  CLAIM: On free-threaded 3.14 a library measured second or third in one process was 5-12% slower
    than when it ran first. The real-world gauntlet already answers this with one fresh process per
    library.
  EVIDENCE:
  - benchmarks/testing_other_di/benchmarks.md:142-152
  IMPACT: The new workflow gives each library its own GIL-off pytest process through DI_LIBS.
  NEXT: Record the approval basis and the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:58:17Z
  TYPE: DECISION
  CLAIM: The owner's chat directives of 2026-10-04 are the confirmation to implement: add the
    scaling benchmark to the dev-to-preprod benchmarks, fix the extra l in its name, and 'finish
    your work, add the workflows'. Defaults told to the owner in chat: one fresh GIL-off process per
    library, 15 s per thread count over threads 1 to 5 (about 225 s of measured work per OS).
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md:13-16
  - context_compass/tickets/tasks/2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md:43-48
  IMPACT: Propose, confirm, implement is satisfied by the explicit directive; the choices above are
    not reopened.
  NEXT: Write the plan note, then rename the benchmark file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T11:58:17Z
  TYPE: PLAN
  CLAIM: Order: rename with mv -n; write shallow-all-thread-scaling.yml (job scaling, three OSes,
    GIL-off, one process per library, per-library validation of the printed lines); add the ci.yml
    job and its merge-ready dependency; add the name to GAUNTLET_JOBS and the docstring; update the
    three test files and add contract tests; update the branch guide; validate; rebuild the bundles
    last.
  EVIDENCE:
  - .github/workflows/real-world-gauntlet.yml:1-216
  - .github/workflows/persistent-runtime-gauntlet.yml:1-171
  - .github/workflows/ci.yml:73-81
  - .github/BRANCH_WORKFLOW.md:14-14
  - .github/BRANCH_WORKFLOW.md:90-95
  IMPACT: Mirrors contracts that already have tests, so the diff stays small and reviewable.
  NEXT: Rename the benchmark file and verify it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T12:49:23Z
  TYPE: FACT
  CLAIM: The owner's pasted run of tests/unit/github_workflows (chat, 2026-10-04) failed about 87
    tests, nearly all with "Incomplete CI dependency evidence: missing=['shallow-all-thread-scaling'];
    unexpected=[]". require_success compares the reported job set with REQUIRED_JOBS plus packages
    before it judges any result, and REQUIRED_JOBS takes the new job from GAUNTLET_JOBS, so every
    test whose result map lacks that job fails exactly this way.
  EVIDENCE:
  - .github/scripts/ci_policy.py:23-28
  - .github/scripts/ci_policy.py:128-155
  IMPACT: Test fixtures lag the policy (a test mismatch), not a policy defect: the fix belongs in
    the tests' job lists, never in require_success.
  NEXT: Record when the edits landed against that failure mode, then rerun the suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T12:49:23Z
  TYPE: FACT
  CLAIM: The implementation landed at 12:02-12:05Z, before its note (recorded late): the benchmark
    renamed with mv -n (same 380 lines, so Note 2's line numbers hold under the new name); the new
    shallow-all-thread-scaling.yml (12:02:01Z); the ci.yml job, its merge-ready dependency and the
    GAUNTLET_JOBS entry (12:02:21Z); the job in the three test files (5, 3 and 7 occurrences) plus
    two contract tests for the new workflow (12:05:18Z); the branch-guide section (12:05:34Z).
  EVIDENCE:
  - .github/scripts/ci_policy.py:23-25
  - tests/unit/github_workflows/test_ci_policy.py:12-16
  IMPACT: The policy demanded the job about three minutes before the tests listed it, and a run in
    that window fails exactly as the owner's did. The current result maps list the job, so the
    owner's run most likely predates 12:05:18Z (HYPOTHESIS until the rerun settles it).
  NEXT: Rerun tests/unit/github_workflows against the current files and record the result.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T12:50:20Z
  TYPE: MEASURE
  CLAIM: python -m pytest tests/unit/github_workflows -q -p no:cacheprovider on the current files:
    475 passed in 2.76s, no failures (device VM, uv-installed CPython 3.14.7 free-threaded build,
    pytest 9.1.1, PyYAML 6.0.3, bytecode writes off). The owner's failing run therefore predates the
    12:05:18Z test edits; the Note 7 hypothesis holds and no test needed another change.
  EVIDENCE:
  - tests/unit/github_workflows/test_ci_policy.py:12-16
  - .github/scripts/ci_policy.py:128-155
  IMPACT: The contract suite agrees with ci.yml and ci_policy.py. It is not the owner's .venv314t
    on Windows, and the hosted three-OS workflow run remains the owner's.
  NEXT: Rebuild the llm_support bundles with --include-untracked, then run the same --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T12:52:00Z
  TYPE: MEASURE
  CLAIM: python llm_support/_builder.py --include-untracked reported UNCHANGED for src, tests, other
    and manifest.json (exit 0), and the same command with --check printed only OK lines (exit 0).
    llm_support/manifest.json was last written at 12:14:41Z, after these edits, so another lane's
    rebuild had already folded them in; nothing under llm_support/ was rewritten by this pass.
  EVIDENCE: context_compass/tickets/tasks/2026-10-04_add_shallow_thread_scaling_to_preprod_benchmarks_task.md:80-86
  IMPACT: Every exit-gate item this agent owns is met; the owner's acceptance, staging of both sides
    of the rename plus the new workflow, and the hosted three-OS run remain.
  NEXT: Owner accepts or redirects; on acceptance, close the ticket and sync the board.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
- DATETIME: 2026-10-06T11:24:36Z
  TYPE: DECISION
  CLAIM: Superseded in part by the owner's 2026-10-06 ruling "Run, never block": the thread-scaling job still
    starts on every dev-to-preprod pull request with the two gauntlets, but from the new speed-tests.yml, not
    ci.yml; merge-ready no longer needs it and CIPolicy has no GAUNTLET_JOBS. The benchmark workflow itself only
    changed its header comment.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-06_make_speed_tests_nonblocking_task.md:235-266
  - .github/workflows/speed-tests.yml:1-52
  IMPACT: This ticket's "must succeed for merge-ready" outcome no longer holds; acceptance now covers the benchmark
    and its wiring through the Speed workflow.
  NEXT: Owner: accept or redirect both tickets together.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Done and validated on the device VM (Notes 7-9): benchmark renamed, reusable workflow, ci.yml job
and merge-ready dependency, GAUNTLET_JOBS entry, tests and branch guide; 475 workflow tests pass and
the llm_support check prints only OK lines. The owner's earlier failure predates the test edits.
Owner-owed: stage both sides of the rename and the new workflow, the hosted three-OS run, and
acceptance; closure waits for that confirmation.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
