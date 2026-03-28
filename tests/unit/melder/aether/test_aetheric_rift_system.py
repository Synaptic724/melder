import pytest

from melder.aether.aetheric_rift_system.aetheric_rift.aetheric_rift import AethericRift
from melder.aether.aetheric_rift_system.aetheric_rift_system import AethericRiftSystem
from melder.aether.aetheric_rift_system.rift_space.rift_space import RiftSpace


def _create_enabled_system() -> AethericRiftSystem:
    """
    Create one enabled AR system with the minimal policy needed for the core
    unit tests.

    Returns:
        AethericRiftSystem: Enabled AR system with direct creation/Rift/state
        access allowed.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_direct_state_access(True)
    system.enable(configuration)
    return system


def test_system_starts_unconfigured_and_disabled() -> None:
    """
    Verify the AR system starts unconfigured and disabled.
    """
    system = AethericRiftSystem()

    assert system.is_configured is False
    assert system.is_enabled is False
    with pytest.raises(RuntimeError, match="not configured"):
        _ = system.configuration


def test_create_rift_requires_enabled_system() -> None:
    """
    Verify Rift creation is blocked while the AR system is disabled.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    system.enable(configuration)
    system.disable()

    with pytest.raises(RuntimeError, match="disabled"):
        system.create_rift(rift_name="alpha")


def test_create_rift_requires_creation_permission() -> None:
    """
    Verify enabling the AR system alone does not open Rift creation.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    configuration.with_rift_creation_enabled(False)
    system.enable(configuration)

    with pytest.raises(ValueError, match="creation is disabled"):
        system.create_rift(rift_name="alpha")


def test_create_rift_programs_shell_and_registers_state_after_enable() -> None:
    """
    Verify an enabled AR system can create, program, and register a Rift shell
    and canonical state.
    """
    system = _create_enabled_system()
    rift = system.create_rift(rift_name="alpha")

    assert system.has_rift(rift.id) is True
    assert rift.has_state is True
    assert rift.state.is_registered is True
    assert rift.state.is_active is True
    assert rift.state.system_frame_name == "aetheric_rift_system"
    assert system.get_rift(rift.id) is rift
    assert system.get_rift_state(rift.id) is rift.state
    assert system.get_rift_by_name("alpha") is rift
    assert system.list_rift_ids() == [rift.id]

    system.remove_rift(rift.id)
    assert system.has_rift(rift.id) is False


def test_create_rift_configuration_uses_system_defaults() -> None:
    """
    Verify per-Rift configuration derives from the installed system defaults.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    system.enable(configuration)
    config = system.create_rift_configuration()

    assert config.get_property("target_frame_name") == "default"
    assert config.get_property("auto_activate_on_program") is True
    assert config.get_property("auto_create_space") is False


def test_external_shell_can_be_programmed_and_then_use_spaces() -> None:
    """
    Verify external shell registration still works once the AR system enables
    creation and external registration.
    """
    system = _create_enabled_system()
    system.configuration.with_allow_external_rift_registration(True)
    system.enable()

    rift = AethericRift(system, rift_name="alpha")
    programmed_rift = system.register_external_rift(rift)

    assert programmed_rift is rift
    assert rift.has_state is True
    assert rift.state.configuration.get_property("target_frame_name") == "default"

    space = RiftSpace(owner_rift_id=rift.id, space_name="main")
    rift.register_space(space)

    assert rift.get_space(space.space_id) is space
    assert rift.get_space_by_name("main") is space
    assert rift.active_space_id == space.space_id


def test_inert_rift_cannot_access_room_operations() -> None:
    """
    Verify an unprogrammed Rift shell remains inert.
    """
    system = AethericRiftSystem()
    rift = AethericRift(system, rift_name="alpha")

    with pytest.raises(RuntimeError, match="inert until state is bound"):
        rift.list_space_ids()


def test_state_access_can_be_token_gated() -> None:
    """
    Verify direct canonical state retrieval can be token-gated independently of
    creation.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_state_access(True)
    configuration.with_state_access_token_required(True)
    configuration.with_state_access_token("secret")
    system.enable(configuration)

    rift = system.create_rift(rift_name="alpha")

    with pytest.raises(ValueError, match="Valid state access token"):
        system.get_rift_state(rift.id)

    assert system.get_rift_state(rift.id, access_token="secret") is rift.state


def test_rift_access_can_be_token_gated() -> None:
    """
    Verify direct live-Rift retrieval can be token-gated independently of
    creation.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_rift_access_token_required(True)
    configuration.with_rift_access_token("secret")
    system.enable(configuration)

    rift = system.create_rift(rift_name="alpha")

    with pytest.raises(ValueError, match="Valid Rift access token"):
        system.get_rift(rift.id)

    assert system.get_rift(rift.id, access_token="secret") is rift


def test_target_frame_allow_and_deny_lists_are_enforced() -> None:
    """
    Verify target-frame governance uses allow-list and deny-list policy with
    deny precedence.
    """
    system = AethericRiftSystem()
    configuration = system.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", "ops"))
    configuration.with_denied_target_frame_names(("ops",))
    system.enable(configuration)

    blocked_config = system.create_rift_configuration().with_target_frame_name("ops")
    with pytest.raises(ValueError, match="denied"):
        system.create_rift(configuration=blocked_config, rift_name="blocked")

    system.configuration.with_denied_target_frame_names(tuple())
    system.enable()
    allowed_config = system.create_rift_configuration().with_target_frame_name("ops")
    rift = system.create_rift(configuration=allowed_config, rift_name="allowed")

    assert rift.state.target_frame_name == "ops"


def test_shared_and_isolated_system_frame_names_are_assigned() -> None:
    """
    Verify the system-frame topology settings shape the canonical state anchor
    name correctly.
    """
    shared_system = _create_enabled_system()
    shared_rift = shared_system.create_rift(rift_name="shared")
    assert shared_rift.state.system_frame_name == "aetheric_frame_system"

    isolated_system = AethericRiftSystem()
    configuration = isolated_system.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_direct_state_access(True)
    configuration.with_system_frame_mode("one_per_workspace")
    configuration.with_max_system_frame_count(2)
    isolated_system.enable(configuration)

    isolated_rift = isolated_system.create_rift(rift_name="isolated")
    assert isolated_rift.state.system_frame_name.startswith("aetheric_frame_system:")
    assert isolated_rift.state.system_frame_name.endswith(isolated_rift.id)
