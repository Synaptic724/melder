# Architecture patch: cleanup_releases_contracts_2026_10_19

Story: STORY-2026-10-17-parked_cleanup_leaves_borrower_copies (S3 of EPIC-2026-10-17-correctness_defects).
Agent: melder_0 (synaptic_python_developer). Status: active - the owner's go (chat 2026-10-19): "sure go ahead and
fix this [...] at least you can check for active contracts and then cleanup".

## Objective
Cleaning up a spell takes the version out of every contract that holds it, then disposes it - the owner's order.
Every `cleanup_spell` door (a root conduit's, a lesser conduit's, the Spellbook's own) runs it, so no borrower keeps
a record of a version its lender disposed: no entry, no borrowed id, no lender-side Detail, and no index link to an
index that went with the version. Contracts and links are structure (src_architecture, Runtime Model).

## Non-goals
- Objects anything built: a cleanup never disposes what a spell built (the owner, 2026-10-19).
- The direct `Spell.cleanup()` and the public `Spellbook.cleanup_and_remove_spell` (probe K6: a parked version is
  refused there with "Spellbook could not resolve the requested local spell."; an active sole member is disposed with
  no release): recorded for the owner, not changed here.
- Ordering `cleanup_spell` against a concurrent link or grant of the same version: the cleanup takes no transaction
  (pre-existing); a link that lands between the release and the disposal can still file the version.
- `remove_index_from_contract`: unchanged - it already removes every version the index holds, active and parked
  (probe U1); the leftover came from the cleanup.

## Changed components
- Conduit: `cleanup_spell` (conduit.py).
- Spellbook: `cleanup_spell`, `_dispose_spell` (spellbook.py).
- ConduitWard: `_emit_spell_disposed`, new; `_emit_index_destroy`'s docstring (conduit_ward.py).

## Invariants
- A version the Book disposes leaves every contract of the Book's root conduit first: the lender-side Detail (an
  index link's member Detail or a version grant), the borrower's entry, active or parked, and its borrowed id. Rule 2
  marks the borrower's contract consumers when an active entry goes (`Spellbook._remove_contracted_spell`).
- When the index goes with the version, its index links go too (the borrower's tracked index and the IndexDetail),
  after the disposal and from the Book's own report, as today.
- A refused cleanup - not owned, disposed, being disposed, or the active member of a multi-member index - touches no
  contract.
- The contracts live on the Book's root conduit, whichever conduit of its lineage, or the Book itself, is called.
- No lock-order edge: the release runs with no Book lock held, between the Book's decision and its disposal, and
  takes ward -> contract -> borrower Book, the order sever and the index emissions take.

## Interface deltas
- No public signature changes. A conjured Book's `Spellbook.cleanup_spell` goes through its root conduit's
  `cleanup_spell`. Internal: `Spellbook._dispose_spell(spell, *, release_contracts=None)`,
  `ConduitWard._emit_spell_disposed(spell_id)`.
- Visible: after a lender's cleanup the borrower holds nothing of the version (probes K1-K5, K7, U2); a borrower's
  meld of a disposed granted version fails as for a version it never held, not with AttributeError (K3); a notch to
  the class staged again completes for the borrower, which melds it (U3).

## Migration order
1. The symptom-named tests, red on 0.2.8260.
2. The three src edits with their docstrings; the tests green, the GIL off and on; probes re-run; the related
   suites and the whole tree.
3. System documents (an operational invariant, a fixed failure mode, the cleanup and code-map lines, the Conduit,
   ConduitWard and Spellbook components, the tests documents) with their indexes and the graph; the release note;
   the notch above 0.2.8260; the rebuild last.

## Rollback
- Revert the three files. No cache generation, record version or persisted shape changes.

## Ticket coverage
| requirement | step | validation |
| --- | --- | --- |
| a parked version's cleanup leaves its index links' borrowers nothing | `_emit_spell_disposed` via `cleanup_spell` | test; probes K1, U2 |
| the unlink afterwards leaves nothing | none (follows) | test; probe U2 |
| a notch to the class staged again completes for borrowers | none (follows) | test; probe U3 |
| version grants leave with their version | `_emit_spell_disposed` | tests; probes K2, K3 |
| every cleanup_spell door releases | `Spellbook.cleanup_spell` routed; root ward | tests; probes K4, K5, K7 |
| contracts first, then the disposal; a refusal touches none | `release_contracts` in `_dispose_spell` | tests |
