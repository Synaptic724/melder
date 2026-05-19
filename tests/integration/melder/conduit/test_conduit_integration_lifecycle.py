from __future__ import annotations

from typing import Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Layer2A
from tests.mocks.spellbook.deep_layers import Depth3Layer2B
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
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


def _make_dynamic_configuration(workers: int = 1) -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for lifecycle tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def _bind_graph(
    spellbook: Spellbook,
    classes: Iterable[type],
    *,
    existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind a dependency graph into the spellbook for integration tests.
    Contract:
        - Each class is bound with the requested Existence.
        - Returns a mapping of class -> spell_id.
    Args:
        spellbook: Target spellbook for bindings.
        classes: Classes to bind in dependency order.
        existence: Existence mode to apply to each binding.
    Returns:
        dict[type, str]: Mapping of class to spell_id.
    """
    spell_ids: dict[type, str] = {}
    for cls in classes:
        spell_ids[cls] = spellbook.bind(
            spell=cls,
            existence=existence,
            permissions="create",
        )
    return spell_ids


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


def test_conduit_cleanup_unregisters_from_aether_and_cloud() -> None:
    """
    Purpose:
        Ensure cleanup removes a conduit from Aether lookups and conduit cloud.
    Contract:
        - Conduit lookups by id, name, and spell id succeed before cleanup.
        - After cleanup, lookups raise and the conduit cloud no longer resolves the conduit.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not unregister the conduit.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    observer_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    observer = observer_book.conjure(automatic=False, name="observer")
    try:
        owner_id = owner.id
        owner_name = owner.name
        cloud = observer.get_conduit_cloud()

        assert observer.get_conduit_by_id(owner_id) is owner
        assert observer.get_conduit_by_name(owner_name) is owner
        assert observer.get_conduit_by_spell_id(spell_id) is owner
        assert cloud.get_conduit(owner_name) is owner

        owner.cleanup()

        with pytest.raises(ValueError, match="not found"):
            observer.get_conduit_by_id(owner_id)
        with pytest.raises(ValueError, match="not found"):
            observer.get_conduit_by_name(owner_name)
        with pytest.raises(ValueError, match="Spell version"):
            observer.get_conduit_by_spell_id(spell_id)
        with pytest.raises(ValueError, match="not found"):
            cloud.get_conduit(owner_name)
    finally:
        observer.cleanup()
        owner.cleanup()


def test_conduit_cleanup_severs_links_and_clears_contracts() -> None:
    """
    Purpose:
        Ensure cleanup severs links and clears contracted spells for peers.
    Contract:
        - Borrower sees link and contracted spell before owner cleanup.
        - Borrower no longer sees link or contracted spell after owner cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not sever links or clear contracts.
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
    owner_id = owner.id
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            ) is True

        assert borrower.find_contracted_spell(spell_id) is not None
        assert borrower.get_spells_in_contract_by_conduit(owner_id) is not None
        assert any(link.id == owner_id for link in borrower.get_links())

        owner.cleanup()

        assert borrower.find_contracted_spell(spell_id) is None
        assert borrower.get_spells_in_contract_by_conduit(owner_id) is None
        assert all(link.id != owner_id for link in borrower.get_links())
        assert borrower_book.contracted_spells.get(owner_id) is None
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_cleanup_cleans_lesser_conduits() -> None:
    """
    Purpose:
        Validate root cleanup cascades to lesser conduits.
    Contract:
        - Cleaning the root conduit cleans lesser and nested lesser conduits.
        - Cleaned lesser conduits reject meld usage.
    Returns:
        None.
    Raises:
        AssertionError: If cleanup does not cascade to lessers.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    nested = lesser.create_lesser_conduit()
    try:
        root.cleanup()

        assert lesser.cleaned is True
        assert nested.cleaned is True
        with pytest.raises(RuntimeError, match="already been cleaned"):
            lesser.meld(spell=spell_id)
        with pytest.raises(RuntimeError, match="already been cleaned"):
            nested.meld(spell=spell_id)
    finally:
        nested.cleanup()
        lesser.cleanup()
        root.cleanup()


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
        with lesser.binding_transaction():
            config_id = lesser.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
            )
        assert isinstance(lesser.meld(spell=config_id), BasicConfig)
        assert root.get_conduit_by_name("upgraded") is lesser
    finally:
        root.cleanup()


def test_conduit_upgrade_to_normal_rejects_duplicate_root_name() -> None:
    """
    Purpose:
        Validate lesser -> normal upgrade respects the frame root-name invariant.
    Contract:
        - upgrading a lesser conduit to a root name already used in the frame
          raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate root names are accepted during upgrade.
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
        with pytest.raises(ValueError, match="Conduit with name root already exists"):
            lesser.upgrade_to_normal(name="root")
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


def test_conduit_transfer_spell_ownership_with_dependencies() -> None:
    """
    Purpose:
        Validate ownership transfer includes direct dependencies when requested.
    Contract:
        - transfer_spell_ownership returns direct dependency spell ids in summary.
        - Root and direct dependency ownership moves to the target conduit.
    Returns:
        None.
    Raises:
        AssertionError: If dependency transfer does not update ownership.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    target_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(automatic=False, name="owner")
    target = target_book.conjure(automatic=False, name="target")
    try:
        owner.meld(spell=depth3_ids[Depth3Root])

        summary = owner.transfer_spell_ownership(
            spell=depth3_ids[Depth3Root],
            target_conduit=target,
            include_dependencies=True,
        )

        expected_deps = {
            depth3_ids[Depth3Layer2A],
            depth3_ids[Depth3Layer2B],
        }
        assert set(summary["dependencies"]) == expected_deps
        assert owner.get_conduit_by_spell_id(depth3_ids[Depth3Root]) is target
        assert owner.get_conduit_by_spell_id(depth3_ids[Depth3Layer2A]) is target
        assert owner.get_conduit_by_spell_id(depth3_ids[Depth3Layer2B]) is target
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
        with borrower.transaction("link", conduits=[borrower, owner]):
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


def test_conduit_find_contracted_spell_returns_none_after_remove() -> None:
    """
    Purpose:
        Validate find_contracted_spell returns None after removal.
    Contract:
        - Contracted spells resolve before removal.
        - Removed spell ids return None after removal.
    Returns:
        None.
    Raises:
        AssertionError: If removal does not clear contracted lookups.
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
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            ) is True

        assert borrower.find_contracted_spell(spell_id) is not None

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.remove_spell_from_contract(
                spell_id=spell_id,
                conduit=owner,
            ) is True
        assert borrower.find_contracted_spell(spell_id) is None
        assert borrower.get_spell_in_contracts(spell_id) is None
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
        assert manager is conduit._aether.mutation_research
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


def test_root_conduit_defaults_name_before_dynamic_registration() -> None:
    """
    Purpose:
        Validate conduit cloud registration requires a name.
    Contract:
        - Dynamic conduits without names raise when registering.
    Returns:
        None.
    Raises:
        AssertionError: If unnamed root conduits do not receive the default
            name.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = None
    try:
        conduit = spellbook.conjure(automatic=False)
        assert conduit.name == "default"
    finally:
        if conduit is not None:
            conduit.cleanup()
        spellbook.cleanup()
