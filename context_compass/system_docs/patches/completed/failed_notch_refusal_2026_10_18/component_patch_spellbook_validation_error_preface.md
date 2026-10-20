# Component patch: SpellbookValidationError takes a preface (failed_notch_refusal_2026_10_18)

## Before / after behavior
- Before: the message is the report alone, first line "Spellbook validation failed. Broken spells: A, B.".
- After: `preface=` (keyword-only, default None) puts one line before that report; without it the message is
  byte-identical. The notch refusal passes "notch_spell refused: ... so the notch did not happen; ... is still the
  active version of the index.".

## Interface deltas
- Public, additive: `SpellbookValidationError(broken_spells, *, system_diagnostics=None, preface=None)`. A preface
  that is not a str raises TypeError; an empty one is refused the same way (it would add a blank first line), and
  so is one with a line break (the refusal is one line; a second would sit between it and the report).

## State and failure deltas
- None: the message is still built once, at construction; `broken_spells` is kept as given.

## Dependency and ordering
- The class docstring's "Message shape" gains one line for the preface; the substrings matchers use are unchanged.

## Validation expectations
- Unit: without a preface the message is unchanged (an existing message-shape test still passes); with one, the first
  line is the preface and the second the report's first line; a non-str, empty or multi-line preface raises
  TypeError.
