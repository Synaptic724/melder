# Architecture patch: spellmap_binding_name_case_2026_10_04

## Objective and non-goals
- Objective: `SpellMap` and `SpellContract` keep `binding_name` exactly as the caller wrote it, as `Bind`
  does, and a SpellMap default resolves through the same case-insensitive address rule bind and meld use,
  so `SpellMap(spellframe="agents", binding_name="ScanProfile")` finds the spell bound as
  `bind(..., spellframe="agents", binding_name="ScanProfile")`.
- Non-goals: no change to the canonical key (`canonical_key` stays lowercase), to Meld's or SpellContract's
  key-based resolution, to annotation matching by kind, or to the descriptors' constructor signatures.

## Changed components
- DI descriptors (`SpellMap`, `SpellContract`).
- SpellCompiler Phase 3 (`CompilerPhase3._resolve_spellmap_default`).
- Phase 4 validation (`SpellMapShapeValidationStrategy`): the lowercase-advice warning is retired.
- Structural snapshot (`StructuralSnapshot` SpellMap reference row): normalized explicitly.

## Invariants
- A descriptor's `binding_name` is the caller's text (or None); `canonical_key` is the lowercase address
  key; `lookup_triplet` is raw.
- Phase 3 compares binding names by their normalized keys (None and "" both mean the default binding) and
  string spellframes by their normalized frame keys; class and Protocol frames stay identity matches.
- Snapshot rows and cache formats are byte-identical to 0.2.8225 for every input; no cache generation move.

## Interface deltas
- `SpellMap.binding_name` and `SpellContract.binding_name`: the value as given instead of lowercased.
- A non-string `binding_name` raises TypeError at construction (was AttributeError from `.lower()`).
- Phase-4 code `SPELLMAP_BINDING_NAME_NOT_NORMALIZED` is no longer emitted.
- A consumer whose constructor default carries a mixed-case SpellMap or SpellContract binding name gets a
  new spell id once, because the bind fingerprint hashes parameter-default reprs.

## Migration order
1. Descriptors. 2. Phase 3 matching. 3. Phase-4 strategy and snapshot row. 4. Tests (two pinned tests
inverted, regression tests added). 5. System docs, graph, notch 0.2.8226, release note. 6. Assets, bundles.

## Rollback
- Restore the lowercasing in both descriptors and the raw comparisons in Phase 3; ids revert with them.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-04_match_descriptor_binding_names_like_bind_task.md |
