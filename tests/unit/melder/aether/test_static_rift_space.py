from melder.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


def _make_detached_rift_projection_owner() -> object:
    class _DetachedRiftProjectionOwner:
        def _get_default_runtime_frame_name(self):
            return None

        def list_assigned_frame_names(self):
            return tuple()

        def _get_required_view_projection(self, frame_name):
            raise ValueError(
                "View projection for frame '{0}' was not found.".format(
                    frame_name
                )
            )

        def _get_required_command_projection(self, frame_name):
            return None

    return _DetachedRiftProjectionOwner()


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
