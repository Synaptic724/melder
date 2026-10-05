# architecture_patch

## Metadata
- Patch ID: many_registration_trim_2026_10_01
- Status: active
- Owner: user (agent fable_0)
- Created: 2026-10-01T01:08:13Z
- Updated: 2026-10-01T01:08:13Z

## Patch Scope and Non-Goals
- Objective: a disposal-bearing `many` creation registers into its scope store with one list append; the
  spell's disposal method list is recorded once per key instead of once per entry; every reader of the many
  disposal metadata (disposal walk, purge, extract/restore) reads the new shape; the three emitters that write
  the registration line emit the new positional verb; the creation-cache generation retires executors emitted
  with the old line. Measured standalone: 204-207 ns -> 104-111 ns per registration (VM, 3.14t, GIL off);
  -11..-49% of a disposal-bearing many plan in the certification harness.
- Non-goals: no change to WHAT is disposed, in which order (newest-first, declared method order) or how
  failures are reported (one RuntimeError per failing method, chained, in one ExceptionGroup); no change to
  unique/per-conduit/per-space registration, to `Existence` routing, to the doors, or to the public
  `add_many_creations` signature; no lock-free append (trimmed B) - the store lock stays a leaf around the
  append so a build finishing after `cleanup()` is still refused and disposed.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Creations and SpellSpace (`creations.py`) | modify | one record per many key: the live bucket aliased plus the key's method list; new hot verb `register_many`; all readers migrate | none |
| SpellCompiler and Validation Pipeline (site-plan lowering, solo templates, specializer emitter) | modify | emit `register_many(sid, v, dm)` instead of the keyword call | Creations verb |
| Creation cache (`caching_system.py`) | modify | generation 16 retires executors emitted with the old line | emitters |

## Interface and Boundary Deltas
- Boundary delta 1: none between components - the store still owns registration, disposal order and refusal;
  the emitters still decide which steps register (only disposal-bearing `many` steps do).
- Interface delta 1: `Creations.register_many(key, item, disposal_methods)` (internal, positional) is added;
  `add_many_creations` keeps its signature and semantics and writes the same shape.
- Interface delta 2: the many disposal metadata shape changes from `spell_id -> list[(object, methods)]` to
  `spell_id -> ManyDisposalBucket(entries=<the live list object>, methods)`; `extract_spell_creations` rows
  (`scope`, `disposable`, `stored`, `disposal_methods`) are unchanged, so `transfer_of_ownership.py` and
  `conduit_ward.py` do not change.

## Cross-Component Invariants
- Invariant 1: every object in a disposal-bearing many bucket is disposed exactly once, newest-first, with the
  key's method list in declared order, by cleanup, clear_all and whole-target purge; single-object purge
  disposes that object with the same list.
- Invariant 2: a many key's entries all share one disposal declaration (the Spell's); the record is created on
  the key's first disposal-bearing registration and lives as long as the bucket; an empty bucket after a single
  purge removes both.
- Invariant 3: the store lock remains a leaf: taken only around dict/list work, never while taking another
  lock or running user code; a build that publishes after `cleanup()` is refused and its object disposed.
- Invariant 4: executors that still call `add_many_creations` stay correct; generation 16 only retires them.

## Migration and Rollout Order
1. Store: the record type, `register_many`, the rewritten `_append_many_locked`, the readers (disposal walk,
   purge paths, extract/restore), docstrings.
2. Emitters: `SitePlanEmission._emit_many`, the two solo executor templates, the specializer's
   `_emit_registration` many branch.
3. Generation 16 in `CachingSystem.CACHE_VERSION_HISTORY`.
4. Tests (unit store, emitter text, component through real conjures, the regression files that read the old
   shape), suites sharded on the VM copy, harness re-run.
5. Landing: notch above 0.2.8215, release note, src_components/src_architecture, graph descriptors, assets last.

## Rollback Strategy
- Rollback trigger: a disposal-order or error-shape difference in the differential tests, or a suite failure
  that traces to the shape.
- Rollback steps: revert the store and the three emitters together; leave generation 16 (a bump is one-way;
  reverting it would re-admit bundles emitted with the new line against the old store).
- Post-rollback verification: the creations unit suite and the ordered-disposal integration tests.

## Validation Expectations and Evidence Plan
- Validation item 1: unit tests on `register_many` and every reader (order, methods, failures, refusal,
  single purge, extract/restore round trip, mixed-declaration refusal).
- Validation item 2: the existing regression files (reverse order, all methods, failure aggregation, first-use
  atomicity) pass unchanged in behaviour; where they read `_disposable_creations` they read the new shape.
- Validation item 3: emitter tests assert the new line; a component test melds a disposal-bearing many root
  through a conduit and a SpellSpace and checks disposal order at scope exit.
- Validation item 4: harness re-run and `commandops_shape_probe.py` before/after (VM); owner-run gauntlet.
- Evidence source 1: artifacts/many_registration_trim_20261001/ (logs, apply scripts, runs).

## Ticket Coverage Map
- Epic: tickets/epics/2026-10-01_static_codegen_and_door_strategies_epic.md
- Story: tickets/stories/2026-09-27_many_registration_trim_story.md
- Tasks: tickets/tasks/2026-10-01_implement_many_registration_trim_task.md

## Unknowns and Decision Requests
- UNKNOWN: none blocking; whether the solo-family many roots in the owner's applications are disposal-bearing
  (decides how much the solo template change buys there).
- DECISION_REQUEST: A1 (`with self._lock:` style) vs A3 (explicit acquire/release, 5-10 ns faster) for the hot
  verb; the no-type-check precondition on the hot verb (the public verb keeps its check).

## Context / Handoff Summary
- What changed: nothing yet; this patch defines the edit.
- What remains: the owner's confirmation of the exact edit, then steps 1-5.
- Next entrypoint: tickets/tasks/2026-10-01_implement_many_registration_trim_task.md (latest note's NEXT).
