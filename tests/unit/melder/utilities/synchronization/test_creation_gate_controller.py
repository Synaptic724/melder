import threading
from typing import Any

import pytest

from melder.utilities.synchronization.creation_gate import CreationGate
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


def test_creation_gate_controller_initial_state() -> None:
    """
    Purpose:
        Verify controller starts with empty dual registries.
    """
    controller = CreationGateController()
    assert controller._conduit_creation_gates == {}
    assert controller._spell_lineage_creation_gates == {}


def test_creation_gate_controller_cleanup_clears_registries() -> None:
    """
    Purpose:
        Verify cleanup clears both conduit and spell-lineage maps.
    """
    controller = CreationGateController()
    controller.create_conduit_gate("c1")
    controller.create_spell_lineage_gate("l1")
    controller.cleanup()
    assert controller._conduit_creation_gates == {}
    assert controller._spell_lineage_creation_gates == {}


def test_creation_gate_controller_cleanup_idempotent() -> None:
    """
    Purpose:
        Verify repeated cleanup does not fail.
    """
    controller = CreationGateController()
    controller.cleanup()
    controller.cleanup()
    assert controller._cleaned is True


def test_create_conduit_gate_success() -> None:
    """
    Purpose:
        Verify conduit gate creation and registry storage.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    assert isinstance(gate, CreationGate)
    assert controller.get_conduit_gate("c1") is gate


@pytest.mark.parametrize("conduit_id", ["", None])
def test_create_conduit_gate_empty_raises(conduit_id: Any) -> None:
    """
    Purpose:
        Ensure empty conduit keys are rejected.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="conduit_id cannot be empty"):
        controller.create_conduit_gate(conduit_id)


def test_create_conduit_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate conduit key registration fails.
    """
    controller = CreationGateController()
    controller.create_conduit_gate("c1")
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.create_conduit_gate("c1")


def test_register_conduit_gate_success() -> None:
    """
    Purpose:
        Verify explicit conduit gate registration.
    """
    controller = CreationGateController()
    gate = CreationGate()
    controller.register_conduit_gate("c1", gate)
    assert controller.get_conduit_gate("c1") is gate


@pytest.mark.parametrize("conduit_id", ["", None])
def test_register_conduit_gate_empty_raises(conduit_id: Any) -> None:
    """
    Purpose:
        Ensure empty conduit keys are rejected on register.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="conduit_id cannot be empty"):
        controller.register_conduit_gate(conduit_id, CreationGate())


def test_register_conduit_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate conduit registration is rejected.
    """
    controller = CreationGateController()
    controller.register_conduit_gate("c1", CreationGate())
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.register_conduit_gate("c1", CreationGate())


def test_unregister_conduit_gate_missing_is_noop() -> None:
    """
    Purpose:
        Verify missing conduit unregistration is a no-op.
    """
    controller = CreationGateController()
    controller.unregister_conduit_gate("missing")
    assert controller.get_conduit_gate("missing") is None


def test_get_conduit_gate_missing_returns_none() -> None:
    """
    Purpose:
        Verify missing conduit lookup returns None.
    """
    controller = CreationGateController()
    assert controller.get_conduit_gate("missing") is None


def test_count_active_threads_for_conduit_missing_returns_zero() -> None:
    """
    Purpose:
        Verify missing conduit count returns zero.
    """
    controller = CreationGateController()
    assert controller.count_active_threads_for_conduit("missing") == 0


def test_count_active_threads_conduits_sums_registry() -> None:
    """
    Purpose:
        Verify conduit aggregate count sums all conduit gates.
    """
    controller = CreationGateController()
    g1 = controller.create_conduit_gate("c1")
    g2 = controller.create_conduit_gate("c2")
    g1.register_ticket()
    g2.register_ticket()
    g2.register_ticket()
    try:
        assert controller.count_active_threads_conduits() == 3
    finally:
        g1.unregister_ticket()
        g2.unregister_ticket()
        g2.unregister_ticket()


def test_close_and_wait_until_conduit_free_missing_is_noop() -> None:
    """
    Purpose:
        Verify close-and-drain on missing conduit key is no-op.
    """
    controller = CreationGateController()
    controller.close_and_wait_until_conduit_free("missing", timeout=0.01, interval=0.001)


def test_close_and_wait_until_conduit_free_drains_tickets() -> None:
    """
    Purpose:
        Verify conduit close-and-drain waits until tickets are released.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    registered = threading.Event()
    release = threading.Event()

    def _worker() -> None:
        gate.register_ticket()
        registered.set()
        release.wait(timeout=1.0)
        gate.unregister_ticket()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    assert registered.wait(timeout=1.0) is True

    closer_done = threading.Event()

    def _close() -> None:
        controller.close_and_wait_until_conduit_free("c1", timeout=2.0, interval=0.01)
        closer_done.set()

    closer = threading.Thread(target=_close, daemon=True)
    closer.start()
    assert closer_done.wait(timeout=0.05) is False
    release.set()
    assert closer_done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    closer.join(timeout=1.0)
    assert gate.is_closed() is True


