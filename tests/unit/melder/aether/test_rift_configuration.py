import threading

import pytest

from melder.nexus.configuration.rift_configuration import RiftConfiguration
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.configuration.rift_validation_mode import (
    RiftValidationMode,
)


def _build_valid_configuration() -> RiftConfiguration:
    """
    Build one mutable Rift configuration populated with the standard defaults.

    Returns:
        RiftConfiguration: Mutable config with all required properties loaded.
    """
    configuration = RiftConfiguration()
    configuration.load_default_dictionary()
    return configuration


def test_rift_configuration_exposes_frozen_and_consumed_state() -> None:
    """
    Verify the configuration exposes its mutable/frozen and consumed posture.
    """
    configuration = RiftConfiguration()

    assert configuration.frozen is False
    assert configuration.consumed is False


def test_rift_configuration_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.
    """
    configuration = RiftConfiguration()

    configuration.cleanup()
    configuration.cleanup()

    assert configuration.cleaned is True


def test_rift_configuration_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the config.
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

    configuration = RiftConfiguration()
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
    assert not hasattr(configuration, '_lock')


def test_rift_configuration_set_property_normalizes_enums() -> None:
    """
    Verify property assignment normalizes enum-backed values.
    """
    configuration = RiftConfiguration()

    configuration.set_property("space_type", "dynamic")
    configuration.set_property("validation_mode", "strict")

    assert configuration.get_property("space_type") is RiftSpaceType.codegen
    assert configuration.get_property("validation_mode") is RiftValidationMode.strict


def test_rift_configuration_set_property_rejects_unknown_frozen_consumed_and_wrong_types() -> None:
    """
    Verify property assignment enforces key, lifecycle, and type contracts.
    """
    configuration = RiftConfiguration()

    with pytest.raises(ValueError, match="Unknown RiftConfiguration property"):
        configuration.set_property("unknown_key", True)

    with pytest.raises(ValueError, match="Expected a string or RiftSpaceType member"):
        configuration.set_property("space_type", object())

    frozen = _build_valid_configuration()
    frozen.freeze()

    with pytest.raises(RuntimeError, match="Cannot modify RiftConfiguration after freeze"):
        frozen.set_property("space_name", "ops")

    consumed = _build_valid_configuration()
    consumed.mark_consumed()

    with pytest.raises(RuntimeError, match="Cannot modify RiftConfiguration after it has been consumed"):
        consumed.set_property("space_name", "ops")


def test_rift_configuration_property_helpers_and_defaults_work() -> None:
    """
    Verify default loading and property helper behavior.
    """
    configuration = RiftConfiguration().with_defaults()

    assert configuration.has_property("space_type") is True
    assert configuration.get_property("space_type") is RiftSpaceType.static
    assert configuration.get_property("space_name") is None
    assert configuration.get_property("auto_activate_on_program") is True
    assert configuration.get_property("validation_mode") is RiftValidationMode.strict

    with pytest.raises(KeyError):
        RiftConfiguration().get_property("space_type")


def test_rift_configuration_validate_rejects_missing_properties() -> None:
    """
    Verify validation rejects incomplete property bags.
    """
    configuration = RiftConfiguration()

    with pytest.raises(ValueError, match="Missing required configuration property"):
        configuration.validate()


def test_rift_configuration_freeze_finalize_and_build_return_self() -> None:
    """
    Verify freeze/finalize/build enforce validation and preserve identity.
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
    with pytest.raises(ValueError, match="RiftConfiguration validation failed"):
        invalid.freeze()


def test_rift_configuration_fluent_setters_return_self_and_store_values() -> None:
    """
    Verify the fluent `with_*` API stores values and preserves chaining.
    """
    configuration = RiftConfiguration()

    chained = (
        configuration
        .with_space_type("dynamic")
        .with_space_name("ops-room")
        .with_auto_activate_on_program(False)
        .with_validation_mode("strict")
    )

    assert chained is configuration
    assert configuration.get_property("space_type") is RiftSpaceType.codegen
    assert configuration.get_property("space_name") == "ops-room"
    assert configuration.get_property("auto_activate_on_program") is False
    assert configuration.get_property("validation_mode") is RiftValidationMode.strict


def test_rift_configuration_mark_consumed_sets_consumed_state() -> None:
    """
    Verify mark_consumed flips the single-use state without cleanup.
    """
    configuration = RiftConfiguration()

    configuration.mark_consumed()

    assert configuration.consumed is True
    assert configuration.frozen is False
