"""Reproduce constructor-count observations separately from benchmark timings.

Run from the repository root with src on PYTHONPATH. Uses the unified experiment
unchanged and writes counts beside this script. Profiler times are not speed claims.
"""

import cProfile
import json
import pstats
from pathlib import Path

from tests.experimentation.test_melder_creation_overrides_performance import (
    MelderExperiment,
    _source_fingerprints,
)


def main() -> None:
    """Count model __init__ calls for matched warmed public Melder operations."""
    repo = Path.cwd()
    before = _source_fingerprints(repo)
    rows = []
    iterations = 128
    for graph in ("shallow", "wide", "deep"):
        world = MelderExperiment()
        try:
            world.setup(graph, "automatic")
            world.verify()
            for case in ("normal", "empty_tuple", "root_one_reused", "root_all_reused", "original_override"):
                call = world.cases[case][0]
                for _ in range(128):
                    call()
                profile = cProfile.Profile()
                profile.enable()
                for _ in range(iterations):
                    call()
                profile.disable()
                constructors = []
                hot_functions = []
                for (filename, line, function), (_primitive, calls, own, cumulative, _callers) in pstats.Stats(profile).stats.items():
                    source = filename.replace("\\", "/")
                    if function == "__init__" and source.endswith(("/test_overrides_all.py", "/deep_layers.py")):
                        constructors.append({"file": source, "line": line, "calls": calls})
                    hot_functions.append({"file": source, "line": line, "function": function,
                                          "calls": calls, "own_seconds": own, "cumulative_seconds": cumulative})
                rows.append({"graph": graph, "case": case, "iterations": iterations,
                             "model_constructors_per_operation": sum(row["calls"] for row in constructors) / iterations,
                             "constructors": constructors,
                             "top_functions_by_own_time": sorted(hot_functions, key=lambda row: row["own_seconds"], reverse=True)[:15]})
                profile.clear()
        finally:
            world.cleanup()
    after = _source_fingerprints(repo)
    changed = sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))
    payload = {"source_changed_during_run": changed, "source_sha256": before, "results": rows}
    Path(__file__).with_name("constructor_counts.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    assert not changed, f"Source changed during profiling: {changed}"


if __name__ == "__main__":
    main()
