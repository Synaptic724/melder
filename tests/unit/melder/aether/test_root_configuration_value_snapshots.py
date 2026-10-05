"""
Unit tests for `get_configuration_dictionary()` on the four root configurations.

WHY THIS EXISTS. A host that embeds Melder next to another Melder user compares
the policy it was handed with the one already installed on a root (MelderOps
does this before reusing or refusing). Aether, Crystallizer, MutationResearch
and Nexus configurations keep their values in a private property bag and had no
public way to read all of them, so the comparison crashed with AttributeError.
Each now returns a snapshot of the properties it holds (0.2.8212).

Contract under test, for every root configuration:
    1. the snapshot carries exactly the values the public readers return;
    2. it is a NEW dict - editing it never edits the configuration;
    3. values are the stored objects, by reference;
    4. equal construction compares equal, one setter makes them differ;
    5. reading it never freezes or activates, and it works frozen and activated;
    6. a cleaned configuration refuses with RuntimeError.
"""

import logging
from typing import Callable, Union

import pytest

from melder import (
    AetherConfiguration,
    CrystallizerConfiguration,
    MutationResearchConfiguration,
    NexusConfiguration,
)

RootConfiguration = Union[
    AetherConfiguration, CrystallizerConfiguration, MutationResearchConfiguration, NexusConfiguration,
]


def _aether() -> AetherConfiguration:
    """Return an Aether configuration seeded with its defaults."""
    return AetherConfiguration().with_defaults()


def _crystallizer() -> CrystallizerConfiguration:
    """Return a Crystallizer configuration seeded with its defaults."""
    return CrystallizerConfiguration().with_defaults()


def _mutation_research() -> MutationResearchConfiguration:
    """Return a MutationResearch configuration seeded with its defaults."""
    return MutationResearchConfiguration().with_defaults()


def _nexus() -> NexusConfiguration:
    """Return a Nexus configuration seeded with its defaults."""
    return NexusConfiguration().with_defaults()


def _change_aether(configuration: AetherConfiguration) -> None:
    """Flip the spell-id regime on a mutable Aether configuration."""
    configuration.set_process_wide_unique_spell_ids(False)


def _change_crystallizer(configuration: CrystallizerConfiguration) -> None:
    """Change the checkpoint retention bound on a mutable Crystallizer configuration."""
    configuration.with_max_persistence_crystals(3)


def _change_mutation_research(configuration: MutationResearchConfiguration) -> None:
    """Switch lane-type enforcement on for a mutable MutationResearch configuration."""
    configuration.with_lane_type_enforcement(True)


def _change_nexus(configuration: NexusConfiguration) -> None:
    """Restrict Rift targets to one named frame on a mutable Nexus configuration."""
    configuration.with_allowed_target_frame_names(("melderops",))


def _public_values(configuration: RootConfiguration) -> dict[str, object]:
    """Read every reported property back through the configuration's public readers.

    Aether exposes typed properties; the other three expose `get_property` over their
    property bag. The snapshot must agree with whatever the public reader returns.
    """
    if isinstance(configuration, AetherConfiguration):
        return {
            "channel_logger_activation_enabled": configuration.channel_logger_activation_enabled,
            "channel_logger_resolver": configuration.channel_logger_resolver,
            "default_logger": configuration.default_logger,
            "process_wide_unique_spell_ids": configuration.process_wide_unique_spell_ids,
        }
    keys = configuration.get_configuration_dictionary().keys()
    assert all(configuration.has_property(key) for key in keys)
    return {key: configuration.get_property(key) for key in keys}


FAMILIES = [
    pytest.param(_aether, _change_aether, id="aether"),
    pytest.param(_crystallizer, _change_crystallizer, id="crystallizer"),
    pytest.param(_mutation_research, _change_mutation_research, id="mutation_research"),
    pytest.param(_nexus, _change_nexus, id="nexus"),
]


