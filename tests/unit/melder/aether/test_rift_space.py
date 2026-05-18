import threading
from types import SimpleNamespace

import pytest

from melder.aether.nexus.rift.frame_viewer.frame_viewer import FrameViewer
from melder.aether.nexus.rift.frame_viewer.static_frame_viewer import (
    StaticFrameViewer,
)
from melder.aether.nexus.rift.rift_space.rift_space import RiftSpace
from melder.aether.nexus.rift.rift_space.static_rift_space import StaticRiftSpace


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
            return SimpleNamespace(
                frame_descriptor=SimpleNamespace(
                    conduit_records_by_id={},
                    spell_records_by_key={},
                ),
                compiled_access_surface=SimpleNamespace(
                    command_frame_enabled=True,
                    enabled_conduit_ids=tuple(),
                    enabled_spell_index_ids=tuple(),
                ),
            )

    return _DetachedRiftProjectionOwner()


def test_rift_space_rejects_empty_owner_and_invalid_frame_viewer() -> None:
    class _BaseSpace(RiftSpace):
        def _create_command_system(self, rift):
            return SimpleNamespace(cleanup=lambda: None)

    with pytest.raises(ValueError, match="owner_rift_id cannot be empty."):
        StaticRiftSpace("", rift=_make_detached_rift_projection_owner())

    base_space = _BaseSpace("rift-1", rift=_make_detached_rift_projection_owner())
    assert base_space.command_system is not None
    root_space = RiftSpace("rift-2", rift=_make_detached_rift_projection_owner())
    assert root_space.command_system is not None
    assert isinstance(root_space.frame_viewer, FrameViewer)
    assert root_space.frame_viewer.count_frames() == 0


def test_rift_space_exposes_space_kind_metadata_and_event_system() -> None:
    metadata = {"mode": "safe"}
    space = StaticRiftSpace(
        "rift-1",
        rift=_make_detached_rift_projection_owner(),
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
        rift=_make_detached_rift_projection_owner(),
        space_name="ops",
        metadata={"mode": "safe"},
    )
    static_viewer = space.frame_viewer

    monkeypatch.setattr(
        StaticFrameViewer,
        "cleanup",
        lambda self: viewer_cleanup.append(self),
    )
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
    assert not hasattr(space, '_space_name')
    assert not hasattr(space, '_owner_rift_id')
    assert not hasattr(space, '_space_kind')
    assert not hasattr(space, '_metadata')
    assert not hasattr(space, '_frame_viewer')
    assert not hasattr(space, '_memory_system')
    assert not hasattr(space, '_event_system')
    assert not hasattr(space, '_workstation')
    assert not hasattr(space, '_command_system')
    assert not hasattr(space, '_id')


def test_rift_space_keeps_same_viewer_asset_without_projection_management() -> None:
    """
    Verify the room keeps one durable viewer asset instead of replacing it.

    Returns:
        None.
    """
    space = RiftSpace("rift-1", rift=_make_detached_rift_projection_owner())
    first_viewer = space.frame_viewer

    assert space.frame_viewer is first_viewer
    assert space.frame_viewer.count_frames() == 0
    assert not hasattr(space, "_sync_frame_viewer_from_projection_sets")


def test_rift_space_event_system_registry_and_event_emission_work() -> None:
    space = StaticRiftSpace("rift-1", rift=_make_detached_rift_projection_owner())
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
    space = StaticRiftSpace("rift-1", rift=_make_detached_rift_projection_owner())

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

    space = StaticRiftSpace("rift-1", rift=_make_detached_rift_projection_owner())
    original_lock = space._lock
    space._lock = _FlipCleanedOnEnter(space)
    try:
        space.cleanup()
    finally:
        space._lock = original_lock

    assert space.cleaned is True
