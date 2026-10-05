# Scripts and other `.github` files

The scripts in `.github/scripts/` hold CI's decisions. They use only the standard library, because workflows run
them right after setting up Python and before installing anything. A workflow runs one as
`python .github/scripts/<name>.py <operation>`, which puts `.github/scripts` on `sys.path`; that is how they
import each other (for example `from ci_policy import object_value`). A refusal prints the reason and exits
non-zero; nothing falls back to a default. Tests load each script by path through
`tests/unit/github_workflows/conftest.py`.

| Script | Operations or options | Called by | Tested in |
| --- | --- | --- | --- |
| `ci_policy.py` | `branch`, `merge-ready`, `hygiene`, `release-head`, `candidate-head`, `candidate-ready` | `ci.yml`, `release-candidate.yml`, `python-publish.yml` | `test_ci_policy.py` |
| `python_runtime_matrix.py` | `discover`, `speed`, `speed-install`, `requirements`, `coverage` | `test-runtime.yml`, `release-candidate.yml`, the three speed tests | `test_python_runtime_matrix.py` |
| `run_runtime_tests.py` | `--report`, `--coverage-report` | `test-runtime.yml` | `test_ci_policy.py` |
| `ci_qualification.py` | `record`, `select`, `verify` | `ci.yml`, `verify-source-qualification.yml` | `test_source_qualification.py`, `test_checkout_identity.py` |
| `check_candidate_run.py` | `--wait-seconds` | `ci.yml`, `python-publish.yml` | `test_candidate_publication.py` |
| `testpypi_candidate.py` | `prepare-upload`, `probe-install` | `release-candidate.yml` | `test_candidate_publication.py` |
| `verify_distributions.py` | `--directory`, `--release-tag` | `build-distributions.yml`, `python-publish.yml` | `test_distributions.py` |
| `normalize_sdist.py` | `--directory` | `build-distributions.yml` | `test_sdist_normalization.py` |
| `smoke_wheel.py` | `--expected-version` | `build-distributions.yml`, `testpypi_candidate.py probe-install` | the distribution contract in `test_workflow_contracts.py` |

`test_workflow_contracts.py` also checks every workflow as data: it parses the YAML and asserts the wiring the
scripts rely on (job names, needs, flags, artifact names, Python requests, install commands).

## What each script decides

### `ci_policy.py`

`CIPolicy` names the permanent branches (`dev`, `preprod`, `release_candidate`, `prod`), the promotion order, the
job lists that `merge-ready` and `package-ready` require (`FULL_JOBS`, `GAUNTLET_JOBS`, `REQUIRED_JOBS`,
`CANDIDATE_JOBS`) and the two runtime release selections (`FULL_RELEASES` "all", `SLICED_RELEASES`
"floor-and-newest"). `validate_route` refuses a pull request that skips a promotion step or comes from a fork,
`validation_requirements` turns an event into the runtime, package, source and gauntlet flags, and
`runtime_releases` decides which test manifests the runtime tests cover: the floor and the newest for a PR into
`dev`, all of them otherwise (table in [workflows.md](workflows.md)). `branch` writes all five as outputs, and
`merge-ready` recomputes them and refuses a mismatch. `require_success` is the merge-ready rule. The
`release-head` and `candidate-head` gates compare full commit SHAs from the event, the checkout and the live
remote, so a branch or tag that moved during a run is refused. The script also provides the input helpers the
others import (`object_value`, `text_value`, `git_output`, `read_event`).

### `python_runtime_matrix.py`

Everything about which Python CI runs; see [python_versions.md](python_versions.md). `discover --releases`
builds the runtime matrix from every test manifest (`all`, the default) or from the floor and the newest
(`floor-and-newest`). Its `coverage` operation, used before the Codecov upload, requires a report for every matrix
cell of this run, taking each cell's newest attempt.

### `run_runtime_tests.py`

The test driver. It refuses to run unless the process is Python 3.14 or newer, free-threaded, with the GIL off,
checks that again after pytest, and runs `tests/unit`, `tests/component` and `tests/integration` in one pytest
process (`tests/experimentation/` is never part of CI). Its exit code is pytest's.

### `ci_qualification.py`

Source proof. After a successful full run that tested every manifest, `record` writes which repository, run,
event, pull request and Git tree were tested; it refuses a light run and a sliced run (a PR into `dev`). `select`
finds that record for the tree being promoted (a `preprod` pull request into `release_candidate`, or the
`release_candidate` branch itself) and `verify` checks the downloaded record field by field. Any change to the
tree means the old proof no longer applies; the fix is a manual full CI run (see
[BRANCH_WORKFLOW.md](../BRANCH_WORKFLOW.md), "Reusing full qualification").

### `check_candidate_run.py`

Before a commit reaches `prod`, and again before publication: the prod merge's candidate parent must have the
same tree, the package version must be final (no `rcN`), and the newest release-candidate run for that exact
commit must have succeeded. It never falls back to an older green run. It can wait up to 600 seconds for a run
that is still in progress.

### `testpypi_candidate.py`

`prepare-upload` verifies the built files and compares them with TestPyPI: identical files already there are
accepted, missing ones are staged for upload, and different ones are refused (choose a new version).
`probe-install` downloads the exact wheel from TestPyPI by its hash, installs it alone into a fresh environment
and runs `smoke_wheel.py` against the expected version.

### `verify_distributions.py`, `normalize_sdist.py` and `smoke_wheel.py`

`verify_distributions.py` inspects the wheel and sdist without importing them: only Melder's files, no caches or
databases, the generated assets present, `Requires-Python >=3.14`, and one version everywhere (the metadata,
`__version__`, every asset manifest and the release tag). `normalize_sdist.py` rewrites only the sdist's member
order, timestamps and ownership, so a same-commit rebuild hashes the same. `smoke_wheel.py` runs inside the
installed environment: Melder must import from site-packages, its metadata, version and packaged documents must
agree, and a small bind, conjure and meld scenario must work with the GIL off.

## Other files in `.github`

- `BRANCH_WORKFLOW.md`: branch, release and publication policy for people and agents.
- `python/`: the Python release manifests ([python_versions.md](python_versions.md)).
- `rulesets/`: `dev.json`, `preprod.json`, `release_candidate.json` and `prod.json` are the branch protection
  payloads. Each requires a pull request and the `CI / merge-ready` status from the GitHub Actions app (ID 15368)
  and forbids deleting the branch or force-pushing to it; `dev` also allows squash merges and requires an
  up-to-date branch, while the promotion branches accept merge commits only. Committing them changes nothing on
  GitHub: they take effect when the owner applies them with `gh api` (BRANCH_WORKFLOW.md, "Activating GitHub
  enforcement").
- `FUNDING.yml`: GitHub's sponsor button; not part of CI.
