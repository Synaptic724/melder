"""
Unit tests for the analysis IO-economy configuration knob
(site_package_dependency_descent): schema default, defaults lane, explicit
values, and freeze discipline.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)


def test_descent_knob_defaults_false_when_absent():
    """
    Purpose:
        Defaulted-optional contract: a roots-only configuration answers
        False without the key ever being set.
    Contract:
        No KeyError; the typed getter serves the schema default.
    """
    configuration = CrystallizerConfiguration()
    configuration.with_user_source_root_paths(("/tmp",))
    assert "site_package_dependency_descent" not in (
        configuration._properties
    )
    assert configuration.site_package_dependency_descent is False


def test_with_defaults_installs_descent_false():
    """
    Purpose:
        Easy-mode parity: with_defaults() writes the knob explicitly.
    Contract:
        Key present and False after with_defaults().
    """
    configuration = CrystallizerConfiguration().with_defaults()
    assert configuration._properties[
        "site_package_dependency_descent"
    ] is False
    assert configuration.site_package_dependency_descent is False


def test_descent_knob_reads_back_explicit_true():
    """
    Purpose:
        The reversibility lane: users restore the interior walk with one
        property write.
    Contract:
        True round-trips through the typed getter.
    """
    configuration = CrystallizerConfiguration()
    configuration.with_user_source_root_paths(("/tmp",))
    configuration.set_property("site_package_dependency_descent", True)
    assert configuration.site_package_dependency_descent is True


def test_descent_knob_rejects_non_bool_values():
    """
    Purpose:
        Schema typing law: the key is bool-typed.
    Contract:
        A non-bool set_property refuses.
    """
    configuration = CrystallizerConfiguration()
    with pytest.raises((TypeError, ValueError)):
        configuration.set_property(
            "site_package_dependency_descent", "yes"
        )


def test_frozen_configuration_rejects_descent_writes():
    """
    Purpose:
        Freeze discipline parity with every other knob.
    Contract:
        Writing after finalize()/freeze raises RuntimeError.
    """
    configuration = CrystallizerConfiguration().with_defaults().finalize()
    with pytest.raises(RuntimeError):
        configuration.set_property(
            "site_package_dependency_descent", True
        )
