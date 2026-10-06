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
  Add a new mandatory reusable workflow to that list.
- Python comes from a manifest or is the helper release ([python_versions.md](python_versions.md)).
- `PYTHON_GIL=0` goes on the steps that run Melder, never on a whole job: Python's setup on macOS runs a
  certificate installer that cannot start with the GIL disabled.
- Secrets are passed explicitly and only where needed: `tests` receives `CODECOV_TOKEN` and nothing else, and the
  publication tokens live in the `pypitest` and `pypi` environments, each used by one job.
- Artifact names carry `${{ github.run_id }}-${{ github.run_attempt }}`, so a rerun never picks up another
  attempt's files.

## Add a job that must pass before a merge

1. Add the job to `ci.yml` with `needs: branch-policy` and an `if:` on the flag that should require it (no `if`
   if it must always run).
2. Add it to `merge-ready`'s `needs`.
3. Add its name to `CIPolicy` in `ci_policy.py`: `FULL_JOBS` when it belongs to the full checks, `GAUNTLET_JOBS`
   for a dev-to-preprod benchmark, or `REQUIRED_JOBS` with its own rule in `require_success` for a new kind.
   `merge-ready` refuses when its `needs` and `CIPolicy` disagree, so steps 2 and 3 land together.
4. Update `test_ci_policy.py`, the assertions in `test_every_pr_reports_a_fail_closed_required_status`, and the
   required-checks table at the top of BRANCH_WORKFLOW.md.

## Add a stage to the release-candidate or publication run

`package-ready` requires exactly `CIPolicy.CANDIDATE_JOBS`; a new release-candidate stage goes into its `needs`
and that list together. A publication job that must finish before the upload goes into `pypi-publish`'s `needs`.

## Add or change a route

Routes are decided only by `validate_route` and `validation_requirements` in `ci_policy.py`. Change them there,
add cases to `test_ci_policy.py`, and update the route tables in [workflows.md](workflows.md) and
BRANCH_WORKFLOW.md.

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
3. Call it from `ci.yml` with `if: needs.branch-policy.outputs.gauntlet-required == 'true'`, and add it to
   `merge-ready`'s `needs` and to `CIPolicy.GAUNTLET_JOBS`.
4. Add the workflow to the speed-test parametrizations in `test_workflow_contracts.py` (Python from the speed
   manifest, the install, the benchmarks import, the GIL-off setup) and to
   `test_reusable_mandatory_jobs_cannot_be_disabled`.

## Add a script

Put it in `.github/scripts/` as standard-library Python with an `argparse` `main()` that exits non-zero (or
raises) when it refuses. Add a fixture in `tests/unit/github_workflows/conftest.py` that loads it with
`load_script`, write its tests beside the others, and describe it in [scripts.md](scripts.md).

## Keep this guide current

A test in `test_workflow_contracts.py` fails when a workflow, a script or a ruleset is not named in backticks
somewhere in this folder, or when a relative link here points at a missing file. Add a row or a section when you
add a file, and correct the prose when you change behaviour.
