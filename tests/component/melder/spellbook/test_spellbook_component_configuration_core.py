import pytest

from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.configuration.system_state import SystemState


from tests._frame_posture_test_support import (
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
)
def test_component_configuration_defaults_validate_and_freeze() -> None:
    """
    Purpose:
        Validate defaults satisfy validation and freeze blocks mutation.
    Contract:
        - validate succeeds after defaults are applied.
        - freeze prevents further property updates.
    Returns:
        None.
    """
    config = SpellbookConfiguration()
    config.with_defaults()
    assert config.validate() is True
    assert (
        build_aetheric_frame_configuration_for_spellbook_configuration(config, ).system_state
        is SystemState.automatic
    )

    config.freeze()
    with pytest.raises(RuntimeError):
        config.set_property("disposal", True)


def test_component_configuration_system_state_is_reconfigurable_pre_freeze() -> None:
    """
    Purpose:
        Validate frame posture can be re-authored before freeze.
    Contract:
        - system_state is converted to an enum.
        - A later explicit change updates the associated frame posture.
    Returns:
        None.
    """
    config = SpellbookConfiguration()
    set_frame_system_state_for_spellbook_configuration(config, "automatic")
    assert build_aetheric_frame_configuration_for_spellbook_configuration(config, ).system_state is SystemState.automatic
    set_frame_system_state_for_spellbook_configuration(config, SystemState.dynamic)
    assert build_aetheric_frame_configuration_for_spellbook_configuration(config, ).system_state is SystemState.dynamic


def test_component_configuration_hooks_register_and_shared_map() -> None:
    """
    Purpose:
        Validate hook registration and shared hook map semantics.
    Contract:
        - Registered hooks are returned in the shared map.
        - Mutations of the returned map reflect in configuration storage.
    Returns:
        None.
    """
    config = SpellbookConfiguration().with_defaults()

    def hook_a() -> None:
        return None

    def hook_b() -> None:
        return None

    config.add_hook("spellbook-1", "on_meld_pre_resolve", hook_a)
    config.add_hooks(
        "spellbook-1",
        on_conduit_post_created=[hook_b],
    )

    hooks = config.get_hooks("spellbook-1")
    assert hooks["on_meld_pre_resolve"] == [hook_a]
    assert hooks["on_conduit_post_created"] == [hook_b]

    hooks["on_meld_pre_resolve"].append(hook_b)
    assert config.get_hooks("spellbook-1")["on_meld_pre_resolve"] == [hook_a]


def test_component_configuration_freeze_blocks_hooks_and_properties() -> None:
    """
    Purpose:
        Validate freeze blocks configuration mutation APIs.
    Contract:
        - add_hook and clear_properties raise after freeze.
    Returns:
        None.
    """
    config = SpellbookConfiguration().with_defaults()
    config.freeze()

    with pytest.raises(RuntimeError):
        config.add_hook("spellbook-1", "on_meld_pre_resolve", lambda: None)
    with pytest.raises(RuntimeError):
        config.clear_properties()


def test_component_configuration_stays_logger_free() -> None:
    """
    Purpose:
        Validate configuration no longer owns logger-factory behavior.
    Contract:
        - Core configuration defaults and validation still work without any
          logger-factory API.
    Returns:
        None.
    """
    config = SpellbookConfiguration().with_defaults().finalize()
    assert build_aetheric_frame_configuration_for_spellbook_configuration(config, ).system_state is SystemState.automatic


def test_component_configuration_validate_requires_required_properties() -> None:
    """
    Purpose:
        Validate required properties must be present before validation.
    Contract:
        - validate raises ValueError when required properties are missing.
    Returns:
        None.
    """
    config = SpellbookConfiguration()
    with pytest.raises(ValueError, match="Missing required configuration property"):
        config.validate()


def test_component_configuration_with_hook_registers_hook() -> None:
    """
    Purpose:
        Validate with_hook registers a single hook fluently.
    Contract:
        - Returns the same configuration instance.
        - Hook is registered and retrievable via get_hooks.
    Returns:
        None.
    """
    config = SpellbookConfiguration()

    def hook() -> None:
        return None

    result = config.with_hook("spellbook-1", "on_meld_pre_resolve", hook)
    assert result is config
    hooks = config.get_hooks("spellbook-1")
    assert hooks["on_meld_pre_resolve"] == [hook]


def test_component_configuration_with_disposal_method_names_sets_list() -> None:
    """
    Purpose:
        Validate with_disposal_method_names sets disposal methods fluently.
    Contract:
        - Returns the same configuration instance.
        - disposal_method_names is set to the provided list.
    Returns:
        None.
    """
    config = SpellbookConfiguration()
    result = config.with_disposal_method_names(["cleanup", "close"])
    assert result is config
    assert config.get_property("disposal_method_names") == ["cleanup", "close"]


def test_component_configuration_with_hooks_registers_multiple() -> None:
    """
    Purpose:
        Validate with_hooks registers multiple hook names fluently.
    Contract:
        - Returns the same configuration instance.
        - Hook mapping includes each provided hook.
    Returns:
        None.
    """
    config = SpellbookConfiguration()

    def pre() -> None:
        return None

    def post() -> None:
        return None

    result = config.with_hooks(
        "spellbook-1",
        on_conduit_pre_created=pre,
        on_conduit_post_created=post,
    )
    assert result is config
    hooks = config.get_hooks("spellbook-1")
    assert hooks["on_conduit_pre_created"] == [pre]
    assert hooks["on_conduit_post_created"] == [post]


def test_component_configuration_fluent_chain_validates_without_defaults() -> None:
    """
    Purpose:
        Validate fluent API can set all required properties without defaults.
    Contract:
        - finalize freezes after validation.
        - All required properties are present with expected values.
    Returns:
        None.
    """
    config = SpellbookConfiguration()

    set_frame_system_state_for_spellbook_configuration(config, "dynamic")
    config.with_disposal(True)
    config.with_disposal_method_names(["cleanup"])
    config.with_full_ahead_of_time_compilation(True)
    config.with_phase_scheduler_workers(2)
    config.with_phase_scheduler_barrier_timeout(1000)
    set_frame_ai_native_for_spellbook_configuration(config, True)
    set_frame_rift_enabled_for_spellbook_configuration(config, False)
    config.finalize()

    frame_configuration = build_aetheric_frame_configuration_for_spellbook_configuration(config, )
    assert frame_configuration.system_state is SystemState.dynamic
    assert config.get_property("disposal") is True
    assert config.get_property("disposal_method_names") == ["cleanup"]
    assert config.get_property("full_ahead_of_time_compilation") is True
    assert config.get_property("phase_scheduler_workers_per_spellbook") == 2
    assert config.get_property("phase_scheduler_barrier_timeout_milliseconds") == 1000
    assert frame_configuration.ai_native_enabled is True
    assert frame_configuration.rift_enabled is False
