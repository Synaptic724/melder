# Story: BUG-164 - Chain verification certifies reordered journal sequences as intact

## Metadata
- Story ID: STORY-2026-07-17-bug164-journal-sequence-integrity
- Epic: EPIC-2026-07-17-bugfix-crystallizer-persistence
- Status: review
- Owner: cowork
- Agent Name: helper_0
- Priority: p1
- Severity: High
- Created: 2026-07-18T14:01:22Z
- Updated: 2026-07-18T14:01:22Z

## Root Cause (verified against current source + runtime repro)
PersistenceCrystal construction (persistence_crystal.py __init__ / from_cached_item)
accepted journal_segment sequence values without checking monotonicity, uniqueness, or
the declared sequence_range. A cached item whose journal was reordered on the wire (e.g.
range [1,2] with entries ordered seq 2 then seq 1) rehydrated cleanly; the chain verifier
checks only checkpoint-level number/window adjacency, not per-entry order, so it returned
'intact'. Restore follows LIST order and thus replays the wrong chronology (audit:
persistence_profile_cache... no - persistence appendix BUG-164, evidence in the audit).

## Fix (root cause at the codec)
Validate journal integrity where both the capture path and the untrusted import path
converge - PersistenceCrystal.__init__. A non-empty window must carry strictly increasing
(hence unique) journal sequences, each within the declared [first, last]; otherwise
construction raises ValueError, so a reordered/duplicated/out-of-range crystal never
enters the ledger and can never be replayed. Empty-window markers (no entries, inverted
range) are exempt. Chosen the codec over the verifier because it also blocks the wrong
REPLAY at the source (restore does not consult the verifier), and avoids defensive-guard
duplication in the verifier.

## Scope Boundaries
- In scope: src/melder/crystallizer/persistence/persistence_crystal.py (__init__ validation)
  + tests/unit/melder/crystallizer/persistence/test_persistence_crystal_artifact.py.
- Out of scope: the verifier's structural checks (unchanged); other crystallizer bugs.

## Tasks (Implementation Checklist)
- [x] Re-verify BUG-164 against current source (codec has no order/range check).
- [x] Add strictly-increasing + in-range journal validation in PersistenceCrystal.__init__.
- [x] Confirm empty-window markers and valid captures still construct.
- [x] Add BUG-164 regressions (reorder, duplicate, out-of-range, reordered import, marker).
- [ ] User runs the persistence suite on 3.14t and accepts.

## Acceptance Criteria
- Reordered/duplicate/out-of-range journals (direct or via from_cached_item) raise ValueError;
  valid ordered journals, single entries, empty markers, and round-trips still succeed; the
  persistence suite is green on the user's 3.14t run.

## Validation / Test Plan
- Verified with the REAL PersistenceCrystal codec IN-CONTAINER (stdlib-only deps: Cleanable +
  RecordVersion) across 9 cases: valid ordered, reordered, duplicate, out-of-range high/low,
  empty marker, single entry, reordered-cached-item import (ValueError), and valid round-trip.
  All behaved as specified.
- py_compile OK. Full pytest suite Not run in-container (broader tests need the 3.14t package
  chain); the user runs it on 3.14t. Agent test-run status: real codec exercised; pytest suite Not run.

## Risks / Mitigations
- Risk: over-strict validation could reject a legitimate crystal. Mitigation: verified all
  in-repo construction sites (capture path is in-order; tests use ordered/empty journals) pass;
  markers explicitly exempt; only malformed imports are rejected.

## Applicable Anti-Patterns
- [x] Reproduced/verified before fixing (real codec runtime repro).
- [x] Root-cause at the codec, not a verifier band-aid.
- [ ] No closure before the user's suite run.

## Decision Log
- DATETIME: 2026-07-18T14:01:22Z
  TYPE: DECISION
  CLAIM: Fix BUG-164 in the codec (PersistenceCrystal.__init__) rather than the verifier, because it blocks both the false-intact verdict AND the wrong replay at the single trusted/untrusted construction choke point.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
BUG-164 fixed at the crystal codec: journal segments must be strictly increasing and in-range,
so reordered/duplicated/out-of-range imports raise instead of replaying the wrong chronology.
Verified with the real codec in-container. Status review, pending the user's 3.14t suite run.
