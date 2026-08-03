"""
Shared cProfile harness for Melder performance scenarios.

Purpose:
    One consistent way to answer two different questions about a scenario:
    - WHERE does time go (cProfile -> .prof dump + pstats top tables)
    - HOW MUCH time does it take (profiler-free wall-clock repeats, so the
      profiler's own overhead never distorts the conclusion)

Rot-finding method:
    Every scenario runs at declared size tiers. Compare the wall-clock ratio
    between tiers against the tier size ratio: linear work tracks the size
    ratio; anything growing faster than its tier ratio is the rot signal, and
    the paired .prof names the frames responsible.

Usage:
    Scenario scripts build a `ProfileScenario` per (name, setup, action) and
    call `run_scenarios([...], tier="small|medium|large")`. Outputs land in
    `tests/experiments/cprofile_testing/results/<scenario>__<tier>.prof` plus a
    plain-text report beside it.

Threading:
    Scenarios run on the calling thread. Runtimes under test own their own
    locking (3.14t no-GIL); the harness adds no synchronization of its own.
"""

import cProfile
import io
import pstats
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional


class ProfileScenario:
    """
    One named, tiered, profile-able scenario.

    Contract:
        - `setup(tier)` builds and returns the scenario state (a context dict);
          setup cost is EXCLUDED from both measurements.
        - `action(state)` is the measured body; it must be re-runnable when
          `repeats > 1` (build fresh state per repeat via `fresh_state_per_run`
          when the action mutates the world irreversibly).
        - `teardown(state)` always runs, best-effort, after measurement.
    """

    def __init__(
            self,
            name: str,
            setup: Callable[[str], Dict[str, object]],
            action: Callable[[Dict[str, object]], object],
            teardown: Optional[Callable[[Dict[str, object]], None]] = None,
            repeats: int = 3,
            fresh_state_per_run: bool = False,
    ) -> None:
        """
        Initialize one scenario definition.

        Args:
            name: Report/file identity for the scenario.
            setup: Tier-aware state builder (excluded from measurement).
            action: The measured body.
            teardown: Optional best-effort cleanup for one state dict.
            repeats: Wall-clock repeat count (best-of reported).
            fresh_state_per_run: Rebuild state before every repeat when the
                action consumes its world (e.g. a checkpoint load).
        """
        self.name = name
        self.setup = setup
        self.action = action
        self.teardown = teardown
        self.repeats = repeats
        self.fresh_state_per_run = fresh_state_per_run

    def _run_teardown(self, state: Dict[str, object]) -> None:
        """Best-effort teardown; failures are reported, never raised."""
        if self.teardown is None:
            return
        try:
            self.teardown(state)
        except Exception as error:
            print("  teardown warning ({0}): {1}".format(self.name, error))

    def run(self, tier: str, results_dir: Path) -> Dict[str, object]:
        """
        Measure this scenario at one tier; write .prof + text report.

        Returns:
            Dict[str, object]: {name, tier, best_seconds, all_seconds,
            profile_path} for the tier-comparison table.
        """
        # Leg 1: profiler-free wall-clock repeats (the honest duration).
        durations: List[float] = []
        state = self.setup(tier)
        try:
            for index in range(self.repeats):
                if self.fresh_state_per_run and index > 0:
                    self._run_teardown(state)
                    state = self.setup(tier)
                started = time.perf_counter()
                self.action(state)
                durations.append(time.perf_counter() - started)
        finally:
            self._run_teardown(state)

        # Leg 2: one profiled run (where the time goes).
        state = self.setup(tier)
        profiler = cProfile.Profile()
        try:
            profiler.activate()
            self.action(state)
            profiler.disable()
        finally:
            self._run_teardown(state)

        results_dir.mkdir(parents=True, exist_ok=True)
        profile_path = results_dir / "{0}__{1}.prof".format(self.name, tier)
        profiler.dump_stats(str(profile_path))

        text_buffer = io.StringIO()
        stats = pstats.Stats(profiler, stream=text_buffer)
        text_buffer.write("== {0} [{1}] ==\n".format(self.name, tier))
        text_buffer.write(
            "wall-clock repeats: {0}\nbest: {1:.6f}s  all: {2}\n\n".format(
                self.repeats,
                min(durations),
                ["{0:.6f}".format(value) for value in durations],
            )
        )
        text_buffer.write("-- top 25 by cumulative --\n")
        stats.sort_stats("cumulative").print_stats(25)
        text_buffer.write("\n-- top 25 by tottime (self time = the rot) --\n")
        stats.sort_stats("tottime").print_stats(25)
        report_path = results_dir / "{0}__{1}.txt".format(self.name, tier)
        report_path.write_text(text_buffer.getvalue(), encoding="utf-8")
        print(
            "  {0} [{1}]: best {2:.6f}s -> {3}".format(
                self.name, tier, min(durations), profile_path.name
            )
        )
        return {
            "name": self.name,
            "tier": tier,
            "best_seconds": min(durations),
            "all_seconds": durations,
            "profile_path": str(profile_path),
        }


def run_scenarios(
        scenarios: List[ProfileScenario],
        tier: str,
        results_dir: Optional[Path] = None,
) -> List[Dict[str, object]]:
    """
    Run every scenario at one tier and print the summary table.

    Args:
        scenarios: Scenario definitions to measure.
        tier: "small" | "medium" | "large".
        results_dir: Output root; defaults to ./results beside the caller.

    Returns:
        List[Dict[str, object]]: Per-scenario measurement rows.
    """
    resolved_dir = results_dir or (Path(__file__).parent / "results")
    rows = [scenario.run(tier, resolved_dir) for scenario in scenarios]
    print("\n== summary [{0}] ==".format(tier))
    for row in rows:
        print(
            "  {0:<44} best {1:.6f}s".format(
                str(row["name"]), float(str(row["best_seconds"])),
            )
        )
    return rows
