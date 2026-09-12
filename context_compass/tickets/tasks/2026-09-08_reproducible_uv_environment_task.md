# Task: Add a reproducible uv development environment

## Metadata
- Task ID: TASK-2026-09-08-reproducible-uv-environment
- Story: none
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-08T10:55:34Z
- Updated: 2026-09-08T11:26:20Z

## Objective
Provide a generated uv.lock and clear commands for contributors and CI to reproduce repository
dependencies while preserving the dynamic OS/free-threaded Python matrix and zero runtime dependencies.

## Ticket Contract
- ENTRY_GATE: Existing owner certification, explicit uv lock request and this active board route.
- EXECUTION_BOUNDARY: uv.lock, dependency configuration/comments, contributor/install guidance,
  approved runtime/build CI integration, focused workflow tests and generated repository assets.
- DEPENDENCIES: Existing pyproject dependency groups, stable no-GIL matrix and separate docs lock.
- EXIT_GATE: Lock freshness, isolated group sync, workflow contracts and distribution checks pass;
  matrix selection remains authoritative, and published runtime dependency metadata stays unchanged.
- FAILURE_ESCALATION: Keep owner environments, unrelated working files, signing and publication intact.
  Do not silently remove dependency groups or downgrade requirements to make resolution pass.

## Scope Boundaries
- In scope: reproducible repository development/install tooling and applicable CI dependency installs.
- Out of scope: runtime API changes, adding runtime dependencies, commits/pushes/publication,
  replacing the separate locked documentation environment or modifying the owner's virtualenvs.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Locked contributor and CI flows are implemented; focused local validation passes.
  Owner review, signed commit and the first hosted matrix execution remain with the project owner.

## Steps / Checklist
- [x] Inspect current groups, install workflows, uv availability and package boundaries.
- [x] Generate a portable lock from public PyPI and document locked contributor commands.
- [x] Apply the approved CI integration scope without replacing the dynamic no-GIL matrix.
- [x] Verify fresh isolated environments, distribution boundaries and generated assets.

## Deliverables
- Generated root uv.lock and contributor guidance.
- Runtime and distribution CI consuming the lock with setup-python's exact selected interpreter.
- Local validation evidence and explicit rollout instructions.

## Validation
- uv 0.11.23: public-index lock generation, freshness check and fresh default-dev sync passed.
- CI-shaped test-group sync passed; 413 workflow tests passed in 3.77s on CPython 3.14.0 free-threaded.
- Build-only sync, wheel/sdist verification and isolated installed-wheel probe passed.
- Installed Melder metadata has no runtime Requires-Dist entries; local no-GIL checks passed.
- Linux x64 and macOS arm64 test-group resolution dry-runs passed; hosted execution was not run locally.
- A disposable stale-lock fixture failed with uv's explicit update-required error, as intended.
- Actionlint, scoped correctness Ruff, source assets, repository corpora and patch indexes passed.
- Final lock/corpus/index/whitespace checks passed at 2026-09-08T11:21:48Z; detailed evidence is linked below.
- Full runtime suite under the new CI environment: not run locally; the next hosted PR run supplies it.

## Risks / Rollback Notes
- Lockfile captures development tooling, not additional runtime dependencies for package consumers.
- All declared dependency groups resolve together; unsupported optional groups must be surfaced.
- Use a task-owned UV_PROJECT_ENVIRONMENT during validation, preserving existing environments.
- Revert this scoped lock/integration change together if the owner declines it.

## Applicable Anti-Patterns
- [x] No lockfile hand-authoring or private registry credentials/absolute local paths.
- [x] No dependency deletion, owner environment replacement or publication without authorization.
- [x] No successful-lock/sync/build claim without executed evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/uv_environment_20260908/
  - system_docs/patches/active/uv_environment_2026_09_08/architecture_patch.md
  - system_docs/patches/active/uv_environment_2026_09_08/architecture_patch_index.md
  - system_docs/patches/active/uv_environment_2026_09_08/component_patch_uv_setup.md
  - system_docs/patches/active/uv_environment_2026_09_08/component_patch_uv_setup_index.md
  - system_docs/patches/active/uv_environment_2026_09_08/code_description_patch_ci_lock.md
  - system_docs/patches/active/uv_environment_2026_09_08/code_description_patch_ci_lock_index.md