def test_enable_all_conduit_gates_opens_all() -> None:
    """
    Purpose:
        Verify conduit-wide enable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_conduit_gate("c1")
    g2 = controller.create_conduit_gate("c2")
    g1.close()
    g2.close()
    controller.enable_all_conduit_gates()
    assert g1.enabled is True
    assert g2.enabled is True


def test_disable_all_conduit_gates_closes_all() -> None:
    """
    Purpose:
        Verify conduit-wide disable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_conduit_gate("c1")
    g2 = controller.create_conduit_gate("c2")
    controller.disable_all_conduit_gates()
    assert g1.enabled is False
    assert g2.enabled is False


def test_create_spell_lineage_gate_success() -> None:
    """
    Purpose:
        Verify spell-lineage gate creation and registry storage.
    """
    controller = CreationGateController()
    gate = controller.create_spell_lineage_gate("l1")
    assert isinstance(gate, CreationGate)
    assert controller.get_spell_lineage_gate("l1") is gate


@pytest.mark.parametrize("lineage_id", ["", None])
def test_create_spell_lineage_gate_empty_raises(lineage_id: Any) -> None:
    """
    Purpose:
        Ensure empty lineage keys are rejected.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="lineage_id cannot be empty"):
        controller.create_spell_lineage_gate(lineage_id)


def test_create_spell_lineage_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate lineage registration fails.
    """
    controller = CreationGateController()
    controller.create_spell_lineage_gate("l1")
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.create_spell_lineage_gate("l1")


def test_register_spell_lineage_gate_success() -> None:
    """
    Purpose:
        Verify explicit spell-lineage gate registration.
    """
    controller = CreationGateController()
    gate = CreationGate()
    controller.register_spell_lineage_gate("l1", gate)
    assert controller.get_spell_lineage_gate("l1") is gate


@pytest.mark.parametrize("lineage_id", ["", None])
def test_register_spell_lineage_gate_empty_raises(lineage_id: Any) -> None:
    """
    Purpose:
        Ensure empty lineage keys are rejected on register.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="lineage_id cannot be empty"):
        controller.register_spell_lineage_gate(lineage_id, CreationGate())


def test_register_spell_lineage_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate lineage registration is rejected.
    """
    controller = CreationGateController()
    controller.register_spell_lineage_gate("l1", CreationGate())
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.register_spell_lineage_gate("l1", CreationGate())


def test_unregister_spell_lineage_gate_missing_is_noop() -> None:
    """
    Purpose:
        Verify missing lineage unregistration is a no-op.
    """
    controller = CreationGateController()
    controller.unregister_spell_lineage_gate("missing")
    assert controller.get_spell_lineage_gate("missing") is None


def test_get_spell_lineage_gate_missing_returns_none() -> None:
    """
    Purpose:
        Verify missing lineage lookup returns None.
    """
    controller = CreationGateController()
    assert controller.get_spell_lineage_gate("missing") is None


