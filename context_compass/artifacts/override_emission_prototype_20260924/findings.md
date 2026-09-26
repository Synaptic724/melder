# Static override emission: measured prototype

Owner: updater_1. Lead: updater_0. Date: 2026-09-24.
Task: tickets/tasks/2026-09-24_experiment_static_many_override_execution_task.md.

## Result

Normal-style call layout plus exact socket substitution removes most of the measured deep-graph
override penalty without skipping a single constructor. This supports the phase-10/11 structural
diagnosis. The prototype is isolated diagnostic code; no production implementation has been changed.

Seven-repeat medians for the original benchmark override shape, through public Conduit.meld:

| Graph | Current override | Prototype override | Speedup | Prototype throughput / normal |
| --- | ---: | ---: | ---: | ---: |
| shallow | 1.997 us | 1.219 us | 1.64x | 41.8% |
| wide | 3.505 us | 1.548 us | 2.26x | 53.3% |
| diamond | 2.808 us | 1.470 us | 1.91x | 41.6% |
| deep | 155.738 us | 33.292 us | 4.68x | 95.3% |

Normal medians in the same run were 0.510, 0.825, 0.612 and 31.738 us respectively.
Their control measurements with prototype bodies selected stayed within 1% of those values.
Deep current samples ranged 153.62-161.31 us; prototype samples ranged 31.77-33.54 us.
All raw samples and other cases are in results.json and results.md.

## What changed in the experiment

The prototype consumes the actual hydrated step sequence and prefiltered SocketRefs of the existing
per-shape executor. It emits a local result for every step, prebinds constructor targets and replaces
only selected argument operands with values read from the current override map. Every constructor
is retained, including ones whose results are later replaced. Unused store lookup, result dictionaries,
parameter-name comparisons and runtime keyword dictionaries are absent from the generated body.

Complete POSITIONAL_OR_KEYWORD layouts use direct positional calls, matching normal-style execution.
Incomplete layouts retain explicit keywords so omitted Python defaults are preserved. This narrow
prototype has not established eligibility for arbitrary user classes or signatures.

The earlier direct-keyword variant independently measured 1.50x, 1.89x, 1.60x and 2.63x public gains.
keyword_results.json, keyword_results.md and keyword_prototype.py retain its exact evidence.
The final positional variant is a separate paired run; the keyword/positional difference is not a
single interleaved comparison of three backends. Both runs have their own current control and hashes.

## Correctness qualification

- Nineteen graph/case comparisons retain identical fixture constructor sequences, not just counts.
- Counts remain shallow 3, wide 9, diamond 5 and deep 511 for every compared input shape.
- Supplied root, exact-path and broadcast identities match the current executor's results.
- Sixty-four alternating a-only/b-only calls vary None, False, zero and fresh objects for each key.
  They create no new shapes, do not capture old values and do not affect subsequent normal creation.
- The existing public dispatch, guard, targeting, shape-cache and wrapper paths remain in use.
- Ruff passes with UP045 omitted for the role's Optional typing and S102 omitted for authorized codegen.

updater_0 independently ran ten unchanged many-only supplied-input, manifest-hydration and eager-error
tests against the candidate: ten passed in 0.20 seconds. Ten executor bodies, defaults and namespace
additions were verified restored. The reviewed SHA256 matches the measured prototype exactly.
Evidence: artifacts/override_execution_lead_20260924/prototype_review.json and prototype_regressions.log.

## Measurement method and limits

The instrument captures the real executor object after binding. Outside each serial sample it swaps
that object's __code__ and keyword defaults between the original and candidate bodies. Function identity
and existing cache references stay the same. There is no extra dispatch trampoline in either measured
path. Original bodies/defaults and added namespace bindings are restored before each world's cleanup.
This technique is for an isolated, quiescent experiment process; it is not a proposed production mechanism.

Public samples use the same existing MelderExperiment call closures, so their normal argument handling,
targeting and object release remain inside timing. Executor-only samples call the resolved inner executor
with a retained normalized socket map, using the same partial wrapper for both bodies. They intentionally
exclude public input allocation, normalization, targeting and outer dispatch; do not equate these doors.

All samples use CPython 3.14.7 free-threaded with GIL disabled, automatic mode and disk cache disabled.
Each pair has the same iteration count. Cases rotate by repeat and backend order alternates. Calls warm
before sampling; explicit GC is outside timing and the prior GC state is restored after every sample.
Both runtime and prototype before/after hashes match. Updater_1 held the serial timing slot and released
it before the lead's independent qualification. This is local microbenchmark evidence, not a universal ratio.

First-case preparation records whether a new executor bound; some cases reuse a previously prepared
shape. Additional prototype building is recorded separately. The diagnostic builds both original and
candidate executors, so it does not measure production cold-start improvement. Extra candidate generation
totaled about 198 ms across the deep graph's specialized executors. A production design should measure
first-shape compilation, code size and cache reuse after eliminating that duplicated diagnostic work.

## Scope

Qualified: disposal-free many-only benchmark classes, scalar named root/path/broadcast sockets,
complete known argument layouts, unchanged graph order and one serial caller. Independent tests also
qualify the selected many-only manifest-hydration/input/error cases.

Outside this prototype: scoped/generalized emitters, collections, contract payloads, positional caller
inputs, keyword-only/variadic/custom-construction semantics, pruning, .melc persistence qualification,
concurrent shape publication, full lifecycle/hook coverage and production API changes. Excluded benchmark
case labels are preserved in results.json. Existing positional/DI rejection is not fixed or counted as a gain.

## Interpretation and recommendation

The large-graph penalty is mostly avoidable execution work in these measurements. We can get deep
override execution close to normal without changing override meaning or introducing init={}.
The next production proposal should share normal call-layout facts, retain exact per-occurrence socket
operands through emission, and preserve existing invalidation and creation-context boundaries.

Smaller and input-heavy graphs still expose substantial public-front-end cost. For wide all-root input,
the final prototype measures 7.377 us publicly and 1.260 us at the inner executor. This points to further
input/targeting/dispatch investigation; the two doors are not an exact allocation of each cost. The result
does not establish that another public argument name is needed to address it.

Keep pruning as an explicit semantic decision in the epic. The constructor/disposal/error effects
documented by the lead are real, and none of the gains above comes from dropping them.

## Reproduction and review seams

```powershell
$env:PYTHONPATH = "$PWD/src;$PWD"
$env:PROTOTYPE_GRAPHS = 'shallow,wide,diamond,deep'
$env:PROTOTYPE_REPEATS = '7'
$env:PROTOTYPE_SAMPLE_MS = '30'
$env:PROTOTYPE_CALL_STYLE = 'positional'
& .venv_new/Scripts/python.exe context_compass/artifacts/override_emission_prototype_20260924/prototype.py
```

EmissionExperiment.bind captures completed real bindings. ExecutorPair.lower builds a candidate,
select(True/False) chooses its body outside execution and cleanup restores the original function and
namespace. The lead's review runner uses these seams independently; no production monkeypatch is proposed.

Timing evidence: results.json, results.md. Earlier control: keyword_results.json and keyword_prototype.py.
Generated *_prototype.py files show exact emitted candidate bodies for the qualified shapes.
