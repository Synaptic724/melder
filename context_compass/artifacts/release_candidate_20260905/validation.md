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
- The shared checkout's separate runtime-lane source manifests remain stale; those were not overwritten.
