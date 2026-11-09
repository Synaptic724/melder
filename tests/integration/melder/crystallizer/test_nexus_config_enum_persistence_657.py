"""Real Nexus configuration checkpoint and cached reload enum contracts."""

import json
from pathlib import Path
from typing import Dict, Iterator, cast

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.asset_management.crystallizer_cache import CrystallizerCache
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import RiftValidationMode
from melder.nexus.nexus import Nexus


def _reboot_world() -> None:
    """Tear down the owned test world and rebind the usual hosted references."""
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


@pytest.fixture(autouse=True)
def isolated_world() -> Iterator[None]:
    """Give each test a fresh hosted world and leave a live successor."""
    _reboot_world()
    try:
        yield
    finally:
        _reboot_world()


def _activate_recorder() -> Crystallizer:
    """Activate the real recorder with the normal sequential restore policy."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.set_property("restore_parallel_enabled", False)
    configuration.activate()
    recorder = Crystallizer()
    recorder.activate(configuration)
    return recorder


def test_nexus_enum_names_remain_plain_through_checkpoint_and_cached_reload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Record plain names, write a real cache and restore the original typed policy."""
    cache_root = tmp_path / "crystallizer-cache"
    monkeypatch.setattr(
        CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: cache_root),
    )
    recorder = _activate_recorder()
    nexus = Nexus()
    configuration = nexus.create_configuration()
    configuration.set_property("nexus_frame_mode", "single")
    configuration.set_property("default_space_type", "capability")
    configuration.set_property("default_validation_mode", "relaxed")
    nexus.activate(configuration)

    checkpoint_id = recorder.create_checkpoint()
    replay = recorder.checkpoint_replay_data(checkpoint_id)
    payloads = cast(Dict[str, Dict[str, Dict[str, object]]], replay["payloads"])
    policy = cast(Dict[str, object], payloads["nexus"]["root"]["configuration_payload"])
    expected = {
        "nexus_frame_mode": "single",
        "default_space_type": "capability",
        "default_validation_mode": "relaxed",
    }
    for key, value in expected.items():
        assert type(policy[key]) is str
        assert policy[key] == value

    assert recorder.flush_checkpoint(checkpoint_id) == [checkpoint_id]
    profile = str(recorder.describe_checkpoint(checkpoint_id)["profile_name"])
    cache_file = cache_root / profile / f"{checkpoint_id}.json"
    cached = json.loads(cache_file.read_text(encoding="utf-8"))
    assert cached["record_version"] == "5.0.0"
    saved = cached["captured_payloads"]["nexus"]["root"]["configuration_payload"]
    for key, value in expected.items():
        assert saved[key] == value

    _reboot_world()
    reloaded = _activate_recorder()
    reloaded.reload_cached_checkpoint(checkpoint_id)
    report = reloaded.load_checkpoint(checkpoint_id)
    assert report["status"] == "complete"
    restored = Nexus().configuration
    assert restored.get_property("nexus_frame_mode") is NexusFrameMode.single
    assert restored.get_property("default_space_type") is RiftSpaceType.capability
    assert restored.get_property("default_validation_mode") is RiftValidationMode.relaxed
