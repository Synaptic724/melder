# Component patch: Phase 9 pool misses seen by the target-local passes (live_unlink_visibility_race_2026_10_04)

## Before / after behavior
- Before: the target-local passes turn a plan-phase failure into a visibility failure only for KeyError
  entries. The Phase 9 contract and runtime processors reported a pool miss as RuntimeError, so a meld
  that raced a sever or an uncontract (the borrowed provider popped after Phase 8 saw it) raised
  PhaseExecutionError, and after an uncontract the next meld failed in the context builder.
- After: both processors raise KeyError(spell_id, message); the pass records the visibility failure
  (invalid verdicts for its scope, `visibility_gap_dependency_filtered` diagnostics), Meld raises
  SpellbookValidationError, and the next meld re-resolves against the current pool.

## Interface deltas
- None public. Exception type of two internal miss sites: RuntimeError -> KeyError (same text in args[1]).

## State and failure deltas
- No new state; the visibility-failure writes are the existing ones.

## Dependency and ordering
- Relies on `SpellbookCreationSystem._extract_missing_dependency_ids` reading `args[0]` of each KeyError.

## Validation expectations
- Unit: both processors raise KeyError naming the id; the extractor reads the id of a two-argument KeyError.
- Integration: a sever or an uncontract forced before either processor makes the meld raise
  SpellbookValidationError (red on the old code), and the consumer melds again after the contract returns.
- The churn test and the touched tiers pass on the device VM.
