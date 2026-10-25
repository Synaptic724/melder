# component_patch_binding_pipeline

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Component: Binding Pipeline (Bind, Spell, SpellIndex)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z

## Component Purpose and Boundary
- Current boundary: a SpellIndex holds its immutable ULID, the selected spell_id and the member set; it records
  nothing about how its members are bound. Bind builds one index for every Spell it creates,
  `SpellIndex(initial_id=spell_id)` (`Bind._bind_logic`).
- Target boundary: a SpellIndex also keeps the binding of the version it was built for and checks a version against it
  (`check_admits`); Bind builds the index with that binding (`SpellIndex.for_binding`). When to check is Spellbook
  Core's call (component_patch_spellbook_core).

## Before/After Behavior Summary
- Before: any version could join any index; nothing recorded or compared how the versions of one index are bound.
- After: `binding_signature` is `(kind, frame_key, binding_key)`. The kind is "none" (no spellframe), "category" (a
  string) or "contract" (a Protocol) - the values of `SpellframeKind` - and the two keys are
  `SpellInputUtils.make_spell_key_from_parts`', the address `Spell._key` holds. `check_admits(spell, *, verb)` builds
  the version's signature from its `spellframe`, `spell_name` and `binding_name` and raises ValueError when it
  differs from the index's.

## Interface Deltas
- Inputs: `SpellIndex.__init__(initial_id, *, binding_signature=None, binding_text=None)`;
  `SpellIndex.for_binding(initial_id, *, spellframe, spell_name, binding_name)` (classmethod; computes both and builds
  the index); `SpellIndex.signature_of(*, spellframe, spell_name, binding_name) -> Tuple[str, str, str]`
  (staticmethod, pure); `check_admits(spell, *, verb)` reads `spell.spellframe`, `spell_name`, `binding_name` and
  `spell_id`, and nothing else.
- Outputs: `binding_signature -> Optional[Tuple[str, str, str]]`, read-only.
- Error semantics: `check_admits` raises ValueError "<verb> refused: SpellIndex <id> keeps the binding its first
  version was bound with - <the index's binding> - and '<name>' (spell_id <id>) is bound with <the version's
  binding>. ..." whose remedy says to stage an edited class with the index's spellframe and binding_name and that a
  renamed class or a new binding name is a new spell. A binding reads "the Protocol spellframe Greeter and
  binding_name 'english'", "the string spellframe 'Reports' and binding_name 'Main'" or "no spellframe (bare,
  addressed by its own name 'Report') and the default binding name". An index built without a binding raises
  RuntimeError "... records no binding ..." (a Melder bug: Melder builds every index with one); a cleaned index
  raises the cleaned RuntimeError.

## State and Lifecycle Deltas
- Owned state: `_binding_signature` and `_binding_text` (slots), written once in `__init__`, read without the lock, and
  kept after cleanup like `_id`: immutable values, so no reader racing a cleanup meets a deleted field.
- Bind: `spell_index = SpellIndex.for_binding(spell_id, spellframe=spellframe, spell_name=str(spell_name),
  binding_name=binding_name)` where it built `SpellIndex(initial_id=spell_id)`, in the same place under the Bind lock.

## Failure Mode Deltas
- New failure mode: the two refusals of `check_admits` (Error semantics above).
- Removed failure mode: none in this component; the staging and notch defects close in Spellbook Core.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. Bind classifies the spellframe (`_classify_spellframe`) before it builds the index, so an index never records an
   object Bind refuses; `signature_of` classifies the three accepted forms (None, a str, a Protocol) as
   `_classify_spellframe` does.
2. The address is the one `Spell._key` and the frame claim use, so the index's address and its versions' keys agree by
   construction.

## Validation Expectations
- tests/unit/melder/spellbook/bind/test_spell_index_binding_signature.py: `signature_of` for the three kinds,
  `for_binding`, `check_admits` admitting a version bound the same way (case aside) and refusing another binding name
  or kind with the message's parts, and an index without a binding.
- test_index_records_the_binding_its_first_version_was_bound_with in the component file.
- The existing SpellIndex unit tests stay green: positional construction still builds an index.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: the binding on the index, its check and Bind's use of it.
- Remaining risks: tests and examples that stage another binding (counted at the suite run).
- Next entrypoint: `SpellIndex.for_binding`, then `Bind._bind_logic` where it builds the index.
