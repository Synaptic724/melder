# CI stage qualification validation

Owner: tickets/tasks/2026-09-06_ci_validation_stage_design_task.md.
This directory holds task-owned temporary tests and tooling; delete on accepted closure.

- Parsed workflow tests: 19 passed.
- Correctness Ruff: passed for changed helpers and workflow tests.
- Initial full workflow-unit run: 260 passed, 66 setup errors from sandboxed Windows temp access.
- Same scope outside the sandbox: 325 passed in 1.03s, report workflow-tests.xml.
- Final focused run: 330 passed; JUnit suite time 1.119s, zero failures/errors/skips.
- Actionlint 1.7.12: all nine workflows pass (shellcheck and pyflakes integrations disabled).
- Official upload/download action transfer contracts verified before the final focused run.
- Regenerated tests (808 files), other (354 files) and the shared corpus manifest.
- Regenerated all three patch indexes; their 17 section ranges validate against their headings.
- All three repository corpus proofs and all three source-asset groups pass their freshness checks.
- All three patch indexes pass independent freshness checks.
- An additional default Ruff run reported 17 findings across the helpers/workflow tests. These are
  style/typing rules (UP045, TRY004, FURB122, I001, PIE807, UP012), not the scoped correctness check.
  UP045 conflicts with the active role's required Optional syntax; ValueError is the documented
  malformed-evidence boundary contract. No broad style rewrite or lint-policy change is in scope.
- Final scoped Ruff (`--select E9,F63,F7,F82`) and `git diff --check`: passed.
- Final source/workflow diff review: complete; final publisher still requires its full runtime matrix.
- Status: ready for owner review and hosted rollout. No additional full runtime suite was run locally.
- No hosted workflow, commit, push or package publication was dispatched by this task.
