"""
commandops-shaped roots measured live: what a real application's `many` roots pay per meld, and what disposal costs.

WHY THIS EXISTS
    The commandops creation cache (`melc_cache_ledger.py` over its `__melder_cache__`) has exactly two kinds of
    root that run a plan per meld: a width-1 `many` root over one unique service (Worker(manager)) and a width-5
    `many` root over four existing objects and one unique service (ContextRoot(...)), both registering for
    disposal on every creation. This file rebuilds those two shapes with and without a disposal method, melds
    them by name through the front door and prints ns per meld with the Python/C call counts, plain and with the
    opt-in singleton specializer, plus a warm unique meld and an existing-object meld for scale.

RUN (3.14t target; caching off, nothing is written)
    python -X gil=0 tests/experimentation/commandops_shape_probe.py
"""

import os
import statistics
import sys
import time
from typing import Callable, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


class Config:
    """Existing object bound as an instance under `spellframe="Config"`."""

    def __init__(self, n: int) -> None:
        self.n = n


class Builders:
    """Existing object."""

    def __init__(self, n: int) -> None:
        self.n = n


class Resources:
    """Existing object."""

    def __init__(self, n: int) -> None:
        self.n = n


class Utilities:
    """Existing object."""

    def __init__(self, n: int) -> None:
        self.n = n


class Spectrum:
    """Unique service with a disposal method."""

    def __init__(self) -> None:
        self.state = 0

    def cleanup(self) -> None:
        """Disposal method named by the configuration."""
        self.state = -1


class Manager:
    """Unique service with a disposal method."""

    def __init__(self) -> None:
        self.state = 0

    def cleanup(self) -> None:
        """Disposal method named by the configuration."""
        self.state = -1


class Worker:
    """commandops' width-1 many root with disposal: Worker(manager)."""

    def __init__(self, manager: Manager) -> None:
        self.manager = manager

    def cleanup(self) -> None:
        """Disposal method named by the configuration."""
        self.manager = None


class WorkerNoDisposal:
    """The same root without a disposal method (no registration is emitted)."""

    def __init__(self, manager: Manager) -> None:
        self.manager = manager


class ContextRoot:
    """commandops' width-5 many root: four existing objects plus one unique service, with disposal."""

    def __init__(
            self,
            context_config: Config,
            builders: Builders,
            resources: Resources,
            utilities: Utilities,
            spectrum: Spectrum,
    ) -> None:
        self.context_config = context_config
        self.builders = builders
        self.resources = resources
        self.utilities = utilities
        self.spectrum = spectrum

    def cleanup(self) -> None:
        """Disposal method named by the configuration."""
        self.spectrum = None


class ContextRootNoDisposal:
    """The width-5 root without a disposal method."""

    def __init__(
            self,
            context_config: Config,
            builders: Builders,
            resources: Resources,
            utilities: Utilities,
            spectrum: Spectrum,
    ) -> None:
        self.context_config = context_config
        self.builders = builders
        self.resources = resources
        self.utilities = utilities
        self.spectrum = spectrum


def build_world(specializer: bool) -> Tuple[Spellbook, Conduit]:
    """Bind the commandops shapes into a fresh automatic world and conjure its root conduit."""
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    configuration = SpellbookConfiguration()
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=False)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    if specializer:
        configuration.set_property("generalized_singleton_specialization_enabled", True)
    book = Spellbook(configuration=configuration)
    book.configure_aether_frame(
        system_state=None, disposal=None, disposal_method_names=None, system_caching_enabled=False,
    )
    book.bind(spell=Config(1), spellframe="Config", existence=Existence.unique, permissions="create")
    book.bind(spell=Builders(2), spellframe=Builders, existence=Existence.unique, permissions="create")
    book.bind(spell=Resources(3), spellframe=Resources, existence=Existence.unique, permissions="create")
    book.bind(spell=Utilities(4), spellframe=Utilities, existence=Existence.unique, permissions="create")
    book.bind(spell=Spectrum, existence=Existence.unique, permissions="create")
    book.bind(spell=Manager, existence=Existence.unique, permissions="create")
    for cls in (Worker, WorkerNoDisposal, ContextRoot, ContextRootNoDisposal):
        book.bind(spell=cls, existence=Existence.many, permissions="create")
    conduit = book.conjure(name=f"cops-{int(specializer)}-root", dynamic=False)
    return book, conduit


def time_ns(fn: Callable[[], object], n: int = 60000, reps: int = 3, warm: int = 20000) -> float:
    """Median ns per call over `reps` batches of `n` calls after `warm` warm-up calls."""
    for _ in range(warm):
        fn()
    samples = []
    for _ in range(reps):
        start = time.perf_counter_ns()
        for _ in range(n):
            fn()
        samples.append((time.perf_counter_ns() - start) / n)
    return statistics.median(samples)


def call_counts(fn: Callable[[], object]) -> Tuple[int, int]:
    """Python and C call counts of one call of `fn`, the profiler's own entry excluded."""
    counts = {"call": 0, "c_call": 0}

    def profile(frame: object, event: str, arg: object) -> None:
        if event in counts:
            counts[event] += 1

    sys.setprofile(profile)
    try:
        fn()
    finally:
        sys.setprofile(None)
    return counts["call"] - 1, counts["c_call"] - 1


def main() -> None:
    """Print the ns-per-meld table for the commandops shapes, plain and with the specializer."""
    print("| root (commandops shape) | specializer | ns/meld by name | py | C |")
    print("| --- | --- | ---: | ---: | ---: |")
    for specializer in (False, True):
        book, conduit = build_world(specializer)
        mode = "on" if specializer else "off"
        try:
            conduit.meld("Spectrum")
            conduit.meld("Manager")
            for name in ("Worker", "WorkerNoDisposal", "ContextRoot", "ContextRootNoDisposal"):
                meld: Callable[[], object] = lambda name=name: conduit.meld(name)
                assert type(meld()).__name__ == name
                ns = time_ns(meld)
                py_calls, c_calls = call_counts(meld)
                print(f"| {name} | {mode} | {ns:.0f} | {py_calls} | {c_calls} |")
            print(f"| Spectrum (unique, warm) | {mode} | {time_ns(lambda: conduit.meld('Spectrum')):.0f} | | |")
            print(f"| Config (existing object) | {mode} | {time_ns(lambda: conduit.meld('Config')):.0f} | | |")
        finally:
            conduit.cleanup()
            book.cleanup()


if __name__ == "__main__":
    main()
