# Architecture patch: meld_state_gate_2026_10_15

## Metadata
- Patch ID: meld_state_gate_2026_10_15
- Status: active; written before any `src/` edit (2026-10-15)
- Owner: user (Option A approved in chat, 2026-10-15); melder_1 (synaptic_python_developer) (patch)
- Ticket: TASK-2026-10-15-make_meld_state_checks_follow_spell_state - rule 1 of its objective. Rule 2 (the meld's
  contract check) is not in this patch and waits for the owner.
- Created: 2026-10-15T21:00:00Z
- Updated: 2026-10-15T22:32:34Z

## Objective
A spell bound `resolvable=False` - an abstract base, a Protocol, a helper registered so agents can discover, inspect
and version it, whose consumers receive the value by override - owes no resolution verdict. RiskManager waits for
that verdict anyway: one such definition keeps its Book's validation flag up for the Book's life, so every meld in the
Book runs the validation gate and no warm meld takes the fast door (measured with the exclusion emulated: 22.8 ->
0.3 us per meld in an automatic world, 27.9 -> 0.9 us in a dynamic one). This patch records the declaration in the
spell-state model as a new `SpellState` flag, `non_resolvable`, written where a lineage's selected version is
registered, and has RiskManager ignore a flagged lineage's risk when it distils the Book flag.

## Non-goals
- No change to validity (`SpellValidity`), to any verdict, to the meld doors or the gate, to Nexus, records,
  MutationResearch, caches or spell ids.
