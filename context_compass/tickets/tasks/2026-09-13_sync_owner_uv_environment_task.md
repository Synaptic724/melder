# Task: Sync the owner's existing environment from uv.lock

## Metadata
- Task ID: TASK-2026-09-13-sync-owner-uv-environment
- Story: none
- Status: review
- Owner: codex
- Agent Name: workflows_1
- Priority: p2
- Created: 2026-09-13T20:41:52Z
- Updated: 2026-09-13T20:48:32Z

## Objective
Apply the repository lock to the owner's existing .venv_new and install the current Melder checkout,
retaining its free-threaded interpreter and extra installed tools.

## Ticket Contract
- ENTRY_GATE: Owner explicitly requested syncing their environment; existing certification applies.
- EXECUTION_BOUNDARY: .venv_new package installation, task-owned validation artifacts and ticket/board state.
- DEPENDENCIES: Existing uv.lock and contributor setup from the reproducible_uv_environment task.
- EXIT_GATE: Locked sync and dependency consistency checks pass; Melder 0.2.40 imports from this checkout
  under Python 3.14.7 with the GIL disabled; extra installed packages are preserved.
- FAILURE_ESCALATION: Record stale-lock or install failures; do not regenerate dependencies or replace
  the interpreter, lockfile, user source changes or unrelated environments to force success.

## Scope Boundaries
- In scope: user-authorized sync of .venv_new using current locked dependency groups.
- Out of scope: source/workflow/lock changes, Python upgrade, other environments, commits or publication.

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: Locked sync, package preservation, dependency compatibility and no-GIL import
  checks passed. The owner's editor Ruff server needs restarting after its executable was unlocked.

## Steps / Checklist
- [x] Identify the active repository environment, interpreter and installed package groups.
- [x] Record the current package inventory and inspect the locked sync dry-run.
- [x] Sync the selected environment with all existing optional groups and preserve unrelated extras.
- [x] Verify lock/environment consistency, installed Melder version and no-GIL import.

## Deliverables
- .venv_new synchronized to repository dependencies and editable Melder 0.2.40.
- Local before/after inventory, sync output and validation record.

## Files / Paths Impacted
- .venv_new/
- context_compass/artifacts/uv_environment_sync_20260913/
- This task and its attention/artifact board routes.

## Validation
- Preflight confirms Python 3.14.7 free-threaded, Py_GIL_DISABLED=1, GIL off and uv 0.12.13.
- Forty installed distributions include every optional group; Melder distribution metadata is absent.
- Locked all-group sync completed; twelve tooling versions upgraded and editable Melder 0.2.40 installed.
- A second offline sync --check reports no changes; uv pip check reports all 41 packages compatible.
- All forty prior package names remain installed. No extra tool was removed.
- Melder imports from src/melder under Python 3.14.7 free-threaded with GIL off and no Requires-Dist.
- pyproject.toml, uv.lock and .venv_new/pyvenv.cfg hashes are unchanged.
- pytest, Ruff, build and mypy command launchers execute successfully. Full test suite not run for this sync.

## Risks / Rollback Notes
- --inexact retains extra installed tools; selected groups still use locked dependency versions.
- Record existing package versions before mutation so any changed versions are explicit.
- Keep the current interpreter and environment path; fail rather than creating a replacement.

## Applicable Anti-Patterns
- [x] No guessed environment or interpreter selection.
- [x] No removal of unrelated packages as a side effect of default exact sync.
- [x] No successful-sync claim without post-install evidence.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/uv_environment_sync_20260913/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Keep the compact validation record and package inventories for environment support.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
- Record the install plan and executed result before progressing between mutation and validation.

