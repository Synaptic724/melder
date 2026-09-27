# Joint proposal: reuse normal creation instructions for overrides

Lead: updater_0. Compiler investigation: updater_1. Date: 2026-09-24.
Status: preserved emission-only evidence; structural planning selected for the next investigation.
Epic: tickets/epics/2026-09-24_override_execution_performance_epic.md.

## Owner direction after prototype review

The owner selected the deeper structural fix: supplying three of five dependencies should remove
their unnecessary construction, rather than only reduce the cost of executing the original full graph.
The measured prototype below retains every constructor. Its code/results stay frozen, and its earlier
recommendation is retained as history rather than the next isolated production change.

Read the new discover_override_execution_semantics and discover_override_occurrence_slicing tasks
under the epic for active work. Compare speed against normal creation as the primary baseline:
41.8% shallow, 53.3% wide, 41.6% diamond and 95.3% deep. The 1.64x-4.68x figures compare with old
override execution, not normal creation. The original deep benchmark replaces one leaf; the separate
root-all case supplies both root branches yet still constructs 511 objects. It demonstrates the
structural gap directly. No production override fix has been implemented.

## Measured prototype result

Seven repeated samples per variant on CPython 3.14.7 free-threaded, GIL disabled. Both variants use
the same public Meld route, target selection and constructor sequence. Only the cached generated body
changes between samples. This is a single-thread diagnostic with disk cache disabled, not a release claim.

| Original override workload | Current public call | Candidate public call | Speedup |
| --- | ---: | ---: | ---: |
| Shallow | 1.997 us | 1.219 us | 1.64x |
| Wide | 3.505 us | 1.548 us | 2.26x |
| Diamond | 2.808 us | 1.470 us | 1.91x |
| Deep | 155.738 us | 33.292 us | 4.68x |

All 19 graph cases preserve constructor order/count (3/9/5/511) and supplied identities; 64 alternating
a/b calls preserve ordinary, falsey and None values. No-override controls remain within 1% between
variants. The deep candidate reaches about 95% of normal throughput while still constructing 511 nodes.
Wide all-root input still costs 7.377 us publicly versus 1.260 us inside its executor; front-end overhead
remains relevant, especially with many override keys.

The lead independently ran ten unchanged many-only input/error/eager-branch regressions against the
candidate, including manifest hydration: ten passed. Ten executor bodies/defaults/namespaces were
verified restored. The prototype's measured and reviewed SHA256 agrees before/after:
5dea8551293b1b8cc35ee3ad2c88c6dc7644343593a6ebcf7b91d8b1907feb1e.

Evidence:
- artifacts/override_emission_prototype_20260924/results.json
- artifacts/override_emission_prototype_20260924/results.md
- artifacts/override_execution_lead_20260924/prototype_review.json
- artifacts/override_execution_lead_20260924/prototype_regressions.log

## Diagnosis

The recorded all-many graph workloads achieve about 20-25% of normal throughput with overrides.
The gap is not explained by recreating the input dictionary, nor by compiling the entire graph on
every call. Override shapes are cached, but the generated instructions remain more expensive.

The captured shallow normal executor calls three prebound constructors through local values.
Its override executor still calls all three constructors, then adds result-dictionary traffic,
keyword-dictionary assembly, socket-name comparisons and repeated metadata/store reads. The discarded
dependency also remains a real creation: the lead's disposable-resource probes confirm its cleanup.

Evidence:
- artifacts/override_execution_performance_20260924/findings.md
- artifacts/override_compiler_investigation_20260924/000_shallow_setup.py
- artifacts/override_compiler_investigation_20260924/002_shallow_root_one_reused.py
- artifacts/override_execution_lead_20260924/lifecycle_observations.json

## Earlier emission-only implementation proposal (retained)

Keep the existing override API, targeting semantics, occurrence order and creation lifecycle. Lower
eligible many-only steps to the normal emitter's prebound constructor/local-result form, with supplied
values substituted at the parameters actually targeted. Values stay per-call; code is specialized by
the stable operand layout. Do not add work to ordinary no-override execution.

This first step addresses instruction overhead independently of branch pruning. It preserves the
current missing-input failures and disposal effects, making performance and compatibility results
directly comparable to the measured baseline. Unsupported call shapes keep their existing execution
route until their equivalent lowering is verified; this is not a new public execution mode.

