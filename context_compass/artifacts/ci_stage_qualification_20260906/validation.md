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

## Stable no-GIL matrix extension

- 382 focused workflow tests passed in 1.38s; report: python-matrix-tests.xml.
- Actionlint and scoped correctness Ruff passed after the runtime matrix changes.
- Live manifest discovery selected Python 3.14.7 across Linux x64, Windows x64 and macOS arm64;
  report: live-python-matrix.json. Python 3.15 prereleases were excluded.
- The first live request was refused by the network sandbox; the same helper succeeded outside it.
- Source assets regenerated for the owner's 0.2.37 version: 452 documentation entries,
  629 bind-guard entries, four system documents. No runtime source/version edits were made.
- All repository corpora regenerated: src 585 inputs, tests 809, other 356.
- New discovery helper/test marked intent-to-add for the default builder's tracked-file discovery;
  their contents are not staged and no commit was created.
- All three extended patch indexes regenerated; final source-asset, corpus, index and diff checks pass.
- Final source/workflow review is complete. The extended task is ready for owner review/hosted rollout.
- No hosted test matrix or publication has been dispatched for this extension.

## PR 147 checkout identity correction

- PR 147 (dev -> preprod), run 34047253419: full runtime/platform, docs, asset and package checks
  passed. Only the record step in job 101526277478 failed. Skipped source-qualification is expected.
- Exact merge 0d82c24da7630d0b54990a26560085adad551781 was reproduced in a disposable checkout.
- Windows Git reported clean; Ubuntu Git reported 235 unchanged historical CRLF documents dirty.
- pr147-byte-identity.json proves all 235 have identical committed blob bytes and modes.
- Corrected guard verifies the index and raw blob/mode identity; real changes still fail with paths.
- 403 focused workflow tests passed in 4.76s; checkout-identity-tests.xml retains the evidence.
- Scoped correctness Ruff passed. Workflow YAML did not change in this correction.
- Ubuntu replay passes on the exact untouched merge; see pr147-fixed-identity.json.
- Disposable checkout/probe/reports are task-owned temporary evidence; no user commits or refs changed.
- Final corpus/source-asset/index and diff checks pass. Hosted rollout requires owner commit/promotion.
- Owner-requested builder rerun at 2026-09-06T17:54:46Z: source assets rebuilt for 0.2.37,
  repository corpora unchanged, and both source/repository --check commands passed.