def test_count_active_threads_for_spell_lineage_missing_returns_zero() -> None:
    """
    Purpose:
        Verify missing lineage count returns zero.
    """
    controller = CreationGateController()
    assert controller.count_active_threads_for_spell_lineage("missing") == 0


def test_count_active_threads_spell_lineages_sums_registry() -> None:
    """
    Purpose:
        Verify lineage aggregate count sums all lineage gates.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_lineage_gate("l1")
    g2 = controller.create_spell_lineage_gate("l2")
    g1.register_ticket()
    g2.register_ticket()
    try:
        assert controller.count_active_threads_spell_lineages() == 2
    finally:
        g1.unregister_ticket()
        g2.unregister_ticket()


def test_close_and_wait_until_spell_lineage_free_missing_is_noop() -> None:
    """
    Purpose:
        Verify close-and-drain on missing lineage key is no-op.
    """
    controller = CreationGateController()
    controller.close_and_wait_until_spell_lineage_free(
        "missing",
        timeout=0.01,
        interval=0.001,
    )


def test_close_and_wait_until_spell_lineage_free_drains_tickets() -> None:
    """
    Purpose:
        Verify lineage close-and-drain waits until tickets are released.
    """
    controller = CreationGateController()
    gate = controller.create_spell_lineage_gate("l1")
    registered = threading.Event()
    release = threading.Event()

    def _worker() -> None:
        gate.register_ticket()
        registered.set()
        release.wait(timeout=1.0)
        gate.unregister_ticket()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    assert registered.wait(timeout=1.0) is True

    closer_done = threading.Event()

    def _close() -> None:
        controller.close_and_wait_until_spell_lineage_free(
            "l1",
            timeout=2.0,
            interval=0.01,
        )
        closer_done.set()

    closer = threading.Thread(target=_close, daemon=True)
    closer.start()
    assert closer_done.wait(timeout=0.05) is False
    release.set()
    assert closer_done.wait(timeout=1.0) is True
    thread.join(timeout=1.0)
    closer.join(timeout=1.0)
    assert gate.is_closed() is True


def test_enable_all_spell_lineage_gates_opens_all() -> None:
    """
    Purpose:
        Verify lineage-wide enable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_lineage_gate("l1")
    g2 = controller.create_spell_lineage_gate("l2")
    g1.close()
    g2.close()
    controller.enable_all_spell_lineage_gates()
    assert g1.enabled is True
    assert g2.enabled is True


def test_disable_all_spell_lineage_gates_closes_all() -> None:
    """
    Purpose:
        Verify lineage-wide disable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_lineage_gate("l1")
    g2 = controller.create_spell_lineage_gate("l2")
    controller.disable_all_spell_lineage_gates()
    assert g1.enabled is False
    assert g2.enabled is False


def test_count_active_threads_total_sums_both_registries() -> None:
    """
    Purpose:
        Verify total active count combines conduit and lineage maps.
    """
    controller = CreationGateController()
    cg = controller.create_conduit_gate("c1")
    lg = controller.create_spell_lineage_gate("l1")
    cg.register_ticket()
    lg.register_ticket()
    try:
        assert controller.count_active_threads_total() == 2
    finally:
        cg.unregister_ticket()
        lg.unregister_ticket()


def test_enable_all_opens_both_registries() -> None:
    """
    Purpose:
        Verify global enable broadcast touches both registries.
    """
    controller = CreationGateController()
    cg = controller.create_conduit_gate("c1")
    lg = controller.create_spell_lineage_gate("l1")
    cg.close()
    lg.close()
    controller.enable_all()
    assert cg.enabled is True
    assert lg.enabled is True


def test_disable_all_closes_both_registries() -> None:
    """
    Purpose:
        Verify global disable broadcast touches both registries.
    """
    controller = CreationGateController()
    cg = controller.create_conduit_gate("c1")
    lg = controller.create_spell_lineage_gate("l1")
    controller.disable_all()
    assert cg.enabled is False
    assert lg.enabled is False


def test_create_gate_alias_uses_conduit_registry() -> None:
    """
    Purpose:
        Verify compatibility alias create_gate maps to conduit registry.
    """
    controller = CreationGateController()
    gate = controller.create_gate("c1")
    assert controller.get_conduit_gate("c1") is gate


def test_register_gate_alias_uses_conduit_registry() -> None:
    """
    Purpose:
        Verify compatibility alias register_gate maps to conduit registry.
    """
    controller = CreationGateController()
    gate = CreationGate()
    controller.register_gate("c1", gate)
    assert controller.get_conduit_gate("c1") is gate


def test_get_gate_alias_reads_conduit_registry() -> None:
    """
    Purpose:
        Verify compatibility alias get_gate maps to conduit lookup.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    assert controller.get_gate("c1") is gate


