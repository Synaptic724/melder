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

macOS extension, 2026-09-05T16:14:46Z:
- Added macos-latest to both the shared runtime and TestPyPI installed-package matrices.
- GitHub's native Apple Silicon runner and official Python 3.14t arm64 artifacts were verified in metadata.
- All 14 workflow contract tests, eight-workflow actionlint, scoped Ruff, and whitespace checks pass.
- Updated patch indexes and tests/other corpora are regenerated and verified.
- No hosted Mac run was executed here; its real runtime result awaits the owner's push.

TestPyPI token repair, 2026-09-05T17:02:19Z:
- All 266 focused workflow, package-metadata, and LLM-builder tests pass (token-auth.xml).
- All eight workflow files pass actionlint 1.7.12; optional shellcheck/pyflakes disabled.
- Scoped correctness Ruff, whitespace, and regenerated tests/other corpus checks pass.
- GitHub secret-name metadata confirms MELDER_API_TOKEN in pypitest; no value was accessed.
- RC publishing uses explicit token authentication; the prod gate still requires exact-source success.
- The owner's previous OIDC run failed invalid-publisher. Updated YAML must reach release_candidate
  before a new hosted run can prove token validity and installation across all three operating systems.
- No commit, push, workflow dispatch/rerun, or package upload was performed by the agent.

macOS setup environment repair, 2026-09-05T17:31:43Z:
- Three parsed setup-environment regression cases failed on the original job-wide PYTHON_GIL=0.
- All 269 focused workflow/package/builder tests pass after the fix (macos-setup.xml).
- All eight workflows pass actionlint; scoped Ruff and whitespace checks pass.
- Changed patch indexes and tests/other corpora are regenerated; corpus output/input proofs pass.
- Python 3.14t, Linux/Windows/macOS matrices, and runtime GIL-state checks remain intact.
- Upstream macOS installation launches the standard-Python certificate helper; setup now receives
  no forced GIL-off setting. Qualification steps retain PYTHON_GIL=0.
- A hosted macOS installation was not executed here. No commits, pushes, reruns, or uploads occurred.
