# Test Mocks Skills

Purpose:
Provide a reusable library of test-only classes and helpers that can be imported
by integration/unit tests without re-defining large object graphs.

Location:
`tests/mocks/` and subfolders (for example, `tests/mocks/spellbook/`).

Usage:
- Import helpers directly from the module you need.
  Example: `from tests.mocks.spellbook import deep_layers`
- These folders are namespace packages; an `__init__.py` is not required for
  imports to work inside this repo.

Notes:
- Prefer reusing shared classes over redefining them inside each test file.
- Keep helpers deterministic and side-effect free.
- When integration tests need concurrency coverage, set
  `phase_scheduler_workers_per_spellbook` to a value greater than 1.
