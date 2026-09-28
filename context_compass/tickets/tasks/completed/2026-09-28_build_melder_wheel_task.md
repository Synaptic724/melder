# Task: Build and install the current Melder wheel

## Metadata
- Task ID: TASK-2026-09-28-build-melder-wheel
- Story: none; standalone packaging task
- Status: done
- Owner: codex
- Agent Name: workflows_0
- Created: 2026-09-28T08:46:50Z
- Updated: 2026-09-28T08:54:31Z

- Completed: 2026-09-28T08:54:31Z
- Summary: Built 0.2.8206 wheel and installed it into the explicitly selected CommandOps environment.

## Objective
Build the current wheel and install it into the owner-selected priv_commandops/.venv314 environment.

## Ticket Contract
- ENTRY_GATE: Existing onboarding/certification remains valid; owner explicitly requests a wheel.
- EXECUTION_BOUNDARY: Packaging configuration reads, generated-asset verification, wheel build under
  dist/, installation into the owner-selected priv_commandops/.venv314, and this task's records.
- DEPENDENCIES: Python 3.14 and the configured setuptools build backend.
- EXIT_GATE: Wheel exists, archive policy/version checks pass, and an isolated import confirms
  version 0.2.8206 inside the exact environment the owner selected.
- FAILURE_ESCALATION: Record build/verification failures; preserve prior wheels and avoid publishing.

## Scope Boundaries
- In scope: build current source, validate the produced artifact, preserve packaging logs.
- Out of scope: source changes, version bump, release cut, commit/tag or package publication.

## State Transition Event
- from_state: ready
- to_state: done
- transition_reason: Requested wheel built and installed; isolated import confirms the target and version.

## Steps / Checklist
- [x] Verify local build tooling and generated assets.
- [x] Build wheel with the repository's setuptools backend.
- [x] Verify wheel archive policy and install/import in priv_commandops/.venv314.
- [x] Deliver the built wheel and verified target installation.

## Deliverables
- dist/melder-0.2.8206-py3-none-any.whl (version rechecked at build time).
- Build and verification evidence under artifacts/wheel_build_20260928/.

## Validation
- Wheel-only archive verifier passed for 0.2.8206. Target pip upgraded 0.2.82 to 0.2.8206.
- Target Python -I imported melder from priv_commandops/.venv314/Lib/site-packages and asserted 0.2.8206.
- Extra runtime smoke tests were not run; the owner directed immediate installation and import verification.

## Risks / Rollback Notes
- The shared working tree contains uncommitted work; the wheel represents current local source.
- Existing dist/melder-0.2.54-py3-none-any.whl is preserved.
- Packaging-only work takes no version notch.

## Applicable Anti-Patterns
- No upload or source changes under a local wheel request.
- No success claim before the artifact and isolated import are verified.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/wheel_build_20260928/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain packaging evidence and the delivered wheel after completion.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record build and verification outcomes before delivery.

## Notes
- DATETIME: 2026-09-28T08:46:50Z
  TYPE: FACT
  CLAIM: Current source version is 0.2.8206. pyproject configures setuptools.build_meta and Python >=3.14;
    CI builds with python -m build --no-isolation. dist contains only the older 0.2.54 wheel.
  EVIDENCE:
  - src/melder/__version__.py:12-12
  - pyproject.toml:1-12
  - .github/workflows/build-distributions.yml:50-67
  IMPACT: Build the current version without replacing the older wheel or changing source.
  NEXT: Verify build dependencies/assets, then build the wheel.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T08:46:50Z
  TYPE: FACT
  CLAIM: Local Python is 3.14.7 free-threaded, with build 1.6.1, setuptools 84.0.0 and wheel 0.48.0.
    All generated-asset checks pass at 0.2.8206. The repository already has build/lib and another
    agent's build staging directory; use a fresh task-owned source staging copy for this wheel.
    The existing distribution verifier exposes verify_wheel separately, so no sdist is required.
  EVIDENCE:
  - context_compass/artifacts/wheel_build_20260928/assets_check.log:1-3
  - .github/scripts/verify_distributions.py:83-122
  - .github/scripts/smoke_wheel.py:38-83
  IMPACT: Build offline with installed tooling, preserving existing build outputs and other agents' files.
  NEXT: Copy canonical packaging inputs into fresh staging and build only the wheel into dist/.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T08:50:00Z
  TYPE: FACT
  CLAIM: The build frontend cannot write pyproject_hooks input.json inside its own newly created
    temporary directory under the restricted Windows token. Redirecting TEMP/TMP to task-owned
    workspace storage produces the same PermissionError. Canonical sources remain untouched.
  EVIDENCE:
  - context_compass/artifacts/wheel_build_20260928/build.log:1-25
  - context_compass/artifacts/wheel_build_20260928/build_retry.log:1-25
  IMPACT: A bounded local build with ordinary filesystem access is needed; no downloads or publication.
  NEXT: Retry the authorized wheel build outside the restricted token, then verify the resulting wheel.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-28T08:54:31Z
  TYPE: MEASURE
  CLAIM: The owner explicitly requested installation into priv_commandops/.venv314, then directed
    immediate installation. Wheel verification passed and target pip successfully replaced 0.2.82
    with 0.2.8206 using --no-index --no-deps. A fresh target Python -I process confirmed 0.2.8206
    and the exact target site-packages import path. No application source or other dependencies changed.
  EVIDENCE:
  - context_compass/artifacts/wheel_build_20260928/install.log:1-8
  - context_compass/artifacts/wheel_build_20260928/assets_check.log:1-3
  IMPACT: Both the wheel and requested environment installation are complete.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Built dist/melder-0.2.8206-py3-none-any.whl (3,220,056 bytes) from fresh source staging.
Archive/version checks passed. Installed into C:/Users/Mark/PycharmProjects/priv_commandops/.venv314,
upgrading Melder 0.2.82 to 0.2.8206. Isolated import confirmed exact version and target site-packages.
No source changes, version bump or publication. Windows temporary-directory ACLs required the
standard build/install commands to run with ordinary filesystem access. No remaining work.
