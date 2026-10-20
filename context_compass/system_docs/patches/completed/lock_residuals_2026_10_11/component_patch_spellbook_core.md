# Component patch: Spellbook Core - inspection and disposal (lock_residuals_2026_10_11)

## Before / after
- `inspect_spell`: held the Book lock for the whole three-stage search, including `Aether._check_for_spell` (frame
  locks) and the walk of `frame._conduits` live. After: the Book lock covers stage 1 only (this Book's `_spells`, the
  lock bind and removal write it under); stage 2 walks `list(frame._conduits.values())` and, as before, a one-call
  copy of each other Book's `_spells`; every `_check_for_spell` runs with no lock held. A stage-1 match is remembered
  with a flag, so a match whose index selects no id still answers None as before.
- `_dispose_spell` (cleanup_spell's body): two calls on one spell could both pass the Book-locked decision and both
  run invalidation and disposal (double unregister, double Aether removal, two destroy emissions, a misleading error
  for the late one). After: the decision checks `_disposing_spell_ids` first and, for a spell it will dispose (owned,
  and not the active member of a multi-member index), adds its id in the same locked section; a call that finds the id
  raises RuntimeError "cleanup_spell: spell <id> is already being disposed by another call."; the disposal branches run
  inside try/finally and the finally discards the id under the Book lock. The not-owned classification and the
  multi-member refusal are unchanged. The 0.2.8231 comment is corrected: Book cleanup does take the spell lock under
  the Book lock (`_cleanup_spells`); this method nests neither.
- New field `_disposing_spell_ids: set[str]` in `__init__` beside the id maps; cleared and deleted in
  `_cleanup_components` with them.

## Interface deltas
New internal field only. Public signatures and quiet-world results unchanged.

## State / failure deltas
New RuntimeError for a disposal that overlaps another of the same spell. `inspect_spell` no longer answers None for a
registered spell because a root registers in the frame.

## Dependency / ordering
The mark is read and written only under the Book lock, in sections that already held it; no lock is taken under it.
inspect_spell drops Book -> frame. A disposal racing the Book's own teardown is unsupported as before.

## Validation expectations
Index-link destroy cascade, multi-member refusal and "already been disposed" tests unchanged; new tests for the
overlapping disposal (active, inactive) and inspection (walk, lock discipline) red on 0.2.8231, green on 0.2.8232.
