from pathlib import Path

import pytest

from melder.crystallizer.configuration.crystallizer_configuration_builder import (
    CrystallizerConfigurationBuilder,
)
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)


def test_crystallizer_configuration_with_user_source_root_paths_normalizes_inputs() -> None:
    """
    Verify configured user source roots normalize and dedupe.

    Returns:
        None.
    """
    root = Path.cwd().resolve()
    nested = root / "src"
    configuration = CrystallizerConfiguration()

    configuration.with_user_source_root_paths((str(root), root, nested))

    assert configuration.user_source_root_paths == (root, nested.resolve())


def test_crystallizer_configuration_freeze_blocks_mutation() -> None:
    """
    Verify freeze closes later property mutation.

    Returns:
        None.
    """
    configuration = CrystallizerConfiguration()
    configuration.with_defaults()
    configuration.freeze()

    with pytest.raises(RuntimeError):
        configuration.with_user_source_root_paths((Path.cwd().resolve(),))


def test_crystallizer_configuration_activate_marks_state_and_freezes() -> None:
    """
    Verify activate validates, freezes, and marks the config active.

    Returns:
        None.
    """
    configuration = CrystallizerConfiguration()
    configuration.with_defaults()

    activated = configuration.activate()

    assert activated is configuration
    assert configuration.frozen is True
    assert configuration.activated is True


def test_crystallizer_configuration_validate_requires_user_source_roots() -> None:
    """
    Verify validation rejects missing root configuration.

    Returns:
        None.
    """
    configuration = CrystallizerConfiguration()

    with pytest.raises(ValueError):
        configuration.validate()


def test_crystallizer_configuration_builder_wraps_the_same_configuration() -> None:
    """
    Verify the builder activates and hands off one wrapped configuration.

    Returns:
        None.
    """
    builder = CrystallizerConfigurationBuilder()
    configuration = (
        builder
        .with_defaults()
        .with_user_source_root_paths((Path.cwd().resolve(),))
        .activate()
    )

    assert isinstance(configuration, CrystallizerConfiguration)
    assert configuration.activated is True
    assert builder.cleaned is True


def test_crystallizer_configuration_builder_cleanup_cleans_owned_configuration() -> None:
    """
    Verify builder cleanup tears down the still-owned configuration.

    Returns:
        None.
    """
    builder = CrystallizerConfigurationBuilder()
    configuration = builder._configuration

    builder.cleanup()

    assert builder.cleaned is True
    assert configuration.cleaned is True


def test_crystallizer_configuration_builder_is_consumed_after_build() -> None:
    """
    Verify the builder cannot be reused after handing off configuration.

    Returns:
        None.
    """
    builder = CrystallizerConfigurationBuilder()
    configuration = builder.build()

    assert isinstance(configuration, CrystallizerConfiguration)
    assert builder.cleaned is True

    with pytest.raises(RuntimeError):
        builder.with_defaults()
