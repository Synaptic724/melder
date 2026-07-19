"""
Unit contract tests for the CrystallizerConfiguration RESTORE-lane knobs
(parallel_restore_ulid_identity S2/S4): the three defaulting getters
(restore_parallel_enabled, restore_scheduler_workers,
restore_scheduler_barrier_timeout_milliseconds), their optionality under
validate(), positive-int discipline on the two int knobs, the reload-lane
backfill floor, and freeze discipline.

These lock the REOPEN root cause (2026-07-19): Crystallizer.activate()
read the three knobs unconditionally and KeyError'd for every configuration
built without with_defaults(). The fix made them defaulted-optional typed
properties; this suite pins that contract from the configuration side.

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)


def test_restore_knobs_default_without_being_set():
    """
    Purpose:
        Verify the three restore getters return schema defaults when the
        knobs were never set (the exact shape the red run activated).
    Contract:
        restore_parallel_enabled -> True (parallel is the driver),
        restore_scheduler_workers -> 4, and
        restore_scheduler_barrier_timeout_milliseconds -> 60000.
    Returns:
        None.
    Raises:
        AssertionError: If any documented default drifts.
    """
    configuration = CrystallizerConfiguration()
    assert configuration.restore_parallel_enabled is True
    assert configuration.restore_scheduler_workers == 4
    assert (
        configuration.restore_scheduler_barrier_timeout_milliseconds == 60000
    )


def test_roots_only_configuration_validates_with_optional_restore_knobs():
    """
    Purpose:
        Regression for the KeyError root cause: only
        user_source_root_paths is hard-required, and the three restore
        knobs must be optional at validate() time.
    Contract:
        A configuration carrying just the source roots validates True; the
        restore knobs are absent from _properties yet do not fail
        validation.
    Returns:
        None.
    Raises:
        AssertionError: If a restore knob is treated as hard-required.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    )
    assert configuration.validate() is True
    assert "restore_parallel_enabled" not in configuration._properties
    assert "restore_scheduler_workers" not in configuration._properties
    assert (
        "restore_scheduler_barrier_timeout_milliseconds"
        not in configuration._properties
    )


def test_with_defaults_installs_all_three_restore_knobs_explicitly():
    """
    Purpose:
        Verify with_defaults() writes the three restore knobs so a
        cache-boot / easy-mode configuration is complete and activatable.
    Contract:
        After with_defaults(), each knob is present in _properties and
        reads its documented value; validate() passes.
    Returns:
        None.
    Raises:
        AssertionError: If any restore knob is missing from easy mode.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    assert configuration.validate() is True
    assert configuration._properties["restore_parallel_enabled"] is True
    assert configuration._properties["restore_scheduler_workers"] == 4
    assert (
        configuration._properties[
            "restore_scheduler_barrier_timeout_milliseconds"
        ]
        == 60000
    )


def test_explicit_restore_values_read_back_and_override_defaults():
    """
    Purpose:
        Verify set_property values win over the schema defaults.
    Contract:
        Setting False / 9 / 30000 makes the getters return exactly those
        values instead of the True / 4 / 60000 defaults.
    Returns:
        None.
    Raises:
        AssertionError: If an explicit override is not honored.
    """
    configuration = CrystallizerConfiguration()
    configuration.set_property("restore_parallel_enabled", False)
    configuration.set_property("restore_scheduler_workers", 9)
    configuration.set_property(
        "restore_scheduler_barrier_timeout_milliseconds", 30000
    )
    assert configuration.restore_parallel_enabled is False
    assert configuration.restore_scheduler_workers == 9
    assert (
        configuration.restore_scheduler_barrier_timeout_milliseconds == 30000
    )


def test_restore_parallel_enabled_accepts_both_polarities():
    """
    Purpose:
        Verify the driver selector is a real bool knob (no positive-int
        trap - False and 0-like values are legitimate).
    Contract:
        Explicit True and explicit False both read back faithfully; the
        selector never raises for a bool value.
    Returns:
        None.
    Raises:
        AssertionError: If a bool polarity is rejected or coerced.
    """
    on = CrystallizerConfiguration()
    on.set_property("restore_parallel_enabled", True)
    assert on.restore_parallel_enabled is True

    off = CrystallizerConfiguration()
    off.set_property("restore_parallel_enabled", False)
    assert off.restore_parallel_enabled is False


def test_int_restore_knobs_reject_bool_zero_and_negative_via_getter():
    """
    Purpose:
        Verify positive-int discipline on the two int knobs at read time.
    Contract:
        A stored True, 0, or -1 makes the getter raise ValueError naming
        the positive-int rule (bool is an int subtype and must be caught).
    Returns:
        None.
    Raises:
        AssertionError: If a non-positive or bool int value is accepted.
    """
    for bad in (True, 0, -1):
        workers = CrystallizerConfiguration()
        workers._properties["restore_scheduler_workers"] = bad
        with pytest.raises(ValueError, match="positive int"):
            _ = workers.restore_scheduler_workers

        timeout = CrystallizerConfiguration()
        timeout._properties[
            "restore_scheduler_barrier_timeout_milliseconds"
        ] = bad
        with pytest.raises(ValueError, match="positive int"):
            _ = timeout.restore_scheduler_barrier_timeout_milliseconds


def test_validate_catches_bad_int_restore_knobs_when_set_explicitly():
    """
    Purpose:
        Verify validate() semantically checks the int restore knobs only
        when they are set explicitly (optional-but-checked contract).
    Contract:
        A roots-valid configuration with a smuggled bool worker count
        fails validate() with the positive-int error.
    Returns:
        None.
    Raises:
        AssertionError: If a smuggled bad int validates.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    )
    configuration.set_property("restore_scheduler_workers", True)
    with pytest.raises(ValueError, match="positive int"):
        configuration.validate()


