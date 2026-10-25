# Scripts and other `.github` files

The scripts in `.github/scripts/` hold CI's decisions. They use only the standard library, because workflows run
them right after setting up Python and before installing anything. A workflow runs one as
`python .github/scripts/<name>.py <operation>`, which puts `.github/scripts` on `sys.path`; that is how they
import each other (for example `from ci_policy import object_value`). A refusal prints the reason and exits
non-zero; nothing falls back to a default. Tests load each script by path through
`tests/unit/github_workflows/conftest.py`. `test_ci_scripts_use_only_the_standard_library` refuses any other
import, with two exceptions that run inside the environment they test: `run_runtime_tests.py` (pytest) and
`smoke_wheel.py` (the installed melder).

| Script | Operations or options | Called by | Tested in |
| --- | --- | --- | --- |
| `ci_policy.py` | `branch`, `speed-route`, `merge-ready`, `hygiene`, `release-head`, `candidate-head`, `candidate-ready` | `ci.yml`, `speed-tests.yml`, `release-candidate.yml`, `python-publish.yml` | `test_ci_policy.py` |
| `python_runtime_matrix.py` | `discover`, `speed`, `speed-install`, `requirements`, `runtime-requirements`, `coverage` | `test-runtime.yml`, `release-candidate.yml`, `build-distributions.yml`, the three speed tests; `testpypi_candidate.py` imports its runtime-pin functions | `test_python_runtime_matrix.py` |
| `run_runtime_tests.py` | `--report`, `--coverage-report` | `test-runtime.yml` | `test_ci_policy.py` |
| `ci_qualification.py` | `record`, `select`, `verify` | `ci.yml`, `verify-source-qualification.yml` | `test_source_qualification.py`, `test_checkout_identity.py` |
| `check_candidate_run.py` | `--wait-seconds` | `ci.yml`, `python-publish.yml` | `test_candidate_publication.py` |
| `testpypi_candidate.py` | `prepare-upload`, `probe-install` | `release-candidate.yml` | `test_candidate_publication.py` |
| `testpypi_provenance.py` | `verify` | `release-candidate.yml` | `test_candidate_provenance.py` |
| `verify_distributions.py` | `--directory`, `--release-tag` | `build-distributions.yml`, `python-publish.yml` | `test_distributions.py` |
| `normalize_sdist.py` | `--directory` | `build-distributions.yml` | `test_sdist_normalization.py` |
| `smoke_wheel.py` | `--expected-version` | `build-distributions.yml`, `testpypi_candidate.py probe-install` | the distribution contract in `test_workflow_contracts.py` |

`test_workflow_contracts.py` also checks every workflow as data: it parses the YAML and asserts the wiring the
scripts rely on (job names, needs, flags, artifact names, Python requests, install commands).

## What each script decides

### `ci_policy.py`

`CIPolicy` names the permanent branches (`dev`, `preprod`, `release_candidate`, `prod`), the promotion order, and
the job lists that `merge-ready` and `package-ready` require: `FULL_JOBS`, `REQUIRED_JOBS` and `CANDIDATE_JOBS`.
`validate_route` refuses a pull request that skips a promotion step or comes from a fork,
`validation_requirements` turns an event into the runtime, package and source flags (table in
[workflows.md](workflows.md)), and `speed_required` says whether the same validated event starts the speed tests
in `speed-tests.yml` (only a `dev` pull request into `preprod`). `require_success` is the merge-ready rule. The
`release-head` and `candidate-head` gates compare full commit SHAs from the event, the checkout and the live
remote, so a branch or tag that moved during a run is refused. The script also provides the input helpers the others import (`object_value`,
`text_value`, `git_output`, `read_event`).

### `python_runtime_matrix.py`

Everything about which Python CI runs; see [python_versions.md](python_versions.md). Its `coverage` operation,
used before the Codecov upload, requires a report for every matrix cell of this run, taking each cell's newest
attempt. Its `runtime-requirements` operation writes the pins of Melder's declared runtime dependencies
(`[project.dependencies]`) from the running release's test manifest, or `--manifest`, for the wheel probe;
`testpypi_candidate.py` calls the same functions (`declared_dependencies`, `release_manifest`, `runtime_pins`).
A declared dependency the manifest leaves unpinned is refused.

### `run_runtime_tests.py`

The test driver. It refuses to run unless the process is Python 3.14 or newer, free-threaded, with the GIL off,
checks that again after pytest, and runs `tests/unit`, `tests/component` and `tests/integration` in one pytest
process (`tests/experimentation/` is never part of CI). Its exit code is pytest's.

### `ci_qualification.py`

Source proof. After a successful full run, `record` writes which repository, run, event, pull request and Git tree
were tested. `select` finds that record for the tree being promoted (a `preprod` pull request into
`release_candidate`, or the `release_candidate` branch itself) and `verify` checks the downloaded record field by
field. Any change to the tree means the old proof no longer applies; the fix is a manual full CI run (see
[BRANCH_WORKFLOW.md](../BRANCH_WORKFLOW.md), "Reusing full qualification").

### `check_candidate_run.py`

