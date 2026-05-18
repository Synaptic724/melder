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
    assert controller._spell_index_creation_gates == {}


def test_creation_gate_controller_cleanup_clears_registries() -> None:
    """
    Purpose:
        Verify cleanup clears both conduit and spell-index maps.
    """
    controller = CreationGateController()
    controller.create_conduit_gate("c1")
    controller.create_spell_index_gate("i1")
    controller.cleanup()
    assert not hasattr(controller, '_conduit_creation_gates')
    assert not hasattr(controller, '_spell_index_creation_gates')
    assert not hasattr(controller, '_conduit_creation_gates_by_root')
    assert not hasattr(controller, '_conduit_root_by_conduit')
    assert not hasattr(controller, '_lock')


def test_creation_gate_controller_cleanup_cleans_registered_gates() -> None:
    """
    Purpose:
        Verify cleanup cascades into all registered conduit/index gates.
    """
    controller = CreationGateController()
    conduit_gate = controller.create_conduit_gate("c1")
    index_gate = controller.create_spell_index_gate("i1")

    controller.cleanup()

    with pytest.raises(RuntimeError, match="CreationGate has already been cleaned"):
        conduit_gate.open()
    with pytest.raises(RuntimeError, match="CreationGate has already been cleaned"):
        index_gate.open()


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


def test_conduit_root_index_maps_lineage_members() -> None:
    """
    Purpose:
        Verify root->conduit index and reverse conduit->root index are tracked.
    """
    controller = CreationGateController()
    controller.create_conduit_gate("c1", root_conduit_id="root-1")
    controller.create_conduit_gate("c2", root_conduit_id="root-1")
    assert controller.get_root_conduit_id_for_conduit("c1") == "root-1"
    assert controller.get_root_conduit_id_for_conduit("c2") == "root-1"
    lineage = controller.get_conduit_lineage_gates("root-1")
    assert set(lineage.keys()) == {"c1", "c2"}


def test_conduit_root_index_lineage_count_uses_root_map() -> None:
    """
    Purpose:
        Verify root-scoped active count sums only one lineage map.
    """
    controller = CreationGateController()
    g1 = controller.create_conduit_gate("c1", root_conduit_id="root-1")
    g2 = controller.create_conduit_gate("c2", root_conduit_id="root-1")
    g3 = controller.create_conduit_gate("c3", root_conduit_id="root-2")
    g1.register_ticket()
    g2.register_ticket()
    g3.register_ticket()
    try:
        assert controller.count_active_threads_for_conduit_lineage("root-1") == 2
        assert controller.count_active_threads_for_conduit_lineage("root-2") == 1
    finally:
        g1.unregister_ticket()
        g2.unregister_ticket()
        g3.unregister_ticket()


def test_unregister_conduit_gate_prunes_empty_root_bucket() -> None:
    """
    Purpose:
        Verify removing last conduit under a root deletes the root bucket.
    """
    controller = CreationGateController()
    controller.create_conduit_gate("c1", root_conduit_id="root-1")
    controller.unregister_conduit_gate("c1")
    assert controller.get_conduit_lineage_gates("root-1") == {}


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


def test_close_and_wait_until_conduit_lineage_free_missing_is_noop() -> None:
    """
    Purpose:
        Verify close-and-drain on missing conduit lineage key is no-op.
    """
    controller = CreationGateController()
    controller.close_and_wait_until_conduit_lineage_free(
        "missing",
        timeout=0.01,
        interval=0.001,
    )


