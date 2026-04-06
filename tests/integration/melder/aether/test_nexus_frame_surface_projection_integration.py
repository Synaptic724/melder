import pytest

from melder.aether.aether import Aether
from melder.aether.aether_utility_system import AetherUtilitySystem
from melder.aether.conduit.conduit import Conduit
from melder.aether.nexus.nexus import Nexus
from melder.aether.nexus.rift.frame_viewer.frame_view import FrameView
from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
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
    yield
    Nexus._reset_singleton_for_tests()
    Aether._reset_singleton_for_tests()
    AetherUtilitySystem._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


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


def test_integration_nexus_can_project_frame_view_after_passive_publish() -> None:
    """
    Verify Nexus can project a `FrameView` after real passive publication.

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
        nexus = Nexus()
        frame_view = nexus.create_frame_view("ops")

        assert isinstance(frame_view, FrameView)
        assert frame_view.frame_name == "ops"
        assert frame_view.metadata["link_count"] >= 3
        assert "frame" in {
            link.source_kind for link in frame_view.links_by_id.values()
        }
    finally:
        conduit.cleanup()


def test_integration_nexus_can_project_frame_viewer_after_passive_publish() -> None:
    """
    Verify Nexus can assemble a `FrameViewer` after real passive publication.

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
        nexus = Nexus()
        viewer = nexus.create_frame_viewer(["ops"], contract_profile_name="safe")

        assert isinstance(viewer, FrameViewer)
        assert viewer.metadata["frame_count"] == 1
        assert viewer.list_frame_names() == ["ops"]
        assert len(viewer.list_links()) >= 3
    finally:
        conduit.cleanup()
