import threading

import pytest

from melder.aether.nexus.configuration.nexus_configuration import (
    NexusConfiguration,
)
from melder.aether.nexus.configuration.nexus_frame_mode import NexusFrameMode
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.aether.nexus.configuration.rift_validation_mode import (
    RiftValidationMode,
)


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

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    configuration = NexusConfiguration()
    coordinated_lock = _CoordinatedLock()
    configuration._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        configuration.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert configuration.cleaned is True
    assert configuration._lock is None


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
    assert configuration.get_property("default_space_type") is RiftSpaceType.dynamic
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
    assert configuration.get_property("default_target_frame_name") == "default"
    assert configuration.get_property("allowed_target_frame_names") == ("default",)

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

    denied_default = _build_valid_configuration()
    denied_default.set_property("denied_target_frame_names", ("default",))
    invalid_cases.append((denied_default, "default_target_frame_name cannot also be denied"))

    missing_default_in_allow = _build_valid_configuration()
    missing_default_in_allow.set_property("allowed_target_frame_names", ("ops",))
    invalid_cases.append((missing_default_in_allow, "default_target_frame_name must be present in allowed_target_frame_names"))

    empty_default_nexus = _build_valid_configuration()
    empty_default_nexus.set_property("default_nexus_frame_name", "")
    invalid_cases.append((empty_default_nexus, "default_nexus_frame_name cannot be empty"))

    empty_default_target = _build_valid_configuration()
    empty_default_target.set_property("default_target_frame_name", "")
    invalid_cases.append((empty_default_target, "default_target_frame_name cannot be empty"))

    for invalid_configuration, message in invalid_cases:
        with pytest.raises(ValueError, match=message):
            invalid_configuration.validate()


def test_nexus_configuration_freeze_finalize_and_build_return_self() -> None:
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
    invalid.validate = lambda: False
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
        .with_default_target_frame_name("ops")
        .with_allowed_target_frame_names(("ops", "default"))
        .with_denied_target_frame_names(("archive",))
        .with_target_frame_override(True)
        .with_multiple_target_frames(True)
        .with_max_target_frame_count(3)
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
    assert configuration.get_property("default_target_frame_name") == "ops"
    assert configuration.get_property("allowed_target_frame_names") == ("ops", "default")
    assert configuration.get_property("denied_target_frame_names") == ("archive",)
    assert configuration.get_property("allow_target_frame_override") is True
    assert configuration.get_property("allow_multiple_target_frames") is True
    assert configuration.get_property("max_target_frame_count") == 3
    assert configuration.get_property("default_space_type") is RiftSpaceType.dynamic
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
