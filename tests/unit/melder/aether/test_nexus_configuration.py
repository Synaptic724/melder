import pytest

from melder.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import (
    RiftValidationMode,
)
from tests._cleanup_recheck_support import CleanupRecheckHandshake


def _build_valid_configuration() -> NexusConfiguration:
    """
    Build one mutable Nexus configuration populated with the standard defaults.

    Returns:
        NexusConfiguration: Mutable config with all required properties loaded.
    """
    configuration = NexusConfiguration()
    configuration.load_default_dictionary()
    return configuration


def test_nexus_configuration_exposes_id_and_frozen_state() -> None:
    """
    Verify the configuration exposes its stable id and mutable/frozen posture.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    assert configuration.id is not None
    assert configuration.frozen is False


def test_nexus_configuration_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_nexus_configuration_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the config.

    The handshake holds the first caller inside the lock until the second has passed the outer `_cleaned` check
    and is about to block; the first caller then runs the real cleanup. The second caller must return at the
    inner recheck - without it the teardown would run twice and a caller would raise on an attribute the other
    had already deleted - so both callers finish without raising and the config reads cleaned with its `_lock`
    dropped. The callers are ordered by the handshake, not by timing: the earlier hand-made lock could lose its
    signal and failed on CI (GitHub #206; TASK-2026-11-08-deterministic_cleanup_recheck_handshake).

    Returns:
        None.
    """
    configuration = NexusConfiguration()
    handshake = CleanupRecheckHandshake()
    configuration._lock = handshake.lock

    handshake.run(configuration.cleanup)

    assert configuration.cleaned is True
    assert not hasattr(configuration, '_lock')


def test_nexus_configuration_set_property_normalizes_enums_and_frame_names() -> None:
    """
    Verify property assignment normalizes enum-backed and sequence-backed values.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    configuration.set_property("nexus_frame_mode", "indexed")
    configuration.set_property("default_space_type", "dynamic")
    configuration.set_property("default_validation_mode", "strict")
    configuration.set_property(
        "allowed_target_frame_names",
        ["default", "ops", "default"],
    )
    configuration.set_property(
        "denied_target_frame_names",
        ("shadow", "shadow", "archive"),
    )

    assert configuration.get_property("nexus_frame_mode") is NexusFrameMode.indexed
    assert configuration.get_property("default_space_type") is RiftSpaceType.codegen
    assert configuration.get_property("default_validation_mode") is RiftValidationMode.strict
    assert configuration.get_property("allowed_target_frame_names") == (
        "default",
        "ops",
    )
    assert configuration.get_property("denied_target_frame_names") == (
        "shadow",
        "archive",
    )


def test_nexus_configuration_set_property_rejects_unknown_frozen_and_wrong_types() -> None:
    """
    Verify property assignment enforces key, frozen, and type contracts.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    with pytest.raises(ValueError, match="Unknown NexusConfiguration property"):
        configuration.set_property("unknown_key", True)

    configuration.load_default_dictionary()
    configuration.freeze()

    with pytest.raises(RuntimeError, match="Cannot modify NexusConfiguration after freeze"):
        configuration.set_property("allow_rift_creation", False)

    other = NexusConfiguration()
    with pytest.raises(TypeError, match="Invalid type for property 'max_active_rift_count'"):
        other.set_property("max_active_rift_count", "two")


def test_nexus_configuration_property_helpers_and_defaults_work() -> None:
    """
    Verify default loading, get/has helpers, and fluent defaults behavior.

    Returns:
        None.
    """
    configuration = NexusConfiguration().with_defaults()

    assert configuration.has_property("allow_rift_creation") is True
    assert configuration.get_property("allow_rift_creation") is True
    assert configuration.get_property("nexus_frame_mode") is NexusFrameMode.single
    assert configuration.get_property("allowed_target_frame_names") == ("default",)
    assert configuration.get_property("projection_refresh_gate_enabled") is True
    assert configuration.get_property("projection_refresh_gate_timeout_seconds") == 30.0
    assert (
        configuration.get_property("projection_refresh_gate_poll_interval_seconds")
        == 0.1
    )

    with pytest.raises(KeyError):
        NexusConfiguration().get_property("allow_rift_creation")


