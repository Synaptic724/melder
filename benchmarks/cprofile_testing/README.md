# cprofile_testing - the rot-finding harness

Post-1.0 performance program: find slow paths and complexity rot in the
non-meld surfaces (checkpoint load/save, MR verbs, linking, transactions).
The meld path is EXCLUDED by owner ruling - it is already optimized.

## Method
Every scenario measures two ways: profiler-free wall-clock repeats (the honest
duration) and one cProfile pass (where the time goes: .prof + top-25 tables by
cumulative and tottime). Scenarios run at THREE TIERS; rot = a best-seconds
ratio between tiers that outgrows the tier size ratio. The paired .prof names
the guilty frames (read the tottime table first).

## Run (3.14t, repo root)
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py small
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py medium
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py large
    python benchmarks/cprofile_testing/profile_mutation_research.py small|medium|large

Outputs land in `results/` as `<scenario>__<tier>.prof` + `.txt`. Deep dives:
    python -m pstats results/crystallizer_checkpoint_load__large.prof

## Files
- profile_harness.py - shared ProfileScenario/run_scenarios runner.
- profile_crystallizer_checkpoints.py - seal / cache round-trip / load.
- profile_mutation_research.py - record entries / residency joins / campaign view.
- (next) profile_linking_transactions.py - link/sever + admission plane.

## Reading results
- tottime (self time) rows in OUR frames = optimization targets.
- cumulative rows dominated by stdlib json/hashlib = payload-size problems.
- lock-wait does not show in cProfile: a big wall-clock/cumulative gap on
  3.14t suggests contention - escalate to a threading-stress bench.
