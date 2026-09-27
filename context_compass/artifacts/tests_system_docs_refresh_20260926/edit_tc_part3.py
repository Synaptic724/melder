from typing import Dict

# Whole-section bodies, keyed by the heading they follow; each runs to the next heading.
SECTIONS_3: Dict[str, str] = {
"### Component: Unit Test Suite\n": """Purpose:
- Validate isolated contracts for runtime classes, descriptors, ACL surfaces,
  spellbook internals, utilities, the package-root surface and build assets; in
  three separate trees, the repository tooling that qualifies and ships the package.

Responsibilities:
- Cover `melder/aether`, `melder/crystallizer`, `melder/mutation_research`,
  `melder/spellbook`, `melder/utilities` and `melder/build_assets`, plus nine
  package-root modules directly under tests/unit/melder/.
- Cover repository tooling that is not `melder`: the CI scripts under `.github/scripts/`
  (`github_workflows`), the LLM support bundle builder (`llm_support`) and the
  architecture-docs tool (`architecture_and_design`).
- Exercise direct API and lifecycle/error-path behavior.
- Reset singleton runtime surfaces around runtime-heavy files, and boot a fresh
  `Aether()` after each reset.

Protects:
- per-class contracts - returns, raises and cleanup - so a regression fails beside
  the class that caused it rather than inside a stack test
- the package-root contract: every `__all__` name resolves to its concrete-path
  object, internal classes stay unbindable, the version and build-asset stamps
  agree (see `### Subcomponent: Package Root Unit Cluster`)
- the release gates in the CI scripts: fail-closed routing, candidate and source
  identity, distribution contents, the free-threaded runtime gate (see
  `### Subcomponent: Repository Tooling Unit Cluster`)
- race fixes, as deterministic stand-ins for the concurrent writer (see
  `### Flow: Concurrent-Writer Stand-In`)

Inputs:
- local runtime classes and helper fixtures; `MagicMock` collaborators where the
  unit is one class (the conduit conftest stubs the Spellbook, Aether, DevOps
  manager, conduit cloud and frame around real `Conduit` objects)
- CI scripts loaded by file path through `tests/unit/github_workflows/conftest.py`,
  without booting Melder

Outputs:
- direct contract assertions with minimal external wiring

Owned State:
- test-local fixtures only, except twelve `CachingSystem` tests that write cwd-relative
  tests/unit/melder/utilities/_caching_system_tmp_* directories which survive runs
  (TREE ARTIFACTS in `tests_architecture`)

Lifecycle/Cleanup:
- runtime-heavy files use autouse fixtures that reset `AetherUtilitySystem`, `Nexus`
  and `Aether`, then boot `Aether()` and bind it to `Spellbook._aether`, both before
  and after each test (`tests/unit/melder/aether/conduit/conftest.py:65-85`); a reset
  alone boots nothing (see `### Flow: Runtime-Heavy Singleton Reset`)

Concurrency/Threading:
- direct coverage of the synchronization primitives (creation gate and controller,
  load gate, phase scheduler, latches, switches, weak concurrent containers);
  `test_abstract_elastic_pool_multithreaded.py` runs threads against the pool; a
  race in larger code is pinned by a stand-in, not by threads

Invariants/Guarantees:
- unit tests stay close to class/method behavior
- the densest tier: 461 `test_*.py` modules among 464 `.py` files
- CI-script tests never import `melder`; each script is loaded as a standalone module

Failure Modes:
- singleton leakage, or a SINGLETON VOID (a reset without a re-boot), makes a test
  pass alone and fail after another file
- stale cwd-relative cache directories survive between runs

Observability:
- direct pytest failures on contract mismatch

Extension Points:
- new subsystem-level direct contract tests; a new CI script gets a loader fixture
  in the github_workflows conftest

Key Files (C1):
- `tests/unit/melder/aether/conduit/conftest.py`
- The aether tree carries 183 `test_*.py` modules beneath these; they are the
  CONTENT of this component rather than its key surfaces, and are counted here
  rather than cited so the core set stays a set an agent can verify.
- No harness or support module of its own; the 45 test_*.py modules in
  tests/unit/melder/crystallizer/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 20 test_*.py modules in
  tests/unit/melder/mutation_research/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- `tests/unit/melder/spellbook/spell_compiler/support/compiler_test_support.py`
- The spellbook tree carries 140 `test_*.py` modules beneath these; they are the
  CONTENT of this component rather than its key surfaces, and are counted here
  rather than cited so the core set stays a set an agent can verify.
- No harness or support module of its own; the 51 test_*.py modules in
  tests/unit/melder/utilities/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- The 3 test_*.py modules in tests/unit/melder/build_assets/ and the 9 package-root
  modules directly under tests/unit/melder/ are cited in their C2 clusters.
- `tests/unit/github_workflows/conftest.py`
- The repository-tooling trees carry 10 `test_*.py` modules (github_workflows 8,
  llm_support 1, architecture_and_design 1), cited in their C2 cluster.

""",
"### Component: Component Test Suite\n": """Purpose:
- Exercise small, real slices of the system where unit tests are too narrow
  and full integration would be too expensive.

Responsibilities:
- use real core objects
- stub or mock external collaborators where needed
- validate internal contracts that span multiple objects

Protects:
- seams inside one subsystem, with real objects: descriptor/ACL publication and
  cleanup, crystallizer graph extraction over real module graphs, the
  mutation-research root on a real Aether, bind/configuration/contract/cache
  behavior of a real Spellbook, compiler phases through real conjures (key-set
  plans, cache restage, spell ids across two interpreters), creation-gate drains
  and load-gate/scheduler composition
- the agent text reader against the real packaged documents rather than generated
  fixtures (`test_agent_text_reader_component.py`)

Inputs:
- small real runtime slices
- controlled fake/stub collaborators

Outputs:
- slice-level behavioral assertions

Owned State:
- test-local slices and stubs; component cache tests write under the package
  directory (TREE ARTIFACTS in `tests_architecture`)

Lifecycle/Cleanup:
- follows the same singleton reset-and-re-boot discipline when runtime objects are
  involved

Concurrency/Threading:
- no parallel harness layer of its own; the synchronization component files start
  threads to prove that a gate drain waits for tickets in flight
  (`tests/component/melder/utilities/synchronization/test_creation_gate_component.py`)

Invariants/Guarantees:
- tier intent is explicitly documented in `tests/component/INFO.MD`: real core
  objects, stubbed external boundaries, deterministic, contract-level assertions
- 141 `test_*.py` modules among 143 `.py` files

Failure Modes:
- component tests drift into unit-style internals or full integration sprawl

Observability:
- visible through component-slice regressions

Extension Points:
- new slice tests for cross-object seams

Key Files (C1):
- `tests/component/INFO.MD`
- No harness or support module of its own; the 58 test_*.py modules in
  tests/component/melder/aether/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 7 test_*.py modules in
  tests/component/melder/crystallizer/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- No harness or support module of its own; the 1 test_*.py modules in
  tests/component/melder/mutation_research/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.
- `tests/component/melder/spellbook/compiler_test_helpers.py`
- `tests/component/melder/spellbook/spell_compiler_runtime_test_support.py`
- The spellbook tree carries 71 `test_*.py` modules beneath these; they are the
  CONTENT of this component rather than its key surfaces, and are counted here
  rather than cited so the core set stays a set an agent can verify.
- No harness or support module of its own; the 4 test_*.py modules in
  tests/component/melder/utilities/ depend only on the shared surfaces at tests/ and the scoped
  conftests named in `tests_architecture.md`. Paths in this bullet are written
  WITHOUT backticks because they are directories - descriptive, never citations.

""",
}
