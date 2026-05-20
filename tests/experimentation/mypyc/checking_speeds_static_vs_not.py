import os
import sys
import shutil
import subprocess
import textwrap
import importlib
import gc
import random
import statistics
from pathlib import Path
from time import perf_counter_ns

workdir = Path("/mnt/data/mypyc_static_bench")
if workdir.exists():
    shutil.rmtree(workdir)
workdir.mkdir(parents=True)

source_code = r'''
from __future__ import annotations

from typing import Callable


class OwnMethodWorker:
    __slots__ = ("offset",)

    offset: int

    def __init__(self, offset: int) -> None:
        self.offset = offset

    def a(self, x: int) -> int:
        return x + self.offset

    def b(self, x: int) -> int:
        return x * 3

    def c(self, x: int) -> int:
        return x - 7

    def d(self, x: int) -> int:
        return x ^ 11

    def run(self, x: int) -> int:
        x = self.a(x)
        x = self.b(x)
        x = self.c(x)
        x = self.d(x)
        return x


class InstanceHelper:
    __slots__ = ("offset",)

    offset: int

    def __init__(self, offset: int) -> None:
        self.offset = offset

    def a(self, x: int) -> int:
        return x + self.offset

    def b(self, x: int) -> int:
        return x * 3

    def c(self, x: int) -> int:
        return x - 7

    def d(self, x: int) -> int:
        return x ^ 11


class InstanceHelperWorker:
    __slots__ = ("helper",)

    helper: InstanceHelper

    def __init__(self, helper: InstanceHelper) -> None:
        self.helper = helper

    def run(self, x: int) -> int:
        helper = self.helper

        x = helper.a(x)
        x = helper.b(x)
        x = helper.c(x)
        x = helper.d(x)
        return x


class StaticHelper:
    @staticmethod
    def a(x: int) -> int:
        return x + 5

    @staticmethod
    def b(x: int) -> int:
        return x * 3

    @staticmethod
    def c(x: int) -> int:
        return x - 7

    @staticmethod
    def d(x: int) -> int:
        return x ^ 11


class StaticHelperWorker:
    __slots__ = ()

    def run(self, x: int) -> int:
        x = StaticHelper.a(x)
        x = StaticHelper.b(x)
        x = StaticHelper.c(x)
        x = StaticHelper.d(x)
        return x


def module_a(x: int) -> int:
    return x + 5


def module_b(x: int) -> int:
    return x * 3


def module_c(x: int) -> int:
    return x - 7


def module_d(x: int) -> int:
    return x ^ 11


class ModuleFunctionWorker:
    __slots__ = ()

    def run(self, x: int) -> int:
        x = module_a(x)
        x = module_b(x)
        x = module_c(x)
        x = module_d(x)
        return x


class CachedStaticHelperWorker:
    __slots__ = ("a", "b", "c", "d")

    a: Callable[[int], int]
    b: Callable[[int], int]
    c: Callable[[int], int]
    d: Callable[[int], int]

    def __init__(self) -> None:
        self.a = StaticHelper.a
        self.b = StaticHelper.b
        self.c = StaticHelper.c
        self.d = StaticHelper.d

    def run(self, x: int) -> int:
        x = self.a(x)
        x = self.b(x)
        x = self.c(x)
        x = self.d(x)
        return x


class CachedModuleFunctionWorker:
    __slots__ = ("a", "b", "c", "d")

    a: Callable[[int], int]
    b: Callable[[int], int]
    c: Callable[[int], int]
    d: Callable[[int], int]

    def __init__(self) -> None:
        self.a = module_a
        self.b = module_b
        self.c = module_c
        self.d = module_d

    def run(self, x: int) -> int:
        x = self.a(x)
        x = self.b(x)
        x = self.c(x)
        x = self.d(x)
        return x


def run_own_methods(iterations: int) -> int:
    worker = OwnMethodWorker(5)
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result


def run_instance_helper(iterations: int) -> int:
    worker = InstanceHelperWorker(InstanceHelper(5))
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result


def run_static_helper(iterations: int) -> int:
    worker = StaticHelperWorker()
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result


def run_module_functions(iterations: int) -> int:
    worker = ModuleFunctionWorker()
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result


def run_cached_static_attrs(iterations: int) -> int:
    worker = CachedStaticHelperWorker()
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result


def run_cached_module_attrs(iterations: int) -> int:
    worker = CachedModuleFunctionWorker()
    result = 0
    for i in range(iterations):
        result += worker.run(i)
    return result
'''

pure_path = workdir / "bench_shapes_py.py"
compiled_path = workdir / "bench_shapes_compiled.py"
setup_path = workdir / "setup.py"

pure_path.write_text(source_code)
compiled_path.write_text(source_code)

setup_path.write_text(
    textwrap.dedent(
        """
        from setuptools import setup
        from mypyc.build import mypycify

        setup(
            name="bench_shapes_compiled",
            ext_modules=mypycify(["bench_shapes_compiled.py"]),
        )
        """
    ).strip()
)

