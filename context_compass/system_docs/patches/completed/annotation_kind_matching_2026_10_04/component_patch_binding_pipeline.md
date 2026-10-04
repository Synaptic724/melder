# component_patch_binding_pipeline

## Metadata
- Patch ID: annotation_kind_matching_2026_10_04
- Status: active
- Owner: user (agent fable_1)
- Created: 2026-10-04T01:20:00Z
- Updated: 2026-10-04T01:20:00Z

<!-- BEGIN ENTRY: "Bind: spellframe kinds and the concrete-class refusal" -->
## Before
- `Bind._bind_logic` accepts any `spellframe`. Step 1 refuses a Protocol as a resolvable spell; step 4 runs
  `_structurally_implements_protocol` for class and existing-object spells when the frame is a Protocol
  (`_is_protocol_type`), and skips function/lambda spells. Nothing classifies the frame; a concrete class, an
  instance or any other object is accepted and keyed by `normalize_frame_key` (`__name__`, else `str()`).
  The Spell is constructed with the raw frame and nothing else about it.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:664-675
  - src/melder/aether/spellbook/bind/bind.py:731-754
  - src/melder/aether/spellbook/bind/bind.py:764-785
  - src/melder/aether/spellbook/bind/bind.py:1238-1263
  - src/melder/aether/spellbook/bind/bind.py:1265-1314

## After
- Step 4 classifies the frame first: `None` -> `SpellframeKind.none`; `str` -> `category`; a Protocol class
  (`_is_protocol_type`) -> `contract`, then the existing structural check; anything else raises
  `TypeError("spellframe must be a string category or a Protocol contract; got <kind> '<name>'. ...")`.
- The Spell is constructed with `spellframe_kind` and `implemented_protocols=(spellframe,)` for a contract,
  `()` otherwise. `_is_protocol_type` delegates to `SpellInputUtils.is_protocol_type` so Phase 3 uses the same
  detection without importing Bind.

## Interface Deltas
- Breaking: a non-string, non-Protocol spellframe is refused at bind. Public enum `SpellframeKind`.

## State / Failure Deltas
- New TypeError text names the offending kind and value and the two accepted forms. Fingerprints are
  unchanged (the frame was already hashed as `str(spellframe)`).

## Validation Expectations
- Unit (test_bind.py): string -> category, Protocol -> contract with the Protocol in `implemented_protocols`,
  None -> none; a concrete class, an instance and an int are refused with the new message; the structural
  check still refuses a class missing a member; functions under a Protocol frame are still accepted unchecked.
<!-- END ENTRY: "Bind: spellframe kinds and the concrete-class refusal" -->

<!-- BEGIN ENTRY: "Spell: spellframe_kind and implemented_protocols" -->
## Before
- `Spell.__init__` stores `spellframe` as given and derives the address key with
  `make_spell_key_from_parts`; no field says what kind of frame it is. Cleanup deletes the owned runtime
  slots and keeps identity data (`spellframe`, `spell_name`, `binding_name`) readable.
  EVIDENCE:
  - src/melder/aether/spellbook/spell.py:296-330
  - src/melder/aether/spellbook/spell.py:406-427
  - src/melder/aether/spellbook/spell.py:600-631

## After
- Two keyword parameters with defaults (`spellframe_kind: SpellframeKind = SpellframeKind.none`,
  `implemented_protocols: Tuple[type, ...] = ()`), stored as public read fields beside `spellframe`; the
  docstring's Key Concepts names the three kinds. Identity data, so not deleted at cleanup. `__repr__`
  unchanged.

## Interface Deltas
- Internal constructor only (Spells are produced by Bind). Two new public read attributes.

## Validation Expectations
- Unit (test_spell*.py): defaults; values pass through; survive cleanup; `describe`/profile unchanged.
<!-- END ENTRY: "Spell: spellframe_kind and implemented_protocols" -->
