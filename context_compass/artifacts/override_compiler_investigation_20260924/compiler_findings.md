# Many-only override compiler diagnosis

Owner: updater_1. Lead: updater_0. Date: 2026-09-24.
Task: tickets/tasks/2026-09-24_investigate_override_compiler_planning_task.md.

Follow-on result: the isolated emitter experiment is now measured and independently reviewed.
See artifacts/override_emission_prototype_20260924/findings.md and the lead's joint_proposal.md.
The source diagnosis below explains that experiment; production implementation remains a later decision.

## Finding

The owner's default-plan-plus-adjustments direction fits the source. Phase 10 already builds both
variants from the same ordered occurrence model, but only the normal variant retains the fast call
layout. Phase 11 specializes overrides while losing exact argument identity before emission. The
result is a larger execution path across the entire graph, including steps unaffected by overrides.

This is not evidence of phases 7-11 rerunning on every call. The existing finalizer caches executors
by plan signature, exact socket shape and positional arity. Values are supplied afresh on each call.

## Phase responsibilities and divergence

| Phase | Existing responsibility | Finding relevant to performance |
| --- | --- | --- |
| 7 | Change-control/revalidation wiring | No measured evidence this phase causes the warm gap. |
| 8 | Occurrence and graph analysis | Occurrence identity remains available downstream. |
| 9 | Model/injection/runtime processing | Both variants start from the same model. |
| 10 | Many-only plan builder | Ordered steps are common; fast callable/arity/dependency arrays are normal-only. |
| 11 | Creation emission and hydration | Overrides emit all steps using dictionary results and runtime argument selection. |

Source:
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_7.py:52-265
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:76-123
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_9.py:62-91
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_10.py:74-112
- src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:79-127
- src/melder/aether/spellbook/spell_compiler/codegen_planner/data/many_only_codegen_plan.py:977-1362

## Actual emitted work

The captured shallow normal executor invokes prebound targets using local results:

```python
v0 = t0()
v1 = t1()
v2 = t2(v0, v1)
```

The captured root-one override executor still invokes all three constructors. For every step it
loads a plan row and Spell, selects a creations store and writes an instance_results entry. The
root compares socket.param_name against a and b, assembles kwargs, then invokes
plan_step.spell.spell(**kwargs). Creation-store selection is emitted even where disposal is statically
False and there is no registration. The root-all override repeats this work despite using neither leaf.

Exact captured source:
- 000_shallow_setup.py:1-35
- 002_shallow_root_one_reused.py:1-110
- 003_shallow_root_all_reused.py:1-119

The nine captured compiler inputs include shallow and diamond normal, baseline and targeted shapes.
Source is recorded at the existing code-cache boundary, which delegates unchanged. This is actual
runtime-generated code, not a hand-written reconstruction. Captured files are evidence snapshots.

| Graph | Normal constructor calls | One supplied root input | All supplied root inputs | Original override |
| --- | ---: | ---: | ---: | ---: |
| shallow | 3 | 3 | 3 | 3 |
| diamond | 5 | 5 | 5 | 5 |

Counts are from one warmed profiled call per case. The diagnostic verifies supplied identities and
expected constructor counts. No elapsed profiler time is used as a performance result. capture.json
records CPython 3.14.7 free-threaded, GIL disabled and no runtime source changes during capture.
The prior unified performance task remains the source of the 20-25% graph-throughput measurements.

## Exact socket information is lost before emission

ManyOnlyFinalizeCreationContextStep builds a socket shape containing node ID, parameter path ID,
parameter name and kind. Its per-shape specialization therefore already knows which parameter is
changed. _compile_override_executor_from_plan_rows passes only targeted Spell IDs, per-Spell counts
and per-step counts to emit_overrides_codegen_creation_executor_shape_source. The emitted code must
recover parameter identity through runtime SocketRef property reads and comparisons.

The many-only manifest hydrator deliberately reuses this finalizer runtime. Unlike generalized
hydration, there is no separate many-only manifest targeting implementation to fix in parallel.

Source:
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:243-469
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py:572-828
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:231-335
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py:615-859
- src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:208-349

## Recommended first tranche

Run an experiment using the existing ordered many-only plan plus an exact socket substitution map.
Keep the same constructor calls and order. Lower unchanged arguments from the normal call layout;
lower changed arguments from per-call override values. Prebind callable targets, retain results in
local variables, and omit unused creation-store selection where disposal is statically absent.
This tests the structural cause without mixing in gains from doing fewer constructions.

For shallow root-one input the proposed call body would be equivalent to:

```python
v0 = t0()
v1 = t1()
v2 = t2(a=supplied_a, b=v1)
```