print("Workdir:", workdir)
print("Python:", sys.version)
print("Compiling with mypyc...")
proc = subprocess.run(
    [sys.executable, "setup.py", "build_ext", "--inplace"],
    cwd=workdir,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=180,
)

print(proc.stdout[-6000:])

if proc.returncode != 0:
    print("mypyc compile failed. Stopping here.")
else:
    compiled_artifacts = sorted(p.name for p in workdir.glob("bench_shapes_compiled*.so"))
    print("Compiled artifacts:", compiled_artifacts)

    sys.path.insert(0, str(workdir))
    bench_py = importlib.import_module("bench_shapes_py")
    bench_compiled = importlib.import_module("bench_shapes_compiled")

    cases = [
        ("own methods on worker", "run_own_methods"),
        ("delegates to instance helper", "run_instance_helper"),
        ("delegates to static helper class", "run_static_helper"),
        ("delegates to module functions", "run_module_functions"),
        ("cached static funcs on worker attrs", "run_cached_static_attrs"),
        ("cached module funcs on worker attrs", "run_cached_module_attrs"),
    ]

    iterations = 100_000
    repeats = 80

    def time_func(func, iterations: int) -> tuple[int, int]:
        start = perf_counter_ns()
        result = func(iterations)
        elapsed = perf_counter_ns() - start
        return elapsed, result

    def benchmark_module(mod, label: str) -> tuple[dict[str, list[int]], dict[str, int]]:
        times_by_name: dict[str, list[int]] = {name: [] for name, _ in cases}
        results_by_name: dict[str, int] = {}

        # Warmup
        for _, func_name in cases:
            func = getattr(mod, func_name)
            for _ in range(10):
                func(iterations)

        gc_was_enabled = gc.isenabled()
        gc.disable()
        try:
            for _ in range(repeats):
                shuffled_cases = cases[:]
                random.shuffle(shuffled_cases)

                for name, func_name in shuffled_cases:
                    func = getattr(mod, func_name)
                    elapsed, result = time_func(func, iterations)
                    times_by_name[name].append(elapsed)
                    results_by_name[name] = result
        finally:
            if gc_was_enabled:
                gc.enable()

        return times_by_name, results_by_name

    print()
    print(f"Benchmarking pure Python and mypyc-compiled modules...")
    print(f"Iterations per timed run: {iterations:,}")
    print(f"Timed repeats per case: {repeats}")
    print()

    py_times, py_results = benchmark_module(bench_py, "pure Python")
    compiled_times, compiled_results = benchmark_module(bench_compiled, "mypyc compiled")

    expected = 15000650000
    print("Sanity check expected result:", expected)
    print("Pure Python results:")
    for name, result in py_results.items():
        print(f"  {name:38} {result}")
    print("Compiled results:")
    for name, result in compiled_results.items():
        print(f"  {name:38} {result}")

    def row_stats(times: list[int]) -> tuple[float, float, float, float]:
        best = min(times) / 1_000_000
        median = statistics.median(times) / 1_000_000
        mean = statistics.mean(times) / 1_000_000
        ns_per_outer = statistics.mean(times) / iterations
        return best, median, mean, ns_per_outer

    print()
    print("PURE PYTHON")
    py_base = statistics.mean(py_times["own methods on worker"])
    print(f"{'case':42} {'best ms':>10} {'median ms':>10} {'mean ms':>10} {'ns/call':>10} {'vs own':>10}")
    for name, _ in cases:
        best, median, mean, ns_call = row_stats(py_times[name])
        rel = statistics.mean(py_times[name]) / py_base
        print(f"{name:42} {best:10.3f} {median:10.3f} {mean:10.3f} {ns_call:10.1f} {rel:10.3f}x")

    print()
    print("MYPYC COMPILED")
    compiled_base = statistics.mean(compiled_times["own methods on worker"])
    print(f"{'case':42} {'best ms':>10} {'median ms':>10} {'mean ms':>10} {'ns/call':>10} {'vs own':>10} {'speedup vs py':>14}")
    for name, _ in cases:
        best, median, mean, ns_call = row_stats(compiled_times[name])
        rel = statistics.mean(compiled_times[name]) / compiled_base
        speedup = statistics.mean(py_times[name]) / statistics.mean(compiled_times[name])
        print(f"{name:42} {best:10.3f} {median:10.3f} {mean:10.3f} {ns_call:10.1f} {rel:10.3f}x {speedup:14.2f}x")

    py_winner = min(py_times, key=lambda name: statistics.mean(py_times[name]))
    compiled_winner = min(compiled_times, key=lambda name: statistics.mean(compiled_times[name]))

    print()
    print(f"Pure Python winner: {py_winner} ({statistics.mean(py_times[py_winner]) / 1_000_000:.3f} ms)")
    print(f"mypyc winner:       {compiled_winner} ({statistics.mean(compiled_times[compiled_winner]) / 1_000_000:.3f} ms)")