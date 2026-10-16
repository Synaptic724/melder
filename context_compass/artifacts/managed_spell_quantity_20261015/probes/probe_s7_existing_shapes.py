"""S7 benchmark: the existing meld shapes and scope cycles, runnable on any tree from 0.2.8240 on.

Each arm reports ns per cycle; a cycle is one meld, or one scope opened, used and closed. Arms run interleaved per
round inside the process; the A/B runner alternates processes between the trees.
  unique            auto root: meld(spell=Single)                 (the stored object)
  many              auto root: meld(spell=Fresh)                  (a new object per meld)
  per_conduit       auto root: meld(spell=PerConduit)             (the conduit's stored object)
  many_of_many      auto root: meld(spell=FreshHolder)            (two constructions)
  many_of_unique    auto root: meld(spell=SingleHolder)           (one construction, one stored read)
  override          auto root: meld(spell=FreshHolder, override)  (a key-set plan; the supplied child is used)
  by_name           auto root: meld("Fresh")                      (the name door)
  dyn_many          dynamic root: meld(spell=DynFresh)
  dyn_unique        dynamic root: meld(spell=DynSingle)
  lesser_cycle      auto root: create_lesser_conduit(), meld a disposal-bearing many, cleanup() (pool return)
  space_cycle       auto root: with enter_spellspace() as s: s.meld(spell=PerSpace) (a unique_per_spell_space)
Run from the tree root: PYTHONPATH=src:. python -X gil=0|1 probe_s7_existing_shapes.py [cycles] [rounds]
"""
import statistics
import sys
import time

import melder
from melder import Existence, Spellbook
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from tests._frame_posture_test_support import apply_dynamic_defaults_for_spellbook_configuration


class Single:
    """Bound `unique`."""

    def __init__(self) -> None:
        self.value = 0


class Fresh:
    """Bound `many`."""

    def __init__(self) -> None:
        self.value = 0


class PerConduit:
    """Bound `unique_per_conduit`."""

    def __init__(self) -> None:
        self.value = 0


class FreshHolder:
    """A `many` holder of one `many` Fresh."""

    def __init__(self, fresh: Fresh) -> None:
        self.fresh = fresh


class SingleHolder:
    """A `many` holder of the `unique` Single."""

    def __init__(self, single: Single) -> None:
        self.single = single


class Closable:
    """A `many` with a disposal method, melded in lesser scopes."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        """Disposal method."""
        self.closed = True


class PerSpace:
    """Bound `unique_per_spell_space`."""

    def __init__(self) -> None:
        self.value = 0


class DynFresh:
    """Bound `many` in the dynamic world."""

    def __init__(self) -> None:
        self.value = 0


class DynSingle:
    """Bound `unique` in the dynamic world."""

    def __init__(self) -> None:
        self.value = 0


def _dynamic_book(frame: str) -> Spellbook:
    configuration = SpellbookConfiguration(aether_frame=frame)
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def main() -> None:
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    scope_cycles = max(1, cycles // 20)
    book = Spellbook()
    book.bind(spell=Single, existence=Existence.unique, permissions="create")
    book.bind(spell=Fresh, existence=Existence.many, permissions="create")
    book.bind(spell=PerConduit, existence=Existence.unique_per_conduit, permissions="create")
    book.bind(spell=FreshHolder, existence=Existence.many, permissions="create")
    book.bind(spell=SingleHolder, existence=Existence.many, permissions="create")
    book.bind(spell=Closable, existence=Existence.many, permissions="create", disposal_method_names=["close"])
    book.bind(spell=PerSpace, existence=Existence.unique_per_spell_space, permissions="create")
    root = book.conjure(name="s7_shapes_auto")
    dyn_book = _dynamic_book("s7_shapes_dynamic")
    dyn_book.bind(spell=DynFresh, existence=Existence.many, permissions="create")
    dyn_book.bind(spell=DynSingle, existence=Existence.unique, permissions="create")
    dyn_root = dyn_book.conjure(dynamic=True, name="s7_shapes_dyn")
    meld = root.meld
    dyn_meld = dyn_root.meld
    supplied = Fresh()
    override = {"fresh": supplied}

    def timed(body, n):
        def arm() -> float:
            start = time.perf_counter_ns()
            body(n)
            return (time.perf_counter_ns() - start) / n
        return arm

    def unique(n):
        for _ in range(n):
            meld(spell=Single)

    def many(n):
        for _ in range(n):
            meld(spell=Fresh)

    def per_conduit(n):
        for _ in range(n):
            meld(spell=PerConduit)

    def many_of_many(n):
        for _ in range(n):
            meld(spell=FreshHolder)

    def many_of_unique(n):
        for _ in range(n):
            meld(spell=SingleHolder)

    def overridden(n):
        for _ in range(n):
            meld(spell=FreshHolder, override=override)

    def by_name(n):
        for _ in range(n):
            meld("Fresh")

    def dyn_many(n):
        for _ in range(n):
            dyn_meld(spell=DynFresh)

    def dyn_unique(n):
        for _ in range(n):
            dyn_meld(spell=DynSingle)

    def lesser_cycle(n):
        create = root.create_lesser_conduit
        for _ in range(n):
            lesser = create()
            lesser.meld(spell=Closable)
            lesser.cleanup()

    def space_cycle(n):
        enter = root.enter_spellspace
        for _ in range(n):
            with enter() as space:
                space.meld(spell=PerSpace)

    arms = {
        "unique": timed(unique, cycles),
        "many": timed(many, cycles),
        "per_conduit": timed(per_conduit, cycles),
        "many_of_many": timed(many_of_many, cycles),
        "many_of_unique": timed(many_of_unique, cycles),
        "override": timed(overridden, cycles),
        "by_name": timed(by_name, cycles),
        "dyn_many": timed(dyn_many, cycles),
        "dyn_unique": timed(dyn_unique, cycles),
        "lesser_cycle": timed(lesser_cycle, scope_cycles),
        "space_cycle": timed(space_cycle, scope_cycles),
    }
    for arm in arms.values():
        arm()  # warm: first melds compile, pools fill
    results = {name: [] for name in arms}
    for _ in range(rounds):
        for name, arm in arms.items():
            results[name].append(arm())
    gil = "enabled" if sys._is_gil_enabled() else "disabled"
    print(f"python {sys.version.split()[0]} gil={gil} melder={melder.__version__} cycles={cycles} rounds={rounds}")
    for name, values in results.items():
        print(f"ARM {name} min {min(values):.1f} median {statistics.median(values):.1f}")
    assert meld(spell=FreshHolder, override=override).fresh is supplied
    dyn_root.cleanup()
    dyn_book.cleanup()
    root.cleanup()
    book.cleanup()


if __name__ == "__main__":
    main()
