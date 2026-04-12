import threading
from collections import deque
from types import SimpleNamespace

import pytest

from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.rift_event_configuration import (
    RiftEventConfiguration,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


def test_rift_space_rejects_empty_owner_and_invalid_frame_viewer() -> None:
    class _BaseSpace(RiftSpace):
        def _create_command_system(self):
            return SimpleNamespace(cleanup=lambda: None)

    with pytest.raises(ValueError, match="owner_rift_id cannot be empty."):
        StaticRiftSpace("")

    with pytest.raises(TypeError, match="frame_viewer must be a FrameViewer when provided."):
        _BaseSpace("rift-1", frame_viewer=object())

    base_space = _BaseSpace("rift-1")
    assert base_space.command_system is not None
    root_space = RiftSpace("rift-2")
    assert root_space.command_system is not None


def test_rift_space_exposes_space_kind_metadata_and_event_configuration() -> None:
    event_configuration = RiftEventConfiguration()
    metadata = {"mode": "safe"}
    space = StaticRiftSpace(
        "rift-1",
        space_name="ops",
        metadata=metadata,
        event_configuration=event_configuration,
    )

    assert space.space_kind == "static"
    assert space.metadata == {"mode": "safe"}
    assert space.metadata is not metadata
    assert space.event_configuration is event_configuration


def test_rift_space_exposes_properties_and_cleanup_cleans_owned_state(monkeypatch) -> None:
    event_cleanup = []
    workstation_cleanup = []
    command_cleanup = []
    viewer_cleanup = []
    event_configuration = RiftEventConfiguration()
    space = StaticRiftSpace(
        "rift-1",
        space_name="ops",
        metadata={"mode": "safe"},
        event_configuration=event_configuration,
    )
    static_viewer = StaticFrameViewer.__new__(StaticFrameViewer)

    monkeypatch.setattr(
        StaticFrameViewer,
        "cleanup",
        lambda self: viewer_cleanup.append(self),
    )
    space._frame_viewer = static_viewer
    space._workstation = SimpleNamespace(cleanup=lambda: workstation_cleanup.append(True))
    space._command_system = SimpleNamespace(cleanup=lambda: command_cleanup.append(True))
    space._event_configuration = SimpleNamespace(cleanup=lambda: event_cleanup.append(True))

    assert space.space_name == "ops"
    assert space.owner_rift_id == "rift-1"
    assert space.frame_viewer is static_viewer
    assert space.workstation is space._workstation
    assert space.command_system is space._command_system

    space.cleanup()
    space.cleanup()

    assert space.cleaned is True
    assert viewer_cleanup == [static_viewer]
    assert workstation_cleanup == [True]
    assert command_cleanup == [True]
    assert event_cleanup == [True]
    assert space._space_name is None
    assert space._owner_rift_id is None
    assert space._space_kind is None
    assert space._metadata is None
    assert space._frame_viewer is None
    assert space._selected_target_ids_by_frame_name is None
    assert space._event_queue is None
    assert space._event_queue_thread is None
    assert space._event_queue_stop_event is None
    assert space._workstation is None
    assert space._command_system is None
    assert space._event_configuration is None
    assert space._space_id is None


def test_rift_space_attach_detach_and_selected_target_guardrails_work(monkeypatch) -> None:
    class _BaseSpace(RiftSpace):
        def _create_command_system(self):
            return SimpleNamespace(cleanup=lambda: None)

    base_space = _BaseSpace("rift-1")
    space = StaticRiftSpace("rift-1")
    first_viewer = StaticFrameViewer.__new__(StaticFrameViewer)
    second_viewer = StaticFrameViewer.__new__(StaticFrameViewer)
    cleaned = []

    monkeypatch.setattr(
        StaticFrameViewer,
        "cleanup",
        lambda self: cleaned.append(self),
    )

    with pytest.raises(TypeError, match="frame_viewer must be a FrameViewer."):
        base_space.attach_frame_viewer(object())

    space.attach_frame_viewer(first_viewer)
    space.attach_frame_viewer(second_viewer)
    assert cleaned == [first_viewer]

    space.detach_frame_viewer()
    assert cleaned == [first_viewer, second_viewer]
    space.detach_frame_viewer()

    space._frame_viewer = SimpleNamespace(default_view_frame_name=None)
    with pytest.raises(ValueError, match="RiftSpace has no default selected frame."):
        space.list_selected_target_ids()

    with pytest.raises(ValueError, match="RiftSpace has no default selected frame."):
        space.select_target("target-1")

    space._selected_target_ids_by_frame_name = {"ops": ["missing"]}
    space._frame_viewer = SimpleNamespace(
        default_view_frame_name="ops",
        execute_method=lambda *args, **kwargs: [],
    )
    with pytest.raises(ValueError, match="RiftSpace '"):
        StaticRiftSpace("rift-2").get_required_frame_viewer()
    with pytest.raises(ValueError, match="target_id cannot be empty."):
        space.select_target("")
    with pytest.raises(ValueError, match="Target 'target-1' was not found in frame 'ops'."):
        space.select_target("target-1")
    with pytest.raises(ValueError, match="Target 'missing' was not found in frame 'ops'."):
        space.describe_selected_targets()
    space._frame_viewer = SimpleNamespace(default_view_frame_name=None, execute_method=lambda *args, **kwargs: [])
    with pytest.raises(ValueError, match="RiftSpace has no default selected frame."):
        space.describe_selected_targets()


def test_rift_space_viewer_and_target_success_paths_work() -> None:
    space = StaticRiftSpace("rift-1")
    available_targets = [
        SimpleNamespace(link_id="target-1", source_kind="spell", source_id="spell-1"),
        SimpleNamespace(link_id="target-2", source_kind="conduit", source_id="conduit-1"),
    ]
    described_targets = [
        {
            "target_id": "target-1",
            "source_kind": "spell",
            "source_id": "spell-1",
            "display_name": "spell_one",
        }
    ]
    fake_viewer = SimpleNamespace(
        default_view_frame_name="ops",
        list_frame_names=lambda: ["ops"],
        execute_method=lambda method_name, **kwargs: (
            available_targets if method_name == "list_targets" else described_targets
        ),
    )
    space._frame_viewer = fake_viewer

    assert space.list_frame_names() == ["ops"]
    assert space.list_available_targets() == available_targets
    assert space.describe_available_targets() == described_targets
    assert space.get_required_frame_viewer() is fake_viewer

    space.select_target("target-1")
    space.select_target("target-1")
    assert space.list_selected_target_ids() == ["target-1"]
    assert space.describe_selected_targets() == [
        {
            "frame_name": "ops",
            "target_id": "target-1",
            "source_kind": "spell",
            "source_id": "spell-1",
            "display_name": "spell_one",
        }
    ]

    space.clear_selected_targets(frame_name="ops")
    assert space.list_selected_target_ids() == []
    space._selected_target_ids_by_frame_name = {"ops": ["target-1"], "finance": ["target-2"]}
    space.clear_selected_targets()
    assert space._selected_target_ids_by_frame_name == {}


def test_rift_space_event_queue_controls_and_cleanup_paths_work(monkeypatch) -> None:
    space = StaticRiftSpace("rift-1")
    published = []
    waited = []

    space._event_queue = deque([{"kind": "a"}, {"kind": "b"}])
    assert [event["kind"] for event in space._drain_event_queue(max_items=1)] == ["a"]
    assert [event["kind"] for event in space._drain_event_queue(max_items=None)] == ["b"]
    with pytest.raises(ValueError, match="max_items must be >= 1 when provided."):
        space._drain_event_queue(max_items=0)

    with pytest.raises(TypeError, match="handler must be callable."):
        space.manage_event_queue(handler=None)

    with pytest.raises(ValueError, match="poll_interval_seconds cannot be negative."):
        space.manage_event_queue(handler=lambda payload: None, poll_interval_seconds=-1)

    with pytest.raises(ValueError, match="drain_batch_size must be >= 1."):
        space.manage_event_queue(handler=lambda payload: None, drain_batch_size=0)

    space._event_queue_thread = SimpleNamespace(is_alive=lambda: True)
    space.manage_event_queue(handler=lambda payload: None)

    with pytest.raises(ValueError, match="join_timeout_seconds cannot be negative."):
        space.stop_managing_event_queue(join_timeout_seconds=-1)

    stop_calls = []
    joined = []
    space._event_queue_stop_event = SimpleNamespace(set=lambda: stop_calls.append(True))
    space._event_queue_thread = SimpleNamespace(
        is_alive=lambda: True,
        join=lambda timeout: joined.append(timeout),
    )
    space.stop_managing_event_queue(join_timeout_seconds=0.5)
    assert stop_calls == [True]
    assert joined == [0.5]

    space._event_queue_stop_event = None
    space.stop_managing_event_queue()

    space._publish_runtime_event({"kind": "demo"})
    queued = list(space.describe_event_queue())
    assert queued[0]["kind"] == "demo"
    assert queued[0]["space_kind"] == "static"

    space._cleaned = True
    space._publish_runtime_event({"kind": "ignored"})

    class _Waiter:
        def __init__(self) -> None:
            self._set = False

        def is_set(self):
            return self._set

        def wait(self, value):
            waited.append(value)
            self._set = True

    handled = []
    space._cleaned = False
    space._event_queue_stop_event = _Waiter()
    space._event_queue = deque([{"kind": "ok"}])
    space._manage_event_queue_loop(lambda event: handled.append(event["kind"]), 0.25, 2)
    assert handled == ["ok"]
    assert waited == [0.25]

    waited.clear()
    space._event_queue = deque([{"kind": "boom"}])
    space._event_queue_stop_event = _Waiter()
    space._manage_event_queue_loop(lambda event: (_ for _ in ()).throw(RuntimeError("boom")), 0.25, 2)


def test_rift_space_manage_event_queue_starts_thread_and_event_configuration_property_is_live(monkeypatch) -> None:
    started = []

    class _Thread:
        def __init__(self, *args, **kwargs) -> None:
            self.kwargs = kwargs

        def start(self) -> None:
            started.append(self.kwargs["name"])

        def is_alive(self) -> bool:
            return False

        def join(self, timeout: float) -> None:
            return None

    monkeypatch.setattr(
        "melder.aether.nexus.rift.rift_space.rift_space.threading.Thread",
        _Thread,
    )
    space = StaticRiftSpace("rift-1", event_configuration=RiftEventConfiguration())

    space.manage_event_queue(handler=lambda payload: None, poll_interval_seconds=0.1, drain_batch_size=2)

    assert started == ["RiftSpaceEventQueue-{0}".format(space.space_id)]
    assert space.event_configuration is not None


def test_rift_space_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _FlipCleanedOnEnter:
        def __init__(self, space: StaticRiftSpace) -> None:
            self._space = space

        def __enter__(self):
            self._space._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

    space = StaticRiftSpace("rift-1")
    original_lock = space._lock
    space._lock = _FlipCleanedOnEnter(space)
    try:
        space.cleanup()
    finally:
        space._lock = original_lock

    assert space.cleaned is True
