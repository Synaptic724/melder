# Release candidate workflow validation

Canonical task: tickets/tasks/2026-09-05_release_candidate_testpypi_workflow_task.md.

This task-owned directory holds disposable test scratch, local package builds, and validation logs.
Results are summarized in the task. No package upload or commit/push is part of local validation.

Final local validation:
- 263 focused tests pass (focused.xml).
- All eight workflows pass actionlint 1.7.12; optional shellcheck/pyflakes disabled.
- Correctness Ruff E4/E7/E9/F passes.
- Snapshot source: 81e62df62c67978fa9d06d909f803c61b9f332b0, with regenerated snapshot assets.
- Real wheel/sdist verification and isolated Windows Python 3.14t runtime/data probe pass.
- Two real sdist builds have unchanged member payloads. Metadata normalization makes their SHA256
  identical: A9ED1747F199CE9A3AF3B3DF4073EABDEFC1D9C942DDE9149F24A9C8031A0E9A.
- Repository tests/other bundle checks pass after regeneration.
- No TestPyPI upload or hosted candidate run was dispatched; GitHub pypitest environment was created
  and verified with only release_candidate allowed. TestPyPI-side trust awaits the owner's first run.
- Source manifests were stale during the original pass; this task did not overwrite that lane's assets.

Working-directory repair, 2026-09-05T13:41:13Z:
- Reproduced the original failure from tests/: 1 failed, 1 passed.
- Replaced the parser-only mock with an isolated temporary version-file fixture and the real parser.
- All 263 focused tests pass from repository root (cwd-root.xml) and tests/ (cwd-tests.xml).
- Scoped correctness Ruff and regenerated tests-corpus checks pass.
- Read-only checks now report all source assets current after the other runtime lane's completion.
- Production gate/workflow code was not changed by this repair. No commits, pushes, or uploads.
