# architecture_patch

## Metadata
- Patch ID: crystal_analysis_reuse_2026_11_17
- Status: implemented at 0.2.8304; deltas merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Created: 2026-11-17T10:20:00Z
- Updated: 2026-11-17T10:38:24Z

## Patch Scope and Non-Goals
- Objective: with the Crystallizer recording, a bind's module-world analysis reuses what earlier analyses derived
  about the same modules - path, custody kind, import facts, the policy roots, site-package provenance - while
  the module object and its file are unchanged, so configure binding many spells takes seconds.
- Non-goals: analysing spells concurrently or after bind returns; caching `retain_user_sources` text; caching for
  custom custody or fact strategies; changing what a crystal records when nothing changed; any public API.

## Changed-Components Matrix
| Component | Change |
| --- | --- |
| `crystal_analysis` (new `ModuleAnswerCache`) | process-wide, value-only, guarded, LRU-bounded answers about modules |
| `CrystalAnalyzer` | path, custody, facts and root resolution consult the cache before computing |
| `SitePackageCustodyStrategy` | distribution provenance comes from the cache, guarded by the site roots' mtimes |
| `SpellCrystal` | unchanged code; its root resolution goes through the cached statics |

## Interface and Boundary Deltas
- No signature changes. `CrystalAnalyzer.resolve_module_path`, `resolve_user_root_paths`,
  `resolve_site_package_root_paths` and `resolve_environment_root_paths` keep their contracts and add reuse.
- `CrystalAnalyzer` contract: an analysis was "current on every analysis"; it is now current as of each module
  object and its file's (mtime_ns, size). Within one analysis the per-pass answers of #327 still apply.
- New kernel class `ModuleAnswerCache` (MELDER KERNEL - guarded); the internal-bind guard manifest gains it.

## Cross-Component Invariants
- A path answer is reused only for the same module name, the same module object (held by weak reference) and the
  same `__file__` text, or - with no module object, where the answer came from `find_spec` - the same
  `sys.path`; only absolute files and `find_spec` origins are kept.
- A custody kind is reused only for the same resolved path text under the same user, environment and site roots;
  synthetic modules are matched live and never kept.
- Facts are reused only for the same module name, module object, resolved path and file (mtime_ns, size), taken
  before the file is read; reads that recorded a walk error are never kept.
- Entries hold strings, ints, tuples and weak references: never a module, source text, AST, crystal, result or
  strategy. A crystal built from reused answers records exactly what a fresh analysis records.

## Migration and Rollout Order
1. Failing-first pins (reuse, invalidation, synthetic, custom strategies, provenance, roots, weak references,
   equality with a fresh analysis, threads).
2. `ModuleAnswerCache`; the analyzer, root and provenance call sites; docstrings.
3. Tests that pinned "a later pass asks again" move to the new rule; caches reset where tests rewrite modules.
4. System docs, graph, release note, notch 0.2.8304, rebuild last.

## Rollback Strategy
- Revert the change set: the call sites fall back to computing every answer, as in 0.2.8303. No record format
  changes, so nothing written under 0.2.8304 needs migrating.

## Validation Expectations and Evidence Plan
- Unit pins under `tests/unit/melder/crystallizer/crystal_analysis/`; the crystallizer unit, component and
  integration suites and the codegen and MutationResearch suites that record crystals, the GIL off.
- The benchmark probe before (0.2.8303, recorded) and after, on the same parameters; the MelderOps configure
  re-measured on a wheel from the commit.

## Ticket Coverage Map
| Patch section | Ticket requirement |
| --- | --- |
| Interface and Boundary Deltas | functional requirements 1-5 |
| Cross-Component Invariants | functional requirement 6, non-functional requirements |
| Validation Expectations | acceptance criteria |

## Unknowns and Decision Requests
- none (the owner decided on 2026-11-17: reuse the analysis across binds, cached like the other caches).

## Accepted Residuals
- A member submodule file created later, a re-pointed symlink or junction, a package installed without touching a
  site root directory, or an edit keeping mtime_ns and size is not seen until the module or its file changes -
  the stat bet `PhysicalSourceCache` already makes.

## Context / Handoff Summary
Implemented at 0.2.8304 within these boundaries, plus the `sys.path` guard for modules not imported, found
when a pass-dedup pin reused another test's path. Benchmark: 600 binds over 150 modules, 14.2 s to 1.8-2.0 s.
