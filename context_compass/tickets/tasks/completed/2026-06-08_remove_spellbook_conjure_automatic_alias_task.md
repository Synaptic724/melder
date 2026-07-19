Completed: 2026-06-12T11:58:04Z
Summary: Closed by user cleanup request with the last routed alias-removal
state preserved in the task for future pickup if needed.

# Task: Remove Spellbook Conjure Automatic Alias

## Metadata
- Task ID: TASK-2026-06-08-remove-spellbook-conjure-automatic-alias
- Story: none
- Epic: none
- Status: done
- Owner: codex
- Agent Name: compiler_0
- Priority: p0
- Created: 2026-06-08T17:24:58Z
- Updated: 2026-06-12T11:58:04Z

## Objective
Remove the backward-compat `automatic` alias from `Spellbook.conjure(...)` and
normalize the codebase onto the real posture contract:
- `dynamic=False` for normal/automatic posture
- `dynamic=True` for dynamic posture

## Ticket Contract
- ENTRY_GATE: the user explicitly rejected the `automatic` alias as backward-compat trash and asked for its removal first.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/nexus/nexus_frame_manager.py`
  - repo callsites under `src/` and `tests/` that still pass `automatic=...` to `Spellbook.conjure(...)`
  - `codex/context_compass/tickets/tasks/2026-06-08_remove_spellbook_conjure_automatic_alias_task.md`
  - `codex/context_compass/attention_board.md`
- EXIT_GATE:
  - `Spellbook.conjure(...)` no longer accepts `automatic`
  - internal/runtime callers use `dynamic=` or the default non-dynamic path
  - tests/docs no longer describe the `automatic` alias as public API
  - focused validation ring is green
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if any external compatibility seam still requires the alias and cannot be converted inside this repo.

## Scope Boundaries
- In scope:
  - remove `automatic` from `Spellbook.conjure(...)`
  - convert internal and test callers
  - update affected tests/docs for the new posture contract
- Out of scope:
  - broader `system_state` redesign
  - unrelated cache/runtime work

## Deliverables
- cleaned `Spellbook.conjure(...)` signature and docstring
- converted `automatic=` callsites
- focused validation proof

## Notes
- DATETIME: 2026-06-08T17:24:58Z
  TYPE: FACT
  CLAIM: The live public API still carries a backward-compat `automatic` alias
    on `Spellbook.conjure(...)`, and the body maps it mechanically onto
    `dynamic = not automatic`. There are many remaining internal/test callers
    still passing `automatic=False` or `automatic=True`, including
    `nexus_frame_manager.py` and public error/integration tests. So this is not
    just a signature cleanup; it is a repo-wide callsite normalization from the
    old alias onto the real posture contract.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3887-4005
  - src/melder/nexus/nexus_frame_manager.py:959-961
  - tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py:60-110
  - tests/experimentation/test_targeted_lesser_spellspace_meld_cycle_harness.py:189-191
  IMPACT: The safe fix boundary is remove the alias and convert every in-repo
    caller in the same slice so we do not leave dead compatibility branches or
    broken tests behind.
  NEXT: patch `Spellbook.conjure(...)`, bulk-convert the callsites, then run a
    focused conjure/public-API validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-08T17:30:54Z
  TYPE: FACT
  CLAIM: The public alias is now removed from `Spellbook.conjure(...)`. The
    signature only keeps `dynamic`, the `dynamic = not automatic` branch is
    gone, and the in-repo `Spellbook.conjure(...)` callers were normalized onto
    either `dynamic=True`, `dynamic=False`, or the default non-dynamic path.
    The remaining `automatic=` occurrences in the repo are outside this API
    surface: helper posture parameters and direct `Conduit(...)` test builders,
    not `Spellbook.conjure(...)` callsites.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3887-3997
  - src/melder/nexus/nexus_frame_manager.py:959-962
  - tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py:59-110
  - tests/unit/melder/aether/test_nexus_frame_manager.py:920-921
  - tests/unit/melder/spellbook/test_spellbook.py:4853-4865
  IMPACT: The conjure posture contract is now explicit instead of carrying a
    stale alias that inverted itself into `dynamic`. Future callsites now have
    one real selector to reason about on the hot path.
  NEXT: keep `dynamic` as the only conjure posture selector and update any
    future callers/tests against that single contract only.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-08T17:30:54Z
  TYPE: MEASURE
  CLAIM: The focused alias-removal validation ring is green. Running
    `.venv_new\\Scripts\\python.exe -m pytest -q`
    against:
    - `tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py`
    - `tests/unit/melder/aether/test_nexus_frame_manager.py`
    - `tests/unit/melder/spellbook/test_spellbook.py -k conjure`
    passed `27` tests with one existing pytest cache warning. A grep over
    `src` and `tests` found no remaining `automatic` references on the
    `Spellbook.conjure(...)` API surface.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3887-3997
  - tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py
  - tests/unit/melder/aether/test_nexus_frame_manager.py
  - tests/unit/melder/spellbook/test_spellbook.py
  IMPACT: The API cleanup is validated without reopening the cache/runtime
    lane. The remaining `automatic=` mentions are separate helper/test
    semantics and can be handled later if you want a broader posture cleanup.
  NEXT: return to the cache/runtime work with the public conjure alias removed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-08T17:53:37Z
  TYPE: FACT
  CLAIM: The full in-repo alias sweep is now done for code paths. The broken
    benchmark callsites were converted, the remaining benchmark conjure helpers
    now use `dynamic`, and the local unit-test `Conduit(...)` builders no
    longer expose an `automatic -> not dynamic` inversion shim. A final grep
    over `src`, `tests`, and `benchmarks` shows no remaining code-level
    `automatic` alias traces for the conjure/posture API surface; the only
    remaining `automatic` match is unrelated logger wording in `aether.py`.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py
  - benchmarks/testing_other_di/test_real_world_gauntlet.py
  - benchmarks/testing_other_di/test_di_perf_basic.py
  - benchmarks/testing_other_di/test_di_perf_overhead_suite.py
  - benchmarks/testing_other_di/test_melder_hotpath_profiles.py
  - benchmarks/testing_other_di/test_melder_single_meld_lock_and_check_cleaned.py
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py
  - tests/experimentation/melder_spellspace_cycle_testbench.py
  - tests/unit/melder/aether/conduit/test_conduit_transactions.py
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py
  IMPACT: The benchmark failure mode from `Spellbook.conjure(..., automatic=...)`
    is removed across the repo, not just on one public entrypoint. Future
    posture work now has one selector (`dynamic`) everywhere that matters.
  NEXT: keep `dynamic` as the only posture selector and reject any future
    reintroduction of `automatic` on conjure-related code paths.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-08T17:53:37Z
  TYPE: MEASURE
  CLAIM: The alias-removal fix covers the original benchmark regression.
    Running
    `.venv_new\\Scripts\\python.exe -m pytest -q benchmarks/testing_other_di/test_melder_gauntlet.py tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py tests/unit/melder/aether/test_nexus_frame_manager.py tests/unit/melder/spellbook/test_spellbook.py -k \"conjure or gauntlet\"`
    passed `28` tests with one existing pytest cache warning.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py
  - tests/integration/melder/spellbook/test_spellbook_integration_public_errors.py
  - tests/unit/melder/aether/test_nexus_frame_manager.py
  - tests/unit/melder/spellbook/test_spellbook.py
  IMPACT: The immediate benchmark break is resolved and the public conjure API
    cleanup remains green under the original failure surface.
  NEXT: return to the cache/runtime hotpath work without the old alias noise in
    the call graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-06-08T19:02:36Z
  TYPE: FACT
  CLAIM: The remaining alias-layer cleanup is complete. The local helper
    wrappers that still exposed `automatic` and inverted it into `dynamic`
    are now normalized too, including the conduit unit-test builders and the
    spellspace experiment bench. A final grep over `src`, `tests`, and
    `benchmarks` shows no remaining conjure/posture alias traces; the only
    remaining `automatic` hit is unrelated wording about automatic channel
    logger activation in `src/melder/aether/aether.py`.
  EVIDENCE:
  - tests/unit/melder/aether/conduit/test_conduit_transactions.py
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py
  - tests/experimentation/melder_spellspace_cycle_testbench.py
  - src/melder/aether/aether.py
  IMPACT: The old `automatic -> not dynamic` posture alias is gone from active
    code paths, helpers, benches, and the public conjure API. Future work can
    reason about one posture selector only: `dynamic`.
  NEXT: resume the cache/runtime hotpath lane without any remaining conjure
    alias translation layers in the repo.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
