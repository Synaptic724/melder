# Architecture patch: failed_notch_refusal_2026_10_18

## Objective and non-goals
- Objective: a notch whose incoming version fails its structural check is refused with nothing moved - the owner's
  answer (a) on STORY-2026-10-17-failed_notch_keeps_switch_without_borrowers (2026-10-17: "refuse it and throw and
  move on"). Today the check runs at the transaction's commit, after the seam switched the index, and nothing can
  undo the switch: `notch_spell` raises, yet the lender selects the broken version, its borrowers keep the old one,
  and the lender cannot meld the index by address until a notch back (probe N2, on 0.2.8252 and on 0.2.8255).
- Non-goals: the seam's own refusals inside the window (TASK-2026-10-16-notch_seam_checks_incoming_before_parking);
  melds in flight during a notch's fan-out (TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout); a
  bind whose commit fails; the signature-claim stories S1 and S2, which wait for
  EPIC-2026-10-18-spell_identity_is_the_code; the change-control machinery (validator, orchestrator, session
  rollback actions), unchanged in code.

## Changed components
- Spellbook, the notch entry and seam: `Spellbook._notch_spell` runs the incoming version's structural check inside
  the held window and, when it fails, reverts the switch (`Spellbook._revert_refused_notch`, new) before it raises;
  `Spellbook._apply_notch` leaves the research journal entry to its caller, which writes it once the notch stands.
- SpellbookValidationError: an optional `preface`, one line placed before the report.
- Docstrings only: `Conduit.notch_spell` (the refusal), `ChangeControlManager._default_structural_validator` (for a
  notch the entry has run the check already) and `Spellbook._stage_spell_for_structural_phases` (stale since the
  commit validator took the notch over).

## Invariants
- A notch either stands or leaves the structure as it was. After a refusal: the index selects the version it
  selected before; that version is active and the refused one parked; the Book's four active maps, its address
  lookup and the frame claim of the refused version's key hold what they held; SpellSystemStates tracks the
  restored version, or no longer tracks an index it did not track before; Nexus publishes the restored version's
  record, or none; no research promotion is journaled; borrowers are untouched, because the fan-out never runs; the
  refused version's Phase 1-4 artifacts are reset, so a later notch checks it again.
- Not restored, by design: the restored version's creation context (the switch cleaned it) and its per-conduit
  verdicts (gated, as after any notch), so its next meld runs its structural and resolution passes once; the marks
  the switch put on dependents (mark only: each rechecks at its next meld and finds the same version); the
  Crystallizer's twins, which receive the switch and then its reversal, so the record ends on the restored version.
- The check and the reversal run on the notch thread inside the held window - the Book, the acting conduit and the
  conduits linked to it claimed EXCLUSIVE, their creation gates frozen. No lock and no lock-order edge is added; the
  phase runner and the seam take the locks they take today.
- A notch that stands runs the same steps in the same order, except that the journal entry follows the check and
  the check runs before `end_transaction` rather than inside its commit, where the validator finds the Phase-4
  result and skips.

## Interface deltas
- Public: `SpellbookValidationError(broken_spells, *, system_diagnostics=None, preface=None)`. `Conduit.notch_spell`
  still raises SpellbookValidationError for a broken incoming version; the message now starts with the refusal line,
  and nothing has moved.
- Internal: `Spellbook._revert_refused_notch(...)`; `Spellbook._apply_notch` no longer journals the promotion.

## Migration order
1. These patch docs, linked from the story; the owner's approval. 2. Claim spellbook.py, conduit.py,
spellbook_validation_error.py and change_control_manager.py from melder_0 by mailbox. 3. Red tests (the component
patches' validation expectations). 4. The code and the docstrings. 5. The suites, GIL off and on; probe N1-N3
re-run. 6. System documents with their indexes, the graph, the release note; the next free notch (0.2.8256 unless
melder_0 lands first). 7. Closure; the rebuild last.

## Rollback
- Put the journal entry back into `_apply_notch` and remove the entry's check and the reversal: the commit-time check
  and the half-made switch return. The `preface` keyword is additive and can stay.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/stories/2026-10-17_failed_notch_keeps_switch_without_borrowers_story.md |
