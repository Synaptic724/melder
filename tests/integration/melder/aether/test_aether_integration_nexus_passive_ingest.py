import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_singletons_for_integration() -> None:
    """
    Purpose:
        Ensure Nexus passive-ingest integration tests start from clean
        singleton state.
    Contract:
        - Resets Aether, Nexus, and utility singletons before and after test.
        - Rebinds Spellbook and Conduit singleton handles to the fresh Aether.
    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_rift_publishable_configuration(
        *,
        aether_frame: str,
) -> Configuration:
    """
    Purpose:
        Build one Spellbook configuration that will publish into passive Nexus
        state after conjure.
    Contract:
        - Uses automatic defaults for the frame.
        - Enables Rift-facing posture without requiring dynamic mode.
        - Keeps scheduler workers low for integration tests.
    Args:
        aether_frame:
            Target frame name.
    Returns:
        Configuration: Configured Spellbook configuration.
    """
    configuration = Configuration(aether_frame=aether_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def test_integration_spellbook_conjure_populates_passive_nexus_records() -> None:
    """
    Purpose:
        Verify successful Spellbook conjure still populates passive Nexus frame,
        conduit, and spell records through the manager-owned boundary.
    Contract:
        - Passive publication does not require `Nexus.enable()`.
        - Conjure binds frame posture, creates the root conduit, and publishes
          frame/conduit/spell records.
    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aether_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = Nexus()
        assert nexus.is_enabled is False

        descriptor = nexus._get_required_frame_descriptor("ops")
        assert descriptor.frame_configuration is not None
        assert descriptor.frame_configuration.rift_enabled is True
        assert descriptor.frame_overview is not None
        assert descriptor.frame_overview.frame_name == "ops"
        assert descriptor.conduit_records_by_id[conduit.id].conduit_name == "root"
        assert ("{0}".format(spellbook.id), spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.cleanup()
