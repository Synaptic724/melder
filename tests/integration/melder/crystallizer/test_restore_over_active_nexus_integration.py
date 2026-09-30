"""
Integration tests: restoring a recorded Nexus into a world whose Nexus is already active (0.2.8210).

An active Nexus now refuses reconfiguration (`configure`, or `activate` handed another configuration). Restore
stage 4 rebuilds the recorded Nexus by activating a freshly reloaded configuration on the hosted Nexus, so a
live-world load over an active Nexus would have been refused and rolled back. Stage 4 now deactivates an active
Nexus first - a truthful recorded act, exactly as stage 3 does for MutationResearch - and these tests pin that a
world-scope load still replaces the live Nexus policy with the recorded one, and replays a recorded "disabled".

Runs only on 3.14t (melder package root import chain).
"""
from pathlib import Path
from typing import Iterator

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.configuration.nexus_configuration import NexusConfiguration
from melder.nexus.nexus import Nexus


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
def reset_world_singletons() -> Iterator[None]:
    """Isolate each test behind fresh Aether/Nexus/Crystallizer singletons."""
    _reset_world()
    yield
    _reset_world()


@pytest.fixture()
def cache_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
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


def _nexus_policy(max_active_rift_count: int) -> NexusConfiguration:
    """Return a mutable default Nexus policy with a distinguishing Rift cap."""
    return NexusConfiguration().with_defaults().with_max_active_rift_count(max_active_rift_count)


def _record_a_nexus_world(deactivate_before_seal: bool) -> str:
    """Record a world whose Nexus ran with a Rift cap of 5; return the flushed checkpoint id."""
    crystallizer = _activate_crystallizer()
    Nexus().activate(_nexus_policy(5))
    if deactivate_before_seal:
        Nexus().deactivate()
    checkpoint_id = crystallizer.create_checkpoint()
    crystallizer.flush_checkpoint(checkpoint_id)
    return checkpoint_id


def _reboot_with_an_active_host_nexus() -> Crystallizer:
    """Simulate a new process whose host brought its own Nexus live (Rift cap 2) before the load."""
    _reset_world()
    rebooted = _activate_crystallizer()
    Nexus().activate(_nexus_policy(2))
    assert Nexus().activated is True
    return rebooted


def test_restore_replaces_an_active_live_nexus_policy_with_the_recorded_one(cache_root: Path) -> None:
    """
    Purpose:
        A world-scope load over a live, active Nexus completes and leaves the recorded policy in force.
    Contract:
        The report completes with one nexus build; the Nexus is active under the recorded Rift cap, and the
        host's policy object is no longer installed.
    """
    checkpoint_id = _record_a_nexus_world(deactivate_before_seal=False)
    rebooted = _reboot_with_an_active_host_nexus()
    host_policy = Nexus().configuration

    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["nexus"] == 1
    assert Nexus().activated is True
    assert Nexus().configuration is not host_policy
    assert Nexus().configuration.get_property("max_active_rift_count") == 5


def test_restore_of_a_disabled_nexus_over_an_active_live_nexus_ends_disabled(cache_root: Path) -> None:
    """
    Purpose:
        A recorded "disabled" Nexus replays over a live, active one as enable-then-disable.
    Contract:
        The report completes with one nexus build; the Nexus ends inactive, still configured with the
        recorded Rift cap.
    """
    checkpoint_id = _record_a_nexus_world(deactivate_before_seal=True)
    rebooted = _reboot_with_an_active_host_nexus()

    rebooted.reload_cached_checkpoint(checkpoint_id)
    report = rebooted.load_checkpoint(checkpoint_id)

    assert report["status"] == "complete"
    assert report["built_counts"]["nexus"] == 1
    assert Nexus().activated is False
    assert Nexus().configured is True
    assert Nexus().configuration.get_property("max_active_rift_count") == 5
