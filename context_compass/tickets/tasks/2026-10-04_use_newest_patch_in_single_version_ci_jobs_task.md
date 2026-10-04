# Task: Use the newest stable 3.14 patch in single-version CI jobs

## Metadata
- Task ID: TASK-2026-10-04-use_newest_patch_in_single_version_ci_jobs
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-04T20:51:55Z
- Updated: 2026-10-04T20:53:47Z

## Objective
Make every single-version CI job that asks for `python-version: "3.14"` also set `check-latest: true`, so it
runs the newest stable 3.14 patch that the runtime matrix tests, and pin the CI's Python version rules with a
contract test. Only stable Python releases are tested; there is no pre-release lane.

## Ticket Contract
- ENTRY_GATE: The owner's chat directives of 2026-10-04 ("setup my matrix to follow every version I support
  314 and up"; "we don't want prerelease stuff"; the speed tests only on the latest version and only for
  dev -> preprod). Active board row: ci_python_check_latest.
- EXECUTION_BOUNDARY: the 13 `python-version: "3.14"` setup steps in seven workflow files,
  tests/unit/github_workflows/test_workflow_contracts.py and the Supported Python versions section of
  .github/BRANCH_WORKFLOW.md. No change to python_runtime_matrix.py, test-runtime.yml, the speed-test
  workflows or src/. No commit, push or PR.
- DEPENDENCIES: none. The llm_support bundles are rebuilt once, as the last write of this session's work,
  because the SpellMap lane edits src/ after this task.
- EXIT_GATE: every bare-minor setup sets check-latest; tests/unit/github_workflows passes here; the owner
  accepts or redirects.
- FAILURE_ESCALATION: Record BLOCKER if the workflow suite cannot run on the device VM.

## Scope Boundaries
- In scope: check-latest on bare-minor setups; one contract test; one branch-guide paragraph.
- Out of scope: pre-release Python testing (owner ruled it out); the speed tests' 3.14.7 pin (owner question
  pending: follow the newest Python or keep a fixed pin); discovery's fail-closed rule for a newest patch
  without free-threaded assets.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-04T20:53:47Z) implemented and validated (Notes 5-6); the owner's acceptance and the
  session's llm_support rebuild remain.
- previous: draft -> in_progress (2026-10-04T20:51:55Z) on the owner's chat directives (Notes 1-4).

## Steps / Checklist
- [x] Investigate discovery, the single-version setups and the speed-test routing (Notes 1-2).
- [x] Insert `check-latest: true` beneath the 13 setups.
- [x] Add the contract test.
- [x] Add the branch-guide paragraph.
- [x] Run tests/unit/github_workflows and record the result.
- [ ] Rebuild llm_support as the session's last write and run its --check (result reported in chat).

## Deliverables
- 13 setup steps with check-latest; one contract test; one branch-guide paragraph.

## Files / Paths Impacted
- .github/workflows/build-repo-assets.yml
- .github/workflows/build-src-assets.yml
- .github/workflows/ci.yml
- .github/workflows/docs.yml
- .github/workflows/python-publish.yml
- .github/workflows/release-candidate.yml
- .github/workflows/verify-source-qualification.yml
- tests/unit/github_workflows/test_workflow_contracts.py
- .github/BRANCH_WORKFLOW.md

## Validation
- 2026-10-04, device VM, uv CPython 3.14.7 free-threaded, pytest 9.1.1, PyYAML 6.0.3 (Note 6):
  - python -m pytest tests/unit/github_workflows -q -p no:cacheprovider: 477 passed.
  - Mutation check: with docs.yml's check-latest removed the new test fails naming docs.yml; restored
    byte-identical, it passes.
