from pathlib import Path

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.aetheric_frame.aetheric_frame_configuration import AethericFrameConfiguration
from melder.nexus.frame_descriptor.frame_descriptor_payload import (
    FrameDescriptorPayload,
)
from melder.nexus.frame_descriptor.frame_record import FrameRecord
from melder.nexus.nexus import Nexus
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState


from tests._frame_posture_test_support import (
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
    configuration = nexus.create_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_allowed_target_frame_names(("ops",))
    nexus.activate(configuration)
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
        "system_caching_enabled": True,
        "system_cache_root_path": Path("__melder_cache__"),
        "disable_all_transactions_after_conjure": False,
        "disable_mutations": True,
        "disable_linking": False,
        "disable_bind": False,
        "disable_conduit_cluster": False,
        "disable_transfer_of_ownership": False,
        "disable_contract_mutation": False,
        "max_transaction_wait_time_in_seconds": 30.0,
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


def test_aetheric_frame_configuration_change_control_defaults() -> None:
    """Frame change-control defaults should match the requested posture."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    assert frame_configuration.disable_all_transactions_after_conjure is False
    assert frame_configuration.disable_mutations is True
    assert frame_configuration.disable_linking is False
    assert frame_configuration.disable_bind is False
    assert frame_configuration.disable_conduit_cluster is False
    assert frame_configuration.disable_transfer_of_ownership is False
    assert frame_configuration.disable_contract_mutation is False
    assert frame_configuration.max_transaction_wait_time_in_seconds == 30.0

def test_aetheric_frame_configuration_with_defaults_resets_change_control_flags() -> None:
    """with_defaults should restore the requested change-control defaults."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.dynamic,
        ai_native_enabled=True,
        rift_enabled=True,
        disable_all_transactions_after_conjure=True,
        disable_mutations=False,
        disable_linking=True,
        disable_bind=True,
        disable_conduit_cluster=True,
        disable_transfer_of_ownership=True,
        disable_contract_mutation=True,
        max_transaction_wait_time_in_seconds=5.0,
    )

    frame_configuration.with_defaults()

    assert frame_configuration.disable_all_transactions_after_conjure is False
    assert frame_configuration.disable_mutations is True
    assert frame_configuration.disable_linking is False
    assert frame_configuration.disable_bind is False
    assert frame_configuration.disable_conduit_cluster is False
    assert frame_configuration.disable_transfer_of_ownership is False
    assert frame_configuration.disable_contract_mutation is False
    assert frame_configuration.max_transaction_wait_time_in_seconds == 30.0


def test_aetheric_frame_configuration_rejects_invalid_transaction_wait_time() -> None:
    """Constructor should reject non-positive transaction wait times."""
    with pytest.raises(ValueError, match="greater than 0"):
        AethericFrameConfiguration(
            origin_spellbook_id="spellbook-alpha",
            system_state=SystemState.automatic,
            ai_native_enabled=False,
            rift_enabled=False,
            max_transaction_wait_time_in_seconds=0,
        )


@pytest.mark.parametrize(
    ("setter_name", "property_name"),
    (
        (
            "with_disable_all_transactions_after_conjure",
            "disable_all_transactions_after_conjure",
        ),
        ("with_disable_mutations", "disable_mutations"),
        ("with_disable_linking", "disable_linking"),
        ("with_disable_bind", "disable_bind"),
        ("with_disable_conduit_cluster", "disable_conduit_cluster"),
        ("with_disable_transfer_of_ownership", "disable_transfer_of_ownership"),
        ("with_disable_contract_mutation", "disable_contract_mutation"),
    ),
)
def test_aetheric_frame_configuration_boolean_mutators_update_flags(
        setter_name: str,
        property_name: str,
) -> None:
    """Boolean posture mutators should update the matching frame flag."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    getattr(frame_configuration, setter_name)(True)
    assert getattr(frame_configuration, property_name) is True

    getattr(frame_configuration, setter_name)(False)
    assert getattr(frame_configuration, property_name) is False


@pytest.mark.parametrize(
    ("setter_name", "error_message"),
    (
        (
            "with_disable_all_transactions_after_conjure",
            "disable_all_transactions_after_conjure must be a bool.",
        ),
        ("with_disable_mutations", "disable_mutations must be a bool."),
        ("with_disable_linking", "disable_linking must be a bool."),
        ("with_disable_bind", "disable_bind must be a bool."),
        ("with_disable_conduit_cluster", "disable_conduit_cluster must be a bool."),
        (
            "with_disable_transfer_of_ownership",
            "disable_transfer_of_ownership must be a bool.",
        ),
        (
            "with_disable_contract_mutation",
            "disable_contract_mutation must be a bool.",
        ),
    ),
)
def test_aetheric_frame_configuration_boolean_mutators_reject_non_bool(
        setter_name: str,
        error_message: str,
) -> None:
    """Boolean posture mutators should reject non-bool inputs."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    with pytest.raises(TypeError, match=error_message):
        getattr(frame_configuration, setter_name)("yes")


