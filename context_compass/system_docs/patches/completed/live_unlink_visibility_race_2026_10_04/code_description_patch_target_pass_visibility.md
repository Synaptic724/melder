# Code description patch: how a Phase 9 miss reaches the visibility rule (live_unlink_visibility_race_2026_10_04)

## Control flow
1. A SpellContract consumer's meld forces its verdict to gated and runs the target pass (5-11) under its
   rebuild window and spell lock, without the Spellbook lock.
2. A concurrent sever pops the borrowed provider from the borrower's pool (two-phase sever, phase 3).
3. Phase 9: the contract processor (`_compile_contract_overrides_for_occurrence`) or the runtime processor
   (`process`) looks the provider up, misses, and raises KeyError(provider_id, message).
4. The scheduler raises PhaseExecutionError carrying it; the target pass extracts `args[0]`, records the
   visibility failure, cleans its scoped artifacts and returns; Meld reads the invalid verdict and raises
   SpellbookValidationError.

## Edge and error semantics
- The pool is read without the Spellbook lock, as every meld-time pass reads it; nothing new is locked.
- A removal that lands before Phase 8 never reaches Phase 9 (the analyzer plans the placeholder or misses
  with its own KeyError); one after Phase 9 is the next meld's to observe.
- Hydration at context build still raises RuntimeError for a spell missing at that point, outside the
  scheduler (unchanged; the churn test allows RuntimeError).

## Invariants and idempotency
- Read-only; the processors write nothing on the miss path (the model section stays as it was).

## Explicit non-goals
- Foundational phases (5-7): the forced-interleaving probe found no failure window there.
