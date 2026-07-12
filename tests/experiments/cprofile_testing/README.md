# Crystallizer performance experiments

These are opt-in experiments, not normal CI tests. They compare direct world
creation, Crystallizer recording, checkpoint transport, and bootstrap restore.
MutationResearch profiling remains here as a separate experimental surface.

## Run (3.14t, repository root)

```powershell
.venv_new\\Scripts\\python.exe tests\\experiments\\cprofile_testing\\trace_creation_vs_bootstrap.py
.venv_new\\Scripts\\python.exe tests\\experiments\\cprofile_testing\\profile_crystallizer_checkpoints.py small
.venv_new\\Scripts\\python.exe tests\\experiments\\cprofile_testing\\profile_mutation_research.py small
```

The `trace_creation_vs_bootstrap.py` experiment uses the same file-backed
RestoreAlpha target as the real integration suite. It prints separate timings
for normal creation, recorded creation, seal, flush, cache reload, and restore.

The tiered profile scripts pair profiler-free wall-clock repeats (the speed
result) with cProfile output (attribution only). Generated `.prof` and `.txt`
files land in `results/` and are ignored by the nested `.gitignore`.

## Pytest wrappers

The `pytest_profile_*.py` filenames intentionally avoid default pytest
discovery. They can still be passed explicitly when a pytest-shaped run is
useful.

## Reading results

- Compare wall-clock values for speed; cProfile adds substantial overhead.
- Use cumulative frames to find repeated work and self-time to find local work.
- SpellIndex tests can correlate with SpellCrystal cost because staging and
  notching create additional spell versions; profile the emitted crystal path
  before assuming the index snapshot operations themselves are slow.
