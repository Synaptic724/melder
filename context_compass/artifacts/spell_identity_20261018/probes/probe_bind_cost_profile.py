"""
Where a bind's time goes, before and after S1 and S2 (melder_0, 2026-10-18; companion of probe_bind_cost.py).

Profiles only the bind lane of the benchmark's `run_cycle` (its `bind_profiler` hook) over N cycles against one
tree, caching disabled and no meld sweep, and prints the functions with the most cumulative time under bind.
cProfile inflates absolute times; read the rows as shares, not as costs.

Usage: python probe_bind_cost_profile.py <tree> <cycles> [rows]
"""
import cProfile
import io
import os
import pstats
import sys
from pathlib import Path


class BindCostProfile:
    """One profiled run over one tree."""

    def __init__(self, tree: Path, cycles: int, rows: int) -> None:
        self.tree = tree
        self.cycles = cycles
        self.rows = rows

    def run(self) -> None:
        os.environ["BENCH_CYCLE_SYNTH_CLASSES"] = "0"
        sys.path.insert(0, str(self.tree / "benchmarks" / "testing_other_di"))
        import profile_bind_conjure_cycle as benchmark
        import melder
        expected = (self.tree / "src" / "melder").resolve()
        if Path(melder.__file__).resolve().parent != expected:
            raise SystemExit(f"imported {melder.__file__}, expected the tree's {expected}")
        benchmark.run_cycle(caching_enabled=False, meld_sweep=False)
        profiler = cProfile.Profile()
        for _ in range(self.cycles):
            benchmark.run_cycle(caching_enabled=False, meld_sweep=False, bind_profiler=profiler)
        out = io.StringIO()
        stats = pstats.Stats(profiler, stream=out)
        stats.sort_stats("cumulative").print_stats(self.rows)
        root = str(self.tree / "src") + os.sep
        print(f"tree {self.tree}; cycles {self.cycles}; gil_enabled={sys._is_gil_enabled()}")
        print(out.getvalue().replace(root, ""))


def main() -> None:
    tree = Path(sys.argv[1]).resolve()
    cycles = int(sys.argv[2])
    rows = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    BindCostProfile(tree, cycles, rows).run()


if __name__ == "__main__":
    main()
