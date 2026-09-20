"""Rebuild the cache-comparison report from the nine measured 3.14.7 runs."""

import json
import statistics
from pathlib import Path


class CacheReport:
    """Own the deterministic report layout; inputs and outputs stay beside this file."""

    MODES = ("disabled", "cold", "warm")
    ORDERS = ("bind_conjure_meld", "conjure_bind_meld")
    LABELS = ("Bind -> conjure -> meld", "Conjure -> bind -> meld")
    PHASES = ("bind_ns", "conjure_ns", "first_meld_ns", "total_ns")

    @staticmethod
    def distribution(values: list[float]) -> dict[str, float]:
        """Return independently computed medians and inclusive deciles in milliseconds."""
        scaled = [value / 1_000_000 for value in values]
        deciles = statistics.quantiles(scaled, n=10, method="inclusive")
        return {"median_ms": statistics.median(scaled), "p10_ms": deciles[0], "p90_ms": deciles[8]}

    @classmethod
    def run(cls) -> None:
        """Validate input treatment/size and write aggregate JSON plus a Markdown report."""
        directory = Path(__file__).resolve().parent
        summary: dict[str, dict] = {}
        repetition_rows: list[str] = []
        for mode in cls.MODES:
            runs = [json.loads((directory / f"cache_{mode}_3147_run_{i}.json").read_text()) for i in (1, 2, 3)]
            for i, run in enumerate(runs, 1):
                meta = run["metadata"]
                assert meta["cache_mode"] == mode and meta["python"].startswith("3.14.7 ")
                assert not meta["gil_enabled"] and meta["src_status"] == ""
                assert meta["measured_pairs"] == 200 and len(run["samples"]) == 400
                medians = [statistics.median(row["total_ns"] for row in run["samples"] if row["sequence"] == order) / 1e6 for order in cls.ORDERS]
                repetition_rows.append(f"| {mode} | {i} | {medians[0]:.4f} | {medians[1]:.4f} | {medians[1] / medians[0]:.3f}x |")
            summary[mode] = {}
            for order in cls.ORDERS:
                rows = [row for run in runs for row in run["samples"] if row["sequence"] == order]
                assert len(rows) == 600
                summary[mode][order] = {
                    "samples": len(rows),
                    "phases": {phase: cls.distribution([row[phase] for row in rows]) for phase in cls.PHASES},
                    "per_first_meld": [cls.distribution([row["per_first_meld_ns"][i] for row in rows]) for i in range(5)],
                    "warm_five_meld": cls.distribution([row["warm_five_meld_ns"] for row in rows]),
                    "calls": runs[0]["call_probes"][order],
                }
                assert all(run["call_probes"][order] == summary[mode][order]["calls"] for run in runs)
        comparisons = {}
        for order in cls.ORDERS:
            totals = {mode: summary[mode][order]["phases"]["total_ns"]["median_ms"] for mode in cls.MODES}
            comparisons[order] = {
                "warm_vs_cold_reduction_percent": 100 * (1 - totals["warm"] / totals["cold"]),
                "warm_vs_disabled_change_percent": 100 * (totals["warm"] / totals["disabled"] - 1),
            }
        output = {"summary": summary, "comparisons": comparisons}
        (directory / "cache_aggregate_3147.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        lines = [
            "# Cached dynamic bind/conjure order comparison on Python 3.14.7",
            "",
            "The late-bind path does not reuse saved execution payloads. A warm bundle avoids rewrites,",
            "but its five spells still compile. Bind-before-conjure loads all five saved payloads.",
            "",
            "## Median complete workflow (milliseconds)",
            "",
            "| Disk cache | Bind -> conjure -> meld | Conjure -> bind -> meld | Latter / former |",
            "| --- | ---: | ---: | ---: |",
        ]
        for mode in cls.MODES:
            totals = [summary[mode][order]["phases"]["total_ns"]["median_ms"] for order in cls.ORDERS]
            lines.append(f"| {mode} | {totals[0]:.4f} | {totals[1]:.4f} | {totals[1]/totals[0]:.3f}x |")
        lines += ["", "## Stage breakdown (milliseconds)", "", "| Cache | Order | Bind five | Conjure | First meld five | Total p10-p90 |", "| --- | --- | ---: | ---: | ---: | ---: |"]
        for mode in cls.MODES:
            for order, label in zip(cls.ORDERS, cls.LABELS):
                phases = summary[mode][order]["phases"]
                values = [phases[phase]["median_ms"] for phase in cls.PHASES[:3]]
                total = phases["total_ns"]
                lines.append(f"| {mode} | {label} | {values[0]:.4f} | {values[1]:.4f} | {values[2]:.4f} | {total['p10_ms']:.4f}-{total['p90_ms']:.4f} |")
        lines += ["", "Stage and total medians are computed independently; medians need not add exactly.", "", "## Interpretation", ""]
        for order, label in zip(cls.ORDERS, cls.LABELS):
            delta = comparisons[order]
            lines.append(f"- {label}: warm uses {delta['warm_vs_cold_reduction_percent']:.1f}% less median time than cold; {delta['warm_vs_disabled_change_percent']:+.1f}% versus cache disabled.")
        lines += [
            "- A warm cache improves over building and writing a cold cache. It gives no meaningful total",
            "  speedup over disabling disk caching for this small five-independent-class workload.",
            "- Conjure still performs phases 1-7. A full hit skips phases 8-11 and publishes cached contexts;",
            "  first meld includes lazy hydration. Those savings compete with bundle loading overhead.",
            "- An empty conjure still loads the cache file, but has no live spells to match. Later binds",
            "  never hydrate those payloads. Existing IDs only suppress payload export and bundle writes.",
            "- This does not generalize to larger dependency graphs, other existence modes or bulk binds.",
            "",
            "## Independent diagnostic call counts", "",
            "| Cache | Order | Payload reads | Cached context publications | Target plan compiles | Bundle writes |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
        for mode in cls.MODES:
            for order, label in zip(cls.ORDERS, cls.LABELS):
                calls = summary[mode][order]["calls"]
                lines.append(f"| {mode} | {label} | {calls['payload_reads']} | {calls['cached_context_publications']} | {calls['target_plan_compilations']} | {calls['bundle_writes']} |")
        lines += ["", "All nine diagnostic passes agree. These are call-through spy runs after measurement;",
                  "their timings are discarded. Target plan counts refer to the late-bind local path;",
                  "zero does not imply that no conduit-wide plan compilation happened on a cold conjure.",
                  "No deferred fallback compilation was observed in any diagnostic case.",
                  "", "## First meld of each object (microseconds)", "",
                  "| Cache | Order | Object 1 | Object 2 | Object 3 | Object 4 | Object 5 |",
                  "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
        for mode in cls.MODES:
            for order, label in zip(cls.ORDERS, cls.LABELS):
                values = " | ".join(f"{entry['median_ms'] * 1000:.2f}" for entry in summary[mode][order]["per_first_meld"])
                lines.append(f"| {mode} | {label} | {values} |")
        lines += ["", "## Repetition stability", "", "| Cache | Process | Bind-first total ms | Conjure-first total ms | Ratio |", "| --- | ---: | ---: | ---: | ---: |", *repetition_rows,
                  "", "## Method and evidence", "",
                  "- Three fresh processes per mode; 20 warm-up pairs plus 200 measured pairs per process:",
                  "  600 samples per order per mode, 3,600 measured workflows total.",
                  "- Same five classes, individual binds, Existence.unique, returned spell IDs, dynamic posture,",
                  "  default five compiler workers, recording off, Nexus publication off and GC enabled.",
                  "- AB/BA sample order alternates. Mode order rotates across repetitions. Processes run serially.",
                  "- Every cycle owns a fresh book/frame/root. Warm files are seeded by the same order in separate",
                  "  task-owned folders. Cold means absent Melder cache, not cold OS/filesystem page caches.",
                  "- Setup, cache deletion/seeding, assertions, repeated instance reads and teardown are untimed.",
                  "  Conjure/bind/first-meld cache I/O remains inside the corresponding workflow timer.",
                  "- All object types/values, repeated-instance identity and frame cleanup checks passed.",
                  "- Raw samples: cache_{disabled,cold,warm}_3147_run_{1,2,3}.json. Pilots are excluded.",
                  "- No runtime source edits. Git revision and source status are captured in every run.",
                  "- See environment_and_stall.md for the uv migration and bounded profiler reproduction.",
                  "", "## Reproduce", "",
                  "Run from the repository root in PowerShell; repeat with each cache mode and unique run ID:",
                  "", "```powershell", "$env:PYTHONPATH = (Join-Path (Get-Location) 'src')",
                  "$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'", "$env:MELDER_BIND_ORDER_CACHE_SPEEDTEST = '1'",
                  "$env:MELDER_BIND_ORDER_CACHE_MODE = 'warm'", "$env:MELDER_BIND_ORDER_SAMPLES = '200'",
                  "$env:MELDER_BIND_ORDER_WARMUPS = '20'", "$env:MELDER_BIND_ORDER_RUN_ID = 'cache_warm_3147_run_1'",
                  "& '.venv_new/Scripts/python.exe' -m pytest tests/experimentation/test_dynamic_bind_conjure_order_cache_speed_experiment.py::test_dynamic_bind_conjure_order_cache_speed --confcutdir=tests/experimentation -p no:cacheprovider -o addopts= -q -s",
                  "```", "", "Rebuild this report with `.venv_new/Scripts/python.exe context_compass/artifacts/bind_conjure_order_20260912/aggregate_cache_results.py`."]
        (directory / "cache_results_3147.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    CacheReport.run()
