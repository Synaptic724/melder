# Architecture patch: parked_versions_wired_at_conjure_2026_10_16

## Metadata
- Patch ID: parked_versions_wired_at_conjure_2026_10_16
- Status: promoted at landing (0.2.8248) and archived; written before any `src/` edit (2026-10-16)
- Owner: user (ruled in chat, 2026-10-16); melder_0 (synaptic_python_developer) (patch)
- Ticket: STORY-2026-10-16-parked_versions_wired_at_conjure (story 8 of EPIC-2026-10-14-managed_spell_quantity)
- Created: 2026-10-16T09:42:16Z
- Updated: 2026-10-16T11:41:08Z

## Objective
A version staged with `bind_inactive` before `conjure` must meld after a notch exactly as a version staged after
conjure does (owner: "bind_inactive should behave the same before and after conjure"). Today conjure wires - stamps
the owner onto - only the Book's active versions (`SpellbookCreationSystem.define_conduit_into_spells` walks
`_spells`), and a notch wires nothing, so a version parked before conjure has no CreationContextFactory, no owner
store and, if managed, no pool: after a notch its first meld raises RuntimeError "Spell has no configured
CreationContextFactory." for unique, unique_per_conduit, many and managed_spell_quantity alike (probe Q1 on
0.2.8246), while the same version staged after conjure melds. `bind_inactive`'s own comment already says
pre-conjure parked spells "are wired at conjure like pre-conjure active spells". Conjure will stamp every parked
version with the same stamp a post-conjure `bind_inactive` applies.

With it the creation cache moves to generation 21 (owner: "you can bump the cache because codegen also requires that
you properly modify it"), retiring bundles written before the managed lease codegen of 0.2.8245.

## Non-goals
- No change to how an active version is wired at conjure, to a post-conjure `bind` or `bind_inactive`, to a notch,
  to an ownership transfer, or to restore and graft - both loaders stage members after conjure through
  `conduit.bind_inactive`, so they take the wired path already.
- No store registration for a parked existing object: it is not live until a notch promotes it, and no disposal is
  lost, because an existing-object spell carries no disposal methods (Bind resolves disposal names only for a class
  binding profile; probe `probe_s8_existing_object_teardown.py`).
- No change to records, spell ids or any emitted plan; no change to `ManagedSpellLease` (the owner kept it as built;
  the story only checks that it works) or to the review items the owner kept as built.

## Changed components
| component | change |
| --- | --- |
| SpellbookCreationSystem (`define_conduit_into_spells`) | after the active loop and under the same Book lock, stamp every version in `_inactive_spells` with the active loop's `_add_owned_conduit` arguments; a failure is logged per version and the loop goes on, as for active versions |
| CachingSystem | `CACHE_VERSION_HISTORY[21] = "managed_spell_lease_codegen"`, so `CURRENT_VERSION` is 21 |
| SitePlanRuntimeHelpers (`raise_missing_managed_pool`) | the missing-pool message drops the pre-conjure staging cause and its "stage the version after conjure" remedy, which no longer apply |
| Spellbook (`bind_inactive`), TransferOfOwnership (`_migrate_inactive_members`) | comments and the docstring only: a version staged before conjure is wired at conjure |

No code-description patch: the change is one loop under a lock conjure already holds, with the active loop's
per-version failure policy; no new control flow, error semantics, rollback or concurrency rule.

## Invariants
1. After conjure every version the Book owns, active or parked, carries the owner stamp: the root's id, name and
   store, its dynamic flag and gate controller, and the Book's caching posture; a managed version has its pool in
   the root's store, registered with `ReleaseManagedSpell`. A parked version gets that stamp and nothing else - no
   store registration of an existing object, no `resolution_required` write, no risk-manager, index or Nexus
   registration - which is exactly what a post-conjure `bind_inactive` does.
2. The active loop runs first and is unchanged; active versions are wired and their existing objects registered as
   before.
3. A parked version stays off resolution until its notch: the stamp resets its context and configures its factory,
   builds nothing and selects nothing, and a meld of its id raises the same KeyError ("No spell found with
   spell_id") as for a version staged after conjure.
4. Locks: Book lock -> spell lock (`_add_owned_conduit`) -> store leaf lock (`ensure_managed_quantity`) -> registry
   leaf lock (registered after the store lock), the active loop's order; no new lock and no new edge.
5. Records, spell ids and every emitted plan are unchanged; conjure pays one stamp per parked version (cold path).
6. Cache admission is unchanged: a bundle is admitted only at the current generation, so every generation-20 bundle is
   cold once after the upgrade and rebuilt at 21.

## Interface deltas
- Public: none; the missing-pool MeldExecutionError text changes (its first clause stays).
- Internal: `CachingSystem.CACHE_VERSION_HISTORY` gains 21 and `CURRENT_VERSION` becomes 21.
- Persisted: creation-cache bundles are written at generation 21; Crystallizer records are untouched.

## Migration order
This patch -> the mapping note -> red tests (unit: the parked stamp; integration: each family staged before conjure
melds after a notch like one staged after it; the cache-schema expectation; the two message tests) -> the loop ->
generation 21 -> the message and the comments -> green with the GIL off and on -> probe Q1 without its probe-only
patch -> the `ManagedSpellLease` check -> system docs, graph, release note, notch -> closure -> rebuild.

## Rollback
Revert the notch's files: conjure stamps active versions only again (a version staged before conjure fails after a
notch, as on 0.2.8247), and the cache returns to generation 20 (generation-21 bundles are then cold, since admission
requires the exact generation). Nothing recorded changes.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | unit: every parked version stamped with the active loop's arguments, a parked existing object stamped but not registered, a parked version's resolution flag untouched, a raising parked stamp logged and the rest wired; integration: unique, unique_per_conduit, many, managed_spell_quantity, an existing object and a function staged before conjure meld after a notch as when staged after it; the managed parked version has its pool and registry entry right after conjure |
| 2 | the existing `define_conduit_into_spells` unit and component tests, unchanged and green |
| 3 | integration: before its notch a version staged before conjure is not meldable by id, as when staged after it |
| 4 | review of the touched lock sites; the direct-spell-cleanup lock-order component tests green |
| 5 | no plan or bind code is touched; the spellbook, conduit and crystallizer suites green in both GIL modes |
| 6 | integration: the cache-schema test (21 admitted, 1-20 cold) |

## Risks
- A Book with many parked versions pays one stamp each at conjure: a context reset and a factory configuration per
  version, and a pool for each managed one. Conjure is a cold path; the stamp is the one a post-conjure
  `bind_inactive` pays per staged version.
- A parked managed version's pool is registered from conjure on, as it is today from a post-conjure `bind_inactive`:
  a release by class with two versions of one class in one index goes to the selected version's pool (the cold
  resolver's existing rule).

## Ticket coverage
- Story: STORY-2026-10-16-parked_versions_wired_at_conjure (epic EPIC-2026-10-14-managed_spell_quantity, story 8).

## Unknowns and decision requests
- None: U12 is settled (the story's FACT and MEASURE notes of 2026-10-16).

## Context / Handoff Summary
- What changed: built as written and landed as 0.2.8248 - the parked loop in `define_conduit_into_spells`,
  generation 21, the missing-pool message and the comments; red then green in both GIL modes, the whole tree
  green; promoted into src_architecture, src_components, the tests docs and the graph, then archived.
- What remains: nothing in this lane; the owner accepts the story with the epic.
- Next entrypoint: none (archived).
