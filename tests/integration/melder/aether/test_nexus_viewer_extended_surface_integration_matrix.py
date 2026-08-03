import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.nexus.nexus import Nexus
from melder.nexus.configuration.rift_space_type import RiftSpaceType
from melder.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spellbook import Spellbook


from tests._frame_posture_test_support import (
    apply_automatic_defaults_for_spellbook_configuration,
    set_frame_rift_enabled_for_spellbook_configuration,
)
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


class SharedCollisionService:
    """
    Shared service used to create real cross-frame spell/binding collisions.
    """

    def run(self) -> str:
        """
        Return a stable string for integration assertions.

        Returns:
            str: Stable integration string.
        """
        return "shared"


class SharedCollisionServiceB:
    """
    The finance-frame counterpart to `SharedCollisionService`.

    A DISTINCT class bound under the SAME spellframe and binding_name, so the two
    frames still collide on the LOOKUP KEY - what the viewer's cross-frame
    compare/collision helpers actually report - while minting DIFFERENT spell_ids.

    Before process-wide uniqueness both frames bound the same class, colliding on
    the lookup key AND the spell_id at once. The spell_id half was incidental
    scaffolding, never the subject; it is refused at conjure now, so the two
    halves are separated here rather than the test being weakened.

    THE __name__ REASSIGNMENT BELOW IS LOAD-BEARING. The viewer groups
    `describe_spell_name_collisions` by the spell NAME, while the bind-time
    fingerprint hashes name AND qualname AND module (bind.py:572-631). Matching
    the name keeps the NAME collision the viewer must report; the differing
    qualname keeps the spell_ids apart. Drop it and spell_name_collisions
    silently finds nothing - which is how this test failed once already.
    """

    def run(self) -> str:
        """
        Return a stable string for integration assertions.

        Returns:
            str: Stable integration string.
        """
        return "shared"


SharedCollisionServiceB.__name__ = SharedCollisionService.__name__


class OpsMismatchService:
    """
    Secondary service used to create one real spellbook mismatch posture.
    """

    def run(self) -> str:
        """
        Return a stable string for integration assertions.

        Returns:
            str: Stable integration string.
        """
        return "mismatch"


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
    StaticFrameViewer._aether = aether
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    StaticFrameViewer._aether = aether


def _make_rift_publishable_configuration(aetheric_frame: str) -> SpellbookConfiguration:
    """
    Build one Spellbook configuration that allows Nexus/Rift publication.

    Args:
        aetheric_frame:
            Target frame name for the spellbook.

    Returns:
        SpellbookConfiguration: Publishable dynamic configuration.
    """
    configuration = SpellbookConfiguration(aether_frame=aetheric_frame)
    apply_automatic_defaults_for_spellbook_configuration(configuration)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    set_frame_rift_enabled_for_spellbook_configuration(configuration, True)
    return configuration


def _build_real_room_viewer() -> object:
    """
    Build one real room-owned viewer for integration checks.

    Returns:
        object: Viewer built from a real Spellbook/Rift path.
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
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(2)
    system_configuration.with_default_space_type(RiftSpaceType.capability)
    system_configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.activate(system_configuration)
    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.capability)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.create_frame_link("ops")
    viewer = rift.get_frame_viewer()
    return spellbook, conduit, nexus, viewer


def _build_real_rift_viewer() -> object:
    """
    Build one real Rift-backed viewer for integration checks.

    Returns:
        object: Tuple of live runtime objects plus the attached Rift viewer.
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
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(2)
    system_configuration.with_default_space_type(RiftSpaceType.capability)
    system_configuration.with_allowed_target_frame_names(("default", "ops"))
    nexus.activate(system_configuration)

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.capability)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="ops_rift")
    rift.create_frame_link("ops")
    viewer = rift.get_frame_viewer()
    return spellbook, conduit, nexus, rift, viewer


