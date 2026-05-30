import threading
from unittest.mock import MagicMock

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.meld.conduit_meld import ConduitMeld
from melder.aether.conduit.meld.meld import Meld


def test_creation_gate_controller_registers_normal_gate(conduit_normal: Conduit) -> None:
    """
    Verify normal conduits register their CreationGate with the controller.

    Contract:
        - The controller exists for a normal conduit.
        - The controller registry returns the same gate instance.
        - The gate starts with no active tickets.
    """
    controller = conduit_normal._creation_gate_controller
    assert controller is not None
    gate = controller.get_conduit_gate(conduit_normal._id)
    assert gate is conduit_normal._creation_gate
    assert gate.has_active_tickets() is False


def test_creation_gate_controller_registers_lesser_gate(
    conduit_normal: Conduit,
) -> None:
    """
    Verify lesser conduits register their own CreationGate in the controller.

    Contract:
        - The lesser conduit has a distinct gate from the normal conduit.
        - Both gates are registered in the controller registry.
    """
    controller = conduit_normal._creation_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        normal_gate = controller.get_conduit_gate(conduit_normal._id)
        lesser_gate = controller.get_conduit_gate(lesser._id)
        assert normal_gate is conduit_normal._creation_gate
        assert lesser_gate is lesser._creation_gate
        assert normal_gate is not lesser_gate
    finally:
        lesser.cleanup()


def test_creation_gate_controller_disable_all(
    conduit_normal: Conduit,
) -> None:
    """
    Verify the controller can disable all registered meld gates.

    Contract:
        - disable_all() sets enabled=False on every registered gate.
        - enable_all() restores enabled=True.
    """
    controller = conduit_normal._creation_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        controller.disable_all()
        assert conduit_normal._creation_gate.enabled is False
        assert lesser._creation_gate.enabled is False
        controller.enable_all()
        assert conduit_normal._creation_gate.enabled is True
        assert lesser._creation_gate.enabled is True
    finally:
        lesser.cleanup()


def test_creation_gate_ticket_tracking_success(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify meld ticket tracking clears after successful meld calls.

    Contract:
        - A meld call registers and unregisters a ticket.
        - active_ticket_count returns to zero after completion.
    """
    meld_mock = MagicMock(return_value="ok")
    monkeypatch.setattr(ConduitMeld, "meld", lambda self, *args, **kwargs: meld_mock(*args, **kwargs))
    result = conduit_dynamic_normal.meld(spell="spell-id")
    assert result == "ok"
    assert conduit_dynamic_normal._creation_gate.active_ticket_count() == 0


def test_creation_gate_ticket_tracking_exception(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify meld ticket tracking clears after exceptions.

    Contract:
        - active_ticket_count returns to zero after a failing meld call.
    """
    meld_mock = MagicMock(side_effect=RuntimeError("boom"))
    monkeypatch.setattr(ConduitMeld, "meld", lambda self, *args, **kwargs: meld_mock(*args, **kwargs))
    with pytest.raises(RuntimeError, match="boom"):
        conduit_dynamic_normal.meld(spell="spell-id")
    assert conduit_dynamic_normal._creation_gate.active_ticket_count() == 0


def test_creation_gate_controller_active_thread_counts(
    conduit_normal: Conduit,
) -> None:
    """
    Verify active ticket counts are reported by the controller.

    Contract:
        - count_active_threads reports per-gate active ticket counts.
        - count_active_threads_lineage sums across registered gates.
    """
    controller = conduit_normal._creation_gate_controller
    assert controller is not None
    lesser = conduit_normal.create_lesser_conduit()
    try:
        conduit_normal._creation_gate.register_ticket()
        lesser._creation_gate.register_ticket()
        assert controller.count_active_threads_for_conduit(conduit_normal._id) == 1
        assert controller.count_active_threads_for_conduit(lesser._id) == 1
        assert controller.count_active_threads_conduits() == 2
    finally:
        conduit_normal._creation_gate.unregister_ticket()
        lesser._creation_gate.unregister_ticket()
        lesser.cleanup()


def test_creation_gate_controller_close_and_wait(
    conduit_dynamic_normal: Conduit,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify close_and_wait_until_free blocks until active tickets drain.

    Contract:
        - Closing a gate waits until its tickets are released.
        - Subsequent meld calls raise when the gate is closed.
    """
    controller = conduit_dynamic_normal._creation_gate_controller
    assert controller is not None

    ticket_registered = threading.Event()
    allow_release = threading.Event()

    def _ticket_worker() -> None:
        conduit_dynamic_normal._creation_gate.register_ticket()
        ticket_registered.set()
        # Hold the ticket until the main thread has initiated close_and_wait_until_free.
        allow_release.wait(timeout=5)
        conduit_dynamic_normal._creation_gate.unregister_ticket()

    t = threading.Thread(target=_ticket_worker)
    t.start()

    # Ensure the ticket exists *before* we attempt to close and wait.
    assert ticket_registered.wait(timeout=5) is True

    # Now: main thread performs the close+wait.
    # This must block until the worker releases the ticket.
    def _release_later() -> None:
        allow_release.set()

    # Start a tiny helper thread that releases immediately after close starts.
    # (No sleeps; just ordering.)
    releaser = threading.Thread(target=_release_later)
    releaser.start()

    controller.close_and_wait_until_conduit_free(
        conduit_dynamic_normal._id,
        timeout=5.0,
        interval=0.01,
    )

    releaser.join(timeout=1)
    t.join(timeout=1)
    assert not t.is_alive()

    # Verify subsequent meld calls raise when the gate is closed.
    meld_mock = MagicMock(return_value="ok")
    monkeypatch.setattr(ConduitMeld, "meld", lambda self, *args, **kwargs: meld_mock(*args, **kwargs))
    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        conduit_dynamic_normal.meld(spell="spell-id")
