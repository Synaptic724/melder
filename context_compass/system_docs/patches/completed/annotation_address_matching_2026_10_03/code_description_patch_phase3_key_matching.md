# Code description patch: `CompilerPhase3` key matching

- Patch id: annotation_address_matching_2026_10_03
- File: `src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py`
- Owner: fable_0
- Created: 2026-10-03T19:25:31Z

<!-- BEGIN ENTRY: "Key matching: control flow and edge semantics" -->
## Control flow
1. `_annotation_key(annotation)`: ForwardRef -> its name; then `SpellInputUtils.normalize_frame_key`.
2. `_spell_keys(spell_obj)`: `(normalize_frame_key(spellframe if not None else spell_name),
   normalize_frame_key(spell_name))`; equal keys collapse to one.
3. `_matches_annotation`: class-spell exclusion; key membership; binding filter.
4. `_build_candidate_index`: `by_key[key] -> [(position, spell_index, spell)]`, one append per distinct key.
5. `_get_candidate_index`: build once per pass; always usable.
6. `_indexed_annotation_candidates`: one bucket; the existing first-position/last-object collapse.

## Edge and error semantics
- `spell_name` is always a string (bind derives it); an annotation that is neither a class nor a string keys
  through `str()` as frames do.
- Two spells with the same class name at one address: Phase 4 refuses; Phase 3 reports both as candidates
  (ambiguity) when it runs first - identical to today's string path.

## Invariants / idempotency
- Pure functions of pass-invariant inputs; the index is rebuilt per pass as today.

## Explicit non-goals
- Inheritance matching (a subclass does not satisfy its base's annotation), unchanged.
<!-- END ENTRY: "Key matching: control flow and edge semantics" -->
