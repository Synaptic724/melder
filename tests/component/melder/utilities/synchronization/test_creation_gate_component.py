from __future__ import annotations

import threading
from unittest.mock import MagicMock

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.configuration.configuration import Configuration
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbook import Spellbook
from melder.utilities.synchronization.creation_gate import CreationGate
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)
from tests.mocks.spellbook.core_classes import BasicService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_creation_gate_component_tests() -> None:
    """
    Purpose:
        Keep component tests isolated from shared Aether singleton state.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_dynamic_spellbook() -> Spellbook:
    """
    Purpose:
        Build a dynamic Spellbook configured for deterministic component tests.
    """
    configuration = Configuration()
    configuration.dynamic_defaults()
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(configuration=configuration)


def test_component_creation_gate_controller_drains_conduit_gate() -> None:
    """
    Purpose:
        Verify controller conduit drain waits for active ticket release.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    registered = threading.Event()
    release = threading.Event()
    drained = threading.Event()

    def _holder() -> None:
        gate.register_ticket()
        registered.set()
        release.wait(timeout=2.0)
        gate.unregister_ticket()

    def _drainer() -> None:
        controller.close_and_wait_until_conduit_free("c1", timeout=2.0, interval=0.01)
        drained.set()

    holder = threading.Thread(target=_holder, daemon=True)
    drainer = threading.Thread(target=_drainer, daemon=True)
    holder.start()
    assert registered.wait(timeout=1.0) is True
    drainer.start()
    assert drained.wait(timeout=0.05) is False
    release.set()
    assert drained.wait(timeout=1.0) is True
    holder.join(timeout=1.0)
    drainer.join(timeout=1.0)


def test_component_creation_gate_controller_drains_spell_lineage_gate() -> None:
    """
    Purpose:
        Verify controller lineage drain waits for active ticket release.
    """
    controller = CreationGateController()
    gate = controller.create_spell_lineage_gate("l1")
    registered = threading.Event()
    release = threading.Event()
    drained = threading.Event()

    def _holder() -> None:
        gate.register_ticket()
        registered.set()
        release.wait(timeout=2.0)
        gate.unregister_ticket()

    def _drainer() -> None:
        controller.close_and_wait_until_spell_lineage_free("l1", timeout=2.0, interval=0.01)
        drained.set()

    holder = threading.Thread(target=_holder, daemon=True)
    drainer = threading.Thread(target=_drainer, daemon=True)
    holder.start()
    assert registered.wait(timeout=1.0) is True
    drainer.start()
    assert drained.wait(timeout=0.05) is False
    release.set()
    assert drained.wait(timeout=1.0) is True
    holder.join(timeout=1.0)
    drainer.join(timeout=1.0)