- DISPOSITION: Validation workspace delete_on_close; patch documents/indexes promote_to_documentation.
- CLEANUP_TRIGGER: After owner acceptance, remove task-owned environments/logs and retire the patch
  lane through the normal closure flow. Durable setup is in CONTRIBUTING.md and .github/BRANCH_WORKFLOW.md.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record resolution decisions, scope choice and validation results before the next work tranche.

## Notes
- DATETIME: 2026-09-08T10:55:34Z
  TYPE: FACT
  CLAIM: No root uv.lock exists. pyproject declares no runtime dependencies and has test/lint/build
    plus optional parallel/typecheck/codemod/benchmark groups. uv 0.11.23 is installed. Current
    runtime and distribution CI use pip with broad group requirements; docs has a separate lock.
  EVIDENCE:
  - pyproject.toml:68-135
  - .github/workflows/test-runtime.yml:58-62
  - .github/workflows/build-distributions.yml:40-43
  - docs/requirements.lock:1-32
  IMPACT: A universal root lock can reproduce contributor dependencies. CI use is a pending
    optional scope choice; lock generation and isolated validation can proceed independently.
  NEXT: Generate the public-index lock using the available free-threaded interpreter.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-08T11:01:53Z
  TYPE: MEASURE
  CLAIM: uv 0.11.23 generated revision-3 universal lock data for 28 packages from public PyPI.
    Fresh default-dev sync installed 15 packages, including editable Melder 0.2.37, into the task
    environment using CPython 3.14.0 free-threaded. The root lock entry intentionally has dynamic
    version metadata and an editable relative source; registry entries have explicit versions.
  EVIDENCE:
  - uv.lock:1-7
  - pyproject.toml:68-135
  IMPACT: Lock/sync succeeds without changing dependency declarations or user environments. The
    patch boundary maps to a minimum uv setting and contributor guide; validate using locked build
    tools and installed metadata. Optional CI scope has no response yet, so keep it separate.
  NEXT: Add the contributor-facing setup and execute its local validation commands.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-08T11:05:31Z
  TYPE: FACT
  CLAIM: Added the tested minimum uv version and contributor commands, plus a public README
    pointer. Default locked sync succeeds under normal project configuration. The isolated
    environment imports Melder 0.2.37 with Py_GIL_DISABLED=1, GIL off and no Requires-Dist entries.
    Local build guidance uses the locked build group without isolation; archive normalization
    remains part of the separate release workflow because it requires SOURCE_DATE_EPOCH.
  EVIDENCE:
  - CONTRIBUTING.md:1-65
  - pyproject.toml:134-141
  - .github/scripts/normalize_sdist.py:62-73
  IMPACT: Contributor setup is implemented. No CI preference response has arrived; CI changes
    remain outside this completed base setup rather than being assumed from silence.
  NEXT: Run focused tests and verify a wheel/sdist built from the locked environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-08T11:05:31Z
  TYPE: DECISION
  CLAIM: Owner explicitly selected CI lock use and reiterated matrix support. Preserve Python/OS
    discovery and freethreaded setup; pass each selected interpreter into locked uv sync. Runtime
    uses the test group/project, distribution building uses only the build group and no isolation.
    Commands run inside the synced environment. The separate docs lock and publication gates remain.
  EVIDENCE:
  - Owner: "Yes, use it in CI"; "make sure it allows for matrix shit to occur".
  - system_docs/patches/active/uv_environment_2026_09_08/code_description_patch_ci_lock.md:1-19
  - https://raw.githubusercontent.com/astral-sh/setup-uv/main/README.md
  IMPACT: The base environment already passed 411 workflow tests and wheel/sdist inspection.
    Map the CI patch to test-runtime.yml/build-distributions.yml and their contract tests; select uv
    from the project's minimum with the action's lowest strategy and isolate cache variants by job.
  NEXT: Implement the two CI workflows and regress locked installs plus preserved matrix semantics.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-08T11:05:31Z
  TYPE: FACT
  CLAIM: Runtime and distribution CI now install uv through the verified setup-uv release, resolve
    its minimum from pyproject, cache against uv.lock, and pass setup-python's exact interpreter
    path to locked sync. Runtime runs the synced test/project environment; builds use the isolated
    build group without backend re-resolution. Wheel probes install only the built wheel separately.
  EVIDENCE:
  - .github/workflows/test-runtime.yml
  - .github/workflows/build-distributions.yml
  - tests/unit/github_workflows/test_workflow_contracts.py
  IMPACT: The approved matrix remains authoritative and dependency versions are now shared with
    contributors. Added contract checks for selected interpreter, group scope and lock enforcement.
  NEXT: Validate both CI group installs, isolated wheel execution and the updated workflow contracts.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-08T11:05:31Z
  TYPE: MEASURE
  CLAIM: CI-shaped locked test sync installed exactly the test group plus Melder into a fresh
    free-threaded environment. All 413 workflow tests pass in 3.77s, including new assertions that
    uv consumes setup-python's exact matrix interpreter and --locked group scope. Actionlint and
    scoped correctness Ruff pass. Base dev environment previously passed 411 tests and archive checks.
  EVIDENCE:
  - artifacts/uv_environment_20260908/ci-workflow-tests.xml:1-1
  - tests/unit/github_workflows/test_workflow_contracts.py
  IMPACT: Runtime installation and matrix wiring are validated locally. Complete build-only sync,
    isolated wheel execution and foreign-platform resolution checks before handoff.
  NEXT: Verify the locked build and wheel-consumer flows independently of the development environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-08T11:17:02Z
  TYPE: MEASURE
  CLAIM: Locked build-only sync installed six tools and produced a verified wheel/sdist. A new
    wheel-only environment passed the isolated package/runtime probe. Linux x64 and macOS arm64
    test-group dry-runs succeeded. Lock audit confirms 27 public-index packages plus the relative
    editable root, with 321 HTTPS/hash-pinned artifacts. The first negative-lock fixture omitted
    the source version module and failed metadata preparation, so it is not stale-lock evidence.
  EVIDENCE:
  - artifacts/uv_environment_20260908/ci-build.log
  - artifacts/uv_environment_20260908/lock-audit.json:1-7
  - artifacts/uv_environment_20260908/stale-lock.log
  IMPACT: Core setup/build/matrix resolution passes. Repair only the disposable fixture's missing
    metadata inputs before claiming its refusal verifies --locked semantics.
  NEXT: Complete the stale-lock negative check, then refresh generated repository assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-08T11:17:02Z
  TYPE: MEASURE
  CLAIM: The repaired disposable fixture now refuses its intentionally stale lock with the exact
    uv --check update-required error. The real pyproject/lock were not modified by this negative
    check. Locked installs, build-only package verification, wheel isolation and platform plans pass.
  EVIDENCE:
  - artifacts/uv_environment_20260908/stale-lock.log:1-3
  - artifacts/uv_environment_20260908/ci-workflow-tests.xml:1-1
  IMPACT: Lock drift refusal is proven rather than inferred from a fixture setup error.
  NEXT: Register new source files for corpus discovery and regenerate/verify all affected assets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-08T11:26:20Z
  TYPE: MEASURE
  CLAIM: Final checks at 11:21:48Z passed for uv lock freshness, source assets, all repository corpora,
    the three patch indexes and git diff whitespace. Tests/other corpora were regenerated after
    registering CONTRIBUTING.md and uv.lock for corpus discovery. Final review confirms that each
    runtime matrix interpreter is passed into locked test sync and build tools remain group-scoped.
  EVIDENCE:
  - artifacts/uv_environment_20260908/validation.md:6-23
  - artifacts/uv_environment_20260908/ci-workflow-tests.xml:1-1
  - .github/workflows/test-runtime.yml:40-76
  - .github/workflows/build-distributions.yml:34-76
  - CONTRIBUTING.md:8-78
  IMPACT: Authorized implementation is ready for owner review and signing. The Python matrix is
    preserved; foreign-platform resolution is not presented as hosted test execution. Existing
    environments and unrelated files remain untouched, with no agent commit or publication.
  NEXT: Owner reviews and commits the changes, then checks the next hosted PR matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner explicitly approved uv.lock use in CI and required preserving the Python/OS no-GIL matrix.
Implemented uv.lock, minimum uv configuration, CONTRIBUTING.md, README/workflow guidance and locked
runtime/build installs. setup-python still chooses each matrix interpreter; uv receives its exact
path. Documentation retains its own lock and publication gates retain their final checks.
Validation passed: 413 workflow tests, fresh locked group installs, wheel/sdist verification,
isolated wheel probe, cross-platform resolution plans, stale-lock refusal, lint and generated assets.
Hosted matrix execution is pending the owner's next PR. Changes are uncommitted; uv.lock and
CONTRIBUTING.md have intent-to-add entries for corpus discovery, with no file content staged.
Ticket remains in review pending acceptance. No further implementation is required by this task.
