from __future__ import annotations

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.spellbook.spell_crafter.blueprints.root_resolution_blueprint import (
    RootResolutionBlueprint,
)
from melder.spellbook.spell_crafter.dag.directed_acyclic_work_graph import (
    DirectedAcyclicWorkGraph,
)
from tests.mocks.spellbook.core_classes import BasicConfig
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


def _make_configuration(
    *,
    aether_frame: str = "default",
    dynamic: bool = False,
    workers: int = 1,
) -> SpellbookConfiguration:
    """
    Purpose:
        Create a configuration for Aether integration tests.
    Contract:
        - system_state is set to automatic or dynamic.
        - phase_scheduler_workers_per_spellbook is set.
    Args:
        dynamic: Whether to use dynamic defaults.
        workers: Scheduler workers per spellbook.
    Returns:
        SpellbookConfiguration: Configured instance.
    """
    configuration = SpellbookConfiguration(aether_frame=aether_frame)
    if dynamic:
        apply_dynamic_defaults_for_spellbook_configuration(configuration)
    else:
        apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", workers)
    return configuration


def test_bottom_up_default_frame_cleanup_blocks_default_access() -> None:
    """
    Purpose:
        Validate bottom-up default-frame cleanup clears default-frame access.
    Contract:
        - _ensure_default_frame raises after default is cleaned.
        - Default-frame accessors raise after cleanup.
    Returns:
        None.
    Raises:
        AssertionError: If default access is still available after cleanup.
    """
    aether = Aether()
    aether._default_frame.cleanup()

    with pytest.raises(RuntimeError, match="Default AethericFrame"):
        aether._ensure_default_frame()
    with pytest.raises(RuntimeError, match="Default AethericFrame"):
        aether._get_conduit_cloud("default")


