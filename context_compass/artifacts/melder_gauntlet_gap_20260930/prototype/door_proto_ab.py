"""
Interleaved A/B of the top-level door overlay on the shared gauntlet's Melder lane (melder_0, 2026-09-30).

Purpose:
    Measure option A of tickets/tasks/2026-09-30_map_remaining_melder_gauntlet_gains_task.md: the same tree run with
    and without `door_proto` installed, each run in a fresh `-X gil=0` process, variants shuffled per round so
    machine drift spreads across both. Works on Linux and Windows; nothing in the repository is modified.

Usage (parent):
    python door_proto_ab.py --repo-root <melder_private> [--rounds 4] [--iterations 30000] [--seed 1]
        [--control dishka] [--out door_proto_ab.jsonl]

Contract:
    - Each run calls the harness's own `_run_gauntlet_benchmark("melder", cfg)`; for variant "proto" the overlay is
      installed first, before any Spellbook exists. `--control dishka` adds an untouched dishka run per round.
    - Appends one JSON line per run to --out and prints a median summary with proto/base ratios at the end.
    - DI_GAUNTLET_ITERS is set from --iterations for every child; the other harness settings are inherited.
"""
import argparse
import json
import os
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def _child(repo_root: Path, variant: str, run_tag: str, out: Path) -> int:
    """
    Run one library once in this process and append its numbers.

    Args:
        repo_root: Tree holding `benchmarks/` and `src/`.
        variant: "base", "proto" (Melder with the overlay) or a control library name.
        run_tag: Label stored with the row.
        out: JSONL file to append to.

    Returns:
        int: 0.
    """
    for path in (repo_root, repo_root / "src", Path(__file__).resolve().parent):
        sys.path.insert(0, str(path))
    installed = 0
    if variant == "proto":
        import door_proto
        originals = door_proto.install(door_proto.door_module())
        installed = sum(len(entries) for entries in originals.values())
    import benchmarks.testing_other_di.test_real_world_gauntlet as gauntlet
    lib = "melder" if variant in ("base", "proto") else variant
    cfg = gauntlet._GauntletConfig.from_env()
    result = gauntlet._run_gauntlet_benchmark(lib, cfg)
    lanes: Dict[str, Dict[str, float]] = {}
    for name, lane in result.lane_summaries.items():
        lanes[name] = {
            "outer_total_avg_us": lane.outer_total_summary.avg_ns / 1000.0,
            "request_total_avg_us": lane.request_total_summary.avg_ns / 1000.0,
            "active_cycles_per_s": lane.active_cycles_per_s,
            "wall_cycles_per_s": lane.wall_cycles_per_s,
        }
    row: Dict[str, Any] = {
        "run_tag": run_tag,
        "variant": variant,
        "lib": lib,
        "overlay_entries": installed,
        "iterations": cfg.iterations,
        "gil_enabled": sys._is_gil_enabled(),
        "setup_ms": result.setup_ns / 1e6,
        "total_ms": result.iteration_summary.total_ns / 1e6,
        "avg_ms": result.iteration_summary.avg_ns / 1e6,
        "p99_ms": result.iteration_summary.p99_ns / 1e6,
        "threaded_avg_ms": result.threaded_summary.avg_ns / 1e6,
        "hot_scopes_per_s": result.hot_scope_cycles_per_s,
        "lanes": lanes,
    }
    with out.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    return 0


def _median(rows: List[Dict[str, Any]], *path: str) -> float:
    """
    Median of one numeric field over rows.

    Args:
        rows: Result rows of one variant.
        path: Keys leading to the field.

    Returns:
        float: The median.
    """
    values: List[float] = []
    for row in rows:
        value: Any = row
        for key in path:
            value = value[key]
        values.append(float(value))
    return statistics.median(values)


def _summary(out: Path, tags: List[str]) -> None:
    """
    Print medians per variant and proto/base ratios for this invocation's runs.

    Args:
        out: The JSONL file.
        tags: Run tags written by this invocation.
    """
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [row for row in rows if row["run_tag"] in tags]
    by_variant: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        by_variant.setdefault(row["variant"], []).append(row)
    fields = [("total_ms",), ("threaded_avg_ms",), ("p99_ms",), ("hot_scopes_per_s",)]
    lanes = ("request", "worker_a", "worker_b")
    print("\nmedians (runs per variant: " + ", ".join(f"{k}={len(v)}" for k, v in by_variant.items()) + ")")
    for variant, vrows in by_variant.items():
        parts = [f"{field[0]}={_median(vrows, *field):.3f}" for field in fields]
        for lane in lanes:
            parts.append(f"{lane}.outer_us={_median(vrows, 'lanes', lane, 'outer_total_avg_us'):.2f}")
            parts.append(f"{lane}.active/s={_median(vrows, 'lanes', lane, 'active_cycles_per_s'):.0f}")
        print(f"  {variant:<7} " + " ".join(parts))
    if "base" in by_variant and "proto" in by_variant:
        base, proto = by_variant["base"], by_variant["proto"]
        print("proto/base ratios (below 1.0 = proto faster for times; above 1.0 = proto faster for rates):")
        for field in fields:
            print(f"  {field[0]:<18} {_median(proto, *field) / _median(base, *field):.4f}")
        for lane in lanes:
            for key in ("outer_total_avg_us", "active_cycles_per_s"):
                ratio = _median(proto, "lanes", lane, key) / _median(base, "lanes", lane, key)
                print(f"  {lane}.{key:<22} {ratio:.4f}")


def main(argv: Optional[List[str]] = None) -> int:
    """
    Parent: run the shuffled rounds and print the summary. Child (--child): run one variant.

    Args:
        argv: Command line (defaults to sys.argv[1:]).

    Returns:
        int: 0, or the exit code of the first failing child.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=Path("door_proto_ab.jsonl"))
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--control", default="")
    parser.add_argument("--round-offset", type=int, default=0)
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--variant", default="base")
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    if args.child:
        return _child(repo_root, args.variant, args.run_tag, args.out)
    env = dict(os.environ)
    if args.iterations is not None:
        env["DI_GAUNTLET_ITERS"] = str(args.iterations)
    variants = ["base", "proto"] + ([args.control] if args.control else [])
    rng = random.Random(args.seed)
    tags: List[str] = []
    for round_ix in range(args.rounds):
        order = list(variants)
        rng.shuffle(order)
        for variant in order:
            tag = f"r{round_ix + 1 + args.round_offset}.{variant}"
            command = [sys.executable, "-X", "gil=0", str(Path(__file__).resolve()), "--child", "--variant", variant,
                       "--run-tag", tag, "--repo-root", str(repo_root), "--out", str(args.out.resolve())]
            t0 = time.perf_counter()
            done = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
            if done.returncode != 0:
                print(done.stdout[-3000:], done.stderr[-3000:])
                return done.returncode
            tags.append(tag)
            row = json.loads(args.out.read_text(encoding="utf-8").splitlines()[-1])
            print(f"# {time.perf_counter() - t0:6.1f}s {tag:<12} total={row['total_ms']:.1f}ms "
                  f"threaded={row['threaded_avg_ms']:.4f}ms hot_scopes/s={row['hot_scopes_per_s']:.0f}", flush=True)
    _summary(args.out.resolve(), tags)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
