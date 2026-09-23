# Task: Repair outdated spell-ID lookup in the DI benchmark directory

- Completed: 2026-09-22T19:50:34Z
- Summary: Accepted 134 spell-ID selector fixes across 23 files and three override keyword updates,
  with passing original gauntlet and scoped compatibility checks. Separate setup finding is backlogged.

## Metadata
- Task ID: TASK-2026-09-19-repair-benchmark-spell-id-lookup
- Story: none; owner-requested benchmark compatibility repair
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-20T00:59:07Z
- Updated: 2026-09-22T19:50:34Z

## Objective
Fix the supplied Melder gauntlet first, then all equivalent outdated spell-ID calls under
benchmarks/testing_other_di, preserving benchmark workloads and the current runtime API.

## Ticket Contract
- ENTRY_GATE: Owner supplied the failing gauntlet trace and authorized repairing the same class
  of error throughout this directory; the attention board routes here.
- EXECUTION_BOUNDARY: Benchmark Melder adapters/call sites, necessary compatibility checks,
  affected generated repository bundles and task evidence. Source runtime remains unchanged.
- DEPENDENCIES: Current Meld identity selection contract; existing benchmark fixtures and configuration.
- EXIT_GATE: The gauntlet and equivalent audited adapters use explicit spell_id selection for
  IDs returned by bind; focused workloads pass and current logical/type selectors remain intact.
- FAILURE_ESCALATION: Record genuinely different failures separately instead of weakening benchmark
  correctness or silently changing runtime lookup semantics.

## Scope Boundaries
- In scope: direct and aliased Melder calls passing bind-generated IDs through the wrong parameter.
- Out of scope: purge implementation, performance redesign, other DI framework behavior, releases.
- Read complete relevant adapter functions before editing. Searches/AST locate candidates; they do
  not prove a value's identity source without reading its binding and call path.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner accepts completed selector repair; distinct setup-order issue has a separate backlog task.

## Steps / Checklist
- [x] Verify current selector semantics and reproduce the initial gauntlet failure.
- [x] Fix and run the standalone Melder gauntlet first.
- [x] Audit direct/aliased calls in the named directory and read their complete adapter paths.
- [x] Apply the same bounded ID-selector correction wherever evidenced.
- [x] Run meaningful adapter/benchmark checks, refresh affected bundles and document limits.

## Deliverables
- Correct benchmark calls and retained source-backed explanation of the error.
- Executed compatibility results and an audited inventory of equivalent fixes.

## Files / Paths Impacted
- benchmarks/testing_other_di/test_melder_gauntlet.py first.
- Other Python files in benchmarks/testing_other_di with the same evidenced outdated selector use.
- ContextCompass records/artifacts and generated repository bundles where their inputs change.

## Validation
- Standalone gauntlet passes default 1000 iterations / one thread and a three-lane smoke run.
- 18 benchmark checks and nine additional adapter checks pass. The shared gauntlet separately fails
  on frozen configuration before resolution; confirmed in a fresh process and retained for follow-up.
- Codemod syntax/AST/byte-preservation, scope audit and whitespace checks pass. Source/repository
  generated assets pass freshness checks after rebuilding the affected other bundle.
- Full directory benchmark matrix and repository suite: Not run. Details in the validation artifact.

## Risks / Rollback Notes
- Some spell= calls intentionally select a class/name; do not blanket-replace all spell keywords.
- Aliased meld callables can hide the same misuse; include them in the audit.
- Preserve unrelated working-tree changes and other agents' records.

## Applicable Anti-Patterns
- [x] No runtime fallback that interprets arbitrary names as IDs.
- [x] No changed workload/assertions merely to make a benchmark pass.
- [x] No full-suite or performance claim from smoke checks.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/benchmark_spell_id_repair_20260919/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: accepted task closure; retain audit and validation evidence.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Noting Behavior
Record each completed adapter/audit unit before further edits or validation.