def test_set_property_guards_unknown_and_typed_restore_keys():
    """
    Purpose:
        Verify the property bag guards the restore knobs by schema type.
    Contract:
        A string worker count raises TypeError (schema says int); the
        driver selector is a registered key (no Unknown error).
    Returns:
        None.
    Raises:
        AssertionError: If the schema guards drift.
    """
    configuration = CrystallizerConfiguration()
    with pytest.raises(TypeError):
        configuration.set_property("restore_scheduler_workers", "four")
    # Registered key: setting a valid bool must not raise Unknown.
    configuration.set_property("restore_parallel_enabled", True)
    assert configuration.restore_parallel_enabled is True


def test_reload_lane_backfills_all_three_restore_knobs():
    """
    Purpose:
        Regression for the reload-lanes expectation update: a pre-epic
        recorded payload (no restore keys) backfills the three schema
        defaults, reported per key.
    Contract:
        load_recorded_dictionary over a payload missing the restore keys
        reports all three in outcome["backfilled"] and the getters read
        their defaults.
    Returns:
        None.
    Raises:
        AssertionError: If a restore knob is not backfilled or reported.
    """
    configuration = CrystallizerConfiguration()
    outcome = configuration.load_recorded_dictionary({
        "user_source_root_paths": ["/recorded/root"],
        "checkpoint_interval_minutes": 15,
        "max_persistence_crystals": 25,
    })
    assert outcome["rejected"] == []
    backfilled = set(outcome["backfilled"])
    assert "restore_parallel_enabled" in backfilled
    assert "restore_scheduler_workers" in backfilled
    assert (
        "restore_scheduler_barrier_timeout_milliseconds" in backfilled
    )
    assert configuration.restore_parallel_enabled is True
    assert configuration.restore_scheduler_workers == 4
    assert (
        configuration.restore_scheduler_barrier_timeout_milliseconds == 60000
    )


def test_reload_lane_keeps_recorded_restore_values_over_defaults():
    """
    Purpose:
        Verify recorded truth wins over the backfill floor for the
        restore knobs (owner law: recorded values, never defaults).
    Contract:
        A payload carrying explicit restore values reloads them verbatim
        and does NOT report them as backfilled.
    Returns:
        None.
    Raises:
        AssertionError: If a recorded restore value is lost to the default.
    """
    configuration = CrystallizerConfiguration()
    outcome = configuration.load_recorded_dictionary({
        "user_source_root_paths": ["/recorded/root"],
        "restore_parallel_enabled": False,
        "restore_scheduler_workers": 7,
        "restore_scheduler_barrier_timeout_milliseconds": 45000,
    })
    assert outcome["rejected"] == []
    backfilled = set(outcome["backfilled"])
    assert "restore_parallel_enabled" not in backfilled
    assert "restore_scheduler_workers" not in backfilled
    assert (
        "restore_scheduler_barrier_timeout_milliseconds" not in backfilled
    )
    assert configuration.restore_parallel_enabled is False
    assert configuration.restore_scheduler_workers == 7
    assert (
        configuration.restore_scheduler_barrier_timeout_milliseconds == 45000
    )


def test_frozen_configuration_rejects_restore_knob_mutation():
    """
    Purpose:
        Verify freeze discipline over the restore knobs.
    Contract:
        After finalize(), set_property on a restore knob raises
        RuntimeError.
    Returns:
        None.
    Raises:
        AssertionError: If a frozen configuration mutates a restore knob.
    """
    configuration = CrystallizerConfiguration().with_defaults().finalize()
    with pytest.raises(RuntimeError, match="after freeze"):
        configuration.set_property("restore_scheduler_workers", 8)


def test_activated_configuration_exposes_restore_defaults_for_the_loader():
    """
    Purpose:
        End-to-end config-side proof of the KeyError fix: a bare, activated
        configuration answers the three properties the crystallizer reads
        at activation without ever raising.
    Contract:
        with_user_source_root_paths(...).activate() yields a frozen,
        activated configuration whose three restore getters return the
        schema defaults - the read path Crystallizer.activate() now uses.
    Returns:
        None.
    Raises:
        AssertionError: If the loader-facing read path is not clean.
    """
    configuration = CrystallizerConfiguration().with_user_source_root_paths(
        (".",)
    ).activate()
    assert configuration.frozen is True
    assert configuration.activated is True
    assert configuration.restore_parallel_enabled is True
    assert configuration.restore_scheduler_workers == 4
    assert (
        configuration.restore_scheduler_barrier_timeout_milliseconds == 60000
    )