def test_aether_devops_accessors_missing_frame_raise() -> None:
    """
    Purpose:
        Validate devops and mutation accessors reject missing frames.
    Contract:
        - Each accessor raises ValueError when frame is missing.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame accessors do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_devops_manager("missing-frame")
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_spell_system_states("missing-frame")
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_incident_manager("missing-frame")
    with pytest.raises(ValueError, match="does not exist"):
        aether._get_change_control_manager("missing-frame")
    assert aether._get_mutation_research() is aether.mutation_research


def test_aether_conduit_cloud_unregister_removes_entry() -> None:
    """
    Purpose:
        Validate explicit conduit cloud unregistration removes the entry.
    Contract:
        - ConduitCloud resolves the root conduit through the borrowed
          frame-owned root registry before and after explicit cloud
          unregistration.
        - `_unregister_conduit_cloud(...)` removes only the explicit dynamic
          cloud entry from `_registry`.
    Returns:
        None.
    Raises:
        AssertionError: If unregistration does not clear the entry.
    """
    frame_name = "frame-cloud"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name, dynamic=True),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(automatic=False, name="root")
    aether = Aether()
    try:
        cloud = aether._get_conduit_cloud(frame_name)
        assert cloud.get_conduit("root") is conduit
        assert cloud._registry["root"] is conduit

        aether._unregister_conduit_cloud(conduit, frame_name)
        assert "root" not in cloud._registry
        assert cloud.get_conduit("root") is conduit
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_add_remove_conduit_duplicate_errors() -> None:
    """
    Purpose:
        Validate duplicate add/remove conduit operations raise ValueError.
    Contract:
        - _add_conduit raises when the conduit is already registered.
        - _remove_conduit raises when the conduit is missing.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate operations do not raise.
    """
    frame_name = "frame-duplicates"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    aether = Aether()
    try:
        with pytest.raises(ValueError, match="already exists"):
            aether._add_conduit(conduit, frame_name)

        aether._remove_conduit(conduit, frame_name)
        with pytest.raises(ValueError, match="does not exist"):
            aether._remove_conduit(conduit, frame_name)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_rejects_duplicate_root_conduit_names_per_frame() -> None:
    """
    Purpose:
        Validate root conduit names are unique within one frame.

    Contract:
        - Conjuring a second root conduit with the same name in the same frame
          raises ValueError.
    Returns:
        None.
    Raises:
        AssertionError: If duplicate root conduit names are accepted.
    """
    frame_name = "frame-duplicate-root-names"
    owner_book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    borrower_book = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    owner_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    borrower_book.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    owner = owner_book.conjure(name="root")
    try:
        with pytest.raises(ValueError, match="Conduit with name root already exists"):
            borrower_book.conjure(name="root")
    finally:
        owner.cleanup()
        owner_book.cleanup()
        borrower_book.cleanup()


def test_aether_remove_single_spell_index_updates_registry() -> None:
    """
    Purpose:
        Validate removal of a single SpellIndex updates the version registry.
    Contract:
        - _check_for_spell finds both spell ids before removal.
        - After removal, the removed spell id is no longer found.
    Returns:
        None.
    Raises:
        AssertionError: If the version registry is stale after removal.
    """
    frame_name = "frame-remove-index"
    spellbook = Spellbook(
        aetheric_frame=frame_name,
        configuration=_make_configuration(aether_frame=frame_name),
    )
    service_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    with spellbook.binding_transaction():
        config_id = spellbook.bind(
            spell=BasicConfig,
            existence=Existence.unique,
            permissions="create",
        )
    aether = Aether()
    try:
        assert aether._check_for_spell(service_id, frame_name) is not None
        assert aether._check_for_spell(config_id, frame_name) is not None

        config_index = next(
            idx for idx in spellbook._spells.keys() if idx.current == config_id
        )
        aether._remove_single_spell_index(conduit.id, config_index, frame_name)

        assert aether._check_for_spell(config_id, frame_name) is None
        assert aether._check_for_spell(service_id, frame_name) is not None
    finally:
        conduit.cleanup()
        spellbook.cleanup()


def test_aether_check_for_spell_missing_frame_raises() -> None:
    """
    Purpose:
        Validate _check_for_spell rejects missing frames.
    Contract:
        - ValueError is raised when frame does not exist.
    Returns:
        None.
    Raises:
        AssertionError: If missing-frame checks do not raise.
    """
    aether = Aether()
    with pytest.raises(ValueError, match="does not exist"):
        aether._check_for_spell("spell-id", "missing-frame")


def test_aether_get_all_spell_versions_empty_frame() -> None:
    """
    Purpose:
        Validate _get_all_spell_versions returns empty set for new frames.
    Contract:
        - New frames have no spell versions.
    Returns:
        None.
    Raises:
        AssertionError: If new frames report non-empty versions.
    """
    aether = Aether()
    aether._ensure_frame("empty-frame")
    versions = aether._get_all_spell_versions("empty-frame")
    assert versions == set()


def test_aether_revalidate_dirty_roots_calls_change_control() -> None:
    """
    Purpose:
        Validate Aether revalidation routes through ChangeControlManager.
    Contract:
        - Dirty roots are passed to the registered revalidator.
        - Dirty flags are cleared after successful revalidation.
    Returns:
        None.
    Raises:
        AssertionError: If revalidation does not execute or clear flags.
    """
    aether = Aether()
    frame_name = "frame-devops"
    conduit_id = "conduit-1"
    aether._ensure_frame(frame_name)
    ccm = aether._get_change_control_manager(frame_name)

    dag = DirectedAcyclicWorkGraph()
    dag.add_node("dep")
    dag.add_node("root")
    blueprint = RootResolutionBlueprint(
        root_spell_id="root",
        root_lineage_id="lineage-root",
        dag=dag,
        ordered_node_ids=["dep", "root"],
    )

    try:
        ccm.rebuild_component_of(conduit_id, {"root": blueprint})
        calls: list[set[str]] = []

        def revalidator(dirty_roots: set[str], _cancel: object | None) -> None:
            calls.append(set(dirty_roots))

        ccm.set_revalidator(conduit_id, revalidator)
        ccm.notify_spell_changed("dep")
        assert ccm.is_root_dirty(conduit_id, "root") is True

        aether._revalidate_dirty_roots(conduit_id, frame_name)

        assert calls == [{"root"}]
        assert ccm.is_root_dirty(conduit_id, "root") is False
    finally:
        blueprint.cleanup()
