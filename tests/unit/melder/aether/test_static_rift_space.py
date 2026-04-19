from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


def _make_detached_rift_projection_owner() -> object:
    return type(
        "_DetachedRiftProjectionOwner",
        (),
        {
            "_get_default_runtime_frame_name": staticmethod(lambda: None),
            "_get_required_command_projection": staticmethod(
                lambda frame_name: None
            ),
        },
    )()


def test_static_rift_space_starts_with_durable_static_viewer_asset() -> None:
    """
    Verify static rooms create a static viewer asset during room init.

    Returns:
        None.
    """
    space = StaticRiftSpace("rift-1", rift=_make_detached_rift_projection_owner())

    assert isinstance(space.frame_viewer, StaticFrameViewer)
    assert space.frame_viewer.count_frames() == 0


def test_static_rift_space_keeps_same_static_viewer_asset() -> None:
    """
    Verify static rooms keep the same static viewer asset while syncing.

    Returns:
        None.
    """
    space = StaticRiftSpace("rift-1", rift=_make_detached_rift_projection_owner())
    first_viewer = space.frame_viewer

    assert isinstance(space.frame_viewer, StaticFrameViewer)
    assert space.frame_viewer is first_viewer
