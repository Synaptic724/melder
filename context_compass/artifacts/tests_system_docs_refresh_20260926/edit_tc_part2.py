from typing import List, Tuple

EDITS_2: List[Tuple[str, str, int]] = [
# E6 Pytest Runner component
("""Purpose:
- Start the suite from the repo root and bind test imports to `src/`.

Responsibilities:
- Define pytest collection roots through `pyproject.toml`.
- Exclude non-test worktrees and generated/cache directories.
- Prepend `src/` to `sys.path` through `tests/conftest.py`.

Inputs:
- `pyproject.toml`
- local repo filesystem layout

Outputs:
- consistent import path for local `melder` code
- stable pytest collection root at `tests/`

Owned State:
- path/bootstrap logic only; no long-lived runtime state

Lifecycle/Cleanup:
- bootstrap happens at pytest startup/import time

Concurrency/Threading:
- no explicit threading concerns

Invariants/Guarantees:
- local tests target local `src/`
- `codex*` worktrees are excluded from pytest recursion by config

Failure Modes:
- broken path bootstrap would cause import failure or wrong-package import

Observability:
- visible through pytest import/collection behavior

Extension Points:
- future pytest options or marker config in `pyproject.toml`

Key Files (C1):
- `pyproject.toml`
- `tests/conftest.py`
""",
"""Purpose:
- Start the suite from the repo root and bind test imports to `src/`; in CI, run
  the three tiers on a verified free-threaded interpreter.

Responsibilities:
- Define collection through `[tool.pytest.ini_options]` in `pyproject.toml`:
  `testpaths = ["tests"]`, a `norecursedirs` list (`benchmarks`, `Plans`,
  `context_compass`, `UX_and_AIX_experiences`, `performance_hunt`, `profiles`,
  `build_scripts`, `.venv`, `.venv_new`, `__pycache__`, `__melder_cache__`) and the
  two declared markers `integration` and `component`.
- Prepend `src/` and the project root to `sys.path` through `tests/conftest.py`;
  the second lets `import tests.mocks...` and the `tests/_*_support` modules
  resolve under a bare `pytest`, not only under `python -m pytest`.
- In CI, `run_runtime_tests.py` `main` runs `tests/unit`, `tests/component` and
  `tests/integration` in one `pytest.main` call with a JUnit report, adding
  `--cov=melder --cov-branch` into one XML only when `--coverage-report` is given.

Protects:
- that tests import the workspace `src/`, never an installed `melder`
- that a CI result comes from a 3.14+ free-threaded build with the GIL off for the
  whole run: `require_free_threading` raises before `pytest.main` and again after
  it, so an import or plugin that re-enabled the GIL fails the run
- that the driver's exit code is pytest's exit code, never masked by reporting

Inputs:
- `pyproject.toml`; the local filesystem layout
- CI: `--report` (JUnit path), optional `--coverage-report`, and `PYTHON_GIL=0`,
  which the workflow sets for the test process

Outputs:
- one import path for local `melder` code; collection rooted at `tests/`
- CI: JUnit XML on every run; coverage XML when requested

Owned State:
- two `sys.path` entries, each inserted only when absent; no runtime state

Lifecycle/Cleanup:
- bootstrap runs once when pytest imports the root conftest; the CI runtime check
  runs in the same process before and after `pytest.main`

Concurrency/Threading:
- no threads of its own; the driver's contract is the process's threading posture
  (free-threaded build, GIL disabled), not test concurrency

Invariants/Guarantees:
- local tests target local `src/`
- collection never enters a `norecursedirs` tree; the list names no `codex*` entry
  (an earlier revision of this entry claimed worktrees were excluded - they are not)
- CI never shards: one pytest process per OS/Python cell runs all three tiers, and
  `tests/experimentation/` is not among them

Failure Modes:
- broken path bootstrap: import failure or a wrong-package import
- `RuntimeError` from the driver naming the required runtime (3.14+ free-threaded,
  `PYTHON_GIL=0`), before or after the run
- a new top-level tree with Python that is not in `norecursedirs` is collected
  silently

Observability:
- pytest import/collection output; the JUnit report of each CI cell

Extension Points:
- markers or options in `pyproject.toml`; tier arguments in the driver

Key Files (C1):
- `pyproject.toml`
- `tests/conftest.py`
- `.github/scripts/run_runtime_tests.py`
- `.github/workflows/test-runtime.yml`
""", 1),
# E7 Shared Test Support gains Protects
("""- Resolve manifest placeholders and turn-script references for JSON-driven
  integration tests.

Inputs:
- descriptor payload builders
""",
"""- Resolve manifest placeholders and turn-script references for JSON-driven
  integration tests.

Protects:
- that viewer and ACL tests at all three tiers assert against one descriptor and
  compiled-surface shape: `_nexus_viewer_matrix_support.py` is imported by 38 unit,
  18 component and 6 integration files, so a projection change fails every tier
  together instead of drifting in one
- that static and capability room behaviour is proven on real runtime stacks (the
  Rift JSON benches), not on mocks
- that every annotation in `src/melder` stays evaluable on 3.14
  (`_annotation_audit_support.py`, enforced by
  `tests/unit/melder/test_annotation_integrity.py`)

Inputs:
- descriptor payload builders
""", 1),
]
