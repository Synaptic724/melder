# component_patch_spellcompiler_phase3

## Metadata
- Patch ID: annotation_kind_matching_2026_10_04
- Status: active
- Owner: user (agent fable_1)
- Created: 2026-10-04T01:20:00Z
- Updated: 2026-10-04T01:20:00Z

<!-- BEGIN ENTRY: "CompilerPhase3: annotation matching by kind" -->
## Before
- `_annotation_key` lowercases the annotation's name (ForwardRef -> name, class -> `__name__`, string ->
  itself). `_spell_keys` returns the spell's frame key (spellframe, else own name) and type key (spell name).
  `_matches_annotation` accepts a spell when the annotation key is in the spell's keys; `_build_candidate_index`
  buckets every spell under its one or two keys in `{"by_key": ...}`; `_indexed_annotation_candidates` reads
  the one bucket. `_resolve_single_by_annotation` and `_resolve_collection_by_annotation` use that predicate
  on both the indexed and the scan paths (0.2.8218). A string category named like a class is therefore a
  provider set for that class, and a class name is a group for a collection.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:186-284
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:310-411
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:413-534

## After
- `_annotation_kind(annotation)` -> `type` (a class that is not a Protocol), `contract` (a Protocol class,
  `SpellInputUtils.is_protocol_type`), `name` (ForwardRef, string, anything else).
- Spell keys by kind: `type_key` = normalized spell name (a class's name; an existing object's class name);
  `contract_key` = normalized Protocol name when `spellframe_kind is contract`, else None; `label_key` = the
  address frame key (spellframe's name, else own name) - what a collection annotation gathers.
- Single resolution: `type` -> type_key equals; `contract` -> contract_key equals; `name` -> type_key or
  contract_key equals. Never the label of a category. Collection resolution: `type` -> type_key; `contract`
  -> contract_key; `name` -> label_key. Ambiguity, the empty mapping (UNRESOLVED_INPUT), resolvable
  preference and the METHOD/LAMBDA exclusion are unchanged.
- The pass index becomes `{"by_type": ..., "by_contract": ..., "by_label": ...}`; a single lookup reads
  one or two buckets and the scan predicate is the same function, so membership and order match the scan.
- `_spell_keys` is retired (the structural snapshot does not call it; verified by grep at landing).

## Interface Deltas
- Internal only. The RuntimeError text for ambiguity is unchanged.

## State / Failure Deltas
- `spectrum: Spectrum` with Toolbox in category "spectrum" resolves Spectrum; Toolbox alone yields
  UNRESOLVED_INPUT (UnresolvedInputError at meld without an override). `repo: "extra_frame"` (a string naming
  a category) no longer resolves a single provider - use `SpellMap(spellframe="extra_frame")`. `list[Impl]`
  gathers spells of class Impl, not members of a category spelled "impl" bound as other classes.

## Validation Expectations
- Unit (test_compiler_phase_3.py): predicate per annotation kind x spell kind; indexed == scan for every
  kind including order; index layout pin updated. Integration: the four strict-xfail cases pass; a
  Protocol-typed parameter resolves its implementer; a TYPE_CHECKING string naming a Protocol resolves;
  `list["category"]`, `list[Proto]`, `list[Cls]` gather their own groups; two providers of one type remain an
  ambiguity; explicit addressing unchanged.
<!-- END ENTRY: "CompilerPhase3: annotation matching by kind" -->
