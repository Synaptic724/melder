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
from melder.aether.spellbook.spell_compiler.spell_crafter import SpellCrafter
from melder.aether.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicConfig
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.deep_layers import Depth3Root
from tests.mocks.spellbook.deep_layers import get_depth_3_classes


from tests._frame_posture_test_support import (
    apply_dynamic_defaults_for_spellbook_configuration,
)
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


def _make_dynamic_configuration() -> SpellbookConfiguration:
    """
    Purpose:
        Build a dynamic configuration for component resolution validation tests.
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


def _wrap_phase_counter(
    monkeypatch: pytest.MonkeyPatch,
    counters: dict[str, int],
    method_name: str,
    counter_key: str,
) -> None:
    """
    Purpose:
        Wrap a SpellCrafter phase method and count invocations.
    Contract:
        - Increments counters[counter_key] once per invocation.
        - Delegates to the original method to preserve behavior.
    Args:
        monkeypatch: Pytest monkeypatch fixture.
        counters: Mutable phase-counter mapping.
        method_name: SpellCrafter method name to wrap.
        counter_key: Counter key to increment.
    Returns:
        None.
    """
    original = getattr(SpellCrafter, method_name)

    def _wrapped(self: SpellCrafter, *args, **kwargs):
        """
        Purpose:
            Count invocation and delegate to original method.
        Contract:
            - Preserves original return value and behavior.
        Returns:
            Any: Original method return.
        """
        counters[counter_key] += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SpellCrafter, method_name, _wrapped)


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
        codes = _diagnostic_codes(state)
        assert (
            "visibility_gap_dependency_filtered" in codes
            or "edge_missing_from_blueprint" in codes
            or "missing_index_dependency" in codes
        )
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
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_conduit_add_spell_to_contract_requires_link_transaction() -> None:
    """
    Purpose:
        Validate contract mutations require an active link transaction.
    Contract:
        - add_spell_to_contract raises without a link transaction.
        - add_spell_to_contract succeeds inside a link transaction.
    Returns:
        None.
    Raises:
        AssertionError: If contract gating behavior is incorrect.
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
        with pytest.raises(RuntimeError, match="link transaction"):
            borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            )

        with borrower.transaction("link", conduits=[borrower, owner]):
            assert borrower.add_spell_to_contract(
                spell_id=spell_id,
                conduit=owner,
                permissions="create",
            ) is True
            contracted = borrower.get_spells_in_contract_by_conduit(owner._id)
            assert contracted is not None
            inbound = contracted.get("inbound", [])
            assert any(entry[0] == spell_id for entry in inbound)
    finally:
        borrower.cleanup()
        owner.cleanup()


def test_component_conduit_upgrade_seeds_resolution_state_from_root() -> None:
    """
    Purpose:
        Validate upgraded lesser conduits inherit root resolution state.
    Contract:
        - Root validation records a valid resolution state.
        - Upgrading a lesser conduit seeds a distinct resolution state.
        - Seeded state preserves root validity.
    Returns:
        None.
    Raises:
        AssertionError: If upgraded resolution state is missing or invalid.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)

    depth3_ids = _bind_graph(
        spellbook,
        get_depth_3_classes(),
        existence=Existence.unique,
    )

    root = spellbook.conjure(automatic=False, name="root")
    lesser = root.create_lesser_conduit()
    try:
        original_id = lesser.id
        root_state = root.validate_resolution()
        assert root_state is not None
        assert root_state.has_errors() is False
        assert root_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid

        lesser.upgrade_to_normal(name="upgraded")
        upgraded_state = lesser.get_resolution_state()

        assert upgraded_state is not None
        assert upgraded_state is not root_state
        assert upgraded_state.has_errors() is False
        assert upgraded_state.get_root_validity(depth3_ids[Depth3Root]) is SpellValidity.valid
        assert lesser.id == original_id
    finally:
        root.cleanup()


def test_component_conduit_validate_resolution_matches_get_resolution_state() -> None:
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
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        state = conduit.validate_resolution()
        assert state is not None
        assert conduit.get_resolution_state() is state
    finally:
        conduit.cleanup()


def test_component_conduit_resolution_state_cleaned_on_conduit_cleanup() -> None:
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

    conduit = spellbook.conjure(automatic=False, name="root")
    state = conduit.validate_resolution()
    conduit.cleanup()

    assert state is not None
    assert state.cleaned is True


def test_component_conduit_validate_resolution_raises_when_cleaned() -> None:
    """
    Purpose:
        Validate cleaned conduits reject resolution validation requests.
    Contract:
        - validate_resolution raises RuntimeError after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If cleaned conduits accept validation.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(automatic=False, name="root")
    conduit.cleanup()

    with pytest.raises(RuntimeError):
        conduit.validate_resolution()


def test_component_meld_revalidation_uses_local_phase_lane(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Purpose:
        Verify component-level meld revalidation routes through local phases 5/6/7.
    Contract:
        - Conjure uses frame-wide 5/6/7 once.
        - Post-conjure bind + meld executes local 5/6/7 exactly once.
        - Frame-wide 5/6/7 are not reinvoked during the meld revalidation pass.
    Returns:
        None.
    Raises:
        AssertionError: If meld revalidation does not use local phase routing.
    """
    configuration = _make_dynamic_configuration()
    spellbook = Spellbook(configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    counters = {
        "root_blueprints": 0,
        "system_validation": 0,
        "change_control": 0,
        "root_blueprints_local": 0,
        "system_validation_local": 0,
        "change_control_local": 0,
    }
    _wrap_phase_counter(monkeypatch, counters, "run_phase_root_blueprints", "root_blueprints")
    _wrap_phase_counter(monkeypatch, counters, "run_phase_system_validation", "system_validation")
    _wrap_phase_counter(monkeypatch, counters, "run_phase_change_control", "change_control")
    _wrap_phase_counter(
        monkeypatch,
        counters,
        "run_phase_root_blueprints_local",
        "root_blueprints_local",
    )
    _wrap_phase_counter(
        monkeypatch,
        counters,
        "run_phase_system_validation_local",
        "system_validation_local",
    )
    _wrap_phase_counter(
        monkeypatch,
        counters,
        "run_phase_change_control_local",
        "change_control_local",
    )

    conduit = spellbook.conjure(automatic=False, name="root")
    try:
        assert counters["root_blueprints"] == 1
        assert counters["system_validation"] == 1
        assert counters["change_control"] == 1

        counters["root_blueprints"] = 0
        counters["system_validation"] = 0
        counters["change_control"] = 0
        counters["root_blueprints_local"] = 0
        counters["system_validation_local"] = 0
        counters["change_control_local"] = 0

        with spellbook.binding_transaction():
            spell_id = spellbook.bind(
                spell=BasicConfig,
                existence=Existence.unique,
                permissions="create",
            )

        instance = conduit.meld(spell=spell_id)
        assert instance is not None
        assert counters["root_blueprints"] == 0
        assert counters["system_validation"] == 0
        assert counters["change_control"] == 0
        assert counters["root_blueprints_local"] == 1
        assert counters["system_validation_local"] == 1
        assert counters["change_control_local"] == 1
    finally:
        conduit.cleanup()
