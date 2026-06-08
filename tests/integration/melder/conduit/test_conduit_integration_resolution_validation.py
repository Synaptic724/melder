from __future__ import annotations

from typing import Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.aetheric_frame.dev_ops.spell_system_states.conduit_resolution_state import (
    ConduitResolutionState,
)
from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Layer2A
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
@pytest.fixture(autouse=True)
def reset_aether_singleton_for_integration_resolution_validation() -> None:
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
        Build a dynamic configuration for resolution validation tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        SpellbookConfiguration: Configured dynamic configuration.
    """
    configuration = SpellbookConfiguration()
    apply_dynamic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return configuration


def _bind_graph(
    spellbook: Spellbook,
    classes: Iterable[type],
    *,
    existence: Existence,
) -> dict[type, str]:
    """
    Purpose:
        Bind a dependency graph into the spellbook for validation tests.
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


def _diagnostic_codes(state: ConduitResolutionState | None) -> set[str]:
    """
    Purpose:
        Extract diagnostic codes from a conduit resolution state.
    Contract:
        - Returns an empty set when state is None.
        - Returns unique diagnostic codes when state is present.
    Args:
        state: Conduit resolution state to inspect.
    Returns:
        set[str]: Unique diagnostic codes.
    """
    if state is None:
        return set()
    return {diag.code for diag in state.list_diagnostics()}


def test_conduit_validate_resolution_reports_missing_contract_dependencies() -> None:
    """
    Purpose:
        Validate resolution catches missing contracted dependencies.
    Contract:
        - Contracting only a root spell without dependencies emits visibility gap errors.
        - ConduitResolutionState records error diagnostics for the conduit.
    Returns:
        None.
    Raises:
        AssertionError: If validation does not surface missing dependencies.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    borrower_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=False,
            )

        state = borrower.validate_resolution()
        assert state is not None
        assert state.has_errors() is True
        assert "visibility_gap_dependency_filtered" in _diagnostic_codes(state)
        assert state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.invalid
    finally:
        borrower.permanent_cleanup()
        owner.permanent_cleanup()


def test_conduit_validate_resolution_recovers_after_contract_changes() -> None:
    """
    Purpose:
        Validate resolution recovers when missing dependencies are restored.
    Contract:
        - Initial validation passes with full dependencies.
        - Removing a dependency causes visibility gap errors.
        - Re-adding the dependency restores valid resolution state.
    Returns:
        None.
    Raises:
        AssertionError: If resolution state does not recover after fixes.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    borrower_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

        state = borrower.validate_resolution()
        assert state is not None
        assert state.has_errors() is False
        assert state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.remove_spell_from_contract(
                spell_id=depth3_ids[Depth3Layer2A],
                conduit=owner,
            )

        broken_state = borrower.validate_resolution()
        assert broken_state is not None
        assert broken_state.has_errors() is True
        assert "visibility_gap_dependency_filtered" in _diagnostic_codes(broken_state)
        assert broken_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.invalid

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Layer2A],
                conduit=owner,
                permissions="create",
            )

        recovered_state = borrower.validate_resolution()
        assert recovered_state is not None
        assert recovered_state.has_errors() is False
        assert recovered_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
    finally:
        borrower.permanent_cleanup()
        owner.permanent_cleanup()


def test_conduit_validate_resolution_for_lesser_uses_root_and_survives_cleanup() -> None:
    """
    Purpose:
        Validate lesser conduits reuse root resolution state and cleanup is isolated.
    Contract:
        - validate_resolution on a lesser conduit uses the root conduit id.
        - lesser cleanup does not invalidate the root's resolution state.
    Returns:
        None.
    Raises:
        AssertionError: If resolution state diverges or is lost after cleanup.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    borrower_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

        root_state = borrower.validate_resolution()
        assert root_state is not None
        assert root_state.has_errors() is False
        assert root_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid

        lesser = borrower.create_lesser_conduit()
        try:
            lesser_state = lesser.validate_resolution(refresh_structural=False)
            assert lesser_state is borrower.get_resolution_state()
            assert lesser_state is root_state
            assert lesser_state.has_errors() is False
            assert lesser_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
        finally:
            lesser.permanent_cleanup()

        refreshed_state = borrower.validate_resolution(refresh_structural=False)
        assert refreshed_state is root_state
        assert refreshed_state.has_errors() is False
        assert refreshed_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
    finally:
        borrower.permanent_cleanup()
        owner.permanent_cleanup()


def test_conduit_validate_resolution_matches_get_resolution_state() -> None:
    """
    Purpose:
        Validate get_resolution_state returns the state produced by validation.
    Contract:
        - validate_resolution returns a conduit-scoped resolution state.
        - get_resolution_state returns the same state instance.
    Returns:
        None.
    Raises:
        AssertionError: If validation state is not reused by get_resolution_state.
    """
    configuration = _make_dynamic_configuration()
    owner_book = Spellbook(configuration=configuration)
    borrower_book = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        owner_book,
        get_depth_3_classes(),
        existence=Existence.unique,
    )
    borrower_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    owner = owner_book.conjure(dynamic=True, name="owner")
    borrower = borrower_book.conjure(dynamic=True, name="borrower")
    try:
        assert owner.link(borrower) is True
        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=depth3_ids[Depth3Root],
                conduit=owner,
                permissions="create",
                link_dependencies=True,
            )

        state = borrower.validate_resolution()
        assert state is not None
        assert borrower.get_resolution_state() is state
    finally:
        borrower.permanent_cleanup()
        owner.permanent_cleanup()


def test_conduit_resolution_state_cleaned_on_conduit_cleanup() -> None:
    """
    Purpose:
        Validate conduit cleanup deterministically cleans its resolution state.
    Contract:
        - Resolution state is cleaned when the owning conduit is cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If resolution state is not cleaned on cleanup.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(dynamic=True, name="root")
    state = conduit.validate_resolution()
    conduit.permanent_cleanup()

    assert state is not None
    assert state.cleaned is True


def test_conduit_validate_resolution_raises_when_lesser_cleaned() -> None:
    """
    Purpose:
        Validate cleaned lesser conduits reject resolution validation requests.
    Contract:
        - validate_resolution raises RuntimeError after lesser cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned lesser conduits accept validation.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    root = spellbook.conjure(dynamic=True, name="root")
    lesser = root.create_lesser_conduit()
    try:
        lesser.permanent_cleanup()

        with pytest.raises(RuntimeError):
            lesser.validate_resolution()
    finally:
        root.permanent_cleanup()


def test_conduit_upgrade_to_normal_preserves_id_and_resolution_state() -> None:
    """
    Purpose:
        Validate upgraded conduits retain id and seed resolution state.
    Contract:
        - Upgrading a lesser conduit preserves its id.
        - Upgraded conduit has a distinct resolution state seeded from root.
    Returns:
        None.
    Raises:
        AssertionError: If id or resolution state invariants fail.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique,
    )

    root = spellbook.conjure(dynamic=True, name="root")
    lesser = root.create_lesser_conduit()
    try:
        original_id = lesser.id
        root_state = root.validate_resolution()
        assert root_state is not None

        lesser.upgrade_to_normal(name="upgraded")
        upgraded_state = lesser.get_resolution_state()

        assert lesser.id == original_id
        assert upgraded_state is not None
        assert upgraded_state is not root_state
        assert upgraded_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
        assert root_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
        assert lesser.validate_resolution(refresh_structural=False) is upgraded_state
    finally:
        root.permanent_cleanup()
