# component_patch_crystal_analysis

## Metadata
- Patch ID: crystal_analysis_reuse_2026_11_17
- Component: crystal_analysis (`CrystalAnalyzer`, new `ModuleAnswerCache`, `SitePackageCustodyStrategy`)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Status: implemented at 0.2.8304; merged into the canonical system docs
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-17T10:20:00Z
- Updated: 2026-11-17T10:38:24Z

## Component Purpose and Boundary
The crystal-analysis subsystem classifies and walks a spell module's world at bind time. This patch adds one
process-wide cache of module answers beside the two existing ones (the analyzer's syntax-fact memo and
`PhysicalSourceCache`) and routes the analyzer's repeated questions through it.

## Before/After Behavior Summary
- Before: each analysis resolved every module's path (`Path.resolve`), matched its custody (more resolves and
  `Path.is_relative_to` root walks), replayed its import facts with a `find_spec` probe per `from x import name`
  member, and each crystal resolved the user, site and environment roots; a site-package root called
  `importlib.metadata.packages_distributions()` (154 ms after the first call). Only one analysis shared answers.
- After: the first analysis to meet a module computes those answers and keeps them; later analyses reuse them while
  the module object and its file are unchanged. A second analysis of an unchanged world resolves no module path,
  matches no custody, probes nothing and records the same result.

## Interface Deltas
- New `crystal_analysis/module_answer_cache.py`: `ModuleAnswerCache`, class-hosted like `PhysicalSourceCache`, with
  lookup/store pairs for module paths, custody kinds, module facts, resolved roots, distribution maps and
  provenance payloads; `_clear_for_tests` and `_stats_for_tests`.
- `CrystalAnalyzer`: `resolve_module_path` and the three root resolvers consult the cache; an analyzer built with
  the default custody chain and default fact strategies keys custody kinds by its roots and reuses facts; one with
  either supplied asks the cache for paths and roots only.
- `SitePackageCustodyStrategy.harvest_provenance` reads the distribution map and payload from the cache.

## State and Lifecycle Deltas
- New class-level maps, each LRU-bounded (8192 entries), under one RLock; no instance state, nothing to clean up
  per analyzer. Weak references let a module be collected; a dead reference is a miss.
- The per-pass dictionaries of #327 stay and front the cache within one analysis.

## Failure Mode Deltas
- A module object that cannot be weakly referenced, a relative `__file__`, a file that cannot be stat'ed, a read
  error or a parse error: the answer is computed and not kept (unchanged results, no reuse).
- Accepted residuals: see the architecture patch.

## Dependency and Ordering Constraints
- The facts guard's stat is taken before the file is read, so a write landing mid-read leaves a guard that misses
  on the next analysis rather than one that keeps stale facts.
- Path and custody answers are looked up before facts; facts depend on the path answer's text.

## Validation Expectations
- Reuse: a second analysis calls no uncached path resolution, no custody `matches` and no `find_spec`.
- Invalidation: an edited file (new mtime and size) or a re-imported module is derived again.
- Equality: describe() of a reused analysis equals a fresh one's, including the leaves and fingerprints.
- Synthetic modules, custom strategies, weak references, LRU eviction, provenance reuse and its site-root guard,
  roots per cwd, and threaded analyses with the GIL off.

## Unknowns and Open Decisions
- none

## Context / Handoff Summary
Implemented at 0.2.8304; the `sys.path` guard for a module with no object was added during validation.