@pytest.mark.parametrize(("build", "change"), FAMILIES)
def test_snapshot_matches_the_public_readers(
        build: Callable[[], RootConfiguration], change: Callable[[RootConfiguration], None],
) -> None:
    """The snapshot reports the same value the public reader returns, key for key."""
    configuration = build()
    snapshot = configuration.get_configuration_dictionary()
    assert snapshot, "a configuration seeded with defaults must report its defaults"
    assert snapshot == _public_values(configuration)
    change(configuration)
    assert configuration.get_configuration_dictionary() == _public_values(configuration)


@pytest.mark.parametrize(("build", "change"), FAMILIES)
def test_snapshot_is_independent_of_the_configuration(
        build: Callable[[], RootConfiguration], change: Callable[[RootConfiguration], None],
) -> None:
    """Editing the returned dict never edits the configuration it came from."""
    configuration = build()
    snapshot = configuration.get_configuration_dictionary()
    first_key = next(iter(snapshot))
    snapshot[first_key] = object()
    snapshot["not_a_property"] = 1
    fresh = configuration.get_configuration_dictionary()
    assert fresh != snapshot
    assert "not_a_property" not in fresh


@pytest.mark.parametrize(("build", "change"), FAMILIES)
def test_equal_construction_compares_equal_and_one_setter_differs(
        build: Callable[[], RootConfiguration], change: Callable[[RootConfiguration], None],
) -> None:
    """Two policies built the same way compare equal; one changed setting separates them."""
    left, right = build(), build()
    assert left.get_configuration_dictionary() == right.get_configuration_dictionary()
    change(right)
    assert left.get_configuration_dictionary() != right.get_configuration_dictionary()


@pytest.mark.parametrize(("build", "change"), FAMILIES)
def test_reading_never_freezes_and_works_frozen_and_activated(
        build: Callable[[], RootConfiguration], change: Callable[[RootConfiguration], None],
) -> None:
    """A snapshot is observation only and is available in every state before cleanup."""
    configuration = build()
    configuration.get_configuration_dictionary()
    assert configuration.frozen is False
    assert configuration.activated is False
    change(configuration)
    mutable_view = configuration.get_configuration_dictionary()
    configuration.activate()
    assert configuration.frozen is True
    assert configuration.activated is True
    assert configuration.get_configuration_dictionary() == mutable_view


@pytest.mark.parametrize(("build", "change"), FAMILIES)
def test_cleaned_configuration_refuses(
        build: Callable[[], RootConfiguration], change: Callable[[RootConfiguration], None],
) -> None:
    """After cleanup the snapshot raises instead of reading a torn-down bag."""
    configuration = build()
    configuration.cleanup()
    with pytest.raises(RuntimeError):
        configuration.get_configuration_dictionary()


def test_aether_snapshot_holds_logger_values_by_reference() -> None:
    """Callables and loggers come back as the same objects, never copies."""

    def resolver(*args: object, **kwargs: object) -> None:
        """Stand-in channel resolver; never called."""
        return None

    default_logger = logging.getLogger("melder.tests.value_snapshot")
    configuration = _aether()
    configuration.set_channel_logger_resolver(resolver)
    configuration.set_default_logger(default_logger)
    snapshot = configuration.get_configuration_dictionary()
    assert snapshot["channel_logger_resolver"] is resolver
    assert snapshot["default_logger"] is default_logger
    assert set(snapshot) == {
        "channel_logger_activation_enabled",
        "channel_logger_resolver",
        "default_logger",
        "process_wide_unique_spell_ids",
    }


def test_crystallizer_snapshot_omits_properties_never_set() -> None:
    """A property that was never set is absent rather than reported with a default."""
    configuration = CrystallizerConfiguration()
    assert configuration.get_configuration_dictionary() == {}
    configuration.with_max_persistence_crystals(5)
    assert configuration.get_configuration_dictionary() == {"max_persistence_crystals": 5}