- No change to how a resolvable=False version is refused: every meld door refuses it before the gate, as before.
- Not the contract check (rule 2: the per-meld SpellContract scan and the borrower-side marking).
- Not the borrowed-provider pin (a borrowed lineage holds a borrower's flag until melded there) and not the
  pre-existing ordering race between two refreshes (both recorded under Risks).

## Changed components
| component | change | file owner |
| --- | --- | --- |
| SpellState | append `non_resolvable` | melder_1 |
| SpellSystemState | `update_flags` (flags only, publishes nothing, says whether they changed), `has_flag` and `_republish_validity` | melder_1 |
| SpellSystemStates | `register_index(..., *, resolvable=None)` records the selected version's capability before it gates; `index_has_flag`; `non_resolvable_index_ids`, the flagged lineages as one immutable set | melder_1 |
| RiskManager | `_refresh_spellbook_flag` ignores flagged lineages (one subset test against the published set); `register_conduit` refreshes once after seeding | melder_1 |
| Spellbook (`bind`, `_apply_notch`) | pass `resolvable=<spell>.resolvable` to `register_index` | melder_0 (handoff) |
| TransferOfOwnership (the flip, `_rollback_spellbook_move`) | pass `resolvable=spell_obj.resolvable` | melder_0 (handoff) |
| System docs, the SpellState graph descriptor, the release note | the flag documented | melder_1 (release note shared) |

## Invariants
1. The flag is set exactly when the lineage's registered selected version is resolvable=False: `register_index` writes
   it from the capability its caller passes, and a registration without a capability keeps it only while the selected
   version is unchanged - a new state, or a changed selection, clears it.
2. Validity stays truthful: the flag changes no validity, no verdict and no other flag, and validation never clears
   it (`clear_dirty` clears only the topology flags).
3. The risk sets track exactly as today. Only the Book flag's distillation ignores a risky lineage whose state carries
   the flag; a `spell:` key, a lineage with no live state and every unflagged lineage count as today.
4. Ignoring that risk is safe: a flagged lineage's selected version is refused at every meld door before the
   flag-guarded gate, and every other lineage keeps its own risk.
5. Transitions take effect at the gated event `register_index` already publishes: a notch to a resolvable=False
   version excludes the lineage, and a notch back counts it again with the risk the sets kept. `set_validity`
   publishes only a changed validity, so when the lineage was already `gated` and the capability write changed
   the flag, `register_index` re-publishes the current validity itself (`SpellSystemState._republish_validity`):
   every bucket holding the lineage refreshes, a borrower whose copy came back by reactivation (no
   `register_spell`) included. A repeat notch is that case: at a notch commit only a member never compiled runs
   phases 1-4 (Phase 4 clears the gate), so a notch to a version compiled before leaves the lineage `gated`,
   and the notch after it publishes no gate event.
6. Locks: the flag is written under the registry lock, then the state lock (`register_index`'s existing order), and
   the registry mirrors it, under the same registry lock and before the gate publishes, into one immutable set of
   flagged lineages (`non_resolvable_index_ids`), replaced whole and never mutated. RiskManager reads that set with
   no lock at all. No new lock and no new lock-order edge.
7. Cost: no read on any meld path; one subset test of a refresh's risky keys against the published set (C-level,
   no lock, no Python work per key); conjure's seeding refreshes once instead of once per spell. The first build
   probed the registry per key (two locks, about 0.5 us a key: 0.5 ms a refresh in a Book with 1000
   definitions); the set replaced it (ticket DECISION 2026-10-15T22:12:54Z).

## Interface deltas
- Internal: `SpellState.non_resolvable`; `SpellSystemState.update_flags(*, flags_to_add=None, flags_to_remove=None)
  -> bool`, `SpellSystemState.has_flag(flag)` and `SpellSystemState._republish_validity()`;
  `SpellSystemStates.register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)` (TypeError for a
  non-bool), `SpellSystemStates.index_has_flag(index_id, flag)` and the read-only property
  `SpellSystemStates.non_resolvable_index_ids` (a frozenset) with its private writer
  `_publish_non_resolvable_membership_locked`; two private RiskManager helpers.
- Public: none. Persisted: none. No cache generation, record version or spell id moves.

## Migration order
This patch -> the mapping note -> on a scratch copy of the tree: red tests -> the four melder_1 files -> the four
call-site keywords -> green with the GIL off and on -> the probe -> the owner's handoff for the call sites -> the same
diff in the real tree -> the suites again -> system docs, graph descriptor, release note, notch -> closure -> rebuild.

## Rollback
Revert the notch's files. Nothing is persisted and no cache generation moves, so a revert restores today's
behaviour (a non-resolvable definition pins its Book's flag again).

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | unit: register_index sets, clears and keeps; the no-capability rule; TypeError; component: bind, notch both ways, transfer, a rolled-back transfer |
| 2 | unit: update_flags leaves validity, reason and dirt; clear_dirty keeps the flag; component: the definition's validity is unchanged |
| 3 | unit: the risk sets are unchanged with the flag; `spell:` keys and missing states count |
| 4 | component: a definition's meld is still refused with the flag down; an override consumer melds through the fast door; the existing non-resolvable admission tests |
| 5 | unit: a False -> True registration raises the flag at the gated event; a flag change on a lineage already gated re-publishes once and refreshes every bucket; component: notch both ways, and a notch back with an index-linked borrower |
| 6 | review of every touched lock site; a multithreaded component test of melds racing notches |
| 7 | the probe (us per meld, conjure, late binds with 0 to 1000 definitions, refresh cost) before and after; unit: register_conduit refreshes once |
| 6, 7 | unit: the published set follows every registration path, unregister and cleanup, is replaced rather than mutated and agrees with each flag; component: every flag check asserts that agreement |

## Risks
- Pre-existing, not changed: a refresh computes the flag under the manager lock and sets it outside, so two concurrent
  refreshes can land out of order. The subset test runs in that window and adds no lock and little time; the race
  class is unchanged.
- Recorded behaviour change: a Book whose flag was held up only by non-resolvable definitions stops running the gate's
  per-meld contract scan and behaves like the same Book without them. Borrower Books stay pinned by their borrowed
  providers (probe part 2), so contract consumers there keep today's behaviour; rule 2 owns the rest.

## Ticket coverage
- Task: TASK-2026-10-15-make_meld_state_checks_follow_spell_state (standalone).

## Unknowns and decision requests
- DECISION_REQUEST (owner): the four call-site keywords sit in melder_0's files (spellbook.py, and
  transfer_of_ownership.py inside its S6 lane), and five test doubles in melder_0's test lanes mirror the old
  signature (component_patch_registration_call_sites.md); the handoff goes through the owner.

## Context / Handoff Summary
- What changed: the patch is written; nothing in `src/` yet. Amended 2026-10-15T21:20:19Z: invariant 5 re-publishes when
  the gate was already closed (found while writing the risk tests).
- Amended 2026-10-15T22:12:54Z: RiskManager's exclusion reads the registry's published set of flagged lineages
  (invariants 6-7) after the probe showed the per-key registry probe growing with the definition count.
- What remains: the handoff, the landing (the scratch tree is built and validated).
- Next entrypoint: component_patch_spell_state_model.md.
