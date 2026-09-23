"""Measure warmed, unchanged pool cycles before and after hook restoration changes."""

import argparse
import json
from pathlib import Path
import statistics
import sys
from time import perf_counter_ns

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests.component.melder.aether.conduit.test_conduit_graduation_ownership_regression import GraduationWorld


def no_op(*args: object) -> None:
    """Seed hook presence without application callback work in the measured cycle."""


def measure(mode: str, seeded: bool, iterations: int, repeats: int) -> dict[str, object]:
    """Measure real warmed pool handoffs; setup and final teardown are excluded."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    Spellbook._aether = Aether()
    Conduit._aether = Aether()
    config = SpellbookConfiguration("graduation-regression").with_defaults()
    if seeded:
        config.with_hooks(on_meld_pre_resolve=no_op, on_conduit_cleanup_start=no_op)
    world = GraduationWorld(shared_configuration=False, configuration=config)
    root = world.root
    samples: list[float] = []
    try:
        root.prewarm_lesser_conduits(2)
        root.prewarm_spellspaces(2)
        for _repeat in range(repeats):
            start = perf_counter_ns()
            if mode == "lesser":
                for _cycle in range(iterations):
                    child = root.create_lesser_conduit()
                    child.cleanup()
            elif mode == "manual_space":
                for _cycle in range(iterations):
                    space = root.create_spellspace()
                    space.cleanup()
            else:
                for _cycle in range(iterations):
                    with root.enter_spellspace():
                        pass
            samples.append((perf_counter_ns() - start) / iterations)
    finally:
        world.cleanup()
        Nexus._reset_singleton_for_tests()
        Aether._reset_singleton_for_tests()
    return {"mode": mode, "seeded": seeded, "median_ns": statistics.median(samples), "samples_ns": samples}


def main() -> None:
    """Write a labelled report with actual interpreter and single-thread conditions."""
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    results = [measure(mode, seeded, args.iterations, args.repeats)
               for seeded in (False, True) for mode in ("lesser", "manual_space", "managed_space")]
    report = {"python": sys.version, "gil_enabled": sys._is_gil_enabled(), "threads": 1,
              "iterations": args.iterations, "repeats": args.repeats, "results": results}
    Path(__file__).with_name(f"pool_{args.label}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    sys.stdout.write(json.dumps([{key: value for key, value in item.items() if key != "samples_ns"}
                               for item in results], indent=2) + "\n")


if __name__ == "__main__":
    main()
