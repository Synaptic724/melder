from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_spellbook_scanner() -> None:
    """
    Purpose:
        Ensure integration Spellbook scanner tests start with a clean Aether singleton.
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


def _make_dynamic_configuration() -> Configuration:
    """
    Purpose:
        Build a dynamic Configuration for integration Spellbook scanner tests.
    Contract:
        - dynamic_defaults are applied.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Configuration: Configured integration configuration.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bind_framed_spell(
    spellbook: Spellbook,
    spell: object,
    spellframe: object,
    binding_name: str,
) -> str:
    """
    Purpose:
        Register a spell under a spellframe and binding name.
    Contract:
        - Returns the finalized spell id from the binder.
    Args:
        spellbook: Spellbook used to register the spell.
        spell: Spell class or object to bind.
        spellframe: Spellframe key for registration.
        binding_name: Binding name for the spell.
    Returns:
        str: The registered spell id.
    """
    binder = spellbook.create_binder()
    binder.bind(spell).under_spellframe(spellframe).named(binding_name).as_unique().with_permissions("create")
    return binder.finalize()


def test_spellbook_scanner_iter_contracted_spells_yields_contracted_spell() -> None:
    """
    Purpose:
        Validate contracted spell iteration yields spells after link and contract.
    Contract:
        - iter_contracted_spells includes the contracted spell id.
    Returns:
        None.
    Raises:
        AssertionError: If the contracted spell is missing.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = _bind_framed_spell(owner_book, BasicService, IService, "primary")

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        scanner = SpellbookScanner(borrower_book)
        try:
            contracted = list(scanner.iter_contracted_spells())
            assert any(index.has_version(spell_id) for index, _spell in contracted)
        finally:
            scanner.cleanup()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_scanner_iter_all_spells_includes_local_and_contracted() -> None:
    """
    Purpose:
        Validate all-spell iteration includes local and contracted spells.
    Contract:
        - iter_all_spells contains all local spells.
        - iter_all_spells includes contracted spell ids.
    Returns:
        None.
    Raises:
        AssertionError: If local or contracted spells are missing.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        scanner = SpellbookScanner(borrower_book)
        try:
            all_spells = list(scanner.iter_all_spells())
            all_indices = {index for index, _spell in all_spells}
            local_indices = set(borrower_book.spells.keys())
            assert local_indices.issubset(all_indices)
            assert any(index.has_version(spell_id) for index, _spell in all_spells)
        finally:
            scanner.cleanup()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_scanner_find_by_frame_and_binding_includes_contracted_when_enabled() -> None:
    """
    Purpose:
        Validate frame and binding lookups include contracted spells when enabled.
    Contract:
        - include_contracted False returns no matches if only contracted spells exist.
        - include_contracted True returns the contracted spell.
    Returns:
        None.
    Raises:
        AssertionError: If contracted frame lookup fails.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = _bind_framed_spell(owner_book, BasicService, IService, "primary")

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        scanner = SpellbookScanner(borrower_book)
        try:
            local_only = scanner.find_by_frame_and_binding(
                spellframe=IService,
                binding_name="primary",
                include_contracted=False,
            )
            assert local_only == {}

            with_contracted = scanner.find_by_frame_and_binding(
                spellframe=IService,
                binding_name="primary",
                include_contracted=True,
            )
            assert any(index.has_version(spell_id) for index in with_contracted.keys())
        finally:
            scanner.cleanup()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_scanner_find_single_by_frame_and_binding_reports_ambiguity() -> None:
    """
    Purpose:
        Validate ambiguous frame and binding lookups report errors.
    Contract:
        - Raises RuntimeError when local and contracted spells share the same binding.
        - Returns None when ambiguity is suppressed.
    Returns:
        None.
    Raises:
        AssertionError: If ambiguity handling does not match expectations.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = _bind_framed_spell(owner_book, BasicService, IService, "primary")
    borrower_book.bind(
        spell=BasicConfig,
        existence=Existence.unique,
        permissions="create",
        spellframe=IService,
        binding_name="primary",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        scanner = SpellbookScanner(borrower_book)
        try:
            with pytest.raises(RuntimeError, match="Ambiguous spell resolution"):
                scanner.find_single_by_frame_and_binding(
                    spellframe=IService,
                    binding_name="primary",
                    include_contracted=True,
                )

            resolved = scanner.find_single_by_frame_and_binding(
                spellframe=IService,
                binding_name="primary",
                include_contracted=True,
                raise_on_ambiguity=False,
            )
            assert resolved is None
        finally:
            scanner.cleanup()
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_spellbook_scanner_find_by_index_resolves_contracted_spell() -> None:
    """
    Purpose:
        Validate index lookup resolves contracted spells.
    Contract:
        - find_by_index returns the contracted spell for a contracted SpellIndex.
    Returns:
        None.
    Raises:
        AssertionError: If the contracted index lookup fails.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    spell_id = owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=spell_id,
            conduit=owner,
            permissions="create",
        )

        contracted_map = borrower_book.contracted_spells.get(owner.id)
        assert contracted_map is not None
        contracted_index = next(iter(contracted_map.keys()))

        scanner = SpellbookScanner(borrower_book)
        try:
            resolved = scanner.find_by_index(contracted_index, include_contracted=True)
            assert resolved is not None
            assert resolved.spell_id == spell_id
        finally:
            scanner.cleanup()
    finally:
        borrower.cleanup()
        owner.cleanup()
