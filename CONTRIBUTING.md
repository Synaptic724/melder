# Working on Melder

The repository includes `uv.lock` so contributors can install the same resolved development
dependencies across supported platforms. Melder itself has no runtime package dependencies.
Applications installing Melder maintain their own lockfiles; this lock describes the checkout.

## Create the development environment

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) version 0.11.23 or newer.
From a clone of this repository, run:

```bash
uv sync --locked --python 3.14t
uv run --locked python -X gil=0 -c "import sys, sysconfig; print(sys.version); assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1; assert not sys._is_gil_enabled()"
```

The `t` requests free-threaded Python. Select the exact version shown in a CI report when
reproducing a version-specific failure, for example `--python 3.14.7t`. The lock supports the
Python range declared in `pyproject.toml`; it does not pin the interpreter to one minor version.

`uv sync` creates `.venv`, installs Melder in editable mode and includes the default `dev` group:
test, lint and build tools. Use a dedicated checkout/environment: syncing removes packages that
are outside the selected groups. To choose a different environment location, set
`UV_PROJECT_ENVIRONMENT` before running the commands.

`--locked` refuses a stale lock instead of changing it during installation. Commit dependency
declarations and the regenerated lock together when intentionally changing requirements.

## Run checks

```bash
uv run --locked python -X gil=0 .github/scripts/run_runtime_tests.py --report reports/runtime.xml
uv run --locked python src/melder/_build_assets/_build_asset_runner.py --check
uv run --locked python llm_support/_builder.py --check
```

The test driver runs unit, component and integration tests and verifies the GIL remains disabled.
To focus on one test file, use `uv run --locked python -X gil=0 -m pytest <path>`.

CI uses this same lock. Its dynamic OS/Python matrix first selects a free-threaded interpreter,
then passes that interpreter to `uv sync --locked --no-default-groups --group test`.
The lock chooses dependencies for each matrix environment; it does not collapse the Python matrix.
Distribution jobs install only the locked `build` group. CI uses the minimum supported uv version
declared in `pyproject.toml`, and a stale lock fails the install step.

Extra development groups are opt-in:

```bash
uv sync --locked --python 3.14t --group typecheck
uv run --locked --group typecheck mypy
```

The other optional groups are `parallel`, `codemod` and `benchmark`. Use `--all-groups` when you
need all of them. Documentation uses its separate locked environment; see
[documentation maintenance](docs/maintaining.md).

## Build and inspect the package

The default development environment includes the locked build backend and build tools:

```bash
uv run --locked python -m build --no-isolation --sdist --wheel
uv run --locked python .github/scripts/verify_distributions.py
```

Build isolation is disabled here so the build uses the installed locked toolchain. The resulting
wheel and source archive still pass the repository's distribution checks. No publishing occurs.

## Update dependencies deliberately

```bash
uv lock --check
uv lock --upgrade-package pytest
uv sync --locked --python 3.14t
```

Use `uv lock` after editing dependency declarations, and `uv lock --upgrade` only for an intentional
refresh of the entire resolution. Review the diff and validate the affected checks before committing
`pyproject.toml` and `uv.lock`. Keep private indexes, credentials and machine-local dependency paths
out of the shared lock. `pip install melder` remains the normal package-consumer installation path.
