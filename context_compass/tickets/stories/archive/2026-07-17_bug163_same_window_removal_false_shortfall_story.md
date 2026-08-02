# Story: BUG-163 - Normal same-window removal produces a false restore shortfall

## Metadata
- Story ID: STORY-2026-07-17-bug163-same-window-removal-false-shortfall
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p2
- Severity: Medium
- Created: 2026-07-18T16:16:39Z
- Updated: 2026-07-18T16:16:39Z

## Root Cause (verified against current source + logic repro)
When an identity is recorded and then removed within one checkpoint window,
capture_segment_since (persistence_profile.py) keeps the emission journal entry but
captures NO payload for it (the twin is gone at seal: _resolve_twin returns None ->
continue), and it captures the removal tombstone. On restore, _fold_chain
(restore_engine.py:647-663) sees the emission entry with payload None and files a
'journal_entry_without_captured_payload' shortfall - even though the later same-window
tombstone fully explains the absence. Routine record-then-remove churn thus produces a
misleading incomplete-restore diagnostic (audit BUG-163).

## Fix (fold without anomaly when a tombstone explains it)
In _fold_chain, pre-scan each window's journal for removal entries (kinds ending in
'_removed') and record the latest removal sequence per key. When an emission entry has no
payload, suppress the shortfall IFF a same-window removal of the SAME key occurs at a later
sequence (the record-then-remove case). Genuine capture gaps - a payload-less entry with no
explaining removal - still file the shortfall, preserving the honesty guard that was added to
catch the SpellbookCrystal emission gap. Chose the restore-side 'fold without anomaly' remedy
(the audit's sanctioned alternative) because the capture side has already lost the twin and its
parent-edge by seal time.

## Scope Boundaries
- In scope: restore_engine.py _fold_chain shortfall guard + regressions.
- Out of scope: capture-side compaction; the pure-subtree case (see Residual).

## Residual / Follow-up (flagged)
- remove_spellbook_subtree journals ONE 'spellbook_removed <parent>' entry (persistence_profile.py:690),
  not per-child 'spell_removed'. A child custody emission orphaned by a subtree sweep has key X while the
  tombstone has key P (X != P), so same-key matching does NOT suppress it; that narrower subtree case still
  files a shortfall. Resolving it needs the child->spellbook parent edge, which the orphaned (payload-less)
  entry no longer carries. Flagged for owner: either journal per-child tombstones on subtree eviction, or
  carry the parent edge in the journal entry. Direct record-then-remove (the audit's repro) is fixed.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-163 against current source (capture drops payload; restore flags it).
- [x] Suppress the shortfall when a later same-window same-key tombstone explains the gap.
- [x] Preserve the honesty guard for genuine gaps (no explaining removal).
- [x] Add regressions for both the fixed case and the preserved-guard case.
- [ ] User runs the restore-engine suite on 3.14t and accepts.
- [ ] Owner decision on the subtree-sweep residual.

## Acceptance Criteria
- Record-then-remove within one window files NO journal_entry_without_captured_payload shortfall and folds
  to empty custody; a genuine payload-less entry still files one; suite green on the user's 3.14t run.

## Validation / Test Plan
- Logic verified in-container with a faithful transcription of the fixed _fold_chain shortfall core across 5
  scenarios: record-then-remove (no shortfall), genuine gap (shortfall), subtree residual (shortfall),
  remove-then-reemit gap (shortfall), normal emission (fold). All matched expectations.
- py_compile OK. Two pytest regressions added (record-then-remove -> no shortfall; orphan -> shortfall)
  using the existing _engine/_window harness. Full pytest Not run in-container (restore engine import chain
  needs 3.14t). Agent test-run status: logic verified; pytest suite Not run.

## Risks / Mitigations
- Risk: over-suppression could hide a real gap. Mitigation: suppression requires a same-key removal at a
  LATER sequence; a payload-less entry with no such removal still files a shortfall.

## Applicable Anti-Patterns
- [x] Reproduced/verified before fixing (logic repro).
- [x] Preserves the honesty guard rather than blanket-silencing shortfalls.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T16:16:39Z
  TYPE: DECISION
  CLAIM: Fold without anomaly at restore (same-key later tombstone) rather than compacting at capture, since the twin/parent edge is already gone by seal time; the pure-subtree case is a flagged residual needing per-child tombstones or parent-edge provenance.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
BUG-163 fixed: record-then-remove churn no longer files a false restore shortfall; genuine gaps still do.
Subtree-sweep supersession flagged as a narrower residual. Status review. This is the LAST bug in story 06
(BUG-158..164) - the story is now functionally complete pending the user's 3.14t suite run.
