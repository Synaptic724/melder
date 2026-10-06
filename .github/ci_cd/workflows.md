# Workflows

Every file in `.github/workflows/`. GitHub loads workflow files only from that folder itself, never from a
subfolder. A name in parentheses is what the Actions tab and a pull request's checks list show.

## Entry workflows

### `ci.yml`: source CI for pull requests

Runs on pull requests into `dev`, `preprod`, `release_candidate` and `prod` (opened, updated, reopened, marked
ready for review, or edited, which includes a changed base branch) and on manual dispatch. A newer commit on the
same pull request cancels the older run. Ordinary pushes do not run it.

| Job | Runs when | What it proves |
| --- | --- | --- |
| `branch-policy` (CI / branch-policy) | always | The route is allowed; it sets the four flags below (`ci_policy.py branch`). |
| `hygiene` (CI / repository-hygiene) | always | No two tracked paths differ only by letter case (`ci_policy.py hygiene`). |
| `source-assets` | runtime | The committed build assets match their builders (`build-src-assets.yml`). |
| `repo-assets` | runtime | The committed LLM bundles match the tracked files (`build-repo-assets.yml`). |
| `tests` | runtime | Every test tier passes on every manifest release and runner (`test-runtime.yml`). |
| `documentation` | runtime | The documentation site and handbooks build and validate (`docs.yml`). |
| `real-world-gauntlet`, `persistent-runtime-gauntlet`, `shallow-all-thread-scaling` | gauntlet | The three speed tests complete (see below). |
| `packages` | package | The wheel and sdist build, verify and install (`build-distributions.yml`). |
| `source-qualification` | source | An earlier full CI run tested this exact tree (`verify-source-qualification.yml`). |
| `merge-ready` (CI / merge-ready) | always | Every required job succeeded (below). |

`ci_policy.py` sets the flags from the event alone (`validation_requirements`):

| Event | runtime | package | source | gauntlet |
| --- | --- | --- | --- | --- |
| PR into `dev` | yes | no | no | no |
| `dev` PR into `preprod` | yes | yes | no | yes |
| `preprod` PR into `release_candidate` | no | no | yes | no |
| `release-fix/*` PR into `release_candidate` | yes | yes | no | no |
| `release_candidate` PR into `prod` | no | no | no | no |
| Manual run on a permanent branch | yes | yes, except on `dev` | no | no |

Every route with `runtime` set runs the whole matrix: every manifest release on every runner (27 cells today). The
owner ruled out a smaller matrix for any route, pull requests into `dev` included (2026-10-05).

`merge-ready` runs even when a job before it failed (`if: always()`). `ci_policy.py merge-ready` recomputes the
four flags from the event, refuses if `branch-policy` reported different ones, and requires a result for every
job in its `needs`: a required job must succeed, an optional one may succeed or be skipped, and a failure or a
cancellation never passes. After a full run it records the tested tree (`ci_qualification.py record`) as the
artifact `source-qualification-<run>-<attempt>`, kept 90 days, which later promotions reuse. On a pull request
into `prod`, or a manual run there, it then waits up to ten minutes for that candidate's release-candidate run to
succeed (`check_candidate_run.py --wait-seconds 600`).

### `release-candidate.yml`: TestPyPI qualification of the candidate

Runs on every push to `release_candidate` and on manual dispatch there. Runs are serialized and never cancelled
midway.

| Job | What it does |
| --- | --- |
| `authorize` (RC / authorize) | Refuses a stale or moved head (`ci_policy.py candidate-head`), builds the release matrix from the test manifests (`python_runtime_matrix.py discover`) and keeps it as an artifact. |
| `source-qualification` | Reuses the full CI evidence for this tree (`verify-source-qualification.yml`). |
| `build` | Builds and verifies the wheel and sdist (`build-distributions.yml`). |
| `publish` (RC / publish-to-TestPyPI) | In the `pypitest` environment: compares the files with what TestPyPI already has and stages only the missing ones (`testpypi_candidate.py prepare-upload`), requires the `melder_api_token` secret, checks the head again and uploads. |
| `install` (RC / installed-package / ...) | For every test-manifest release on Linux, Windows and macOS: downloads the exact uploaded wheel by its hash, installs it alone into a fresh environment and runs `smoke_wheel.py` (`testpypi_candidate.py probe-install`). |
| `package-ready` (RC / package-ready) | Requires all five stages to have succeeded and the head to be unchanged (`ci_policy.py candidate-ready`, `candidate-head`). |

### `python-publish.yml`: PyPI publication

Runs when a release is published (a GitHub prerelease does not publish) or on manual dispatch on `prod`.
Publication runs are serialized.

