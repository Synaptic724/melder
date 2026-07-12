"""
Normal construction versus Crystallizer recording/bootstrap profiles.

Scenarios (tiered by world size):
    - normal_world_build_unrecorded: ordinary construction baseline.
    - normal_world_build_recorded:   same construction while recording.
    - checkpoint_seal:               create_checkpoint over a recorded world.
    - cache_round_trip:              seal + flush + reload from disk.
    - checkpoint_load:               restore-only from an in-memory checkpoint.
    - bootstrap_cache_load:          disk reload plus full restore.

Run (3.14t):
    .venv_new\\Scripts\\python.exe tests/experiments/cprofile_testing/profile_crystallizer_checkpoints.py small
    .venv_new\\Scripts\\python.exe tests/experiments/cprofile_testing/profile_crystallizer_checkpoints.py medium
    .venv_new\\Scripts\\python.exe tests/experiments/cprofile_testing/profile_crystallizer_checkpoints.py large

Rot check:
    Compare profiler-free wall-clock for the two normal builds and the two
    restore paths. Use cProfile only to attribute the difference, especially
    SpellIndex bind/hydration frames; profiler time is not a speed result.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))
from profile_harness import ProfileScenario, run_scenarios

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)

_TIER_BINDS = {"small": 20, "medium": 100, "large": 400}
_TIER_BOOKS = {"small": 2, "medium": 5, "large": 10}


def _reset_world() -> None:
    """Reset every world singleton between scenario states."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _activate_crystallizer() -> Crystallizer:
    """Activate one fresh Crystallizer with benchmark source retention."""
    crystallizer = Crystallizer()
    configuration = crystallizer.create_configuration()
    configuration.set_property("user_source_root_paths", [str(_REPO_ROOT)])
    configuration.with_defaults()
    configuration.activate()
    crystallizer.activate(configuration)
    return crystallizer


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


def _make_service_matrix(tier: str):
    """Build the tier's service classes outside the measured body."""
    return [
        _make_service_classes(
            _TIER_BINDS[tier] // _TIER_BOOKS[tier],
            "{0}_{1}".format(tier, book_index),
        )
        for book_index in range(_TIER_BOOKS[tier])
    ]


def _setup_direct_world(tier: str, *, recorded: bool):
    """Prepare a fresh world for one measured direct-build pass."""
    _reset_world()
    crystallizer = _activate_crystallizer() if recorded else Crystallizer()
    return {
        "crystallizer": crystallizer,
        "tier": tier,
        "service_matrix": _make_service_matrix(tier),
        "books": [],
    }


def _setup_direct_world_unrecorded(tier: str):
    """Prepare a normal build with crystallizer recording disabled."""
    return _setup_direct_world(tier, recorded=False)


def _setup_direct_world_recorded(tier: str):
    """Prepare a normal build with crystallizer recording enabled."""
    return _setup_direct_world(tier, recorded=True)


def _build_direct_world(state) -> object:
    """Measured body: configure frames, bind spells, and conjure roots."""
    books = []
    tier = state["tier"]
    for book_index, service_classes in enumerate(state["service_matrix"]):
        frame_name = "bench_frame_{0}".format(book_index)
        book_configuration = SpellbookConfiguration(aether_frame=frame_name)
        apply_dynamic_defaults_for_spellbook_configuration(book_configuration)
        book_configuration.set_property(
            "phase_scheduler_workers_per_spellbook", 1,
        )
        book_configuration.finalize()
        book = Spellbook(
            aetheric_frame=frame_name,
            configuration=book_configuration,
        )
        for cls in service_classes:
            book.bind(spell=cls, existence=Existence.unique)
        book.conjure(dynamic=True, name="root_{0}".format(book_index))
        books.append(book)
    state["books"] = books
    return books


def _build_recorded_world(tier: str):
    """Build one dynamic world with Crystallizer recording enabled."""
    state = _setup_direct_world_recorded(tier)
    _build_direct_world(state)
    return state


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


def _setup_cached_checkpoint(tier: str):
    """Create a cached checkpoint, then return a fresh bootstrap world."""
    state = _build_recorded_world(tier)
    checkpoint_id = state["crystallizer"].create_checkpoint()
    state["crystallizer"].flush_checkpoint(checkpoint_id)
    _reset_world()
    rebooted = _activate_crystallizer()
    return {
        "crystallizer": rebooted,
        "books": [],
        "checkpoint_id": checkpoint_id,
    }


def _setup_sealed(tier: str):
    """Setup a checkpoint already decoded into a fresh restore world."""
    state = _setup_cached_checkpoint(tier)
    state["crystallizer"].reload_cached_checkpoint(state["checkpoint_id"])
    return state


def _load(state) -> None:
    """Measured body: restore an already decoded checkpoint."""
    state["crystallizer"].load_checkpoint(state["checkpoint_id"])


def _bootstrap_cache_load(state) -> None:
    """Measured body: reload a checkpoint from disk and restore its world."""
    crystallizer = state["crystallizer"]
    checkpoint_id = state["checkpoint_id"]
    crystallizer.reload_cached_checkpoint(checkpoint_id)
    crystallizer.load_checkpoint(checkpoint_id)


if __name__ == "__main__":
    tier_argument = sys.argv[1] if len(sys.argv) > 1 else "small"
    run_scenarios(
        [
            ProfileScenario(
                "normal_world_build_unrecorded",
                _setup_direct_world_unrecorded, _build_direct_world, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
            ProfileScenario(
                "normal_world_build_recorded",
                _setup_direct_world_recorded, _build_direct_world, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
            ProfileScenario(
                "crystallizer_checkpoint_seal",
                _build_recorded_world, _seal, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
            ProfileScenario(
                "crystallizer_cache_round_trip",
                _build_recorded_world, _cache_round_trip, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
            ProfileScenario(
                "crystallizer_checkpoint_load",
                _setup_sealed, _load, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
            ProfileScenario(
                "crystallizer_bootstrap_cache_load",
                _setup_cached_checkpoint, _bootstrap_cache_load, _teardown,
                repeats=3, fresh_state_per_run=True,
            ),
        ],
        tier=tier_argument,
    )
