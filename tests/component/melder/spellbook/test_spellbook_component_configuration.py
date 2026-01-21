import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook_configuration() -> None:
    """
    Purpose:
        Ensure component Spellbook configuration tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_configuration(aether_frame: str) -> Configuration:
    """
    Purpose:
        Build a Configuration instance with a specific Aether frame name.
    Contract:
        - Returns a Configuration whose _aether_frame matches the input.
    Args:
        aether_frame: Target frame name for the configuration instance.
    Returns:
        Configuration: Newly created configuration for the frame.
    """
    return Configuration(aether_frame=aether_frame)


def test_component_spellbook_initialize_configuration_adopts_aether_config_and_locks() -> None:
    """
    Purpose:
        Validate Spellbook adopts an existing Aether configuration when present.
    Contract:
        - Spellbook reuses the Aether configuration instance.
        - Configuration is marked as locked when adopted.
    Returns:
        None.
    Raises:
        AssertionError: If the configuration is not adopted or locked.
    """
    aether = Spellbook._aether
    frame_name = "frame-config-adopt"
    aether._ensure_frame(frame_name)
    config = _make_configuration(frame_name)
    aether._bind_configuration(config, frame_name)

    spellbook = Spellbook(aetheric_frame=frame_name)
    try:
        assert spellbook.get_configuration() is config
        assert spellbook.is_configuration_locked() is True
    finally:
        spellbook.cleanup()


def test_component_spellbook_initialize_configuration_reuses_matching_provided_config() -> None:
    """
    Purpose:
        Validate Spellbook accepts a provided configuration when it matches Aether.
    Contract:
        - The provided configuration instance is reused.
        - Configuration is locked when Aether already has the config.
    Returns:
        None.
    Raises:
        AssertionError: If the config is not reused or locked.
    """
    aether = Spellbook._aether
    frame_name = "frame-config-match"
    aether._ensure_frame(frame_name)
    config = _make_configuration(frame_name)
    aether._bind_configuration(config, frame_name)

    spellbook = Spellbook(aetheric_frame=frame_name, configuration=config)
    try:
        assert spellbook.get_configuration() is config
        assert spellbook.is_configuration_locked() is True
    finally:
        spellbook.cleanup()


def test_component_spellbook_initialize_configuration_rejects_mismatched_aether_config() -> None:
    """
    Purpose:
        Validate Spellbook rejects a provided configuration when Aether already has another.
    Contract:
        - Initialization raises RuntimeError when the provided config differs from Aether's.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    aether = Spellbook._aether
    frame_name = "frame-config-conflict"
    aether._ensure_frame(frame_name)
    config_aether = _make_configuration(frame_name)
    config_other = _make_configuration(frame_name)
    aether._bind_configuration(config_aether, frame_name)

    with pytest.raises(RuntimeError, match="Aether configuration does not match"):
        Spellbook(aetheric_frame=frame_name, configuration=config_other)


def test_component_spellbook_initialize_configuration_rejects_frame_mismatch() -> None:
    """
    Purpose:
        Validate Spellbook rejects a configuration whose frame does not match.
    Contract:
        - Initialization raises RuntimeError when config frame differs from spellbook frame.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    config = _make_configuration("frame-a")
    with pytest.raises(RuntimeError, match="Configuration name does not match"):
        Spellbook(aetheric_frame="frame-b", configuration=config)


def test_component_spellbook_initialize_configuration_creates_default_config_when_missing() -> None:
    """
    Purpose:
        Validate Spellbook creates a new Configuration when none is supplied.
    Contract:
        - A new Configuration instance is created for the requested frame.
        - Configuration is not locked when freshly created.
    Returns:
        None.
    Raises:
        AssertionError: If the configuration is missing or locked.
    """
    frame_name = "frame-config-new"
    spellbook = Spellbook(aetheric_frame=frame_name)
    try:
        config = spellbook.get_configuration()
        assert isinstance(config, Configuration)
        assert config._aether_frame == frame_name
        assert spellbook.is_configuration_locked() is False
    finally:
        spellbook.cleanup()


def test_component_spellbook_bind_configuration_to_aether_propagates_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate _bind_configuration_to_aether surfaces binding failures.
    Contract:
        - Exceptions from the Aether binder propagate to the caller.
    Args:
        monkeypatch: Pytest fixture for patching Aether binding behavior.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    spellbook = Spellbook()

    def _raise_bind(configuration: object, aetheric_frame_name: str = "default") -> None:
        """
        Purpose:
            Simulate an Aether configuration bind failure.
        Contract:
            Raises ValueError unconditionally.
        Args:
            configuration: Configuration instance to bind.
            aetheric_frame_name: Target frame name.
        Raises:
            ValueError: Always raised for the stub.
        """
        raise ValueError("bind-failed")

    try:
        monkeypatch.setattr(spellbook._aether, "_bind_configuration", _raise_bind)
        with pytest.raises(ValueError, match="bind-failed"):
            spellbook._bind_configuration_to_aether()
    finally:
        spellbook.cleanup()


def test_component_spellbook_get_configuration_from_aether_propagates_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate _get_configuration_from_aether surfaces Aether lookup errors.
    Contract:
        - Exceptions raised by Aether _get_configuration propagate to callers.
    Args:
        monkeypatch: Pytest fixture for patching Aether configuration lookup.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    spellbook = Spellbook()

    def _raise_get_configuration(aetheric_frame_name: str = "default") -> None:
        """
        Purpose:
            Simulate an Aether configuration lookup failure.
        Contract:
            Raises ValueError unconditionally.
        Args:
            aetheric_frame_name: Frame name provided by the caller.
        Raises:
            ValueError: Always raised for the stub.
        """
        raise ValueError(f"missing-frame:{aetheric_frame_name}")

    try:
        monkeypatch.setattr(spellbook._aether, "_get_configuration", _raise_get_configuration)
        with pytest.raises(ValueError, match="missing-frame"):
            spellbook._get_configuration_from_aether()
    finally:
        spellbook.cleanup()


def test_component_spellbook_initialize_configuration_propagates_aether_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Validate _initialize_configuration re-raises Aether lookup errors.
    Contract:
        - Exceptions from _get_configuration_from_aether propagate to the caller.
    Args:
        monkeypatch: Pytest fixture for patching configuration lookup.
    Returns:
        None.
    Raises:
        AssertionError: If the error is not raised.
    """
    spellbook = Spellbook()

    def _raise_get_configuration() -> None:
        """
        Purpose:
            Simulate a configuration lookup failure.
        Contract:
            Raises RuntimeError unconditionally.
        Raises:
            RuntimeError: Always raised for the stub.
        """
        raise RuntimeError("aether-lookup-failed")

    try:
        monkeypatch.setattr(spellbook, "_get_configuration_from_aether", _raise_get_configuration)
        spellbook._configuration = None
        spellbook._configuration_locked = False
        with pytest.raises(RuntimeError, match="aether-lookup-failed"):
            spellbook._initialize_configuration()
    finally:
        spellbook.cleanup()
