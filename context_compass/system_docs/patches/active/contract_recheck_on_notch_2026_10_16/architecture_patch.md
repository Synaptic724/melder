# Architecture patch: contract_recheck_on_notch_2026_10_16

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Status: active; written before any `src/` edit (2026-10-16); waiting for the owner's approval and decisions
- Owner: user (the story settled in chat, 2026-10-16); melder_1 (synaptic_python_developer) (patch)
- Ticket: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes - rule 2 of the owner's 2026-10-15
  direction (rule 1 landed as 0.2.8247 in TASK-2026-10-15-make_meld_state_checks_follow_spell_state).
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Objective
A SpellContract consumer - a spell with a `SpellContract(...)` default, built from a provider its Book borrows from
a linked conduit - is checked on every gated meld today. `Meld._ensure_lineage_resolvable` calls
`_check_contracts_and_force_revalidation`, which reads the consumer's signature, looks each contract key up in the
Book's active contracted maps and gates the conduit verdict, so phases 5-11 rerun on every such meld: 1470-1650 us a
warm meld against 1.8-2.0 us without it (probe, both GIL modes). That scan is also the only thing that makes a
consumer follow its lender's notch: no path that changes a borrower Book's active contracted copy marks the consumers
of that copy; removed alone, the consumer keeps getting the old version.

The owner's rule (2026-10-16): a satisfied contract needs no per-meld check; a change of the provider a consumer
resolves - a notch above all, because a notched version's `__init__` may differ - marks that consumer for a recheck;
its next meld re-validates the contract and rebuilds against the version now active, or fails with the error a first
meld would give; objects already built keep their provider (mark only).

This patch: (1) the borrower Book's five contracted-map mutators mark the consumers of the changed copy's key
`gated` + `contract_unvalidated` through the existing `SpellSystemStates.mark_contract_dependents_dirty`; (2) the
meld's per-meld scan is removed, so the gate's structural branch is the recheck; (3) on the owner's decisions, a lost
provider is named in the meld's error (D1) and a notch back reactivates a parked version-anchored copy (D3).

## Non-goals
- No change to the compiler's contract handling (Phase 3 sockets and the contract index, Phase 4's presence check,
  Phases 8-9), to `SpellValidity` or `SpellState`, to the gate's two branches, to the meld doors, to RiskManager, to
  records, caches, spell ids or MutationResearch.
- Mark only: nothing is disposed, extracted or rebuilt when a provider changes. Grant, uncontract, sever and
  remove-all keep the extraction `ConduitWard._invalidate_contract_consumers` already does.
- Not the provider's own dependencies: a notch of something the provider resolves does not reach the consumer, as
  it does not reach a consumer of a dependency inside one Book (a pre-existing defect; D2).
- Not a lent consumer's Book-local provider loss (a consumer lent to a second Book whose own link to the provider
  goes away): pre-existing, and the scan never closed it (Risks; D4).
- No new lock, no new state, no new read on any meld path.

## Changed components
| component | change | file owner |
| --- | --- | --- |
| Spellbook: `_add_contracted_spell`, `_deactivate_contracted_spell`, `_reactivate_contracted_spell`, `_remove_contracted_spell` (active branch), `_clear_contracted_spells_for_conduit`; new `_mark_contract_dependents_dirty` | after the Book lock, when conjured, mark the Book's consumers of the changed active copy's key | melder_0 (handoff) |
| Meld: `_ensure_lineage_resolvable` | the per-meld scan removed with its two helpers (`_check_contracts_and_force_revalidation`, `_iter_spell_contract_defaults`) and their imports; docstrings | melder_1 |
| SpellbookValidationError (D1, option B) | a spell with no error but a gating Phase-4 warning shows that warning as its reason | melder_1 |
| ContractProviderPresenceStrategy (D1, option B) | the SPELL_CONTRACT_MISSING_PROVIDER message gains its remedy | melder_1 |
| Conduit: `notch_spell`, new `_activate_borrowed_spell` (D3) | after the notch window, reactivate every linked peer's parked copy of the incoming version | melder_1 |
| ConduitWard: `_add_spell_to_contract` docstring | says what a version-anchored grant does on a notch | melder_1 |
| tests; system docs, graph descriptors, release note | the scan's unit tests replaced; marking, recheck, report and reactivation tests; docs | melder_1 (after S8 lands) |

