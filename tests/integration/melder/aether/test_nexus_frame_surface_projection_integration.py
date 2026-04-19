import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.configuration.rift_space_type import RiftSpaceType
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_singletons_for_nexus_projection_integration() -> None:
    """
    Reset singleton state around each Nexus projection integration test.

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


def _make_rift_publishable_configuration(
        *,
        aetheric_frame: str,
) -> Configuration:
    """
    Build one Spellbook configuration that publishes passive Nexus state.

    Args:
        aetheric_frame:
            Target frame name.

    Returns:
        Configuration:
            Configured Spellbook configuration.
    """
    configuration = Configuration(aether_frame=aetheric_frame)
    configuration.automatic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    configuration.set_property("rift_enabled", True)
    return configuration


def _enable_nexus_for_target_frame(frame_name: str) -> Nexus:
    """
    Enable Nexus for Rift creation against one target frame.

    Args:
        frame_name:
            Target frame name to allow.

    Returns:
        Nexus: Enabled Nexus with direct Rift access.
    """
    nexus = Nexus()
    configuration = nexus.create_system_configuration()
    configuration.with_rift_creation_enabled(True)
    configuration.with_direct_rift_access(True)
    configuration.with_target_frame_override(True)
    configuration.with_allowed_target_frame_names(("default", frame_name))
    nexus.enable(configuration)
    return nexus


def test_integration_rift_space_can_attach_room_owned_frame_viewer_after_passive_publish() -> None:
    """
    Verify Rift attaches a room-owned `FrameViewer` after real passive
    publication.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = _enable_nexus_for_target_frame("ops")
        rift_configuration = (
            nexus.create_rift_configuration()
            .with_space_type(RiftSpaceType.capability)
        )
        rift = nexus.create_rift(
            configuration=rift_configuration,
            rift_name="ops_rift",
        )
        rift.target_frame("ops")
        viewer = rift.get_frame_viewer()

        assert isinstance(viewer, FrameViewer)
        assert viewer.metadata["frame_count"] == 1
        assert viewer.metadata["rift_id"] == rift.id
        assert viewer.list_frame_names() == ["ops"]
        assert len(viewer.execute_method("list_targets")) >= 3
    finally:
        conduit.cleanup()


def test_integration_rift_get_frame_viewer_exposes_assigned_frame_after_passive_publish() -> None:
    """
    Verify Rift-assigned frames populate available views after real passive
    Nexus publication.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = _enable_nexus_for_target_frame("ops")
        rift_configuration = (
            nexus.create_rift_configuration()
            .with_space_type(RiftSpaceType.capability)
        )
        rift = nexus.create_rift(
            configuration=rift_configuration,
            rift_name="ops_rift",
        )
        rift.target_frame("ops")

        viewer = rift.get_frame_viewer()

        assert isinstance(viewer, FrameViewer)
        assert viewer.metadata["rift_id"] == rift.id
        assert viewer.metadata["assigned_frame_names"] == ("ops",)
        assert list(viewer.frame_descriptors_by_name.keys()) == ["ops"]
        assert viewer.frame_descriptors_by_name["ops"].frame_name == "ops"
        assert len(viewer.execute_method("list_targets")) >= 1
    finally:
        conduit.cleanup()


def test_integration_rift_scoped_refresh_rebuilds_room_owned_viewer_after_passive_publish() -> None:
    """
    Verify a scoped refresh rebuilds the room-owned viewer after passive
    publication.

    Returns:
        None.
    """
    configuration = _make_rift_publishable_configuration(aetheric_frame="ops")
    spellbook = Spellbook(aetheric_frame="ops", configuration=configuration)
    spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )

    conduit = spellbook.conjure(name="root")
    try:
        nexus = _enable_nexus_for_target_frame("ops")
        rift_configuration = (
            nexus.create_rift_configuration()
            .with_space_type(RiftSpaceType.capability)
        )
        rift = nexus.create_rift(
            configuration=rift_configuration,
            rift_name="ops_rift",
        )
        rift.target_frame("ops")

        first_viewer = rift.get_frame_viewer()
        first_viewer_metadata = first_viewer.metadata
        first_viewer_frame_names = list(first_viewer.frame_descriptors_by_name.keys())
        rift.refresh_runtime_projections(frame_names=("ops",))
        second_viewer = rift.get_frame_viewer()

        assert isinstance(first_viewer, FrameViewer)
        assert isinstance(second_viewer, FrameViewer)
        assert first_viewer is second_viewer
        assert first_viewer_metadata["rift_id"] == rift.id
        assert second_viewer.metadata["assigned_frame_names"] == ("ops",)
        assert first_viewer_frame_names == ["ops"]
    finally:
        conduit.cleanup()
