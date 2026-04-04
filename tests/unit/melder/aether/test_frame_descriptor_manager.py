import types

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.nexus.frame_descriptor_manager import FrameDescriptorManager
from melder.spellbook.configuration.system_state import SystemState


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each manager unit test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def _bind_frame_posture(
        frame_name: str,
        *,
        rift_enabled: bool,
) -> Aether:
    """
    Bind one frame posture into Aether for manager tests.

    Args:
        frame_name:
            Target frame name.
        rift_enabled:
            Whether the frame should be publishable.

    Returns:
        Aether: Active Aether singleton.
    """
    aether = Aether()
    aether._ensure_frame(frame_name)
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=rift_enabled,
    )
    aether._bind_aetheric_frame_configuration(frame_configuration, frame_name)
    return aether


def test_manager_publish_frame_record_creates_descriptor_and_overview() -> None:
    """
    Verify frame publication lazily creates the descriptor and stores overview.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert manager._publish_frame_record(spellbook) is True

    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_overview is not None
    assert descriptor.frame_overview.frame_name == "ops"
    assert descriptor.frame_overview.rift_enabled is True


def test_manager_create_and_detach_nexus_frame_record_updates_descriptor_indexes() -> None:
    """
    Verify Nexus-managed frame records are stored and detached through manager.

    Returns:
        None.
    """
    aether = Aether()
    manager = FrameDescriptorManager(aether)

    record = manager._create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-1",
        immutable=False,
        nexus_frame_mode=NexusFrameMode.single,
    )

    assert manager._get_nexus_frame_record("ops") is record
    assert manager._count_nexus_frame_records() == 1
    assert manager._list_nexus_frame_names() == ["ops"]

    detached = manager._detach_nexus_frame_record("ops")

    assert detached is record
    assert manager._get_nexus_frame_record("ops") is None
    assert manager._count_nexus_frame_records() == 0
    assert manager._list_nexus_frame_names() == []


def test_manager_publishable_frame_posture_short_circuits_when_rift_disabled() -> None:
    """
    Verify manager keeps the descriptor but denies passive publication posture.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=False)
    manager = FrameDescriptorManager(aether)

    posture = manager._get_publishable_frame_posture("ops")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is not None
    assert descriptor.frame_configuration.rift_enabled is False


def test_manager_refresh_frame_posture_cache_returns_none_for_missing_frame() -> None:
    """
    Verify posture refresh clears descriptor state when the frame is missing.

    Returns:
        None.
    """
    aether = Aether()
    manager = FrameDescriptorManager(aether)

    posture = manager._refresh_frame_posture_cache("missing")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("missing")
    assert descriptor.frame_configuration is None
    assert descriptor.frame_handle is None


def test_manager_refresh_frame_posture_cache_returns_none_when_posture_not_bound() -> None:
    """
    Verify posture refresh leaves a descriptor without posture when the frame
    exists but has no bound frame configuration.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame("ops")
    manager = FrameDescriptorManager(aether)

    posture = manager._refresh_frame_posture_cache("ops")

    assert posture is None
    descriptor = manager._get_required_frame_descriptor("ops")
    assert descriptor.frame_configuration is None
    assert descriptor.frame_handle is None


def test_manager_required_getters_raise_for_missing_records() -> None:
    """
    Verify required descriptor/frame-record getters fail loudly when absent.

    Returns:
        None.
    """
    manager = FrameDescriptorManager(Aether())

    with pytest.raises(KeyError, match="ops"):
        manager._get_required_frame_descriptor("ops")

    with pytest.raises(ValueError, match="Nexus frame 'ops' was not found."):
        manager._get_required_nexus_frame_record("ops")


def test_manager_get_or_create_nexus_frame_record_reuses_existing_record() -> None:
    """
    Verify get-or-create returns the same Nexus frame record on repeat calls.

    Returns:
        None.
    """
    manager = FrameDescriptorManager(Aether())

    first_record = manager._get_or_create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-1",
        immutable=False,
        nexus_frame_mode=NexusFrameMode.single,
    )
    second_record = manager._get_or_create_nexus_frame_record(
        "ops",
        creator_rift_id="rift-2",
        immutable=True,
        nexus_frame_mode=NexusFrameMode.indexed,
    )

    assert second_record is first_record
    assert second_record.creator_rift_id == "rift-1"
    assert second_record.immutable is False


def test_manager_cleanup_cleans_owned_descriptors_and_nuls_state() -> None:
    """
    Verify manager cleanup cascades into owned descriptors and releases state.

    Returns:
        None.
    """
    aether = _bind_frame_posture("ops", rift_enabled=True)
    manager = FrameDescriptorManager(aether)
    spellbook = types.SimpleNamespace(_aetheric_frame="ops", _id="spellbook-alpha")

    assert manager._publish_frame_record(spellbook) is True
    descriptor = manager._get_required_frame_descriptor("ops")

    manager.cleanup()

    assert descriptor.cleaned is True
    assert manager._lock is None