The peer's exact candidate symbol map is in
artifacts/override_compiler_investigation_20260924/compiler_findings.md. The key seams are
ManyOnlyCodegenPlanBuilder._build_no_overrides_plan/_build_overrides_plan, the finalizer's
_compile_override_executor_from_plan_rows, override shape metadata/emission, and normal call-expression
lowering. Any persisted field addition must pass build_override_step_row and _hydrate_overrides_runtime.
The prototype derives operands from current rows before committing to new phase-10 fields.

updater_1 delivered the artifact-only prototype in
tickets/tasks/2026-09-24_experiment_static_many_override_execution_task.md. It keeps identical
constructor order/count and initially handles disposal-free many-only named inputs. updater_0 has
read the timing harness and completed independent parity/result review. Complete argument layouts use
normal-style positional calls; incomplete layouts retain keyword calls so Python defaults still apply.
No production files are assigned for editing by that task.

## Mandatory cache constraint

The source-cache shape must encode the actual argument placement used in emitted instructions.
Many-only already has that exact socket identity; carry it through instead of dropping it to counts
before emission. Its manifest hydrator reuses the same finalizer. The separate generalized emitted-source
cache is coarser and would need refinement if that family later gains static operand substitution.
Target counts alone cannot distinguish an a-only override from a b-only override in the same root.
Keep call values out of source identity and static bindings; retain the existing atomic publication
of complete cached entries. Qualify alternating equal-count shapes, values, positional arities and
fresh/manifest-hydrated contexts. Reuse existing context invalidation rather than adding a cache plane.

The generalized family already has raw-key shape caching for non-overlapping selectors. Its overlap
path retains value-dependent conflict checks. Do not assume the entire codebase lacks shape caching,
and do not copy an optimization into this family without verifying its separate execution contract.

## Separate branch-pruning decision

If the owner chooses pruning, replace dependency edges at targeted sockets and retain only occurrences
still required by the root. A shared provider used elsewhere must remain. Specify behavior for nested
overrides below a replaced parent before changing execution. Supplying an external object does not
transfer disposal responsibility to Melder under the current contract.

Pruning intentionally removes constructors, their possible errors, and disposal of the objects that
would otherwise be generated. Existing eager-branch characterization tests must then change by
decision, not merely to make a new implementation pass. This remains part of the epic's design space,
separate from the proposed first instruction-only implementation.

## Qualification and responsibility

- updater_1 owns the many-only compiler diagnosis and baseline experiment.
- updater_0 owns runtime/lifecycle constraints, independent validation and combined design review.
- Before source edits, assign one writer per file and record the selected patch contracts in the epic.
- Reuse the 36 passing targeted contracts and the detailed matrix in runtime_constraints.md.
- Add same-count/different-parameter specialization regressions and meaningful parity checks for the
  selected emitter boundary, including changing values and concurrent callers.
- Production qualification must rerun matched performance/count checks and no-override controls.
  The measured prototype gain is evidence for the design, not a guarantee for a future implementation.
- Keep build generation outside discovery. When later authorized, run it after the final source,
  documentation and ticket changes.

## Current evidence and limits

Lead validation: 36 baseline tests, ten untimed lifecycle cases and ten candidate contract tests.
Peer measurement: 19 graph cases plus 64 alternating shape/value calls, two emitter variants and seven
repeats. A direct-keyword control is retained separately in keyword_results.json; final results use
normal-style positional calls where the entire parameter layout is supplied. Runtime/prototype source
fingerprints are stable. Original first-case and extra prototype preparation are recorded separately;
some first-case calls are already warm, and no production cold-start improvement is claimed. Extra
candidate generation totaled about 198 ms across deep specialized executors; production work must
measure first-shape cost and code size without the diagnostic's duplicated original/candidate build.

Generalized/scoped lifetimes, disposal-bearing plans, collections, contract payloads, positional input
overrides, multithread races and full-suite production compatibility are not qualified by the prototype.
No production optimization, new public API, version bump or asset rebuild occurred. The epic remains
open for a concrete production design decision; pruning remains an explicit separate behavior decision.
