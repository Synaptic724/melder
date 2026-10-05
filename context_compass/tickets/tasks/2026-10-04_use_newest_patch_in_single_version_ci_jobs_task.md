# Task: Use the newest stable 3.14 patch in single-version CI jobs

## Metadata
- Task ID: TASK-2026-10-04-use_newest_patch_in_single_version_ci_jobs
- Story: none (standalone task; owner request)
- Status: review
- Owner: claude
- Agent Name: melder_1
- Priority: p2
- Created: 2026-10-04T20:51:55Z
- Updated: 2026-10-05T11:42:00Z

## Objective
Make CI explicit and manifest-driven (owner, 2026-10-05; Notes 24-25). Every Python release CI runs is named
by a TOML manifest: one per release under .github/python/tests/ (3.14.0-3.14.8) for the runtime tests and the
release candidate's install probes, exactly one under .github/python/speed/ (3.14.7) for the three speed tests,
each pinning that release's dependencies. Single-version helper jobs pin 3.14.7. Nothing discovers or follows
the newest Python; a new release runs only once a manifest adds it. Superseded on the way: check-latest on the
bare 3.14 setups (Notes 1-6), the newest-patch speed tests (Notes 7-11) and every-release discovery (Notes 17-21).

## Ticket Contract
- ENTRY_GATE: The owner's chat directives of 2026-10-04 ("setup my matrix to follow every version I support
  314 and up"; "we don't want prerelease stuff"; the speed tests only on the latest version and only for
  dev -> preprod). Active board row: ci_python_check_latest.
- EXECUTION_BOUNDARY: the 13 `python-version: "3.14"` setup steps in seven workflow files,
  tests/unit/github_workflows/test_workflow_contracts.py and the Supported Python versions section of
  .github/BRANCH_WORKFLOW.md. Reopened on the owner's answer (Note 7): the three speed-test workflows
  (real-world-gauntlet.yml, persistent-runtime-gauntlet.yml, shallow-all-thread-scaling.yml) and their contract
  tests join the boundary. No change to src/. No commit, push or PR.
  Reopened again on the owner's directive (Note 17): .github/scripts/python_runtime_matrix.py,
  tests/unit/github_workflows/test_python_runtime_matrix.py, test-runtime.yml and release-candidate.yml step
  names, the three speed-test workflows' pin, assertion and install command, their contract tests and the
  branch guide's version section; the llm_support rebuild and --check stay the last write.
  Reopened a third time (Note 24, manifests): .github/python/tests/ and .github/python/speed/, every
  setup-python step (helpers pin 3.14.7), test-runtime.yml's cell install, the speed workflows' Python and
  install source, both workflow test files and the branch guide.
  Documentation the change made false joins it (Note 30): CONTRIBUTING.md's CI paragraph, the tests system
  documents' CI entrypoint, flow, unknown and C1 extents (indexes regenerated) and one release-note line.
- DEPENDENCIES: none. The llm_support bundles are rebuilt once, as the last write of this session's work,
  because the SpellMap lane edits src/ after this task.
- EXIT_GATE: every setup-python request is a manifest release or the 3.14.7 helper pin;
  tests/unit/github_workflows passes here; llm_support --check is OK; the owner accepts or redirects.
- FAILURE_ESCALATION: Record BLOCKER if the workflow suite cannot run on the device VM.

## Scope Boundaries
- In scope: the per-release manifests, python_runtime_matrix.py (local discovery, speed, speed-install and
  requirements operations), every setup-python step, the runtime cell install, the speed workflows' manifest
  job and install, both workflow test files, and the documentation the change made false (Note 30).
- Out of scope: pre-release Python testing (owner ruled it out); Melder source; the Codecov lane; the
  github_workflows C1 extents in tests_components that earlier lanes left stale.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: (2026-10-05T11:42:00Z) manifest-driven CI implemented and validated here (Notes 26-31); the
  owner's commit and push, the hosted runs and acceptance remain.
- previous: review -> in_progress (2026-10-05T01:53:09Z) the owner reported the speed-test install failing
  on hosted 3.14.8t runners and asked for per-minor pins (Notes 12-15).
- previous: in_progress -> review (2026-10-04T23:59:15Z) the speed tests follow the newest stable 3.14
  patch and the contracts pass (Notes 7-11); the owner's push and acceptance remained.
- previous: review -> in_progress
  (2026-10-04T23:12:37Z) the owner answered the speed-test question (Note 7); the lane reopens.
- previous: in_progress -> review (2026-10-04T20:53:47Z) implemented and validated (Notes 5-6); the
  owner's acceptance and the session's llm_support rebuild remained.
