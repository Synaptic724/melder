"""
Warm-meld micro-benchmark for the slotted_lifetime lane (EPIC-2026-10-14-slotted_lifetime_ownership_fixes, end of pass).

Times warm `Conduit.meld` by id for one `unique`, one `unique_per_conduit` and one `unique_per_conduit_cluster` spell
(the cluster store moved to the cluster in 0.2.8237), on a dynamic root that leads its cluster. Prints the median and
min of 7 repeats of 100,000 melds per kind, in ns per meld. Run the same file against the base and the fixed tree:
    PYTHONPATH=<tree>/src:<tree> python bench_warm_meld_lane.py <label>
"""
import statistics
import sys
import time
from typing import Dict, List

from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class BenchUnique:
    """`unique` spell."""


class BenchPerConduit:
    """`unique_per_conduit` spell."""


class BenchCluster:
    """`unique_per_conduit_cluster` spell."""


def main() -> int:
    """Build the world, warm each spell once, then time warm melds."""
    configuration = SpellbookConfiguration(aether_frame="bench")
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(aetheric_frame="bench", configuration=configuration)
    ids = {
        "unique": book.bind(spell=BenchUnique, existence=Existence.unique, permissions="create"),
        "unique_per_conduit": book.bind(spell=BenchPerConduit, existence=Existence.unique_per_conduit,
                                        permissions="create"),
        "unique_per_conduit_cluster": book.bind(spell=BenchCluster, existence=Existence.unique_per_conduit_cluster,
                                                permissions="create"),
    }
    root = book.conjure(dynamic=True, name="bench-root")
    cloud = Spellbook._aether.get_conduit_cloud("bench")
    cloud.create_cluster("bench")
    cloud.add_conduit_to_cluster(root, "bench")
    cloud.get_cluster("bench").elect_leader(root.id)
    results: Dict[str, List[float]] = {}
    for kind, spell_id in ids.items():
        first = root.meld(spell_id=spell_id)
        assert root.meld(spell_id=spell_id) is first
        meld = root.meld
        samples: List[float] = []
        for _ in range(7):
            start = time.perf_counter_ns()
            for _ in range(100_000):
                meld(spell_id=spell_id)
            samples.append((time.perf_counter_ns() - start) / 100_000)
        results[kind] = samples
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    for kind, samples in results.items():
        print(f"{label} | {kind} | median {statistics.median(samples):.1f} ns | min {min(samples):.1f} ns")
    root.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
