from typing import Optional

import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook


class BasicExtendedService:
    """
    Basic service used to seed one real spell into the extended viewer matrix.
    """

    def run(self) -> str:
        """
        Return a stable string for integration assertions.

        Returns:
            str: Stable integration string.
        """
        return "ok"


@pytest.fixture(autouse=True)
def fresh_singletons() -> None:
    """
    Reset singleton runtime surfaces around each integration matrix case.

    Returns:
        None.
    """
    AetherUtilitySystem._reset_singleton_for_tests()
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_rift_publishable_configuration(aetheric_frame: str) -> Configuration:
    """
    Build one Spellbook configuration that allows Nexus/Rift publication.

    Args:
        aetheric_frame:
            Target frame name for the spellbook.

    Returns:
        Configuration: Publishable dynamic configuration.
    """
    configuration = Configuration(aether_frame=aetheric_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def _build_real_nexus_viewer() -> object:
    """
    Build one real Nexus-backed viewer for integration checks.

    Returns:
        object: Descriptor-driven viewer built from a real Spellbook/Nexus path.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicExtendedService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root")
    nexus = Nexus()
    viewer = nexus.create_frame_viewer(["ops"])
    return spellbook, conduit, nexus, viewer


def _build_real_rift_viewer() -> object:
    """
    Build one real Rift-backed frame-specific viewer for integration checks.

    Returns:
        object: Tuple of live runtime objects plus the Rift-created viewer.
    """
    spellbook, conduit, nexus, _ = _build_real_nexus_viewer()
    system_configuration = nexus.create_system_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(2)
    system_configuration.with_default_space_type(RiftSpaceType.dynamic)
    system_configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.enable(system_configuration)

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.static)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.target_frame("ops", set_as_default=True)
    viewer = rift.create_new_frame_viewer("ops", viewer_profile_name="general")
    return spellbook, conduit, nexus, rift, viewer


def _build_method_kwargs(viewer: object, method_name: str) -> dict[str, object]:
    """
    Build the required kwargs for one real viewer method call.

    Args:
        viewer:
            Bound real viewer instance.
        method_name:
            Method name being executed.

    Returns:
        dict[str, object]: Method kwargs.
    """
    conduit_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="conduit",
    )[0].source_id
    spell_source_id = viewer.execute_method(
        "list_targets",
        frame_name="ops",
        source_kind="spell",
    )[0].source_id
    if method_name in {
        "list_frame_ids",
        "list_nexus_contracts",
        "count_conduit_records",
        "count_spellbooks",
        "list_origin_spellbook_ids",
        "list_spell_record_ids",
        "list_spell_names",
        "list_binding_names",
        "list_lineage_ids",
        "list_permissions",
        "list_existence_kinds",
        "describe_descriptor_inventory",
    }:
        return {}
    if method_name in {
        "describe_descriptor_topology",
        "describe_conduit_records",
        "describe_spell_records",
        "describe_visible_surface",
        "describe_visible_inventory_by_kind",
        "describe_frame_topology",
    }:
        return {"frame_name": "ops"}
    if method_name == "describe_spell_record":
        return {"spell_source_id": spell_source_id}
    if method_name in {
        "describe_conduit_inventory",
        "describe_conduit_relationships",
        "describe_conduit_access_summary",
    }:
        return {"frame_name": "ops", "conduit_id": conduit_id}
    if method_name in {
        "describe_spell_identity",
        "describe_spell_origin",
        "describe_spell_access_summary",
    }:
        return {"frame_name": "ops", "spell_source_id": spell_source_id}
    raise ValueError(method_name)


INTEGRATION_METHOD_CASES = [
    ("list_frame_ids", "list"),
    ("list_nexus_contracts", "list"),
    ("count_conduit_records", "int"),
    ("count_spellbooks", "int"),
    ("list_origin_spellbook_ids", "list"),
    ("list_spell_record_ids", "list"),
    ("list_spell_names", "list"),
    ("list_binding_names", "list"),
    ("list_lineage_ids", "list"),
    ("list_permissions", "list"),
    ("list_existence_kinds", "list"),
    ("describe_descriptor_inventory", "dict"),
    ("describe_descriptor_topology", "dict"),
    ("describe_conduit_records", "list"),
    ("describe_spell_records", "list"),
    ("describe_spell_record", "dict"),
    ("describe_visible_surface", "dict"),
    ("describe_visible_inventory_by_kind", "dict"),
    ("describe_frame_topology", "dict"),
    ("describe_conduit_inventory", "dict"),
    ("describe_conduit_relationships", "dict"),
    ("describe_conduit_access_summary", "dict"),
    ("describe_spell_identity", "dict"),
    ("describe_spell_origin", "dict"),
    ("describe_spell_access_summary", "dict"),
]


@pytest.mark.parametrize(("method_name", "expected_type"), INTEGRATION_METHOD_CASES)
def test_real_nexus_viewer_extended_method_matrix(
        method_name: str,
        expected_type: str,
) -> None:
    spellbook, conduit, _, viewer = _build_real_nexus_viewer()
    try:
        result = viewer.execute_method(
            method_name,
            **_build_method_kwargs(viewer, method_name),
        )
        if expected_type == "dict":
            assert isinstance(result, dict)
        elif expected_type == "list":
            assert isinstance(result, list)
        elif expected_type == "int":
            assert isinstance(result, int)
        else:
            raise AssertionError(expected_type)
    finally:
        conduit.cleanup()
        spellbook.cleanup()


@pytest.mark.parametrize(("method_name", "expected_type"), INTEGRATION_METHOD_CASES)
def test_real_rift_viewer_extended_method_matrix(
        method_name: str,
        expected_type: str,
) -> None:
    spellbook, conduit, _, rift, viewer = _build_real_rift_viewer()
    try:
        result = viewer.execute_method(
            method_name,
            **_build_method_kwargs(viewer, method_name),
        )
        if expected_type == "dict":
            assert isinstance(result, dict)
        elif expected_type == "list":
            assert isinstance(result, list)
        elif expected_type == "int":
            assert isinstance(result, int)
        else:
            raise AssertionError(expected_type)
    finally:
        rift.cleanup()
        conduit.cleanup()
        spellbook.cleanup()