- previous: draft -> in_progress (2026-10-04T20:51:55Z) on the owner's chat directives (Notes 1-4).

## Steps / Checklist
- [x] Earlier passes: check-latest (Notes 1-6), newest-patch speed tests (Notes 7-11), the dependency-injector
      diagnosis and source build (Notes 12-15), every-release discovery (Notes 17-21); all superseded except the
      source build.
- [x] Write the nine test manifests and the speed manifest.
- [x] Rewrite python_runtime_matrix.py for local manifests; add speed-install.
- [x] Pin every helper setup to 3.14.7; install each runtime cell from its manifest.
- [x] Give each speed workflow a manifest job; install and assert from the speed manifest.
- [x] Update the contract and matrix tests; run the suite and mutation checks.
- [x] Scratch-run the cell install and speed-install on the device VM (Note 29).
- [x] Update the branch guide, CONTRIBUTING, the tests system documents and the release note (Note 30).
- [x] Rebuild the build assets and llm_support last and run both checks (Note 31).
- [ ] Owner: commit (git add -A: the ten new manifests are untracked) and push; hosted runs; accept or redirect.

## Deliverables
- Ten manifests; the manifest-driven script and its tests; every workflow's Python request on a manifest or
  the helper pin; contract tests; the branch guide, CONTRIBUTING, tests system documents and a release-note line.

## Files / Paths Impacted
- .github/python/tests/3.14.0.toml ... 3.14.8.toml (new) and .github/python/speed/3.14.7.toml (new)
- .github/scripts/python_runtime_matrix.py
- .github/workflows/test-runtime.yml, release-candidate.yml, build-distributions.yml
- .github/workflows/build-repo-assets.yml, build-src-assets.yml, ci.yml, docs.yml, python-publish.yml,
  verify-source-qualification.yml
- .github/workflows/real-world-gauntlet.yml, persistent-runtime-gauntlet.yml, shallow-all-thread-scaling.yml
- tests/unit/github_workflows/test_python_runtime_matrix.py, test_workflow_contracts.py
- .github/BRANCH_WORKFLOW.md, CONTRIBUTING.md, release_docs/next_version_release.md
- context_compass/system_docs/tests_architecture.md, tests_components.md and their indexes
- src/melder/_build_assets manifests and llm_support bundles (regenerated)

## Validation
- 2026-10-05, device VM, CPython 3.14.7t, pytest 9.1.1, PyYAML 6.0.3 (Notes 28-31):
  - tests/unit/github_workflows: 498 passed; nine mutations each caught and restored byte for byte.
  - Scratch cell install (manifest-only venv): 13,600 tests collected, workflow suite 498 passed.
  - speed-install with real pip: exit 0 in 46 s, only dependency-injector from source; GIL build refused.
  - Build assets rebuilt, --check OK; llm_support rebuilt, --check --include-untracked OK (three lines).
- Not run: the hosted workflows (27 runtime cells, the RC matrix, the three speed jobs), the Windows and macOS
  dependency-injector source builds, and a tracked-only llm_support --check before the manifests are committed.

## Risks / Rollback Notes
- Risk: dependency-injector's source build on the Windows (MSVC) and macOS (clang) runners is UNKNOWN until
  the hosted speed jobs run; Linux built in 46 s.
- Risk: no Python release runs without a manifest, by design; adding 3.14.9 or 3.15 is a deliberate change.
- Risk: the editable Melder install still builds with isolation, fetching setuptools within pyproject's range,
  as uv sync did before.
- Rollback: restore the workflows, script, tests and docs from git and delete .github/python/.

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

