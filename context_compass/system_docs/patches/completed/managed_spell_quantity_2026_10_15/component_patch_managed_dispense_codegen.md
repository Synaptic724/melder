# Component patch: leases through plans, doors and managed_spell_meld (managed_spell_quantity_2026_10_15, S5)

Components: SpellOccurrenceInstanceProcessorStrategy and SpellOccurrenceGraphAnalyzerStrategy (sharedness),
SoloCodegenPlanDiscoveryStrategy, the generalized manifest (route key), the generalized manifest no-overrides compiler
(a row predicate), the generalized hydrator (the singleton specializer), the door compiler (route tables),
SitePlanLowering / SitePlanEmission / SitePlanRuntimeHelpers (the managed site kind) and Conduit
(`managed_spell_meld`). Story: STORY-2026-10-15-managed_dispense_codegen. Control flow, edge semantics and invariants:
the code-description patch beside this.

## Before / after
- Before (0.2.8244): a managed spell is bound, stamped and pooled (S2-S4), but nothing dispenses it. Both sharedness
  predicates count it shared (one instance key), solo discovery claims a lone managed spell, the generalized manifest
  raises for route "managed", SitePlanEmission would treat it as a shared site whose `_route` raises, and no door
  serves route "managed".
- After:
  - Sharedness: `_is_shared_existence` of the occurrence instance processor and of the occurrence graph analyzer
    answer False for `managed_spell_quantity`, as for `many`: one instance key and one occurrence per path, so every
    injection is its own lease.
  - Discovery: the solo strategy declines a model whose existence counts hold `managed_spell_quantity`; many_only
    already declines (not all-many); the generalized family claims it.
  - Manifest: `_resolve_route_key_from_model` accepts route family "managed". MANIFEST_VERSION stays 4.
  - Door: the four route tables map "managed" (both fast bits) onto the existing `many` template objects. The
    no-overrides doors call the normal plan, the overrides doors call `_execute_with_overrides`, and the hooks doors
    report `created=True`, so every lease runs the activation hooks (U7). No template is added or recompiled.
  - Specializer: `rows_contain_managed_step(rows)`, a pure predicate beside `rows_feed_many_into_non_many_step`,
    makes `_install_specializing_door` return the plain door for any graph with a managed row.
  - SitePlanEmission: a managed step is a LEASING site when no winning key targets its own parameters, else a FRESH
    site.
    - Leasing site: placed like a shared site (its own `_miss{i}`), with exactly one consumer (per path) or none
      (the root). Its value is an inline pop from the pool: `pp{i}()` when the pool is a plan constant (S9's rule -
      automatic owner, owner store set - and the pool present at emission), else `h{i}._idle.pop()` after a
      per-creation pool read; an empty pool calls the miss.
    - Its miss: the unresolved-input check, `h{i}.reserve()` (an object served returns at once), `kids{i}` when
      disposal-bearing `many` children live inside, then children, its own leases and construction inside a `try`
      whose handler calls `h{i}.abandon(kids, exc)` and re-raises, then `h{i}.adopt(v, kids)` when kids exist.
    - Placement: each lease is emitted right before its consumer's construction region; for a consumer that has a
      miss (shared or leasing managed) at the end of that miss's children, before the guard.
    - Return: an exception between a consumer's first lease and its construction (a later lease's build, the
      construction, a pinned refusal, the publication) puts back every lease taken for that consumer; a shared
      consumer that loses its cold race puts back its unused leases.
    - Children: a disposal-bearing `many` child inside a managed miss is recorded with the object
      (`kids{i}.append((v, dm))`, then `adopt`), never `register_many`.
    - Fresh site: constructed like a `many` step at its consumer's context; never pooled, counted, registered or
      adopted (the caller's object). Its own leases follow the same placement and return.
  - Conduit: `managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)`
    resolves the target as `meld` does, refuses a non-managed spell before melding, reads its pool from the spell's
    owner store, melds the resolved version by id and returns `ManagedSpellLease(obj, pool)`.

## Interface deltas
- Public: `Conduit.managed_spell_meld`.
- Internal: `SitePlanRuntimeHelpers.return_leases`, `return_unused_leases` and `raise_missing_managed_pool` (bound
  into a plan's namespace only when it has a managed site); `rows_contain_managed_step`; the door tables' "managed"
  rows; the two predicates' answer for managed.
- Persisted: none new. A managed spell's manifest rows carry `existence: "managed_spell_quantity"` and route key
  "managed" in the same row shape. No manifest version, record version or cache generation moves (the epic's planned
  generation 21 is dropped: plans are emitted at hydration, and every notch already makes the cache cold).

## State / failure deltas
- Missing pool (per-creation read, MeldExecutionError): "Managed spell '<name>' has no pool to lease from: its owner
  root was torn down, or this version was never given one (a version staged with bind_inactive before conjure and
  notched in after it). Meld it through a live root, or stage the version after conjure."
- `managed_spell_meld` of another existence (ValueError, nothing melded): "managed_spell_meld leases a managed spell;
  '<name>' is <existence>. Meld it with meld(), or bind it with existence=Existence.managed_spell_quantity."
- Exhaustion, torn-down and reset errors come from the pool unchanged (S3). A put-back that fails while a lease is
  returned on an exception becomes a note on that exception: "Returning an object leased from managed spell
  '<name>' failed: <failure>". Put-backs that fail after a lost race raise once all were tried: ExceptionGroup
  "Returning objects leased for a construction another meld finished first failed".

## Dependency / ordering
- S1 (route family "managed"), S2 (Spell fields), S3 (`reserve`, `put_back`, `abandon`, `adopt`; `_idle` is assigned
  once and drained, never swapped, so a bound pop stays valid for the pool's life), S4 (`ManagedSpellLease`).
- S6 relies on the per-creation read in dynamic worlds and on an ownership stamp cleaning the stamped spell's own
  creation context; a version staged before conjure and notched in has no owner (the story's FACT note) - the
  re-stamp at notch is S6's, raised to the owner.

## Validation expectations
- Unit, both GIL modes (test_site_plan_lowering_managed.py): emitted shapes - root lease (constant and per-creation),
  lease under a many, a shared and a managed consumer, collections, fresh site under own-parameter keys, supplied
  consumer parameter (no lease); runtime behaviour on real pools - pop hit, reserve on empty, served object, abandon
  on a raising child and a raising constructor (place back, kids disposed, notes), adopt with kids, the lease return
  on a raising consumer, a raising sibling and a lost race, the missing-pool error; discovery, predicates, manifest
  key, specializer decline and door rows.
- Component (test_conduit_component_managed_spell_quantity.py): direct meld reuse, injection into many and unique
  holders, every mode's refusal and wait through melds, overrides, failed-construction return, trim disposes the
  object and its recorded children, hooks see `created=True`, `managed_spell_meld` with and without `with`.
- Integration (test_conduit_integration_managed_spell_quantity.py): two roots, two binding names, per-frame ids,
  dynamic world (per-creation read), crystallizer restore, `managed_spell_meld`.
- Emission diff: `s5_emission_capture.py` output equal before and after for every non-managed entry.
- Benchmark: the warm lease cycle (meld plus release) inside a plan, both modes.
