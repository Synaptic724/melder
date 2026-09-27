from typing import List, Tuple

EDITS_7: List[Tuple[str, str, int]] = [
("""### Flow: Runtime-Heavy Singleton Reset
1. autouse fixture resets `AetherUtilitySystem`, `Nexus`, and `Aether`
   singleton state.
2. some files also rebind `Spellbook._aether`, `Conduit._aether`, and viewer
   class-level `_aether` references.
3. test builds runtime fixtures.
4. fixture teardown resets the same singleton surfaces again.
""",
"""### Flow: Runtime-Heavy Singleton Reset
1. an autouse fixture calls `AetherUtilitySystem._reset_singleton_for_tests()`,
   `Nexus._reset_singleton_for_tests()` and `Aether._reset_singleton_for_tests()`.
   A reset cleans and forgets the instance; it boots nothing.
2. the fixture boots `Aether()`, which builds the Nexus and the other hosted
   roots, and binds it to the class-level references its tests use. Three exist in
   src: `Spellbook._aether` (a `ClassVar`), `CommandSystem._aether` and
   `StaticFrameViewer._aether`. `Conduit` has no class-level `_aether`, so the
   `Conduit._aether = ...` lines many test files carry set an attribute nothing
   reads.
3. test builds runtime fixtures.
4. teardown repeats steps 1-2; `tests/unit/melder/aether/conduit/conftest.py:65-85`
   is the model. A teardown that stops after step 1 leaves no world, and the next
   file's `Spellbook()` raises "Nexus must be initialized with an Aether instance".
   `tests/unit/melder/test_system_document_view.py:51-84` did that until
   2026-09-26 (its teardown now ends by booting); the registration-guard file now
   boots its own world (`tests/unit/melder/test_melder_registration_guard.py:22-45`).
""", 1),
("""### Flow: Capability Rift JSON Bench
1. harness builds two Spellbooks/conduits plus one capability Rift stack.
2. harness exposes the same JSON-like surface concept over capability-room
   behavior.
3. request matrix and turn-script tests drive the live capability room.
4. harness cleanup tears down owned runtime objects.
""",
"""### Flow: Capability Rift JSON Bench
1. harness builds two Spellbooks/conduits plus one capability Rift stack.
2. harness exposes the same JSON-like surface concept over capability-room
   behavior.
3. request matrix and turn-script tests drive the live capability room.
4. harness cleanup tears down owned runtime objects.

### Flow: CI Runtime Qualification
1. the workflow sets `PYTHON_GIL: "0"` and runs `run_runtime_tests.py` with
   `--report` and `--coverage-report` (`.github/workflows/test-runtime.yml:70-73`).
2. `main` parses its arguments, imports pytest and calls
   `require_free_threading(sys.version_info, Py_GIL_DISABLED, sys._is_gil_enabled())`,
   which raises `RuntimeError` unless the process is 3.14+, free-threaded and
   running with the GIL off.
3. `pytest.main(["-q", "tests/unit", "tests/component", "tests/integration",
   "--junitxml=..."])`, plus `--cov=melder --cov-branch --cov-report=xml:...` when
   a coverage report was requested.
4. `require_free_threading` runs again on the same process, then `main` returns
   pytest's exit code unchanged.
   EVIDENCE: .github/scripts/run_runtime_tests.py:10-50

### Flow: Concurrent-Writer Stand-In
1. the regression builds a real Spellbook, binds `PoolConfig`, `PoolRepository` and
   `PoolService`, and conjures, so every compiler pass has a real graph.
2. it replaces `spellbook._spell_id_pool` with `_GrowsWhileIterated`, a dict whose
   `items`/`values`/`keys`/iteration insert one entry after yielding the first,
   which is what a live iteration sees when another thread binds; its `copy()`
   returns the entries as they were, as a real pool's copy does.
3. each test runs one pass - a structural rerun, Phase 5 local, Phases 5 and 6
   frame-wide, the Phase-8 walk - and asserts the pass completes (and, for Phase 5,
   that an entry with no registered state is left out). On source that iterates the
   live pool they fail as the race did: "dictionary changed size during iteration",
   "requires a live SpellSystemState", or a Phase-8 walk that returns None.
   EVIDENCE:
   - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py:51-103
   - tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py:148-235
""", 1),
# C1 intro
("""above - 118 paths - and nothing else. Change a component's key files and this set
follows; if the two ever disagree, this section is wrong, not the catalog.
""",
"""above - __CORE_COUNT__ paths - and nothing else. Change a component's key files and this set
follows; if the two ever disagree, this section is wrong, not the catalog.
""", 1),
("""builders - not every `test_*.py` module beneath it. The 638 test modules are the
component's CONTENT; they are counted in each entry rather than cited, because a
""",
"""builders - not every `test_*.py` module beneath it. The 743 test modules of the
three CI tiers (and the 33 experimentation modules) are the component's CONTENT;
they are counted in each entry rather than cited, because a
""", 1),
("""Every range was MEASURED from disk on 2026-08-02. THIS SIDE HAS NO GRAPH TO JOIN
""",
"""Every range was RE-MEASURED from disk on 2026-09-26 (first measured 2026-08-02);
each entry's `verified_at` is the pass that measured it. THIS SIDE HAS NO GRAPH TO JOIN
""", 1),
# Diagrams
("""[pytest + pyproject]
        |
        v
[conftest bootstrap]
""",
"""[CI: test-runtime.yml -> run_runtime_tests.py]   (free-threaded gate before + after)
        |
        v
[pytest + pyproject]
        |
        v
[conftest bootstrap]
""", 1),
("""[mocks] feed spellbook and crystallizer test lanes
```
""",
"""[mocks] feed spellbook and crystallizer test lanes
[unit/github_workflows, llm_support, architecture_and_design] test repository tooling
[experimentation + experiments/cprofile_testing] local only; CI never runs them
```
""", 1),
("""graph TD
  P["pytest / pyproject"] --> C["conftest bootstrap"]
""",
"""graph TD
  CI["CI: run_runtime_tests.py"] -->|"unit, component, integration"| P
  P["pytest / pyproject"] --> C["conftest bootstrap"]
""", 1),
("""  M["tests/mocks"] --> U
  M --> CP
```
""",
"""  M["tests/mocks"] --> U
  M --> CP
  EX -.->|"imported as cases"| CP
  EX -.-> I
  RT["repository tooling tests"] --> U
  LOC["experimentation probes (local pytest only)"] -.-> EX
```
""", 1),
# Information Sources
("""- `pyproject.toml`
- `tests/conftest.py`
- `tests/_annotation_audit_support.py`
""",
"""- `pyproject.toml`
- `tests/conftest.py`
- `.github/scripts/run_runtime_tests.py`
- `.github/workflows/test-runtime.yml`
- `tests/unit/github_workflows/conftest.py`
- `tests/unit/melder/aether/conduit/conftest.py`
- `tests/unit/melder/test_system_document_view.py`
- `tests/unit/melder/test_melder_registration_guard.py`
- `tests/unit/melder/spellbook/spell_compiler/phases/test_compiler_pool_snapshot_reads.py`
- `tests/experiments/cprofile_testing/README.md`
- `src/melder/aether/spellbook/spellbook.py` (`Spellbook._aether`, the one `ClassVar` Aether cache)
- `src/melder/nexus/rift/command_system/command_system.py` (`CommandSystem._aether`)
- `src/melder/nexus/rift/frame_viewer/static_frame_viewer.py` (`StaticFrameViewer._aether`)
- module docstrings and test names of every file cited in a `Protects:` line (read 2026-09-26)
- `tests/_annotation_audit_support.py`
""", 1),
# Open questions
("""- Whether future external CI/docs should describe a formal marker taxonomy or
  shard map; no in-repo CI workflow evidence exists in this checkout.
""",
"""- ANSWERED 2026-09-26 (was: whether future external CI/docs should describe a
  formal marker taxonomy or shard map; no in-repo CI workflow evidence existed).
  CI is in the repository and runs no shards; tiers are selected by directory,
  not by the declared `integration` and `component` markers.
- Whether the tracked generated packages under tests/experimentation/ and the six
  `bundle.json` leftovers should leave the repository (see `## Unknowns`).
""", 1),
# Handoff
("""## Context / Handoff Summary

2026-09-26 override site-plan lane:""",
"""## Context / Handoff Summary

REFRESHED 2026-09-26 (paired with the `tests_architecture` refresh). Every C3 entry
and every test C2 cluster now carries a `Protects:` line naming the behaviour it
guards, read from the tests' own docstrings and names. New: the CI driver in the
runner component, an Experimentation And Profiling Trees component (local only),
C2 clusters for the package root, build assets, utilities (unit and component),
repository tooling, conduit, multithreading and live-sim lanes, and the CI and
concurrent-writer flows. Corrected: the `codex*` exclusion claim (no such entry),
the singleton-reset flow (a reset boots nothing; three class-level Aether caches;
`Conduit._aether` assignments are inert), and every tree count. The index commands
moved out of `## Indexing` (portability rule). C1 ranges remeasured and the core
set rebuilt as the union of the Key Files lists. Open: the per-run CI matrix, the
tracked generated experimentation packages and the six `bundle.json` leftovers.
Next to map: the conduit integration lane per file, and the aether unit tree (183
modules) below cluster level.

2026-09-26 compiler pool reads: `test_compiler_pool_snapshot_reads.py` joined the
Spellbook Compiler Unit Cluster (see `### Flow: Concurrent-Writer Stand-In`).

2026-09-26 override site-plan lane:""", 1),
]
