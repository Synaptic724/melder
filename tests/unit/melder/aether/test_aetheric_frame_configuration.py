import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each test.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()


def test_frame_configuration_derives_from_spellbook_configuration() -> None:
    """
    Verify the narrow frame posture can be derived from a full Spellbook
    configuration.

    Returns:
        None.
    """
    configuration = Configuration()
    configuration.with_system_state(SystemState.dynamic)
    configuration.with_ai_native(True)
    configuration.with_rift_enabled(True)

    frame_configuration = configuration.to_aetheric_frame_configuration(
        origin_spellbook_id="spellbook-alpha",
    )

    assert frame_configuration.origin_spellbook_id == "spellbook-alpha"
    assert frame_configuration.system_state == SystemState.dynamic
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.rift_enabled is True
    assert frame_configuration.overrides_enabled is True


def test_aetheric_frame_configuration_first_writer_wins() -> None:
    """
    Verify the first bound frame posture remains canonical for a frame and
    later conflicting writes are ignored.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame("ops")

    first = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
    )
    conflicting = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-beta",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
    )

    aether._bind_aetheric_frame_configuration(first, "ops")
    aether._bind_aetheric_frame_configuration(conflicting, "ops")

    bound = aether._get_aetheric_frame_configuration("ops")

    assert bound is first
    assert bound.origin_spellbook_id == "spellbook-alpha"
    assert bound.system_state == SystemState.automatic
    assert bound.ai_native_enabled is False
    assert bound.rift_enabled is True

    with pytest.raises(RuntimeError):
        _ = conflicting.id


def test_nexus_runtime_posture_accepts_bound_frame_configuration() -> None:
    """
    Verify Nexus target-frame runtime validation can consume the narrow bound
    frame posture even when no full Spellbook configuration is bound.

    Returns:
        None.
    """
    aether = Aether()
    aether._ensure_frame("ops")
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=True,
    )
    aether._bind_aetheric_frame_configuration(frame_configuration, "ops")

    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_allowed_target_frame_names(("ops",))
    nexus.enable(configuration)
    descriptor = nexus._get_or_create_frame_descriptor("ops")
    descriptor.set_frame_overview(
        FrameRecord(
            frame_name="ops",
            frame_id="ops-frame",
            config_origin_spellbook_id="spellbook-alpha",
            payload=FrameDescriptorPayload(
                system_state=SystemState.automatic,
                ai_native_enabled=False,
                rift_enabled=True,
                root_conduit_count=0,
                root_conduit_ids=tuple(),
                named_root_conduits=tuple(),
                conduit_cloud_entry_count=0,
                conduit_cloud_names=tuple(),
                cluster_count=0,
                cluster_names=tuple(),
            ),
        )
    )

    rift = nexus.create_rift()

    assert rift.list_assigned_frame_names() == tuple()

    rift.create_frame_link("ops")

    assert rift.list_assigned_frame_names() == ("ops",)


def test_aetheric_frame_configuration_rejects_non_bool_ai_native_flag() -> None:
    """Constructor should reject non-bool ai_native_enabled values."""
    with pytest.raises(TypeError, match="ai_native_enabled must be a bool"):
        AethericFrameConfiguration(
            origin_spellbook_id="spellbook-alpha",
            system_state=SystemState.dynamic,
            ai_native_enabled="yes",
            rift_enabled=True,
        )


def test_aetheric_frame_configuration_rejects_non_bool_rift_flag() -> None:
    """Constructor should reject non-bool rift_enabled values."""
    with pytest.raises(TypeError, match="rift_enabled must be a bool"):
        AethericFrameConfiguration(
            origin_spellbook_id="spellbook-alpha",
            system_state=SystemState.dynamic,
            ai_native_enabled=True,
            rift_enabled="yes",
        )


def test_from_spellbook_configuration_rejects_none_configuration() -> None:
    """from_spellbook_configuration should reject None."""
    with pytest.raises(TypeError, match="configuration cannot be None"):
        AethericFrameConfiguration.from_spellbook_configuration(
            origin_spellbook_id="spellbook-alpha",
            configuration=None,
        )


def test_aetheric_frame_configuration_exposes_id_and_describe_posture() -> None:
    """Configuration should expose a stable id and a detached posture description."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    assert frame_configuration.id is not None
    assert frame_configuration.describe_posture() == {
        "origin_spellbook_id": "spellbook-alpha",
        "system_state": SystemState.dynamic,
        "ai_native_enabled": True,
        "rift_enabled": False,
        "overrides_enabled": True,
    }


def test_matches_posture_returns_false_for_none() -> None:
    """matches_posture should return False when the comparison target is None."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    assert frame_configuration.matches_posture(None) is False


def test_cleanup_is_idempotent_for_frame_configuration() -> None:
    """cleanup should be safe to call repeatedly."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=False,
    )

    frame_configuration.cleanup()
    frame_configuration.cleanup()

    assert frame_configuration._cleaned is True

