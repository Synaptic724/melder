"""Measure one real integration-shaped creation against Crystallizer bootstrap.

This is an experiment, not a pytest test. It uses the file-backed RestoreAlpha
target from the integration suite so CrystalAnalyzer sees the same dependency
graph that makes those tests slow.

Run:
    .venv_new\\Scripts\\python.exe tests\\experiments\\cprofile_testing\\trace_creation_vs_bootstrap.py
"""

import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "src"))

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management.crystallizer_cache import (
    CrystallizerCache,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
from tests.integration.melder.crystallizer.test_crystallizer_restore_integration import (
    RestoreAlpha,
)


def _reset_world() -> None:
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _activate_crystallizer() -> Crystallizer:
    crystallizer = Crystallizer()
    configuration = crystallizer.create_configuration().with_defaults()
    configuration.activate()
    crystallizer.activate(configuration)
    return crystallizer


def _build_world(*, recorded: bool):
    crystallizer = _activate_crystallizer() if recorded else Crystallizer()
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    book = Spellbook(configuration=configuration)
    spell_id = book.bind(
        spell=RestoreAlpha,
        existence=Existence.unique,
        permissions="create",
    )
    book.conjure(dynamic=True, name="experiment-root")
    return crystallizer, book, spell_id


def _timed(label, operation):
    started = time.perf_counter()
    value = operation()
    elapsed = time.perf_counter() - started
    print("{0:<36} {1:>9.6f}s".format(label, elapsed), flush=True)
    return elapsed, value


def main() -> None:
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
            prefix="creation_vs_bootstrap_", dir=results_dir,
    ) as cache_directory:
        cache_root = Path(cache_directory)
        CrystallizerCache.resolve_cache_root_path = staticmethod(
            lambda: cache_root
        )

        # Warm the compiler cache before either side of the comparison.
        _reset_world()
        _build_world(recorded=False)
        _reset_world()

        normal_seconds, _normal = _timed(
            "normal_create_world",
            lambda: _build_world(recorded=False),
        )
        _timed("normal_world_cleanup", _reset_world)

        recorded_seconds, recorded = _timed(
            "recorded_create_world",
            lambda: _build_world(recorded=True),
        )
        crystallizer, _book, _spell_id = recorded
        seal_seconds, checkpoint_id = _timed(
            "checkpoint_seal", crystallizer.create_checkpoint,
        )
        flush_seconds, _ = _timed(
            "checkpoint_flush",
            lambda: crystallizer.flush_checkpoint(checkpoint_id),
        )

        reset_seconds, _ = _timed("fresh_boot_reset", _reset_world)
        activation_seconds, rebooted = _timed(
            "fresh_boot_activation", _activate_crystallizer,
        )
        reload_seconds, _ = _timed(
            "bootstrap_cache_reload",
            lambda: rebooted.reload_cached_checkpoint(checkpoint_id),
        )
        restore_seconds, _ = _timed(
            "bootstrap_restore",
            lambda: rebooted.load_checkpoint(checkpoint_id),
        )

        print("", flush=True)
        print(
            "recording_tax_ratio                  {0:>9.3f}x".format(
                recorded_seconds / normal_seconds
            ),
            flush=True,
        )
        print(
            "bootstrap_reload_plus_restore_ratio  {0:>9.3f}x".format(
                (reload_seconds + restore_seconds) / normal_seconds
            ),
            flush=True,
        )
        print(
            "full_boot_ratio                      {0:>9.3f}x".format(
                (
                    reset_seconds
                    + activation_seconds
                    + reload_seconds
                    + restore_seconds
                ) / normal_seconds
            ),
            flush=True,
        )
        print(
            "checkpoint_transport_seconds         {0:>9.6f}s".format(
                seal_seconds + flush_seconds
            ),
            flush=True,
        )

        _reset_world()


if __name__ == "__main__":
    main()
