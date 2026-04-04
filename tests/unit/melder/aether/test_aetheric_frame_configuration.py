import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame_configuration import AethericFrameConfiguration
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
    configuration.with_ai_profiles(True)

    frame_configuration = configuration.to_aetheric_frame_configuration(
        origin_spellbook_id="spellbook-alpha",
    )

    assert frame_configuration.origin_spellbook_id == "spellbook-alpha"
    assert frame_configuration.system_state == SystemState.dynamic
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.ai_profiles_enabled is True


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
        ai_profiles_enabled=True,
    )
    conflicting = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-beta",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        ai_profiles_enabled=True,
    )

    aether._bind_aetheric_frame_configuration(first, "ops")
    aether._bind_aetheric_frame_configuration(conflicting, "ops")

    bound = aether._get_aetheric_frame_configuration("ops")

    assert bound is first
    assert bound.origin_spellbook_id == "spellbook-alpha"
    assert bound.system_state == SystemState.automatic
    assert bound.ai_native_enabled is False
    assert bound.ai_profiles_enabled is True

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
        ai_profiles_enabled=True,
    )
    aether._bind_aetheric_frame_configuration(frame_configuration, "ops")

    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_default_target_frame_name("ops")
    configuration.with_allowed_target_frame_names(("ops",))
    nexus.enable(configuration)

    rift = nexus.create_rift()

    assert rift.default_target_frame_name == "ops"
    assert rift.target_frame_names == ("ops",)
