from __future__ import annotations

from typing import Iterable

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.dev_ops.spell_system_states.conduit_resolution_state import (
    ConduitResolutionState,
)
from melder.aether.dev_ops.spell_system_states.spell_validity import SpellValidity
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_resolution_validation() -> None:
    """
    Purpose:
        Ensure component resolution validation tests start with a clean Aether singleton.
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
        Build a dynamic configuration for component resolution validation tests.
    Contract:
        - system_state is dynamic.
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Configuration: Configured dynamic configuration.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
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
        Bind a dependency graph into the spellbook for component validation tests.
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


def test_component_conduit_validate_resolution_reports_missing_dependencies() -> None:
    """
    Purpose:
        Validate component resolution surfaces missing contracted dependencies.
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

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
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
        borrower.cleanup()
        owner.cleanup()


def test_component_conduit_validate_resolution_returns_valid_state() -> None:
    """
    Purpose:
        Validate component resolution succeeds with complete contracts.
    Contract:
        - Contracting a root spell with dependencies yields valid resolution state.
        - ConduitResolutionState marks the root as valid.
    Returns:
        None.
    Raises:
        AssertionError: If resolution state is not valid after validation.
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

    owner = owner_book.conjure(automatic=False, name="owner")
    borrower = borrower_book.conjure(automatic=False, name="borrower")
    try:
        assert owner.link(borrower) is True
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
    finally:
        borrower.cleanup()
        owner.cleanup()
