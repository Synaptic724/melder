# Architecture patch: live_unlink_visibility_race_2026_10_04

## Objective and non-goals
- Objective: a meld whose target-local resolution pass loses a dependency to a concurrent link sever,
  uncontract or unbind fails with the same SpellbookValidationError a meld starting a moment later gets,
  never with an internal PhaseExecutionError. Found by the hosted macOS 3.14.8 run of
  test_multithreading_live_link_unlink_and_contract_churn_cycles.
- Non-goals: no lock between resolution passes and pool writers (passes stay lock-free, per the 2026-09-26
  compiler pool-read rule); no change to the target passes' classifier, to the conduit-wide (conjure)
  passes, to the hydration errors raised at context build, or to anything on the success path.

## Changed components
- SpellCompiler Phase 9 artifact processors: `SpellOccurrenceContractProcessorStrategy` and
  `SpellRuntimeProcessorStrategy`.

## Invariants
- Every Phase 8/9 lookup that misses a spell in the live `_spell_id_pool` raises KeyError whose `args[0]`
  is the missing spell id (the analyzer and the instance processor already did, by subscript). The two
  processors keep their old text as `args[1]`.
- The target-local passes (full and deferred) keep their rule: a plan-phase PhaseExecutionError carrying
  KeyError entries becomes a visibility failure; anything else re-raises.

## Interface deltas
- None public. A meld racing a sever, uncontract or unbind of a spell it is resolving raises
  SpellbookValidationError (diagnostic `visibility_gap_dependency_filtered`) where it could raise
  PhaseExecutionError ("Occurrence spell could not be resolved from the spell lookup." or
  "SpellRuntimeProcessorStrategy could not resolve spell_id ..."). On the conjure path the same miss now
  appears inside PhaseExecutionError as a KeyError carrying the same text.

## Migration order
1. The two processors. 2. Unit tests (one updated from RuntimeError, two added). 3. Deterministic
integration regression (sever or uncontract forced before either processor). 4. System docs, graph, notch
0.2.8227, release note. 5. Assets, bundles.

## Rollback
- Restore the RuntimeError in both processors; the race then surfaces as PhaseExecutionError again.

## Ticket coverage matrix
| patch section | ticket |
| --- | --- |
| all | tickets/tasks/2026-10-04_fix_live_unlink_churn_phase_error_task.md |
