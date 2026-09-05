# Branch CI validation workspace

Canonical findings and results live in the implementation ticket:
`tickets/tasks/2026-09-04_implement_branch_ci_release_validation_task.md`.

This directory holds disposable test temporary data, package outputs, logs, and the checksum-verified
actionlint executable. It is ignored except for this note and its .gitignore. No credentials belong here.

First focused attempt: 112 passed, 29 fixture-setup errors caused by denied access to the shared
Windows pytest temp directory. Rerun with an explicit task-local --basetemp and cache_dir.

Final results:
- 147 focused tests passed after the raw ZIP-name correction.
- Local suite: 11,130 passed, 28 skipped, 15 xfailed, one xpassed; coroutine shutdown warning.
- Hosted Linux/Windows: each 11,109 passed, 28 skipped, 15 xfailed, one xpassed; same warning.
- actionlint (without optional shellcheck/pyflakes), correctness Ruff, real package build/verification,
  and isolated wheel smoke test passed.
- Review-branch source and repository asset checks passed.
- GitHub PR 121, signed commit cb24d33b6f30a6b76b137a3a34a8ccf6e15cf80e, CI run 33928393747.
- Rulesets 22307416, 22307417, and 22307418 are active.

The review-worktree was removed through git worktree remove on 2026-09-05 at owner request.
Its local/remote temporary branch was retired and PR 121 closed; codex_features2 preserves the work.
The remaining files in this directory are validation records/tooling, not another checkout.

Final local review, 2026-09-05:
- Reproduced the moved-release-tag acceptance with a failing CLI regression.
- Added a live remote tag target check, including annotated-tag peeling and deleted-tag refusal.
- 167 focused tests pass; all seven workflows pass actionlint; correctness Ruff passes.
- Regenerated tests/other bundles verify against the current tracked working tree.
- This final patch is local only. Owner handles commits/pushes; PR 121 remains the earlier baseline.
