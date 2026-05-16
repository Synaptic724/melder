from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.helpers.general_helpers import SpellInputUtils
from tests.mocks.spellbook.core_classes import BasicLogger
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration() -> None:
    """
    Purpose:
        Ensure integration tests start with a clean Aether singleton.
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


def _make_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Create a configuration for lookup helper integration tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_inspect_spell_and_check_spell_id() -> None:
    """
    Purpose:
        Validate inspect_spell and check_spell_id in a registered conduit.
    Contract:
        - check_spell_id returns True for bound spells and False otherwise.
        - inspect_spell returns spell_id for bound spell classes.
        - inspect_spell returns None for unknown spell classes.
    Returns:
        None.
    Raises:
        AssertionError: If inspections return unexpected results.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.check_spell_id(spell_id) is True
        assert conduit.check_spell_id("missing") is False
        assert conduit.inspect_spell(BasicService) == spell_id
        assert conduit.inspect_spell(BasicLogger) is None
    finally:
        conduit.cleanup()


def test_conduit_find_spell_id_and_key_return_current_ids() -> None:
    """
    Purpose:
        Validate find_spell_id/find_spell_key return current spell identifiers.
    Contract:
        - find_spell_id returns the current spell_id for the lineage.
        - find_spell_key matches SpellInputUtils.make_spell_key_from_parts.
    Returns:
        None.
    Raises:
        AssertionError: If lookup helpers return inconsistent values.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        spell = conduit.get_spell_by_id(spell_id)
        assert spell is not None

        resolved_id = conduit.find_spell_id(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        )
        assert resolved_id == spell_id

        expected_key = SpellInputUtils.make_spell_key_from_parts(
            spellframe=spell.spellframe,
            spell_name=spell.spell_name,
            binding_name=spell.binding_name,
        )
        assert conduit.find_spell_key(
            spell.spellframe,
            spell.spell_name,
            spell.binding_name,
        ) == expected_key
    finally:
        conduit.cleanup()


def test_conduit_find_spell_id_and_key_raise_for_missing() -> None:
    """
    Purpose:
        Validate lookup helpers raise when spells are missing.
    Contract:
        - find_spell_id raises ValueError for missing spell identifiers.
        - find_spell_key raises RuntimeError for missing spell keys.
    Returns:
        None.
    Raises:
        AssertionError: If missing lookups do not raise.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(ValueError, match="not found"):
            conduit.find_spell_id("missing-frame", "MissingSpell", "missing-bind")
        with pytest.raises(RuntimeError, match="Spell key not found"):
            conduit.find_spell_key("missing-frame", "MissingSpell", "missing-bind")
    finally:
        conduit.cleanup()


def test_conduit_get_spell_permissions_handles_missing_spell() -> None:
    """
    Purpose:
        Validate get_spell_permissions for existing and missing spells.
    Contract:
        - Returns the configured permissions for a bound spell.
        - Raises RuntimeError for missing spell ids.
    Returns:
        None.
    Raises:
        AssertionError: If permissions do not match or missing lookups succeed.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.get_spell_permissions(spell_id) == "create"
        with pytest.raises(RuntimeError, match="not found"):
            conduit.get_spell_permissions("missing")
    finally:
        conduit.cleanup()


def test_conduit_get_conduit_by_id_name_missing_raises() -> None:
    """
    Purpose:
        Validate conduit lookup helpers raise for missing id and name.
    Contract:
        - get_conduit_by_id raises ValueError when id is missing.
        - get_conduit_by_name raises ValueError when name is missing.
    Returns:
        None.
    Raises:
        AssertionError: If missing lookups do not raise.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(ValueError, match="not found"):
            conduit.get_conduit_by_id("missing-id")
        with pytest.raises(ValueError, match="not found"):
            conduit.get_conduit_by_name("missing-name")
    finally:
        conduit.cleanup()


def test_conduit_refresh_cluster_shares_noop_without_membership() -> None:
    """
    Purpose:
        Validate refresh_cluster_shares is a no-op when not in a cluster.
    Contract:
        - No clusters are listed before or after refresh.
    Returns:
        None.
    Raises:
        AssertionError: If refresh mutates cluster membership.
    """
    spellbook = Spellbook(configuration=_make_configuration())
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        assert conduit.list_clusters() == []
        conduit.refresh_cluster_shares()
        assert conduit.list_clusters() == []
    finally:
        conduit.cleanup()