Keep error translation around each call. These lines illustrate the proposed lowering subsequently
tested by the follow-on experiment. Keep ordinary no-override execution as the comparison control.
Initially specialize disposal-free many-only steps with known argument layouts and named socket
overrides. Complex signatures, collections, contract payloads and positional-input cases keep their
existing execution until separately qualified. The existing normal planner's eligibility checks
already reject CALLN, collection and unsuitable positional layouts; do not guess from dependency count.

Use the existing experiment for shallow/wide/diamond/deep, fresh/reused payloads, root-one/root-all,
exact nested and broadcast keys. Measure public calls and executor-only calls separately; retain
constructor counts, warm/cold preparation and repeated alternating-shape/value checks. Coordinate
timing with the lead. No claimed improvement until this experiment provides measurements.

Mandatory equal-count control: alternate a-only and b-only overrides with changing values. The
many-only source cache already keys exact socket shape. The lead found generalized source/factory
caching keyed more coarsely by targeted Spell IDs and counts; extending static operand placement there
must extend that cache identity too. Do not generalize the many-only cache conclusion across families.

The same distinction matters within a graph: _build_shape_source_step_metadata sets targeted presence
from Spell ID even when it has an exact per-occurrence target count. A repeated Spell's untouched
occurrence can therefore enter override assembly with count zero, emitting membership checks against
the empty override map. Select the unchanged-step path from exact local operand changes. Add a nested
selector control where the same Spell occurs on another untouched branch.
Source: many_only_overrides_codegen_creation_compiler.py:615-754, 976-1328 and 1790-1933.

## Proposed production seams after the experiment and design decision

Paths below are candidates for review, not changes made by this investigation.

| File under src/melder/aether/spellbook/spell_compiler/ | Symbols and responsibility |
| --- | --- |
| codegen_planner/data/many_only_codegen_plan.py | ManyOnlyCodegenPlanBuilder._build_no_overrides_plan / _build_overrides_plan: share default call-layout derivation while retaining override occurrence metadata. |
| codegen_creation_system/strategies/many_only/steps/many_only_finalize_creation_context_step.py | _compile_override_executor_from_plan_rows / _get_or_build_override_executor_source: carry exact per-occurrence socket operands instead of counts alone. |
| codegen_creation_system/strategies/many_only/compilers/many_only_overrides_codegen_creation_compiler.py | Shape metadata/emission and namespace binding: lower static operands, prebind targets and preserve ordered construction/error handling. |
| codegen_creation_system/strategies/many_only/compilers/many_only_no_overrides_codegen_creation_compiler.py | _build_no_overrides_codegen_executor_source / _build_unrolled_call_expression: source of existing direct-call rules; factor shared lowering only where needed. |
| codegen_creation_system/strategies/many_only/many_only_codegen_creation_helpers.py | build_override_step_row: retain any selected new value-only call-layout data through schema export. |
| codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py | _hydrate_overrides_runtime: keep cold/manifest paths equivalent if new default-plan data is passed. |

A phase-11 experiment can derive operands from current rows and the existing normal manifest payload
before committing to new phase-10 fields. Production should establish one call-layout owner, rather
than copying the normal planner's CALL0-CALL8 eligibility rules into another independent implementation.
If schema changes are selected, follow existing manifest/cache invalidation; do not introduce a second
cache lifecycle. Phases 7-9 and public Conduit/Meld gates need no change for the initial experiment.

## Pruning is a separate semantic decision

The lead's runtime_constraints.md documents ten untimed lifecycle observations and 36 passing
contract tests. Discarded dependencies are constructed and disposed today; supplied references remain
external. Existing tests intentionally characterize failures within replaced branches. Consequently,
removing construction changes observable behavior, even if final root fields match.

If pruning is selected, compute remaining reachable occurrences after socket substitution. Preserve
providers still needed by other edges, and define what nested selectors beneath replaced branches mean.
Do not infer removability from Spell ID alone. The unresolved policy includes constructor side effects,
disposal, required-input errors and nested selectors under cut branches. A separate init={} surface
might deliberately choose those semantics, but a new public spelling is not required for faster
argument emission using information the compiler already has.

## Reproduction and validation

```powershell
$env:PYTHONPATH = "$PWD/src;$PWD"
& .venv_new/Scripts/python.exe context_compass/artifacts/override_compiler_investigation_20260924/capture_codegen.py
```

Source capture and eight case assertions passed; the diagnostic script also passes Ruff.
This investigation made no production edits or asset
rebuilds. Prototype speedup, full-suite validation and coverage are not measured by this diagnostic.
