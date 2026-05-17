import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    apply_dynamic_defaults_for_spellbook_configuration,
    build_aetheric_frame_configuration_for_spellbook_configuration,
    set_frame_ai_native_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
    set_frame_system_state_for_spellbook_configuration,
    set_shared_framewide_spellbook_configuration_for_spellbook_configuration,
)
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
) -> SpellbookConfiguration:
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
        SpellbookConfiguration: Configured Spellbook configuration.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    set_frame_rift_enabled_for_spellbook_configuration(configuration, True)
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
        assert (
            descriptor.conduit_records_by_id[conduit.id].payload.conduit_name
            == "root"
        )
        assert ("{0}".format(spellbook.id), spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.cleanup()


def test_integration_post_conjure_bind_updates_and_removes_passive_nexus_spell_record() -> None:
    """
    Purpose:
        Verify post-conjure binds publish incremental spell records into passive
        Nexus and cleanup removes them again.
    Contract:
        - Late binds on a Rift-enabled frame publish a new spell record without
          requiring Nexus.enable().
        - Conduit cleanup removes the late-bound spell record from the passive
          descriptor store.
    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aether_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook_id = spellbook.id

    conduit = spellbook.conjure(name="root")
    late_spell_id = None
    try:
        with spellbook.binding_transaction():
            late_spell_id = spellbook.bind(
                spell=BasicService,
                existence=Existence.unique,
                permissions="create",
                binding_name="late",
            )

        nexus = Nexus()
        descriptor = nexus._get_required_frame_descriptor("ops")
        assert (spellbook_id, late_spell_id) in descriptor.spell_records_by_key
    finally:
        conduit.cleanup()

    nexus = Nexus()
    descriptor = nexus._get_required_frame_descriptor("ops")
    assert (spellbook_id, late_spell_id) not in descriptor.spell_records_by_key
