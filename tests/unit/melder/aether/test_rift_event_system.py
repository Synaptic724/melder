import pytest

from melder.aether.nexus.rift.rift_space.event_system.rift_event_system import (
    RiftEventSystem,
)


def test_rift_event_system_preserves_callback_order_and_cleanup_is_idempotent() -> None:
    received = []

    def _first_callback(event) -> None:
        received.append(("first", event.event_type))

    def _second_callback(event) -> None:
        received.append(("second", event.event_type))

    event_system = RiftEventSystem(
        rift_id="rift-1",
        space_id="space-1",
        space_kind="static",
    )

    first_subscription_id = event_system.register_event_callback(_first_callback)
    second_subscription_id = event_system.register_event_callback(_second_callback)

    event = event_system.create_and_emit_event(
        "binding_collected",
        payload={"binding_name": "client"},
        frame_name="ops",
        metadata={"scope": "test"},
    )

    assert event.rift_id == "rift-1"
    assert event.space_id == "space-1"
    assert event.space_kind == "static"
    assert event.frame_name == "ops"
    assert event.payload == {"binding_name": "client"}
    assert event.metadata == {"scope": "test"}
    assert received == [
        ("first", "binding_collected"),
        ("second", "binding_collected"),
    ]

    event_system.unregister_event_callback(first_subscription_id)
    event_system.unregister_event_callback(second_subscription_id)
    event_system.create_and_emit_event("ignored")
    assert received == [
        ("first", "binding_collected"),
        ("second", "binding_collected"),
    ]

    event_system.cleanup()
    event_system.cleanup()

    assert event_system.cleaned is True


def test_rift_event_system_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="rift_id cannot be empty."):
        RiftEventSystem(
            rift_id="",
            space_id="space-1",
            space_kind="static",
        )

    event_system = RiftEventSystem(
        rift_id="rift-1",
        space_id="space-1",
        space_kind="static",
    )

    with pytest.raises(TypeError, match="callback must be callable."):
        event_system.register_event_callback(None)

    with pytest.raises(ValueError, match="subscription_id cannot be empty."):
        event_system.unregister_event_callback("")

    with pytest.raises(ValueError, match="event_type cannot be empty."):
        event_system.create_event("")
