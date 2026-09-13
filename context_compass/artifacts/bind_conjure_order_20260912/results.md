# Dynamic five-object bind/conjure order speed test

Bind -> conjure -> meld used 49.2% less median workflow time. Conjure-first took 1.967x as long.

## Method
- Five distinct independent classes with tiny constructors and deterministic values.
- Five individual Spellbook.bind calls with Existence.unique and permissions=create; no outer batch transaction.
- Both frames configured dynamic before timing; conjure(dynamic=True) in both sequences.
- Meld each returned spell_id once, validating all five actual instance types and values after timing.
- Fresh book/frame/root for each sample. Setup and cleanup are measured separately and excluded from the main total.
- Three fresh pytest processes; 20 warm-up pairs and 200 measured pairs in each: 600 samples per order.
- AB/BA order alternates, with an untimed GC collection before each pair; GC remains enabled during measurement.
- Default five compiler workers; disk system caching, Crystallizer recording and Nexus publication disabled.
- No coverage, tracing or profiling; pytest external plugin autoload disabled.
- Repeated unique-instance melds are measured separately and checked to return the original instances.

## Main results
All values below are milliseconds. Stage and total medians are computed independently.

| Sequence | Bind five | Conjure | First meld of all five | Workflow total | Total p10-p90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Bind -> conjure -> meld | 1.0766 | 2.5968 | 0.1069 | 3.8274 | 3.1448-5.4172 |
| Conjure -> bind -> meld | 1.8735 | 0.3211 | 5.3196 | 7.5289 | 6.4966-10.5421 |

## Each object's first meld

| Object | Bind first (ms) | Conjure first (ms) |
| --- | ---: | ---: |
| Payload 1 | 0.0445 | 2.0251 |
| Payload 2 | 0.0183 | 0.9018 |
| Payload 3 | 0.0150 | 0.8214 |
| Payload 4 | 0.0143 | 0.7944 |
| Payload 5 | 0.0142 | 0.7778 |

## Repetition stability

| Process | Bind-first total (ms) | Conjure-first total (ms) | Conjure-first / bind-first |
| --- | ---: | ---: | ---: |
| run_1 | 3.7044 | 7.3198 | 1.976x |
| run_2 | 3.7248 | 7.4804 | 2.008x |
| run_3 | 4.2298 | 8.5022 | 2.010x |

## Costs outside the requested workflow

| Sequence | Book/frame setup (ms) | Five warmed melds (ms) | Cleanup (ms) |
| --- | ---: | ---: | ---: |
| Bind -> conjure -> meld | 0.3188 | 0.0044 | 1.1644 |
| Conjure -> bind -> meld | 0.3132 | 0.0045 | 1.1888 |

## Runtime and source
- Python: 3.14.0 free-threading build (tags/v3.14.0:ebf955d, Oct  7 2025, 10:13:09) [MSC v.1944 64 bit (AMD64)]
- Executable: C:\Users\Mark\PycharmProjects\melder_private\.venv_new\Scripts\python.exe
- Platform: Windows-11-10.0.26200-SP0
- Processor: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel
- Melder: 0.2.37
- Source: C:\Users\Mark\PycharmProjects\melder_private\src\melder\__init__.py
- Git commit: ed9f5047d8a7305954ae4d1cc74818323c118c88
- Runtime source had no uncommitted changes in any measured process.

## Interpretation
The empty conjure is much cheaper, but that advantage is outweighed by later binding and first-meld costs.
The timing locates the difference; it does not by itself attribute individual internal compiler functions.
This result is for independent classes, unique existence, individual binds, and disk caching off.
It is not a claim about dependency chains, bulk transactions, prebuilt instances, or warm disk-cache scenarios.
Absolute times varied between processes, while the relative workflow result was consistent.

## Reproduce
From the repository root in PowerShell, run each repetition sequentially with a different run id:

    $env:PYTHONPATH = (Join-Path (Get-Location) 'src')
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
    $env:MELDER_BIND_ORDER_SPEEDTEST = '1'
    $env:MELDER_BIND_ORDER_SAMPLES = '200'
    $env:MELDER_BIND_ORDER_WARMUPS = '20'
    $env:MELDER_BIND_ORDER_RUN_ID = 'run_1'
    & '.venv_new/Scripts/python.exe' -m pytest tests/experimentation/test_dynamic_bind_conjure_order_speed_experiment.py --confcutdir=tests/experimentation -p no:cacheprovider -o addopts= -q -s

Evidence: run_1.json, run_2.json, run_3.json contain every measured sample; aggregate.json contains the combined statistics.
pilot.json is the earlier correctness pilot and is excluded from the combined statistics.