def test_nexus_configuration_validate_rejects_missing_properties_and_invalid_invariants() -> None:
    """
    Verify validation rejects missing properties and cross-field invariant breaks.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    with pytest.raises(ValueError, match="Missing required configuration property"):
        configuration.validate()

    invalid_cases = []

    negative_rifts = _build_valid_configuration()
    negative_rifts.set_property("max_active_rift_count", -1)
    invalid_cases.append((negative_rifts, "max_active_rift_count must be >= 0"))

    bad_nexus_frame_count = _build_valid_configuration()
    bad_nexus_frame_count.set_property("max_nexus_frame_count", 0)
    invalid_cases.append((bad_nexus_frame_count, "max_nexus_frame_count must be >= 1"))

    bad_target_frame_count = _build_valid_configuration()
    bad_target_frame_count.set_property("max_target_frame_count", 0)
    invalid_cases.append((bad_target_frame_count, "max_target_frame_count must be >= 1"))

    bad_single_mode = _build_valid_configuration()
    bad_single_mode.set_property("max_nexus_frame_count", 2)
    invalid_cases.append((bad_single_mode, "max_nexus_frame_count must be 1 when nexus_frame_mode is single"))

    bad_multiple_target = _build_valid_configuration()
    bad_multiple_target.set_property("max_target_frame_count", 2)
    invalid_cases.append((bad_multiple_target, "max_target_frame_count must be 1 when allow_multiple_target_frames is False"))

    bad_refresh_timeout = _build_valid_configuration()
    bad_refresh_timeout.set_property("projection_refresh_gate_timeout_seconds", 0)
    invalid_cases.append((bad_refresh_timeout, "projection_refresh_gate_timeout_seconds must be > 0"))

    bad_refresh_interval = _build_valid_configuration()
    bad_refresh_interval.set_property("projection_refresh_gate_poll_interval_seconds", 0)
    invalid_cases.append((bad_refresh_interval, "projection_refresh_gate_poll_interval_seconds must be > 0"))

    empty_default_nexus = _build_valid_configuration()
    empty_default_nexus.set_property("default_nexus_frame_name", "")
    invalid_cases.append((empty_default_nexus, "default_nexus_frame_name cannot be empty"))

    for invalid_configuration, message in invalid_cases:
        with pytest.raises(ValueError, match=message):
            invalid_configuration.validate()


def test_nexus_configuration_freeze_finalize_and_build_return_self(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify freeze/finalize/build enforce validation and preserve fluent identity.

    Returns:
        None.
    """
    configuration = _build_valid_configuration()

    configuration.freeze()
    assert configuration.frozen is True

    finalized_source = _build_valid_configuration()
    built_source = _build_valid_configuration()
    finalized = finalized_source.finalize()
    built = built_source.build()

    assert finalized.frozen is True
    assert built.frozen is True
    assert finalized is finalized_source
    assert built is built_source

    frozen_before = configuration.frozen
    configuration.freeze()
    assert configuration.frozen is frozen_before

    invalid = _build_valid_configuration()
    monkeypatch.setattr(NexusConfiguration, "validate", lambda self: False)
    with pytest.raises(ValueError, match="NexusConfiguration validation failed"):
        invalid.freeze()


def test_nexus_configuration_fluent_setters_return_self_and_store_values() -> None:
    """
    Verify the fluent `with_*` API stores values and preserves builder chaining.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    chained = (
        configuration
        .with_rift_creation_enabled(True)
        .with_creation_token_required(True)
        .with_creation_token("create-token")
        .with_direct_rift_access(True)
        .with_rift_access_token_required(True)
        .with_rift_access_token("access-token")
        .with_allow_external_rift_registration(False)
        .with_allow_nested_rift_creation(True)
        .with_max_active_rift_count(2)
        .with_nexus_frame_mode("indexed")
        .with_default_nexus_frame_name("nexus-main")
        .with_auto_create_nexus_frames(False)
        .with_max_nexus_frame_count(3)
        .with_allowed_target_frame_names(("ops", "default"))
        .with_denied_target_frame_names(("archive",))
        .with_target_frame_override(True)
        .with_multiple_target_frames(True)
        .with_max_target_frame_count(3)
        .with_projection_refresh_gate(False)
        .with_projection_refresh_gate_timeout_seconds(9.5)
        .with_projection_refresh_gate_poll_interval_seconds(0.25)
        .with_default_space_type("dynamic")
        .with_default_auto_activate_on_program(False)
        .with_default_auto_create_space(True)
        .with_default_validation_mode("strict")
    )

    assert chained is configuration
    assert configuration.get_property("allow_rift_creation") is True
    assert configuration.get_property("creation_token_required") is True
    assert configuration.get_property("creation_token_value") == "create-token"
    assert configuration.get_property("allow_direct_rift_access") is True
    assert configuration.get_property("rift_access_token_required") is True
    assert configuration.get_property("rift_access_token_value") == "access-token"
    assert configuration.get_property("allow_external_rift_registration") is False
    assert configuration.get_property("allow_nested_rift_creation") is True
    assert configuration.get_property("max_active_rift_count") == 2
    assert configuration.get_property("nexus_frame_mode") is NexusFrameMode.indexed
    assert configuration.get_property("default_nexus_frame_name") == "nexus-main"
    assert configuration.get_property("auto_create_nexus_frames") is False
    assert configuration.get_property("max_nexus_frame_count") == 3
    assert configuration.get_property("allowed_target_frame_names") == ("ops", "default")
    assert configuration.get_property("denied_target_frame_names") == ("archive",)
    assert configuration.get_property("allow_target_frame_override") is True
    assert configuration.get_property("allow_multiple_target_frames") is True
    assert configuration.get_property("max_target_frame_count") == 3
    assert configuration.get_property("projection_refresh_gate_enabled") is False
    assert configuration.get_property("projection_refresh_gate_timeout_seconds") == 9.5
    assert configuration.get_property("projection_refresh_gate_poll_interval_seconds") == 0.25
    assert configuration.get_property("default_space_type") is RiftSpaceType.codegen
    assert configuration.get_property("default_auto_activate_on_program") is False
    assert configuration.get_property("default_auto_create_space") is True
    assert configuration.get_property("default_validation_mode") is RiftValidationMode.strict


def test_nexus_configuration_normalize_frame_names_rejects_bad_input() -> None:
    """
    Verify frame-name normalization rejects bad shapes and empty names.

    Returns:
        None.
    """
    configuration = NexusConfiguration()

    with pytest.raises(TypeError, match="not a single string"):
        configuration.set_property("allowed_target_frame_names", "default")

    with pytest.raises(TypeError, match="must be sequences of strings"):
        configuration.set_property("allowed_target_frame_names", 42)

    with pytest.raises(TypeError, match="must contain only strings"):
        configuration.set_property("allowed_target_frame_names", ("default", 1))

    with pytest.raises(ValueError, match="Frame names cannot be empty"):
        configuration.set_property("allowed_target_frame_names", ("default", ""))
