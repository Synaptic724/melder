from __future__ import annotations

from typing import Any

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService

from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
CONDUIT_ID = "cid"

@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_change_control() -> None:
    """
    Purpose:
        Ensure component change-control tests start with a clean Aether singleton.
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
        Build a dynamic SpellbookConfiguration for component change-control tests.
    Contract:
        - dynamic_defaults are applied.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        SpellbookConfiguration: Configured dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str) -> Any:
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
        Any: The resolved spell or None if missing.
    """
    for spell_index, spell in spellbook.spells.items():
        if spell_index.current == spell_id:
            return spell
    return None


def _run_spell_to_phase5(spell: Any) -> None:
    """
    Purpose:
        Advance a spell through Phase 5 artifacts for component assertions.
    Contract:
        - Runs Phases 1-5 in order.
        - Phase 5 requires Phase 4 to succeed.
    Args:
        spell: Spell instance to advance.
    Returns:
        None.
    """
    compiler_system = SpellCompilerSystem()
    try:
        compiler_system.run_phase_requirements(spell)
        compiler_system.run_phase_symbolic_graph(spell)
        compiler_system.run_phase_local_frame(spell._spellbook, spell)
        compiler_system.run_phase_validation(spell._spellbook, spell)
        compiler_system.run_phase_root_blueprints(spell._spellbook, spell, CONDUIT_ID)
    finally:
        compiler_system.cleanup()


def test_component_change_control_wires_component_of_for_local_root() -> None:
    """
    Purpose:
        Validate Phase 7 change-control wiring for local roots.
    Contract:
        - component_of includes root and dependency spell ids.
        - Revalidator registration is enabled.
    Returns:
        None.
    Raises:
        AssertionError: If component-of index or revalidator wiring is missing.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)
        compiler_system = SpellCompilerSystem()
        try:
            compiler_system.run_phase_change_control(
                spellbook,
                consumer_spell,
                CONDUIT_ID,
            )
        finally:
            compiler_system.cleanup()

        manager = Spellbook._aether._get_change_control_manager(
            spellbook._aetheric_frame
        )
        assert manager is not None
        info = manager.describe()
        component_of = info["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[consumer_id] == {consumer_id}
        assert component_of[service_id] == {consumer_id}
        assert CONDUIT_ID in info["revalidator_registered_by_conduit"]
    finally:
        spellbook.cleanup()


def test_component_change_control_revalidator_clears_dirty_roots() -> None:
    """
    Purpose:
        Validate change-control revalidator clears dirty roots.
    Contract:
        - notify_spell_changed marks the root as dirty.
        - revalidate_dirty_roots clears dirty roots and monitoring.
    Returns:
        None.
    Raises:
        AssertionError: If dirty roots are not cleared by revalidation.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        manager = Spellbook._aether._get_change_control_manager(
            spellbook._aetheric_frame
        )
        assert manager is not None
        info = manager.describe()
        assert CONDUIT_ID in info["revalidator_registered_by_conduit"]

        manager.notify_spell_changed(service_id)
        assert manager.is_root_dirty(CONDUIT_ID, consumer_id) is True

        manager.revalidate_dirty_roots(CONDUIT_ID)
        after = manager.describe()
        assert after["dirty_roots_by_conduit"][CONDUIT_ID] == set()
        assert after["monitor_active_by_conduit"][CONDUIT_ID] is False
    finally:
        spellbook.cleanup()


