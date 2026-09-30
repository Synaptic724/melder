"""
Integration test: restoring into a live world whose first frame sealed the regime still completes (0.2.8209).

Aether now refuses a configuration whose spell-id regime differs from the one a live frame sealed. Restore
stage 1 installs the recorded root configuration whenever the live Aether is not explicitly configured - which
is also true of the default policy a live world's first frame sealed - so this guards the common case: the
recorded root configuration carries the default regime (its record holds only the logger half) and the restore
completes with the regime unchanged.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import (
    SpellbookConfiguration,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus
from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)


class SealedRegimeService:
    """Importable restore target bound in the recorded world."""

    def __init__(self) -> None:
        """Initialize the marker service."""
        self.alive: bool = True


def _reset_world() -> None:
    """Reset every world singleton and rebind the static Aether references."""
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """Isolate the test behind fresh Aether/Nexus/Crystallizer singletons."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture()
def cache_root(tmp_path, monkeypatch):
    """Route the crystallizer cache into a per-test directory."""
    from melder.crystallizer.asset_management import crystallizer_cache

    root = tmp_path / "__melder_cache__" / "__crystallizer_cache__"
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: root),
    )
    return root


def _activate_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _dynamic_book() -> Spellbook:
    """Build one dynamic-posture Spellbook with its configuration finalized first."""
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.finalize()
    return Spellbook(configuration=configuration)


def test_restore_into_a_live_world_with_a_sealed_regime_completes(cache_root) -> None:
    """
    Purpose:
        A checkpoint restored into a world whose first frame already sealed the regime
        installs its recorded root configuration and completes.
    Contract:
        The restore completes and rebuilds the spell; stage 1 installed the recorded root
        configuration (Aether is now configured); the regime in force is unchanged.
    """
    recorded_root = AetherConfiguration().with_defaults()
    recorded_root.activate()
    Aether().activate(recorded_root)
    crystallizer = _activate_crystallizer()
    book = _dynamic_book()
    book.bind(spell=SealedRegimeService, existence=Existence.unique, permissions="create")
    book.conjure(dynamic=True, name="root")
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)

    _reset_world()
    Spellbook(aetheric_frame="live_world")
    assert Aether().configured is False
    rebooted = _activate_crystallizer()
    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["spell_active"] == 1
    assert Aether().configured is True
    assert Aether().configuration.process_wide_unique_spell_ids is True
