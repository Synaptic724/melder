from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.interfaces import ISpell
from melder.utilities.custom_exceptions.spell_space_scope_error import SpellSpaceScopeError
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


def test_conduit_unique_reuses_across_lineage() -> None:
    """
    Purpose:
        Validate Existence.unique reuses instances across a conduit lineage.
    Contract:
        - Root and lesser conduits resolve the same instance.
        - Instance type matches the bound spell.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not shared across the lineage.
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
    lesser = conduit.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        assert root_instance is lesser_instance
        assert isinstance(root_instance, BasicService)
    finally:
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_unique_per_conduit_isolated_per_conduit() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit isolates instances per conduit.
    Contract:
        - Root and lesser conduits receive different instances.
        - Each conduit reuses its own instance on repeated melds.
    Returns:
        None.
    Raises:
        AssertionError: If instances leak across conduits or are not reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        assert root_instance is not lesser_instance
        assert conduit.meld(spell=spell_id) is root_instance
        assert lesser.meld(spell=spell_id) is lesser_instance
    finally:
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_many_creates_new_each_time() -> None:
    """
    Purpose:
        Validate Existence.many creates a new instance per meld call.
    Contract:
        - Each meld call returns a distinct instance.
    Returns:
        None.
    Raises:
        AssertionError: If instances are reused.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.many,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        first = conduit.meld(spell=spell_id)
        second = conduit.meld(spell=spell_id)
        assert first is not second
    finally:
        conduit.cleanup()


def test_conduit_unique_per_conduit_lineage_reuses_across_lineage() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit_lineage reuses across a lineage.
    Contract:
        - Root and nested lesser conduits resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If lineage sharing fails.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_lineage,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    lesser = conduit.create_lesser_conduit()
    nested = lesser.create_lesser_conduit()
    try:
        root_instance = conduit.meld(spell=spell_id)
        lesser_instance = lesser.meld(spell=spell_id)
        nested_instance = nested.meld(spell=spell_id)
        assert root_instance is lesser_instance is nested_instance
    finally:
        nested.cleanup()
        lesser.cleanup()
        conduit.cleanup()