def test_component_change_control_tracks_contracted_dependency_in_component_of() -> None:
    """
    Purpose:
        Validate component-of index includes contracted dependencies.
    Contract:
        - Contracted dependency spell ids map back to the root spell id.
        - Revalidator registration is enabled after Phase 5.
    Returns:
        None.
    Raises:
        AssertionError: If contracted spell ids are missing from component-of.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    owner = None
    borrower = None
    try:
        service_id = owner_book.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )
        owner = owner_book.conjure(dynamic=True, name="owner")
        borrower = borrower_book.conjure(dynamic=True, name="borrower")
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        borrower_book.begin_transaction("bind")
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_book.end_transaction("bind")
        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        manager = Spellbook._aether._get_change_control_manager(
            borrower_book._aetheric_frame
        )
        assert manager is not None
        info = manager.describe()
        component_of = info["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[service_id] == {consumer_id}
        assert component_of[consumer_id] == {consumer_id}
        assert CONDUIT_ID in info["revalidator_registered_by_conduit"]
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()
        borrower_book.cleanup()
        owner_book.cleanup()


def test_component_change_control_excludes_uncontracted_remote_spells() -> None:
    """
    Purpose:
        Validate uncontracted remote spells are excluded from component-of index.
    Contract:
        - Uncontracted remote spell ids do not appear in component_of.
        - Contracted dependencies are still present.
    Returns:
        None.
    Raises:
        AssertionError: If uncontracted remote spells leak into component-of.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)
    remote_book = Spellbook(configuration=configuration)

    class Consumer:
        """
        Purpose:
            Provide a consumer spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    class RemoteOnly:
        """
        Purpose:
            Provide a spell bound only in the remote Spellbook.
        Contract:
            - Declares no constructor parameters.
        """

        def __init__(self) -> None:
            """
            Purpose:
                Initialize the remote-only spell.
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
            spellframe=BasicService.__name__,
        )
        remote_id = remote_book.bind(
            spell=RemoteOnly,
            existence=Existence.unique,
            permissions="create",
        )

        owner = owner_book.conjure(dynamic=True, name="owner")
        borrower = borrower_book.conjure(dynamic=True, name="borrower")
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=service_id,
                conduit=owner,
                permissions="create",
            )
        borrower_book.begin_transaction("bind")
        consumer_id = borrower_book.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        borrower_book.end_transaction("bind")
        consumer_spell = _get_spell_by_version_id(borrower_book, consumer_id)
        assert consumer_spell is not None
        _run_spell_to_phase5(consumer_spell)

        manager = Spellbook._aether._get_change_control_manager(
            borrower_book._aetheric_frame
        )
        assert manager is not None
        info = manager.describe()
        component_of = info["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[service_id] == {consumer_id}
        assert remote_id not in component_of
    finally:
        if borrower is not None:
            borrower.cleanup()
        if owner is not None:
            owner.cleanup()
        remote_book.cleanup()
        borrower_book.cleanup()
        owner_book.cleanup()


def test_component_change_control_shared_dependency_maps_to_multiple_roots() -> None:
    """
    Purpose:
        Validate component-of index maps shared dependencies to multiple roots.
    Contract:
        - Shared dependency spell id maps to both root spell ids.
        - Each root maps to itself in component_of.
    Returns:
        None.
    Raises:
        AssertionError: If shared dependency roots are incomplete.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)

    class ConsumerA:
        """
        Purpose:
            Provide a root spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    class ConsumerB:
        """
        Purpose:
            Provide a second root spell that depends on BasicService.
        Contract:
            - Declares a BasicService dependency for DI.
        Args:
            service: Injected BasicService instance.
        """

        def __init__(self, service: BasicService) -> None:
            """
            Purpose:
                Capture the injected BasicService dependency.
            Contract:
                Stores the dependency for completeness.
            Args:
                service: Injected BasicService dependency.
            Returns:
                None.
            """
            self.service = service

    try:
        service_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=BasicService.__name__,
        )
        consumer_a_id = spellbook.bind(
            spell=ConsumerA,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_b_id = spellbook.bind(
            spell=ConsumerB,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_a = _get_spell_by_version_id(spellbook, consumer_a_id)
        consumer_b = _get_spell_by_version_id(spellbook, consumer_b_id)
        assert consumer_a is not None
        assert consumer_b is not None
        _run_spell_to_phase5(consumer_a)
        _run_spell_to_phase5(consumer_b)

        manager = Spellbook._aether._get_change_control_manager(
            spellbook._aetheric_frame
        )
        assert manager is not None
        info = manager.describe()
        component_of = info["component_of_by_conduit"][CONDUIT_ID]
        assert component_of[service_id] == {consumer_a_id, consumer_b_id}
        assert component_of[consumer_a_id] == {consumer_a_id}
        assert component_of[consumer_b_id] == {consumer_b_id}
    finally:
        spellbook.cleanup()
