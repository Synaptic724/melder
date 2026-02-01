import threading
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit


def test_meld_gate_controller_registers_normal_gate(conduit_normal: Conduit) -> None:
    """
    Verify normal conduits register their MeldGate with the controller.

    Contract:
        - The controller exists for a normal conduit.
        - The controller registry returns the same gate instance.
        - The gate starts with no active tickets.
    """
    controller = conduit_normal._meld_gate_controller
    assert controller is not None
    gate = controller.get_gate(conduit_normal._id)
    assert gate is conduit_normal._meld_gate
    assert gate.has_active_tickets() is False


def test_meld_gate_controller_registers_lesser_gate(
    conduit_normal: Conduit,
) -> None:
    """
    Verify lesser conduits register their own MeldGate in the controller.

    Contract:
        - The lesser conduit has a distinct gate from the normal conduit.
        - Both gates are registered in the controller registry.
    """
    controller = conduit_normal._meld_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        normal_gate = controller.get_gate(conduit_normal._id)
        lesser_gate = controller.get_gate(lesser._id)
        assert normal_gate is conduit_normal._meld_gate
        assert lesser_gate is lesser._meld_gate
        assert normal_gate is not lesser_gate
    finally:
        lesser.cleanup()


def test_meld_gate_controller_disable_all(
    conduit_normal: Conduit,
) -> None:
    """
    Verify the controller can disable all registered meld gates.

    Contract:
        - disable_all() sets enabled=False on every registered gate.
        - enable_all() restores enabled=True.
    """
    controller = conduit_normal._meld_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        controller.disable_all()
        assert conduit_normal._meld_gate.enabled is False
        assert lesser._meld_gate.enabled is False
        controller.enable_all()
        assert conduit_normal._meld_gate.enabled is True
        assert lesser._meld_gate.enabled is True
    finally:
        lesser.cleanup()


def test_meld_gate_ticket_tracking_success(conduit_normal: Conduit) -> None:
    """
    Verify meld ticket tracking clears after successful meld calls.

    Contract:
        - A meld call registers and unregisters a ticket.
        - active_ticket_count returns to zero after completion.
    """
    conduit_normal._meld.meld = MagicMock(return_value="ok")
    result = conduit_normal.meld(spell="spell-id")
    assert result == "ok"
    assert conduit_normal._meld_gate.active_ticket_count() == 0


def test_meld_gate_ticket_tracking_exception(conduit_normal: Conduit) -> None:
    """
    Verify meld ticket tracking clears after exceptions.

    Contract:
        - active_ticket_count returns to zero after a failing meld call.
    """
    conduit_normal._meld.meld = MagicMock(side_effect=RuntimeError("boom"))
    with pytest.raises(RuntimeError, match="boom"):
        conduit_normal.meld(spell="spell-id")
    assert conduit_normal._meld_gate.active_ticket_count() == 0


def test_meld_gate_controller_active_thread_counts(
    conduit_normal: Conduit,
) -> None:
    """
    Verify active ticket counts are reported by the controller.

    Contract:
        - count_active_threads reports per-gate active ticket counts.
        - count_active_threads_lineage sums across registered gates.
    """
    controller = conduit_normal._meld_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        conduit_normal._meld_gate.register_ticket()
        lesser._meld_gate.register_ticket()
        assert controller.count_active_threads(conduit_normal._id) == 1
        assert controller.count_active_threads(lesser._id) == 1
        assert controller.count_active_threads_lineage() == 2
    finally:
        conduit_normal._meld_gate.unregister_ticket()
        lesser._meld_gate.unregister_ticket()
        lesser.cleanup()


def test_meld_gate_controller_close_and_wait(
    conduit_normal: Conduit,
) -> None:
    """
    Verify close_and_wait_until_free blocks until active tickets drain.

    Contract:
        - Closing a gate waits until its tickets are released.
        - Subsequent meld calls raise when the gate is closed.
    """
    controller = conduit_normal._meld_gate_controller
    assert controller is not None
    conduit_normal._meld_gate.register_ticket()
    closed = threading.Event()

    def _close_gate() -> None:
        controller.close_and_wait_until_free(conduit_normal._id)
        closed.set()

    thread = threading.Thread(target=_close_gate)
    thread.start()
    assert closed.is_set() is False
    conduit_normal._meld_gate.unregister_ticket()
    thread.join(timeout=1)
    assert closed.is_set() is True
    with pytest.raises(RuntimeError, match="MeldGate is closed"):
        conduit_normal.meld(spell="spell-id")
