"""
Bind cost before and after S1 and S2 (melder_0, 2026-10-18; S1's exit gate).

Runs the bind and conjure lanes of benchmarks/testing_other_di/profile_bind_conjure_cycle.py - the gauntlet's
29 classes, or its generated N-class graph - against one source tree, caching disabled, with no first-meld sweep
(the benchmark's sweep melds a spellspace-scoped spell at the root on 0.2.8256 and fails there, before and after
this change alike). Each cycle starts from a fresh Aether, binds every class and conjures, exactly as the
benchmark's own `run_cycle` does; only `meld_sweep=False` differs.

Usage: python probe_bind_cost.py <tree> <repeats> [synth_classes]
Prints the interpreter, the melder module it imported (it must be the tree's), and per lane the median, mean and
minimum in milliseconds, plus the median of one bind in microseconds.
"""
import os
import statistics
import sys
from pathlib import Path
from typing import List


class BindCostProbe:
    """One measurement run over one tree."""

    def __init__(self, tree: Path, repeats: int, synth_classes: int) -> None:
        self.tree = tree
        self.repeats = repeats
        self.synth_classes = synth_classes

    def load_benchmark(self) -> object:
        """Import the tree's benchmark module, which puts the tree's src first on sys.path."""
        os.environ["BENCH_CYCLE_SYNTH_CLASSES"] = str(self.synth_classes)
        sys.path.insert(0, str(self.tree / "benchmarks" / "testing_other_di"))
        import profile_bind_conjure_cycle as benchmark
        import melder
        expected = (self.tree / "src" / "melder").resolve()
        if Path(melder.__file__).resolve().parent != expected:
            raise SystemExit(f"imported {melder.__file__}, expected the tree's {expected}")
        return benchmark

    @staticmethod
    def line(label: str, values_ns: List[int]) -> str:
        ms = [v / 1e6 for v in values_ns]
        return (f"{label}: median {statistics.median(ms):.3f} ms, mean {statistics.fmean(ms):.3f} ms, "
                f"min {min(ms):.3f} ms ({len(ms)} cycles)")

    def run(self) -> None:
        benchmark = self.load_benchmark()
        import melder
        print(f"python {sys.version.split()[0]} gil_enabled={sys._is_gil_enabled()} melder={melder.__version__}")
        print(f"tree {self.tree}; classes {len(benchmark._support.ALL_CLASSES)}; repeats {self.repeats}")
        # One unmeasured cycle warms imports and code objects in both trees alike.
        benchmark.run_cycle(caching_enabled=False, meld_sweep=False)
        binds: List[int] = []
        conjures: List[int] = []
        per_bind: List[int] = []
        for _ in range(self.repeats):
            timings = benchmark.run_cycle(caching_enabled=False, meld_sweep=False)
            binds.append(timings.bind_ns)
            conjures.append(timings.conjure_ns)
            per_bind.extend(timings.per_bind_ns)
        print(self.line("bind lane", binds))
        print(self.line("conjure lane", conjures))
        print(f"one bind: median {statistics.median(per_bind) / 1e3:.1f} us over {len(per_bind)} binds")


def main() -> None:
    tree = Path(sys.argv[1]).resolve()
    repeats = int(sys.argv[2])
    synth = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    BindCostProbe(tree, repeats, synth).run()


if __name__ == "__main__":
    main()
