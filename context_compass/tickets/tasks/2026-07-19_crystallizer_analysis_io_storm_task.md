# Task: Crystallizer analysis IO storm - integration tests pay whole-world file reads per bind/load (strategy)

## Metadata
- Task ID: TASK-2026-07-19-crystallizer-analysis-io-storm
- Status: in_progress
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-19T11:05:00Z
- Updated: 2026-07-19T11:05:00Z

## Problem / Opportunity
Owner report: every crystallizer integration test takes SECONDS. Root cause is bind-time
and load-time module-world analysis doing unmemoized file IO over the entire repo per
bind and per restore.

## Ticket Contract
- ENTRY_GATE: owner question 2026-07-19 ("why do all my crystallizer integration tests go
  so slow").
- EXECUTION_BOUNDARY: STRATEGY in this task - investigation notes + owner decision
  capture. Implementation gets its own lane (analysis cache is concurrency-adjacent;
  site-package descent is record-shape sensitive).
- DEPENDENCIES: none.
- EXIT_GATE: owner picks fix option(s); implementation lane opened or deferred.
- FAILURE_ESCALATION: DECISION_REQUEST rows; no code edits from this task.

## Noting Behavior
- Task notes: tactical findings, immediate impacts, one-step continuation.

## Notes
- DATETIME: 2026-07-19T11:05:00Z
  TYPE: FACT
  CLAIM: The seconds-per-test cost is O(transitive import world) file IO at EVERY bind and
    EVERY load. Chain: (1) with_defaults() sets user_source_root_paths=(cwd,), so under
    the repo every module - all 551 src/melder/**.py files AND tests/** - classifies
    user_source: descends AND makes a sha256 fingerprint claim. (2) Every dynamic-lane
    bind emits custody (spellbook.py:4522,4843 -> create_spell_crystal) and the analyzer
    walks the FULL transitive import graph from the spell's root module; for spells
    defined in the integration test file that root is the ~3000-line test module whose
    imports pull in the whole melder runtime - and pytest: SitePackageCustodyStrategy
    descends=True, so pluggy/_pytest walk too (source read + parsed, no fingerprint).
    (3) Per walked module per bind: resolve_source READS the file from disk on every call
    (documented contract), sha256 for the memo digest, sha256 again for the user_source
    fingerprint; the class-level syntax memo skips ONLY ast.parse on repeat digests - the
    IO and hashing repeat for every bind. (4) Every restore/formation load:
    SourceDriftStrategy re-reads + re-hashes EVERY recorded physical_module_fingerprints
    entry, retention-agnostic, deduped only per (module,path) pair - the recorded world IS
    the whole repo walk, so hundreds of reads per load. A test binding 3 spells and
    restoring twice pays roughly 3x~600 + 2x~500 = ~2800 file reads + SHA256s (plus
    full-world AST parses on the session's first bind) - seconds on NTFS. Thread
    spawn/join per book pool and singleton reset cascades are milliseconds by comparison.
    This is also a REAL production surface: user binds pay O(import world) reads per bind,
    loads pay O(recorded world) reads per restore.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:598-629
  - src/melder/aether/spellbook/spellbook.py:4522-4523
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:678-800
  - src/melder/crystallizer/crystal_analysis/crystal_analyzer.py:840-940
  - src/melder/crystallizer/crystal_analysis/custody/site_package_custody_strategy.py:85-93
  - src/melder/crystallizer/crystal_analysis/custody/user_source_custody_strategy.py:160-186
  - src/melder/crystallizer/crystal_analysis/preflight/source_drift_strategy.py:63-101
  IMPACT: Every integration test (and every real-world bind/load) pays whole-world disk
    reads + hashes; the syntax memo hides only the parse cost.
  NEXT: Owner ruling on the strategy options (stat-guarded content cache; site-package
    descent policy; drift-preflight stat-guard) - then open the implementation lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T11:37:30Z
  TYPE: DECISION
  CLAIM: Owner ruling captured ("best outcomes... investigate then send it"): implement
    A (stat-guarded content cache) + C (drift surfaces ride it) + B as a policy knob with
    the perf-correct default (site_package_dependency_descent=False; provenance still
    captures; one-line reversal). Implementation landed in
    STORY-2026-07-19-crystallizer-analysis-io-cache behind patch lane
    crystallizer_analysis_io_cache_2026_07_19. This strategy task's exit gate is met.
  EVIDENCE:
  - context_compass/tickets/stories/2026-07-19_crystallizer_analysis_io_cache_story.md:1-1
  IMPACT: Strategy lane closes into the implementation story; ruling durable.
  NEXT: Close this task at the owner's acceptance walkthrough alongside the story.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Strategy-only lane: the analysis IO storm is evidenced; fix options await the owner
ruling (A: stat-guarded content-fingerprint cache in the analyzer; B: site-package
descent policy ruling - record-shape sensitive; C: reuse the cache in SourceDriftStrategy).
