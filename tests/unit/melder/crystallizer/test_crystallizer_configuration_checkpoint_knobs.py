"""
Unit contract tests for the CrystallizerConfiguration checkpoint knobs:
defaulting getters, the full with_defaults() easy mode (regression for the
all-keys validate bug), builder validation, and freeze discipline.
"""
import pytest

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)


def test_checkpoint_knobs_default_without_being_set():
    """
    Purpose:
        Verify the defaulting getters.
    Contract:
        checkpoint_interval_minutes defaults to 60 and
        max_persistence_crystals to 100 when never set.
    Returns:
        None.
    Raises:
        AssertionError: If the documented defaults drift.
    """
    configuration = CrystallizerConfiguration()
    assert configuration.checkpoint_interval_minutes == 60
    assert configuration.max_persistence_crystals == 100


def test_with_defaults_installs_a_complete_valid_configuration():
    """
    Purpose:
        Regression: with_defaults() must produce an activatable config.
    Contract:
        All four knobs are installed; validate() passes; activate()
        freezes and marks the configuration activated.
    Returns:
        None.
    Raises:
        AssertionError: If easy mode cannot activate (the C4-era bug).
    """
    configuration = CrystallizerConfiguration().with_defaults()
    assert configuration.validate() is True
    configuration.activate()
    assert configuration.frozen is True
    assert configuration.activated is True
    assert configuration.remove_inactive_synthmodules is False
    assert configuration.checkpoint_interval_minutes == 60
    assert configuration.max_persistence_crystals == 100


def test_roots_only_configuration_validates():
    """
    Purpose:
        Regression: only user_source_root_paths is hard-required.
    Contract:
        A configuration with just the roots validates; the defaulted
        knobs are not required properties.
    Returns:
        None.
    Raises:
        AssertionError: If defaulted knobs are hard-required again.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    )
    assert configuration.validate() is True


def test_validate_requires_source_roots_with_teaching_error():
    """
    Purpose:
        Verify the single hard requirement's error quality.
    Contract:
        Missing roots raise ValueError naming the property and pointing
        at with_defaults().
    Returns:
        None.
    Raises:
        AssertionError: If the teach-grade error drifts.
    """
    configuration = CrystallizerConfiguration()
    with pytest.raises(ValueError, match="user_source_root_paths"):
        configuration.validate()


def test_builders_chain_and_store_values():
    """
    Purpose:
        Verify the fluent knob builders.
    Contract:
        Builders return self for chaining and the getters read the
        stored values back.
    Returns:
        None.
    Raises:
        AssertionError: If chaining or storage drifts.
    """
    configuration = (
        CrystallizerConfiguration()
        .with_user_source_root_paths((".",))
        .with_checkpoint_interval_minutes(5)
        .with_max_persistence_crystals(250)
    )
    assert configuration.checkpoint_interval_minutes == 5
    assert configuration.max_persistence_crystals == 250
    assert configuration.validate() is True


def test_builders_reject_bool_zero_and_negative_values():
    """
    Purpose:
        Verify positive-int validation at the builder boundary.
    Contract:
        True, 0, and -5 all raise ValueError for both knobs (bool is an
        int subtype and must be rejected explicitly).
    Returns:
        None.
    Raises:
        AssertionError: If a non-positive or bool value is accepted.
    """
    configuration = CrystallizerConfiguration()
    for bad in (True, 0, -5):
        with pytest.raises(ValueError, match="positive int"):
            configuration.with_checkpoint_interval_minutes(bad)
        with pytest.raises(ValueError, match="positive int"):
            configuration.with_max_persistence_crystals(bad)


def test_validate_catches_bool_smuggled_through_set_property():
    """
    Purpose:
        Verify the bool trap is caught at validation time.
    Contract:
        set_property accepts True for an int knob (isinstance subtype),
        but validate() rejects it with the positive-int error.
    Returns:
        None.
    Raises:
        AssertionError: If a smuggled bool validates.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    )
    configuration.set_property("checkpoint_interval_minutes", True)
    with pytest.raises(ValueError, match="positive int"):
        configuration.validate()


def test_set_property_guards_unknown_keys_and_types():
    """
    Purpose:
        Verify the property bag guards.
    Contract:
        Unknown keys raise ValueError; type mismatches raise TypeError.
    Returns:
        None.
    Raises:
        AssertionError: If the guards drift.
    """
    configuration = CrystallizerConfiguration()
    with pytest.raises(ValueError, match="Unknown"):
        configuration.set_property("not_a_knob", 1)
    with pytest.raises(TypeError):
        configuration.set_property("max_persistence_crystals", "many")


def test_frozen_configuration_rejects_mutation():
    """
    Purpose:
        Verify freeze discipline over the new knobs.
    Contract:
        After finalize(), set_property raises RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a frozen config mutates.
    """
    configuration = CrystallizerConfiguration().with_defaults().finalize()
    with pytest.raises(RuntimeError, match="after freeze"):
        configuration.set_property("checkpoint_interval_minutes", 5)
