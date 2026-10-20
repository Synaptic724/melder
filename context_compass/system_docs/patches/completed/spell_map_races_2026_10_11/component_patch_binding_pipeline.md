# Component patch: Binding Pipeline (spell_map_races_2026_10_11)

## Before / after
- SpellIndex.has_spell: check_cleaned() then lock then read; a cleanup between them raised AttributeError. After:
  the check is repeated under the lock, so the only failure is the documented RuntimeError.
- New SpellIndex._has_spell_unless_cleaned(spell_id): membership under the lock, False once cleaned (for walkers
  over indexes they neither own nor lock).
- Detail.has_spell and IndexDetail.has_spell read spell_index._spells_in_index unlocked and unchecked; after: their
  own check_cleaned() then SpellIndex._has_spell_unless_cleaned.

## Validation expectations
Unit tests: has_spell with a cleanup forced between check and lock raises RuntimeError (AttributeError before);
the probe answers membership while live and False after cleanup; Detail and IndexDetail over a cleaned index
answer False.
