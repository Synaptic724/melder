import threading

import pytest

from melder.aether.nexus.rift.frame_link.frame_link_contract import (
    FrameLinkContract,
)


def test_frame_link_contract_defaults_to_same_name_selection() -> None:
    """
    Verify assigned frames default every ACL family to `default`.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    assert contract.get_selected_contract_names("ops") == {
        "view": "default",
        "command": "default",
        "codegen": "default",
    }
    assert contract.get_selected_contract_name("ops") == "default"


def test_frame_link_contract_accepts_same_name_string_mapping_on_init() -> None:
    """
    Verify constructor accepts same-name string mappings as convenience input.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        selected_contract_names_by_frame_name={"ops": "ops_contract"},
    )

    assert contract.get_selected_contract_names("ops") == {
        "view": "ops_contract",
        "command": "ops_contract",
        "codegen": "ops_contract",
    }

    duplicate_contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "ops"),
        default_frame_name="ops",
    )
    assert duplicate_contract.assigned_frame_names == ("ops",)


def test_frame_link_contract_accepts_explicit_family_selection_on_init() -> None:
    """
    Verify constructor accepts explicit family-name selections.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        selected_contract_names_by_frame_name={
            "ops": {
                "view": "view_ops",
                "command": "command_ops",
                "codegen": "codegen_ops",
            }
        },
    )

    assert contract.get_selected_contract_names("ops") == {
        "view": "view_ops",
        "command": "command_ops",
        "codegen": "codegen_ops",
    }
    assert contract.get_selected_contract_name("ops") == "view_ops"


def test_frame_link_contract_properties_and_snapshot_views_are_detached() -> None:
    metadata = {"mode": "safe"}
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        metadata=metadata,
    )

    metadata["mutated"] = True
    selection_snapshot = contract.selected_contract_names_by_frame_name
    selection_snapshot["ops"]["view"] = "mutated"

    assert contract.contract_id
    assert contract.rift_id == "rift-1"
    assert contract.assigned_frame_names == ("ops",)
    assert contract.default_frame_name == "ops"
    assert contract.metadata == {"mode": "safe"}
    assert contract.selected_contract_names_by_frame_name == {
        "ops": {
            "view": "default",
            "command": "default",
            "codegen": "default",
        }
    }


def test_frame_link_contract_register_frame_can_seed_and_replace_default() -> None:
    """
    Verify register_frame can seed same-name or explicit family selections.

    Returns:
        None.
    """
    contract = FrameLinkContract(rift_id="rift-1")

    contract.register_frame("ops")
    contract.register_frame(
        "finance",
        set_as_default=True,
        view_contract_name="view_finance",
        command_contract_name="command_finance",
        codegen_contract_name="codegen_finance",
    )

    assert contract.default_frame_name == "finance"
    assert contract.get_selected_contract_names("ops") == {
        "view": "default",
        "command": "default",
        "codegen": "default",
    }
    assert contract.get_selected_contract_names("finance") == {
        "view": "view_finance",
        "command": "command_finance",
        "codegen": "codegen_finance",
    }


def test_frame_link_contract_can_update_selected_contract_names_for_assigned_frame() -> None:
    """
    Verify same-name and explicit family selection updates both work.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )

    contract.set_selected_contract_name("ops", "ops_contract")
    assert contract.get_selected_contract_names("ops") == {
        "view": "ops_contract",
        "command": "ops_contract",
        "codegen": "ops_contract",
    }

    contract.set_selected_contract_names(
        "ops",
        view_contract_name="view_ops",
        command_contract_name="command_ops",
        codegen_contract_name="codegen_ops",
    )
    assert contract.get_selected_contract_names("ops") == {
        "view": "view_ops",
        "command": "command_ops",
        "codegen": "codegen_ops",
    }


