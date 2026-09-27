"""Median conjure setup (ms) of the owner's four override graphs; run from a tree root with PYTHONPATH=src:."""
import statistics, sys, time
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment

print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
for graph in ("shallow", "wide", "diamond", "deep"):
    runs = []
    for _ in range(9):
        e = MelderExperiment()
        s = time.perf_counter_ns()
        e.setup(graph, "automatic")
        runs.append((time.perf_counter_ns() - s) / 1e6)
        e.cleanup()
    print(f"{graph:8} setup median {statistics.median(runs):7.2f} ms  min {min(runs):7.2f}")
