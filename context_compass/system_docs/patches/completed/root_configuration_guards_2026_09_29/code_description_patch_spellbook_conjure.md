# code_description_patch_spellbook_conjure

## Metadata
- Patch ID: root_configuration_guards_2026_09_29
- Status: active
- Owner: user (agent melder_0)
- Created: 2026-09-29T23:43:57Z
- Updated: 2026-09-30T00:19:44Z

<!-- BEGIN ENTRY: "conjure control flow" -->
## Control Flow
1. check_cleaned; start the CONJURE transaction (spellbook EXCLUSIVE; binds cannot run).
2. effective = `_effective_conjure_mode(dynamic)`: missing posture -> the flag; unfrozen posture and dynamic=True ->
   True; otherwise posture.system_state is dynamic.
3. `_refuse_recorded_conjure_after_mutable_binds(effective)`: effective and early-bind count > 0 and Crystallizer
   active -> log and raise the existing RuntimeError.
4. `_settle_or_inherit_conjure_mode(dynamic)` (unchanged) -> `_conjure_within_transaction_window(...)`, which
   re-runs step 3 on the SETTLED mode through the same helper; end the transaction in `finally`.

## Edge / Error Semantics
- The early-bind count cannot change between steps 2 and 4: binds need the spellbook INTENT the transaction excludes.
- Crystallizer activation racing a conjure is unordered, as before.
- Frame posture belongs to the frame, not the Book: another Book's conjure in the same frame can settle it between
  steps 2 and 4. A stale "automatic" prediction then lets step 3 pass, and the window's re-check on the settled
  mode refuses (with the frame settled by that other Book, not by this conjure). A stale "dynamic" prediction
  refuses a conjure the caller asked to run dynamic, which the discipline forbids anyway.

## Invariants / Idempotency
- Steps 2-3 mutate nothing; a refusal leaves the frame posture exactly as it was.

## Explicit Non-Goals
- Failures after step 4 (validation, policy strings) keep settling the frame.
<!-- END ENTRY: "conjure control flow" -->
