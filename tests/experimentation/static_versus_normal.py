from time import perf_counter_ns
import gc
import random
import statistics
import sys


class OwnMethodWorker:
    __slots__ = ("offset",)

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


class CachedStaticHelperWorker:
    __slots__ = ("a", "b", "c", "d")

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


class CachedStaticLocalWorker:
    __slots__ = ("a", "b", "c", "d")

    def __init__(self) -> None:
        self.a = StaticHelper.a
        self.b = StaticHelper.b
        self.c = StaticHelper.c
        self.d = StaticHelper.d

    def run(self, x: int) -> int:
        a = self.a
        b = self.b
        c = self.c
        d = self.d

        x = a(x)
        x = b(x)
        x = c(x)
        x = d(x)
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


class CachedModuleFunctionWorker:
    __slots__ = ("a", "b", "c", "d")

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


def bench_worker(worker: object, iterations: int) -> tuple[int, int]:
    # For this benchmark, every worker has a concrete .run method.
    # Using a direct attribute read here keeps the benchmark focused on the inner helper shape.
    run = worker.run

    result = 0
    start = perf_counter_ns()

    for i in range(iterations):
        result += run(i)

    elapsed = perf_counter_ns() - start
    return elapsed, result


def summarize(name: str, times: list[int], iterations: int) -> dict[str, float | str]:
    mean_ns = statistics.mean(times)
    median_ns = statistics.median(times)
    best_ns = min(times)

    return {
        "case": name,
        "best_ms": best_ns / 1_000_000,
        "median_ms": median_ns / 1_000_000,
        "mean_ms": mean_ns / 1_000_000,
        "mean_ns_per_outer_call": mean_ns / iterations,
        "mean_ns_per_inner_method": mean_ns / (iterations * 4),
    }


iterations = 100_000
repeats = 50

workers = [
    ("own methods on worker", OwnMethodWorker(5)),
    ("delegates to instance helper", InstanceHelperWorker(InstanceHelper(5))),
    ("delegates to static helper class", StaticHelperWorker()),
    ("cached static funcs on worker attrs", CachedStaticHelperWorker()),
    ("cached static funcs as locals in run", CachedStaticLocalWorker()),
    ("delegates to module functions", ModuleFunctionWorker()),
    ("cached module funcs on worker attrs", CachedModuleFunctionWorker()),
]

times_by_name: dict[str, list[int]] = {name: [] for name, _ in workers}
results_by_name: dict[str, int] = {}

for _, worker in workers:
    for _ in range(5):
        bench_worker(worker, iterations)

gc_was_enabled = gc.isenabled()
gc.deactivate()

try:
    for _ in range(repeats):
        shuffled_workers = workers[:]
        random.shuffle(shuffled_workers)

        for name, worker in shuffled_workers:
            elapsed, result = bench_worker(worker, iterations)
            times_by_name[name].append(elapsed)
            results_by_name[name] = result
finally:
    if gc_was_enabled:
        gc.activate()

rows = [
    summarize(name, times_by_name[name], iterations)
    for name, _ in workers
]

baseline_mean = statistics.mean(times_by_name["own methods on worker"])

print(f"Python: {sys.version}")
print(f"Iterations per timed run: {iterations:,}")
print(f"Timed repeats: {repeats}")
print()
print("Result sanity check:")
for name, result in results_by_name.items():
    print(f"  {name:38} {result}")

print()
print(f"{'case':42} {'best ms':>10} {'median ms':>10} {'mean ms':>10} {'ns/outer':>12} {'ns/inner':>12} {'vs own':>10}")
for row in rows:
    case = str(row["case"])
    case_mean = statistics.mean(times_by_name[case])
    print(
        f"{case:42} "
        f"{row['best_ms']:10.3f} "
        f"{row['median_ms']:10.3f} "
        f"{row['mean_ms']:10.3f} "
        f"{row['mean_ns_per_outer_call']:12.1f} "
        f"{row['mean_ns_per_inner_method']:12.1f} "
        f"{case_mean / baseline_mean:10.3f}x"
    )

winner_name = min(times_by_name, key=lambda name: statistics.mean(times_by_name[name]))
winner_mean = statistics.mean(times_by_name[winner_name])

print()
print(f"Winner by mean: {winner_name}")
print(f"Winner mean: {winner_mean / 1_000_000:.3f} ms per {iterations:,} calls")