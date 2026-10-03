# Architecture patch: owner-store constants on the warm path of a site plan (S9)

- Patch id: flat_warm_body_2026_10_03
- Status: active (entry gate for TASK-2026-10-03-certify-and-implement-site-store-constants)
- Owner: fable_0
- Created: 2026-10-03T21:41:39Z

<!-- BEGIN ENTRY: "Owner-store constants: objective, non-goals, invariants" -->
## Objective
A shared site of existence `unique` whose provider Spell is owned by an automatic conduit reads its instance from
a store the plan namespace binds at hydration (`c{i}`), instead of re-reading `spells[i]._owner_creations` on
every creation. The emitted body loses one line per such site; the namespace gains one constant. Measured on the
VM: -7..-17% of the plan on the harness shapes with unique providers (8-10 ns per site), -3% on a chain with one.

## Non-goals
- The other shared existences (per-conduit, spellspace, lineage, cluster): their store is one attribute read on
  the `meld` parameter already and lineage/cluster stores move.
- Dynamic posture: ownership transfer repoints a spell's owner store, so the per-creation read stays.
- S11 (key identity): already true - every `sid{i}` is the live Spell's `spell_id` object, because plans are
  emitted at hydration from rows resolved to live spells. S2a (existing-object constants): parked by the owner.

## Invariants
- The constant is the Creations OBJECT; the dict it reads (`c{i}._creations`) is still read per creation, so a
  store swapped empty by cleanup or clear is seen as today.
- An owned spell's owner store changes only through `Spell._add_owned_conduit` (conjure, and ownership transfer
  in dynamic posture); a notch or a late bind re-gates and recompiles the plan, which re-emits the constant from
  the live spell. In an automatic world nothing repoints the store after conjure.
- A provider without an owner store at emission keeps today's line (the failure mode is unchanged).
- The miss keeps its `c{i}` parameter; the warm call passes the global; misses are byte-identical.
- No cache generation bump: the manifest persists rows, never emitted plan source.

## Interface deltas
- Public API: none. Behaviour: none observable (same objects, same errors, same locks).
- Private: `SitePlanEmission._emit_shared_hit` binds `c{i}` for eligible sites; the class contract documents it.

## Migration order
1. Lowering edit + the `_spell` test stub (`_dynamic_environment`), emitter unit tests for both postures and the
   unowned case; component tests (automatic: no alias line, same instance across melds and a cache full hit;
   dynamic: the line is present).
2. Harness re-run on the shipped body; docs (component SpellCompiler codegen, architecture invariant), release
   note, notch, assets last.

## Rollback
Emit the line unconditionally again (one condition).

## Ticket coverage matrix
| patch section | ticket | validation |
| --- | --- | --- |
| lowering edit | TASK-2026-10-03-certify-and-implement-site-store-constants | emitter unit tests, component conjures, harness |
<!-- END ENTRY: "Owner-store constants: objective, non-goals, invariants" -->
