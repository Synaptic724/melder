"""S1 conjure-cost probe: time spent in the site-graph processor strategy per conjure.

Run from the repository root: PYTHONPATH=src:. python s1_conjure_cost.py
For each override-experiment graph, conjures REPEATS fresh worlds (disk caching off, so phases 1-11 run)
and reports the median setup time (bind plus conjure), the median time inside every Phase-9 processor strategy, and the
median time inside SpellSiteGraphProcessorStrategy.process alone.
"""
import statistics
import sys
import time
from collections import defaultdict

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy_builder import (
    SpellArtifactProcessorStrategyBuilder,
)
from tests.experimentation.test_melder_creation_overrides_performance import MelderExperiment

REPEATS = 7
GRAPHS = ("shallow", "wide", "diamond", "deep")


def main() -> None:
    totals = defaultdict(float)
    counts = defaultdict(int)
    builder = SpellArtifactProcessorStrategyBuilder()
    wrapped = {}
    for name in builder.registered_strategy_names():
        strategy_type = type(builder.get_strategy(name))
        original = strategy_type.process

        def timed(self, spell, artifact, model, _original=original, _name=name):
            start = time.perf_counter_ns()
            try:
                return _original(self, spell, artifact, model)
            finally:
                totals[_name] += time.perf_counter_ns() - start
                counts[_name] += 1

        wrapped[strategy_type] = original
        strategy_type.process = timed
    builder.cleanup()
    print(f"python {sys.version.split()[0]} gil={sys._is_gil_enabled()}")
    print(f"{'graph':13} {'setup ms':>11} {'phase9 ms':>10} {'site_graph ms':>14} {'share':>14} {'calls':>6}")
    try:
        for graph in GRAPHS:
            conjure_ms, phase9_ms, site_ms, calls = [], [], [], []
            for _ in range(REPEATS):
                totals.clear()
                counts.clear()
                experiment = MelderExperiment()
                start = time.perf_counter_ns()
                experiment.setup(graph, "automatic")
                elapsed = time.perf_counter_ns() - start
                experiment.cleanup()
                conjure_ms.append(elapsed / 1e6)
                phase9_ms.append(sum(totals.values()) / 1e6)
                site_ms.append(totals["spell_site_graph_processor"] / 1e6)
                calls.append(counts["spell_site_graph_processor"])
            conj = statistics.median(conjure_ms)
            site = statistics.median(site_ms)
            print(
                f"{graph:13} {conj:11.2f} {statistics.median(phase9_ms):10.2f} {site:14.3f} "
                f"{100 * site / conj:13.2f}% {statistics.median(calls):6.0f}"
            )
    finally:
        for strategy_type, original in wrapped.items():
            strategy_type.process = original


if __name__ == "__main__":
    main()