def test_conduit_unique_per_spell_space_scopes_instances() -> None:
    """
    Purpose:
        Validate Existence.unique_per_spell_space scopes instances to a spellspace.
    Contract:
        - Reuses within the same spellspace.
        - Creates a new instance for a new spellspace.
        - Raises when no spellspace is active.
    Returns:
        None.
    Raises:
        AssertionError: If spellspace scoping is incorrect.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique_per_spell_space,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        with conduit.enter_spellspace() as space:
            first = space.meld(spell=spell_id)
            second = space.meld(spell=spell_id)
            assert first is second
        with conduit.enter_spellspace() as space:
            third = space.meld(spell=spell_id)
            assert third is not first
        with pytest.raises(SpellSpaceScopeError, match="requires an active SpellSpace"):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_conduit_unique_per_conduit_cluster_shares_across_cluster() -> None:
    """
    Purpose:
        Validate Existence.unique_per_conduit_cluster shares across a cluster.
    Contract:
        - Bound spell_id resolves to a local spell after conjure.
        - Resolved spell objects implement the ISpell protocol.
        - Borrower can resolve the spell by ID and inspect the bound target.
        - Borrower receives a contracted spell entry after cluster refresh.
        - Two conduits in the same cluster resolve the same instance.
    Returns:
        None.
    Raises:
        AssertionError: If the instance is not shared across the cluster.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique_per_conduit_cluster,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")

    borrower_book = Spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")

    owner_spell = owner.get_spell_by_id(spell_id)
    assert owner_spell is not None
    assert owner_spell.spell_id == spell_id
    assert isinstance(owner_spell, ISpell)
    assert any(spell_index.has_version(spell_id) for spell_index in owner_book.spells.keys())

    borrower_spell = borrower.get_spell_by_id(spell_id)
    assert borrower_spell is not None
    assert borrower_spell.spell_id == spell_id
    assert isinstance(borrower_spell, ISpell)

    inspected_wrapper_id = borrower.inspect_spell(owner_spell)
    inspected_target_id = borrower.inspect_spell(owner_spell.spell)
    assert inspected_target_id == spell_id

    owner.link(borrower)
    owner.create_cluster("cluster-a")
    owner.join_cluster("cluster-a")
    borrower.join_cluster("cluster-a")
    owner.refresh_cluster_shares()

    spell_in_contracts = borrower.get_spell_in_contracts(spell_id)
    spells_by_conduit = borrower.get_spells_in_contract_by_conduit(owner._id)

    contracted_spells = borrower_book.contracted_spells.get(owner._id)
    assert contracted_spells is not None
    assert any(spell_index.has_version(spell_id) for spell_index in contracted_spells.keys()), (
        f"Expected spell_id in contracted keys. "
        f"inspected_wrapper_id={inspected_wrapper_id}, "
        f"inspected_target_id={inspected_target_id}, "
        f"spell_in_contracts={spell_in_contracts}, "
        f"spells_by_conduit={spells_by_conduit}"
    )
    assert any(spell.spell_id == spell_id for spell in contracted_spells.values()), (
        f"Expected spell_id in contracted values. "
        f"inspected_wrapper_id={inspected_wrapper_id}, "
        f"inspected_target_id={inspected_target_id}, "
        f"spell_in_contracts={spell_in_contracts}, "
        f"spells_by_conduit={spells_by_conduit}"
    )

    try:
        owner_instance = owner.meld(spell=spell_id)
        borrower_instance = borrower.meld(spell=spell_id)
        assert owner_instance is borrower_instance
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_contract_by_spell_id_dynamic_link() -> None:
    """
    Purpose:
        Validate dynamic link contracts using a spell_id.
    Contract:
        - Borrower can contract a spell by spell_id after link.
        - Contracted spell appears in borrower contract lookups.
        - Borrower can meld the contracted spell.
    Returns:
        None.
    Raises:
        AssertionError: If the contract is not established or resolution fails.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.many,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")

    borrower_book = Spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")

    owner.link(borrower)
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell_id=spell_id, conduit=owner, permissions="create")

        spell_in_contracts = borrower.get_spell_in_contracts(spell_id)
        assert spell_in_contracts is not None
        contracted_conduit_id, contracted_spell = spell_in_contracts
        assert contracted_conduit_id == owner._id
        assert isinstance(contracted_spell, ISpell)
        assert contracted_spell.spell_id == spell_id

        contracted_spells = borrower_book.contracted_spells.get(owner._id)
        assert contracted_spells is not None
        assert any(spell_index.has_version(spell_id) for spell_index in contracted_spells.keys())
        assert any(spell.spell_id == spell_id for spell in contracted_spells.values())

        instance = borrower.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_contract_by_spell_object_dynamic_link() -> None:
    """
    Purpose:
        Validate dynamic link contracts using a spell object.
    Contract:
        - Borrower can contract a spell by ISpell after link.
        - Contracted spell appears in borrower contract lookups.
        - Borrower can meld the contracted spell by spell_id.
    Returns:
        None.
    Raises:
        AssertionError: If the contract is not established or resolution fails.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)

    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.many,
        permissions="create",
    )
    owner = owner_book.conjure(automatic=False, name="owner")

    borrower_book = Spellbook()
    borrower = borrower_book.conjure(automatic=False, name="borrower")

    owner_spell = owner.get_spell_by_id(spell_id)
    assert owner_spell is not None
    assert isinstance(owner_spell, ISpell)
    inspected_wrapper_id = borrower.inspect_spell(owner_spell)
    inspected_target_id = borrower.inspect_spell(owner_spell.spell)
    assert inspected_target_id == spell_id

    owner.link(borrower)
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            borrower.add_spell_to_contract(spell=owner_spell, conduit=owner, permissions="create")

        spell_in_contracts = borrower.get_spell_in_contracts(spell_id)
        assert spell_in_contracts is not None
        contracted_conduit_id, contracted_spell = spell_in_contracts
        assert contracted_conduit_id == owner._id
        assert isinstance(contracted_spell, ISpell)
        assert contracted_spell.spell_id == spell_id

        contracted_spells = borrower_book.contracted_spells.get(owner._id)
        assert contracted_spells is not None
        assert any(spell_index.has_version(spell_id) for spell_index in contracted_spells.keys()), (
            f"Expected spell_id in contracted keys. inspected_wrapper_id={inspected_wrapper_id}, "
            f"inspected_target_id={inspected_target_id}, spell_in_contracts={spell_in_contracts}"
        )
        assert any(spell.spell_id == spell_id for spell in contracted_spells.values()), (
            f"Expected spell_id in contracted values. inspected_wrapper_id={inspected_wrapper_id}, "
            f"inspected_target_id={inspected_target_id}, spell_in_contracts={spell_in_contracts}"
        )

        instance = borrower.meld(spell=spell_id)
        assert isinstance(instance, BasicService)
    finally:
        borrower.cleanup()
        owner.cleanup()
