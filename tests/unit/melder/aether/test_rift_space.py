import threading
from types import SimpleNamespace

import pytest

from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


def test_rift_space_rejects_empty_owner_and_invalid_frame_viewer() -> None:
    class _BaseSpace(RiftSpace):
        def _create_command_system(self):
            return SimpleNamespace(cleanup=lambda: None)

    with pytest.raises(ValueError, match="owner_rift_id cannot be empty."):
        StaticRiftSpace("")

    base_space = _BaseSpace("rift-1")
    assert base_space.command_system is not None
    root_space = RiftSpace("rift-2")
    assert root_space.command_system is not None


def test_rift_space_exposes_space_kind_metadata_and_event_system() -> None:
    metadata = {"mode": "safe"}
    space = StaticRiftSpace(
        "rift-1",
        space_name="ops",
        metadata=metadata,
        space_id="space-custom",
    )

    assert space.space_kind == "static"
    assert space.metadata == {"mode": "safe"}
    assert space.metadata is not metadata
    assert space.event_system is space._event_system
    assert space.event_system.rift_id == "rift-1"
    assert space.event_system.space_id == "space-custom"
    assert space.event_system.space_kind == "static"


def test_rift_space_exposes_properties_and_cleanup_cleans_owned_state(monkeypatch) -> None:
    event_cleanup = []
    workstation_cleanup = []
    command_cleanup = []
    viewer_cleanup = []
    space = StaticRiftSpace(
        "rift-1",
        space_name="ops",
        metadata={"mode": "safe"},
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
    space._event_system = SimpleNamespace(cleanup=lambda: event_cleanup.append(True))

    assert space.space_name == "ops"
    assert space.owner_rift_id == "rift-1"
    assert space.frame_viewer is static_viewer
    assert space.memory_system is space._memory_system
    assert space.event_system is space._event_system
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
    assert space._memory_system is None
    assert space._event_system is None
    assert space._workstation is None
    assert space._command_system is None
    assert space._space_id is None


def test_rift_space_internal_viewer_replacement_and_target_guardrails_work(monkeypatch) -> None:
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
        base_space._replace_frame_viewer(object())

    space._replace_frame_viewer(first_viewer)
    space._replace_frame_viewer(second_viewer)
    assert cleaned == [first_viewer]

    space._clear_frame_viewer()
    assert cleaned == [first_viewer, second_viewer]
    space._clear_frame_viewer()

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


def test_rift_space_event_system_registry_and_event_emission_work() -> None:
    space = StaticRiftSpace("rift-1")
    received = []

    with pytest.raises(TypeError, match="callback must be callable."):
        space.event_system.register_event_callback(None)

    with pytest.raises(ValueError, match="subscription_id cannot be empty."):
        space.event_system.unregister_event_callback("")

    subscription_id = space.event_system.register_event_callback(lambda event: received.append(event))
    assert isinstance(subscription_id, str)

    event = space.event_system.create_event(
        "demo",
        payload={"kind": "demo"},
        frame_name="ops",
        metadata={"scope": "test"},
    )
    assert event.event_type == "demo"
    assert event.rift_id == "rift-1"
    assert event.space_id == space.space_id
    assert event.space_kind == "static"
    assert event.frame_name == "ops"
    assert event.payload == {"kind": "demo"}
    assert event.metadata == {"scope": "test"}

    emitted_event = space.event_system.create_and_emit_event(
        "binding_collected",
        payload={"binding_name": "client"},
    )
    assert emitted_event is received[0]
    assert emitted_event.event_type == "binding_collected"
    assert emitted_event.payload == {"binding_name": "client"}

    space.event_system.unregister_event_callback(subscription_id)
    space.event_system.create_and_emit_event("ignored", payload={"kind": "ignored"})
    assert len(received) == 1


def test_rift_space_event_system_property_is_live() -> None:
    space = StaticRiftSpace("rift-1")

    assert space.event_system is not None


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
