import pytest

from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.configuration.system_state import SystemState


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
    config = Configuration()
    config.with_defaults()
    assert config.validate() is True
    assert config.get_property("system_state") is SystemState.automatic

    config.freeze()
    with pytest.raises(RuntimeError):
        config.set_property("debugging", True)


def test_component_configuration_idempotent_system_state_cannot_change() -> None:
    """
    Purpose:
        Validate idempotent properties cannot be modified once set.
    Contract:
        - system_state is converted to an enum.
        - Second assignment raises RuntimeError.
    Returns:
        None.
    """
    config = Configuration()
    config.set_property("system_state", "automatic")
    assert config.get_property("system_state") is SystemState.automatic

    with pytest.raises(RuntimeError):
        config.set_property("system_state", SystemState.dynamic)


def test_component_configuration_hooks_register_and_snapshot() -> None:
    """
    Purpose:
        Validate hook registration and snapshot semantics.
    Contract:
        - Registered hooks are returned in snapshots.
        - Snapshots are independent of internal storage.
    Returns:
        None.
    """
    config = Configuration().with_defaults()

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
    config = Configuration().with_defaults()
    config.freeze()

    with pytest.raises(RuntimeError):
        config.add_hook("spellbook-1", "on_meld_pre_resolve", lambda: None)
    with pytest.raises(RuntimeError):
        config.clear_properties()


def test_component_configuration_logger_factory_roundtrip() -> None:
    """
    Purpose:
        Validate logger factories are stored and invoked.
    Contract:
        - get_logger_for returns factory output.
        - clear_logger_factory disables logging.
    Returns:
        None.
    """
    config = Configuration().with_defaults()

    def factory(obj: object) -> str:
        return f"logger:{obj}"

    config.set_logger_factory(factory)
    assert config.has_logger_factory() is True
    assert config.get_logger_for("root") == "logger:root"

    config.clear_logger_factory()
    assert config.has_logger_factory() is False
    assert config.get_logger_for("root") is None


def test_component_configuration_logger_factory_rejects_async() -> None:
    """
    Purpose:
        Validate async logger factories are rejected.
    Contract:
        - set_logger_factory raises TypeError for async callables.
    Returns:
        None.
    """
    config = Configuration().with_defaults()

    async def async_factory(obj: object) -> object:
        return obj

    with pytest.raises(TypeError):
        config.set_logger_factory(async_factory)


def test_component_configuration_validate_requires_required_properties() -> None:
    """
    Purpose:
        Validate required properties must be present before validation.
    Contract:
        - validate raises ValueError when required properties are missing.
    Returns:
        None.
    """
    config = Configuration()
    with pytest.raises(ValueError, match="Missing required configuration property"):
        config.validate()