- DATETIME: 2026-10-04T23:12:37Z
  TYPE: DECISION
  CLAIM: Owner (chat, 2026-10-04 ~23:00Z): "we want tests to be 314 and we can test every minor version ... I
    don't want the gauntlet and all that other shit running on all the versinos just the latest one ... update
    the workflows to test all minor version since 314"; then "do the rest o the changes for the cicd
    workflows". Reading: the required runtime tests keep every stable minor from 3.14 at its newest patch
    (already true, Note 1, to be re-checked against the live manifest); the three speed tests leave the 3.14.7
    pin and run once, on the newest stable Python, still only for dev -> preprod. Whether a brand-new minor
    (3.15) should take the speed tests on its first day depends on the benchmarked libraries running on it:
    UNKNOWN until checked.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:74-115
  - .github/workflows/real-world-gauntlet.yml:57-62
  IMPACT: Answers the open question of Note 6; the boundary grows to the three speed-test workflows.
  NEXT: Run the matrix discovery against the live manifest and list the speed tests' third-party libraries.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:46:46Z
  TYPE: MEASURE
  CLAIM: Discovery run on the device VM against the live actions/python-versions manifest: floor (3, 14, 0);
    newest stable 3.14.8; 3.15.0 is still a release candidate (rc.2), so the runtime matrix is [3.14.8] today
    and 3.15 joins it with no edit once 3.15.0 is marked stable. 'Test every minor from 3.14' is therefore
    already the required runtime matrix (Note 1); nothing in discovery or test-runtime.yml changes.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:30-44
  - .github/scripts/python_runtime_matrix.py:74-115
  IMPACT: The owner's request reduces to the three speed tests.
  NEXT: Decide how 'the latest one' maps onto the speed tests' setup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:46:46Z
  TYPE: DECISION
  CLAIM: The speed tests ask setup-python for python-version '3.14' with check-latest true (the newest stable
    3.14 patch, 3.14.8 today, the same patch the matrix runs) and assert a final 3.14 release instead of
    (3, 14, 7). They do not follow a new minor automatically: each installs pinned third-party benchmark
    libraries wheels-only (--only-binary=:all:), and whether those publish free-threaded wheels for 3.15 on
    its release day is UNKNOWN, so an automatic jump could fail the dev-to-preprod gate. Moving them to 3.15 is
    one edit per workflow (setup and assertion), which the contract test keeps in step. Still single-version,
    no Python matrix, dev-to-preprod only.
  EVIDENCE:
  - .github/workflows/real-world-gauntlet.yml:55-80
  - .github/workflows/real-world-gauntlet.yml:128-128
  - .github/workflows/persistent-runtime-gauntlet.yml:60-63
  - .github/workflows/shallow-all-thread-scaling.yml:59-62
  IMPACT: Today 'the latest' is exact; the 3.15 move stays a deliberate one-line step, which the owner can
    overrule.
  NEXT: Edit the three workflows, the contract test and the branch guide; run tests/unit/github_workflows.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:59:15Z
  TYPE: FACT
  CLAIM: Applied: the three speed tests ask for python-version '3.14' with check-latest true and assert
    sys.version_info[:2] == (3, 14) and a final release level instead of (3, 14, 7). The contract test now
    refuses any literal exact-patch request in any workflow, and a new parametrized test checks each speed test:
    no Python matrix, free-threaded, check-latest, a minor at or above the pyproject floor, and an in-script
    assertion of exactly that minor. Two older gauntlet/scaling tests that pinned '3.14.7' now expect '3.14'
    with check-latest. The branch guide's three 3.14.7 mentions are replaced, and its version section says how
    to move the speed tests to a new minor.
  EVIDENCE:
  - .github/workflows/real-world-gauntlet.yml:59-60
  - .github/workflows/real-world-gauntlet.yml:129-129
  - tests/unit/github_workflows/test_workflow_contracts.py:118-170
  - .github/BRANCH_WORKFLOW.md:151-160
  IMPACT: The speed tests run the newest stable 3.14 patch (3.14.8 today), once each, dev-to-preprod only;
    the required runtime matrix keeps every stable minor from 3.14 unchanged.
  NEXT: Run the workflow suite and mutation checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-04T23:59:15Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t: python -m pytest tests/unit/github_workflows -q -p no:cacheprovider
    -o addopts="" gave 480 passed. Mutations of persistent-runtime-gauntlet.yml, each restored byte for byte:
    asserting (3, 15) while asking for 3.14 failed the new speed-test check; re-pinning '3.14.7' failed both
    the no-pin check and the speed-test check. The hosted workflows run on the owner's next push.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:146-170
  IMPACT: The contract suite agrees with the edits and catches both drifts it was written for.
  NEXT: Assets and llm_support rebuild as the session's last write; then the owner pushes and accepts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:53:09Z
  TYPE: FACT
  CLAIM: Owner report (chat, about 01:43Z): the persistent gauntlet's install step failed on the ubuntu-24.04 and
    windows-2025 runners under Python 3.14.8 free-threaded with "No matching distribution found for
    dependency-injector==4.49.1" (pip install --only-binary=:all: of the pinned set). The owner reads it as a
    reason to pin versions per minor: the code must work on everything, the speed tests run against specific
    versions, and old minors are retired as the project moves on.
  EVIDENCE: .github/workflows/persistent-runtime-gauntlet.yml:65-86
  IMPACT: The dev-to-preprod speed tests cannot start on hosted runners.
  NEXT: Check which wheels dependency-injector publishes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T01:53:09Z
  TYPE: FACT
  CLAIM: PyPI JSON (read from the device VM): dependency-injector 4.49.1, its newest release (2026-06-18), ships
    wheels tagged cp38, cp39, cp310-abi3 and pp311 plus an sdist; none of its last six releases (4.48.0-4.49.1)
    ships a cp314t or abi3t wheel. Free-threaded 3.14 cannot load abi3 wheels, and wheel tags carry no patch
    number, so every free-threaded 3.14.x runner (3.14.7 included) fails this wheels-only install the same way;
    the move to 3.14.8 (Notes 10-11) did not cause it. All three speed-test workflows share the install command.
  EVIDENCE:
  - .github/workflows/real-world-gauntlet.yml:64-85
  - .github/workflows/persistent-runtime-gauntlet.yml:65-86
  - .github/workflows/shallow-all-thread-scaling.yml:64-85
  IMPACT: Pinning the Python patch cannot fix the install; the package has to be built from source on
    free-threaded Python, or left out.
  NEXT: Try the source build on free-threaded 3.14.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T01:53:09Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7 free-threaded venv, gcc 11.4: pip wheel --no-deps --only-binary=:all:
    --no-binary=dependency-injector dependency-injector==4.49.1 built dependency_injector-4.49.1-cp314-cp314t-
    linux_x86_64.whl in 39 s (the first attempt ran out of disk on the shared /sessions volume; TMPDIR pointed
    at /tmp fixed it). Installed with dishka 1.10.1 wheels-only, a Singleton smoke test passed under PYTHON_GIL=0
    with sys._is_gil_enabled() False; without PYTHON_GIL the import re-enables the GIL with a RuntimeWarning (the
    module declares no free-threading support). The three workflows set PYTHON_GIL=0 on the benchmark steps.
    Windows (MSVC) and macOS (clang) builds are UNKNOWN until a hosted run.
  EVIDENCE:
  - .github/workflows/persistent-runtime-gauntlet.yml:87-90
  - .github/workflows/real-world-gauntlet.yml:134-137
  IMPACT: Allowing a source build for that one package makes the install work; everything else stays
    wheels-only.
  NEXT: Ask the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T01:53:09Z
  TYPE: DECISION_REQUEST
  CLAIM: Two changes, recommended together: (1) add --no-binary=dependency-injector to the three install commands
    so pip builds only that package from source, plus a contract test; (2) the owner's per-minor pin for the speed
    tests: python-version '3.14.8' exact without check-latest and an in-script assertion of (3, 14, 8), with the
    contract tests changed from "no exact pins anywhere" to "speed tests pin one exact stable patch, every other
    job floats with check-latest"; the required runtime matrix keeps the newest patch of every supported minor.
  EVIDENCE:
  - tests/unit/github_workflows/test_workflow_contracts.py:118-170
  - .github/scripts/python_runtime_matrix.py:74-115
  IMPACT: (1) unblocks the speed tests; (2) makes their numbers comparable run to run, bumped on purpose.
  NEXT: Owner answers; then implement, run the workflow suite, rebuild llm_support last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:29:46Z
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Owner (chat, about 02:00Z) asks for the best overall setup: speed-test workflows pinned by Python version,
    comparison libraries pinned too (older versions acceptable, since the measurement is relative), and still
    reads the failure as a Python-version problem. Objective: correctness proven on every supported Python;
    benchmark numbers comparable run to run. Known: the failure is the missing cp314t wheel (Note 13), not the
    patch; runner images are already pinned (ubuntu-24.04, windows-2025, macos-15-intel); library pins exist but
    are pasted into all three workflows. Unknown: the dependency-injector source build on the Windows and macOS
    runners. Recommendation: two rules. Tests float (newest patch of every supported minor, as today). Speed tests
    freeze everything - exact free-threaded Python 3.14.8, exact library versions kept in one file all three
    workflows read, pinned runners - and compare libraries within one job, so only Melder's code moves; pins are
    bumped on purpose in one change, and the first run after a bump is the new baseline. dependency-injector is
    built from source at its pinned version; everything else stays wheels-only. A new minor moves the speed tests
    in one change once the competitors install on it.
  EVIDENCE:
  - .github/workflows/persistent-runtime-gauntlet.yml:37-63
  - .github/workflows/persistent-runtime-gauntlet.yml:65-86
  - .github/scripts/python_runtime_matrix.py:74-115
  IMPACT: Supersedes the speed-test half of Notes 10-11 (newest 3.14 patch) once the owner agrees.
  NEXT: Owner says go; then implement the source build, the exact pin, the shared pins file, contract tests,
    branch guide, and rebuild llm_support last.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:44:02Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 10:35Z): "pin all speed tests to 3.14.7 then ensure that the tests are done on all minor
    versions ... moving to 3.14.8 might not be possible for most people and if they do they need to test it".
    The owner's "minor" here is the patch release (3.14.x). Reading: the required runtime tests (and the release
    candidate's install matrix, which reuses discovery) run every stable release at or above the floor, not only
    the newest patch per minor, because a user's other dependencies can hold them on an older 3.14 patch; the three
    speed tests pin exactly 3.14.7 free-threaded and install dependency-injector from source (Notes 13-15).
    Supersedes Note 16's 3.14.8 pin and the newest-patch-only rule of Notes 1 and 10.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:57-110
  - .github/workflows/release-candidate.yml:18-40
  - .github/workflows/release-candidate.yml:108-135
  IMPACT: The runtime matrix grows from 3 to 27 jobs today (9 releases x 3 platforms) and keeps growing until the
    owner raises the floor; the speed tests become reproducible and installable.
  NEXT: Check every 3.14 release for free-threaded assets, then read the matrix tests and plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T10:44:02Z
  TYPE: MEASURE
  CLAIM: Live actions/python-versions manifest, read with the repository's own fetch_manifest on the device VM:
    stable 3.14.0 through 3.14.8 (nine releases) all publish free-threaded assets for linux x64, win32 x64 and
    darwin arm64; 3.15.0 is still a release candidate (rc.3). Current discovery returns 3.14.8 on the three
    runners only.
  EVIDENCE: .github/scripts/python_runtime_matrix.py:74-110
  IMPACT: Every-release discovery can stay fail-closed on missing free-threaded assets: today nothing is missing.
  NEXT: Read tests/unit/github_workflows/test_python_runtime_matrix.py and the speed-test contract tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:46:42Z
  TYPE: PLAN
  CLAIM: python_runtime_matrix.py: discover_matrix selects every stable release at or above the floor, requires the
    floor release itself, and keeps refusing any selected release without free-threaded assets on a required
    platform; version_matrix allows several patches of one minor and refuses an empty list, a repeated release,
    a release below the floor, a missing floor minor or an oversized matrix, each with its own message. Its tests
    follow (every-patch discovery, defective older patch, missing floor release, several patches per minor).
    The three speed tests (all-CRLF files) request '3.14.7' without check-latest, assert sys.version_info[:3] ==
    (3, 14, 7), and add --no-binary=dependency-injector to the wheels-only install; the contract tests change to
    "helpers float, speed tests pin one exact release, all three the same, matching their assertion", plus one
    ast-based test of the install flags; two older gauntlet tests expect '3.14.7'. Discovery step names say
    release instead of minor. The branch guide's three speed-test mentions and its version section are
    rewritten. Then the workflow suite, mutations, the llm_support rebuild and --check.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:57-110
  - tests/unit/github_workflows/test_python_runtime_matrix.py:23-121
  - tests/unit/github_workflows/test_workflow_contracts.py:118-170
  - .github/BRANCH_WORKFLOW.md:141-166
  IMPACT: One change set moves the runtime matrix and the speed tests to the owner's policy.
  NEXT: Apply the edits.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:55:11Z
  TYPE: FACT
  CLAIM: Applied (Note 19 plan): discovery selects every stable release from the floor and requires the floor
    release; version_matrix allows several patches per minor with one message per refusal; the three speed tests
    pin '3.14.7' without check-latest, assert sys.version_info[:3] == (3, 14, 7), and build only
    dependency-injector from source; contract tests and the branch guide follow; discovery step names say release.
    Live manifest through the edited script: 27 jobs, 3.14.0-3.14.8 on the three runners.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:55-145
  - .github/workflows/persistent-runtime-gauntlet.yml:56-80
  - tests/unit/github_workflows/test_workflow_contracts.py:118-190
  IMPACT: Working tree matches the owner's 10:35Z directive.
  NEXT: Validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:55:11Z
  TYPE: MEASURE
  CLAIM: Device VM, CPython 3.14.7t, bytecode writes off: tests/unit/github_workflows gave 490 passed. Mutations,
    each restored byte for byte (cmp clean): a speed test back on '3.14' with check-latest failed the
    single-version and pin tests; dropping --no-binary=dependency-injector failed the install-flag test; an
    assertion of (3, 14, 8) against the 3.14.7 pin failed the pin test; the original newest-patch-only script
    failed six matrix tests. llm_support rebuilt (tests and other bundles) and --check printed three OK lines.
    The hosted runs are Not run.
  EVIDENCE: tests/unit/github_workflows/test_python_runtime_matrix.py:23-60
  IMPACT: The working tree is consistent and green here.
  NEXT: The owner's newer direction (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T10:55:11Z
  TYPE: DECISION_REQUEST
  CLAIM: Owner (chat, about 10:55Z, interrupting): no dynamic Python discovery at all; one concrete pinned "workflow
    file" per Python release, CI pytest ones in one folder and speed tests in another, each pinning its own
    dependencies (LogXide is likely to become Melder's first runtime dependency), and never the newest Python
    unless a file adds it. Constraint: GitHub Actions only loads workflow files placed directly in
    .github/workflows; "Subdirectories of the workflows directory are not supported" (GitHub docs, reusing
    workflows). Proposal: keep the workflow YAML at the top level and put one pin file per release in folders the
    workflows read without network (tests: one per release, 3.14.0-3.14.8; speed: one, 3.14.7), each holding that
    release's pinned dependencies; adding a release means adding a file, and nothing else runs. Manifest
    discovery is removed. Awaiting the owner's go-ahead; the every-release discovery above is superseded once
    they agree.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:15-66
  - .github/workflows/release-candidate.yml:18-40
  - pyproject.toml:5-10
  IMPACT: Replaces manifest discovery with an explicit, reviewed list and gives each release its own pins.
  NEXT: Owner confirms the folder-of-pin-files design (and whether the helper jobs pin 3.14.7 too); then
    implement.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T10:56:56Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: Owner asked whether CI can iterate over manifest files to build itself. Yes: the Note 22 proposal is that
    design. Only workflow YAML must sit directly in .github/workflows; manifests are data files a discovery step
    reads (no network) to build the matrix. Proposed shape: one TOML manifest per Python release (python version,
    free-threaded flag, exact dependency pins) under .github/python/tests/ and .github/python/speed/, parsed with
    tomllib like supported_floor already does; adding a release means adding a manifest.
  EVIDENCE: .github/scripts/python_runtime_matrix.py:30-45
  IMPACT: Clarifies the proposal; no repository change yet.
  NEXT: Owner's go-ahead on per-release TOML manifests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-05T10:59:24Z
  TYPE: DECISION
  CLAIM: Owner (chat, about 11:05Z): "yeah this makes sense do 3.14.0 -> 3.14.8 and for the speed test do only
    3.14.7". CI becomes manifest-driven: one TOML manifest per Python release under .github/python/tests/
    (3.14.0-3.14.8) and one under .github/python/speed/ (3.14.7); a local discovery step builds the runtime and RC
    matrices from the test manifests with no network lookup, each test cell installs exactly its manifest's pins,
    the speed tests read their single manifest, and single-version helper jobs pin 3.14.7 (owner's rule: never
    run the newest Python unless a manifest adds it). Supersedes Notes 1, 10-11 and 19-21's manifest discovery.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:93-145
  - .github/workflows/test-runtime.yml:15-90
  IMPACT: The boundary is all setup-python steps, the discovery script and its tests, the runtime and speed
    workflows, their contract tests and the branch guide.
  NEXT: Read every setup-python step, the uv.lock test pins and run_runtime_tests.py, then write the plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T11:02:16Z
  TYPE: PLAN
  CLAIM: (1) Manifests: .github/python/tests/3.14.0-3.14.8.toml and .github/python/speed/3.14.7.toml (python,
    freethreaded, exact dependency pins; build_from_source for dependency-injector in the speed manifest); test
    pins copy the uv.lock test-group closure (pytest 9.1.1, pytest-cov 7.1.0, coverage 7.16.1, PyYAML 6.0.3,
    iniconfig 2.3.0, packaging 26.3, pluggy 1.6.0, Pygments 2.21.0, colorama 0.4.6 on win32). (2)
    python_runtime_matrix.py drops the network manifest and gains load_manifest, discover (test manifests),
    speed (exactly one speed manifest) and requirements operations; coverage is unchanged. (3) test-runtime.yml
    cells install their manifest with uv pip --no-deps plus Melder editable instead of uv sync; discover and
    coverage pin 3.14.7. (4) release-candidate.yml and every helper setup pin 3.14.7 (no check-latest, no
    python-version-file). (5) Each speed workflow gets a manifest job; its benchmark job takes Python and pins from
    the speed manifest. (6) Contract and matrix tests, branch guide. (7) Validate here: suite, mutations, a scratch
    run of the cell install on 3.14.7t; llm_support last.
  EVIDENCE:
  - .github/workflows/test-runtime.yml:14-90
  - .github/workflows/persistent-runtime-gauntlet.yml:34-130
  - uv.lock:1-1
  IMPACT: Every Python CI uses is named in a manifest or is the one helper pin.
  NEXT: Write the manifests and the discovery script.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:14:30Z
  TYPE: FACT
  CLAIM: Applied (Note 25 steps 1-4): nine test manifests (3.14.0-3.14.8, the uv.lock test-group pins, colorama
    marked win32) and one speed manifest (3.14.7, the benchmark pins, build_from_source = dependency-injector).
    python_runtime_matrix.py reads them locally: load_manifest validates file name, keys, free-threading, exact
    unique pins and source builds; discover needs the floor release's manifest and refuses one below it; speed
    needs exactly one manifest; requirements writes one cell's pins. Its 57 tests passed before compaction. After
    the compaction, before re-onboarding (a gate deviation, recorded here), one edit pass: the pyproject
    dependency check parses names with a regex; the 13 helper setups and build-distributions' and test-runtime's
    python-version-file setups now ask for "3.14.7" with no check-latest; test-runtime cells write their
    manifest's pins and install them with uv pip --no-deps plus Melder editable, the uv cache keyed on the
    manifest; the runtime and candidate discovery steps are renamed.
  EVIDENCE:
  - .github/python/tests/3.14.0.toml:1-16
  - .github/python/speed/3.14.7.toml:1-17
  - .github/scripts/python_runtime_matrix.py:123-238
  - .github/scripts/python_runtime_matrix.py:312-359
  - .github/workflows/test-runtime.yml:20-72
  - .github/workflows/test-runtime.yml:125-130
  - .github/workflows/release-candidate.yml:24-32
  - tests/unit/github_workflows/test_python_runtime_matrix.py:129-160
  IMPACT: The runtime matrix and every helper job no longer read the network for Python; the speed workflows,
    their contract tests and the branch guide still describe the interim inline pins.
  NEXT: Read the three speed workflows and the contract tests, then move the speed tests onto their manifest.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:28:30Z
  TYPE: FACT
  CLAIM: Applied (Note 25 steps 5-6): python_runtime_matrix.py gains speed-install, which installs the speed
    manifest's pins into the running interpreter only when it is that manifest's free-threaded release (pip
    --only-binary=:all: first, then --no-binary per build_from_source entry, --report, -r) and keeps
    requirements.txt, install.log and install-report.json in the benchmark's results directory. The three speed
    workflows gain a manifest job (helper Python, the speed operation, output python); the benchmark job needs
    it, sets SPEED_PYTHON, sets up that release free-threaded, installs through speed-install instead of the
    inline pins, and its provenance asserts platform.python_version() against SPEED_PYTHON. The runtime discover
    job is renamed. Contract tests: three speed/setup tests replaced (manifest-or-helper rule; Python from the
    speed manifest; install into the evidence directory), the locked-install test split into the locked build
    and the per-release cell install, five setup assertions follow the new sources. Six new matrix tests.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:245-302
  - .github/scripts/python_runtime_matrix.py:376-418
  - .github/workflows/persistent-runtime-gauntlet.yml:34-87
  - .github/workflows/real-world-gauntlet.yml:130-130
  - tests/unit/github_workflows/test_workflow_contracts.py:118-197
  - tests/unit/github_workflows/test_workflow_contracts.py:397-447
  - tests/unit/github_workflows/test_python_runtime_matrix.py:134-216
  IMPACT: The speed tests now read their release and pins from one file; the inline pin lists are gone from
    all three workflows.
  NEXT: Run the workflow suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:28:30Z
  TYPE: MEASURE
  CLAIM: Device VM, $HOME/v314t (CPython 3.14.7 free-threaded, pytest 9.1.1, PyYAML 6.0.3), bytecode writes
    off: python -m pytest tests/unit/github_workflows -q -p no:cacheprovider -o addopts="" gave 498 passed
    (test_python_runtime_matrix.py alone: 63 passed). Mutations, the scratch cell install and the hosted runs
    are still to come; Windows and macOS speed installs are Not run.
  EVIDENCE: tests/unit/github_workflows/test_workflow_contracts.py:118-197
  IMPACT: The edits agree with the contract suite.
  NEXT: Rewrite the branch guide's version section and speed mentions, and the CI paragraph of CONTRIBUTING.md
    (it names uv sync --group test, which the cells no longer run).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:38:30Z
  TYPE: MEASURE
  CLAIM: Validation on the device VM. Nine mutations of the new rules, each restored byte for byte and each
    caught by its test: helper check-latest, a second helper release, a speed setup pinned literally, a benchmark
    job without needs, install outside the evidence folder, the provenance assertion removed, a cell install with
    dependency resolution, --no-binary before --only-binary, any interpreter accepted. Scratch copy in /tmp of
    the 3.14.7 cell (uv 0.12.13, CPython 3.14.7t): the requirements op wrote 9 pins, uv pip --no-deps installed
    8 (colorama skipped by its marker) plus Melder editable, pytest collected 13,600 tests with no error, and
    tests/unit/github_workflows passed 498 in that manifest-only venv. speed-install with real pip 26.2.1 on
    3.14.7t: exit 0 in 46 s, dependency-injector from its sdist and the other seven as wheels (install report),
    requirements.txt, install.log and install-report.json written; on the GIL build it refused with exit 1 and
    wrote nothing. discover and speed on the repository manifests: 27 cells, python=3.14.7. Scratch removed.
    Windows and macOS installs and every hosted run are Not run.
  EVIDENCE:
  - .github/scripts/python_runtime_matrix.py:245-302
  - .github/workflows/test-runtime.yml:65-72
  - .github/python/speed/3.14.7.toml:1-17
  IMPACT: The cell install and the speed install work end to end on Linux; the contract suite catches each drift
    it was written for.
  NEXT: Record the documentation pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-05T11:38:30Z
  TYPE: DECISION
  CLAIM: Documentation the change made false is updated in the same pass rather than left stale: the branch
    guide's runtime-tests bullet, both speed-test mentions, its Supported Python versions section (manifest
    format, the two folders, how to add a release or move the speed tests, helper pin, discovery refusals) and
    its uv.lock paragraph; CONTRIBUTING.md's CI paragraph (it named uv sync --group test); the tests system
    documents' CI entrypoint, qualification flow and the per-run-matrix UNKNOWN (now RESOLVED: the manifests
    name every release), with C1 extents of test-runtime.yml, test_workflow_contracts.py and
    test_python_runtime_matrix.py remeasured and both indexes regenerated (index --check OK for all four
    system documents); one Packaging-and-documentation line in the running release note. Other github_workflows
    C1 extents in tests_components (for example test_ci_policy.py, 511 recorded, 557 now) were already stale
    from earlier lanes and are not remeasured here. No src/ change, so no notch.
  EVIDENCE:
  - .github/BRANCH_WORKFLOW.md:137-184
  - CONTRIBUTING.md:40-44
  - context_compass/system_docs/tests_architecture.md:181-189
  - context_compass/system_docs/tests_architecture.md:348-351
  - context_compass/system_docs/tests_components.md:132-135
  IMPACT: Readers of the guide, CONTRIBUTING and the system documents see the manifest-driven CI.
  NEXT: Rebuild the build assets and llm_support (with untracked files) and run both checks as the last write.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-05T11:42:00Z
  TYPE: MEASURE
  CLAIM: Last write of the change set, device VM, CPython 3.14.7t, git with GIT_OPTIONAL_LOCKS=0 (no index lock
    left): the build-asset runner wrote its three manifests at v0.2.8227 in 51 s and --check printed three OK
    lines; llm_support/_builder.py --include-untracked left src unchanged and rewrote tests and other, and --check
    --include-untracked printed three OK lines. The tracked-only --check fails for other until the ten new
    manifests are committed; they are the only untracked files besides the Codecov ticket, which the bundles
    exclude. No version notch: nothing under src/ changed.
  EVIDENCE: llm_support/_builder.py:300-349
  IMPACT: Assets and bundles are current for the working tree; git add -A makes the CI check pass.
  NEXT: Owner commits (git add -A) and pushes, runs the hosted workflows, and accepts or redirects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Review (Notes 24-31): CI is manifest-driven. .github/python/tests/ holds one manifest per release (3.14.0-3.14.8,
the uv.lock test pins); discovery builds the 27-cell matrix from them with no network lookup and each cell
installs exactly its pins plus Melder with uv pip --no-deps. .github/python/speed/3.14.7.toml drives the three
speed tests through a manifest job and the speed-install operation (dependency-injector built from source).
Every helper setup pins 3.14.7; nothing uses check-latest or a version file. Contract suite 498 passed with nine
mutations caught; Linux scratch installs pass; docs, system documents, assets and llm_support are current
(--include-untracked). Owner-owed: git add -A (the ten manifests are untracked), push, the hosted runs
(including the Windows and macOS source builds) and acceptance.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
