# Code description patch: Conduit - resolving and checking the notch target

## Metadata
- Patch ID: public_notch_target_2026_10_16
- Component: `Conduit.notch_spell`, `Conduit._resolve_notch_target`, `Conduit._owned_notch_target`
- Writer: melder_0 (synaptic_python_developer)
- Created: 2026-10-16T12:50:00Z
- Status: built as described (0.2.8249); promoted into src_components (the notch flow) and src_architecture (the
  invariant and failure modes); the argument check now shared with the index moves (`_check_spell_argument`);
  archived
- Why a code-description patch: new error semantics (five refusals) and a check repeated inside a transaction
  window for a concurrency reason.

## Control flow
```text
notch_spell(spell_index, spell=None, spell_id=None, change_reason)
  check_cleaned; dynamic gate (RuntimeError); owning Book present (RuntimeError)
  spell = _resolve_notch_target(spell_index, spell, spell_id)
      both / neither                      -> ValueError
      spell_id not str / spell is a str   -> TypeError
      _owned_notch_target(spell_index, spell_id or spell.spell_id, spell or None)
          owned = Book._get_owned_spell(id); None, or not the given object -> ValueError (not owned)
          owned.spell_index is not spell_index                         -> ValueError (another index)
          return owned
  metadata from spell; outgoing_id = spell_index.selected_spell_id
  mediator.start_transaction(NOTCH)          # seals the Book and its conduit EXCLUSIVE, freezes their gates
  try:
      _owned_notch_target(spell_index, spell.spell_id, spell)   # same checks, now under the seal
      result = Book._notch_spell(spell_index, spell, change_reason)
  except: end_transaction(success=False); raise
  end_transaction(success=True)
  if outgoing_id != spell.spell_id: park borrowers' outgoing copies; move index-link subscriptions
  return result
```

## Edge and error semantics
| call | outcome |
| --- | --- |
| `spell_id=<parked member of spell_index>` | the version becomes active; returns it |
| `spell_id=<active member of spell_index>` | no-op: the seam returns the spell; no fan-out |
| `spell=<owned member>` | as before |
| both, or neither | ValueError, nothing started |
| `spell_id` not a str; `spell` a str | TypeError, nothing started |
| an id the Book does not own (unknown, another Book's or frame's, disposed) | ValueError (not owned), nothing started |
| a Spell the Book does not own (another Book's; a stale object for a disposed id) | ValueError (not owned), nothing started |
| a version of another index of the Book (parked or active) | ValueError (another index), nothing started |
| the target moved to another index or Book after the first check | ValueError inside the window; transaction ended failed; seam not called |
| an automatic frame; a cleaned conduit; no Book | RuntimeError, unchanged |

Messages name the version id, say what is wrong and how to fix it; none quotes a Spell's repr.

## Invariants and idempotency
- The resolved target is the object the seam receives and the metadata names; the fan-out reads `spell.spell_id`,
  the same object, so a notch by id and a notch by the same Spell are indistinguishable after resolution.
- Repeating a notch to the now-active version is a no-op (seam idempotency, unchanged).
- Each check is a pure read; a refusal leaves the Book, both indexes and every conduit as they were.

## Concurrency
- The first check runs with no claim held: a concurrent add, remove, notch or transfer can move the target between
  it and admission. Admission seals the Book and its conduit EXCLUSIVE (the notch strategy), which excludes every
  other index operation on the Book until the transaction ends, so the second check is the one the switch relies
  on.
- `Conduit.cleanup_spell` is not admitted through a transaction: a disposal of the target between the second check
  and the seam's Book lock still reaches the seam, which parks the outgoing version before it checks the incoming
  one. Pre-existing; filed as a backlog task for the spellbook.py holder, outside this patch.

## Non-goals
- No new lookup, no change to `find_spell_by_id` / `get_spell_by_id`, no change to the seam or the strategy, no
  keyword on `add_to_spell_index` / `remove_from_spell_index` without the owner's word.