## Invariants
1. Marking. Every change of a conjured Book's active contracted copy - added, parked, reactivated, removed, cleared -
   marks the Book's consumers of that copy's key `gated` + `contract_unvalidated` (not transitively dirty), after
   the map change is published and after the Book lock is released. A change of a parked copy only
   (`_add_inactive_contracted_spell`, the parked branch of `_remove_contracted_spell`) marks nothing: no consumer
   resolves a parked copy. Before conjure nothing is marked: conjure runs phases 1-4 for every spell.
2. Coverage. Every path that changes an active contracted copy ends in those five mutators: a grant and its
   dependency copies, an index link and its member copies, a lender's notch on every linked peer
   (`Conduit._deactivate_borrowed_spell`) and on index-link receivers (`ConduitWard._emit_index_notch`), an index
   member's removal and an index destroy (`_uncontract_member_spell`), an uncontract, a remove-all, a root's
   dependency fallout (`_remove_root_from_contracts`) and an ownership transfer (it drives the ward's grant and
   uncontract verbs). A sever pops whole buckets (`_detach_link_contract`) and already marks every consumer on both
   sides (`_invalidate_contract_consumers`).
3. Mark only. The mark changes state; it builds, disposes and extracts nothing. Objects already built keep their
   provider; the next build of a consumer object uses the version active at that meld.
4. Recheck. A marked consumer's lineage is `gated`, so the event raises the Book flag in every bucket holding it and
   the consumer's next meld enters the gate: phases 1-4 rerun (Phase 4's presence check); a missing provider leaves
   the lineage `gated` and the meld raises the first meld's SpellbookValidationError; a present one makes it `valid`,
   the conduit verdict is gated (`structure_changed`) and phases 5-11 rebuild against the version now active. The
   CreationContext is per spell, so one rebuild serves every conduit that melds the lineage.
5. No per-meld contract work. A meld whose lineage and conduit verdict are `valid` reads no signature, looks nothing
   up and forces no rebuild, contract consumer or not.
6. One key. The mark uses the copy's key (`Spell._key`, the same as `Spellbook._make_spell_key`), the normalization
   of `SpellContract.canonical_key` that Phase 3's contract index records.
7. Locks. The mark runs after the mutator releases the Book lock: registry lock -> state lock (released before the
   callback) -> RiskManager lock -> the Book flag's plain attribute write. It adds edges only into the registry -
   from the owner's ward lock where `_emit_index_notch`, `_emit_index_destroy` and `_emit_index_member_removed` call
   the receiver's mutators, and from a contract lock in `_remove_root_from_contracts` - and nothing under the
   registry, state or RiskManager lock takes a ward, contract, conduit or Book lock, so no cycle.
8. Cost. One registry call per active-copy change (cold path). A warm meld of a contract consumer goes from about
   1.5 ms to about 2 us; the first meld after a change pays one structural and one 5-11 pass, as today's every meld.
9. Errors. Every path keeps its error type except a meld whose provider is gone: it raises the first meld's
   SpellbookValidationError instead of the scan's MeldExecutionError (both RuntimeError). D1 decides its message.

## Interface deltas
- Removed (private): `Meld._check_contracts_and_force_revalidation`, `Meld._iter_spell_contract_defaults`.
- Added (private): `Spellbook._mark_contract_dependents_dirty(contract_keys)`; with D3,
  `Conduit._activate_borrowed_spell(spell_id)`. With D1 option B, a class constant beside `INTERNAL_CODES`:
  `SpellbookValidationError.GATING_WARNING_CODES`.
- Public: no signature changes. Behaviour: a consumer follows a lender's notch with one rebuild instead of a rebuild
  per meld; a meld whose provider is gone raises SpellbookValidationError (release note, **Breaking** for code that
  catches MeldExecutionError there); with D1 option B the message names the parameter and the contract key; with D3
  a version-anchored borrower gets its copy back when a notch back makes its version active again.
- Persisted: none. No cache generation, record version or spell id moves.

