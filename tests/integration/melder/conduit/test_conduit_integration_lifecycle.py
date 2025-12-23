from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
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


def _make_dynamic_configuration(workers: int = 1) -> Configuration:
    """
    Purpose:
        Create a dynamic configuration for lifecycle tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        workers: Scheduler workers per spellbook.
    Returns:
        Configuration: Dynamic configuration instance.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_conduit_cleanup_is_idempotent_and_blocks_meld() -> None:
    """
    Purpose:
        Validate cleanup is idempotent and blocks meld usage.
    Contract:
        - cleanup can be called more than once without error.
        - meld raises after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup is not idempotent or meld is allowed.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    conduit.cleanup()
    conduit.cleanup()

    with pytest.raises(RuntimeError, match="already been cleaned"):
        conduit.meld(spell=spell_id)


def test_conduit_meld_requires_identifier() -> None:
    """
    Purpose:
        Validate meld requires at least one identifier.
    Contract:
        - meld raises ValueError when no identifiers are provided.
    Returns:
        None.
    Raises:
        AssertionError: If meld accepts an empty call.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(ValueError, match="requires at least one"):
            conduit.meld()
    finally:
        conduit.cleanup()


def test_conduit_set_new_policy_inbound_only_blocks_outbound_links() -> None:
    """
    Purpose:
        Validate dynamic policy updates affect link behavior.
    Contract:
        - set_new_policy accepts inbound_only in dynamic mode.
        - outbound link attempts from inbound_only conduits raise.
    Returns:
        None.
    Raises:
        AssertionError: If link attempts succeed under inbound_only.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.set_new_policy("inbound_only")
        with pytest.raises(RuntimeError, match="inbound_only"):
            owner.link(borrower)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_upgrade_to_normal_allows_binding_and_lookup() -> None:
    """
    Purpose:
        Validate dynamic upgrade to normal enables binding and lookup.
    Contract:
        - upgrade_to_normal succeeds for lesser conduits in dynamic mode.
        - upgraded conduit can bind and meld new spells.
        - upgraded conduit is visible by name in Aether.
    Returns:
        None.
    Raises:
        AssertionError: If upgrade does not enable binding or lookup.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        lesser.upgrade_to_normal(name="upgraded")
        config_id = lesser.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
        assert isinstance(lesser.meld(spell=config_id), BasicConfig)
        assert root.get_conduit_by_name("upgraded") is lesser
    finally:
        root.cleanup()


def test_conduit_transfer_spell_ownership_moves_registry_and_meld() -> None:
    """
    Purpose:
        Validate spell ownership transfer updates the registry and meld behavior.
    Contract:
        - transfer_spell_ownership returns a summary with source/target info.
        - Aether ownership for the spell shifts to the target conduit.
        - Target can meld the transferred spell; source cannot.
    Returns:
        None.
    Raises:
        AssertionError: If ownership transfer does not update resolution.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    target_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    try:
        summary = owner.transfer_spell_ownership(
            spell=spell_id,
            target_conduit=target,
        )
        assert summary["spell_id"] == spell_id
        assert summary["source"] == owner.id
        assert summary["target"] == target.id
        assert owner.get_conduit_by_spell_id(spell_id) is target
        assert isinstance(target.meld(spell=spell_id), BasicService)
        with pytest.raises(KeyError, match="No spell found"):
            owner.meld(spell=spell_id)
    finally:
        target.cleanup()
        owner.cleanup()


def test_conduit_find_contracted_spell_returns_contract_entry() -> None:
    """
    Purpose:
        Validate find_contracted_spell locates borrowed spells.
    Contract:
        - Contracted spells are returned when present.
        - Missing spell ids return None.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spells cannot be resolved.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        owner.link(borrower)
        borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        contracted = borrower.find_contracted_spell(spell_id)
        assert contracted is not None
        assert contracted.spell_id == spell_id
        assert borrower.find_contracted_spell("missing-spell") is None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_get_mutation_research_dynamic_returns_manager() -> None:
    """
    Purpose:
        Validate MutationResearch access in dynamic mode.
    Contract:
        - Dynamic normal conduits return a MutationResearch manager.
    Returns:
        None.
    Raises:
        AssertionError: If MutationResearch is not returned.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        manager = conduit.get_mutation_research()
        assert manager is not None
    finally:
        conduit.cleanup()


def test_conduit_get_mutation_research_rejects_automatic() -> None:
    """
    Purpose:
        Validate MutationResearch access is blocked in automatic mode.
    Contract:
        - Automatic conduits raise when requesting MutationResearch.
    Returns:
        None.
    Raises:
        AssertionError: If automatic access is allowed.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with pytest.raises(RuntimeError, match="Dynamic environment is not enabled"):
            conduit.get_mutation_research()
    finally:
        conduit.cleanup()


def test_conduit_register_conduit_cloud_requires_name() -> None:
    """
    Purpose:
        Validate conduit cloud registration requires a name.
    Contract:
        - Dynamic conduits without names raise when registering.
    Returns:
        None.
    Raises:
        AssertionError: If unnamed conduits can register in the cloud.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False)
    try:
        with pytest.raises(RuntimeError, match="name is not set"):
            conduit.register_conduit_cloud(conduit)
    finally:
        conduit.cleanup()