def _build_real_multi_frame_room_viewer() -> object:
    """
    Build one real two-frame room-owned viewer with collision and mismatch
    state.

    Returns:
        object: Tuple of spellbooks, conduits, Nexus, and attached viewer.
    """
    ops_configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    finance_configuration = _make_rift_publishable_configuration(
        aetheric_frame="finance"
    )

    ops_spellbook = Spellbook(aetheric_frame="ops", configuration=ops_configuration)
    finance_spellbook = Spellbook(
        aetheric_frame="finance",
        configuration=finance_configuration,
    )

    ops_spellbook.bind(
        spell=SharedCollisionService,
        existence=Existence.unique,
        permissions="create",
        binding_name="shared_binding",
        spellframe="SharedFrame",
    )
    ops_spellbook.bind(
        spell=OpsMismatchService,
        existence=Existence.many,
        permissions="read",
        binding_name="ops_mismatch",
        spellframe="OpsFrame",
    )
    finance_spellbook.bind(
        spell=SharedCollisionServiceB,
        existence=Existence.unique,
        permissions="create",
        binding_name="shared_binding",
        spellframe="SharedFrame",
    )

    ops_conduit = ops_spellbook.conjure(name="ops_root")
    finance_conduit = finance_spellbook.conjure(name="finance_root")
    nexus = Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(3)
    system_configuration.with_default_space_type(RiftSpaceType.capability)
    system_configuration.with_allowed_target_frame_names(("default", "ops", "finance"))
    nexus.activate(system_configuration)
    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.capability)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="dual_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")
    viewer = rift.get_frame_viewer()
    return (
        ops_spellbook,
        finance_spellbook,
        ops_conduit,
        finance_conduit,
        nexus,
        viewer,
    )