@pytest.mark.parametrize(
    "setter_name",
    (
        "with_system_state",
        "with_ai_native",
        "with_rift_enabled",
        "with_shared_framewide_spellbook_configuration",
        "with_disable_all_transactions_after_conjure",
        "with_disable_mutations",
        "with_disable_linking",
        "with_disable_bind",
        "with_disable_conduit_cluster",
        "with_disable_transfer_of_ownership",
        "with_disable_contract_mutation",
        "with_max_transaction_wait_time_in_seconds",
        "with_defaults",
    ),
)
def test_aetheric_frame_configuration_mutators_reject_after_freeze(
        setter_name: str,
) -> None:
    """All posture mutators should reject writes after freeze."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    frame_configuration.freeze(origin_spellbook_id="spellbook-alpha")

    with pytest.raises(RuntimeError, match="after it is frozen"):
        if setter_name == "with_system_state":
            frame_configuration.with_system_state(SystemState.dynamic)
        elif setter_name == "with_ai_native":
            frame_configuration.with_ai_native(True)
        elif setter_name == "with_rift_enabled":
            frame_configuration.with_rift_enabled(True)
        elif setter_name == "with_shared_framewide_spellbook_configuration":
            frame_configuration.with_shared_framewide_spellbook_configuration(True)
        elif setter_name == "with_disable_all_transactions_after_conjure":
            frame_configuration.with_disable_all_transactions_after_conjure(True)
        elif setter_name == "with_disable_mutations":
            frame_configuration.with_disable_mutations(False)
        elif setter_name == "with_disable_linking":
            frame_configuration.with_disable_linking(True)
        elif setter_name == "with_disable_bind":
            frame_configuration.with_disable_bind(True)
        elif setter_name == "with_disable_conduit_cluster":
            frame_configuration.with_disable_conduit_cluster(True)
        elif setter_name == "with_disable_transfer_of_ownership":
            frame_configuration.with_disable_transfer_of_ownership(True)
        elif setter_name == "with_disable_contract_mutation":
            frame_configuration.with_disable_contract_mutation(True)
        elif setter_name == "with_max_transaction_wait_time_in_seconds":
            frame_configuration.with_max_transaction_wait_time_in_seconds(5.0)
        else:
            frame_configuration.with_defaults()


def test_aetheric_frame_configuration_transaction_wait_mutator_normalizes_int_to_float() -> None:
    """Transaction wait mutator should normalize ints to floats."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    frame_configuration.with_max_transaction_wait_time_in_seconds(5)

    assert frame_configuration.max_transaction_wait_time_in_seconds == 5.0


@pytest.mark.parametrize(
    ("field_name", "mutator_name", "mutator_value"),
    (
        (
            "disable_all_transactions_after_conjure",
            "with_disable_all_transactions_after_conjure",
            True,
        ),
        ("disable_linking", "with_disable_linking", True),
        ("disable_bind", "with_disable_bind", True),
        ("disable_conduit_cluster", "with_disable_conduit_cluster", True),
        (
            "disable_transfer_of_ownership",
            "with_disable_transfer_of_ownership",
            True,
        ),
        (
            "disable_contract_mutation",
            "with_disable_contract_mutation",
            True,
        ),
        (
            "max_transaction_wait_time_in_seconds",
            "with_max_transaction_wait_time_in_seconds",
            5.0,
        ),
    ),
)
def test_aetheric_frame_configuration_matches_posture_detects_transaction_field_drift(
        field_name: str,
        mutator_name: str,
        mutator_value,
) -> None:
    """matches_posture should return False when any transaction posture field differs."""
    left = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    )
    right = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-beta",
        system_state=SystemState.dynamic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    getattr(right, mutator_name)(mutator_value)

    assert left.matches_posture(right) is False


def test_aetheric_frame_configuration_freeze_sets_origin_spellbook_id_when_supplied() -> None:
    """freeze should record the supplied origin spellbook id."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id=None,
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    frame_configuration.freeze(origin_spellbook_id="spellbook-omega")

    assert frame_configuration.origin_spellbook_id == "spellbook-omega"


def test_aetheric_frame_configuration_freeze_is_idempotent() -> None:
    """freeze should be safe to call repeatedly after the first success."""
    frame_configuration = AethericFrameConfiguration(
        origin_spellbook_id="spellbook-alpha",
        system_state=SystemState.automatic,
        ai_native_enabled=False,
        rift_enabled=False,
    )

    frame_configuration.freeze(origin_spellbook_id="spellbook-alpha")
    frame_configuration.freeze(origin_spellbook_id="spellbook-beta")

    assert frame_configuration.origin_spellbook_id == "spellbook-alpha"

