from typing import Dict, List, Tuple

SECTIONS_4: Dict[str, str] = {
"### Component: Integration Runtime Suite\n": """Purpose:
- Validate real runtime wiring across Melder subsystems and AR surfaces.

Responsibilities:
- build real Spellbook/Conduit/Nexus/Rift stacks
- exercise descriptor projection and viewer matrices
- exercise room-mode harnesses and JSON-like request drivers
- cover additional integration lanes for conduit, crystallizer, live_sim,
  multithreading, mutation_research, and spellbook behavior

Protects:
- behaviour that only exists once several real subsystems are wired: meld through
  the real front door across linked and clustered conduits, scope ordering and
  existence across lineages and SpellSpaces, contracts and ownership transfer,
  disposal order at scoped teardown, Nexus projection after passive publication,
  and room behaviour driven through the Rift benches
- the concurrency claims the unit tier cannot make: link/contract churn under
  concurrent melds, the meld lock order (shapes that deadlocked before the
  per-slot build locks), and thread-safe lazy loading of the packaged documents
  (see `### Subcomponent: Multithreading Integration Cluster`)
- a whole application bootstrapped the way a user would, automatic and dynamic
  (see `### Subcomponent: Live Sim Integration Cluster`)

Inputs:
- real runtime objects
- shared bench support

Outputs:
- end-to-end or near-end-to-end behavioral assertions

Owned State:
- harness-local runtime objects and manifests

Lifecycle/Cleanup:
- runtime-heavy files reset singleton surfaces and cleanup harness-owned
  objects explicitly

Concurrency/Threading:
- the multithreading directory drives real threads: orchestrated mutation lanes
  against concurrent meld workers, lock-order shapes run in child processes under
  gate timeouts with a `subprocess.run(timeout=...)` backstop, and sixteen-thread
  races on first lazy loads; the conduit concurrency file stresses
  concurrent melds across four linked conduits

Invariants/Guarantees:
- integration tests use real runtime stacks rather than hand-built shallow mocks
- 141 `test_*.py` modules among 148 `.py` files; the others are benches and the
  live-sim application

Failure Modes:
- expensive or flaky runtime setup if singleton/reset discipline drifts
- a rare race shows as an intermittent multithreading failure; it is pinned by a
  deterministic stand-in at the unit tier, not by rerunning this suite

Observability:
- matrix and harness failures expose multi-object regressions

Extension Points:
- new room-mode benches
- new subsystem integration lanes

Key Files (C1):
- `tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py`
- `tests/integration/melder/aether/rift/codegen_rift_json_testbench_support.py`
- `tests/integration/melder/aether/rift/static_rift_json_testbench_support.py`
- The aether tree carries 36 `test_*.py` modules beneath these; they are the
  CONTENT of this component rather than its key surfaces, and are counted here
  rather than cited so the core set stays a set an agent can verify.
- The rift tree (inside the aether tree) carries 3 `test_*.py` modules over the
  same three benches; they are counted here rather than cited.
- No harness or support module of its own; the 34 test_*.py modules in
  tests/integration/melder/conduit/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 12 test_*.py modules in
  tests/integration/melder/crystallizer/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- `tests/integration/melder/live_sim/bootstrap.py`
- `tests/integration/melder/live_sim/conftest.py`
- `tests/integration/melder/live_sim/interfaces/protocols.py`
- `tests/integration/melder/live_sim/mini_application/application.py`
- The live_sim tree carries 2 `test_*.py` modules beneath these; they are the
  CONTENT of this component rather than its key surfaces, and are counted here
  rather than cited so the core set stays a set an agent can verify.
- No harness or support module of its own; the 5 test_*.py modules in
  tests/integration/melder/multithreading/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 2 test_*.py modules in
  tests/integration/melder/mutation_research/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 47 test_*.py modules in
  tests/integration/melder/spellbook/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.

""",
}

EDITS_4: List[Tuple[str, str, int]] = [
# Mock corpus Protects
("""- support scan/bind import and duplicate/reexport cases

Inputs:
- imported by unit/component/integration tests
""",
"""- support scan/bind import and duplicate/reexport cases

Protects:
- scan-bind refusals and edge cases against modules of fixed shape (corrupt
  `scan_bind` metadata, duplicates, an empty module, lambdas, re-exports, wrapped
  callables)
- crystallizer module-graph extraction against one fixed physical package
  (`spell_crystal_demo_pkg`), which `spell_crystal_harness.py` imports under a known
  prefix so the expected targets, dependencies and kinds are stable

Inputs:
- imported by unit/component/integration tests
""", 1),
# New C3 before the C2 catalog
("""- `tests/mocks/spellbook/scan_bind_module_wrapped.py`

## C2 Subcomponents Catalog
""",
"""- `tests/mocks/spellbook/scan_bind_module_wrapped.py`

### Component: Experimentation And Profiling Trees (Local Only)
Purpose:
- Hold the experiments, probes and benches that informed design decisions, plus
  opt-in profiling scripts, outside the three tiers CI runs.

Responsibilities:
- `tests/experimentation/`: 33 `test_*.py` experiment and probe modules (cache and
  meld parity probes, lineage and SpellSpace experiments, performance
  comparisons) and bench modules; a local `pytest` collects the test modules
- supply the two synthetic-module benches that component and integration
  crystallizer tests import as stable cases (see
  `### Subcomponent: Synthetic Module Experiment Benches`)
- `tests/experiments/cprofile_testing/`: crystallizer and mutation-research
  profiling scripts; their `pytest_profile_*.py` wrappers are named to avoid
  default discovery and run only when passed explicitly

Protects:
- nothing CI enforces. The probes record measured answers to design questions; a
  probe that starts failing means the question's answer changed, which is worth
  reading but is not a regression gate

Inputs:
- the local runtime; for the profiling scripts, a size argument such as `small`

Outputs:
- pytest results locally; profiling timings and `.prof`/`.txt` files under
  `results/`, ignored by that directory's own `.gitignore`

Owned State:
- case packages the synthetic-module benches write under their own directory
  (see `## Unknowns` for the tracked copies)

Lifecycle/Cleanup:
- the benches remove their case directories in teardown with
  `shutil.rmtree(..., ignore_errors=True)`, so a removal that fails leaves the
  directory behind without a signal; a new case always gets a fresh directory name

Concurrency/Threading:
- several experiments measure thread behavior (cross-thread SpellSpace scope,
  atomic counters); none is a gate

Invariants/Guarantees:
- not in CI: the driver runs only the three tiers, and `tests/experiments/` holds
  no module matching default discovery
- 196 `.py` files in `tests/experimentation/`, 140 of them generated case packages

Failure Modes:
- a probe written for older behavior fails after a deliberate change; update or
  retire the probe rather than the runtime

Observability:
- local pytest output; profiling scripts print their timings

Extension Points:
- new probe modules; new profiling tiers in the profiling harness

Key Files (C1):
- `tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py`
- `tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py`
- `tests/experiments/cprofile_testing/profile_harness.py`
- The 33 `test_*.py` modules in tests/experimentation/ are counted here rather than
  cited; they are this component's content.

## C2 Subcomponents Catalog
""", 1),
]
