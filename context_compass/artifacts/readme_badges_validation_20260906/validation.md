# README badges and coverage validation

- Workflow regression suite: 339 passed, 1.31s. No runtime suite or coverage percentage measured.
- actionlint: all workflows pass.
- CI, monthly/lifetime downloads and typing badge endpoints: HTTP 200, valid SVG.
- Actual Codecov upload: not run locally. The owner reports the repository secret configured.
- Coverage uses existing three-platform tests; failed tests remain blocking. Upload failures do not.
- No OIDC, new environment, publishing credentials, extra suite triggers, commits or pushes.
- Only codecov.yml was marked intent-to-add for the tracked-file asset generator.
- Codecov YAML validation: HTTP 200, Valid.
- Tests/other corpora regenerated; all three corpus checks pass.
- Source-asset checks pass (v0.2.36); patch indexes/ranges validated.
- Scoped Ruff E9/F63/F7/F82 and git diff --check pass.
- Remaining: owner-hosted rollout and the first real prod coverage report.
