import threading
import time

import pytest

from melder.nexus.rift.rift_gate.rift_gate import RiftGate
from melder.nexus.rift.rift_gate_controller.rift_gate_controller import (
    RiftGateController,
)


def test_rift_gate_starts_open_and_tracks_tickets() -> None:
    gate = RiftGate()

    assert gate.enabled is True
    assert gate.is_closed() is False
    assert gate.has_active_tickets() is False
    assert gate.active_ticket_count() == 0

    gate.register_ticket()
    gate.register_ticket()

    assert gate.has_active_tickets() is True
    assert gate.active_ticket_count() == 2

    gate.unregister_ticket()
    gate.unregister_ticket()

    assert gate.has_active_tickets() is False
    assert gate.active_ticket_count() == 0


def test_rift_gate_wait_blocks_until_open() -> None:
    gate = RiftGate(enabled=False)
    released = []

    def _waiter() -> None:
        gate.wait()
        released.append(True)

    thread = threading.Thread(target=_waiter)
    thread.start()
    time.sleep(0.05)
    assert released == []

    gate.open()
    thread.join(timeout=1.0)

    assert released == [True]


def test_rift_gate_admit_raises_when_entry_mode_is_raise() -> None:
    gate = RiftGate(enabled=False, entry_mode="raise")

    with pytest.raises(RuntimeError, match="RiftGate entry is disabled."):
        gate.admit()


def test_rift_gate_admit_waits_when_entry_mode_is_wait() -> None:
    gate = RiftGate(enabled=False, entry_mode="wait")
    released = []

    def _waiter() -> None:
        gate.admit()
        released.append(True)

    thread = threading.Thread(target=_waiter)
    thread.start()
    time.sleep(0.05)
    assert released == []

    gate.open()
    thread.join(timeout=1.0)

    assert released == [True]


def test_rift_gate_close_and_wait_until_free_waits_for_drain() -> None:
    gate = RiftGate()
    started = threading.Event()

    def _holder() -> None:
        gate.register_ticket()
        started.set()
        time.sleep(0.1)
        gate.unregister_ticket()

    thread = threading.Thread(target=_holder)
    thread.start()
    started.wait(timeout=1.0)

    gate.close_and_wait_until_free(timeout=2.0, interval=0.01)
    thread.join(timeout=1.0)

    assert gate.is_closed() is True
    assert gate.enabled is False
    assert gate.active_ticket_count() == 0


def test_rift_gate_close_and_wait_until_free_timeout_raises() -> None:
    gate = RiftGate()
    gate.register_ticket()

    with pytest.raises(RuntimeError, match="Timeout waiting for rift tickets to drain."):
        gate.close_and_wait_until_free(timeout=0.05, interval=0.01)

    gate.unregister_ticket()


def test_rift_gate_cleanup_is_idempotent() -> None:
    gate = RiftGate()

    gate.cleanup()
    gate.cleanup()

    assert gate.cleaned is True

    with pytest.raises(RuntimeError, match="RiftGate has already been cleaned"):
        gate.wait()


def test_rift_gate_entry_mode_can_be_updated() -> None:
    gate = RiftGate()

    gate.set_entry_mode("raise")
    assert gate.entry_mode == "raise"

    gate.set_entry_mode("wait")
    assert gate.entry_mode == "wait"

    with pytest.raises(ValueError, match="entry_mode must be 'wait' or 'raise'"):
        gate.set_entry_mode("unknown")


def test_rift_gate_controller_create_register_unregister_and_counts() -> None:
    controller = RiftGateController()
    first_gate = controller.create_rift_gate("rift-1")
    second_gate = RiftGate()
    controller.register_rift_gate("rift-2", second_gate)

    assert controller.get_rift_gate("rift-1") is first_gate
    assert controller.get_rift_gate("rift-2") is second_gate

    first_gate.register_ticket()
    second_gate.register_ticket()
    second_gate.register_ticket()

    assert controller.count_active_threads_for_rift("rift-1") == 1
    assert controller.count_active_threads_for_rift("rift-2") == 2
    assert controller.count_active_threads_total() == 3

    first_gate.unregister_ticket()
    second_gate.unregister_ticket()
    second_gate.unregister_ticket()

    controller.unregister_rift_gate("rift-2")
    assert controller.get_rift_gate("rift-2") is None


def test_rift_gate_controller_enable_disable_and_close_and_wait_work() -> None:
    controller = RiftGateController()
    gate = controller.create_rift_gate("rift-1")

    controller.disable_all_rift_gates()
    assert gate.enabled is False

    controller.enable_all()
    assert gate.enabled is True

    gate.register_ticket()

    def _release() -> None:
        time.sleep(0.1)
        gate.unregister_ticket()

    thread = threading.Thread(target=_release)
    thread.start()

    controller.close_and_wait_until_rift_free("rift-1", timeout=2.0, interval=0.01)
    thread.join(timeout=1.0)

    assert gate.is_closed() is True


def test_rift_gate_controller_can_update_entry_modes() -> None:
    controller = RiftGateController()
    first_gate = controller.create_rift_gate("rift-1")
    second_gate = controller.create_rift_gate("rift-2")

    controller.set_rift_gate_entry_mode("rift-1", "raise")
    assert first_gate.entry_mode == "raise"
    assert second_gate.entry_mode == "wait"

    controller.set_all_rift_gate_entry_mode("raise")
    assert first_gate.entry_mode == "raise"
    assert second_gate.entry_mode == "raise"


def test_rift_gate_controller_rejects_duplicate_ids_and_cleanup_is_idempotent() -> None:
    controller = RiftGateController()
    controller.create_rift_gate("rift-1")

    with pytest.raises(ValueError, match="RiftGate already registered for rift_id=rift-1."):
        controller.create_rift_gate("rift-1")

    with pytest.raises(ValueError, match="RiftGate already registered for rift_id=rift-1."):
        controller.register_rift_gate("rift-1", RiftGate())

    controller.cleanup()
    controller.cleanup()

    assert controller.cleaned is True
