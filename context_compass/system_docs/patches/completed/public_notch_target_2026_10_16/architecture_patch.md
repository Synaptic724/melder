# Architecture patch: public_notch_target_2026_10_16

## Metadata
- Patch ID: public_notch_target_2026_10_16
- Status: landed as 0.2.8249 - the notch target and, on the owner's extension, `add_to_spell_index` /
  `remove_from_spell_index` by `spell_id=` with the lane's text saying spell_id; built as patched, promoted into
  src_architecture, src_components, tests_components, tests_architecture and the graph; archived with the task
- Owner: user (option A, ruled in chat 2026-10-16); melder_0 (synaptic_python_developer) (patch)
- Ticket: TASK-2026-10-16-public_notch_target_for_staged_versions
- Created: 2026-10-16T12:50:00Z
- Updated: 2026-10-16T15:54:20Z

## Objective
Make the stage -> notch -> meld loop run on public calls. `Conduit.notch_spell(spell_index=..., spell=...)` needs the
staged version's Spell object, and no public call returns a parked version's Spell: `find_spell_by_id` and
`Conduit.get_spell_by_id` answer a parked id with the index's live spell, so a notch to what they return is a silent
no-op (probe C1). The owner chose option A: "just use the private version if its inside the public call thats
reasonable". `notch_spell` takes `spell_id=` beside `spell=` - exactly one of the two - and resolves the id inside
the call through the Book's internal `_get_owned_spell`, which returns the owned version active or parked.

Resolving an id makes every version of the Book nameable, and today's notch checks nothing about its target before
it mutates: a version parked in another index of the Book is accepted and corrupts both indexes, and the active
version of another index, or another Book's version, raises RuntimeError after the index's active version was
already parked (probes C3-C5). So the call checks its target - owned by this conduit's Book, a member of the index
passed - before the transaction starts and once more inside the held window, for both forms.

Extension (owner, 2026-10-16: "yeah that makes sense sure"). `add_to_spell_index` and `remove_from_spell_index`
have the same gap: they take only a Spell object and move only a spell parked in the Book, and no public call
returns a parked spell's Spell object. They take `spell_id=` beside `spell=` too, resolved the same way. The owner
also ruled on the vocabulary: the identifier is the `spell_id` that `bind` and `bind_inactive` generate, so this
lane's messages, docstrings, tests and docs say spell_id, not "version id".

## Non-goals
- No public exact-version lookup (option B was not chosen); `find_spell_by_id` and `Conduit.get_spell_by_id` keep
  their documented live-spell answer.
- No change to the Spellbook (`_notch_spell`, `_apply_notch`, `_get_owned_spell`), to the notch transaction strategy,
  to the post-window fan-out (`_deactivate_borrowed_spell`, `_emit_index_notch`) or to any meld path.
  spellbook.py is released to melder_1 (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- No new check for `add_to_spell_index` / `remove_from_spell_index` beyond resolving a `spell_id` to a spell the
  Book owns: their seams keep refusing (RuntimeError) a spell another Book owns, an active spell and, for remove, a
  spell outside the source index or its only member; for add, a target index the Book does not own. Their `spell=`
  form passes through unchanged.
- The seam's own ordering (`_apply_notch` parks the outgoing version before `_reactivate_owned_spell` checks the
  incoming one) stays as it is; a non-transactional disposal racing a notch to the same parked version can still
  leave the index without an active version. Filed for the spellbook.py holder (see Risks).
- No persisted change: no record version, cache generation or spell id moves.

## Changed components
| component | change | file owner |
| --- | --- | --- |
| Conduit (`notch_spell`; new `_resolve_notch_target`, `_owned_notch_target`) | `spell_id: Optional[str] = None` beside `spell` (now defaulting to None); exactly one of the two; the id resolved through `Spellbook._get_owned_spell`; the target checked (owned, member of the index passed) before admission and again inside the window; the docstring | melder_0 (this task) |
| README, docs/expert/governed-change.md, UX expert 17 and 26, the expert concept map | the stage -> notch -> meld loop on public calls, by id; the "notch is not driven by hand" stance superseded by the owner's ruling | melder_0 |
| system docs, conduit.py's graph descriptor, release note | the boundary list, the SpellIndex mutation sequence, an invariant, failure modes, the code map; the Conduit component entries; the tests docs | melder_0 |
| Conduit (`add_to_spell_index`, `remove_from_spell_index`; shared `_check_spell_argument`, new `_owned_spell_by_id`) | `spell_id: Optional[str] = None` beside `spell` (now defaulting to None); exactly one of the two; a `spell_id` resolved through `Spellbook._get_owned_spell`, an id the Book does not own refused before the transaction; the docstrings say the conduit admits the transaction and list the seams' refusals (extension) | melder_0 (this task) |

