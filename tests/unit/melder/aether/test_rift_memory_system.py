import pytest

from melder.aether.nexus.rift.rift_space.memory_system.rift_memory import RiftMemory
from melder.aether.nexus.rift.rift_space.memory_system.rift_memory_system import (
    RiftMemorySystem,
)


def test_rift_memory_system_creates_memory_from_locked_shared_context() -> None:
    system = RiftMemorySystem(rift_id="rift-1", space_type="static")
    system.update_context(
        task_name="task-a",
        activity_name="activity-a",
        mission_name="mission-a",
        agent_name="agent-a",
        agent_id="agent-1",
        metadata={"channel": "ops"},
    )

    memory = system.create_memory(
        frame_name="ops",
        action_name="command.invoke",
        metadata={"target_id": "t-1"},
    )

    assert isinstance(memory, RiftMemory)
    assert memory.frame_name == "ops"
    assert memory.action_name == "command.invoke"
    assert memory.step_counter == 1
    assert memory.epoch_counter == 0
    assert memory.metadata == {
        "channel": "ops",
        "rift_id": "rift-1",
        "space_type": "static",
        "task_name": "task-a",
        "activity_name": "activity-a",
        "mission_name": "mission-a",
        "agent_name": "agent-a",
        "agent_id": "agent-1",
        "target_id": "t-1",
    }


def test_rift_memory_system_counters_can_increment_and_reset() -> None:
    system = RiftMemorySystem(rift_id="rift-1", space_type="codegen")

    assert system.step_counter == 0
    assert system.epoch_counter == 0

    assert system.increment_step() == 1
    assert system.increment_step() == 2
    assert system.increment_epoch() == 1
    assert system.step_counter == 0
    assert system.epoch_counter == 1

    system.increment_step()
    system.reset_step()
    system.reset_epoch()

    assert system.step_counter == 0
    assert system.epoch_counter == 0


def test_rift_memory_system_context_can_be_cleared() -> None:
    system = RiftMemorySystem(rift_id="rift-1", space_type="capability")
    system.update_context(
        task_name="task-a",
        activity_name="activity-a",
        mission_name="mission-a",
        agent_name="agent-a",
        agent_id="agent-1",
        metadata={"channel": "ops"},
    )

    system.clear_context()
    state = system.describe_state()

    assert state["task_name"] is None
    assert state["activity_name"] is None
    assert state["mission_name"] is None
    assert state["agent_name"] is None
    assert state["agent_id"] is None
    assert state["metadata"] == {}


def test_rift_memory_system_requires_frame_and_action_names() -> None:
    system = RiftMemorySystem(rift_id="rift-1", space_type="static")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        system.create_memory(frame_name="", action_name="command.invoke")

    with pytest.raises(ValueError, match="action_name cannot be empty."):
        system.create_memory(frame_name="ops", action_name="")


def test_rift_memory_system_cleanup_is_idempotent() -> None:
    system = RiftMemorySystem(rift_id="rift-1", space_type="static")

    system.cleanup()
    system.cleanup()

    assert system.cleaned is True
