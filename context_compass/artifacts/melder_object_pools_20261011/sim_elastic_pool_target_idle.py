"""
Simulation: how AbstractElasticPool's steps move its variables as live instances go from 20 to 200.

Drives the real `AbstractElasticPool` (base `acquire()` / `release()`, which run stretch and decay) with
a counting subclass and a fake clock, single-threaded, so every number is exact. Prints markdown tables.

Settings compared:
    kernel  - baseline_idle 20, max_idle 20 (what SpellSpacePool and ConduitPool are built with)
    elastic - baseline_idle 20, max_idle 200 (a range for target_idle to move in); other knobs default:
              stretch 200%, settle 1800 s, decay 10% per 600 s

Scenarios:
    ramp up   - bursts of 20, 40, ... 200 live at once, then all returned, one minute apart
    ramp down - bursts of 180, 160, ... 20, ten minutes apart
    overload  - elastic only: bursts of 220 (above max_idle), ten minutes apart, for two hours

Run on a copy of `src`:
    PYTHONPATH=<copy>/src PYTHONDONTWRITEBYTECODE=1 python sim_elastic_pool_target_idle.py
"""
import sys
from typing import Any, Dict, List

from melder.utilities.general_base.abstract_elastic_pool import AbstractElasticPool


class FakeClock:
    """Monotonic clock the simulation advances by hand."""

    def __init__(self) -> None:
        """Start at zero seconds."""
        self.now = 0.0

    def __call__(self) -> float:
        """Return the current simulated time in seconds."""
        return self.now


class CountingPool(AbstractElasticPool[object]):
    """Concrete pool that counts constructions and destructions."""

    __slots__ = AbstractElasticPool.__slots__ + ["built", "destroyed"]

    def __init__(self, **kwargs: Any) -> None:
        """Forward the elastic settings and zero the counters."""
        super().__init__(**kwargs)
        self.built = 0
        self.destroyed = 0

    def create_object(self, *args: Any, **kwargs: Any) -> object:
        """Build one new object (a miss)."""
        self.built += 1
        return object()

    def destroy_object(self, obj: object) -> None:
        """Destroy one object the pool will not keep."""
        self.destroyed += 1


def burst(pool: CountingPool, live: int) -> Dict[str, Any]:
    """Take `live` objects at once, then return them all; report how each variable moved."""
    built_before = pool.built
    destroyed_before = pool.destroyed
    idle_before = pool.idle_count
    path: List[int] = [pool.target_idle]
    held = []
    for _ in range(live):
        held.append(pool.acquire())
        if pool.target_idle != path[-1]:
            path.append(pool.target_idle)
    target_after_acquire = pool.target_idle
    for obj in held:
        pool.release(obj)
    built = pool.built - built_before
    return {
        "live": live,
        "idle_before": idle_before,
        "reused": live - built,
        "built": built,
        "target_path": path,
        "target_after_acquire": target_after_acquire,
        "target_after_return": pool.target_idle,
        "idle_after": pool.idle_count,
        "destroyed": pool.destroyed - destroyed_before,
        "decay_step": pool._decay_step,
    }


def write(line: str) -> None:
    """Write one output line."""
    sys.stdout.write(line + "\n")


def table(title: str, rows: List[Dict[str, Any]], clock_marks: List[float]) -> None:
    """Print one markdown table of burst results."""
    write(f"\n### {title}\n")
    write("| t (min) | live | idle before | reused | built | target during acquire | target after return "
          "| idle kept | destroyed | decay_step |")
    write("|---|---|---|---|---|---|---|---|---|---|")
    for mark, row in zip(clock_marks, rows):
        path = " -> ".join(str(value) for value in row["target_path"])
        write(
            f"| {mark / 60:.0f} | {row['live']} | {row['idle_before']} | {row['reused']} | {row['built']} | {path} "
            f"| {row['target_after_return']} | {row['idle_after']} | {row['destroyed']} | {row['decay_step']} |"
        )


def run(label: str, max_idle: int, overload: bool) -> None:
    """Run the scenarios for one setting and print their tables."""
    clock = FakeClock()
    pool = CountingPool(baseline_idle=20, max_idle=max_idle, time_func=clock)
    up_rows, up_marks = [], []
    for live in range(20, 201, 20):
        up_marks.append(clock.now)
        up_rows.append(burst(pool, live))
        clock.now += 60.0
    table(f"{label}: ramp up, one minute apart", up_rows, up_marks)
    down_rows, down_marks = [], []
    for live in range(180, 19, -20):
        clock.now += 540.0
        down_marks.append(clock.now)
        down_rows.append(burst(pool, live))
    table(f"{label}: ramp down, ten minutes apart", down_rows, down_marks)
    if overload:
        over_rows, over_marks = [], []
        for _ in range(12):
            clock.now += 600.0
            over_marks.append(clock.now)
            over_rows.append(burst(pool, 220))
        table(f"{label}: overload (220 live, above max_idle), ten minutes apart", over_rows, over_marks)
    write(f"\n{label} totals: built {pool.built}, destroyed {pool.destroyed}, idle at end {pool.idle_count}, "
          f"target at end {pool.target_idle}")


def main() -> int:
    """Run both settings and return 0."""
    run("kernel (baseline 20, max 20)", 20, overload=False)
    run("elastic (baseline 20, max 200)", 200, overload=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
