"""
Crystallizer checkpoint save/load profiles (the slow-test suspects).

Scenarios (tiered by world size):
    - checkpoint_seal:    create_checkpoint over a recorded dynamic world.
    - cache_round_trip:   flush_checkpoint + reload_cached_checkpoint.
    - checkpoint_load:    load_checkpoint (full RestoreEngine unfold) - the
                          scenario the owner's slow tests point at.

Run (3.14t):
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py small
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py medium
    python benchmarks/cprofile_testing/profile_crystallizer_checkpoints.py large

Rot check:
    tiers scale binds 20 -> 100 -> 400 (x5, x4). If checkpoint_load's
    best-seconds ratio grows faster than the tier ratio, open the .prof and
    look at the tottime table: fold/preflight/emit frames growing
    super-linearly are the finding.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from profile_harness import ProfileScenario, run_scenarios

from melder.aether.aether import Aether
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer

_TIER_BINDS = {"small": 20, "medium": 100, "large": 400}
_TIER_BOOKS = {"small": 2, "medium": 5, "large": 10}


def _reset_world() -> None:
    """Reset the Aether singleton world between scenario states."""
    if Aether._instance is not None:
        try:
            Aether().cleanup()
        except Exception:
            pass
    Aether._instance = None
    Aether._initialized = False
    aether = Aether()
    Spellbook._aether = aether
    from melder.aether.conduit.conduit import Conduit
    Conduit._aether = aether


def _make_service_classes(count: int, stamp: str):
    """Mint `count` distinct service classes so binds carry real content."""
    classes = []
    for index in range(count):
        namespace = {}
        source = (
            "class Service_{0}_{1}:\n"
            "    def value(self) -> int:\n"
            "        return {1}\n"
        ).format(stamp, index)
        exec(source, namespace)
        classes.append(namespace["Service_{0}_{1}".format(stamp, index)])
    return classes


def _build_recorded_world(tier: str):
    """
    Build one dynamic, crystallizer-recorded world at tier size.

    Returns:
        Dict[str, object]: {crystallizer, books, checkpoint_id (unsealed)}.
    """
    _reset_world()
    crystallizer = Crystallizer()
    configuration = crystallizer.create_configuration()
    configuration.set_property("user_source_root_paths", [str(Path.cwd())])
    configuration.with_defaults()
    crystallizer.configure(configuration)
    crystallizer.activate()
    books = []
    for book_index in range(_TIER_BOOKS[tier]):
        book_configuration = SpellbookConfiguration()
        book_configuration.load_default_dictionary()
        book_configuration.set_property("system_state", "dynamic")
        book_configuration.set_property(
            "phase_scheduler_workers_per_spellbook", 1,
        )
        book = Spellbook(
            aetheric_frame="bench_frame_{0}".format(book_index),
            configuration=book_configuration,
        )
        for cls in _make_service_classes(
                _TIER_BINDS[tier] // _TIER_BOOKS[tier],
                "{0}_{1}".format(tier, book_index),
        ):
            book.bind(cls)
        book.conjure(dynamic=True, name="root_{0}".format(book_index))
        books.append(book)
    return {"crystallizer": crystallizer, "books": books}


def _teardown(state) -> None:
    """Tear the bench world down (best-effort, harness-reported)."""
    _reset_world()


def _seal(state) -> object:
    """Measured body: seal one checkpoint over the recorded world."""
    return state["crystallizer"].create_checkpoint()


def _cache_round_trip(state) -> None:
    """Measured body: flush every checkpoint then reload from cache."""
    crystallizer = state["crystallizer"]
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    crystallizer.reload_cached_checkpoint(checkpoint_id)


def _setup_sealed(tier: str):
    """Setup for load: recorded world + one sealed checkpoint id."""
    state = _build_recorded_world(tier)
    state["checkpoint_id"] = state["crystallizer"].create_checkpoint()
    return state


def _load(state) -> None:
    """Measured body: full RestoreEngine unfold of the sealed checkpoint."""
    state["crystallizer"].load_checkpoint(state["checkpoint_id"])


if __name__ == "__main__":
    tier_argument = sys.argv[1] if len(sys.argv) > 1 else "small"
    run_scenarios(
        [
            ProfileScenario(
                "crystallizer_checkpoint_seal",
                _build_recorded_world, _seal, _teardown,
            ),
            ProfileScenario(
                "crystallizer_cache_round_trip",
                _build_recorded_world, _cache_round_trip, _teardown,
            ),
            ProfileScenario(
                "crystallizer_checkpoint_load",
                _setup_sealed, _load, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
        ],
        tier=tier_argument,
    )
