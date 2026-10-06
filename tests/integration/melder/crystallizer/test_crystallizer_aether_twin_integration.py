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


def _activated_crystallizer() -> Crystallizer:
    """Activate the Aether-hosted crystallizer with default knobs."""
    configuration = CrystallizerConfiguration().with_defaults()
    configuration.activate()
    crystallizer = Crystallizer()
    crystallizer.activate(configuration)
    return crystallizer


def _recorded_aether_payload(crystallizer: Crystallizer) -> dict:
    """Seal one checkpoint and return the Aether twin configuration payload it captured."""
    checkpoint_id = crystallizer.create_checkpoint()
    replay = crystallizer.checkpoint_replay_data(checkpoint_id)
    return dict(replay["payloads"]["aether"]["root"]["configuration_payload"])


def test_aether_root_twin_records_the_spell_id_regime() -> None:
    """
    Purpose:
        A world run under per-frame spell ids must say so in its record, or a restore rebuilds it process-wide.
    Contract:
        Activating a per-frame root configuration while recording puts process_wide_unique_spell_ids False in the
        Aether twin; activating it on Aether (which re-applies the logger policy through the utility system, and the
        utility system re-emits the twin from live truth) keeps it False.
    Returns:
        None.
    """
    crystallizer = _activated_crystallizer()
    aether_configuration = AetherConfiguration().with_defaults().with_process_wide_unique_spell_ids(False)
    aether_configuration.activate()
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is False
    Aether().activate(aether_configuration)
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is False


def test_utility_system_reemission_records_the_regime_in_force() -> None:
    """
    Purpose:
        The utility system's logger verbs re-emit the Aether twin from live truth, and that twin replaces the
        configuration's own, so it must carry the regime too or it would erase it.
    Contract:
        On an Aether that was never configured, a logger verb re-emits a twin carrying the default regime in force
        (True).
    Returns:
        None.
    """
    crystallizer = _activated_crystallizer()
    AetherUtilitySystem().set_channel_logger_activation_enabled(False)
    assert _recorded_aether_payload(crystallizer)["process_wide_unique_spell_ids"] is True