## Notes
- DATETIME: 2026-09-13T20:41:52Z
  TYPE: DECISION
  CLAIM: Owner requested applying the new setup to their environment. .venv_new already uses
    uv-managed Python 3.14.7 free-threaded; all optional group tools are installed. Use --locked
    --all-groups --inexact against that exact environment/interpreter to align declared dependencies,
    install editable Melder 0.2.40 and retain extra tooling. No Python upgrade is needed.
  EVIDENCE:
  - .venv_new/pyvenv.cfg:1-5
  - src/melder/__version__.py:1-11
  - CONTRIBUTING.md:8-55
  - tickets/tasks/completed/2026-09-12_bind_conjure_order_benchmark_task.md:226-255
  IMPACT: This is explicit new permission to change the owner's environment; earlier CI work left it alone.
  NEXT: Capture the package inventory and inspect uv's dry-run before installation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:41:52Z
  TYPE: MEASURE
  CLAIM: The locked dry-run resolves all 28 packages, targets .venv_new and proposes twelve version
    upgrades plus editable Melder. Every uninstall is paired with the replacement version; no
    extra installed package is scheduled for removal. Captured all forty pre-sync distributions
    and hashes of pyproject.toml, uv.lock and the environment's interpreter configuration.
  EVIDENCE:
  - artifacts/uv_environment_sync_20260913/dry-run.log:1-30
  - artifacts/uv_environment_sync_20260913/before.json:1-173
  IMPACT: The install plan matches the authorized environment update and preserves extra tooling.
  NEXT: Apply the identical locked sync without --dry-run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:41:52Z
  TYPE: FACT
  CLAIM: The first sync resolved the lock but could not download packages because the sandbox's
    network tunnel refused the connection (OS error 10061). Failure occurred during downloads.
    The requested mypy artifact correctly targets cp314t Windows AMD64.
  EVIDENCE:
  - artifacts/uv_environment_sync_20260913/sync.log:1-54
  IMPACT: Retry the same authorized installation with network access; do not alter the lock or groups.
  NEXT: Run locked sync through the sandbox escalation mechanism.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-13T20:45:53Z
  TYPE: FACT
  CLAIM: Network-enabled sync downloaded/built all thirteen packages, then Windows refused removal
    of ruff.exe because PID 51556 is this environment's long-running `ruff.exe server`. A second
    Ruff process belongs to priv_commandops and is outside scope. The failed uninstall phase already
    removed five distributions, so complete the prepared sync before considering the environment usable.
  EVIDENCE:
  - artifacts/uv_environment_sync_20260913/sync-network.log:1-15
  - artifacts/uv_environment_sync_20260913/before.json:1-173
  - Direct Win32_Process query: PID 51556, .venv_new/Scripts/ruff.exe, argument `server`.
  IMPACT: Stop only the identified project Ruff server, immediately retry sync and validate every
    pre-existing package remains installed. Do not stop the IDE or unrelated project processes.
  NEXT: Release the Ruff server's executable lock and finish the cached installation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-13T20:45:53Z
  TYPE: MEASURE
  CLAIM: After stopping only the verified Ruff server, the retry completed successfully: seven
    remaining old packages were uninstalled and all thirteen prepared packages installed, including
    editable Melder 0.2.40. The sync retained the selected interpreter and used the unchanged lock.
  EVIDENCE:
  - artifacts/uv_environment_sync_20260913/sync-complete.log:1-23
  IMPACT: The interrupted install is repaired. Verify dependency consistency, complete inventory,
    source/lock/interpreter hashes and Melder's no-GIL import before reporting completion.
  NEXT: Execute post-install environment and import checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-13T20:48:32Z
  TYPE: MEASURE
  CLAIM: Offline locked sync --check makes no changes; uv pip check verifies all 41 package names.
    Before/after comparison confirms twelve upgrades, editable Melder added and no original package
    removed. Source import reports Melder 0.2.40 with GIL off on the unchanged 3.14.7 interpreter.
    Lock/project/interpreter-configuration hashes are unchanged; four tool launchers work.
  EVIDENCE:
  - artifacts/uv_environment_sync_20260913/verification.json:1-14
  - artifacts/uv_environment_sync_20260913/validation.md:1-25
  IMPACT: Environment sync is complete. Only the project Ruff server was stopped for its file lock;
    it has not restarted automatically, so the owner should restart that editor integration.
  NEXT: Owner resumes development and restarts Ruff in the editor.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
.venv_new is synchronized from the existing lock using --locked --all-groups --inexact. Editable
Melder 0.2.40 imports from this checkout on unchanged Python 3.14.7 free-threaded; GIL remains off.
Twelve tools were upgraded and all forty prior package names retained. Lock consistency, dependency
compatibility, import and launcher checks passed. No source, lockfile, CI, interpreter or commit changes.
Windows locked ruff.exe through this project's Ruff server; that server alone was stopped to finish
installation. It did not restart automatically. Restart the editor's Ruff integration to resume linting.
