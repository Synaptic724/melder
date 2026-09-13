# Task: Build Melder 0.2.40 wheel for CommandOps

## Metadata
- Task ID: TASK-2026-09-13-build-commandops-local-wheel
- Story: none
- Status: review
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-13T16:38:44Z
- Updated: 2026-09-13T16:42:22Z

## Objective
Produce a local Melder 0.2.40 wheel containing the current fixes for the owner to move into CommandOps.

## Ticket Contract
- ENTRY_GATE: Owner explicitly authorizes local build using the existing 0.2.40 version.
- EXECUTION_BOUNDARY: Existing build runners, local wheel output, package verification and isolated smoke.
- DEPENDENCIES: Current source/build assets; .venv_new Python 3.14.7 free-threaded with build installed.
- EXIT_GATE: Wheel exists, metadata/packaged assets match 0.2.40, and isolated import/DI smoke passes.
- FAILURE_ESCALATION: Record build or validation failures; do not change runtime or package version silently.

## Scope Boundaries
- In scope: local wheel build and validation, evidence and a user-accessible output path.
- Out of scope: publishing, CommandOps installation, named lesser implementation, 0.2.50 version change.

## State Transition Event
- from_state: ready
- to_state: review
- transition_reason: Wheel built, archive verified and isolated installed-wheel smoke passed.

## Steps
- [x] Read packaging/version configuration and existing distribution verifier.
- [x] Verify generated assets and build one wheel from current source.
- [x] Verify contents/version and smoke-test the wheel independently of the source checkout.
- [x] Record evidence and deliver the wheel path.

## Deliverables
- dist/melder-0.2.40-py3-none-any.whl

## Validation
- PASS: build runners, existing verify_wheel policy and exact default-precedence source byte comparison.
- PASS: isolated uv-installed wheel with Python 3.14.7 free-threaded; metadata/documents/graph/runtime.
- Disposable probe environment removed after successful verification. No CommandOps installation performed.

## Risks / Rollback Notes
- Use the existing 0.2.40 source version; preserve unrelated working-tree edits.
- No package publication, external repository writes or dependency changes.

## Applicable Anti-Patterns
- [x] Do not publish or install into CommandOps as part of this local build request.
- [x] Verify the archive itself, not an editable-source import.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/commandops_local_wheel_20260913/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Keep wheel and build evidence for owner transfer/review.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record build identity, evidence and the next concrete action in this task.

## Notes
- DATETIME: 2026-09-13T16:38:44Z
  TYPE: FACT
  CLAIM: Current canonical version is 0.2.40; pyproject reads that literal through setuptools.
    Owner confirmed this version and deferred named-conduit work/version 0.2.50 until after this build.
    The existing verify_wheel function checks archive boundaries, metadata and bundled manifest versions.
  EVIDENCE:
  - src/melder/__version__.py:1-12
  - pyproject.toml:135-143
  - .github/scripts/verify_distributions.py:83-114
  - Owner's version confirmation and wheel-only instruction in this conversation.
  IMPACT: Build the current checkout with no version change or unrelated feature work.
  NEXT: Verify build assets, then produce the wheel with the existing build backend.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10


- DATETIME: 2026-09-13T16:39:25Z
  TYPE: BLOCKER
  CLAIM: Both build-asset checks pass at 0.2.40. The standard wheel frontend failed before backend
    work because the sandbox could not write input.json in Python's freshly created temp directory.
  EVIDENCE:
  - artifacts/commandops_local_wheel_20260913/build.log:1-40
  IMPACT: No wheel was produced. This is a filesystem-access failure rather than a package build error.
  NEXT: Retry the same authorized local build with sandbox escalation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:40:24Z
  TYPE: MEASURE
  CLAIM: The standard build succeeds with filesystem access and produces
    dist/melder-0.2.40-py3-none-any.whl. Sandbox access also refuses reading the resulting wheel;
    archive verification and the isolated installed-wheel smoke must use the same access context.
  EVIDENCE:
  - artifacts/commandops_local_wheel_20260913/build_retry.log
  - .github/workflows/build-distributions.yml:63-74
  IMPACT: Build is complete; validation is pending. No package version or feature source changed.
  NEXT: Verify the archive and install only this wheel into a disposable probe environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T16:42:22Z
  TYPE: MEASURE
  CLAIM: Built dist/melder-0.2.40-py3-none-any.whl (3,088,864 bytes). Existing archive verification
    passes metadata/assets/version/boundaries; packaged default-precedence source matches checkout
    bytes. Installed only that wheel with uv --no-deps --no-index into a disposable environment;
    the repository smoke passes under -I and verifies the actual site-packages import, documents,
    graph and public bind/conjure/meld/reuse/cleanup. Probe environment removed; logs/wheel retained.
  EVIDENCE:
  - artifacts/commandops_local_wheel_20260913/wheel_verification.txt:1-5
  - artifacts/commandops_local_wheel_20260913/smoke.log:1-1
  - artifacts/commandops_local_wheel_20260913/build_retry.log
  IMPACT: Transferable local wheel is ready. SHA256:
    13762e8f273d9fcb37772d0b68c50bbeb13101b83c2e38e2d1e7b89869b5b943.
    Version stays 0.2.40. No publication, CommandOps modification or feature implementation occurred.
  NEXT: Owner moves the wheel into CommandOps; revisit named lesser conduits afterward for 0.2.50.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Verified wheel delivered at dist/melder-0.2.40-py3-none-any.whl. Archive and isolated installed-package
smoke passed; build/probe evidence retained in the linked artifact folder. Named lesser conduits and
ConduitCloud work are explicitly deferred until afterward; owner plans version 0.2.50 for that change.