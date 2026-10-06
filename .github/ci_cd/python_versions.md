# Python versions and the manifests

CI never chooses a Python release by itself. Every interpreter it sets up is one of these:

| Where | Which Python | Comes from |
| --- | --- | --- |
| Runtime test cells (`test-runtime.yml`) and the release candidate's install probes (`release-candidate.yml`) | Every release that has a test manifest, free-threaded, on Linux x64, Windows x64 and macOS arm64 | `.github/python/tests/<release>.toml`, read by `python_runtime_matrix.py discover` |
| The three speed tests | The one speed release, free-threaded, on three x64 runners | `.github/python/speed/<release>.toml`, read by `python_runtime_matrix.py speed` |
| Every other job (policy, assets, docs, builds, publication, the speed tests' manifest jobs) | The helper release, written as `python-version: "3.14.7"` | The workflow file; the release must have a test manifest |

Nothing is looked up on the network and nothing follows the newest patch, so a new Python release, 3.15 included,
runs only after someone adds its manifest. `test_workflow_contracts.py` refuses any `setup-python` step that asks
for `check-latest`, a version file, a pre-release, a second helper release, or a release with no test manifest.

## The manifest format

A manifest is a TOML file named after its exact release:

```toml
# .github/python/tests/3.14.0.toml
python = "3.14.0"
freethreaded = true
dependencies = [
    "pytest==9.1.1",
    "pytest-cov==7.1.0",
    "coverage==7.16.1",
    "PyYAML==6.0.3",
    "iniconfig==2.3.0",
    "packaging==26.3",
    "pluggy==1.6.0",
    "Pygments==2.21.0",
    "colorama==0.4.6; sys_platform == 'win32'",
]
```

- `python` is an exact final release and matches the file name.
- `freethreaded` must be `true`: Melder CI qualifies free-threaded builds only.
- `dependencies` is the whole install: exact `name==version` pins, one per distribution, each optionally followed
  by `; marker`. Installs skip dependency resolution, so a pinned package's own dependencies must be pinned too.
  The test manifests hold the `test` group's closure from `uv.lock`.
- `build_from_source` (optional) lists pinned distributions that pip must build from their sdist because no
  usable wheel exists. The speed manifest uses it for dependency-injector.

`load_manifest` refuses anything else: another or a non-final release, `freethreaded = false`, a range or a
missing pin, a pin repeated, an unknown key, a source build that is not pinned. The tests folder must contain the
floor release (from `project.requires-python`, today `>=3.14`, so 3.14.0) and nothing below it; the speed folder
must contain exactly one manifest. Every refusal names the file and the rule.

## How each consumer installs

A test cell (`test-runtime.yml`, one per release and runner) runs:

```bash
python .github/scripts/python_runtime_matrix.py requirements --manifest ".github/python/tests/<release>.toml" --output reports/requirements.txt
uv venv --python "<that release's interpreter>" .venv
uv pip install --no-deps -r reports/requirements.txt
uv pip install --no-deps -e .
uv run --no-sync python .github/scripts/run_runtime_tests.py --report reports/runtime.xml --coverage-report <xml>
```

A speed test's `manifest` job outputs the release. The benchmark job sets that release up, exports it as
`SPEED_PYTHON` and runs `python .github/scripts/python_runtime_matrix.py speed-install --results <its results
folder>`. That refuses any interpreter except the manifest's free-threaded release, writes `requirements.txt`, runs
`pip install --only-binary=:all: --no-binary=<each build_from_source entry> --report install-report.json -r
requirements.txt` and keeps `install.log` beside them. The provenance step then asserts that
`platform.python_version()` equals `SPEED_PYTHON`.

The release candidate's probes install only the published wheel, without dependencies (see the dependency recipe
below).

## Recipes

### Add a Python release (for example 3.14.9)

1. Copy the newest test manifest to `.github/python/tests/3.14.9.toml` and set `python = "3.14.9"`.
2. Make sure every pin installs on that release as a free-threaded wheel (a `cp314t` wheel or a pure-Python one);
   change the pins that do not, in this manifest only.
3. Run the workflow tests ([validating.md](validating.md)). The runtime matrix and the release candidate's probes
   each gain three jobs; nothing else changes.

A new minor (3.15) works the same way. Expect to adjust pins: libraries publish free-threaded wheels for a new
minor on their own schedule.

### Retire releases or raise the floor

1. Change `project.requires-python` in `pyproject.toml`.
2. Delete every test manifest below the new floor and make sure the floor release has one. Discovery refuses
   leftovers instead of skipping them.
3. Update the two places that hard-code today's floor: `metadata_version` in `verify_distributions.py` (it
   requires `Requires-Python` to be `>=3.14`) and `require_free_threading` in `run_runtime_tests.py` (`(3, 14)`).
   Move the helper release too if it falls below the new floor.

### Change a test pin

Edit that pin in each manifest that should change. Releases are independent: an older release may keep an older
pin when a newer version of the library does not support it.

### Add a runtime dependency to Melder (for example LogXide)

1. Add it to `[project.dependencies]` in `pyproject.toml` and update `uv.lock`.
2. Pin it, with its own dependencies, in every test manifest. A test fails while any test manifest leaves out a
   declared dependency.
3. Pin it in the speed manifest too: the speed jobs import Melder from the checkout (`PYTHONPATH=src`), not from
   an installed wheel.
4. Before merging, change the two installed-package probes. They install the wheel without its dependencies and
   would then fail to import Melder: the wheel probe in `build-distributions.yml`
   (`uv pip install --no-deps dist/*.whl`) and `probe_install` in `testpypi_candidate.py`
   (`pip install --no-deps --no-index`). Pinning the dependency for them keeps the probes reproducible.
5. If the documentation build imports Melder, add the dependency to the documentation requirements as well.

### Move the speed tests to another release

Replace the single file in `.github/python/speed/` with one named after the new release; that release must also
have a test manifest. Check that the benchmark pins install on it. The first run afterwards is the new baseline:
benchmark numbers compare only between runs on the same manifest.

### Change the helper release

Replace every `python-version: "3.14.7"` in `.github/workflows/` (including the speed tests' `'3.14.7'`) with the
new release in one change; it must have a test manifest. The contract test refuses a mix.
