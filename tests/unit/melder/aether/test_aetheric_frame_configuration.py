import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
from melder.aether.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.aether.nexus.frame_descriptor.frame_record import FrameRecord
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.configuration.system_state import SystemState


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
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
    configuration = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(configuration, SystemState.dynamic)
    set_frame_ai_native_for_spellbook_configuration(configuration, True)
    set_frame_rift_enabled_for_spellbook_configuration(configuration, True)
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration(configuration, True)
    frame_configuration = build_aetheric_frame_configuration_for_spellbook_configuration(configuration, 
        origin_spellbook_id="spellbook-alpha",
    )

    assert frame_configuration.origin_spellbook_id == "spellbook-alpha"
    assert frame_configuration.system_state == SystemState.dynamic
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.rift_enabled is True
    assert frame_configuration.shared_framewide_spellbook_configuration is True


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

    aether._ensure_frame("ops").bind_frame_configuration(first)
    aether._ensure_frame("ops").bind_frame_configuration(conflicting)

    bound = aether._get_aetheric_frame_configuration("ops")

    assert bound is not first
    assert bound.origin_spellbook_id == "spellbook-alpha"
    assert bound.system_state == SystemState.automatic
    assert bound.ai_native_enabled is False
    assert bound.rift_enabled is True
    assert bound.shared_framewide_spellbook_configuration is False

    with pytest.raises(RuntimeError):
        _ = conflicting.id
    with pytest.raises(RuntimeError):
        _ = first.id


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
    aether._ensure_frame("ops").bind_frame_configuration(frame_configuration)

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
    """The old SpellbookConfiguration conversion classmethod no longer exists."""
    assert hasattr(AethericFrameConfiguration, "from_spellbook_configuration") is False


def test_aetheric_frame_configuration_exposes_id_and_describe_posture() -> None:
    """SpellbookConfiguration should expose a stable id and a detached posture description."""
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
        "shared_framewide_spellbook_configuration": False,
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

