# Override performance: first measured findings

Date: 2026-09-24. Owner: updater_1.
Epic: tickets/epics/2026-09-24_override_execution_performance_epic.md.
Experiment: tests/experimentation/test_melder_creation_overrides_performance.py.

## Baseline result
The owner's approximately 20% throughput observation is reproduced for the supplied graph cases.
These are warm single-thread medians on CPython 3.14.7 free-threaded, GIL disabled, seven samples per
case, GC disabled inside timing and disk caching disabled. Runtime source fingerprints stayed stable.

| Graph | Normal us/call | Original override us/call | Override throughput / normal |
| --- | ---: | ---: | ---: |
| Shallow | 0.505 | 2.055 | 24.6% |
| Wide | 0.821 | 3.516 | 23.4% |
| Diamond | 0.619 | 2.901 | 21.3% |
| Deep | 31.983 | 156.884 | 20.4% |

The shallow/wide cases supply one direct root dependency. Diamond uses **leaf; deep uses the original
eight-edge exact path. All normal graph nodes are Existence.many. The old suite's solo existing-object
retrieval is intentionally not compared with transient construction.

Dynamic-mode original override throughput is 36.1% shallow, 30.7% wide, 30.5% diamond and 20.9% deep.
Those ratios use each graph's own dynamic normal baseline, rather than the automatic baseline.
Detailed samples and machine/source metadata are in automatic/results.json and dynamic/results.json.

## Constructor inputs and controls
- A single scalar constructor assignment measures 0.390 us normally and 0.681 us with a fresh
  {value: 13} override, or 57.3% throughput. Constructor work and resulting value are equal here.
- Reusing the graph override dictionaries makes only small differences relative to the four/fivefold
  gap. Caller-side dictionary allocation is not the main explanation in these measurements.
- Empty dict normalization takes the no-override executor after missing the initial warm lookup path.
  It retains 74-99% throughput across graph sizes.
- Empty tuple normalizes to a nonempty __args__ payload and takes override execution. Deep falls from
  31.983 us to 153.695 us even with zero supplied positional values. This isolates a large execution
  path cost without requiring nested target selection.
- Supplying all eight wide root inputs costs 9.517 us, or 8.6% of its normal throughput. More supplied
  root values do not currently turn this into a cheap direct-constructor path.
- Direct Python root-only rows are lower-bound controls with supplied dependencies. They omit Melder
  lookup, admission, lifetime and hook semantics and are not a proposed implementation's measured speed.

## Constructor-count evidence
Separate cProfile runs count fixture __init__ calls over 128 warmed public operations per case.
Profiler elapsed times are not used as throughput evidence.

| Graph | Normal | One root dependency supplied | All root dependencies supplied |
| --- | ---: | ---: | ---: |
| Shallow | 3 | 3 | 3 |
| Wide | 9 | 9 | 9 |
| Deep | 511 | 511 | 511 |

The deep call still constructs all 511 nodes when both direct root dependencies are supplied.
This is a concrete investigation target: the override executor visits/constructs descendants whose
values are replaced at the root. Counts, source fingerprints and profiler function records are in
constructor_counts.json; count_constructors.py reproduces them using the unified experiment.

## Input-semantics observation
Nonempty positional tuples for shallow/wide/diamond/deep currently raise a duplicate-argument TypeError
wrapped in MeldExecutionError, because generated dependency keywords coexist with the positional values.
The scalar positional case works. Reports list all rejected cases explicitly and assign no timing.
The experiment catches only this observed error shape; any other unexpected error still fails.

## Next investigation
Trace the generated many-only override executor's per-node construction/kwargs work. Compare:
1. Specializing simple root keyword arguments within the current override API.
2. A distinct init={} input contract with explicit root-only argument handling.

Determine when supplied roots may skip descendant construction and what that means for constructor
side effects, hooks, disposal and shared lifetimes. The current experiment covers transient graphs;
it does not establish those broader semantics. Keep nested path/broadcast behavior separately governed.
Renaming an argument without changing execution does not address the measured work.

## Validation and limits
- Contract qualification: 6 passed.
- Automatic measurement run: 7 passed in 14.58 s.
- Dynamic measurement run: 7 passed in 14.60 s.
- Ruff passed with UP045 excluded to preserve the selected role's Optional typing requirement.
- Runtime and fixture source hashes matched before/after each measured/profiling run.
- No production runtime code or init={} API was implemented. No multi-thread throughput or full-suite
  coverage claim. Initial failed positional observations remain in contracts.log for review.
