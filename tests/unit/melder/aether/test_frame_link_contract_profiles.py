import pytest
import threading

from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)


def test_frame_link_contract_requires_non_empty_rift_id() -> None:
    """
    Verify frame-link contracts reject empty Rift ids.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        FrameLinkContract(rift_id="")


def test_frame_link_contract_rejects_invalid_assigned_frame_names() -> None:
    """
    Verify frame-link contracts reject invalid assigned frame-name entries.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="assigned_frame_names must contain non-empty strings",
    ):
        FrameLinkContract(rift_id="rift-1", assigned_frame_names=("ops", ""))


def test_frame_link_contract_rejects_default_frame_outside_assignment() -> None:
    """
    Verify the default frame must be present in the assignment set.

    Returns:
        None.
    """
    with pytest.raises(
            ValueError,
            match="default_frame_name must be present in assigned_frame_names",
    ):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            default_frame_name="finance",
        )

    with pytest.raises(ValueError, match="default_frame_name cannot be empty"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            default_frame_name="",
        )


def test_frame_link_contract_rejects_invalid_selected_contract_mapping_inputs() -> None:
    """
    Verify selected-contract mapping validation rejects bad shapes and values.

    Returns:
        None.
    """
    with pytest.raises(TypeError, match="must be a dict when provided"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name=[],
        )

    with pytest.raises(ValueError, match="must be present in assigned_frame_names"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name={"finance": "default"},
        )

    with pytest.raises(ValueError, match="must be non-empty strings"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name={"ops": ""},
        )


def test_frame_link_contract_deduplicates_assigned_frame_names_preserving_order() -> None:
    """
    Verify duplicate assigned frame names are normalized once in order.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "ops", "finance", "ops"),
        default_frame_name="ops",
    )

    assert contract.assigned_frame_names == ("ops", "finance")
    assert contract.default_frame_name == "ops"


def test_frame_link_contract_list_and_has_frame_reflect_current_assignment() -> None:
    """
    Verify frame-list and membership helpers reflect the current assignment set.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    assert contract.list_frame_names() == ["ops", "finance"]
    assert contract.has_frame("ops") is True
    assert contract.has_frame("audit") is False
    assert contract.get_selected_contract_name("ops") == "default"
    assert contract.get_selected_contract_name("finance") == "default"


def test_frame_link_contract_register_frame_can_seed_and_replace_default() -> None:
    """
    Verify registering frames can seed and replace the default frame.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1")

    contract.register_frame("ops")
    contract.register_frame("finance", set_as_default=True, contract_name="ops_contract")

    assert contract.assigned_frame_names == ("ops", "finance")
    assert contract.default_frame_name == "finance"
    assert contract.get_selected_contract_name("ops") == "default"
    assert contract.get_selected_contract_name("finance") == "ops_contract"

    with pytest.raises(ValueError, match="contract_name cannot be empty"):
        contract.register_frame("audit", contract_name="")


def test_frame_link_contract_remove_frame_updates_default_and_ignores_missing() -> None:
    """
    Verify removing frames updates the default and ignores missing names.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    contract.remove_frame("ops")
    contract.remove_frame("missing")

    assert contract.assigned_frame_names == ("finance",)
    assert contract.default_frame_name == "finance"


def test_frame_link_contract_can_update_selected_contract_name_for_assigned_frame() -> None:
    """
    Verify the contract can change the selected ACL contract name per frame.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )

    contract.set_selected_contract_name("ops", "ops_contract")

    assert contract.get_selected_contract_name("ops") == "ops_contract"

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.set_selected_contract_name("", "ops_contract")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.get_selected_contract_name("")

    with pytest.raises(KeyError, match="not assigned on this Rift contract"):
        contract.get_selected_contract_name("finance")

    with pytest.raises(ValueError, match="contract_name cannot be empty"):
        contract.set_selected_contract_name("ops", "")

    with pytest.raises(KeyError, match="not assigned on this Rift contract"):
        contract.set_selected_contract_name("finance", "ops_contract")


def test_frame_link_contract_describe_and_clone_include_selected_contract_names() -> None:
    """
    Verify describe and clone preserve the selected contract-name mapping.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        selected_contract_names_by_frame_name={"ops": "ops_contract"},
    )

    description = contract.describe()
    clone = contract.clone()

    assert description["selected_contract_names_by_frame_name"] == {
        "ops": "ops_contract",
    }
    assert clone.get_selected_contract_name("ops") == "ops_contract"


