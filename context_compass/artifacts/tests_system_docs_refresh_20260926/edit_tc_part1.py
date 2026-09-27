from typing import List, Tuple

EDITS_1: List[Tuple[str, str, int]] = [
# E1 Scope
("""This document defines C3 components, C2 subcomponents, and C1 code references
for tests under `tests/`. It complements
`tests_architecture.md` by describing the actual
test components and the shared support layers they use.
""",
"""This document defines C3 components, C2 subcomponents, and C1 code references
for tests under `tests/`. It complements `tests_architecture`, which owns the
layer boundaries, by describing the test components inside them, the shared
support layers they use, and the behaviour each surface protects.

Covered: the three pytest tiers CI runs (`unit`, `component`, `integration`); the
repository-tooling trees under `tests/unit/` that test the CI scripts and support
tools rather than `melder`; the locally collected experimentation tree and the
opt-in profiling scripts; the mock corpus; and the CI driver that runs the tiers.
""", 1),
# E2 Indexing commands -> prose
("""This document is AUTHORED. Its only generated companion is
`tests_components_index.md`, rebuilt in the SAME pass as any edit:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_components.md
```

The navigable unit is the H3 `### Component: <Name>` entry.
`## C3 Components Catalog` is a CONTAINER - it indexes as a range spanning every
component beneath it, so select a component, never the catalog.

Consume by slicing, and verify before trusting a range:

```bash
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_components.md --slice "<section name>"
python tools/system_documents/index_document.py \\
    --doc system_docs/tests_components.md --check
```
""",
"""This document is AUTHORED. Its only generated companion is its index
(`tests_components_index`), rebuilt in the SAME pass as any edit by the
documentation tooling that maintains these documents. The commands live with that
tooling, not here: this document ships with the code and the tooling does not.

The navigable unit is the H3 `### Component: <Name>` entry.
`## C3 Components Catalog` is a CONTAINER - it indexes as a range spanning every
component beneath it, so select a component, never the catalog.

Consume it by slicing a named section rather than reading it whole, and verify the
index proof (line count, line ending, content hash) before trusting a range.
""", 1),
# E3 Unknowns
("""- UNKNOWN: external CI ownership of suite partitioning/sharding is still not
  documented here.
  Why it matters: test components may be executed in smaller CI groups than
  the local tree implies.
  Local evidence boundary: this checkout has no in-repo `.github/` workflow
  config, so there is no local CI topology to cite here.
  Where to investigate: external CI configuration outside this checkout.
  Current status: blocked on external evidence.
""",
"""- RESOLVED 2026-09-26 (was UNKNOWN: external CI ownership of suite
  partitioning/sharding, blocked while the checkout had no in-repo `.github/`
  workflow config). CI is in the repository and does not shard: each OS/Python
  cell runs `tests/unit`, `tests/component` and `tests/integration` in one pytest
  process through `.github/scripts/run_runtime_tests.py`. See
  `### Component: Pytest Runner And Path Bootstrap`.
- UNKNOWN: which Python minors a given CI run tested.
  Why it matters: the matrix is discovered per run (every stable free-threaded
  minor at or above the `requires-python` floor, on three runners), so the tree
  records no version list and "passes in CI" names no interpreter.
  Where to investigate: the `runtime-python-matrix-*` artifact of that run.
  Current status: by design; recorded per run, not in the tree.
- UNKNOWN: whether six tracked `bundle.json` files under
  tests/unit/melder/utilities/_caching_system_tmp_load_*/ are fixtures or leftovers.
  Why it matters: no test references those directories, so they are dead
  fixtures or committed droppings of the cwd-relative cache tests.
  Where to investigate: `tests/unit/melder/utilities/test_caching_system.py` history.
  Current status: raised to the owner; not changed.
- UNKNOWN: whether the 140 tracked `.py` files under
  tests/experimentation/_physical_to_synth_swap_tmp/ and
  tests/experimentation/_synthetic_edge_tmp/ should be in the repository.
  Why it matters: they are case packages the two synthetic-module benches write
  (50 of the tree's 57 `__init__.py` files). The benches create a fresh suffixed or
  uuid-named directory per case, so no run reads the tracked copies back; they only
  inflate the tree and its file counts.
  EVIDENCE:
  - tests/experimentation/physical_to_synthetic_module_swap_semantics_testbench.py:109-123
  - tests/experimentation/unittest_synthetic_module_edge_cases_testbench.py:62-65
  Where to investigate: the two benches' teardown and the commits that added the
  directories.
  Current status: raised to the owner; not changed.
""", 1),
# E4 Table of Contents
("""- Documentation Quality Standard
- DO NOT ASSUME / Unknowns Gate
""",
"""- Documentation Quality Standard
- Indexing
- DO NOT ASSUME / Unknowns Gate
""", 1),
("- C1 Code Map (Key Paths)\n- Diagrams\n", "- C1 Code Map (Core)\n- Diagrams\n", 1),
# E5 Component template gains Protects
("""Each component entry includes:
- Purpose
- Responsibilities
""",
"""Each component entry includes:
- Purpose
- Responsibilities
- Protects (added 2026-09-26: the behaviour a regression in this surface breaks,
  so an entry cannot describe a harness without naming what it guards; C2
  clusters carry the same line)
""", 1),
]
