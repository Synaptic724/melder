# Task: Let the release candidate recover from a TestPyPI outage without a full rebuild

## Metadata
- Task ID: TASK-2026-10-06-recover_release_candidate_from_testpypi_outage
- Story: none (standalone task; owner report)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p1
- Created: 2026-10-06T09:37:20Z
- Updated: 2026-10-06T09:56:18Z

## Objective
Explain the owner's failed release-candidate run and, on the owner's approval, make it recoverable: a transient
TestPyPI error should not fail the candidate outright, and "Re-run failed jobs" should reuse the run's own build
instead of asking for an artifact that attempt never made. Until then the recovery is "Re-run all jobs".

## Ticket Contract
- ENTRY_GATE: The owner's hosted run 37443362134 of release-candidate.yml (chat, 2026-10-06): attempt 1 failed in
  prepare-upload with HTTP 503 from TestPyPI; attempt 2 ("Re-run failed jobs") failed to download
  candidate-dists-37443362134-2. Active board row: rc_testpypi_recovery.
- EXECUTION_BOUNDARY: approved by the owner (Note 4):
  .github/workflows/build-distributions.yml, release-candidate.yml and python-publish.yml,
  .github/scripts/testpypi_candidate.py, tests/unit/github_workflows, .github/ci_cd docs. No src/ change.
- DEPENDENCIES: none.
- EXIT_GATE: the owner's decision recorded; if approved, the new behaviour proven red then green,
  tests/unit/github_workflows passing, the CI guide updated, build assets and llm_support rebuilt last; the owner
  reruns and accepts or redirects.
- FAILURE_ESCALATION: DECISION_REQUEST before any change to how the candidate's evidence is produced or named.

## Scope Boundaries
- In scope: the release-candidate artifact naming across attempts, TestPyPI request retries, their tests and docs.
- Out of scope: TestPyPI's own availability; the candidate gates' rules (candidate-ready stays fail-closed);
  Codecov (codecov_upload_tls).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-06T09:56:18Z) both fixes implemented as the owner chose them (Note 6): the candidate's
  failed-jobs re-run reuses its build, publication refuses one by name, TestPyPI lookups ride out outages;
  512 passed, eight mutations caught, assets and llm_support current (Notes 8-9). A hosted run remains.
- previous: blocked -> in_progress (2026-10-06T09:45:54Z) the owner chose option 1, both fixes (Note 4), refined to
  "RC reuses, PyPI strict" once the release rule was shown (Notes 5-6).
- previous: in_progress -> blocked (2026-10-06T09:38:38Z) diagnosed; the fixes waited for the owner's choice among the
  options of Note 3.
- previous: draft -> in_progress (2026-10-06T09:37:20Z) the owner reported both failures in chat (Notes 1-2).

## Steps / Checklist
- [x] Diagnose attempt 1 (Note 1) and attempt 2 (Note 2).
- [x] Check the other workflows for the same re-run hazard; propose fixes (Note 3).
- [x] Owner: decide on the fixes: option 1, both (Note 4).
- [x] Implement both fixes with tests and docs (Notes 7-8); rebuild assets and llm_support last (Note 9).
- [ ] Owner: commit and push; re-run all jobs on run 37443362134 (its old workflow file cannot reuse the build);
      accept or redirect.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- The diagnosis and the owner's recovery steps; on approval, the re-run and retry fixes with tests and docs.

## Files / Paths Impacted
- .github/workflows/build-distributions.yml, release-candidate.yml, python-publish.yml
- .github/scripts/testpypi_candidate.py
- tests/unit/github_workflows/test_candidate_publication.py, test_workflow_contracts.py
- .github/BRANCH_WORKFLOW.md; .github/ci_cd/workflows.md, scripts.md, extending.md, validating.md
- context_compass/system_docs/tests_components.md and its index (C1 extents)
- src/melder/_build_assets manifests and llm_support bundles (regenerated)

## Validation
- 2026-10-06 09:49-09:58Z, device VM, CPython 3.14.7t (Notes 8-9): new and changed tests red first (9 failed,
  503 passed), then tests/unit/github_workflows 512 passed; eight mutations caught and restored byte for byte;
  tests_components index --check OK; build assets rebuilt and --check OK; llm_support rebuilt, --check
  --include-untracked and the tracked-only --check OK.
