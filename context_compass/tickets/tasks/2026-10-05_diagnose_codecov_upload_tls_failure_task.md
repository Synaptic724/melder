# Task: Diagnose the Codecov upload failure (uploader download refused over TLS)

## Metadata
- Task ID: TASK-2026-10-05-diagnose_codecov_upload_tls_failure
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-05T00:55:17Z
- Updated: 2026-10-06T09:45:54Z

## Objective
Explain why the hosted "Upload coverage to Codecov" step failed, whether it blocks CI or merging, and whether a
repository change is warranted; recommend one path.

## Ticket Contract
- ENTRY_GATE: The owner's chat report of 2026-10-05 (the failing step's log). Active board row:
  codecov_upload_tls.
- EXECUTION_BOUNDARY: read-only diagnosis of .github/workflows/test-runtime.yml (coverage job),
  .github/workflows/ci.yml (merge-ready), .github/scripts/ci_policy.py, .github/rulesets/*.json and Codecov's public
  endpoints. No workflow edit without the owner's explicit go-ahead. No src change, no commit, push or PR.
  Reopened on the owner's directive (Note 9): the coverage job's upload step and a PyPI fallback step in
  .github/workflows/test-runtime.yml, one contract test in tests/unit/github_workflows/test_workflow_contracts.py
  and the Codecov paragraph of .github/BRANCH_WORKFLOW.md join the boundary; the llm_support rebuild and
  --check are the last write.
- DEPENDENCIES: none.
- EXIT_GATE: diagnosis and recommendation recorded and reported; the owner accepts or asks for a change.
- FAILURE_ESCALATION: DECISION_REQUEST if the owner wants hardening (a retry or a PyPI install) despite Note 4.

## Scope Boundaries
- In scope: the root cause of the failed upload, its CI and merge impact, the repository-side options.
- Out of scope: Codecov's own infrastructure; disabling TLS verification (never).

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-05T01:53:09Z) the PyPI fallback is in, 481 workflow
  tests pass and llm_support checks OK (Notes 11-13); the owner's push and acceptance remain.
- previous: review -> in_progress (2026-10-05T01:41:23Z) the owner asked for the PyPI fallback in
  the next version (Note 9); the lane reopens.
- previous: in_progress -> review (2026-10-05T00:58:41Z) diagnosis complete (Notes 1-4): a Codecov-side
  TLS and certificate failure, no repository change recommended; the owner's acceptance remained.
- previous: draft -> in_progress (2026-10-05T00:55:17Z) on the owner's report.

## Steps / Checklist
- [x] Read the failing step's log and the coverage job (Note 1).
- [x] Check what a failed coverage job blocks (Note 2).
- [x] Check Codecov's endpoints and status (Note 3).
- [x] Recommend one path (Note 4).
- [ ] Owner accepts or redirects.
- [x] Add the PyPI fallback step and its contract test (Note 9).
- [x] Run tests/unit/github_workflows and a mutation check.
- [x] Rebuild llm_support last and run --check.

## Deliverables
- The diagnosis and recommendation in Notes 1-4 and the chat reply.

## Files / Paths Impacted
- none (read-only diagnosis)

## Validation
- Not run: the hosted coverage job (the owner re-runs it once Codecov recovers). No repository file changed, so
  no test suite or rebuild applies.

## Risks / Rollback Notes
- Risk: coverage for the affected commits is missing on Codecov until a re-run or the next push uploads it.
- Rollback: not applicable (no change).

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
- DATETIME: 2026-10-05T00:55:17Z
  TYPE: FACT
  CLAIM: The failed step never reached an upload. Per the owner's log, the codecov-action wrapper's download of the
    uploader from https://cli.codecov.io/latest/linux/codecov failed with curl error 35 (OpenSSL 3.0.13, "sslv3
    alert handshake failure"); the SHA256SUM and .sig downloads from the same host failed too, so gpg found no
    signature file and the wrapper exited ("Could not verify signature"), which fail_ci_if_error: true makes a
    step failure. The log shows no retry of the download.
  EVIDENCE: .github/workflows/test-runtime.yml:150-158
  IMPACT: The failure is in fetching Codecov's tool, before any of our reports were read; the tests and the
    coverage XML are not implicated.
  NEXT: Check what a failed coverage job blocks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T00:55:17Z
  TYPE: FACT
  CLAIM: A failed upload blocks nothing. The coverage job is continue-on-error: true at job level ("Reporting
    availability must not turn passing tests into a release failure"), so the reusable runtime workflow and
    ci.yml's tests job still conclude success; the four rulesets require only "CI / merge-ready", whose policy
    reads needs.<job>.result alone. The job still shows a red X on its run. The test jobs keep their coverage
    reports 14 days and the coverage job downloads them from every attempt of the run, so re-running only that
    job later uploads them.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:94-106
  - .github/workflows/test-runtime.yml:74-84
  - .github/workflows/test-runtime.yml:126-136
  - .github/workflows/ci.yml:111-136
  - .github/scripts/ci_policy.py:128-155
  - .github/rulesets/dev.json:19-19
  IMPACT: Merges and releases are unaffected; only that run's coverage upload is missing.
  NEXT: Check Codecov's endpoints and status.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T00:58:41Z
  TYPE: MEASURE
  CLAIM: Checked from this session at about 2026-10-05T00:58Z with an independent HTTPS client (the web fetch
    tool, not the runner): cli.codecov.io refused the TLS handshake with the same SSLV3_ALERT_HANDSHAKE_FAILURE,
    and api.codecov.io and ingest.codecov.io (the upload hosts) failed verification with "certificate has
    expired"; pypi.org, status.codecov.com and raw.githubusercontent.com connected normally. status.codecov.com
    showed all systems operational and no incident in the past 14 days. The device VM's proxy refuses codecov
    hosts (HTTP 403), so no second client was tried. Whether the runner also sees the expired certificate is
    UNKNOWN.
  EVIDENCE: .github/workflows/test-runtime.yml:150-158
  IMPACT: The fault is Codecov's TLS and certificates, still live after the owner's run; a re-run fails until
    Codecov fixes it, and an uploader installed from PyPI would still send to the failing hosts.
  NEXT: Record the recommendation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T00:58:41Z
  TYPE: DECISION
  CLAIM: Recommend no repository change (the owner decides). A retry would retry into the same outage;
    use_pypi: true would skip the uploader's GPG check and still upload to the failing hosts; fail_ci_if_error:
    false would only hide real upload failures in a job that is already non-blocking; TLS verification is never
    disabled. Once Codecov is fixed, re-run the failed Coverage / Codecov job on that run, or let the next push
    upload. Revisit one automatic retry only if short download blips recur after this outage.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:94-106
  - .github/workflows/test-runtime.yml:150-158
  IMPACT: Nothing to edit, rebuild or push for this.
  NEXT: Owner accepts or asks for hardening.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:06:03Z
  TYPE: FACT
  CLAIM: The owner's second log (step debug output, PR #176, head 8f9a0abb683f, event pull_request) shows the same
    failure with nothing new: inputs use_pypi false, version latest, skip_validation false, fail_ci_if_error true;
    curl error 35 on the uploader download, the SHA256SUM and .sig downloads empty, gpg finds no signature, exit 1.
  EVIDENCE: .github/workflows/test-runtime.yml:150-158
  IMPACT: Confirms Note 1 on a second run; the owner found the full log hard to read, so the reply points at the
    one line that matters.
  NEXT: Re-check cli.codecov.io and test the PyPI route.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-05T01:06:03Z
  TYPE: MEASURE
  CLAIM: Re-checked about 01:05Z: cli.codecov.io still refuses the TLS handshake (SSLV3_ALERT_HANDSHAKE_FAILURE) to
    the web fetch tool; status.codecov.com and statuscentral.io still show no incident. codecov-action's newest
    release is v7.0.0 (June 7) and the wrapper on main still downloads from cli.codecov.io, so no host move is
    announced. On the device VM, codecov-cli 11.3.1 installs from PyPI into a CPython 3.14.7 venv (the interpreter
    the coverage job sets up) and runs (codecovcli --version). Whether the runner can reach the upload hosts during
    this outage is UNKNOWN.
  EVIDENCE: .github/workflows/test-runtime.yml:120-124
  IMPACT: use_pypi: true would sidestep the broken download host; it does not prove the upload itself succeeds.
  NEXT: Offer the owner one optional change.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:06:03Z
  TYPE: DECISION_REQUEST
  CLAIM: Default stays no change (Note 4): the job cannot block CI and Codecov must fix its host. Optional, owner's
    call: keep the signed download as the first attempt and, only when that step fails, run the upload again with
    use_pypi: true. Cost: about ten workflow lines, one contract test, the llm_support rebuild; the fallback attempt
    skips the uploader's GPG check.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:94-106
  - .github/workflows/test-runtime.yml:150-158
  IMPACT: Without it the red X recurs on every push until Codecov recovers; nothing is blocked either way.
  NEXT: Owner answers yes (implement under this ticket) or no (accept and close).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:37:44Z
  TYPE: FACT
  CLAIM: The owner's Firefox cannot open app.codecov.io: "can't create a secure connection", error code
    SSL_ERROR_NO_CYPHER_OVERLAP (screenshot in chat). With Notes 3 and 6, Codecov's HTTPS now fails on its web app,
    its uploader download host and (to the fetch tool) its upload hosts, for three independent clients: the
    runner, the fetch tool and the owner's browser. status.codecov.com still showed no incident at 2026-10-05T01:37:44Z.
  EVIDENCE: .github/workflows/test-runtime.yml:150-158
  IMPACT: A PyPI-installed uploader would very likely fail at the upload too, so the fallback offered in Note 7 is
    withdrawn: nothing on our side can make uploads work until Codecov fixes its servers.
  NEXT: Owner re-runs the failed Coverage / Codecov job once app.codecov.io loads normally, then accepts; close.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:41:23Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 01:40Z): "just gonna skip it next version codecov can be added ... go ahead and use the
    pypi backup for the next version please add that in". The owner skips coverage for the current push and wants
    the fallback of Note 7 in place for the next version: the signed download stays the first attempt, and only
    when that step fails does a second attempt run with use_pypi: true. This overrides the withdrawal in Note 8;
    the fallback cannot help during the present outage (the upload hosts fail too) but covers a download-only
    failure such as the 2026-04-23 integrity incident.
  EVIDENCE: .github/workflows/test-runtime.yml:150-158
  IMPACT: The boundary grows to the workflow step, one contract test, one branch-guide paragraph and the
    llm_support rebuild.
  NEXT: Read the contract-test helpers and the branch guide's Codecov section, then write the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:42:27Z
  TYPE: PLAN
  CLAIM: In test-runtime.yml (mixed line endings; lines 150-158 are LF) the upload step gets id codecov and
    step-level continue-on-error: true, and a fallback step follows it: if the credential check passed and
    steps.codecov.outcome == 'failure', the same codecov-action@v7 inputs plus use_pypi: true, with no
    continue-on-error, so a second failure still fails the (non-blocking) job. The existing contract test reads the
    upload and selection steps by position and requires every later step's if to be the credential check; it is
    adjusted to the new shape, and one new test pins the fallback (exactly two codecov steps, last; the first keeps
    the signed download; the fallback runs only after a failed first attempt and differs only by use_pypi). One
    paragraph joins the branch guide's Codecov section. Then tests/unit/github_workflows, two mutation checks, and
    the llm_support rebuild and --check as the last write.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:150-158
  - tests/unit/github_workflows/test_workflow_contracts.py:251-282
  - .github/BRANCH_WORKFLOW.md:190-194
  IMPACT: The workflow and its contract tests change together; nothing in src moves, so no notch or release note.
  NEXT: Apply the three edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:46:16Z
  TYPE: FACT
  CLAIM: Applied. The upload step has id codecov and step-level continue-on-error: true; a new step, "Upload
    coverage to Codecov with the PyPI uploader", runs only when the credential check passed and
    steps.codecov.outcome == 'failure', with the same inputs plus use_pypi: true and no continue-on-error, so a
    second failure still fails the non-blocking job. Inserted lines match their LF neighbours (the file's 16 CRLF
    lines are untouched). test_coverage_upload_is_nonblocking_token_only_and_skips_fork_prs now checks both upload
    steps and finds the selection step at -3; the new
    test_codecov_upload_retries_with_the_pypi_uploader_only_after_a_failed_first_attempt pins the fallback. The
    branch guide's Codecov section says how the retry works and what it skips.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:150-172
  - tests/unit/github_workflows/test_workflow_contracts.py:251-301
  - .github/BRANCH_WORKFLOW.md:196-199
  IMPACT: A download-host failure gets one automatic retry from PyPI; the signed download stays the default.
  NEXT: Run the workflow suite and mutation checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:46:16Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t venv, PYTHONDONTWRITEBYTECODE=1: python -m pytest tests/unit/github_workflows -q
    -p no:cacheprovider -o addopts="" gave 481 passed (480 before, plus the new test). Mutations of
    test-runtime.yml, each restored byte for byte (cmp clean): dropping use_pypi failed the new test; dropping the
    outcome condition failed the new test and the adjusted one. The hosted run is Not run (owner's next push).
  EVIDENCE: tests/unit/github_workflows/test_workflow_contracts.py:285-301
  IMPACT: The contract suite agrees with the edit and catches both ways the fallback could drift.
  NEXT: Rebuild llm_support as the last write and run --check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:53:09Z
  TYPE: MEASURE
  CLAIM: llm_support/_builder.py --include-untracked rewrote the tests and other bundles (src unchanged); --check
    --include-untracked printed OK for src, tests and other; the build-asset --check printed three current lines
    at v0.2.8227. No untracked file exists outside context_compass/, so the bundles match what a commit of the
    working tree carries. No .git/index.lock was left.
  EVIDENCE: .github/workflows/test-runtime.yml:150-172
  IMPACT: The change set is complete and CI's bundle check will agree once it is committed.
  NEXT: Owner commits and pushes; the fallback runs from the next upload on; accept or redirect.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-06T09:42:08Z
  TYPE: FACT
  CLAIM: Owner (chat, 2026-10-06 about 09:30Z): "codecov isn't populating anymore in the cicd". Uploads work on
    every route that runs the tests. In CI run 37397870593 (the dev -> preprod PR, d2bf3fe1e) "tests / Coverage /
    Codecov" succeeded 01:38:46-01:39:07Z; its first upload attempt succeeded and the PyPI fallback was skipped
    (GitHub's public jobs API). Codecov's public API lists dev updated 2026-10-06T01:39:52Z and codex_features2
    00:56:59Z, commits 0b28a066d and d2bf3fe1e complete at 86.93%. What stays still is by design: Codecov's
    default branch for the repository is prod (86.71%, updated 2026-09-28T13:28Z) and the README badge tracks
    prod, which receives coverage only from the final publication's tests or a manual Runtime tests run on prod;
    the preprod -> release_candidate and release_candidate -> prod PRs run no tests; and codecov.yml turns off
    Codecov's PR comments and project/patch statuses, so no PR check ever shows Codecov. Codecov's status page
    records the 2026-10-05 outage behind Notes 1-8 as an expired SSL certificate, resolved at 09:15Z.
  EVIDENCE:
  - codecov.yml:1-6
  - README.md:24-24
  - .github/BRANCH_WORKFLOW.md:229-233
  - .github/workflows/test-runtime.yml:156-178
  - .github/workflows/python-publish.yml:62-69
  IMPACT: Nothing is broken; the fallback has not been needed since the outage ended.
  NEXT: Owner decides whether the prod-only dashboard and badge are what they want (Note 15).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-06T09:42:08Z
  TYPE: DECISION_REQUEST
  CLAIM: How should coverage show? (1) Keep the design: dev and feature data land every run, prod's number and
    the badge move at each release. (2) Refresh prod now without a release: Actions -> Runtime tests -> Run
    workflow on prod (the branch guide's documented seed). (3) Make Codecov track dev: set the default branch to
    dev in Codecov's repository settings (owner's account) and point the README badge at dev. (4) Show Codecov in
    PR checks: enable informational project/patch statuses or comments in codecov.yml.
  EVIDENCE:
  - codecov.yml:1-6
  - .github/BRANCH_WORKFLOW.md:229-233
  IMPACT: Changes only what is displayed; the uploads already work.
  NEXT: Owner picks one or more options; (3) and (4) are small repository edits under this ticket.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-06T09:45:54Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 09:45Z): "Keep as is" for how coverage shows, and "its just weird codecov wasn't
    showing up in the CICD and it used to". No repository change: tested routes (PRs into dev, dev -> preprod,
    release fixes, manual CI, publication) upload and show the "Coverage / Codecov" job; the promotion PRs into
    release_candidate and prod run no tests, so they show no Codecov job, likely what the owner saw on today's
    promotion (UNKNOWN until confirmed); prod's number and badge move at the next publication.
  EVIDENCE:
  - codecov.yml:1-6
  - .github/BRANCH_WORKFLOW.md:229-233
  IMPACT: The Codecov lane needs no further work; it waits for the owner's acceptance.
  NEXT: Owner accepts or redirects; then close.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Diagnosed (Notes 1-8): the upload failed because Codecov's servers broke TLS (download host, upload hosts and
web app); the coverage job cannot block CI. On the owner's directive (Note 9) the upload now retries once
with the PyPI-installed uploader when the signed download fails (Notes 10-13): 481 workflow tests pass,
mutations caught, llm_support checks OK. Owner-owed: commit, push, and acceptance; then close.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
