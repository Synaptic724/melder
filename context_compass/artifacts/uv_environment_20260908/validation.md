# uv environment validation

Owner: tickets/tasks/2026-09-08_reproducible_uv_environment_task.md.
Temporary environments/cache/builds belong to this task and are removed at accepted closure.

- Installed uv: 0.11.23.
- Generated 28-package universal lock: 27 public PyPI packages plus relative editable Melder.
- Audited 321 HTTPS distribution artifacts with SHA256 hashes; no credentials/private registry paths.
- Fresh default-dev sync: 15 installed packages, Melder 0.2.37, CPython 3.14.0 free-threaded.
- Installed metadata: no runtime Requires-Dist; GIL-off probe passed.
- Existing workflow tests in default-dev environment: 411 passed in 3.97s.
- CI test-group sync: 10 installed packages; updated workflow tests: 413 passed in 3.77s.
- Locked build-only environment: six tools; wheel/sdist verification and isolated wheel probe passed.
- Linux x64 and macOS arm64 test-group dry-runs passed; these were resolution checks, not hosted runs.
- Stale-lock fixture refused the changed dependency declaration. Its first attempt lacked source
  metadata and was repaired before accepting the negative test result.
- Actionlint and scoped correctness Ruff passed.
- Final verification at 2026-09-08T11:21:48Z: uv lock --check, source asset --check, all repository
  corpus checks, three patch-index checks and git diff --check passed.
- Tests/other corpora and their indexes/manifest were regenerated after the final source changes.
- Full runtime suite and hosted OS matrix under the new CI environment were not run locally;
  focused workflow tests and local package checks are the executed evidence above.
- No user environments, runtime dependency declarations, commits or publication were changed.
