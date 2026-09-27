"""Follow-up corrections to tests_architecture.md found while refreshing tests_components (2026-09-26)."""
import pathlib
import sys

DOC = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/tests_architecture.md"
EDITS = [
("""- TREE ARTIFACTS: cache tests write inside the repository - nine `CachingSystem`
  unit tests use cwd-relative `tests/unit/melder/utilities/_caching_system_tmp_*`
  directories (under `tests/tests/...` when pytest runs from `tests/`), and
  component cache tests write under the package directory (`src/melder/tests/...`).
  `.gitignore` covers `*.melc` and the `tests/tests/...` form, so the caches never
  reach a commit, but they survive between runs; newer tests use `tmp_path`.
""",
"""- TREE ARTIFACTS: cache tests write inside the repository - twelve `CachingSystem`
  unit tests use cwd-relative `tests/unit/melder/utilities/_caching_system_tmp_*`
  directories (under `tests/tests/...` when pytest runs from `tests/`), and
  component cache tests write under the package directory (`src/melder/tests/...`).
  `.gitignore` covers `*.melc` and the `tests/tests/...` form, so the `.melc` caches
  never reach a commit (six `bundle.json` files under the `_load_*` directories did;
  see `## Unknowns`), but they survive between runs; newer tests use `tmp_path`. The
  two synthetic-module benches write case packages under
  tests/experimentation/_physical_to_synth_swap_tmp/ and _synthetic_edge_tmp/ and
  remove them with `shutil.rmtree(..., ignore_errors=True)`; 140 such files are
  tracked (see `## Unknowns`).
""", 1),
("""  join against. A renamed or deleted test file leaves a citation that still
  parses and points nowhere. Existence must be checked explicitly; see
  `## Indexing` and the recipe in `tests_components_instructions.md`.
""",
"""  join against. A renamed or deleted test file leaves a citation that still
  parses and points nowhere. Existence must be checked explicitly; see the
  recipe under `## Indexing`.
""", 1),
("""- `tests/experimentation/` holds 33 `test_*.py` experiment and probe modules beside
  the synthetic-module benches; a local `pytest` collects them, CI does not
""",
"""- `tests/experimentation/` holds 33 `test_*.py` experiment and probe modules beside
  the synthetic-module benches; a local `pytest` collects them, CI does not
- `tests/experiments/cprofile_testing/` holds opt-in crystallizer and
  mutation-research profiling scripts; no file there matches default discovery
  (its `pytest_profile_*.py` wrappers run only when passed explicitly)
""", 1),
("""  Where to investigate: `tests/unit/melder/utilities/test_caching_system.py` history.
  Current status: raised to the owner; not changed.
""",
"""  Where to investigate: `tests/unit/melder/utilities/test_caching_system.py` history.
  Current status: raised to the owner; not changed.
- UNKNOWN: whether the 140 tracked `.py` files under
  tests/experimentation/_physical_to_synth_swap_tmp/ and _synthetic_edge_tmp/ belong
  in the repository.
  Why it matters: they are case packages the synthetic-module benches write (50 of
  the tree's 57 `__init__.py` files); each case gets a fresh directory, so no run
  reads the tracked copies back.
  Where to investigate: `tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py`
  and `tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py` teardown.
  Current status: raised to the owner; not changed.
""", 1),
]


def main() -> int:
    """Apply each anchored edit exactly once."""
    t = DOC.read_text(encoding="utf-8")
    for old, new, count in EDITS:
        if t.count(old) != count:
            raise SystemExit(f"ANCHOR {t.count(old)}: {old[:70]!r}")
        t = t.replace(old, new)
    DOC.write_text(t, encoding="utf-8")
    print("ok", len(t.split("\n")) - 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