- Not run: a hosted release-candidate run, a hosted failed-jobs re-run (which also settles whether GitHub hands
  the build's output to re-run jobs, UNKNOWN per Note 3) and a hosted publication.

## Risks / Rollback Notes
- Risk: a retry that is too long hides a real outage behind a slow job; bound it like download_wheel's.
- Rollback: none needed while nothing changes.

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
- DATETIME: 2026-10-06T09:37:20Z
  TYPE: FACT
  CLAIM: Attempt 1 of run 37443362134 failed outside Melder. prepare-upload reads
    https://test.pypi.org/pypi/melder/<version>/json once; TestPyPI answered HTTP 503 "Backend is unhealthy", and
    remote_files tolerates only a 404 (no upload yet) and re-raises everything else, with no retry. Publish
    failed, install was skipped, and candidate-ready refused ("['publish', 'install']") as designed. The wheel
    download in probe-install already retries index propagation six times, ten seconds apart; the JSON lookup
    does not.
  EVIDENCE:
  - .github/scripts/testpypi_candidate.py:64-98
  - .github/scripts/testpypi_candidate.py:140-165
  - .github/workflows/release-candidate.yml:55-104
  - .github/workflows/release-candidate.yml:138-154
  IMPACT: One TestPyPI blip fails the whole candidate; the gate's refusal itself is correct.
  NEXT: Record attempt 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-06T09:37:20Z
  TYPE: FACT
  CLAIM: Attempt 2 ("Re-run failed jobs") failed in publish's download: "Artifact not found for name:
    candidate-dists-37443362134-2". build names its artifact candidate-dists-<run>-<attempt>, and publish and
    install download the same expression. A failed-jobs re-run does not repeat build, so the run holds only
    candidate-dists-37443362134-1 while the re-run asks for -2: every failed-jobs re-run of a publish or install
    failure fails this way. "Re-run all jobs" or a new dispatch rebuilds under the new attempt and works.
  EVIDENCE:
  - .github/workflows/release-candidate.yml:49-53
  - .github/workflows/release-candidate.yml:70-73
  - .github/workflows/release-candidate.yml:122-125
  IMPACT: Recovery from any publish or install failure costs a full rebuild today; the owner must use "Re-run
    all jobs".
  NEXT: Check python-publish.yml and ci.yml for the same pattern, then propose fixes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:38:38Z
  TYPE: DECISION_REQUEST
  CLAIM: python-publish.yml has the same hazard: release-build names release-dists-<run>-<attempt> and
    pypi-publish downloads that expression, so a failed-jobs re-run after a failed PyPI upload would not find its
    build either. ci.yml's ci-dists artifact has no downloader in its run, and the coverage job already downloads
    across attempts by pattern. Options. (1) Recommended: build-distributions.yml returns the name it uploaded as
    a workflow output; publish and install (release-candidate.yml) and pypi-publish (python-publish.yml) download
    needs.<build>.outputs.artifact-name, so a failed-jobs re-run uses the attempt that built and a full re-run
    builds and names a new one. It relies on GitHub handing a job that is not re-run's outputs to the re-run jobs,
    which this repository's partial-rerun design already assumes (the cells' matrix comes from discover's
    output) but which is UNKNOWN against GitHub's documentation here. With it, remote_files retries HTTP 5xx,
    timeouts and connection errors up to six times, ten seconds apart, and still fails closed; a 404 still means
    no upload and other 4xx still raise at once. Contract tests red then green, the CI guide updated. (2) Only the
    retry. (3) No change: after any publish or install failure, use "Re-run all jobs".
  EVIDENCE:
  - .github/workflows/python-publish.yml:72-101
  - .github/workflows/build-distributions.yml:1-74
  - .github/workflows/test-runtime.yml:131-142
  - .github/scripts/testpypi_candidate.py:32-38
  IMPACT: Decides whether recovery from a failed upload needs a full rebuild; nothing changes until the owner picks.
  NEXT: Owner: re-run all jobs on run 37443362134 now, and pick option 1, 2 or 3.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:45:54Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 09:45Z): "Both fixes (Recommended)", then "just fix everything so it works properly
    as intended". Option 1 of Note 3: build-distributions.yml returns the artifact name it uploaded and
    release-candidate.yml's publish and install, and python-publish.yml's pypi-publish, download that name, so a
    failed-jobs re-run uses the attempt that built; and remote_files retries transient TestPyPI failures a bounded
    number of times, still failing closed. The run that failed keeps its old workflow file (a re-run uses the
    original commit), so it still needs "Re-run all jobs".
  EVIDENCE:
  - .github/workflows/build-distributions.yml:1-74
  - .github/scripts/testpypi_candidate.py:64-98
  IMPACT: The boundary opens for the three workflows, the script, their tests and the CI guide; no src/ change.
  NEXT: Read the tests and docs that pin these workflows and the script, then write the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:47:28Z
  TYPE: CONFLICT
  CLAIM: Option 1's re-run half reverses a documented rule I did not cite in Note 3. The branch guide says a
    TestPyPI or PyPI retry uses "Re-run all jobs" for fresh same-attempt artifacts, and that rerunning only a
    failed upload must not reuse an earlier attempt's artifact implicitly; the CI guide's extending rules say
    artifact names carry run and attempt so a rerun never picks up another attempt's files. Reuse through the
    build job's output is explicit and the files are verified again before each upload (verify_distributions in
    prepare-upload and before the PyPI upload, hash-pinned install probes), but it is still a policy change, most
    of all for the irreversible PyPI publication. The TestPyPI retry does not touch this rule.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:395-400
  - .github/BRANCH_WORKFLOW.md:431-435
  - .github/ci_cd/extending.md:23-24
  - .github/workflows/python-publish.yml:96-104
  IMPACT: Implementing Note 4 as written would contradict the release rules; the owner decides with the rule in view.
  NEXT: Ask the owner: reuse in both workflows, reuse for the RC only, or keep fresh builds with a clear error.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:49:03Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 09:48Z), shown the rule of Note 5: "RC reuses, PyPI strict (Recommended)", then "just
    do the right thing". The release candidate's failed-jobs re-run uses this run's verified build (named by the
    build job's output); the final PyPI publication keeps a fresh build per attempt and stops a failed-jobs
    re-run of its upload with a message naming "Re-run all jobs" instead of "Artifact not found". The TestPyPI
    lookup retries transient failures. The branch guide's RC rule changes; its publication rule stays.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:395-400
  - .github/BRANCH_WORKFLOW.md:431-435
  IMPACT: Recovering a candidate from a TestPyPI blip becomes a failed-jobs re-run; publication stays strict.
  NEXT: Write the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:49:03Z
  TYPE: PLAN
  CLAIM: (1) build-distributions.yml returns artifact-name (workflow_call output from the job output
    `${{ inputs.artifact-name }}`). (2) release-candidate.yml: publish and install download
    `${{ needs.build.outputs.artifact-name }}`; build still names a fresh artifact per attempt. (3)
    python-publish.yml: before its download, pypi-publish refuses when the build's output is not this attempt's
    release-dists name, with an error naming "Re-run all jobs"; the download keeps this attempt's name. (4)
    testpypi_candidate.py: release_json retries HTTP 429/500/502/503/504, timeouts and connection errors up to
    six times, ten seconds apart, printing each retry; 404 is still the only "no upload"; other statuses and
    malformed JSON raise at once; remote_files parses as before. Tests first and red: retry recovery, bound,
    no retry for 403 or bad JSON (test_candidate_publication.py); the build output, the RC downloads and the
    publication guard (test_workflow_contracts.py). Docs: BRANCH_WORKFLOW.md (RC rule, publication note), the CI
    guide (workflows, scripts, extending, validating), C1 extents in tests_components. Then the suite, mutations,
    assets and llm_support last. Line endings kept per line (four of these files are mixed).
  EVIDENCE:
  - .github/workflows/build-distributions.yml:1-74
  - .github/workflows/release-candidate.yml:49-136
  - .github/workflows/python-publish.yml:72-104
  - .github/scripts/testpypi_candidate.py:32-98
  - tests/unit/github_workflows/test_candidate_publication.py:236-283
  - tests/unit/github_workflows/test_workflow_contracts.py:370-395
  - tests/unit/github_workflows/test_workflow_contracts.py:492-553
  IMPACT: One change set; no src/ change, no notch, no release-note entry (CI only).
  NEXT: Write the new and changed tests and run them red.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-06T09:53:23Z
  TYPE: MEASURE
  CLAIM: Implemented per Note 7 and proven (device VM, CPython 3.14.7t). The new and changed tests were red first
    (9 failed, 503 passed) and pass after the change: tests/unit/github_workflows 512 passed. Edits:
    build-distributions.yml returns artifact-name (workflow output from the job output of its input);
    release-candidate.yml's publish and install download needs.build.outputs.artifact-name; python-publish.yml's
    pypi-publish refuses before its download when the build's output is not this attempt's release-dists name
    ("Use Re-run all jobs: ..."); testpypi_candidate.py's release_document retries HTTP 429/500/502/503/504,
    timeouts and connection errors up to six times, ten seconds apart, printing each retry, and remote_files
    parses its answer. Eight mutations, each caught and restored byte for byte: either RC download back on its
    own attempt, the publication guard never exiting, the build output dropped, 503 not transient, no pause, 403
    retried, bad JSON retried. Docs: BRANCH_WORKFLOW.md (the RC rule now reuses the run's build; publication
    unchanged, plus the guard), the CI guide's workflows, scripts, extending and validating pages; tests_components
    C1 extents (test_candidate_publication 434, test_workflow_contracts 860), index OK. Line endings kept per line.
  EVIDENCE:
  - .github/workflows/build-distributions.yml:12-15
  - .github/workflows/build-distributions.yml:35-37
  - .github/workflows/release-candidate.yml:70-77
  - .github/workflows/release-candidate.yml:126-131
  - .github/workflows/python-publish.yml:97-107
  - .github/scripts/testpypi_candidate.py:68-128
  - tests/unit/github_workflows/test_candidate_publication.py:255-344
  - tests/unit/github_workflows/test_workflow_contracts.py:398-431
  - .github/BRANCH_WORKFLOW.md:395-405
  IMPACT: A TestPyPI blip is ridden out, and a failed-jobs re-run of the candidate reuses its build; publication
    fails a partial re-run with a clear instruction. Not run: a hosted failed-jobs re-run, which is also what
    proves GitHub hands the build's output to re-run jobs (UNKNOWN until then, Note 3).
  NEXT: Rebuild the build assets and llm_support last and run their checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:56:18Z
  TYPE: MEASURE
  CLAIM: Rebuilt last. The build-asset runner exited 0 in 51 s (agent documentation 462, bind guard 622, system
    documents 4, v0.2.8227) and its --check prints only OK lines; llm_support --include-untracked rewrote tests
    (1063 files) and other (402), src unchanged; --check --include-untracked and the tracked-only --check print
    only OK lines. No .git/index.lock. No src/ change, no notch, no release-note entry.
  EVIDENCE: .github/workflows/release-candidate.yml:70-77
  IMPACT: The change set is ready for the owner's commit; CI's asset and bundle checks pass on the working tree.
  NEXT: Owner: commit and push; "Re-run all jobs" on run 37443362134 (its workflow file predates the fix); accept
    or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Review (Notes 1-9): the failed candidate run was a TestPyPI outage (503) at the one unretried lookup, and the
failed-jobs re-run could not work because the build artifact's name carried the consumer's attempt. Fixed as the
owner chose (Note 6): the build reports its artifact; the candidate's publish and install download it, so a
failed-jobs re-run reuses the run's verified build; final publication keeps fresh builds and refuses a partial
re-run with "Use Re-run all jobs"; the TestPyPI lookup retries 429/5xx, timeouts and connection failures six
times, ten seconds apart. 512 passed, eight mutations caught, docs and assets current. Owner-owed: commit, push,
"Re-run all jobs" on run 37443362134, then acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