def test_frame_link_contract_helper_methods_reject_empty_frame_name_inputs() -> None:
    """
    Verify frame helper methods reject empty frame-name inputs.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.has_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.register_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        contract.remove_frame("")


def test_frame_link_contract_clone_detaches_metadata_and_assignment_state() -> None:
    """
    Verify cloned contracts detach the metadata and assignment state.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        metadata={"source": "rift"},
    )

    cloned = contract.clone()
    cloned.register_frame("finance")

    assert cloned is not contract
    assert contract.assigned_frame_names == ("ops",)
    assert cloned.assigned_frame_names == ("ops", "finance")
    assert contract.metadata == {"source": "rift"}


def test_frame_link_contract_describe_summarizes_availability() -> None:
    """
    Verify the contract summary exposes the assigned-frame availability.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    assert contract.describe() == {
        "rift_id": "rift-1",
        "assigned_frame_names": ("ops", "finance"),
        "default_frame_name": "ops",
        "selected_contract_names_by_frame_name": {
            "ops": "default",
            "finance": "default",
        },
        "assigned_frame_count": 2,
    }


def test_frame_link_contract_cleanup_clears_owned_state() -> None:
    """
    Verify frame-link contract cleanup clears owned state.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )

    contract.cleanup()

    assert contract.cleaned is True
    assert contract._assigned_frame_names is None
    assert contract._default_frame_name is None
    assert contract._metadata is None


def test_frame_link_contract_cleanup_rechecks_cleaned_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the contract.

    Returns:
        None.
    """

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )
    coordinated_lock = _CoordinatedLock()
    contract._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        contract.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert contract.cleaned is True
    assert contract._lock is None


def test_frame_link_contract_exposes_identity_and_selected_contract_snapshot() -> None:
    """
    Verify contract identity and selected-contract snapshots are detached.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        selected_contract_names_by_frame_name={"ops": "ops_contract"},
    )

    selected_snapshot = contract.selected_contract_names_by_frame_name
    selected_snapshot["ops"] = "mutated"

    assert contract.contract_id is not None
    assert contract.rift_id == "rift-1"
    assert contract.selected_contract_names_by_frame_name == {"ops": "ops_contract"}


def test_frame_link_contract_cleanup_is_idempotent_inside_lock() -> None:
    """
    Verify cleanup returns early when another thread already cleaned the contract.

    Returns:
        None.
    """
    import threading

    class _CoordinatedLock:
        def __init__(self) -> None:
            self._entered_first = threading.Event()
            self._second_attempted = threading.Event()
            self._lock = threading.RLock()

        def __enter__(self):
            if self._entered_first.is_set():
                self._second_attempted.set()
            self._lock.acquire()
            if not self._entered_first.is_set():
                self._entered_first.set()
                assert self._second_attempted.wait(timeout=1.0)
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )
    coordinated_lock = _CoordinatedLock()
    contract._lock = coordinated_lock

    thread_results = []

    def _run_cleanup() -> None:
        contract.cleanup()
        thread_results.append(True)

    first = threading.Thread(target=_run_cleanup)
    second = threading.Thread(target=_run_cleanup)
    first.start()
    coordinated_lock._entered_first.wait(timeout=1.0)
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert thread_results == [True, True]
    assert contract.cleaned is True
    assert contract._lock is None