## Migration order
This patch -> the owner's approval and decisions -> the mapping note in the ticket -> melder_0's S8 lands (0.2.8248)
-> on a scratch copy of the tree: red tests -> the melder_1 files (meld.py; with D1-B the error and the strategy;
with D3 conduit.py and the ward docstring) -> the five mutators (spellbook.py, after melder_0's handoff) -> green
with the GIL off and on -> the probes before and after -> the same diff in the real tree -> the suites again ->
system docs, graph descriptors, release note, notch (above S8's) -> closure -> rebuild.
The marking and the scan's removal land in one notch: the scan alone is what makes a consumer follow today.

## Rollback
Revert the notch's files. Nothing is persisted and no cache generation moves, so a revert restores today's behaviour
(the per-meld scan; no marking).

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | unit (each mutator, real SpellSystemStates): marks the key's consumers when conjured, nothing before conjure, nothing for a parked copy; the mark runs with the Book lock free |
| 2 | component, both GIL modes: index-link notch, notch back and repeat notch; grant and notch; index destroy; member removal; uncontract; remove-all; transfer with repoint; sever (unchanged) |
| 3 | component: a unique consumer keeps its object after a notch and builds the new version after a purge; a many consumer built before keeps its provider |
| 4 | component: after a notch the consumer is `gated` + `contract_unvalidated`, its next meld reruns 1-4 and 5-11 once, warm melds after it run neither; a lost provider raises the first meld's error; a notch to a version whose `__init__` cannot be resolved raises the first meld's UnresolvedInputError; a consumer lent to a second Book follows in both with one rebuild |
| 5 | unit: a `valid` consumer's gate pass makes no lookup and gates no verdict; component: warm melds count no 5-11 pass |
| 6 | unit: a contract with a mixed-case binding name is marked by the provider copy's key |
| 7 | review of each mutator's lock span; component: melds racing notches and index destroys, GIL off |
| 8 | the probes before and after (us per warm meld; passes per change) |
| 9 | component: the lost-provider meld raises SpellbookValidationError; with D1-B its message names the contract |

## Risks
- The scan's removal without the marking breaks follow (measured 2026-10-15): the two land together.
- Grant marks twice (the mutator, then `_invalidate_contract_consumers`); the second `set_validity` finds the lineage
  `gated` and publishes nothing.
- A mark that raises (a cleaned registry while its Book is live) propagates after the map change, as the collection
  mark in `_add_contracted_spell` already does.
- Pre-existing, unchanged: structural validity is per lineage, frame-wide, while contract presence is per Book, so
  a lineage melded through two Books holds the verdict of the last Book that reran Phase 4; and a consumer lent to a
  second Book keeps building the old provider there when only that Book loses its provider - its flag is down, so
  the scan never ran there either (probe L3, L4).
- Pre-existing, unchanged without D2: a provider's dependency notch does not reach the provider's consumers.

## Ticket coverage
- Task: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (standalone).

## Unknowns and decision requests
- UNKNOWN: none in the design; each claim is a source read or a probe run recorded in the ticket.
- DECISION_REQUEST D1 (the message for a lost provider):
  - A: keep the first meld's message ("... No validation error was recorded for this spell ... 1 warning not
    shown"), which names no contract;
  - B (recommended): SpellbookValidationError shows a gating Phase-4 warning as the spell's reason when the spell
    has no error, and the warning gains a remedy - "Spell 'Consumer' parameter 'service' has no provider for its
    SpellContract (frame_key='iservice', binding_key='svc') ... [SPELL_CONTRACT_MISSING_PROVIDER]"; the type and
    the first line stay, so matchers keep passing (component_patch_validation_report.md);
  - C: keep a scan on the failure path and raise MeldExecutionError; it changes the FIRST meld's error type too, so
    not recommended.
- DECISION_REQUEST D2: keep the provider's dependencies out of rule 2 and open a separate task for the
  dependency-notch defect, which also exists inside one Book (recommended); or widen rule 2.
- DECISION_REQUEST D3: wire the notch-back reactivation the docstrings describe - `notch_spell` reactivates every
  linked peer's parked copy of the incoming version, a mirror of its deactivate fan-out - and correct the grant
  docstring (recommended; component_patch_notch_reactivation.md); or leave anchored copies parked and only correct
  the docstring.
- DECISION_REQUEST D4: the lent consumer's Book-local provider loss goes to its own task, or is accepted as is.
- DECISION_REQUEST D5: land after melder_0's S8 (0.2.8248) with melder_0's handoff of spellbook.py for the five
  mutators; the notch above S8's.

## Context / Handoff Summary
- What changed: the patch is written; nothing in `src/` yet.
- What remains: the owner's approval and decisions D1-D5, the mapping note, the handoff, the build.
- Next entrypoint: component_patch_borrower_contracted_maps.md.