- Not run: the hosted workflows (the owner's next push runs them); llm_support rebuild and --check
  (the session's last write, after the SpellMap lane).

## Risks / Rollback Notes
- Risk: with check-latest, setup-python consults the actions/python-versions manifest on every run (one
  extra network read per job). The runtime matrix discovery already depends on the same manifest.
- Rollback: remove the 13 inserted lines, the contract test and the paragraph.

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
- DATETIME: 2026-10-04T20:51:55Z
  TYPE: FACT
  CLAIM: Runtime discovery already follows every supported stable minor: it reads the floor from
    requires-python, skips stable:false manifest entries (alpha, beta, rc), keeps the newest patch of each
    minor at or above the floor, and refuses a newest patch without free-threaded assets on Linux, Windows
    and macOS; test-runtime.yml runs exactly that matrix free-threaded. 3.15 therefore joins the required
    matrix by itself once 3.15.0 is stable, and the matrix code needs no change.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:30-44
  - .github/scripts/python_runtime_matrix.py:74-115
  - .github/workflows/test-runtime.yml:15-56
  IMPACT: "Follow every version from 3.14 up" is already the runtime-test behaviour; the gap is only in the
    single-version helper jobs.
  NEXT: Record the single-version setups and the speed-test routing.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:51:55Z
  TYPE: FACT
  CLAIM: 13 setup-python steps in seven workflows ask for a bare `python-version: "3.14"` with no
    check-latest, so each takes whatever 3.14 patch the runner image has cached (setup-python's check-latest
    defaults to false), which can trail the newest patch the matrix tests (the owner saw 3.14.8 in the
    matrix against a local 3.14.7). The three speed tests pin '3.14.7' (the real-world gauntlet also asserts
    it), run no Python matrix, and are required only when a dev branch PR targets preprod.
  EVIDENCE:
  - .github/workflows/build-repo-assets.yml:22-22
  - .github/workflows/build-src-assets.yml:27-27
  - .github/workflows/ci.yml:37-37
  - .github/workflows/ci.yml:50-50
  - .github/workflows/ci.yml:126-126
  - .github/workflows/docs.yml:22-22
  - .github/workflows/python-publish.yml:34-34
  - .github/workflows/python-publish.yml:51-51
  - .github/workflows/python-publish.yml:96-96
  - .github/workflows/release-candidate.yml:28-28
  - .github/workflows/release-candidate.yml:69-69
  - .github/workflows/release-candidate.yml:148-148
  - .github/workflows/verify-source-qualification.yml:20-20
  - .github/workflows/real-world-gauntlet.yml:57-62
  - .github/scripts/ci_policy.py:104-125
  IMPACT: One inserted line per setup aligns every single-version job with the matrix's newest 3.14 patch;
    the speed tests already meet the owner's single-version, dev-to-preprod-only rule.
  NEXT: Record the owner's rulings.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:51:55Z
  TYPE: DECISION
  CLAIM: Owner rulings (chat, 2026-10-04): no pre-release lane ("we don't want prerelease stuff we want real
    shit"); the speed tests run on one Python only, never the matrix, and only for dev -> preprod. The
    allowed-to-fail pre-release job drafted after the compaction was never written. check-latest on the
    bare 3.14 setups stands from the earlier agreement. The speed tests stay on 3.14.7 until the owner says
    whether they should follow the newest Python or keep a fixed pin.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:137-143
  - .github/scripts/ci_policy.py:104-125
  IMPACT: The branch guide already says pre-releases are excluded; this task adds no new lane.
  NEXT: Record the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:51:55Z
  TYPE: PLAN
  CLAIM: Insert `check-latest: true` at the same indentation beneath each of the 13 lines (binary
    read-modify-write keeping CRLF, asserting the per-file counts 1/1/3/1/3/3/1). Add a contract test that
    walks every workflow's setup-python steps: a bare major.minor version requires check-latest true, an
    exact pin appears only in the three speed-test workflows, and no speed-test job iterates a Python
    matrix. Add one branch-guide paragraph. Run tests/unit/github_workflows.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:14-22
  - tests/unit/github_workflows/test_workflow_contracts.py:97-115
  - .github/BRANCH_WORKFLOW.md:137-149
  IMPACT: The test fails if a new workflow adds a bare minor without check-latest or a pinned Python
    outside the speed tests.
  NEXT: Apply the 13 insertions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:53:47Z
  TYPE: FACT
  CLAIM: Applied: `check-latest: true` sits beneath all 13 bare `python-version: "3.14"` lines at the same
    indentation (per-file counts 1/1/3/1/3/3/1; each file kept its own line endings, python-publish.yml and
    release-candidate.yml being mixed in the working tree and verify-source-qualification.yml LF).
    test_single_version_setups_follow_the_newest_stable_patch walks every workflow's setup-python steps:
    no pre-release request anywhere, check-latest on every bare minor, exact pins only in the three speed
    tests, and none of those iterates a Python matrix. The branch guide states the rule.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:118-146
  - .github/workflows/ci.yml:37-38
  - .github/workflows/real-world-gauntlet.yml:128-128
  - .github/BRANCH_WORKFLOW.md:151-155
  IMPACT: Every single-version job now resolves 3.14 to its newest stable patch, matching the matrix; a new
    workflow cannot drift back without failing the contract suite.
  NEXT: Run tests/unit/github_workflows and a mutation check of the new test.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T20:53:47Z
  TYPE: MEASURE
  CLAIM: Device VM, uv CPython 3.14.7 free-threaded, pytest 9.1.1, PyYAML 6.0.3, bytecode writes off:
    python -m pytest tests/unit/github_workflows -q -p no:cacheprovider gave 477 passed in 3.39s. With the
    check-latest line removed from docs.yml the new test failed with AssertionError ('docs.yml', '3.14');
    the file was restored from a byte copy (cmp clean) and the test passed again.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:118-146
  IMPACT: The contract suite agrees with the 13 edits, and the new test bites. The hosted workflows run on
    the owner's next push.
  NEXT: Owner accepts or redirects, and answers whether the speed tests should follow the newest Python;
    the llm_support rebuild runs as the session's last write.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (Notes 5-6): the 13 single-version setups use check-latest, a contract test guards the version rules
(no pre-release anywhere, exact pins only in the three speed tests), and the branch guide says so; 477
workflow tests pass. Runtime tests already followed every stable Python from 3.14 up (Note 1). Owner-owed:
acceptance, and whether the speed tests should follow the newest Python instead of the 3.14.7 pin. The
llm_support rebuild runs as the session's last write.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
