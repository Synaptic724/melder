# Research: Optional codegen / Cython executor path

Date: 2026-01-25

## Scope
Identify current execution entrypoints that would need to branch to a codegen
executor and capture known constraints.

## Evidence
- src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py:MeldRuntime.execute
- src/melder/aether/conduit/meld/meld_engine/meld_engine.py:MeldEngine.run

## Findings
- MeldRuntime.execute instantiates MeldEngine directly and delegates to
  engine.run; no alternative executor path is present in this file.
- MeldEngine.run performs the per-call graph/plan work and executes nodes
  in a loop (docstring and run flow), so any codegen executor would need to
  bypass this path.

## Unknowns
- UNKNOWN: Where the codegen executor should live to satisfy cleanup and
  module-scope constraints (new module vs existing meld_runtime/engine).
  - Why it matters: codegen storage and cleanup must not leak resources.
  - Where to investigate: src/melder/aether/conduit/meld/meld_runtime/meld_runtime.py
    and src/melder/aether/conduit/meld/meld_engine/meld_engine.py for lifecycle patterns.
  - Status: uninvestigated.

- UNKNOWN: Whether Python-level codegen is sufficient for the stated targets or
  if Cython is required for the tight execution loop.
  - Why it matters: impacts scope and dependency strategy.
  - Where to investigate: benchmarks/testing_other_di/test_melder_hotpath_profiles.py
    to define baseline profiles and measure codegen variants.
  - Status: uninvestigated.
