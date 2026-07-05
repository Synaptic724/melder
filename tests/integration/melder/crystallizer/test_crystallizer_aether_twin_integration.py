"""
Integration test for the OPTIONAL Aether root twin: emitted from
AetherConfiguration.activate (config-owned emission) whenever the user
configures the root while the crystallizer records - ABOVE the frame posture
gate by design (root config is retained regardless of posture).

Runs only on 3.14t (melder package root import chain).
"""
import pytest

from melder.aether.aether import Aether
from melder.aether.aether_configuration import AetherConfiguration
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spellbook import Spellbook
from melder.crystallizer.configuration.crystallizer_configuration import (
    CrystallizerConfiguration,
)
from melder.crystallizer.crystallizer import Crystallizer
from melder.nexus.nexus import Nexus


@pytest.fixture(autouse=True)
def reset_world_singletons():
    """
    Purpose:
        Isolate each test behind fresh world singletons.
    Contract:
        - Resets Aether/AetherUtilitySystem/Nexus/Crystallizer and rebinds
          the static Aether references before and after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Crystallizer._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def test_aether_root_configuration_emits_the_optional_root_twin():
    """
    Purpose:
        Verify the root twin's config-owned emission on the real runtime.
    Contract:
        With the crystallizer activated, AetherConfiguration.activate()
        emits the AetherCrystal (setup canon: Aether config is optional;
        when used, its confirmation records above the posture gate), and
        Aether.activate() then applies it to the host unchanged.
    Returns:
        None.
    Raises:
        AssertionError: If the root confirmation fails to record.
    """
    crystallizer_configuration = CrystallizerConfiguration().with_defaults()
    crystallizer_configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(crystallizer_configuration)
    assert crystallizer.describe_profile()["has_aether_crystal"] is False
    aether_configuration = AetherConfiguration().with_defaults()
    aether_configuration.activate()
    assert crystallizer.describe_profile()["has_aether_crystal"] is True
    Aether().activate(aether_configuration)
    assert crystallizer.describe_profile()["has_aether_crystal"] is True


def test_unconfigured_aether_records_no_root_twin():
    """
    Purpose:
        Verify the OPTIONAL nature of the root twin.
    Contract:
        A recording world whose user never configures Aether has no
        aether twin - absence is the honest record of an unconfigured
        root.
    Returns:
        None.
    Raises:
        AssertionError: If a root twin appears uninvited.
    """
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    assert crystallizer.describe_profile()["has_aether_crystal"] is False
