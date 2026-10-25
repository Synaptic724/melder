# Python versions and the manifests

CI never chooses a Python release by itself. Every interpreter it sets up is one of these:

| Where | Which Python | Comes from |
| --- | --- | --- |
| Runtime test cells (`test-runtime.yml`) and the release candidate's install probes (`release-candidate.yml`) | Every release that has a test manifest, free-threaded, on Linux x64, Windows x64 and macOS arm64 | `.github/python/tests/<release>.toml`, read by `python_runtime_matrix.py discover` |
| The three speed tests | The one speed release, free-threaded, on three x64 runners | `.github/python/speed/<release>.toml`, read by `python_runtime_matrix.py speed` |
| Every other job (policy, assets, docs, builds, publication, the provenance check, the speed tests' manifest jobs) | The helper release, written as `python-version: "3.14.7"` | The workflow file; the release must have a test manifest |

Nothing is looked up on the network and nothing follows the newest patch, so a new Python release runs only after
someone adds its manifest. `test_workflow_contracts.py` refuses any `setup-python` step that asks for
`check-latest`, a version file, a pre-release, a second helper release, or a release with no test manifest.

## The manifest format

A manifest is a TOML file named after its exact release:

```toml
# .github/python/tests/3.14.0.toml
python = "3.14.0"
freethreaded = true
dependencies = [
    # Melder's runtime dependency ([project.dependencies] in pyproject.toml); the rest is the test group.
    "pip==26.2.2",
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
  The test manifests hold Melder's runtime dependency (pip) and the `test` group's closure from `uv.lock`; the
  speed manifest holds pip and the benchmarks' pins.
- `build_from_source` (optional) lists pinned distributions built from their sdist because no usable wheel
  exists: dependency-injector in the speed manifest, PyYAML in the 3.15 test manifests. The speed install
  passes each to pip as `--no-binary`; a test cell's `uv pip install` builds any pin that has no wheel for
  its release, so in a test manifest the list records which pins are built. Their build tools (setuptools
  and Cython for PyYAML) are fetched into that isolated build only.

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

The two installed-package probes install a built wheel beside Melder's runtime dependencies, at the pins of the
test manifest of the release they run, with no resolver. `python_runtime_matrix.py runtime-requirements` writes
those pins: the manifest's pins of the names in `[project.dependencies]`, refused when the manifest leaves one out.
The wheel probe in `build-distributions.yml` runs, on the helper release:

```bash
python .github/scripts/python_runtime_matrix.py runtime-requirements --output "$RUNNER_TEMP/melder-runtime-requirements.txt"
uv venv --python "<the helper interpreter>" "$RUNNER_TEMP/melder-wheel-probe"
uv pip install --python "$RUNNER_TEMP/melder-wheel-probe/bin/python" --no-deps -r "$RUNNER_TEMP/melder-runtime-requirements.txt" dist/*.whl
uv pip check --python "$RUNNER_TEMP/melder-wheel-probe/bin/python"
```

and then `smoke_wheel.py` in that environment. The release candidate's probe (`testpypi_candidate.py
probe-install`, on every test-manifest release) downloads the wheel from TestPyPI by its hash and the same pins
from PyPI (`pip download --no-deps --only-binary=:all:`), installs them together into a fresh environment with
`pip install --no-deps --no-index`, runs `pip check` and then `smoke_wheel.py`. `pip check` is what proves the
pinned set satisfies the wheel's own requirements.

The provenance check (`testpypi_provenance.py verify`, on the helper release) installs nothing from a test
manifest. It builds its own environment from `.github/provenance/requirements.txt`, the hashed closure of the
publishing action's signing tools, with `pip install --isolated --no-deps --only-binary=:all: --require-hashes`
and then `pip check`. That lock is resolved for the helper release on Linux x64.

## Recipes

### Add a Python release (for example 3.14.9)

1. Copy the newest test manifest to `.github/python/tests/3.14.9.toml` and set `python = "3.14.9"`.
2. Make sure every pin installs on that release as a free-threaded wheel (a `cp314t` wheel or a pure-Python one);
   change the pins that do not, in this manifest only. A pin that has no such wheel in any version may stay
   if its sdist builds on all three runners: list it in `build_from_source`, as the 3.15 manifests do for PyYAML.
3. Run the workflow tests ([validating.md](validating.md)). The runtime matrix and the release candidate's probes
   each gain three jobs; nothing else changes.

A new minor works the same way. Expect to adjust pins: libraries publish free-threaded wheels for a new minor on
their own schedule. 3.15 arrived before PyYAML published a `cp315t` wheel, so its manifests build PyYAML from
source; when a release with that wheel appears, pin it there and drop `build_from_source`.

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
   declared dependency, or pins one at another version than an exact `==` declaration.
3. Pin it in the speed manifest too: the speed jobs import Melder from the checkout (`PYTHONPATH=src`), not from
   an installed wheel. A test fails while the speed manifest leaves out a declared dependency.
4. The installed-package probes follow on their own: both install, beside the wheel, the pins `runtime_pins`
   selects (see "How each consumer installs"), and `pip check` runs before the smoke probe. They select
   declared names only, so a dependency that brings its own dependencies fails `pip check` until `runtime_pins`
   in `python_runtime_matrix.py` selects those too (pip declares none).
5. The documentation build imports Melder from `src` for autodoc (`docs/conf.py`): pin the dependency in
   `docs/requirements.lock` as well.

### Move the speed tests to another release

Replace the single file in `.github/python/speed/` with one named after the new release; that release must also
have a test manifest. Check that the benchmark pins install on it. The first run afterwards is the new baseline:
benchmark numbers compare only between runs on the same manifest.

### Change the helper release

Replace every `python-version: "3.14.7"` in `.github/workflows/` (including the speed tests' `'3.14.7'`) with the
new release in one change; it must have a test manifest. The contract test refuses a mix. A new minor also needs
the provenance tool's lock regenerated for it (the command is in the header of
`.github/provenance/requirements.txt`).
