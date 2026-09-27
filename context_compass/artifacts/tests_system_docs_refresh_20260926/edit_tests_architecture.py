"""Refresh tests_architecture.md (2026-09-26). Anchored str edits; --check writes nothing."""
import pathlib
import sys

DOC = pathlib.Path.home() / "mnt/melder_private/context_compass/system_docs/tests_architecture.md"
E = []

E.append(("- Updated: 2026-06-13\n", "- Updated: 2026-09-26\n"))
E.append(("- deterministic fixture/mocks under `tests/mocks/`\n",
          "- deterministic fixture/mocks under `tests/mocks/`\n"
          "- a locally collected experimentation tree under `tests/experimentation/`\n"
          "  (under `testpaths`, outside the three tiers CI runs)\n"))
E.append(("""This document is AUTHORED. Its only generated companion is
`tests_architecture_index.md`, rebuilt in the SAME pass as any edit:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_architecture.md
```

Consume it by slicing rather than reading this document whole, and verify before
trusting a range:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_architecture.md --slice "<section name>"
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_architecture.md --check
```
""", """This document is AUTHORED. Its only generated companion is its index
(`tests_architecture_index`), rebuilt in the SAME pass as any edit by the
documentation tooling that maintains these documents. The commands live with that
tooling, not here: this document ships with the code and the tooling does not.

Consume it by slicing a named section rather than reading it whole, and verify the
index proof (line count, line ending, content hash) before trusting a range.
"""))
E.append(("""- UNKNOWN: external CI shard/split behavior is not documented here.
  Why it matters: a future reader may otherwise assume the local pytest layout
  is the whole execution topology.
  Local evidence boundary: this checkout has no in-repo `.github/` workflow
  config, so there is no local CI topology to cite here.
  Where to investigate: external CI configuration outside this checkout.
  Current status: blocked on external evidence.
""", """- RESOLVED 2026-09-26 (was UNKNOWN: external CI shard/split behavior, blocked while
  the checkout had no in-repo `.github/` workflow config). CI now lives in the
  repository and does not shard: `.github/workflows/test-runtime.yml` runs
  `.github/scripts/run_runtime_tests.py`, which runs `tests/unit`,
  `tests/component` and `tests/integration` in ONE pytest process per OS/Python
  cell. See `## System Boundary and External Interfaces`.
- UNKNOWN: which Python minors a given CI run tested.
  Why it matters: the matrix is discovered at run time (every stable free-threaded
  minor at or above the `requires-python` floor, on three runners), so no file in
  the tree records the versions a run used.
  Where to investigate: the `runtime-python-matrix-*` artifact of that run.
  Current status: by design; recorded per run, not in the tree.
- UNKNOWN: whether the six tracked `bundle.json` files under
  tests/unit/melder/utilities/_caching_system_tmp_load_*/ are fixtures or leftovers.
  Why it matters: no current test references those directories (the caching tests
  that write cwd-relative directories use other names, and newer ones use
  `tmp_path`), so they are either dead fixtures or committed droppings.
  Where to investigate: `tests/unit/melder/utilities/test_caching_system.py` history.
  Current status: raised to the owner; not changed.
"""))
E.append(("""Primary test entrypoint:
- pytest, configured through `[tool.pytest.ini_options]` in `pyproject.toml`
""", """Primary test entrypoint:
- pytest, configured through `[tool.pytest.ini_options]` in `pyproject.toml`

CI entrypoint (verified 2026-09-26 against the files named):
- `.github/scripts/run_runtime_tests.py`, called by `.github/workflows/test-runtime.yml`
  (itself called by `.github/workflows/ci.yml` for pull requests). It calls
  `pytest.main` with `-q tests/unit tests/component tests/integration` and a JUnit
  report, adds `--cov=melder --cov-branch` when a coverage report is requested, and
  raises before AND after the run unless the process is Python 3.14+ built
  free-threaded with the GIL off. `tests/experimentation/` is therefore collected by
  a local `pytest` (it sits under `testpaths`) and never by CI.
- Matrix: `.github/scripts/python_runtime_matrix.py` discovers every stable
  free-threaded Python minor at or above the `requires-python` floor for
  ubuntu-latest (x64), windows-latest (x64) and macos-latest (arm64). Each cell
  installs locked test dependencies (`uv sync --locked --group test`) and runs with
  `PYTHON_GIL=0`. Coverage uploads only after every cell reported, and an upload
  failure does not fail the run.
- Nothing in the repository runs the GIL-enabled posture. Lanes that need it run the
  suites by hand with `PYTHON_GIL=1` on the same interpreter.
"""))
E.append(("""- `tests/integration/melder/aether`, `conduit`, `crystallizer`,
  `live_sim`, `multithreading`, `mutation_research`, and `spellbook`
""", """- `tests/integration/melder/aether`, `conduit`, `crystallizer`,
  `live_sim`, `multithreading`, `mutation_research`, and `spellbook`
- `tests/unit/` also holds three trees that test repository tooling, not `melder`:
  `github_workflows` (the CI scripts, loaded by path through their own conftest),
  `llm_support` (the whole-repository text-bundle builder) and
  `architecture_and_design` (the architecture-docs tool)
- `tests/experimentation/` holds 33 `test_*.py` experiment and probe modules beside
  the synthetic-module benches; a local `pytest` collects them, CI does not
"""))
E.append(("""  source of runner truth.
""", """  source of runner truth. The CI driver `.github/scripts/run_runtime_tests.py` is a
  thin `pytest.main` wrapper, not a second runner: it adds tier selection,
  JUnit/coverage output and the free-threading gate below.
- GUARDRAIL - FREE THREADING (CI): the driver raises before and after pytest unless
  the interpreter is 3.14+, built free-threaded and running with the GIL disabled,
  so an import or plugin that re-enables the GIL fails the run instead of passing
  on the wrong runtime.
"""))
E.append(("""  file would silently depend on whichever file ran before it.
""", """  file would silently depend on whichever file ran before it.
  A reset BOOTS NOTHING: `_reset_singleton_for_tests()` cleans the instance and
  clears the bookkeeping, and constructs no new world. `Spellbook`, `CommandSystem`
  and `StaticFrameViewer` hold class-level `_aether` references bound at import, and
  `Spellbook()` asks for the Nexus that an Aether boot builds. A fixture that
  resets must therefore boot `Aether()` again and rebind the class references its
  tests use, after as well as before (see `### Flow: Singleton Reset And Re-Boot`).
"""))
E.append(("""3. Scoped conftests apply beneath their directories, and there are only THREE
   in the tree - the root, `tests/integration/melder/live_sim/conftest.py`
   (29 lines, providing `reset_aether_singleton_for_live_sim`), and
   `tests/unit/melder/aether/conduit/conftest.py` (444 lines, the largest by an
   order of magnitude, providing `fresh_singletons`, `configuration_automatic`,
   `configuration_dynamic` and the spellbook/aether/dev-ops stubs).
""", """3. Scoped conftests apply beneath their directories, and there are FOUR in the
   tree (three until the CI tests arrived) - the root,
   `tests/integration/melder/live_sim/conftest.py` (28 lines, providing
   `reset_aether_singleton_for_live_sim`),
   `tests/unit/melder/aether/conduit/conftest.py` (445 lines, the largest by an
   order of magnitude, providing `fresh_singletons`, `configuration_automatic`,
   `configuration_dynamic` and the spellbook/aether/dev-ops stubs), and
   `tests/unit/github_workflows/conftest.py` (73 lines), which prepends
   `.github/scripts` to `sys.path` per test and loads each CI script by path, so
   those tests create no runtime package and never boot Melder.
"""))
E.append(("""### Flow: Viewer/ACL Matrix Fixture Path
""", """### Flow: CI Runtime Qualification
1. `ci.yml` routes a pull request through `branch-policy`; when the runtime is in
   scope it calls `test-runtime.yml` (and the asset and documentation checks).
2. `discover` computes the OS/Python matrix and keeps it as an artifact.
3. each cell sets up a free-threaded Python, installs locked test dependencies and
   runs `run_runtime_tests.py` with `PYTHON_GIL=0`.
4. the driver checks the runtime, runs the three tiers in one pytest process,
   checks the runtime again and returns pytest's exit code; JUnit XML is always
   kept, coverage XML only when the run passed.
5. `coverage` requires a report from every cell before uploading to Codecov.

### Flow: Singleton Reset And Re-Boot
1. an autouse fixture resets `AetherUtilitySystem`, `Nexus` and `Aether`.
2. it boots a fresh `Aether()`, which builds the Nexus, utility system and the
   other hosted roots, and rebinds the class-level `_aether` references its tests
   use (`Spellbook._aether` at least).
3. the test runs; teardown repeats steps 1-2 so the next file finds a live world.
4. skipping step 2 leaves no Aether behind: the next `Spellbook()` raises "Nexus
   must be initialized with an Aether instance" inside a test that did nothing
   wrong. The system-document view fixtures did this until 2026-09-26, which made
   `test_bind_rejects_internal_class` depend on test order.

### Flow: Concurrent-Writer Stand-In
1. a regression for a race builds the real runtime (a Spellbook, bindings, a
   conjured conduit) instead of starting threads.
2. it swaps the shared structure for a stand-in whose iteration performs the
   concurrent write deterministically (for the spell pool: a dict that inserts one
   entry after yielding its first item, and whose `copy()` returns the entries as
   they were).
3. the pass under test runs once: before the fix it fails the way the race did,
   after it passes. The multithreading suite stays the stress layer, but a rare
   race is proven by the stand-in, not by rerunning the suite.
   EVIDENCE: tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py:51-103

### Flow: Viewer/ACL Matrix Fixture Path
"""))
E.append(("""- The capability Rift bench is intentionally real-runtime, not pure mocks.
""", """- The capability Rift bench is intentionally real-runtime, not pure mocks.
- CI runs exactly `tests/unit`, `tests/component` and `tests/integration`, in one
  pytest process per OS/Python cell, free-threaded only. A local `pytest` also
  collects `tests/experimentation/`.
- A singleton reset is always followed by a re-boot before the fixture yields and
  after it tears down; a bare reset leaves the next test without a world.
- Races are proven by deterministic stand-ins for the concurrent writer; the
  multithreading lane is stress coverage, not the proof.
"""))
E.append(("""- SINGLETON BLEED: a runtime-heavy test that does not reset `Aether`, `Nexus`
  or `Spellbook` state leaves the next test running against a world it did not
  build. The failure surfaces in an unrelated test file, which is what makes it
  expensive - the reset fixtures exist to stop it.
""", """- SINGLETON BLEED: a runtime-heavy test that does not reset `Aether`, `Nexus`
  or `Spellbook` state leaves the next test running against a world it did not
  build. The failure surfaces in an unrelated test file, which is what makes it
  expensive - the reset fixtures exist to stop it.
- SINGLETON VOID: the reverse, a teardown that resets without booting a new Aether.
  The next test's `Spellbook()` raises "Nexus must be initialized with an Aether
  instance". It passes alone and fails after the offending file, so check the
  previous file's fixture teardown before the failing test.
- RUNTIME POSTURE (CI): a GIL-enabled process fails the CI driver's gate before or
  after pytest, with the instruction to use a free-threaded build and `PYTHON_GIL=0`.
- TREE ARTIFACTS: cache tests write inside the repository - nine `CachingSystem`
  unit tests use cwd-relative `tests/unit/melder/utilities/_caching_system_tmp_*`
  directories (under `tests/tests/...` when pytest runs from `tests/`), and
  component cache tests write under the package directory (`src/melder/tests/...`).
  `.gitignore` covers `*.melc` and the `tests/tests/...` form, so the caches never
  reach a commit, but they survive between runs; newer tests use `tmp_path`.
"""))
E.append(("""- `unit/`: 334 `.py` files
- `component/`: 81 `.py` files
- `integration/`: 88 `.py` files
- `mocks/`: 42 `.py` files
""", """- `unit/`: 464 `.py` files (334 on 2026-06-13)
- `component/`: 143 `.py` files (81)
- `integration/`: 148 `.py` files (88)
- `mocks/`: 44 `.py` files (42)
- `experimentation/`: 196 `.py` files, 33 of them `test_*.py` (not counted before)
Recounted 2026-09-26 with `find tests/<tier> -name '*.py'` (pycache excluded).
"""))
E.append(("""- Whether any external CI system shards or subsets the suite beyond the local
  pytest entrypoint; no in-repo CI workflow evidence exists in this checkout.
""", """- ANSWERED 2026-09-26: whether any external CI system shards or subsets the suite
  beyond the local pytest entrypoint. It does not shard; it subsets to the three
  tiers (see `## System Boundary and External Interfaces`). The question read "no
  in-repo CI workflow evidence exists in this checkout" until the workflows landed.
"""))
E.append(("""[frame-posture support] and [codegen/compiler helpers] feed runtime-heavy lanes
[shared helpers + mocks] feed all three tiers
```
""", """[frame-posture support] and [codegen/compiler helpers] feed runtime-heavy lanes
[shared helpers + mocks] feed all three tiers

[CI: ci.yml -> test-runtime.yml -> run_runtime_tests.py (free-threaded gate)]
        |  one pytest process per OS/Python cell
        v
[unit/] [component/] [integration/]        [experimentation/] local pytest only
```
"""))
E.append(("""  SH --> I
```
""", """  SH --> I
  CI["CI: test-runtime.yml / run_runtime_tests.py"] -->|"free-threaded, one process"| U
  CI --> CP
  CI --> I
  L["local pytest (testpaths)"] --> X["tests/experimentation"]
```
"""))
E.append(("""- `tests/unit/melder/aether/test_command_system_direct.py`
- direct filesystem inventory of `tests/`
""", """- `tests/unit/melder/aether/test_command_system_direct.py`
- `.github/workflows/ci.yml`
- `.github/workflows/test-runtime.yml`
- `.github/scripts/run_runtime_tests.py`
- `.github/scripts/python_runtime_matrix.py`
- `tests/unit/github_workflows/conftest.py`
- `tests/integration/melder/live_sim/conftest.py`
- `tests/unit/melder/aether/conduit/conftest.py`
- `tests/unit/melder/test_system_document_view.py`
- `tests/unit/melder/test_melder_registration_guard.py`
- `tests/unit/melder/utilities/test_caching_system.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`
- `.gitignore`
- direct filesystem inventory of `tests/`
"""))
E.append(("""## Context / Handoff Summary

""", """## Context / Handoff Summary

REFRESHED 2026-09-26 (first update since 2026-06-13 besides the August
recomposition). CI now lives in the repository: one free-threaded pytest process per
OS/Python cell over the three tiers, with `tests/experimentation/` collected only
locally. Added the fourth conftest (CI scripts), the singleton-reset rule that a
reset boots nothing (and the SINGLETON VOID failure it prevents), the
concurrent-writer stand-in pattern for race regressions, the in-tree cache
artifacts, and recounted the inventory. The index commands were moved out of
`## Indexing` to the documentation tooling (portability rule). C1 ranges remeasured.
Open: the per-run CI matrix, and six tracked `bundle.json` leftovers under
tests/unit/melder/utilities/ that no test references.

"""))


def main() -> int:
    """Apply every edit once, or report mismatches."""
    check = "--check" in sys.argv
    t = DOC.read_text(encoding="utf-8")
    for old, new in E:
        n = t.count(old)
        if n != 1:
            print("MISMATCH", n, repr(old[:70]))
            return 1
        t = t.replace(old, new)
    long = [ln for ln in t.split("\n") if len(ln) > 120 and "`" not in ln]
    print("edits", len(E), "long prose lines", len(long))
    if not check:
        DOC.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
