from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.creations.creations import Creations
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_creations() -> None:
    """
    Purpose:
        Ensure integration creations tests start with a clean Aether singleton.
    Contract:
        - Resets the Aether singleton before the test runs.
        - Rebinds Spellbook._aether and Conduit._aether to the new instance.
        - Resets the singleton again after the test for isolation.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_configuration(workers: int = 1) -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for integration creations tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


class _UniqueService:
    """
    Purpose:
        Provide a service type for unique-per-conduit creation tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for unique instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _SpellspaceService:
    """
    Purpose:
        Provide a service type for spellspace creation tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for spellspace instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()


class _ManyService:
    """
    Purpose:
        Provide a service type for many-scope creation tests.
    Contract:
        - Instances are distinguishable by identity.
    """

    def __init__(self) -> None:
        """
        Purpose:
            Initialize an identity marker for many instances.
        Contract:
            - marker is unique per instance.
        Returns:
            None.
        """
        self.marker = object()

    def cleanup(self) -> None:
        """
        Purpose:
            Provide a disposal hook for many-scope registration tests.
        Contract:
            - Does not raise.
        Returns:
            None.
        """
        return


def test_conduit_integration_creations_extract_restore_reuses_instances() -> None:
    """
    Purpose:
        Validate extract/restore reuses instances across Conduit + SpellSpace.
    Contract:
        - Unique-per-conduit instances are reused after restore.
        - Spellspace instances are reused after restore within the same space.
    Returns:
        None.
    Raises:
        AssertionError: If restore does not preserve instance reuse.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    unique_id = spellbook.bind(
        spell=_UniqueService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    spellspace_id = spellbook.bind(
        spell=_SpellspaceService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    try:
        creations = conduit._creations
        unique_instance = conduit.meld(spell=unique_id)

        unique_snapshot = creations.extract_spell_creations(unique_id)
        creations.restore_spell_creations(unique_id, unique_snapshot)

        reused_unique = conduit.meld(spell=unique_id)
        assert reused_unique is unique_instance

        with conduit.enter_spellspace() as space:
            spellspace_instance = space.meld(spell=spellspace_id)
            spellspace_snapshot = creations.extract_spell_creations(spellspace_id)
            creations.restore_spell_creations(spellspace_id, spellspace_snapshot)
            reused_spellspace = space.meld(spell=spellspace_id)
            assert reused_spellspace is spellspace_instance
    finally:
        conduit.cleanup()


def test_conduit_integration_upgrade_transfers_lesser_creations() -> None:
    """
    Purpose:
        Validate lesser upgrade transfers creations into normal scope.
    Contract:
        - Unique-per-conduit instance is reused after upgrade.
        - Many instances remain tracked after upgrade.
    Returns:
        None.
    Raises:
        AssertionError: If upgrade drops or fails to preserve creations.
    """
    configuration = SpellbookConfiguration()
    configuration.set_property("system_state", "dynamic")
    configuration.set_property("disposal", True)
    configuration.set_property("disposal_method_names", ["cleanup"])
    configuration.load_default_dictionary()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook = Spellbook(configuration=configuration)
    unique_id = spellbook.bind(
        spell=_UniqueService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )
    many_id = spellbook.bind(
        spell=_ManyService,
        existence=Existence.many,
        permissions="create",
    )
    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        unique_instance = lesser.meld(spell=unique_id)
        many_instance = lesser.meld(spell=many_id)

        lesser.upgrade_to_normal(name="upgraded")

        assert isinstance(lesser._creations, Creations)
        reused_unique = lesser.meld(spell=unique_id)
        assert reused_unique is unique_instance

        many_after = lesser.meld(spell=many_id)
        assert many_after is not many_instance
        bucket = lesser._creations._creations.get(many_id)
        assert bucket is not None
        values = [creation.value for creation in bucket]
        assert many_instance in values
        assert many_after in values
    finally:
        lesser.cleanup()
        root.cleanup()
