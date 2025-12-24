from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.validation.validation_system import SpellValidationSystem
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_validation_system() -> None:
    """
    Purpose:
        Ensure integration validation system tests start with a clean Aether singleton.
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
        Build a dynamic Configuration for integration validation tests.
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


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> object | None:
    """
    Purpose:
        Resolve a local Spell instance by its versioned spell id.
    Contract:
        - Returns the first local spell whose SpellIndex.current matches `spell_id`.
        - Returns None if no matching spell is found.
    Args:
        spellbook: Spellbook holding locally bound spells.
        spell_id: Versioned spell id to locate.
    Returns:
        Spell | None: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def test_validation_system_resolves_contracted_dependency_without_dangling() -> None:
    """
    Purpose:
        Validate contracted dependencies resolve without dangling errors.
    Contract:
        - A dependency spell_id that is contracted is not flagged as dangling.
    Returns:
        None.
    Raises:
        AssertionError: If dangling dependency issues are produced.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class Consumer:
        """
        Purpose:
            Provide a consumer spell for dependency validation.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the consumer spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    owner = None
    borrower = None
    try:
        service_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=service_id,
            conduit=owner,
            permissions="create",
        )

        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        consumer_spell.dependencies = [service_id]
        consumer_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=consumer_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert result.issues == []
            assert result.has_errors is False
            assert result.has_warnings is False
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_validation_system_duplicate_spell_name_across_contracted() -> None:
    """
    Purpose:
        Validate duplicate spell names are detected across local and contracted spells.
    Contract:
        - Duplicate spell_name across local and contracted spells yields an error.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate spell names are not reported.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    system = SpellValidationSystem()

    class ContainerA:
        """
        Purpose:
            Provide a namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
            Contract:
                No runtime behavior beyond construction.
            """

            def __init__(self) -> None:
                """
                Purpose:
                    Initialize the Service spell.
                Contract:
                    No side effects beyond construction.
                Returns:
                    None.
                """
                return None

    class ContainerB:
        """
        Purpose:
            Provide a second namespace for a Service spell.
        Contract:
            Defines a nested Service class for duplicate name testing.
        """

        class Service:
            """
            Purpose:
                Provide a Service spell with a shared name.
            Contract:
                No runtime behavior beyond construction.
            """

            def __init__(self) -> None:
                """
                Purpose:
                    Initialize the Service spell.
                Contract:
                    No side effects beyond construction.
                Returns:
                    None.
                """
                return None

    owner = None
    borrower = None
    try:
        owner_id = owner_book.bind(
            spell=ContainerB.Service,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_id = borrower_book.bind(
            spell=ContainerA.Service,
            existence=Existence.unique,
            permissions="create",
        )
        owner = owner_book.conjure(automatic=False, name="owner")
        borrower = borrower_book.conjure(automatic=False, name="borrower")
        assert owner.link(borrower) is True
        assert borrower.add_spell_to_contract(
            spell_id=owner_id,
            conduit=owner,
            permissions="create",
        )

        local_spell = _get_spell_by_version_id(borrower_book, borrower_id)
        assert local_spell is not None
        local_spell.dependency_graph = object()

        result = system.validate_spell(
            spell=local_spell,
            requirements=None,
            symbolic_graph=None,
            resolution_frame=object(),
        )
        try:
            assert len(result.issues) == 1
            issue = result.issues[0]
            assert issue.code == "DUPLICATE_SPELL_NAME"
            assert issue.severity == "error"
            assert issue.details["collision_count"] == 2
        finally:
            result.cleanup()
    finally:
        system.cleanup()
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()


def test_spell_validation_phase4_marks_leaf_as_validated() -> None:
    """
    Purpose:
        Validate Phase 4 marks a leaf spell as validated and not broken.
    Contract:
        - run_phase_validation sets validated True and is_broken False.
        - Validation produces no issues for a leaf spell.
    Returns:
        None.
    Raises:
        AssertionError: If validation flags or issues are unexpected.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class Leaf:
        """
        Purpose:
            Provide a minimal leaf spell for validation testing.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the leaf spell.
            Contract:
                No side effects beyond construction.
            Returns:
                None.
            """
            return None

    try:
        spell_id = spellbook.bind(
            spell=Leaf,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        assert result.issues == []
        assert spell.validated is True
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()


def test_spell_validation_phase4_warns_on_required_hole_not_broken() -> None:
    """
    Purpose:
        Validate required hole warnings do not mark a spell as broken.
    Contract:
        - REQUIRED_HOLE warnings are present.
        - The spell is validated and not broken.
    Returns:
        None.
    Raises:
        AssertionError: If warnings are missing or the spell is marked broken.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)

    class NeedsInput:
        """
        Purpose:
            Provide a spell with a required plain parameter.
        Contract:
            - Declares an unannotated required parameter.
        Args:
            value: Required plain parameter with no default.
        """

        def __init__(self, value: int) -> None:
            """
            Purpose:
                Capture the required value input.
            Contract:
                Stores the provided value for completeness.
            Args:
                value: Required input for the spell.
            Returns:
                None.
            """
            self.value = value

    try:
        spell_id = spellbook.bind(
            spell=NeedsInput,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.run_phase_requirements()
        spell.run_phase_symbolic_graph()
        spell.run_phase_local_frame()
        spell.run_phase_validation()

        result = spell.validation_result_phase4
        assert result is not None
        codes = {issue.code for issue in result.issues}
        assert "REQUIRED_HOLE" in codes
        assert result.has_errors is False
        assert result.has_warnings is True
        assert spell.validated is True
        assert spell.is_broken is False
    finally:
        spellbook.cleanup()
