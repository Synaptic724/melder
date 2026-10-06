# Extending CI

Every change below ends the same way: run the workflow tests, update this folder and
[BRANCH_WORKFLOW.md](../BRANCH_WORKFLOW.md) wherever they describe the behaviour you changed, and follow
[validating.md](validating.md) before handing off.

## Rules every workflow follows

`tests/unit/github_workflows/test_workflow_contracts.py` parses each workflow and checks these:

- Workflow files sit directly in `.github/workflows/`; GitHub does not load subfolders.
- Reusable workflows declare `on: workflow_call` (most also allow `workflow_dispatch` for manual runs), read-only
  `permissions`, and no `concurrency`: the caller owns concurrency, so a helper can never cancel its caller.
- In the mandatory reusable workflows (the list in `test_reusable_mandatory_jobs_cannot_be_disabled`) no job has
  an `if`, `continue-on-error` or an `environment`, and every job has `timeout-minutes`, so a required check can
  never turn into a skipped success. The one exception is `test-runtime.yml`'s `coverage` job, which only reports.
  Add a new mandatory reusable workflow to that list. The speed workflows follow the same rule in
  `test_speed_workflows_measure_everything_once_started`: they block nothing, but a started speed test never skips
  itself or hides a failure.
- Python comes from a manifest or is the helper release ([python_versions.md](python_versions.md)).
- Linux jobs run on `ubuntu-24.04`, never `ubuntu-latest`: GitHub moves that label to Ubuntu 26.04 from
  2026-10-19, and setup-python's Linux builds are made per Ubuntu release, so a moved label could fail a
  manifest release that passes today. Move to a newer Ubuntu deliberately: change every label and
  `RuntimeMatrixPolicy.TARGETS` together and run the full matrix.
- `PYTHON_GIL=0` goes on the steps that run Melder, never on a whole job: Python's setup on macOS runs a
  certificate installer that cannot start with the GIL disabled.
- Secrets are passed explicitly and only where needed: `tests` receives `CODECOV_TOKEN` and nothing else, and the
  publication tokens live in the `pypitest` and `pypi` environments, each used by one job.
- Artifact names carry `${{ github.run_id }}-${{ github.run_attempt }}`, so a rerun never picks up another
  attempt's files by accident. A job that downloads a build made earlier in the same run names it from the build
  job's output (`needs.<build>.outputs.artifact-name`), never from its own attempt, because a failed-jobs re-run
  does not repeat a successful build. The release candidate reuses that build on such a re-run; final publication
  refuses one and asks for "Re-run all jobs".

## Add a job that must pass before a merge

1. Add the job to `ci.yml` with `needs: branch-policy` and an `if:` on the flag that should require it (no `if`
   if it must always run).
2. Add it to `merge-ready`'s `needs`.
3. Add its name to `CIPolicy` in `ci_policy.py`: `FULL_JOBS` when it belongs to the full checks, or
   `REQUIRED_JOBS` with its own rule in `require_success` for a new kind. `merge-ready` refuses when its `needs`
   and `CIPolicy` disagree, so steps 2 and 3 land together.
4. Update `test_ci_policy.py`, the assertions in `test_every_pr_reports_a_fail_closed_required_status`, and the
   required-checks table at the top of BRANCH_WORKFLOW.md.

A job that should only report does not belong in `ci.yml` at all, not even as an optional job: later promotions
reuse a CI run only when the whole run finished green, so it could hold or refuse a promotion. Give it its own
workflow, as `speed-tests.yml` does for the speed tests.

## Add a stage to the release-candidate or publication run

`package-ready` requires exactly `CIPolicy.CANDIDATE_JOBS`; a new release-candidate stage goes into its `needs`
and that list together. A publication job that must finish before the upload goes into `pypi-publish`'s `needs`.

## Add or change a route

Routes are decided only by `validate_route`, `validation_requirements` and, for the speed tests, `speed_required`
in `ci_policy.py`. Change them there, add cases to `test_ci_policy.py`, and update the route tables in
[workflows.md](workflows.md) and BRANCH_WORKFLOW.md.

## Add a speed test

1. Copy one of the three speed workflows and keep both of its jobs: `manifest` (helper Python, then
   `python_runtime_matrix.py speed`) and the benchmark job with `needs: manifest`,
   `SPEED_PYTHON: ${{ needs.manifest.outputs.python }}`, `python-version: ${{ needs.manifest.outputs.python }}`
   with `freethreaded: true`, the install step
   `python .github/scripts/python_runtime_matrix.py speed-install --results <its results folder>`, a provenance
   step asserting `platform.python_version() == os.environ['SPEED_PYTHON']`, `PYTHON_GIL=0` on the measured steps
   only, and an upload of the results folder with `if: always()`. A `shell: python` step runs from a temporary
   file, so the checkout is not on `sys.path`: call `sys.path.insert(0, str(Path.cwd()))` before importing
   `benchmarks`, or the step fails with "No module named 'benchmarks'".
2. Pin any new benchmark library in the speed manifest, and list it under `build_from_source` if it publishes no
   free-threaded wheel.
3. Call it from `speed-tests.yml` with `needs: route` and `if: needs.route.outputs.speed-required == 'true'`, and
   nothing more: no `continue-on-error`, so a failure stays red on the pull request, and never from `ci.yml`, so it
   blocks nothing.
4. Add the workflow to the speed-test parametrizations in `test_workflow_contracts.py` (Python from the speed
   manifest, the install, the benchmarks import, the GIL-off setup), to
   `test_speed_workflows_measure_everything_once_started`, and to the job set in
   `test_speed_tests_start_beside_ci_and_block_nothing`.

## Add a script

Put it in `.github/scripts/` as standard-library Python with an `argparse` `main()` that exits non-zero (or
raises) when it refuses. Add a fixture in `tests/unit/github_workflows/conftest.py` that loads it with
`load_script`, write its tests beside the others, and describe it in [scripts.md](scripts.md).

## Keep this guide current

A test in `test_workflow_contracts.py` fails when a workflow, a script or a ruleset is not named in backticks
somewhere in this folder, or when a relative link here points at a missing file. Add a row or a section when you
add a file, and correct the prose when you change behaviour.