def test_count_active_threads_alias_reads_conduit_registry() -> None:
    """
    Purpose:
        Verify compatibility alias count_active_threads maps to conduit count.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    gate.register_ticket()
    try:
        assert controller.count_active_threads("c1") == 1
    finally:
        gate.unregister_ticket()


def test_count_active_threads_lineage_alias_sums_conduit_registry_only() -> None:
    """
    Purpose:
        Verify conduit-compat aggregate alias excludes lineage registry.
    """
    controller = CreationGateController()
    conduit_gate = controller.create_conduit_gate("c1")
    lineage_gate = controller.create_spell_lineage_gate("l1")
    conduit_gate.register_ticket()
    lineage_gate.register_ticket()
    try:
        assert controller.count_active_threads_lineage() == 1
    finally:
        conduit_gate.unregister_ticket()
        lineage_gate.unregister_ticket()


def test_close_and_wait_until_free_alias_drains_conduit_gate() -> None:
    """
    Purpose:
        Verify compatibility alias close_and_wait_until_free maps to conduit gate.
    """
    controller = CreationGateController()
    gate = controller.create_conduit_gate("c1")
    gate.register_ticket()

    def _release() -> None:
        gate.unregister_ticket()

    releaser = threading.Timer(0.05, _release)
    releaser.start()
    controller.close_and_wait_until_free("c1", timeout=1.0, interval=0.01)
    releaser.cancel()
    assert gate.is_closed() is True


def test_unregister_gate_alias_removes_conduit_gate() -> None:
    """
    Purpose:
        Verify compatibility alias unregister_gate removes conduit entry.
    """
    controller = CreationGateController()
    controller.create_gate("c1")
    controller.unregister_gate("c1")
    assert controller.get_conduit_gate("c1") is None


@pytest.mark.parametrize(
    "method_name,args",
    [
        ("create_conduit_gate", ("c1",)),
        ("register_conduit_gate", ("c1", CreationGate())),
        ("unregister_conduit_gate", ("c1",)),
        ("get_conduit_gate", ("c1",)),
        ("count_active_threads_for_conduit", ("c1",)),
        ("count_active_threads_conduits", ()),
        ("create_spell_lineage_gate", ("l1",)),
        ("register_spell_lineage_gate", ("l1", CreationGate())),
        ("unregister_spell_lineage_gate", ("l1",)),
        ("get_spell_lineage_gate", ("l1",)),
        ("count_active_threads_for_spell_lineage", ("l1",)),
        ("count_active_threads_spell_lineages", ()),
        ("count_active_threads_total", ()),
        ("enable_all", ()),
        ("disable_all", ()),
        ("create_gate", ("c1",)),
        ("register_gate", ("c1", CreationGate())),
        ("get_gate", ("c1",)),
        ("count_active_threads", ("c1",)),
        ("count_active_threads_lineage", ()),
        ("close_and_wait_until_free", ("c1",)),
    ],
)
def test_creation_gate_controller_methods_raise_after_cleanup(
    method_name: str,
    args: tuple[Any, ...],
) -> None:
    """
    Purpose:
        Ensure public methods enforce cleaned guard after cleanup.
    """
    controller = CreationGateController()
    controller.cleanup()
    method = getattr(controller, method_name)
    with pytest.raises(RuntimeError, match="CreationGateController has already been cleaned"):
        method(*args)

