import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spellbook_scanner import SpellbookScanner
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_spellbook_scanner() -> None:
    """
    Purpose:
        Ensure component Spellbook scanner tests start with a clean Aether singleton.
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


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component scanner tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: A configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_index_by_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local SpellIndex by its versioned spell id.
    Contract:
        - Returns the first local SpellIndex whose spell_id matches the input.
        - Returns None if no match is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        SpellIndex | None: The resolved index or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell.spell_id == spell_id:
            return spell_index
    return None


def test_component_spellbook_scanner_iter_local_spells_yields_bound_spells() -> None:
    """
    Purpose:
        Validate local spell iteration yields bound spells from a real Spellbook.
    Contract:
        - iter_local_spells returns exactly the Spellbook.spells entries.
    Returns:
        None.
    Raises:
        AssertionError: If local spell iteration does not match Spellbook state.
    """
    spellbook = _make_spellbook()
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )

        scanner = SpellbookScanner(spellbook)
        try:
            local = list(scanner.iter_local_spells())
            local_indices = {index for index, _spell in local}
            expected_indices = set(spellbook.spells.keys())
            assert local_indices == expected_indices
        finally:
            scanner.cleanup()
    finally:
        spellbook.cleanup()


def test_component_spellbook_scanner_find_by_frame_and_binding_matches_local() -> None:
    """
    Purpose:
        Validate frame and binding lookups match local Spellbook bindings.
    Contract:
        - find_by_frame_and_binding returns the locally bound spell for the frame.
    Returns:
        None.
    Raises:
        AssertionError: If the local frame binding is not resolved.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
            binding_name="primary",
        )
        expected_index = _get_spell_index_by_id(spellbook, spell_id)
        assert expected_index is not None

        scanner = SpellbookScanner(spellbook)
        try:
            result = scanner.find_by_frame_and_binding(
                spellframe=IService,
                binding_name="primary",
                include_contracted=False,
            )
            assert set(result.keys()) == {expected_index}
        finally:
            scanner.cleanup()
    finally:
        spellbook.cleanup()


def test_component_spellbook_scanner_find_by_spell_name_matches_local() -> None:
    """
    Purpose:
        Validate spell_name lookups resolve local class spells.
    Contract:
        - find_by_spell_name returns the BasicService spell only.
    Returns:
        None.
    Raises:
        AssertionError: If the spell_name lookup returns unexpected results.
    """
    spellbook = _make_spellbook()
    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )

        scanner = SpellbookScanner(spellbook)
        try:
            result = scanner.find_by_spell_name(
                BasicService.__name__,
                include_contracted=False,
            )
            assert len(result) == 1
            resolved_spell = next(iter(result.values()))
            assert resolved_spell.spell is BasicService
        finally:
            scanner.cleanup()
    finally:
        spellbook.cleanup()


def test_component_spellbook_scanner_find_by_target_matches_existing_object() -> None:
    """
    Purpose:
        Validate target lookups resolve existing-object bindings.
    Contract:
        - find_by_target returns the spell bound to the existing object.
    Returns:
        None.
    Raises:
        AssertionError: If the existing object is not matched.
    """
    spellbook = _make_spellbook()
    try:
        existing = BasicConfig(label="existing")
        spellbook.bind(
            spell=existing,
            existence=Existence.unique,
            permissions="create",
        )

        scanner = SpellbookScanner(spellbook)
        try:
            result = scanner.find_by_target(existing, include_contracted=False)
            assert len(result) == 1
            resolved_spell = next(iter(result.values()))
            assert resolved_spell.user_created_object is existing
        finally:
            scanner.cleanup()
    finally:
        spellbook.cleanup()


def test_component_spellbook_scanner_find_by_index_returns_local_spell() -> None:
    """
    Purpose:
        Validate index lookups resolve local spells.
    Contract:
        - find_by_index returns the local Spell for the provided SpellIndex.
    Returns:
        None.
    Raises:
        AssertionError: If the index lookup does not return the local spell.
    """
    spellbook = _make_spellbook()
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell_index = _get_spell_index_by_id(spellbook, spell_id)
        assert spell_index is not None

        scanner = SpellbookScanner(spellbook)
        try:
            resolved = scanner.find_by_index(spell_index, include_contracted=False)
            assert resolved is spellbook.spells[spell_index]
        finally:
            scanner.cleanup()
    finally:
        spellbook.cleanup()
