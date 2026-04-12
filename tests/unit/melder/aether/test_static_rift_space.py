from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


def test_static_rift_space_attach_frame_viewer_keeps_static_viewer_instance(monkeypatch) -> None:
    space = StaticRiftSpace.__new__(StaticRiftSpace)
    attached = []
    static_viewer = StaticFrameViewer.__new__(StaticFrameViewer)

    monkeypatch.setattr(
        "melder.aether.nexus.rift.rift_space.rift_space.RiftSpace.attach_frame_viewer",
        lambda self, frame_viewer: attached.append(frame_viewer),
    )

    space.attach_frame_viewer(static_viewer)

    assert attached == [static_viewer]


def test_static_rift_space_attach_frame_viewer_wraps_non_static_viewer(monkeypatch) -> None:
    space = StaticRiftSpace.__new__(StaticRiftSpace)
    attached = []
    plain_viewer = FrameViewer.__new__(FrameViewer)
    wrapped_viewer = StaticFrameViewer.__new__(StaticFrameViewer)

    monkeypatch.setattr(
        "melder.aether.nexus.rift.frame_viewer.static_frame_viewer.StaticFrameViewer.from_frame_viewer",
        lambda frame_viewer: wrapped_viewer,
    )
    monkeypatch.setattr(
        "melder.aether.nexus.rift.rift_space.rift_space.RiftSpace.attach_frame_viewer",
        lambda self, frame_viewer: attached.append(frame_viewer),
    )

    space.attach_frame_viewer(plain_viewer)

    assert attached == [wrapped_viewer]
