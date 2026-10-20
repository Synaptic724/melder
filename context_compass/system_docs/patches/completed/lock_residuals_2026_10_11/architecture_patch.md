# Architecture patch: lock_residuals_2026_10_11

## Objective
Fix the lock bugs found after 0.2.8231 (owner direction 2026-10-11: "fix the bugs you found ... make sure performance
doesn't break"). (A) `Conduit.find_contracted_spell` walks the Book's live `_contracted_spells` keys, which a peer's
link or sever writes under the Book lock, and raised "dictionary changed size during iteration" (proven, ticket
Note 2). (B) `Spellbook.inspect_spell` walks the frame's live `_conduits`, which root registration writes under the
frame lock, and answered None for a registered spell (proven, Note 2). (D) `Spellbook.inspect_spell` holds its Book
lock, and `Conduit.inspect_spell` the conduit lock, through `Aether._check_for_spell`, which takes frame locks, while
frame teardown takes frame -> conduit -> Book: a hang against a racing frame teardown (source, Note 4). (C) Two
simultaneous `cleanup_spell` calls of one spell both pass the locked decision and both run the disposal (source,
Note 3). (F) The 0.2.8231 comment in `_dispose_spell` claiming the spell lock is never taken under the Book lock is
wrong. Ticket: tickets/tasks/2026-10-11_close_lock_residuals_and_evaluate_mediator_admission_task.md.

## Non-goals
- No change to the meld path, to what any operation returns on a quiet world, or to any public signature.
- No new lock and no new lock-order edge; the spell lock is not held across a disposal (Note 3).
- Left as is, recorded: a direct `Spell.cleanup()` of a live owned spell holds the spell lock into
  `cleanup_and_remove_spell` (spell -> Book) against Book teardown's Book -> spell (Note 4, E); the index-move window
  of cleanup_spell (Note 1); the other 0.2.8230 snapshots.

## Changed components
- Conduit Runtime: `find_contracted_spell` and `inspect_spell` take no conduit lock; `find_contracted_spell` walks a
  one-call copy of the Book's contracted peer ids; `cleanup_spell` documents the new refusal.
- Spellbook Core: `inspect_spell` holds the Book lock only for its own Book's spells and walks a one-call copy of the
  frame's conduit map; `_dispose_spell` marks the spell id as being disposed in `_disposing_spell_ids` under the
  Book lock its decision holds, refuses a second disposal while the mark stands, and clears it when it finishes.

## Invariants
1. A walk of a map its writers change under a lock the walker does not hold iterates a one-call copy (`list(...)`),
   exact under concurrent writers on 3.14t: the Book's contracted peer ids in `find_contracted_spell`, the frame's
   conduit map in `inspect_spell`.
2. `inspect_spell` (Book and Conduit) holds no Book or conduit lock while it calls into the Aether or a frame.
3. At most one `cleanup_spell` of a spell runs its disposal: the id enters `_disposing_spell_ids` in the same
   Book-locked section as the ownership decision and leaves it, under the Book lock, when that disposal ends (finished
   or failed); a call that finds it there raises RuntimeError "cleanup_spell: spell <id> is already being disposed by
   another call." before touching the spell.
4. Lock orders are unchanged: nothing here nests a lock that was not nested before; two nestings are removed
   (Book -> frame and conduit -> Book -> frame in inspect_spell; conduit -> spell and conduit -> SpellIndex in
   find_contracted_spell).

## Interface deltas
- New internal field `Spellbook._disposing_spell_ids: set[str]`, guarded by the Book lock, deleted at Book cleanup.
- Public behaviour: a second simultaneous `Spellbook.cleanup_spell` / `Conduit.cleanup_spell` of one spell raises the
  new RuntimeError; `find_contracted_spell` and `inspect_spell` no longer fail or answer None because a peer links or
  severs or a root registers in the frame. No signature changes.

## Migration order
Patch docs -> tests (red on 0.2.8231) -> src (scratch) -> full tree -> component docs -> architecture doc and indexes
-> graph -> notch 0.2.8232 and release note -> assets and llm_support last.

## Rollback
Revert conduit.py and spellbook.py and remove the new tests; no data, cache or record format change.

## Coverage matrix
| invariant | test |
| --- | --- |
| 1 (A) | a peer links to the owner while find_contracted_spell is between two peers: the lookup returns, no RuntimeError |
| 1 (B) | a root is registered in the frame while inspect_spell walks another Book: the provider's id is still returned |
| 2 (D) | `Aether._check_for_spell` called from inspect_spell (Book and Conduit) finds neither lock held by the caller |
| 3 (C) | second cleanup_spell while the first is parked mid-disposal (active and inactive member) -> the new RuntimeError; the first completes; one destroy emitted |
