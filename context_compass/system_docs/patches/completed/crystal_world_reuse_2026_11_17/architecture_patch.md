# architecture_patch

## Metadata
- Patch ID: crystal_world_reuse_2026_11_17
- Status: implemented at 0.2.8305; deltas merged into src_components, src_architecture, tests_components and the
  source graph
- Owner: Mark (accountable); melder_0 (synaptic_python_developer) authors and implements
- Ticket: https://github.com/Synaptic724/melder/issues/331 (second iteration)
- Created: 2026-11-17T11:00:00Z
- Updated: 2026-11-17T11:15:23Z

## Patch Scope and Non-Goals
- Objective: a bind stops revisiting its module world. A spell whose root module's world was analysed before, and
  whose modules are unchanged in memory, receives a copy of that finished result; a loaded module's answers are
  checked against the module object and its import spec instead of its file; the walk that still runs records each
  shared leaf once and finds target membership in O(1).
- Non-goals: concurrency; caching retained user-source text; caching for custom strategies; changing what a fresh
  analysis records; any public API.

## Changed-Components Matrix
| Component | Change |
| --- | --- |
| `ModuleAnswerCache` | a loaded module's facts keyed by object and spec, not file stat; kept whole worlds |
| `CrystalAnalyzer` | reuses a world before walking; keeps a reusable world after a clean walk; dedupes leaf records |
| `CrystalAnalysisResult` | set-backed membership for its target lists; loads a described payload in one step |
| `SitePackageCustodyStrategy` | exposes its site-root signature so a world with provenance can be checked |

## Interface and Boundary Deltas
- No public signature changes. `CrystalAnalysisResult.load_described_payload` (kernel-internal) installs an exact
  copy of a `describe()` payload into a fresh result. `SitePackageCustodyStrategy.site_root_signature` replaces the
  private `_site_root_signature` of 0.2.8304.
- Contract change (owner direction 2026-11-17: repeat work works off in-memory data): a loaded module's analysis is
  current as of its module object and import spec. A reload or re-import replaces the spec or the object and is
  analysed again; a file edited on disk without a reload keeps its earlier analysis until then. A module that is not
  imported keeps the file (mtime_ns, size) and `sys.path` checks.

## Cross-Component Invariants
- A world is reused only when every module the walk touched still resolves to the same object and spec (or still to
  no object, with the same `sys.path` and, for a read file, the same stat), the root path and policy are the same,
  and any recorded provenance's site roots keep their directory times.
- A world is never kept when the walk recorded a read or parse error, touched a synthetic module, saw a module
  object change during the pass, ran with retained user sources, or rooted at a synthetic or unknown module.
- The reused result is an exact copy of the kept `describe()` payload: what a fresh analysis would record.
- Skipping a leaf record is exact: it is skipped only when the same leaf record was the last one for that name.

## Migration and Rollout Order
1. Failing-first pins: world reuse and its invalidations, reload, edit without reload, a module not imported, the
   exclusions, leaf dedupe, the payload load, the world bound.
2. Result sets and payload load; cache facts guard and worlds; analyzer reuse, collection and dedupe.
3. Pins of the 0.2.8304 stat rule for loaded modules move to the reload rule.
4. Docs, graph, release note, notch 0.2.8305, rebuild last.

## Rollback Strategy
- Revert the change set; 0.2.8304's per-module reuse remains. No record format change.

## Validation Expectations and Evidence Plan
- Unit pins beside the 0.2.8304 ones; the crystallizer, MutationResearch, aether, spellbook and conduit suites and
  the full suite with the GIL off; the probe before and after; the MelderOps configure re-measured on a wheel.

## Ticket Coverage Map
| Patch section | Ticket requirement |
| --- | --- |
| Interface and Boundary Deltas | the owner's 2026-11-17 direction; configure in seconds |
| Cross-Component Invariants | a crystal records what a fresh analysis records |

## Unknowns and Decision Requests
- none (owner direction of 2026-11-17, recorded on the ticket).

## Context / Handoff Summary
Implemented at 0.2.8305 within these boundaries. Benchmark: 600 binds over 150 modules, 1.8-2.0 s at 0.2.8304
to 1.15 s; the rest of that bind time is bind's own structural validation, outside this patch.