def test_frame_link_contract_rejects_invalid_selection_inputs() -> None:
    """
    Verify the contract rejects malformed selection payloads.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="rift_id cannot be empty"):
        FrameLinkContract(rift_id="")

    with pytest.raises(ValueError, match="assigned_frame_names must contain non-empty strings"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops", ""),
        )

    with pytest.raises(ValueError, match="default_frame_name must be present"):
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

    with pytest.raises(
            TypeError,
            match="selected_contract_names_by_frame_name must be a dict when provided.",
    ):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name="bad",
        )

    with pytest.raises(ValueError, match="selected contract frame 'finance' must be present"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name={"finance": "finance_contract"},
        )

    with pytest.raises(ValueError, match="contract_name cannot be empty"):
        contract = FrameLinkContract(rift_id="rift-1", assigned_frame_names=("ops",))
        contract.set_selected_contract_name("ops", "")

    with pytest.raises(ValueError, match="view_contract_name must be a non-empty string"):
        FrameLinkContract(
            rift_id="rift-1",
            assigned_frame_names=("ops",),
            selected_contract_names_by_frame_name={
                "ops": {
                    "view": "",
                    "command": "command_ops",
                    "codegen": "codegen_ops",
                }
            },
        )

    contract = FrameLinkContract(rift_id="rift-1", assigned_frame_names=("ops",))

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.has_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.get_selected_contract_names("")

    with pytest.raises(KeyError, match="Frame 'missing' is not assigned"):
        contract.get_selected_contract_names("missing")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.get_selected_contract_name("")

    with pytest.raises(KeyError, match="Frame 'missing' is not assigned"):
        contract.get_selected_contract_name("missing")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.set_selected_contract_name("", "ops_contract")

    with pytest.raises(KeyError, match="Frame 'missing' is not assigned"):
        contract.set_selected_contract_name("missing", "ops_contract")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.set_selected_contract_names("")

    with pytest.raises(KeyError, match="Frame 'missing' is not assigned"):
        contract.set_selected_contract_names("missing")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.remove_frame("")

    with pytest.raises(ValueError, match="frame_name cannot be empty."):
        contract.register_frame("")

    with pytest.raises(ValueError, match="command_contract_name must be a non-empty string."):
        FrameLinkContract._normalize_contract_selection(
            "default",
            command_contract_name="",
        )

    with pytest.raises(ValueError, match="codegen_contract_name must be a non-empty string."):
        FrameLinkContract._normalize_contract_selection(
            "default",
            codegen_contract_name="",
        )

    with pytest.raises(ValueError, match="selected contract names must be provided as a string or dict."):
        FrameLinkContract._normalize_contract_selection_input(object())

    with pytest.raises(ValueError, match="view_contract_name must be a non-empty string."):
        FrameLinkContract._normalize_contract_selection(
            "default",
            view_contract_name=123,
        )


def test_frame_link_contract_describe_and_clone_include_nested_selection() -> None:
    """
    Verify describe and clone preserve nested family selections.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops",),
        default_frame_name="ops",
        selected_contract_names_by_frame_name={
            "ops": {
                "view": "view_ops",
                "command": "command_ops",
                "codegen": "codegen_ops",
            }
        },
    )

    description = contract.describe()
    clone = contract.clone()

    assert description["selected_contract_names_by_frame_name"] == {
        "ops": {
            "view": "view_ops",
            "command": "command_ops",
            "codegen": "codegen_ops",
        }
    }
    assert clone.get_selected_contract_names("ops") == {
        "view": "view_ops",
        "command": "command_ops",
        "codegen": "codegen_ops",
    }


def test_frame_link_contract_remove_frame_updates_default_and_selection() -> None:
    """
    Verify removing frames updates the default frame and selection map.

    Returns:
        None.
    """
    contract = FrameLinkContract(
        rift_id="rift-1",
        assigned_frame_names=("ops", "finance"),
        default_frame_name="ops",
    )

    contract.remove_frame("ops")

    assert contract.default_frame_name == "finance"
    assert contract.has_frame("finance") is True
    assert contract.has_frame("ops") is False

    contract.remove_frame("missing")
    assert contract.assigned_frame_names == ("finance",)


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
        assigned_frame_names=("ops",),
        default_frame_name="ops",
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
        assigned_frame_names=("ops",),
        default_frame_name="ops",
    )

    contract.cleanup()
    contract.cleanup()

    assert contract.cleaned is True