## Invariants
1. Exactly one target: `spell` or `spell_id`. Both given, or neither, raises ValueError; a `spell_id` that is not a
   str, or a str passed as `spell`, raises TypeError. Nothing is started.
2. The target is a version this conduit's Book owns - `spell_id` resolves through `_get_owned_spell`; a `spell` must
   be the very object `_get_owned_spell(spell.spell_id)` returns - and it belongs to the index passed
   (`target.spell_index is spell_index`). Otherwise ValueError naming the version and the remedy.
3. Checked twice: before the transaction (a refusal starts nothing - no seal, no gate freeze) and right after
   admission, inside the held window, where the notch seals the Book and its conduit EXCLUSIVE, so no other index
   operation (add, remove, notch, transfer) can move the target between that check and the switch. A refusal there
   ends the transaction as failed before the seam runs, so nothing is mutated.
4. Valid calls behave exactly as before: the same transaction metadata (the target's `spell_id` and `_key`), the
   same seam call, the same fan-out, the same return value (the now-active Spell). A notch to the index's active
   version stays a no-op with no fan-out.
5. No new lock and no new lock edge: `_get_owned_spell` takes the Book lock alone and releases it; the identity
   checks read without a lock. Nothing on a meld path changes.
6. `add_to_spell_index` and `remove_from_spell_index` take exactly one of `spell` and `spell_id`, with invariant
   1's rules and texts worded for their verb (one shared argument check). A `spell_id` resolves through
   `_get_owned_spell`; one the Book does not own is a ValueError before the transaction, so nothing is started.
   The resolved spell is what the metadata, the seam and the index-link fan-out read; the seams' own refusals and
   everything after resolution are unchanged, as is every call made with `spell=`.
7. One word for the identifier: messages, docstrings, tests and docs of this lane say `spell_id`. The notch
   refusals read "spell_id '<id>' ..." where they read "version '<id>' ...".

## Interface deltas
- Public: `Conduit.notch_spell(*, spell_index, spell=None, spell_id: Optional[str] = None, change_reason=...)`.
  Every argument stays keyword-only, so every existing call keeps working. New refusals: ValueError (both, neither,
  not owned, another index's version) and TypeError (a non-str `spell_id`, a str `spell`). Calls that corrupted the
  Book or raised RuntimeError half-way (C3-C5) now raise ValueError up front.
- Internal: `Conduit._resolve_notch_target` (the argument checks) and `Conduit._owned_notch_target` (the
  resolution and both target checks, in one place; planned as `_refuse_foreign_notch_target`).
- Extension: `Conduit.add_to_spell_index(*, spell=None, spell_id: Optional[str] = None, target_index)` and
  `Conduit.remove_from_spell_index(*, spell=None, spell_id: Optional[str] = None, source_index)`; every argument
  stays keyword-only. New refusals: ValueError (both, neither, a `spell_id` the Book does not own) and TypeError
  (a non-str `spell_id`, a str `spell`). Internal: `Conduit._check_spell_argument` (the argument checks, shared
  with `_resolve_notch_target`) and `Conduit._owned_spell_by_id`. The notch messages change wording only
  (invariant 7).
- Persisted: none.

## Migration order
This patch -> the mapping note in the ticket -> red tests (unit: argument and target checks against a stubbed
Book, nothing started on a refusal, the id resolved and passed on; integration: the loop by id after and before
conjure, the revert, the no-op, the C3-C5 refusals with both indexes intact) -> the conduit.py change -> green with
the GIL off and on -> the README-loop probe and the today-probe rerun -> docs (README, governed-change, UX expert 17
and 26, the concept map) -> system docs with their indexes, the graph descriptor re-extracted and the graph
assembled -> release note -> notch -> closure -> rebuild last.
Extension, before the closure: this amendment and the index-move component patch -> the mapping note -> red
tests (unit: the argument checks and the id resolution of both verbs against a stubbed Book, nothing started on a
refusal; integration: add and remove by spell_id in a real dynamic world, the refusals with the indexes intact)
-> the conduit.py change (the shared argument check, the two verbs, their docstrings, the notch wording) -> green
with the GIL off and on, the index-move suites unchanged -> the spell_id wording in the lane's docs -> system docs,
graph, release note -> archive -> closure -> rebuild last. The notch stays 0.2.8249: one landing.

## Rollback
Revert the conduit.py hunk, its tests and the docs: `notch_spell` takes `spell` alone again and checks nothing.
Nothing persisted changes.

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | unit: both, neither, a non-str id and a str `spell` refused before the Book is asked and before any transaction |
| 2 | unit: an unknown id, a version of another index (by id and by object), a Spell the Book does not own - each refused with nothing started; integration: C3, C4 and C5 refused with both indexes and their melds intact |
| 3 | unit: a target moved out of the index between the first check and admission is refused inside the window, the transaction ended as failed and the seam never called |
| 4 | integration: notch by id promotes a version staged after conjure and one staged before it, meld builds it, notch back by id restores the first; a notch to the active version is a no-op; the existing notch, index-link and crystallizer suites unchanged and green |
| 5 | review of the touched lines; the conduit, spellbook and crystallizer suites in both GIL modes |
| 6 | unit: both, neither, a non-str spell_id and a str `spell` refused for each verb before the Book is asked and before any transaction; an unknown spell_id refused with nothing started; a spell_id resolved through `_get_owned_spell` reaches the metadata and the seam; `spell=` passed through; integration: add and remove by spell_id move a parked spell, an active spell_id is refused by the seam with the indexes intact, the existing index-move suites unchanged |
| 7 | the notch unit and integration tests assert the reworded messages; a search of the lane's files for "version id" |

## Risks
- melder_1's D3 adds `_activate_borrowed_spell` after the window in `notch_spell`. This change keeps the window's
  `_notch_spell` call and the fan-out lines as they are (the resolved target is rebound to `spell`) and adds one
  re-check line inside the window's `try`, so melder_1's diff applies with a context shift; conduit.py is released at
  this task's closure.
- A misuse refused inside the window has already frozen and drained the sealed conduits' gates; the first check
  refuses every misuse not caused by a concurrent index operation, so that cost stays with the race.
- Residual (pre-existing, filed): `Conduit.cleanup_spell` is not admitted through a transaction, so a disposal of the
  target between the in-window check and the seam's Book lock still meets the seam's park-first ordering.

## Ticket coverage
- Task: TASK-2026-10-16-public_notch_target_for_staged_versions.

## Unknowns and decision requests
- Resolved 2026-10-16: the owner extended the landing to `add_to_spell_index` / `remove_from_spell_index` (the
  ticket's DECISION note) and asked for spell_id wording.

## Context / Handoff Summary
- What changed: built as patched (the second helper is named `_owned_notch_target`): `notch_spell` takes `spell_id=`
  beside `spell=` and checks its target before admission and inside the window; 16 unit and 10 integration tests
  green with the GIL off and on, the notch callers' suites unchanged; README, governed-change, UX expert 17 and 26
  and the concept map run by id; the system docs, their indexes and the graph carry it (the canonical docs also
  name the linked conduits the notch seals); the release note has its section; notched 0.2.8249.
- The extension (invariants 6-7; component_patch_conduit_index_move_target.md) is built as patched: both verbs
  take `spell_id=` through `_resolve_spell_to_move` (the shared `_check_spell_argument`, `_owned_spell_by_id`);
  16 unit and 10 integration tests green with the GIL off and on, the index-move and notch callers' suites
  unchanged; the lane's text says spell_id; the system docs, the graph and the release note carry it. Still
  0.2.8249: one landing.
- What remains: nothing in this lane; the rebuild runs last, after the task's closure. Backlog: the seam's
  park-first ordering (Risks).
- Next entrypoint: the canonical documents (src_architecture, src_components, tests_components,
  tests_architecture) and the graph.
