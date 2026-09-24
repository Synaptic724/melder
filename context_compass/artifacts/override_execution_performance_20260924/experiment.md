# Melder override performance baseline

Associated task: tickets/tasks/2026-09-24_measure_melder_creation_and_overrides_task.md.
Associated epic: tickets/epics/2026-09-24_override_execution_performance_epic.md.

## Experiment
tests/experimentation/test_melder_creation_overrides_performance.py reuses only the graph models from
benchmarks/testing_other_di/test_overrides_all.py, which mirrors the shallow suite's transient graphs.
It invokes no competitor builder. A new scalar constructor control has equal construction work with
and without an explicit override. The legacy existing-instance solo timing is excluded from creation ratios.

## Method
- Same public meld call and fixed-iteration timing loop for every Melder case.
- Warmup precedes calibration; sample counts target 30 ms unless explicitly configured.
- Seven samples per case by default, with rotating case order.
- Setup, correctness assertions and explicit garbage collection are outside timing.
- GC inside samples is selectable; the default is disabled and prior state is restored afterward.
- Disk caching is disabled; ordinary in-memory compilation, specialization and warm lookup remain.
- Root inputs reuse actual precreated values. Supplied graphs are labeled; Python root construction
  is a lower-bound control and does not stand in for a new Melder API.
- Runtime source hashes before/after detect concurrent source edits. No latency thresholds assert success.

## Commands (PowerShell, repository root)
```powershell
& .venv_new/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/experimentation/test_melder_creation_overrides_performance.py -k matrix
$env:MELDER_OVERRIDE_PERF = '1'
$env:MELDER_OVERRIDE_OUTPUT = 'context_compass/artifacts/override_execution_performance_20260924/automatic'
& .venv_new/Scripts/python.exe -m pytest -q -s -p no:cacheprovider tests/experimentation/test_melder_creation_overrides_performance.py -k performance
```

Set MELDER_OVERRIDE_MODES=dynamic and choose a separate output directory for the dynamic comparison.
Set MELDER_OVERRIDE_GRAPHS to a comma-separated subset to investigate individual shapes.
MELDER_OVERRIDE_ITERS overrides calibration; MELDER_OVERRIDE_REPEATS controls repeated samples.

## Results
Measured automatic and dynamic results are in their respective results.json/results.md files.
findings.md contains the comparison and the next investigation targets. Four positional/DI cases
are rejected by the current runtime and explicitly excluded from timing; scalar positional input works.

For separate constructor-count profiling:
```powershell
$env:PYTHONPATH = 'src;.'
& .venv_new/Scripts/python.exe context_compass/artifacts/override_execution_performance_20260924/count_constructors.py
```
This writes constructor_counts.json and does not change the unified timing experiment.
