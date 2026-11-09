"""SystemState string migration and real frame-recording compatibility."""

import json
import pickle
from enum import StrEnum
from pathlib import Path
from typing import Iterator, cast

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.system_state import SystemState
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import CrystallizerConfiguration
from melder.crystallizer.crystallizer import Crystallizer
from melder.crystallizer.crystals.aetheric_frame_crystal import AethericFrameCrystal
from melder.nexus.nexus import Nexus


@pytest.fixture
def active_recorder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Crystallizer]:
    """Use an isolated real recorder and reset the test process's hosted roots."""
    from melder.crystallizer.asset_management import crystallizer_cache

    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    monkeypatch.setattr(
        crystallizer_cache.CrystallizerCache,
        "resolve_cache_root_path",
        staticmethod(lambda: tmp_path / "crystallizer-cache"),
    )
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    recorder = Crystallizer()
    recorder.activate(configuration)
    yield recorder
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()


@pytest.mark.parametrize(("member", "legacy_number"), [(SystemState.automatic, 1), (SystemState.dynamic, 2)])
def test_system_state_keeps_old_numeric_and_pickle_inputs(member: SystemState, legacy_number: int) -> None:
    """Exact string values coexist with captured historical numeric pickle payloads."""
    old_pickle_prefix = bytes.fromhex(
        "8004954c000000000000008c326d656c6465722e6165746865722e7370656c6c626f6f6b2e"
        "636f6e66696775726174696f6e2e73797374656d5f7374617465948c0b53797374656d53746174659493944b"
    )
    old_pickle = old_pickle_prefix + bytes([legacy_number]) + bytes.fromhex("859452942e")
    assert isinstance(member, StrEnum)
    assert member.value == member.name
    assert str(member) == member.name
    assert json.loads(json.dumps(member)) == member.name
    assert SystemState(legacy_number) is member
    assert SystemState(float(legacy_number)) is member
    assert pickle.loads(old_pickle) is member


def test_frame_emits_plain_state_and_reloads_recorded_posture(
    active_recorder: Crystallizer, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real recorder sees a plain state string before JSON and can rebuild it."""
    captured: list[dict[str, object]] = []
    original_emit = Crystallizer.emit

    def capture_emit(recorder: Crystallizer, crystal: object) -> None:
        """Observe frame twins while retaining the real recorder emission."""
        if isinstance(crystal, AethericFrameCrystal):
            captured.append(crystal.describe())
        original_emit(recorder, crystal)

    monkeypatch.setattr(Crystallizer, "emit", capture_emit)
    posture = AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    try:
        posture.freeze(origin_frame_name="state-test")
        assert len(captured) == 1
        payload = cast(dict[str, object], captured[0]["dev_ops_payload"])
        assert type(payload["system_state"]) is str
        assert payload["system_state"] == "dynamic"
        checkpoint_id = active_recorder.create_checkpoint()
        replay = active_recorder.checkpoint_replay_data(checkpoint_id)
        frames = cast(dict[str, dict[str, object]], cast(dict[str, object], replay["payloads"])["frame"])
        recorded = frames["state-test"]
        assert recorded["system_state_name"] == "dynamic"
        restored, _ = AethericFrameConfiguration.from_recorded_posture(recorded)
        try:
            assert restored.system_state is SystemState.dynamic
            assert restored.frozen is True
        finally:
            restored.cleanup()
    finally:
        posture.cleanup()


def test_frame_state_rejects_a_foreign_string_enum() -> None:
    """A same-spelled foreign family does not become a valid frame posture."""
    class ForeignState(StrEnum):
        dynamic = "dynamic"

    with pytest.raises(ValueError):
        AethericFrameConfiguration(
            origin_spellbook_id=None,
            system_state=cast(SystemState, ForeignState.dynamic),
            ai_native_enabled=False,
            rift_enabled=False,
        )