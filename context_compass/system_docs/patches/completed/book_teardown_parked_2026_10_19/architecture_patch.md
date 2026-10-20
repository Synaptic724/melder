# Architecture patch: book_teardown_parked_2026_10_19

Story: STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned (S7 of EPIC-2026-10-17-correctness_defects).
Agent: melder_1 (synaptic_python_developer). Status: draft, for the owner's word before any src edit.

## Objective
A Spellbook's teardown retires every version it owns - the parked ones included - and every SpellIndex it owns,
including an index only parked versions hold (one `remove_from_spell_index` minted). Melder's infrastructure cleans
up its own state (src_architecture, Runtime Model); a Spell and its SpellIndex are Melder's records of a version.

## Non-goals
- Frame signature claims a parked version may hold after a notch across keys (the two signature stories).
- Index-link borrowers' copies (the ward's teardown) and the Crystallizer record (it already evicts the Book).
- Userland objects: nothing new is disposed; a parked version's managed pool already leaves with the root's store.

## Changed components
- Spellbook teardown (`Spellbook._cleanup_spells`, its caller `_cleanup_components`), one module: spellbook.py.

## Invariants
- After `Spellbook.cleanup()` - reached from a root's teardown, a frame's teardown or a direct call - every Spell and
  SpellIndex the Book owned reads cleaned, and `Spell.cleanup()` on any of them returns.
- A parked version's retirement is local: it holds no lineage registration, no resolution-map entry and no frame
  lookup of its own, and the root's teardown has already unregistered its index from the frame (0.2.8259).
- Lock order unchanged: spell and index locks are taken under the Book lock, as the active loop takes them.

## Interface deltas
- None public. Visible: a torn-down Book's parked versions read `cleaned` True and their `cleanup()` returns; it
  raised RuntimeError "Spellbook has already been cleaned.".

## Migration order
1. The edit in `_cleanup_spells` with its docstrings; the symptom-named tests red before, green after.
2. System documents (the cleanup sequence, an operational invariant, a fixed failure mode, the Spellbook component)
   with their indexes and the graph; the release note; the notch; closure; the rebuild last.

## Rollback
- Revert the edit. No cache generation, record version or persisted shape changes.

## Ticket coverage
| requirement | step | validation |
| --- | --- | --- |
| parked versions cleaned at teardown | edit (parked loop) | tests: shared index, own index, unconjured Book |
| parked-only index cleaned | edit (parked-only indexes) | test: own index; probe T3 |
| `Spell.cleanup()` returns afterwards | edit | tests; probe T2 |
| active-only and managed unchanged | none | controls; probe T1, T5 |
