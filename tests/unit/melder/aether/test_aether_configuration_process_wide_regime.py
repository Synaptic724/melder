"""
Unit tests for `AetherConfiguration.process_wide_unique_spell_ids`.

This flag decides whether a spell_id may exist once per PROCESS or once per
FRAME. It is the switch that retires (or restores) per-frame multi-tenancy, so
its default, its freeze behaviour and its type discipline all carry weight:

- DEFAULT TRUE. Frames are lazy - `import melder` creates zero frames - so a
  frame can be born before any configuration is installed and must still get
  the documented regime rather than falling open.
- FREEZE-GUARDED HARDER THAN THE LOGGER FLAGS. Frames capture the regime when
  they are born, so flipping it mid-process would strand ids across two
  registries with no single surface able to answer whether an id exists.

Pure configuration object - no Aether singleton, no frames, no fixture needed.
"""

from typing import Any

import pytest

from melder.aether.aether_configuration import AetherConfiguration


def test_process_wide_unique_spell_ids_defaults_to_true() -> None:
    """
    Purpose:
        A fresh, unseeded configuration must already carry the documented
        default, because `__init__` seeds `_properties` directly and a frame may
        read the regime before `with_defaults()` is ever called.
    Returns:
        None.
    Raises:
        AssertionError: If the default is not True.
    """
    configuration = AetherConfiguration()
    assert configuration.process_wide_unique_spell_ids is True


def test_with_defaults_seeds_process_wide_unique_spell_ids() -> None:
    """
    Purpose:
        `with_defaults()` overwrites everything set earlier, so it must seed this
        flag too or calling it would silently revert an explicit choice.
    Returns:
        None.
    Raises:
        AssertionError: If `with_defaults()` does not restore True.
    """
    configuration = AetherConfiguration()
    configuration.set_process_wide_unique_spell_ids(False)
    assert configuration.process_wide_unique_spell_ids is False

    returned = configuration.with_defaults()

    assert returned is configuration, "with_defaults must return self, not a copy"
    assert configuration.process_wide_unique_spell_ids is True


def test_set_process_wide_unique_spell_ids_round_trips() -> None:
    """
    Purpose:
        The imperative setter must store both values.
    Returns:
        None.
    Raises:
        AssertionError: If either value fails to round-trip.
    """
    configuration = AetherConfiguration().with_defaults()

    configuration.set_process_wide_unique_spell_ids(False)
    assert configuration.process_wide_unique_spell_ids is False

    configuration.set_process_wide_unique_spell_ids(True)
    assert configuration.process_wide_unique_spell_ids is True


def test_with_process_wide_unique_spell_ids_is_fluent_and_mutating() -> None:
    """
    Purpose:
        The fluent setter must mutate in place and return the same instance,
        matching the sibling `with_*` builders on this class.
    Returns:
        None.
    Raises:
        AssertionError: If it copies, or fails to apply the value.
    """
    configuration = AetherConfiguration().with_defaults()

    returned = configuration.with_process_wide_unique_spell_ids(False)

    assert returned is configuration, "fluent setters mutate; they do not copy"
    assert configuration.process_wide_unique_spell_ids is False


def test_setter_rejects_non_bool() -> None:
    """
    Purpose:
        A truthy non-bool must be refused rather than coerced. The regime is read
        on the bind path and a drifted type would be silently truthy forever.
    Returns:
        None.
    Raises:
        AssertionError: If a non-bool is accepted.
    """
    configuration = AetherConfiguration().with_defaults()

    # Passed through `Any` deliberately: the point is a RUNTIME type refusal,
    # and inline suppression comments are a banned pattern in this repository.
    truthy_string: Any = "yes"
    truthy_int: Any = 1

    with pytest.raises(TypeError):
        configuration.set_process_wide_unique_spell_ids(truthy_string)

    with pytest.raises(TypeError):
        configuration.set_process_wide_unique_spell_ids(truthy_int)

    assert configuration.process_wide_unique_spell_ids is True, (
        "a refused assignment must leave the previous value intact"
    )


def test_setter_is_refused_after_freeze() -> None:
    """
    Purpose:
        THE LOAD-BEARING GUARANTEE. Frames capture the regime at birth, so the
        regime must not change under a live world - otherwise some ids sit in the
        unified surface and others in per-frame ones, and nothing can answer
        whether an id exists.
    Returns:
        None.
    Raises:
        AssertionError: If a frozen configuration accepts a regime change.
    """
    configuration = AetherConfiguration().with_defaults()
    configuration.freeze()

    with pytest.raises(RuntimeError):
        configuration.set_process_wide_unique_spell_ids(False)

    with pytest.raises(RuntimeError):
        configuration.with_process_wide_unique_spell_ids(False)

    assert configuration.process_wide_unique_spell_ids is True, (
        "the sealed value must survive a refused post-freeze write"
    )


def test_frozen_read_is_stable() -> None:
    """
    Purpose:
        A value set before freeze must still read back after it - the seal
        preserves the choice rather than resetting to the default.
    Returns:
        None.
    Raises:
        AssertionError: If freezing loses the configured value.
    """
    configuration = AetherConfiguration().with_defaults()
    configuration.set_process_wide_unique_spell_ids(False)
    configuration.freeze()

    assert configuration.process_wide_unique_spell_ids is False


def test_property_refuses_a_tampered_value() -> None:
    """
    Purpose:
        The defensive read guards the backing map against direct tampering, which
        is the documented contract on every property of this class.
    Contract:
        - Writing a non-bool straight into `_properties` must raise on READ
          rather than returning a truthy string to the bind path.
    Returns:
        None.
    Raises:
        AssertionError: If a drifted value is returned instead of raising.
    """
    configuration = AetherConfiguration().with_defaults()
    configuration._properties["process_wide_unique_spell_ids"] = "true"

    with pytest.raises(TypeError):
        _ = configuration.process_wide_unique_spell_ids