| Job | What it does |
| --- | --- |
| `release-gate` (Require current prod HEAD) | The event, the checkout and the current `prod` head (and the live release tag) are one commit (`ci_policy.py release-head`), and that commit's candidate passed TestPyPI qualification (`check_candidate_run.py`). |
| `hygiene`, `source-assets`, `repo-assets`, `tests` | The full checks again, fresh. |
| `release-build` | Builds and verifies the distributions and compares the release tag with the package version (`build-distributions.yml`). |
| `pypi-publish` (Publish to PyPI) | In the `pypi` environment: rechecks the files, the candidate and the release head immediately before uploading with `PYPI_API_TOKEN`. |

## Reusable workflows

### `test-runtime.yml`: the test tiers on every release

- `discover` (Runtime / read the test manifests) builds the matrix from `.github/python/tests/`
  (`python_runtime_matrix.py discover`) and keeps it as `runtime-python-matrix-<run>-<attempt>` for 90 days.
- `test` (Runtime / <os> / Python <release> no-GIL) is one job per release and runner (`ubuntu-latest` x64,
  `windows-latest` x64, `macos-latest` arm64). It sets up that free-threaded release, installs exactly its
  manifest's pins plus Melder with `uv pip install --no-deps`, and runs `run_runtime_tests.py` with
  `PYTHON_GIL=0`: the unit, component and integration tiers in one pytest process, with JUnit and coverage XML
  kept 14 days.
- `coverage` (Coverage / Codecov) never blocks and is skipped for pull requests from forks. It requires a
  coverage report from every cell of this run (`python_runtime_matrix.py coverage`) and uploads them to Codecov,
  retrying once with the uploader from PyPI when the first attempt fails. Without the `CODECOV_TOKEN` secret it
  warns and skips.

### `build-src-assets.yml` (Source assets / verify)

Runs `src/melder/_build_assets/_build_asset_runner.py --list` and `--check`: the committed manifests under
`src/melder/_build_assets/` must match what their builders produce. Fix it by running the runner without
`--check` and committing the result.

### `build-repo-assets.yml` (Repository assets / verify)

Runs `llm_support/_builder.py --list` and `--check`: the committed LLM bundles must match the tracked files. Fix
it by running the builder and committing the result.

### `docs.yml` (Docs / site and handbook)

Installs `docs/requirements.txt`, runs the documentation tests and checks, builds the site, validates links,
anchors and publication metadata (`docs/seo.toml`), builds the ePub and PDF handbooks, and keeps the rendered
output for 14 days. The documentation tooling lives in `docs/tools/`; see `docs/maintaining.md`.

### `build-distributions.yml` (Distributions / build-and-verify)

Takes `artifact-name` and an optional `release-tag`. On free-threaded Python it installs the locked build tools
(`uv sync --locked --only-group build`), checks the build assets, builds the wheel and sdist with the commit's
timestamp, normalizes the sdist (`normalize_sdist.py`), checks both archives (`verify_distributions.py`),
installs the wheel alone into a fresh environment and runs `smoke_wheel.py` there with `PYTHON_GIL=0`, then keeps
the files under the given artifact name for 14 days.

### `verify-source-qualification.yml` (Source / full qualification)

`ci_qualification.py select` finds the full CI run that tested this exact Git tree, the workflow downloads that
run's `source-qualification` artifact by its ID, and `ci_qualification.py verify` checks the record against the
current tree and repeats the selection, so evidence that changed in the meantime cannot be reused.

### The three speed tests

`real-world-gauntlet.yml`, `persistent-runtime-gauntlet.yml` and `shallow-all-thread-scaling.yml` run only for a
`dev` pull request into `preprod`, and by hand. Each has two jobs:

- `manifest` (Speed manifest / <branch>) reads the single speed manifest in `.github/python/speed/` and outputs
  its release (`python_runtime_matrix.py speed`).
- The benchmark job (`gauntlet`, `gauntlet` and `scaling`) runs on `ubuntu-24.04`, `windows-2025` and
  `macos-15-intel`, all x64. It sets up that release free-threaded, installs the speed manifest's pins
  (`python_runtime_matrix.py speed-install`; dependency-injector is built from source because it publishes no
  free-threaded wheel), records provenance and asserts that it runs the manifest's release with the GIL off, runs
  the benchmark from `benchmarks/testing_other_di/` with `PYTHON_GIL=0`, and keeps the results for 30 days.

They compare Melder with dependency-injector and dishka. There is no speed threshold: a run fails only when the
benchmark fails or is incomplete, or when its settings or GIL state are wrong. Their inputs (thread counts,
iteration counts, durations) are described in each workflow and in [BRANCH_WORKFLOW.md](../BRANCH_WORKFLOW.md).