def _build_real_multi_frame_rift_viewer() -> object:
    """
    Build one real two-frame Rift-projected viewer with collision state.

    Returns:
        object: Tuple of spellbooks, conduits, Nexus, Rift, and viewer.
    """
    ops_configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    finance_configuration = _make_rift_publishable_configuration(
        aetheric_frame="finance"
    )

    ops_spellbook = Spellbook(aetheric_frame="ops", configuration=ops_configuration)
    finance_spellbook = Spellbook(
        aetheric_frame="finance",
        configuration=finance_configuration,
    )

    ops_spellbook.bind(
        spell=SharedCollisionService,
        existence=Existence.unique,
        permissions="create",
        binding_name="shared_binding",
        spellframe="SharedFrame",
    )
    ops_spellbook.bind(
        spell=OpsMismatchService,
        existence=Existence.many,
        permissions="read",
        binding_name="ops_mismatch",
        spellframe="OpsFrame",
    )
    finance_spellbook.bind(
        spell=SharedCollisionServiceB,
        existence=Existence.unique,
        permissions="create",
        binding_name="shared_binding",
        spellframe="SharedFrame",
    )

    ops_conduit = ops_spellbook.conjure(name="ops_root")
    finance_conduit = finance_spellbook.conjure(name="finance_root")
    nexus = Nexus()
    system_configuration = nexus.create_configuration()
    system_configuration.with_rift_creation_enabled(True)
    system_configuration.with_direct_rift_access(True)
    system_configuration.with_target_frame_override(True)
    system_configuration.with_multiple_target_frames(True)
    system_configuration.with_max_target_frame_count(3)
    system_configuration.with_default_space_type(RiftSpaceType.capability)
    system_configuration.with_allowed_target_frame_names(("default", "ops", "finance"))
    nexus.activate(system_configuration)

    rift_configuration = (
        nexus.create_rift_configuration()
        .with_space_type(RiftSpaceType.capability)
    )
    rift = nexus.create_rift(configuration=rift_configuration, rift_name="dual_rift")
    rift.create_frame_link("ops")
    rift.create_frame_link("finance")
    viewer = rift.get_frame_viewer()
    return (
        ops_spellbook,
        finance_spellbook,
        ops_conduit,
        finance_conduit,
        nexus,
        rift,
        viewer,
    )


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
    conduit_id = viewer.list_targets(
        frame_name="ops",
        source_kind="conduit",
    )[0].source_id
    spell_source_id = viewer.list_targets(
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
        "list_index_ids",
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
    ("list_index_ids", "list"),
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
    spellbook, conduit, _, viewer = _build_real_room_viewer()
    try:
        result = getattr(viewer, method_name)(**_build_method_kwargs(viewer, method_name))
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
        result = getattr(viewer, method_name)(**_build_method_kwargs(viewer, method_name))
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


def test_real_nexus_viewer_multi_frame_compare_collision_and_filter_helpers() -> None:
    (
        ops_spellbook,
        _finance_spellbook,
        ops_conduit,
        finance_conduit,
        _,
        viewer,
    ) = _build_real_multi_frame_room_viewer()
    try:
        comparison = viewer.compare_frames_brief("ops", "finance")
        binding_collisions = viewer.describe_binding_name_collisions()
        spell_name_collisions = viewer.describe_spell_name_collisions()
        spellframe_groups = viewer.describe_spellframe_groups()
        permission_mismatches = viewer.describe_spellbook_permission_mismatches()
        existence_mismatches = viewer.describe_spellbook_existence_mismatches()

        assert comparison["same_frame_id"] is False
        assert comparison["same_nexus_contract"] is True
        assert comparison["left_only_spell_count"] >= 1
        assert comparison["right_only_spell_count"] >= 1

        assert binding_collisions["shared_binding"] == (
            binding_collisions["shared_binding"][0],
            binding_collisions["shared_binding"][1],
        )
        assert len(binding_collisions["shared_binding"]) == 2
        assert any(len(source_ids) == 2 for source_ids in spell_name_collisions.values())
        assert len(spellframe_groups["SharedFrame"]) == 2

        assert len(viewer.list_spells_by_owner_conduit(ops_conduit.id, frame_name="ops")) == 2
        assert len(viewer.list_spells_by_spellbook_id(ops_spellbook.id)) == 2
        assert len(viewer.list_spells_by_permission("read")) == 1
        assert len(viewer.list_spells_by_existence("many")) == 1
        assert len(viewer.list_spells_by_spellframe("SharedFrame")) == 2

        assert ops_spellbook.id in permission_mismatches
        assert permission_mismatches[ops_spellbook.id]["values"] == ("create", "read")
        assert ops_spellbook.id in existence_mismatches
        assert existence_mismatches[ops_spellbook.id]["values"] == ("many", "unique")
    finally:
        ops_conduit.cleanup()
        finance_conduit.cleanup()
        ops_spellbook.cleanup()
        _finance_spellbook.cleanup()


def test_real_rift_viewer_multi_frame_compare_collision_and_filter_helpers() -> None:
    (
        ops_spellbook,
        _finance_spellbook,
        ops_conduit,
        finance_conduit,
        _,
        rift,
        viewer,
    ) = _build_real_multi_frame_rift_viewer()
    try:
        comparison = viewer.compare_frames("ops", "finance")
        binding_collisions = viewer.describe_binding_name_collisions()
        spellframe_groups = viewer.describe_spellframe_groups()
        permission_mismatches = viewer.describe_spellbook_permission_mismatches()

        assert viewer.list_frame_names() == ["finance", "ops"]
        assert comparison["same_frame_id"] is False
        assert comparison["same_nexus_contract"] is True
        assert len(binding_collisions["shared_binding"]) == 2
        assert len(spellframe_groups["SharedFrame"]) == 2
        assert len(viewer.list_spells_by_spellbook_id(ops_spellbook.id)) == 2
        assert len(viewer.list_spells_by_permission("read")) == 1
        assert len(viewer.list_spells_by_existence("many")) == 1
        assert len(viewer.list_spells_by_spellframe("SharedFrame")) == 2
        assert permission_mismatches[ops_spellbook.id]["values"] == ("create", "read")
    finally:
        rift.cleanup()
        ops_conduit.cleanup()
        finance_conduit.cleanup()
        ops_spellbook.cleanup()
        _finance_spellbook.cleanup()


def test_real_nexus_viewer_multi_frame_explicit_frame_routes_helper_reads() -> None:
    (
        ops_spellbook,
        finance_spellbook,
        ops_conduit,
        finance_conduit,
        _,
        viewer,
    ) = _build_real_multi_frame_room_viewer()
    try:
        inventory = viewer.describe_frame_inventory(frame_name="finance")
        spells = viewer.describe_spells(frame_name="finance")
        finance_spell_source_ids = viewer.list_spells_by_spellbook_id(finance_spellbook.id)

        assert inventory["frame_name"] == "finance"
        assert len(spells) == 1
        assert [spell["source_id"] for spell in spells] == finance_spell_source_ids
    finally:
        ops_conduit.cleanup()
        finance_conduit.cleanup()
        ops_spellbook.cleanup()
        finance_spellbook.cleanup()


def test_real_rift_viewer_multi_frame_explicit_frame_routes_helper_reads() -> None:
    (
        ops_spellbook,
        finance_spellbook,
        ops_conduit,
        finance_conduit,
        _,
        rift,
        viewer,
    ) = _build_real_multi_frame_rift_viewer()
    try:
        inventory = viewer.describe_frame_inventory(frame_name="finance")
        spells = viewer.describe_spells(frame_name="finance")
        finance_spell_source_ids = viewer.list_spells_by_spellbook_id(finance_spellbook.id)

        assert inventory["frame_name"] == "finance"
        assert len(spells) == 1
        assert [spell["source_id"] for spell in spells] == finance_spell_source_ids
    finally:
        rift.cleanup()
        ops_conduit.cleanup()
        finance_conduit.cleanup()
        ops_spellbook.cleanup()
        finance_spellbook.cleanup()