## Notes
- DATETIME: 2026-09-20T00:59:07Z
  TYPE: FACT
  CLAIM: The standalone gauntlet assigns Spellbook.bind results to spell_ids, then its root,
    lesser and SpellSpace calls pass those IDs through spell=. The complete standalone adapter was
    read. The owner's trace shows the ID hash used as a logical frame key and failing lookup.
  EVIDENCE:
  - benchmarks/testing_other_di/test_melder_gauntlet.py:112-142
  - benchmarks/testing_other_di/test_melder_gauntlet.py:145-288
  IMPACT: Confirm the current selector contract before correcting this adapter and equivalent calls.
  NEXT: Read the scoped Meld component and current identity dispatch, then reproduce the gauntlet.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:01:30Z
  TYPE: FACT
  CLAIM: The unchanged standalone gauntlet reproduces the exact hash-as-name KeyError. Public
    Conduit.meld treats a string passed through spell as a logical name and only spell_id enters
    the internal ID lane. The gauntlet's 21 calls all use values from its bind-result dictionary.
  EVIDENCE:
  - artifacts/benchmark_spell_id_repair_20260919/gauntlet_red.log
  - src/melder/aether/conduit/conduit.py:4075-4117
  - benchmarks/testing_other_di/test_melder_gauntlet.py:112-288
  IMPACT: Correct the benchmark callers, preserving the intentional runtime distinction and workload.
  NEXT: Replace those 21 gauntlet selectors and run its three-lane smoke configuration.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:02:21Z
  TYPE: MEASURE
  CLAIM: All 21 standalone gauntlet ID selectors now use spell_id=. The original failure
    reproduced before correction; the unchanged workload/assertions pass afterward with two
    iterations and all three lanes enabled (1 passed in 0.34s). This is compatibility evidence,
    not the default 1000-iteration performance run.
  EVIDENCE:
  - artifacts/benchmark_spell_id_repair_20260919/gauntlet_red.log
  - artifacts/benchmark_spell_id_repair_20260919/gauntlet_green.log:1-2
  IMPACT: The owner's first benchmark is repaired. Audit the remaining named directory next.
  NEXT: Inventory direct and aliased calls, then read each affected adapter's binding-to-resolution unit.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:03:45Z
  TYPE: FACT
  CLAIM: Read complete binding/resolution adapter units for real-world gauntlet, shallow/rotation,
    multithreading, overrides, and CodegenBenchmarkSession. Each candidate uses bind-generated IDs.
    The override adapter and codegen session also use the obsolete public spell_override keyword;
    current Conduit/SpellSpace facades accept override and translate it internally.
  EVIDENCE:
  - benchmarks/testing_other_di/test_real_world_gauntlet.py:945-1146
  - benchmarks/testing_other_di/test_shallow_all.py:1169-1273
  - benchmarks/testing_other_di/test_shallow_all.py:1563-1675
  - benchmarks/testing_other_di/test_multithreading_di.py:451-535
  - benchmarks/testing_other_di/test_overrides_all.py:545-599
  - benchmarks/testing_other_di/run_codegen_benchmark_deltas.py:154-313
  - src/melder/aether/conduit/conduit.py:4075-4117
  IMPACT: Correct these caller keywords only; keep payloads, graph declarations and assertions intact.
  NEXT: Finish reading remaining profiling/basic/deep adapter units before the bounded mechanical sweep.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:07:10Z
  TYPE: DECISION
  CLAIM: Owner explicitly requested a safe codemod. All remaining inventory candidates were read
    through their complete call units and binding sources: they pass bind-result IDs or forwarded
    ID arguments. The patch will match recorded file/line/callee/expression, edit keyword bytes only,
    parse the result and require exact AST equality apart from the approved keyword replacements.
    Internal fake-door positional calls are outside the inventory and remain untouched.
  EVIDENCE:
  - artifacts/benchmark_spell_id_repair_20260919/call_inventory.json
  - benchmarks/testing_other_di/test_conduit_integration_perf_deep_graphs.py:56-512
  - benchmarks/testing_other_di/test_di_perf_overhead_suite.py:262-337
  - benchmarks/testing_other_di/profile_scope_cycle_contention.py:134-262
  - benchmarks/testing_other_di/test_family_lane_harness.py:207-362
  IMPACT: This is a bounded compatibility correction, not an AST rewrite or runtime API change.
  NEXT: Run the codemod dry run and apply the verified plan, then execute focused benchmark checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:09:54Z
  TYPE: MEASURE
  CLAIM: Safe codemod applied 113 additional ID selectors and three public override keyword
    corrections across 22 files. Together with the first gauntlet repair this is 134 ID selectors
    across 23 files. Every planned edit parsed and matched the expected AST with all other bytes
    preserved. A full directory scan finds no remaining meld(spell=...) calls. The standalone
    gauntlet also passes its default 1000 iterations / one thread (1 passed in 1.10s).
  EVIDENCE:
  - artifacts/benchmark_spell_id_repair_20260919/codemod_applied.json
  - artifacts/benchmark_spell_id_repair_20260919/gauntlet_default.log:1-2
  IMPACT: The requested class of selector error is patched; benchmark workloads/assertions are unchanged.
  NEXT: Finish focused scope/override checks and refresh the affected other repository bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-20T01:15:40Z
  TYPE: MEASURE
  CLAIM: Selector repair is complete. Default standalone gauntlet, 18 scoped benchmark tests
    and nine additional adapters pass. Directory AST audits and generated source/repository
    checks pass. The shared gauntlet fails independently at its scheduler-worker configuration
    mutation after configure_aether_frame; fresh-process isolation confirms this before any meld.
  EVIDENCE:
  - artifacts/benchmark_spell_id_repair_20260919/validation.md:1-53
  - artifacts/benchmark_spell_id_repair_20260919/benchmark_compat.log:1-2
  - artifacts/benchmark_spell_id_repair_20260919/shared_gauntlet_isolated.log:1-8
  IMPACT: Requested keyword migration is review-ready; the distinct setup-order issue remains explicit.
  NEXT: Owner reviews the patch; investigate shared-gauntlet setup separately if requested.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed by owner instruction. The distinct setup-order finding is retained in
tickets/tasks/backlog/2026-09-22_shared_gauntlet_configuration_order_followup_task.md.
It has not been marked fixed. The selector/override correction below is the accepted completed scope.

Requested repair complete and review-ready: 134 ID selectors across 23 files, plus three obsolete
public override keywords. Safe codemod and reports are retained in the task artifact directory.
Original gauntlet passes at defaults; 18 selected benchmark checks and nine extra adapters pass.
The shared gauntlet has a separate frozen-configuration setup-order failure before meld, confirmed
in isolation and recorded in validation.md. No runtime code, workloads or assertions changed.
Affected other bundle rebuilt; source/repository asset checks pass. Purge remains a draft only.