def test_close_and_wait_until_conduit_lineage_free_drains_tickets() -> None:
    """
    Purpose:
        Verify lineage close-and-drain waits until all lineage tickets release.
    """
    controller = CreationGateController()
    gate_one = controller.create_conduit_gate("c1", root_conduit_id="root-1")
    gate_two = controller.create_conduit_gate("c2", root_conduit_id="root-1")
    registered = threading.Event()
    release = threading.Event()

    def _worker() -> None:
        gate_one.register_ticket()
        registered.set()
        release.wait(timeout=1.0)
        gate_one.unregister_ticket()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    assert registered.wait(timeout=1.0) is True

    closer_done = threading.Event()

    def _close() -> None:
        controller.close_and_wait_until_conduit_lineage_free(
            "root-1",
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
    assert gate_one.is_closed() is True
    assert gate_two.is_closed() is True


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


def test_create_spell_index_gate_success() -> None:
    """
    Purpose:
        Verify spell-index gate creation and registry storage.
    """
    controller = CreationGateController()
    gate = controller.create_spell_index_gate("i1")
    assert isinstance(gate, CreationGate)
    assert controller.get_spell_index_gate("i1") is gate


@pytest.mark.parametrize("index_id", ["", None])
def test_create_spell_index_gate_empty_raises(index_id: Any) -> None:
    """
    Purpose:
        Ensure empty spell-index keys are rejected.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="index_id cannot be empty"):
        controller.create_spell_index_gate(index_id)


def test_create_spell_index_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate spell-index registration fails.
    """
    controller = CreationGateController()
    controller.create_spell_index_gate("i1")
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.create_spell_index_gate("i1")


def test_register_spell_index_gate_success() -> None:
    """
    Purpose:
        Verify explicit spell-index gate registration.
    """
    controller = CreationGateController()
    gate = CreationGate()
    controller.register_spell_index_gate("i1", gate)
    assert controller.get_spell_index_gate("i1") is gate


@pytest.mark.parametrize("index_id", ["", None])
def test_register_spell_index_gate_empty_raises(index_id: Any) -> None:
    """
    Purpose:
        Ensure empty spell-index keys are rejected on register.
    """
    controller = CreationGateController()
    with pytest.raises(ValueError, match="index_id cannot be empty"):
        controller.register_spell_index_gate(index_id, CreationGate())


def test_register_spell_index_gate_duplicate_raises() -> None:
    """
    Purpose:
        Ensure duplicate spell-index registration is rejected.
    """
    controller = CreationGateController()
    controller.register_spell_index_gate("i1", CreationGate())
    with pytest.raises(ValueError, match="CreationGate already registered"):
        controller.register_spell_index_gate("i1", CreationGate())


def test_unregister_spell_index_gate_missing_is_noop() -> None:
    """
    Purpose:
        Verify missing spell-index unregistration is a no-op.
    """
    controller = CreationGateController()
    controller.unregister_spell_index_gate("missing")
    assert controller.get_spell_index_gate("missing") is None


def test_get_spell_index_gate_missing_returns_none() -> None:
    """
    Purpose:
        Verify missing spell-index lookup returns None.
    """
    controller = CreationGateController()
    assert controller.get_spell_index_gate("missing") is None


def test_count_active_threads_for_spell_index_missing_returns_zero() -> None:
    """
    Purpose:
        Verify missing spell-index count returns zero.
    """
    controller = CreationGateController()
    assert controller.count_active_threads_for_spell_index("missing") == 0


def test_count_active_threads_spell_indexes_sums_registry() -> None:
    """
    Purpose:
        Verify spell-index aggregate count sums all spell-index gates.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_index_gate("i1")
    g2 = controller.create_spell_index_gate("i2")
    g1.register_ticket()
    g2.register_ticket()
    try:
        assert controller.count_active_threads_spell_indexes() == 2
    finally:
        g1.unregister_ticket()
        g2.unregister_ticket()


def test_close_and_wait_until_spell_index_free_missing_is_noop() -> None:
    """
    Purpose:
        Verify close-and-drain on missing spell-index key is no-op.
    """
    controller = CreationGateController()
    controller.close_and_wait_until_spell_index_free(
        "missing",
        timeout=0.01,
        interval=0.001,
    )


def test_close_and_wait_until_spell_index_free_drains_tickets() -> None:
    """
    Purpose:
        Verify spell-index close-and-drain waits until tickets are released.
    """
    controller = CreationGateController()
    gate = controller.create_spell_index_gate("i1")
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
        controller.close_and_wait_until_spell_index_free(
            "i1",
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


def test_enable_all_spell_index_gates_opens_all() -> None:
    """
    Purpose:
        Verify spell-index-wide enable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_index_gate("i1")
    g2 = controller.create_spell_index_gate("i2")
    g1.close()
    g2.close()
    controller.enable_all_spell_index_gates()
    assert g1.enabled is True
    assert g2.enabled is True


def test_disable_all_spell_index_gates_closes_all() -> None:
    """
    Purpose:
        Verify spell-index-wide disable broadcast.
    """
    controller = CreationGateController()
    g1 = controller.create_spell_index_gate("i1")
    g2 = controller.create_spell_index_gate("i2")
    controller.disable_all_spell_index_gates()
    assert g1.enabled is False
    assert g2.enabled is False


def test_count_active_threads_total_sums_both_registries() -> None:
    """
    Purpose:
        Verify total active count combines conduit and spell-index maps.
    """
    controller = CreationGateController()
    cg = controller.create_conduit_gate("c1")
    lg = controller.create_spell_index_gate("i1")
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
    lg = controller.create_spell_index_gate("i1")
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
    lg = controller.create_spell_index_gate("i1")
    controller.disable_all()
    assert cg.enabled is False
    assert lg.enabled is False


@pytest.mark.parametrize(
    "method_name,args",
    [
        ("create_conduit_gate", ("c1",)),
        ("register_conduit_gate", ("c1", CreationGate())),
        ("unregister_conduit_gate", ("c1",)),
        ("get_conduit_gate", ("c1",)),
        ("count_active_threads_for_conduit", ("c1",)),
        ("count_active_threads_conduits", ()),
        ("get_root_conduit_id_for_conduit", ("c1",)),
        ("get_conduit_lineage_gates", ("root-1",)),
        ("count_active_threads_for_conduit_lineage", ("root-1",)),
        ("create_spell_index_gate", ("i1",)),
        ("register_spell_index_gate", ("i1", CreationGate())),
        ("unregister_spell_index_gate", ("i1",)),
        ("get_spell_index_gate", ("i1",)),
        ("count_active_threads_for_spell_index", ("i1",)),
        ("count_active_threads_spell_indexes", ()),
        ("count_active_threads_total", ()),
        ("enable_all", ()),
        ("disable_all", ()),
        ("close_and_wait_until_conduit_free", ("c1",)),
        ("close_and_wait_until_conduit_lineage_free", ("root-1",)),
        ("close_and_wait_until_spell_index_free", ("i1",)),
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