def test_component_creation_gate_controller_disable_enable_conduit_waiters_resume() -> None:
    """
    Purpose:
        Verify disable/enable broadcasts release blocked conduit waiters.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    gate.close()
    released = threading.Event()

    def _waiter() -> None:
        gate.wait()
        released.set()

    waiter = threading.Thread(target=_waiter, daemon=True)
    waiter.start()
    assert released.wait(timeout=0.05) is False
    controller.enable_all_conduit_gates()
    assert released.wait(timeout=1.0) is True
    waiter.join(timeout=1.0)


def test_component_creation_gate_controller_disable_enable_lineage_waiters_resume() -> None:
    """
    Purpose:
        Verify disable/enable broadcasts release blocked lineage waiters.
    """
    controller = CreationGateController()
    gate = controller.create_spell_lineage_gate("l1")
    gate.close()
    released = threading.Event()

    def _waiter() -> None:
        gate.wait()
        released.set()

    waiter = threading.Thread(target=_waiter, daemon=True)
    waiter.start()
    assert released.wait(timeout=0.05) is False
    controller.enable_all_spell_lineage_gates()
    assert released.wait(timeout=1.0) is True
    waiter.join(timeout=1.0)


def test_component_creation_gate_controller_disable_enable_all_both_registries() -> None:
    """
    Purpose:
        Verify global disable/enable touches conduit and lineage gates.
    """
    controller = CreationGateController()
    conduit_gate = controller.create_conduit_gate("c1")
    lineage_gate = controller.create_spell_lineage_gate("l1")
    controller.disable_all()
    assert conduit_gate.enabled is False
    assert lineage_gate.enabled is False
    controller.enable_all()
    assert conduit_gate.enabled is True
    assert lineage_gate.enabled is True


def test_component_creation_gate_controller_total_counts_live_tickets() -> None:
    """
    Purpose:
        Verify total ticket count reflects live tickets across registries.
    """
    controller = CreationGateController()
    conduit_gate = controller.create_conduit_gate("c1")
    lineage_gate = controller.create_spell_lineage_gate("l1")
    conduit_gate.register_ticket()
    lineage_gate.register_ticket()
    try:
        assert controller.count_active_threads_total() == 2
        assert controller.count_active_threads_for_conduit("c1") == 1
        assert controller.count_active_threads_for_spell_lineage("l1") == 1
    finally:
        conduit_gate.unregister_ticket()
        lineage_gate.unregister_ticket()


def test_component_conduit_meld_with_creation_gate_blocks_until_enabled() -> None:
    """
    Purpose:
        Verify Conduit dynamic meld can run with CreationGate swapped in.
    Contract:
        - disable_meld blocks calls while gate is disabled.
        - enable_meld releases blocked calls.
    """
    spellbook = _make_dynamic_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        conduit._creation_gate = CreationGate()
        conduit.disable_meld()
        started = threading.Event()
        finished = threading.Event()
        result: dict[str, object] = {}

        def _worker() -> None:
            started.set()
            result["value"] = conduit.meld(spell=spell_id)
            finished.set()

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        assert started.wait(timeout=0.5) is True
        assert finished.wait(timeout=0.05) is False
        conduit.enable_meld()
        assert finished.wait(timeout=1.0) is True
        assert isinstance(result["value"], BasicService)
        thread.join(timeout=1.0)
    finally:
        conduit.cleanup()


def test_component_conduit_meld_with_creation_gate_terminal_close_raises() -> None:
    """
    Purpose:
        Verify Conduit meld rejects calls when swapped CreationGate is terminally closed.
    """
    spellbook = _make_dynamic_spellbook()
    spell_id = spellbook.bind(
        spell=BasicService,
        existence=Existence.unique,
        permissions="create",
    )
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        conduit._creation_gate = CreationGate()
        conduit._creation_gate.close_and_wait_until_free(timeout=0.1, interval=0.01)
        with pytest.raises(RuntimeError, match="CreationGate is closed"):
            conduit.meld(spell=spell_id)
    finally:
        conduit.cleanup()


def test_component_conduit_meld_with_creation_gate_ticket_tracking_success() -> None:
    """
    Purpose:
        Verify ticket tracking returns to zero after successful meld call.
    """
    spellbook = _make_dynamic_spellbook()
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        conduit._creation_gate = CreationGate()
        conduit._meld.meld = MagicMock(return_value="ok")
        result = conduit.meld(spell="spell-id")
        assert result == "ok"
        assert conduit._creation_gate.active_ticket_count() == 0
    finally:
        conduit.cleanup()


def test_component_conduit_meld_with_creation_gate_ticket_tracking_exception() -> None:
    """
    Purpose:
        Verify ticket tracking returns to zero after failing meld call.
    """
    spellbook = _make_dynamic_spellbook()
    conduit = spellbook.conjure(name="root", automatic=False)
    try:
        conduit._creation_gate = CreationGate()
        conduit._meld.meld = MagicMock(side_effect=RuntimeError("boom"))
        with pytest.raises(RuntimeError, match="boom"):
            conduit.meld(spell="spell-id")
        assert conduit._creation_gate.active_ticket_count() == 0
    finally:
        conduit.cleanup()

