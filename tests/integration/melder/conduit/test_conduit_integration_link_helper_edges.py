from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


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


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Create a dynamic configuration for link helper edge tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Returns:
        SpellbookConfiguration: Dynamic configuration instance.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def test_conduit_initiated_and_provider_accessors_empty_when_unlinked() -> None:
    """
    Purpose:
        Validate initiated/provider accessors return empty results without links.
    Contract:
        - get_initiated_conduit/get_provider_conduit return None when unlinked.
        - get_initiated_conduits/get_provider_conduits return empty lists.
    Returns:
        None.
    Raises:
        AssertionError: If unlinked accessors are not empty.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.get_initiated_conduit(borrower.id) is None
        assert borrower.get_provider_conduit(owner.id) is None
        assert owner.get_initiated_conduits() == []
        assert borrower.get_provider_conduits() == []
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_initiated_and_provider_accessors_clear_after_sever() -> None:
    """
    Purpose:
        Validate initiated/provider accessors clear after severing a link.
    Contract:
        - Accessors resolve the peer after link.
        - Accessors return None/empty after sever_link.
    Returns:
        None.
    Raises:
        AssertionError: If accessors do not clear after severing.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert owner.get_initiated_conduit(borrower.id) is borrower
        assert borrower.get_provider_conduit(owner.id) is owner

        assert owner.sever_link(borrower) is True
        assert owner.get_initiated_conduit(borrower.id) is None
        assert borrower.get_provider_conduit(owner.id) is None
        assert owner.get_initiated_conduits() == []
        assert borrower.get_provider_conduits() == []
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_conduit_add_spell_to_contract_with_dependencies_requires_link() -> None:
    """
    Purpose:
        Validate contract helper rejects calls without a link.
    Contract:
        - add_spell_to_contract_with_dependencies raises without a contract.
        - No inbound contract entries are created on failure.
    Returns:
        None.
    Raises:
        AssertionError: If missing link does not raise or creates entries.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book = Spellbook(configuration=configuration)

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        with borrower.transaction("link", conduits=[borrower, owner]):
            with pytest.raises(RuntimeError, match="No contract found"):
                borrower.add_spell_to_contract_with_dependencies(
                    spell_id=spell_id,
                    conduit=owner,
                    permissions="create",
                )
        assert borrower.get_spells_in_contract_by_conduit(owner.id) is None
    finally:
        borrower.cleanup()
        owner.cleanup()
