import threading

import pytest

from melder.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)


def test_frame_link_contract_defaults_to_frame_name_selection() -> None:
    """
    Verify one per-frame contract defaults every ACL family to `frame_name`.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    assert contract.frame_name == "ops"
    assert contract.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }
    assert contract.get_selected_contract_name() == "ops"


def test_frame_link_contract_properties_and_snapshot_views_are_detached() -> None:
    """
    Verify metadata and selection snapshots are detached.

    Returns:
        None.
    """
    metadata = {"mode": "safe"}
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
        metadata=metadata,
    )

    metadata["mutated"] = True
    selection_snapshot = contract.get_selected_contract_names()
    selection_snapshot["view"] = "mutated"

    assert contract.contract_id
    assert contract.rift_id == "rift-1"
    assert contract.frame_name == "ops"
    assert contract.metadata == {"mode": "safe"}
    assert contract.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }


def test_frame_link_contract_rejects_invalid_inputs() -> None:
    """
    Verify the one-frame contract rejects malformed inputs.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        FrameLinkContract(rift_id="", frame_name="ops")

    with pytest.raises(ValueError, match="frame_name cannot be empty"):
        FrameLinkContract(rift_id="rift-1", frame_name="")


def test_frame_link_contract_describe_and_clone_include_selection() -> None:
    """
    Verify describe and clone preserve per-frame selection.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    description = contract.describe()
    clone = contract.clone()

    assert description["frame_name"] == "ops"
    assert description["selected_contract_names"] == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }
    assert clone.frame_name == "ops"
    assert clone.get_selected_contract_names() == {
        "view": "ops",
        "command": "ops",
        "codegen": "ops",
    }


def test_frame_link_contract_cleanup_rechecks_cleaned_inside_lock() -> None:
    class _CoordinatedLock:
        def __init__(self, contract: FrameLinkContract) -> None:
            self._contract = contract
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
                self._contract._cleaned = True
            return self

        def __exit__(self, exc_type, exc, tb):
            self._lock.release()

    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )
    contract._lock = _CoordinatedLock(contract)

    first = threading.Thread(target=contract.cleanup)
    second = threading.Thread(target=contract.cleanup)
    first.start()
    second.start()
    first.join(timeout=1.0)
    second.join(timeout=1.0)

    assert contract.cleaned is True


def test_frame_link_contract_cleanup_is_idempotent() -> None:
    """
    Verify cleanup can be called repeatedly.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        frame_name="ops",
    )

    contract.cleanup()
    contract.cleanup()

    assert contract.cleaned is True
