# Architecture patch: managed_spell_quantity_2026_10_15

## Metadata
- Patch ID: managed_spell_quantity_2026_10_15
- Status: active; written before any `src/` edit of the lane (2026-10-15)
- Owner: user (design rulings 2026-10-12 to 2026-10-15); melder_0 (synaptic_python_developer) (patch)
- Tickets: EPIC-2026-10-14-managed_spell_quantity and its stories S1-S7 (the epic's Stories section)
- Build contract: the epic's Build Specification B1-B13 (tickets/epics/2026-10-14_managed_spell_quantity_epic.md)

## Objective
Add a seventh Existence member, `managed_spell_quantity`, whose objects are leased instead of cached: a meld or an
injection takes an idle object from the spell's pool or builds one, and the holder gives it back explicitly through
`ReleaseManagedSpell` (optionally reset) for the next lease. One `ManagedSpellQuantity` pool per managed spell version
lives in the owning root's Creations, reuses the kernel pools' elastic retention (`AbstractElasticPool`, 0.2.8234) and
travels with an ownership transfer like any record. Melder keeps the structure right - pools, the release registry,
records, transfer - and leaves the objects it hands out to the agents (src_architecture, "Runtime Model: Structure Is
the Contract").

## Non-goals
- No automatic return (scope cleanup, GC hooks, finalizers, generator leases); no record of objects that are out.
- No managed purge verb (owner, 2026-10-15): purge leaves a managed spell untouched.
- No behaviour change to the six existing members: spell ids, emitted executors and records byte-identical.
- No release through Aether, no ManagedSpells handle, no mixin or protocol member, no async, no MelderOps code.

## Changed components
| component | change | story |
| --- | --- | --- |
| Existence, ResolutionStyleMatrix | the seventh member; matrix count 7, the member non-unique (callable and existing-object families refuse it) | S1 |
| SpellArtifactProcessor | route family `"managed"` | S1 |
| Phase 6 ScopeOrderingStrategy | managed ranks 0 with unique | S1 |
| Bind, Spell, Spellbook.bind / bind_inactive, SpellBinder, scan_bind | four keyword options, checks, normalized Spell fields, a managed-only fingerprint part | S2 |
| SpellCrystal, RestoreEngine, GraftRunner, RecordVersion | the options recorded and replayed; RecordVersion 4.2.0 | S2 |
| ManagedSpellQuantity (new), ManagedSpellExhaustedError (new) | the pool (an AbstractElasticPool) and the exhaustion error | S3 |
| Creations, Spell._add_owned_conduit | a pool map beside `_creations`, ensure at owner stamping, pools disposed first, a `managed` extract/restore row | S3 |
| ConduitMeld, SpellSpaceMeld | store readers leave a managed spell alone (purge 0; the live probe answers from the pool) | S3 |
| ReleaseManagedSpell (new), ManagedSpellLease (new), package root | the class-keyed registry, release / managed / release_all / describe, the lease; four root exports | S4 |
| Occurrence instance processor and graph analyzer | a managed site is per path (one lease per injection) | S5 |
| Phase 10 discovery | the solo family declines a managed model (the generalized site plan dispenses) | S5 |
| Generalized manifest, SitePlanLowering, door compiler, generalized hydrator | the managed site kind (inline pop, reserve-first miss, children recorded with the object, leases returned when their consumer is never built), door route `"managed"` on the `many` templates, the specializer declines | S5 |
| Conduit | `managed_spell_meld` (meld plus a lease) | S5 |
| CachingSystem | no change (S5: plans are emitted at hydration and every notch already colds the cache) | S5 |
| TransferOfOwnership, Creations | pools move as rows; no-move keeps the old pool for rollback only; the owner stamp follows the lineage (stamped parked members re-stamped; a rollback stamps back and discards a pool a stamp composed, `discard_managed_quantity`) | S6 |
| System docs, graph, README, release note | the member documented | S7 |

## Invariants
1. Non-managed bindings are untouched: the fingerprint part is added only for managed bindings, every existing
   emitted executor is byte-identical, records gain fields only for managed spells, existing meld costs hold.
2. One pool per (owning root store, managed spell version). Pools live only in root stores, in their own map:
   resolution, live probes and purge never read a pool as an object.
3. A pool never constructs. On a miss the plan reserves a place first, builds the site's children, then the object;
   a failed build gives the place back and disposes the children it built.
4. `count` is the number of objects built and alive (idle plus out). `limited_quantity` never exceeds its limit;
   `queue` waiters are served by a release or raise at their deadline; `elastic` never refuses.
5. A release runs the optional reset, then appends. Disposal runs only when the pool destroys an object (elastic
   trim, a raising reset, teardown); a raising reset destroys the object, frees its place and propagates.
6. No reference to an object that is out is kept. Root teardown disposes the idle objects and every recorded `many`
   child (children of objects still out included), then unregisters the pools; the out objects are the agents'.
7. The registry holds exactly the pools held by live stores (register when a store takes one, unregister when it
   gives one up), is read lock-free, and needs neither a conduit nor Aether to release.
8. An ownership transfer disposes nothing: moving carries the same pool object with its idle objects, children and
   count; not moving keeps the old pool only for rollback; rollback restores it. The owner stamp follows the
   lineage: every member that carries one names the target's store after the transfer and its old store after a
   failed one, and a pool a stamp composed is discarded by the rollback (S6).
9. Locks: the pool lock and the registry lock are leaves; resets, constructors and disposal never run under a
   Melder lock; no new edge joins frame -> conduit -> Book.
10. Overrides: a managed node supplied by an override takes no lease; winning keys on the managed site's own
    parameters build a fresh object that is not pooled, counted or registered.
11. Melder returns an object to its pool itself only when it leased it for a holder that is never built: the
    holder's construction (or anything after the lease and before it) raised, or a shared holder lost its cold
    race to another meld (F9, widened in S5).

## Interface deltas
- Public: `Existence.managed_spell_quantity`; `ManagedSpellMode`; keyword options `managed_spell_mode`,
  `managed_spell_limit`, `managed_spell_timeout_seconds`, `managed_spell_reset_methods` on `Spellbook.bind`,
  `Spellbook.bind_inactive`, SpellBinder and `scan_bind`; `ReleaseManagedSpell` (`release`, `managed`, `release_all`,
  `describe`); `ManagedSpellLease`; `ManagedSpellExhaustedError` (a MeldExecutionError);
  `Conduit.managed_spell_meld`; `ManagedSpellMode`, `ReleaseManagedSpell`, `ManagedSpellLease` and
  `ManagedSpellExhaustedError` at the package root (the lease joined in S4). No existing signature or default
  changes.
- Internal: `Creations._managed_quantities`, `Creations.ensure_managed_quantity`,
  `Creations.discard_managed_quantity` (S6), the `managed` extract row; the
  `ManagedSpellQuantity` API (`reserve`, `put_back`, `abandon`, `adopt`, `destroy_object`, `cleanup`, `describe`);
  `ReleaseManagedSpell.register` / `unregister`; route family `"managed"`; the managed site in SitePlanEmission; the
  door tables' `"managed"` rows. The bind-guard manifest gains the new internal classes at the rebuild.
- Persisted: SpellCrystal fields for the four options (managed spells only); RecordVersion 4.1.0 -> 4.2.0 (minor:
  added fields). No creation-cache generation (S5).

## Migration order
This patch -> per story: component patch (and code description where required) -> mapping note -> red tests (GIL
off and on) -> `src/` -> green -> notch and the running release note's managed section -> next story. Order: S1
member and classification, S2 bind options and record, S3 pool and Creations, S4 registry and lease, S5 codegen and
`managed_spell_meld` (emission diff gate), S6 transfer, S7 documentation, benchmarks, patch promotion, rebuild last.

## Rollback
Each story is one notch with its tests: revert that notch's files. Records written at 4.2.0 hold managed fields only
for managed spells; a build without the member cannot restore a managed spell (its existence name is unknown), and
every other record reads as before.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | S2 id byte-identity tests for every existing member; S5 emission diff over the certification worlds; S7 meld benchmarks within noise |
| 2 | S3 unit: the map, ensure/adopt, resolution and purge never see a pool |
| 3 | S3 unit (reserve/abandon/adopt); S5 component: a failing constructor and a failing child give the place back and dispose the built children |
| 4 | S3 unit per mode and the multithreaded stress test (limit never exceeded, waiters served or timed out, no hang) |
| 5 | S3 unit: reset order, raising reset destroys and frees, disposal only on destroy; S5 component: trim disposes the object and its children |
| 6 | S3 unit and S5 component: teardown disposes idle objects and recorded children (weak references), out objects untouched, pools unregistered |
| 7 | S4 unit: register/unregister follow take/give-up, lock-free reads, ambiguity and filters, not-managed error |
| 8 | S6 unit and integration: move, no move, rollback, parked members, owner stamps both ways, releases after the move |
| 9 | S3/S4 multithreaded tests; reviews of every new lock site against B10 |
| 10 | S5 component: a supplied managed node takes no lease; own-parameter keys build a fresh unpooled object |
| 11 | S5 unit and component: a consumer constructor, a sibling lease's build or a pinned refusal that raises returns the leases; a lost race returns them |