Before a commit reaches `prod`, and again before publication: the prod merge's candidate parent must have the
same tree, the package version must be final (no `rcN`), and the newest release-candidate run for that exact
commit must have succeeded. It never falls back to an older green run. It can wait up to 600 seconds for a run
that is still in progress.

### `testpypi_candidate.py`

`prepare-upload` verifies the built files and compares them with TestPyPI: identical files already there are
accepted, missing ones are staged for upload, and different ones are refused (choose a new version). Its release
lookup retries HTTP 429 and 5xx answers, timeouts and failed connections up to six times, ten seconds apart; only a
404 means nothing is uploaded yet. It writes two step outputs: `upload-required` and `uploaded`, the JSON list of
the staged files, which the provenance job reads as the files this publish attempt signed.
`probe-install` downloads the exact wheel from TestPyPI by its hash and Melder's runtime dependencies from PyPI at
the running release's test-manifest pins (isolated, wheels only, no dependencies), installs them together into a
fresh environment with `--no-deps --no-index`, runs `pip check` and then `smoke_wheel.py` against the expected
version.

### `testpypi_provenance.py`

`verify` runs in `RC / provenance`, after the upload and before any probe installs a file. For every built file
(verified again first) it reads the provenance TestPyPI's Integrity API holds
(`https://test.pypi.org/integrity/melder/<version>/<file>/provenance`, retrying a 404 and the outage answers six
times, ten seconds apart, and refusing a redirect) and checks it in five layers:

1. a provenance exists;
2. its one bundle's publisher record is this repository's `release-candidate.yml` in `pypitest`;
3. Sigstore verifies its one attestation on the production trust root (certificate chain to Fulcio,
   transparency-log entry, signature);
4. the signing certificate names the expected signer claim by claim: its one subject alternative name is the
   workflow on `release_candidate`, and every Fulcio claim from issuer to token subject matches - repository and
   owner with their numeric ids, workflow and commit, GitHub-hosted runner, public visibility, the `pypitest`
   environment and, for a file this run uploaded, this run's id, publish attempt and event (a file TestPyPI already
   had may come from another run of the workflow at this commit);
5. the attested statement names exactly the file and its sha256 with PyPI's publish predicate.

The script checks layers 1, 2, 4 and 5 itself, reading the certificate's extensions from its DER with the
standard library. It then builds a fresh environment from `.github/provenance/requirements.txt` (pip isolated,
`--require-hashes --no-deps --only-binary=:all:`, then `pip check`) and runs
`.github/provenance/verify_attestations.py` in it, which checks layers 3 and 4 with pypi-attestations and
sigstore, the versions `pypa/gh-action-pypi-publish` signs with. The same run first proves the tool: the recorded
genuine attestation `.github/provenance/known_good_provenance.json` must verify, and two tampered copies of it (another
digest, another signer) must be refused, or no verdict counts. The expected identity lives in one class,
`ProvenancePolicy`; every refusal names the file, the claim, what was expected and what was found. The report
`reports/provenance.json` is written only after every check passed.

### `verify_distributions.py`, `normalize_sdist.py` and `smoke_wheel.py`

`verify_distributions.py` inspects the wheel and sdist without importing them: only Melder's files, no caches or
databases, the generated assets present, `Requires-Python >=3.14`, and one version everywhere (the metadata,
`__version__`, every asset manifest and the release tag). `normalize_sdist.py` rewrites only the sdist's member
order, timestamps and ownership, so a same-commit rebuild hashes the same. `smoke_wheel.py` runs inside the
installed environment: Melder must import from site-packages, its metadata, version and packaged documents must
agree, and a small bind, conjure and meld scenario must work with the GIL off.

## Other files in `.github`

- `BRANCH_WORKFLOW.md`: branch, release and publication policy for people and agents.
- `provenance/`: the provenance check's tool, used only by `testpypi_provenance.py`.
  `.github/provenance/verify_attestations.py` is the verifier, the one script under `.github/` that imports
  packages outside the standard library, so it never runs on a bare interpreter.
  `.github/provenance/requirements.txt` is its hashed lock; its header gives the command that regenerates it.
  `.github/provenance/known_good_provenance.json` is the recorded control: PyPI's provenance of the
  pypi-attestations wheel the lock installs. Moving the tool is one change: the publishing action's pin in
  `release-candidate.yml`, the lock at the versions that action signs with, and the control re-recorded for the
  new pypi-attestations wheel with `ProvenanceControl` updated ([extending.md](extending.md)).
- `python/`: the Python release manifests ([python_versions.md](python_versions.md)).
- `rulesets/`: `dev.json`, `preprod.json`, `release_candidate.json` and `prod.json` are the branch protection
  payloads. Each requires a pull request and the `CI / merge-ready` status from the GitHub Actions app (ID 15368)
  and forbids deleting the branch or force-pushing to it; `dev` also allows squash merges and requires an
  up-to-date branch, while the promotion branches accept merge commits only. Committing them changes nothing on
  GitHub: they take effect when the owner applies them with `gh api` (BRANCH_WORKFLOW.md, "Activating GitHub
  enforcement").
- `FUNDING.yml`: GitHub's sponsor button; not part of CI.
