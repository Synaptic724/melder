"""
Warm-meld micro-benchmark for STORY-2026-10-25-creations_store_slots_by_binding.

Measures ns per call of the meld paths the store-key change touches, on whatever `melder` is first on sys.path
(PYTHONPATH=<src tree>:<repo root>), so the same script runs on the tree before the change and after it:
    unique_warm      - `root.meld(spell_id=...)` of a built `unique` (fast meld door, owner-store read)
    upc_warm         - the same for `unique_per_conduit` (caller-store read)
    many_disposal    - a disposal-bearing `many`: a new object and `register_many` per call
    plan_shared      - a `many` consumer of a `unique` and a `unique_per_conduit` (a site plan: two shared hits)
    space_cycle      - enter a spellspace, meld a `unique_per_spell_space` object (built and published per cycle), exit
    unique_by_class  - `root.meld(spell=Dep)` (fast input door by class)
Each scenario: warm-up, then REPEATS timed runs of CALLS calls; prints min and median ns per call.
"""

import statistics
import sys
import time

from melder import Aether, Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration

CALLS = 20000
REPEATS = 9
WARMUP = 3000


class Dep:
    """A `unique` dependency."""

    def close(self) -> None:
        """Disposal method."""


class DepP:
    """A `unique_per_conduit` dependency."""


class Many:
    """A disposal-bearing `many`."""

    def close(self) -> None:
        """Disposal method."""


class Consumer:
    """A `many` consumer of both dependencies."""

    def __init__(self, dep: Dep, depp: DepP) -> None:
        self.dep = dep
        self.depp = depp


class Marker:
    """A `unique_per_spell_space` object without disposal methods."""


def _world():
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    book = Spellbook(configuration=configuration)
    ids = {
        "dep": book.bind(spell=Dep, existence=Existence.unique, permissions="create",
                         disposal_method_names=["close"]),
        "depp": book.bind(spell=DepP, existence=Existence.unique_per_conduit, permissions="create"),
        "many": book.bind(spell=Many, existence=Existence.many, permissions="create",
                          disposal_method_names=["close"]),
        "consumer": book.bind(spell=Consumer, existence=Existence.many, permissions="create"),
        "marker": book.bind(spell=Marker, existence=Existence.unique_per_spell_space, permissions="create"),
    }
    root = book.conjure(name="root")
    return root, ids


def _time(fn) -> list:
    for _ in range(WARMUP):
        fn()
    runs = []
    for _ in range(REPEATS):
        start = time.perf_counter_ns()
        for _ in range(CALLS):
            fn()
        runs.append((time.perf_counter_ns() - start) / CALLS)
    return runs


def main() -> None:
    root, ids = _world()
    meld = root.meld
    dep_id, depp_id, many_id, consumer_id, marker_id = (
        ids["dep"], ids["depp"], ids["many"], ids["consumer"], ids["marker"])

    def space_cycle() -> None:
        with root.enter_spellspace() as space:
            space.meld(spell_id=marker_id)

    scenarios = [
        ("unique_warm", lambda: meld(spell_id=dep_id)),
        ("upc_warm", lambda: meld(spell_id=depp_id)),
        ("many_disposal", lambda: meld(spell_id=many_id)),
        ("plan_shared", lambda: meld(spell_id=consumer_id)),
        ("space_cycle", space_cycle),
        ("unique_by_class", lambda: meld(spell=Dep)),
    ]
    import melder
    gil = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"melder {melder.__version__} from {melder.__file__}; python {sys.version.split()[0]}; gil={gil}; "
          f"calls={CALLS} repeats={REPEATS}")
    for name, fn in scenarios:
        runs = _time(fn)
        print(f"{name:16s} min {min(runs):8.1f} ns  median {statistics.median(runs):8.1f} ns")
    root.permanent_cleanup()


if __name__ == "__main__":
    main()
